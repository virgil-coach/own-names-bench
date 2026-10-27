#!/usr/bin/env python3
"""Selects the background-noise clips of the v1.3 conversation test suite from FSD50K metadata (no audio is read
here). The conversation train and dev data mixed MUSAN noise (every licence-clean MUSAN noise file is in its train or
dev half) and the FSD50K street clips of lore-poc convdata/fsd_street.json, so the test suite uses neither: only
FSD50K clips that are

  - not in fsd_street.json (the train and dev clips), by FSD50K clip id (= Freesound sound id),
  - by an uploader with no clip in fsd_street.json (so no recording session or device of a train/dev noise),
  - licensed CC0 1.0 or CC BY 3.0 (CC BY-NC and Sampling+ are left out),
  - labelled with none of the speech, voice, singing or music labels (FORBIDDEN).

Two pools, as in the dev data: `street` (traffic, vehicle, siren, crowd, rain, wind and subway sounds: the categories
of fsd_street.json) and `musan` (indoor and ambient background noise in place of MUSAN noise: appliances, typing,
dishes, water, machines, weather and the like). At most PER_UPLOADER clips per uploader and PER_CATEGORY per category.

usage: fsd_test.py <FSD50K metadata dir with labels/ and metadata/> <fsd_street.json>  -> fsd_test.json
"""
import csv
import json
import random
import sys
from collections import Counter, defaultdict
from pathlib import Path

REPO, REVISION = "Fhrozen/FSD50k", "ccf1acaff12f3f4a4c10052dddafbb6d22152c9b"
LICENCES = {"http://creativecommons.org/publicdomain/zero/1.0/", "http://creativecommons.org/licenses/by/3.0/"}
FORBIDDEN = {"Human_voice", "Speech", "Male_speech_and_man_speaking", "Female_speech_and_woman_speaking", "Child_speech_and_kid_speaking",
             "Conversation", "Speech_synthesizer", "Whispering", "Chatter", "Shout", "Yell", "Screaming", "Laughter", "Giggle",
             "Chuckle_and_chortle", "Crying_and_sobbing", "Singing", "Male_singing", "Female_singing", "Music", "Musical_instrument",
             "Cheering", "Applause", "Ringtone", "Telephone"}
STREET = ["Traffic_noise_and_roadway_noise", "Car_passing_by", "Bus", "Truck", "Motorcycle", "Vehicle_horn_and_car_horn_and_honking", "Siren",
          "Crowd", "Rain", "Wind", "Subway_and_metro_and_underground", "Motor_vehicle_(road)", "Idling"]
GENERAL = ["Mechanical_fan", "Typing", "Computer_keyboard", "Printer", "Dishes_and_pots_and_pans", "Cutlery_and_silverware", "Water_tap_and_faucet",
           "Sink_(filling_or_washing)", "Microwave_oven", "Frying_(food)", "Boiling", "Door", "Drawer_open_or_close", "Cupboard_open_or_close",
           "Walk_and_footsteps", "Clock", "Tick-tock", "Hiss", "Engine", "Mechanisms", "Power_tool", "Drill", "Crumpling_and_crinkling",
           "Writing", "Zipper_(clothing)", "Stream", "Waves_and_surf", "Thunderstorm", "Fire", "Crackle", "Bird_vocalization_and_bird_call_and_bird_song",
           "Dog", "Rail_transport", "Aircraft", "Pour", "Toilet_flush", "Keys_jangling", "Knock", "Squeak", "Buzz"]
PER_UPLOADER, PER_CATEGORY = 2, {"street": 24, "musan": 9}
SEED = 1313


def main() -> None:
    meta, street_json = Path(sys.argv[1]), Path(sys.argv[2])
    used = json.loads(street_json.read_text())["clips"]
    used_ids = {c["fname"] for c in used}
    used_uploaders = {c["uploader"] for c in used}
    info = {**json.loads((meta / "metadata" / "dev_clips_info_FSD50K.json").read_text()),
            **json.loads((meta / "metadata" / "eval_clips_info_FSD50K.json").read_text())}
    labels: dict[str, tuple[str, set[str]]] = {}
    for split in ("dev", "eval"):
        for r in csv.DictReader((meta / "labels" / f"{split}.csv").open()):
            labels[r["fname"]] = (split, set(r["labels"].split(",")))
    dropped: Counter = Counter()
    by_cat: dict[tuple[str, str], list[str]] = defaultdict(list)
    for fname, (split, labs) in sorted(labels.items(), key=lambda kv: int(kv[0])):
        i = info.get(fname)
        if i is None:
            dropped["no clip info"] += 1
            continue
        if fname in used_ids:
            dropped["a train or dev clip"] += 1
            continue
        if i["uploader"] in used_uploaders:
            dropped["uploader of a train or dev clip"] += 1
            continue
        if i["license"] not in LICENCES:
            dropped["licence not CC0 / CC BY 3.0"] += 1
            continue
        if labs & FORBIDDEN:
            dropped["speech, voice or music label"] += 1
            continue
        for pool, cats in (("street", STREET), ("musan", GENERAL)):
            cat = next((c for c in cats if c in labs), None)
            if cat:
                by_cat[(pool, cat)].append(fname)
                break
    rng = random.Random(SEED)
    per_uploader: Counter = Counter()
    clips = []
    for (pool, cat), fnames in sorted(by_cat.items()):
        rng.shuffle(fnames)
        n = 0
        for f in fnames:
            if n >= PER_CATEGORY[pool]:
                break
            up = info[f]["uploader"]
            if per_uploader[up] >= PER_UPLOADER:
                continue
            per_uploader[up] += 1
            n += 1
            split, labs = labels[f]
            clips.append({"fsd_split": split, "fname": f, "labels": ",".join(sorted(labs)), "category": cat, "pool": pool,
                          "licence": info[f]["license"], "uploader": up, "title": info[f]["title"],
                          "url": f"https://freesound.org/s/{f}/"})
    out = {"repo": REPO, "revision": REVISION, "licence": "CC BY 4.0 (FSD50K); per clip CC0 1.0 or CC BY 3.0 only",
           "rule": __doc__.split("usage:")[0].strip(), "excluded_train_dev_clips": len(used_ids), "excluded_train_dev_uploaders": len(used_uploaders),
           "dropped": dict(dropped), "clips": clips}
    Path(__file__).with_name("fsd_test.json").write_text(json.dumps(out, indent=1, ensure_ascii=False) + "\n")
    print(f"{len(clips)} clips: " + ", ".join(f"{p} {n}" for p, n in Counter(c['pool'] for c in clips).items())
          + f"; {len({c['uploader'] for c in clips})} uploaders; licences {dict(Counter(c['licence'].split('/')[-3] for c in clips))}; dropped {dict(dropped)}")


if __name__ == "__main__":
    main()
