#!/usr/bin/env python3
"""Builds the v1.3 audiobook test suite ("books13") in the benchmark's dataset format, so that `bench run` and
`bench report` run and score it as the clips task, with the benchmark's own passes, metrics and normalization.

The protocol is build/build_dataset.py's build_clips (the v1.2.0 clips), line for line where it can be:
  - pieces: align_book.py (pause cuts of lore_text.segment, 3.5-15 s, the book text placed by forced alignment only),
    curated by curate.py (plan.json): removed names are not names, merged spellings are variants, and a piece that says a
    name dropped for colliding with a held name is never used
  - enrollment (lore-poc books/enroll.py `cut`, held-out rules): per name, the reader's best isolated occurrence
    (forced-alignment score >= 0.3, 0.25-1.4 s for one word, no possessive, no variant), cut with 60 ms margins and
    5 ms fades; one take, the first (build_dataset.py uses the first take only)
  - glossary entries: every name with an enrollment cut; a book's own list is all of them, most frequent in the book
    first (`own:<book>`); no all-books list (see the data card)
  - name mentions: per name, PER_NAME distinct pieces (3 invented, 1 traditional) at random, never a piece an
    enrollment cut came from, no variant spellings
  - name-free pieces: pieces with no name of the book, 4-15 s, whose reference holds no listed name of any books13 book, never an enrollment piece, and stricter than the mention pieces on alignment (every word
    >= FREE_WORD_MIN, no unexplained letter frame): FREE_PER_BOOK per book at random
  - every piece whose reference shares a run of 8 words with a held text (lore, bookdev, bigcast and own-names-bench
    texts and references) is left out before sampling
Mention groups are the benchmark's: "invented" / "traditional" by the book's pool.

usage: build.py  -> data/manifest.json, data/audio/{clips,enroll}/<book>/*.flac, build/build_stats.json
"""
import hashlib
import json
import random
import re
import shutil
import sys
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np
import soundfile as sf

from common import DATA, JL, RATE, SEED, WORK, log, write_json
from own_names_bench import BENCH_NAME, BENCH_VERSION
from own_names_bench.text import NORMALIZATION_VERSION, find_all, name_key, name_tokens, nfc, ordinary_tokens

PER_NAME = {"invented": 3, "traditional": 1}
FREE_PER_BOOK = 60
FREE_SECONDS = (4.0, 15.0)
FREE_WORD_MIN = 0.5
MARGIN = 0.06
ENROLL_SCORE = 0.3
SUITE = "books13"
SUITE_VERSION = "1.3.0-test"


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def grams(text: str, n: int = 8) -> set[tuple[str, ...]]:
    t = ordinary_tokens(text)
    return {tuple(t[i:i + n]) for i in range(len(t) - n + 1)}


def held_texts() -> list[tuple[str, str]]:
    """(label, text) of every text held elsewhere whose 8-word runs a test reference may not share."""
    out = []
    for folder, label in ((JL / "lore-poc" / "books" / "texts", "lore books"),
                          (JL / "own-names-bench-wt-bookdev" / "bookdev" / "lore_books" / "texts", "bookdev"),
                          (JL / "own-names-bench-wt-bigcast" / "bigcast" / "lore_books" / "texts", "bigcast")):
        for p in sorted(folder.glob("*.txt")):
            out.append((label, p.read_text(errors="replace")))
    m = json.loads((JL / "own-names-bench-src" / "dataset" / "manifest.json").read_text())
    out += [("own-names-bench v1.2.0", c["reference"]) for c in m["clips"].values()]
    out += [("own-names-bench v1.2.0", s["reference"]) for ch in m["chapters"] for s in ch["segments"]]
    for f in ("book", "stream", "tts"):
        d = json.loads((WORK / "src" / "hf" / "lore-eval-sets" / "defs" / f"{f}.json").read_text())
        out += [("lore eval sets", it["reference"]) for it in d["items"]]
    return out


def occurrence(r: dict, m: dict) -> dict:
    """lore-poc books/enroll.py `occurrence`: the silence around a mention and whether it may be an enrollment cut."""
    inside = [i for i, w in enumerate(r["words"]) if w["span"][0] >= m["span"][0] and w["span"][1] <= m["span"][1]]
    a, b = inside[0], inside[-1] + 1
    w = r["words"]
    gap_before = round(m["start"] - (w[a - 1]["end"] if a else 0.0), 3)
    gap_after = round((w[b]["start"] if b < len(w) else r["seconds"]) - m["end"], 3)
    poss = r["reference"][m["span"][1]:m["span"][1] + 2] in ("'s", "’s")
    seconds = m["end"] - m["start"]
    ok = (not poss and not m.get("variant") and m["score"] >= ENROLL_SCORE
          and 0.25 <= seconds <= 1.4 + 0.6 * (len(inside) - 1))
    return {"piece": r["id"], "audio": r["audio"], "reader": r["reader"], "start": m["start"], "end": m["end"],
            "score": m["score"], "gap_before": gap_before, "gap_after": gap_after, "ok": ok,
            "isolation": (min(gap_before, MARGIN) + min(gap_after, MARGIN), m["score"])}


def cut_audio(book: str, o: dict) -> np.ndarray:
    """lore-poc books/enroll.py `cut_audio`."""
    samples, rate = sf.read(WORK / "books" / book / o["audio"], dtype="float32")
    assert rate == RATE
    a = max(0, int((o["start"] - min(MARGIN, max(o["gap_before"], 0.02))) * RATE))
    b = min(len(samples), int((o["end"] + min(MARGIN, max(o["gap_after"], 0.02))) * RATE))
    piece = samples[a:b].copy()
    ramp = np.linspace(0.0, 1.0, 80, dtype=np.float32)
    piece[:80] *= ramp
    piece[-80:] *= ramp[::-1]
    return piece


def write_flac(path: Path, x: np.ndarray) -> dict:
    path.parent.mkdir(parents=True, exist_ok=True)
    sf.write(path, x, RATE, format="FLAC", subtype="PCM_16")
    y, _ = sf.read(path, dtype="int16")
    return {"sha256": sha256(path), "pcm_sha256": hashlib.sha256(y.astype("<i2").tobytes()).hexdigest(),
            "seconds": round(len(y) / RATE, 3)}


def main() -> None:
    books = {b["key"]: b for b in json.loads((WORK / "books.json").read_text())["books"]}
    plan = json.loads((WORK / "plan.json").read_text())["books"]
    ex = json.loads((WORK / "excl.json").read_text())
    trained_keys = {name_key(n) for n in ex["trained_names"]}
    keys = sorted(k for k in plan if plan[k]["names"])
    stats: Counter = Counter()
    if DATA.exists():
        if any(not (p.stat().st_mode & 0o200) for p in DATA.rglob("*")):
            raise SystemExit(f"{DATA} is read-only: the suite is sealed")
        shutil.rmtree(DATA)
    DATA.mkdir(parents=True)

    log("held texts: 8-word runs")
    held = set()
    for _, t in held_texts():
        held |= grams(t)
    log(f"held 8-word runs {len(held)}")

    # ------------------------------------------------------------ pieces, curated
    pieces: dict[str, dict] = {}
    for k in keys:
        p = plan[k]
        kept, removed, merged = set(p["names"]), set(p["remove"]), p["merge"]
        dropped = set(p["drop"])
        for r in (json.loads(line) for line in (WORK / "books" / k / "pieces.jsonl").open()):
            ns = []
            for m in r["names"]:
                if m["name"] in removed:
                    continue
                if m["name"] in merged:
                    m["name"], m["variant"] = merged[m["name"]], True
                ns.append(m)
            r["names"] = ns
            if any(m["name"] in dropped for m in ns):
                stats["pieces left out: say a name dropped for a collision"] += 1
                continue
            if any(m["name"] not in kept for m in ns):
                stats["pieces left out: say a name not kept"] += 1
                continue
            if grams(r["reference"]) & held:
                stats["pieces left out: share an 8-word run with a held text"] += 1
                continue
            pieces[r["id"]] = r
    by_book = defaultdict(list)
    for r in pieces.values():
        by_book[r["book"]].append(r)

    # ------------------------------------------------------------ enrollment cuts and entries
    entries: dict[str, dict] = {}
    enroll_pieces: set[str] = set()
    name_entry: dict[tuple[str, str], str] = {}
    for k in keys:
        occ = defaultdict(list)
        for r in sorted(by_book[k], key=lambda r: r["id"]):
            for m in r["names"]:
                occ[m["name"]].append(occurrence(r, m))
        counts = {n["name"]: n["count_in_text"] for n in json.loads((WORK / "books" / k / "names.json").read_text())}
        for i, name in enumerate(sorted(occ)):
            if name_key(name) in trained_keys:
                continue
            best = sorted((o for o in occ[name] if o["ok"]), key=lambda o: o["isolation"], reverse=True)
            if not best:
                stats["names without an enrollment cut"] += 1
                continue
            o = best[0]
            nid = f"n{i:04d}"
            eid = f"{k}/{nid}"
            rel = f"audio/enroll/{k}/{nid}.flac"
            meta = write_flac(DATA / rel, cut_audio(k, o))
            src = pieces[o["piece"]]
            entries[eid] = {"id": eid, "written": nfc(name), "book": k, "reader": o["reader"], "group": books[k]["pool"],
                            "occurrences": int(counts.get(name, 0)), "sample": rel, "sample_sha256": meta["sha256"],
                            "sample_pcm_sha256": meta["pcm_sha256"], "sample_seconds": meta["seconds"],
                            "sample_source_piece": o["piece"], "sample_source_url": src["chapter_url"],
                            "sample_source_s": [round(src["start"] + o["start"], 3), round(src["start"] + o["end"], 3)],
                            "in_wikidata_name_lists": name in plan[k]["in_wikidata_name_lists"]}
            enroll_pieces.add(o["piece"])
            name_entry[(k, name)] = eid
    lists = {}
    for k in keys:
        ids = sorted((e for e in entries if entries[e]["book"] == k), key=lambda i: (-entries[i]["occurrences"], entries[i]["written"]))
        lists[f"own:{k}"] = {"kind": "own", "book": k, "entries": ids}
    all_keys = {name_key(e["written"]) for e in entries.values()}
    log(f"entries {len(entries)}")

    # ------------------------------------------------------------ mentions
    rng = random.Random(SEED + 1)
    chosen = []
    for k in keys:
        cands = defaultdict(list)
        for r in sorted(by_book[k], key=lambda r: r["id"]):
            if r["id"] in enroll_pieces:
                continue
            for m in r["names"]:
                eid = name_entry.get((k, m["name"]))
                if eid and not m.get("variant"):
                    cands[eid].append((r, m))
        for eid, its in sorted(cands.items()):
            seen, pick = set(), []
            for r, m in rng.sample(its, len(its)):
                if r["id"] in seen:
                    continue
                pick.append((r, m))
                seen.add(r["id"])
                if len(pick) == PER_NAME[books[k]["pool"]]:
                    break
            chosen += [(eid, r, m) for r, m in pick]

    # ------------------------------------------------------------ name-free pieces
    rng = random.Random(SEED + 2)
    free = []
    forbid = all_keys
    for k in keys:
        cs = []
        for r in sorted(by_book[k], key=lambda r: r["id"]):
            if r["names"] or r["id"] in enroll_pieces or not FREE_SECONDS[0] <= r["seconds"] <= FREE_SECONDS[1]:
                continue
            if r["min_word_score"] < FREE_WORD_MIN or r["unexplained_frames"] > 0:
                stats["name-free candidates left out: alignment not strict enough"] += 1
                continue
            toks = name_tokens(r["reference"])
            if any(find_all(toks, key) for key in forbid):
                stats["name-free candidates left out: a listed or training name"] += 1
                continue
            cs.append(r)
        stats[f"name-free candidates {k}"] = len(cs)
        free += rng.sample(cs, min(len(cs), FREE_PER_BOOK))

    # ------------------------------------------------------------ clips
    need = {r["id"]: r for _, r, _ in chosen} | {r["id"]: r for r in free}
    clips = {}
    for pid, r in sorted(need.items()):
        x, _ = sf.read(WORK / "books" / r["book"] / r["audio"], dtype="float32")
        rel = f"audio/clips/{r['book']}/{pid}.flac"
        meta = write_flac(DATA / rel, x)
        clips[pid] = {"id": pid, "audio": rel, "sha256": meta["sha256"], "pcm_sha256": meta["pcm_sha256"], "seconds": meta["seconds"],
                      "book": r["book"], "reader": r["reader"], "reference": nfc(r["reference"]), "source": r["chapter_url"],
                      "source_s": [r["start"], r["end"]], "align_score": r["align_score"], "min_word_score": r["min_word_score"],
                      "unexplained_frames": r["unexplained_frames"]}
    mentions = []
    for eid, r, m in chosen:
        ref = clips[r["id"]]["reference"]
        a, b = m["span"]
        if tuple(name_tokens(ref[a:b])) != name_key(entries[eid]["written"]):
            stats["mentions lost: span does not read as the name"] += 1
            continue
        mentions.append({"id": f"{r['id']}@{a}", "clip": r["id"], "entry": eid, "span": [a, b], "group": entries[eid]["group"],
                         "said_as": nfc(m["text"]), "name_at_s": [m["start"], m["end"]], "name_score": m["score"],
                         "taught_by_same_reader": entries[eid]["reader"] == r["reader"],
                         "in_wikidata_name_lists": entries[eid]["in_wikidata_name_lists"]})
    name_free = [{"id": f"free:{r['id']}", "clip": r["id"]} for r in free]

    attribution = {}
    for k in keys:
        b = books[k]
        used = sorted({clips[c]["source"] for c in clips if clips[c]["book"] == k}
                      | {e["sample_source_url"] for e in entries.values() if e["book"] == k})
        attribution[k] = {"title": b["title"], "author": b["author"], "readers": b["readers"], "librivox_id": b["librivox_id"],
                          "librivox_url": b["librivox_url"], "archive_item": f"https://archive.org/details/{b['archive_item']}",
                          "gutenberg_ids": b["gutenberg_ids"], "public_domain_basis": b["pd_basis"], "group": b["pool"],
                          "recordings_used": used}
    name_words = sorted({w for e in entries.values() for w in ordinary_tokens(e["written"]) if not w.isdigit()})
    files = {str(p.relative_to(DATA)): sha256(p) for p in sorted(DATA.rglob("*")) if p.is_file()}
    manifest = {
        "benchmark": BENCH_NAME, "version": BENCH_VERSION, "suite": SUITE, "suite_version": SUITE_VERSION, "sealed": True,
        "format_note": f"`version` is the benchmark code's data format ({BENCH_VERSION}); this folder is the held-out "
                       f"{SUITE} test suite ({SUITE_VERSION}), scored once per final system as the clips task",
        "seed": SEED, "normalization_version": NORMALIZATION_VERSION,
        "sampling": {"mentions_per_name": PER_NAME, "name_free_per_book": FREE_PER_BOOK, "name_free_seconds": list(FREE_SECONDS),
                     "enrollment": "best isolated occurrence (lore enroll.py rules), one take; no clip is a piece an enrollment cut was taken from"},
        "entries": entries, "lists": lists, "clips": dict(sorted(clips.items())), "mentions": mentions, "name_free": name_free,
        "chapters": [], "name_words": name_words, "attribution": {"clips": attribution, "chapters": {}},
        "licence": "Audio: LibriVox recordings, public domain (US). Text: Project Gutenberg texts, public domain (US). "
                   "Annotations: CC BY 4.0.",
        "files": files,
    }
    (DATA / "manifest.json").write_text(json.dumps(manifest, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    per_book = {}
    for k in keys:
        mb = [mn for mn in mentions if clips[mn["clip"]]["book"] == k]
        per_book[k] = {"pool": books[k]["pool"], "reader": books[k]["reader"], "entries": len(lists[f"own:{k}"]["entries"]),
                       "mentions": len(mb), "names_mentioned": len({mn["entry"] for mn in mb}),
                       "name_free": sum(clips[nf["clip"]]["book"] == k for nf in name_free),
                       "hours": round(sum(c["seconds"] for c in clips.values() if c["book"] == k) / 3600, 3)}
    st = {"per_book": per_book, "stats": dict(sorted(stats.items())),
          "total": {"books": len(keys), "readers": len({books[k]["reader"] for k in keys}), "entries": len(entries),
                    "mentions": len(mentions), "names_mentioned": len({m["entry"] for m in mentions}), "name_free": len(name_free),
                    "clips": len(clips), "hours": round(sum(c["seconds"] for c in clips.values()) / 3600, 3),
                    "name_free_minutes": round(sum(clips[nf["clip"]]["seconds"] for nf in name_free) / 60, 1),
                    "mentions_by_group": dict(Counter(m["group"] for m in mentions))}}
    write_json(WORK / "build_stats.json", st)
    log(json.dumps(st["total"]))


if __name__ == "__main__":
    sys.exit(main())
