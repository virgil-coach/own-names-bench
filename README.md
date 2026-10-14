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
| **Latency, cost** | Per-request latency and real-time factor on the recorded machine; list price per audio hour (with the date checked) for hosted services, measured real-time factor × machine price for local models. |

Two tasks:

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

Every number comes with a 95% interval (Wilson for shares of items; bootstrap over books or
chapters for word error and rates per minute), and systems are compared **paired, on the same
items** (bootstrap interval of the difference, exact McNemar test).

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
uv run bench fetch                       # the pinned dataset (virgil-coach/own-names-bench@v1.0.0), checked file by file
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

`bench estimate --system elevenlabs` prints the audio hours and list-price cost of a full run
before you spend anything. Runs resume: passes already written are not sent again.
`pod/run.sh` is how we ran the local models on a rented GPU; `pod/mini_mlx.sh` how we ran `ours-mlx` on a Mac.

Each run writes `results/runs/<label>/run.json` (system configuration with model revisions and
API model names, benchmark and dataset version, manifest SHA-256, code revision, machine, OS,
GPU, exact commands and dates) and `passes.jsonl` (every pass: the text, the names sent, how the
list was fitted, latency).

## What is pinned

- Benchmark version `1.0.0` (code and data move together; a change to either is a new version).
- Dataset `virgil-coach/own-names-bench`, tag `v1.0.0`: every audio file's SHA-256 is in
  `manifest.json`, and `bench` refuses to run on a changed file.
- The name lists, their order, the reference text and its normalization (`own_names_bench/text.py`,
  normalization version 1), the sampling seed (20261013).
- Model revisions (Hugging Face commit hashes) and API model names, in `run.json`.
- Python dependencies in `uv.lock`.

## Results (v1.0.0, runs of 2026-10-13)

Clips with each book's own name list (1,107 mentions, 12 books) and continuous chapters (343
mentions, 8 chapters). Percent, 95% interval. Full tables, paired comparisons, speed, cost and
every configuration: [results/scores/REPORT.md](results/scores/REPORT.md).

| System (how it got the names) | Names right, clips | Untaught overwritten, clips | Name-free clips, a listed name inserted | Ordinary-word error, clips | Names right, chapters | Untaught overwritten, chapters |
| --- | --- | --- | --- | --- | --- | --- |
| Ours, v0.3.0 `audio-text-note` + spotter (spelling + one recording per name) | 96.7 [95.4, 97.6] | 7.0 [5.7, 8.7] | 3.9 [2.4, 6.3] | 2.7 [2.4, 3.0] | 99.4 [97.9, 99.8] | 1.8 [0.6, 5.0] |
| ElevenLabs Scribe v2 (`keyterms`, all names) | 92.2 [90.5, 93.7] | 3.3 [2.4, 4.6] | 0.2 [0.0, 1.4] | 1.7 [1.4, 1.9] | 98.5 [96.6, 99.4] | 1.8 [0.6, 5.0] |
| Deepgram Nova-3 (`keyterm`, as many as its 500-token limit takes) | 75.2 [72.6, 77.7] | 8.2 [6.7, 10.0] | 1.7 [0.8, 3.5] | 4.1 [3.1, 5.0] | 83.4 [79.1, 86.9] | 5.3 [2.8, 9.7] |
| Whisper large-v3 (prompt, 223 tokens) | 74.3 [71.7, 76.8] | 1.6 [1.0, 2.6] | 0.2 [0.0, 1.4] | 3.0 [2.4, 3.4] | 77.0 [72.2, 81.1] | 1.8 [0.6, 5.0] |
| Parakeet TDT 0.6B v2 (GPU phrase boosting) | 78.5 [76.0, 80.8] | 27.2 [24.7, 29.9] | 7.1 [5.0, 10.0] | 3.5 [2.9, 4.0] | 91.8 [88.5, 94.3] | 4.7 [2.4, 9.0] |
| Qwen3-ASR-1.7B (names as context) | 63.9 [61.0, 66.6] | 4.3 [3.3, 5.7] | 0.2 [0.0, 1.4] | 3.6 [2.6, 4.5] | 89.2 [85.5, 92.1] | 2.9 [1.3, 6.7] |
| Qwen3-ASR-1.7B (no list) | 41.8 [39.0, 44.8] | n/a | 0.0 [0.0, 0.9] | 4.3 [3.8, 4.8] | 22.7 [18.6, 27.5] | n/a |

Ours on the shipping engine (Rust/MLX, Apple M5 Pro) agrees with the PyTorch reference (RTX 4090)
within noise: names right 96.7 vs 96.7 (6 items each way), untaught overwritten 6.8 vs 7.0.
Whisper on an RTX 4090 and an A100 wrote identical text for 99.6% of passes.

Notes that matter for reading the table: hosted services and Whisper likely know these classic
texts (with no list at all, ElevenLabs already writes 59.5% of the names right); Parakeet's boosting
weight was picked on the chapters task (NeMo gives no default), so its chapter numbers are
optimistic; Deepgram and Whisper could only take part of the longest lists (85.8% and 65.6% of
spoken names were among the names they received).

Rebuild the report from the published runs:

```bash
uv run bench report --baseline ours-rtx4090 \
  --only ours-rtx4090 ours-mlx-macmini elevenlabs deepgram whisper-rtx4090 parakeet-a100 qwen-rtx4090 qwen-context-rtx4090 \
  --pair ours-rtx4090 ours-mlx-macmini --pair whisper-rtx4090 whisper-a100
```

## Data and licences

- Code: Apache 2.0, © 2026 Little Bear Labs, Inc. (`LICENSE`, `NOTICE`). The vendored Whisper
  normalizer is MIT (OpenAI).
- Audio: LibriVox recordings, public domain (US). Readers are credited in the dataset card.
- Text and names: from the public-domain Project Gutenberg texts of the same books.
- How the data was cut, and the contamination check against our own model's training data:
  `build/` and the dataset card.
