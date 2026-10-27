"""Shared paths, sources and helpers for the own-names-bench v1.3 conversation test suite (README.md).

Copied from lore-poc convdata/common.py (branch data/conv-names-v1, commit 9004fe4, sha256 2e1ff34c...), the recipe of
the conversation train and dev data, so the test suite is augmented exactly as dev was. Changed: the paths (the
sealed suite has a volume path of its own; the train and dev data are only read) and the source list (test splits).
Added: write_flac_checked (every file is read back and hash-checked: one EUR-IS-1 host wrote zero-filled files)."""
import hashlib
import io
import json
import os
import re
import socket
import unicodedata
from pathlib import Path

import numpy as np

# the sealed suite and its build files (never under a ctxft/, convdata/, lore-conv or v06-* path)
SEALED = Path(os.environ.get("ONB_SEALED", "/gpu-cli-workspaces/jameslal/onb-v13-conv-SEALED"))
WORK = SEALED / "build"     # sources, prepared utterances, noise (not part of the sealed suite)
SUITE = SEALED / "suite"    # the sealed suite: suite.json per condition, audio, licences
# the conversation train and dev data the suite is checked against (read only): the EUR-IS-1 copy that v0.6 trains on
TRAINDEV = Path(os.environ.get("CONV_TRAINDEV", "/gpu-cli-workspaces/jameslal/v06-conv/lore-conv"))
RATE = 16000

# Every source, its licence and the revision fetched. Licences were read from each source's own
# licence file or card on 2026-10-14; only commercial-use permissive licences (CC0, CC BY) are used.
SOURCES: dict[str, dict] = {
    "voxpopuli": {"repo": "facebook/voxpopuli", "revision": "42f01879c780b4a2e90ec0b4f616c2ece526e4f1", "licence": "CC0 1.0",
                  "files": ["en/test-00000-of-00001.parquet"],
                  "what": "European Parliament plenary speeches, English transcribed subset, test split; speaker ids"},
    "libritts": {"repo": "mythicinfinity/libritts_r", "revision": "0d1718db351207d5a493135a62d5ed8cc4733830", "licence": "CC BY 4.0",
                 "files": [f"data/test.{s}/test.{s}-0000{i}-of-00003.parquet" for s in ("clean", "other") for i in range(3)],
                 "what": "LibriTTS-R test-clean and test-other (restored LibriVox read speech)"},
    "fsd": {"repo": "Fhrozen/FSD50k", "revision": "ccf1acaff12f3f4a4c10052dddafbb6d22152c9b",
            "licence": "CC BY 4.0 (FSD50K); only clips whose own licence is CC0 1.0 or CC BY 3.0 (fsd_test.json)",
            "what": "FSD50K clips without speech or music, none used in train or dev and by no train/dev uploader: street and "
                    "indoor/ambient background noise"},
    "meta": {"repo": "openslr 12 raw-metadata.tar.gz", "revision": "sha256 in build/src/fetched.json", "licence": "CC BY 4.0",
             "what": "LibriSpeech SPEAKERS.TXT / CHAPTERS.TXT: reader names and LibriVox projects, for the reader and book exclusions"},
    "wav2vec2": {"repo": "facebook/wav2vec2-large-960h-lv60-self", "revision": "54074b1c16f4de6a5ad59affb4caa8f2ea03a119",
                 "licence": "Apache 2.0", "what": "CTC character model, used only to time the reference's words by forced alignment "
                                                 "(no transcript is produced)"},
}


def flac_bytes(x: np.ndarray) -> bytes:
    import soundfile as sf
    pcm = np.clip(np.round(np.asarray(x, dtype=np.float64) * 32768.0), -32768, 32767).astype(np.int16)
    buf = io.BytesIO()
    sf.write(buf, pcm, RATE, subtype="PCM_16", format="FLAC")
    return buf.getvalue()


def pcm_sha(x: np.ndarray) -> str:
    """SHA-256 of the 16-bit PCM of a float signal, as own-names-bench hashes PCM."""
    pcm = np.clip(np.round(np.asarray(x, dtype=np.float64) * 32768.0), -32768, 32767).astype("<i2")
    return hashlib.sha256(pcm.tobytes()).hexdigest()


def write_flac_checked(path: Path, x: np.ndarray) -> dict:
    """Writes 16-bit FLAC, fsyncs, reads it back and compares SHA-256 with the bytes meant (a zero-filled or short write
    raises). Returns {sha256, pcm_sha256, seconds}."""
    data = flac_bytes(x)
    want = hashlib.sha256(data).hexdigest()
    path.parent.mkdir(parents=True, exist_ok=True)
    for _ in range(3):
        with path.open("wb") as f:
            f.write(data)
            f.flush()
            os.fsync(f.fileno())
        if hashlib.sha256(path.read_bytes()).hexdigest() == want:
            import soundfile as sf
            y, _ = sf.read(path, dtype="int16")
            return {"sha256": want, "pcm_sha256": hashlib.sha256(y.astype("<i2").tobytes()).hexdigest(), "seconds": round(len(y) / RATE, 3)}
    raise SystemExit(f"VOLUME WRITE CORRUPTED {path} on {socket.gethostname()}")

TAG = f"[{socket.gethostname()[-6:]}/{os.getpid()}]"


def log(*parts: object) -> None:
    print(TAG, *parts, flush=True)


def jsonl(path: Path):
    with Path(path).open() as f:
        for line in f:
            if line.strip():
                yield json.loads(line)


def letters(s: str) -> str:
    s = unicodedata.normalize("NFKD", s.replace("æ", "ae").replace("Æ", "Ae"))
    return "".join(c for c in s.lower() if "a" <= c <= "z")


def to_mono16k(x: np.ndarray, rate: int) -> np.ndarray:
    from scipy.signal import resample_poly
    x = x.astype(np.float32)
    if x.ndim > 1:
        x = x.mean(axis=1)
    if rate != RATE:
        g = np.gcd(rate, RATE)
        x = resample_poly(x, RATE // g, rate // g).astype(np.float32)
    return x


# ---------------------------------------------------------------- word times

class Aligner:
    """Word times by CTC forced alignment of known words with an Apache-2.0 character model."""

    def __init__(self, device: str = "cuda") -> None:
        import torch
        from transformers import Wav2Vec2ForCTC, Wav2Vec2Processor
        rev = SOURCES["wav2vec2"]
        self.torch, self.device = torch, device
        self.proc = Wav2Vec2Processor.from_pretrained(rev["repo"], revision=rev["revision"])
        self.model = Wav2Vec2ForCTC.from_pretrained(rev["repo"], revision=rev["revision"]).to(device).eval().half()
        self.vocab = self.proc.tokenizer.get_vocab()
        self.blank = self.proc.tokenizer.pad_token_id
        self.sep = self.vocab["|"]

    def spell(self, word: str) -> list[int]:
        w = unicodedata.normalize("NFKD", word.replace("’", "'")).upper()
        return [self.vocab[c] for c in w if c in self.vocab and c not in "|" and (c.isalpha() or c == "'")]

    def words(self, x: np.ndarray, words: list[str]) -> list[dict] | None:
        torch = self.torch
        spelled = [self.spell(w) for w in words]
        if not words or not all(spelled):
            return None
        tokens: list[int] = []
        owner: list[int] = []
        for i, s in enumerate(spelled):
            if i:
                tokens.append(self.sep)
                owner.append(-1)
            tokens += s
            owner += [i] * len(s)
        with torch.inference_mode():
            inp = torch.from_numpy((x - x.mean()) / (x.std() + 1e-7)).to(self.device).half()[None]
            lp = torch.log_softmax(self.model(inp).logits.float(), dim=-1)[0].cpu().numpy()
        T = lp.shape[0]
        if len(tokens) * 2 + 1 > 2 * T:
            return None
        path = ctc_align(lp, np.array(tokens, dtype=np.int64), self.blank)
        if path is None:
            return None
        step = len(x) / RATE / T
        out = [{"start": None, "end": None, "score": []} for _ in words]
        for t, k in enumerate(path):
            if k >= 0 and owner[k] >= 0:
                o = out[owner[k]]
                o["start"] = t * step if o["start"] is None else o["start"]
                o["end"] = (t + 1) * step
                o["score"].append(float(np.exp(lp[t, tokens[k]])))
        for o in out:
            if o["start"] is None:
                return None
            o["start"], o["end"], o["score"] = round(o["start"], 3), round(o["end"], 3), round(float(np.mean(o["score"])), 3)
        return out


def ctc_align(lp: np.ndarray, tokens: np.ndarray, blank: int) -> list[int] | None:
    """Viterbi CTC alignment: for every frame, the index of the token it emits (-1 for blank)."""
    T, L = lp.shape[0], len(tokens)
    S = 2 * L + 1
    lab = np.full(S, blank, dtype=np.int64)
    lab[1::2] = tokens
    emit = lp[:, lab]  # (T, S)
    NEG = -1e30
    dp = np.full(S, NEG)
    dp[0], dp[1] = emit[0, 0], emit[0, 1]
    back = np.zeros((T, S), dtype=np.int8)
    skip_ok = np.zeros(S, dtype=bool)
    skip_ok[3::2] = lab[3::2] != lab[1:-2:2]
    for t in range(1, T):
        a = dp
        b = np.concatenate([[NEG], dp[:-1]])
        c = np.concatenate([[NEG, NEG], dp[:-2]])
        c = np.where(skip_ok, c, NEG)
        stack = np.stack([a, b, c])
        arg = stack.argmax(axis=0)
        dp = stack[arg, np.arange(S)] + emit[t]
        back[t] = arg
    end = S - 1 if dp[S - 1] >= dp[S - 2] else S - 2
    if dp[end] < -1e29:
        return None
    s, path = end, []
    for t in range(T - 1, -1, -1):
        path.append(s)
        s -= int(back[t, s])
    path.reverse()
    return [int((p - 1) // 2) if p % 2 == 1 else -1 for p in path]


# ---------------------------------------------------------------- names in text

TITLES = set("""mr mrs ms miss madam madame sir dr doctor president commissioner minister prime chair chairman chairwoman
member members house rapporteur vice general secretary council commission parliament european union committee court
group party state states lord lady king queen saint st mount lake river street road monday tuesday wednesday thursday
friday saturday sunday january february march april may june july august september october november december
""".split())


class NameFinder:
    """Proper nouns of a corpus: words capitalized mid-sentence, never written in lower case in the corpus, and not
    among the 1,500 most frequent English words, nor a title or month (so Commission, May and Mr are not names; Juncker, Greece, London and Laura are). Runs of
    such words (up to three, with a capitalized neighbour that is not a title) make one name."""

    def __init__(self, texts: list[str], top: int = 1500) -> None:
        from wordfreq import top_n_list
        self.common = set(top_n_list("en", top))
        lower, mid = set(), set()
        for t in texts:
            for i, (w, initial) in enumerate(tokens(t)):
                k = letters(w)
                if not k:
                    continue
                if w[:1].islower():
                    lower.add(k)
                elif not initial:
                    mid.add(k)
        self.proper = {k for k in mid - lower if len(k) >= 3 and k not in self.common and k not in TITLES}

    def find(self, text: str) -> list[dict]:
        """[{name, a, b}] word spans (indices into text.split()) of names in a text."""
        toks = tokens(text)
        out, i = [], 0
        while i < len(toks):
            w, initial = toks[i]
            k = letters(w)
            if k in self.proper and (not initial or k in self.proper):
                a, b = i, i + 1
                while b < len(toks) and b - a < 3 and letters(toks[b][0]) in self.proper and not toks[b - 1][0].endswith((",", ".", ";", ":")):
                    b += 1
                spelled = " ".join(clean_word(toks[j][0]) for j in range(a, b))
                if all(clean_word(toks[j][0]) for j in range(a, b)):
                    out.append({"name": spelled, "a": a, "b": b})
                i = b
            else:
                i += 1
        return out


def clean_word(w: str) -> str:
    w = w.strip(".,;:!?()[]{}\"“”‘’*`").replace("’", "'")
    w = re.sub(r"'s$", "", w)
    return w if re.fullmatch(r"[A-Za-zÀ-ÿ][A-Za-zÀ-ÿ'\-]*", w) else ""


def tokens(text: str) -> list[tuple[str, bool]]:
    """Whitespace words with a flag: sentence-initial."""
    out, initial = [], True
    for w in text.split():
        out.append((w, initial))
        initial = bool(re.search(r"[.!?:]['\"”’)]*$", w)) or w.startswith(("\"", "“", "‘"))
    return out


# ---------------------------------------------------------------- augmentation

def rms(x: np.ndarray) -> float:
    return float(np.sqrt(np.mean(x.astype(np.float64) ** 2)) + 1e-9)


def mix(speech: np.ndarray, noise: np.ndarray, snr_db: float, rng: np.random.Generator) -> np.ndarray:
    if len(noise) < len(speech):
        noise = np.tile(noise, len(speech) // max(1, len(noise)) + 1)
    at = int(rng.integers(0, len(noise) - len(speech) + 1))
    n = noise[at:at + len(speech)]
    n = n * (rms(speech) / rms(n)) / (10 ** (snr_db / 20))
    return (speech + n).astype(np.float32)


def level(x: np.ndarray, rng: np.random.Generator, lo: float = -32, hi: float = -18) -> np.ndarray:
    """Scales to a random RMS level (dBFS) and keeps peaks below 0.99."""
    y = x * (10 ** (rng.uniform(lo, hi) / 20) / rms(x))
    peak = float(np.abs(y).max())
    return (y / peak * 0.99 if peak > 0.99 else y).astype(np.float32)


def reverb(x: np.ndarray, rir: np.ndarray) -> np.ndarray:
    from scipy.signal import fftconvolve
    d = int(np.argmax(np.abs(rir)))
    y = fftconvolve(x, rir)[d:d + len(x)]
    return y.astype(np.float32)


def telephone(x: np.ndarray, rng: np.random.Generator) -> tuple[np.ndarray, dict]:
    """A phone line: 300-3400 Hz, 8 kHz, a narrowband codec (G.711 mu-law or A-law, GSM 06.10, or Opus at 6-12 kb/s),
    sometimes a few lost 20 ms packets, back to 16 kHz."""
    import subprocess
    import tempfile

    from scipy.signal import butter, resample_poly, sosfilt
    sos = butter(4, [300, 3400], btype="bandpass", fs=RATE, output="sos")
    y = sosfilt(sos, x).astype(np.float32)
    y = resample_poly(y, 1, 2).astype(np.float32)
    y = level(y, rng, -26, -16)
    codec = str(rng.choice(["mulaw", "alaw", "gsm", "opus", "opus"]))
    info = {"codec": codec}
    if codec in ("mulaw", "alaw"):
        y = g711(y, codec)
    else:
        args = ["-c:a", "libgsm"] if codec == "gsm" else ["-c:a", "libopus", "-b:a", f"{int(rng.integers(6, 13))}k", "-application", "voip"]
        ext = ".gsm" if codec == "gsm" else ".ogg"
        with tempfile.TemporaryDirectory() as d:
            src, enc, dec = f"{d}/a.wav", f"{d}/b{ext}", f"{d}/c.wav"
            import soundfile as sf
            sf.write(src, y, 8000)
            ok = subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-i", src, "-ar", "8000", "-ac", "1", *args, enc],
                                capture_output=True).returncode == 0 and \
                subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-i", enc, "-ar", "8000", "-ac", "1", dec],
                               capture_output=True).returncode == 0
            if ok:
                z, _ = sf.read(dec, dtype="float32")
                y = np.pad(z, (0, max(0, len(y) - len(z))))[:len(y)]
            else:
                y, info["codec"] = g711(y, "mulaw"), "mulaw (fallback)"
    if rng.random() < 0.3:  # lost packets, concealed by silence
        frames = len(y) // 160
        lost = rng.random(frames) < rng.uniform(0.005, 0.03)
        for f in np.flatnonzero(lost):
            y[f * 160:(f + 1) * 160] = 0.0
        info["lost_packets"] = int(lost.sum())
    y = resample_poly(y, 2, 1).astype(np.float32)[:len(x)]
    return np.pad(y, (0, len(x) - len(y))), info


def g711(y: np.ndarray, law: str) -> np.ndarray:
    y = np.clip(y, -1, 1)
    if law == "mulaw":
        mu = 255.0
        c = np.sign(y) * np.log1p(mu * np.abs(y)) / np.log1p(mu)
        q = np.round(c * 127) / 127
        return (np.sign(q) * np.expm1(np.abs(q) * np.log1p(mu)) / mu).astype(np.float32)
    A = 87.6
    a = np.abs(y)
    c = np.where(a < 1 / A, A * a / (1 + np.log(A)), (1 + np.log(np.maximum(A * a, 1e-12))) / (1 + np.log(A)))
    q = np.round(np.sign(y) * c * 127) / 127
    aq = np.abs(q)
    lin = np.where(aq < 1 / (1 + np.log(A)), aq * (1 + np.log(A)) / A, np.exp(aq * (1 + np.log(A)) - 1) / A)
    return (np.sign(q) * lin).astype(np.float32)


def make_rirs(n: int, seed: int) -> list[dict]:
    """Shoebox rooms (pyroomacoustics, MIT): 3-12 m, RT60 0.25-1.0 s, talker 1-5 m from the microphone, plus a second
    source position for noise. Returns [{rir, noise_rir, rt60, distance, room}]."""
    import pyroomacoustics as pra
    rng = np.random.default_rng(seed)
    out = []
    while len(out) < n:
        room = np.array([rng.uniform(3, 12), rng.uniform(3, 10), rng.uniform(2.4, 4)])
        rt60 = rng.uniform(0.25, 1.0)
        try:
            absorption, order = pra.inverse_sabine(rt60, room)
        except ValueError:
            continue
        mic = np.array([rng.uniform(0.5, room[0] - 0.5), rng.uniform(0.5, room[1] - 0.5), rng.uniform(0.7, 1.5)])
        pos = []
        for _ in range(2):
            for _ in range(50):
                p = np.array([rng.uniform(0.3, room[0] - 0.3), rng.uniform(0.3, room[1] - 0.3), rng.uniform(1.1, 1.9)])
                if 1.0 <= np.linalg.norm(p - mic) <= 5.0:
                    pos.append(p)
                    break
        if len(pos) < 2:
            continue
        r = pra.ShoeBox(room, fs=RATE, materials=pra.Material(absorption), max_order=min(order, 17))
        for p in pos:
            r.add_source(p)
        r.add_microphone(mic)
        r.compute_rir()
        out.append({"rir": np.asarray(r.rir[0][0], dtype=np.float32), "noise_rir": np.asarray(r.rir[0][1], dtype=np.float32),
                    "rt60": round(float(rt60), 2), "distance": round(float(np.linalg.norm(pos[0] - mic)), 2),
                    "room": [round(float(v), 1) for v in room]})
    return out
