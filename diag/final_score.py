"""Scores the v0.6 finalist run (lore-poc ctxft/v06_amendment4_c3.md) with the benchmark's own scoring code
(score.score_clips, report.prop/ratio/paired_suite), unchanged, and applies the pre-registered ship rule (S1-S5,
N1-N3, lore-poc ctxft/v06_preregistration.md) and F1 (amendment 1) on own-names-bench v1.2.0.

Systems (shards of one run, <label>--<k>, are read together):
  v1.2.0   elevenlabs (published v1.2.0 run), ours-fixed (v0.3.0 + fixes, results/diag/ours-fixed--*),
           ours-reread-v030 (v0.3.0 + guard + re-read), ours-reread-v6j (the finalist: v6j + guard + re-read)
  conv13   the same four, each run once on the sealed v1.3 conversation suite (results/v06final/c13-*)

usage: python diag/final_score.py --v12 <v1.2.0 dataset> --conv13 <conv13 wrapped dataset> [--md OUT.md] [--json OUT.json]
"""

import argparse
import gzip
import json
from pathlib import Path

from own_names_bench.data import load
from own_names_bench.passes import all_passes
from own_names_bench.report import paired_suite, prop, ratio
from own_names_bench.score import score_clips

ROOT = Path(__file__).resolve().parent.parent
R = ROOT / "results"
V12_SUITES = ["calls", "svq", "modulate", "ami", "books"]
NAMES = {"elevenlabs": "ElevenLabs Scribe v2 (keyterms)", "ours-fixed": "v0.3.0 + fixes (ours-fixed)",
         "ours-reread-v030": "v0.3.0 + guard + re-read", "ours-reread-v6j": "**finalist: v6j + guard + re-read**"}


def read_rows(paths: list[Path]) -> dict[str, dict]:
    rows: dict[str, dict] = {}
    for d in paths:
        for name in ("passes.jsonl", "passes.jsonl.gz"):
            f = d / name
            if f.exists():
                text = gzip.decompress(f.read_bytes()).decode() if name.endswith(".gz") else f.read_text()
                for line in text.splitlines():
                    if line.strip():
                        r = json.loads(line)
                        if not r.get("error"):
                            rows[r["id"]] = r
    return rows


def shards(base: Path, label: str) -> list[Path]:
    return sorted(p for p in base.glob(f"{label}--*") if p.is_dir())


def v12_configs() -> dict[str, dict[str, dict]]:
    return {"elevenlabs": read_rows([R / "runs/elevenlabs"]), "ours-fixed": read_rows(shards(R / "diag", "ours-fixed")),
            "ours-reread-v030": read_rows(shards(R / "v06final", "ours-reread-v030")),
            "ours-reread-v6j": read_rows(shards(R / "v06final", "ours-reread-v6j"))}


def c13_configs() -> dict[str, dict[str, dict]]:
    v = R / "v06final"
    return {"elevenlabs": read_rows([v / "c13-elevenlabs"]), "ours-fixed": read_rows(shards(v, "c13-ours-fixed")),
            "ours-reread-v030": read_rows(shards(v, "c13-ours-reread-v030")), "ours-reread-v6j": read_rows(shards(v, "c13-ours-reread-v6j"))}


def pct(d: dict | None) -> str:
    return "n/a" if d is None else f"{100 * d['rate']:.1f} [{100 * d['lo']:.1f}, {100 * d['hi']:.1f}]"


def kn(d: dict | None) -> str:
    return "" if d is None else f" ({d['k']}/{d['n']})"


def pdiff(d: dict | None) -> str:
    if d is None:
        return "n/a"
    s = f"{100 * d['diff']:+.1f} [{100 * d['lo']:+.1f}, {100 * d['hi']:+.1f}]"
    return f"**{s}**" if d["holds"] else s


def measures(s: dict, suite: str) -> dict:
    m, nf, w = s["mentions"], s["name_free"], s["wer"]
    return {"right": prop(m, "own_right", "book"), "over": prop(m, "own_overwritten", "book"),
            "ins": prop(nf, "own_inserted", "book"), "fins": prop(nf, "own_inserted_foreign", "book") if suite != "books" else None,
            "wer": ratio(w, "own_errors", "words", "book")}


def table(title: str, b, suites: list[str], cfgs: dict[str, dict[str, dict]], expected: dict[str, int], out: dict) -> list[str]:
    lines: list[str] = []
    for suite in suites:
        bench = b if suite == "books" else b.suites[suite]
        P = "" if suite == "books" else f"suite/{suite}/"
        scored: dict[str, dict] = {}
        for cfg, rows in cfgs.items():
            texts = {k: r["text"] for k, r in rows.items() if k.startswith(P) and (suite != "books" or k.startswith("clip/"))}
            if texts:
                scored[cfg] = (score_clips(bench, texts), len(texts))
        if not scored:
            continue
        el = scored.get("elevenlabs", (None, 0))[0]
        fx = scored.get("ours-fixed", (None, 0))[0]
        elm = measures(el, suite) if el else {}
        lines += [f"\n### {title}: {suite}\n",
                  "| System | Passes scored | Names right | Untaught overwritten | Name-free items, a listed name inserted (ElevenLabs beside) | … a name from another recording | Ordinary-word error | Names right − ElevenLabs | Overwritten − ElevenLabs | Inserted − ElevenLabs | Word error − ElevenLabs | Names right − ours-fixed | Overwritten − ours-fixed | Inserted − ours-fixed | Word error − ours-fixed |",
                  "| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |"]
        for cfg, (s, n_passes) in scored.items():
            ms = measures(s, suite)
            out.setdefault(title, {}).setdefault(suite, {})[cfg] = ms
            pe = paired_suite(s, el) if el is not None and cfg != "elevenlabs" else {}
            pf = paired_suite(s, fx) if fx is not None and cfg != "ours-fixed" else {}
            ins = pct(ms["ins"]) + kn(ms["ins"])
            if cfg != "elevenlabs" and elm.get("ins"):
                ins += f"; EL {elm['ins']['k']}/{elm['ins']['n']}"
            exp = expected.get(f"{cfg}|{suite}")
            lines.append(f"| {NAMES[cfg]} | {n_passes}{'' if exp is None else f' / {exp}'} | {pct(ms['right'])}{kn(ms['right'])} | "
                         f"{pct(ms['over'])}{kn(ms['over'])} | {ins} | {pct(ms['fins'])}{kn(ms['fins'])} | {pct(ms['wer'])} | "
                         f"{pdiff(pe.get('own_right'))} | {pdiff(pe.get('own_overwritten'))} | {pdiff(pe.get('own_free_inserted'))} | "
                         f"{pdiff(pe.get('own_ordinary_wer'))} | {pdiff(pf.get('own_right'))} | {pdiff(pf.get('own_overwritten'))} | "
                         f"{pdiff(pf.get('own_free_inserted'))} | {pdiff(pf.get('own_ordinary_wer'))} |")
        groups = sorted({r["group"] for r in next(iter(scored.values()))[0]["mentions"]})
        if title.startswith("conv") and groups:
            lines += ["", "| System (names right by group) | " + " | ".join(groups) + " |", "| --- |" + " --- |" * len(groups)]
            for cfg, (s, _) in scored.items():
                cells = [pct(p) + kn(p) for p in (prop([r for r in s["mentions"] if r["group"] == g], "own_right", "book") for g in groups)]
                lines.append(f"| {NAMES[cfg]} | " + " | ".join(cells) + " |")
    return lines


def expected_counts(b, suites: list[str], cfgs: dict[str, dict[str, dict]]) -> dict[str, int]:
    """Passes each run should have (none + own + own-minus, no chapters, audiobooks: clips) per suite."""
    exp = [p.id for p in all_passes(b, ("none", "own"), chapters=False)]
    out = {}
    for suite in suites:
        P = "clip/" if suite == "books" else f"suite/{suite}/"
        want = [i for i in exp if i.startswith(P)]
        for cfg in cfgs:
            if cfg != "elevenlabs" or suite != "books":
                out[f"{cfg}|{suite}"] = len(want)
    return out


def rule(v12: dict) -> list[str]:
    """S1-S5, N1-N3 (pre-registration) and F1 (amendment 1), point estimates, for each ours system."""
    lines = ["\n## Ship rule on v1.2.0 (pre-registered S1-S5, N1-N3; amendment 1 F1)\n",
             "| Rule | Measure | Bar | v0.3.0 + guard + re-read | finalist (v6j + guard + re-read) |", "| --- | --- | --- | --- | --- |"]
    verdict = {}
    for cfg in ("ours-reread-v030", "ours-reread-v6j"):
        verdict[cfg] = []

    def get(suite, cfg, key):
        d = v12[suite][cfg][key]
        return None if d is None else 100 * d["rate"]

    rows = []
    for name, suite, key, op, bar_of in (
            ("S1", "calls", "right", ">", lambda: get("calls", "elevenlabs", "right")),
            ("S2", "svq", "right", ">", lambda: get("svq", "elevenlabs", "right")),
            ("S3", "modulate", "right", ">", lambda: get("modulate", "elevenlabs", "right")),
            ("S4", "ami", "wer", "<", lambda: get("ami", "elevenlabs", "wer")),
            ("S5", "books", "right", ">", lambda: get("books", "elevenlabs", "right")),
            ("S5", "books", "right", ">=", lambda: get("books", "ours-fixed", "right") - 1.0)):
        rows.append((name, suite, key, op, bar_of()))
    for suite in ("calls", "svq", "modulate", "books"):
        rows.append(("N1", suite, "over", "<=", get(suite, "ours-fixed", "over") + 0.5))
    for suite in ("calls", "svq", "ami", "books"):
        rows.append(("N2", suite, "ins", "<=", get(suite, "ours-fixed", "ins") + 0.5))
    for suite in ("calls", "svq", "modulate", "books"):
        rows.append(("N3", suite, "wer", "<=", get(suite, "ours-fixed", "wer") + 0.3))
    for suite in ("calls", "svq", "ami", "books"):
        rows.append(("F1", suite, "ins", "<", 1.0))
    label = {"right": "names right", "over": "untaught overwritten", "ins": "name-free inserted", "wer": "ordinary-word error"}
    for name, suite, key, op, bar in rows:
        cells = []
        for cfg in ("ours-reread-v030", "ours-reread-v6j"):
            v = get(suite, cfg, key)
            ok = {">": v > bar, "<": v < bar, ">=": v >= bar, "<=": v <= bar}[op]
            verdict[cfg].append((name, suite, ok))
            extra = ""
            if key == "ins":
                d = v12[suite][cfg]["ins"]
                extra = f" ({d['k']}/{d['n']})"
            cells.append(f"{v:.2f}{extra} {'pass' if ok else '**FAIL**'}")
        lines.append(f"| {name} | {suite} {label[key]} | {op} {bar:.2f} | " + " | ".join(cells) + " |")
    lines.append("")
    for cfg in ("ours-reread-v030", "ours-reread-v6j"):
        fails = [f"{n} {s}" for n, s, ok in verdict[cfg] if not ok]
        lines.append(f"- {NAMES[cfg]}: " + ("every rule holds" if not fails else "fails " + ", ".join(fails)))
    return lines


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--v12", type=Path, required=True)
    ap.add_argument("--conv13", type=Path, default=None)
    ap.add_argument("--md", type=Path, default=None)
    ap.add_argument("--json", type=Path, default=None)
    args = ap.parse_args()
    out: dict = {}
    b = load(args.v12, verify=False)
    cfgs = v12_configs()
    lines = ["## own-names-bench v1.2.0, every suite"]
    lines += table("v1.2.0", b, V12_SUITES, cfgs, expected_counts(b, V12_SUITES, cfgs), out)
    lines += rule(out["v1.2.0"])
    if args.conv13:
        c = load(args.conv13, verify=False)
        cc = c13_configs()
        names = sorted(c.suites)
        lines += ["\n## Sealed v1.3 conversation suite (suite hash dbff73e6…0fdd3), every condition"]
        lines += table("conv13", c, names, cc, expected_counts(c, names, cc), out)
    md = "\n".join(lines) + "\n"
    print(md)
    if args.md:
        args.md.write_text(md)
    if args.json:
        args.json.write_text(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()
