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

  name_guard  in a window with little speech, a listed name written that the no-list text does not hold, that the
              no-list text has nothing like and whose recording does not match the audio, gives the window the no-list
              text (ours_ref/guard.py; detailkeeper engine/name-guard guard.rs)

`ours-guard` is `ours-fixed` with the name guard.

  reread  a window with under 4 s of speech is written once more with up to 4 s of the recording either side and the
          shortlists of what that touches, keeping its part of the answer (ours_ref/reread.py; detailkeeper main
          ffc673a session.rs `reread`, detailkeeper-bench)

`ours-reread` is `ours-guard` with the re-read (the adapter: v0.3.0, or OURS_ADAPTER).
"""

import hashlib
import time

import numpy as np

from ..ours_ref import guard as guard_rule
from ..ours_ref import reread as reread_rule
from ..ours_ref import segmenter
from .base import Output
from .ours_torch import CACHE_WINDOWS, TOP, OursTorch, read16k

# set on the dev sets (diag/dev.py), never on benchmark items
MIN_SPEECH_S = 4.0
HOLD_S = 1.0


class OursFixed(OursTorch):
    def __init__(self, name: str = "ours-fixed", guard: bool = True, level: bool = True, min_speech_s: float = MIN_SPEECH_S,
                 hold_s: float = HOLD_S, variants: tuple[str, ...] = ("none", "own"), name_guard: bool = False,
                 reread: bool = False) -> None:
        super().__init__()
        self.name, self.guard, self.level, self.min_speech_s, self.hold_s = name, guard, level, min_speech_s, hold_s
        self.name_guard, self.reread = name_guard, reread
        self.variants = variants

    def config(self) -> dict:
        c = super().config()
        c.update({"fixes": {"guard": "an empty list answer gets the no-list text" if self.guard else "off",
                            "level": "taught recordings scaled to the window's speech RMS (louder half of 20 ms frames)" if self.level else "off",
                            "short": (f"a pause cuts a window with under {self.min_speech_s} s of speech only after {self.hold_s} s of quiet"
                                      if self.min_speech_s > 0 else "off"),
                          "name_guard": (f"under {guard_rule.SHORT_SPEECH_S} s of speech, a written listed name the no-list text lacks, "
                                         f"letter agreement < {guard_rule.AGREES_AT} and recording match (emb) < {guard_rule.SOUNDS_AT}: "
                                         "the no-list text" if self.name_guard else "off"),
                          "reread": (f"a window with under {reread_rule.REREAD_BELOW_S} s of speech and a neighbour is written again with up to "
                                     f"{reread_rule.REREAD_CONTEXT_S} s either side ({reread_rule.REREAD_MOST_S} s at most) and the merged "
                                     "shortlists, keeping its part of the answer" if self.reread else "off")},
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
        windows = list(segmenter.windows(x, self.min_speech_s, self.hold_s))
        all_hits: list[list] = []
        for w in windows:
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
            unverified: str | None = None
            listed: list[str] = []
            hits = []
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
                    elif self.name_guard and (h := guard_rule.unverified(text, plain, hits, w.audio)) is not None:
                        text, unverified = plain, h.term.written
            texts.append(text)
            all_hits.append(hits)
            wins.append({"start_s": round(w.audio_from_s, 3), "end_s": round(w.end_s, 3), "shortlist": listed, "plain": plain,
                         "written": written, "recited": was_recited, "guarded": guarded, "unverified": unverified,
                         "final": text})
        if self.reread:
            texts = self._reread(x, windows, all_hits, texts, wins)
        return Output(" ".join(t for t in texts if t), extra={"windows": wins, "enroll_s": round(enroll_s, 3),
                                                                 "enrolled": {k: self.heard[k] for k in new}},
                      latency_s=time.perf_counter() - t0 + reused)

    def _reread(self, x: np.ndarray, windows: list, all_hits: list[list], firsts: list[str], wins: list[dict]) -> list[str]:
        """Each short window with a neighbour written once more with what is around it, in order (what was settled
        before it is its context). detailkeeper-bench's loop, line for line."""
        from ..ours_ref.writer import level_matched, recited

        total_s = len(x) / 16000
        settled: list[str] = []
        for k, w in enumerate(windows):
            text = firsts[k]
            if guard_rule.speech_s(w.audio) < reread_rule.REREAD_BELOW_S:
                ctx = reread_rule.context_s(w.audio_from_s, w.end_s)
                from_s, to_s = max(0.0, w.audio_from_s - ctx), min(total_s, w.end_s + ctx)
                before_in = k > 0 and windows[k - 1].end_s > from_s
                after_in = k + 1 < len(windows) and to_s > w.end_s + 0.05
                merged = [h for o, hs in zip(windows, all_hits, strict=True) if o.end_s > from_s and o.audio_from_s < to_s for h in hs]
                merged.sort(key=lambda h: -h.score)  # stable, as Rust's sort_by
                seen: set[str] = set()
                merged = [h for h in merged if not (h.term.key in seen or seen.add(h.term.key))][:TOP]
                trace: dict = {"span": [round(from_s, 3), round(to_s, 3)], "before_in": before_in, "after_in": after_in}
                if (before_in or after_in) and merged:
                    span = x[int(from_s * 16000):min(int(to_s * 16000), len(x))]
                    names = [h.term.written for h in merged]
                    clips = [self.clips[h.term.key] for h in merged]
                    if self.level:
                        clips = [level_matched(c, span) for c in clips]
                    again = self.writer.write(span, [(h.term.written, h.term.heard_as, c) for h, c in zip(merged, clips, strict=True)])
                    trace.update({"list": names, "answer": again})
                    if not recited(again, names) and again.strip():
                        before = settled[k - 1] if before_in else ""
                        after = firsts[k + 1] if after_in else ""
                        own = reread_rule.extract(again, before, text, after)
                        if own is not None:
                            text = own
                            trace["used"] = True
                wins[k]["reread"] = trace
                wins[k]["settled"] = text
            settled.append(text)
        return settled
