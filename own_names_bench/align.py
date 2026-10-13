"""Word alignment of a hypothesis against a reference that may have holes.

The reference is a token sequence in which GAP stands for audio with no reference text (an
unaligned stretch of a chapter, or the place an enrollment cut was taken from). A GAP absorbs any
number of hypothesis words at no cost; everywhere else substitutions, deletions and insertions
cost one. Ties prefer a match/substitution, then a deletion, then an insertion, so the result is
the same on every machine.
"""

from dataclasses import dataclass

import numpy as np
from numba import njit

GAP = "\x00GAP"


@njit(cache=True)
def _dp(ref: np.ndarray, gap: np.ndarray, hyp: np.ndarray) -> np.ndarray:
    n, m = ref.shape[0], hyp.shape[0]
    big = 1 << 30
    d = np.empty((n + 1, m + 1), dtype=np.int32)
    back = np.empty((n + 1, m + 1), dtype=np.int8)  # 0 diagonal, 1 up (deletion), 2 left (insertion)
    d[0, 0] = 0
    back[0, 0] = -1
    for j in range(1, m + 1):
        d[0, j] = j
        back[0, j] = 2
    for i in range(1, n + 1):
        g = gap[i - 1]
        step = 0 if g else 1
        d[i, 0] = d[i - 1, 0] + step
        back[i, 0] = 1
        for j in range(1, m + 1):
            if g:
                diag = big
            else:
                diag = d[i - 1, j - 1] + (0 if ref[i - 1] == hyp[j - 1] else 1)
            up = d[i - 1, j] + step
            left = d[i, j - 1] + step
            best, how = diag, 0
            if up < best:
                best, how = up, 1
            if left < best:
                best, how = left, 2
            d[i, j] = best
            back[i, j] = how
    return back


@dataclass
class Alignment:
    errors: int  # substitutions + deletions + insertions outside gaps
    ref_words: int  # reference tokens that are not GAP
    hyp_at: list[int]  # per reference token: the hypothesis token aligned to it, or -1
    ref_of_hyp: list[int]  # per hypothesis token: reference token it is aligned to (substitution or match), or
    #   -(k+1) when it is inserted after reference token k-1 (k = 0: before the first),
    in_gap: list[bool]  # per hypothesis token: absorbed by a GAP (not scored)


def align(ref: list[str], hyp: list[str]) -> Alignment:
    vocab: dict[str, int] = {}
    r = np.array([vocab.setdefault(t, len(vocab)) for t in ref], dtype=np.int64)
    h = np.array([vocab.setdefault(t, len(vocab)) for t in hyp], dtype=np.int64)
    gap = np.array([t == GAP for t in ref], dtype=np.bool_)
    back = _dp(r, gap, h)
    i, j = len(ref), len(hyp)
    hyp_at = [-1] * len(ref)
    ref_of_hyp = [0] * len(hyp)
    in_gap = [False] * len(hyp)
    errors = 0
    while i > 0 or j > 0:
        how = back[i, j]
        if how == 0:
            hyp_at[i - 1] = j - 1
            ref_of_hyp[j - 1] = i - 1
            errors += ref[i - 1] != hyp[j - 1]
            i, j = i - 1, j - 1
        elif how == 1:
            errors += ref[i - 1] != GAP
            i -= 1
        else:
            if i > 0 and ref[i - 1] == GAP:
                in_gap[j - 1] = True
            else:
                errors += 1
            ref_of_hyp[j - 1] = -(i + 1)
            j -= 1
    return Alignment(errors, sum(t != GAP for t in ref), hyp_at, ref_of_hyp, in_gap)


def hyp_window(a: Alignment, lo: int, hi: int, n_hyp: int) -> tuple[int, int]:
    """The hypothesis tokens [start, end) that stand for reference tokens [lo, hi): those aligned
    to them and those inserted among or right after them."""
    idx = [a.hyp_at[k] for k in range(lo, hi) if a.hyp_at[k] >= 0]
    idx += [j for j in range(n_hyp) if a.ref_of_hyp[j] < 0 and lo < -a.ref_of_hyp[j] - 1 <= hi]
    if idx:
        return min(idx), max(idx) + 1
    # all deleted: the empty place between the neighbours
    before = [a.hyp_at[k] for k in range(0, lo) if a.hyp_at[k] >= 0]
    start = (max(before) + 1) if before else 0
    return start, start
