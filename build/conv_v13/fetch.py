#!/usr/bin/env python3
"""Downloads the test splits for the v1.3 conversation test suite into $ONB_SEALED/build/src: VoxPopuli en test,
LibriTTS-R test-clean and test-other, the FSD50K clips of fsd_test.json (all Hugging Face files pinned to the commit
in common.SOURCES) and LibriSpeech's speaker and chapter tables (openslr 12, recorded by URL and SHA-256).

Not fetched, and why (README.md): FLEURS (every en_us split, test included, is in the dev data), NOTSOFAR-1 (every
eval meeting not in dev has a participant who is in a dev meeting; the dev_set meetings are train meetings),
Common Voice, EdAcc and DailyTalk (licence), AMI, ICSI, Earnings-21 and the other own-names-bench v1.2 / reserved
v1.3 sources.

usage: fetch.py [voxpopuli libritts fsd meta]  (default: all)  -> build/src/<source>/..., build/src/fetched.json
"""
import hashlib
import json
import subprocess
import sys
import tarfile
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from common import SOURCES, WORK, log

SRC = WORK / "src"
HERE = Path(__file__).resolve().parent


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1 << 22), b""):
            h.update(block)
    return h.hexdigest()


def hf(dest: str, files: list[str]) -> dict[str, str]:
    """Files of a Hugging Face dataset at the pinned revision, by plain HTTPS; {file: sha256 of what was fetched}."""
    repo, rev = SOURCES[dest]["repo"], SOURCES[dest]["revision"]

    def one(f: str) -> tuple[str, str]:
        path = SRC / dest / f
        if not path.exists():
            path.parent.mkdir(parents=True, exist_ok=True)
            part = path.with_name(path.name + ".part")
            url = f"https://huggingface.co/datasets/{repo}/resolve/{rev}/{f}"
            subprocess.run(["curl", "-sSfL", "--retry", "8", "--retry-all-errors", "-o", str(part), url], check=True)
            part.rename(path)
        return f, sha256(path)

    with ThreadPoolExecutor(8) as pool:
        out = dict(pool.map(one, files))
    log(f"{dest}: {len(out)} files")
    return out


MIRRORS = ("https://openslr.elda.org", "https://www.openslr.org", "https://openslr.trmal.net")


def openslr(path: str, dest: Path) -> dict:
    dest.parent.mkdir(parents=True, exist_ok=True)
    url = ""
    if not dest.exists():
        part = dest.with_suffix(".part")
        for m in MIRRORS:
            url = m + path
            if subprocess.run(["curl", "-sSfL", "--retry", "4", "--retry-all-errors", "-o", str(part), url]).returncode == 0:
                break
            log(f"{url} failed")
        else:
            raise SystemExit(f"no mirror serves {path}")
        part.rename(dest)
    return {"url": url, "sha256": sha256(dest)}


def main() -> None:
    which = sys.argv[1:] or ["meta", "fsd", "voxpopuli", "libritts"]
    SRC.mkdir(parents=True, exist_ok=True)
    rec_path = SRC / "fetched.json"
    rec = json.loads(rec_path.read_text()) if rec_path.exists() else {}
    t = time.time()
    for w in which:
        if w in ("voxpopuli", "libritts"):
            rec[w] = {"repo": SOURCES[w]["repo"], "revision": SOURCES[w]["revision"], "files": hf(w, SOURCES[w]["files"])}
        elif w == "fsd":
            clips = json.loads((HERE / "fsd_test.json").read_text())["clips"]
            rec[w] = {"repo": SOURCES[w]["repo"], "revision": SOURCES[w]["revision"],
                      "files": hf(w, [f"clips/{c['fsd_split']}/{c['fname']}.wav" for c in clips])}
        elif w == "meta":
            tgz = SRC / "meta" / "raw-metadata.tar.gz"
            rec[w] = openslr("/resources/12/raw-metadata.tar.gz", tgz)
            with tarfile.open(tgz) as tar:
                tar.extractall(SRC / "meta", filter="data")
        rec_path.write_text(json.dumps(rec, indent=1))
        log(f"{w} done in {time.time() - t:.0f}s")
    subprocess.run(["du", "-sh", str(SRC)])


if __name__ == "__main__":
    main()
