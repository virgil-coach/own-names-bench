"""Diagnosis only (local branch diag/v12-conversation, not part of the published benchmark).

Ours (ours_torch.OursTorch) with one part of the pipeline changed at a time, and every window's
texts recorded so a pass can be taken apart afterwards:

  ours-trace            ours as published (shortlist 10, Segmenter windows, taught prompt), plus a
                        per-window record of the no-list text, the list answer and the final text
  ours-top40            shortlist 40: every name of a 40-name suite list goes to the writer
                        (audiobook lists of over 40 names: the spotter's 40 best)
  ours-wholeclip        qwen-context's window cutter: the recording whole when it is 30 s or
                        shorter, otherwise the Segmenter's windows
  ours-adapter-context  the adapter with qwen-context's prompt (names joined by ", "), no taught
                        recordings, no spotter, qwen-context's window cutter
  ours-level            ours with every taught recording scaled to the window's speech level before
                        the writer hears them (the far-field question: e2)
"""

import hashlib
import time
from pathlib import Path

import numpy as np

from ..ours_ref import segmenter
from .base import Output
from .ours_torch import CACHE_WINDOWS, OursTorch, read16k

WHOLE_S = 30.0


def qwen_cutter(x: np.ndarray) -> list[tuple[float, float, np.ndarray]]:
    if len(x) <= WHOLE_S * 16000:
        return [(0.0, len(x) / 16000, x)]
    return [(w.audio_from_s, w.end_s, w.audio) for w in segmenter.windows(x)]


def seg_cutter(x: np.ndarray) -> list[tuple[float, float, np.ndarray]]:
    return [(w.audio_from_s, w.end_s, w.audio) for w in segmenter.windows(x)]


def speech_rms(x: np.ndarray, frame: int = 320) -> float:
    """RMS over the louder half of 20 ms frames (the speech, not the pauses)."""
    n = len(x) // frame
    if n == 0:
        return float(np.sqrt(np.mean(x**2) + 1e-12))
    e = np.sqrt((x[: n * frame].reshape(n, frame) ** 2).mean(axis=1))
    loud = e[e >= np.median(e)]
    return float(np.sqrt(np.mean(loud**2)) + 1e-9)


class OursAblate(OursTorch):
    def __init__(self, name: str, top: int = 10, cutter: str = "segmenter", prompt: str = "taught", level: bool = False,
                 variants: tuple[str, ...] = ("none", "own")) -> None:
        super().__init__()
        self.name, self.top, self.cutter, self.prompt, self.level = name, top, cutter, prompt, level
        self.variants = variants

    def config(self) -> dict:
        c = super().config()
        c.update({"ablation": self.name, "shortlist": self.top if self.prompt == "taught" else "none (every name, as text)",
                  "windows": {"segmenter": c["windows"], "qwen": "qwen-context's cutter: whole when <= 30 s, else the Detail Keeper Segmenter"}[self.cutter],
                  "prompt": {"taught": "the adapter's taught prompt (spelling, heard-as, taught recording)",
                             "context": "qwen-context's prompt: names joined by ', ' (no recordings, no spotter)"}[self.prompt],
                  "level": "taught recordings scaled to the window's speech RMS" if self.level else "off",
                  "trace": "per-window plain / written / final text in extra.windows"})
        if self.prompt == "context":
            c["list_feature"] = "adapter + text context: names joined by ', '"
            c["fit"] = "all names"
        return c

    def start(self) -> None:
        if self.prompt == "context":
            import torch

            from ..ours_ref.writer import Writer
            from .ours_torch import ADAPTER

            torch.manual_seed(0)
            self.writer = Writer(self.device, ADAPTER)
            self.writer.load()
            return
        super().start()

    def transcribe(self, audio: Path, names: list[str], entries: list[dict]) -> Output:
        from ..ours_ref.writer import recited

        x = read16k(audio)
        cut = qwen_cutter if self.cutter == "qwen" else seg_cutter
        t0 = time.perf_counter()
        if self.prompt == "context":
            prompt = ", ".join(names) if names else None
            texts, wins = [], []
            for a, e, w in cut(x):
                text = self.writer._run(w, prompt)
                texts.append(text)
                wins.append({"start_s": round(a, 3), "end_s": round(e, 3), "final": text})
            return Output(" ".join(t for t in texts if t), extra={"windows": wins}, latency_s=time.perf_counter() - t0)

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
        for a, e, w in cut(x):
            key = hashlib.sha1(w.tobytes()).hexdigest()
            cached = self.plain_cache.get(key)
            if cached is None:
                t = time.perf_counter()
                cached = (self.writer.plain(w), time.perf_counter() - t)
                self.plain_cache[key] = cached
                if len(self.plain_cache) > CACHE_WINDOWS:
                    self.plain_cache.popitem(last=False)
            else:
                reused += cached[1]
            plain = cached[0]
            text, written, was_recited = plain, None, False
            listed: list[str] = []
            if terms:
                hits = self.spotter.rank(terms, w, plain, self.top)
                reused += self.spotter.reused_s
                listed = [h.term.written for h in hits]
                if hits:
                    gain = 1.0
                    if self.level:
                        gain = speech_rms(w)
                    clips = []
                    for h in hits:
                        c = self.clips[h.term.key]
                        clips.append((c * (gain / speech_rms(c))).astype(np.float32) if self.level else c)
                    written = self.writer.write(w, [(h.term.written, h.term.heard_as, c) for h, c in zip(hits, clips)])
                    text = written
                    if recited(text, listed):
                        text, was_recited = plain, True
            texts.append(text)
            wins.append({"start_s": round(a, 3), "end_s": round(e, 3), "shortlist": listed, "plain": plain, "written": written,
                         "recited": was_recited, "final": text})
        return Output(" ".join(t for t in texts if t), extra={"windows": wins, "enroll_s": round(enroll_s, 3),
                                                                 "enrolled": {k: self.heard[k] for k in new}},
                      latency_s=time.perf_counter() - t0 + reused)
