# own-names-bench v1.2.0 → v1.3.0

## Data

- The v1.2.0 data is unchanged: the same `manifest.json` (SHA-256 `3025b1e5…`, dataset fingerprint `1625ef57df22bdba`)
  and the same suites. Every v1.2.0 run stays complete and scores exactly as it did.
- Two sealed test suites are added, each a dataset folder of its own, published byte for byte as they were sealed and
  scored (`bench --data <dataset>/books13 ...`):
  - `books13/`: held-out audiobooks (20 books, 20 readers, 1,100 mentions, 1,200 name-free clips). Suite hash
    `3d6d8b65d4810c4f9571e8274bf02659a1bb507e65c7d0c333a48145a41e202f`, manifest `e02be6a4…`, fingerprint
    `455a97ea15754481`.
  - `conv13/`: held-out conversation (VoxPopuli test, LibriTTS-R test; eight conditions, 2,327 mentions, 1,196 name-free
    pieces). Suite hash `dbff73e6e5785d0efcf36be582af061b63d59d351cd655ccb6e153ffa850fdd3` over `conv13/suites/`; the
    wrapper `conv13/manifest.json` (`48286d15…`, fingerprint `54d0fa007c55db72`) is the one the sealed runs were made with.
- The data format (a manifest's `version`) stays `1.2.0`: the code reads `DATA_FORMAT` and the benchmark is `1.3.0`.

## Code

- Scoring is unchanged: `score.py`, `match.py`, `text.py`, `align.py`, `stats.py`, `passes.py` and the normalizer are
  byte for byte v1.2.0's.
- `bench fetch` checks both sealed suites against their suite hashes; `scripts/verify_sealed.py` also checks the
  published sealed pass outputs against the SHA-256 recorded when they were scored and rebuilds their reports.
- `bench report`: a run made without the chapters task (run.json `chapters: false`, now recorded by `bench run`) is
  complete without them; a run marked `stale` is listed but left out of every table; the runs list shows each
  command's code revision and machine and any metadata correction; a list a run did not make says "not run".
- `build/merge_runs.py --local-paths`: fold shards whose configurations differ only in machine-local paths.
- `build/fix_run_meta.py`: the run metadata corrections below. `build/contamination_v13.py`: the contamination check
  against v7c's training data for every suite.

## Runs

- New: `ours-mlx-v7c` (v7c, the shipped path, on every v1.2.0 suite; the 2026-10-20 release-check passes folded into
  one run, no new inference; protocol look 16), `elevenlabs-2026-10-26` and `deepgram-2026-10-26` (hosted re-runs, see
  `HOSTED_RERUN_2026-10-26.md`), and the sealed runs `results/books13/` (v7c and ElevenLabs, 2026-10-27) and
  `results/conv13/` (v7c 2026-10-27; ElevenLabs 2026-10-16, reused), now with their pass outputs.
- `REPORT.md` has v7c as its baseline.
- Stale, left out of the tables: `elevenlabs` and `deepgram` (2026-10-13/14; superseded by the 2026-10-26 re-runs) and
  `ours-mlx-macmini`, each with commands run from uncommitted code (`-dirty`).
- Corrected (old values kept in each run.json's `metadata_fixes`): the dataset and benchmark version of `parakeet`,
  `qwen-context` and `whisper` (v1.2.0, not the version their first command ran on), the sealed runs' dataset (the
  published v1.3.0 folder, not the code's `@v1.2.0` constant); `ours` names the RTX PRO 6000 its suites ran on;
  `parakeet`'s speed line is marked not attributable to one machine.

## Headline

v1.2.0 compared our v0.3.0 adapter (PyTorch reference) with ElevenLabs and Deepgram as of 2026-10-13/14. v1.3.0 compares
v7c (v0.7.0, the Detail Keeper engine) with them: on the sealed suites first, on the v1.2.0 suites, and on the v1.2.0
audiobook clips only as a development set (v7c was selected on them).
