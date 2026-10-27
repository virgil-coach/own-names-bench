# own-names-bench v1.3 conversation test suite (held out, sealed)

A frozen test suite for the conversation conditions of own-names-bench v1.3, built with the recipe of the
conversation train and dev data (lore-poc `convdata/`, branch `data/conv-names-v1`, commit `9004fe4`) from each
source's own **test** split, before any final v0.6 adapter or name guard existed. It is scored **once per final
system** (ours, ElevenLabs Scribe v2) with the benchmark's own code. Nothing was scored on it while it was built.

**Rule.** Do not read, train, tune, select or smoke-test on this data. No model or API was run on its audio during
the build; the only model that touched it is the forced aligner that timed the reference's words (prep.py). Validity
was checked with data tooling only (hashes, levels, alignment against the clean source).

## Where it is

The audio, the `suite.json` files (references and lists) and the build files are on the RunPod global volume
`gpu-cli-user` (EUR-IS-1), in a path of their own, apart from `lore-conv`, `v06-conv`, `ctxft` and `convdata`:

| Path | What |
| --- | --- |
| `/gpu-cli-workspaces/jameslal/onb-v13-conv-SEALED/suite/conv13-<cond>/` | one benchmark suite per condition: `suite.json`, `audio/clips`, `audio/enroll`, `LICENCE.txt`, `NOISE_ATTRIBUTION.csv` (read-only) |
| `/gpu-cli-workspaces/jameslal/onb-v13-conv-SEALED/MANIFEST.json`, `SHA256SUMS`, `SEALED.txt` | the seal: every file's SHA-256 and the suite hash |
| `/gpu-cli-workspaces/jameslal/onb-v13-conv-SEALED/build/` | prepared test utterances, noise, build stats, contamination and validity reports |

Nothing of it is in git except this card, the build code and the seal's reports (`sealed/`: the manifest with every
file hash (the suite hash recomputes from its `files`), the contamination report and the validity report, all counts only). Not uploaded anywhere else.

## Conditions

As in dev (`sub` in the dev rows); each condition is a suite `conv13-<cond>` with its named mentions (scored with
the name on its list and, by the benchmark's `own-minus` pass, off it: dev's taught / untaught pair) and, where dev has
them, its name-free pieces (`free_<cond>`).

| Suite | Clips | Augmentation (dev's, common.py) |
| --- | --- | --- |
| `conv13-xspk` | names taught from another person's recording | clean (55%), indoor/ambient noise 5-20 dB or street noise -2-15 dB |
| `conv13-conv` | spontaneous parliament speech + `free_conv` | clean, as recorded |
| `conv13-tel` | + `free_tel` | clip and every taught recording through a phone line (300-3400 Hz, 8 kHz, G.711 / GSM / Opus 6-12 kb/s, lost packets) |
| `conv13-far` | + `free_far` | simulated room (RT60 0.25-1.0 s, 1-5 m; noise, babble or both at 0-20 / 3-15 dB), left quiet (-42 to -24 dBFS) |
| `conv13-street` | + `free_street` | traffic, vehicle, siren, crowd, rain, wind and subway sounds at -2 to 15 dB SNR |
| `conv13-level` | + `free_level` | far-field clip at -50 to -36 dBFS, taught recordings loud close-talk (-16 to -10 dBFS) |
| `conv13-near` | a real name one or two sounds from the spoken one is always listed | conv/tel/far/street per list group |
| `conv13-short` | 0.5-2 s around the name + `free_short` (0.4-2 s name-free stretches) | conv/tel/far/street/level per list group |

Every mention records `name_seen_in_train` (dev's definition: the name is said in a conversation training
utterance) and its mention `group` is `name never seen in training` or `name seen in training`, so the benchmark's
`right_by_group` gives the "names never seen in training" row directly. Lists prefer names never said in training.
Counts per condition are in `sealed/MANIFEST.json` (`suites`) and below.

| Suite | Mentions (dev) | VoxPopuli / LibriTTS-R | Name never seen in training | Taught by another speaker | Name-free pieces | Clips | Hours |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `conv13-xspk` | 348 (600) | 103 / 245 | 60 | 348 | 0 | 348 | 0.819 |
| `conv13-conv` | 132 (350) | 132 / 0 | 27 | 84 | 200 | 332 | 0.787 |
| `conv13-tel` | 270 (270) | 120 / 150 | 177 | 90 | 200 | 470 | 1.005 |
| `conv13-far` | 333 (350) | 133 / 200 | 227 | 98 | 150 | 483 | 1.051 |
| `conv13-street` | 320 (320) | 120 / 200 | 227 | 92 | 150 | 470 | 1.037 |
| `conv13-level` | 300 (300) | 120 / 180 | 207 | 87 | 120 | 420 | 0.924 |
| `conv13-near` | 280 (350) | 80 / 200 | 215 | 65 | 0 | 280 | 0.648 |
| `conv13-short` | 344 (360) | 134 / 210 | 237 | 104 | 376 | 720 | 0.189 |
| **total** | **2327** | | **1377** | | **1196** | **3523** | **6.46** |

Suite hash `dbff73e6e5785d0efcf36be582af061b63d59d351cd655ccb6e153ffa850fdd3` (86867 files, 1.38 GB), sealed 2026-10-16T06:36:49Z from build commit `07da163`. `conv` falls short of dev's 350 and `xspk` of 600: after removing every train/dev speaker, VoxPopuli test keeps 218 utterances with a name, and `xspk` needs a second speaker saying the same name. Name-free pieces: 1,196 (102.9 minutes), so one insertion is 0.08%.

## How it differs from dev (on purpose)

- **Clips are cut by the source, not by our engine.** Dev rows were our engine's windows; a test clip is a whole
  utterance (1.5-20 s) or a 0.5-2 s stretch on aligned word boundaries, so no system is handed its own segmentation.
- **References are the sources' human transcripts.** Dev labels were the untrained recognizer's transcript of the
  clean counterpart; here no recognizer runs on test audio.
- **Lists are the benchmark's: 40 names per clip**, shared by a group of at most 8 clips of one speaker: its taught
  names, the closest-spelled real names of each (for `near`, its three real sound-alikes), then other names of the
  test split, never a name said anywhere in the group's references. Dev rows carried our spotter's top ten of such a
  40-name glossary; here every system gets the 40 and our pipeline runs its spotter itself.
- **Noise and rooms are new.** FSD50K clips that are in no train/dev noise set, by no train/dev uploader, and whose
  energy envelope matches no train/dev noise file (MUSAN, FSD50K); rooms from a new seed.

## Sources, licences, attribution

| Source | Licence | Revision | Used |
| --- | --- | --- | --- |
| VoxPopuli en, **test** split (`facebook/voxpopuli`) | CC0 1.0 | `42f01879c780b4a2e90ec0b4f616c2ece526e4f1` | speakers in no train/dev utterance |
| LibriTTS-R **test-clean, test-other** (`mythicinfinity/libritts_r`) | CC BY 4.0 | `0d1718db351207d5a493135a62d5ed8cc4733830` | readers and books in no train/dev, benchmark, lore held-out or v0.3.0 data |
| FSD50K (`Fhrozen/FSD50k`, `fsd_test.json`) | CC BY 4.0; clips CC0 1.0 / CC BY 3.0 | `ccf1acaff12f3f4a4c10052dddafbb6d22152c9b` | background noise, credited per clip in `NOISE_ATTRIBUTION.csv` |
| LibriSpeech metadata (openslr 12) | CC BY 4.0 | sha256 in `build/src/fetched.json` | reader and book exclusions |
| wav2vec2-large-960h-lv60-self | Apache 2.0 | `54074b1c16f4de6a5ad59affb4caa8f2ea03a119` | forced alignment of reference words only |
| pyroomacoustics | MIT | 0.10.1 | simulated rooms |

The suite (annotations and processed audio) is CC BY 4.0. Attribution: VoxPopuli (Wang et al., 2021), LibriTTS-R
(Koizumi et al., 2023; from LibriTTS, Zen et al., 2019, from LibriVox), FSD50K (Fonseca et al., 2022) and each
Freesound uploader listed in the suite's `NOISE_ATTRIBUTION.csv`.

**Deviations from the design, accepted 2026-10-16.** No FLEURS, no NOTSOFAR-1 (so no real meeting-room audio: far and level use simulated rooms; real meetings come from ICSI in v1.3), and VoxPopuli held out by speaker but not by debate item. Each is explained below and in the contamination section. The suite was sealed before these were accepted and was not changed.

**Not used, and why.**
- **FLEURS**: the dev data used all three en_us splits, test included, so no FLEURS recording is held out from dev.
- **NOTSOFAR-1**: its eval set has 12 participants; the dev data's 60 eval meetings hold 6 of them and every one of
  the 69 other eval meetings has at least one of those 6; the `dev_set` meetings are train meetings. No NOTSOFAR
  meeting is speaker-disjoint from train and dev, so real far-field meetings are left to ICSI (reserved for v1.3).
- Common Voice, EdAcc, DailyTalk (licence); AMI, Modulate, AppTek, SVQ (own-names-bench v1.2); ICSI, Earnings-21
  (reserved for v1.3).

## Contamination check (`check.py`, `sealed/contamination.json`)

Against the conversation train and dev data (the EUR-IS-1 copy v0.6 trains on, `v06-conv/lore-conv`; the EU-RO-1
build has identical statistics), own-names-bench v1.2.0 (`excl.json`, from its manifest and suites), the v0.3.0
adapter's training data (`attribution_v030/`) and the corpora reserved for v1.3:

- speakers: no test speaker or teacher is a train/dev speaker, a benchmark suite speaker, a benchmark or lore held-out
  reader, a v0.3.0 LibriTTS speaker or a reader of a v0.3.0 LibriVox book;
- sessions: no LibriTTS-R chapter or book is in train, dev, the benchmark or v0.3.0's books. **VoxPopuli debate items
  are not disjoint**: 440 of VoxPopuli's 489 test debate items also occur in its train/validation shards (and so in
  our train/dev), and only 104 test utterances are both speaker- and debate-disjoint. As in dev, VoxPopuli is held
  out by speaker; every clip carries `session_shared`, the disjoint utterances were used first, and the counts are
  in the report;
- recordings and audio: no test utterance is a train/dev utterance; no test file equals a train/dev or benchmark file
  by SHA-256 of the file or of its PCM;
- text: no test text shares a run of 8 normalized words with a train/dev utterance or a benchmark reference;
- noise and rooms: no clip id, uploader, file or energy envelope of a train/dev noise; no train/dev room.

**Result: PASS** (no failures). Test speakers 235, shared with train/dev, the benchmark, lore held-out or v0.3.0: 0. LibriTTS-R chapters/books shared: 0. Recordings shared: 0. Files hash-equal to train/dev (122,143 hashed) or to the benchmark (6,123 hashes): 0. Texts sharing an 8-word run: 0 of 5,421. Noise: clip ids, uploaders, files and envelope near-duplicates shared 0 (max correlation 0.949; prep dropped 175 FSD50K clips at >= 0.95 before the build, a deliberately conservative cut). Rooms shared 0. VoxPopuli: 265 of 404 VoxPopuli utterances used are in one of 148 debate items that also hold other speakers' train/dev utterances (flagged `session_shared` on every clip). Validity: PASS (no problem found; aligned names sit a median 0.9 dB above their utterance's level in the clean source). Repeated file hashes in the suite are taught recordings: the same close-talk cut of a name is listed in several groups.

## Rebuild

`excl.json`, the exclusion lists that `prep.py` and `check.py` read (own-names-bench v1.2.0's readers, books, speakers,
audio hashes and texts, and the lore held-out readers and books), is internal and not published: it is not in this
repository or the dataset. Its SHA-256 is in `sealed/MANIFEST.json` (`build_files`), so the seal still pins it. A
rebuild without it cannot apply those exclusions; the contamination report records what the check found with it.

`launch.sh` (from this folder, a gpu-cli project, EUR-IS-1): copies the benchmark's text module into `_onb/`, then
runs `run.sh` on a pod: volume write self-test, `fetch.py`, `prep.py`, `build.py`, `check.py`, `seal.py`. `fsd_test.py`
selected the noise clips from FSD50K metadata (run once, locally). Each script documents itself. The build is
seeded (1313; rooms 13) and pinned (`uv.lock`); `run.sh` refuses to run once `SEALED.txt` exists.
