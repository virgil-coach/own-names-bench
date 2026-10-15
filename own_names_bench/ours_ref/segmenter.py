"""Detail Keeper's window cutter (services/engine/crates/detailkeeper/src/session.rs `Segmenter`,
detailkeeper@10b709d), line for line, with the same float arithmetic: a window is cut at a pause of
0.45 s once two seconds have been heard, otherwise at the quietest point between five and eight
seconds. Fed 0.1 s at a time, as the benchmark runners do on every runtime.

The live app also cuts early when a draft is due; offline there are no drafts, so the cap does it.

Short windows (`min_speech_s`, off at 0): a pause does not cut a window whose speech, first speech
frame to last, is shorter than `min_speech_s`, unless the quiet has lasted `hold_s`: a short
utterance waits for what is said next and goes to the writer with it (the cap still holds), and a
short utterance after which the speaker stops is cut after `hold_s`. The writer given a shortlist
drops very short windows (own-names-bench v1.2 diagnosis); this is the engine's rule (session.rs).
"""

from dataclasses import dataclass

import numpy as np
from numba import njit

RATE = 16000
FRAME = 320
MAX_S = 8.0
MIN_S = 2.0
PAUSE_S = 0.45
CAP_FROM_S = 5.0
WINDOW_STEP_S = 0.2
CHUNK = 1600


def step() -> int:
    return round(WINDOW_STEP_S * RATE / FRAME)


@njit(cache=True)
def _rms(buf: np.ndarray, n: int) -> np.ndarray:
    out = np.empty(n, dtype=np.float32)
    for i in range(n):
        s = 0.0
        for k in range(i * FRAME, (i + 1) * FRAME):
            v = np.float32(buf[k] * buf[k])
            s += np.float64(v)
        out[i] = np.sqrt(np.float32(s / FRAME))
    return out


@njit(cache=True)
def _smooth5(x: np.ndarray) -> np.ndarray:
    n = x.shape[0]
    out = np.empty(n, dtype=np.float64)
    for i in range(n):
        s = 0.0
        for k in range(5):
            j = i + 2 - k
            if 0 <= j < n:
                s += np.float64(x[j]) * 0.2
        out[i] = s
    return out


def _percentile(x: np.ndarray, q: float) -> float:
    v = np.sort(x.astype(np.float64))
    pos = (len(v) - 1) * q / 100.0
    lo, hi = int(np.floor(pos)), int(np.ceil(pos))
    return float(v[lo] + (v[hi] - v[lo]) * (pos - lo))


@dataclass
class Window:
    n: int
    start_s: float
    audio_from_s: float
    end_s: float
    at_pause: bool
    audio: np.ndarray


class Segmenter:
    def __init__(self, at_s: float = 0.0, min_speech_s: float = 0.0, hold_s: float = PAUSE_S) -> None:
        self.min_speech_s, self.hold_s = min_speech_s, hold_s
        self.start_s = at_s
        self.from_s = at_s
        self.buf = np.zeros(0, dtype=np.float32)
        self.loud = 0.0
        self.cuts = 0
        self.rms = np.zeros(0, dtype=np.float32)

    def speech(self) -> np.ndarray:
        n = len(self.buf) // FRAME
        if n == 0:
            self.rms = np.zeros(0, dtype=np.float32)
            return np.zeros(0, dtype=bool)
        self.rms = _rms(self.buf, n)
        self.loud = max(self.loud, _percentile(self.rms, 95.0))
        bar = max(0.002, 0.08 * self.loud)
        return self.rms.astype(np.float64) >= bar

    def push(self, x: np.ndarray) -> list[Window]:
        self.loud *= 0.5 ** (len(x) / RATE / 30.0)
        self.buf = np.concatenate([self.buf, x.astype(np.float32)])
        out = []
        while (w := self.cut()) is not None:
            out.append(w)
        return out

    def drop_front(self, samples: int) -> None:
        samples = min(samples, len(self.buf))
        self.buf = self.buf[samples:]
        self.from_s += samples / RATE

    def quietest(self, lo: int, hi: int, upto: int) -> int:
        smooth = _smooth5(self.rms[: min(upto, len(self.rms))])
        st = step()
        best_k, best_v = 0, float("inf")
        k, i = 0, lo
        while i <= hi and i < len(smooth):
            if smooth[i] < best_v:
                best_k, best_v = k, smooth[i]
            k += 1
            i += st
        return lo + st * best_k

    def cut(self) -> Window | None:
        speech = self.speech()
        if not speech.any():
            if len(self.buf) > 2 * RATE:
                self.drop_front(len(self.buf) - int(0.3 * RATE))
            return None
        first = int(np.argmax(speech))
        lead = first * FRAME - int(0.2 * RATE)
        if lead > 0:
            self.drop_front(lead)
            speech = self.speech()
        n = len(speech)
        tail = int(PAUSE_S * RATE / FRAME)
        if len(self.buf) >= MAX_S * RATE:
            lo = int(CAP_FROM_S * RATE / FRAME)
            hi = int(MAX_S * RATE / FRAME)
            at = self.quietest(lo, hi, hi)
            return self.take(at * FRAME, speech, False)
        said = int(speech.sum())
        if len(self.buf) >= MIN_S * RATE and not speech[max(0, n - tail):].any() and said >= 10:
            st = step()
            last = int(n - 1 - np.argmax(speech[::-1]))
            if (last - int(np.argmax(speech)) + 1) * FRAME < self.min_speech_s * RATE:
                # a short utterance: keep it for what comes next, unless the speaker has stopped
                hold = int(self.hold_s * RATE / FRAME)
                if n - 1 - last < hold:
                    return None
                return self.take(max(0, last + 1 + tail - 5) // st * st * FRAME, speech, True)
            return self.take(max(0, n - 5) // st * st * FRAME, speech, True)
        return None

    def take(self, cut: int, speech: np.ndarray, at_pause: bool) -> Window:
        cut = min(cut, len(self.buf))
        end_s = self.from_s + cut / RATE
        audio = self.buf[:cut].copy()
        self.buf = self.buf[cut:]
        w = Window(self.cuts, self.start_s, self.from_s, end_s, at_pause, audio)
        self.start_s = end_s
        self.from_s = end_s
        self.cuts += 1
        return w

    def flush(self) -> Window | None:
        speech = self.speech()
        if int(speech.sum()) >= 10:
            return self.take(len(self.buf), speech, True)
        self.drop_front(len(self.buf))
        return None


def windows(audio: np.ndarray, min_speech_s: float = 0.0, hold_s: float = PAUSE_S) -> list[Window]:
    seg = Segmenter(0.0, min_speech_s, hold_s)
    out: list[Window] = []
    for i in range(0, len(audio), CHUNK):
        out += seg.push(audio[i : i + CHUNK])
    last = seg.flush()
    if last is not None:
        out.append(last)
    return out
