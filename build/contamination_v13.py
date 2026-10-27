#!/usr/bin/env python3
"""The v1.3.0 contamination check: every suite of the benchmark against the training data of v7c, the
adapter the v1.3.0 results are for (virgil-coach/own-names-qwen3-asr v0.7.0, `audio-text-note`).

v0.7.0's card lists every training item by id in its `attribution/` folder (public, at the model's tag
v0.7.0): the 47 LibriVox training books and their readers, the LibriTTS dev speakers and utterances (cloned
voices and real recordings), the 40 Gutenberg template sentences, the YODAS videos, and the conversation
data (LibriTTS-R train-clean-100 utterances with speaker, chapter, LibriVox project and Gutenberg book,
VoxPopuli train/validation sessions, NOTSOFAR-1 training meetings, MUSAN and FSD50K noise). The v0.3.0
recipe part is the same items as v0.3.0's, so this check covers v0.3.0 too.

Checked against the v1.2.0 audiobooks (clips and chapters), the v1.2.0 suites (calls, svq, ami, modulate),
books13 and conv13 (the sealed v1.3 suites). A **failure** is benchmark audio of training data: a reader or
speaker who is in training, a LibriVox recording (project or archive.org item) or book text read in a
training audiobook, a LibriTTS-R chapter or utterance in training, a FSD50K clip in training, or a suite
drawn from a training corpus without a held-out split. **Reported, not failed**: the same Gutenberg text read
by another reader in training (LibriTTS-R), VoxPopuli plenary sessions shared with training (conv13 is held
out by speaker, not by session; its card says so), and listed names that are in a training-book name list,
the generated training names or the template names (counts: names recur across books and speech).

Speaker ids become reader names with LibriSpeech's SPEAKERS.TXT and chapters become LibriVox projects with
CHAPTERS.TXT (openslr 12). Needs, besides the public attribution, the lore name lists the existing check
reads (lore-poc books/, ctxft/gen.py, lore-eval-sets taken.json). Not checkable here, and said so: YODAS
voices (no speaker or channel), VoxPopuli speakers (the attribution lists sessions; conv13's build checked its
speakers against the conversation train/dev rows themselves, `build/conv_v13/sealed/contamination.json`),
and names said in conversation training utterances (only conv13 records them, per entry, as
`name_seen_in_train`; its lists include such names by design and report them apart).

usage: python build/contamination_v13.py --v12 DIR --books13 DIR --conv13 DIR --attribution DIR --attribution-rev SHA
         --librispeech DIR --lore-books DIR --gen GEN.PY --taken TAKEN.JSON --out FILE
"""

import argparse
import csv
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from contamination import base_name, generated_names  # noqa: E402

from own_names_bench.text import name_key  # noqa: E402

TRAIN_CORPORA = {"mythicinfinity/libritts", "mythicinfinity/libritts_r", "facebook/voxpopuli", "espnet/yodas", "microsoft/NOTSOFAR",
                 "Fhrozen/FSD50k", "openslr/musan", "librivox"}
TEMPLATE_GUTENBERG = {"11", "778", "503", "836", "1874", "113", "289"}


def item_id(url: str) -> str:
    return (url or "").rstrip("/").split("/")[-1]


def ids(v) -> set[str]:
    if v is None:
        return set()
    if isinstance(v, (list, tuple, set)):
        return {str(x).strip() for x in v if str(x).strip()}
    return {x.strip() for x in re.split(r"[;,\s]+", str(v)) if x.strip()}


def librispeech(root: Path) -> tuple[dict[str, str], dict[str, dict]]:
    spk, chap = {}, {}
    for line in (root / "SPEAKERS.TXT").read_text().splitlines():
        p = [x.strip() for x in line.split("|")]
        if not line.startswith(";") and len(p) >= 5:
            spk[p[0]] = p[4]
    for line in (root / "CHAPTERS.TXT").read_text().splitlines():
        p = [x.strip() for x in line.split("|")]
        if not line.startswith(";") and len(p) >= 6:
            chap[p[0]] = {"reader": p[1], "subset": p[3], "project": p[4], "gutenberg": p[5]}
    return spk, chap


class Training:
    def __init__(self, attr: Path, spk: dict[str, str], chap: dict[str, dict]):
        self.readers: set[str] = set()
        self.speaker_ids: set[str] = set()
        self.projects: set[str] = set()
        self.items: set[str] = set()
        self.titles: set[str] = set()
        self.book_gutenberg: set[str] = set()   # texts read in a training audiobook
        self.other_gutenberg: set[str] = set()  # texts read by others in LibriTTS / LibriTTS-R, and the template books
        self.chapters: set[str] = set()
        self.utterances: set[str] = set()
        self.vp_sessions: set[str] = set()
        self.fsd: set[str] = set()
        self.counts: dict[str, int] = {}
        books = list(csv.DictReader((attr / "librivox_books.csv").open()))
        for b in books:
            self.readers |= {base_name(r) for r in b["readers"].split(";") if r.strip()}
            self.projects |= ids(b["librivox_id"])
            self.items.add(item_id(b["archive_item"]))
            self.titles.add(b["title"].casefold())
            self.book_gutenberg |= ids(b["gutenberg_ids"])
        tts = list(csv.DictReader((attr / "libritts.csv").open()))
        for r in tts:
            self._speaker(r["speaker_id"], spk)
            self._utt(r["utterance_id"], chap)
        conv = list(csv.DictReader((attr / "conv_libritts_r.csv").open()))
        for r in conv:
            self._speaker(r["speaker_id"], spk)
            if r.get("reader"):
                self.readers.add(base_name(r["reader"]))
            self._utt(r["utterance_id"], chap)
            self.projects |= ids(r.get("librivox_project"))
            self.other_gutenberg |= ids(r.get("gutenberg"))
        self.other_gutenberg |= TEMPLATE_GUTENBERG
        vp = list(csv.DictReader((attr / "conv_voxpopuli_sessions.csv").open()))
        self.vp_sessions = {r["session"].removeprefix("vp:") for r in vp}
        fsd = list(csv.DictReader((attr / "conv_noise_fsd50k.csv").open()))
        self.fsd = {r["freesound_id"] for r in fsd}
        self.counts = {"librivox_books": len(books), "libritts_rows": len(tts), "libritts_r_utterances": len(conv),
                       "voxpopuli_sessions": len(self.vp_sessions), "fsd50k_clips": len(self.fsd),
                       "notsofar_meetings": sum(1 for _ in csv.DictReader((attr / "conv_notsofar_meetings.csv").open())),
                       "yodas_videos": sum(1 for _ in csv.DictReader((attr / "yodas_videos.csv").open())),
                       "readers_by_name": len(self.readers), "speaker_ids": len(self.speaker_ids), "librivox_projects": len(self.projects)}

    def _speaker(self, sid: str, spk: dict[str, str]) -> None:
        self.speaker_ids.add(sid)
        if sid in spk:
            self.readers.add(base_name(spk[sid]))

    def _utt(self, utt: str, chap: dict[str, dict]) -> None:
        self.utterances.add(utt)
        parts = utt.split("_")
        if len(parts) > 1:
            self.chapters.add(parts[1])
            c = chap.get(parts[1])
            if c:
                self.projects.add(c["project"])
                self.other_gutenberg.add(c["gutenberg"])


def trained_names(lore_books: Path, gen: Path, taken: Path, attr: Path) -> dict[str, set[str]]:
    splits = json.loads((lore_books / "splits.json").read_text())
    book = set()
    for k, v in splits["books"].items():
        if v["split"] == "train":
            dropped = set(splits["drop_names"].get(k, []))
            book |= {name_key(n["name"]) for n in json.loads((lore_books / "results" / "names" / f"{k}.json").read_text())
                     if n["name"] not in dropped}
    tpl = {name_key(n) for t in json.loads((attr / "templates.json").read_text()) for n in t.get("names", [])}
    return {"training_book_lists": book, "generated": {name_key(n) for n in generated_names(gen, taken)}, "templates": tpl}


def name_hits(names: set[str], tn: dict[str, set[str]]) -> dict[str, int]:
    keys = {name_key(n) for n in names}
    out = {"listed_names": len(keys)}
    for k, s in tn.items():
        out[f"in_{k}"] = len(keys & s)
    return out


def audiobooks(m: dict, T: Training, tn: dict, task: str) -> dict:
    """An audiobook dataset (the v1.2.0 clips and chapters, or books13): readers, recordings, texts, names."""
    readers = {c["reader"] for c in m["clips"].values()} | {c["reader"] for c in m.get("chapters", [])} | \
              {e["reader"] for e in m["entries"].values()}
    books = []
    for part in ("clips", "chapters"):
        books += list((m.get("attribution") or {}).get(part, {}).values())
    d = {"readers": len(readers), "readers_in_training": sorted(r for r in readers if base_name(r) in T.readers),
         "books": len(books), "books_recording_in_training": [], "books_text_read_in_training_audiobook": [],
         "books_text_read_by_others_in_training": []}
    for a in books:
        g = ids(a.get("gutenberg_ids"))
        if ids(a.get("librivox_id")) & T.projects or item_id(a.get("archive_item", "")) in T.items:
            d["books_recording_in_training"].append(a["title"])
        if g & T.book_gutenberg or a["title"].casefold() in T.titles:
            d["books_text_read_in_training_audiobook"].append(a["title"])
        if g & T.other_gutenberg:
            d["books_text_read_by_others_in_training"].append(a["title"])
    d.update(name_hits({e["written"] for e in m["entries"].values()}, tn))
    d["fail"] = len(d["readers_in_training"]) + len(d["books_recording_in_training"]) + len(d["books_text_read_in_training_audiobook"])
    d["task"] = task
    return d


def suite_v12(s: dict, T: Training, tn: dict) -> dict:
    repo = s["source"]["repo"]
    d = {"source": f"{repo}@{s['source']['revision'][:12]}", "source_is_a_training_corpus": repo in TRAIN_CORPORA,
         "clips": len(s["clips"])}
    skip = set(s.get("not_names", []))
    d.update(name_hits({e["written"] for i, e in s["entries"].items() if i not in skip}, tn))
    d["fail"] = int(d["source_is_a_training_corpus"])
    return d


def conv13(root: Path, T: Training, tn: dict) -> dict:
    m = json.loads((root / "manifest.json").read_text())
    utts, lt_spk, lt_chap, vp_spk, sessions, shared_flag, fsd, names, seen = set(), set(), set(), set(), set(), 0, set(), set(), 0
    clips = 0
    for ref in m["suites"]:
        s = json.loads((root / ref["file"]).read_text())
        for c in s["clips"].values():
            clips += 1
            src = c["source"].split(":", 1)[1].split("@")[0] if ":" in c["source"] else ""
            if c["corpus"] == "libritts":
                utts.add(src.removeprefix("lt_"))
                lt_spk.add(c["reader"].split(":")[1])
                lt_chap.add(c["session"].removeprefix("lt:"))
            else:
                vp_spk.add(c["reader"])
                sessions.add(c["session"].removeprefix("vp:"))
                shared_flag += bool(c.get("session_shared"))
            for v in (c.get("aug") or {}).values():
                if isinstance(v, str) and v.startswith("fsd:"):
                    fsd.add(v[4:])
        skip = set(s.get("not_names", []))
        for i, e in s["entries"].items():
            if e["source"] == "libritts" and e.get("teach_utt"):
                utts.add(e["teach_utt"].removeprefix("lt_"))
                lt_spk.add(e["reader"].split(":")[1])
            elif e["source"] != "libritts":
                vp_spk.add(e["reader"])
            if i not in skip:
                names.add(e["written"])
            seen += bool(e.get("name_seen_in_train"))
    d = {"clips": clips, "libritts_r_utterances": len(utts), "libritts_r_utterances_in_training": len(utts & T.utterances),
         "libritts_r_speakers": len(lt_spk), "libritts_r_speakers_in_training": len(lt_spk & T.speaker_ids),
         "libritts_r_chapters": len(lt_chap), "libritts_r_chapters_in_training": len(lt_chap & T.chapters),
         "fsd50k_clips": len(fsd), "fsd50k_clips_in_training": len(fsd & T.fsd),
         "voxpopuli_speakers": len(vp_spk),
         "voxpopuli_sessions": len(sessions), "voxpopuli_sessions_shared_with_training": len(sessions & T.vp_sessions),
         "voxpopuli_clips_flagged_session_shared": shared_flag,
         "entries_name_seen_in_conversation_training": seen}
    d.update(name_hits(names, tn))
    d["fail"] = d["libritts_r_utterances_in_training"] + d["libritts_r_speakers_in_training"] + d["libritts_r_chapters_in_training"] + \
        d["fsd50k_clips_in_training"]
    return d


def main() -> None:
    ap = argparse.ArgumentParser()
    for a in ("--v12", "--books13", "--conv13", "--attribution", "--librispeech", "--lore-books", "--gen", "--taken", "--out"):
        ap.add_argument(a, type=Path, required=True)
    ap.add_argument("--attribution-rev", required=True)
    args = ap.parse_args()
    spk, chap = librispeech(args.librispeech)
    T = Training(args.attribution, spk, chap)
    tn = trained_names(args.lore_books, args.gen, args.taken, args.attribution)
    v12 = json.loads((args.v12 / "manifest.json").read_text())
    out = {"adapter": f"virgil-coach/own-names-qwen3-asr v0.7.0 (v7c), attribution/ at {args.attribution_rev}",
           "rule": __doc__.split("usage:")[0].strip(),
           "training": T.counts | {f"names_{k}": len(v) for k, v in tn.items()}, "suites": {}}
    out["suites"]["v1.2.0 audiobooks"] = audiobooks(v12, T, tn, "clips and chapters")
    for ref in v12.get("suites", []):
        out["suites"][f"v1.2.0 {ref['name']}"] = suite_v12(json.loads((args.v12 / ref["file"]).read_text()), T, tn)
    out["suites"]["books13"] = audiobooks(json.loads((args.books13 / "manifest.json").read_text()), T, tn, "clips")
    out["suites"]["conv13"] = conv13(args.conv13, T, tn)
    out["not_checkable"] = ["YODAS clips carry no speaker or channel: a benchmark speaker in a training video cannot be ruled out by name.",
                            "VoxPopuli speakers: v0.7.0's attribution lists sessions, not speakers; conv13's build checked its speakers "
                            "against the conversation train/dev rows (build/conv_v13/sealed/contamination.json: 0 shared).",
                            "Names said in conversation training utterances: recorded only for conv13 (name_seen_in_train)."]
    out["fail"] = sum(s["fail"] for s in out["suites"].values())
    out["result"] = "PASS" if out["fail"] == 0 else "FAIL"
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(out, indent=1, ensure_ascii=False) + "\n")
    for k, s in out["suites"].items():
        print(k, json.dumps({kk: (len(v) if isinstance(v, list) else v) for kk, v in s.items()}))
    print(out["result"], out["fail"])


if __name__ == "__main__":
    main()
