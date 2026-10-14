# own-names-bench

**Does a speech recognizer spell the names you taught it, and leave alone the ones you didn't?**

own-names-bench measures how well recognizers write *taught names*: invented and uncommon
names (Mowgli, Pellucidar, Brandoch Daha, Agamemnon) given to the system ahead of time through
its custom-vocabulary feature. Every system gets the same names, in the same order, on the
same public-domain audiobook audio, and is scored by the same code. Anyone can rerun it and
get the same numbers.

Built by [Virgil](https://virgil.coach) (Little Bear Labs, Inc.) to check our own claims. Read
[CLAIMS.md](CLAIMS.md) before quoting a number.

## What it measures

| Metric | Meaning |
| --- | --- |
| **Names right** | The spoken name is on the list and is written with exactly the listed letters (case and punctuation aside) at the place it is said. |
| **Untaught overwritten** | The same clip is run again with the spoken name *removed* from the list. A listed name written in its place counts. A system that writes listed names wherever something sounds a bit like one does badly here. |
| **Wrong name written** | The spoken name is on the list, but another listed name is written there instead. |
| **Name-free insertions** | Clips that say no name from the list: a listed name written anywhere. |
| **Ordinary-word error** | Word error rate outside names (every word of every benchmark name removed from both sides), with OpenAI Whisper's English normalizer: does the list damage the rest of the transcript? |
| **Full-transcript error** | The same with nothing removed, so a wrongly written name counts too. |
| **Taught by another reader** | Ours only (systems taught by recording): the same mention with the name taught in a different reader's voice. |
| **Latency, cost** | Per-request latency and real-time factor on the recorded machine; list price per audio hour (with the date checked) for hosted services, measured real-time factor × machine price for local models. |

Three tasks:

1. **Clips.** 1,107 mentions of 798 names in 1,051 clips (3.5–15 s) from 12 held-out LibriVox
   audiobooks read by 12 readers, plus 408 name-free clips. Each mention is run with the book's
   own list (18–316 names) and again with the spoken name removed. A harder variant gives every
   clip the **all-books list** (869 distinct names) to the systems whose feature can take it.
   Invented names (Kipling, Burroughs, Baum, Haggard) and traditional names (Homer, Virgil,
   Norse myth, Malory) are reported apart.
2. **Continuous chapters.** 8 whole LibriVox chapters (Dunsany, Eddison; 4 readers, 118 min,
   343 name mentions) with the book's list (28–64 names), again with half the names removed, and
   with no list: names right, wrong names per minute, untaught names overwritten, ordinary-word
   error.

3. **Suites (v1.2): other speech, other speakers.** Each in its own folder under its source's licence.
   - `calls`: AppTek role-played call-centre dialogues (CC BY-SA 4.0), 14 English accents. 1,050
     mentions in 210 calls, the name taught from its first mention (by the same party or the other
     party in the call), plus 409 name-free stretches of 30–60 s (5.9 h) run with the call's list:
     the measure of names inserted into long conversation.
   - `svq`: Google Simple Voice Questions (CC BY 4.0). 1,424 mentions; each name taught from one
     person's reading, tested on four other people in clean and noisy recordings.
   - `ami`: AMI meetings, far-field microphone (CC BY 4.0). 119 name-free stretches (1.1 h): insertions only.
   - `modulate`: Modulate's entity benchmark, public meetings (CC BY-SA 4.0). 714 mentions. Its audio
     is not re-hosted; `bench fetch` cuts it from Modulate's repository at a pinned revision.

Every number comes with a 95% interval from a bootstrap over books (clips) or chapters (mentions in
one book share a reader, a text and names), and systems are compared **paired, on the same items**
with the same clustered bootstrap. Names are matched one to one: a name written once cannot count
for two mentions. Only complete runs are compared.

## Systems

| `--system` | What | How it gets the names |
| --- | --- | --- |
| `ours` | Detail Keeper's pipeline, PyTorch reference runner: spotter shortlist (top 10 of the list per window) → Qwen3-ASR-1.7B + own-names LoRA `audio-text-note` v0.3.0 | spelling + one recording of each name (taught, as in the app) |
| `ours-mlx` | The same pipeline in the shipping Detail Keeper engine (Rust, MLX, Apple silicon) | same |
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
uv run bench fetch                       # the pinned dataset (virgil-coach/own-names-bench@v1.1.0), anonymously, checked file by file
export OWN_NAMES_BENCH_DATA=$PWD/data

# hosted services (keys from the environment; see keys.env.example)
op run --env-file keys.env -- uv run bench run --system elevenlabs
op run --env-file keys.env -- uv run bench run --system deepgram

# local models: each has its own pinned stack in uv.lock
uv run --extra whisper bench run --system whisper --hourly-usd 0.89
uv run --extra parakeet bench run --system parakeet --hourly-usd 0.89
uv run --extra qwen bench run --system qwen --hourly-usd 0.89
uv run --extra qwen bench run --system qwen-context --hourly-usd 0.89
uv run --extra qwen bench run --system ours --hourly-usd 0.89   # needs espeak-ng

uv run bench report                      # results/scores/<run>.json and results/scores/REPORT.md
uv run bench compare results/runs/ours results/runs/ours-mlx    # the same pipeline on two machines
```

No account or token is needed once the repository and dataset are public: `bench fetch` downloads
anonymously on purpose. Until launch they are private, and fetching needs `bench fetch --token` with
access to virgil-coach. `scripts/launch_check.sh` is the launch-day check: a fresh HOME with no
credentials, an anonymous clone and fetch, the tests, and the report rebuilt from the published runs.

`bench estimate --system elevenlabs` prints the audio hours and list-price cost of a full run
before you spend anything. Runs resume: passes already written are not sent again.
`pod/run.sh` is how we ran the local models on a rented GPU; `pod/mini_mlx.sh` how we ran `ours-mlx` on a Mac.

Each run writes `results/runs/<label>/run.json` (system configuration with model revisions and
API model names, benchmark and dataset version, manifest SHA-256, code revision, machine, OS,
GPU, exact commands and dates) and `passes.jsonl` (every pass: the text, the names sent, how the
list was fitted, latency).

## What is pinned

- Benchmark version `1.0.0` (code and data move together; a change to either is a new version).
- Dataset `virgil-coach/own-names-bench`, tag `v1.1.0` (`v1.0.0` keeps the first release): every audio file's SHA-256 is in
  `manifest.json`, and `bench` refuses to run on a changed file.
- The name lists, their order, the reference text and its normalization (`own_names_bench/text.py`,
  normalization version 1), the sampling seed (20261013).
- Model revisions (Hugging Face commit hashes) and API model names, in `run.json`.
- Python dependencies in `uv.lock`.

## Results (v1.1.0; runs of 2026-10-13, untaught passes rerun 2026-10-14)

Percent, with 95% intervals from a bootstrap over books (clips) or chapters. Clips: each book's own
name list, 1,107 mentions in 12 books. Chapters: 343 mentions in 8 chapters. Full tables, paired
differences, costs and every configuration: [results/scores/REPORT.md](results/scores/REPORT.md);
what changed from v1.0.0: [results/scores/CHANGES_v1.0_to_v1.1.md](results/scores/CHANGES_v1.0_to_v1.1.md).

| System (how it got the names) | Names right, clips | Untaught overwritten, clips | Name-free clips: listed name inserted | Ordinary-word error, clips | Names right, chapters |
| --- | --- | --- | --- | --- | --- |
| Ours, v0.3.0 `audio-text-note` + spotter (spelling + one recording per name) | 96.7 [94.9, 98.6] | 7.0 [2.3, 11.3] | 3.9 [0.5, 9.6] | 2.7 [2.4, 3.0] | 99.4 [98.6, 100.0] |
| ElevenLabs Scribe v2 (`keyterms`, all names) | 92.2 [87.6, 97.2] | 3.3 [1.1, 5.8] | 0.2 [0.0, 0.7] | 1.7 [1.4, 1.9] | 98.5 [95.2, 100.0] |
| Deepgram Nova-3 (`keyterm`; 85.8% of spoken names fit its limit) | 75.2 [62.0, 89.7] | 8.4 [5.7, 11.0] | 1.7 [0.5, 2.9] | 4.1 [3.1, 5.0] | 83.4 [76.1, 91.4] |
| Whisper large-v3 (prompt; 65.6% fit in 223 tokens) | 74.3 [63.7, 88.6] | 1.6 [0.2, 3.4] | 0.2 [0.0, 0.7] | 3.0 [2.4, 3.4] | 77.0 [54.5, 93.8] |
| Parakeet TDT 0.6B v2 (phrase boosting, weight picked on chapters) | 78.5 [72.3, 85.3] | 27.2 [15.9, 37.3] | 7.1 [4.2, 10.3] | 3.5 [2.9, 4.0] | 91.8 [87.5, 97.9] |
| Qwen3-ASR-1.7B (names as context) | 63.9 [54.6, 75.2] | 4.3 [1.6, 7.2] | 0.2 [0.0, 0.7] | 3.6 [2.6, 4.5] | 89.2 [85.4, 94.6] |
| Qwen3-ASR-1.7B (no list) | 41.8 [35.4, 47.5] | n/a | 0.0 | 4.3 [3.8, 4.8] | 22.2 [10.4, 37.6] |

Against ElevenLabs Scribe v2, same items (ours minus Scribe, points, clustered 95% interval):
names right on clips +4.4 [+0.5, +7.6], all of it from traditional names (+7.1 [+1.6, +10.5];
invented names +1.2 [−1.6, +4.1], no measurable difference); untaught names overwritten +3.7
[+1.0, +6.4] (worse); ordinary-word error +1.0 [+0.7, +1.3] (worse); name-free insertions +3.7
[0.0, +9.6] (not established either way); chapters, names right +0.9 [−1.3, +4.4] (no measurable
difference) and ordinary-word error +0.7 [+0.3, +1.3] (worse).

Ours on the shipping engine (Rust/MLX, Apple M5 Pro) agrees with the PyTorch reference (RTX 4090)
on the 6,550 passes both ran: names right 1,070 vs 1,070 (6 items each way), overwrites +0.3
[−0.2, +0.7]. Its v1.1.0 run is incomplete (the 65 corrected untaught passes and the 65
cross-reader passes were not rerun on the shared Mac), so it is left out of the result tables.
Whisper on an RTX 4090 and an A100 wrote identical text for 99.6% of passes.

Read with care: hosted services and Whisper likely know these classic texts (with no list at
all, ElevenLabs already writes 59.5% of the names right); Parakeet's boosting weight was picked on
the chapters task, so its chapter numbers are optimistic; Deepgram and Whisper received only part
of the longest lists.

Rebuild the report from the published runs: `uv run bench report $(sed -n 's/^# report-args: //p' results/scores/REPORT_ARGS)`.

## Data and licences

- Code: Apache 2.0, © 2026 Little Bear Labs, Inc. (`LICENSE`, `NOTICE`). The vendored Whisper
  normalizer is MIT (OpenAI).
- Audio: LibriVox recordings, public domain (US). Readers are credited in the dataset card.
- Text and names: from the public-domain Project Gutenberg texts of the same books.
- How the data was cut, and the contamination check against our own model's training data:
  `build/` and the dataset card.
