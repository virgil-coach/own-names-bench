#!/usr/bin/env python3
"""The espeak-ng pronunciation of every benchmark name as the spotter's phoneme ids, computed once
(espeak-ng 1.52.0) and shipped, so both runtimes of `ours` use the same pronunciations whatever
espeak-ng the machine has (or none). Same conversion as the engine's spotter (`pronounce`).

usage: python build/g2p_table.py --dataset DIR --vocab vocab.json --out own_names_bench/ours_ref/g2p.json
"""
import argparse
import json
import subprocess
from pathlib import Path


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dataset", type=Path, required=True)
    ap.add_argument("--vocab", type=Path, required=True)
    ap.add_argument("--out", type=Path, required=True)
    a = ap.parse_args()
    vocab = json.loads(a.vocab.read_text())
    m = json.loads((a.dataset / "manifest.json").read_text())
    names = {e["written"] for e in m["entries"].values()}
    for ref in m.get("suites", []):
        names |= {e["written"] for e in json.loads((a.dataset / ref["file"]).read_text())["entries"].values()}
    names = sorted(names)
    version = subprocess.run(["espeak-ng", "--version"], capture_output=True, text=True, check=True).stdout.strip()
    table = {}
    for text in names:
        ipa = subprocess.run(["espeak-ng", "-q", "--ipa", "-v", "en-us", "--", text], capture_output=True, text=True, check=True).stdout
        ipa = "".join(ch for ch in ipa if ch not in "ˈˌ \n_-")
        out, i = [], 0
        while i < len(ipa):
            for size in (3, 2, 1):
                piece = ipa[i : i + size]
                if len(piece) == size and piece in vocab:
                    out.append(vocab[piece])
                    i += size
                    break
            else:
                i += 1
        table[text] = out
    a.out.write_text(json.dumps(table, ensure_ascii=False, sort_keys=True))
    print(f"{len(table)} names, {version}")


if __name__ == "__main__":
    main()
