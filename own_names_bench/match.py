"""One-to-one matching of name occurrences between reference and hypothesis.

Every occurrence of a name in the reference may claim at most one occurrence of the same name in
the hypothesis, and every hypothesis occurrence may be claimed at most once. An occurrence can
only be claimed where the alignment puts it: inside the hypothesis words that stand for the
reference occurrence widened by one reference word on each side. Among candidates, a hypothesis
occurrence aligned exactly to the reference one wins, then the nearest; ties go left to right.

So "Alice Alice went home" against "Alice went home" has one name right, not two, and a name the
hypothesis writes once cannot count both as the spoken name and as a correct second mention.
"""

from .align import Alignment, hyp_window
from .text import find_all


def window(a: Alignment, n_ref: int, n_hyp: int, lo: int, hi: int) -> tuple[int, int]:
    """Hypothesis tokens standing for reference tokens [lo, hi) widened by one on each side."""
    return hyp_window(a, max(0, lo - 1), min(n_ref, hi + 1), n_hyp)


def overlaps(start: int, k: int, w: tuple[int, int]) -> bool:
    w0, w1 = w
    return w1 > w0 and start < w1 and start + k > w0


def match(a: Alignment, ref: list[str], hyp: list[str], key: tuple[str, ...]) -> dict[int, int]:
    """Reference start -> hypothesis start for the occurrences of `key`, one to one."""
    k = len(key)
    rs, hs = find_all(ref, key), find_all(hyp, key)
    if not rs or not hs:
        return {}
    cands = []
    for r in rs:
        w = window(a, len(ref), len(hyp), r, r + k)
        anchor = a.hyp_at[r] if a.hyp_at[r] >= 0 else w[0]
        for h in hs:
            if overlaps(h, k, w):
                exact = 0 if a.hyp_at[r] == h else 1
                cands.append((exact, abs(h - anchor), r, h))
    cands.sort()
    out: dict[int, int] = {}
    used: set[int] = set()
    for _, _, r, h in cands:
        if r in out or h in used:
            continue
        out[r] = h
        used.add(h)
    return out
