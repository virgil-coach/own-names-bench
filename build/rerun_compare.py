"""New minus old for one hosted system, every task and metric, aggregates only.

Reads two results/scores/<run>.json made by `bench report` and prints a Markdown section: old and new
rates with clustered 95% intervals and the paired difference (same items, same clusters, the
benchmark's own bootstrap). Never prints per-item rows.

usage: uv run python build/rerun_compare.py <scores-dir> <old-label> <new-label> <title>
"""

import json
import sys
from pathlib import Path

from own_names_bench.stats import cluster_ratio_ci, paired_diff


def rate(rows, num, den, cluster):
    rs = [r for r in rows if num in r]
    if not rs:
        return None
    p, lo, hi = cluster_ratio_ci([float(r[num]) for r in rs], [float(r[den]) if den else 1.0 for r in rs], [r[cluster] for r in rs])
    return p, lo, hi, len(rs)


def pair(ra, rb, ida, num, den, cluster):
    ia = {ida(n, r): r for n, r in enumerate(ra) if num in r}
    ib = {ida(n, r): r for n, r in enumerate(rb) if num in r}
    ids = [i for i in ia if i in ib]
    if not ids:
        return None
    return paired_diff([ia[i][num] for i in ids], [ib[i][num] for i in ids], [ia[i][den] if den else 1 for i in ids],
                       [ia[i][cluster] for i in ids])


def fr(x, scale):
    if x is None:
        return "n/a"
    p, lo, hi, _ = x
    d = 2 if scale == 1 else 1
    return f"{scale * p:.{d}f} [{scale * lo:.{d}f}, {scale * hi:.{d}f}]"


def fd(x, scale):
    if x is None:
        return "n/a"
    d = 2 if scale == 1 else 1
    if x["holds"] and min(abs(scale * x["lo"]), abs(scale * x["hi"])) < 0.5 * 10 ** -d:
        d += 2  # a difference that holds but rounds to zero: show it, not "+0.0 [+0.0, +0.0]"
    s = f"{scale * x['diff']:+.{d}f} [{scale * x['lo']:+.{d}f}, {scale * x['hi']:+.{d}f}]"
    if "only_a" in x:
        s += f" ({x['only_a']} vs {x['only_b']})"
    if x["holds"]:
        s += " **holds**"
    return s


def specs(items):
    """(task, metric, rows, id function, numerator, denominator or None, cluster, scale)"""
    out = []
    c, ch = items["clips"], items["chapters"]
    by_id = lambda n, r: r["id"]
    by_clip = lambda n, r: r["clip"]
    for v, vname in (("own", "Clips, the book's own list"), ("all", "Clips, all-books list"), ("none", "Clips, no list")):
        for g in ("invented", "traditional", "all"):
            ms = [r for r in c["mentions"] if g == "all" or r["group"] == g]
            out.append((vname, f"Names right, {g}", ms, by_id, f"{v}_right", None, "book", 100))
        if v != "none":
            out.append((vname, "Untaught overwritten", c["mentions"], by_id, f"{v}_overwritten", None, "book", 100))
            out.append((vname, "Wrong name written", c["mentions"], by_id, f"{v}_wrong_name", None, "book", 100))
        out.append((vname, "Name-free: a listed name inserted" if v != "none" else "Name-free: a book name inserted",
                    c["name_free"], by_id, f"{v}_inserted", None, "book", 100))
        out.append((vname, "Ordinary-word error", c["wer"], by_clip, f"{v}_errors", "words", "book", 100))
        out.append((vname, "Full-transcript error", c["wer"], by_clip, f"{v}_full_errors", "full_words", "book", 100))
    ms = ch["mentions"]
    by_pos = lambda n, r: (r["chapter"], n)
    by_ch = lambda n, r: r["chapter"]
    for cond, cname in (("taught", "Chapters, the book's list"), ("untaught", "Chapters, half the names removed"), ("none", "Chapters, no list")):
        # keep the position index of the full mention list so items pair across runs
        idx = [(n, m) for n, m in enumerate(ms) if cond != "untaught" or not m["untaught"]]
        rows = [dict(m, _pos=n) for n, m in idx]
        pos = lambda n, r: (r["chapter"], r["_pos"])
        out.append((cname, "Names right", rows, pos, f"{cond}_right", None, "chapter", 100))
        out.append((cname, "Names right, same reader taught it", [r for r in rows if r["same_reader"]], pos, f"{cond}_right", None, "chapter", 100))
        out.append((cname, "Names right, another reader taught it", [r for r in rows if not r["same_reader"]], pos, f"{cond}_right", None, "chapter", 100))
        if cond == "untaught":
            un = [dict(m, _pos=n) for n, m in enumerate(ms) if m["untaught"]]
            out.append((cname, "Untaught overwritten", un, pos, "untaught_other", None, "chapter", 100))
        out.append((cname, "Wrong names per minute", ch["chapters"], by_ch, f"{cond}_wrong_writes", "minutes", "chapter", 1))
        out.append((cname, "Ordinary-word error", ch["chapters"], by_ch, f"{cond}_errors", "words", "chapter", 100))
        out.append((cname, "Full-transcript error", ch["chapters"], by_ch, f"{cond}_full_errors", "full_words", "chapter", 100))
    for name, s in items["suites"].items():
        t = f"Suite {name}"
        groups = sorted({r["group"] for r in s["mentions"]})
        out.append((t, "Names right", s["mentions"], by_id, "own_right", None, "book", 100))
        if len(groups) > 1:
            for g in groups:
                out.append((t, f"Names right: {g}", [r for r in s["mentions"] if r["group"] == g], by_id, "own_right", None, "book", 100))
        out.append((t, "Untaught overwritten", s["mentions"], by_id, "own_overwritten", None, "book", 100))
        out.append((t, "Wrong name written", s["mentions"], by_id, "own_wrong_name", None, "book", 100))
        out.append((t, "Name-free: items with a listed name inserted", s["name_free"], by_id, "own_inserted", None, "book", 100))
        out.append((t, "Listed names inserted per minute", s["name_free"], by_id, "own_inserted_count", "minutes", "book", 1))
        out.append((t, "Name-free: items with a name from another recording", s["name_free"], by_id, "own_inserted_foreign", None, "book", 100))
        out.append((t, "Names from other recordings inserted per minute", s["name_free"], by_id, "own_inserted_foreign_count", "minutes", "book", 1))
        out.append((t, "Ordinary-word error", s["wer"], by_clip, "own_errors", "words", "book", 100))
        out.append((t, "Full-transcript error", s["wer"], by_clip, "own_full_errors", "full_words", "book", 100))
        out.append((t, "Names right, no list", s["mentions"], by_id, "none_right", None, "book", 100))
        out.append((t, "No list: name-free items with a name inserted", s["name_free"], by_id, "none_inserted", None, "book", 100))
        out.append((t, "No list: ordinary-word error", s["wer"], by_clip, "none_errors", "words", "book", 100))
    return out


def main():
    scores, old_l, new_l, title = Path(sys.argv[1]), sys.argv[2], sys.argv[3], sys.argv[4]
    old = json.loads((scores / f"{old_l}.json").read_text())
    new = json.loads((scores / f"{new_l}.json").read_text())
    so, sn = specs(old["items"]), specs(new["items"])
    print(f"### {title}\n")
    task = None
    holds = []
    for (t, m, ro, ida, num, den, cl, sc), (_, _, rn, _, _, _, _, _) in zip(so, sn):
        a, b = rate(ro, num, den, cl), rate(rn, num, den, cl)
        if a is None and b is None:
            continue
        if t != task:
            unit = "points; per-minute rows in names per minute"
            print(f"\n**{t}**\n\n| Metric | Old ({old_l}) | New ({new_l}) | New − old ({unit}) |\n| --- | --- | --- | --- |")
            task = t
        d = pair(rn, ro, ida, num, den, cl)
        print(f"| {m} | {fr(a, sc)} | {fr(b, sc)} | {fd(d, sc)} |")
        if d and d["holds"]:
            holds.append(f"{t}: {m} {fd(d, sc)}")
    print("\nDifferences that hold: " + ("; ".join(holds) if holds else "none") + ".\n")


if __name__ == "__main__":
    main()
