"""Two runs of the same pipeline on different machines or runtimes: how far apart they are.

Pass level: share of passes with identical text, and the word difference between the two texts.
Item level: for every scored outcome, how many items agree, and the paired difference with its
interval (stats.paired_diff), which is what "agree within noise" is judged on.
"""

from pathlib import Path

from .align import align
from .data import Bench
from .report import paired
from .run import load_texts
from .score import score
from .text import ordinary_tokens


def compare(b: Bench, a_dir: Path, b_dir: Path) -> dict:
    ma, ra = load_texts(a_dir)
    mb, rb = load_texts(b_dir)
    common = sorted(set(ra) & set(rb))
    same = sum(ra[i]["text"] == rb[i]["text"] for i in common)
    errs = words = 0
    shortlist_same = shortlist_n = 0
    for i in common:
        x, y = ordinary_tokens(ra[i]["text"]), ordinary_tokens(rb[i]["text"])
        al = align(x, y)
        errs += al.errors
        words += al.ref_words
        wa, wb = ra[i].get("extra", {}).get("windows"), rb[i].get("extra", {}).get("windows")
        if wa is not None and wb is not None and len(wa) == len(wb):
            for p, q in zip(wa, wb):
                if p["shortlist"]:
                    shortlist_n += 1
                    shortlist_same += p["shortlist"] == q["shortlist"]
    sa = score(b, {i: ra[i]["text"] for i in common})
    sb = score(b, {i: rb[i]["text"] for i in common})
    agree = {}
    ia = {r["id"]: r for r in sa["clips"]["mentions"]}
    ib = {r["id"]: r for r in sb["clips"]["mentions"]}
    for key in ("none_right", "own_right", "own_overwritten", "all_right", "all_overwritten"):
        ids = [i for i in ia if key in ia[i] and key in ib.get(i, {})]
        if ids:
            agree[key] = {"items": len(ids), "agree": sum(ia[i][key] == ib[i][key] for i in ids),
                          "a": sum(ia[i][key] for i in ids), "b": sum(ib[i][key] for i in ids)}
    return {
        "a": {"label": a_dir.name, "machine": ma["machine"], "config": ma["config"]},
        "b": {"label": b_dir.name, "machine": mb["machine"], "config": mb["config"]},
        "passes_compared": len(common),
        "identical_text": same,
        "word_difference_between_runs": errs / max(1, words),
        "windows_same_shortlist": {"same": shortlist_same, "of": shortlist_n},
        "items": agree,
        "paired_a_minus_b": paired(sa, sb),
    }
