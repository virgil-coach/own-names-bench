#!/usr/bin/env python3
"""Builds the own-names-bench v1.3 conversation test suite from the prepared test-split utterances (prep.py): one
own-names-bench suite per condition, `conv13-<cond>`, in the v1.2 suite format (entries, lists, clips, mentions,
name_free), so every system is run and scored by the benchmark's own code.

The conditions and their augmentation are the dev recipe's (lore-poc convdata/build.py, PLAN["dev"]; common.py is the
same code): xspk (the name taught from another person's recording; clean, MUSAN-like or street noise), conv
(spontaneous parliament speech, clean), tel (clip and every taught recording through a phone line), far (simulated
room, left quiet), street (traffic and street sounds at -2 to 15 dB SNR), level (quiet far-field clip, loud
close-talk taught recordings), near (a real name one or two sounds from the spoken one is always listed), short
(0.5-2 s around the name), and name-free pieces free_conv/tel/far/street/level/short (1.5-20 s utterances, and
0.4-2 s stretches for free_short) in the suite of their condition.

What differs from dev, so that the suite is fair to every system and needs no model output:
  - Clips are cut by the source, not by our engine's segmenter: a whole utterance (1.5-20 s), or for short / free_short
    a 0.5-2 s (0.4-2 s) stretch on the aligned word boundaries. No system is handed its own windowing.
  - The reference is the source's human transcript (dev labels were an untrained recognizer's transcript); no
    recognizer, spotter or other system is run on any test audio. The only model is the forced aligner in prep.py.
  - Every clip gets a 40-name list as the benchmark's suites do: a group of clips by one speaker (at most GROUP clips)
    shares one list, its taught names first (one per clip), then sound-alikes of them (and for near the three real
    sound-alikes of each), then other names of the test split, never a name that occurs in a reference of the group.
    The untaught variant is the benchmark's own `own-minus` pass (the spoken name taken off the list).
  - Lists prefer names never said in the conversation training data; every mention records `name_seen_in_train`
    (dev's definition: said in a train utterance of the conversation data), and its mention group is
    "name never seen in training" or "name seen in training", so the benchmark reports both rows.
  - Noise is FSD50K only (fsd_test.json: no train/dev clip or uploader), rooms are new (seed 13).

usage: build.py [--limit N]  -> suite/conv13-<cond>/suite.json, suite/conv13-<cond>/audio/..., build/build_stats.json
"""
import argparse
import json
import random
import re
import sys
import time
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np
import soundfile as sf
from rapidfuzz.distance import Levenshtein
from rapidfuzz.process import cdist

from common import RATE, SOURCES, SUITE, WORK, jsonl, letters, level, log, make_rirs, mix, reverb, telephone, write_flac_checked

sys.path.insert(0, str(Path(__file__).resolve().parent / "_onb"))
from own_names_bench.text import find_all, name_key, name_tokens, name_tokens_spans, nfc, ordinary_tokens  # noqa: E402

LIST_SIZE = 40
GROUP = 8          # clips per list group (one speaker)
PAD = 0.04
SEED = 1313
NAME_CAP = 4       # mentions of one name per condition

# named mentions / name-free pieces per (condition, source): dev-sized per condition (dev: xspk 600, conv 350, tel 270,
# far 350, street 320, level 300, near 350, short 360 mentions; 1,040 name-free pieces). FLEURS and NOTSOFAR shares
# of dev go to LibriTTS-R and VoxPopuli (README: why neither can be used).
PLAN = {
    "xspk": {"libritts": 380, "voxpopuli": 220},
    "conv": {"voxpopuli": 350},
    "tel": {"voxpopuli": 120, "libritts": 150},
    "far": {"voxpopuli": 150, "libritts": 200},
    "street": {"voxpopuli": 120, "libritts": 200},
    "level": {"voxpopuli": 120, "libritts": 180},
    "near": {"voxpopuli": 150, "libritts": 200},
    "short": {"voxpopuli": 150, "libritts": 210},
    "free_conv": {"voxpopuli": 200},
    "free_tel": {"voxpopuli": 100, "libritts": 100},
    "free_far": {"voxpopuli": 75, "libritts": 75},
    "free_street": {"voxpopuli": 70, "libritts": 80},
    "free_level": {"voxpopuli": 60, "libritts": 60},
    "free_short": {"voxpopuli": 200, "libritts": 220},
}
SEEN = "name seen in training"
UNSEEN = "name never seen in training"


class Data:
    def __init__(self) -> None:
        self.utts: dict[str, dict] = {}
        for src in ("voxpopuli", "libritts"):
            for u in jsonl(WORK / "utts" / f"{src}.jsonl"):
                self.utts[u["id"]] = u
        from common import TRAINDEV
        self.train_names = {letters(n["name"]) for p in sorted((TRAINDEV / "utts").glob("*.jsonl")) for u in jsonl(p)
                            if u["split"] == "train" for n in u["names"]}
        self.mentions: list[dict] = []
        for u in self.utts.values():
            if not u.get("words"):
                continue
            try:
                spans = word_spans(u["text"])
            except ValueError:
                continue
            for n in u["names"]:
                ws = u["words"][n["a"]:n["b"]]
                if not ws or any(w.get("score", 1.0) < 0.2 for w in ws):
                    continue
                t0, t1 = ws[0]["start"], ws[-1]["end"]
                if not 0.15 <= t1 - t0 <= 0.75 * (n["b"] - n["a"]) + 0.9:
                    continue
                self.mentions.append({"utt": u["id"], "name": n["name"], "key": letters(n["name"]), "a": n["a"], "b": n["b"], "t0": t0, "t1": t1,
                                      "speaker": u["speaker"], "source": u["source"], "group": u["group"], "span": [spans[n["a"]][0], spans[n["b"] - 1][1]]})
        self.by_key: dict[str, list[dict]] = defaultdict(list)
        for m in self.mentions:
            self.by_key[m["key"]].append(m)
        self.spelling = {k: Counter(m["name"] for m in ms).most_common(1)[0][0] for k, ms in self.by_key.items()}
        self.audio_cache: dict[str, np.ndarray] = {}
        log(f"test: {len(self.utts)} utterances, {len(self.mentions)} timed mentions of {len(self.by_key)} names "
            f"({sum(k not in self.train_names for k in self.by_key)} never said in train)")

    def audio(self, u: dict) -> np.ndarray:
        f = u["audio"]
        if f not in self.audio_cache:
            if len(self.audio_cache) > 256:
                self.audio_cache.clear()
            self.audio_cache[f] = sf.read(f, dtype="float32")[0]
        return self.audio_cache[f]

    def take_audio(self, m: dict) -> np.ndarray:
        x = self.audio(self.utts[m["utt"]])
        return x[max(0, int((m["t0"] - PAD) * RATE)):int((m["t1"] + PAD) * RATE)].copy()


def word_spans(text: str) -> list[tuple[int, int]]:
    """Character spans in nfc(text) of the whitespace words of text (text.split() and nfc(text).split() line up)."""
    t = nfc(text)
    spans = [(m.start(), m.end()) for m in re.finditer(r"\S+", t)]
    if len(spans) != len(text.split()):
        raise ValueError("nfc changed the word count")
    return spans


class Noise:
    def __init__(self, rng: random.Random) -> None:
        rows = json.loads((WORK / "noise" / "noise.json").read_text())["kept"]
        self.files = {k: [r["path"] for r in rows if r["pool"] == k] for k in ("musan", "street")}
        self.ids = {r["path"]: r["fname"] for r in rows}
        self.rng = rng
        self.cache: dict[str, np.ndarray] = {}
        self.used: Counter = Counter()
        log("noise: " + ", ".join(f"{k} {len(v)} files" for k, v in self.files.items()))
        if min(len(v) for v in self.files.values()) < 100:
            raise SystemExit("fewer than 100 noise files in a pool: run prep.py noise first")

    def get(self, pool: str = "musan") -> tuple[np.ndarray, str]:
        f = self.rng.choice(self.files[pool] or self.files["musan"])
        if f not in self.cache:
            self.cache[f] = sf.read(f, dtype="float32")[0]
        self.used[self.ids[f]] += 1
        return self.cache[f], f"fsd:{self.ids[f]}"


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--limit", type=int, default=0, help="smoke: at most this many items per (condition, source); writes under suite_smoke/")
    args = ap.parse_args()
    rng = random.Random(SEED)
    nrng = np.random.default_rng(SEED)
    D = Data()
    noise = Noise(rng)
    t = time.time()
    rirs = make_rirs(120, seed=13)
    log(f"{len(rirs)} simulated rooms in {time.time() - t:.0f}s")
    root = SUITE if not args.limit else SUITE.with_name("suite_smoke")
    stats: Counter = Counter()
    free_utts = [u for u in D.utts.values() if not u["names"]]
    by_source_free: dict[str, list[dict]] = defaultdict(list)
    for u in free_utts:
        by_source_free[u["source"]].append(u)
    keys_all = sorted(D.by_key)

    # ------------------------------------------------------------ augmentation (the dev recipe's, build.py)
    def babble(n_samples: int, avoid: str) -> np.ndarray:
        pool = [u for u in rng.sample(free_utts, min(len(free_utts), 40)) if u["speaker"] != avoid][:rng.randint(3, 6)]
        out = np.zeros(n_samples, dtype=np.float32)
        for u in pool:
            x = D.audio(u)
            x = np.tile(x, n_samples // max(1, len(x)) + 1)
            at = rng.randrange(0, max(1, len(x) - n_samples))
            out += x[at:at + n_samples] / (np.sqrt(np.mean(x ** 2)) + 1e-9)
        return out

    def far(x: np.ndarray, speaker: str) -> tuple[np.ndarray, dict]:
        room = rng.choice(rirs)
        y = reverb(x, room["rir"])
        kind = rng.choice(["noise", "babble", "both", "street"])
        info = {"aug": "far_sim", "rt60": room["rt60"], "distance": room["distance"], "room": room["room"], "noise": kind}
        if kind in ("noise", "both", "street"):
            nz, name = noise.get("street" if kind == "street" else "musan")
            y = mix(y, reverb(np.tile(nz, len(x) // len(nz) + 2)[:len(x) + RATE], room["noise_rir"]), snr := rng.uniform(0, 20), nrng)
            info.update(noise_file=name, snr=round(snr, 1))
        if kind in ("babble", "both"):
            b = reverb(babble(len(x), speaker), room["noise_rir"])
            y = mix(y, b, snr := rng.uniform(3, 15), nrng)
            info.update(babble_snr=round(snr, 1))
        return level(y, nrng, -42, -24), info

    def noisy(x: np.ndarray, pool: str = "musan") -> tuple[np.ndarray, dict]:
        nz, name = noise.get(pool)
        snr = rng.uniform(-2, 15) if pool == "street" else rng.uniform(5, 20)
        return level(mix(x, nz, snr, nrng), nrng), {"aug": "street" if pool == "street" else "noise", "noise_file": name, "snr": round(snr, 1)}

    def augment(cond: str, u: dict, clean_x: np.ndarray) -> tuple[np.ndarray, dict]:
        if cond == "xspk":
            r = rng.random()
            if r < 0.45:
                return noisy(clean_x, "street" if r < 0.2 else "musan")
            return clean_x, {"aug": "clean"}
        if cond == "conv":
            return clean_x, {"aug": "clean"}
        if cond == "tel":
            y, info = telephone(clean_x, nrng)
            return y, dict(info, aug="telephone")
        if cond == "street":
            return noisy(clean_x, "street")
        y, aug = far(clean_x, u["speaker"])
        if cond == "level":
            y = level(y, nrng, -50, -36)
            aug = dict(aug, level="quiet clip, loud taught recordings")
        return y, aug

    def dbfs(y: np.ndarray) -> float:
        return round(20 * np.log10(np.sqrt(np.mean(y.astype(np.float64) ** 2)) + 1e-9), 1)

    def teacher(m: dict, cond: str) -> dict | None:
        others = [o for o in D.by_key[m["key"]] if o["utt"] != m["utt"]]
        other_spk = [o for o in others if o["speaker"] != m["speaker"]]
        same_spk = [o for o in others if o["speaker"] == m["speaker"]]
        share = {"xspk": 1.0, "conv": 0.6}.get(cond, 0.75)
        teach = other_spk if (rng.random() < share and other_spk) or cond == "xspk" else (same_spk or other_spk)
        return rng.choice(teach) if teach else None

    def near_keys(key: str) -> list[str]:
        d = cdist([key], keys_all, scorer=Levenshtein.normalized_distance, workers=8)[0]
        order = np.argsort(d)
        return [keys_all[i] for i in order[:8] if keys_all[i] != key and d[i] <= 0.4 and not keys_all[i].startswith(key) and not key.startswith(keys_all[i])]

    def in_text(written: str, text: str) -> bool:
        k = name_key(written)
        return bool(find_all(name_tokens(text), k)) or letters(written) in {letters(w) for w in text.split()}

    # ------------------------------------------------------------ items
    def named_item(m: dict, cond: str, aug_cond: str) -> dict | None:
        u = D.utts[m["utt"]]
        take = teacher(m, cond)
        if take is None:
            stats[f"{cond}: no other recording of the name"] += 1
            return None
        near = near_keys(m["key"]) if cond == "near" else []
        if cond == "near" and not near:
            stats["near: no real name within 0.4 of the name"] += 1
            return None
        written = D.spelling[m["key"]]
        ref_span = nfc(u["text"])[m["span"][0]:m["span"][1]]
        if tuple(t for t in name_tokens(ref_span)) != name_key(written):
            stats[f"{cond}: the reference spells the name otherwise than the list"] += 1
            return None
        x = D.audio(u)
        if cond == "short":
            ws = u["words"]
            for _ in range(6):
                i = max(0, m["a"] - rng.choice([0, 0, 1, 2]))
                j = min(len(ws), m["b"] + rng.choice([0, 0, 1, 2]))
                t0, t1 = ws[i]["start"] - 0.08, ws[j - 1]["end"] + 0.08
                if 0.5 <= t1 - t0 <= 2.0:
                    break
            else:
                stats["short: no 0.5-2 s span around the name"] += 1
                return None
            t0 = max(0.0, t0)
            words = u["text"].split()[i:j]
            reference = " ".join(words)
            try:
                sp = word_spans(reference)
            except ValueError:
                return None
            span = [sp[m["a"] - i][0], sp[m["b"] - 1 - i][1]]
            clean = x[int(t0 * RATE):int(t1 * RATE)]
            win = [round(t0, 3), round(t1, 3)]
            name_at = [round(m["t0"] - t0, 3), round(m["t1"] - t0, 3)]
        else:
            reference, span, clean, win, name_at = u["text"], m["span"], x, [0.0, round(len(x) / RATE, 3)], [m["t0"], m["t1"]]
        y, aug = augment(aug_cond, u, clean)
        aug["clip_dbfs"] = dbfs(y)
        return {"kind": "named", "cond": cond, "m": m, "take": take, "utt": u, "y": y, "aug": aug, "reference": reference, "span": span,
                "win": win, "name_at": name_at, "near": near, "written": written}

    def short_free_item(u: dict, aug_cond: str) -> dict | None:
        ws, taken = u.get("words") or [], {k for n in u["names"] for k in range(n["a"], n["b"])}
        if len(ws) < 2:
            return None
        n_w = rng.choice([1, 2, 2, 3, 3, 4])
        i = rng.randrange(0, max(1, len(ws) - n_w))
        j = min(len(ws), i + n_w)
        if taken & set(range(i, j)):
            return None
        t0, t1 = max(0.0, ws[i]["start"] - 0.08), ws[j - 1]["end"] + 0.08
        if not 0.4 <= t1 - t0 <= 2.0:
            return None
        x = D.audio(u)[int(t0 * RATE):int(t1 * RATE)]
        if len(x) < int(0.3 * RATE):
            return None
        y, aug = augment(aug_cond, u, x)
        aug["clip_dbfs"] = dbfs(y)
        return {"kind": "free", "cond": "free_short", "utt": u, "y": y, "aug": aug, "reference": " ".join(w["word"] for w in ws[i:j]),
                "win": [round(t0, 3), round(t1, 3)]}

    def free_item(u: dict, cond: str, aug_cond: str) -> dict:
        y, aug = augment(aug_cond, u, D.audio(u))
        aug["clip_dbfs"] = dbfs(y)
        return {"kind": "free", "cond": cond, "utt": u, "y": y, "aug": aug, "reference": u["text"], "win": [0.0, round(len(y) / RATE, 3)]}

    # augmentation of a list group: short and near mix conditions as dev did, one per group (its taught recordings
    # are processed to match: phone line for tel, loud close-talk for level)
    def group_aug(cond: str) -> str:
        if cond == "short":
            return rng.choice(["conv", "conv", "tel", "far", "street", "level"])
        if cond == "near":
            return rng.choice(["conv", "conv", "conv", "tel", "far", "street"])
        return cond

    limit = args.limit
    suites: dict[str, dict] = {}
    for cond in [c for c in PLAN if not c.startswith("free")]:
        suites[cond] = {"groups": []}
    for cond, per_source in PLAN.items():
        base = cond[5:] if cond.startswith("free_") else cond
        for source, want in per_source.items():
            want = min(want, limit) if limit else want
            made = 0
            groups = suites[base]["groups"]
            if cond.startswith("free"):
                if cond == "free_short":
                    pool = [u for u in D.utts.values() if u["source"] == source and u.get("words")]
                else:
                    pool = list(by_source_free.get(source, []))
                rng.shuffle(pool)
                pool.sort(key=lambda u: u.get("session_shared", False))  # debate items not in train/dev first
                by_spk: dict[str, list[dict]] = defaultdict(list)
                for u in pool:
                    by_spk[u["speaker"]].append(u)
                open_groups: dict[str, dict] = {}
                for u in pool:
                    if made >= want:
                        break
                    g = open_groups.get(u["speaker"])
                    if g is None or len(g["items"]) >= GROUP:
                        g = {"cond": base, "kind": "free", "source": source, "speaker": u["speaker"], "items": [],
                             "aug_cond": group_aug(base) if base == "short" else base}
                        open_groups[u["speaker"]] = g
                        groups.append(g)
                    it = short_free_item(u, g["aug_cond"]) if cond == "free_short" else free_item(u, cond, g["aug_cond"])
                    if it is None:
                        continue
                    g["items"].append(it)
                    made += 1
            else:
                pool = [m for m in D.mentions if m["source"] == source]
                rng.shuffle(pool)
                # names never said in training first, then debate items not in train/dev
                pool.sort(key=lambda m: (m["key"] in D.train_names, D.utts[m["utt"]].get("session_shared", False)))
                used_utts: set[str] = set()
                per_name: Counter = Counter()
                open_groups = {}
                for m in pool:
                    if made >= want:
                        break
                    if m["utt"] in used_utts or per_name[m["key"]] >= NAME_CAP:
                        continue
                    g = open_groups.get(m["speaker"])
                    written = D.spelling[m["key"]]
                    u = D.utts[m["utt"]]
                    # one list per group: no taught name of the group may be said in another clip of it
                    if g is not None and (len(g["items"]) >= GROUP or m["key"] in {it["m"]["key"] for it in g["items"]}
                                          or any(in_text(it["written"], u["text"]) for it in g["items"])
                                          or any(in_text(written, it["utt"]["text"]) for it in g["items"])):
                        g = None
                    if g is None:
                        g = {"cond": base, "kind": "named", "source": source, "speaker": m["speaker"], "items": [], "aug_cond": group_aug(base)}
                        open_groups[m["speaker"]] = g
                        groups.append(g)
                    it = named_item(m, cond, g["aug_cond"])
                    if it is None:
                        continue
                    g["items"].append(it)
                    used_utts.add(m["utt"])
                    per_name[m["key"]] += 1
                    made += 1
            stats[f"planned {cond} {source}"] = made
            log(f"{cond} {source}: {made} of {want} ({time.time() - t:.0f}s)")

    # ------------------------------------------------------------ lists, taught recordings, suite files
    canon = {k: rng.choice(D.by_key[k]) for k in keys_all}
    unseen_keys = [k for k in keys_all if k not in D.train_names]
    seen_keys = [k for k in keys_all if k in D.train_names]
    licence_used: Counter = Counter()
    for cond, s in suites.items():
        name = f"conv13-{cond}"
        out = root / name
        entries: dict[str, dict] = {}
        lists: dict[str, dict] = {}
        clips: dict[str, dict] = {}
        mentions: list[dict] = []
        name_free: list[dict] = []
        n_clip = 0
        for gi, g in enumerate([g for g in s["groups"] if g["items"]]):
            book = f"{cond}-g{gi:04d}"
            texts = [it["utt"]["text"] for it in g["items"]] + [it["reference"] for it in g["items"]]
            own = [it for it in g["items"] if it["kind"] == "named"]
            own_keys = [it["m"]["key"] for it in own]
            blocked = set(own_keys)
            cand_ok = lambda k: k not in blocked and not any(in_text(D.spelling[k], tx) for tx in texts)  # noqa: E731
            picked: list[str] = []
            for it in own:  # the near condition: each mention's real sound-alikes, always listed
                for k in it["near"]:
                    if len([p for p in picked]) < 3 * len(own) and k not in picked and cand_ok(k):
                        picked.append(k)
            for k in own_keys:  # the closest-spelled real names of each taught name
                d = cdist([k], keys_all, scorer=Levenshtein.normalized_distance, workers=8)[0]
                close = [keys_all[i] for i in np.argsort(d)[:12] if keys_all[i] not in picked and cand_ok(keys_all[i])][:2]
                picked += close
            room = LIST_SIZE - len(own_keys) - len(picked)
            others = []
            for k in rng.sample(unseen_keys, min(len(unseen_keys), 4 * LIST_SIZE)) + rng.sample(seen_keys, min(len(seen_keys), 2 * LIST_SIZE)):
                if len(others) >= room:
                    break
                if k not in picked and k not in others and cand_ok(k):
                    if k in D.train_names and rng.random() < 0.6:  # mostly names never said in training
                        continue
                    others.append(k)
            keys = own_keys + (picked + others)[:LIST_SIZE - len(own_keys)]
            proc = "tel" if g["aug_cond"] == "tel" else ("loud" if g["aug_cond"] == "level" else "")
            group_utts = {it["utt"]["id"] for it in g["items"]}
            ids = []
            for k_i, k in enumerate(keys):
                if k in own_keys:
                    take = next(it["take"] for it in own if it["m"]["key"] == k)
                else:
                    take = canon[k] if canon[k]["utt"] not in group_utts else next((o for o in D.by_key[k] if o["utt"] not in group_utts), None)
                if take is None or take["utt"] in group_utts:
                    stats[f"{cond}: list name with no recording outside the group"] += 1
                    continue
                x = D.take_audio(take)
                if proc == "tel":
                    x, _ = telephone(np.pad(x, (1600, 1600)), nrng)
                    x = x[1600:-1600]
                elif proc == "loud":
                    x = level(x, nrng, -16, -10)
                rel = f"audio/enroll/{book}/{k_i:03d}.flac"
                meta = write_flac_checked(out / rel, x)
                eid = f"{book}/{k_i:03d}"
                entries[eid] = {"id": eid, "written": D.spelling[k], "book": book, "reader": take["speaker"], "group": cond,
                                "sample": f"suites/{name}/{rel}", "sample_sha256": meta["sha256"], "sample_pcm_sha256": meta["pcm_sha256"],
                                "sample_seconds": meta["seconds"], "sample_proc": proc or "close-talk", "source": take["source"],
                                "teach_utt": take["utt"], "name_seen_in_train": k in D.train_names}
                ids.append(eid)
            lists[f"own:{book}"] = {"kind": "own", "book": book, "entries": ids}
            listed = {letters(entries[e]["written"]): e for e in ids}
            for it in g["items"]:
                u = it["utt"]
                cid = f"{cond}-{n_clip:05d}"
                n_clip += 1
                if it["kind"] == "free" and any(in_text(entries[e]["written"], it["reference"]) or in_text(entries[e]["written"], u["text"]) for e in ids):
                    stats[f"{it['cond']}: dropped, a listed name in its text"] += 1
                    continue
                if it["kind"] == "named" and it["m"]["key"] not in listed:
                    stats[f"{cond}: dropped, taught name has no recording"] += 1
                    continue
                rel = f"audio/clips/{cid}.flac"
                meta = write_flac_checked(out / rel, it["y"])
                if "noise_file" in it["aug"]:
                    licence_used[it["aug"]["noise_file"]] += 1
                clips[cid] = {"id": cid, "audio": f"suites/{name}/{rel}", "sha256": meta["sha256"], "pcm_sha256": meta["pcm_sha256"],
                              "seconds": meta["seconds"], "book": book, "reader": u["speaker"], "reference": it["reference"],
                              "source": f"{SOURCES[u['source']]['repo']}@{SOURCES[u['source']]['revision'][:12]}:{u['id']}@{it['win'][0]}-{it['win'][1]}",
                              "corpus": u["source"], "cond": it["cond"], "aug": it["aug"], "session": u["group"],
                              "session_shared": bool(u.get("session_shared")), "kind": "mention" if it["kind"] == "named" else "name-free"}
                if it["kind"] == "named":
                    m = it["m"]
                    eid = listed[m["key"]]
                    seen = m["key"] in D.train_names
                    mentions.append({"id": f"{cid}:0", "clip": cid, "entry": eid, "span": it["span"], "group": SEEN if seen else UNSEEN,
                                     "cond": cond, "name_seen_in_train": seen, "teach_cross": entries[eid]["reader"] != m["speaker"],
                                     "name_at_s": it["name_at"], "near_listed": [listed[k] for k in it["near"][:3] if k in listed]})
                    stats[f"mentions {cond} {u['source']}"] += 1
                else:
                    name_free.append({"id": f"free:{cid}", "clip": cid, "cond": it["cond"]})
                    stats[f"name-free {it['cond']} {u['source']}"] += 1
        name_words = sorted({w for e in entries.values() for w in ordinary_tokens(e["written"]) if not w.isdigit()})
        doc = {"suite": name, "version": "1.3.0-test", "condition": cond, "sealed": True,
               "source": {k: {"repo": SOURCES[k]["repo"], "revision": SOURCES[k]["revision"]} for k in ("voxpopuli", "libritts", "fsd")},
               "licence": "CC BY 4.0", "rehosted": True, "attribution": ATTRIBUTION,
               "entries": entries, "lists": lists, "clips": clips, "mentions": mentions, "name_free": name_free, "name_words": name_words,
               "not_names": [], "dropped": {k: v for k, v in stats.items() if k.startswith(f"{cond}:") or k.startswith(f"free_{cond}:")}}
        out.mkdir(parents=True, exist_ok=True)
        (out / "suite.json").write_text(json.dumps(doc, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
        stats[f"suite {name}: clips"] = len(clips)
        stats[f"suite {name}: mentions"] = len(mentions)
        stats[f"suite {name}: name-free"] = len(name_free)
        stats[f"suite {name}: entries"] = len(entries)
        stats[f"suite {name}: lists"] = len(lists)
        log(f"{name}: {len(clips)} clips ({sum(c['seconds'] for c in clips.values()) / 3600:.2f} h), {len(mentions)} mentions "
            f"({sum(not mn['name_seen_in_train'] for mn in mentions)} names never seen in training), {len(name_free)} name-free, {len(lists)} lists")
    stats["noise files used"] = len(noise.used)
    (WORK / ("build_stats.json" if not limit else "build_smoke_stats.json")).write_text(json.dumps(dict(sorted(stats.items())), indent=1))
    (WORK / "noise_used.json").write_text(json.dumps(dict(noise.used), indent=1))
    log(f"DONE build in {time.time() - t:.0f}s")


ATTRIBUTION = ("Audio: VoxPopuli (Wang et al., 2021; European Parliament recordings, CC0 1.0), test split; LibriTTS-R (Koizumi et al., "
               "2023; restored LibriTTS, from LibriVox public-domain recordings, CC BY 4.0), test-clean and test-other; background "
               "noise from FSD50K (Fonseca et al., 2022; CC BY 4.0), clips under CC0 1.0 or CC BY 3.0 credited by uploader in "
               "NOISE_ATTRIBUTION.csv. Simulated rooms: pyroomacoustics (MIT). Lists, mentions and processing: own-names-bench, CC BY 4.0.")


if __name__ == "__main__":
    main()
