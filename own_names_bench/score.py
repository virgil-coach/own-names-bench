"""Scoring. Every system's text is scored by the same rules; nothing here knows which system wrote it.

A name is written right when its name tokens (text.py) appear, in order, at the place of the
mention: the hypothesis words aligned (align.py) to the mention's reference words, widened by one
reference word on each side. Case, punctuation, hyphens and a possessive 's do not matter;
letters and diacritics do.

Clip items (each name mention), per list variant (own, all):
  right        known pass: the spoken name is on the list and written right
  wrong_name   known pass: another listed name written at the mention instead
  overwritten  untaught pass (the spoken name taken off the list): a listed name written at the mention
  right_untaught  untaught pass: the spoken name written right anyway
  none_right   no-list pass: written right with no list at all
Name-free pieces: inserted = a listed name appears anywhere in the text.
Ordinary-word error: Whisper-normalized words, every word of any benchmark name removed from
both sides (manifest `name_words`), errors / reference words, over the full-list passes.

Chapters (taught / untaught / none): right per mention, wrong writes = a listed name written
where the reference has no such name (outside the unscored holes), per scored minute;
overwritten = an untaught name's mention written as a listed name; ordinary-word error.
"""

from dataclasses import dataclass, field

from .align import GAP, Alignment, align, hyp_window
from .data import Bench
from .text import find_all, name_key, name_tokens, name_tokens_spans, ordinary_tokens


def _span_tokens(spans: list[tuple[str, int, int]], a: int, b: int) -> tuple[int, int]:
    idx = [k for k, (_, s, e) in enumerate(spans) if s < b and e > a]
    return (idx[0], idx[-1] + 1) if idx else (-1, -1)


def _occurs_in(tokens: list[str], key: tuple[str, ...], lo: int, hi: int) -> bool:
    """`key` occurs in tokens overlapping [lo, hi)."""
    k = len(key)
    return any(s < hi and s + k > lo for s in find_all(tokens, key))


@dataclass
class Ref:
    tokens: list[str]                 # name tokens, GAP where there is no reference
    ordinary: list[str]               # ordinary tokens less name words, GAP likewise
    keys_here: set = field(default_factory=set)


def _ordinary(text: str, name_words: frozenset[str]) -> list[str]:
    return [w for w in ordinary_tokens(text) if w not in name_words]


def _at_mention(a: Alignment, ref: list[str], hyp: list[str], lo: int, hi: int) -> tuple[int, int]:
    return hyp_window(a, max(0, lo - 1), min(len(ref), hi + 1), len(hyp))


def _wer(ref: list[str], hyp: list[str]) -> tuple[int, int]:
    a = align(ref, hyp)
    return a.errors, a.ref_words


def score_clips(b: Bench, texts: dict[str, str]) -> dict:
    """texts: pass id -> text. Returns per-item outcomes (missing passes are left out)."""
    nw = frozenset(b.m["name_words"])
    keys = {e: name_key(v["written"]) for e, v in b.entries.items()}
    cache: dict[str, tuple[list[str], Alignment]] = {}
    refs = {cid: name_tokens_spans(c["reference"]) for cid, c in b.clips.items()}

    def aligned(pid: str, clip: str) -> tuple[list[str], Alignment] | None:
        if pid not in texts:
            return None
        if pid not in cache:
            hyp = name_tokens(texts[pid])
            cache[pid] = (hyp, align([t for t, _, _ in refs[clip]], hyp))
        return cache[pid]

    mentions = []
    for mn in b.m["mentions"]:
        clip = mn["clip"]
        spans = refs[clip]
        ref = [t for t, _, _ in spans]
        lo, hi = _span_tokens(spans, *mn["span"])
        target = keys[mn["entry"]]
        book = b.clips[clip]["book"]
        row = {"id": mn["id"], "clip": clip, "entry": mn["entry"], "book": book, "group": mn["group"]}

        def look(pid: str, listed: list[str]) -> dict | None:
            got = aligned(pid, clip)
            if got is None:
                return None
            hyp, a = got
            h0, h1 = _at_mention(a, ref, hyp, lo, hi)
            right = _occurs_in(hyp, target, h0, h1)
            others = [e for e in listed if e != mn["entry"] and keys[e] != target
                      and _occurs_in(hyp, keys[e], h0, h1) and not _occurs_in(ref, keys[e], max(0, lo - 1), hi + 1)]
            return {"right": right, "other": bool(others)}

        own = b.lists[f"own:{book}"]["entries"]
        r = look(f"clip/{clip}/none", own)
        if r is not None:
            row["none_right"] = r["right"]
        for v in ("own", "all"):
            full = b.lists[f"{v}:{book}"]["entries"]
            k = look(f"clip/{clip}/{v}", full)
            if k is not None:
                row[f"{v}_right"] = k["right"]
                row[f"{v}_wrong_name"] = k["other"]
            u = look(f"clip/{clip}/{v}-minus/{mn['entry']}", [e for e in full if e != mn["entry"]])
            if u is not None:
                row[f"{v}_overwritten"] = u["other"]
                row[f"{v}_right_untaught"] = u["right"]
        mentions.append(row)

    free = []
    for nf in b.m["name_free"]:
        clip = nf["clip"]
        book = b.clips[clip]["book"]
        row = {"id": nf["id"], "clip": clip, "book": book}
        for v, pid, lst in (("none", f"clip/{clip}/none", f"own:{book}"), ("own", f"clip/{clip}/own", f"own:{book}"),
                            ("all", f"clip/{clip}/all", f"all:{book}")):
            if pid in texts:
                hyp = name_tokens(texts[pid])
                row[f"{v}_inserted"] = any(find_all(hyp, keys[e]) for e in b.lists[lst]["entries"])
        free.append(row)

    wer = []
    used = sorted({mn["clip"] for mn in b.m["mentions"]} | {nf["clip"] for nf in b.m["name_free"]})
    for clip in used:
        ref = _ordinary(b.clips[clip]["reference"], nw)
        row = {"clip": clip, "book": b.clips[clip]["book"]}
        for v in ("none", "own", "all"):
            pid = f"clip/{clip}/{v}"
            if pid in texts:
                row[f"{v}_errors"], row["words"] = _wer(ref, _ordinary(texts[pid], nw))
        wer.append(row)
    return {"mentions": mentions, "name_free": free, "wer": wer}


def _chapter_refs(b: Bench, ch: dict) -> tuple[list[str], list[str], list[tuple[int, int]], float]:
    """Name tokens and ordinary tokens of a chapter with GAPs; each mention's reference token range;
    scored minutes."""
    nw = frozenset(b.m["name_words"])
    toks: list[str] = [GAP]
    ords: list[str] = [GAP]
    seg_at: list[int] = []
    prev_end = None
    for seg in ch["segments"]:
        if prev_end is not None and abs(seg["start_s"] - prev_end) >= 0.05:
            toks.append(GAP)
            ords.append(GAP)
        seg_at.append(len(toks))
        toks += [t for t, _, _ in name_tokens_spans(seg["reference"])]
        ords += _ordinary(seg["reference"], nw)
        prev_end = seg["end_s"]
    toks.append(GAP)
    ords.append(GAP)
    ranges = []
    for mn in ch["mentions"]:
        spans = name_tokens_spans(ch["segments"][mn["segment"]]["reference"])
        lo, hi = _span_tokens(spans, *mn["span"])
        ranges.append((seg_at[mn["segment"]] + lo, seg_at[mn["segment"]] + hi))
    minutes = sum(s["end_s"] - s["start_s"] for s in ch["segments"]) / 60
    return toks, ords, ranges, minutes


def score_chapters(b: Bench, texts: dict[str, str]) -> dict:
    nw = frozenset(b.m["name_words"])
    keys = {e: name_key(v["written"]) for e, v in b.entries.items()}
    mentions, chapters = [], []
    for ch in b.m["chapters"]:
        ref, ords, ranges, minutes = _chapter_refs(b, ch)
        full = b.lists[ch["list"]]["entries"]
        untaught = set(ch["untaught"])
        lists = {"none": [], "taught": full, "untaught": [e for e in full if e not in untaught]}
        row = {"chapter": ch["id"], "minutes": round(minutes, 3), "book": ch["book"]}
        per = [{"chapter": ch["id"], "entry": mn["entry"], "untaught": mn["entry"] in untaught,
                "same_reader": mn["taught_by_same_reader"]} for mn in ch["mentions"]]
        for cond, listed in lists.items():
            pid = f"chapter/{ch['id']}/{cond}"
            if pid not in texts:
                continue
            hyp = name_tokens(texts[pid])
            a = align(ref, hyp)
            compare = listed or full
            for m, (lo, hi), mn in zip(per, ranges, ch["mentions"]):
                h0, h1 = _at_mention(a, ref, hyp, lo, hi)
                m[f"{cond}_right"] = _occurs_in(hyp, keys[mn["entry"]], h0, h1)
                m[f"{cond}_other"] = any(e != mn["entry"] and _occurs_in(hyp, keys[e], h0, h1)
                                         and not _occurs_in(ref, keys[e], max(0, lo - 1), hi + 1) for e in compare)
            # wrong writes: a listed name in the text that no reference occurrence of it explains
            wrong = 0
            for e in compare:
                k = keys[e]
                ref_at = find_all(ref, k)
                windows = [_at_mention(a, ref, hyp, s, s + len(k)) for s in ref_at]
                for s in find_all(hyp, k):
                    if a.in_gap[s]:
                        continue
                    if not any(w0 <= s < max(w1, w0 + 1) or (s < w1 and s + len(k) > w0) for w0, w1 in windows):
                        wrong += 1
            row[f"{cond}_wrong_writes"] = wrong
            oa = align(ords, [w for w in ordinary_tokens(texts[pid]) if w not in nw])
            row[f"{cond}_errors"], row["words"] = oa.errors, oa.ref_words
        mentions += per
        chapters.append(row)
    return {"mentions": mentions, "chapters": chapters}


def score(b: Bench, texts: dict[str, str]) -> dict:
    return {"clips": score_clips(b, texts), "chapters": score_chapters(b, texts)}
