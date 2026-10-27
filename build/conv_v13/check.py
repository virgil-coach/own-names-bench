#!/usr/bin/env python3
"""Contamination check of the v1.3 conversation test suite against the conversation train and dev data
($CONV_TRAINDEV: utterances, rows, noise), own-names-bench v1.2.0 (excl.json), the v0.3.0 adapter's training data
(attribution_v030/) and the corpora reserved for v1.3 (ICSI, Earnings-21). Exits non-zero on any failure and writes
build/contamination.json (counts and ids only: no transcript or name is written).

  sources    every test utterance is VoxPopuli test or LibriTTS-R test-clean/test-other; every noise file an FSD50K clip
             of fsd_test.json; no id, path or session names a benchmark or reserved corpus
  speakers   no test speaker is a train or dev speaker, a benchmark suite speaker, a benchmark / lore held-out reader,
             a v0.3.0 LibriTTS speaker or a reader of a v0.3.0 LibriVox book
  sessions   no LibriTTS-R chapter or book (LibriVox project, Gutenberg id) is in train, dev, the benchmark or v0.3.0's
             books; VoxPopuli debate items shared with train or dev are counted and allowed (speaker-disjoint, as dev)
  recordings no test utterance id, audio file or taught-recording source is a train or dev one
  audio      SHA-256 of every test file (file and 16-bit PCM) against every train/dev file (utterances, windows, taught
             recordings, noise) and every benchmark audio hash
  text       no test text shares a run of 8 normalized words with a train or dev utterance or a benchmark reference
  noise      no test noise clip is a train/dev noise file by clip id, uploader, file or PCM hash, or by its energy
             20 ms energy envelope (a near-duplicate of a MUSAN or FSD50K train/dev file: Pearson >= 0.95 over >= 2 s)
  rooms      no simulated test room equals a train or dev room (seeds 1 and 2 of the recipe; test seed 13)
  names      reported, not failed: test names said in train utterances (the `name_seen_in_train` share)

usage: check.py  -> build/contamination.json
"""
import csv
import hashlib
import json
import re
import sys
from collections import Counter
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

import numpy as np
import soundfile as sf

from common import RATE, SUITE, TRAINDEV, WORK, jsonl, letters, log, make_rirs

HERE = Path(__file__).resolve().parent
BANNED = re.compile(r"apptek|svq|simple.?voice|\bami\b|edinburghcstr|modulate|mlcommons|people.?s.?speech|earnings.?2[12]|icsi|notsofar|fleurs", re.I)


def sha_pair(path: str) -> tuple[str, str, str]:
    data = Path(path).read_bytes()
    try:
        x, _ = sf.read(path, dtype="int16")
        pcm = hashlib.sha256(x.astype("<i2").tobytes()).hexdigest()
    except Exception:  # noqa: BLE001 - an unreadable file is reported by its hash alone
        pcm = ""
    return path, hashlib.sha256(data).hexdigest(), pcm


def hash_all(files: list[str]) -> dict[str, tuple[str, str]]:
    with ProcessPoolExecutor(16) as ex:
        return {p: (a, b) for p, a, b in ex.map(sha_pair, sorted(files), chunksize=64)}


def grams(text: str, n: int = 8) -> set[tuple[str, ...]]:
    w = re.findall(r"[a-z']+", text.lower())
    return {tuple(w[i:i + n]) for i in range(len(w) - n + 1)}


def base_name(s: str) -> str:
    return re.sub(r"\s*\(.*?\)\s*", "", s).strip().casefold()


HOP_S = 0.02        # envelope resolution: 20 ms log-energy frames
MIN_OVERLAP = 100   # frames (2 s) of overlap for a comparison


def envelope(path: str) -> np.ndarray:
    """Log-energy envelope at 20 ms (level-independent up to an offset, which Pearson correlation ignores)."""
    x, _ = sf.read(path, dtype="float32")
    x = x if x.ndim == 1 else x.mean(axis=1)
    hop = int(RATE * HOP_S)
    n = len(x) // hop
    if not n:
        return np.zeros(0)
    return np.log10(np.mean(x[:n * hop].reshape(n, hop).astype(np.float64) ** 2, axis=1) + 1e-10)


def pearson_lags(a: np.ndarray, b: np.ndarray) -> np.ndarray:
    """Pearson correlation of the overlapping parts of a and b at every lag with at least MIN_OVERLAP frames
    (lag k pairs a[n + k] with b[n])."""
    la, lb = len(a), len(b)
    size = 1 << (la + lb - 2).bit_length()
    c = np.fft.irfft(np.fft.rfft(a, size) * np.conj(np.fft.rfft(b, size)), size)
    lags = np.arange(-(lb - 1), la)
    sab = np.concatenate([c[size - (lb - 1):], c[:la]]) if lb > 1 else c[:la]
    i0, i1 = np.maximum(0, lags), np.minimum(la, lags + lb)       # a[i0:i1]
    j0, j1 = i0 - lags, i1 - lags                                   # b[j0:j1]
    n = (i1 - i0).astype(np.float64)
    ca, ca2 = np.concatenate([[0], np.cumsum(a)]), np.concatenate([[0], np.cumsum(a * a)])
    cb, cb2 = np.concatenate([[0], np.cumsum(b)]), np.concatenate([[0], np.cumsum(b * b)])
    sa, sa2 = ca[i1] - ca[i0], ca2[i1] - ca2[i0]
    sb, sb2 = cb[j1] - cb[j0], cb2[j1] - cb2[j0]
    with np.errstate(invalid="ignore", divide="ignore"):
        r = (sab - sa * sb / n) / np.sqrt(np.maximum(sa2 - sa * sa / n, 1e-12) * np.maximum(sb2 - sb * sb / n, 1e-12))
    return np.where(n >= MIN_OVERLAP, r, -1.0)


def env_job(args: tuple[str, list[str]]) -> tuple[str, float, str]:
    """Best Pearson correlation of a test noise envelope against every train/dev envelope (>= 2 s overlap)."""
    test_path, others = args
    a = envelope(test_path)
    best, which = 0.0, ""
    if len(a) < MIN_OVERLAP:
        return test_path, best, which
    for p in others:
        b = ENVS.get(p)
        if b is None or len(b) < MIN_OVERLAP:
            continue
        r = float(np.max(pearson_lags(a, b)))
        if r > best:
            best, which = r, p
    return test_path, best, which


ENVS: dict[str, np.ndarray] = {}
NEAR_DUP = 0.95


def _set_envs(envs: dict[str, np.ndarray]) -> None:
    ENVS.update(envs)


def near_duplicates(test_paths: list[str], td_paths: list[str]) -> list[tuple[str, float, str]]:
    """(test file, best correlation, train/dev file) for every test noise file."""
    with ProcessPoolExecutor(16) as ex:
        for p, e in zip(td_paths, ex.map(envelope, td_paths, chunksize=16)):
            ENVS[p] = e
    with ProcessPoolExecutor(16, initializer=_set_envs, initargs=(dict(ENVS),)) as ex:
        return list(ex.map(env_job, [(p, td_paths) for p in test_paths], chunksize=4))


def main() -> None:
    fails: list[str] = []
    excl = json.loads((HERE / "excl.json").read_text())
    res: dict = {"against": {"train_dev": str(TRAINDEV), "benchmark": excl["bench"], "reserved_for_v1_3": ["ICSI", "Earnings-21"],
                             "v030_training_data": "attribution_v030/ (LibriTTS speakers, LibriVox books and readers)"}}
    td_utts = [u for p in sorted((TRAINDEV / "utts").glob("*.jsonl")) for u in jsonl(p)]
    td_rows = {s: list(jsonl(TRAINDEV / "rows" / f"{s}.jsonl")) for s in ("train", "dev")}
    td_noise = json.loads((TRAINDEV / "noise" / "noise.json").read_text())["kept"]
    test_utts = [u for s in ("voxpopuli", "libritts") for u in jsonl(WORK / "utts" / f"{s}.jsonl")]
    test_noise = json.loads((WORK / "noise" / "noise.json").read_text())["kept"]
    suites = {p.parent.name: json.loads(p.read_text()) for p in sorted(SUITE.glob("conv13-*/suite.json"))}
    used_utt_ids = {c["source"].split(":", 1)[1].rsplit("@", 1)[0] for s in suites.values() for c in s["clips"].values()}
    used_utt_ids |= {e["teach_utt"] for s in suites.values() for e in s["entries"].values()}
    by_id = {u["id"]: u for u in test_utts}
    used = [by_id[i] for i in sorted(used_utt_ids)]
    res["counts"] = {"train_dev_utterances": len(td_utts), "train_rows": len(td_rows["train"]), "dev_rows": len(td_rows["dev"]),
                     "train_dev_noise_files": len(td_noise), "test_utterances_prepared": len(test_utts), "test_utterances_used": len(used),
                     "test_noise_files": len(test_noise), "suites": len(suites)}
    if len(td_rows["train"]) != 23211 or len(td_rows["dev"]) != 7662:
        fails.append(f"train/dev rows: {len(td_rows['train'])}/{len(td_rows['dev'])}, expected 23,211/7,662")

    # sources
    fsd_ids = {c["fname"] for c in json.loads((HERE / "fsd_test.json").read_text())["clips"]}
    bad = [u["id"] for u in test_utts if u["source"] not in ("voxpopuli", "libritts") or u["split"] != "test"
           or BANNED.search(u["id"]) or BANNED.search(u["group"])]
    bad += [n["path"] for n in test_noise if n["fname"] not in fsd_ids]
    bad += [c["id"] for s in suites.values() for c in s["clips"].values() if BANNED.search(c["source"])]
    bad += [p for p in [str(SUITE), str(WORK)] if re.search(r"ctxft|convdata|lore-conv|v06-", p)]
    res["sources"] = {"test_utterances_by_source": dict(Counter(u["source"] for u in test_utts)),
                      "used_by_source": dict(Counter(u["source"] for u in used)), "bad": len(bad)}
    if bad:
        fails.append(f"sources: {len(bad)} items not from an allowed test split or path")

    # speakers
    v030_books = list(csv.DictReader((HERE / "attribution_v030" / "librivox_books.csv").open()))
    v030_tts = {f"libritts:{r['speaker_id']}" for r in csv.DictReader((HERE / "attribution_v030" / "libritts.csv").open())}
    td_spk = {u["speaker"] for u in td_utts} | {r["speaker"] for rs in td_rows.values() for r in rs} | \
        {r.get("teach_speaker") for rs in td_rows.values() for r in rs if r.get("teach_speaker")}
    test_spk = {u["speaker"] for u in test_utts} | {e["reader"] for s in suites.values() for e in s["entries"].values()}
    suite_spk = {x for v in excl["bench_speakers"].values() for x in v}
    readers = {base_name(r) for r in excl["bench_readers"] + excl["lore_heldout"]["readers"]} | \
        {base_name(x) for b in v030_books for x in re.split(r"[;,]\s*", b["readers"]) if x.strip()}
    sp = {"train_dev": sorted(test_spk & td_spk), "benchmark_suite_ids": sorted({s.split(":", 1)[-1] for s in test_spk} & suite_spk),
          "v030_libritts": sorted(test_spk & v030_tts),
          "benchmark_lore_v030_readers": sorted({u["reader"] for u in test_utts if base_name(u.get("reader", "")) in readers})}
    res["speakers"] = {"test_speakers": len(test_spk), "train_dev_speakers": len(td_spk), **{k: len(v) for k, v in sp.items()}}
    if any(sp.values()):
        fails.append("speakers: " + ", ".join(f"{k} {len(v)}" for k, v in sp.items() if v))

    # sessions
    td_groups = {u["group"] for u in td_utts}
    lt = [u for u in test_utts if u["source"] == "libritts"]
    td_lt = [u for u in td_utts if u["source"] == "libritts"]
    books_proj = set(excl["bench_books"]["librivox_ids"]) | set(excl["lore_heldout"]["librivox_ids"]) | {u.get("librivox_project") for u in td_lt} | \
        {int(b["librivox_id"]) for b in v030_books if b["librivox_id"].isdigit()}
    books_gut = set(excl["bench_books"]["gutenberg_ids"]) | set(excl["lore_heldout"]["gutenberg_ids"]) | {u.get("gutenberg") for u in td_lt} | \
        {int(g) for b in v030_books for g in re.findall(r"\d+", b["gutenberg_ids"] or "")}
    books_proj.discard(None)
    books_gut.discard(None)
    ch_bad = sorted({u["group"] for u in lt if u["group"] in td_groups or u.get("librivox_project") in books_proj or u.get("gutenberg") in books_gut})
    vp_used = [u for u in used if u["source"] == "voxpopuli"]
    vp_shared = sorted({u["group"] for u in vp_used if u["group"] in td_groups})
    res["sessions"] = {"libritts_chapters": len({u["group"] for u in lt}), "libritts_chapters_or_books_shared": len(ch_bad),
                       "voxpopuli_debate_items_used": len({u["group"] for u in vp_used}),
                       "voxpopuli_debate_items_shared_with_train_dev (allowed: speaker-disjoint, as dev)": len(vp_shared),
                       "voxpopuli_utterances_used_in_a_shared_debate_item": sum(u["group"] in td_groups for u in vp_used),
                       "voxpopuli_utterances_used": len(vp_used)}
    if ch_bad:
        fails.append(f"sessions: {len(ch_bad)} LibriTTS-R chapters/books shared")

    # recordings
    td_ids = {u["id"] for u in td_utts} | {r.get("utt") for rs in td_rows.values() for r in rs} | {r.get("teach_utt") for rs in td_rows.values() for r in rs}
    rec_bad = sorted(used_utt_ids & td_ids)
    res["recordings"] = {"test_utterances_used": len(used_utt_ids), "shared_with_train_dev": len(rec_bad)}
    if rec_bad:
        fails.append(f"recordings: {len(rec_bad)} test utterances are train/dev utterances")

    # audio hashes
    td_files = {u["audio"] for u in td_utts if "audio" in u} | {u[k] for u in td_utts for k in ("far", "ct") if k in u} | {n["path"] for n in td_noise}
    for rs in td_rows.values():
        for r in rs:
            td_files.add(r["audio"]["file"])
            td_files |= {e["rec"]["file"] for e in r["entries"]}
    test_files = {u["audio"] for u in test_utts} | {n["path"] for n in test_noise} | {str(p) for p in SUITE.rglob("*.flac")}
    log(f"hashing {len(td_files)} train/dev files and {len(test_files)} test files")
    td_h = hash_all(sorted(td_files))
    te_h = hash_all(sorted(test_files))
    td_set = {h for pair in td_h.values() for h in pair if h}
    bench = set(excl["bench_audio_sha256"])
    zero = hashlib.sha256(b"").hexdigest()
    a_td = sorted(p for p, pair in te_h.items() if set(pair) & td_set)
    a_bench = sorted(p for p, pair in te_h.items() if set(pair) & bench)
    dup = Counter(pair[0] for pair in te_h.values())
    res["audio"] = {"train_dev_files_hashed": len(td_h), "test_files_hashed": len(te_h), "benchmark_hashes": len(bench),
                    "test_equal_to_train_dev": len(a_td), "test_equal_to_benchmark": len(a_bench),
                    "train_dev_files_unreadable": sum(1 for pair in td_h.values() if not pair[1]),
                    "test_files_empty": sum(pair[0] == zero for pair in te_h.values()),
                    "test_files_with_a_repeated_hash": sum(n for n in dup.values() if n > 1)}
    if a_td or a_bench or res["audio"]["test_files_empty"]:
        fails.append(f"audio: {len(a_td)} test files hash-equal to train/dev, {len(a_bench)} to the benchmark")

    # text
    tg: dict[tuple, int] = {}
    for t in [u["text"] for u in td_utts] + excl["bench_texts"]:
        for g in grams(t):
            tg[g] = 1
    text_hits = [u["id"] for u in test_utts if grams(u["text"]) & tg.keys()]
    res["text"] = {"test_texts": len(test_utts), "train_dev_and_benchmark_texts": len(td_utts) + len(excl["bench_texts"]),
                   "sharing_an_8_word_run": len(text_hits)}
    if text_hits:
        fails.append(f"text: {len(text_hits)} test texts share an 8-word run")

    # noise
    street = json.loads((HERE / "fsd_street.json").read_text())["clips"]
    td_fsd = {c["fname"] for c in street}
    td_up = {c["uploader"] for c in street}
    nz = {"clip_ids_shared": sorted({n["fname"] for n in test_noise} & td_fsd),
          "uploaders_shared": sorted({n["uploader"] for n in test_noise} & td_up)}
    te_noise_h = {te_h[n["path"]] for n in test_noise}
    td_noise_h = {td_h[n["path"]] for n in td_noise}
    nz["files_hash_equal"] = len({h for pair in te_noise_h for h in pair} & {h for pair in td_noise_h for h in pair})
    log(f"noise envelopes: {len(test_noise)} test against {len(td_noise)} train/dev files")
    env = near_duplicates([n["path"] for n in test_noise], [n["path"] for n in td_noise])
    near = [(Path(p).name, round(r, 3), Path(w).name) for p, r, w in env if r >= NEAR_DUP]
    nz["envelope_near_duplicates"] = len(near)
    nz["envelope_max_correlation"] = round(max((r for _, r, _ in env), default=0.0), 3)
    nz["envelope_near_duplicate_pairs"] = near[:50]
    res["noise"] = {k: (len(v) if isinstance(v, list) and k != "envelope_near_duplicate_pairs" else v) for k, v in nz.items()}
    if nz["clip_ids_shared"] or nz["uploaders_shared"] or nz["files_hash_equal"] or near:
        fails.append(f"noise: {len(nz['clip_ids_shared'])} clips, {len(nz['uploaders_shared'])} uploaders, {nz['files_hash_equal']} files, "
                     f"{len(near)} envelope near-duplicates shared")

    # rooms
    def key(r: dict) -> tuple:
        return (tuple(r["room"]), r["rt60"], r["distance"])
    td_rooms = {key(r) for r in make_rirs(300, seed=1)} | {key(r) for r in make_rirs(120, seed=2)}
    te_rooms = {key(r) for r in make_rirs(120, seed=13)}
    res["rooms"] = {"test_rooms": len(te_rooms), "train_dev_rooms": len(td_rooms), "shared": len(te_rooms & td_rooms)}
    if te_rooms & td_rooms:
        fails.append("rooms: a test room equals a train/dev room")

    # names (reported)
    train_names = {letters(n["name"]) for u in td_utts if u["split"] == "train" for n in u["names"]}
    mns = [mn for s in suites.values() for mn in s["mentions"]]
    listed = [e for s in suites.values() for e in s["entries"].values()]
    res["names"] = {"mentions": len(mns), "mentions_name_never_seen_in_train": sum(not mn["name_seen_in_train"] for mn in mns),
                    "list_entries": len(listed), "list_entries_never_seen_in_train": sum(not e["name_seen_in_train"] for e in listed),
                    "distinct_test_names_on_lists": len({letters(e["written"]) for e in listed}),
                    "distinct_on_lists_never_seen_in_train": len({letters(e["written"]) for e in listed} - train_names)}

    res["fails"] = fails
    res["verdict"] = "PASS" if not fails else "FAIL"
    (WORK / "contamination.json").write_text(json.dumps(res, indent=1, ensure_ascii=False))
    print(json.dumps({k: v for k, v in res.items()}, indent=1, ensure_ascii=False)[:8000])
    print(res["verdict"], fails)
    sys.exit(0 if not fails else 1)


if __name__ == "__main__":
    main()
