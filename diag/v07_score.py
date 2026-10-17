"""Scores candidates on the own-names-bench v1.2.0 audiobook clips under results/v07bench/PROTOCOL.md: the suite is a
selection target, so these numbers are not an unbiased held-out estimate; aggregates only (nothing per clip is
printed or written). Same scoring code and table format as diag/final_score.py (score.score_clips, report.prop /
ratio / paired_suite, clustered by book), with paired differences against ElevenLabs and the v6j finalist.

Reference rows are the existing runs, re-scored, not re-run: ElevenLabs (results/runs/elevenlabs), v0.3.0 + fixes
(results/diag/ours-fixed--*), v6j finalist (results/v06final/ours-reread-v6j--*).

usage: python diag/v07_score.py --v12 <v1.2.0 dataset> [--cand KEY=NAME=RESULTS_SUBDIR/LABEL]... [--md OUT] [--json OUT]
  e.g. --cand v7a="v7a + guard + re-read"=v07bench/ours-reread-v7a   (reads results/v07bench/ours-reread-v7a--*)
"""

import argparse
import json
from pathlib import Path

from final_score import kn, measures, pct, pdiff, read_rows, shards

from own_names_bench.data import load
from own_names_bench.passes import all_passes
from own_names_bench.report import paired_suite
from own_names_bench.score import score_clips

ROOT = Path(__file__).resolve().parent.parent
R = ROOT / "results"
REFS = {"elevenlabs": ("ElevenLabs Scribe v2 (keyterms)", [R / "runs/elevenlabs"]),
        "ours-fixed": ("v0.3.0 + fixes (ours-fixed)", shards(R / "diag", "ours-fixed")),
        "v6j": ("v6j finalist + guard + re-read", shards(R / "v06final", "ours-reread-v6j"))}


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--v12", type=Path, required=True)
    ap.add_argument("--cand", action="append", default=[])
    ap.add_argument("--md", type=Path, default=None)
    ap.add_argument("--json", type=Path, default=None)
    args = ap.parse_args()
    b = load(args.v12, verify=False)
    systems = dict(REFS)
    for c in args.cand:
        key, name, sub = c.split("=", 2)
        d, label = sub.rsplit("/", 1)
        systems[key] = (name, shards(R / d, label))
    want = sum(1 for p in all_passes(b, ("none", "own"), chapters=False) if p.id.startswith("clip/"))
    scored = {}
    for key, (name, dirs) in systems.items():
        texts = {k: r["text"] for k, r in read_rows(dirs).items() if k.startswith("clip/")}
        if not texts:
            raise SystemExit(f"{key}: no audiobook passes in {[str(d) for d in dirs]}")
        scored[key] = (score_clips(b, texts), len(texts))
    el, v6 = scored["elevenlabs"][0], scored["v6j"][0]
    elm = measures(el, "books")
    lines = ["| System | Passes scored | Names right | Untaught overwritten | Name-free items, a listed name inserted (ElevenLabs beside) | Ordinary-word error | Names right − ElevenLabs | Overwritten − ElevenLabs | Inserted − ElevenLabs | Word error − ElevenLabs | Names right − v6j | Overwritten − v6j | Inserted − v6j | Word error − v6j |",
             "| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |"]
    out = {}
    for key, (s, n) in scored.items():
        ms = measures(s, "books")
        out[key] = {"name": systems[key][0], "passes": n, **ms}
        pe = paired_suite(s, el) if key != "elevenlabs" else {}
        pv = paired_suite(s, v6) if key != "v6j" else {}
        ins = pct(ms["ins"]) + kn(ms["ins"]) + ("" if key == "elevenlabs" else f"; EL {elm['ins']['k']}/{elm['ins']['n']}")
        exp = "" if key == "elevenlabs" else f" / {want}"
        lines.append(f"| {systems[key][0]} | {n}{exp} | {pct(ms['right'])}{kn(ms['right'])} | {pct(ms['over'])}{kn(ms['over'])} | "
                     f"{ins} | {pct(ms['wer'])} | {pdiff(pe.get('own_right'))} | {pdiff(pe.get('own_overwritten'))} | "
                     f"{pdiff(pe.get('own_free_inserted'))} | {pdiff(pe.get('own_ordinary_wer'))} | {pdiff(pv.get('own_right'))} | "
                     f"{pdiff(pv.get('own_overwritten'))} | {pdiff(pv.get('own_free_inserted'))} | {pdiff(pv.get('own_ordinary_wer'))} |")
        out[key]["paired_el"], out[key]["paired_v6j"] = pe, pv
    md = "\n".join(lines) + "\n"
    print(md)
    if args.md:
        args.md.write_text(md)
    if args.json:
        args.json.write_text(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()
