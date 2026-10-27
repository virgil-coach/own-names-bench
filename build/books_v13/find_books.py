#!/usr/bin/env python3
"""Candidate LibriVox books for the v1.3 audiobook test suite, every one checked against build/excl.json.

The LibriVox API is read for the authors in AUTHORS (writers of invented-name fantasy and adventure, and translators /
retellers of traditions the benchmark does not hold: Irish, Welsh, Persian, Indian, Chinese, Japanese, Finnish,
Native American) and for every project of the genres in GENRES. A (project, reader) pair is a candidate when:
  - the project is English, first published before 1931 (`copyright_year`; US public domain by age, as lore's rule)
    and has a Project Gutenberg text (`url_text_source`)
  - the reader read at least MIN_HOURS of it alone (one reader on each of those sections); only those sections are used
  - the reader, the project, its archive.org item, its Gutenberg text and its work (title across readings and
    volumes) are in no exclusion list, and the title is not of a series or tradition held by lore or the benchmark
Writes build/candidates.json, one row per pair with the reasons a pair was dropped.

usage: find_books.py   (light HTTP: LibriVox API)
"""
import json
import re
import subprocess
import time
import urllib.parse
from collections import defaultdict

from common import WORK, base_reader, log, write_json
from excl import work_title

MIN_HOURS = 2.0
AUTHORS = [
    # invented names
    "Morris", "Dunsany", "Haggard", "Burroughs", "Baum", "MacDonald", "Merritt", "Hodgson", "Cabell", "Eddison",
    "Lindsay", "Bramah", "Beckford", "Meredith", "Stockton", "Nesbit", "Kingsley", "Wells", "Griffith", "Doyle",
    "Kipling", "Lang", "Mirrlees", "England", "Serviss", "Cummings", "Hastings", "Flint", "Rousseau", "Farley",
    "Bradshaw", "Adolph", "Paltock", "Hoffmann", "Wright", "Lytton", "Bulwer", "Corelli", "Machen", "Blackwood",
    "Housman", "Molesworth", "Ingelow", "Kenneth Morris", "Chambers", "Ewers", "Ballantyne", "Henty", "Verne",
    "Hudson", "Butler", "Swift", "Cleland", "Carroll", "Barrie", "Fouque", "Hauff", "Andersen", "Alcott",
    "Pyle", "Lagerlof", "Wilde", "Stevenson", "Rider", "Mundy", "Futrelle", "Dent", "Wylie",
    # traditions in translation or retold
    "Gregory", "Rolleston", "Curtin", "Stephens", "Colum", "Yeats", "Joyce", "Hyde", "Young", "Guest",
    "Zimmern", "Firdausi", "Ferdowsi", "Dutt", "Arnold", "Mackenzie", "Ozaki", "Chamberlain", "Hearn", "Davis",
    "Werner", "Giles", "Brewitt-Taylor", "Suematsu", "Murasaki", "Kirby", "Crawford", "Lonnrot", "Schoolcraft",
    "Eastman", "Grinnell", "Judson", "Spence", "Sturluson", "Dasent", "Magnusson", "Jacobs", "Ralston",
    "Afanasyev", "Wiggin", "Ransome", "Bain", "Pyle", "Smith", "Long", "Valmiki", "Vyasa",
]
GENRES = ["Fantasy Fiction", "Fantastic Fiction", "Myths, Legends & Fairy Tales", "Epics", "Sagas",
          "Action & Adventure Fiction", "Classics (Greek & Latin Antiquity)", "Science Fiction"]
# series and traditions held by lore or the benchmark (bookdev/find_books.py's list, plus the dev sets' series)
SERIES_OR_RESERVED = re.compile(
    r"barsoom|mars|pellucidar|tarzan|\boz\b|ozma|quatermain|allan|pegana|ouroboros|wonder|dreamer|elfland|odin|iliad|"
    r"odyssey|aeneid|arthur|morte|zixi|santa|jungle|just so|volsung|sigurd|mabinogion|beowulf|kalevala|gulliver|"
    r"houyhnhnm|olga romanoff|peter wilkins|curdie|princess and the goblin|kai lung|caspak|land that time|"
    r"time forgot|out of time|people that time|asgard|norse|ulysses|troy|homer|virgil|arabian nights|thousand and one|"
    r"mahabharata|zenda|wolfings|jurgen|poictesme|moon pool|arcturus|lost continent|ayesha|\bshe\b", re.I)


def curl(url: str) -> bytes:
    for attempt in range(5):
        r = subprocess.run(["curl", "-sSfL", "-m", "90", url], capture_output=True)
        if r.returncode == 0:
            return r.stdout
        if b"404" in r.stderr:
            return b""
        time.sleep(2 + 3 * attempt)
    return b""


def feed(query: str) -> list[dict]:
    out, offset = [], 0
    while True:
        raw = curl(f"https://librivox.org/api/feed/audiobooks/?{query}&extended=1&format=json&limit=50&offset={offset}")
        try:
            books = json.loads(raw)["books"] if raw else []
        except (json.JSONDecodeError, KeyError, TypeError):
            books = []
        if not books:
            return out
        out += books
        offset += 50
        time.sleep(0.3)


def gutenberg_id(lv: dict) -> int | None:
    m = re.search(r"gutenberg\.org/(?:ebooks|etext|files|cache/epub)/(\d+)", lv.get("url_text_source") or "")
    return int(m.group(1)) if m else None


def year(lv: dict) -> int | None:
    y = str(lv.get("copyright_year") or "").strip()
    return int(y) if y.isdigit() and int(y) > 0 else None


def check(lv: dict, ex: dict, query: str) -> list[dict]:
    pid = str(int(lv["id"]))
    item = (lv.get("url_iarchive") or "").rstrip("/").split("/")[-1]
    gid = gutenberg_id(lv)
    secs = lv.get("sections") or []
    project_why = []
    if lv.get("language") != "English":
        project_why.append(f"language {lv.get('language')}")
    if pid in ex["projects"]:
        project_why.append(ex["projects"][pid])
    if item in ex["items"]:
        project_why.append(ex["items"][item])
    if gid is None:
        project_why.append("no Gutenberg text source")
    elif str(gid) in ex["gutenberg"]:
        project_why.append(ex["gutenberg"][str(gid)])
    wt = work_title(lv["title"])
    if wt in ex["titles"]:
        project_why.append(f"work held: {ex['titles'][wt]}")
    if SERIES_OR_RESERVED.search(lv["title"]):
        project_why.append("series or tradition held by lore / the benchmark")
    y = year(lv)
    if y is None or y > 1930:
        project_why.append(f"first published {y}: not public domain by age")
    by_reader: dict[str, list[dict]] = defaultdict(list)
    for s in secs:
        rs = [(r.get("display_name") or "?").strip() for r in (s.get("readers") or [])]
        if len(rs) == 1:
            by_reader[rs[0]].append(s)
    all_readers = sorted({(r.get("display_name") or "?").strip() for s in secs for r in (s.get("readers") or [])})
    rows = []
    for reader, mine in by_reader.items():
        hours = sum(int(s.get("playtime") or 0) for s in mine) / 3600
        why = list(project_why)
        if base_reader(reader) in ex["readers"]:
            why.append(f"reader {reader}: {ex['readers'][base_reader(reader)]}")
        if hours < MIN_HOURS:
            why.append(f"{hours:.1f} h by this reader")
        rows.append({"query": query, "librivox_id": int(pid), "title": lv["title"],
                     "author": " ".join(f"{a.get('first_name', '')} {a.get('last_name', '')}".strip() for a in lv.get("authors", [])),
                     "reader": reader, "project_readers": len(all_readers), "sections": len(mine), "sections_in_project": len(secs),
                     "hours": round(hours, 2), "archive_item": item, "gutenberg_id": gid, "copyright_year": y,
                     "url": lv.get("url_librivox"), "genres": [g["name"] for g in lv.get("genres", [])], "ok": not why, "why": why})
    return rows


def main() -> None:
    ex = json.loads((WORK / "excl.json").read_text())
    seen: set[int] = set()
    out = []
    queries = [f"author={urllib.parse.quote(a)}" for a in dict.fromkeys(AUTHORS)] + \
              [f"genre={urllib.parse.quote(g)}" for g in GENRES]
    for q in queries:
        for lv in feed(q):
            if int(lv["id"]) in seen:
                continue
            seen.add(int(lv["id"]))
            out += check(lv, ex, q)
        log(f"{q}: {len(seen)} projects, {sum(r['ok'] for r in out)} usable (project, reader) pairs")
    write_json(WORK / "candidates.json", out)
    log(f"{sum(r['ok'] for r in out)} usable pairs of {len(out)}, {len(seen)} projects")


if __name__ == "__main__":
    main()
