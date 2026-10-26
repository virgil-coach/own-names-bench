# Hosted re-run, 2026-10-26 (own-names-bench v1.2.0)

ElevenLabs Scribe v2 and Deepgram Nova-3 were run again on every v1.2.0 task, so that a launch claim
about them carries a fresh date (CLAIMS.md rule 9). The runs of 2026-10-13/14 stay as they were.

| | ElevenLabs | Deepgram |
| --- | --- | --- |
| New run | `results/runs/elevenlabs-2026-10-26` | `results/runs/deepgram-2026-10-26` |
| Old run | `results/runs/elevenlabs` (2026-10-13/14) | `results/runs/deepgram` (2026-10-13/14) |
| Configuration | `scribe_v2`, language `en`, temperature 0, seed 0, `keyterms` (at most 1,000; terms breaking a per-term rule dropped) | `nova-3`, language `en`, `smart_format`, `keyterm` (the longest prefix of the list, most frequent first, within 500 keyterm tokens) |
| Configuration fingerprint | unchanged from the old run | unchanged from the old run (`e5045cde16a03e6b`) |
| Passes | 16,260 of 16,260, 0 failed (none, own, all-books) | 13,694 of 13,694, 0 failed (none, own; its feature cannot take the all-books list) |
| Run on | 2026-10-26, 20:29–21:33 UTC, Apple M4 Max | 2026-10-26, 20:29–21:03 UTC, Apple M4 Max |
| Audio sent | 53.5 h | 46.1 h |
| Cost at list price (prices checked 2026-10-13) | $16.35 | $14.09 |

Both runs: code `644c960` (main, v1.2.0), dataset `virgil-coach/own-names-bench@v1.2.0` (dataset fingerprint
`1625ef57df22bdba` and suite fingerprints the same as the old runs; `manifest.json` SHA-256 `3025b1e5…`, identical
to the file at tag `v1.2.0` on Hugging Face; the old runs' `run.json` still carries the manifest hash
`a31da74c…` from when they were started on an earlier dataset release and migrated). Both are listed complete in `REPORT.md`.

## How to read this

Each row: the old rate and the new one, each with its 95% interval from a bootstrap over books (clips), chapters
or suite recordings; then the paired difference **new minus old** on the same items with the same clusters
(`own_names_bench.stats.paired_diff`, 10,000 resamples, seed 20261013), in points (per-minute rows in names per
minute). In brackets: items only the new run / only the old run got. **holds** marks a difference whose
interval excludes zero; everywhere else the result is "no measurable difference". A difference that holds but
rounds to zero is shown with two more decimals. Aggregates only: no per-clip output was read
(`own-names-bench-wt-v7crel/results/v07bench/PROTOCOL.md`, section 2).

Made by `uv run python build/rerun_compare.py results/scores <old> <new> <title>` from the score files that
`bench report` wrote (`results/scores/<run>.json`); its rates match `REPORT.md` row for row.

## Summary

- **Deepgram Nova-3: unchanged.** Every rate is within 0.3 points of the old run except chapters with no list
  (names right 14.9 → 14.0, −0.9 [−2.1, +0.0], no measurable difference). One difference holds: full-transcript
  error on chapters with no list, +0.018 points [+0.004, +0.036], a few words in 118 minutes.
- **ElevenLabs Scribe v2: no measurable difference on any with-list measure of names**, on clips (own or all-books
  list), chapters, or any suite. Differences that hold: with **no list**, it now writes more names right on clips
  (all names +1.0 [+0.2, +2.1]; invented +1.4 [+0.2, +2.9]); and on chapters with the book's list, ordinary-word
  error is slightly lower (−0.087 points [−0.183, −0.016]; full-transcript −0.078 [−0.178, −0.005]). The largest
  moves that do not hold: chapters with no list, names right 63.6 → 57.1 (−6.4 [−17.2, +4.7]); AMI insertions
  1 → 0 stretches (−0.8 [−2.5, +0.0]).
- **Our comparisons against them are unchanged.** `REPORT.md` now has columns for the new runs beside the old
  ones. Across all 102 paired "ours minus hosted" cells (audiobook tasks and suites), whether a difference holds
  is the same against the new run as against the old one, for both services.

So launch claims about either service can be dated "runs of 2026-10-26" and quoted from the `-2026-10-26`
columns of `REPORT.md`.

## Every task and metric

### ElevenLabs Scribe v2 (`scribe_v2`, keyterms)


**Clips, the book's own list**

| Metric | Old (elevenlabs) | New (elevenlabs-2026-10-26) | New − old (points; per-minute rows in names per minute) |
| --- | --- | --- | --- |
| Names right, invented | 96.6 [93.7, 98.6] | 96.8 [94.3, 98.6] | +0.2 [-0.7, +1.1] (3 vs 2) |
| Names right, traditional | 88.7 [83.4, 96.3] | 89.5 [84.8, 96.3] | +0.8 [-0.2, +1.5] (7 vs 2) |
| Names right, all | 92.2 [87.6, 97.2] | 92.8 [88.5, 97.2] | +0.5 [-0.2, +1.1] (10 vs 4) |
| Untaught overwritten | 3.3 [1.1, 5.8] | 2.9 [1.2, 4.8] | -0.5 [-1.0, +0.1] (3 vs 8) |
| Wrong name written | 1.8 [0.4, 3.0] | 1.4 [0.4, 2.2] | -0.5 [-0.9, +0.1] (1 vs 6) |
| Name-free: a listed name inserted | 0.2 [0.0, 0.7] | 0.2 [0.0, 0.7] | +0.0 [+0.0, +0.0] (0 vs 0) |
| Ordinary-word error | 1.7 [1.4, 1.9] | 1.7 [1.4, 1.9] | +0.0 [-0.1, +0.1] |
| Full-transcript error | 1.7 [1.4, 1.9] | 1.7 [1.3, 1.9] | -0.0 [-0.1, +0.0] |

**Clips, all-books list**

| Metric | Old (elevenlabs) | New (elevenlabs-2026-10-26) | New − old (points; per-minute rows in names per minute) |
| --- | --- | --- | --- |
| Names right, invented | 94.0 [90.4, 96.8] | 93.6 [90.8, 96.2] | -0.4 [-1.6, +0.9] (4 vs 6) |
| Names right, traditional | 86.8 [81.8, 94.3] | 86.8 [82.0, 93.9] | +0.0 [-1.1, +2.5] (7 vs 7) |
| Names right, all | 90.1 [86.0, 94.8] | 89.9 [85.9, 94.3] | -0.2 [-1.1, +1.1] (11 vs 13) |
| Untaught overwritten | 3.7 [1.6, 5.8] | 3.5 [1.5, 5.5] | -0.2 [-0.6, +0.2] (2 vs 4) |
| Wrong name written | 1.6 [0.5, 2.5] | 1.7 [0.5, 2.8] | +0.1 [-0.2, +0.4] (3 vs 2) |
| Name-free: a listed name inserted | 0.5 [0.0, 1.2] | 0.5 [0.0, 1.2] | +0.0 [+0.0, +0.0] (0 vs 0) |
| Ordinary-word error | 1.8 [1.5, 2.1] | 1.8 [1.5, 2.1] | -0.0 [-0.1, +0.1] |
| Full-transcript error | 1.8 [1.5, 2.1] | 1.8 [1.5, 2.1] | -0.0 [-0.1, +0.1] |

**Clips, no list**

| Metric | Old (elevenlabs) | New (elevenlabs-2026-10-26) | New − old (points; per-minute rows in names per minute) |
| --- | --- | --- | --- |
| Names right, invented | 56.1 [46.9, 64.5] | 57.5 [49.2, 65.2] | +1.4 [+0.2, +2.9] (20 vs 13) **holds** |
| Names right, traditional | 62.3 [53.5, 67.9] | 63.0 [55.9, 67.5] | +0.7 [-0.4, +2.4] (20 vs 16) |
| Names right, all | 59.5 [52.7, 64.5] | 60.5 [54.6, 64.8] | +1.0 [+0.2, +2.1] (40 vs 29) **holds** |
| Name-free: a book name inserted | 0.0 [0.0, 0.0] | 0.0 [0.0, 0.0] | +0.0 [+0.0, +0.0] (0 vs 0) |
| Ordinary-word error | 3.1 [2.7, 3.6] | 3.1 [2.7, 3.5] | -0.0 [-0.1, +0.0] |
| Full-transcript error | 3.1 [2.7, 3.5] | 3.1 [2.7, 3.4] | -0.0 [-0.1, +0.0] |

**Chapters, the book's list**

| Metric | Old (elevenlabs) | New (elevenlabs-2026-10-26) | New − old (points; per-minute rows in names per minute) |
| --- | --- | --- | --- |
| Names right | 98.5 [95.2, 100.0] | 97.4 [91.3, 100.0] | -1.2 [-3.9, +0.0] (0 vs 4) |
| Names right, same reader taught it | 98.2 [93.9, 100.0] | 96.8 [89.1, 100.0] | -1.4 [-4.9, +0.0] (0 vs 4) |
| Names right, another reader taught it | 100.0 [100.0, 100.0] | 100.0 [100.0, 100.0] | +0.0 [+0.0, +0.0] (0 vs 0) |
| Wrong names per minute | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] | +0.00 [+0.00, +0.00] |
| Ordinary-word error | 2.0 [1.1, 3.5] | 1.9 [1.0, 3.5] | -0.087 [-0.183, -0.016] **holds** |
| Full-transcript error | 2.0 [1.0, 3.5] | 1.9 [1.0, 3.4] | -0.078 [-0.178, -0.005] **holds** |

**Chapters, half the names removed**

| Metric | Old (elevenlabs) | New (elevenlabs-2026-10-26) | New − old (points; per-minute rows in names per minute) |
| --- | --- | --- | --- |
| Names right | 95.9 [86.3, 100.0] | 98.3 [94.1, 100.0] | +2.3 [+0.0, +7.8] (4 vs 0) |
| Names right, same reader taught it | 94.9 [82.9, 100.0] | 97.8 [92.7, 100.0] | +2.9 [+0.0, +9.8] (4 vs 0) |
| Names right, another reader taught it | 100.0 [100.0, 100.0] | 100.0 [100.0, 100.0] | +0.0 [+0.0, +0.0] (0 vs 0) |
| Untaught overwritten | 1.8 [0.0, 3.4] | 1.8 [0.0, 3.4] | +0.0 [+0.0, +0.0] (0 vs 0) |
| Wrong names per minute | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] | +0.00 [+0.00, +0.00] |
| Ordinary-word error | 2.5 [1.3, 4.5] | 2.5 [1.2, 4.5] | -0.0 [-0.2, +0.2] |
| Full-transcript error | 2.5 [1.3, 4.5] | 2.5 [1.2, 4.5] | +0.0 [-0.2, +0.3] |

**Chapters, no list**

| Metric | Old (elevenlabs) | New (elevenlabs-2026-10-26) | New − old (points; per-minute rows in names per minute) |
| --- | --- | --- | --- |
| Names right | 63.6 [30.6, 85.5] | 57.1 [26.8, 80.0] | -6.4 [-17.2, +4.7] (12 vs 34) |
| Names right, same reader taught it | 65.0 [26.7, 87.4] | 57.2 [24.4, 81.3] | -7.8 [-21.0, +6.7] (12 vs 34) |
| Names right, another reader taught it | 56.7 [0.0, 100.0] | 56.7 [0.0, 100.0] | +0.0 [+0.0, +0.0] (0 vs 0) |
| Wrong names per minute | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] | +0.00 [+0.00, +0.00] |
| Ordinary-word error | 2.8 [1.5, 4.7] | 3.0 [1.8, 4.9] | +0.2 [-0.1, +0.6] |
| Full-transcript error | 2.8 [1.6, 4.7] | 3.0 [1.8, 4.9] | +0.2 [-0.1, +0.6] |

**Suite calls**

| Metric | Old (elevenlabs) | New (elevenlabs-2026-10-26) | New − old (points; per-minute rows in names per minute) |
| --- | --- | --- | --- |
| Names right | 95.5 [93.5, 97.2] | 95.3 [93.3, 97.0] | -0.1 [-0.9, +0.6] (3 vs 4) |
| Names right: taught by the other speaker | 96.6 [94.1, 98.6] | 96.6 [94.3, 98.4] | +0.0 [-1.1, +1.0] (2 vs 2) |
| Names right: taught by the same speaker | 94.1 [90.9, 96.8] | 93.8 [90.5, 96.6] | -0.3 [-1.5, +0.7] (1 vs 2) |
| Untaught overwritten | 1.6 [0.5, 2.9] | 1.6 [0.5, 3.0] | +0.0 [-0.6, +0.8] (2 vs 2) |
| Wrong name written | 1.0 [0.3, 1.8] | 0.7 [0.1, 1.4] | -0.3 [-0.7, +0.0] (0 vs 2) |
| Name-free: items with a listed name inserted | 1.7 [0.7, 2.9] | 1.4 [0.5, 2.6] | -0.2 [-0.7, +0.0] (0 vs 1) |
| Listed names inserted per minute | 0.02 [0.01, 0.03] | 0.02 [0.01, 0.03] | -0.00 [-0.01, +0.00] |
| Name-free: items with a name from another recording | 0.0 [0.0, 0.0] | 0.0 [0.0, 0.0] | +0.0 [+0.0, +0.0] (0 vs 0) |
| Names from other recordings inserted per minute | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] | +0.00 [+0.00, +0.00] |
| Ordinary-word error | 9.1 [8.4, 9.9] | 9.1 [8.4, 9.9] | -0.1 [-0.2, +0.0] |
| Full-transcript error | 9.1 [8.4, 9.9] | 9.0 [8.3, 9.8] | -0.1 [-0.2, +0.0] |
| Names right, no list | 83.9 [79.7, 87.4] | 83.7 [79.7, 87.2] | -0.1 [-1.0, +0.8] (5 vs 6) |
| No list: name-free items with a name inserted | 0.7 [0.0, 1.7] | 0.7 [0.0, 1.7] | +0.0 [+0.0, +0.0] (0 vs 0) |
| No list: ordinary-word error | 9.2 [8.5, 10.0] | 9.2 [8.5, 10.0] | -0.0 [-0.1, +0.1] |

**Suite svq**

| Metric | Old (elevenlabs) | New (elevenlabs-2026-10-26) | New − old (points; per-minute rows in names per minute) |
| --- | --- | --- | --- |
| Names right | 98.6 [97.7, 99.3] | 98.5 [97.6, 99.2] | -0.1 [-0.4, +0.3] (3 vs 4) |
| Names right: background_speech | 97.7 [96.1, 99.2] | 97.7 [96.1, 99.2] | +0.0 [-1.1, +1.1] (2 vs 2) |
| Names right: clean | 99.4 [98.6, 100.0] | 99.2 [98.0, 100.0] | -0.3 [-0.9, +0.0] (0 vs 1) |
| Names right: media_noise | 99.2 [98.1, 100.0] | 99.4 [98.6, 100.0] | +0.3 [+0.0, +0.9] (1 vs 0) |
| Names right: traffic_noise | 98.0 [96.4, 99.4] | 97.7 [96.0, 99.2] | -0.3 [-0.9, +0.0] (0 vs 1) |
| Untaught overwritten | 0.6 [0.1, 1.3] | 0.6 [0.1, 1.3] | -0.1 [-0.2, +0.0] (0 vs 1) |
| Wrong name written | 0.2 [0.0, 0.5] | 0.3 [0.1, 0.6] | +0.1 [+0.0, +0.2] (1 vs 0) |
| Name-free: items with a listed name inserted | 0.6 [0.0, 1.6] | 0.9 [0.0, 2.2] | +0.3 [+0.0, +0.9] (1 vs 0) |
| Listed names inserted per minute | 0.08 [0.00, 0.21] | 0.12 [0.00, 0.28] | +0.04 [+0.00, +0.13] |
| Name-free: items with a name from another recording | 0.6 [0.0, 1.6] | 0.9 [0.0, 2.2] | +0.3 [+0.0, +0.9] (1 vs 0) |
| Names from other recordings inserted per minute | 0.08 [0.00, 0.21] | 0.12 [0.00, 0.28] | +0.04 [+0.00, +0.13] |
| Ordinary-word error | 14.5 [12.2, 17.0] | 13.8 [11.7, 16.2] | -0.7 [-1.9, +0.4] |
| Full-transcript error | 12.5 [10.5, 14.6] | 11.9 [10.1, 14.0] | -0.6 [-1.6, +0.4] |
| Names right, no list | 83.5 [80.4, 86.5] | 83.7 [80.5, 86.7] | +0.1 [-0.6, +0.8] (17 vs 15) |
| No list: name-free items with a name inserted | 0.0 [0.0, 0.0] | 0.0 [0.0, 0.0] | +0.0 [+0.0, +0.0] (0 vs 0) |
| No list: ordinary-word error | 19.2 [16.9, 21.8] | 19.1 [16.7, 21.8] | -0.1 [-1.1, +1.0] |

**Suite ami**

| Metric | Old (elevenlabs) | New (elevenlabs-2026-10-26) | New − old (points; per-minute rows in names per minute) |
| --- | --- | --- | --- |
| Name-free: items with a listed name inserted | 0.8 [0.0, 2.5] | 0.0 [0.0, 0.0] | -0.8 [-2.5, +0.0] (0 vs 1) |
| Listed names inserted per minute | 0.02 [0.00, 0.05] | 0.00 [0.00, 0.00] | -0.02 [-0.05, +0.00] |
| Name-free: items with a name from another recording | 0.8 [0.0, 2.5] | 0.0 [0.0, 0.0] | -0.8 [-2.5, +0.0] (0 vs 1) |
| Names from other recordings inserted per minute | 0.02 [0.00, 0.05] | 0.00 [0.00, 0.00] | -0.02 [-0.05, +0.00] |
| Ordinary-word error | 16.7 [14.9, 18.2] | 16.7 [15.0, 18.2] | +0.0 [-0.3, +0.4] |
| Full-transcript error | 16.7 [14.9, 18.3] | 16.8 [15.0, 18.3] | +0.1 [-0.3, +0.4] |
| No list: name-free items with a name inserted | 0.0 [0.0, 0.0] | 0.0 [0.0, 0.0] | +0.0 [+0.0, +0.0] (0 vs 0) |
| No list: ordinary-word error | 16.6 [15.0, 18.1] | 16.9 [15.1, 18.1] | +0.3 [-0.1, +0.7] |

**Suite modulate**

| Metric | Old (elevenlabs) | New (elevenlabs-2026-10-26) | New − old (points; per-minute rows in names per minute) |
| --- | --- | --- | --- |
| Names right | 93.0 [88.6, 96.3] | 93.1 [89.3, 96.2] | +0.1 [-0.9, +1.3] (7 vs 6) |
| Untaught overwritten | 0.3 [0.0, 0.8] | 0.3 [0.0, 0.8] | +0.0 [+0.0, +0.0] (0 vs 0) |
| Wrong name written | 0.3 [0.0, 0.8] | 0.1 [0.0, 0.6] | -0.1 [-0.5, +0.0] (0 vs 1) |
| Ordinary-word error | 11.6 [9.7, 14.4] | 11.6 [9.6, 14.5] | +0.0 [-0.1, +0.3] |
| Full-transcript error | 11.1 [9.3, 13.8] | 11.2 [9.2, 13.9] | +0.0 [-0.1, +0.3] |
| Names right, no list | 83.1 [69.1, 91.2] | 83.3 [69.7, 91.4] | +0.3 [+0.0, +0.8] (4 vs 2) |
| No list: ordinary-word error | 12.6 [10.3, 16.0] | 12.7 [10.4, 16.0] | +0.1 [-0.0, +0.3] |

Differences that hold: Clips, no list: Names right, invented +1.4 [+0.2, +2.9] (20 vs 13) **holds**; Clips, no list: Names right, all +1.0 [+0.2, +2.1] (40 vs 29) **holds**; Chapters, the book's list: Ordinary-word error -0.087 [-0.183, -0.016] **holds**; Chapters, the book's list: Full-transcript error -0.078 [-0.178, -0.005] **holds**.


### Deepgram Nova-3 (`nova-3`, keyterm)


**Clips, the book's own list**

| Metric | Old (deepgram) | New (deepgram-2026-10-26) | New − old (points; per-minute rows in names per minute) |
| --- | --- | --- | --- |
| Names right, invented | 92.2 [89.2, 95.4] | 92.0 [89.0, 95.1] | -0.2 [-0.7, +0.0] (0 vs 1) |
| Names right, traditional | 61.3 [47.2, 78.6] | 61.2 [47.2, 78.4] | -0.2 [-0.6, +0.0] (0 vs 1) |
| Names right, all | 75.2 [62.0, 89.7] | 75.1 [61.8, 89.5] | -0.2 [-0.5, +0.0] (0 vs 2) |
| Untaught overwritten | 8.4 [5.7, 11.0] | 8.5 [5.9, 11.1] | +0.1 [+0.0, +0.3] (1 vs 0) |
| Wrong name written | 3.1 [1.0, 5.3] | 3.1 [1.0, 5.3] | +0.0 [+0.0, +0.0] (0 vs 0) |
| Name-free: a listed name inserted | 1.7 [0.5, 2.9] | 1.7 [0.5, 2.9] | +0.0 [+0.0, +0.0] (0 vs 0) |
| Ordinary-word error | 4.1 [3.1, 5.0] | 4.2 [3.1, 5.1] | +0.1 [-0.0, +0.2] |
| Full-transcript error | 4.1 [3.1, 5.0] | 4.2 [3.1, 5.2] | +0.1 [-0.0, +0.2] |

**Clips, no list**

| Metric | Old (deepgram) | New (deepgram-2026-10-26) | New − old (points; per-minute rows in names per minute) |
| --- | --- | --- | --- |
| Names right, invented | 28.1 [22.7, 33.0] | 27.9 [22.7, 32.7] | -0.2 [-0.5, +0.0] (0 vs 1) |
| Names right, traditional | 24.3 [20.5, 28.0] | 24.3 [20.5, 28.0] | +0.0 [+0.0, +0.0] (0 vs 0) |
| Names right, all | 26.0 [23.0, 29.8] | 25.9 [23.0, 29.6] | -0.1 [-0.3, +0.0] (0 vs 1) |
| Name-free: a book name inserted | 0.0 [0.0, 0.0] | 0.0 [0.0, 0.0] | +0.0 [+0.0, +0.0] (0 vs 0) |
| Ordinary-word error | 6.0 [5.2, 6.6] | 6.0 [5.2, 6.6] | -0.0 [-0.0, +0.0] |
| Full-transcript error | 5.9 [5.2, 6.5] | 5.9 [5.2, 6.5] | +0.0 [-0.0, +0.0] |

**Chapters, the book's list**

| Metric | Old (deepgram) | New (deepgram-2026-10-26) | New − old (points; per-minute rows in names per minute) |
| --- | --- | --- | --- |
| Names right | 83.4 [76.1, 91.4] | 83.4 [76.1, 91.4] | +0.0 [+0.0, +0.0] (0 vs 0) |
| Names right, same reader taught it | 80.2 [72.0, 87.2] | 80.2 [72.0, 87.2] | +0.0 [+0.0, +0.0] (0 vs 0) |
| Names right, another reader taught it | 98.3 [96.2, 100.0] | 98.3 [96.2, 100.0] | +0.0 [+0.0, +0.0] (0 vs 0) |
| Wrong names per minute | 0.04 [0.00, 0.10] | 0.04 [0.00, 0.10] | +0.00 [+0.00, +0.00] |
| Ordinary-word error | 3.2 [2.2, 4.7] | 3.2 [2.2, 4.7] | +0.0 [+0.0, +0.0] |
| Full-transcript error | 3.2 [2.2, 4.7] | 3.2 [2.2, 4.7] | +0.0 [+0.0, +0.0] |

**Chapters, half the names removed**

| Metric | Old (deepgram) | New (deepgram-2026-10-26) | New − old (points; per-minute rows in names per minute) |
| --- | --- | --- | --- |
| Names right | 83.1 [62.8, 96.0] | 83.1 [62.8, 96.0] | +0.0 [+0.0, +0.0] (0 vs 0) |
| Names right, same reader taught it | 79.0 [54.0, 94.0] | 79.0 [54.0, 94.0] | +0.0 [+0.0, +0.0] (0 vs 0) |
| Names right, another reader taught it | 100.0 [100.0, 100.0] | 100.0 [100.0, 100.0] | +0.0 [+0.0, +0.0] (0 vs 0) |
| Untaught overwritten | 5.3 [0.6, 10.0] | 5.3 [0.6, 10.0] | +0.0 [+0.0, +0.0] (0 vs 0) |
| Wrong names per minute | 0.07 [0.01, 0.17] | 0.07 [0.01, 0.17] | +0.00 [+0.00, +0.00] |
| Ordinary-word error | 4.0 [2.6, 5.8] | 4.0 [2.7, 5.8] | -0.0 [-0.0, +0.0] |
| Full-transcript error | 4.2 [2.8, 6.0] | 4.2 [2.8, 6.0] | -0.0 [-0.0, +0.0] |

**Chapters, no list**

| Metric | Old (deepgram) | New (deepgram-2026-10-26) | New − old (points; per-minute rows in names per minute) |
| --- | --- | --- | --- |
| Names right | 14.9 [6.6, 23.7] | 14.0 [6.3, 21.8] | -0.9 [-2.1, +0.0] (0 vs 3) |
| Names right, same reader taught it | 14.8 [5.3, 25.7] | 13.8 [4.7, 23.3] | -1.1 [-2.6, +0.0] (0 vs 3) |
| Names right, another reader taught it | 15.0 [0.0, 100.0] | 15.0 [0.0, 100.0] | +0.0 [+0.0, +0.0] (0 vs 0) |
| Wrong names per minute | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] | +0.00 [+0.00, +0.00] |
| Ordinary-word error | 4.8 [3.2, 7.0] | 4.8 [3.2, 7.0] | +0.0 [+0.0, +0.0] |
| Full-transcript error | 5.0 [3.4, 7.1] | 5.0 [3.4, 7.1] | +0.018 [+0.004, +0.036] **holds** |

**Suite calls**

| Metric | Old (deepgram) | New (deepgram-2026-10-26) | New − old (points; per-minute rows in names per minute) |
| --- | --- | --- | --- |
| Names right | 91.9 [89.5, 94.2] | 91.9 [89.5, 94.2] | +0.0 [-0.4, +0.4] (1 vs 1) |
| Names right: taught by the other speaker | 92.2 [88.9, 95.0] | 92.4 [89.1, 95.2] | +0.3 [+0.0, +0.9] (1 vs 0) |
| Names right: taught by the same speaker | 91.6 [87.8, 95.2] | 91.3 [87.4, 94.8] | -0.3 [-1.1, +0.0] (0 vs 1) |
| Untaught overwritten | 1.6 [0.6, 2.8] | 1.7 [0.7, 3.0] | +0.1 [+0.0, +0.5] (1 vs 0) |
| Wrong name written | 0.8 [0.2, 1.7] | 0.8 [0.2, 1.7] | +0.0 [+0.0, +0.0] (0 vs 0) |
| Name-free: items with a listed name inserted | 1.2 [0.2, 2.4] | 1.2 [0.2, 2.4] | +0.0 [+0.0, +0.0] (0 vs 0) |
| Listed names inserted per minute | 0.01 [0.00, 0.03] | 0.01 [0.00, 0.03] | +0.00 [+0.00, +0.00] |
| Name-free: items with a name from another recording | 0.2 [0.0, 0.7] | 0.2 [0.0, 0.7] | +0.0 [+0.0, +0.0] (0 vs 0) |
| Names from other recordings inserted per minute | 0.00 [0.00, 0.01] | 0.00 [0.00, 0.01] | +0.00 [+0.00, +0.00] |
| Ordinary-word error | 10.1 [9.4, 11.0] | 10.2 [9.4, 11.0] | +0.0 [-0.0, +0.0] |
| Full-transcript error | 10.1 [9.3, 10.9] | 10.1 [9.3, 11.0] | +0.0 [-0.0, +0.0] |
| Names right, no list | 75.9 [71.0, 80.7] | 76.2 [71.3, 80.9] | +0.3 [+0.0, +0.7] (2 vs 0) |
| No list: name-free items with a name inserted | 0.5 [0.0, 1.2] | 0.5 [0.0, 1.2] | +0.0 [+0.0, +0.0] (0 vs 0) |
| No list: ordinary-word error | 10.4 [9.6, 11.3] | 10.6 [9.7, 11.5] | +0.2 [-0.0, +0.5] |

**Suite svq**

| Metric | Old (deepgram) | New (deepgram-2026-10-26) | New − old (points; per-minute rows in names per minute) |
| --- | --- | --- | --- |
| Names right | 89.4 [87.2, 91.4] | 89.4 [87.2, 91.5] | +0.1 [-0.1, +0.3] (2 vs 1) |
| Names right: background_speech | 89.0 [85.5, 92.3] | 89.3 [85.8, 92.5] | +0.3 [+0.0, +0.9] (1 vs 0) |
| Names right: clean | 93.0 [89.9, 95.7] | 93.0 [89.9, 95.7] | +0.0 [+0.0, +0.0] (0 vs 0) |
| Names right: media_noise | 93.5 [90.8, 96.0] | 93.2 [90.5, 95.8] | -0.3 [-0.9, +0.0] (0 vs 1) |
| Names right: traffic_noise | 82.0 [77.6, 86.2] | 82.3 [77.8, 86.4] | +0.3 [+0.0, +0.9] (1 vs 0) |
| Untaught overwritten | 1.3 [0.7, 2.1] | 1.5 [0.8, 2.3] | +0.1 [+0.0, +0.4] (2 vs 0) |
| Wrong name written | 0.6 [0.2, 1.0] | 0.5 [0.1, 0.9] | -0.1 [-0.2, +0.0] (0 vs 1) |
| Name-free: items with a listed name inserted | 0.0 [0.0, 0.0] | 0.0 [0.0, 0.0] | +0.0 [+0.0, +0.0] (0 vs 0) |
| Listed names inserted per minute | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] | +0.00 [+0.00, +0.00] |
| Name-free: items with a name from another recording | 0.0 [0.0, 0.0] | 0.0 [0.0, 0.0] | +0.0 [+0.0, +0.0] (0 vs 0) |
| Names from other recordings inserted per minute | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] | +0.00 [+0.00, +0.00] |
| Ordinary-word error | 17.4 [15.5, 19.3] | 17.3 [15.5, 19.3] | -0.0 [-0.2, +0.1] |
| Full-transcript error | 15.2 [13.6, 16.9] | 15.2 [13.6, 16.9] | -0.0 [-0.2, +0.1] |
| Names right, no list | 65.9 [61.9, 69.8] | 66.1 [62.0, 69.9] | +0.1 [-0.3, +0.6] (6 vs 4) |
| No list: name-free items with a name inserted | 0.0 [0.0, 0.0] | 0.0 [0.0, 0.0] | +0.0 [+0.0, +0.0] (0 vs 0) |
| No list: ordinary-word error | 22.3 [20.3, 24.6] | 22.4 [20.3, 24.7] | +0.1 [-0.2, +0.3] |

**Suite ami**

| Metric | Old (deepgram) | New (deepgram-2026-10-26) | New − old (points; per-minute rows in names per minute) |
| --- | --- | --- | --- |
| Name-free: items with a listed name inserted | 0.0 [0.0, 0.0] | 0.0 [0.0, 0.0] | +0.0 [+0.0, +0.0] (0 vs 0) |
| Listed names inserted per minute | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] | +0.00 [+0.00, +0.00] |
| Name-free: items with a name from another recording | 0.0 [0.0, 0.0] | 0.0 [0.0, 0.0] | +0.0 [+0.0, +0.0] (0 vs 0) |
| Names from other recordings inserted per minute | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] | +0.00 [+0.00, +0.00] |
| Ordinary-word error | 19.1 [17.6, 20.9] | 19.0 [17.5, 20.9] | -0.1 [-0.3, +0.0] |
| Full-transcript error | 19.2 [17.6, 20.9] | 19.1 [17.5, 20.9] | -0.1 [-0.3, +0.0] |
| No list: name-free items with a name inserted | 0.0 [0.0, 0.0] | 0.0 [0.0, 0.0] | +0.0 [+0.0, +0.0] (0 vs 0) |
| No list: ordinary-word error | 19.1 [17.6, 20.8] | 19.1 [17.6, 20.8] | -0.0 [-0.1, +0.1] |

**Suite modulate**

| Metric | Old (deepgram) | New (deepgram-2026-10-26) | New − old (points; per-minute rows in names per minute) |
| --- | --- | --- | --- |
| Names right | 85.2 [79.3, 89.9] | 84.9 [79.1, 89.6] | -0.3 [-1.0, +0.2] (1 vs 3) |
| Untaught overwritten | 1.5 [0.5, 3.3] | 1.5 [0.5, 3.3] | +0.0 [+0.0, +0.0] (0 vs 0) |
| Wrong name written | 0.7 [0.0, 1.8] | 0.7 [0.0, 1.8] | +0.0 [+0.0, +0.0] (0 vs 0) |
| Ordinary-word error | 14.1 [11.6, 17.5] | 14.0 [11.5, 17.5] | -0.0 [-0.1, +0.1] |
| Full-transcript error | 13.8 [11.4, 17.3] | 13.8 [11.4, 17.3] | -0.0 [-0.1, +0.1] |
| Names right, no list | 77.7 [62.5, 87.2] | 77.7 [62.5, 87.1] | +0.0 [-0.7, +0.8] (2 vs 2) |
| No list: ordinary-word error | 14.7 [11.9, 18.6] | 14.6 [11.8, 18.4] | -0.1 [-0.3, +0.0] |

Differences that hold: Chapters, no list: Full-transcript error +0.018 [+0.004, +0.036] **holds**.

