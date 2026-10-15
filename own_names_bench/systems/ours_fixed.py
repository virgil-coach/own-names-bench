"""Ours (ours_torch.OursTorch) with the three pipeline fixes of the v1.2 conversation diagnosis, each
switchable, every window traced (no-list text, list answer, final text) so a pass can be taken apart:

  guard   empty-answer guard: a window whose list answer is empty while its no-list text has words
          gets the no-list text (the engine runs the no-list pass only then; here it is run for the
          spotter anyway)
  level   level-match: every taught recording scaled to the window's speech level before the writer
          hears it (writer.level_matched)
  short   short windows: a pause does not cut a window with under `min_speech_s` of speech unless the
          speaker has stopped for `hold_s` (segmenter.Segmenter)

`ours-fixed` is all three, as the engine branch engine/empty-level-short runs them.
"""

import hashlib
import time

import numpy as np

from ..ours_ref import segmenter
from .base import Output
from .ours_torch import CACHE_WINDOWS, TOP, OursTorch, read16k

# set on the dev sets (diag/dev.py), never on benchmark items
MIN_SPEECH_S = 2.5
HOLD_S = 1.0


class OursFixed(OursTorch):
    def __init__(self, name: str = "ours-fixed", guard: bool = True, level: bool = True, min_speech_s: float = MIN_SPEECH_S,
                 hold_s: float = HOLD_S, variants: tuple[str, ...] = ("none", "own")) -> None:
        super().__init__()
        self.name, self.guard, self.level, self.min_speech_s, self.hold_s = name, guard, level, min_speech_s, hold_s
        self.variants = variants

    def config(self) -> dict:
        c = super().config()
        c.update({"fixes": {"guard": "an empty list answer gets the no-list text" if self.guard else "off",
                            "level": "taught recordings scaled to the window's speech RMS (louder half of 20 ms frames)" if self.level else "off",
                            "short": (f"a pause cuts a window with under {self.min_speech_s} s of speech only after {self.hold_s} s of quiet"
                                      if self.min_speech_s > 0 else "off")},
                  "windows": c["windows"] + (f"; short windows held (min speech {self.min_speech_s} s, hold {self.hold_s} s)" if self.min_speech_s > 0 else ""),
                  "trace": "per-window plain / written / final text in extra.windows"})
        return c

    def transcribe(self, audio, names: list[str], entries: list[dict]) -> Output:
        from ..ours_ref.writer import level_matched, recited

        x = read16k(audio) if not isinstance(audio, np.ndarray) else audio
        want = set(names)
        seen: set[str] = set()
        chosen = []
        for e in entries:
            if e["written"] in want and e["written"] not in seen:
                seen.add(e["written"])
                chosen.append(e)
        t_enroll = time.perf_counter()
        new = [e["id"] for e in chosen if e["id"] not in self.heard]
        terms = [self._term(e) for e in chosen]
        t0 = time.perf_counter()
        enroll_s = t0 - t_enroll
        texts, wins = [], []
        reused = 0.0
        for w in segmenter.windows(x, self.min_speech_s, self.hold_s):
            key = hashlib.sha1(w.audio.tobytes()).hexdigest()
            cached = self.plain_cache.get(key)
            if cached is None:
                t = time.perf_counter()
                cached = (self.writer.plain(w.audio), time.perf_counter() - t)
                self.plain_cache[key] = cached
                if len(self.plain_cache) > CACHE_WINDOWS:
                    self.plain_cache.popitem(last=False)
            else:
                reused += cached[1]
            plain = cached[0]
            text, written, was_recited, guarded = plain, None, False, False
            listed: list[str] = []
            if terms:
                hits = self.spotter.rank(terms, w.audio, plain, TOP)
                reused += self.spotter.reused_s
                listed = [h.term.written for h in hits]
                if hits:
                    clips = [self.clips[h.term.key] for h in hits]
                    if self.level:
                        clips = [level_matched(c, w.audio) for c in clips]
                    written = self.writer.write(w.audio, [(h.term.written, h.term.heard_as, c) for h, c in zip(hits, clips, strict=True)])
                    text = written
                    if recited(text, listed):
                        text, was_recited = plain, True
                    elif self.guard and not text.strip() and plain.strip():
                        text, guarded = plain, True
            texts.append(text)
            wins.append({"start_s": round(w.audio_from_s, 3), "end_s": round(w.end_s, 3), "shortlist": listed, "plain": plain,
                         "written": written, "recited": was_recited, "guarded": guarded, "final": text})
        return Output(" ".join(t for t in texts if t), extra={"windows": wins, "enroll_s": round(enroll_s, 3),
                                                                 "enrolled": {k: self.heard[k] for k in new}},
                      latency_s=time.perf_counter() - t0 + reused)
