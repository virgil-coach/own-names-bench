"""Window-level view of the trace runs: how often the list answer of a window is empty (or recited)
while the no-list text has words, and how many words the list answers keep, per suite."""
import json, sys
from collections import Counter
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent
cfg = sys.argv[1] if len(sys.argv) > 1 else "ours-trace"
c = Counter()
for d in sorted((ROOT / "results/diag").glob(f"{cfg}--*")):
    f = d / "passes.jsonl"
    if not f.exists():
        continue
    for line in f.read_text().splitlines():
        r = json.loads(line)
        pid = r["id"]
        s = pid.split("/")[1] if pid.startswith("suite/") else "books"
        v = "minus" if "-minus/" in pid else pid.rsplit("/", 1)[1]
        if v not in ("own", "minus"):
            continue
        for w in r["extra"]["windows"]:
            if w.get("written") is None:
                continue
            k = (s, v)
            c[k + ("win",)] += 1
            pw, ww = len(w["plain"].split()), len(w["written"].split())
            c[k + ("plain_words",)] += pw
            c[k + ("final_words",)] += len(w["final"].split())
            if pw and not ww:
                c[k + ("empty",)] += 1
            if w["recited"]:
                c[k + ("recited",)] += 1
            if pw >= 4 and ww < 0.5 * pw:
                c[k + ("halved",)] += 1
for s in ["calls", "svq", "modulate", "ami", "books"]:
    for v in ["own", "minus"]:
        n = c[(s, v, "win")]
        if n:
            print(f"{s:9s} {v:5s} windows {n:6d}  empty {100*c[(s,v,'empty')]/n:5.1f}%  under half the no-list words {100*c[(s,v,'halved')]/n:5.1f}%  "
                  f"recited {100*c[(s,v,'recited')]/n:4.1f}%  words kept {c[(s,v,'final_words')]/max(1,c[(s,v,'plain_words')]):.3f}")
