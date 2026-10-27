#!/usr/bin/env python3
"""Validity check and seal of the v1.3 audiobook test suite. Data tooling only: no model or system reads the audio.

validity   every file of data/manifest.json exists with its SHA-256; every clip decodes (16 kHz mono), is 3.5-15 s as
           listed, is not empty, silent or clipped (> 0.5% of samples at full scale), and its level is recorded; every
           mention's span reads as its entry's spelling (the benchmark's name tokens), its entry is on the clip's own
           list, its aligned time lies inside the clip and is not near-silent (> 25 dB under the clip); no name of any
           list occurs in a name-free reference; taught recordings are 0.15-2.6 s and not silent; the benchmark's own
           loader reads the folder (file hashes checked) and builds its passes; and the benchmark's scorer, fed the
           references themselves as transcripts, gives every name right, none overwritten, no insertion, no word error
seal       LICENCE.txt and ATTRIBUTION.csv in data/; MANIFEST.json and SHA256SUMS beside data/ (every file's SHA-256 and
           the suite hash: SHA-256 of the sorted "<sha256>  <path>" lines), SEALED.txt; data/ made read-only

usage: seal.py  -> ROOT/{MANIFEST.json,SHA256SUMS,SEALED.txt}, build/validity.json
"""
import csv
import hashlib
import json
import os
import stat
import subprocess
import time
from collections import Counter, defaultdict

import numpy as np
import soundfile as sf

from common import DATA, HERE, RATE, ROOT, WORK, log, write_json
from own_names_bench.data import load
from own_names_bench.passes import all_passes
from own_names_bench.score import score_clips
from own_names_bench.text import find_all, name_key, name_tokens, nfc

CODE = ["common.py", "excl.py", "find_books.py", "rank_books.py", "manifest.py", "lore_text.py", "align_book.py", "calib.py",
        "curate.py", "curation.json", "build.py", "check.py", "seal.py", "pyproject.toml", "uv.lock"]


def sha(p) -> str:
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def dbfs(x: np.ndarray) -> float:
    return float(20 * np.log10(np.sqrt(np.mean(x.astype(np.float64) ** 2)) + 1e-9))


def pct(v: list[float]) -> dict:
    a = np.asarray(v)
    return {"n": len(v), "p5": round(float(np.percentile(a, 5)), 1), "median": round(float(np.median(a)), 1),
            "p95": round(float(np.percentile(a, 95)), 1)} if v else {}


def validity(m: dict) -> dict:
    problems: Counter = Counter()
    levels: dict[str, list[float]] = defaultdict(list)
    for rel, h in m["files"].items():
        if not (DATA / rel).is_file() or sha(DATA / rel) != h:
            problems["file missing or changed"] += 1
    audio = {}
    for c in m["clips"].values():
        x, sr = sf.read(DATA / c["audio"], dtype="float32")
        audio[c["id"]] = x
        if sr != RATE or x.ndim != 1 or not np.isfinite(x).all() or not np.any(x):
            problems["clip unreadable, wrong rate or all zero"] += 1
            continue
        if abs(len(x) / RATE - c["seconds"]) > 0.01 or not 3.5 <= c["seconds"] <= 15.0:
            problems["clip length differs from the manifest or is outside 3.5-15 s"] += 1
        if np.mean(np.abs(x) >= 0.999) > 0.005:
            problems["more than 0.5% of samples clipped"] += 1
        lv = dbfs(x)
        levels["clip_dbfs"].append(lv)
        if lv < -60:
            problems["clip below -60 dBFS"] += 1
    for e in m["entries"].values():
        x, _ = sf.read(DATA / e["sample"], dtype="float32")
        if not 0.15 <= len(x) / RATE <= 2.6 or dbfs(x) < -60:
            problems["taught recording outside 0.15-2.6 s or silent"] += 1
        levels["taught_dbfs"].append(dbfs(x))
    for mn in m["mentions"]:
        c, e = m["clips"][mn["clip"]], m["entries"][mn["entry"]]
        ref = nfc(c["reference"])
        if tuple(name_tokens(ref[mn["span"][0]:mn["span"][1]])) != name_key(e["written"]):
            problems["mention span is not the listed spelling"] += 1
        if mn["entry"] not in m["lists"][f"own:{c['book']}"]["entries"]:
            problems["spoken entry not on the clip's list"] += 1
        a, b = mn["name_at_s"]
        if not 0 <= a < b <= c["seconds"] + 0.05:
            problems["aligned name time outside the clip"] += 1
            continue
        x = audio[c["id"]]
        seg = x[int(a * RATE):int(b * RATE)]
        if len(seg) == 0 or dbfs(seg) < dbfs(x) - 25:
            problems["aligned name near-silent"] += 1
        levels["name_minus_clip_db"].append(dbfs(seg) - dbfs(x) if len(seg) else -99.0)
    every = {name_key(e["written"]) for e in m["entries"].values()}
    for nf in m["name_free"]:
        toks = name_tokens(m["clips"][nf["clip"]]["reference"])
        if any(find_all(toks, k) for k in every):
            problems["a listed name in a name-free reference"] += 1
    # the benchmark's own loader, passes and scorer
    b = load(DATA, verify=True)
    passes = all_passes(b, ("none", "own", "xr"), chapters=False, suites=False)
    texts = {p.id: b.clips[p.id.split("/")[1]]["reference"] for p in passes if p.variant != "none"}
    s = score_clips(b, texts)
    oracle = {"passes_own_and_minus": len(texts), "mentions": len(s["mentions"]),
              "own_right": sum(r.get("own_right", False) for r in s["mentions"]),
              "own_overwritten": sum(r.get("own_overwritten", False) for r in s["mentions"]),
              "own_wrong_name": sum(r.get("own_wrong_name", False) for r in s["mentions"]),
              "name_free": len(s["name_free"]), "own_inserted": sum(r.get("own_inserted", False) for r in s["name_free"]),
              "word_errors": sum(r.get("own_errors", 0) for r in s["wer"]), "words": sum(r.get("words", 0) for r in s["wer"])}
    if oracle["own_right"] != len(m["mentions"]) or oracle["own_overwritten"] or oracle["own_wrong_name"] or oracle["own_inserted"] \
            or oracle["word_errors"]:
        problems["the benchmark's scorer does not give the references a perfect score"] += 1
    run_passes = all_passes(b, ("none", "own", "xr"), chapters=False, suites=False)
    out = {"problems": {k: v for k, v in problems.items() if v}, "levels_db": {k: pct(v) for k, v in sorted(levels.items())},
           "oracle_score": oracle, "passes_for_a_system_with_none_own": len([p for p in run_passes if p.variant in ("none", "own")]),
           "passes_cross_reader": len([p for p in run_passes if p.variant == "xr"])}
    out["verdict"] = "PASS" if not out["problems"] else "FAIL"
    return out


def main() -> None:
    if (ROOT / "SEALED.txt").exists():
        raise SystemExit("already sealed")
    m = json.loads((DATA / "manifest.json").read_text())
    v = validity(m)
    write_json(WORK / "validity.json", v)
    log(json.dumps(v, indent=1))
    if v["verdict"] != "PASS":
        raise SystemExit(f"validity FAIL: {v['problems']}")
    cont = json.loads((WORK / "contamination.json").read_text())
    if cont["verdict"] != "PASS":
        raise SystemExit("contamination check did not pass; not sealing")

    with (DATA / "ATTRIBUTION.csv").open("w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["book", "title", "author", "reader", "librivox_url", "archive_item", "gutenberg_ids", "public_domain_basis", "group"])
        for k, a in sorted(m["attribution"]["clips"].items()):
            w.writerow([k, a["title"], a["author"], "; ".join(a["readers"]), a["librivox_url"], a["archive_item"],
                        " ".join(map(str, a["gutenberg_ids"])), a["public_domain_basis"], a["group"]])
    (DATA / "LICENCE.txt").write_text(
        "own-names-bench v1.3 audiobook test suite (books13), held out and sealed.\n\n"
        "Audio: LibriVox recordings, dedicated to the public domain by their readers (US); cut into clips and taught\n"
        "recordings. Reference texts: the Project Gutenberg texts of the same books, public domain in the US. Every book,\n"
        "its reader, LibriVox page, archive.org item and Gutenberg text is listed in ATTRIBUTION.csv.\n"
        "Annotations (lists, mentions, spans, times, manifest.json): Creative Commons Attribution 4.0 International,\n"
        "https://creativecommons.org/licenses/by/4.0/, (c) 2026 Little Bear Labs, Inc.\n"
        "Word times were made by forced alignment with facebook/wav2vec2-large-960h-lv60-self (Apache 2.0); the model is not\n"
        "distributed.\n")
    files = sorted(p for p in DATA.rglob("*") if p.is_file())
    file_sha = {str(p.relative_to(DATA)): sha(p) for p in files}
    zero = hashlib.sha256(b"").hexdigest()
    if any(h == zero for h in file_sha.values()):
        raise SystemExit("an empty file in the suite; not sealing")
    blob = "".join(f"{h}  {p}\n" for p, h in sorted(file_sha.items()))
    suite_hash = hashlib.sha256(blob.encode()).hexdigest()
    (ROOT / "SHA256SUMS").write_text(blob)
    commit = subprocess.run(["git", "-C", str(HERE), "rev-parse", "HEAD"], capture_output=True, text=True).stdout.strip()
    dirty = subprocess.run(["git", "-C", str(HERE), "status", "--porcelain", "--", "."], capture_output=True, text=True).stdout.strip()
    stats = json.loads((WORK / "build_stats.json").read_text())
    manifest = {
        "name": "own-names-bench v1.3 audiobook test suite, books13 (held out, sealed)",
        "sealed_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "suite_hash": suite_hash, "suite_hash_rule": "sha256 of SHA256SUMS: the sorted lines '<sha256>  <path relative to data/>' of every file",
        "storage": {"host": os.uname().nodename, "path": str(DATA), "root": str(ROOT)},
        "build": {"repo": "own-names-bench", "branch": "suite/books-v13", "commit": commit + ("-dirty" if dirty else ""),
                  "code_sha256": {f: sha(HERE / f) for f in CODE if (HERE / f).exists()},
                  "excl_sha256": cont["excl_sha256"], "dataset_manifest_sha256": file_sha["manifest.json"]},
        "counts": stats, "contamination": {"verdict": cont["verdict"], "report": "contamination.json"},
        "validity": {"verdict": v["verdict"], "report": "validity.json"},
        "rule": "Held out: scored once per final system. No model or API was run on this audio while building it (the forced aligner "
                "timed the book text's words). Do not train, tune, select or smoke-test on it.",
        "files": file_sha,
    }
    (ROOT / "MANIFEST.json").write_text(json.dumps(manifest, indent=1, ensure_ascii=False) + "\n")
    for p in sorted(DATA.rglob("*"), reverse=True):
        p.chmod(p.stat().st_mode & ~(stat.S_IWUSR | stat.S_IWGRP | stat.S_IWOTH))
    DATA.chmod(DATA.stat().st_mode & ~(stat.S_IWUSR | stat.S_IWGRP | stat.S_IWOTH))
    (ROOT / "SEALED.txt").write_text(f"SEALED {manifest['sealed_at']} suite_hash {suite_hash}\nDo not read, train, tune or smoke-test "
                                     "on this data. It is scored once per final system (own-names-bench v1.3, books13).\n")
    log(f"SEALED suite_hash {suite_hash}: {len(file_sha)} files")


if __name__ == "__main__":
    main()
