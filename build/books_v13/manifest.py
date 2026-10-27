#!/usr/bin/env python3
"""build/books.json and build/texts/<key>.txt for the picked books (PICKS), as lore's make_manifest.py made them.

PICKS come from build/ranked.json (rank_books.py): usable (project, reader) pairs of build/candidates.json, one book per
reader, no two books of one series or author's world, invented-name books first, then traditional ones. Only the
sections the pair's reader read alone are used. The Gutenberg text is the one LibriVox lists as read from, stripped as
lore's make_manifest.py does (rank_books.strip_gutenberg).

usage: manifest.py      (light HTTP: LibriVox API; texts from build/texts_all)
"""
import json
import re

from common import WORK, log, write_json
from find_books import curl
from rank_books import gutenberg_text

# librivox id -> (reader, pool, public-domain basis). Pool as the benchmark's: "invented" = names the author made up;
# "traditional" = names of myth, legend or history in translation or retelling.
PICKS: dict[int, tuple[str, str, str]] = {
    # invented
    18217: ("tjfria", "invented", "1919 serial; US PD (pre-1931)"),                     # The Mouthpiece of Zitu, Giesy
    14678: ("MrsLSid", "invented", "1922; US PD (pre-1931)"),                           # The Perfect World, Scrymsour
    # 11995 Four and Twenty Fairy Tales (SaraHale) was picked first and left out: her sections are one tale with no names
    19838: ("Andy Sames", "invented", "1922; US PD (pre-1931)"),                        # The Virgin of the Sun, Haggard
    5881: ("Carol Box", "invented", "1884; US PD"),                                     # The Old-Fashioned Fairy Book, Harrison
    5906: ("MaryAnn", "invented", "1911; US PD"),                                       # The Princess Galva, Whitelaw
    6668: ("klbonds", "invented", "1921 serial; US PD (pre-1931)"),                     # The Devolutionist and the Emancipatrix, Flint
    8454: ("Deon Gines", "invented", "1858 (translation 1901); US PD"),                 # The Romance of a Mummy, Gautier
    4535: ("Mike Harris", "invented", "1888; US PD"),                                   # Plain Tales from the Hills, Kipling
    3738: ("skoval", "invented", "1816; US PD"),                                        # The Antiquary, Scott
    11067: ("Kenneth Sergeant Gaghan", "invented", "1917; US PD (pre-1931)"),           # The Rulers of the Lakes, Altsheler
    15528: ("Warren Kati", "invented", "1911; US PD"),                                  # South Sea Tales, London (added for mentions)
    # traditional
    12768: ("Lynda Marie Neilson", "traditional", "1888; US PD"),                       # The Legends and Myths of Hawaii, Kalakaua
    21188: ("Katharina21", "traditional", "1914; US PD (pre-1931)"),                    # Mexican Archaeology, Joyce
    452: ("Michael Scherer", "traditional", "1846; US PD"),                             # Typee, Melville (Marquesan names)
    3518: ("Jacquerie", "traditional", "1863; US PD"),                                  # Legends of Charlemagne, Bulfinch
    1139: ("Scott Robbins", "traditional", "1908; US PD"),                              # Japanese Fairy Tales, Ozaki
    7104: ("Gabriela Cowan", "traditional", "1892; US PD"),                             # Indian Fairy Tales, Jacobs
    2312: ("meyerli", "traditional", "translation 1882 (LibriVox 1900 edition); US PD"),  # The Tale of Genji, Suematsu
    22039: ("Hox", "traditional", "translation 1921; US PD (pre-1931)"),               # The Swedish Fairy Book, Stroebe
    19910: ("Lynette Caulkins", "traditional", "1924; US PD (pre-1931)"),               # Tales from Silver Lands, Finger
}


def main() -> None:
    cands = {(c["librivox_id"], c["reader"]): c for c in json.loads((WORK / "candidates.json").read_text())}
    books = []
    (WORK / "texts").mkdir(parents=True, exist_ok=True)
    for lid, (reader, pool, pd) in PICKS.items():
        c = cands[(lid, reader)]
        assert c["ok"], (lid, c["why"])
        lv = json.loads(curl(f"https://librivox.org/api/feed/audiobooks/?id={lid}&extended=1&format=json"))["books"][0]
        key = re.sub(r"_librivox$", "", c["archive_item"]) or f"lv{lid}"
        sections, dropped = [], []
        for s in lv["sections"]:
            readers = [r["display_name"].strip() for r in s["readers"]]
            row = {"n": int(s["section_number"]), "title": s["title"], "url": s["listen_url"].replace("http://", "https://"),
                   "seconds": int(s["playtime"] or 0), "readers": readers, "reader_ids": [int(r["reader_id"]) for r in s["readers"]]}
            (sections if readers == [reader] else dropped).append(row)
        text = gutenberg_text(c["gutenberg_id"])
        assert text, lid
        (WORK / "texts" / f"{key}.txt").write_text(text)
        books.append({"key": key, "title": c["title"], "author": c["author"], "gutenberg_ids": [c["gutenberg_id"]],
                      "archive_item": c["archive_item"], "librivox_id": lid, "librivox_url": c["url"], "pd_basis": pd,
                      "pool": pool, "reader": reader, "readers": [reader], "sections": sections, "dropped_sections": dropped,
                      "hours": round(sum(s["seconds"] for s in sections) / 3600, 2), "text_words": len(text.split())})
        log(f"{key:<45} {pool[:4]} {len(sections):>3} sections {books[-1]['hours']:>5.1f} h {reader}")
    write_json(WORK / "books.json", {"books": books})
    log(f"{len(books)} books, {sum(b['hours'] for b in books):.1f} h, {len({b['reader'] for b in books})} readers")


if __name__ == "__main__":
    main()
