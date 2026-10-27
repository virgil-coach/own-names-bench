#!/usr/bin/env python3
"""Folds a run that was split across machines back into one: the rows of RUN_B that RUN_A lacks
(same pass id and list fingerprint) are added to RUN_A, and RUN_B's commands (with their machines)
are appended to RUN_A's run.json. Both runs must be the same system, configuration and dataset.

--local-paths KEY,...: the configurations may differ only in these keys, and only as paths on each
machine (the same adapter and binary, checked by SHA-256 when the run was made, under another home
folder). RUN_B's values are recorded with each of its commands (`config_local`).

usage: python build/merge_runs.py [--local-paths KEY,...] RUN_A RUN_B
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
    args = sys.argv[1:]
    local: list[str] = []
    if args and args[0] == "--local-paths":
        local, args = args[1].split(","), args[2:]
    a, b = Path(args[0]), Path(args[1])
    ma, mb = json.loads((a / "run.json").read_text()), json.loads((b / "run.json").read_text())
    for k in ("system", "dataset_fingerprint", "variants", "chapters"):
        if ma.get(k) != mb.get(k):
            raise SystemExit(f"{k} differs: {ma.get(k)} vs {mb.get(k)}")
    from own_names_bench.run import VOLATILE_CONFIG

    ca, cb = ma["config"], mb["config"]
    differ = sorted(k for k in set(ca) | set(cb) if k not in VOLATILE_CONFIG and ca.get(k) != cb.get(k))
    if ma.get("fingerprint") != mb.get("fingerprint") and (not differ or set(differ) - set(local)):
        raise SystemExit(f"configuration differs: {', '.join(differ) or 'fingerprint'}")
    from own_names_bench.data import default_dir, load, suite_fingerprints
    from own_names_bench.passes import all_passes

    bench = load(default_dir(), verify=False)
    expected = {(p.id, p.list_sha) for p in all_passes(bench, tuple(ma.get("variants") or mb.get("variants")), ma.get("chapters", True))}
    # one row per (pass, list): a pod's output sync can hand back a file with rows repeated
    ra = list({(r["id"], r.get("list_sha")): r for r in rows(a)}.values())
    have = {(r["id"], r.get("list_sha")) for r in ra if not r.get("error")}
    new = list({(r["id"], r.get("list_sha")): r for r in rows(b) if not r.get("error") and (r["id"], r.get("list_sha")) not in have}.values())
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
    extra = {"config_local": {k: cb.get(k) for k in differ}} if differ else {}
    ma["commands"] += [dict(c, merged_from=b.name, **extra) for c in mb["commands"] if c["started"] not in known]
    ma["suite_fingerprints"] = suite_fingerprints(bench)
    (a / "run.json").write_text(json.dumps(ma, indent=1) + "\n")
    print(f"{a.name}: +{len(new)} rows from {b.name} ({len(out)} in all, {len(aside)} not of the current benchmark set aside)")


if __name__ == "__main__":
    main()
