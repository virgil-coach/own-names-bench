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
| `parakeet` | NVIDIA Parakeet TDT 0.6B v2 | NeMo GPU phrase boosting |
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
`pod/run.sh` is how we ran the local models on a rented GPU; `pod/mac_mlx.sh` runs `ours-mlx`.

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

## Results

See [results/scores/REPORT.md](results/scores/REPORT.md) and the per-run JSON files next to it.

## Data and licences

- Code: Apache 2.0, © 2026 Little Bear Labs, Inc. (`LICENSE`, `NOTICE`). The vendored Whisper
  normalizer is MIT (OpenAI).
- Audio: LibriVox recordings, public domain (US). Readers are credited in the dataset card.
- Text and names: from the public-domain Project Gutenberg texts of the same books.
- How the data was cut, and the contamination check against our own model's training data:
  `build/` and the dataset card.
