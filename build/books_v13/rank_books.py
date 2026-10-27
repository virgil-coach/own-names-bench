#!/usr/bin/env python3
"""Ranks the usable candidates (build/candidates.json) by the names their Gutenberg text would give, text only.

For each usable (project, reader) pair: the Gutenberg text (stripped as lore's make_manifest.py does), its invented names
by the v1.2 rule (lore_text.find_names), and how many of them survive the collision rule (curate.py: no name equal to,
within 25% letter distance of, or sharing a 4+ letter word with a held name; no training-list name). Expected usable
names = names with at least 4 occurrences per hour of the reader's sections, scaled to those hours. No audio is read.

Only pairs of at least MIN_HOURS in the GENRES are ranked.

usage: rank_books.py   -> build/ranked.json, build/texts_all/<gutenberg id>.txt
"""
import json
import re
import subprocess
import time
from pathlib import Path

from common import WORK, log, write_json
from curate import Held
from lore_text import Lexicon, find_names, parse

MIN_HOURS = 2.5
GENRES = re.compile(r"Fantasy|Fantastic|Myths|Epic|Saga|Adventure|Science Fiction|Classics|Children|Legends|Poetry|Ancient|"
                    r"Medieval|Historical Fiction|Culture", re.I)
NOT_BOOK = re.compile(r"gutenberg|distributed proofread|pgdp\.net|transcriber'?s?[’']?s? note|\be-?text\b|\be-?book\b"
                      r"|^\s*produced by|this file was produced|internet archive", re.I)


def curl(url: str) -> bytes:
    for attempt in range(4):
        r = subprocess.run(["curl", "-sSfL", "-m", "90", url], capture_output=True)
        if r.returncode == 0:
            return r.stdout
        time.sleep(2 + 3 * attempt)
    return b""


def strip_gutenberg(raw: str) -> tuple[str, int]:
    """As lore make_manifest.py: the book between the START and END markers, minus Gutenberg / production paragraphs."""
    a = re.search(r"\*\*\* ?START OF.*?\*\*\*", raw, re.S)
    b = re.search(r"\*\*\* ?END OF", raw)
    if not (a and b):
        raise ValueError("no START/END markers")
    body = raw[a.end():b.start()].replace("\r\n", "\n")
    body = re.sub(r"\[Illustration[^\]]*\]", "", body)
    kept, dropped = [], 0
    for para in re.split(r"\n\s*\n", body):
        if NOT_BOOK.search(para):
            dropped += 1
        elif para.strip():
            kept.append(para.strip("\n"))
    text = "\n\n".join(kept) + "\n"
    assert "gutenberg" not in text.lower()
    return text, dropped


def gutenberg_text(gid: int) -> str | None:
    p = WORK / "texts_all" / f"{gid}.txt"
    if p.exists():
        return p.read_text()
    time.sleep(1.0)  # politely, one text at a time
    raw = curl(f"https://www.gutenberg.org/cache/epub/{gid}/pg{gid}.txt")
    if not raw:
        return None
    try:
        text, _ = strip_gutenberg(raw.decode("utf-8-sig", errors="replace"))
    except (ValueError, AssertionError):
        return None
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(text)
    return text


def main() -> None:
    cands = [c for c in json.loads((WORK / "candidates.json").read_text())
             if c["ok"] and c["hours"] >= MIN_HOURS and GENRES.search(",".join(c["genres"]))]
    lex, held = Lexicon(), Held()
    out = []
    for c in cands:
        text = gutenberg_text(c["gutenberg_id"])
        if text is None:
            out.append({**c, "rank_error": "no text"})
            continue
        units, _ = parse(text)
        names = find_names(units, lex)
        counts = {n["spelling"]: len(n["runs"]) for n in names.values()}
        free = {n: k for n, k in counts.items() if held.why(n) is None}
        words = len(units)
        # the reader's share of the text, by hours (the project's sections are usually the whole text)
        share = min(1.0, c["hours"] / max(c["hours"], words / 9000))
        usable = sum(1 for k in free.values() if k * share >= 4)
        out.append({**c, "text_words": words, "names": len(counts), "names_free": len(free), "names_usable": usable,
                    "top": sorted(free, key=lambda n: -free[n])[:12]})
        log(f"{c['librivox_id']:>6} {c['hours']:>5.1f} h usable {usable:>3} of {len(counts):>3}  {c['title'][:40]} | {c['reader'][:20]}")
    out.sort(key=lambda r: -r.get("names_usable", -1))
    write_json(WORK / "ranked.json", out)


if __name__ == "__main__":
    main()
