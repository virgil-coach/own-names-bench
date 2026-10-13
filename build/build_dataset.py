#!/usr/bin/env python3
"""Builds the own-names-bench dataset folder from the private Lore sources it was cut from.

This is the provenance of the published dataset, kept so every choice is inspectable. It needs
access to the private source repos and is not part of running the benchmark: everyone else
downloads the published dataset (`bench fetch`).

Sources (pinned):
  littlebearlabs/lore-audiobook-names @ dd90a6cb  test split: pieces, enrollment cuts, items, meta
  littlebearlabs/lore-eval-sets       @ 3def0bb7  `long` chapters, `long_enroll`, defs/long/long.json
  lore-poc git                        @ b1be458   spotting/data_book: chapter reference pieces, terms
  detailkeeper git                    @ 10b709d   common_words.txt (what counts as an ordinary word)

usage: uv run --with pyarrow==21.0.0 python build/build_dataset.py --abn DIR --evs DIR --lore-poc DIR \
           --common-words FILE --out DIR
"""

import argparse
import hashlib
import json
import random
import shutil
from collections import defaultdict
from pathlib import Path

import pyarrow.parquet as pq

from own_names_bench import BENCH_NAME, BENCH_VERSION
from own_names_bench.text import NORMALIZATION_VERSION, find_all, name_key, name_tokens, name_tokens_spans, nfc, ordinary_tokens

SEED = 20261013
SOURCES = {
    "lore-audiobook-names": "littlebearlabs/lore-audiobook-names@dd90a6cb6234ad58cabe5ef2836154cf65771d25",
    "lore-eval-sets": "littlebearlabs/lore-eval-sets@3def0bb736da8eb2486d634dc416190331e6553a",
    "lore-poc": "lore-poc@b1be458",
    "common-words": "detailkeeper@10b709d services/engine/crates/detailkeeper/src/common_words.txt",
}
# Readers whose voice is in the v0.3.0 adapter's training data. Mark Nelson is LibriTTS speaker 251
# (dev-clean): a cloned reference voice and a source of name-free real recordings in v0.3.0
# (attribution/libritts.csv). Every book he reads is left out.
EXCLUDED_READERS = {"Mark Nelson": "LibriTTS speaker 251, in own-names-qwen3-asr-lora v0.3.0 training (cloned voice, real recordings)"}
# Names of a benchmark book that also stand in the name list of a v0.3.0 training book (the
# Voelsunga Saga, train split; 0 mentions kept there, but listed). Left out of every glossary, and
# no name-free piece may say them.
TRAINED_NAMES = {"Allfather", "Midgard", "Mimir", "Niflheim", "Ymir"}
PER_NAME = {"invented": 3, "traditional": 1}
FREE_PER_BOOK = 34
FREE_SECONDS = (4.0, 15.0)
CHAPTER_BOOKS = {
    "The Gods of Pegana": "pegana",
    "The Worm Ouroboros (chapters 2-8)": "ouroboros",
    "A Dreamer's Tales": "dreamers",
    # the two readings of The Book of Wonder share one name list; each name was enrolled once, by
    # whichever reader it was first cut from, so some names are taught in the other reader's voice
    "The Book of Wonder": "wonder",
    "The Book of Wonder (version 2)": "wonder",
}


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def write(out: Path, rel: str, data: bytes) -> dict:
    p = out / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_bytes(data)
    return {"path": rel, "sha256": hashlib.sha256(data).hexdigest()}


def flac_seconds(data: bytes) -> float:
    """Duration from a FLAC STREAMINFO block."""
    assert data[:4] == b"fLaC", "not FLAC"
    info = data[8 : 8 + 34]
    rate = (info[10] << 12) | (info[11] << 4) | (info[12] >> 4)
    total = ((info[13] & 0x0F) << 32) | (info[14] << 24) | (info[15] << 16) | (info[16] << 8) | info[17]
    return round(total / rate, 3)


def locate_span(reference: str, name: str, span: list[int]) -> list[int] | None:
    """The name's char span in nfc(reference): the given span if it still reads as the name."""
    a, b = span
    return [a, b] if name_tokens(reference[a:b]) == list(name_key(name)) else None


def build_clips(args, out: Path) -> tuple[dict, list, list, dict, dict]:
    abn = args.abn
    splits = json.loads((abn / "meta" / "splits.json").read_text())
    books_meta = {b["key"]: b for b in json.loads((abn / "meta" / "books.json").read_text())["books"]}
    test_books = sorted(k for k, v in splits["books"].items() if v["split"] == "test")
    dropped_books = {k: splits["books"][k]["readers"] for k in test_books if set(splits["books"][k]["readers"]) & EXCLUDED_READERS.keys()}
    books = [k for k in test_books if k not in dropped_books]
    pool = {k: splits["books"][k]["pool"] for k in books}
    print(f"test books {len(test_books)}; dropped for reader overlap with training: {sorted(dropped_books)}")

    # ---- glossary entries: every test name with an enrollment cut, its first take
    enroll = pq.read_table(abn / "enroll" / "test-00000-of-00001.parquet").to_pylist()
    first: dict[tuple[str, str], dict] = {}
    for r in enroll:
        if r["book"] not in books:
            continue
        k = (r["book"], r["name_id"])
        if k not in first or r["take"] < first[k]["take"]:
            first[k] = r
    counts: dict[str, dict[str, int]] = {}
    for b in books:
        names = json.loads((abn / "meta" / "books" / b / "names.json").read_text())
        counts[b] = {n["name"]: int(n.get("count_in_text") or 0) for n in names}
    entries: dict[str, dict] = {}
    enroll_pieces: set[str] = set()
    trained_keys = {name_key(n) for n in TRAINED_NAMES}
    for (b, nid), r in sorted(first.items()):
        if name_key(r["name"]) in trained_keys:
            continue
        eid = f"{b}/{nid}"
        rel = f"audio/enroll/{b}/{nid}.flac"
        meta = write(out, rel, r["audio"]["bytes"])
        entries[eid] = {
            "id": eid,
            "written": nfc(r["name"]),
            "book": b,
            "reader": r["reader"],
            "group": pool[b],
            "occurrences": counts[b].get(r["name"], 0),
            "sample": rel,
            "sample_sha256": meta["sha256"],
            "sample_seconds": flac_seconds(r["audio"]["bytes"]),
            "sample_source_piece": r["piece"],
        }
        enroll_pieces.add(r["piece"])
    by_book: dict[str, list[str]] = defaultdict(list)
    for eid, e in entries.items():
        by_book[e["book"]].append(eid)
    # priority: most frequent in the book first (what a user would put first when a service caps the list)
    lists = {}
    for b in books:
        ids = sorted(by_book[b], key=lambda i: (-entries[i]["occurrences"], entries[i]["written"]))
        lists[f"own:{b}"] = {"kind": "own", "book": b, "entries": ids}
    every = sorted(entries)
    rng = random.Random(SEED)
    for b in books:
        own = lists[f"own:{b}"]["entries"]
        others = [i for i in every if entries[i]["book"] != b]
        rng.shuffle(others)
        lists[f"all:{b}"] = {"kind": "all", "book": b, "entries": own + others}
    print(f"glossary entries {len(entries)}; all-books glossary {len(every)}")

    # ---- name mentions
    items = pq.read_table(abn / "items" / "test-00000-of-00001.parquet").to_pylist()
    name_to_entry = {(entries[e]["book"], e.split("/")[1]): e for e in entries}
    cands: dict[tuple[str, str], list[dict]] = defaultdict(list)
    for it in items:
        if it["book"] not in books or it["variant"] or it["piece"] in enroll_pieces:
            continue
        eid = name_to_entry.get((it["book"], it["name_id"]))
        if eid is None:
            continue
        cands[(it["book"], eid)].append(it)
    rng = random.Random(SEED + 1)
    chosen = []
    for (b, eid), its in sorted(cands.items()):
        its = sorted(its, key=lambda x: x["id"])
        seen_pieces: set[str] = set()
        pick = []
        for it in rng.sample(its, len(its)):
            if it["piece"] in seen_pieces:
                continue
            pick.append(it)
            seen_pieces.add(it["piece"])
            if len(pick) == PER_NAME[pool[b]]:
                break
        chosen += [(eid, it) for it in pick]
    print(f"name mentions chosen {len(chosen)} for {len({e for e, _ in chosen})} names")

    # ---- name-free pieces and the audio, one pass over the test pieces
    keys = {b: [name_key(entries[e]["written"]) for e in by_book[b]] + sorted(trained_keys) for b in books}
    want = {it["piece"] for _, it in chosen}
    free_cands: dict[str, list[dict]] = defaultdict(list)
    piece_rows: dict[str, dict] = {}
    source_url: dict[str, str] = {}
    for part in sorted((abn / "pieces").glob("test-*.parquet")):
        t = pq.read_table(part, columns=["id", "book", "reader", "seconds", "reference", "names", "chapter_url"])
        for r in t.to_pylist():
            if r["id"] in enroll_pieces:
                source_url[r["id"]] = r["chapter_url"]
            if r["book"] not in books or r["id"] in enroll_pieces:
                continue
            if r["id"] in want:
                piece_rows[r["id"]] = r
            if not r["names"] and FREE_SECONDS[0] <= r["seconds"] <= FREE_SECONDS[1]:
                toks = name_tokens(r["reference"])
                if not any(find_all(toks, k) for k in keys[r["book"]]):
                    free_cands[r["book"]].append(r)
    rng = random.Random(SEED + 2)
    free = []
    for b in books:
        cs = sorted(free_cands[b], key=lambda r: r["id"])
        free += rng.sample(cs, min(len(cs), FREE_PER_BOOK))
    for r in free:
        piece_rows[r["id"]] = r
    print(f"name-free pieces {len(free)}")
    for e in entries.values():
        e["sample_source_url"] = source_url.get(e["sample_source_piece"])
    need = set(piece_rows)
    clips: dict[str, dict] = {}
    for part in sorted((abn / "pieces").glob("test-*.parquet")):
        pf = pq.ParquetFile(part)
        for g in range(pf.metadata.num_row_groups):
            ids = pf.read_row_group(g, columns=["id"]).column("id").to_pylist()
            if not need.intersection(ids):
                continue
            for r in pf.read_row_group(g, columns=["id", "audio"]).to_pylist():
                if r["id"] not in need:
                    continue
                row = piece_rows[r["id"]]
                rel = f"audio/clips/{row['book']}/{r['id']}.flac"
                meta = write(out, rel, r["audio"]["bytes"])
                clips[r["id"]] = {
                    "id": r["id"],
                    "audio": rel,
                    "sha256": meta["sha256"],
                    "seconds": flac_seconds(r["audio"]["bytes"]),
                    "book": row["book"],
                    "reader": row["reader"],
                    "reference": nfc(row["reference"]),
                    "source": row["chapter_url"],
                }
    assert set(clips) == need, f"missing audio for {len(need - set(clips))} pieces"

    mentions = []
    lost = 0
    for eid, it in chosen:
        ref = clips[it["piece"]]["reference"]
        span = locate_span(ref, it["name_text"], list(it["span"]))
        if span is None or nfc(it["reference"]) != ref:
            lost += 1
            continue
        mentions.append({"id": it["id"], "clip": it["piece"], "entry": eid, "span": span, "group": pool[entries[eid]["book"]],
                         "said_as": nfc(it["name_text"])})
    print(f"mentions kept {len(mentions)} (lost {lost} whose span did not read as the name)")
    name_free = [{"id": f"free:{r['id']}", "clip": r["id"]} for r in free]

    attribution = {}
    for b in books:
        m = books_meta[b]
        used = {clips[c]["source"] for c in clips if clips[c]["book"] == b}
        used |= {entries[e]["sample_source_url"] for e in by_book[b] if entries[e].get("sample_source_url")}
        attribution[b] = {
            "title": m["title"], "author": m["author"], "readers": splits["books"][b]["readers"],
            "librivox_id": m.get("librivox_id"), "archive_item": f"https://archive.org/details/{m['archive_item']}",
            "gutenberg_ids": m.get("gutenberg_ids"), "public_domain_basis": m.get("pd_basis"),
            "group": pool[b], "recordings_used": sorted(used),
        }
    return entries, mentions, name_free, clips, {"lists": lists, "attribution": attribution, "dropped_books": dropped_books}


def build_chapters(args, out: Path) -> tuple[dict, list, dict, dict]:
    long = json.loads((args.evs / "defs" / "long" / "long.json").read_text())
    manifest = json.loads((args.lore_poc / "spotting" / "data_book" / "manifest.json").read_text())
    terms_meta = {t["id"]: t for t in manifest["terms"] if t["origin"] == "book"}
    enroll_rows = {r["file"]: r for r in pq.read_table(args.evs / "long_enroll" / "test-00000-of-00001.parquet").to_pylist()}
    audio_rows = {r["file"]: r for r in pq.read_table(args.evs / "long" / "test-00000-of-00001.parquet").to_pylist()}
    entries: dict[str, dict] = {}
    for tid_s, t in long["terms"].items():
        tid = int(tid_s)
        m = terms_meta.get(tid)
        if m is None:
            continue
        book = CHAPTER_BOOKS[m["book"]]
        r = enroll_rows[f"long/enroll/{tid:04d}.flac"]
        rel = f"audio/enroll/chapters/{book}/{tid:04d}.flac"
        meta = write(out, rel, r["audio"]["bytes"])
        eid = f"ch-{book}/{tid:04d}"
        entries[eid] = {
            "id": eid, "written": nfc(t["spelling"]), "book": book, "reader": m["speaker"], "group": "invented",
            "occurrences": int(m.get("occurrences") or 0), "sample": rel, "sample_sha256": meta["sha256"],
            "sample_seconds": flac_seconds(r["audio"]["bytes"]),
            "sample_source_piece": m["enroll"]["same"]["utt"], "term_id": tid,
        }
    removed = set(long["removed"])
    lists = {}
    for book in sorted({e["book"] for e in entries.values()}):
        ids = sorted((i for i, e in entries.items() if e["book"] == book), key=lambda i: (-entries[i]["occurrences"], entries[i]["written"]))
        lists[f"chapter:{book}"] = {"kind": "chapter", "book": book, "entries": ids}
    chapters = []
    meta_books = {b["title"]: b for b in manifest["books"]}
    attribution = {}
    lost = 0
    for ch in long["chapters"]:
        name = ch["name"]
        info = json.loads((args.lore_poc / "spotting" / "data_book" / "long" / f"{name}.json").read_text())
        book = CHAPTER_BOOKS[info["book"]]
        r = audio_rows[f"long/{name}.flac"]
        rel = f"audio/chapters/{name}.flac"
        meta = write(out, rel, r["audio"]["bytes"])
        excluded = [[e["start_s"], e["end_s"], e["reason"]] for e in info["excluded"]]

        def inside_excluded(a: float, b: float) -> bool:
            return any(a < e[1] and e[0] < b for e in excluded)

        segments = [{"start_s": p["start_s"], "end_s": p["end_s"], "reference": nfc(p["reference"])}
                    for p in info["pieces"] if not inside_excluded(p["start_s"], p["end_s"])]
        # mentions: each matched to an occurrence of the name in its segment, in order
        by_seg: dict[int, list[dict]] = defaultdict(list)
        for mn in ch["mentions"]:
            if not mn.get("target"):
                continue
            mid = (mn["start_s"] + mn["end_s"]) / 2
            si = next((i for i, s in enumerate(segments) if s["start_s"] <= mid < s["end_s"]), None)
            if si is None:
                continue
            by_seg[si].append(mn)
        mentions = []
        for si, mns in sorted(by_seg.items()):
            seg = segments[si]
            toks = name_tokens_spans(seg["reference"])
            words = [t for t, _, _ in toks]
            groups: dict[int, list[dict]] = defaultdict(list)
            for mn in sorted(mns, key=lambda m: m["start_s"]):
                groups[mn["term_id"]].append(mn)
            for tid, ms in groups.items():
                eid = f"ch-{book}/{tid:04d}"
                if eid not in entries:
                    lost += len(ms)
                    continue
                at = find_all(words, name_key(entries[eid]["written"]))
                if len(at) != len(ms):
                    lost += len(ms)
                    continue
                k = len(name_key(entries[eid]["written"]))
                for mn, i in zip(ms, at):
                    mentions.append({"segment": si, "entry": eid, "span": [toks[i][1], toks[i + k - 1][2]],
                                     "start_s": mn["start_s"], "end_s": mn["end_s"],
                                     "taught_by_same_reader": entries[eid]["reader"] == ch["reader"]})
        chapters.append({
            "id": name, "audio": rel, "sha256": meta["sha256"], "seconds": round(ch["seconds"], 3), "book": book,
            "reader": ch["reader"], "list": f"chapter:{book}",
            "untaught": sorted(e for e in lists[f"chapter:{book}"]["entries"] if entries[e]["term_id"] in removed),
            "segments": segments, "excluded": excluded, "mentions": mentions, "source": info["url"],
        })
        mb = meta_books[info["book"]]
        a = attribution.setdefault(info["book"], {"title": mb["title"], "author": mb["author"], "readers": [],
                                                  "archive_item": mb["audio_url"], "text": mb["text_url"], "recordings_used": []})
        if ch["reader"] not in a["readers"]:
            a["readers"].append(ch["reader"])
        a["recordings_used"].append(info["url"])
    print(f"chapters {len(chapters)}; chapter entries {len(entries)}; mentions {sum(len(c['mentions']) for c in chapters)} (lost {lost})")
    return entries, chapters, lists, attribution


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--abn", type=Path, required=True)
    ap.add_argument("--evs", type=Path, required=True)
    ap.add_argument("--lore-poc", type=Path, required=True)
    ap.add_argument("--common-words", type=Path, required=True)
    ap.add_argument("--out", type=Path, required=True)
    args = ap.parse_args()
    out = args.out
    if out.exists():
        shutil.rmtree(out)
    out.mkdir(parents=True)
    common = frozenset(args.common_words.read_text(encoding="utf-8").split())
    entries, mentions, name_free, clips, extra = build_clips(args, out)
    ch_entries, chapters, ch_lists, ch_attr = build_chapters(args, out)
    entries.update(ch_entries)
    lists = {**extra["lists"], **ch_lists}
    name_words = sorted({w for e in entries.values() for w in ordinary_tokens(e["written"]) if w not in common and not w.isdigit()})
    files = {}
    for p in sorted(out.rglob("*")):
        if p.is_file():
            files[str(p.relative_to(out))] = sha256(p)
    manifest = {
        "benchmark": BENCH_NAME,
        "version": BENCH_VERSION,
        "seed": SEED,
        "normalization_version": NORMALIZATION_VERSION,
        "sources": SOURCES,
        "excluded_readers": EXCLUDED_READERS,
        "excluded_books": extra["dropped_books"],
        "excluded_names": {"names": sorted(TRAINED_NAMES), "why": "in the name list of a v0.3.0 training book (Voelsunga Saga)"},
        "sampling": {"mentions_per_name": PER_NAME, "name_free_per_book": FREE_PER_BOOK, "name_free_seconds": list(FREE_SECONDS),
                     "enrollment": "first take of each name; no clip is a piece an enrollment cut was taken from"},
        "entries": entries,
        "lists": lists,
        "clips": dict(sorted(clips.items())),
        "mentions": mentions,
        "name_free": name_free,
        "chapters": chapters,
        "name_words": name_words,
        "attribution": {"clips": extra["attribution"], "chapters": ch_attr},
        "files": files,
    }
    (out / "manifest.json").write_text(json.dumps(manifest, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    secs = sum(c["seconds"] for c in clips.values())
    print(f"wrote {out}: {len(files)} audio files, {len(clips)} clips ({secs / 3600:.2f} h), {len(chapters)} chapters "
          f"({sum(c['seconds'] for c in chapters) / 3600:.2f} h), {len(entries)} entries, {len(name_words)} name words")


if __name__ == "__main__":
    main()
