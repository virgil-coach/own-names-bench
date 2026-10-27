"""The name guard, as the Detail Keeper engine runs it (detailkeeper engine/name-guard, guard.rs).

In a window with under SHORT_SPEECH_S of speech (first to last 20 ms frame whose RMS is at least 8% of the window's
95th percentile frame RMS, and at least 0.002), a listed name the writer wrote that the no-list text does not hold is
unverified when both
  agreement  the letter similarity (rapidfuzz normalized, letters a-z) of its spelling or of how its taught recording
             was heard to the closest 1-4 word run of the no-list text is under AGREES_AT, and
  audio      the spotter's recording match for it in this window (Hit.emb) is under SOUNDS_AT (none counts as under);
the window then gets the no-list text. Thresholds chosen on the lore v0.6 dev sets only
(lore-poc ctxft/v06_guard_amendment.md), never on benchmark items.
"""

import numpy as np
from rapidfuzz.distance import Levenshtein

from .spotter import letters, text_windows
from .writer import _pattern

SHORT_SPEECH_S = 1.2
AGREES_AT = 0.55
SOUNDS_AT = -0.48
FRAME = 320


def speech_s(x: np.ndarray) -> float:
    n = len(x) // FRAME
    if n == 0:
        return 0.0
    # RMS in float64 kept as float32, as the engine (guard.rs) and the dev measure (lore-poc ctxft/guard_spans.py)
    rms = np.sqrt((x[: n * FRAME].astype(np.float64).reshape(n, FRAME) ** 2).mean(axis=1)).astype(np.float32)
    on = np.flatnonzero(rms >= max(0.002, 0.08 * float(np.percentile(rms, 95))))
    return 0.0 if len(on) == 0 else (on[-1] - on[0] + 1) * FRAME / 16000


def agreement(plain: str, forms: list[str]) -> float:
    runs = [r for r in (letters(w) for w in text_windows(plain)) if r]
    return max((Levenshtein.normalized_similarity(f, r) for f in (letters(x) for x in forms) if f for r in runs), default=0.0)


def names_any(written: str, hits) -> bool:
    return any(_pattern(h.term.written).search(written) for h in hits)


def unverified(written: str, plain: str, hits, audio: np.ndarray):
    """The first listed name nothing backs up, or None."""
    if not hits or speech_s(audio) >= SHORT_SPEECH_S:
        return None
    for h in hits:
        name = h.term.written
        if not _pattern(name).search(written) or _pattern(name).search(plain):
            continue
        if agreement(plain, [name, h.term.heard_as]) < AGREES_AT and (h.emb is None or h.emb < SOUNDS_AT):
            return h
    return None
