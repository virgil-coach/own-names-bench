"""Ours, reference runner (PyTorch, any machine): Detail Keeper's pipeline over each recording.

Every recording is cut into windows by the engine's own cutter (ours_ref/segmenter.py). For each
window: the adapted writer with no list writes it once; the spotter ranks the whole name list
against the window (its letter score reads that text) and keeps its ten best; the writer writes
the window again with those ten (spelling, how the untrained recognizer heard the taught
recording, and the recording itself). An answer that reads the list back is replaced by the
no-list text. The window texts, in order, are the transcript. With no list, the no-list text is
the transcript. Pruning is off and there is no gate, as in the app's configuration
(detailkeeper config.toml, 2026-10-12).

Every name has one taught recording: the benchmark's enrollment cut (the reader saying the name
once, from another place in the book). The other systems get the spelling only, which is all
their custom-vocabulary features take.
"""

import hashlib
import os
import platform
import time
from collections import OrderedDict
from pathlib import Path

import numpy as np
import soundfile as sf

from ..ours_ref import segmenter
from .base import Fit, Output, System, unique

# v0.3.0, public release (adapter_model.safetensors SHA-256 67dbabef..., the same bytes as the
# private littlebearlabs/own-names-qwen3-asr-lora@8ab4e83a it was developed against)
ADAPTER = ("virgil-coach/own-names-qwen3-asr", "e02efd5e0db0f357f7ada3caf18e1ca293528098", "audio-text-note")
ADAPTER_SHA256 = "67dbabef14851e89ad1b62d509e595713d4a2b6254fbc26cdb700fca1e097f55"
TOP = 10
# The no-list text and the spotter's acoustic features of a window do not depend on the list, and
# every list variant of a recording is run back to back: they are worked out once per window and
# reused (results are identical; latency adds back the time they first took).
CACHE_WINDOWS = 512


def read16k(path: Path) -> np.ndarray:
    x, rate = sf.read(path, dtype="float32")
    if rate != 16000:
        raise ValueError(f"{path}: {rate} Hz, expected 16000")
    return x if x.ndim == 1 else x.mean(axis=1)


class OursTorch(System):
    name = "ours"
    variants = ("none", "own", "all")

    def __init__(self) -> None:
        import torch

        self.device = os.environ.get("BENCH_DEVICE") or ("cuda" if torch.cuda.is_available() else "cpu")
        self.heard: dict[str, str] = {}
        self.plain_cache: OrderedDict[str, tuple[str, float]] = OrderedDict()
        self.clips: dict[str, np.ndarray] = {}

    def config(self) -> dict:
        import torch
        import transformers

        from ..ours_ref import spotter, writer

        return {"runtime": "PyTorch reference (own_names_bench/ours_ref)", "device": self.device,
                "torch": torch.__version__, "transformers": transformers.__version__,
                "cuda_device": torch.cuda.get_device_name(0) if self.device == "cuda" else None,
                "base": f"{writer.BASE[0]}@{writer.BASE[1]}", "adapter": f"{ADAPTER[0]}@{ADAPTER[1]}/{ADAPTER[2]}",
                "adapter_version": "v0.3.0", "adapter_sha256": ADAPTER_SHA256, "dtype": "float32", "decoding": "greedy, at most 200 new tokens",
                "spotter_phon": f"{spotter.PHON[0]}@{spotter.PHON[1]}", "spotter_wavlm": f"{spotter.WAVLM[0]}@{spotter.WAVLM[1]}",
                "g2p": "own_names_bench/ours_ref/g2p.json (espeak-ng 1.52.0, every benchmark name)", "shortlist": TOP, "prune": "off", "gate": "none",
                "windows": "Detail Keeper Segmenter (pause 0.45 s after 2 s, cap 8 s), fed 0.1 s at a time",
                "list_feature": "spotter shortlist of the whole list -> writer prompt + taught recordings",
                "fit": "no limit: the spotter ranks every name", "platform": platform.platform()}

    def start(self) -> None:
        import torch

        from ..ours_ref.spotter import Spotter
        from ..ours_ref.writer import Writer

        torch.manual_seed(0)
        self.writer = Writer(self.device, ADAPTER)
        self.writer.load()
        self.spotter = Spotter(self.device)
        self.spotter.load()

    def fit(self, names: list[str]) -> Fit:
        return Fit(unique(names), "all names (the spotter shortlists ten per window)")

    def _term(self, e: dict):
        from ..ours_ref.spotter import Term, trim

        key = e["id"]
        if key not in self.heard:
            wav = read16k(e["sample_path"])
            self.heard[key] = self.writer.bare(wav)
            self.spotter.learn(key, wav)
            self.clips[key] = trim(wav)
        return Term(key, e["written"], self.heard[key])

    def transcribe(self, audio: Path, names: list[str], entries: list[dict]) -> Output:
        from ..ours_ref.writer import recited

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
        x = read16k(audio)
        texts, wins = [], []
        reused = 0.0  # seconds of list-independent work taken from the cache, as first measured
        for w in segmenter.windows(x):
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
            text = plain
            listed: list[str] = []
            if terms:
                hits = self.spotter.rank(terms, w.audio, plain, TOP)
                reused += self.spotter.reused_s
                listed = [h.term.written for h in hits]
                if hits:
                    text = self.writer.write(w.audio, [(h.term.written, h.term.heard_as, self.clips[h.term.key]) for h in hits])
                    if recited(text, listed):
                        text = plain
            texts.append(text)
            wins.append({"start_s": round(w.audio_from_s, 3), "end_s": round(w.end_s, 3), "shortlist": listed})
        # latency is the whole pass as if nothing were cached (cached work counts at its first-measured
        # time); teaching names (the first time a name is seen) is reported apart
        return Output(" ".join(t for t in texts if t), extra={"windows": wins, "enroll_s": round(enroll_s, 3),
                                                                 "enrolled": {k: self.heard[k] for k in new}},
                      latency_s=time.perf_counter() - t0 + reused)
