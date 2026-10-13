"""Confidence intervals and paired comparisons, all 95%.

proportion of items      Wilson score interval
word error, per minute   bootstrap over books (clips) or chapters, 10,000 resamples, seed 20261013:
                         items from one book share a reader and a text, so resampling whole books
                         is the honest unit
paired difference        system A minus system B on the same items: bootstrap over books (same
                         resamples for both), and an exact McNemar test on the discordant items
"""

import math
from collections import defaultdict
from collections.abc import Sequence

import numpy as np

Z = 1.959963984540054
RESAMPLES = 10_000
SEED = 20261013


def wilson(k: int, n: int) -> tuple[float, float]:
    if n == 0:
        return (float("nan"), float("nan"))
    p = k / n
    d = 1 + Z * Z / n
    c = (p + Z * Z / (2 * n)) / d
    h = Z * math.sqrt(p * (1 - p) / n + Z * Z / (4 * n * n)) / d
    return (max(0.0, c - h), min(1.0, c + h))


def _clusters(groups: Sequence[str]) -> tuple[list[str], np.ndarray]:
    names = sorted(set(groups))
    idx = {g: i for i, g in enumerate(names)}
    return names, np.array([idx[g] for g in groups])


def cluster_ratio_ci(num: Sequence[float], den: Sequence[float], groups: Sequence[str]) -> tuple[float, float, float]:
    """sum(num)/sum(den) with a bootstrap CI over clusters."""
    num_a, den_a = np.asarray(num, float), np.asarray(den, float)
    names, g = _clusters(groups)
    k = len(names)
    cn = np.bincount(g, weights=num_a, minlength=k)
    cd = np.bincount(g, weights=den_a, minlength=k)
    point = cn.sum() / cd.sum() if cd.sum() else float("nan")
    rng = np.random.default_rng(SEED)
    pick = rng.integers(0, k, size=(RESAMPLES, k))
    w = np.apply_along_axis(np.bincount, 1, pick, minlength=k)
    with np.errstate(invalid="ignore", divide="ignore"):
        boot = (w @ cn) / (w @ cd)
    boot = boot[np.isfinite(boot)]
    return point, float(np.percentile(boot, 2.5)), float(np.percentile(boot, 97.5))


def paired_diff(a: Sequence[float], b: Sequence[float], den: Sequence[float], groups: Sequence[str]) -> dict:
    """(sum(a) - sum(b)) / sum(den) with a cluster bootstrap CI; for 0/1 items also McNemar."""
    aa, bb, dd = np.asarray(a, float), np.asarray(b, float), np.asarray(den, float)
    names, g = _clusters(groups)
    k = len(names)
    ca = np.bincount(g, weights=aa, minlength=k)
    cb = np.bincount(g, weights=bb, minlength=k)
    cd = np.bincount(g, weights=dd, minlength=k)
    point = (ca.sum() - cb.sum()) / cd.sum()
    rng = np.random.default_rng(SEED)
    pick = rng.integers(0, k, size=(RESAMPLES, k))
    w = np.apply_along_axis(np.bincount, 1, pick, minlength=k)
    with np.errstate(invalid="ignore", divide="ignore"):
        boot = (w @ (ca - cb)) / (w @ cd)
    boot = boot[np.isfinite(boot)]
    out = {"diff": float(point), "lo": float(np.percentile(boot, 2.5)), "hi": float(np.percentile(boot, 97.5)), "n": int(len(aa))}
    if set(np.unique(aa)) <= {0.0, 1.0} and set(np.unique(bb)) <= {0.0, 1.0} and np.all(dd == 1):
        only_a = int(((aa == 1) & (bb == 0)).sum())
        only_b = int(((aa == 0) & (bb == 1)).sum())
        out.update({"only_a": only_a, "only_b": only_b, "mcnemar_p": mcnemar(only_a, only_b)})
    return out


def mcnemar(only_a: int, only_b: int) -> float:
    n = only_a + only_b
    if n == 0:
        return 1.0
    k = min(only_a, only_b)
    tail = sum(math.comb(n, i) for i in range(k + 1)) / 2**n
    return min(1.0, 2 * tail)


def group_by(rows: list[dict], key: str) -> dict[str, list[dict]]:
    out: dict[str, list[dict]] = defaultdict(list)
    for r in rows:
        out[r[key]].append(r)
    return out
