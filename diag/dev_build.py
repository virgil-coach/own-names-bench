"""Dev sets for the three pipeline fixes (fix/v12-pipeline). Nothing here comes from own-names-bench: the fixes were
found on benchmark outputs, so they are validated (and any threshold set) on these first.

  books        the lore dev split (6 books, 6 readers; no benchmark book or reader; lore-books splits.json): pieces
               with a taught name said ("known": the book's own names taught, each by a recording from elsewhere in
               the book; "unknown": the same piece with that name off the list) and name-free pieces of 4-15 s
  books_far    a subset of the known pieces and name-free pieces through a simulated far-field room (reverb,
               20-32 dB quieter, noise); the taught recordings stay close-talk
  ls_short     LibriSpeech test-other utterances of 3.5 s or less, each alone (dictation-like), name-free, with a
               40-name list of a lore dev book (its taught recordings)
  ls_turns     4-8 consecutive test-other utterances of one reader joined with 0.25-1.5 s gaps (at most 30 s): the
               cutter meets short utterances between pauses
  ls_short_far, ls_turns_far   the same through the simulated far field
LibriSpeech test-other (CC BY 4.0): chapters of a benchmark book or read by a benchmark reader are left out.

usage: python diag/dev_build.py OUT_DIR    -> OUT_DIR/items.jsonl and OUT_DIR/audio/*.flac
"""

import json
import random
import re
import subprocess
import sys
import tarfile
from pathlib import Path

import numpy as np
import soundfile as sf

BK = Path("/gpu-cli-workspaces/jameslal/lore-books")
SP = Path("/gpu-cli-workspaces/jameslal/lore-spot")
RATE = 16000
LS_URL = "https://www.openslr.org/resources/12/test-other.tar.gz"
# own-names-bench v1.2.0 audiobook books and readers (manifest.json clips / attribution): kept out of the dev sets
BENCH_BOOK_WORDS = ["aeneid", "children of odin", "eric brighteyes", "iliad", "jungle book", "just so stories", "king arthur",
                    "santa claus", "mad king", "pellucidar", "zixi", "tarzan"]


def far(x: np.ndarray, rng: random.Random) -> tuple[np.ndarray, dict]:
    """A simulated far-field recording: exponential-decay room response (RT60 0.3-0.9 s, direct-to-reverberant
    -3..6 dB), level 20-32 dB lower, white-ish noise at 10-25 dB SNR (to the reverberant speech)."""
    rt60, drr, drop, snr = rng.uniform(0.3, 0.9), rng.uniform(-3, 6), rng.uniform(20, 32), rng.uniform(10, 25)
    nr = np.random.default_rng(rng.randrange(1 << 30))
    n = int(rt60 * RATE)
    t = np.arange(n) / RATE
    tail = nr.standard_normal(n) * np.exp(-6.9 * t / rt60)
    tail[: int(0.002 * RATE)] = 0.0
    tail *= np.sqrt(10 ** (-drr / 10) / (np.sum(tail**2) + 1e-12))
    rir = tail
    rir[0] = 1.0
    m = len(x) + n - 1
    size = 1 << (m - 1).bit_length()
    y = np.fft.irfft(np.fft.rfft(x, size) * np.fft.rfft(rir, size), size)[: len(x)]
    y *= np.sqrt(np.mean(x**2) / (np.mean(y**2) + 1e-12)) * 10 ** (-drop / 20)
    noise = nr.standard_normal(len(y))
    noise *= np.sqrt(np.mean(y**2) / 10 ** (snr / 10)) / (np.std(noise) + 1e-12)
    out = (y + noise).astype(np.float32)
    return out, {"rt60": round(rt60, 2), "drr_db": round(drr, 1), "drop_db": round(drop, 1), "snr_db": round(snr, 1)}


def glossaries() -> tuple[dict[str, list[dict]], dict[str, dict]]:
    """Per dev book: its own names, each with its taught recordings [(path, heard_as, clip)]; and the dev pieces."""
    pools = json.loads((SP / "pools" / "dev.json").read_text())
    books: dict[str, list[dict]] = {}
    for group, members in pools["pools"].items():
        if not group.startswith("books/"):
            continue
        names = []
        for i in members["own"]:
            kind, _, name, takes = pools["entries"][i]
            names.append({"name": name, "takes": [[t[0] if t[0].startswith("/") else str(BK / t[0]), t[1], t[2]] for t in takes]})
        books[group[len("books/"):]] = names
    pieces = {}
    for line in (BK / "splits" / "dev.jsonl").open():
        pc = json.loads(line)
        pieces[pc["id"]] = pc
    return books, pieces


def entries_for(names: list[dict], clip: str, drop: str | None, tag: str) -> list[dict]:
    out = []
    for n in names:
        if n["name"] == drop:
            continue
        take = next((t for t in n["takes"] if t[2] != clip), None)
        if take is not None:
            out.append({"id": f"{tag}/{n['name']}", "written": n["name"], "sample_path": take[0]})
    return out


def main() -> None:
    out = Path(sys.argv[1])
    (out / "audio").mkdir(parents=True, exist_ok=True)
    rng = random.Random(17)
    books, pieces = glossaries()
    items: list[dict] = []

    # ---- lore dev books
    rows = [json.loads(line) for line in (SP / "books_dev.jsonl").open()]
    by_name: dict[tuple[str, str], list[dict]] = {}
    free = []
    for row in rows:
        pc = pieces.get(row["id"])
        if pc is None or row["group"] not in books:
            continue
        good = {it[1] for it in row.get("items", []) if it[2] and not it[3]}
        for name in row["want"]:
            if name in good:
                by_name.setdefault((row["group"], name), []).append(row)
        if not row["want"] and not row["said"] and not row.get("pool_said") and 4.0 <= pc["seconds"] <= 15.0:
            free.append(row)
    known = []
    for (book, name), rs in sorted(by_name.items()):
        for row in rng.sample(rs, min(len(rs), 2)):
            known.append((book, name, row))
    known = rng.sample(known, min(len(known), 300))
    for book, name, row in known:
        pc = pieces[row["id"]]
        for cond in ("known", "unknown"):
            items.append({"id": f"books/{cond}/{row['id']}/{name}", "set": "books", "cond": cond, "group": book, "audio": str(BK / pc["audio"]),
                          "want": name, "reference": pc["reference"], "entries": entries_for(books[book], row["id"], name if cond == "unknown" else None, book)})
    for row in rng.sample(free, min(len(free), 250)):
        pc = pieces[row["id"]]
        items.append({"id": f"books/free/{row['id']}", "set": "books", "cond": "free", "group": row["group"], "audio": str(BK / pc["audio"]),
                      "want": None, "reference": pc["reference"], "entries": entries_for(books[row["group"]], row["id"], None, row["group"])})
    # far field: 150 known pieces, 100 name-free
    frng = random.Random(23)
    base = [it for it in items if it["set"] == "books"]
    pick = frng.sample([it for it in base if it["cond"] == "known"], 150) + frng.sample([it for it in base if it["cond"] == "free"], 100)
    for it in pick:
        x, rate = sf.read(it["audio"], dtype="float32")
        assert rate == RATE
        y, sim = far(x if x.ndim == 1 else x.mean(axis=1), frng)
        path = out / "audio" / (re.sub(r"[^\w.-]", "_", it["id"]) + "_far.flac")
        sf.write(path, y, RATE)
        items.append({**it, "id": it["id"].replace("books/", "books_far/", 1), "set": "books_far", "audio": str(path), "far": sim})

    # ---- LibriSpeech test-other
    ls = out / "librispeech"
    if not (ls / "LibriSpeech" / "test-other").exists():
        ls.mkdir(exist_ok=True)
        subprocess.run(["curl", "-sSL", "-o", str(ls / "t.tgz"), LS_URL], check=True)
        with tarfile.open(ls / "t.tgz") as t:
            t.extractall(ls, filter="data")
        (ls / "t.tgz").unlink()
    root = ls / "LibriSpeech"
    bench = json.loads(Path(__file__).with_name("bench_readers.json").read_text())
    chapters = {}
    for line in (root / "CHAPTERS.TXT").read_text(errors="replace").splitlines():
        if line.startswith(";"):
            continue
        f = [p.strip() for p in line.split("|")]
        if len(f) >= 7 and f[3] == "test-other":
            chapters[f[0]] = f[6].lower()
    readers = {}
    for line in (root / "SPEAKERS.TXT").read_text(errors="replace").splitlines():
        if line.startswith(";"):
            continue
        f = [p.strip() for p in line.split("|")]
        if len(f) >= 5:
            readers[f[0]] = f[4]
    dropped = set()
    utts: dict[tuple[str, str], list[tuple[str, Path, str, float]]] = {}
    for trans in sorted((root / "test-other").glob("*/*/*.trans.txt")):
        spk, chap = trans.parent.parent.name, trans.parent.name
        title, reader = chapters.get(chap, ""), readers.get(spk, "")
        if any(w in title for w in BENCH_BOOK_WORDS) or reader in bench:
            dropped.add(f"{spk}/{chap} {title!r} {reader!r}")
            continue
        for line in trans.read_text().splitlines():
            uid, text = line.split(" ", 1)
            path = trans.parent / f"{uid}.flac"
            utts.setdefault((spk, chap), []).append((uid, path, text, sf.info(path).duration))
    print(f"LibriSpeech test-other: {sum(map(len, utts.values()))} utterances in {len(utts)} chapters kept; dropped {sorted(dropped)}", flush=True)
    lrng = random.Random(31)
    names_books = sorted(books)

    def gloss(tag: str) -> tuple[str, list[dict]]:
        book = lrng.choice(names_books)
        names = books[book]
        chosen = lrng.sample(names, min(40, len(names)))
        if len(chosen) < 40:  # pad from the other books
            others = [n for b in names_books if b != book for n in books[b]]
            chosen += lrng.sample(others, 40 - len(chosen))
        return book, entries_for(chosen, "", None, f"ls/{book}")

    shorts = [(spk, chap, u) for (spk, chap), us in sorted(utts.items()) for u in us if u[3] <= 3.5]
    short_items = []
    for spk, chap, (uid, path, text, dur) in lrng.sample(shorts, min(300, len(shorts))):
        book, ents = gloss(uid)
        short_items.append({"id": f"ls_short/{uid}", "set": "ls_short", "cond": "free", "group": spk, "audio": str(path), "want": None,
                            "reference": text, "entries": ents, "seconds": round(dur, 2)})
    turn_items = []
    keys = sorted(utts)
    for k in range(150):
        spk, chap = keys[k % len(keys)]
        us = utts[(spk, chap)]
        n = lrng.randint(4, 8)
        start = lrng.randrange(max(1, len(us) - n))
        parts, refs, total = [], [], 0.0
        for uid, path, text, dur in us[start:start + n]:
            if total + dur > 30.0 and parts:
                break
            x, _ = sf.read(path, dtype="float32")
            if parts:
                gap = lrng.uniform(0.25, 1.5)
                parts.append(np.zeros(int(gap * RATE), dtype=np.float32))
                total += gap
            parts.append(x)
            refs.append(text)
            total += dur
        path = out / "audio" / f"ls_turns_{k:03d}.flac"
        sf.write(path, np.concatenate(parts), RATE)
        book, ents = gloss(f"t{k}")
        turn_items.append({"id": f"ls_turns/{k:03d}", "set": "ls_turns", "cond": "free", "group": spk, "audio": str(path), "want": None,
                           "reference": " ".join(refs), "entries": ents, "utterances": len(refs)})
    items += short_items + turn_items
    for it in short_items + turn_items:
        x, _ = sf.read(it["audio"], dtype="float32")
        y, sim = far(x, frng)
        tag = it["set"] + "_far"
        path = out / "audio" / (re.sub(r"[^\w.-]", "_", it["id"]) + "_far.flac")
        sf.write(path, y, RATE)
        items.append({**it, "id": it["id"].replace(it["set"], tag, 1), "set": tag, "audio": str(path), "far": sim})

    with (out / "items.jsonl").open("w") as f:
        for it in items:
            f.write(json.dumps(it) + "\n")
    counts: dict[str, int] = {}
    for it in items:
        counts[f"{it['set']} {it['cond']}"] = counts.get(f"{it['set']} {it['cond']}", 0) + 1
    print(json.dumps(counts, indent=1), flush=True)
    print("DONE dev_build", flush=True)


if __name__ == "__main__":
    main()
