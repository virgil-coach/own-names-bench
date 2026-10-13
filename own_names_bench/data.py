"""The benchmark data: a folder with manifest.json and the audio it lists, pinned by revision and
checked file by file against the SHA-256 in the manifest."""

import hashlib
import json
import os
from dataclasses import dataclass
from pathlib import Path

from . import BENCH_VERSION

DATASET_REPO = "virgil-coach/own-names-bench"
DATASET_REVISION = "v1.0.0"  # a git tag of the dataset repo; the tag names the benchmark version


def default_dir() -> Path:
    return Path(os.environ.get("OWN_NAMES_BENCH_DATA", Path.cwd() / "data"))


def fetch(dest: Path, revision: str = DATASET_REVISION) -> Path:
    from huggingface_hub import snapshot_download

    snapshot_download(DATASET_REPO, repo_type="dataset", revision=revision, local_dir=dest)
    return dest


def _sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


@dataclass
class Bench:
    root: Path
    m: dict

    @property
    def entries(self) -> dict[str, dict]:
        return self.m["entries"]

    @property
    def lists(self) -> dict[str, dict]:
        return self.m["lists"]

    @property
    def clips(self) -> dict[str, dict]:
        return self.m["clips"]

    def path(self, rel: str) -> Path:
        return self.root / rel

    def written(self, ids: list[str]) -> list[str]:
        return [self.entries[i]["written"] for i in ids]


def load(root: Path, verify: bool = True) -> Bench:
    m = json.loads((root / "manifest.json").read_text(encoding="utf-8"))
    if m["version"] != BENCH_VERSION:
        raise SystemExit(f"{root}: dataset version {m['version']}, this code is benchmark version {BENCH_VERSION}")
    if verify:
        bad = [rel for rel, digest in m["files"].items() if not (root / rel).is_file() or _sha256(root / rel) != digest]
        if bad:
            raise SystemExit(f"{root}: {len(bad)} files missing or changed, e.g. {bad[:3]}; run `bench fetch`")
    return Bench(root, m)


def manifest_sha256(root: Path) -> str:
    return _sha256(root / "manifest.json")
