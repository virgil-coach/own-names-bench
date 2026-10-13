"""Plain Qwen3-ASR-1.7B (Hugging Face transformers), no adapter.

`qwen`          no list: the recognizer our writer is built on, as it comes.
`qwen-context`  the names as its text context: Qwen3-ASR's documented way to bias recognition
                (the context goes in the system prompt), names joined by ", ".

Clips go whole. Chapters (longer than the model's audio window is meant for) are cut by the same
window cutter as ours (ours_ref/segmenter.py) and the window texts joined. Greedy, English, at
most 200 new tokens per window, float32."""

import os
from pathlib import Path

from ..ours_ref import segmenter
from .base import Fit, Output, System, unique
from .ours_torch import read16k

BASE = ("Qwen/Qwen3-ASR-1.7B-hf", "bcd2b5b7f32b480ab5790554cfa8347f246a14f3")
MAX_NEW = 200


class PlainQwen(System):
    def __init__(self, context: bool) -> None:
        import torch

        self.context = context
        self.name = "qwen-context" if context else "qwen"
        self.variants = ("none", "own", "all") if context else ("none",)
        self.device = os.environ.get("BENCH_DEVICE") or ("cuda" if torch.cuda.is_available() else "cpu")

    def config(self) -> dict:
        import torch
        import transformers

        return {"model": f"{BASE[0]}@{BASE[1]}", "runtime": f"transformers {transformers.__version__}, torch {torch.__version__}",
                "device": self.device, "dtype": "float32", "decoding": "greedy, language English, at most 200 new tokens",
                "long_form": "chapters cut by the Detail Keeper window cutter",
                "list_feature": "context (system prompt): names joined by ', '" if self.context else "none",
                "fit": "all names" if self.context else "no list"}

    def start(self) -> None:
        import torch
        from transformers import AutoProcessor, Qwen3ASRForConditionalGeneration

        self.proc = AutoProcessor.from_pretrained(BASE[0], revision=BASE[1])
        self.model = Qwen3ASRForConditionalGeneration.from_pretrained(BASE[0], revision=BASE[1], dtype=torch.float32).to(self.device).eval()

    def fit(self, names: list[str]) -> Fit:
        return Fit(unique(names) if self.context else [], "all names" if self.context else "no list")

    def _one(self, x, prompt: str | None) -> str:
        import torch

        kwargs = {} if prompt is None else {"prompt": [prompt]}
        inputs = self.proc.apply_transcription_request(audio=[x], language=["English"], **kwargs).to(self.device, self.model.dtype)
        with torch.inference_mode():
            out = self.model.generate(**inputs, max_new_tokens=MAX_NEW, do_sample=False)
        text = self.proc.tokenizer.decode(out[0, inputs["input_ids"].shape[1] :], skip_special_tokens=True)
        return text.split("<asr_text>")[-1].strip()

    def transcribe(self, audio: Path, names: list[str], entries: list[dict]) -> Output:
        x = read16k(audio)
        prompt = ", ".join(names) if names else None
        if len(x) <= 30 * 16000:
            return Output(self._one(x, prompt))
        return Output(" ".join(t for t in (self._one(w.audio, prompt) for w in segmenter.windows(x)) if t))
