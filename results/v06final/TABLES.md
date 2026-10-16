# own-names v0.6 finalist: the one benchmark run (lore-poc ctxft/v06_amendment4_c3.md)

> **Amendment 4 (C3 relaxed to "not worse") was made after seeing the dev results.** The dev rule's C3 was loosened
> from "conv dev word error <= v0.3.0 - 0.5" to "<= v0.3.0 + 0.1" once every v0.6 arm had failed it; v6j was chosen
> under the amended rule. Nothing below was seen by any v0.6, guard or re-read work before this run; every system
> was run once, and no number here changed any setting. Every figure that depends on choosing v6j depends on that
> amendment.

**Verdict: the finalist (v6j + name guard + re-read) does not ship.** On own-names-bench v1.2.0 it fails S1 (calls
names right 94.5 vs ElevenLabs 95.5), S2 (svq 95.0 vs 98.6), S3 (modulate 91.7 vs 93.0), S4 (AMI word error 17.2 vs
16.7), S5's second clause (books names right 94.9, bar >= 95.4 = v0.3.0 + fixes - 1.0), N3 on svq (word error 8.55, bar
<= 7.47) and F1 on calls (7/417 = 1.68%) and books (14/408 = 3.43%). It passes N1, N2, S5's first clause and F1 on
svq (0/320) and AMI (0/119). v0.3.0 + guard + re-read does not ship either (fails S2, S3, S4, F1 calls 9/417, F1 books
17/408).

What the finalist does well, for the record (not a ship criterion): fewer untaught names overwritten than v0.3.0 +
fixes on every suite with them except modulate (v1.2.0 calls 11 vs 24 of 706, books 52 vs 75 of 1107), no AMI or svq
false insertions, and on the sealed v1.3 conversation suite 89.9% names right pooled (2091/2327) vs v0.3.0 + fixes
85.2% (1982/2327) and ElevenLabs 91.9% (2139/2327), with 4/1196 (0.33%) name-free insertions vs ElevenLabs 29/1196
(2.42%) and v0.3.0 + fixes 2/1196 (0.17%). Its gains are concentrated in short (86.0 vs 61.0) and level (77.7 vs 72.0)
clips; ElevenLabs stays ahead on far and level.

## What was run

| System | Code | Where |
| --- | --- | --- |
| finalist: v6j + guard + re-read (`ours-reread`, OURS_ADAPTER=v6j, SHA-256 f4f39c56…706d checked on every pod) | own-names-bench `v06/final` 42f2dc1 (system), pod script 9b4eee2 (c13a's v6j shards: fbf8a8a, same system code) | RunPod RTX PRO 6000, EUR-IS-1 |
| v0.3.0 + guard + re-read (`ours-reread`) | same | same |
| v0.3.0 + fixes (`ours-fixed`): v1.2.0 = the published run (results/diag/ours-fixed--*), conv13 = run here once | fix/v12-pipeline / v06/final | same |
| ElevenLabs Scribe v2, keyterms (`elevenlabs`, cloud.py): v1.2.0 = the published run, conv13 = run here once from this Mac | v06/final b086d92 (`--no-sample-files`: plumbing, see below) | api.elevenlabs.io |

- v1.2.0: the 16 shards of the ours-fixed run (podin/fx-*), none + own + own-minus, audiobook clips, no chapters;
  data manifest 3025b1e5… (the ours-fixed run's) verified file by file on each pod. Every expected pass is scored.
- Sealed v1.3 conversation suite: copied from the volume to each pod, suite hash recomputed from the copy and from
  the volume's SHA256SUMS: **dbff73e6e5785d0efcf36be582af061b63d59d351cd655ccb6e153ffa850fdd3** (match); 9,373 passes per
  system, every one scored. ElevenLabs ran on a clips-only tar of that verified copy (SHA-256 708c17d9… checked after
  transfer; every one of 3,523 clips matched its suite.json SHA-256).
- Ship rule and F1 are on v1.2.0 only (amendment 4); conv13 is reported.
- Re-read and guard firing (from the passes' window traces): v1.2.0 finalist 3,331 windows re-read of 27,378 (3,317
  answers used), guard fired 11 times; v0.3.0 + guard + re-read 3,331 re-read, guard 0. conv13: finalist 1,351 re-read,
  guard 29; v0.3.0 0. Every conv13 short clip is one window, so it is never re-read (the engine's rule: a re-read
  needs a neighbour), which is why v0.3.0 + guard + re-read equals v0.3.0 + fixes on conv13-short.

Plumbing fixed during the run (no setting changed): the pod script set HF_HUB_OFFLINE, which stops peft loading the
v0.3.0 hub adapter (the 8 failed shards had written no pass and were re-run on another pod); the v6j adapter was read
from the volume after gpu-cli's sync of it failed; `bench run --no-sample-files` lets the keyterm system run without
the taught recordings on disk (only the clips could be brought to this Mac at a usable speed).

Cells: rate % [clustered 95% interval] (count/total). "Name-free items, a listed name inserted" carries ElevenLabs'
count beside it. Paired differences are clustered; bold = interval excludes 0.

## own-names-bench v1.2.0, every suite

### v1.2.0: calls

| System | Passes scored | Names right | Untaught overwritten | Name-free items, a listed name inserted (ElevenLabs beside) | … a name from another recording | Ordinary-word error | Names right − ElevenLabs | Overwritten − ElevenLabs | Inserted − ElevenLabs | Word error − ElevenLabs | Names right − ours-fixed | Overwritten − ours-fixed | Inserted − ours-fixed | Word error − ours-fixed |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| ElevenLabs Scribe v2 (keyterms) | 2837 / 2837 | 95.5 [93.5, 97.2] (674/706) | 1.6 [0.5, 2.9] (11/706) | 1.7 [0.7, 2.9] (7/417) | 0.0 [0.0, 0.0] (0/417) | 9.1 [8.4, 9.9] | n/a | n/a | n/a | n/a | -0.1 [-2.2, +1.8] | **-1.8 [-3.7, -0.2]** | -0.2 [-1.2, +0.7] | **-1.1 [-1.5, -0.6]** |
| v0.3.0 + fixes (ours-fixed) | 2837 / 2837 | 95.6 [93.9, 97.1] (675/706) | 3.4 [1.5, 5.6] (24/706) | 1.9 [0.7, 3.3] (8/417); EL 7/417 | 0.7 [0.0, 1.7] (3/417) | 10.2 [9.4, 11.1] | +0.1 [-1.8, +2.2] | **+1.8 [+0.2, +3.7]** | +0.2 [-0.7, +1.2] | **+1.1 [+0.6, +1.5]** | n/a | n/a | n/a | n/a |
| v0.3.0 + guard + re-read | 2837 / 2837 | 95.9 [94.3, 97.3] (677/706) | 3.1 [1.3, 5.3] (22/706) | 2.2 [1.0, 3.6] (9/417); EL 7/417 | 0.7 [0.0, 1.7] (3/417) | 9.8 [9.0, 10.6] | +0.4 [-1.5, +2.4] | +1.6 [+0.0, +3.4] | +0.5 [-0.7, +1.7] | **+0.6 [+0.3, +1.0]** | +0.3 [+0.0, +0.7] | -0.3 [-0.7, +0.0] | +0.2 [+0.0, +0.7] | **-0.4 [-0.7, -0.2]** |
| **finalist: v6j + guard + re-read** | 2837 / 2837 | 94.5 [92.2, 96.4] (667/706) | 1.6 [0.5, 2.8] (11/706) | 1.7 [0.5, 2.9] (7/417); EL 7/417 | 0.5 [0.0, 1.2] (2/417) | 9.8 [9.1, 10.6] | -1.0 [-3.6, +1.6] | +0.0 [-1.0, +0.9] | +0.0 [-1.0, +1.0] | **+0.7 [+0.4, +1.0]** | -1.1 [-2.8, +0.4] | **-1.8 [-3.4, -0.4]** | -0.2 [-1.2, +0.5] | **-0.4 [-0.7, -0.1]** |

### v1.2.0: svq

| System | Passes scored | Names right | Untaught overwritten | Name-free items, a listed name inserted (ElevenLabs beside) | … a name from another recording | Ordinary-word error | Names right − ElevenLabs | Overwritten − ElevenLabs | Inserted − ElevenLabs | Word error − ElevenLabs | Names right − ours-fixed | Overwritten − ours-fixed | Inserted − ours-fixed | Word error − ours-fixed |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| ElevenLabs Scribe v2 (keyterms) | 4608 / 4608 | 98.6 [97.7, 99.3] (1400/1420) | 0.6 [0.1, 1.3] (9/1420) | 0.6 [0.0, 1.6] (2/320) | 0.6 [0.0, 1.6] (2/320) | 14.5 [12.2, 17.0] | n/a | n/a | n/a | n/a | **+3.9 [+2.5, +5.5]** | +0.4 [-0.1, +1.0] | +0.6 [+0.0, +1.6] | **+7.4 [+5.2, +9.7]** |
| v0.3.0 + fixes (ours-fixed) | 4608 / 4608 | 94.6 [93.0, 96.1] (1344/1420) | 0.3 [0.1, 0.6] (4/1420) | 0.0 [0.0, 0.0] (0/320); EL 2/320 | 0.0 [0.0, 0.0] (0/320) | 7.2 [6.2, 8.2] | **-3.9 [-5.5, -2.5]** | -0.4 [-1.0, +0.1] | -0.6 [-1.6, +0.0] | **-7.4 [-9.7, -5.2]** | n/a | n/a | n/a | n/a |
| v0.3.0 + guard + re-read | 4608 / 4608 | 94.9 [93.3, 96.4] (1348/1420) | 0.4 [0.1, 0.7] (5/1420) | 0.0 [0.0, 0.0] (0/320); EL 2/320 | 0.0 [0.0, 0.0] (0/320) | 7.1 [6.1, 8.1] | **-3.7 [-5.2, -2.3]** | -0.3 [-0.9, +0.3] | -0.6 [-1.6, +0.0] | **-7.5 [-9.8, -5.3]** | **+0.3 [+0.1, +0.6]** | +0.1 [-0.1, +0.3] | +0.0 [+0.0, +0.0] | -0.1 [-0.3, +0.0] |
| **finalist: v6j + guard + re-read** | 4608 / 4608 | 95.0 [93.5, 96.4] (1349/1420) | 0.2 [0.0, 0.5] (3/1420) | 0.0 [0.0, 0.0] (0/320); EL 2/320 | 0.0 [0.0, 0.0] (0/320) | 8.6 [7.4, 9.9] | **-3.6 [-5.1, -2.2]** | -0.4 [-1.0, +0.1] | -0.6 [-1.6, +0.0] | **-6.0 [-8.1, -4.0]** | +0.4 [-0.9, +1.6] | -0.1 [-0.4, +0.2] | +0.0 [+0.0, +0.0] | **+1.4 [+0.6, +2.2]** |

### v1.2.0: modulate

| System | Passes scored | Names right | Untaught overwritten | Name-free items, a listed name inserted (ElevenLabs beside) | … a name from another recording | Ordinary-word error | Names right − ElevenLabs | Overwritten − ElevenLabs | Inserted − ElevenLabs | Word error − ElevenLabs | Names right − ours-fixed | Overwritten − ours-fixed | Inserted − ours-fixed | Word error − ours-fixed |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| ElevenLabs Scribe v2 (keyterms) | 1962 / 1962 | 93.0 [88.6, 96.3] (664/714) | 0.3 [0.0, 0.8] (2/714) | n/a | n/a | 11.6 [9.7, 14.4] | n/a | n/a | n/a | n/a | +2.1 [-0.2, +3.9] | -0.1 [-0.6, +0.0] | n/a | -0.2 [-1.2, +0.3] |
| v0.3.0 + fixes (ours-fixed) | 1962 / 1962 | 90.9 [87.0, 94.1] (649/714) | 0.4 [0.0, 1.1] (3/714) | n/a | n/a | 11.8 [9.9, 14.7] | -2.1 [-3.9, +0.2] | +0.1 [+0.0, +0.6] | n/a | +0.2 [-0.3, +1.2] | n/a | n/a | n/a | n/a |
| v0.3.0 + guard + re-read | 1962 / 1962 | 91.0 [87.1, 94.3] (650/714) | 0.4 [0.0, 1.1] (3/714) | n/a | n/a | 11.8 [9.9, 14.7] | -2.0 [-3.8, +0.4] | +0.1 [+0.0, +0.6] | n/a | +0.3 [-0.3, +1.2] | +0.1 [+0.0, +0.5] | +0.0 [+0.0, +0.0] | n/a | +0.0 [-0.1, +0.1] |
| **finalist: v6j + guard + re-read** | 1962 / 1962 | 91.7 [88.1, 94.7] (655/714) | 0.6 [0.1, 1.2] (4/714) | n/a | n/a | 11.8 [9.7, 14.9] | -1.3 [-3.0, +1.1] | +0.3 [+0.0, +0.8] | n/a | +0.2 [-0.3, +1.1] | +0.8 [-0.6, +2.5] | +0.1 [-0.4, +0.7] | n/a | -0.0 [-0.5, +0.5] |

### v1.2.0: ami

| System | Passes scored | Names right | Untaught overwritten | Name-free items, a listed name inserted (ElevenLabs beside) | … a name from another recording | Ordinary-word error | Names right − ElevenLabs | Overwritten − ElevenLabs | Inserted − ElevenLabs | Word error − ElevenLabs | Names right − ours-fixed | Overwritten − ours-fixed | Inserted − ours-fixed | Word error − ours-fixed |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| ElevenLabs Scribe v2 (keyterms) | 238 / 238 | n/a | n/a | 0.8 [0.0, 2.5] (1/119) | 0.8 [0.0, 2.5] (1/119) | 16.7 [14.9, 18.2] | n/a | n/a | n/a | n/a | n/a | n/a | -0.8 [-3.3, +1.7] | **-1.5 [-1.8, -1.1]** |
| v0.3.0 + fixes (ours-fixed) | 238 / 238 | n/a | n/a | 1.7 [0.0, 3.3] (2/119); EL 1/119 | 1.7 [0.0, 3.3] (2/119) | 18.2 [16.4, 19.9] | n/a | n/a | +0.8 [-1.7, +3.3] | **+1.5 [+1.1, +1.8]** | n/a | n/a | n/a | n/a |
| v0.3.0 + guard + re-read | 238 / 238 | n/a | n/a | 0.8 [0.0, 2.5] (1/119); EL 1/119 | 0.8 [0.0, 2.5] (1/119) | 17.7 [16.2, 19.3] | n/a | n/a | +0.0 [-2.5, +2.5] | **+1.0 [+0.2, +1.5]** | n/a | n/a | -0.8 [-2.5, +0.0] | **-0.5 [-0.8, -0.2]** |
| **finalist: v6j + guard + re-read** | 238 / 238 | n/a | n/a | 0.0 [0.0, 0.0] (0/119); EL 1/119 | 0.0 [0.0, 0.0] (0/119) | 17.2 [15.5, 18.8] | n/a | n/a | -0.8 [-2.5, +0.0] | **+0.6 [+0.2, +0.9]** | n/a | n/a | -1.7 [-3.3, +0.0] | **-0.9 [-1.1, -0.8]** |

### v1.2.0: books

| System | Passes scored | Names right | Untaught overwritten | Name-free items, a listed name inserted (ElevenLabs beside) | … a name from another recording | Ordinary-word error | Names right − ElevenLabs | Overwritten − ElevenLabs | Inserted − ElevenLabs | Word error − ElevenLabs | Names right − ours-fixed | Overwritten − ours-fixed | Inserted − ours-fixed | Word error − ours-fixed |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| ElevenLabs Scribe v2 (keyterms) | 6591 | 92.2 [87.6, 97.2] (1021/1107) | 3.3 [1.1, 5.8] (37/1107) | 0.2 [0.0, 0.7] (1/408) | n/a | 1.7 [1.4, 1.9] | n/a | n/a | n/a | n/a | **-4.2 [-7.4, -0.3]** | **-3.4 [-5.7, -1.1]** | **-4.2 [-10.3, -0.5]** | **-1.1 [-1.4, -0.7]** |
| v0.3.0 + fixes (ours-fixed) | 4025 / 4025 | 96.4 [94.7, 98.4] (1067/1107) | 6.8 [2.4, 10.7] (75/1107) | 4.4 [0.7, 10.5] (18/408); EL 1/408 | n/a | 2.7 [2.4, 3.1] | **+4.2 [+0.3, +7.4]** | **+3.4 [+1.1, +5.7]** | **+4.2 [+0.5, +10.3]** | **+1.1 [+0.7, +1.4]** | n/a | n/a | n/a | n/a |
| v0.3.0 + guard + re-read | 4025 / 4025 | 96.5 [94.6, 98.5] (1068/1107) | 6.9 [2.4, 10.9] (76/1107) | 4.2 [0.5, 10.3] (17/408); EL 1/408 | n/a | 2.6 [2.3, 3.0] | **+4.2 [+0.7, +7.1]** | **+3.5 [+0.9, +6.1]** | **+3.9 [+0.2, +10.0]** | **+1.0 [+0.6, +1.3]** | +0.1 [-0.3, +0.7] | +0.1 [-0.3, +0.4] | -0.2 [-0.7, +0.0] | **-0.1 [-0.2, -0.0]** |
| **finalist: v6j + guard + re-read** | 4025 / 4025 | 94.9 [92.7, 97.2] (1050/1107) | 4.7 [1.5, 7.6] (52/1107) | 3.4 [0.5, 8.6] (14/408); EL 1/408 | n/a | 2.7 [2.3, 3.1] | +2.6 [-1.0, +5.5] | +1.4 [-0.5, +3.0] | **+3.2 [+0.2, +8.3]** | **+1.1 [+0.7, +1.4]** | **-1.5 [-2.4, -0.5]** | **-2.1 [-3.2, -0.7]** | -1.0 [-2.2, +0.2] | -0.0 [-0.1, +0.1] |

## Ship rule on v1.2.0 (pre-registered S1-S5, N1-N3; amendment 1 F1)

| Rule | Measure | Bar | v0.3.0 + guard + re-read | finalist (v6j + guard + re-read) |
| --- | --- | --- | --- | --- |
| S1 | calls names right | > 95.47 | 95.89 pass | 94.48 **FAIL** |
| S2 | svq names right | > 98.59 | 94.93 **FAIL** | 95.00 **FAIL** |
| S3 | modulate names right | > 93.00 | 91.04 **FAIL** | 91.74 **FAIL** |
| S4 | ami ordinary-word error | < 16.67 | 17.71 **FAIL** | 17.23 **FAIL** |
| S5 | books names right | > 92.23 | 96.48 pass | 94.85 pass |
| S5 | books names right | >= 95.39 | 96.48 pass | 94.85 **FAIL** |
| N1 | calls untaught overwritten | <= 3.90 | 3.12 pass | 1.56 pass |
| N1 | svq untaught overwritten | <= 0.78 | 0.35 pass | 0.21 pass |
| N1 | modulate untaught overwritten | <= 0.92 | 0.42 pass | 0.56 pass |
| N1 | books untaught overwritten | <= 7.28 | 6.87 pass | 4.70 pass |
| N2 | calls name-free inserted | <= 2.42 | 2.16 (9/417) pass | 1.68 (7/417) pass |
| N2 | svq name-free inserted | <= 0.50 | 0.00 (0/320) pass | 0.00 (0/320) pass |
| N2 | ami name-free inserted | <= 2.18 | 0.84 (1/119) pass | 0.00 (0/119) pass |
| N2 | books name-free inserted | <= 4.91 | 4.17 (17/408) pass | 3.43 (14/408) pass |
| N3 | calls ordinary-word error | <= 10.51 | 9.79 pass | 9.83 pass |
| N3 | svq ordinary-word error | <= 7.47 | 7.05 pass | 8.55 **FAIL** |
| N3 | modulate ordinary-word error | <= 12.12 | 11.83 pass | 11.81 pass |
| N3 | books ordinary-word error | <= 3.03 | 2.63 pass | 2.73 pass |
| F1 | calls name-free inserted | < 1.00 | 2.16 (9/417) **FAIL** | 1.68 (7/417) **FAIL** |
| F1 | svq name-free inserted | < 1.00 | 0.00 (0/320) pass | 0.00 (0/320) pass |
| F1 | ami name-free inserted | < 1.00 | 0.84 (1/119) pass | 0.00 (0/119) pass |
| F1 | books name-free inserted | < 1.00 | 4.17 (17/408) **FAIL** | 3.43 (14/408) **FAIL** |

- v0.3.0 + guard + re-read: fails S2 svq, S3 modulate, S4 ami, F1 calls, F1 books
- **finalist: v6j + guard + re-read**: fails S1 calls, S2 svq, S3 modulate, S4 ami, S5 books, N3 svq, F1 calls, F1 books

## Sealed v1.3 conversation suite (suite hash dbff73e6…0fdd3), every condition

### conv13: conv13-conv

| System | Passes scored | Names right | Untaught overwritten | Name-free items, a listed name inserted (ElevenLabs beside) | … a name from another recording | Ordinary-word error | Names right − ElevenLabs | Overwritten − ElevenLabs | Inserted − ElevenLabs | Word error − ElevenLabs | Names right − ours-fixed | Overwritten − ours-fixed | Inserted − ours-fixed | Word error − ours-fixed |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| ElevenLabs Scribe v2 (keyterms) | 796 / 796 | 97.7 [94.8, 100.0] (129/132) | 0.8 [0.0, 2.4] (1/132) | 0.0 [0.0, 0.0] (0/200) | 0.0 [0.0, 0.0] (0/200) | 7.0 [6.0, 8.1] | n/a | n/a | n/a | n/a | -0.8 [-3.5, +1.6] | -2.3 [-5.1, +0.0] | -0.5 [-1.6, +0.0] | +0.2 [-0.5, +1.2] |
| v0.3.0 + fixes (ours-fixed) | 796 / 796 | 98.5 [96.1, 100.0] (130/132) | 3.0 [0.7, 6.2] (4/132) | 0.5 [0.0, 1.6] (1/200); EL 0/200 | 0.0 [0.0, 0.0] (0/200) | 6.8 [6.0, 7.6] | +0.8 [-1.6, +3.5] | +2.3 [+0.0, +5.1] | +0.5 [+0.0, +1.6] | -0.2 [-1.2, +0.5] | n/a | n/a | n/a | n/a |
| v0.3.0 + guard + re-read | 796 / 796 | 98.5 [96.1, 100.0] (130/132) | 3.0 [0.7, 6.2] (4/132) | 0.5 [0.0, 1.6] (1/200); EL 0/200 | 0.0 [0.0, 0.0] (0/200) | 6.7 [5.9, 7.5] | +0.8 [-1.6, +3.5] | +2.3 [+0.0, +5.1] | +0.5 [+0.0, +1.6] | -0.3 [-1.3, +0.4] | +0.0 [+0.0, +0.0] | +0.0 [+0.0, +0.0] | +0.0 [+0.0, +0.0] | -0.1 [-0.2, +0.1] |
| **finalist: v6j + guard + re-read** | 796 / 796 | 98.5 [96.2, 100.0] (130/132) | 1.5 [0.0, 3.9] (2/132) | 0.0 [0.0, 0.0] (0/200); EL 0/200 | 0.0 [0.0, 0.0] (0/200) | 6.5 [5.7, 7.3] | +0.8 [-2.3, +4.2] | +0.8 [-1.6, +3.4] | +0.0 [+0.0, +0.0] | -0.5 [-1.5, +0.2] | +0.0 [-2.2, +2.3] | -1.5 [-5.3, +2.2] | -0.5 [-1.6, +0.0] | -0.3 [-0.7, +0.1] |

| System (names right by group) | name never seen in training | name seen in training |
| --- | --- | --- |
| ElevenLabs Scribe v2 (keyterms) | 96.3 [88.0, 100.0] (26/27) | 98.1 [95.1, 100.0] (103/105) |
| v0.3.0 + fixes (ours-fixed) | 100.0 [100.0, 100.0] (27/27) | 98.1 [95.1, 100.0] (103/105) |
| v0.3.0 + guard + re-read | 100.0 [100.0, 100.0] (27/27) | 98.1 [95.1, 100.0] (103/105) |
| **finalist: v6j + guard + re-read** | 96.3 [88.9, 100.0] (26/27) | 99.0 [97.0, 100.0] (104/105) |

### conv13: conv13-far

| System | Passes scored | Names right | Untaught overwritten | Name-free items, a listed name inserted (ElevenLabs beside) | … a name from another recording | Ordinary-word error | Names right − ElevenLabs | Overwritten − ElevenLabs | Inserted − ElevenLabs | Word error − ElevenLabs | Names right − ours-fixed | Overwritten − ours-fixed | Inserted − ours-fixed | Word error − ours-fixed |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| ElevenLabs Scribe v2 (keyterms) | 1299 / 1299 | 88.0 [84.4, 91.5] (293/333) | 11.4 [8.3, 14.8] (38/333) | 1.3 [0.0, 3.4] (2/150) | 0.0 [0.0, 0.0] (0/150) | 19.1 [13.6, 28.5] | n/a | n/a | n/a | n/a | **+9.9 [+5.5, +14.3]** | +3.6 [+0.0, +7.1] | +1.3 [+0.0, +3.4] | -0.8 [-5.6, +8.2] |
| v0.3.0 + fixes (ours-fixed) | 1299 / 1299 | 78.1 [72.9, 83.1] (260/333) | 7.8 [5.1, 10.9] (26/333) | 0.0 [0.0, 0.0] (0/150); EL 2/150 | 0.0 [0.0, 0.0] (0/150) | 19.9 [17.7, 22.2] | **-9.9 [-14.3, -5.5]** | -3.6 [-7.1, +0.0] | -1.3 [-3.4, +0.0] | +0.8 [-8.2, +5.6] | n/a | n/a | n/a | n/a |
| v0.3.0 + guard + re-read | 1299 / 1299 | 78.7 [73.6, 83.6] (262/333) | 7.5 [4.8, 10.6] (25/333) | 0.0 [0.0, 0.0] (0/150); EL 2/150 | 0.0 [0.0, 0.0] (0/150) | 19.1 [16.9, 21.4] | **-9.3 [-13.6, -4.9]** | **-3.9 [-7.4, -0.3]** | -1.3 [-3.4, +0.0] | -0.0 [-9.0, +4.8] | +0.6 [-0.6, +1.8] | -0.3 [-0.9, +0.0] | +0.0 [+0.0, +0.0] | **-0.8 [-1.2, -0.4]** |
| **finalist: v6j + guard + re-read** | 1299 / 1299 | 80.8 [75.4, 85.6] (269/333) | 5.7 [3.3, 8.4] (19/333) | 0.7 [0.0, 2.1] (1/150); EL 2/150 | 0.0 [0.0, 0.0] (0/150) | 19.8 [17.3, 22.5] | **-7.2 [-11.8, -2.9]** | **-5.7 [-9.2, -2.4]** | -0.7 [-3.1, +1.4] | +0.7 [-8.6, +5.8] | +2.7 [-0.9, +6.5] | -2.1 [-5.3, +0.9] | +0.7 [+0.0, +2.1] | -0.1 [-1.1, +1.0] |

| System (names right by group) | name never seen in training | name seen in training |
| --- | --- | --- |
| ElevenLabs Scribe v2 (keyterms) | 85.9 [81.1, 90.5] (195/227) | 92.5 [87.7, 97.0] (98/106) |
| v0.3.0 + fixes (ours-fixed) | 76.2 [69.2, 82.8] (173/227) | 82.1 [75.0, 88.9] (87/106) |
| v0.3.0 + guard + re-read | 76.7 [69.7, 83.3] (174/227) | 83.0 [76.1, 89.3] (88/106) |
| **finalist: v6j + guard + re-read** | 76.7 [69.5, 83.2] (174/227) | 89.6 [84.0, 94.7] (95/106) |

### conv13: conv13-level

| System | Passes scored | Names right | Untaught overwritten | Name-free items, a listed name inserted (ElevenLabs beside) | … a name from another recording | Ordinary-word error | Names right − ElevenLabs | Overwritten − ElevenLabs | Inserted − ElevenLabs | Word error − ElevenLabs | Names right − ours-fixed | Overwritten − ours-fixed | Inserted − ours-fixed | Word error − ours-fixed |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| ElevenLabs Scribe v2 (keyterms) | 1140 / 1140 | 84.3 [79.8, 88.7] (253/300) | 11.0 [7.8, 14.4] (33/300) | 1.7 [0.0, 4.2] (2/120) | 0.0 [0.0, 0.0] (0/120) | 14.7 [12.8, 16.8] | n/a | n/a | n/a | n/a | **+12.3 [+7.5, +17.3]** | +2.7 [-1.0, +6.3] | +1.7 [+0.0, +4.2] | **-5.0 [-6.3, -3.6]** |
| v0.3.0 + fixes (ours-fixed) | 1140 / 1140 | 72.0 [66.4, 77.4] (216/300) | 8.3 [5.4, 11.6] (25/300) | 0.0 [0.0, 0.0] (0/120); EL 2/120 | 0.0 [0.0, 0.0] (0/120) | 19.7 [17.5, 22.0] | **-12.3 [-17.3, -7.5]** | -2.7 [-6.3, +1.0] | -1.7 [-4.2, +0.0] | **+5.0 [+3.6, +6.3]** | n/a | n/a | n/a | n/a |
| v0.3.0 + guard + re-read | 1140 / 1140 | 72.3 [66.7, 77.8] (217/300) | 7.7 [4.8, 10.8] (23/300) | 0.0 [0.0, 0.0] (0/120); EL 2/120 | 0.0 [0.0, 0.0] (0/120) | 18.6 [16.5, 20.9] | **-12.0 [-17.0, -7.2]** | -3.3 [-6.8, +0.0] | -1.7 [-4.2, +0.0] | **+3.9 [+2.6, +5.2]** | +0.3 [-0.7, +1.4] | -0.7 [-1.7, +0.0] | +0.0 [+0.0, +0.0] | **-1.1 [-1.5, -0.7]** |
| **finalist: v6j + guard + re-read** | 1140 / 1140 | 77.7 [72.8, 82.3] (233/300) | 9.3 [6.2, 12.7] (28/300) | 0.8 [0.0, 2.7] (1/120); EL 2/120 | 0.0 [0.0, 0.0] (0/120) | 18.9 [16.7, 21.4] | **-6.7 [-11.0, -2.4]** | -1.7 [-5.3, +2.0] | -0.8 [-3.8, +1.8] | **+4.2 [+2.8, +5.7]** | **+5.7 [+1.9, +9.5]** | +1.0 [-2.6, +4.7] | +0.8 [+0.0, +2.7] | -0.8 [-1.9, +0.4] |

| System (names right by group) | name never seen in training | name seen in training |
| --- | --- | --- |
| ElevenLabs Scribe v2 (keyterms) | 80.2 [74.3, 85.7] (166/207) | 93.5 [88.2, 97.9] (87/93) |
| v0.3.0 + fixes (ours-fixed) | 65.7 [58.7, 72.5] (136/207) | 86.0 [79.2, 92.4] (80/93) |
| v0.3.0 + guard + re-read | 66.2 [59.2, 73.0] (137/207) | 86.0 [79.3, 92.2] (80/93) |
| **finalist: v6j + guard + re-read** | 73.4 [67.3, 79.4] (152/207) | 87.1 [80.6, 93.3] (81/93) |

### conv13: conv13-near

| System | Passes scored | Names right | Untaught overwritten | Name-free items, a listed name inserted (ElevenLabs beside) | … a name from another recording | Ordinary-word error | Names right − ElevenLabs | Overwritten − ElevenLabs | Inserted − ElevenLabs | Word error − ElevenLabs | Names right − ours-fixed | Overwritten − ours-fixed | Inserted − ours-fixed | Word error − ours-fixed |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| ElevenLabs Scribe v2 (keyterms) | 840 / 840 | 92.5 [89.3, 95.4] (259/280) | 12.5 [8.6, 16.9] (35/280) | n/a | n/a | 6.0 [4.6, 7.7] | n/a | n/a | n/a | n/a | +0.7 [-2.6, +4.1] | -1.1 [-5.0, +2.9] | n/a | **-2.2 [-3.2, -1.3]** |
| v0.3.0 + fixes (ours-fixed) | 840 / 840 | 91.8 [88.3, 94.9] (257/280) | 13.6 [9.7, 17.8] (38/280) | n/a | n/a | 8.2 [6.7, 10.0] | -0.7 [-4.1, +2.6] | +1.1 [-2.9, +5.0] | n/a | **+2.2 [+1.3, +3.2]** | n/a | n/a | n/a | n/a |
| v0.3.0 + guard + re-read | 840 / 840 | 91.8 [88.3, 94.9] (257/280) | 12.1 [8.4, 16.1] (34/280) | n/a | n/a | 7.8 [6.3, 9.5] | -0.7 [-4.1, +2.6] | -0.4 [-4.3, +3.5] | n/a | **+1.8 [+0.9, +2.7]** | +0.0 [+0.0, +0.0] | **-1.4 [-3.0, -0.3]** | n/a | **-0.4 [-0.7, -0.2]** |
| **finalist: v6j + guard + re-read** | 840 / 840 | 90.7 [86.9, 94.1] (254/280) | 6.1 [3.5, 9.0] (17/280) | n/a | n/a | 7.2 [5.7, 9.1] | -1.8 [-5.4, +1.9] | **-6.4 [-10.9, -2.2]** | n/a | **+1.2 [+0.3, +2.1]** | -1.1 [-3.8, +1.7] | **-7.5 [-11.0, -4.3]** | n/a | **-1.0 [-1.6, -0.4]** |

| System (names right by group) | name never seen in training | name seen in training |
| --- | --- | --- |
| ElevenLabs Scribe v2 (keyterms) | 91.6 [87.8, 95.2] (197/215) | 95.4 [89.4, 100.0] (62/65) |
| v0.3.0 + fixes (ours-fixed) | 89.8 [85.4, 93.8] (193/215) | 98.5 [95.1, 100.0] (64/65) |
| v0.3.0 + guard + re-read | 89.8 [85.4, 93.8] (193/215) | 98.5 [95.1, 100.0] (64/65) |
| **finalist: v6j + guard + re-read** | 88.4 [83.7, 92.7] (190/215) | 98.5 [95.1, 100.0] (64/65) |

### conv13: conv13-short

| System | Passes scored | Names right | Untaught overwritten | Name-free items, a listed name inserted (ElevenLabs beside) | … a name from another recording | Ordinary-word error | Names right − ElevenLabs | Overwritten − ElevenLabs | Inserted − ElevenLabs | Word error − ElevenLabs | Names right − ours-fixed | Overwritten − ours-fixed | Inserted − ours-fixed | Word error − ours-fixed |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| ElevenLabs Scribe v2 (keyterms) | 1784 / 1784 | 84.6 [80.2, 88.8] (291/344) | 13.7 [10.1, 17.4] (47/344) | 6.4 [3.8, 9.2] (24/376) | 0.0 [0.0, 0.0] (0/376) | 52.9 [48.3, 57.7] | n/a | n/a | n/a | n/a | **+23.5 [+17.8, +29.1]** | **+8.4 [+4.4, +12.4]** | **+6.1 [+3.5, +8.9]** | **+8.5 [+4.2, +12.6]** |
| v0.3.0 + fixes (ours-fixed) | 1784 / 1784 | 61.0 [55.7, 66.4] (210/344) | 5.2 [3.0, 7.6] (18/344) | 0.3 [0.0, 0.9] (1/376); EL 24/376 | 0.0 [0.0, 0.0] (0/376) | 44.4 [39.8, 49.4] | **-23.5 [-29.1, -17.8]** | **-8.4 [-12.4, -4.4]** | **-6.1 [-8.9, -3.5]** | **-8.5 [-12.6, -4.2]** | n/a | n/a | n/a | n/a |
| v0.3.0 + guard + re-read | 1784 / 1784 | 61.0 [55.7, 66.4] (210/344) | 5.2 [3.0, 7.6] (18/344) | 0.3 [0.0, 0.9] (1/376); EL 24/376 | 0.0 [0.0, 0.0] (0/376) | 44.4 [39.8, 49.4] | **-23.5 [-29.1, -17.8]** | **-8.4 [-12.4, -4.4]** | **-6.1 [-8.9, -3.5]** | **-8.5 [-12.6, -4.2]** | +0.0 [+0.0, +0.0] | +0.0 [+0.0, +0.0] | +0.0 [+0.0, +0.0] | +0.0 [+0.0, +0.0] |
| **finalist: v6j + guard + re-read** | 1784 / 1784 | 86.0 [82.2, 89.6] (296/344) | 5.8 [3.5, 8.3] (20/344) | 0.5 [0.0, 1.4] (2/376); EL 24/376 | 0.0 [0.0, 0.0] (0/376) | 41.0 [36.4, 45.8] | +1.5 [-3.3, +6.4] | **-7.8 [-12.0, -3.7]** | **-5.9 [-8.7, -3.1]** | **-12.0 [-16.1, -7.8]** | **+25.0 [+20.2, +29.7]** | +0.6 [-2.5, +3.8] | +0.3 [+0.0, +0.9] | **-3.5 [-6.9, -0.3]** |

| System (names right by group) | name never seen in training | name seen in training |
| --- | --- | --- |
| ElevenLabs Scribe v2 (keyterms) | 84.0 [78.5, 89.3] (199/237) | 86.0 [78.4, 92.9] (92/107) |
| v0.3.0 + fixes (ours-fixed) | 56.5 [50.2, 62.8] (134/237) | 71.0 [61.1, 80.4] (76/107) |
| v0.3.0 + guard + re-read | 56.5 [50.2, 62.8] (134/237) | 71.0 [61.1, 80.4] (76/107) |
| **finalist: v6j + guard + re-read** | 86.1 [81.2, 90.5] (204/237) | 86.0 [79.8, 91.7] (92/107) |

### conv13: conv13-street

| System | Passes scored | Names right | Untaught overwritten | Name-free items, a listed name inserted (ElevenLabs beside) | … a name from another recording | Ordinary-word error | Names right − ElevenLabs | Overwritten − ElevenLabs | Inserted − ElevenLabs | Word error − ElevenLabs | Names right − ours-fixed | Overwritten − ours-fixed | Inserted − ours-fixed | Word error − ours-fixed |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| ElevenLabs Scribe v2 (keyterms) | 1260 / 1260 | 95.6 [93.3, 97.7] (306/320) | 6.9 [4.3, 9.6] (22/320) | 0.0 [0.0, 0.0] (0/150) | 0.0 [0.0, 0.0] (0/150) | 6.1 [5.2, 7.1] | n/a | n/a | n/a | n/a | +2.5 [-0.9, +6.0] | **-3.8 [-7.4, -0.3]** | +0.0 [+0.0, +0.0] | **-1.9 [-2.6, -1.1]** |
| v0.3.0 + fixes (ours-fixed) | 1260 / 1260 | 93.1 [90.0, 96.1] (298/320) | 10.6 [7.3, 14.2] (34/320) | 0.0 [0.0, 0.0] (0/150); EL 0/150 | 0.0 [0.0, 0.0] (0/150) | 8.0 [7.1, 8.9] | -2.5 [-6.0, +0.9] | **+3.8 [+0.3, +7.4]** | +0.0 [+0.0, +0.0] | **+1.9 [+1.1, +2.6]** | n/a | n/a | n/a | n/a |
| v0.3.0 + guard + re-read | 1260 / 1260 | 93.8 [90.7, 96.6] (300/320) | 10.6 [7.3, 14.2] (34/320) | 0.0 [0.0, 0.0] (0/150); EL 0/150 | 0.0 [0.0, 0.0] (0/150) | 7.8 [6.9, 8.8] | -1.9 [-5.2, +1.3] | **+3.8 [+0.3, +7.4]** | +0.0 [+0.0, +0.0] | **+1.7 [+0.9, +2.5]** | +0.6 [+0.0, +1.6] | +0.0 [+0.0, +0.0] | +0.0 [+0.0, +0.0] | **-0.2 [-0.4, -0.0]** |
| **finalist: v6j + guard + re-read** | 1260 / 1260 | 93.1 [89.9, 96.1] (298/320) | 6.2 [3.7, 9.1] (20/320) | 0.0 [0.0, 0.0] (0/150); EL 0/150 | 0.0 [0.0, 0.0] (0/150) | 7.5 [6.6, 8.5] | -2.5 [-5.9, +0.9] | -0.6 [-3.4, +2.3] | +0.0 [+0.0, +0.0] | **+1.4 [+0.5, +2.2]** | +0.0 [-1.9, +1.9] | **-4.4 [-7.2, -1.6]** | +0.0 [+0.0, +0.0] | **-0.5 [-1.0, -0.0]** |

| System (names right by group) | name never seen in training | name seen in training |
| --- | --- | --- |
| ElevenLabs Scribe v2 (keyterms) | 95.6 [92.9, 97.9] (217/227) | 95.7 [91.0, 99.0] (89/93) |
| v0.3.0 + fixes (ours-fixed) | 91.6 [87.3, 95.4] (208/227) | 96.8 [92.6, 100.0] (90/93) |
| v0.3.0 + guard + re-read | 92.1 [87.8, 95.8] (209/227) | 97.8 [94.4, 100.0] (91/93) |
| **finalist: v6j + guard + re-read** | 91.2 [87.0, 95.0] (207/227) | 97.8 [94.4, 100.0] (91/93) |

### conv13: conv13-tel

| System | Passes scored | Names right | Untaught overwritten | Name-free items, a listed name inserted (ElevenLabs beside) | … a name from another recording | Ordinary-word error | Names right − ElevenLabs | Overwritten − ElevenLabs | Inserted − ElevenLabs | Word error − ElevenLabs | Names right − ours-fixed | Overwritten − ours-fixed | Inserted − ours-fixed | Word error − ours-fixed |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| ElevenLabs Scribe v2 (keyterms) | 1210 / 1210 | 97.0 [94.9, 98.9] (262/270) | 8.1 [5.1, 11.4] (22/270) | 0.5 [0.0, 1.6] (1/200) | 0.0 [0.0, 0.0] (0/200) | 4.7 [3.9, 5.6] | n/a | n/a | n/a | n/a | -1.5 [-3.9, +0.7] | +1.1 [-2.4, +4.5] | +0.5 [+0.0, +1.6] | **-0.8 [-1.3, -0.3]** |
| v0.3.0 + fixes (ours-fixed) | 1210 / 1210 | 98.5 [96.9, 99.6] (266/270) | 7.0 [4.1, 10.2] (19/270) | 0.0 [0.0, 0.0] (0/200); EL 1/200 | 0.0 [0.0, 0.0] (0/200) | 5.5 [4.8, 6.3] | +1.5 [-0.7, +3.9] | -1.1 [-4.5, +2.4] | -0.5 [-1.6, +0.0] | **+0.8 [+0.3, +1.3]** | n/a | n/a | n/a | n/a |
| v0.3.0 + guard + re-read | 1210 / 1210 | 98.5 [96.9, 99.6] (266/270) | 7.0 [4.1, 10.2] (19/270) | 0.0 [0.0, 0.0] (0/200); EL 1/200 | 0.0 [0.0, 0.0] (0/200) | 5.4 [4.6, 6.1] | +1.5 [-0.7, +3.9] | -1.1 [-4.5, +2.4] | -0.5 [-1.6, +0.0] | **+0.7 [+0.2, +1.2]** | +0.0 [+0.0, +0.0] | +0.0 [+0.0, +0.0] | +0.0 [+0.0, +0.0] | -0.1 [-0.3, +0.0] |
| **finalist: v6j + guard + re-read** | 1210 / 1210 | 98.1 [96.4, 99.6] (265/270) | 3.3 [1.4, 5.6] (9/270) | 0.0 [0.0, 0.0] (0/200); EL 1/200 | 0.0 [0.0, 0.0] (0/200) | 4.9 [4.2, 5.6] | +1.1 [-1.2, +3.6] | **-4.8 [-8.1, -1.7]** | -0.5 [-1.6, +0.0] | +0.2 [-0.3, +0.7] | -0.4 [-2.0, +1.2] | **-3.7 [-6.4, -1.1]** | +0.0 [+0.0, +0.0] | **-0.6 [-0.9, -0.3]** |

| System (names right by group) | name never seen in training | name seen in training |
| --- | --- | --- |
| ElevenLabs Scribe v2 (keyterms) | 98.3 [96.2, 100.0] (174/177) | 94.6 [89.4, 98.9] (88/93) |
| v0.3.0 + fixes (ours-fixed) | 98.9 [97.1, 100.0] (175/177) | 97.8 [94.4, 100.0] (91/93) |
| v0.3.0 + guard + re-read | 98.9 [97.1, 100.0] (175/177) | 97.8 [94.4, 100.0] (91/93) |
| **finalist: v6j + guard + re-read** | 97.7 [95.3, 99.5] (173/177) | 98.9 [96.5, 100.0] (92/93) |

### conv13: conv13-xspk

| System | Passes scored | Names right | Untaught overwritten | Name-free items, a listed name inserted (ElevenLabs beside) | … a name from another recording | Ordinary-word error | Names right − ElevenLabs | Overwritten − ElevenLabs | Inserted − ElevenLabs | Word error − ElevenLabs | Names right − ours-fixed | Overwritten − ours-fixed | Inserted − ours-fixed | Word error − ours-fixed |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| ElevenLabs Scribe v2 (keyterms) | 1044 / 1044 | 99.4 [98.5, 100.0] (346/348) | 1.7 [0.6, 3.2] (6/348) | n/a | n/a | 4.4 [3.4, 5.8] | n/a | n/a | n/a | n/a | +0.3 [-0.9, +1.5] | -1.1 [-3.6, +1.2] | n/a | -1.0 [-1.8, +0.1] |
| v0.3.0 + fixes (ours-fixed) | 1044 / 1044 | 99.1 [98.0, 100.0] (345/348) | 2.9 [1.2, 4.9] (10/348) | n/a | n/a | 5.4 [4.5, 6.3] | -0.3 [-1.5, +0.9] | +1.1 [-1.2, +3.6] | n/a | +1.0 [-0.1, +1.8] | n/a | n/a | n/a | n/a |
| v0.3.0 + guard + re-read | 1044 / 1044 | 99.1 [98.0, 100.0] (345/348) | 2.6 [1.1, 4.3] (9/348) | n/a | n/a | 5.2 [4.4, 6.2] | -0.3 [-1.5, +0.9] | +0.9 [-1.3, +3.1] | n/a | +0.8 [-0.2, +1.7] | +0.0 [+0.0, +0.0] | -0.3 [-0.9, +0.0] | n/a | **-0.2 [-0.3, -0.0]** |
| **finalist: v6j + guard + re-read** | 1044 / 1044 | 99.4 [98.5, 100.0] (346/348) | 0.9 [0.0, 1.9] (3/348) | n/a | n/a | 4.9 [4.1, 5.7] | +0.0 [-1.1, +1.2] | -0.9 [-2.6, +0.8] | n/a | +0.4 [-0.6, +1.3] | +0.3 [+0.0, +0.9] | **-2.0 [-4.0, -0.3]** | n/a | **-0.5 [-0.9, -0.1]** |

| System (names right by group) | name never seen in training | name seen in training |
| --- | --- | --- |
| ElevenLabs Scribe v2 (keyterms) | 100.0 [100.0, 100.0] (60/60) | 99.3 [98.2, 100.0] (286/288) |
| v0.3.0 + fixes (ours-fixed) | 100.0 [100.0, 100.0] (60/60) | 99.0 [97.6, 100.0] (285/288) |
| v0.3.0 + guard + re-read | 100.0 [100.0, 100.0] (60/60) | 99.0 [97.6, 100.0] (285/288) |
| **finalist: v6j + guard + re-read** | 100.0 [100.0, 100.0] (60/60) | 99.3 [98.2, 100.0] (286/288) |
