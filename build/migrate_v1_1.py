#!/usr/bin/env python3
"""Brings the v1.0.0 runs into the v1.1.0 layout without changing a transcript.

Each pass row gets the fingerprint of the list it was actually made with (v1.0.0's pass
definitions: an untaught list dropped only the spoken name's own entry). Rows whose v1.0.0 list
differs from v1.1.0's (65 all-books untaught passes, where another book's entry of the same
spelling stayed on the list) therefore no longer count, and `bench run` redoes exactly those.
run.json gets the dataset fingerprint, the system's list variants and its configuration fingerprint.

usage: python build/migrate_v1_1.py RUN_DIR...
"""
import gzip
import hashlib
import json
import sys
from pathlib import Path

from own_names_bench.data import dataset_fingerprint, default_dir, load
from own_names_bench.report import SYSTEM_VARIANTS
from own_names_bench.run import config_fingerprint


def sha(entries: list[str]) -> str:
    return hashlib.sha256("\n".join(entries).encode()).hexdigest()[:16]


def v1_0_lists(b) -> dict[str, list[str]]:
    out = {}
    for clip_id in {mn["clip"] for mn in b.m["mentions"]} | {nf["clip"] for nf in b.m["name_free"]}:
        book = b.clips[clip_id]["book"]
        out[f"clip/{clip_id}/none"] = []
        for v in ("own", "all"):
            out[f"clip/{clip_id}/{v}"] = b.lists[f"{v}:{book}"]["entries"]
    for mn in b.m["mentions"]:
        book = b.clips[mn["clip"]]["book"]
        for v in ("own", "all"):
            out[f"clip/{mn['clip']}/{v}-minus/{mn['entry']}"] = [e for e in b.lists[f"{v}:{book}"]["entries"] if e != mn["entry"]]
    for ch in b.m["chapters"]:
        full = b.lists[ch["list"]]["entries"]
        un = set(ch["untaught"])
        out[f"chapter/{ch['id']}/none"] = []
        out[f"chapter/{ch['id']}/taught"] = full
        out[f"chapter/{ch['id']}/untaught"] = [e for e in full if e not in un]
    return out


def main() -> None:
    b = load(default_dir(), verify=False)
    lists = v1_0_lists(b)
    fp = dataset_fingerprint(b)
    for rd in map(Path, sys.argv[1:]):
        gz = rd / "passes.jsonl.gz"
        rows = [json.loads(line) for line in gzip.decompress(gz.read_bytes()).decode().splitlines()]
        for r in rows:
            r.setdefault("list_sha", sha(lists[r["id"]]))
        gz.write_bytes(gzip.compress(("\n".join(json.dumps(r, ensure_ascii=False) for r in rows) + "\n").encode(), mtime=0))
        meta = json.loads((rd / "run.json").read_text())
        meta.setdefault("dataset_fingerprint", fp)
        meta.setdefault("variants", list(SYSTEM_VARIANTS[meta["system"]]))
        meta.setdefault("fingerprint", config_fingerprint(meta["system"], meta["config"], fp))
        meta.setdefault("migrated", "v1.0.0 run; list fingerprints added from v1.0.0's pass definitions (build/migrate_v1_1.py)")
        (rd / "run.json").write_text(json.dumps(meta, indent=1) + "\n")
        print(rd.name, len(rows), "rows")


if __name__ == "__main__":
    main()
