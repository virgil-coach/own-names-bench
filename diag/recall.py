"""(a) Spotter recall from the published ours run: is the spoken name in the shortlist of the window it was said in?
Mention time is not in the data; it is estimated from the mention's character position in the reference
(fraction of the clip). 'any' = in the shortlist of any window of the clip (upper bound)."""
import gzip, json
from collections import defaultdict
from pathlib import Path
from own_names_bench.data import load
from own_names_bench.report import prop

ROOT = Path(__file__).resolve().parent.parent
b = load(Path("/Users/jameslal/workspace/jl/own-names-bench-src/dataset"), verify=False)
R = {}
for line in gzip.decompress((ROOT / "results/runs/ours/passes.jsonl.gz").read_bytes()).decode().splitlines():
    r = json.loads(line)
    if not r.get("error"):
        R[r["id"]] = r
items = json.loads((ROOT / "results/scores/ours.json").read_text())["items"]["suites"]
def f(d): return "n/a" if d is None else f"{100*d['rate']:.1f} [{100*d['lo']:.1f}, {100*d['hi']:.1f}] ({d['k']}/{d['n']})"
out = {}
for suite in ["calls", "svq", "modulate"]:
    S = b.suites[suite]
    mi = {r["id"]: r for r in items[suite]["mentions"]}
    rows = []
    nwin = defaultdict(int)
    for mn in S.m["mentions"]:
        if mn["id"] not in mi:
            continue
        clip = S.clips[mn["clip"]]
        r = R.get(f"suite/{suite}/clip/{mn['clip']}/own")
        if r is None: continue
        wins = r["extra"]["windows"]
        name = S.entries[mn["entry"]]["written"]
        t = (mn["span"][0] + mn["span"][1]) / 2 / max(1, len(clip["reference"])) * clip["seconds"]
        inwin = [w for w in wins if w["start_s"] - 0.3 <= t <= w["end_s"] + 0.3]
        at = any(name in w["shortlist"] for w in inwin)
        anyw = any(name in w["shortlist"] for w in wins)
        nwin[len(wins)] += 1
        rows.append({"book": mn["clip"].rsplit("-", 1)[0] if suite != "svq" else clip["book"], "group": mn["group"], "at": at, "any": anyw,
                     "single": len(wins) == 1, "right": mi[mn["id"]]["own_right"], "covered": bool(wins)})
    # use the scorer's cluster (book)
    for r, mn in zip(rows, [m for m in S.m["mentions"] if m["id"] in mi]):
        r["book"] = S.clips[mn["clip"]]["book"]
    print(f"== {suite}: windows per clip {dict(sorted(nwin.items()))}")
    for g in ["all"] + sorted({r["group"] for r in rows}):
        rs = [r for r in rows if g == "all" or r["group"] == g]
        print(f"  {g:28s} at-window {f(prop(rs,'at','book'))}  any-window {f(prop(rs,'any','book'))}  single-window clips {f(prop([r for r in rs if r['single']],'at','book'))}")
    miss = [r for r in rows if not r["any"]]
    hit = [r for r in rows if r["any"]]
    print(f"  names right when in shortlist: {f(prop([dict(r, right=float(r['right'])) for r in hit],'right','book'))}; when not: {f(prop([dict(r, right=float(r['right'])) for r in miss],'right','book'))}")
    print(f"  no window at all (Segmenter dropped the clip): {sum(not r['covered'] for r in rows)}")
