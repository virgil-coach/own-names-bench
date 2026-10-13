"""Ours, as shipped: the Detail Keeper engine itself (Rust, MLX, Apple silicon), driven through
its offline batch command `detailkeeper-bench` (services/engine/crates/detailkeeper/src/bin/).
The pipeline is ours_torch's (same window cutter, spotter, writer and guards); the runtime is the
engine's: MLX, the writer merged with the adapter and quantized to 8 bits (audio encoder bf16).

Set DETAILKEEPER_BENCH to the built binary (with mlx.metallib beside it). Recordings are written
once as 16-bit WAV (the engine reads WAV), sample for sample the same as the FLAC."""

import json
import os
import subprocess
import tempfile
from pathlib import Path

import soundfile as sf

from .base import Fit, Output, System, unique
from .ours_torch import ADAPTER, TOP


class OursMlx(System):
    name = "ours-mlx"
    variants = ("none", "own", "all")

    def __init__(self) -> None:
        self.bin = Path(os.environ.get("DETAILKEEPER_BENCH", "detailkeeper-bench"))
        self.wavs = Path(os.environ.get("BENCH_WAV_CACHE", Path(tempfile.gettempdir()) / "own-names-bench-wav"))
        self.cache = self.wavs.parent / "detailkeeper-bench-cache"
        self.proc: subprocess.Popen | None = None
        self.ready: dict = {}

    def config(self) -> dict:
        rev = subprocess.run(["git", "-C", str(self.bin.resolve().parent), "rev-parse", "HEAD"], capture_output=True, text=True,
                             check=False).stdout.strip()
        return {"runtime": "Detail Keeper engine (Rust, MLX), detailkeeper-bench", "engine_commit": rev or "unknown",
                "binary": str(self.bin), "adapter": f"hf://{ADAPTER[0]}@{ADAPTER[1]}/{ADAPTER[2]}", "adapter_version": "v0.3.0",
                "writer": "merged adapter, text decoder affine 8-bit, audio encoder bf16",
                "g2p": "own_names_bench/ours_ref/g2p.json (espeak-ng 1.52.0, every benchmark name)", "shortlist": TOP, "prune": "off",
                "gate": "none", "engine": self.ready,
                "list_feature": "spotter shortlist of the whole list -> writer prompt + taught recordings",
                "fit": "no limit: the spotter ranks every name"}

    def start(self) -> None:
        import shutil

        self.wavs.mkdir(parents=True, exist_ok=True)
        self.cache.mkdir(parents=True, exist_ok=True)
        # the same pronunciations as the reference runner (see ours_ref/spotter.py G2P_TABLE)
        shutil.copyfile(Path(__file__).parent.parent / "ours_ref" / "g2p.json", self.cache / "g2p.json")
        self.proc = subprocess.Popen(
            [str(self.bin), "--adapter", f"hf://{ADAPTER[0]}@{ADAPTER[1]}/{ADAPTER[2]}", "--format", "audio_heard",
             "--cache", str(self.cache)],
            stdin=subprocess.PIPE, stdout=subprocess.PIPE, text=True, bufsize=1)
        assert self.proc.stdout is not None
        line = self.proc.stdout.readline()
        if not line:
            raise RuntimeError("detailkeeper-bench exited before it was ready")
        self.ready = json.loads(line)

    def stop(self) -> None:
        if self.proc is not None:
            assert self.proc.stdin is not None
            self.proc.stdin.close()
            self.proc.wait(timeout=120)
            self.proc = None

    def _wav(self, path: Path, key: str) -> str:
        out = self.wavs / (key.replace("/", "__") + ".wav")
        if not out.exists():
            x, rate = sf.read(path, dtype="int16")
            tmp = out.with_suffix(".tmp.wav")
            sf.write(tmp, x, rate, subtype="PCM_16")
            tmp.replace(out)
        return str(out)

    def fit(self, names: list[str]) -> Fit:
        return Fit(unique(names), "all names (the spotter shortlists ten per window)")

    def transcribe(self, audio: Path, names: list[str], entries: list[dict]) -> Output:
        assert self.proc is not None and self.proc.stdin is not None and self.proc.stdout is not None
        want, seen, terms = set(names), set(), []
        for e in entries:
            if e["written"] in want and e["written"] not in seen:
                seen.add(e["written"])
                terms.append({"key": e["id"], "written": e["written"], "sample": self._wav(e["sample_path"], "enroll/" + e["id"])})
        job = {"id": str(audio), "audio": self._wav(audio, audio.stem), "terms": terms}
        self.proc.stdin.write(json.dumps(job, ensure_ascii=False) + "\n")
        self.proc.stdin.flush()
        line = self.proc.stdout.readline()
        if not line:
            raise RuntimeError("detailkeeper-bench stopped")
        r = json.loads(line)
        # latency is the engine's time for the pass; enrolling names it had not seen is not in it
        return Output(r["text"], extra={"windows": r["windows"], "enrolled": r.get("enrolled", {})}, latency_s=r["seconds"])
