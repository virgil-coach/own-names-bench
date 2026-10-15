"""Runs ours with some of the three fixes on the dev sets (diag/dev_build.py), every window traced. The empty-answer
guard is not applied here: it only swaps a window's text, so it is derived from the trace when scoring
(diag/devscore.py), exactly.

usage: python diag/dev.py ITEMS.jsonl OUT.jsonl [--level] [--min-speech S] [--hold S] [--sets a,b]
"""

import argparse
import json
import time
from pathlib import Path

from own_names_bench.systems.ours_fixed import HOLD_S, OursFixed


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("items", type=Path)
    ap.add_argument("out", type=Path)
    ap.add_argument("--level", action="store_true")
    ap.add_argument("--min-speech", type=float, default=0.0)
    ap.add_argument("--hold", type=float, default=HOLD_S)
    ap.add_argument("--sets", default="")
    args = ap.parse_args()
    items = [json.loads(line) for line in args.items.open()]
    if args.sets:
        keep = set(args.sets.split(","))
        items = [it for it in items if it["set"] in keep]
    done = set()
    if args.out.exists():
        done = {json.loads(line)["id"] for line in args.out.open() if line.strip()}
    todo = [it for it in items if it["id"] not in done]
    print(f"{len(items)} items, {len(done)} done, {len(todo)} to go", flush=True)
    sys_ = OursFixed(name="dev", guard=False, level=args.level, min_speech_s=args.min_speech, hold_s=args.hold)
    sys_.start()
    t0 = time.time()
    with args.out.open("a") as f:
        for i, it in enumerate(todo):
            names = [e["written"] for e in it["entries"]]
            o = sys_.transcribe(Path(it["audio"]), names, it["entries"])
            f.write(json.dumps({"id": it["id"], "text": o.text, "latency_s": round(o.latency_s, 3), "windows": o.extra["windows"]}) + "\n")
            f.flush()
            if (i + 1) % 50 == 0:
                print(f"  {i + 1}/{len(todo)} {(i + 1) / (time.time() - t0):.2f} items/s", flush=True)
    print(f"DONE {args.out.name}", flush=True)


if __name__ == "__main__":
    main()
