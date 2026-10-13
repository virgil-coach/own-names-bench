#!/usr/bin/env python3
"""Checks that no benchmark book, reader or name is in the training data of the adapter under test
(littlebearlabs/own-names-qwen3-asr-lora v0.3.0), and writes the evidence to contamination.json.

v0.3.0 trained on (its card, "Data"): LibriVox audiobook pieces of 47 training books
(attribution/librivox_books.csv, with readers), LibriTTS dev recordings and LibriTTS dev voices
cloned for synthetic speech (attribution/libritts.csv, by speaker id), no-speech pieces cut from
training-book readers, 3,000 generated names (lore-poc ctxft/gen.py, seed 2026), and YODAS video
clips (attribution/yodas_videos.csv, video ids only).

Speaker ids are turned into reader names with LibriSpeech's SPEAKERS.TXT (openslr resource 12,
raw-metadata.tar.gz). YODAS gives no speaker or channel, so YODAS voices cannot be checked by
name; that is stated, not hidden.

usage: python build/contamination.py --dataset DIR --lora DIR --speakers SPEAKERS.TXT --abn DIR --gen GEN.PY --taken TAKEN.JSON
"""

import argparse
import csv
import json
import re
from pathlib import Path

from own_names_bench.text import name_key


def base_name(reader: str) -> str:
    return re.sub(r"\s*\(.*?\)\s*", "", reader).strip().casefold()


def generated_names(gen_py: Path, taken: Path) -> list[str]:
    """The 3,000 synthetic training names, regenerated exactly as gen.py draws them."""
    src = gen_py.read_text()
    start, end = src.index("# (spoken, spellings)"), src.index("def siblings(")
    body = src[start:end]
    body = re.sub(r"TEMPLATES = .*\n", "", body)
    ns: dict = {"random": __import__("random"), "json": json, "re": re}
    exec(compile(body, str(gen_py), "exec"), ns)  # noqa: S102 - our own pinned source, run for provenance
    return [t["spelling"] for t in ns["names"](3000, set(json.loads(taken.read_text())))]


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dataset", type=Path, required=True)
    ap.add_argument("--lora", type=Path, required=True, help="v0.3.0 snapshot with attribution/")
    ap.add_argument("--speakers", type=Path, required=True)
    ap.add_argument("--abn", type=Path, required=True)
    ap.add_argument("--gen", type=Path, required=True)
    ap.add_argument("--taken", type=Path, required=True)
    args = ap.parse_args()
    m = json.loads((args.dataset / "manifest.json").read_text())

    speakers = {}
    for line in args.speakers.read_text().splitlines():
        if line.startswith(";"):
            continue
        p = [x.strip() for x in line.split("|")]
        if len(p) >= 5:
            speakers[p[0]] = {"name": p[4], "subset": p[2]}
    tts = list(csv.DictReader((args.lora / "attribution" / "libritts.csv").open()))
    tts_ids = sorted({r["speaker_id"] for r in tts})
    tts_readers = {base_name(speakers[i]["name"]): i for i in tts_ids if i in speakers}
    books = list(csv.DictReader((args.lora / "attribution" / "librivox_books.csv").open()))
    train_readers = {base_name(r) for b in books for r in b["readers"].split(";")}
    train_items = {b["archive_item"].rstrip("/").split("/")[-1] for b in books}
    train_titles = {b["title"].casefold() for b in books}

    bench_readers = sorted({c["reader"] for c in m["clips"].values()} | {c["reader"] for c in m["chapters"]}
                           | {e["reader"] for e in m["entries"].values()})
    readers = {}
    for r in bench_readers:
        b = base_name(r)
        readers[r] = {
            "in_training_audiobooks": b in train_readers,
            "libritts_speaker_used_in_training": tts_readers.get(b),
            "librispeech_ids": sorted(k for k, v in speakers.items() if base_name(v["name"]) == b),
        }
    bench_books = []
    for key, a in m["attribution"]["clips"].items():
        item = a["archive_item"].rstrip("/").split("/")[-1]
        bench_books.append({"book": key, "title": a["title"], "in_training": item in train_items or a["title"].casefold() in train_titles})
    for key, a in m["attribution"]["chapters"].items():
        item = a["archive_item"].rstrip("/").split("/")[-1]
        bench_books.append({"book": key, "title": a["title"], "in_training": item in train_items or a["title"].casefold() in train_titles})

    splits = json.loads((args.abn / "meta" / "splits.json").read_text())
    train_names = set()
    for k, v in splits["books"].items():
        if v["split"] == "train":
            dropped = set(splits["drop_names"].get(k, []))  # removed from that book's training labels
            for n in json.loads((args.abn / "meta" / "books" / k / "names.json").read_text()):
                if n["name"] not in dropped:
                    train_names.add(name_key(n["name"]))
    gen = {name_key(n) for n in generated_names(args.gen, args.taken)}
    names = {e["written"] for e in m["entries"].values()}
    hits_train = sorted(n for n in names if name_key(n) in train_names)
    hits_gen = sorted(n for n in names if name_key(n) in gen)

    out = {
        "adapter": "littlebearlabs/own-names-qwen3-asr-lora v0.3.0 (8ab4e83a)",
        "readers": readers,
        "books": bench_books,
        "names_in_training_book_lists": hits_train,
        "names_in_generated_training_names": hits_gen,
        "libritts_speakers_in_training": len(tts_ids),
        "training_audiobooks": len(books),
        "not_checkable": "YODAS clips carry no speaker or channel; a benchmark reader appearing in a training video cannot be ruled out by name.",
        "excluded_readers": m["excluded_readers"],
    }
    (args.dataset / "contamination.json").write_text(json.dumps(out, indent=1, ensure_ascii=False) + "\n")
    bad_r = [r for r, v in readers.items() if v["in_training_audiobooks"] or v["libritts_speaker_used_in_training"]]
    bad_b = [b["title"] for b in bench_books if b["in_training"]]
    print(f"readers {len(readers)}: in training {bad_r}; books {len(bench_books)}: in training {bad_b}; "
          f"names in training book lists {len(hits_train)} {hits_train[:10]}; in generated names {len(hits_gen)} {hits_gen[:10]}")


if __name__ == "__main__":
    main()
