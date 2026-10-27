"""The re-read of short windows, as the Detail Keeper engine runs it (detailkeeper main ffc673a: session.rs `reread`,
detailkeeper-bench, text.rs `extract_transcript`; chosen on the lore v0.6 dev sets only, lore-poc
ctxft/v06_reread_lists_amendment.md, never on benchmark items).

A window with under REREAD_BELOW_S of speech (guard.speech_s, on the window alone) is written once more after every
window of the recording has had its first pass: its audio with up to REREAD_CONTEXT_S of the recording either side
(REREAD_MOST_S in all; the context shrinks equally first), and the shortlists of every window that span touches,
merged (best spotter score first, each entry once, ten at most). Only a window with a neighbour in that span is re-read
(a window before it that the span reaches into, or a window after it with audio of the span): a recording of one window
keeps its first pass. An answer that reads its list back, or is empty, or shares no word with the context, leaves the
first pass; otherwise the window's text is its part of the answer (`extract`), with `before` the settled text of the
window before (when the span reaches into it) and `after` the first text of the window after (when the span has
audio after the window).

`extract` is lore-poc ctxft/rl_reread.py `extract` (which agreed with the Rust on all 9,646 dev re-reads).
"""

import unicodedata

REREAD_BELOW_S = 4.0
REREAD_CONTEXT_S = 4.0
REREAD_MOST_S = 10.0


def context_s(audio_from_s: float, end_s: float) -> float:
    return min(REREAD_CONTEXT_S, max(0.0, REREAD_MOST_S - (end_s - audio_from_s)) / 2.0)


def _key(word: str) -> str:
    t = unicodedata.normalize("NFKD", word.lower())
    return "".join(c for c in t if c.isalnum() and c.isascii())


def _words(text: str) -> list[str]:
    out: list[str] = []
    for t in (text or "").split():
        if not _key(t) and out:
            out[-1] += " " + t  # punctuation on its own rides with the word before
        else:
            out.append(t)
    return out


def extract(t: str, before: str, own: str, after: str) -> str | None:
    """The part of the re-read answer `t` that is the window's, or None when it shares no word with before + own +
    after (the first pass stands then)."""
    tt = _words(t)
    ref = [(w, 0) for w in _words(before)] + [(w, 1) for w in _words(own)] + [(w, 2) for w in _words(after)]
    n, m = len(tt), len(ref)
    if n == 0:
        return None
    tk, rk = [_key(w) for w in tt], [_key(w) for w, _ in ref]
    inf = float("inf")

    def sub(a: int, b: int) -> float:
        return 0.0 if tk[a] == rk[b] else (1.0 if ref[b][1] == 1 else 1.01)

    def skip(b: int) -> float:
        return 1.0 if ref[b][1] == 1 else 0.0

    d = [[inf] * (m + 1) for _ in range(n + 1)]
    d[0][0] = 0.0
    for i in range(n + 1):
        for j in range(m + 1):
            if i == 0 and j == 0:
                continue
            best = inf
            if i and j:
                best = d[i - 1][j - 1] + sub(i - 1, j - 1)
            if j:
                best = min(best, d[i][j - 1] + skip(j - 1))
            if i:
                best = min(best, d[i - 1][j] + 1.0)
            d[i][j] = best
    label: list[int | None] = [None] * n
    i, j = n, m
    anchored = False
    while i or j:
        if i and j and d[i][j] == d[i - 1][j - 1] + sub(i - 1, j - 1):
            label[i - 1] = ref[j - 1][1]
            anchored |= tk[i - 1] == rk[j - 1]
            i, j = i - 1, j - 1
        elif j and d[i][j] == d[i][j - 1] + skip(j - 1):
            j -= 1
        else:
            i -= 1
    if not anchored:
        return None
    out = []
    for k in range(n):
        lab = label[k]
        if lab is None:
            b = next((label[x] for x in range(k - 1, -1, -1) if label[x] is not None), None)
            a = next((label[x] for x in range(k + 1, n) if label[x] is not None), None)
            if b is not None and a == b:
                lab = b
            elif b is None and a == 0:
                lab = 0
            elif a is None and b == 2:
                lab = 2
            else:
                lab = 1
        if lab == 1:
            out.append(tt[k])
    return " ".join(out)
