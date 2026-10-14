"""v1.2 build, `cut` stage: audio cut from the sources, lists, suites. Imported by build_v12.py."""

import collections
import glob
import hashlib
import io
import json
import random
from pathlib import Path

import numpy as np
import soundfile as sf

from build_v12 import AMI_GROUPS, AMI_STRETCHES, LIST_SIZE, SEED, SOURCES, STRETCH_S
from own_names_bench.text import find_all, name_key, name_tokens, ordinary_tokens

PAD_S = 0.08
ENROLL_S = (0.15, 2.5)
LICENCE_TEXT = {
    "CC BY-SA 4.0": "Creative Commons Attribution-ShareAlike 4.0 International, https://creativecommons.org/licenses/by-sa/4.0/",
    "CC BY 4.0": "Creative Commons Attribution 4.0 International, https://creativecommons.org/licenses/by/4.0/",
}


def pcm_sha(x: np.ndarray) -> str:
    pcm = np.clip(np.round(x * 32768.0), -32768, 32767).astype("<i2")
    return hashlib.sha256(pcm.tobytes()).hexdigest()


ONLY: set[str] = {"calls", "svq", "ami", "modulate"}  # suites this run may write (cut --only)


def write_flac(root: Path, rel: str, x: np.ndarray) -> dict:
    if root.name not in ONLY:  # a suite kept as built: never touch its files
        return {"audio": rel, "sha256": "", "seconds": round(len(x) / 16000, 3)}
    p = root / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    pcm = np.clip(np.round(x * 32768.0), -32768, 32767).astype(np.int16)
    sf.write(p, pcm, 16000, subtype="PCM_16", format="FLAC")
    return {"audio": rel, "sha256": hashlib.sha256(p.read_bytes()).hexdigest(), "seconds": round(len(x) / 16000, 3)}


def build_lists(groups: dict[str, list[str]], entries: dict[str, dict], texts: dict[str, list[str]], rng: random.Random) -> dict:
    """own:<group>: the group's taught names (as ordered), then names taught elsewhere in the suite,
    never one that occurs anywhere in the group's reference text, up to LIST_SIZE."""
    everyone = sorted(entries)
    lists = {}
    for g, own in sorted(groups.items()):
        toks = [name_tokens(t) for t in texts.get(g, [])]
        own_keys = {name_key(entries[e]["written"]) for e in own}
        others = [e for e in everyone if e not in own and name_key(entries[e]["written"]) not in own_keys
                  and not any(find_all(tk, name_key(entries[e]["written"])) for tk in toks)]
        rng.shuffle(others)
        picked, keys = list(own), set(own_keys)
        for e in others:
            if len(picked) >= LIST_SIZE:
                break
            k = name_key(entries[e]["written"])
            if k not in keys:
                picked.append(e)
                keys.add(k)
        lists[f"own:{g}"] = {"kind": "own", "book": g, "entries": picked}
    return lists


def cut(args) -> None:
    global ONLY
    ONLY = set((args.only or "calls,svq,ami,modulate").split(","))
    src = Path(args.src)
    plan = json.loads((src / "plan.json").read_text())
    align = json.loads(Path(args.align).read_text())["spans"]
    root = Path(args.dataset)
    rng = random.Random(SEED + 7)
    suites = {}

    # ---------------- calls
    out = root / "suites" / "calls"
    entries, clips, mentions, free, groups, spoken = {}, {}, [], [], collections.defaultdict(list), {}
    dropped = collections.Counter()
    for c in plan["calls"]:
        cid = c["call"]
        wav = src / "apptek" / "diarization" / c["accent"] / c["file"]
        x, sr = sf.read(wav, dtype="float32")
        assert sr == 16000
        if x.ndim > 1:
            x = x.mean(axis=1)
        segs = {s["i"]: s for s in c["segments"]}
        spoken[cid] = [s["text"] for s in c["segments"]]
        ok = set()
        for eid, e in c["entries"].items():
            sp = align.get(f"enroll:{eid}")
            if not sp or not (ENROLL_S[0] <= sp["end"] - sp["start"] <= ENROLL_S[1]):
                dropped["calls enrollment not aligned"] += 1
                continue
            a, b = int((sp["start"] - PAD_S) * sr), int((sp["end"] + PAD_S) * sr)
            meta = write_flac(out, f"audio/enroll/{cid}/{len(ok):03d}.flac", x[max(0, a):b])
            entries[eid] = {"id": eid, "written": e["written"], "book": cid, "reader": e["speaker"], "group": "call",
                            "sample": f"suites/calls/{meta['audio']}", "sample_sha256": meta["sha256"], "sample_seconds": meta["seconds"],
                            "accent": c["accent"]}
            groups[cid].append(eid)
            ok.add(eid)
        n_in_seg = collections.Counter()
        for mn in c["mentions"]:
            if mn["entry"] not in ok:
                continue
            s = segs[mn["seg"]]
            clip_id = f"calls-{cid}-t{mn['seg']:04d}"
            if clip_id not in clips:
                a, b = int(s["start"] * sr), int(s["end"] * sr)
                meta = write_flac(out, f"audio/clips/{cid}/{mn['seg']:04d}.flac", x[a:b])
                clips[clip_id] = {"id": clip_id, "audio": f"suites/calls/{meta['audio']}", "sha256": meta["sha256"], "seconds": meta["seconds"],
                                  "book": cid, "reader": s["speaker"], "reference": s["text"], "source": f"{c['file']}@{s['start']}-{s['end']}",
                                  "accent": c["accent"]}
            k = n_in_seg[(clip_id, mn["entry"])]
            n_in_seg[(clip_id, mn["entry"])] += 1
            mentions.append({"id": f"{clip_id}:{mn['entry'].split('/')[-1]}:{k}", "clip": clip_id, "entry": mn["entry"], "span": mn["span"],
                             "group": "taught by the same speaker" if mn["same_speaker"] else "taught by the other speaker"})
        for k, st in enumerate(c["stretches"]):
            ss = [segs[i] for i in st]
            text = " ".join(s["text"] for s in ss)
            a, b = int(ss[0]["start"] * sr), int(max(x["end"] for x in ss) * sr)
            clip_id = f"calls-{cid}-s{k}"
            meta = write_flac(out, f"audio/free/{cid}/{k}.flac", x[a:b])
            clips[clip_id] = {"id": clip_id, "audio": f"suites/calls/{meta['audio']}", "sha256": meta["sha256"], "seconds": meta["seconds"],
                              "book": cid, "reader": "both", "reference": text, "source": f"{c['file']}@{ss[0]['start']}-{max(x['end'] for x in ss)}",
                              "accent": c["accent"], "kind": "stretch"}
            free.append({"id": f"free:{clip_id}", "clip": clip_id})
    # every call has a list, even one with no taught name of its own (its stretches still need one)
    for c in plan["calls"]:
        groups.setdefault(c["call"], [])
    lists = build_lists(groups, entries, spoken, rng)
    # a stretch keeps only if none of its list's names is in its reference
    keep_free = []
    for nf in free:
        clip = clips[nf["clip"]]
        toks = name_tokens(clip["reference"])
        lst = lists[f"own:{clip['book']}"]["entries"]
        if any(find_all(toks, name_key(entries[e]["written"])) for e in lst):
            dropped["calls stretch holding a listed name"] += 1
            del clips[nf["clip"]]
            continue
        keep_free.append(nf)
    used = {m["clip"] for m in mentions} | {nf["clip"] for nf in keep_free}
    clips = {k: v for k, v in clips.items() if k in used}
    suites["calls"] = {"entries": entries, "lists": lists, "clips": clips, "mentions": mentions, "name_free": keep_free, "dropped": dropped}

    import pyarrow.parquet as pq

    only = ONLY
    # ---------------- svq

    out = root / "suites" / "svq"
    need = {r["utt_id"] for it in plan["svq"]["items"] for r in [it["enroll"], *it["tests"]]} | {r["utt_id"] for r in plan["svq"]["free"]}
    utts = {}
    for p in sorted(glob.glob(str(src / "svq" / "2.0.0" / "utts_en_*.parquet"))):
        t = pq.read_table(p, columns=["utt_id", "waveform", "candidate_salient_terms", "candidate_salient_terms_timestamps", "speaker_id",
                                      "locale", "environment"])
        for r in t.to_pylist():
            if r["utt_id"] in need:
                utts[r["utt_id"]] = r
    entries, clips, mentions, free, groups, spoken = {}, {}, [], [], collections.defaultdict(list), {}
    dropped = collections.Counter()

    def svq_audio(r: dict) -> np.ndarray:
        y, sr = sf.read(io.BytesIO(r["waveform"]["bytes"]), dtype="float32")
        assert sr == 16000
        return y if y.ndim == 1 else y.mean(axis=1)

    for n, it in enumerate(plan["svq"]["items"]):
        g = f"q{n:03d}"
        er = utts.get(it["enroll"]["utt_id"])
        spoken[g] = [it["text"]]
        if er is None:
            dropped["svq enrollment reading missing"] += 1
            continue
        terms = er["candidate_salient_terms"] or []
        stamps = er["candidate_salient_terms_timestamps"] or []
        y = svq_audio(er)
        ok = []
        for k, (nm, a, b) in enumerate(it["names"]):
            words = [w.lower() for w in nm.replace("-", " ").split()]
            spans = []
            for w in words:
                ts = [stamps[i] for i, t in enumerate(terms) if t == w]
                if not ts:
                    break
                spans.append((float(np.median([t[0] for t in ts])), float(np.median([t[1] for t in ts]))))
            if len(spans) != len(words):
                dropped["svq name without word times"] += 1
                continue
            s0, s1 = min(s for s, _ in spans), max(e for _, e in spans)
            if not (ENROLL_S[0] <= s1 - s0 <= 3.5):
                dropped["svq name time implausible"] += 1
                continue
            eid = f"svq/{g}/{nm}"
            meta = write_flac(out, f"audio/enroll/{g}/{k}.flac", y[max(0, int((s0 - PAD_S) * 16000)):int((s1 + PAD_S) * 16000)])
            entries[eid] = {"id": eid, "written": nm, "book": g, "reader": er["speaker_id"], "group": "question",
                            "sample": f"suites/svq/{meta['audio']}", "sample_sha256": meta["sha256"], "sample_seconds": meta["seconds"]}
            groups[g].append(eid)
            ok.append((eid, a, b))
        for tr in it["tests"]:
            r = utts.get(tr["utt_id"])
            if r is None or not ok:
                continue
            clip_id = f"svq-{g}-{tr['utt_id']}"
            meta = write_flac(out, f"audio/clips/{g}/{tr['utt_id']}.flac", svq_audio(r))
            clips[clip_id] = {"id": clip_id, "audio": f"suites/svq/{meta['audio']}", "sha256": meta["sha256"], "seconds": meta["seconds"],
                              "book": g, "reader": r["speaker_id"], "reference": it["text"], "locale": r["locale"], "environment": r["environment"]}
            for eid, a, b in ok:
                mentions.append({"id": f"{clip_id}:{eid.split('/')[-1]}", "clip": clip_id, "entry": eid, "span": [a, b], "group": r["environment"]})
    # name-free questions: one list per pair of readings of a question, drawn from all taught questions
    fg = 0
    for r0 in plan["svq"]["free"]:
        r = utts.get(r0["utt_id"])
        if r is None:
            continue
        g = f"free{fg // 2:03d}"
        fg += 1
        clip_id = f"svq-{g}-{r0['utt_id']}"
        meta = write_flac(out, f"audio/free/{r0['utt_id']}.flac", svq_audio(r))
        clips[clip_id] = {"id": clip_id, "audio": f"suites/svq/{meta['audio']}", "sha256": meta["sha256"], "seconds": meta["seconds"],
                          "book": g, "reader": r["speaker_id"], "reference": r0["text"], "locale": r["locale"], "environment": r["environment"]}
        free.append({"id": f"free:{clip_id}", "clip": clip_id})
        groups.setdefault(g, [])
        spoken.setdefault(g, []).append(r0["text"])
    lists = build_lists(groups, entries, spoken, rng)
    suites["svq"] = {"entries": entries, "lists": lists, "clips": clips, "mentions": mentions, "name_free": free, "dropped": dropped}

    # ---------------- ami (name-free far-field meeting stretches; lists of call names)
    out = root / "suites" / "ami"
    rows = []
    for p in sorted(glob.glob(str(src / "ami" / "sdm" / "test-*.parquet"))):
        t = pq.read_table(p)
        rows += t.to_pylist()
    rows.sort(key=lambda r: (r["meeting_id"], r["begin_time"]))
    by_meeting = collections.defaultdict(list)
    for r in rows:
        by_meeting[r["meeting_id"]].append(r)
    stretches = []
    for mid, rs in sorted(by_meeting.items()):
        run = []
        for r in rs:
            if run and r["begin_time"] < run[-1]["end_time"]:
                continue  # overlapping speech of another speaker: joining it would repeat the room's audio
            if run and r["begin_time"] - run[-1]["end_time"] > 2.0:
                run = []
            run.append(r)
            if run[-1]["end_time"] - run[0]["begin_time"] >= STRETCH_S[0]:
                stretches.append((mid, run))
                run = []
    stretches = rng.sample(stretches, min(AMI_STRETCHES, len(stretches)))
    stretches.sort(key=lambda s: (s[0], s[1][0]["begin_time"]))
    call_entries = suites["calls"]["entries"]
    entries, clips, free, lists = {}, {}, [], {}
    pool = sorted(call_entries)
    for gi in range(AMI_GROUPS):
        pick = rng.sample(pool, LIST_SIZE)
        lists[f"own:ami{gi}"] = {"kind": "own", "book": f"ami{gi}", "entries": [f"ami/{e}" for e in pick]}
        for e in pick:
            entries[f"ami/{e}"] = {**call_entries[e], "id": f"ami/{e}", "book": f"ami{gi}"}
    for k, (mid, run) in enumerate(stretches):
        g = f"ami{k % AMI_GROUPS}"
        parts = []
        for r in run:
            y = np.asarray(r["audio"]["array"], dtype=np.float32) if "array" in r["audio"] else sf.read(io.BytesIO(r["audio"]["bytes"]), dtype="float32")[0]
            parts += [y, np.zeros(3200, dtype=np.float32)]
        text = " ".join(r["text"] for r in run).lower()
        lst = lists[f"own:{g}"]["entries"]
        if any(find_all(name_tokens(text), name_key(entries[e]["written"])) for e in lst):
            continue
        clip_id = f"ami-{mid}-{k:03d}"
        meta = write_flac(out, f"audio/free/{clip_id}.flac", np.concatenate(parts))
        clips[clip_id] = {"id": clip_id, "audio": f"suites/ami/{meta['audio']}", "sha256": meta["sha256"], "seconds": meta["seconds"],
                          "book": g, "reader": "meeting", "reference": text, "meeting": mid,
                          "source": f"{mid} {run[0]['begin_time']}-{run[-1]['end_time']} ({len(run)} utterances, 0.2 s between)"}
        free.append({"id": f"free:{clip_id}", "clip": clip_id})
    suites["ami"] = {"entries": entries, "lists": lists, "clips": clips, "mentions": [], "name_free": free, "dropped": {}}

    # ---------------- modulate (reference only: no audio written here; `bench fetch` cuts it from the source)
    maudio: dict[str, np.ndarray] = {}
    for p in sorted(glob.glob(str(src / "modulate" / "data" / "*.parquet"))):
        for row in pq.read_table(p, columns=["id", "audio"]).to_pylist():
            y, sr = sf.read(io.BytesIO(row["audio"]["bytes"]), dtype="float32")
            maudio[row["id"]] = y if y.ndim == 1 else y.mean(axis=1)
    entries, clips, mentions, groups, spoken = {}, {}, [], collections.defaultdict(list), {}
    dropped = collections.Counter()
    for item in plan["modulate"]:
        g = item["group"]
        spoken[g] = [c["transcript"] for c in item["clips"].values()]
        ok = set()
        for k, (eid, e) in enumerate(sorted(item["entries"].items())):
            sp = align.get(f"enroll:{eid}")
            if not sp or not (ENROLL_S[0] <= sp["end"] - sp["start"] <= ENROLL_S[1]):
                dropped["modulate enrollment not aligned"] += 1
                continue
            rel = f"suites/modulate/audio/enroll/{g}/{k:03d}.wav"
            st, en = round(sp["start"] - PAD_S, 3), round(sp["end"] + PAD_S, 3)
            y = maudio[e["clip"]]
            entries[eid] = {"id": eid, "written": e["written"], "book": g, "reader": "unknown", "group": "public meeting", "sample": rel,
                            "remote": {"id": e["clip"], "start": st, "end": en},
                            "sample_pcm_sha256": pcm_sha(y[max(0, int(st * 16000)):int(en * 16000)])}
            groups[g].append(eid)
            ok.add(eid)
        for mn in item["mentions"]:
            if mn["entry"] not in ok:
                continue
            cid = mn["clip"]
            if cid not in clips:
                c = item["clips"][cid]
                clips[cid] = {"id": cid, "audio": f"suites/modulate/audio/clips/{cid}.wav", "seconds": round(len(maudio[cid]) / 16000, 3),
                              "book": g, "reader": "unknown", "reference": c["transcript"], "remote": {"id": cid},
                              "pcm_sha256": pcm_sha(maudio[cid])}
            mentions.append({"id": f"{cid}:{mn['span'][0]}", "clip": cid, "entry": mn["entry"], "span": mn["span"], "group": "public meeting"})
    lists = build_lists(groups, entries, spoken, rng)
    suites["modulate"] = {"entries": entries, "lists": lists, "clips": clips, "mentions": mentions, "name_free": [], "dropped": dropped}

    # ---------------- write each suite with its licence, then the manifest pointer
    for name, s in suites.items():
        if name not in only:
            print(f"{name}: kept as built (not rewritten)")
            continue
        d = root / "suites" / name
        d.mkdir(parents=True, exist_ok=True)
        common = frozenset(Path(args.common_words).read_text().split()) if args.common_words else frozenset()
        name_words = sorted({w for e in s["entries"].values() for w in ordinary_tokens(e["written"]) if w not in common and not w.isdigit()})
        meta = SOURCES[name]
        doc = {"suite": name, "source": {"repo": meta["repo"], "revision": meta["revision"]}, "licence": meta["licence"],
               "rehosted": meta["rehosted"], "attribution": meta["attribution"], "entries": s["entries"], "lists": s["lists"],
               "clips": s["clips"], "mentions": s["mentions"], "name_free": s["name_free"], "name_words": name_words,
               "dropped": dict(s["dropped"])}
        (d / "suite.json").write_text(json.dumps(doc, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
        (d / "LICENCE.txt").write_text(f"{meta['attribution']}\n\nThis folder (suite.json and audio/) is licensed under "
                                       f"{LICENCE_TEXT[meta['licence']]}.\n" + ("" if meta["rehosted"] else
                                       "No audio of this source is distributed here; `bench fetch` reads it from the source at the pinned revision.\n"))
        secs = sum(c["seconds"] for c in s["clips"].values())
        print(f"{name}: {len(s['entries'])} entries, {len(s['clips'])} clips ({secs / 3600:.2f} h), {len(s['mentions'])} mentions, "
              f"{len(s['name_free'])} name-free; dropped {dict(s['dropped'])}")
    update_manifest(root)


def update_manifest(root: Path) -> None:
    m = json.loads((root / "manifest.json").read_text(encoding="utf-8"))
    refs = []
    for name in ("calls", "svq", "ami", "modulate"):
        f = root / "suites" / name / "suite.json"
        doc = json.loads(f.read_text(encoding="utf-8"))
        refs.append({"name": name, "file": f"suites/{name}/suite.json", "sha256": hashlib.sha256(f.read_bytes()).hexdigest(),
                     "licence": doc["licence"], "rehosted": doc["rehosted"], "source": doc["source"]})
    m["version"] = "1.2.0"
    m["suites"] = refs
    m.setdefault("changes", {})["1.2.0"] = ("Adds four suites, each in suites/<name>/ under its own licence: calls (AppTek, CC BY-SA 4.0), "
                                           "svq (Google SVQ, CC BY 4.0), ami (AMI, CC BY 4.0) and modulate (Modulate, CC BY-SA 4.0; "
                                           "audio not re-hosted). The audiobook data is unchanged (same content fingerprint).")
    (root / "manifest.json").write_text(json.dumps(m, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
