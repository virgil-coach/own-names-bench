"""Shared paths and helpers of the own-names-bench v1.3 audiobook test suite ("books13").

Everything the build reads or writes outside git lives under ROOT (default ~/workspace/jl/onb-v13-books-SEALED):
  ROOT/build/   work files: exclusion lists, LibriVox / Gutenberg metadata, aligned pieces, build stats, reports
  ROOT/data/    the suite itself, in the benchmark's dataset format (manifest.json + audio/), read-only once sealed
"""
import json
import os
import re
import sys
import time
import unicodedata
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parent.parent
JL = REPO.parent
ROOT = Path(os.environ.get("BOOKS13_ROOT", Path.home() / "workspace" / "jl" / "onb-v13-books-SEALED"))
WORK = ROOT / "build"
DATA = ROOT / "data"
RATE = 16000
SEED = 1313

sys.path.insert(0, str(REPO))


def log(*parts: object) -> None:
    print(time.strftime("%H:%M:%S"), *parts, flush=True)


def norm(s: str) -> str:
    """A person's or a title's comparison key: letters only, lower case (as bookdev/find_books.py)."""
    s = unicodedata.normalize("NFKD", s)
    return re.sub(r"[^a-z]", "", s.lower())


def base_reader(s: str) -> str:
    """A reader's display name without a parenthesised note ("Anthony Ogus (1945-2013)")."""
    return norm(re.sub(r"\s*\(.*?\)\s*", " ", s))


def letters(s: str) -> str:
    s = unicodedata.normalize("NFKD", s.replace("æ", "ae").replace("Æ", "Ae"))
    return "".join(c for c in s.lower() if "a" <= c <= "z")


def word_keys(s: str) -> set[str]:
    return {w for w in (letters(p) for p in re.split(r"[\s\-]+", s)) if len(w) >= 4}


def jsonl(path: Path) -> list[dict]:
    with path.open() as f:
        return [json.loads(line) for line in f if line.strip()]


def write_json(path: Path, obj: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=1, ensure_ascii=False) + "\n")
