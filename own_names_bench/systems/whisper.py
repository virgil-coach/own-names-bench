"""OpenAI Whisper large-v3 (Hugging Face transformers), names as the initial prompt.

The prompt is the names joined by ", " (as OpenAI's prompting guide suggests for spellings).
Whisper keeps at most 223 prompt tokens (half its 448-token context, less one); the list is
fitted to that with Whisper's own tokenizer, most frequent names first. Greedy decoding,
English, no temperature fallback. Recordings over 30 s (chapters) use transformers' sequential
long-form decoding with the prompt given to every 30-second segment."""

import os
from pathlib import Path

import numpy as np

from .base import Fit, Output, System, unique
from .ours_torch import read16k

MODEL = ("openai/whisper-large-v3", "06f233fe06e710322aca913c1bc4249a0d71fce1")
PROMPT_TOKENS = 223


class Whisper(System):
    name = "whisper"
    variants = ("none", "own")

    def __init__(self) -> None:
        import torch

        self.device = os.environ.get("BENCH_DEVICE") or ("cuda" if torch.cuda.is_available() else "cpu")
        self.dtype = torch.float16 if self.device == "cuda" else torch.float32
        from transformers import WhisperTokenizer

        self.tok = WhisperTokenizer.from_pretrained(MODEL[0], revision=MODEL[1])

    def config(self) -> dict:
        import torch
        import transformers

        return {"model": f"{MODEL[0]}@{MODEL[1]}", "runtime": f"transformers {transformers.__version__}, torch {torch.__version__}",
                "device": self.device, "dtype": str(self.dtype).removeprefix("torch."), "decoding": "greedy, language en, task transcribe",
                "long_form": "sequential, condition_on_prev_tokens=True, prompt_condition_type=all-segments (the names before every 30 s segment)",
                "list_feature": "prompt_ids (initial prompt): names joined by ', '",
                "limits": f"{PROMPT_TOKENS} prompt tokens", "fit": "longest prefix of the list (most frequent first) within the token limit"}

    def start(self) -> None:
        from transformers import WhisperForConditionalGeneration, WhisperProcessor

        self.proc = WhisperProcessor.from_pretrained(MODEL[0], revision=MODEL[1])
        self.model = WhisperForConditionalGeneration.from_pretrained(MODEL[0], revision=MODEL[1], dtype=self.dtype).to(self.device).eval()

    def _prompt(self, names: list[str]) -> str:
        return ", ".join(names)

    def fit(self, names: list[str]) -> Fit:
        names = unique(names)
        lo, hi = 0, len(names)
        while lo < hi:  # longest prefix that fits
            mid = (lo + hi + 1) // 2
            if len(self.tok.encode(" " + self._prompt(names[:mid]), add_special_tokens=False)) <= PROMPT_TOKENS:
                lo = mid
            else:
                hi = mid - 1
        return Fit(names[:lo], f"{lo} of {len(names)} names in {PROMPT_TOKENS} tokens", names[lo:])

    def transcribe(self, audio: Path, names: list[str], entries: list[dict]) -> Output:
        import torch

        x = read16k(audio)
        long = len(x) > 30 * 16000
        # long-form decoding conditions each 30 s segment on the text before it (OpenAI's default,
        # and what transformers requires for a prompt on every segment); short clips are one segment
        kw: dict = {"language": "en", "task": "transcribe", "num_beams": 1, "do_sample": False, "condition_on_prev_tokens": long}
        if names:
            kw["prompt_ids"] = torch.tensor(self.proc.get_prompt_ids(self._prompt(names)), device=self.device)
            if long:
                kw["prompt_condition_type"] = "all-segments"
        if long:
            feats = self.proc(x, sampling_rate=16000, return_tensors="pt", truncation=False, padding="longest", return_attention_mask=True)
            kw["return_timestamps"] = True
        else:
            feats = self.proc(x, sampling_rate=16000, return_tensors="pt", return_attention_mask=True)
        inputs = {k: v.to(self.device) for k, v in feats.items()}
        inputs["input_features"] = inputs["input_features"].to(self.dtype)
        with torch.inference_mode():
            ids = self.model.generate(**inputs, **kw)
        seq = ids if isinstance(ids, torch.Tensor) else ids["sequences"]
        text = self.proc.batch_decode(seq, skip_special_tokens=True)[0]
        if names:  # the prompt is decoded with the answer by some versions; keep only the answer
            p = self._prompt(names)
            text = text.split(p, 1)[1] if p in text else text
        return Output(text.strip())


_ = np  # numpy is imported for read16k's return type
