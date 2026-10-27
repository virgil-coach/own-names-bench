#!/usr/bin/env python3
"""Contamination check of the v1.3 audiobook test suite (data/manifest.json) against everything in build/excl.json
(own-names-bench v1.2.0, lore books / eval sets, bookdev, bigcast, the v0.3.0-v0.7.0 adapters' training data,
LibriSpeech dev / test). Exits non-zero on any failure; writes build/contamination.json, counts only (no name, reader,
book or text of any held-out set is written).

  sources    every clip and taught recording is a piece of a build/books.json book, cut from a section of that book's
             archive.org item read by its one reader
  readers    no suite reader is an excluded reader (benchmark, lore, dev sets, training books, LibriTTS / LibriTTS-R
             training speakers, LibriSpeech dev / test speakers)
  books      no suite book's LibriVox project, archive.org item, Gutenberg text or work (title across readings and
             volumes) is excluded, and no title is of a held series
  names      no listed name is a training-list or generated training name (exact), or equal or close to, or sharing a
             4+ letter word with, a held name (curate.py's rule)
  audio      SHA-256 of every suite file (file, and 16-bit PCM) against every own-names-bench v1.2.0, bookdev and bigcast
             audio hash; no two suite clips are the same file
  text       no clip reference shares a run of 8 normalized words with a held text (lore books, bookdev, bigcast,
             own-names-bench references and chapters, lore eval-set references)
  reported   (not failed) listed names that are in the Wikidata name lists (lore-name-lists, used for YODAS / synthetic
             data), suite readers who are LibriSpeech train-360 / train-500 speakers (not in any of our training data)

usage: check.py  -> build/contamination.json
"""
import hashlib
import json
import re
import sys
from collections import Counter

import soundfile as sf

from build import grams, held_texts
from common import DATA, JL, WORK, base_reader, log, write_json
from curate import Held
from excl import librispeech, work_title
from find_books import SERIES_OR_RESERVED
from own_names_bench.text import name_key


def pcm_sha(path) -> str:
    x, _ = sf.read(path, dtype="int16")
    return hashlib.sha256(x.astype("<i2").tobytes()).hexdigest()


def main() -> None:
    m = json.loads((DATA / "manifest.json").read_text())
    ex = json.loads((WORK / "excl.json").read_text())
    books = {b["key"]: b for b in json.loads((WORK / "books.json").read_text())["books"]}
    fails: Counter = Counter()
    rep: dict = {}

    # sources
    for c in m["clips"].values():
        b = books.get(c["book"])
        if b is None or c["reader"] != b["reader"] or c["source"] not in {s["url"] for s in b["sections"]}:
            fails["sources: clip not from its book's own sections"] += 1
    for e in m["entries"].values():
        b = books.get(e["book"])
        if b is None or e["reader"] != b["reader"] or e["sample_source_url"] not in {s["url"] for s in b["sections"]}:
            fails["sources: taught recording not from its book's own sections"] += 1
    used = sorted({c["book"] for c in m["clips"].values()})
    rep["books"] = len(used)

    # readers
    readers = sorted({c["reader"] for c in m["clips"].values()} | {e["reader"] for e in m["entries"].values()})
    rep["readers"] = len(readers)
    fails["readers: excluded"] = sum(base_reader(r) in ex["readers"] for r in readers)
    spk, chap = librispeech()
    ls_names = {}
    for sid, c in chap.items():
        if c["reader"] in spk:
            ls_names.setdefault(base_reader(spk[c["reader"]]), set()).add(c["subset"])
    rep["readers_who_are_librispeech_speakers"] = sum(base_reader(r) in ls_names for r in readers)
    rep["readers_who_are_librispeech_speakers_subsets"] = sorted({s for r in readers for s in ls_names.get(base_reader(r), ())})
    ls_proj: dict[str, set[str]] = {}
    for c in chap.values():
        ls_proj.setdefault(c["project"], set()).add(c["subset"])
    rep["books_whose_librivox_project_is_in_librispeech"] = sum(str(books[k]["librivox_id"]) in ls_proj for k in used)
    same = 0
    chapters = 0
    for k in used:
        mine = [c for c in chap.values() if c["project"] == str(books[k]["librivox_id"])
                and base_reader(spk.get(c["reader"], "")) == base_reader(books[k]["reader"])]
        same += bool(mine)
        chapters += len(mine)
    rep["books_whose_reading_by_its_suite_reader_is_in_librispeech"] = same
    rep["librispeech_chapters_of_those_readings"] = chapters
    rep["books_whose_librivox_project_is_in_librispeech_subsets"] = sorted({s for k in used for s in ls_proj.get(str(books[k]["librivox_id"]), ())})

    # books
    for k in used:
        b = books[k]
        a = m["attribution"]["clips"][k]
        fails["books: LibriVox project excluded"] += str(b["librivox_id"]) in ex["projects"]
        fails["books: archive.org item excluded"] += b["archive_item"] in ex["items"]
        fails["books: Gutenberg text excluded"] += any(str(g) in ex["gutenberg"] for g in b["gutenberg_ids"])
        fails["books: work excluded"] += work_title(b["title"]) in ex["titles"]
        fails["books: held series"] += bool(SERIES_OR_RESERVED.search(b["title"]))
        fails["books: two suite books share a work"] += sum(work_title(books[o]["title"]) == work_title(b["title"]) for o in used if o != k)
        assert a["librivox_id"] == b["librivox_id"]

    # names
    held = Held()
    names = [e["written"] for e in m["entries"].values()]
    rep["entries"] = len(names)
    fails["names: training-list or generated training name"] = sum(name_key(n) in held.trained for n in names)
    fails["names: equal, close to or sharing a word with a held name"] = sum(held.why(n) is not None for n in names)
    wk = {name_key(n) for n in ex["wikidata_names"]}
    rep["entries_in_wikidata_name_lists"] = sum(name_key(n) in wk for n in names)
    rep["mentions_of_names_in_wikidata_name_lists"] = sum(name_key(m["entries"][mn["entry"]]["written"]) in wk for mn in m["mentions"])

    # audio
    bench_hashes = set(json.loads((JL / "lore-poc-wt-v06" / "convdata" / "excl.json").read_text())["bench_audio_sha256"])
    src = json.loads((JL / "own-names-bench-src" / "dataset" / "manifest.json").read_text())
    bench_hashes |= set(src["files"].values())
    for f in ("own-names-bench-wt-bookdev/bookdev/out/manifest.json", "own-names-bench-wt-bookdev/bookdev/out/manifest_v2.json",
              "own-names-bench-wt-bigcast/bigcast/out/manifest.json"):
        mm = json.loads((JL / f).read_text())
        bench_hashes |= set(mm["files"].values())
        bench_hashes |= {c.get("pcm_sha256") for c in mm["clips"].values() if c.get("pcm_sha256")}
    rep["held_audio_hashes"] = len(bench_hashes)
    files = [p for p in sorted((DATA / "audio").rglob("*.flac"))]
    fh = Counter()
    for p in files:
        h = hashlib.sha256(p.read_bytes()).hexdigest()
        fh[h] += 1
        fails["audio: file equal to a held file"] += h in bench_hashes
        fails["audio: PCM equal to a held file"] += pcm_sha(p) in bench_hashes
    rep["audio_files_hashed"] = len(files)
    clip_h = Counter(c["sha256"] for c in m["clips"].values())
    fails["audio: two clips are the same file"] = sum(n - 1 for n in clip_h.values() if n > 1)

    # text
    held_g = set()
    for _, t in held_texts():
        held_g |= grams(t)
    rep["held_8_word_runs"] = len(held_g)
    fails["text: a clip reference shares an 8-word run with a held text"] = sum(bool(grams(c["reference"]) & held_g)
                                                                              for c in m["clips"].values())
    rep["clip_references_checked"] = len(m["clips"])
    rep["not_checkable"] = ("YODAS clips in v0.3.0-v0.7.0 training carry no speaker or channel; a suite reader appearing in a "
                            "training video cannot be ruled out by name.")
    fails = {k: int(v) for k, v in sorted(fails.items())}
    verdict = "PASS" if not any(fails.values()) else "FAIL"
    out = {"verdict": verdict, "failures": fails, "report": rep, "exclusions": ex["counts"],
           "excl_sha256": hashlib.sha256((WORK / "excl.json").read_bytes()).hexdigest()}
    write_json(WORK / "contamination.json", out)
    log(json.dumps(out, indent=1))
    if verdict != "PASS":
        sys.exit("contamination check FAILED")


if __name__ == "__main__":
    main()
