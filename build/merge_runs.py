#!/usr/bin/env python3
"""Folds a run that was split across machines back into one: the rows of RUN_B that RUN_A lacks
(same pass id and list fingerprint) are added to RUN_A, and RUN_B's commands (with their machines)
are appended to RUN_A's run.json. Both runs must be the same system, configuration and dataset.

usage: python build/merge_runs.py RUN_A RUN_B
"""
import gzip
import json
import sys
from pathlib import Path


def rows(d: Path) -> list[dict]:
    f = d / "passes.jsonl"
    text = f.read_text() if f.exists() else gzip.decompress((d / "passes.jsonl.gz").read_bytes()).decode()
    return [json.loads(line) for line in text.splitlines()]


def main() -> None:
    a, b = Path(sys.argv[1]), Path(sys.argv[2])
    ma, mb = json.loads((a / "run.json").read_text()), json.loads((b / "run.json").read_text())
    for k in ("system", "fingerprint", "dataset_fingerprint"):
        if ma.get(k) != mb.get(k):
            raise SystemExit(f"{k} differs: {ma.get(k)} vs {mb.get(k)}")
    from own_names_bench.data import default_dir, load, suite_fingerprints
    from own_names_bench.passes import all_passes

    bench = load(default_dir(), verify=False)
    expected = {(p.id, p.list_sha) for p in all_passes(bench, tuple(ma.get("variants") or mb.get("variants")), True)}
    ra, rb = rows(a), rows(b)
    have = {(r["id"], r.get("list_sha")) for r in ra if not r.get("error")}
    new = [r for r in rb if not r.get("error") and (r["id"], r.get("list_sha")) not in have]
    # only rows of the benchmark as it is now: rows of a rebuilt suite are set aside, not merged
    merged = ra + new
    out = [r for r in merged if (r["id"], r.get("list_sha")) in expected]
    aside = [r for r in merged if (r["id"], r.get("list_sha")) not in expected]
    if aside:
        with (a / "passes.discarded.jsonl").open("a") as f:
            f.writelines(json.dumps(r, ensure_ascii=False) + "\n" for r in aside)
    (a / "passes.jsonl.gz").write_bytes(gzip.compress(("\n".join(json.dumps(r, ensure_ascii=False) for r in out) + "\n").encode(), mtime=0))
    (a / "passes.jsonl").unlink(missing_ok=True)
    known = {c["started"] for c in ma["commands"]}
    ma["commands"] += [dict(c, merged_from=b.name) for c in mb["commands"] if c["started"] not in known]
    ma["suite_fingerprints"] = suite_fingerprints(bench)
    (a / "run.json").write_text(json.dumps(ma, indent=1) + "\n")
    print(f"{a.name}: +{len(new)} rows from {b.name} ({len(out)} in all, {len(aside)} not of the current benchmark set aside)")


if __name__ == "__main__":
    main()
