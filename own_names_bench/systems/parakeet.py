"""NVIDIA Parakeet TDT 0.6B v2 (NeMo), the English Parakeet with the best Open ASR Leaderboard
average, names through NeMo's GPU phrase boosting (GPU-PB, `boosting_tree` in greedy decoding,
NeMo's documented word-boosting feature for CTC/RNN-T/TDT models).

Greedy (label-looping) decoding. Recordings longer than 20 minutes use the model card's
long-audio setting (local attention, 256 frames each side). The boosting weight is NeMo's
documented default; it was not tuned on this benchmark."""

import os
from pathlib import Path

from .base import Fit, Output, System, unique
from .ours_torch import read16k

MODEL = ("nvidia/parakeet-tdt-0.6b-v2", "ae9ad07059c7c739ffaf932226a8fe64ae2620b0", "parakeet-tdt-0.6b-v2.nemo")
LONG_S = 20 * 60


class Parakeet(System):
    name = "parakeet"
    variants = ("none", "own", "all")

    def __init__(self) -> None:
        import torch

        self.device = os.environ.get("BENCH_DEVICE") or ("cuda" if torch.cuda.is_available() else "cpu")
        self.current: tuple[str, ...] | None = None
        self.local = False

    def config(self) -> dict:
        import nemo
        import torch

        return {"model": f"{MODEL[0]}@{MODEL[1]}", "runtime": f"NeMo {nemo.__version__}, torch {torch.__version__}", "device": self.device,
                "decoding": "greedy_batch (TDT label looping)", "long_form": f"over {LONG_S // 60} min: rel_pos_local_attn [256, 256]",
                "list_feature": "GPU phrase boosting: decoding.greedy.boosting_tree.key_phrases_list",
                "boosting": getattr(self, "boost_cfg", None), "fit": "all names"}

    def start(self) -> None:
        from huggingface_hub import hf_hub_download
        from nemo.collections.asr.models import ASRModel

        path = hf_hub_download(MODEL[0], MODEL[2], revision=MODEL[1])
        self.model = ASRModel.restore_from(path, map_location=self.device).eval()
        self.base_cfg = self.model.cfg.decoding
        self._decoding(())

    def _decoding(self, names: tuple[str, ...]) -> None:
        if names == self.current:
            return
        from copy import deepcopy

        from omegaconf import open_dict

        cfg = deepcopy(self.base_cfg)
        with open_dict(cfg):
            cfg.strategy = "greedy_batch"
            if names:
                cfg.greedy.boosting_tree.key_phrases_list = list(names)
                self.boost_cfg = {k: v for k, v in dict(cfg.greedy.boosting_tree).items() if k != "key_phrases_list"}
                self.boost_cfg["boosting_tree_alpha"] = cfg.greedy.get("boosting_tree_alpha")
            else:
                cfg.greedy.boosting_tree.key_phrases_list = None
        self.model.change_decoding_strategy(cfg, verbose=False)
        self.current = names

    def fit(self, names: list[str]) -> Fit:
        return Fit(unique(names), "all names")

    def transcribe(self, audio: Path, names: list[str], entries: list[dict]) -> Output:
        import torch

        x = read16k(audio)
        long = len(x) > LONG_S * 16000
        if long != self.local:
            if long:
                self.model.change_attention_model("rel_pos_local_attn", [256, 256])
                self.model.change_subsampling_conv_chunking_factor(1)
            else:
                self.model.change_attention_model("rel_pos")
                self.model.change_subsampling_conv_chunking_factor(-1)
            self.local = long
        self._decoding(tuple(names))
        with torch.inference_mode():
            out = self.model.transcribe([x], batch_size=1, verbose=False)
        h = out[0] if isinstance(out, list) else out[0][0]
        return Output(getattr(h, "text", h))
