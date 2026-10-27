#!/usr/bin/env python3
"""Test-split utterances for the v1.3 conversation test suite: 16 kHz flac on the volume with speaker, session, text,
the names said and, for utterances with a name, word times (forced alignment of the reference, common.Aligner).
The same steps as lore-poc convdata/prep.py (the dev recipe), on each source's own test split, with everything the
conversation train and dev data contain left out (read from $CONV_TRAINDEV/utts, never written):

  voxpopuli  en test split. Left out: utterances with no speaker id, every speaker of a train or dev utterance.
             Kept and flagged (`session_shared`): a debate item (audio_id prefix) in which other speakers are in train
             or dev (440 of VoxPopuli's 489 test debate items are also in its train/validation shards).
  libritts   test-clean and test-other. Left out: readers of own-names-bench v1.2 books or clips, lore-books dev/test
             readers, LibriTTS speakers of the v0.3.0 adapter's training data and readers of its 47 LibriVox books
             (attribution_v030/), any train or dev speaker; chapters of a book (LibriVox project, Gutenberg id or title)
             of the benchmark, of lore held-out or v0.3.0 training books, or of any train or dev chapter.
  both       a text sharing a run of 8 normalized words with any train or dev utterance or any benchmark reference;
             digits or symbols in the text (as dev); outside 1.5-20 s.
  noise      the FSD50K clips of fsd_test.json, 16 kHz mono flac, pools `musan` (indoor/ambient) and `street`.

Names are found with common.NameFinder over the source's test texts together with its train and dev texts (more
lower-case evidence keeps ordinary words off the name list).

usage: prep.py <voxpopuli|libritts|noise>  -> build/utts/<source>.jsonl, build/audio/<source>/..., build/noise/
"""
import csv
import io
import json
import random
import re
import sys
import time
from collections import Counter
from pathlib import Path

import numpy as np
import soundfile as sf

from common import RATE, TRAINDEV, WORK, Aligner, NameFinder, jsonl, letters, log, to_mono16k, write_flac_checked

SRC = WORK / "src"
UTTS = WORK / "utts"
AUDIO = WORK / "audio"
HERE = Path(__file__).resolve().parent
FREE_CAP = 3000
MIN_S, MAX_S = 1.5, 20.0


def base_name(s: str) -> str:
    return re.sub(r"\s*\(.*?\)\s*", "", s).strip().casefold()


def grams(text: str, n: int = 8) -> set[tuple[str, ...]]:
    w = re.findall(r"[a-z']+", text.lower())
    return {tuple(w[i:i + n]) for i in range(len(w) - n + 1)}


def ok_text(t: str) -> bool:
    return not re.search(r"[0-9%&@#$€£/+=<>_]", t)


def decode(cell: dict) -> np.ndarray:
    x, rate = sf.read(io.BytesIO(cell["bytes"]), dtype="float32")
    return to_mono16k(x, rate)


class TrainDev:
    """What the conversation train and dev data contain (speakers, sessions, texts), from their utterance files."""

    def __init__(self) -> None:
        self.utts = [u for p in sorted((TRAINDEV / "utts").glob("*.jsonl")) if not p.name.endswith("_stats.jsonl") for u in jsonl(p)]
        if len(self.utts) < 50000:
            raise SystemExit(f"{TRAINDEV}/utts: only {len(self.utts)} utterances; expected the full train and dev data")
        self.speakers = {u["speaker"] for u in self.utts}
        self.groups = {u["group"] for u in self.utts}
        self.texts = {u["source"]: [] for u in self.utts}
        for u in self.utts:
            self.texts[u["source"]].append(u["text"])
        excl = json.loads((HERE / "excl.json").read_text())
        self.grams: set[tuple[str, ...]] = set()
        for t in [u["text"] for u in self.utts] + excl["bench_texts"]:
            self.grams |= grams(t)
        log(f"train/dev: {len(self.utts)} utterances, {len(self.speakers)} speakers, {len(self.groups)} sessions; {len(self.grams)} 8-word runs "
            f"(with {len(excl['bench_texts'])} benchmark texts)")

    def text_clash(self, t: str) -> bool:
        return bool(grams(t) & self.grams)


def finish(source: str, rows: list[dict], audio_of, aligner: Aligner, stats: Counter) -> None:
    rng = random.Random(13)
    named = [r for r in rows if r["names"]]
    free = [r for r in rows if not r["names"]]
    keep = named + rng.sample(free, min(len(free), FREE_CAP))
    keep.sort(key=lambda r: (r.get("_file", ""), r.get("_row", 0)))
    t = time.time()
    out_path = UTTS / f"{source}.jsonl"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with out_path.open("w") as out:
        for i, r in enumerate(keep):
            x = audio_of(r)
            if not MIN_S <= len(x) / RATE <= MAX_S:
                stats["outside 1.5-20 s"] += 1
                continue
            if r["names"]:
                words = r["text"].split()
                timed = aligner.words(x, words)
                if timed is None:
                    stats["named: alignment failed"] += 1
                    continue
                r["words"] = [{"word": w, "start": tw["start"], "end": tw["end"], "score": tw["score"]} for w, tw in zip(words, timed)]
            path = AUDIO / source / f"{re.sub(r'[^A-Za-z0-9_.-]', '_', r['id'])}.flac"
            meta = write_flac_checked(path, x)
            r = {k: v for k, v in r.items() if not k.startswith("_")}
            r.update(audio=str(path), seconds=meta["seconds"], sha256=meta["sha256"], pcm_sha256=meta["pcm_sha256"])
            stats[f"test {'named' if r['names'] else 'free'}"] += 1
            out.write(json.dumps(r, ensure_ascii=False) + "\n")
            if i % 1000 == 0:
                log(f"{source}: {i}/{len(keep)} in {time.time() - t:.0f}s")
    log(f"{source}: {json.dumps(dict(stats))}")
    (UTTS / f"{source}_stats.json").write_text(json.dumps(dict(stats), indent=1))


def parquet_audio(rows_file_key: str = "_file"):
    import pyarrow.parquet as pq
    cache: dict[str, list] = {}

    def audio_of(r: dict) -> np.ndarray:
        if r[rows_file_key] not in cache:
            cache.clear()
            cache[r[rows_file_key]] = pq.read_table(r[rows_file_key], columns=["audio"]).column("audio").to_pylist()
        return decode(cache[r[rows_file_key]][r["_row"]])
    return audio_of


def voxpopuli(aligner: Aligner, td: TrainDev) -> None:
    import pyarrow.parquet as pq
    meta = []
    for f in sorted((SRC / "voxpopuli" / "en").glob("test-*.parquet")):
        for k, r in enumerate(pq.read_table(f, columns=["audio_id", "raw_text", "speaker_id", "gender"]).to_pylist()):
            meta.append(dict(r, file=str(f), row=k))
    stats: Counter = Counter({"test split utterances": len(meta)})
    finder = NameFinder([r["raw_text"] for r in meta] + td.texts.get("voxpopuli", []))
    rows = []
    for r in meta:
        if r["speaker_id"] in (None, "", "None"):
            stats["no speaker id"] += 1
            continue
        spk = f"vp:{r['speaker_id']}"
        if spk in td.speakers:
            stats["speaker in train or dev"] += 1
            continue
        text = r["raw_text"].strip()
        if not text or not ok_text(text):
            stats["text with digits or symbols"] += 1
            continue
        if td.text_clash(text):
            stats["text shares 8 words with train, dev or benchmark"] += 1
            continue
        sess = f"vp:{r['audio_id'].split('_')[0]}"
        rows.append({"id": f"vp_{r['audio_id']}", "source": "voxpopuli", "split": "test", "speaker": spk, "group": sess,
                     "session_shared": sess in td.groups, "gender": r["gender"], "text": text, "names": finder.find(text),
                     "_file": r["file"], "_row": r["row"]})
    finish("voxpopuli", rows, parquet_audio(), aligner, stats)


def libritts(aligner: Aligner, td: TrainDev) -> None:
    import pyarrow.parquet as pq
    excl = json.loads((HERE / "excl.json").read_text())
    v030_books = list(csv.DictReader((HERE / "attribution_v030" / "librivox_books.csv").open()))
    v030_tts = {r["speaker_id"] for r in csv.DictReader((HERE / "attribution_v030" / "libritts.csv").open())}
    bad_readers = {base_name(r) for r in excl["bench_readers"] + excl["lore_heldout"]["readers"]}
    bad_readers |= {base_name(x) for b in v030_books for x in re.split(r"[;,]\s*", b["readers"]) if x.strip()}
    train_lt = [u for u in td.utts if u["source"] == "libritts"]
    bad_proj = set(excl["bench_books"]["librivox_ids"]) | set(excl["lore_heldout"]["librivox_ids"]) | \
        {int(b["librivox_id"]) for b in v030_books if b["librivox_id"].isdigit()} | {u.get("librivox_project") for u in train_lt}
    bad_gut = set(excl["bench_books"]["gutenberg_ids"]) | set(excl["lore_heldout"]["gutenberg_ids"]) | {u.get("gutenberg") for u in train_lt} | \
        {int(g) for b in v030_books for g in re.findall(r"\d+", b["gutenberg_ids"] or "")}
    bad_proj.discard(None)
    bad_gut.discard(None)
    bad_titles = {t.casefold() for t in excl["bench_books"]["titles"]} | {b["title"].casefold() for b in v030_books}
    meta_dir = next(SRC.glob("meta/**/SPEAKERS.TXT")).parent
    speakers = {}
    for line in (meta_dir / "SPEAKERS.TXT").read_text(errors="replace").splitlines():
        if not line.startswith(";"):
            p = [x.strip() for x in line.split("|")]
            if len(p) >= 5:
                speakers[p[0]] = p[4]
    chapters = {}
    for line in (meta_dir / "CHAPTERS.TXT").read_text(errors="replace").splitlines():
        if not line.startswith(";"):
            p = [x.strip() for x in line.split("|")]
            if len(p) >= 8:
                chapters[p[0]] = {"reader": p[1], "project": p[4], "book": p[5], "title": p[7]}
    meta = []
    for sub in ("test.clean", "test.other"):
        for f in sorted((SRC / "libritts" / "data" / sub).glob("*.parquet")):
            for k, r in enumerate(pq.read_table(f, columns=["id", "speaker_id", "chapter_id", "text_original"]).to_pylist()):
                meta.append(dict(r, file=str(f), row=k, subset=sub))
    stats: Counter = Counter({"test split utterances": len(meta)})
    finder = NameFinder([r["text_original"] for r in meta] + td.texts.get("libritts", []))
    rows = []
    for r in meta:
        spk, ch = str(r["speaker_id"]), str(r["chapter_id"])
        c = chapters.get(ch, {})
        if f"libritts:{spk}" in td.speakers or spk in v030_tts:
            stats["speaker in train, dev or v0.3.0 training data"] += 1
            continue
        if base_name(speakers.get(spk, "")) in bad_readers:
            stats["reader of a benchmark, lore held-out or v0.3.0 training book"] += 1
            continue
        proj = int(c["project"]) if c.get("project", "").isdigit() else None
        book = int(c["book"]) if c.get("book", "").isdigit() else None
        if not c or proj in bad_proj or book in bad_gut or c.get("title", "").casefold() in bad_titles or f"lt:{ch}" in td.groups:
            stats["chapter of a benchmark, held-out, v0.3.0 or train/dev book (or unknown)"] += 1
            continue
        text = r["text_original"].strip()
        if not text or not ok_text(text):
            stats["text with digits or symbols"] += 1
            continue
        if td.text_clash(text):
            stats["text shares 8 words with train, dev or benchmark"] += 1
            continue
        rows.append({"id": f"lt_{r['id']}", "source": "libritts", "split": "test", "subset": r["subset"], "speaker": f"libritts:{spk}",
                     "group": f"lt:{ch}", "session_shared": False, "reader": speakers.get(spk, ""), "librivox_project": proj, "gutenberg": book,
                     "text": text, "names": finder.find(text), "_file": r["file"], "_row": r["row"]})
    finish("libritts", rows, parquet_audio(), aligner, stats)


def noise() -> None:
    clips = json.loads((HERE / "fsd_test.json").read_text())["clips"]
    out = WORK / "noise"
    rows, dropped = [], Counter()
    for c in clips:
        f = SRC / "fsd" / "clips" / c["fsd_split"] / f"{c['fname']}.wav"
        if not f.exists():
            dropped["clip missing"] += 1
            continue
        x, rate = sf.read(f, dtype="float32")
        x = to_mono16k(x, rate)
        if len(x) < RATE:
            dropped["shorter than 1 s"] += 1
            continue
        if float(np.sqrt(np.mean(x.astype(np.float64) ** 2))) < 1e-4:
            dropped["silent"] += 1
            continue
        path = out / f"test_fsd_{c['fname']}.flac"
        meta = write_flac_checked(path, x / max(1.0, float(np.abs(x).max()) / 0.99))
        rows.append({**c, "split": "test", "path": str(path), "seconds": meta["seconds"], "sha256": meta["sha256"], "pcm_sha256": meta["pcm_sha256"]})
    # a clip whose energy envelope matches a train/dev noise file (a MUSAN file can be the same Freesound sound) is left out
    from check import NEAR_DUP, near_duplicates
    td = [n["path"] for n in json.loads((TRAINDEV / "noise" / "noise.json").read_text())["kept"]]
    best = {p: r for p, r, _ in near_duplicates([r["path"] for r in rows], td)}
    for r in rows:
        r["train_dev_envelope_max_corr"] = round(best[r["path"]], 3)
    dropped["envelope near-duplicate of a train/dev noise file"] = sum(r["train_dev_envelope_max_corr"] >= NEAR_DUP for r in rows)
    rows = [r for r in rows if r["train_dev_envelope_max_corr"] < NEAR_DUP]
    (out / "noise.json").write_text(json.dumps({"kept": rows, "dropped": dict(dropped)}, indent=1))
    log(f"noise: {len(rows)} files ({Counter(r['pool'] for r in rows)}), {sum(r['seconds'] for r in rows) / 3600:.2f} h; dropped {dict(dropped)}")


def main() -> None:
    which = sys.argv[1]
    if which == "noise":
        noise()
        return
    td = TrainDev()
    aligner = Aligner()
    {"voxpopuli": voxpopuli, "libritts": libritts}[which](aligner, td)


if __name__ == "__main__":
    main()
