#!/usr/bin/env python3
"""Validity check and seal of the v1.3 conversation test suite. Data tooling only: no model or system reads the audio.

validity   every file listed in a suite.json exists and has its SHA-256; every clip decodes, is not empty or
           zero-filled, and its level (RMS dBFS, peak, clipped share) is recorded; every mention's span is the listed
           spelling (own-names-bench name tokens), its aligned time lies inside the clip and is not silence in the clean
           source; every spoken entry is on its clip's list; no listed name occurs in a name-free clip's reference;
           taught recordings are 0.15-2.6 s and not silent.
seal       LICENCE.txt and NOISE_ATTRIBUTION.csv per suite; MANIFEST.json with every file's SHA-256, one suite hash
           (SHA-256 of the sorted "<sha256>  <path>" lines), counts per condition, licences, the build commit and code
           hashes, the volume path; the suite folder is made read-only.

usage: seal.py  -> $ONB_SEALED/MANIFEST.json, build/validity.json (both also copied to out/ by run.sh)
"""
import csv
import hashlib
import json
import os
import stat
import sys
import time
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np
import soundfile as sf

from common import RATE, SEALED, SOURCES, SUITE, WORK, jsonl, log

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE / "_onb"))
from own_names_bench.text import find_all, name_key, name_tokens, nfc  # noqa: E402

CODE = ["build.py", "check.py", "common.py", "fetch.py", "fsd_test.py", "prep.py", "seal.py", "run.sh", "launch.sh", "gpu.jsonc",
        "pyproject.toml", "uv.lock", "excl.json", "fsd_test.json", "fsd_street.json", "attribution_v030/libritts.csv",
        "attribution_v030/librivox_books.csv", "_onb/own_names_bench/text.py"]


def sha(p: Path) -> str:
    h = hashlib.sha256()
    with p.open("rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def dbfs(x: np.ndarray) -> float:
    return float(20 * np.log10(np.sqrt(np.mean(x.astype(np.float64) ** 2)) + 1e-9))


def pct(v: list[float]) -> dict:
    if not v:
        return {}
    a = np.asarray(v)
    return {"n": len(v), "p5": round(float(np.percentile(a, 5)), 1), "median": round(float(np.median(a)), 1), "p95": round(float(np.percentile(a, 95)), 1)}


def main() -> None:
    utts = {u["id"]: u for s in ("voxpopuli", "libritts") for u in jsonl(WORK / "utts" / f"{s}.jsonl")}
    fsd = {c["fname"]: c for c in json.loads((HERE / "fsd_test.json").read_text())["clips"]}
    problems: Counter = Counter()
    levels: dict[str, list[float]] = defaultdict(list)
    peaks: dict[str, list[float]] = defaultdict(list)
    counts: dict[str, dict] = {}
    seen_hashes: Counter = Counter()
    noise_by_suite: dict[str, Counter] = defaultdict(Counter)
    for sj in sorted(SUITE.glob("conv13-*/suite.json")):
        s = json.loads(sj.read_text())
        name = s["suite"]
        clips, entries, lists = s["clips"], s["entries"], s["lists"]
        for c in clips.values():
            p = SUITE / c["audio"].split("/", 1)[1]
            if not p.is_file() or sha(p) != c["sha256"]:
                problems[f"{name}: clip missing or changed"] += 1
                continue
            seen_hashes[(name, c["sha256"])] += 1
            x, sr = sf.read(p, dtype="float32")
            if sr != RATE or not np.isfinite(x).all() or not np.any(x):
                problems[f"{name}: clip unreadable, wrong rate or all zero"] += 1
                continue
            lv, pk = dbfs(x), float(np.abs(x).max())
            levels[c["cond"]].append(lv)
            peaks[c["cond"]].append(20 * np.log10(pk + 1e-9))
            if np.mean(np.abs(x) >= 0.999) > 0.005:
                problems[f"{name}: more than 0.5% of samples clipped"] += 1
            if lv < -60:
                problems[f"{name}: clip below -60 dBFS"] += 1
            if abs(c["seconds"] - len(x) / RATE) > 0.01:
                problems[f"{name}: clip length differs from suite.json"] += 1
            if "noise_file" in c["aug"]:
                noise_by_suite[name][c["aug"]["noise_file"].split(":", 1)[1]] += 1
        for e in entries.values():
            p = SUITE / e["sample"].split("/", 1)[1]
            if not p.is_file() or sha(p) != e["sample_sha256"]:
                problems[f"{name}: taught recording missing or changed"] += 1
                continue
            x, _ = sf.read(p, dtype="float32")
            if not 0.15 <= len(x) / RATE <= 2.6 or dbfs(x) < -60:
                problems[f"{name}: taught recording outside 0.15-2.6 s or silent"] += 1
        for mn in s["mentions"]:
            c = clips[mn["clip"]]
            e = entries[mn["entry"]]
            ref = nfc(c["reference"])
            if tuple(name_tokens(ref[mn["span"][0]:mn["span"][1]])) != name_key(e["written"]):
                problems[f"{name}: mention span is not the listed spelling"] += 1
            if mn["entry"] not in lists[f"own:{c['book']}"]["entries"]:
                problems[f"{name}: spoken entry not on the clip's list"] += 1
            a, b = mn["name_at_s"]
            if not (0 <= a < b <= c["seconds"] + 0.05):
                problems[f"{name}: aligned name time outside the clip"] += 1
            # the name is not silence in the clean source (alignment sanity, data tooling only)
            uid = c["source"].split(":", 1)[1].rsplit("@", 1)[0]
            u = utts[uid]
            x, _ = sf.read(u["audio"], dtype="float32")
            w0 = float(c["source"].rsplit("@", 1)[1].split("-")[0])
            seg = x[int((w0 + a) * RATE):int((w0 + b) * RATE)]
            if len(seg) == 0 or dbfs(seg) < dbfs(x) - 25:
                problems[f"{name}: aligned name is near-silent in the clean source"] += 1
            levels[f"name_minus_utterance_db:{mn['cond']}"].append(dbfs(seg) - dbfs(x) if len(seg) else -99.0)
        for nf in s["name_free"]:
            c = clips[nf["clip"]]
            toks = name_tokens(c["reference"])
            if any(find_all(toks, name_key(entries[e]["written"])) for e in lists[f"own:{c['book']}"]["entries"]):
                problems[f"{name}: a listed name in a name-free reference"] += 1
        list_sizes = [len(v["entries"]) for v in lists.values()]
        mns = s["mentions"]
        counts[name] = {
            "condition": s["condition"], "clips": len(clips), "hours": round(sum(c["seconds"] for c in clips.values()) / 3600, 3),
            "mentions": len(mns), "mentions_by_source": dict(Counter(clips[m["clip"]]["corpus"] for m in mns)),
            "mentions_name_never_seen_in_train": sum(not m["name_seen_in_train"] for m in mns),
            "mentions_taught_by_another_speaker": sum(m["teach_cross"] for m in mns),
            "name_free": len(s["name_free"]), "name_free_by_kind": dict(Counter(nf["cond"] for nf in s["name_free"])),
            "name_free_by_source": dict(Counter(clips[nf["clip"]]["corpus"] for nf in s["name_free"])),
            "name_free_minutes": round(sum(clips[nf["clip"]]["seconds"] for nf in s["name_free"]) / 60, 1),
            "clips_in_a_voxpopuli_debate_item_shared_with_train_dev": sum(c["session_shared"] for c in clips.values()),
            "entries": len(entries), "lists": len(lists), "list_size_min_median_max": [min(list_sizes), int(np.median(list_sizes)), max(list_sizes)],
            "list_entries_never_seen_in_train": sum(not e["name_seen_in_train"] for e in entries.values()),
            "speakers": len({c["reader"] for c in clips.values()}),
        }
    # within a suite no two clips are the same file (a zero-filled write would repeat); across suites a clean utterance
    # may be a clip of both xspk and conv, as in dev
    problems["clip files with a repeated hash within a suite"] = sum(n for n in seen_hashes.values() if n > 1)
    validity = {"problems": {k: v for k, v in problems.items() if v}, "levels_dbfs": {k: pct(v) for k, v in sorted(levels.items())},
                "peak_dbfs": {k: pct(v) for k, v in sorted(peaks.items())},
                "clips_equal_across_suites": sum(n > 1 for n in Counter(h for _, h in seen_hashes).values())}
    validity["verdict"] = "PASS" if not validity["problems"] else "FAIL"
    (WORK / "validity.json").write_text(json.dumps(validity, indent=1))
    log(json.dumps(validity, indent=1))
    if validity["problems"]:
        raise SystemExit(f"validity FAIL: {validity['problems']}")
    contamination = json.loads((WORK / "contamination.json").read_text())
    if contamination["verdict"] != "PASS":
        raise SystemExit("contamination check did not pass; not sealing")

    # ---------------------------------------------------------------- licences and attribution per suite
    for sj in sorted(SUITE.glob("conv13-*/suite.json")):
        d = sj.parent
        name = d.name
        with (d / "NOISE_ATTRIBUTION.csv").open("w", newline="") as f:
            w = csv.writer(f)
            w.writerow(["freesound_id", "title", "uploader", "licence", "url", "clips_using_it"])
            for fid, n in sorted(noise_by_suite[name].items(), key=lambda kv: int(kv[0])):
                c = fsd[fid]
                w.writerow([fid, c["title"], c["uploader"], c["licence"], c["url"], n])
        (d / "LICENCE.txt").write_text(
            f"own-names-bench v1.3 conversation test suite, {name}.\n\n{json.loads(sj.read_text())['attribution']}\n\n"
            "This folder (suite.json, audio/, NOISE_ATTRIBUTION.csv) is licensed under Creative Commons Attribution 4.0 International, "
            "https://creativecommons.org/licenses/by/4.0/. VoxPopuli audio is CC0 1.0; LibriTTS-R audio is CC BY 4.0 (Koizumi et al., "
            "LibriTTS-R, 2023, from LibriTTS by Zen et al., 2019, from LibriVox); FSD50K clips are CC0 1.0 or CC BY 3.0, each credited "
            "in NOISE_ATTRIBUTION.csv (title, Freesound uploader, licence, URL); they were resampled, mixed and processed.\n")

    # ---------------------------------------------------------------- manifest
    files = sorted(p for p in SUITE.rglob("*") if p.is_file())
    file_sha = {str(p.relative_to(SUITE)): sha(p) for p in files}
    zero = hashlib.sha256(b"").hexdigest()
    if any(v == zero for v in file_sha.values()):
        raise SystemExit("an empty file in the suite; not sealing")
    blob = "".join(f"{h}  {p}\n" for p, h in sorted(file_sha.items()))
    suite_hash = hashlib.sha256(blob.encode()).hexdigest()
    (SEALED / "SHA256SUMS").write_text(blob)
    total = {"clips": sum(c["clips"] for c in counts.values()), "mentions": sum(c["mentions"] for c in counts.values()),
             "name_free": sum(c["name_free"] for c in counts.values()), "hours": round(sum(c["hours"] for c in counts.values()), 2),
             "mentions_name_never_seen_in_train": sum(c["mentions_name_never_seen_in_train"] for c in counts.values()),
             "files": len(file_sha), "bytes": sum(p.stat().st_size for p in files)}
    fetched = json.loads((WORK / "src" / "fetched.json").read_text()) if (WORK / "src" / "fetched.json").exists() else {}
    manifest = {
        "name": "own-names-bench v1.3 conversation test suite (held out, sealed)",
        "sealed_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "suite_hash": suite_hash, "suite_hash_rule": "sha256 of SHA256SUMS: the sorted lines '<sha256>  <path relative to suite/>' of every file",
        "volume": {"provider": "RunPod", "volume": "gpu-cli-user (global, EUR-IS-1)", "path": str(SEALED), "suite": str(SUITE),
                   "build_files": str(WORK)},
        "build": {"repo": "own-names-bench", "branch": "suite/conv-v13", "commit": os.environ.get("BUILD_COMMIT", "unknown"),
                  "code_sha256": {f: sha(HERE / f) for f in CODE if (HERE / f).exists()},
                  "recipe": "lore-poc convdata (branch data/conv-names-v1, commit 9004fe4), see README.md"},
        "suites": counts, "total": total,
        "contamination": {"verdict": contamination["verdict"], "report": "contamination.json"},
        "validity": {"verdict": validity["verdict"], "report": "validity.json"},
        "sources": {k: {**{kk: vv for kk, vv in SOURCES[k].items() if kk != "files"}} for k in SOURCES},
        "fetched": {k: ({"files": v["files"]} if isinstance(v, dict) and "files" in v else v) for k, v in fetched.items()},
        "licence": "CC BY 4.0 (suite annotations and processed audio); VoxPopuli CC0 1.0; LibriTTS-R CC BY 4.0; FSD50K CC BY 4.0 with "
                   "clips CC0 1.0 / CC BY 3.0 (NOISE_ATTRIBUTION.csv per suite)",
        "noise_clips_used": {"total": len({f for c in noise_by_suite.values() for f in c}),
                             "by_licence": dict(Counter(fsd[f]["licence"] for f in {f for c in noise_by_suite.values() for f in c}))},
        "rule": "Held out: scored once per final system (ours, ElevenLabs Scribe v2). No model or API was run on this audio while building it "
                "(the forced aligner timed reference words in prep). Do not train, tune, select or smoke-test on it.",
        "files": file_sha,
    }
    (SEALED / "MANIFEST.json").write_text(json.dumps(manifest, indent=1, ensure_ascii=False) + "\n")
    for p in sorted(SUITE.rglob("*"), reverse=True):
        mode = p.stat().st_mode
        p.chmod(mode & ~(stat.S_IWUSR | stat.S_IWGRP | stat.S_IWOTH))
    SUITE.chmod(SUITE.stat().st_mode & ~(stat.S_IWUSR | stat.S_IWGRP | stat.S_IWOTH))
    (SEALED / "SEALED.txt").write_text(f"SEALED {manifest['sealed_at']} suite_hash {suite_hash}\nDo not read, train, tune or smoke-test on this data. "
                                       "It is scored once per final system (own-names-bench v1.3).\n")
    log(f"SEALED suite_hash {suite_hash}: {json.dumps(total)}")


if __name__ == "__main__":
    main()
