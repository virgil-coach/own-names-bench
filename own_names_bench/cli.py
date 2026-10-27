"""bench fetch | run --system NAME | score/report | estimate --system NAME | compare RUN RUN"""

import argparse
import json
from pathlib import Path

from .data import DATASET_REVISION, check_sealed, default_dir, fetch, load
from .passes import all_passes, view


def main() -> None:
    ap = argparse.ArgumentParser(prog="bench", description="own-names-bench: spelling taught names in speech")
    ap.add_argument("--data", type=Path, default=None, help="dataset folder (default $OWN_NAMES_BENCH_DATA or ./data)")
    sub = ap.add_subparsers(dest="cmd", required=True)
    f = sub.add_parser("fetch", help="download the pinned dataset and check every file")
    f.add_argument("--revision", default=None)
    f.add_argument("--token", action="store_true", help="use this machine's Hugging Face login (only needed while the dataset is private)")
    r = sub.add_parser("run", help="run one system over every pass (resumes)")
    r.add_argument("--system", required=True)
    r.add_argument("--label", default=None, help="results/runs/<label> (default: the system name)")
    r.add_argument("--out", type=Path, default=Path("results/runs"))
    r.add_argument("--limit", type=int, default=0, help="only the first N passes (smoke test)")
    r.add_argument("--only", default="", help="only passes whose id starts with this, e.g. chapter/")
    r.add_argument("--no-chapters", action="store_true")
    r.add_argument("--hourly-usd", type=float, default=None, help="what the machine costs per hour, for cost per audio hour")
    r.add_argument("--no-sample-files", action="store_true",
                   help="do not require the taught recordings on disk (a system that takes names as text, e.g. keyterms)")
    r.add_argument("--accept-config-change", default="", metavar="REASON",
                   help="resume a run whose configuration changed, recording why (only for changes that cannot alter a transcript)")
    s = sub.add_parser("report", help="score every run and write results/scores/*.json and REPORT.md")
    s.add_argument("--runs", type=Path, default=Path("results/runs"))
    s.add_argument("--out", type=Path, default=Path("results/scores"))
    s.add_argument("--baseline", default="ours")
    s.add_argument("--only", nargs="*", default=None, help="run labels to include")
    s.add_argument("--pair", nargs=2, action="append", default=[], metavar=("RUN_A", "RUN_B"),
                   help="also compare two runs of the same system (repeatable)")
    e = sub.add_parser("estimate", help="audio hours and list-price cost of a full run")
    e.add_argument("--system", required=True)
    c = sub.add_parser("compare", help="how two runs of the same system differ, pass by pass")
    c.add_argument("a", type=Path)
    c.add_argument("b", type=Path)
    args = ap.parse_args()
    root = args.data or default_dir()

    if args.cmd == "fetch":
        fetch(root, args.revision or DATASET_REVISION, use_token=args.token)
        b = load(root)
        print(f"{root}: {len(b.m['files'])} files, all checked")
        for name, h in check_sealed(root).items():
            print(f"{root / name}: sealed suite hash {h[:8]}…{h[-5:]}, every file checked")
        return
    b = load(root, verify=args.cmd == "run", samples=not getattr(args, "no_sample_files", False))
    if args.cmd == "run":
        from .run import run
        from .systems import SYSTEMS

        system = SYSTEMS[args.system]()
        run(b, system, args.out / (args.label or args.system), chapters=not args.no_chapters, limit=args.limit,
            only=args.only, hourly_usd=args.hourly_usd, accept_config_change=args.accept_config_change)
    elif args.cmd == "report":
        from .report import build

        runs = sorted(p for p in args.runs.iterdir() if ((p / "passes.jsonl").exists() or (p / "passes.jsonl.gz").exists()) and (args.only is None or p.name in args.only))
        pairs = [(args.runs / a, args.runs / c) for a, c in args.pair]
        print(build(b, runs, args.out, args.baseline, pairs))
    elif args.cmd == "estimate":
        estimate(b, args.system)
    elif args.cmd == "compare":
        from .compare import compare

        print(json.dumps(compare(b, args.a, args.b), indent=1))


def estimate(b, system_name: str) -> None:
    from .systems import SYSTEMS

    system = SYSTEMS[system_name]()
    price = system.price()
    passes = all_passes(b, system.variants, True)
    hours = sum(p.seconds for p in passes) / 3600
    listed = [p for p in passes if p.entries]
    out = {"passes": len(passes), "audio_hours": round(hours, 2), "with_list_hours": round(sum(p.seconds for p in listed) / 3600, 2)}
    if price:
        billed = 0.0
        cost = 0.0
        for p in passes:
            n = len(system.fit(view(b, p).written(list(p.entries))).sent) if p.entries else 0
            secs = max(p.seconds, price.get("min_billable_s_over_100_terms", 0)) if n > 100 else p.seconds
            billed += secs
            cost += secs / 3600 * (price["usd_per_audio_hour_with_list"] if n else price["usd_per_audio_hour"])
        out.update({"billed_hours": round(billed / 3600, 2), "usd": round(cost, 2), "price": price})
    print(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()
