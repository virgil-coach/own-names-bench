#!/usr/bin/env python3
"""Builds the v1.2.0 suites: conversational calls (AppTek), cross-speaker questions (Google SVQ),
far-field meetings for insertions (AMI), and public meetings (Modulate, reference only: its audio
is fetched from Modulate's repository at run time, never re-hosted).

Three stages, so the one model step runs on a GPU machine:
  plan   choose items and lists from the sources' metadata; write plan.json and align_jobs.json
  align  (pod) word times for the names an enrollment recording is cut from (build/align.py)
  cut    cut the audio, write the suites into the dataset folder and its manifest

usage: build/build_v12.py plan  --src DIR --common-words FILE
       build/build_v12.py cut   --src DIR --align FILE --dataset DIR
"""

import argparse
import collections
import glob
import hashlib
import json
import random
import re
from pathlib import Path

import numpy as np
import soundfile as sf

SEED = 20261014
SOURCES = {
    "calls": {"repo": "apptek-com/apptek_callcenter_dialogues", "revision": "b98967d9946f7f59f58d08624a2a00fe98fe0219",
              "licence": "CC BY-SA 4.0", "rehosted": True,
              "attribution": "AppTek Call-Center Dialogues (AppTek), https://huggingface.co/datasets/apptek-com/apptek_callcenter_dialogues, "
                             "CC BY-SA 4.0. Clips cut from the merged-channel diarization audio; references cleaned (fillers in "
                             "parentheses and cut-off words removed)."},
    "svq": {"repo": "google/svq", "revision": "74f17ec92f0654860c160029d3542199626f63ef", "licence": "CC BY 4.0", "rehosted": True,
            "attribution": "Simple Voice Questions (Google), https://huggingface.co/datasets/google/svq, CC BY 4.0."},
    "ami": {"repo": "edinburghcstr/ami", "revision": "46f28f2503e2ec48f8867a84eef356c70476beab", "licence": "CC BY 4.0", "rehosted": True,
            "attribution": "AMI Meeting Corpus (University of Edinburgh et al.), https://groups.inf.ed.ac.uk/ami/corpus/, CC BY 4.0. "
                           "Single distant microphone, test split; consecutive utterances of a meeting joined."},
    "modulate": {"repo": "modulate/entity-transcription-benchmark", "revision": "45b2f1411ff15a6598b68db1ec8423b9965153e5",
                 "licence": "CC BY-SA 4.0", "rehosted": False,
                 "attribution": "Entity Transcription Benchmark (Modulate), https://huggingface.co/datasets/modulate/entity-transcription-benchmark, "
                                "CC BY-SA 4.0; MLCommons People's Speech test portion. Audio is not re-hosted: `bench fetch` reads it "
                                "from Modulate's repository at the pinned revision."},
}
CALL_ACCENTS = ["en-AU", "en-CA", "en-CN", "en-GB", "en-GB_SCT", "en-GB_WLS", "en-IE", "en-IN", "en-MX", "en-SG", "en-US_Aave",
                "en-US_General", "en-US_Southern", "en-ZA"]
CALLS_PER_ACCENT = 15
LIST_SIZE = 40          # every list: the recording's own names, then names from elsewhere in the suite (seeded), up to this
MAX_CLIP_S = 15.0
STRETCH_S = (30.0, 60.0)
STRETCHES_PER_CALL = 2
SVQ_TEXTS = 320
SVQ_TEST_READINGS = 4
SVQ_FREE_TEXTS = 160
AMI_STRETCHES = 120
AMI_GROUPS = 4          # the AMI stretches are split in groups that each get one list

# Not names: interjections, contractions handled apart, calendar words, titles.
SKIP = set("""mhm yep yup uh-huh mm-hm ma'am goodbye bye-bye okay ok hi hello hey yeah yes no sir madam mister miss mrs mr ms dr
monday tuesday wednesday thursday friday saturday sunday january february march april may june july august september october
november december christmas easter god imma gonna wanna gotta hmm um uh ah oh ohh wow alright alrighty cheers ta mum dad
wi-fi e-ticket e-mail e-mails airlines airways british english french spanish american indian chinese european african
asian australian canadian irish scottish welsh egyptian german italian japanese mexican""".split())


def clean_call_text(t: str) -> str:
    """AppTek references: fillers in parentheses and cut-off words (with ~) removed."""
    t = re.sub(r"\([^)]*\)", " ", t)
    t = " ".join(w for w in t.split() if "~" not in w)
    return re.sub(r"\s+", " ", t).strip()


def name_spans(text: str, common: frozenset[str], sentence_initial_ok: bool = False) -> list[tuple[str, int, int]]:
    """Capitalised words that are not ordinary English, joined when adjacent ("Hong Kong")."""
    out: list[tuple[str, int, int]] = []
    for m in re.finditer(r"[A-Za-z][A-Za-z\-]*(?:'[A-Za-z]+)?", text):
        w = m.group(0)
        if "'" in w and not w.lower().endswith("'s"):
            continue
        base = w[:-2] if w.lower().endswith("'s") else w
        if not base[0].isupper() or len(base) < 3 or (base.isupper() and len(base) <= 5):
            continue
        if base.lower() in common or base.lower() in SKIP:
            continue
        start, end = m.start(), m.start() + len(base)
        if not sentence_initial_ok:
            before = text[:start].rstrip()
            if not before or before[-1] in ".?!":
                continue
        if out and text[out[-1][2]:start] == " ":
            prev = out.pop()
            out.append((text[prev[1]:end], prev[1], end))
        else:
            out.append((base, start, end))
    return out


def plan(args: argparse.Namespace) -> None:
    src = Path(args.src)
    common = frozenset(Path(args.common_words).read_text().split())
    rng = random.Random(SEED)
    plan: dict = {"seed": SEED, "sources": SOURCES}
    jobs = []

    # ---- calls
    calls = []
    for acc in CALL_ACCENTS:
        rows = [json.loads(line) for line in (src / "apptek" / "diarization" / acc / "metadata.jsonl").open()]
        rows.sort(key=lambda r: r["file_name"])
        calls += [dict(r, accent=acc) for r in rng.sample(rows, min(CALLS_PER_ACCENT, len(rows)))]
    call_items = []
    for c in calls:
        cid = Path(c["file_name"]).stem
        segs = []
        for i, s in enumerate(c["segments"]):
            text = clean_call_text(s["text"])
            segs.append({"i": i, "start": s["start"], "end": s["end"], "speaker": s["speaker_id"], "role": s["role"], "text": text,
                         "names": name_spans(text, common)})
        by_name: dict[str, list[tuple[int, int, int]]] = collections.defaultdict(list)
        for s in segs:
            for n, a, b in s["names"]:
                by_name[n].append((s["i"], a, b))
        entries, mentions = {}, []
        for n, occ in sorted(by_name.items()):
            seg_ids = sorted({i for i, _, _ in occ})
            if len(seg_ids) < 2:
                continue  # a name said once cannot be taught from elsewhere in the call
            # taught from its first mention, by whoever said it; the other mentions are tested
            e_seg = seg_ids[0]
            ea, eb = next((a, b) for i, a, b in occ if i == e_seg)
            eid = f"calls/{cid}/{n}"
            entries[eid] = {"written": n, "call": cid, "speaker": segs[e_seg]["speaker"], "seg": e_seg}
            jobs.append({"job": f"enroll:{eid}", "source": "calls", "file": c["file_name"], "accent": c["accent"],
                         "start": segs[e_seg]["start"], "end": segs[e_seg]["end"], "text": segs[e_seg]["text"], "span": [ea, eb]})
            for i, a, b in occ:
                s = segs[i]
                if i == e_seg or s["end"] - s["start"] > MAX_CLIP_S:
                    continue
                mentions.append({"seg": i, "entry": eid, "span": [a, b], "same_speaker": s["speaker"] == segs[e_seg]["speaker"]})
        stretches, run = [], []
        for s in segs + [None]:
            if s is None or s["names"]:
                if run and run[-1]["end"] - run[0]["start"] >= STRETCH_S[0]:
                    stretches.append(run)
                run = []
                continue
            if run and s["end"] - run[0]["start"] > STRETCH_S[1]:
                if run[-1]["end"] - run[0]["start"] >= STRETCH_S[0]:
                    stretches.append(run)
                run = []
            run.append(s)
        stretches = rng.sample(stretches, min(STRETCHES_PER_CALL, len(stretches)))
        call_items.append({"call": cid, "file": c["file_name"], "accent": c["accent"], "domain": c["domain"], "duration": c["duration"],
                           "segments": segs, "entries": entries, "mentions": mentions,
                           "stretches": [[s["i"] for s in st] for st in stretches]})
    plan["calls"] = call_items

    # ---- svq: questions read by about 20 people; a name is taught from one reading, tested on others
    import pyarrow.parquet as pq

    rows = [r for r in pq.read_table(src / "svq" / "1.0.0" / "speech_transcription.parquet").to_pylist() if r["locale"].startswith("en_")]
    by_text: dict[str, list[dict]] = collections.defaultdict(list)
    for r in rows:
        by_text[r["text"]].append(r)
    texts = sorted(by_text)
    with_names = [t for t in texts if name_spans(t, common)]
    free = [t for t in texts if not name_spans(t, common, sentence_initial_ok=True)]
    pick = rng.sample(with_names, min(SVQ_TEXTS, len(with_names)))
    svq_items = []
    for t in pick:
        rs = sorted(by_text[t], key=lambda r: r["utt_id"])
        clean = [r for r in rs if r["environment"] == "clean"]
        enroll = rng.choice(clean)
        others = [r for r in rs if r["speaker_id"] != enroll["speaker_id"]]
        tests = []
        for env in ("clean", "background_speech", "media_noise", "traffic_noise"):
            pool = [r for r in others if r["environment"] == env and r["utt_id"] not in {x["utt_id"] for x in tests}]
            if pool:
                tests.append(rng.choice(pool))
        svq_items.append({"text": t, "names": name_spans(t, common), "enroll": enroll, "tests": tests[:SVQ_TEST_READINGS]})
    svq_free = []
    for t in rng.sample(free, min(SVQ_FREE_TEXTS, len(free))):
        rs = sorted(by_text[t], key=lambda r: r["utt_id"])
        svq_free += [rng.choice([r for r in rs if r["environment"] == "clean"] or rs),
                     rng.choice([r for r in rs if r["environment"] == "background_speech"] or rs)]
    plan["svq"] = {"items": svq_items, "free": svq_free}

    # ---- modulate (reference only): entities said in at least two clips of the same public recording
    mrows = []
    for p in sorted(glob.glob(str(src / "modulate" / "data" / "*.parquet"))):
        t = pq.read_table(p)
        mrows += t.select([c for c in t.schema.names if c != "audio"]).to_pylist()
    mrows = [r for r in mrows if r["subset"].startswith("MLCommons")]
    groups: dict[str, list[dict]] = collections.defaultdict(list)
    for r in mrows:
        groups[r["id"].split("-")[-1].rsplit("_", 1)[0]].append(r)
    mod_items = []
    for g, rs in sorted(groups.items()):
        rs.sort(key=lambda r: r["id"])
        occ: dict[str, list[tuple[str, int, int]]] = collections.defaultdict(list)
        for r in rs:
            for o in json.loads(r["entity_offsets"] or "[]"):
                occ[o["text"]].append((r["id"], o["start"], o["end"]))
        entries, mentions = {}, []
        for n, os_ in sorted(occ.items()):
            clips = sorted({c for c, _, _ in os_})
            if len(clips) < 2:
                continue
            e_clip = clips[0]
            ea, eb = next((a, b) for c, a, b in os_ if c == e_clip)
            eid = f"modulate/{g}/{n}"
            entries[eid] = {"written": n, "group": g, "clip": e_clip}
            e_row = next(r for r in rs if r["id"] == e_clip)
            jobs.append({"job": f"enroll:{eid}", "source": "modulate", "clip": e_clip, "text": e_row["transcript"], "span": [ea, eb]})
            mentions += [{"clip": c, "entry": eid, "span": [a, b]} for c, a, b in os_ if c != e_clip]
        if mentions:
            mod_items.append({"group": g, "entries": entries, "mentions": mentions,
                              "clips": {r["id"]: {"transcript": r["transcript"], "seconds": float(r["duration_s"])} for r in rs}})
    plan["modulate"] = mod_items
    out = src / "plan.json"
    out.write_text(json.dumps(plan, ensure_ascii=False))
    (src / "align_jobs.json").write_text(json.dumps(jobs, ensure_ascii=False))
    n_calls_m = sum(len(c["mentions"]) for c in call_items)
    print(f"calls {len(call_items)}: {sum(len(c['entries']) for c in call_items)} taught names, {n_calls_m} mentions, "
          f"{sum(len(c['stretches']) for c in call_items)} name-free stretches")
    print(f"svq {len(svq_items)} questions, {sum(len(i['tests']) * len(i['names']) for i in svq_items)} mentions, {len(svq_free)} name-free")
    print(f"modulate {len(mod_items)} recordings, {sum(len(m['mentions']) for m in mod_items)} mentions")
    print(f"align jobs {len(jobs)}")


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _write_wav(path: Path, x: np.ndarray) -> str:
    path.parent.mkdir(parents=True, exist_ok=True)
    pcm = np.clip(np.round(x * 32768.0), -32768, 32767).astype(np.int16)
    sf.write(path, pcm, 16000, subtype="PCM_16", format="WAV")
    return _sha(path)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("stage", choices=["plan", "cut"])
    ap.add_argument("--src", required=True)
    ap.add_argument("--common-words")
    ap.add_argument("--align")
    ap.add_argument("--dataset")
    a = ap.parse_args()
    if a.stage == "plan":
        plan(a)
    else:
        from build_v12_cut import cut  # noqa: E402

        cut(a)
