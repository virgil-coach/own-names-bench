# own-names-bench v1.1.0 results

Scored 2026-10-14. Rates in percent with 95% intervals from a bootstrap over clusters: books for clips (each clip book has one reader), chapters for chapters. Name matches are one to one. Every system got the same names in the same order through its own custom-vocabulary feature.

## Runs: expected, completed and failed passes

| Run | System | List variants | Expected | Completed | Failed | Stale (made from an older list) | Complete |
| --- | --- | --- | --- | --- | --- | --- | --- |
| deepgram | deepgram | none, own | 4049 | 4049 | 0 | 0 | yes |
| elevenlabs | elevenlabs | none, own, all | 6615 | 6615 | 0 | 0 | yes |
| ours-mlx-macmini | ours-mlx | none, own, all, xr | 6680 | 6550 | 0 | 65 | **no: left out of every table below** |
| ours-rtx4090 | ours | none, own, all, xr | 6680 | 6680 | 0 | 0 | yes |
| parakeet-a100 | parakeet | none, own, all | 6615 | 6615 | 0 | 0 | yes |
| qwen-context-rtx4090 | qwen-context | none, own, all | 6615 | 6615 | 0 | 0 | yes |
| qwen-rtx4090 | qwen | none | 1483 | 1483 | 0 | 0 | yes |
| whisper-rtx4090 | whisper | none, own | 4049 | 4049 | 0 | 0 | yes |

## Clips, the book's own name list

| System | Names right, invented | Names right, traditional | Names right, all | Untaught overwritten | Wrong name written | Name-free: a listed name inserted | Ordinary-word error | Full-transcript error | Spoken name among the names sent |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| deepgram | 92.2 [89.2, 95.4] | 61.3 [47.2, 78.6] | 75.2 [62.0, 89.7] | 8.4 [5.7, 11.0] | 3.1 [1.0, 5.3] | 1.7 [0.5, 2.9] | 4.1 [3.1, 5.0] | 4.1 [3.1, 5.0] | 85.8 [69.4, 100.0] |
| elevenlabs | 96.6 [93.7, 98.6] | 88.7 [83.4, 96.3] | 92.2 [87.6, 97.2] | 3.3 [1.1, 5.8] | 1.8 [0.4, 3.0] | 0.2 [0.0, 0.7] | 1.7 [1.4, 1.9] | 1.7 [1.4, 1.9] | 100.0 [100.0, 100.0] |
| ours-rtx4090 | 97.8 [95.9, 99.4] | 95.7 [93.6, 98.4] | 96.7 [94.9, 98.6] | 7.0 [2.3, 11.3] | 0.8 [0.1, 1.5] | 3.9 [0.5, 9.6] | 2.7 [2.4, 3.0] | 2.7 [2.3, 3.0] | 100.0 [100.0, 100.0] |
| parakeet-a100 | 82.4 [72.8, 89.4] | 75.3 [68.5, 82.9] | 78.5 [72.3, 85.3] | 27.2 [15.9, 37.3] | 7.6 [2.3, 12.4] | 7.1 [4.2, 10.3] | 3.5 [2.9, 4.0] | 3.7 [3.0, 4.4] | 100.0 [100.0, 100.0] |
| qwen-context-rtx4090 | 76.4 [69.3, 82.0] | 53.6 [44.7, 62.1] | 63.9 [54.6, 75.2] | 4.3 [1.6, 7.2] | 3.0 [1.0, 4.9] | 0.2 [0.0, 0.7] | 3.6 [2.6, 4.5] | 3.7 [2.6, 5.0] | 100.0 [100.0, 100.0] |
| qwen-rtx4090 | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a | its feature cannot take this list |
| whisper-rtx4090 | 92.4 [88.8, 95.1] | 59.5 [52.1, 68.5] | 74.3 [63.7, 88.6] | 1.6 [0.2, 3.4] | 1.0 [0.0, 1.8] | 0.2 [0.0, 0.7] | 3.0 [2.4, 3.4] | 2.9 [2.4, 3.4] | 65.6 [46.0, 92.6] |

## Clips, all-books list (902 entries)

| System | Names right, invented | Names right, traditional | Names right, all | Untaught overwritten | Wrong name written | Name-free: a listed name inserted | Ordinary-word error | Full-transcript error | Spoken name among the names sent |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| deepgram | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a | its feature cannot take this list |
| elevenlabs | 94.0 [90.4, 96.8] | 86.8 [81.8, 94.3] | 90.1 [86.0, 94.8] | 3.7 [1.6, 5.8] | 1.6 [0.5, 2.5] | 0.5 [0.0, 1.2] | 1.8 [1.5, 2.1] | 1.8 [1.5, 2.1] | 100.0 [100.0, 100.0] |
| ours-rtx4090 | 96.4 [93.4, 98.9] | 94.9 [92.7, 97.7] | 95.6 [93.7, 97.8] | 12.3 [7.1, 16.9] | 1.4 [0.2, 2.3] | 5.4 [1.7, 11.0] | 2.8 [2.4, 3.2] | 2.8 [2.4, 3.2] | 100.0 [100.0, 100.0] |
| parakeet-a100 | 71.3 [60.5, 79.4] | 67.8 [64.1, 71.9] | 69.4 [64.3, 75.0] | 42.4 [34.8, 48.4] | 14.5 [9.2, 19.2] | 23.3 [16.9, 30.1] | 5.2 [4.7, 5.8] | 5.7 [5.1, 6.3] | 100.0 [100.0, 100.0] |
| qwen-context-rtx4090 | 66.7 [60.6, 72.0] | 49.2 [43.7, 55.1] | 57.1 [50.4, 65.8] | 5.2 [3.2, 7.7] | 3.9 [2.2, 5.3] | 0.2 [0.0, 0.7] | 4.0 [3.1, 4.7] | 4.4 [3.4, 5.3] | 100.0 [100.0, 100.0] |
| qwen-rtx4090 | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a | its feature cannot take this list |
| whisper-rtx4090 | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a | its feature cannot take this list |

## Clips, no list

| System | Names right, invented | Names right, traditional | Names right, all | Name-free: a book name inserted | Ordinary-word error | Full-transcript error |
| --- | --- | --- | --- | --- | --- | --- |
| deepgram | 28.1 [22.7, 33.0] | 24.3 [20.5, 28.0] | 26.0 [23.0, 29.8] | 0.0 [0.0, 0.0] | 6.0 [5.2, 6.6] | 5.9 [5.2, 6.5] |
| elevenlabs | 56.1 [46.9, 64.5] | 62.3 [53.5, 67.9] | 59.5 [52.7, 64.5] | 0.0 [0.0, 0.0] | 3.1 [2.7, 3.6] | 3.1 [2.7, 3.5] |
| ours-rtx4090 | 34.3 [24.3, 43.3] | 39.3 [34.7, 46.1] | 37.0 [31.4, 42.5] | 0.0 [0.0, 0.0] | 4.9 [4.3, 5.4] | 4.8 [4.3, 5.3] |
| parakeet-a100 | 39.7 [33.9, 45.6] | 39.1 [34.3, 49.6] | 39.4 [35.2, 44.9] | 0.0 [0.0, 0.0] | 4.3 [3.8, 4.7] | 4.3 [3.8, 4.6] |
| qwen-context-rtx4090 | 39.5 [27.4, 49.8] | 43.8 [39.8, 49.6] | 41.8 [35.4, 47.5] | 0.0 [0.0, 0.0] | 4.3 [3.8, 4.8] | 4.2 [3.7, 4.7] |
| qwen-rtx4090 | 39.5 [27.4, 49.8] | 43.8 [39.8, 49.6] | 41.8 [35.4, 47.5] | 0.0 [0.0, 0.0] | 4.3 [3.8, 4.8] | 4.2 [3.7, 4.7] |
| whisper-rtx4090 | 51.3 [41.6, 60.9] | 48.5 [42.5, 59.0] | 49.8 [44.0, 57.0] | 0.0 [0.0, 0.0] | 3.7 [3.3, 4.0] | 3.7 [3.3, 4.0] |

## Continuous chapters

| System | Names right (taught) | same reader taught it | another reader taught it | Wrong names per minute | Untaught overwritten | Ordinary-word error | Full-transcript error | Names right, no list |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| deepgram | 83.4 [76.1, 91.4] | 80.2 [72.0, 87.2] | 98.3 [96.2, 100.0] | 0.04 [0.00, 0.10] | 5.3 [0.6, 10.0] | 3.2 [2.2, 4.7] | 3.2 [2.2, 4.7] | 14.9 [6.6, 23.7] |
| elevenlabs | 98.5 [95.2, 100.0] | 98.2 [93.9, 100.0] | 100.0 [100.0, 100.0] | 0.00 [0.00, 0.00] | 1.8 [0.0, 3.4] | 2.0 [1.1, 3.5] | 2.0 [1.0, 3.5] | 63.6 [30.6, 85.5] |
| ours-rtx4090 | 99.4 [98.6, 100.0] | 99.3 [98.2, 100.0] | 100.0 [100.0, 100.0] | 0.01 [0.00, 0.02] | 1.8 [0.0, 3.4] | 2.8 [1.7, 4.4] | 2.7 [1.7, 4.3] | 26.2 [12.0, 44.7] |
| parakeet-a100 | 91.8 [87.5, 97.9] | 90.5 [86.3, 97.5] | 98.3 [96.8, 100.0] | 0.01 [0.00, 0.02] | 4.7 [0.0, 10.0] | 2.8 [1.7, 4.3] | 2.8 [1.8, 4.2] | 39.4 [18.3, 57.7] |
| qwen-context-rtx4090 | 89.2 [85.4, 94.6] | 87.6 [84.0, 93.4] | 96.7 [96.2, 100.0] | 0.83 [0.04, 2.04] | 2.9 [0.0, 5.9] | 2.9 [1.9, 4.6] | 3.4 [2.0, 5.4] | 22.2 [10.4, 37.6] |
| qwen-rtx4090 | 22.2 [10.4, 37.6] | 18.0 [8.8, 27.1] | 41.7 [0.0, 77.4] | 0.00 [0.00, 0.00] | 1.2 [0.0, 2.7] | 4.5 [2.9, 6.6] | 4.5 [3.0, 6.5] | 22.2 [10.4, 37.6] |
| whisper-rtx4090 | 77.0 [54.5, 93.8] | 82.0 [59.3, 96.5] | 53.3 [9.7, 100.0] | 0.01 [0.00, 0.02] | 1.8 [0.0, 3.4] | 3.6 [2.4, 5.3] | 3.5 [2.3, 5.1] | 26.5 [14.0, 43.6] |

## Taught in the reader's own voice or another reader's (clips)

Systems taught by recording. Mentions whose name another benchmark book also lists, read by a different reader: the same clip and own list, with the name taught once by the clip's reader and once by the other reader.

| System | Mentions | Right, taught by the same reader | Right, taught by another reader | Another listed name written instead |
| --- | --- | --- | --- | --- |
| ours-rtx4090 | 65 | 100.0 [100.0, 100.0] | 96.9 [93.1, 100.0] | 1.5 [0.0, 3.4] |

## Speed and cost

| System | Machine | Clip latency p50 / p90 (s) | Real-time factor (clips) | Cost per audio hour: nominal | Cost per audio hour: this workload |
| --- | --- | --- | --- | --- | --- |
| deepgram | Apple M4 Max | 0.41 / 0.67 | 0.044 | $0.336 with a list, $0.258 without (2026-10-13) | chapters $0.310; clips, no list $0.258; clips, own list $0.336 |
| elevenlabs | Apple M4 Max | 1.07 / 1.75 | 0.114 | $0.270 with a list, $0.220 without (2026-10-13) | chapters $0.253; clips, all-books list $0.522; clips, no list $0.220; clips, own list $0.399 |
| ours-rtx4090 | NVIDIA GeForce RTX 4090, 580.126.09, 24564 MiB | 2.34 / 3.41 | 0.223 | $0.198 | measured real-time factor 0.223 x $0.89/h for the machine |
| parakeet-a100 | NVIDIA GeForce RTX 4090, 580.126.09, 24564 MiB | 0.23 / 0.43 | 0.029 | $0.026 | measured real-time factor 0.029 x $0.89/h for the machine |
| qwen-context-rtx4090 | NVIDIA GeForce RTX 4090, 580.126.09, 24564 MiB | 0.69 / 1.65 | 0.089 | $0.079 | measured real-time factor 0.089 x $0.89/h for the machine |
| qwen-rtx4090 | NVIDIA GeForce RTX 4090, 580.159.04, 24564 MiB | 0.47 / 0.64 | 0.046 | $0.041 | measured real-time factor 0.046 x $0.89/h for the machine |
| whisper-rtx4090 | NVIDIA GeForce RTX 4090, 580.159.04, 24564 MiB | 0.34 / 0.46 | 0.033 | $0.030 | measured real-time factor 0.033 x $0.89/h for the machine |

## Paired differences: ours-rtx4090 minus each system, same items

Points, 95% bootstrap interval over books (clips) or chapters; **holds** when the interval excludes zero. In brackets: items only the first system / only the second got (no item-level test; it would ignore the clustering).

| Measure | ours-rtx4090 − deepgram | ours-rtx4090 − elevenlabs | ours-rtx4090 − parakeet-a100 | ours-rtx4090 − qwen-context-rtx4090 | ours-rtx4090 − qwen-rtx4090 | ours-rtx4090 − whisper-rtx4090 |
| --- | --- | --- | --- | --- | --- | --- |
| Names right, own list | +21.4 [+8.0, +33.2] (247 vs 10) **holds** | +4.4 [+0.5, +7.6] (67 vs 18) **holds** | +18.2 [+12.3, +23.3] (215 vs 14) **holds** | +32.8 [+22.9, +40.5] (370 vs 7) **holds** | n/a | +22.3 [+9.1, +31.6] (259 vs 12) **holds** |
|   invented | +5.6 [+2.2, +8.2] (35 vs 7) **holds** | +1.2 [-1.6, +4.1] (15 vs 9) | +15.4 [+8.0, +25.1] (85 vs 8) **holds** | +21.4 [+16.8, +27.4] (111 vs 4) **holds** | n/a | +5.4 [+2.4, +9.1] (35 vs 8) **holds** |
|   traditional | +34.4 [+18.2, +46.5] (212 vs 3) **holds** | +7.1 [+1.6, +10.5] (52 vs 9) **holds** | +20.4 [+14.4, +25.1] (130 vs 6) **holds** | +42.1 [+35.5, +48.6] (259 vs 3) **holds** | n/a | +36.2 [+29.7, +41.5] (224 vs 4) **holds** |
| Untaught overwritten, own list | -1.4 [-4.4, +1.3] (47 vs 62) | +3.7 [+1.0, +6.4] (51 vs 10) **holds** | -20.1 [-26.8, -11.3] (28 vs 251) **holds** | +2.7 [+0.3, +5.1] (57 vs 27) **holds** | n/a | +5.4 [+2.0, +8.7] (65 vs 5) **holds** |
| Wrong name written, own list | -2.3 [-3.8, -0.8] (7 vs 32) **holds** | -1.0 [-1.7, -0.2] (6 vs 17) **holds** | -6.8 [-11.0, -2.1] (4 vs 79) **holds** | -2.2 [-3.5, -0.7] (8 vs 32) **holds** | n/a | -0.2 [-0.5, +0.2] (9 vs 11) |
| Name-free inserted, own list | +2.2 [-1.2, +8.1] (14 vs 5) | +3.7 [+0.0, +9.6] (16 vs 1) | -3.2 [-8.3, +3.9] (13 vs 26) | +3.7 [+0.0, +9.6] (16 vs 1) | n/a | +3.7 [+0.0, +9.6] (15 vs 0) |
| Ordinary-word error, own list | -1.4 [-2.1, -0.6] **holds** | +1.0 [+0.7, +1.3] **holds** | -0.8 [-1.2, -0.3] **holds** | -0.9 [-1.7, -0.2] **holds** | n/a | -0.3 [-0.6, +0.2] |
| Full-transcript error, own list | -1.5 [-2.2, -0.6] **holds** | +1.0 [+0.7, +1.3] **holds** | -1.1 [-1.6, -0.4] **holds** | -1.1 [-2.2, -0.2] **holds** | n/a | -0.3 [-0.6, +0.2] |
| Names right, all-books list | n/a | +5.5 [+1.2, +9.0] (85 vs 24) **holds** | +26.2 [+20.8, +31.2] (306 vs 16) **holds** | +38.5 [+31.2, +43.8] (434 vs 8) **holds** | n/a | n/a |
| Untaught overwritten, all-books list | n/a | +8.6 [+4.9, +11.8] (106 vs 11) **holds** | -30.1 [-34.0, -25.2] (47 vs 380) **holds** | +7.0 [+2.5, +10.7] (106 vs 28) **holds** | n/a | n/a |
| Chapters: names right | +16.0 [+7.9, +23.4] (57 vs 2) **holds** | +0.9 [-1.3, +4.4] (5 vs 2) | +7.6 [+1.1, +12.2] (28 vs 2) **holds** | +10.2 [+4.6, +14.4] (37 vs 2) **holds** | +77.3 [+61.7, +89.3] (265 vs 0) **holds** | +22.4 [+6.1, +44.6] (78 vs 1) **holds** |
| Chapters: untaught overwritten | -3.5 [-7.2, +0.0] (0 vs 6) | +0.0 [+0.0, +0.0] (0 vs 0) | -2.9 [-6.8, +0.0] (0 vs 5) | -1.2 [-2.7, +0.0] (0 vs 2) | +0.6 [+0.0, +2.2] (1 vs 0) | +0.0 [+0.0, +0.0] (0 vs 0) |
| Chapters: ordinary-word error | -0.5 [-0.7, -0.2] **holds** | +0.7 [+0.3, +1.3] **holds** | -0.0 [-0.6, +0.5] | -0.2 [-0.6, +0.1] | -1.7 [-2.6, -1.0] **holds** | -0.8 [-1.5, -0.3] **holds** |
| Chapters: full-transcript error | -0.5 [-0.7, -0.3] **holds** | +0.7 [+0.3, +1.2] **holds** | -0.1 [-0.7, +0.4] | -0.7 [-1.7, -0.1] **holds** | -1.8 [-2.7, -1.1] **holds** | -0.8 [-1.5, -0.3] **holds** |
| Chapters: wrong names per minute | -0.03 [-0.09, +0.02] | +0.01 [+0.00, +0.02] | +0.00 [+0.00, +0.00] | -0.82 [-2.04, -0.02] **holds** | +0.01 [+0.00, +0.02] | +0.00 [+0.00, +0.00] |

## How each system took the names

- **deepgram**: keyterm; limits: 500 keyterm tokens per request (Deepgram's tokenizer, unpublished); fit: the longest prefix of the list (most frequent first) the service accepts, found by binary search with half a second of silence (refused requests are not billed)
- **elevenlabs**: keyterms; limits: <=1000 terms, each <50 chars and <=5 words, no <>{}[]\; fit: drop terms that break a per-term rule, then keep the first 1000 (most frequent in the book first)
- **ours-rtx4090**: spotter shortlist of the whole list -> writer prompt + taught recordings; limits: none; fit: no limit: the spotter ranks every name
- **parakeet-a100**: GPU phrase boosting: decoding.greedy.boosting_tree.key_phrases_list; limits: none; fit: all names
- **qwen-context-rtx4090**: context (system prompt): names joined by ', '; limits: none; fit: all names
- **qwen-rtx4090**: none; limits: none; fit: no list
- **whisper-rtx4090**: prompt_ids (initial prompt): names joined by ', '; limits: 223 prompt tokens; fit: longest prefix of the list (most frequent first) within the token limit

## Runs

- **deepgram**: `deepgram` {"service": "Deepgram pre-recorded", "endpoint": "https://api.deepgram.com/v1/listen", "model": "nova-3", "language": "en", "smart_format": true, "list_feature": "keyterm", "limits": "500 keyterm tokens per request (Deepgram's tokenizer, unpublished)", "fit": "the longest prefix of the list (most frequent first) the service accepts, found by binary search with half a second of silence (refused requests are not billed)"}; machine {"platform": "macOS-26.3.1-arm64-arm-64bit", "machine": "arm64", "python": "3.12.13", "cpu": "Apple M4 Max", "memory_gb": 128.0, "os": "macOS 26.3.1 (25D771280a)"}; code HEAD; dataset virgil-coach/own-names-bench@v1.0.0 (fingerprint 1625ef57df22); commands ['/Users/jameslal/workspace/jl/own-names-bench/.venv/bin/bench run --system deepgram']; started 2026-10-13T20:02:28+00:00
- **elevenlabs**: `elevenlabs` {"service": "ElevenLabs Speech to Text", "endpoint": "https://api.elevenlabs.io/v1/speech-to-text", "model_id": "scribe_v2", "language_code": "en", "tag_audio_events": false, "temperature": 0.0, "seed": 0, "list_feature": "keyterms", "limits": "<=1000 terms, each <50 chars and <=5 words, no <>{}[]\\", "fit": "drop terms that break a per-term rule, then keep the first 1000 (most frequent in the book first)"}; machine {"platform": "macOS-26.3.1-arm64-arm-64bit", "machine": "arm64", "python": "3.12.13", "cpu": "Apple M4 Max", "memory_gb": 128.0, "os": "macOS 26.3.1 (25D771280a)"}; code 9247c769925118a1cca7fb84ea7ae5b68d359e63-dirty; dataset virgil-coach/own-names-bench@v1.1.0 (fingerprint 1625ef57df22); commands ['/Users/jameslal/workspace/jl/own-names-bench/.venv/bin/bench run --system elevenlabs', '/Users/jameslal/workspace/jl/own-names-bench/.venv/bin/bench run --system elevenlabs']; started 2026-10-13T20:02:34+00:00
- **ours-rtx4090**: `ours` {"runtime": "PyTorch reference (own_names_bench/ours_ref)", "device": "cuda", "torch": "2.14.1+cu130", "transformers": "5.19.0", "cuda_device": "NVIDIA GeForce RTX 4090", "base": "Qwen/Qwen3-ASR-1.7B-hf@bcd2b5b7f32b480ab5790554cfa8347f246a14f3", "adapter": "virgil-coach/own-names-qwen3-asr@e02efd5e0db0f357f7ada3caf18e1ca293528098/audio-text-note", "adapter_version": "v0.3.0", "adapter_sha256": "67dbabef14851e89ad1b62d509e595713d4a2b6254fbc26cdb700fca1e097f55", "dtype": "float32", "decoding": "greedy, at most 200 new tokens", "spotter_phon": "facebook/wav2vec2-lv-60-espeak-cv-ft@0c380a877907192512147c466ead03055f200cad", "spotter_wavlm": "microsoft/wavlm-base-plus@98fd61b9c652129c839c0a25a05987d8f59256a4", "g2p": "own_names_bench/ours_ref/g2p.json (espeak-ng 1.52.0, every benchmark name)", "shortlist": 10, "prune": "off", "gate": "none", "windows": "Detail Keeper Segmenter (pause 0.45 s after 2 s, cap 8 s), fed 0.1 s at a time", "list_feature": "spotter shortlist of the whole list -> writer prompt + taught recordings", "fit": "no limit: the spotter ranks every name", "platform": "Linux-6.8.0-71-generic-x86_64-with-glibc2.35"}; machine {"platform": "Linux-6.8.0-71-generic-x86_64-with-glibc2.35", "machine": "x86_64", "python": "3.12.15", "cpu": "AMD EPYC 7443 24-Core Processor", "memory_gb": 251.5, "os": "Ubuntu 22.04.5 LTS", "gpu": "NVIDIA GeForce RTX 4090, 580.126.09, 24564 MiB"}; code f7d4044; dataset virgil-coach/own-names-bench@v1.1.0 (fingerprint 1625ef57df22); commands ['/gpu-cli-workspaces/jameslal/path-3172b95136962215/.pod/venv-qwen/bin/bench run --system ours --label ours-rtx4090 --hourly-usd 0.89', '/gpu-cli-workspaces/jameslal/path-3172b95136962215/.pod/venv-qwen/bin/bench run --system ours --label ours-rtx4090 --hourly-usd 0.89', '/gpu-cli-workspaces/jameslal/path-3172b95136962215/.pod/venv-qwen/bin/bench run --system ours --label ours-rtx4090 --hourly-usd 0.89', '/gpu-cli-workspaces/jameslal/path-3172b95136962215/.pod/venv-qwen/bin/bench run --system ours --label ours-rtx4090 --hourly-usd 0.89']; started 2026-10-13T21:18:29+00:00
- **parakeet-a100**: `parakeet` {"model": "nvidia/parakeet-tdt-0.6b-v2@ae9ad07059c7c739ffaf932226a8fe64ae2620b0", "runtime": "NeMo 3.0.0, torch 2.14.1+cu130", "device": "cuda", "decoding": "greedy_batch (TDT label looping)", "long_form": "over 20 min: rel_pos_local_attn [256, 256]", "list_feature": "GPU phrase boosting: decoding.greedy.boosting_tree.key_phrases_list", "boosting": {"boosting_tree_alpha": 2.0, "context_score": 1.0, "depth_scaling": 2.0, "alpha_chosen_on": "the chapters task: grid 0.25, 0.5, 1, 2, 4; 2 had the most names right less untaught overwritten (92.7% - 4.1%)"}, "fit": "all names"}; machine {"platform": "Linux-6.8.0-71-generic-x86_64-with-glibc2.35", "machine": "x86_64", "python": "3.12.15", "cpu": "AMD EPYC 7443 24-Core Processor", "memory_gb": 251.5, "os": "Ubuntu 22.04.5 LTS", "gpu": "NVIDIA GeForce RTX 4090, 580.126.09, 24564 MiB"}; code 8d8f168; dataset virgil-coach/own-names-bench@v1.1.0 (fingerprint 1625ef57df22); commands ['/gpu-cli-workspaces/jameslal/path-3b0609d92f9af37f/.pod/venv-parakeet/bin/bench run --system parakeet --label parakeet-a100 --hourly-usd 1.79', '/gpu-cli-workspaces/jameslal/path-3172b95136962215/.pod/venv-parakeet/bin/bench run --system parakeet --label parakeet-a100 --hourly-usd 0.89']; started 2026-10-13T22:12:57+00:00
- **qwen-context-rtx4090**: `qwen-context` {"model": "Qwen/Qwen3-ASR-1.7B-hf@bcd2b5b7f32b480ab5790554cfa8347f246a14f3", "runtime": "transformers 5.19.0, torch 2.14.1+cu130", "device": "cuda", "dtype": "float32", "decoding": "greedy, language English, at most 200 new tokens", "long_form": "chapters cut by the Detail Keeper window cutter", "list_feature": "context (system prompt): names joined by ', '", "fit": "all names"}; machine {"platform": "Linux-6.8.0-71-generic-x86_64-with-glibc2.35", "machine": "x86_64", "python": "3.12.15", "cpu": "AMD EPYC 7443 24-Core Processor", "memory_gb": 251.5, "os": "Ubuntu 22.04.5 LTS", "gpu": "NVIDIA GeForce RTX 4090, 580.126.09, 24564 MiB"}; code 8d8f168; dataset virgil-coach/own-names-bench@v1.1.0 (fingerprint 1625ef57df22); commands ['/gpu-cli-workspaces/jameslal/path-3172b95136962215/.pod/venv-qwen/bin/bench run --system qwen-context --label qwen-context-rtx4090 --hourly-usd 0.89', '/gpu-cli-workspaces/jameslal/path-3172b95136962215/.pod/venv-qwen/bin/bench run --system qwen-context --label qwen-context-rtx4090 --hourly-usd 0.89']; started 2026-10-13T21:51:37+00:00
- **qwen-rtx4090**: `qwen` {"model": "Qwen/Qwen3-ASR-1.7B-hf@bcd2b5b7f32b480ab5790554cfa8347f246a14f3", "runtime": "transformers 5.19.0, torch 2.14.1+cu130", "device": "cuda", "dtype": "float32", "decoding": "greedy, language English, at most 200 new tokens", "long_form": "chapters cut by the Detail Keeper window cutter", "list_feature": "none", "fit": "no list"}; machine {"platform": "Linux-6.8.0-124-generic-x86_64-with-glibc2.35", "machine": "x86_64", "python": "3.12.15", "cpu": "AMD Ryzen 9 7950X 16-Core Processor", "memory_gb": 187.8, "os": "Ubuntu 22.04.5 LTS", "gpu": "NVIDIA GeForce RTX 4090, 580.159.04, 24564 MiB"}; code 1ba0dc2da466d4576e3b34d2efb94f41116f662b; dataset virgil-coach/own-names-bench@v1.0.0 (fingerprint 1625ef57df22); commands ['/gpu-cli-workspaces/jameslal/path-3172b95136962215/.pod/venv-qwen/bin/bench run --system qwen --label qwen-rtx4090 --hourly-usd 0.89']; started 2026-10-13T21:21:57+00:00
- **whisper-rtx4090**: `whisper` {"model": "openai/whisper-large-v3@06f233fe06e710322aca913c1bc4249a0d71fce1", "runtime": "transformers 5.19.0, torch 2.14.1+cu130", "device": "cuda", "dtype": "float16", "decoding": "greedy, language en, task transcribe", "long_form": "chapters cut by the Detail Keeper window cutter; every window decoded with the prompt", "list_feature": "prompt_ids (initial prompt): names joined by ', '", "limits": "223 prompt tokens", "fit": "longest prefix of the list (most frequent first) within the token limit"}; machine {"platform": "Linux-6.8.0-124-generic-x86_64-with-glibc2.35", "machine": "x86_64", "python": "3.12.15", "cpu": "AMD Ryzen 9 7950X 16-Core Processor", "memory_gb": 187.8, "os": "Ubuntu 22.04.5 LTS", "gpu": "NVIDIA GeForce RTX 4090, 580.159.04, 24564 MiB"}; code 1ba0dc2da466d4576e3b34d2efb94f41116f662b; dataset virgil-coach/own-names-bench@v1.0.0 (fingerprint 1625ef57df22); commands ['/gpu-cli-workspaces/jameslal/path-3172b95136962215/.pod/venv-whisper/bin/bench run --system whisper --label whisper-rtx4090 --hourly-usd 0.89', '/gpu-cli-workspaces/jameslal/path-3172b95136962215/.pod/venv-whisper/bin/bench run --system whisper --label whisper-chapterwin-rtx4090 --hourly-usd 0.89 --only chapter/']; started 2026-10-13T23:58:25+00:00; note: clip passes from the first run; chapter passes rerun with the windowed long-form (see config.long_form)

## Reproducibility: the same system on two machines

Identical text: passes whose transcript is the same string. Word difference: word error of one run's text against the other's. Paired difference: first minus second, same items, 95% bootstrap interval over books.

| Runs | Machines | Passes | Identical text | Word difference | Same shortlist (windows) | Items with the same outcome: right (own list) / overwritten | Names right (own list), difference | Untaught overwritten, difference | Chapter names right, difference |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| ours-rtx4090 vs ours-mlx-macmini | NVIDIA GeForce RTX 4090, 580.126.09, 24564 MiB vs Apple M5 Pro | 6550 | 5361 (81.8%) | 0.55% | 4800/14182 (33.8%) | 1095/1107 / 1098/1107 | +0.00 [-0.43, +0.54] (6 vs 6) | +0.27 [-0.22, +0.67] (6 vs 3) | -0.29 [-1.05, +0.00] (0 vs 1) |
| whisper-rtx4090 vs whisper-a100 | NVIDIA GeForce RTX 4090, 580.159.04, 24564 MiB vs NVIDIA A100-SXM4-80GB, 595.91.07, 81920 MiB | 4025 | 4007 (99.6%) | 0.01% | n/a | 1107/1107 / 1107/1107 | +0.00 [+0.00, +0.00] (0 vs 0) | +0.00 [+0.00, +0.00] (0 vs 0) | n/a |
