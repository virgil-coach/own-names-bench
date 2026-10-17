# v0.7 adapters on the own-names-bench v1.2.0 audiobook clips (results/v07bench/PROTOCOL.md)

> **Selection target, not a held-out estimate.** Under the 2026-10-17 protocol the v1.2.0 audiobook suite is used to
> choose between candidates, so these numbers are optimistic for whichever candidate is chosen. Aggregates only: no
> per-clip output, reference, audio or failing clip was read. The launch claim needs a fresh sealed audiobook suite.
> Each look is logged in LOOKS.md.

Target: false name insertions (name-free items with a listed name inserted) under 1%, ideally ElevenLabs' 0.2% (1/408).
**None of v7a, v7b, v7c reaches it**: v7c is lowest at 1.2% (5/408), v7a and v7b 2.5% (10/408). All three are below
v6j's 3.4% (14/408), but no paired difference against v6j on insertions excludes 0 (v7c −2.2 [−6.4, +0.0]), and v7c pays
1.9 points of names right against v6j (interval excludes 0).

## What was run

| System | Adapter (SHA-256 checked on the pod) | Code | Where |
| --- | --- | --- | --- |
| v7a + guard + re-read (`ours-reread`, OURS_ADAPTER) | qwen17B_audio_heard_v7a 64530033…37df | own-names-bench `v07/bench` ecdb4df | RunPod RTX PRO 6000, EUR-IS-1, pod n0ecj1n3neqzng |
| v7b + guard + re-read | qwen17B_audio_heard_v7b 192e7fec…0a01 | same | same |
| v7c + guard + re-read | qwen17B_audio_heard_v7c de91437d…226c | same | same |

- `diag/adapter_pod.sh 1.74 v07bench <spec>...`, 18 specs (6 shards per adapter, `podin/bk-0..5`: the 1,459 audiobook
  clips of the v0.6 run's shards), none + own + own-minus, no chapters, 6 processes on the GPU. v1.2.0 data manifest
  3025b1e5… verified file by file on the pod. 4,025 / 4,025 passes per adapter, 0 errors; the pulled files match the
  pod's SHA256SUMS. (run.json records hourly_usd 1.74, the inventory figure; the pod was billed at $2.49/h.)
- Reference rows are the existing runs re-scored, not re-run (ElevenLabs published run, ours-fixed results/diag, v6j
  results/v06final); their numbers equal results/v06final/TABLES.md.
- Scored with `diag/v07_score.py` (the benchmark's score_clips / prop / ratio / paired_suite, clustered by book).

Cells: rate % [clustered 95% interval] (count/total). Paired differences are clustered; bold = interval excludes 0.

## v1.2.0: books

| System | Passes scored | Names right | Untaught overwritten | Name-free items, a listed name inserted (ElevenLabs beside) | Ordinary-word error | Names right − ElevenLabs | Overwritten − ElevenLabs | Inserted − ElevenLabs | Word error − ElevenLabs | Names right − v6j | Overwritten − v6j | Inserted − v6j | Word error − v6j |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| ElevenLabs Scribe v2 (keyterms) | 6591 | 92.2 [87.6, 97.2] (1021/1107) | 3.3 [1.1, 5.8] (37/1107) | 0.2 [0.0, 0.7] (1/408) | 1.7 [1.4, 1.9] | n/a | n/a | n/a | n/a | -2.6 [-5.5, +1.0] | -1.4 [-3.0, +0.5] | **-3.2 [-8.3, -0.2]** | **-1.1 [-1.4, -0.7]** |
| v0.3.0 + fixes (ours-fixed) | 4025 / 4025 | 96.4 [94.7, 98.4] (1067/1107) | 6.8 [2.4, 10.7] (75/1107) | 4.4 [0.7, 10.5] (18/408); EL 1/408 | 2.7 [2.4, 3.1] | **+4.2 [+0.3, +7.4]** | **+3.4 [+1.1, +5.7]** | **+4.2 [+0.5, +10.3]** | **+1.1 [+0.7, +1.4]** | **+1.5 [+0.5, +2.4]** | **+2.1 [+0.7, +3.2]** | +1.0 [-0.2, +2.2] | +0.0 [-0.1, +0.1] |
| v6j finalist + guard + re-read | 4025 / 4025 | 94.9 [92.7, 97.2] (1050/1107) | 4.7 [1.5, 7.6] (52/1107) | 3.4 [0.5, 8.6] (14/408); EL 1/408 | 2.7 [2.3, 3.1] | +2.6 [-1.0, +5.5] | +1.4 [-0.5, +3.0] | **+3.2 [+0.2, +8.3]** | **+1.1 [+0.7, +1.4]** | n/a | n/a | n/a | n/a |
| v7a (1:1 decoys) + guard + re-read | 4025 / 4025 | 94.1 [91.1, 97.1] (1042/1107) | 5.7 [1.9, 9.2] (63/1107) | 2.5 [0.2, 6.1] (10/408); EL 1/408 | 2.7 [2.3, 3.2] | +1.9 [-1.0, +4.1] | **+2.3 [+0.1, +4.6]** | +2.2 [+0.0, +5.9] | **+1.1 [+0.7, +1.4]** | -0.7 [-1.8, +0.7] | **+1.0 [+0.1, +1.8]** | -1.0 [-2.7, +0.0] | +0.0 [-0.1, +0.2] |
| v7b (2:1 decoys) + guard + re-read | 4025 / 4025 | 94.5 [91.0, 98.0] (1046/1107) | 4.5 [0.9, 7.9] (50/1107) | 2.5 [0.0, 6.6] (10/408); EL 1/408 | 2.7 [2.3, 3.2] | +2.3 [-0.1, +4.1] | +1.2 [-1.1, +3.3] | +2.2 [-0.2, +6.4] | **+1.1 [+0.7, +1.4]** | -0.4 [-1.9, +1.4] | -0.2 [-1.0, +0.5] | -1.0 [-2.2, +0.0] | +0.0 [-0.1, +0.1] |
| v7c (+ phoneme-edit rows) + guard + re-read | 4025 / 4025 | 93.0 [89.7, 96.3] (1029/1107) | 4.9 [1.1, 8.5] (54/1107) | 1.2 [0.2, 2.5] (5/408); EL 1/408 | 2.8 [2.3, 3.3] | +0.7 [-2.0, +2.9] | +1.5 [-1.8, +4.2] | +1.0 [-0.2, +2.2] | **+1.1 [+0.7, +1.5]** | **-1.9 [-3.2, -0.3]** | +0.2 [-1.6, +1.4] | -2.2 [-6.4, +0.0] | +0.1 [-0.1, +0.2] |
