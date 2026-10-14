"""Offline diagnosis from the published v1.2.0 runs (no re-running, no scoring change)."""
import gzip, json, sys
from collections import defaultdict
from pathlib import Path
import numpy as np
from own_names_bench.data import load
from own_names_bench.report import prop, ratio
from own_names_bench.text import name_key, ordinary_tokens

ROOT = Path(__file__).resolve().parent.parent
b = load(Path("/Users/jameslal/workspace/jl/own-names-bench-src/dataset"), verify=False)
items = {s: json.loads((ROOT / f"results/scores/{s}.json").read_text())["items"] for s in ["ours", "qwen-context", "qwen", "elevenlabs", "whisper"]}

def rows(run):
    out = {}
    for line in gzip.decompress((ROOT / f"results/runs/{run}/passes.jsonl.gz").read_bytes()).decode().splitlines():
        r = json.loads(line)
        if not r.get("error"):
            out[r["id"]] = r
    return out

def f(d, scale=100):
    return "n/a" if d is None else f"{scale*d['rate']:.1f} [{scale*d['lo']:.1f}, {scale*d['hi']:.1f}]"

# 1. WER by variant and by clip length (<=30 s whole for qwen/whisper; >30 s Segmenter for all)
print("## ordinary-word error, own and none, by clip length")
for suite in ["ami", "calls", "svq", "modulate"]:
    S = b.suites[suite]
    for sysn in ["ours", "qwen-context", "qwen", "elevenlabs", "whisper"]:
        w = items[sysn]["suites"][suite]["wer"]
        for v in ["own", "none"]:
            cells = []
            for lab, sel in [("all", lambda r: True), ("<=30s", lambda r: S.clips[r["clip"]]["seconds"] <= 30), (">30s", lambda r: S.clips[r["clip"]]["seconds"] > 30)]:
                rs = [r for r in w if sel(r)]
                cells.append(f"{lab} {f(ratio(rs, f'{v}_errors', 'words', 'book'))} (n={len([r for r in rs if f'{v}_errors' in r])})")
            print(suite, sysn, v, " | ".join(cells))

# 2. words written / reference words (median) on AMI and calls name-free
print("\n## words written / reference words (median over clips)")
for suite in ["ami", "calls"]:
    S = b.suites[suite]
    for run in ["ours", "qwen-context", "qwen", "elevenlabs", "whisper"]:
        R = rows(run)
        for v in ["own", "none"]:
            rat = []
            for nf in S.m["name_free"]:
                pid = f"suite/{suite}/clip/{nf['clip']}/{v}"
                if pid in R:
                    rat.append(len(ordinary_tokens(R[pid]["text"])) / max(1, len(ordinary_tokens(S.clips[nf["clip"]]["reference"]))))
            if rat:
                print(suite, run, v, f"median {np.median(rat):.3f} mean {np.mean(rat):.3f} n={len(rat)}")
