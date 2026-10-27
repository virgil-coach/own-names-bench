"""The benchmark data: a folder with manifest.json and the audio it lists, pinned by revision and
checked file by file against the SHA-256 in the manifest.

From v1.2 the manifest also points at suites (suites/<name>/suite.json): other sources, each in its
own folder under its own licence, with the same shape as the audiobook data (entries, lists, clips,
mentions, name-free items). A suite whose source may not be re-hosted (`rehosted: false`) carries no
audio; `bench fetch` reads it from the source at the pinned revision and cuts it locally, checked
against the PCM hash in the suite.

From v1.3 the dataset also holds the two sealed launch suites, each a dataset folder of its own beside
the v1.2.0 data (run one with `bench --data <dataset>/books13 run ...`): `books13` (held-out audiobooks,
the clips task) and `conv13` (held-out conversation, eight suites). They are published exactly as they
were sealed and scored, so their suite hashes (SEALED_SUITES) recompute from the files."""

import hashlib
import json
import os
from dataclasses import dataclass
from pathlib import Path

from . import DATA_FORMAT

DATASET_REPO = "virgil-coach/own-names-bench"
DATASET_REVISION = "v1.3.0"  # a git tag of the dataset repo; the tag names the benchmark version
# folder -> (the sealed suite's hash: SHA-256 of the sorted '<sha256>  <path>' lines of every file under `under`, under)
SEALED_SUITES = {"books13": ("3d6d8b65d4810c4f9571e8274bf02659a1bb507e65c7d0c333a48145a41e202f", ""),
                 "conv13": ("dbff73e6e5785d0efcf36be582af061b63d59d351cd655ccb6e153ffa850fdd3", "suites")}


def default_dir() -> Path:
    return Path(os.environ.get("OWN_NAMES_BENCH_DATA", Path.cwd() / "data"))


def fetch(dest: Path, revision: str = DATASET_REVISION, use_token: bool = False) -> Path:
    """Downloads the dataset anonymously (no Hugging Face login needed once it is public).
    use_token: send this machine's Hugging Face credentials (before launch, while it is private)."""
    from huggingface_hub import snapshot_download
    from huggingface_hub.errors import GatedRepoError, RepositoryNotFoundError

    try:
        snapshot_download(DATASET_REPO, repo_type="dataset", revision=revision, local_dir=dest, token=None if use_token else False)
    except (RepositoryNotFoundError, GatedRepoError) as e:
        raise SystemExit(f"{DATASET_REPO}@{revision} cannot be read {'with these credentials' if use_token else 'anonymously'}. "
                         "It is public from launch; before that it needs `bench fetch --token` with access to virgil-coach.") from e
    materialize(dest)
    return dest


def materialize(root: Path) -> None:
    """Cuts the audio of suites that are not re-hosted from their source, at the pinned revision."""
    import io

    import numpy as np
    import soundfile as sf

    m = json.loads((root / "manifest.json").read_text(encoding="utf-8"))
    for ref in m.get("suites", []):
        s = json.loads((root / ref["file"]).read_text(encoding="utf-8"))
        if s.get("rehosted", True):
            continue
        want: dict[str, list[tuple[Path, dict]]] = {}
        for c in s["clips"].values():
            want.setdefault(c["remote"]["id"], []).append((root / c["audio"], {"pcm_sha256": c["pcm_sha256"]}))
        for e in s["entries"].values():
            r = e["remote"]
            want.setdefault(r["id"], []).append((root / e["sample"], {"pcm_sha256": e["sample_pcm_sha256"], "start": r["start"], "end": r["end"]}))
        if all(p.is_file() for items in want.values() for p, _ in items):
            continue
        from huggingface_hub import HfApi, hf_hub_download
        import pyarrow.parquet as pq

        repo, rev = s["source"]["repo"], s["source"]["revision"]
        files = [f for f in HfApi().list_repo_files(repo, repo_type="dataset", revision=rev, token=False)
                 if f.startswith("data/") and f.endswith(".parquet")]
        for f in sorted(files):
            t = pq.read_table(hf_hub_download(repo, f, repo_type="dataset", revision=rev, token=False), columns=["id", "audio"])
            for row in t.to_pylist():
                for path, spec in want.get(row["id"], []):
                    x, sr = sf.read(io.BytesIO(row["audio"]["bytes"]), dtype="float32")
                    x = x if x.ndim == 1 else x.mean(axis=1)
                    if "start" in spec:
                        x = x[max(0, int(spec["start"] * sr)) : int(spec["end"] * sr)]
                    pcm = np.clip(np.round(x * 32768.0), -32768, 32767).astype("<i2")
                    if hashlib.sha256(pcm.tobytes()).hexdigest() != spec["pcm_sha256"]:
                        raise SystemExit(f"{path}: the source audio no longer matches the benchmark ({repo}@{rev})")
                    path.parent.mkdir(parents=True, exist_ok=True)
                    sf.write(path, pcm, sr, subtype="PCM_16", format="WAV")
        missing = [str(p) for items in want.values() for p, _ in items if not p.is_file()]
        if missing:
            raise SystemExit(f"{ref['name']}: {len(missing)} clips not found in {repo}@{rev}, e.g. {missing[:2]}")


def sealed_suite_hash(folder: Path) -> str:
    """The suite hash a sealed suite was sealed with: SHA-256 of the sorted '<sha256>  <relative path>' lines of every file."""
    lines = sorted(f"{_sha256(p)}  {p.relative_to(folder).as_posix()}\n" for p in folder.rglob("*") if p.is_file())
    return hashlib.sha256("".join(lines).encode()).hexdigest()


def check_sealed(root: Path) -> dict[str, str]:
    """Each sealed suite of the dataset: its files against the hash it was sealed with."""
    out = {}
    for name, (want, under) in SEALED_SUITES.items():
        folder = root / name / under if under else root / name
        if not folder.is_dir():
            raise SystemExit(f"{folder}: missing; run `bench fetch`")
        got = sealed_suite_hash(folder)
        if got != want:
            raise SystemExit(f"{folder}: suite hash {got}, sealed as {want}; run `bench fetch`")
        load(root / name)
        out[name] = got
    return out


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
    name: str = ""          # "" for the audiobooks (the top level), else the suite's name
    licence: str = ""
    suites: dict = None     # type: ignore[assignment]

    @property
    def prefix(self) -> str:
        """Pass ids of a suite start with suite/<name>/."""
        return f"suite/{self.name}/" if self.name else ""

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


def load(root: Path, verify: bool = True, samples: bool = True) -> Bench:
    """samples=False: the taught recordings need not be on disk (clips are still checked)."""
    m = json.loads((root / "manifest.json").read_text(encoding="utf-8"))
    if m["version"] != DATA_FORMAT:
        raise SystemExit(f"{root}: data format {m['version']}, this code reads data format {DATA_FORMAT}")
    if verify:
        bad = [rel for rel, digest in m["files"].items() if not (root / rel).is_file() or _sha256(root / rel) != digest]
        if bad:
            raise SystemExit(f"{root}: {len(bad)} files missing or changed, e.g. {bad[:3]}; run `bench fetch`")
    suites = {}
    for ref in m.get("suites", []):
        f = root / ref["file"]
        if _sha256(f) != ref["sha256"]:
            raise SystemExit(f"{f}: changed; run `bench fetch`")
        s = json.loads(f.read_text(encoding="utf-8"))
        sm = {"entries": s["entries"], "lists": s["lists"], "clips": s["clips"], "mentions": s["mentions"],
              "name_free": s["name_free"], "chapters": [], "name_words": s["name_words"], "not_names": s.get("not_names", [])}
        if verify:
            bad = []
            for c in s["clips"].values():
                p = root / c["audio"]
                if not p.is_file() or ("sha256" in c and _sha256(p) != c["sha256"]):
                    bad.append(c["audio"])
            for e in (s["entries"].values() if samples else ()):
                p = root / e["sample"]
                if not p.is_file() or ("sample_sha256" in e and _sha256(p) != e["sample_sha256"]):
                    bad.append(e["sample"])
            if bad:
                raise SystemExit(f"{ref['name']}: {len(bad)} files missing or changed, e.g. {bad[:3]}; run `bench fetch`")
        suites[ref["name"]] = Bench(root, sm, name=ref["name"], licence=s["licence"])
    return Bench(root, m, suites=suites)


FINGERPRINT_KEYS = ("files", "entries", "lists", "clips", "mentions", "name_free", "chapters", "name_words")


def dataset_fingerprint(b: "Bench") -> str:
    """What the benchmark is, independent of its version label and descriptive fields: the audio
    hashes, names, lists, references, mentions and chapters."""
    blob = json.dumps({k: b.m[k] for k in FINGERPRINT_KEYS}, sort_keys=True, ensure_ascii=False)
    return hashlib.sha256(blob.encode()).hexdigest()[:16]


def suite_fingerprints(b: "Bench") -> dict[str, str]:
    out = {}
    for name, s in (b.suites or {}).items():
        blob = json.dumps({k: s.m[k] for k in ("entries", "lists", "clips", "mentions", "name_free", "name_words")}, sort_keys=True,
                          ensure_ascii=False)
        out[name] = hashlib.sha256(blob.encode()).hexdigest()[:16]
    return out


def manifest_sha256(root: Path) -> str:
    return _sha256(root / "manifest.json")
