"""Scores the dev runs (diag/dev.py) set by set, with the benchmark's own text normalization, alignment and cluster
bootstrap (own_names_bench.text / align / stats). Clusters: the book (books sets) or the reader (LibriSpeech sets).

  names right          known items: the taught name said in the piece is written (one-to-one alignment match)
  untaught overwritten unknown items (the said name off the list): a listed name written that the reference does not have
  name-free inserted   free items: a listed name written that the reference does not have
  ordinary-word error  word error outside names (every word of a listed or said name left out of both sides)
  empty windows        windows given a shortlist whose answer is empty while the no-list text has words
  emptied items        items whose whole text is empty while the reference has words

Derived configurations, rules fixed before scoring:
  +guard   a window whose list answer is empty while its no-list text has words gets the no-list text
  +short   (analysis only) also a window whose list answer has under half the no-list text's words and at least 3
           fewer: how much a "suspiciously short" trigger could add, and how often it would fire

usage: python diag/devscore.py ITEMS.jsonl results/dev [--ref base] [--md OUT.md]
"""

import argparse
import json
import sys
from collections import defaultdict
from pathlib import Path

import numpy as np

from own_names_bench.align import align
from own_names_bench.match import match
from own_names_bench.stats import cluster_ratio_ci, paired_diff
from own_names_bench.text import find_all, name_key, name_tokens, ordinary_tokens

SETS = ["books", "books_far", "ls_short", "ls_short_far", "ls_turns", "ls_turns_far"]


def words(t: str | None) -> int:
    return len((t or "").split())


def text_of(r: dict, rule: str) -> tuple[str, int, int]:
    """The item's text under a derived rule, and (windows with a list, windows the rule's trigger fires on)."""
    out, listed, fired = [], 0, 0
    for w in r["windows"]:
        t = w["final"]
        if w.get("written") is not None:
            listed += 1
            plain, written = w.get("plain") or "", w["written"]
            empty = not written.strip() and plain.strip() and not w.get("recited")
            short = (not w.get("recited") and written.strip() and words(written) < 0.5 * words(plain) and words(plain) - words(written) >= 3)
            if rule in ("guard", "short") and empty:
                t, fired = plain, fired + 1
            elif rule == "short" and short:
                t, fired = plain, fired + 1
        out.append(t)
    return " ".join(t for t in out if t), listed, fired


def score_item(it: dict, text: str) -> dict:
    listed = [e["written"] for e in it["entries"]]
    keys = {n: name_key(n) for n in listed + ([it["want"]] if it["want"] else [])}
    name_words = frozenset(w for k in keys.values() for w in k for w in ordinary_tokens(w))
    ref_n, hyp_n = name_tokens(it["reference"]), name_tokens(text)
    row: dict = {"cluster": it["group"], "set": it["set"], "cond": it["cond"]}
    a = align(ref_n, hyp_n)
    if it["cond"] == "known":
        k = keys[it["want"]]
        occ = find_all(ref_n, k)
        if occ:
            pairs = match(a, ref_n, hyp_n, k)
            row["right"] = int(any(o in pairs for o in occ))
    wrong = 0
    for n in listed:
        k = keys[n]
        extra = len(find_all(hyp_n, k)) - len(find_all(ref_n, k))
        wrong += max(0, extra)
    if it["cond"] == "unknown":
        row["overwritten"] = int(wrong > 0)
    if it["cond"] == "free":
        row["inserted"] = int(wrong > 0)
    ref_o = [w for w in ordinary_tokens(it["reference"]) if w not in name_words]
    hyp_o = [w for w in ordinary_tokens(text) if w not in name_words]
    al = align(ref_o, hyp_o)
    row["errors"], row["words"] = al.errors, al.ref_words
    row["emptied"] = int(not text.strip() and bool(ref_o))
    return row


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("items", type=Path)
    ap.add_argument("runs", type=Path)
    ap.add_argument("--ref", default="base")
    ap.add_argument("--md", type=Path)
    args = ap.parse_args()
    items = {}
    for line in args.items.open():
        it = json.loads(line)
        items[it["id"]] = it
    runs: dict[str, dict[str, dict]] = {}
    for f in sorted(args.runs.glob("*.jsonl")):
        rows = {}
        for line in f.open():
            if line.strip():
                r = json.loads(line)
                rows[r["id"]] = r
        runs[f.stem] = rows
    common = set(items)
    for rows in runs.values():
        common &= set(rows)
    print(f"{len(common)} items scored in every run of {sorted(runs)}", file=sys.stderr)
    scored: dict[str, dict[str, dict]] = {}
    stats: dict[str, dict] = {}
    for name, rows in runs.items():
        for rule in ("", "guard", "short"):
            cfg = name + (f"+{rule}" if rule else "")
            out, listed, fired, empty_w = {}, 0, 0, 0
            for i in sorted(common):
                text, l, f = text_of(rows[i], rule or "none")
                listed += l
                fired += f
                empty_w += sum(1 for w in rows[i]["windows"] if w.get("written") is not None and not w["written"].strip()
                               and (w.get("plain") or "").strip() and not w.get("recited"))
                out[i] = score_item(items[i], text)
            scored[cfg] = out
            stats[cfg] = {"listed_windows": listed, "fired": fired, "empty_windows": empty_w,
                          "windows": sum(len(rows[i]["windows"]) for i in common)}
    lines = []
    ref = scored.get(args.ref)
    measures = [("right", "Names right"), ("overwritten", "Untaught overwritten"), ("inserted", "Name-free inserted"),
                ("emptied", "Items emptied")]
    for st in SETS:
        ids = [i for i in sorted(common) if items[i]["set"] == st]
        if not ids:
            continue
        lines += [f"\n## {st} ({len(ids)} items)\n",
                  "| Configuration | " + " | ".join(m[1] for m in measures) + " | Ordinary-word error | Empty list answers (windows) | Guard fires (share of listed windows) | "
                  + " | ".join(f"{m[1]} − {args.ref}" for m in measures[:3]) + f" | Ordinary-word error − {args.ref} |",
                  "| --- " * (len(measures) + 4 + 4) + "|"]
        for cfg, out in scored.items():
            rs = [out[i] for i in ids]
            cells = []
            for key, _ in measures:
                sub = [r for r in rs if key in r]
                if not sub:
                    cells.append("n/a")
                    continue
                p, lo, hi = cluster_ratio_ci([r[key] for r in sub], [1.0] * len(sub), [r["cluster"] for r in sub])
                cells.append(f"{100 * p:.1f} [{100 * lo:.1f}, {100 * hi:.1f}] ({sum(r[key] for r in sub)}/{len(sub)})")
            p, lo, hi = cluster_ratio_ci([r["errors"] for r in rs], [r["words"] for r in rs], [r["cluster"] for r in rs])
            cells.append(f"{100 * p:.1f} [{100 * lo:.1f}, {100 * hi:.1f}]")
            base_name = cfg.split("+")[0]
            rows = runs[base_name]
            lw = [w for i in ids for w in rows[i]["windows"] if w.get("written") is not None]
            ew = sum(1 for w in lw if not w["written"].strip() and (w.get("plain") or "").strip() and not w.get("recited"))
            cells.append(f"{ew}/{len(lw)} = {100 * ew / max(1, len(lw)):.1f}%")
            rule = cfg.split("+")[1] if "+" in cfg else ""
            fired = sum(text_of(rows[i], rule or "none")[2] for i in ids)
            cells.append(f"{100 * fired / max(1, len(lw)):.1f}%" if rule else "n/a")
            for key, _ in measures[:3]:
                if ref is None or cfg == args.ref:
                    cells.append("n/a")
                    continue
                pa = [(out[i], ref[i]) for i in ids if key in out[i] and key in ref[i]]
                if not pa:
                    cells.append("n/a")
                    continue
                d = paired_diff([a[key] for a, _ in pa], [b[key] for _, b in pa], [1.0] * len(pa), [a["cluster"] for a, _ in pa])
                s = f"{100 * d['diff']:+.1f} [{100 * d['lo']:+.1f}, {100 * d['hi']:+.1f}]"
                cells.append(f"**{s}**" if d["holds"] else s)
            if ref is None or cfg == args.ref:
                cells.append("n/a")
            else:
                d = paired_diff([out[i]["errors"] for i in ids], [ref[i]["errors"] for i in ids], [ref[i]["words"] for i in ids],
                                [out[i]["cluster"] for i in ids])
                s = f"{100 * d['diff']:+.2f} [{100 * d['lo']:+.2f}, {100 * d['hi']:+.2f}]"
                cells.append(f"**{s}**" if d["holds"] else s)
            lines.append(f"| {cfg} | " + " | ".join(cells) + " |")
    md = "\n".join(lines) + "\n"
    print(md)
    if args.md:
        args.md.write_text(md)


if __name__ == "__main__":
    np.seterr(all="ignore")
    main()
