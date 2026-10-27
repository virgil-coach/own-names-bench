"""Text, name and pause-cut code of the lore audiobook pipeline, vendored unchanged from own-names-bench dev/bookdev
bookdev/lore_books/pipeline.py (= lore-poc books/pipeline.py @301afec, the code that cut the v1.2.0 audiobook clips'
source): fold / parse (book text to alignment units), Lexicon / find_names (invented names: capitalised words no word
list knows, never lower case, capitalised mid-sentence, at least twice in the book), segment (chapters cut at pauses into
5-15 s pieces), reference / mentions. The only edits: the word lists are read from /usr/share/dict (the same files
pipeline.py keeps copies of; their SHA-256 is checked), and nothing here imports a recognizer.
"""
import bisect
import collections
import functools
import hashlib
import re
import unicodedata
from pathlib import Path

import numpy as np

RATE = 16000
MIN_NAME_COUNT = 2      # a name must occur at least this often in the book text
DICT = Path("/usr/share/dict")
DICT_SHA256 = {"words": "be41ad97963bf8dabedd5871d5d691596175269d540956b0f9965a885c2bbab9",
               "propernames": "626d634b40b1ad9257d0e4f16e155ea87d258dd458e9ccf94fb84bb1b63e585a"}


# ---------------------------------------------------------------- text (as gen_book.py)

EDGE = ".,;:!?()[]{}\"“”‘’'*`"
ROMAN = {"II": "second", "III": "third", "IV": "fourth", "VI": "sixth", "VII": "seventh", "VIII": "eighth",
         "IX": "ninth", "XI": "eleventh", "XII": "twelfth", "XIII": "thirteenth", "XIV": "fourteenth"}


def fold(s: str) -> str:
    s = unicodedata.normalize("NFKD", s.replace("’", "'").replace("æ", "ae").replace("Æ", "Ae"))
    return "".join(ch for ch in s.lower() if "a" <= ch <= "z" or ch == "'").strip("'")


def parse(text: str) -> tuple[list[dict], list[str]]:
    """Words of a text as alignment units (hyphenated words are split), plus display tokens."""
    text = re.sub(r"--+|—|–", " — ", text.replace("_", ""))
    units, tokens = [], []
    for para in re.split(r"\n\s*\n", text):
        trail, first = ".", True
        for raw in para.split():
            core = raw.strip(EDGE)
            lead = raw[:len(raw) - len(raw.lstrip(EDGE))]
            if not core or core == "—":
                tokens.append(raw)
                trail = "," if core == "—" else trail + raw
                continue
            this_trail = raw[len(raw.rstrip(EDGE)):]
            shown = raw
            parts = core.split("-")
            if core in ROMAN and units and units[-1]["cap"] and not first:
                parts, shown = ["the", ROMAN[core]], raw  # "Gorice XII" is read "Gorice the Twelfth"
            elif core.isupper() and sum(ch.isalpha() for ch in core) > 1:
                shown = raw.replace(core, "-".join(p.capitalize() for p in parts))
                parts = [p.capitalize() for p in parts]
            for k, part in enumerate(parts):
                norm = fold(part)
                if not norm:
                    continue
                poss = norm.endswith("'s")
                units.append({
                    "raw": re.sub(r"['’]s$", "", part) if poss else part.strip("'’"),
                    "norm": norm, "key": norm[:-2] if poss else norm.replace("'", ""), "tok": len(tokens),
                    "hyph": k > 0, "cap": part[:1].isupper(), "poss": poss,
                    "brk": k == 0 and (first or bool(trail) or bool(lead)),
                    "sent": k == 0 and (first or any(ch in trail for ch in ".!?:") or any(ch in lead for ch in "\"“‘'")),
                })
            tokens.append(shown)
            trail, first = this_trail, False
    return units, tokens


ROMAN_NUMERAL = re.compile(r"m{0,3}(cm|cd|d?c{0,3})(xc|xl|l?x{0,3})(ix|iv|v?i{0,3})")
TITLES = set("sir lord lady king queen prince princess saint god mrs miss".split())


class Lexicon:
    SUFFIXES = ["s", "es", "ed", "d", "ing", "ly", "er", "est", "ness", "ies", "ied", "men", "ful", "less", "th", "eth"]

    def __init__(self) -> None:
        from wordfreq import top_n_list
        for name, digest in DICT_SHA256.items():
            assert hashlib.sha256((DICT / name).read_bytes()).hexdigest() == digest, f"{DICT / name} differs from pipeline.py's copy"
        self.words = set(top_n_list("en", 50000))
        self.common = set(self.words) | {w.lower() for w in (DICT / "propernames").read_text().split()}
        for name in ("words", "propernames"):  # copies of macOS /usr/share/dict, as gen_book.py uses
            self.words.update(w.lower() for w in (DICT / name).read_text().split())

    def known(self, w: str) -> bool:
        if w in self.words:
            return True
        for suffix in self.SUFFIXES:
            if w.endswith(suffix) and len(w) - len(suffix) >= 3:
                stem = w[:-len(suffix)]
                if any(t in self.words for t in (stem, stem + "e", stem + "y")):
                    return True
        return False


def find_names(units: list[dict], lex: Lexicon) -> dict[tuple, dict]:
    """Invented names: runs of capitalized words that contain a word no word list
    knows, that is never written in lower case and is capitalized mid-sentence."""
    lower, mid = set(), set()
    for u in units:
        if not u["cap"]:
            lower.add(u["key"])
        elif not u["sent"]:
            mid.add(u["key"])

    @functools.cache
    def invented(key: str) -> bool:
        return len(key) >= 2 and key.isalpha() and key in mid and key not in lower and not lex.known(key) \
            and not ROMAN_NUMERAL.fullmatch(key)

    @functools.cache
    def joins(key: str) -> bool:
        """A word the lists only know by accident ("Tars" as tar+s) that the book always
        capitalizes: part of the name when it stands next to an invented word."""
        return len(key) >= 3 and key.isalpha() and key in mid and key not in lower and key not in lex.common \
            and key not in TITLES and not ROMAN_NUMERAL.fullmatch(key)

    names: dict[tuple, dict] = {}
    i = 0
    while i < len(units):
        if not units[i]["cap"]:
            i += 1
            continue
        j = i + 1
        while j < len(units) and units[j]["cap"] and (units[j]["hyph"] or not units[j]["brk"]):
            j += 1
        groups: list[list[int]] = []  # hyphenated words stay whole
        for k in range(i, j):
            if units[k]["hyph"] and groups:
                groups[-1].append(k)
            else:
                groups.append([k])
        # A name is a run of neighbouring invented words ("Brandoch Daha"); known
        # words around or between them ("Lord", "By") are not part of it.
        # Unlike gen_book.py, an always-capitalized uncommon word beside them joins ("Tars Tarkas").
        runs: list[list[list[int]]] = [[]]
        for group in groups:
            if any(invented(units[k]["key"]) for k in group) or all(joins(units[k]["key"]) for k in group):
                runs[-1].append(group)
            elif runs[-1]:
                runs.append([])
        for run in runs:
            if not run or len(run) > 4 or not any(invented(units[k]["key"]) for g in run for k in g):
                continue
            s, e = run[0][0], run[-1][-1] + 1
            key = tuple(units[k]["key"] for k in range(s, e))
            spelling = " ".join("-".join(units[k]["raw"] for k in g) for g in run)
            if sum(len(k) for k in key) >= 4:
                n = names.setdefault(key, {"key": key, "spellings": collections.Counter(), "runs": []})
                n["spellings"][spelling] += 1
                n["runs"].append((s, e))
        i = j
    for n in names.values():
        n["spelling"] = n["spellings"].most_common(1)[0][0]
    return {k: n for k, n in names.items() if len(n["runs"]) >= MIN_NAME_COUNT}


# ---------------------------------------------------------------- pieces and recognition

def segment(x: np.ndarray) -> list[tuple[int, int]]:
    """Cuts a chapter at pauses into consecutive pieces of about 5-15 s (sample ranges)."""
    hop = RATE // 100
    n = len(x) // hop
    rms = np.sqrt((x[:n * hop].reshape(n, hop) ** 2).mean(axis=1))
    quiet = rms < max(np.percentile(rms, 5) * 2.5, np.percentile(rms, 90) * 0.05)
    edges = np.flatnonzero(np.diff(np.concatenate(([0], quiet.astype(np.int8), [0]))))
    pauses = [((a + b) // 2, b - a) for a, b in zip(edges[::2].tolist(), edges[1::2].tolist()) if b - a >= 20]
    mids = [p[0] for p in pauses]
    cuts, pos = [0], 0
    while n - pos > 1500:
        cand: list[tuple[int, int]] = []
        for lo, hi in ((600, 1400), (300, 1500)):
            cand = pauses[bisect.bisect_left(mids, pos + lo):bisect.bisect_right(mids, pos + hi)]
            if cand:
                break
        if cand:
            pos = max(cand, key=lambda p: p[1])[0]
        else:
            smooth = np.convolve(rms[pos + 800:pos + 1400], np.ones(10) / 10, mode="same")
            pos = pos + 800 + int(smooth.argmin())
        cuts.append(pos)
    cuts.append(n)
    return [(a * hop, b * hop) for a, b in zip(cuts, cuts[1:])]


# ---------------------------------------------------------------- one book

def reference(units: list[dict], tokens: list[str], r0: int, r1: int) -> tuple[str, list[tuple[int, int]]]:
    """The book's text for units [r0, r1) and each unit's character span inside it."""
    t0, t1 = units[r0]["tok"], units[r1 - 1]["tok"]
    starts, at = {}, 0
    for t in range(t0, t1 + 1):
        starts[t] = at
        at += len(tokens[t]) + 1
    text = " ".join(tokens[t0:t1 + 1])
    spans, cursor = [], 0
    for u in units[r0:r1]:
        base = starts[u["tok"]]
        token = tokens[u["tok"]]
        cursor = max(cursor, base)
        found = text.find(u["raw"], cursor, base + len(token)) if u["raw"] else -1
        if found < 0:  # spoken form differs from the print ("XII" read as "the twelfth")
            spans.append((base, base + len(token)))
        else:
            spans.append((found, found + len(u["raw"])))
            cursor = found + len(u["raw"])
    return text, spans


def mentions(names: dict[tuple, dict], units: list[dict], r0: int, r1: int) -> list[tuple[dict, int, int]]:
    """Names inside units [r0, r1): the occurrences find_names recorded (they never overlap)."""
    out = []
    for n in names.values():
        lo = bisect.bisect_left(n["runs"], (r0, 0))
        for s, e in n["runs"][lo:]:
            if s >= r1:
                break
            if e <= r1:
                out.append((n, s, e))
    out.sort(key=lambda m: (m[1], m[2]))
    return out


