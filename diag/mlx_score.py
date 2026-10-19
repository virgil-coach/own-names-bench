"""Scores the shipped path (ours-mlx: the Detail Keeper engine, MLX, writer merged + affine 8-bit, guard + re-read) on
every own-names-bench v1.2.0 suite, beside the existing torch runs re-scored (not re-run): ElevenLabs (published run),
v0.3.0 + fixes (results/diag/ours-fixed--*), v0.3.0 and v6j + guard + re-read (results/v06final/ours-reread-*--*).
Paired differences against ElevenLabs and against BASE (default: v0.3.0 on MLX, the app as it ships today).

The audiobook suite is a selection target under results/v07bench/PROTOCOL.md (log every look in LOOKS.md). Aggregates
only: nothing per clip is printed or written. Same scoring code as diag/final_score.py (score.score_clips,
report.prop / ratio / paired_suite, clustered by book / recording group). Never reads the sealed v1.3 suite.

usage: python diag/mlx_score.py --v12 <v1.2.0 dataset> --sys KEY=NAME=RESULTS_SUBDIR/LABEL ... [--base KEY] [--md OUT] [--json OUT]
  e.g. --sys v030-mlx="v0.3.0, MLX 8-bit (app today)"=v7crel/v030-mlx   (reads results/v7crel/v030-mlx--*)
"""

import argparse
import json
from pathlib import Path

from final_score import expected_counts, kn, measures, pct, pdiff, read_rows, shards

from own_names_bench.data import load
from own_names_bench.report import paired_suite
from own_names_bench.score import score_clips

ROOT = Path(__file__).resolve().parent.parent
R = ROOT / "results"
SUITES = ["calls", "svq", "modulate", "ami", "books"]
REFS = {"elevenlabs": ("ElevenLabs Scribe v2 (keyterms)", [R / "runs/elevenlabs"]),
        "ours-fixed": ("v0.3.0 + fixes, torch (ours-fixed)", shards(R / "diag", "ours-fixed")),
        "ours-reread-v030": ("v0.3.0 + guard + re-read, torch", shards(R / "v06final", "ours-reread-v030")),
        "ours-reread-v6j": ("v6j (v0.6.0) + guard + re-read, torch", shards(R / "v06final", "ours-reread-v6j"))}


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--v12", type=Path, required=True)
    ap.add_argument("--sys", action="append", default=[])
    ap.add_argument("--base", default="v030-mlx")
    ap.add_argument("--md", type=Path, default=None)
    ap.add_argument("--json", type=Path, default=None)
    args = ap.parse_args()
    b = load(args.v12, verify=False)
    names = {k: v[0] for k, v in REFS.items()}
    cfgs = {k: read_rows(v[1]) for k, v in REFS.items()}
    for c in args.sys:
        key, name, sub = c.split("=", 2)
        d, label = sub.rsplit("/", 1)
        names[key] = name
        cfgs[key] = read_rows(shards(R / d, label))
    expected = expected_counts(b, SUITES, cfgs)
    lines, out = [], {}
    for suite in SUITES:
        bench = b if suite == "books" else b.suites[suite]
        P = "clip/" if suite == "books" else f"suite/{suite}/"
        scored = {}
        for cfg, rows in cfgs.items():
            texts = {k: r["text"] for k, r in rows.items() if k.startswith(P)}
            if texts:
                scored[cfg] = (score_clips(bench, texts), len(texts))
        el = scored.get("elevenlabs", (None, 0))[0]
        base = scored.get(args.base, (None, 0))[0]
        elm = measures(el, suite) if el else {}
        lines += [f"\n### v1.2.0: {suite}\n",
                  f"| System | Passes scored | Names right | Untaught overwritten | Name-free items, a listed name inserted | Ordinary-word error | "
                  f"Names right − ElevenLabs | Inserted − ElevenLabs | Word error − ElevenLabs | Names right − {args.base} | "
                  f"Overwritten − {args.base} | Inserted − {args.base} | Word error − {args.base} |",
                  "| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |"]
        for cfg, (s, n) in scored.items():
            ms = measures(s, suite)
            out.setdefault(suite, {})[cfg] = {"passes": n, **ms}
            pe = paired_suite(s, el) if el is not None and cfg != "elevenlabs" else {}
            pb = paired_suite(s, base) if base is not None and cfg != args.base else {}
            out[suite][cfg]["paired_el"], out[suite][cfg]["paired_base"] = pe, pb
            ins = pct(ms["ins"]) + kn(ms["ins"])
            if cfg != "elevenlabs" and elm.get("ins"):
                ins += f"; EL {elm['ins']['k']}/{elm['ins']['n']}"
            exp = expected.get(f"{cfg}|{suite}")
            lines.append(f"| {names[cfg]} | {n}{'' if exp is None or cfg == 'elevenlabs' else f' / {exp}'} | {pct(ms['right'])}{kn(ms['right'])} | "
                         f"{pct(ms['over'])}{kn(ms['over'])} | {ins} | {pct(ms['wer'])} | {pdiff(pe.get('own_right'))} | "
                         f"{pdiff(pe.get('own_free_inserted'))} | {pdiff(pe.get('own_ordinary_wer'))} | {pdiff(pb.get('own_right'))} | "
                         f"{pdiff(pb.get('own_overwritten'))} | {pdiff(pb.get('own_free_inserted'))} | {pdiff(pb.get('own_ordinary_wer'))} |")
    md = "\n".join(lines) + "\n"
    print(md)
    if args.md:
        args.md.write_text(md)
    if args.json:
        args.json.write_text(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()
