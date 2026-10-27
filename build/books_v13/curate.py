#!/usr/bin/env python3
"""Name curation and the collision rule of the v1.3 audiobook test suite (lore-poc books/split.py and
bookdev/lore_books/split_bookdev.py, as the v1.2 test books and bookdev were curated).

Per book, from build/books/<key>/names.json (names with a kept mention):
  - removed: elided verse and dialect words (rule), and the hand list curation.json (ordinary words, foreign words and
    other non-names the automatic finder took; read as text, never heard)
  - merged: a plural whose singular is also a name ("Tharks" into "Thark"), and the hand merges of curation.json
  - dropped (collision): a name whose spelling is a name of a training-book list or a generated / synthetic training
    name (exact, as build_dataset.py's TRAINED_NAMES), or is within 25% letter distance of, or shares a 4+ letter word
    with, any name held elsewhere: lore books (train, dev, test), own-names-bench v1.2.0 (clips and chapters), bookdev,
    bigcast, the lore eval sets (build/excl.json `held_names`). A piece that says a dropped name is never used.
    Which held name it met is not written (held-out material); only the books13 name and the kind of rule.
  - books13 names that collide with each other across books are left alone (every list is a book's own).
Writes build/plan.json (per book: kept names, removed, merged, dropped) and build/curation_log.json (counts).

usage: curate.py
"""
import json
import re
from collections import defaultdict

from rapidfuzz.distance import Levenshtein

from common import HERE, WORK, letters, log, word_keys, write_json
from own_names_bench.text import name_key

ELIDED = re.compile(r"\w{2,}['’](d|n|rer|ring|st)")


def distance(a: str, b: str, cap: int) -> int:
    """Levenshtein distance, or cap + 1 when it is over cap (split_bookdev.py's distance, in C)."""
    return Levenshtein.distance(a, b, score_cutoff=cap)


class Held:
    def __init__(self) -> None:
        ex = json.loads((WORK / "excl.json").read_text())
        self.trained = {name_key(n) for n in ex["trained_names"]}
        self.by_len: dict[int, list[str]] = defaultdict(list)
        self.words: set[str] = set()
        for n in ex["held_names"]:
            ln = letters(n)
            if ln:
                self.by_len[len(ln)].append(ln)
            self.words |= word_keys(n)
        for k in self.by_len:
            self.by_len[k] = sorted(set(self.by_len[k]))
        self.wikidata = {name_key(n) for n in ex["wikidata_names"]}

    def why(self, name: str) -> str | None:
        if name_key(name) in self.trained:
            return "a training-list or generated training name"
        mine = letters(name)
        for L in range(int(len(mine) * 0.75) - 1, int(len(mine) / 0.75) + 2):
            for hl in self.by_len.get(L, ()):
                cap = int(0.25 * max(len(mine), len(hl)))
                if distance(mine, hl, cap) <= cap:
                    return "equal or close to a held name"
        if word_keys(name) & self.words:
            return "shares a 4+ letter word with a held name"
        return None


def main() -> None:
    books = json.loads((WORK / "books.json").read_text())["books"]
    hand = json.loads((HERE / "curation.json").read_text())
    held = Held()
    plan, report = {"books": {}}, {}
    for b in books:
        k = b["key"]
        if not (WORK / "books" / k / "names.json").exists():
            continue
        have = {n["name"]: n for n in json.loads((WORK / "books" / k / "names.json").read_text()) if n["mentions_kept"]}
        remove, merge = {}, {}
        for n in have:
            if ELIDED.fullmatch(n):
                remove[n] = "auto: elided word"
        remove.update({n: "hand: " + r for n, r in hand.get(k, {}).get("remove", {}).items() if n in have})
        merge.update({n: t for n, t in hand.get(k, {}).get("merge", {}).items() if n in have and t in have})
        by_letters = {letters(n): n for n in have}
        for n in have:
            ln = letters(n)
            base = next((by_letters[x] for x in (ln[:-1], ln[:-2]) if ln.endswith("s" if x == ln[:-1] else "es")
                         and x in by_letters and by_letters[x] not in remove), None)
            if base and n not in remove and n not in merge:
                merge[n] = base
        kept = sorted({merge.get(n, n) for n in have if n not in remove})
        drops = {n: w for n in kept if (w := held.why(n))}
        names = [n for n in kept if n not in drops]
        plan["books"][k] = {"title": b["title"], "reader": b["reader"], "pool": b["pool"], "names": names,
                            "remove": sorted(remove), "merge": merge, "drop": sorted(drops),
                            "in_wikidata_name_lists": sorted(n for n in names if name_key(n) in held.wikidata)}
        report[k] = {"names_found": len(have), "removed": len(remove), "merged": len(merge), "dropped_for_collision": len(drops),
                     "dropped_by_rule": dict(sorted({w: sum(v == w for v in drops.values()) for w in set(drops.values())}.items())),
                     "names_kept": len(names)}
        log(f"{k:<45} found {len(have):>4} removed {len(remove):>3} merged {len(merge):>3} collisions {len(drops):>3} kept {len(names):>4}")
    write_json(WORK / "plan.json", plan)
    write_json(WORK / "curation_log.json", report)


if __name__ == "__main__":
    main()
