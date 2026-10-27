# own-names-bench

**Does a speech recognizer spell the names you taught it, and leave alone the ones you didn't?**

own-names-bench measures how well recognizers write *taught names*: invented and uncommon
names (Mowgli, Pellucidar, Brandoch Daha, Agamemnon) given to the system ahead of time through
its custom-vocabulary feature. Every system gets the same names, in the same order, on the
same audio (public-domain audiobooks, since v1.2.0 call-centre dialogues, voice questions and
meetings, and since v1.3.0 two sealed held-out test suites), and is scored by the same code. Anyone can
rerun it and get the same numbers.

Built by [Virgil](https://virgil.coach) (Little Bear Labs, Inc.) to check our own claims. Read
[CLAIMS.md](CLAIMS.md) before quoting a number.

## What it measures

| Metric | Meaning |
| --- | --- |
| **Names right** | The spoken name is on the list and is written with exactly the listed letters (case and punctuation aside) at the place it is said. |
| **Untaught overwritten** | The same clip is run again with the spoken name *removed* from the list. A listed name written in its place counts. A system that writes listed names wherever something sounds a bit like one does badly here. |
| **Wrong name written** | The spoken name is on the list, but another listed name is written there instead. |
| **Name-free insertions** | Clips that say no name from the list: a listed name written anywhere. In the suites also per minute, and counted apart for names taught from *other* recordings, which are never said in this one (a name of the recording itself may be said in a stretch whose reference missed it). |
| **Ordinary-word error** | Word error rate outside names (every word of every benchmark name removed from both sides), with OpenAI Whisper's English normalizer: does the list damage the rest of the transcript? |
| **Full-transcript error** | The same with nothing removed, so a wrongly written name counts too. |
| **Taught by another reader** | Ours only (systems taught by recording): the same mention with the name taught in a different reader's voice. |
| **Latency, cost** | Per-request latency and real-time factor on the recorded machine; list price per audio hour (with the date checked) for hosted services, measured real-time factor × machine price for local models. |

Four tasks:

1. **Sealed test suites (v1.3).** Two suites built from held-out sources, sealed (every file hashed) before any
   system was scored on them, and scored **once per final system** with the benchmark's own code. They are the
   held-out numbers for the launch.
   - `books13`: held-out audiobooks. 20 LibriVox books read by 20 readers that no other part of this benchmark, no
     dev set and no training set of our adapters (v0.3.0 to v0.7.0) has used: 1,100 mentions of 638 names (777 of
     invented names, 323 of traditional ones), each run with its book's own list (9–176 names) and again with the
     spoken name removed, and 1,200 name-free clips (193 min). The clips task, with the book's text placed on the
     audio by forced alignment only. Suite hash `3d6d8b65…202f`.
   - `conv13`: held-out conversation. European Parliament speech (VoxPopuli test split) and read speech (LibriTTS-R
     test-clean and test-other) in eight conditions, each a suite: as recorded, a phone line, far from the microphone,
     street noise, very quiet with names taught up close, a sound-alike on the list, 0.5–2 s snippets, and names
     taught by another person. 2,327 mentions with 40-name lists, 1,196 name-free pieces (103 min). Suite hash
     `dbff73e6…0fdd3`.
2. **Clips (v1.2.0 audiobooks).** 1,107 mentions of 798 names in 1,051 clips (3.5–15 s) from 12 held-out LibriVox
   audiobooks read by 12 readers, plus 408 name-free clips. Each mention is run with the book's
   own list (18–316 names) and again with the spoken name removed. A harder variant gives every
   clip the **all-books list** (869 distinct names) to the systems whose feature can take it.
   Invented names (Kipling, Burroughs, Baum, Haggard) and traditional names (Homer, Virgil,
   Norse myth, Malory) are reported apart. **Since 2026-10-17 this is our development set**: we chose between our
   candidate adapters on it ([results/v07bench/PROTOCOL.md](results/v07bench/PROTOCOL.md), 16 logged looks in
   [LOOKS.md](results/v07bench/LOOKS.md)), so our numbers on it are optimistic, not a held-out estimate.
3. **Continuous chapters.** 8 whole LibriVox chapters (Dunsany, Eddison; 4 readers, 118 min,
   343 name mentions) with the book's list (28–64 names), again with half the names removed, and
   with no list: names right, wrong names per minute, untaught names overwritten, ordinary-word
   error.
4. **Suites (v1.2): other speech, other speakers.** Each in its own folder under its source's licence.
   - `calls`: AppTek role-played call-centre dialogues (CC BY-SA 4.0), 14 English accents. 706
     scored mentions in 142 calls, the name taught from its first mention (by the same party or the
     other party in the call), plus 417 name-free stretches of 30–60 s (6.0 h) from all 210 calls,
     run with the call's list: the measure of names inserted into long conversation.
   - `svq`: Google Simple Voice Questions (CC BY 4.0). 1,424 mentions; each name taught from one
     person's reading, tested on four other people in clean and noisy recordings.
   - `ami`: AMI meetings, far-field microphone (CC BY 4.0). 119 name-free stretches (1.1 h), each with
     a 40-name list taught in call voices: insertions only.
   - `modulate`: Modulate's entity benchmark, public meetings (CC BY-SA 4.0). 714 mentions. Its audio
     is not re-hosted; `bench fetch` cuts it from Modulate's repository at a pinned revision.

   Lists are 40 names per recording: its taught names, then names taught elsewhere in the suite.
   Suite names were found automatically (capitalised words no word list knows); 26 spellings that
   turned out to be ordinary words ("Theatre", "Mam", "Fridays") stay on the lists the systems were
   given but are never scored (`not_names` in each `suite.json`).

Every number comes with a 95% interval from a bootstrap over books (clips), chapters or suite
recordings (mentions in one book or call share a speaker, a text and names), and systems are compared **paired, on the same items**
with the same clustered bootstrap. Names are matched one to one: a name written once cannot count
for two mentions. Only complete runs are compared.

## Systems

| `--system` | What | How it gets the names |
| --- | --- | --- |
| `ours-mlx` | Detail Keeper's pipeline as it ships: the Detail Keeper engine (Rust, MLX, Apple silicon), spotter shortlist (top 10 of the list per window) → Qwen3-ASR-1.7B + own-names adapter `audio-text-note` v0.7.0 (v7c; writer merged, affine 8-bit) with the name guard and re-read of short windows | spelling + one recording of each name (taught, as in the app) |
| `ours` | The same pipeline as a PyTorch reference runner, with adapter v0.3.0 (the v1.2.0 results) | same |
| `elevenlabs` | ElevenLabs Scribe v2 | `keyterms` (≤1,000) |
| `deepgram` | Deepgram Nova-3 | `keyterm` (≤500 tokens; fitted by asking the service) |
| `whisper` | OpenAI Whisper large-v3 | initial prompt (≤223 tokens) |
| `parakeet` | NVIDIA Parakeet TDT 0.6B v2 | NeMo GPU phrase boosting (weight 2, picked on the chapters task) |
| `qwen` | Qwen3-ASR-1.7B as released | none |
| `qwen-context` | Qwen3-ASR-1.7B as released | its text context |

Every system also runs with **no list**. When a list is longer than a feature allows, the most
frequent names in the book are kept (what a user would do), and every pass records exactly which
names were sent.

**Read this before comparing ours with a hosted service:** our system is taught each name with a
recording of it (that is how Detail Keeper users teach names). Hosted custom-vocabulary features
take only the spelling. The benchmark measures each system as its makers offer it; it does not
pretend the inputs are the same.

## Run it

Python 3.12 and [uv](https://docs.astral.sh/uv/).

```bash
uv run bench fetch                       # the pinned dataset (virgil-coach/own-names-bench@v1.3.0), anonymously, checked file by file
export OWN_NAMES_BENCH_DATA=$PWD/data    # the v1.2.0 suites; data/books13 and data/conv13 are the sealed v1.3 suites

# hosted services (keys from the environment; see keys.env.example)
op run --env-file keys.env -- uv run bench run --system elevenlabs
op run --env-file keys.env -- uv run bench run --system deepgram

# local models: each has its own pinned stack in uv.lock
uv run --extra whisper bench run --system whisper --hourly-usd 0.89
uv run --extra parakeet bench run --system parakeet --hourly-usd 0.89
uv run --extra qwen bench run --system qwen --hourly-usd 0.89
uv run --extra qwen bench run --system qwen-context --hourly-usd 0.89
uv run --extra qwen bench run --system ours --hourly-usd 0.89   # needs espeak-ng

# a sealed suite is a dataset folder of its own
op run --env-file keys.env -- uv run bench --data data/books13 run --system elevenlabs --label books13-elevenlabs --out results/books13
uv run bench --data data/books13 report --runs results/books13 --out results/books13/scores --baseline books13-v7c-mlx

uv run bench report $(sed -n 's/^# report-args: //p' results/scores/REPORT_ARGS)   # results/scores/<run>.json and REPORT.md
uv run python scripts/verify_sealed.py data   # the sealed suites' hashes, published passes and reports
```

No account or token is needed once the repository and dataset are public: `bench fetch` downloads
anonymously on purpose. Until launch they are private, and fetching needs `bench fetch --token` with
access to virgil-coach. `scripts/launch_check.sh` is the launch-day check: a fresh HOME with no
credentials, an anonymous clone and fetch, the tests, the report rebuilt from the published runs, and the
sealed results verified.

`bench estimate --system elevenlabs` prints the audio hours and list-price cost of a full run
before you spend anything. Runs resume: passes already written are not sent again.
`pod/run.sh` is how we ran the local models on a rented GPU, `pod/resume.sh` how a run was finished
or split across GPUs (`build/merge_runs.py` folds the parts back into one run), and
`pod/mac_mlx.sh` how we ran `ours-mlx` on our Macs (`diag/sealed_mlx.sh` for the sealed suites).

Each run writes `results/runs/<label>/run.json` (system configuration with model revisions and
API model names, benchmark and dataset version, manifest SHA-256, code revision, machine, OS,
GPU, exact commands and dates) and `passes.jsonl` (every pass: the text, the names sent, how the
list was fitted, latency). A run's metadata corrected after the fact keeps the old value in `metadata_fixes`;
a run whose code was not recorded exactly is marked `stale` and left out of the report's tables
(`build/fix_run_meta.py`).

## What is pinned

- Benchmark version `1.3.0` (code and data move together; a change to either is a new version). The data
  format (a manifest's `version`) is still `1.2.0`: v1.3.0 adds folders, not a new layout.
- Dataset `virgil-coach/own-names-bench`, tag `v1.3.0` (`v1.2.0`, `v1.1.0` and `v1.0.0` keep the earlier releases): every audio file's
  SHA-256 is in `manifest.json` or its suite's `suite.json`, and `bench` refuses to run on a changed file. Sources read at run
  time (Modulate) are pinned to a revision and checked against PCM hashes. The v1.2.0 files are unchanged in v1.3.0.
- The sealed suites, published byte for byte as they were sealed and scored: `books13/` hashes to suite hash
  `3d6d8b65d4810c4f9571e8274bf02659a1bb507e65c7d0c333a48145a41e202f` and `conv13/suites/` to
  `dbff73e6e5785d0efcf36be582af061b63d59d351cd655ccb6e153ffa850fdd3` (SHA-256 of the `<sha256>  <path>` lines of
  every file, sorted by path; `bench fetch` checks both). `books13/manifest.json` (`e02be6a4…`) and the
  `conv13/manifest.json` wrapper (`48286d15…`) are the manifests the sealed runs record; their dataset fingerprints
  are `455a97ea15754481` and `54d0fa007c55db72`. The seals: `build/books_v13/sealed/`, `build/conv_v13/sealed/`.
- The name lists, their order, the reference text and its normalization (`own_names_bench/text.py`,
  normalization version 1), the sampling seed (20261013).
- Model revisions (Hugging Face commit hashes) and API model names, in `run.json`.
- Python dependencies in `uv.lock`.

## Results (v1.3.0)

Percent, with 95% intervals from a bootstrap over clusters: books (clips), chapters, or recordings
(suites: a call, a question, a meeting; for conv13 a list group). Ours is v7c (`ours-mlx`: adapter v0.7.0, SHA-256
`de91437d…1226c`, Detail Keeper engine `af939d6`), taught each name with one recording; the hosted services get the
spelling only. Paired differences are ours minus the other system on the same items; a difference is
**better** or **worse** only where its interval excludes zero, otherwise *no measurable difference*.

Runs: v7c on the sealed suites 2026-10-27, on the v1.2.0 suites 2026-10-20; ElevenLabs Scribe v2 (`scribe_v2`,
`keyterms`, every name) on books13 2026-10-27, on conv13 **2026-10-16** (that run is reused: it was made for the
v0.6 final and not re-run), on the v1.2.0 suites 2026-10-26; Deepgram Nova-3 (`nova-3`, keyterm prompting, the most
frequent names that fit 500 tokens) on the v1.2.0 suites 2026-10-26, not run on the sealed suites. The other local
models' v1.2.0 runs are of 2026-10-13/14.

### Sealed audiobooks (books13)

Clips with the book's own list, 1,100 mentions in 20 books; 1,200 name-free clips.
Source: [results/books13/scores/REPORT.md](results/books13/scores/REPORT.md).

| System (how it got the names) | Names right | invented | traditional | Untaught overwritten | Name-free clips: listed name inserted | Ordinary-word error |
| --- | --- | --- | --- | --- | --- | --- |
| Ours, v7c (spelling + one recording per name) | 89.6 [83.4, 94.4] | 92.9 [91.2, 95.1] | 81.7 [71.8, 96.1] | 3.6 [1.1, 6.6] | 0.2 [0.0, 0.4] (2/1200) | 2.1 [1.7, 2.6] |
| ElevenLabs Scribe v2 (`keyterms`, all names) | 88.2 [79.4, 95.1] | 92.4 [88.6, 96.1] | 78.0 [64.1, 97.5] | 1.5 [0.5, 2.4] | 0.2 [0.0, 0.4] (2/1200) | 1.5 [1.2, 1.9] |

Ours minus Scribe, same items: names right +1.5 [−1.9, +4.7], no measurable difference (invented +0.5 [−2.1, +3.6],
traditional +3.7 [−7.5, +8.4]); name-free insertions +0.0 [−0.2, +0.2], no measurable difference; untaught names
overwritten +2.2 [+0.1, +4.6] (worse); ordinary-word error +0.6 [+0.4, +0.7] (worse).

Read with care:
- **books13 was sealed after v7c was frozen** (2026-10-27; v7c had been chosen on the v1.2.0 clips). Nothing about
  the suite could feed back into v7c and no system was run on it while it was built, but unlike conv13 it was not
  sealed before the final choice.
- **LibriSpeech overlap:** 11 of its 20 readers are LibriSpeech speakers, and 5 of its books' readings (the suite
  reader's own reading; 9 LibriSpeech chapters) are in LibriSpeech. None of it is in our training data; the base
  Qwen3-ASR, the hosted services and the aligner may have trained on LibriSpeech.
- References are the Gutenberg text placed on the audio by forced alignment (gated, calibrated on a dev book), not
  human transcripts. There is no all-books list and no chapters task.

### Sealed conversation (conv13)

2,327 mentions and 1,196 name-free pieces in eight conditions, each a suite with 40-name lists. Pooled over the eight
(counts; there is no pooled interval): names right ours 2,103/2,327 (90.4%), Scribe 2,139/2,327 (91.9%); untaught
overwritten ours 93 (4.0%), Scribe 204 (8.8%); name-free pieces with a listed name inserted ours 6/1,196 (0.5%), Scribe
29/1,196 (2.4%); ordinary-word error ours 11.2%, Scribe 10.3%. Per condition, with intervals: [results/conv13/scores/REPORT.md](results/conv13/scores/REPORT.md).

| Condition | Names right: ours | Scribe | Ours − Scribe | Untaught overwritten: ours − Scribe | Name-free inserted: ours − Scribe | Ordinary-word error: ours − Scribe |
| --- | --- | --- | --- | --- | --- | --- |
| As recorded (`conv13-conv`) | 98.5 [96.2, 100.0] | 97.7 [94.8, 100.0] | +0.8 [−2.3, +4.2] | −0.8 [−2.4, +0.0] | +0.0 [+0.0, +0.0] | −0.7 [−1.7, +0.1] |
| Phone line (`tel`) | 98.1 [96.3, 99.6] | 97.0 [94.9, 98.9] | +1.1 [−1.1, +3.4] | −5.6 [−8.8, −2.4] (better) | −0.5 [−1.6, +0.0] | +0.3 [−0.3, +0.8] |
| Far from the microphone (`far`) | 82.9 [78.3, 87.2] | 88.0 [84.4, 91.5] | −5.1 [−9.1, −1.4] (worse) | −6.0 [−9.4, −2.7] (better) | −1.3 [−3.4, +0.0] | +1.1 [−7.9, +6.1] |
| Street noise (`street`) | 93.8 [90.9, 96.4] | 95.6 [93.3, 97.7] | −1.9 [−4.9, +1.2] | −1.2 [−4.0, +1.6] | +0.0 [+0.0, +0.0] | +1.1 [+0.3, +1.9] (worse) |
| Very quiet, taught up close (`level`) | 78.7 [73.7, 83.5] | 84.3 [79.8, 88.7] | −5.7 [−9.9, −1.4] (worse) | −5.7 [−8.9, −2.5] (better) | +0.0 [−3.4, +3.3] | +4.1 [+2.7, +5.5] (worse) |
| A sound-alike on the list (`near`) | 92.1 [88.9, 95.1] | 92.5 [89.3, 95.4] | −0.4 [−3.9, +3.2] | −7.1 [−11.9, −2.8] (better) | n/a | +1.4 [+0.5, +2.3] (worse) |
| Short snippets (`short`) | 85.2 [81.1, 89.0] | 84.6 [80.2, 88.8] | +0.6 [−4.2, +5.4] | −8.7 [−12.5, −5.1] (better) | −5.3 [−8.3, −2.6] (better) | −11.8 [−15.7, −7.9] (better) |
| Taught by another person (`xspk`) | 99.1 [98.0, 100.0] | 99.4 [98.5, 100.0] | −0.3 [−1.5, +0.9] | −1.1 [−2.8, +0.3] | n/a | +0.6 [−0.5, +1.5] |

No measurable difference unless marked. Read with care:
- **Scribe's conv13 run is of 2026-10-16, reused** (made for the v0.6 final, same dataset fingerprint `54d0fa00…`,
  not re-run); ours is of 2026-10-27. A hosted service changes; this compares Scribe as it was on 2026-10-16.
- **VoxPopuli is held out by speaker, not by debate:** no test speaker is in our training or dev data, but 265 of the
  404 VoxPopuli utterances used come from a plenary debate that also holds other speakers' training utterances
  (flagged `session_shared` on every clip). LibriTTS-R is held out by reader and book.
- Some listed names were said in our conversation training data: each mention's group (`name never seen in training`
  / `name seen in training`) is in the per-condition tables. Deviations from the design (no FLEURS, no NOTSOFAR-1, so
  far and level use simulated rooms) are in its card, `build/conv_v13/README.md`.

### v1.2.0 suites: conversation, other speakers, meetings

Every system with the recording's 40-name list. *Calls, inserted*: name-free stretches (417, 6.0 h)
where a listed name was written; *from other calls*: only names taught from other calls, which are
never said in this one. Source: [results/scores/REPORT.md](results/scores/REPORT.md).

| System | Calls: names right | Calls: untaught overwritten | Calls: name-free stretches, a listed name inserted | Calls: … a name from other calls | SVQ (taught by another person): names right | Modulate meetings: names right | AMI meetings: name-free stretches, a listed name inserted |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Ours, v7c (spelling + one recording per name) | 95.3 [93.4, 97.0] | 1.0 [0.2, 2.1] | 1.7 [0.5, 2.9] | 0.5 [0.0, 1.2] | 93.8 [92.0, 95.5] | 91.6 [88.3, 94.2] | 0.0 [0.0, 0.0] |
| ElevenLabs Scribe v2 (`keyterms`, 2026-10-26) | 95.3 [93.3, 97.0] | 1.6 [0.5, 3.0] | 1.4 [0.5, 2.6] | 0.0 [0.0, 0.0] | 98.5 [97.6, 99.2] | 93.1 [89.3, 96.2] | 0.0 [0.0, 0.0] |
| Deepgram Nova-3 (`keyterm`, 2026-10-26) | 91.9 [89.5, 94.2] | 1.7 [0.7, 3.0] | 1.2 [0.2, 2.4] | 0.2 [0.0, 0.7] | 89.4 [87.2, 91.5] | 84.9 [79.1, 89.6] | 0.0 [0.0, 0.0] |
| Ours, v0.3.0 (PyTorch reference) | 92.8 [90.8, 94.6] | 3.4 [1.7, 5.4] | 2.6 [1.0, 4.6] | 1.2 [0.2, 2.6] | 91.4 [89.6, 93.2] | 88.7 [84.0, 92.6] | 1.7 [0.0, 3.3] |
| Whisper large-v3 (prompt) | 90.4 [87.2, 92.9] | 1.3 [0.4, 2.5] | 2.2 [1.0, 3.6] | 1.0 [0.2, 1.9] | 80.1 [76.8, 83.1] | 83.6 [72.2, 90.2] | 1.7 [0.0, 3.3] |
| Parakeet TDT 0.6B v2 (phrase boosting) | 88.1 [84.5, 91.3] | 13.2 [10.0, 16.8] | 15.6 [12.0, 19.4] | 13.9 [10.5, 17.5] | 85.8 [83.5, 88.2] | 81.1 [65.3, 89.7] | 9.2 [6.8, 11.8] |
| Qwen3-ASR-1.7B (names as context) | 94.6 [92.6, 96.4] | 1.3 [0.5, 2.1] | 4.1 [2.2, 6.2] | 2.6 [1.2, 4.4] | 95.4 [93.7, 97.0] | 89.6 [84.5, 93.4] | 5.9 [1.7, 10.8] |

Ours (v7c) minus Scribe, same items: calls, names right +0.0 [−2.2, +2.2], untaught overwritten −0.6 [−1.6, +0.3],
name-free stretches with an insertion +0.2 [−0.5, +1.0], with a name from other calls +0.5 [+0.0, +1.2] (all no
measurable difference), ordinary-word error +0.7 [+0.4, +1.1] (worse). SVQ, a name taught by one person and said by
another, names right −4.7 [−6.5, −3.1] (worse), ordinary-word error −4.9 [−7.0, −3.0] (better). Modulate meetings,
names right −1.5 [−2.8, +0.0] (no measurable difference). AMI insertions +0.0 [+0.0, +0.0] (no measurable
difference), ordinary-word error +2.3 [+0.7, +3.9] (worse).

Ours (v7c) minus Deepgram: names right on calls +3.4 [+0.9, +5.9], SVQ +4.4 [+2.2, +6.5] and Modulate +6.7 [+4.1, +9.9]
(better); untaught overwritten on SVQ −1.3 [−2.1, −0.7] (better), on calls −0.7 [−2.0, +0.4] and Modulate −1.0
[−2.3, +0.0] (no measurable difference); name-free insertions on calls +0.5 [−0.5, +1.4], SVQ and AMI +0.0 (no
measurable difference); ordinary-word error on SVQ −8.4 [−10.0, −6.9] and Modulate −2.2 [−2.9, −1.4] (better), on
calls −0.3 [−0.7, +0.0] and AMI −0.0 [−2.2, +2.2] (no measurable difference).

Read with care:
- AppTek's references miss some spoken names (a name said in a call written as "man", or left out),
  so a call's own name written in a "name-free" stretch can be right. That is why insertions of names
  from other calls are reported apart: those are never said in the call.
- On far-field meeting audio (AMI) v7c's ordinary-word error is 19.0% [16.4, 20.9] against 16.7% for Scribe and
  19.0% for Deepgram (v0.3.0: 28.2%). Fewer words written also means fewer chances to insert a name.
- Qwen3-ASR with names as context sometimes writes the list itself into the transcript (up to dozens
  of names in one 30 s stretch): 2.95 listed names per minute of name-free AMI audio, 1.51 on calls.
- Hosted services and Qwen3-ASR may have trained on AMI and on People's Speech (Modulate's source);
  AppTek (2026, evaluation only) and SVQ are less likely to be in anyone's training data.

### Development set: the v1.2.0 audiobook clips and chapters

**Not a held-out estimate for ours.** From 2026-10-17 the v1.2.0 audiobook clips were used to choose between our
candidate adapters (protocol: [results/v07bench/PROTOCOL.md](results/v07bench/PROTOCOL.md); every look, 16 of
them, in [LOOKS.md](results/v07bench/LOOKS.md)), so v7c's figures here are optimistic. books13 above is the held-out
audiobook number. Clips: each book's own list, 1,107 mentions in 12 books; chapters: 343 mentions in 8 chapters.

| System (how it got the names) | Names right, clips | Untaught overwritten, clips | Name-free clips: listed name inserted | Ordinary-word error, clips | Names right, chapters |
| --- | --- | --- | --- | --- | --- |
| Ours, v7c (spelling + one recording per name; selected on these clips) | 92.6 [88.8, 96.5] | 4.6 [1.1, 8.0] | 1.2 [0.2, 2.5] | 2.8 [2.3, 3.3] | not run |
| ElevenLabs Scribe v2 (`keyterms`, all names, 2026-10-26) | 92.8 [88.5, 97.2] | 2.9 [1.2, 4.8] | 0.2 [0.0, 0.7] | 1.7 [1.4, 1.9] | 97.4 [91.3, 100.0] |
| Deepgram Nova-3 (`keyterm`, 2026-10-26; 85.8% of spoken names fit its limit) | 75.1 [61.8, 89.5] | 8.5 [5.9, 11.1] | 1.7 [0.5, 2.9] | 4.2 [3.1, 5.1] | 83.4 [76.1, 91.4] |
| Ours, v0.3.0 (PyTorch reference; before the protocol) | 96.7 [94.9, 98.6] | 7.0 [2.3, 11.3] | 3.9 [0.5, 9.6] | 2.7 [2.4, 3.0] | 99.4 [98.6, 100.0] |
| Whisper large-v3 (prompt; 65.6% fit in 223 tokens) | 74.3 [63.7, 88.6] | 1.6 [0.2, 3.4] | 0.2 [0.0, 0.7] | 3.0 [2.4, 3.4] | 77.0 [54.5, 93.8] |
| Parakeet TDT 0.6B v2 (phrase boosting, weight picked on chapters) | 78.5 [72.3, 85.3] | 27.2 [15.9, 37.3] | 7.1 [4.2, 10.3] | 3.5 [2.9, 4.0] | 91.8 [87.5, 97.9] |
| Qwen3-ASR-1.7B (names as context) | 63.9 [54.6, 75.2] | 4.3 [1.6, 7.2] | 0.2 [0.0, 0.7] | 3.6 [2.6, 4.5] | 89.2 [85.4, 94.6] |
| Qwen3-ASR-1.7B (no list) | 41.8 [35.4, 47.5] | n/a | 0.0 | 4.3 [3.8, 4.8] | 22.2 [10.4, 37.6] |

v7c minus Scribe on the clips, same items: names right −0.2 [−2.7, +1.9], untaught overwritten +1.7 [−1.3, +4.4],
name-free insertions +1.0 [−0.2, +2.2] (5 clips against 1), all no measurable difference; ordinary-word error +1.1
[+0.7, +1.5] (worse). v7c minus Deepgram: names right +17.5 [+5.9, +27.2] (better), untaught overwritten −3.9 [−7.4,
−1.3] (better), name-free insertions −0.5 [−2.0, +1.0] (no measurable difference), ordinary-word error −1.4 [−2.0,
−0.7] (better). v7c was not run on the chapters or with the all-books list.

Read with care: hosted services and Whisper likely know these classic texts (with no list at
all, Scribe already writes 60.5% of the names right); Parakeet's boosting weight was picked on
the chapters task, so its chapter numbers are optimistic; Deepgram and Whisper received only part
of the longest lists. Whisper on an RTX 4090 and an A100 wrote identical text for 99.6% of passes.
The 2026-10-13/14 ElevenLabs and Deepgram runs (the v1.2.0 results) are superseded by the 2026-10-26 re-runs
([results/scores/HOSTED_RERUN_2026-10-26.md](results/scores/HOSTED_RERUN_2026-10-26.md)) and marked stale: some of
their passes were made from uncommitted code.

Rebuild the report from the published runs: `uv run bench report $(sed -n 's/^# report-args: //p' results/scores/REPORT_ARGS)`.
What v1.3.0 changed: [results/scores/CHANGES_v1.2_to_v1.3.md](results/scores/CHANGES_v1.2_to_v1.3.md).

## Contamination

`build/contamination_v13.py` checks every suite against the training data of v7c, from the item-by-item attribution
published with the adapter (`virgil-coach/own-names-qwen3-asr` v0.7.0, `attribution/`; it includes v0.3.0's items):
[results/contamination/v7c_v1.3.0.json](results/contamination/v7c_v1.3.0.json). **PASS, 0 failures**: no reader or
speaker, LibriVox recording, training-audiobook text, LibriTTS-R utterance, speaker or chapter, FSD50K clip or training
corpus is shared with the v1.2.0 audiobooks, the four v1.2.0 suites, books13 or conv13. Reported: conv13's VoxPopuli
debates (125 of its 199 plenary sessions also hold training utterances of other speakers; held out by speaker), and
listed names that are also in a training name list (v1.2.0 audiobooks 1 of 1,055, calls 2, svq 1, ami 2, modulate 2,
books13 0 of 894, conv13 11 of 1,019). Not checkable from the
attribution, and said so there: YODAS voices, VoxPopuli speakers (checked by conv13's own build against the
conversation train/dev data), and names said in conversation training utterances. Each sealed suite's own build check
(`build/books_v13/sealed/contamination.json`, `build/conv_v13/sealed/contamination.json`) also passed.

## Data and licences

- Code: Apache 2.0, © 2026 Little Bear Labs, Inc. (`LICENSE`, `NOTICE`). The vendored Whisper
  normalizer is MIT (OpenAI).
- Audiobooks (v1.2.0): LibriVox recordings, public domain (US). Readers are credited in the dataset card.
  Text and names: from the public-domain Project Gutenberg texts of the same books. Our annotations
  of them: Apache 2.0.
- Suites (v1.2.0): each in its own dataset folder `suites/<name>/`, audio and our annotations under the
  source's licence (`LICENCE.txt` there): `calls` from AppTek Call-Center Dialogues, CC BY-SA 4.0;
  `svq` from Google Simple Voice Questions, CC BY 4.0; `ami` from the AMI Meeting Corpus, CC BY 4.0;
  `modulate` from Modulate's Entity Transcription Benchmark, CC BY-SA 4.0. Modulate's audio is not
  re-hosted: the folder holds only our annotations, and `bench fetch` reads the audio from
  Modulate's repository at a pinned revision.
- `books13/` (v1.3.0): LibriVox recordings and Project Gutenberg texts, public domain in the US; annotations CC BY
  4.0, © 2026 Little Bear Labs, Inc. Every book, reader, LibriVox page, archive.org item, Gutenberg id and
  public-domain basis is in `books13/ATTRIBUTION.csv` and the manifest's `attribution`. Card:
  [build/books_v13/README.md](build/books_v13/README.md).
- `conv13/` (v1.3.0): CC BY 4.0 (`LICENCE.txt` in each condition). VoxPopuli test-split audio (Wang et al., 2021;
  European Parliament recordings, CC0 1.0; source: European Parliament), LibriTTS-R test-clean and test-other
  (Koizumi et al., 2023, from LibriTTS by Zen et al., 2019, from LibriVox; CC BY 4.0), and FSD50K background noise
  (Fonseca et al., 2022), clips under CC0 1.0 or CC BY 3.0, each credited by title, Freesound uploader, licence and
  URL in the condition's `NOISE_ATTRIBUTION.csv`; resampled, mixed and processed. Card:
  [build/conv_v13/README.md](build/conv_v13/README.md).
- How the data was cut: `build/` (`build/build_v12.py` for the v1.2.0 suites, `build/books_v13/` and
  `build/conv_v13/` for the sealed suites) and the dataset card. Contamination: above.
