"""Scores the diagnosis runs with the benchmark's own scoring code (score.score_clips, report.prop/ratio,
report.paired_suite), unchanged. Shards of one configuration (results/diag/<config>--<shard>) are read
together. Published runs come from results/runs/<label>.

Derived configuration (rule fixed before any run was scored):
  +empty  a window whose list answer is empty while its no-list text is not gets the no-list text.

usage: python diag/score.py [--md OUT.md]
"""

import argparse
import gzip
import json
import sys
from collections import defaultdict
from pathlib import Path

from own_names_bench.data import load
from own_names_bench.report import paired_suite, prop, ratio
from own_names_bench.score import score_clips

ROOT = Path(__file__).resolve().parent.parent
DATA = Path("/Users/jameslal/workspace/jl/own-names-bench-src/dataset")
PUBLISHED = ["ours", "qwen-context", "elevenlabs"]
SUITES = ["calls", "svq", "modulate", "ami"]


def read_rows(paths: list[Path]) -> dict[str, dict]:
    rows: dict[str, dict] = {}
    for d in paths:
        for name in ("passes.jsonl", "passes.jsonl.gz"):
            f = d / name
            if f.exists():
                text = gzip.decompress(f.read_bytes()).decode() if name.endswith(".gz") else f.read_text()
                for line in text.splitlines():
                    if not line.strip():
                        continue
                    r = json.loads(line)
                    if not r.get("error"):
                        rows[r["id"]] = r
    return rows


def empty_fallback(r: dict) -> str:
    wins = r.get("extra", {}).get("windows", [])
    if not wins or "final" not in wins[0]:
        return r["text"]
    out = []
    for w in wins:
        t = w["final"]
        if w.get("written") is not None and not w["written"].strip() and w.get("plain", "").strip():
            t = w["plain"]
        out.append(t)
    return " ".join(t for t in out if t)


def configs() -> dict[str, dict[str, dict]]:
    out: dict[str, dict[str, dict]] = {}
    for lab in PUBLISHED:
        out[lab] = read_rows([ROOT / "results/runs" / lab])
    groups: dict[str, list[Path]] = defaultdict(list)
    for d in sorted((ROOT / "results/diag").glob("*")):
        if d.is_dir() and not d.name.startswith("smk"):
            groups[d.name.split("--")[0]].append(d)
    for cfg, paths in groups.items():
        rows = read_rows(paths)
        out[cfg] = rows
        if any(w.get("written") is not None for r in list(rows.values())[:200] for w in r.get("extra", {}).get("windows", [])):
            out[cfg + "+empty"] = {k: dict(r, text=empty_fallback(r)) for k, r in rows.items()}
    return out


def cell(d: dict | None, scale: float = 100) -> str:
    if d is None:
        return "n/a"
    return f"{scale * d['rate']:.1f} [{scale * d['lo']:.1f}, {scale * d['hi']:.1f}]"


def pcell(d: dict | None) -> str:
    if d is None:
        return "n/a"
    s = f"{100 * d['diff']:+.1f} [{100 * d['lo']:+.1f}, {100 * d['hi']:+.1f}]"
    return f"**{s}**" if d["holds"] else s


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--md", type=Path, default=None)
    ap.add_argument("--ref", default="elevenlabs", help="paired differences against this configuration")
    args = ap.parse_args()
    b = load(DATA, verify=False)
    cfgs = configs()
    lines: list[str] = []
    items: dict[str, dict[str, dict]] = {}
    for suite in SUITES + ["books"]:
        bench = b if suite == "books" else b.suites[suite]
        P = "" if suite == "books" else f"suite/{suite}/"
        lines += [f"\n## {suite}\n",
                  "| Configuration | Names right | Untaught overwritten | Name-free items, a listed name inserted | … a name from another recording | Ordinary-word error | Mentions scored (own / untaught) | Names right − ElevenLabs | Ordinary-word error − ElevenLabs |",
                  "| --- | --- | --- | --- | --- | --- | --- | --- | --- |"]
        for cfg, rows in cfgs.items():
            texts = {k[len(P):] if False else k: r["text"] for k, r in rows.items() if k.startswith(P) and (suite != "books" or k.startswith("clip/"))}
            if not texts:
                continue
            s = score_clips(bench, texts)
            # audiobooks: only mentions and name-free clips with an own-list pass (the diag runs did not run 'all'/'xr')
            items.setdefault(suite, {})[cfg] = s
            m, nf, w = s["mentions"], s["name_free"], s["wer"]
            right = prop(m, "own_right", "book")
            over = prop(m, "own_overwritten", "book")
            ins = prop(nf, "own_inserted", "book")
            fins = prop(nf, "own_inserted_foreign", "book") if suite != "books" else None
            wer = ratio(w, "own_errors", "words", "book")
            n_own = sum("own_right" in r for r in m)
            n_unt = sum("own_overwritten" in r for r in m)
            ref = items[suite].get(args.ref)
            pr = paired_suite(s, ref) if ref is not None and cfg != args.ref else {}
            lines.append(f"| {cfg} | {cell(right)} | {cell(over)} | {cell(ins)} | {cell(fins)} | {cell(wer)} | {n_own} / {n_unt} | "
                         f"{pcell(pr.get('own_right'))} | {pcell(pr.get('own_ordinary_wer'))} |")
    md = "\n".join(lines) + "\n"
    print(md)
    if args.md:
        args.md.write_text(md)
    (ROOT / "results/diag/items.json").write_text(json.dumps(items))


if __name__ == "__main__":
    sys.exit(main())
