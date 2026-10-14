"""Splits a configuration's passes into N shards of about equal work, by recording (all list
variants of a clip stay in one shard, so the no-list text and spotter features are reused), using
the published ours run's per-pass latency as the work estimate. Writes podin/<name>-<k>.txt, one
pass-id prefix per line.

usage: python diag/shards.py NAME N SCOPE...     SCOPE: calls svq modulate ami books
"""

import gzip
import json
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def main() -> None:
    name, n, scopes = sys.argv[1], int(sys.argv[2]), sys.argv[3:]
    pre = tuple("clip/" if s == "books" else f"suite/{s}/" for s in scopes)
    work: dict[str, float] = defaultdict(float)
    for line in gzip.decompress((ROOT / "results/runs/ours/passes.jsonl.gz").read_bytes()).decode().splitlines():
        r = json.loads(line)
        pid = r["id"]
        if not pid.startswith(pre) or r.get("error"):
            continue
        tail = pid.split("/clip/", 1)[1] if pid.startswith("suite/") else pid[len("clip/"):]
        variant = tail.split("/", 1)[1]
        if variant.startswith(("all", "own-xr")):
            continue
        clip = pid[: pid.index("/clip/") + 6] + tail.split("/", 1)[0] + "/" if pid.startswith("suite/") else "clip/" + tail.split("/", 1)[0] + "/"
        work[clip] += r.get("latency_s") or 1.0
    bins = [[0.0, []] for _ in range(n)]
    for clip, w in sorted(work.items(), key=lambda kv: -kv[1]):
        bins.sort(key=lambda b: b[0])
        bins[0][0] += w
        bins[0][1].append(clip)
    for k, (w, clips) in enumerate(sorted(bins, key=lambda b: -b[0])):
        (ROOT / "podin" / f"{name}-{k}.txt").write_text("\n".join(sorted(clips)) + "\n")
        print(f"{name}-{k}: {len(clips)} clips, {w / 3600:.2f} h of published ours latency")


if __name__ == "__main__":
    main()
