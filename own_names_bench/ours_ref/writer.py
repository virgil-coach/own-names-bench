"""The writer in PyTorch: Qwen3-ASR-1.7B with the v0.3.0 `audio-text-note` LoRA adapter, as in the
adapter repo's inference.py, with the Detail Keeper engine's input building (the taught
recording trimmed of silence, writer.rs) and its guard against an answer that reads the list back
(text.rs `recited`)."""

import re

import numpy as np
import torch

BASE = ("Qwen/Qwen3-ASR-1.7B-hf", "bcd2b5b7f32b480ab5790554cfa8347f246a14f3")
LEAD = "The recording starts with these names said one at a time, in this order"
GAP, LONG_GAP = 4800, 9600
MAX_NEW = 200
RECITED_MOST, RECITED_SHARE = 4, 0.5


def clean(heard: str) -> str:
    return heard.strip().rstrip(".!?,").strip()


def fmt_list(entries: list[tuple[str, str]]) -> str:
    notes = "; ".join(f"{s} (heard as {clean(h)})" for s, h in entries)
    return f"{LEAD}: {notes}. Transcribe only the speech after them."


def _pattern(written: str) -> re.Pattern[str]:
    return re.compile(r"(?<![^\W_])" + re.escape(written) + r"(?![^\W_])", re.IGNORECASE)


def recited(text: str, shortlist: list[str]) -> bool:
    low = text.lower()
    if "(heard as" in low or "these names said" in low or "transcribe only the speech" in low:
        return True
    at, found = 0, 0
    for name in shortlist:
        if not name.strip():
            continue
        m = _pattern(name).search(text, at)
        if m is not None:
            at, found = m.end(), found + 1
    return found >= max(RECITED_MOST, RECITED_SHARE * len(shortlist))


class Writer:
    def __init__(self, device: str, adapter: tuple[str, str, str], dtype: torch.dtype = torch.float32) -> None:
        self.device, self.adapter, self.dtype = device, adapter, dtype

    def load(self) -> None:
        from peft import PeftModel
        from transformers import AutoProcessor, Qwen3ASRForConditionalGeneration

        self.proc = AutoProcessor.from_pretrained(BASE[0], revision=BASE[1])
        model = Qwen3ASRForConditionalGeneration.from_pretrained(BASE[0], revision=BASE[1], dtype=self.dtype).to(self.device)
        repo, revision, folder = self.adapter
        self.model = PeftModel.from_pretrained(model, repo, subfolder=folder, revision=revision).eval()

    @torch.no_grad()
    def _run(self, audio: np.ndarray, prompt: str | None) -> str:
        kwargs = {} if prompt is None else {"prompt": [prompt]}
        inputs = self.proc.apply_transcription_request(audio=[audio], language=["English"], **kwargs).to(self.device, self.model.dtype)
        out = self.model.generate(**inputs, max_new_tokens=MAX_NEW, do_sample=False)
        new = out[0, inputs["input_ids"].shape[1] :]
        text = self.proc.tokenizer.decode(new, skip_special_tokens=True)
        return text.split("<asr_text>")[-1].strip()

    def bare(self, audio: np.ndarray) -> str:
        """The untrained recognizer (adapter switched off): how a taught recording is heard."""
        with self.model.disable_adapter():
            return self._run(audio, None)

    def plain(self, audio: np.ndarray) -> str:
        """The adapted writer with no list."""
        return self._run(audio, None)

    def write(self, audio: np.ndarray, entries: list[tuple[str, str, np.ndarray]]) -> str:
        """entries: (written, heard_as, trimmed taught recording), in shortlist order."""
        parts: list[np.ndarray] = []
        for i, (_, _, clip) in enumerate(entries):
            if i:
                parts.append(np.zeros(GAP, dtype=np.float32))
            parts.append(clip)
        parts += [np.zeros(LONG_GAP, dtype=np.float32), audio]
        return self._run(np.concatenate(parts).astype(np.float32), fmt_list([(w, h) for w, h, _ in entries]))
