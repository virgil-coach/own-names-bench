"""Scoring. Every system's text is scored by the same rules; nothing here knows which system wrote it.

A name is written right when its name tokens (text.py) appear, in order, at the place of the
mention: the hypothesis words aligned (align.py) to the mention's reference words, widened by one
reference word on each side. Matching is one to one (match.py): each hypothesis occurrence of a
name can stand for one reference occurrence only. Case, punctuation, hyphens and a possessive 's
do not matter; letters and diacritics do. A listed name written at a mention counts against the
system only when no reference occurrence of that name claims it.

Clip items (each name mention), per list variant (own, all):
  right        known pass: the spoken name is on the list and written right
  wrong_name   known pass: another listed name written at the mention instead
  overwritten  untaught pass (the spoken name taken off the list): a listed name written at the mention
  right_untaught  untaught pass: the spoken name written right anyway
  none_right   no-list pass: written right with no list at all
  xr_right     (systems taught by recording) known pass with the name taught in another reader's voice
Name-free pieces: inserted = a listed name appears anywhere in the text.
Ordinary-word error: Whisper-normalized words, every word of any benchmark name removed from
both sides (manifest `name_words`), errors / reference words, over the full-list passes.
Full-transcript error: the same with nothing removed, so a wrongly written name counts too.

Chapters (taught / untaught / none): right per mention, wrong writes = a listed name written
where the reference has no such name (outside the unscored holes), per scored minute;
overwritten = an untaught name's mention written as a listed name; ordinary-word error.
"""

from .align import GAP, align
from .data import Bench
from .match import match, overlaps, window
from .passes import cross_reader, minus
from .text import find_all, name_key, name_tokens, name_tokens_spans, ordinary_tokens


def _span_tokens(spans: list[tuple[str, int, int]], a: int, b: int) -> tuple[int, int]:
    idx = [k for k, (_, s, e) in enumerate(spans) if s < b and e > a]
    return (idx[0], idx[-1] + 1) if idx else (-1, -1)


def _ordinary(text: str, name_words: frozenset[str]) -> list[str]:
    return [w for w in ordinary_tokens(text) if w not in name_words]


class Matched:
    """One hypothesis against one reference: alignment and one-to-one matches, per name."""

    def __init__(self, ref: list[str], hyp: list[str]) -> None:
        self.ref, self.hyp = ref, hyp
        self.a = align(ref, hyp)
        self._m: dict[tuple[str, ...], dict[int, int]] = {}

    def pairs(self, key: tuple[str, ...]) -> dict[int, int]:
        if key not in self._m:
            self._m[key] = match(self.a, self.ref, self.hyp, key)
        return self._m[key]

    def right(self, key: tuple[str, ...], lo: int) -> bool:
        return lo in self.pairs(key)

    def unclaimed_at(self, key: tuple[str, ...], lo: int, hi: int) -> bool:
        """`key` written at the mention [lo, hi) where no reference occurrence of it claims it."""
        w = window(self.a, len(self.ref), len(self.hyp), lo, hi)
        claimed = set(self.pairs(key).values())
        return any(h not in claimed and overlaps(h, len(key), w) for h in find_all(self.hyp, key))

    def unclaimed(self, key: tuple[str, ...]) -> list[int]:
        claimed = set(self.pairs(key).values())
        return [h for h in find_all(self.hyp, key) if h not in claimed and not self.a.in_gap[h]]


def _wer(ref: list[str], hyp: list[str]) -> tuple[int, int]:
    a = align(ref, hyp)
    return a.errors, a.ref_words


def score_clips(b: Bench, texts: dict[str, str]) -> dict:
    """texts: pass id -> text. Returns per-item outcomes (missing passes are left out)."""
    nw = frozenset(b.m["name_words"])
    keys = {e: name_key(v["written"]) for e, v in b.entries.items()}
    cache: dict[str, Matched] = {}
    refs = {cid: name_tokens_spans(c["reference"]) for cid, c in b.clips.items()}
    xr = cross_reader(b) if not b.name else {}

    P = b.prefix

    def matched(pid: str, clip: str) -> Matched | None:
        if pid not in texts:
            return None
        if pid not in cache:
            cache[pid] = Matched([t for t, _, _ in refs[clip]], name_tokens(texts[pid]))
        return cache[pid]

    # entries the source's name finder took that are ordinary words: on the lists as given, never scored as names
    skip = set(b.m.get("not_names", []))
    unscored = {keys[e] for e in skip}

    mentions = []
    for mn in b.m["mentions"]:
        if mn["entry"] in skip:
            continue
        clip = mn["clip"]
        spans = refs[clip]
        lo, hi = _span_tokens(spans, *mn["span"])
        target = keys[mn["entry"]]
        book = b.clips[clip]["book"]
        row = {"id": mn["id"], "clip": clip, "entry": mn["entry"], "book": book, "group": mn["group"],
               "xr_entry": xr.get(mn["id"])}

        def look(pid: str, listed: list[str]) -> dict | None:
            m = matched(pid, clip)
            if m is None:
                return None
            other_keys = {keys[e] for e in listed} - {target} - unscored
            return {"right": m.right(target, lo), "other": any(m.unclaimed_at(k, lo, hi) for k in other_keys)}

        own = b.lists[f"own:{book}"]["entries"]
        r = look(f"{P}clip/{clip}/none", own)
        if r is not None:
            row["none_right"] = r["right"]
        for v in ("own", "all"):
            if f"{v}:{book}" not in b.lists:
                continue
            full = b.lists[f"{v}:{book}"]["entries"]
            k = look(f"{P}clip/{clip}/{v}", full)
            if k is not None:
                row[f"{v}_right"] = k["right"]
                row[f"{v}_wrong_name"] = k["other"]
            u = look(f"{P}clip/{clip}/{v}-minus/{mn['entry']}", minus(b, full, mn["entry"]))
            if u is not None:
                row[f"{v}_overwritten"] = u["other"]
                row[f"{v}_right_untaught"] = u["right"]
        x = look(f"{P}clip/{clip}/own-xr/{mn['entry']}", own)
        if x is not None:
            row["xr_right"] = x["right"]
            row["xr_wrong_name"] = x["other"]
        mentions.append(row)

    free = []
    for nf in b.m["name_free"]:
        clip = nf["clip"]
        book = b.clips[clip]["book"]
        row = {"id": nf["id"], "clip": clip, "book": book, "minutes": b.clips[clip]["seconds"] / 60}
        for v, pid, lst in (("none", f"{P}clip/{clip}/none", f"own:{book}"), ("own", f"{P}clip/{clip}/own", f"own:{book}"),
                            ("all", f"{P}clip/{clip}/all", f"all:{book}")):
            if pid in texts and lst in b.lists:
                hyp = name_tokens(texts[pid])
                entries = b.lists[lst]["entries"]
                n = sum(len(find_all(hyp, k)) for k in {keys[e] for e in entries} - unscored)
                row[f"{v}_inserted"] = n > 0
                row[f"{v}_inserted_count"] = n
                # names taught from other recordings: never said in this one, so a write of one is an insertion
                # whatever the reference missed (a name of this recording may be said in the stretch unwritten)
                # (a name is this recording's when its taught recording was cut from it; AMI's lists are
                # taught in call voices and say none of their names)
                said = {keys[e] for e in entries if b.entries[e]["book"] == book and f"/{book}/" in b.entries[e]["sample"]}
                foreign = {keys[e] for e in entries} - said - unscored
                nf_ = sum(len(find_all(hyp, k)) for k in foreign)
                row[f"{v}_inserted_foreign"] = nf_ > 0
                row[f"{v}_inserted_foreign_count"] = nf_
        free.append(row)

    wer = []
    used = sorted({mn["clip"] for mn in b.m["mentions"]} | {nf["clip"] for nf in b.m["name_free"]})
    for clip in used:
        ref = _ordinary(b.clips[clip]["reference"], nw)
        ref_full = ordinary_tokens(b.clips[clip]["reference"])
        row = {"clip": clip, "book": b.clips[clip]["book"]}
        for v in ("none", "own", "all"):
            pid = f"{P}clip/{clip}/{v}"
            if pid in texts:
                row[f"{v}_errors"], row["words"] = _wer(ref, _ordinary(texts[pid], nw))
                row[f"{v}_full_errors"], row["full_words"] = _wer(ref_full, ordinary_tokens(texts[pid]))
        wer.append(row)
    return {"mentions": mentions, "name_free": free, "wer": wer}


def _chapter_refs(b: Bench, ch: dict) -> tuple[list[str], list[str], list[str], list[tuple[int, int]], float]:
    """Name tokens and ordinary tokens of a chapter with GAPs; each mention's reference token range;
    scored minutes."""
    nw = frozenset(b.m["name_words"])
    toks: list[str] = [GAP]
    ords: list[str] = [GAP]
    fulls: list[str] = [GAP]
    seg_at: list[int] = []
    prev_end = None
    for seg in ch["segments"]:
        if prev_end is not None and abs(seg["start_s"] - prev_end) >= 0.05:
            toks.append(GAP)
            ords.append(GAP)
            fulls.append(GAP)
        seg_at.append(len(toks))
        toks += [t for t, _, _ in name_tokens_spans(seg["reference"])]
        ords += _ordinary(seg["reference"], nw)
        fulls += ordinary_tokens(seg["reference"])
        prev_end = seg["end_s"]
    toks.append(GAP)
    ords.append(GAP)
    fulls.append(GAP)
    ranges = []
    for mn in ch["mentions"]:
        spans = name_tokens_spans(ch["segments"][mn["segment"]]["reference"])
        lo, hi = _span_tokens(spans, *mn["span"])
        ranges.append((seg_at[mn["segment"]] + lo, seg_at[mn["segment"]] + hi))
    minutes = sum(s["end_s"] - s["start_s"] for s in ch["segments"]) / 60
    return toks, ords, fulls, ranges, minutes


def score_chapters(b: Bench, texts: dict[str, str]) -> dict:
    nw = frozenset(b.m["name_words"])
    keys = {e: name_key(v["written"]) for e, v in b.entries.items()}
    mentions, chapters = [], []
    for ch in b.m["chapters"]:
        ref, ords, fulls, ranges, minutes = _chapter_refs(b, ch)
        full = b.lists[ch["list"]]["entries"]
        untaught = set(ch["untaught"])
        rest = full
        for e in ch["untaught"]:
            rest = minus(b, rest, e)
        lists = {"none": [], "taught": full, "untaught": rest}
        row = {"chapter": ch["id"], "minutes": round(minutes, 3), "book": ch["book"]}
        per = [{"chapter": ch["id"], "book": ch["book"], "entry": mn["entry"], "untaught": mn["entry"] in untaught,
                "same_reader": mn["taught_by_same_reader"]} for mn in ch["mentions"]]
        for cond, listed in lists.items():
            pid = f"chapter/{ch['id']}/{cond}"
            if pid not in texts:
                continue
            m = Matched(ref, name_tokens(texts[pid]))
            compare = {keys[e] for e in (listed or full)}
            for p, (lo, hi), mn in zip(per, ranges, ch["mentions"]):
                target = keys[mn["entry"]]
                p[f"{cond}_right"] = m.right(target, lo)
                p[f"{cond}_other"] = any(m.unclaimed_at(k, lo, hi) for k in compare - {target})
            # wrong writes: a listed name in the text that no reference occurrence of it claims
            row[f"{cond}_wrong_writes"] = sum(len(m.unclaimed(k)) for k in compare)
            oa = align(ords, [w for w in ordinary_tokens(texts[pid]) if w not in nw])
            row[f"{cond}_errors"], row["words"] = oa.errors, oa.ref_words
            fa = align(fulls, ordinary_tokens(texts[pid]))
            row[f"{cond}_full_errors"], row["full_words"] = fa.errors, fa.ref_words
        mentions += per
        chapters.append(row)
    return {"mentions": mentions, "chapters": chapters}


def score(b: Bench, texts: dict[str, str]) -> dict:
    return {"clips": score_clips(b, texts), "chapters": score_chapters(b, texts),
            "suites": {name: score_clips(s, texts) for name, s in (b.suites or {}).items()}}
