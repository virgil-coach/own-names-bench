#!/usr/bin/env python3
"""Every exclusion of the v1.3 audiobook test suite, gathered from its sources into build/excl.json.

No book, reader or name of the suite may come from:
  bench       own-names-bench v1.2.0 (own-names-bench-src/dataset/manifest.json: clip and chapter readers, books, entries,
              audio hashes, references) and the train-side exclusion file of the conversation data
              (lore-poc-wt-v06/convdata/excl.json: the same benchmark, lore held-out readers and books)
  lore        lore-poc books/ (books.json, splits.json, results/names: the 70 lore audiobooks, train / dev / test, i.e.
              v0.3.0-v0.7.0 training books, lore dev and the benchmark's source), dataset/book_candidates.json (80 audited
              candidates), spotting/data_book (the lore `book` / `long` / `stream` eval sets), the private HF sets
              littlebearlabs/lore-* (eval-set definitions, name lists, synthetic-voice manifests)
  dev sets    own-names-bench dev/bookdev and dev/bigcast (books.json, every name their pipeline found, their manifests)
  training    lore-poc ctxft attribution of every adapter branch (train/*, release/v0.7.0, data/conv-names-v1):
              librivox_books.csv (training books and readers), libritts.csv (LibriTTS speakers, cloned voices and real
              recordings), conv_libritts_r.csv (LibriTTS-R train-clean-100 utterances of the conversation data), the
              v0.3.0 template books, the 3,000 generated names (ctxft/gen.py, as build/contamination.py regenerates them)
  LibriSpeech every dev / test speaker and LibriVox project (the sealed v1.3 conversation suite's LibriTTS-R readers come
              from test-clean / test-other; its own files are not read), resolved with SPEAKERS.TXT and CHAPTERS.TXT

Output (build/excl.json, kept out of git; its SHA-256 goes into the seal): readers, LibriVox projects, archive items,
Gutenberg ids and work titles with the first reason each was excluded; names held elsewhere (for the collision rule);
names of training-book lists and generated training names (exact exclusion); Wikidata name-list names (reported only).

usage: excl.py
"""
import csv
import json
import re
import sys
from collections import defaultdict
from pathlib import Path

import pyarrow.parquet as pq

from common import JL, WORK, base_reader, log, norm, write_json

LORE = JL / "lore-poc"
SRC = JL / "own-names-bench-src" / "dataset"
CONV_EXCL = JL / "lore-poc-wt-v06" / "convdata" / "excl.json"
BOOKDEV = JL / "own-names-bench-wt-bookdev" / "bookdev"
BIGCAST = JL / "own-names-bench-wt-bigcast" / "bigcast"
HF = WORK / "src" / "hf"
LIBRISPEECH = LORE / "spotting" / "cache_real" / "librispeech" / "LibriSpeech"
# v0.3.0's 40 sentence templates were taken from these Project Gutenberg books (ctxft/public/attribution/ATTRIBUTION.md)
TEMPLATE_BOOKS = {11: "Alice's Adventures in Wonderland", 778: "Five Children and It", 503: "The Blue Fairy Book",
                  836: "The Phoenix and the Carpet", 1874: "The Railway Children", 113: "The Secret Garden",
                  289: "The Wind in the Willows"}


def work_title(t: str) -> str:
    """A work's key across readings and volumes: no "(Version 3)", "Volume 2", leading article or punctuation."""
    t = re.sub(r"\((?:[^)]*version[^)]*|[^)]*vol[^)]*)\)", " ", t, flags=re.I)
    t = re.sub(r"\b(version|vol\.?|volume|book|part)\s*[0-9ivx]+\b", " ", t, flags=re.I)
    t = re.sub(r"^\s*(the|a|an)\s+", "", t.strip(), flags=re.I)
    t = re.split(r"[:;]", t)[0]
    return norm(t)


class Excl:
    def __init__(self) -> None:
        self.readers: dict[str, str] = {}
        self.projects: dict[str, str] = {}
        self.items: dict[str, str] = {}
        self.gutenberg: dict[str, str] = {}
        self.titles: dict[str, str] = {}
        self.held_names: dict[str, set[str]] = defaultdict(set)   # name -> sources (collision rule)
        self.trained_names: dict[str, set[str]] = defaultdict(set)  # name -> sources (exact exclusion)
        self.counts: dict[str, int] = {}

    def reader(self, r: str | None, why: str) -> None:
        if r and base_reader(r):
            self.readers.setdefault(base_reader(r), why)

    def project(self, p, why: str) -> None:
        if p not in (None, "", 0):
            self.projects.setdefault(str(int(p)), why)

    def item(self, a: str | None, why: str) -> None:
        if a:
            a = a.rstrip("/").split("/")[-1]
            self.items.setdefault(a, why)

    def gut(self, g, why: str) -> None:
        if g not in (None, ""):
            for x in re.findall(r"\d+", str(g)):
                self.gutenberg.setdefault(str(int(x)), why)

    def title(self, t: str | None, why: str) -> None:
        if t and work_title(t):
            self.titles.setdefault(work_title(t), why)

    def book(self, why: str, *, title=None, project=None, item=None, gutenberg=None, readers=()) -> None:
        self.title(title, why)
        self.project(project, why)
        self.item(item, why)
        for g in (gutenberg if isinstance(gutenberg, list) else [gutenberg]):
            self.gut(g, why)
        for r in readers:
            self.reader(r, f"reader of {why}")


def librispeech() -> tuple[dict[str, str], dict[str, dict]]:
    spk, chap = {}, {}
    for line in (LIBRISPEECH / "SPEAKERS.TXT").read_text(errors="replace").splitlines():
        if line.startswith(";"):
            continue
        f = [p.strip() for p in line.split("|")]
        if len(f) >= 5:
            spk[f[0]] = f[4]
    for line in (LIBRISPEECH / "CHAPTERS.TXT").read_text(errors="replace").splitlines():
        if line.startswith(";"):
            continue
        f = [p.strip() for p in line.split("|")]
        if len(f) >= 7:
            chap[f[0]] = {"reader": f[1], "subset": f[3], "project": f[4], "book": f[5]}
    return spk, chap


def names_json(path: Path) -> list[str]:
    return [n["name"] for n in json.loads(path.read_text())]


def main() -> None:
    ex = Excl()
    spk, chap = librispeech()

    # ------------------------------------------------------------ own-names-bench v1.2.0
    m = json.loads((SRC / "manifest.json").read_text())
    assert m["version"] == "1.2.0"
    for c in m["clips"].values():
        ex.reader(c["reader"], "own-names-bench v1.2.0 clip reader")
    for e in m["entries"].values():
        ex.reader(e["reader"], "own-names-bench v1.2.0 enrollment reader")
        ex.held_names[e["written"]].add("own-names-bench v1.2.0")
    for ch in m["chapters"]:
        ex.reader(ch["reader"], "own-names-bench v1.2.0 chapter reader")
    for k, a in m["attribution"]["clips"].items():
        ex.book(f"own-names-bench v1.2.0 book {k}", title=a["title"], project=a.get("librivox_id"), item=a["archive_item"],
                gutenberg=a.get("gutenberg_ids") or [], readers=a["readers"])
    for k, a in m["attribution"]["chapters"].items():
        ex.book(f"own-names-bench v1.2.0 chapter book {k}", title=a["title"], item=a["archive_item"],
                gutenberg=re.findall(r"\d+", a.get("text") or ""), readers=a["readers"])
    cx = json.loads(CONV_EXCL.read_text())
    for r in cx["bench_readers"]:
        ex.reader(r, "own-names-bench reader (convdata excl)")
    for r in cx["lore_heldout"]["readers"]:
        ex.reader(r, "lore held-out reader (convdata excl)")
    for p in cx["bench_books"]["librivox_ids"] + cx["lore_heldout"]["librivox_ids"]:
        ex.project(p, "own-names-bench / lore held-out book (convdata excl)")
    for a in cx["bench_books"]["archive_items"]:
        ex.item(a, "own-names-bench book (convdata excl)")
    for g in cx["bench_books"]["gutenberg_ids"] + cx["lore_heldout"]["gutenberg_ids"]:
        ex.gut(g, "own-names-bench / lore held-out text (convdata excl)")
    for t in cx["bench_books"]["titles"]:
        ex.title(t, "own-names-bench book (convdata excl)")

    # ------------------------------------------------------------ lore books (v0.3.0-v0.7.0 training, lore dev and test)
    splits = json.loads((LORE / "books" / "splits.json").read_text())
    for b in json.loads((LORE / "books" / "books.json").read_text())["books"]:
        sp = splits["books"][b["key"]]["split"]
        why = f"lore book {b['key']} ({sp})"
        ex.book(why, title=b["title"], project=b["librivox_id"], item=b["archive_item"], gutenberg=b["gutenberg_ids"])
        for s in b["sections"] + b.get("dropped_sections", []):
            for r in s["readers"]:
                ex.reader(r, f"reader of {why}")
        for n in names_json(LORE / "books" / "results" / "names" / f"{b['key']}.json"):
            ex.held_names[n].add(f"lore {sp} book")
            if sp == "train":
                ex.trained_names[n].add("lore training book list (v0.3.0-v0.7.0)")
    for r, s in splits["readers"].items():
        ex.reader(r, f"lore books reader ({s})")
    for path, label in ((LORE / "dataset" / "book_candidates.json", "lore candidate"),
                        (HF / "lore-name-lists" / "meta" / "book_candidates.json", "lore-name-lists candidate")):
        for c in json.loads(path.read_text()):
            ex.book(f"{label} {c['title']}", title=c["title"], project=c.get("librivox_id"), item=c.get("archive_item"),
                    gutenberg=c.get("gutenberg_id"), readers=c.get("readers") or [])
    db = json.loads((LORE / "spotting" / "data_book" / "manifest.json").read_text())
    for b in db["books"]:
        ex.book(f"lore eval-set book {b['key']}", title=b["title"], item=b.get("audio_url"),
                gutenberg=re.findall(r"\d+", b.get("text_url") or ""), readers=[b["reader"]])
    for r in db.get("readers", []):
        ex.reader(r if isinstance(r, str) else r.get("name"), "lore eval-set reader")
    for t in db["terms"]:
        ex.reader(t.get("speaker"), "lore eval-set speaker")
        ex.held_names[t["spelling"]].add("lore eval sets")
    for ch in json.loads((HF / "lore-eval-sets" / "defs" / "long" / "long.json").read_text())["chapters"]:
        ex.reader(ch["reader"], "lore-eval-sets long reader")
    for f in ("book", "tts"):
        for n in json.loads((HF / "lore-eval-sets" / "defs" / f"{f}.json").read_text())["spelling"]:
            ex.held_names[n].add(f"lore-eval-sets {f}")
    for n in json.loads((HF / "lore-eval-sets" / "defs" / "taken.json").read_text()):
        ex.held_names[n].add("lore-eval-sets taken")
    for f in ("omnivoice", "qwen3tts"):
        mm = json.loads((HF / "lore-synthetic-names" / "meta" / f / "manifest.json").read_text())
        for v in mm["voices"]:
            sid = v["slug"].removeprefix("libri")
            if sid.isdigit() and sid in spk:
                ex.reader(spk[sid], "LibriTTS reference voice of lore-synthetic-names")
        for t in mm["terms"]:
            ex.trained_names[t["spelling"]].add("lore-synthetic-names term")

    # ------------------------------------------------------------ own-names-bench dev sets
    for folder, label in ((BOOKDEV, "bookdev"), (BIGCAST, "bigcast")):
        for b in json.loads((folder / "lore_books" / "books.json").read_text())["books"]:
            why = f"own-names-bench {label} book {b['key']} ({b.get('use', 'dev')})"
            ex.book(why, title=b["title"], project=b["librivox_id"], item=b["archive_item"], gutenberg=b["gutenberg_ids"],
                    readers=b["readers"])
            for s in b["sections"] + b.get("dropped_sections", []):
                for r in s["readers"]:
                    ex.reader(r, f"reader of {why}")
            if b.get("use") == "train":
                for n in names_json(folder / "out" / "books" / "names" / f"{b['key']}.json") \
                        if (folder / "out" / "books" / "names" / f"{b['key']}.json").exists() else []:
                    ex.trained_names[n].add(f"{label} training book list")
        for p in sorted((folder / "out" / "books" / "names").glob("*.json")):
            for n in names_json(p):
                ex.held_names[n].add(f"own-names-bench {label}")
        for mf in sorted((folder / "out").glob("manifest*.json")):
            mm = json.loads(mf.read_text())
            for c in mm["clips"].values():
                ex.reader(c["reader"], f"own-names-bench {label} reader")
            for e in mm["entries"].values():
                ex.reader(e["reader"], f"own-names-bench {label} reader")
                ex.held_names[e["written"]].add(f"own-names-bench {label}")
            for k, a in mm["attribution"]["clips"].items():
                ex.book(f"own-names-bench {label} book {k}", title=a["title"], project=a.get("librivox_id"),
                        item=a["archive_item"], gutenberg=a.get("gutenberg_ids") or [], readers=a["readers"])

    # ------------------------------------------------------------ adapter training data (every lore-poc branch)
    attr_dirs = sorted({p for p in JL.glob("lore-poc*/ctxft/**/attribution") if p.is_dir()})
    for d in attr_dirs:
        lb = d / "librivox_books.csv"
        if lb.exists():
            for row in csv.DictReader(lb.open()):
                ex.book(f"adapter training book ({d.relative_to(JL).parts[0]})", title=row["title"], project=row.get("librivox_id"),
                        item=row.get("archive_item"), gutenberg=row.get("gutenberg_ids"), readers=row["readers"].split(";"))
        lt = d / "libritts.csv"
        if lt.exists():
            for row in csv.DictReader(lt.open()):
                sid = row["speaker_id"]
                ex.reader(spk.get(sid), "LibriTTS speaker in adapter training (cloned voice or real recording)")
                ch = row["utterance_id"].split("_")[1] if row.get("utterance_id") else ""
                if ch in chap:
                    ex.project(chap[ch]["project"], "LibriTTS book in adapter training")
        lr = d / "conv_libritts_r.csv"
        if lr.exists():
            for row in csv.DictReader(lr.open()):
                ex.reader(spk.get(row["speaker_id"]), "LibriTTS-R speaker in conversation training (v0.6/v0.7)")
                ex.reader(row.get("reader"), "LibriTTS-R speaker in conversation training (v0.6/v0.7)")
                ex.project(row.get("librivox_project"), "LibriTTS-R book in conversation training (v0.6/v0.7)")
                ex.gut(row.get("gutenberg"), "LibriTTS-R text in conversation training (v0.6/v0.7)")
    for g, t in TEMPLATE_BOOKS.items():
        ex.book(f"v0.3.0 template book {t}", title=t, gutenberg=g)
    for sid, c in chap.items():
        if c["subset"] == "train-clean-100":
            ex.project(c["project"], "LibriTTS-R train-clean-100 book (conversation training)")
            ex.reader(spk.get(c["reader"]), "LibriTTS-R train-clean-100 speaker (conversation training)")
        if c["subset"].split("-")[0] in ("dev", "test"):
            ex.project(c["project"], f"LibriSpeech {c['subset']} book (lore / v1.3 conversation suite test readers)")
            ex.reader(spk.get(c["reader"]), f"LibriSpeech {c['subset']} speaker (lore / v1.3 conversation suite test readers)")

    # generated training names, regenerated exactly as build/contamination.py does
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
    from contamination import generated_names  # noqa: E402
    gen = generated_names(LORE / "ctxft" / "gen.py", HF / "lore-eval-sets" / "defs" / "taken.json")
    for n in gen:
        ex.trained_names[n].add("generated training name (ctxft/gen.py)")
    wikidata = []
    for s in ("train", "dev", "test"):
        t = pq.read_table(HF / "lore-name-lists" / "names" / f"{s}-00000-of-00001.parquet", columns=["name"])
        wikidata += [(n, s) for n in t.column("name").to_pylist()]

    ex.counts = {"readers": len(ex.readers), "librivox_projects": len(ex.projects), "archive_items": len(ex.items),
                 "gutenberg_ids": len(ex.gutenberg), "work_titles": len(ex.titles), "held_names": len(ex.held_names),
                 "trained_names": len(ex.trained_names), "generated_names": len(gen), "wikidata_names": len(wikidata),
                 "attribution_dirs": len(attr_dirs)}
    write_json(WORK / "excl.json", {
        "readers": dict(sorted(ex.readers.items())), "projects": dict(sorted(ex.projects.items())),
        "items": dict(sorted(ex.items.items())), "gutenberg": dict(sorted(ex.gutenberg.items())),
        "titles": dict(sorted(ex.titles.items())),
        "held_names": {k: sorted(v) for k, v in sorted(ex.held_names.items())},
        "trained_names": {k: sorted(v) for k, v in sorted(ex.trained_names.items())},
        "wikidata_names": {n: s for n, s in wikidata},
        "attribution_dirs": [str(d.relative_to(JL)) for d in attr_dirs], "counts": ex.counts})
    log(json.dumps(ex.counts))


if __name__ == "__main__":
    main()
