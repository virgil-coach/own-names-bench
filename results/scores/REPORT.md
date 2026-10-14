# own-names-bench v1.2.0 results

Scored 2026-10-14. Rates in percent with 95% intervals from a bootstrap over clusters: books for clips (each clip book has one reader), chapters for chapters. Name matches are one to one. Every system got the same names in the same order through its own custom-vocabulary feature.

## Runs: expected, completed and failed passes

| Run | System | List variants | Expected | Completed | Failed | Stale (made from an older list) | Complete |
| --- | --- | --- | --- | --- | --- | --- | --- |
| deepgram | deepgram | none, own | 13694 | 13694 | 0 | 0 | yes |
| elevenlabs | elevenlabs | none, own, all | 16260 | 16260 | 0 | 0 | yes |
| ours | ours | none, own, all, xr | 16325 | 16325 | 0 | 0 | yes |
| ours-mlx-macmini | ours-mlx | none, own, all, xr | 16325 | 6550 | 0 | 65 | **no: left out of every table below** |
| parakeet | parakeet | none, own, all | 16260 | 16260 | 0 | 0 | yes |
| qwen | qwen | none | 4896 | 4896 | 0 | 0 | yes |
| qwen-context | qwen-context | none, own, all | 16260 | 16260 | 0 | 0 | yes |
| whisper | whisper | none, own | 13694 | 13694 | 0 | 0 | yes |

## Clips, the book's own name list

| System | Names right, invented | Names right, traditional | Names right, all | Untaught overwritten | Wrong name written | Name-free: a listed name inserted | Ordinary-word error | Full-transcript error | Spoken name among the names sent |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| deepgram | 92.2 [89.2, 95.4] | 61.3 [47.2, 78.6] | 75.2 [62.0, 89.7] | 8.4 [5.7, 11.0] | 3.1 [1.0, 5.3] | 1.7 [0.5, 2.9] | 4.1 [3.1, 5.0] | 4.1 [3.1, 5.0] | 85.8 [69.4, 100.0] |
| elevenlabs | 96.6 [93.7, 98.6] | 88.7 [83.4, 96.3] | 92.2 [87.6, 97.2] | 3.3 [1.1, 5.8] | 1.8 [0.4, 3.0] | 0.2 [0.0, 0.7] | 1.7 [1.4, 1.9] | 1.7 [1.4, 1.9] | 100.0 [100.0, 100.0] |
| ours | 97.8 [95.9, 99.4] | 95.7 [93.6, 98.4] | 96.7 [94.9, 98.6] | 7.0 [2.3, 11.3] | 0.8 [0.1, 1.5] | 3.9 [0.5, 9.6] | 2.7 [2.4, 3.0] | 2.7 [2.3, 3.0] | 100.0 [100.0, 100.0] |
| parakeet | 82.4 [72.8, 89.4] | 75.3 [68.5, 82.9] | 78.5 [72.3, 85.3] | 27.2 [15.9, 37.3] | 7.6 [2.3, 12.4] | 7.1 [4.2, 10.3] | 3.5 [2.9, 4.0] | 3.7 [3.0, 4.4] | 100.0 [100.0, 100.0] |
| qwen | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a | its feature cannot take this list |
| qwen-context | 76.4 [69.3, 82.0] | 53.6 [44.7, 62.1] | 63.9 [54.6, 75.2] | 4.3 [1.6, 7.2] | 3.0 [1.0, 4.9] | 0.2 [0.0, 0.7] | 3.6 [2.6, 4.5] | 3.7 [2.6, 5.0] | 100.0 [100.0, 100.0] |
| whisper | 92.4 [88.8, 95.1] | 59.5 [52.1, 68.5] | 74.3 [63.7, 88.6] | 1.6 [0.2, 3.4] | 1.0 [0.0, 1.8] | 0.2 [0.0, 0.7] | 3.0 [2.4, 3.4] | 2.9 [2.4, 3.4] | 65.6 [46.0, 92.6] |

## Clips, all-books list (902 entries)

| System | Names right, invented | Names right, traditional | Names right, all | Untaught overwritten | Wrong name written | Name-free: a listed name inserted | Ordinary-word error | Full-transcript error | Spoken name among the names sent |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| deepgram | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a | its feature cannot take this list |
| elevenlabs | 94.0 [90.4, 96.8] | 86.8 [81.8, 94.3] | 90.1 [86.0, 94.8] | 3.7 [1.6, 5.8] | 1.6 [0.5, 2.5] | 0.5 [0.0, 1.2] | 1.8 [1.5, 2.1] | 1.8 [1.5, 2.1] | 100.0 [100.0, 100.0] |
| ours | 96.4 [93.4, 98.9] | 94.9 [92.7, 97.7] | 95.6 [93.7, 97.8] | 12.3 [7.1, 16.9] | 1.4 [0.2, 2.3] | 5.4 [1.7, 11.0] | 2.8 [2.4, 3.2] | 2.8 [2.4, 3.2] | 100.0 [100.0, 100.0] |
| parakeet | 71.3 [60.5, 79.4] | 67.8 [64.1, 71.9] | 69.4 [64.3, 75.0] | 42.4 [34.8, 48.4] | 14.5 [9.2, 19.2] | 23.3 [16.9, 30.1] | 5.2 [4.7, 5.8] | 5.7 [5.1, 6.3] | 100.0 [100.0, 100.0] |
| qwen | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a | its feature cannot take this list |
| qwen-context | 66.7 [60.6, 72.0] | 49.2 [43.7, 55.1] | 57.1 [50.4, 65.8] | 5.2 [3.2, 7.7] | 3.9 [2.2, 5.3] | 0.2 [0.0, 0.7] | 4.0 [3.1, 4.7] | 4.4 [3.4, 5.3] | 100.0 [100.0, 100.0] |
| whisper | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a | its feature cannot take this list |

## Clips, no list

| System | Names right, invented | Names right, traditional | Names right, all | Name-free: a book name inserted | Ordinary-word error | Full-transcript error |
| --- | --- | --- | --- | --- | --- | --- |
| deepgram | 28.1 [22.7, 33.0] | 24.3 [20.5, 28.0] | 26.0 [23.0, 29.8] | 0.0 [0.0, 0.0] | 6.0 [5.2, 6.6] | 5.9 [5.2, 6.5] |
| elevenlabs | 56.1 [46.9, 64.5] | 62.3 [53.5, 67.9] | 59.5 [52.7, 64.5] | 0.0 [0.0, 0.0] | 3.1 [2.7, 3.6] | 3.1 [2.7, 3.5] |
| ours | 34.3 [24.3, 43.3] | 39.3 [34.7, 46.1] | 37.0 [31.4, 42.5] | 0.0 [0.0, 0.0] | 4.9 [4.3, 5.4] | 4.8 [4.3, 5.3] |
| parakeet | 39.7 [33.9, 45.6] | 39.1 [34.3, 49.6] | 39.4 [35.2, 44.9] | 0.0 [0.0, 0.0] | 4.3 [3.8, 4.7] | 4.3 [3.8, 4.6] |
| qwen | 39.5 [27.4, 49.8] | 43.8 [39.8, 49.6] | 41.8 [35.4, 47.5] | 0.0 [0.0, 0.0] | 4.3 [3.8, 4.8] | 4.2 [3.7, 4.7] |
| qwen-context | 39.5 [27.4, 49.8] | 43.8 [39.8, 49.6] | 41.8 [35.4, 47.5] | 0.0 [0.0, 0.0] | 4.3 [3.8, 4.8] | 4.2 [3.7, 4.7] |
| whisper | 51.3 [41.6, 60.9] | 48.5 [42.5, 59.0] | 49.8 [44.0, 57.0] | 0.0 [0.0, 0.0] | 3.7 [3.3, 4.0] | 3.7 [3.3, 4.0] |

## Continuous chapters

| System | Names right (taught) | same reader taught it | another reader taught it | Wrong names per minute | Untaught overwritten | Ordinary-word error | Full-transcript error | Names right, no list |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| deepgram | 83.4 [76.1, 91.4] | 80.2 [72.0, 87.2] | 98.3 [96.2, 100.0] | 0.04 [0.00, 0.10] | 5.3 [0.6, 10.0] | 3.2 [2.2, 4.7] | 3.2 [2.2, 4.7] | 14.9 [6.6, 23.7] |
| elevenlabs | 98.5 [95.2, 100.0] | 98.2 [93.9, 100.0] | 100.0 [100.0, 100.0] | 0.00 [0.00, 0.00] | 1.8 [0.0, 3.4] | 2.0 [1.1, 3.5] | 2.0 [1.0, 3.5] | 63.6 [30.6, 85.5] |
| ours | 99.4 [98.6, 100.0] | 99.3 [98.2, 100.0] | 100.0 [100.0, 100.0] | 0.01 [0.00, 0.02] | 1.8 [0.0, 3.4] | 2.8 [1.7, 4.4] | 2.7 [1.7, 4.3] | 26.2 [12.0, 44.7] |
| parakeet | 91.8 [87.5, 97.9] | 90.5 [86.3, 97.5] | 98.3 [96.8, 100.0] | 0.01 [0.00, 0.02] | 4.7 [0.0, 10.0] | 2.8 [1.7, 4.3] | 2.8 [1.8, 4.2] | 39.4 [18.3, 57.7] |
| qwen | 22.2 [10.4, 37.6] | 18.0 [8.8, 27.1] | 41.7 [0.0, 77.4] | 0.00 [0.00, 0.00] | 1.2 [0.0, 2.7] | 4.5 [2.9, 6.6] | 4.5 [3.0, 6.5] | 22.2 [10.4, 37.6] |
| qwen-context | 89.2 [85.4, 94.6] | 87.6 [84.0, 93.4] | 96.7 [96.2, 100.0] | 0.83 [0.04, 2.04] | 2.9 [0.0, 5.9] | 2.9 [1.9, 4.6] | 3.4 [2.0, 5.4] | 22.2 [10.4, 37.6] |
| whisper | 77.0 [54.5, 93.8] | 82.0 [59.3, 96.5] | 53.3 [9.7, 100.0] | 0.01 [0.00, 0.02] | 1.8 [0.0, 3.4] | 3.6 [2.4, 5.3] | 3.5 [2.3, 5.1] | 26.5 [14.0, 43.6] |

## Taught in the reader's own voice or another reader's (clips)

Systems taught by recording. Mentions whose name another benchmark book also lists, read by a different reader: the same clip and own list, with the name taught once by the clip's reader and once by the other reader.

| System | Mentions | Right, taught by the same reader | Right, taught by another reader | Another listed name written instead |
| --- | --- | --- | --- | --- |
| ours | 65 | 100.0 [100.0, 100.0] | 96.9 [93.1, 100.0] | 1.5 [0.0, 3.4] |

## Suite: ami

AMI meetings, single distant microphone (CC BY 4.0): name-free 30 s+ stretches of meeting speech (consecutive utterances joined), each run with a 40-name list taught in the call voices. Insertions only.

0 name mentions; 119 name-free items (63.7 min). Own list per recording (its taught names, then names taught elsewhere in the suite, 40 in all); untaught = the spoken name removed.

| System | Names right | Untaught overwritten | Wrong name written | Name-free: items with a listed name inserted | Listed names inserted per minute (name-free) | Name-free: items with a name from another recording inserted | Names from other recordings inserted per minute | Ordinary-word error | Full-transcript error | Names right, no list |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| deepgram | n/a | n/a | n/a | 0.0 [0.0, 0.0] | 0.00 [0.00, 0.00] | 0.0 [0.0, 0.0] | 0.00 [0.00, 0.00] | 19.1 [17.6, 20.9] | 19.2 [17.6, 20.9] | n/a |
| elevenlabs | n/a | n/a | n/a | 0.8 [0.0, 2.5] | 0.02 [0.00, 0.05] | 0.8 [0.0, 2.5] | 0.02 [0.00, 0.05] | 16.7 [14.9, 18.2] | 16.7 [14.9, 18.3] | n/a |
| ours | n/a | n/a | n/a | 1.7 [0.0, 3.3] | 0.03 [0.00, 0.06] | 1.7 [0.0, 3.3] | 0.03 [0.00, 0.06] | 28.2 [26.5, 30.1] | 28.2 [26.5, 30.2] | n/a |
| parakeet | n/a | n/a | n/a | 9.2 [6.8, 11.8] | 0.20 [0.14, 0.28] | 9.2 [6.8, 11.8] | 0.20 [0.14, 0.28] | 15.7 [13.5, 17.9] | 15.8 [13.5, 18.0] | n/a |
| qwen | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a |
| qwen-context | n/a | n/a | n/a | 5.9 [1.7, 10.8] | 2.95 [1.08, 4.67] | 5.9 [1.7, 10.8] | 2.95 [1.08, 4.67] | 17.5 [16.1, 18.8] | 19.4 [18.9, 20.1] | n/a |
| whisper | n/a | n/a | n/a | 1.7 [0.0, 3.3] | 0.03 [0.00, 0.06] | 1.7 [0.0, 3.3] | 0.03 [0.00, 0.06] | 26.6 [25.8, 27.5] | 26.6 [25.9, 27.6] | n/a |

Paired, ours minus each system (points; per-minute rows in names per minute):

| Measure | ours − deepgram | ours − elevenlabs | ours − parakeet | ours − qwen | ours − qwen-context | ours − whisper |
| --- | --- | --- | --- | --- | --- | --- |
| Names right | n/a | n/a | n/a | n/a | n/a | n/a |
| Untaught overwritten | n/a | n/a | n/a | n/a | n/a | n/a |
| Wrong name written | n/a | n/a | n/a | n/a | n/a | n/a |
| Name-free items with an insertion | +1.7 [+0.0, +3.3] (2 vs 0) | +0.8 [-1.7, +3.3] (2 vs 1) | -7.6 [-11.7, -4.2] (2 vs 11) **holds** | n/a | -4.2 [-10.2, +1.7] (1 vs 6) | +0.0 [-2.5, +2.5] (2 vs 2) |
| Name-free items with a name from another recording | +1.7 [+0.0, +3.3] (2 vs 0) | +0.8 [-1.7, +3.3] (2 vs 1) | -7.6 [-11.7, -4.2] (2 vs 11) **holds** | n/a | -4.2 [-10.2, +1.7] (1 vs 6) | +0.0 [-2.5, +2.5] (2 vs 2) |
| Ordinary-word error | +9.0 [+8.7, +9.4] **holds** | +11.5 [+10.6, +12.2] **holds** | +12.5 [+10.4, +14.3] **holds** | n/a | +10.7 [+9.9, +11.5] **holds** | +1.6 [-0.1, +4.3] |
| Full-transcript error | +9.1 [+8.7, +9.5] **holds** | +11.5 [+10.6, +12.3] **holds** | +12.5 [+10.3, +14.4] **holds** | n/a | +8.8 [+6.8, +10.9] **holds** | +1.6 [-0.1, +4.3] |
| Listed names inserted per minute | +0.03 [+0.00, +0.06] | +0.02 [-0.03, +0.06] | -0.17 [-0.26, -0.13] **holds** | n/a | -2.92 [-4.64, -1.03] **holds** | +0.00 [-0.05, +0.05] |
| Names from other recordings inserted per minute | +0.03 [+0.00, +0.06] | +0.02 [-0.03, +0.06] | -0.17 [-0.26, -0.13] **holds** | n/a | -2.92 [-4.64, -1.03] **holds** | +0.00 [-0.05, +0.05] |

## Suite: calls

AppTek call-centre dialogues (CC BY-SA 4.0): role-played calls in 14 English accents, fictional names. A name is taught from its first mention in the call (cut by forced alignment) and tested on its other mentions; *taught by the other speaker* means the agent taught a name the customer says, or the reverse. Name-free items are 30-60 s stretches of the call with no name in them, run with the call's list.

706 name mentions; 417 name-free items (362.5 min). Own list per recording (its taught names, then names taught elsewhere in the suite, 40 in all); untaught = the spoken name removed.

| System | Names right | right: taught by the other speaker | right: taught by the same speaker | Untaught overwritten | Wrong name written | Name-free: items with a listed name inserted | Listed names inserted per minute (name-free) | Name-free: items with a name from another recording inserted | Names from other recordings inserted per minute | Ordinary-word error | Full-transcript error | Names right, no list |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| deepgram | 91.9 [89.5, 94.2] | 92.2 [88.9, 95.0] | 91.6 [87.8, 95.2] | 1.6 [0.6, 2.8] | 0.8 [0.2, 1.7] | 1.2 [0.2, 2.4] | 0.01 [0.00, 0.03] | 0.2 [0.0, 0.7] | 0.00 [0.00, 0.01] | 10.1 [9.4, 11.0] | 10.1 [9.3, 10.9] | 75.9 [71.0, 80.7] |
| elevenlabs | 95.5 [93.5, 97.2] | 96.6 [94.1, 98.6] | 94.1 [90.9, 96.8] | 1.6 [0.5, 2.9] | 1.0 [0.3, 1.8] | 1.7 [0.7, 2.9] | 0.02 [0.01, 0.03] | 0.0 [0.0, 0.0] | 0.00 [0.00, 0.00] | 9.1 [8.4, 9.9] | 9.1 [8.4, 9.9] | 83.9 [79.7, 87.4] |
| ours | 92.8 [90.8, 94.6] | 91.9 [89.0, 94.5] | 93.8 [90.9, 96.5] | 3.4 [1.7, 5.4] | 0.3 [0.0, 0.7] | 2.6 [1.0, 4.6] | 0.03 [0.01, 0.05] | 1.2 [0.2, 2.6] | 0.01 [0.00, 0.03] | 10.7 [9.8, 11.6] | 10.6 [9.8, 11.6] | 80.3 [75.9, 84.5] |
| parakeet | 88.1 [84.5, 91.3] | 88.8 [84.5, 92.3] | 87.3 [82.3, 91.8] | 13.2 [10.0, 16.8] | 4.4 [2.9, 6.0] | 15.6 [12.0, 19.4] | 0.23 [0.18, 0.30] | 13.9 [10.5, 17.5] | 0.21 [0.16, 0.27] | 10.8 [10.0, 11.6] | 10.8 [10.0, 11.6] | 74.5 [68.8, 79.6] |
| qwen | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a | 80.3 [75.6, 84.6] |
| qwen-context | 94.6 [92.6, 96.4] | 94.5 [91.8, 97.0] | 94.7 [91.5, 97.6] | 1.3 [0.5, 2.1] | 0.6 [0.1, 1.2] | 4.1 [2.2, 6.2] | 1.51 [0.64, 2.60] | 2.6 [1.2, 4.4] | 1.44 [0.59, 2.52] | 10.3 [9.4, 11.2] | 11.1 [10.1, 12.2] | 80.3 [75.6, 84.6] |
| whisper | 90.4 [87.2, 92.9] | 90.9 [87.0, 94.1] | 89.8 [85.7, 93.3] | 1.3 [0.4, 2.5] | 0.8 [0.1, 2.0] | 2.2 [1.0, 3.6] | 0.02 [0.01, 0.04] | 1.0 [0.2, 1.9] | 0.01 [0.00, 0.02] | 16.3 [15.0, 17.9] | 16.2 [14.9, 17.8] | 78.6 [73.9, 83.0] |

Paired, ours minus each system (points; per-minute rows in names per minute):

| Measure | ours − deepgram | ours − elevenlabs | ours − parakeet | ours − qwen | ours − qwen-context | ours − whisper |
| --- | --- | --- | --- | --- | --- | --- |
| Names right | +0.8 [-1.6, +3.3] (38 vs 32) | -2.7 [-4.7, -0.6] (16 vs 35) **holds** | +4.7 [+1.8, +7.7] (59 vs 26) **holds** | n/a | -1.8 [-4.0, +0.1] (20 vs 33) | +2.4 [-0.4, +5.6] (48 vs 31) |
| Untaught overwritten | +1.8 [-0.1, +3.9] (21 vs 8) | +1.8 [+0.2, +3.6] (18 vs 5) **holds** | -9.8 [-13.4, -6.5] (10 vs 79) **holds** | n/a | +2.1 [+0.4, +4.0] (21 vs 6) **holds** | +2.1 [+0.6, +3.8] (18 vs 3) **holds** |
| Wrong name written | -0.6 [-1.5, +0.3] (2 vs 6) | -0.7 [-1.5, +0.0] (1 vs 6) | -4.1 [-5.7, -2.7] (2 vs 31) **holds** | n/a | -0.3 [-0.9, +0.3] (1 vs 3) | -0.6 [-1.7, +0.2] (1 vs 5) |
| Name-free items with an insertion | +1.4 [+0.0, +3.1] (7 vs 1) | +1.0 [-0.5, +2.6] (6 vs 2) | -12.9 [-17.0, -8.9] (7 vs 61) **holds** | n/a | -1.4 [-3.6, +0.7] (6 vs 12) | +0.5 [-1.0, +2.2] (6 vs 4) |
| Name-free items with a name from another recording | +1.0 [-0.2, +2.4] (5 vs 1) | +1.2 [+0.2, +2.6] (5 vs 0) **holds** | -12.7 [-16.6, -9.0] (5 vs 58) **holds** | n/a | -1.4 [-3.6, +0.7] (5 vs 11) | +0.2 [-1.0, +1.4] (4 vs 3) |
| Ordinary-word error | +0.5 [+0.1, +1.1] **holds** | +1.5 [+1.1, +2.1] **holds** | -0.1 [-0.5, +0.4] | n/a | +0.4 [+0.2, +0.6] **holds** | -5.7 [-7.0, -4.6] **holds** |
| Full-transcript error | +0.5 [+0.1, +1.1] **holds** | +1.6 [+1.1, +2.1] **holds** | -0.1 [-0.6, +0.3] | n/a | -0.5 [-1.2, +0.2] | -5.6 [-6.9, -4.5] **holds** |
| Listed names inserted per minute | +0.02 [+0.00, +0.04] | +0.01 [-0.01, +0.03] | -0.20 [-0.27, -0.14] **holds** | n/a | -1.48 [-2.57, -0.61] **holds** | +0.01 [-0.01, +0.02] |
| Names from other recordings inserted per minute | +0.01 [-0.00, +0.03] | +0.01 [+0.00, +0.03] **holds** | -0.20 [-0.26, -0.14] **holds** | n/a | -1.42 [-2.50, -0.58] **holds** | +0.00 [-0.01, +0.02] |

## Suite: modulate

Modulate's entity benchmark, MLCommons public-meeting part (CC BY-SA 4.0; audio read from Modulate's repository, not re-hosted): an entity said in two clips of the same meeting recording is taught from the first and tested on the others (the speaker is unknown and may differ).

714 name mentions; 0 name-free items (0 min). Own list per recording (its taught names, then names taught elsewhere in the suite, 40 in all); untaught = the spoken name removed.

| System | Names right | right: public meeting | Untaught overwritten | Wrong name written | Name-free: items with a listed name inserted | Listed names inserted per minute (name-free) | Name-free: items with a name from another recording inserted | Names from other recordings inserted per minute | Ordinary-word error | Full-transcript error | Names right, no list |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| deepgram | 85.2 [79.3, 89.9] | 85.2 [79.3, 89.9] | 1.5 [0.5, 3.3] | 0.7 [0.0, 1.8] | n/a | n/a | n/a | n/a | 14.1 [11.6, 17.5] | 13.8 [11.4, 17.3] | 77.7 [62.5, 87.2] |
| elevenlabs | 93.0 [88.6, 96.3] | 93.0 [88.6, 96.3] | 0.3 [0.0, 0.8] | 0.3 [0.0, 0.8] | n/a | n/a | n/a | n/a | 11.6 [9.7, 14.4] | 11.1 [9.3, 13.8] | 83.1 [69.1, 91.2] |
| ours | 88.7 [84.0, 92.6] | 88.7 [84.0, 92.6] | 0.4 [0.0, 1.1] | 0.4 [0.0, 1.0] | n/a | n/a | n/a | n/a | 12.1 [10.1, 15.1] | 11.9 [9.9, 14.8] | 84.0 [76.5, 89.2] |
| parakeet | 81.1 [65.3, 89.7] | 81.1 [65.3, 89.7] | 0.6 [0.1, 1.2] | 0.4 [0.0, 0.9] | n/a | n/a | n/a | n/a | 10.8 [8.4, 14.3] | 10.6 [8.2, 13.9] | 80.8 [65.0, 89.5] |
| qwen | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a | 83.8 [75.0, 89.7] |
| qwen-context | 89.6 [84.5, 93.4] | 89.6 [84.5, 93.4] | 0.8 [0.1, 1.9] | 0.7 [0.1, 1.6] | n/a | n/a | n/a | n/a | 11.5 [9.4, 14.5] | 11.1 [9.1, 14.0] | 83.8 [75.0, 89.7] |
| whisper | 83.6 [72.2, 90.2] | 83.6 [72.2, 90.2] | 0.8 [0.2, 1.7] | 0.6 [0.1, 1.3] | n/a | n/a | n/a | n/a | 16.4 [14.0, 20.3] | 17.6 [14.5, 23.1] | 82.2 [66.5, 90.8] |

Paired, ours minus each system (points; per-minute rows in names per minute):

| Measure | ours − deepgram | ours − elevenlabs | ours − parakeet | ours − qwen | ours − qwen-context | ours − whisper |
| --- | --- | --- | --- | --- | --- | --- |
| Names right | +3.5 [+0.9, +6.6] (50 vs 25) **holds** | -4.3 [-6.9, -1.7] (16 vs 47) **holds** | +7.6 [+0.8, +20.6] (76 vs 22) **holds** | n/a | -1.0 [-3.5, +1.9] (24 vs 31) | +5.0 [+0.2, +13.7] (64 vs 28) **holds** |
| Untaught overwritten | -1.1 [-2.5, -0.2] (1 vs 9) **holds** | +0.1 [+0.0, +0.6] (1 vs 0) | -0.1 [-0.8, +0.6] (2 vs 3) | n/a | -0.4 [-1.3, +0.2] (1 vs 4) | -0.4 [-1.4, +0.4] (2 vs 5) |
| Wrong name written | -0.3 [-1.0, +0.3] (1 vs 3) | +0.1 [+0.0, +0.5] (2 vs 1) | +0.0 [-0.6, +0.6] (2 vs 2) | n/a | -0.3 [-0.8, +0.0] (1 vs 3) | -0.1 [-0.9, +0.5] (2 vs 3) |
| Name-free items with an insertion | n/a | n/a | n/a | n/a | n/a | n/a |
| Name-free items with a name from another recording | n/a | n/a | n/a | n/a | n/a | n/a |
| Ordinary-word error | -2.0 [-3.0, -1.0] **holds** | +0.5 [-0.1, +1.5] | +1.3 [-0.1, +2.1] | n/a | +0.6 [-0.0, +1.3] | -4.3 [-6.7, -2.1] **holds** |
| Full-transcript error | -1.9 [-3.0, -0.9] **holds** | +0.8 [+0.2, +1.8] **holds** | +1.3 [-0.1, +2.2] | n/a | +0.8 [+0.2, +1.6] **holds** | -5.7 [-9.8, -3.0] **holds** |
| Listed names inserted per minute | n/a | n/a | n/a | n/a | n/a | n/a |
| Names from other recordings inserted per minute | n/a | n/a | n/a | n/a | n/a | n/a |

## Suite: svq

Google Simple Voice Questions (CC BY 4.0): each question is read by about 20 people. A name is taught from one person's clean reading and tested on four other people's readings, in clean, background-speech, media-noise and traffic-noise recordings. Name-free items are questions without names.

1420 name mentions; 320 name-free items (24.5 min). Own list per recording (its taught names, then names taught elsewhere in the suite, 40 in all); untaught = the spoken name removed.

| System | Names right | right: background_speech | right: clean | right: media_noise | right: traffic_noise | Untaught overwritten | Wrong name written | Name-free: items with a listed name inserted | Listed names inserted per minute (name-free) | Name-free: items with a name from another recording inserted | Names from other recordings inserted per minute | Ordinary-word error | Full-transcript error | Names right, no list |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| deepgram | 89.4 [87.2, 91.4] | 89.0 [85.5, 92.3] | 93.0 [89.9, 95.7] | 93.5 [90.8, 96.0] | 82.0 [77.6, 86.2] | 1.3 [0.7, 2.1] | 0.6 [0.2, 1.0] | 0.0 [0.0, 0.0] | 0.00 [0.00, 0.00] | 0.0 [0.0, 0.0] | 0.00 [0.00, 0.00] | 17.4 [15.5, 19.3] | 15.2 [13.6, 16.9] | 65.9 [61.9, 69.8] |
| elevenlabs | 98.6 [97.7, 99.3] | 97.7 [96.1, 99.2] | 99.4 [98.6, 100.0] | 99.2 [98.1, 100.0] | 98.0 [96.4, 99.4] | 0.6 [0.1, 1.3] | 0.2 [0.0, 0.5] | 0.6 [0.0, 1.6] | 0.08 [0.00, 0.21] | 0.6 [0.0, 1.6] | 0.08 [0.00, 0.21] | 14.5 [12.2, 17.0] | 12.5 [10.5, 14.6] | 83.5 [80.4, 86.5] |
| ours | 91.4 [89.6, 93.2] | 93.2 [90.6, 95.7] | 92.1 [88.7, 95.2] | 95.8 [93.5, 97.8] | 84.5 [80.3, 88.5] | 0.3 [0.1, 0.6] | 0.3 [0.1, 0.6] | 0.0 [0.0, 0.0] | 0.00 [0.00, 0.00] | 0.0 [0.0, 0.0] | 0.00 [0.00, 0.00] | 8.1 [7.0, 9.2] | 7.8 [6.8, 8.9] | 76.1 [72.2, 79.8] |
| parakeet | 85.8 [83.5, 88.2] | 79.4 [75.0, 83.7] | 91.5 [88.6, 94.4] | 87.6 [83.9, 91.0] | 84.8 [80.9, 88.5] | 13.2 [10.9, 15.5] | 6.1 [4.7, 7.7] | 8.1 [5.0, 11.6] | 1.22 [0.74, 1.78] | 8.1 [5.0, 11.6] | 1.22 [0.74, 1.78] | 16.3 [14.5, 18.2] | 15.3 [13.7, 17.0] | 67.4 [63.6, 71.1] |
| qwen | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a | 78.2 [74.5, 81.7] |
| qwen-context | 95.4 [93.7, 97.0] | 97.5 [95.7, 98.9] | 95.5 [93.1, 97.7] | 96.1 [93.9, 98.0] | 92.7 [89.7, 95.3] | 0.7 [0.3, 1.3] | 0.6 [0.2, 1.2] | 0.0 [0.0, 0.0] | 0.00 [0.00, 0.00] | 0.0 [0.0, 0.0] | 0.00 [0.00, 0.00] | 6.4 [5.5, 7.5] | 8.0 [6.0, 10.4] | 78.2 [74.5, 81.7] |
| whisper | 80.1 [76.8, 83.1] | 78.6 [74.3, 82.7] | 83.9 [80.1, 87.7] | 83.7 [79.7, 87.5] | 74.1 [69.5, 78.7] | 0.2 [0.0, 0.6] | 0.2 [0.0, 0.6] | 0.0 [0.0, 0.0] | 0.00 [0.00, 0.00] | 0.0 [0.0, 0.0] | 0.00 [0.00, 0.00] | 10.3 [9.2, 11.5] | 9.1 [8.1, 10.1] | 73.7 [70.1, 77.3] |

Paired, ours minus each system (points; per-minute rows in names per minute):

| Measure | ours − deepgram | ours − elevenlabs | ours − parakeet | ours − qwen | ours − qwen-context | ours − whisper |
| --- | --- | --- | --- | --- | --- | --- |
| Names right | +2.0 [-0.1, +4.3] (93 vs 64) | -7.2 [-9.0, -5.4] (8 vs 110) **holds** | +5.6 [+3.2, +8.0] (152 vs 73) **holds** | n/a | -4.0 [-5.8, -2.2] (30 vs 87) **holds** | +11.3 [+8.2, +14.6] (218 vs 57) **holds** |
| Untaught overwritten | -1.1 [-1.8, -0.4] (3 vs 18) **holds** | -0.4 [-1.0, +0.1] (3 vs 8) | -12.9 [-15.2, -10.7] (2 vs 185) **holds** | n/a | -0.4 [-1.0, +0.1] (3 vs 9) | +0.1 [-0.2, +0.4] (3 vs 2) |
| Wrong name written | -0.3 [-0.7, +0.1] (3 vs 7) | +0.1 [-0.3, +0.4] (4 vs 3) | -5.8 [-7.4, -4.4] (4 vs 87) **holds** | n/a | -0.4 [-1.0, +0.2] (4 vs 9) | +0.1 [-0.4, +0.5] (4 vs 3) |
| Name-free items with an insertion | +0.0 [+0.0, +0.0] (0 vs 0) | -0.6 [-1.6, +0.0] (0 vs 2) | -8.1 [-11.6, -5.0] (0 vs 26) **holds** | n/a | +0.0 [+0.0, +0.0] (0 vs 0) | +0.0 [+0.0, +0.0] (0 vs 0) |
| Name-free items with a name from another recording | +0.0 [+0.0, +0.0] (0 vs 0) | -0.6 [-1.6, +0.0] (0 vs 2) | -8.1 [-11.6, -5.0] (0 vs 26) **holds** | n/a | +0.0 [+0.0, +0.0] (0 vs 0) | +0.0 [+0.0, +0.0] (0 vs 0) |
| Ordinary-word error | -9.3 [-11.0, -7.6] **holds** | -6.5 [-8.9, -4.2] **holds** | -8.2 [-9.9, -6.6] **holds** | n/a | +1.6 [+0.8, +2.5] **holds** | -2.2 [-3.4, -1.1] **holds** |
| Full-transcript error | -7.4 [-9.0, -5.9] **holds** | -4.7 [-6.8, -2.7] **holds** | -7.5 [-9.0, -6.0] **holds** | n/a | -0.2 [-2.4, +1.7] | -1.3 [-2.3, -0.2] **holds** |
| Listed names inserted per minute | +0.00 [+0.00, +0.00] | -0.08 [-0.21, +0.00] | -1.22 [-1.78, -0.74] **holds** | n/a | +0.00 [+0.00, +0.00] | +0.00 [+0.00, +0.00] |
| Names from other recordings inserted per minute | +0.00 [+0.00, +0.00] | -0.08 [-0.21, +0.00] | -1.22 [-1.78, -0.74] **holds** | n/a | +0.00 [+0.00, +0.00] | +0.00 [+0.00, +0.00] |

## Speed and cost

| System | Machine | Clip latency p50 / p90 (s) | Real-time factor (clips) | Cost per audio hour: nominal | Cost per audio hour: this workload |
| --- | --- | --- | --- | --- | --- |
| deepgram | Apple M4 Max | 0.41 / 0.67 | 0.044 | $0.336 with a list, $0.258 without (2026-10-13) | ami: no list $0.258; ami: own list $0.336; calls: no list $0.258; calls: own list $0.336; chapters $0.310; clips, no list $0.258; clips, own list $0.336; modulate: no list $0.258; modulate: own list $0.336; svq: no list $0.258; svq: own list $0.336 |
| elevenlabs | Apple M4 Max | 1.07 / 1.75 | 0.114 | $0.270 with a list, $0.220 without (2026-10-13) | ami: no list $0.220; ami: own list $0.270; calls: no list $0.220; calls: own list $0.270; chapters $0.253; clips, all-books list $0.522; clips, no list $0.220; clips, own list $0.399; modulate: no list $0.220; modulate: own list $0.270; svq: no list $0.220; svq: own list $0.270 |
| ours | NVIDIA GeForce RTX 4090, 580.126.09, 24564 MiB | 2.34 / 3.41 | 0.223 | $0.198 | measured real-time factor 0.223 x $0.89/h for the machine |
| parakeet | NVIDIA GeForce RTX 4090, 580.126.09, 24564 MiB | 0.23 / 0.43 | 0.029 | $0.026 | measured real-time factor 0.029 x $0.89/h for the machine |
| qwen | NVIDIA GeForce RTX 4090, 580.159.04, 24564 MiB | 0.47 / 0.64 | 0.046 | $0.041 | measured real-time factor 0.046 x $0.89/h for the machine |
| qwen-context | NVIDIA GeForce RTX 4090, 580.126.09, 24564 MiB | 0.69 / 1.65 | 0.089 | $0.079 | measured real-time factor 0.089 x $0.89/h for the machine |
| whisper | NVIDIA GeForce RTX 4090, 580.159.04, 24564 MiB | 0.34 / 0.46 | 0.033 | $0.030 | measured real-time factor 0.033 x $0.89/h for the machine |

## Paired differences: ours minus each system, same items

Points, 95% bootstrap interval over books (clips) or chapters; **holds** when the interval excludes zero. In brackets: items only the first system / only the second got (no item-level test; it would ignore the clustering).

| Measure | ours − deepgram | ours − elevenlabs | ours − parakeet | ours − qwen | ours − qwen-context | ours − whisper |
| --- | --- | --- | --- | --- | --- | --- |
| Names right, own list | +21.4 [+8.0, +33.2] (247 vs 10) **holds** | +4.4 [+0.5, +7.6] (67 vs 18) **holds** | +18.2 [+12.3, +23.3] (215 vs 14) **holds** | n/a | +32.8 [+22.9, +40.5] (370 vs 7) **holds** | +22.3 [+9.1, +31.6] (259 vs 12) **holds** |
|   invented | +5.6 [+2.2, +8.2] (35 vs 7) **holds** | +1.2 [-1.6, +4.1] (15 vs 9) | +15.4 [+8.0, +25.1] (85 vs 8) **holds** | n/a | +21.4 [+16.8, +27.4] (111 vs 4) **holds** | +5.4 [+2.4, +9.1] (35 vs 8) **holds** |
|   traditional | +34.4 [+18.2, +46.5] (212 vs 3) **holds** | +7.1 [+1.6, +10.5] (52 vs 9) **holds** | +20.4 [+14.4, +25.1] (130 vs 6) **holds** | n/a | +42.1 [+35.5, +48.6] (259 vs 3) **holds** | +36.2 [+29.7, +41.5] (224 vs 4) **holds** |
| Untaught overwritten, own list | -1.4 [-4.4, +1.3] (47 vs 62) | +3.7 [+1.0, +6.4] (51 vs 10) **holds** | -20.1 [-26.8, -11.3] (28 vs 251) **holds** | n/a | +2.7 [+0.3, +5.1] (57 vs 27) **holds** | +5.4 [+2.0, +8.7] (65 vs 5) **holds** |
| Wrong name written, own list | -2.3 [-3.8, -0.8] (7 vs 32) **holds** | -1.0 [-1.7, -0.2] (6 vs 17) **holds** | -6.8 [-11.0, -2.1] (4 vs 79) **holds** | n/a | -2.2 [-3.5, -0.7] (8 vs 32) **holds** | -0.2 [-0.5, +0.2] (9 vs 11) |
| Name-free inserted, own list | +2.2 [-1.2, +8.1] (14 vs 5) | +3.7 [+0.0, +9.6] (16 vs 1) | -3.2 [-8.3, +3.9] (13 vs 26) | n/a | +3.7 [+0.0, +9.6] (16 vs 1) | +3.7 [+0.0, +9.6] (15 vs 0) |
| Ordinary-word error, own list | -1.4 [-2.1, -0.6] **holds** | +1.0 [+0.7, +1.3] **holds** | -0.8 [-1.2, -0.3] **holds** | n/a | -0.9 [-1.7, -0.2] **holds** | -0.3 [-0.6, +0.2] |
| Full-transcript error, own list | -1.5 [-2.2, -0.6] **holds** | +1.0 [+0.7, +1.3] **holds** | -1.1 [-1.6, -0.4] **holds** | n/a | -1.1 [-2.2, -0.2] **holds** | -0.3 [-0.6, +0.2] |
| Names right, all-books list | n/a | +5.5 [+1.2, +9.0] (85 vs 24) **holds** | +26.2 [+20.8, +31.2] (306 vs 16) **holds** | n/a | +38.5 [+31.2, +43.8] (434 vs 8) **holds** | n/a |
| Untaught overwritten, all-books list | n/a | +8.6 [+4.9, +11.8] (106 vs 11) **holds** | -30.1 [-34.0, -25.2] (47 vs 380) **holds** | n/a | +7.0 [+2.5, +10.7] (106 vs 28) **holds** | n/a |
| Chapters: names right | +16.0 [+7.9, +23.4] (57 vs 2) **holds** | +0.9 [-1.3, +4.4] (5 vs 2) | +7.6 [+1.1, +12.2] (28 vs 2) **holds** | +77.3 [+61.7, +89.3] (265 vs 0) **holds** | +10.2 [+4.6, +14.4] (37 vs 2) **holds** | +22.4 [+6.1, +44.6] (78 vs 1) **holds** |
| Chapters: untaught overwritten | -3.5 [-7.2, +0.0] (0 vs 6) | +0.0 [+0.0, +0.0] (0 vs 0) | -2.9 [-6.8, +0.0] (0 vs 5) | +0.6 [+0.0, +2.2] (1 vs 0) | -1.2 [-2.7, +0.0] (0 vs 2) | +0.0 [+0.0, +0.0] (0 vs 0) |
| Chapters: ordinary-word error | -0.5 [-0.7, -0.2] **holds** | +0.7 [+0.3, +1.3] **holds** | -0.0 [-0.6, +0.5] | -1.7 [-2.6, -1.0] **holds** | -0.2 [-0.6, +0.1] | -0.8 [-1.5, -0.3] **holds** |
| Chapters: full-transcript error | -0.5 [-0.7, -0.3] **holds** | +0.7 [+0.3, +1.2] **holds** | -0.1 [-0.7, +0.4] | -1.8 [-2.7, -1.1] **holds** | -0.7 [-1.7, -0.1] **holds** | -0.8 [-1.5, -0.3] **holds** |
| Chapters: wrong names per minute | -0.03 [-0.09, +0.02] | +0.01 [+0.00, +0.02] | +0.00 [+0.00, +0.00] | +0.01 [+0.00, +0.02] | -0.82 [-2.04, -0.02] **holds** | +0.00 [+0.00, +0.00] |

## How each system took the names

- **deepgram**: keyterm; limits: 500 keyterm tokens per request (Deepgram's tokenizer, unpublished); fit: the longest prefix of the list (most frequent first) the service accepts, found by binary search with half a second of silence (refused requests are not billed)
- **elevenlabs**: keyterms; limits: <=1000 terms, each <50 chars and <=5 words, no <>{}[]\; fit: drop terms that break a per-term rule, then keep the first 1000 (most frequent in the book first)
- **ours**: spotter shortlist of the whole list -> writer prompt + taught recordings; limits: none; fit: no limit: the spotter ranks every name
- **parakeet**: GPU phrase boosting: decoding.greedy.boosting_tree.key_phrases_list; limits: none; fit: all names
- **qwen**: none; limits: none; fit: no list
- **qwen-context**: context (system prompt): names joined by ', '; limits: none; fit: all names
- **whisper**: prompt_ids (initial prompt): names joined by ', '; limits: 223 prompt tokens; fit: longest prefix of the list (most frequent first) within the token limit

## Runs

- **deepgram**: `deepgram` {"service": "Deepgram pre-recorded", "endpoint": "https://api.deepgram.com/v1/listen", "model": "nova-3", "language": "en", "smart_format": true, "list_feature": "keyterm", "limits": "500 keyterm tokens per request (Deepgram's tokenizer, unpublished)", "fit": "the longest prefix of the list (most frequent first) the service accepts, found by binary search with half a second of silence (refused requests are not billed)"}; machine {"platform": "macOS-26.3.1-arm64-arm-64bit", "machine": "arm64", "python": "3.12.13", "cpu": "Apple M4 Max", "memory_gb": 128.0, "os": "macOS 26.3.1 (25D771280a)"}; code 26ee0b82325a4d2d78569bd23a6d6ae6b44d2cd7-dirty; dataset virgil-coach/own-names-bench@v1.2.0 (fingerprint 1625ef57df22); commands ['/Users/jameslal/workspace/jl/own-names-bench/.venv/bin/bench run --system deepgram', '/Users/jameslal/workspace/jl/own-names-bench/.venv/bin/bench run --system deepgram', '/Users/jameslal/workspace/jl/own-names-bench/.venv/bin/bench run --system deepgram --only suite/calls']; started 2026-10-13T20:02:28+00:00
- **elevenlabs**: `elevenlabs` {"service": "ElevenLabs Speech to Text", "endpoint": "https://api.elevenlabs.io/v1/speech-to-text", "model_id": "scribe_v2", "language_code": "en", "tag_audio_events": false, "temperature": 0.0, "seed": 0, "list_feature": "keyterms", "limits": "<=1000 terms, each <50 chars and <=5 words, no <>{}[]\\", "fit": "drop terms that break a per-term rule, then keep the first 1000 (most frequent in the book first)"}; machine {"platform": "macOS-26.3.1-arm64-arm-64bit", "machine": "arm64", "python": "3.12.13", "cpu": "Apple M4 Max", "memory_gb": 128.0, "os": "macOS 26.3.1 (25D771280a)"}; code 17f62b29b83abe936b33887ad1e27b4754127a4f; dataset virgil-coach/own-names-bench@v1.2.0 (fingerprint 1625ef57df22); commands ['/Users/jameslal/workspace/jl/own-names-bench/.venv/bin/bench run --system elevenlabs', '/Users/jameslal/workspace/jl/own-names-bench/.venv/bin/bench run --system elevenlabs', '/Users/jameslal/workspace/jl/own-names-bench/.venv/bin/bench run --system elevenlabs', '/Users/jameslal/workspace/jl/own-names-bench/.venv/bin/bench run --system elevenlabs --only suite/calls']; started 2026-10-13T20:02:34+00:00
- **ours**: `ours` {"runtime": "PyTorch reference (own_names_bench/ours_ref)", "device": "cuda", "torch": "2.14.1+cu130", "transformers": "5.19.0", "cuda_device": "NVIDIA RTX PRO 6000 Blackwell Server Edition", "base": "Qwen/Qwen3-ASR-1.7B-hf@bcd2b5b7f32b480ab5790554cfa8347f246a14f3", "adapter": "virgil-coach/own-names-qwen3-asr@e02efd5e0db0f357f7ada3caf18e1ca293528098/audio-text-note", "adapter_version": "v0.3.0", "adapter_sha256": "67dbabef14851e89ad1b62d509e595713d4a2b6254fbc26cdb700fca1e097f55", "dtype": "float32", "decoding": "greedy, at most 200 new tokens", "spotter_phon": "facebook/wav2vec2-lv-60-espeak-cv-ft@0c380a877907192512147c466ead03055f200cad", "spotter_wavlm": "microsoft/wavlm-base-plus@98fd61b9c652129c839c0a25a05987d8f59256a4", "g2p": "own_names_bench/ours_ref/g2p.json (espeak-ng 1.52.0, every benchmark name)", "shortlist": 10, "prune": "off", "gate": "none", "windows": "Detail Keeper Segmenter (pause 0.45 s after 2 s, cap 8 s), fed 0.1 s at a time", "list_feature": "spotter shortlist of the whole list -> writer prompt + taught recordings", "fit": "no limit: the spotter ranks every name", "platform": "Linux-6.8.0-138-generic-x86_64-with-glibc2.35"}; machine {"platform": "Linux-6.8.0-71-generic-x86_64-with-glibc2.35", "machine": "x86_64", "python": "3.12.15", "cpu": "AMD EPYC 7443 24-Core Processor", "memory_gb": 251.5, "os": "Ubuntu 22.04.5 LTS", "gpu": "NVIDIA GeForce RTX 4090, 580.126.09, 24564 MiB"}; code 26ee0b8; dataset virgil-coach/own-names-bench@v1.2.0 (fingerprint 1625ef57df22); commands ['/gpu-cli-workspaces/jameslal/path-3172b95136962215/.pod/venv-qwen/bin/bench run --system ours --label ours-rtx4090 --hourly-usd 0.89', '/gpu-cli-workspaces/jameslal/path-3172b95136962215/.pod/venv-qwen/bin/bench run --system ours --label ours-rtx4090 --hourly-usd 0.89', '/gpu-cli-workspaces/jameslal/path-3172b95136962215/.pod/venv-qwen/bin/bench run --system ours --label ours-rtx4090 --hourly-usd 0.89', '/gpu-cli-workspaces/jameslal/path-3172b95136962215/.pod/venv-qwen/bin/bench run --system ours --label ours-rtx4090 --hourly-usd 0.89', '/gpu-cli-workspaces/jameslal/path-3172b95136962215/.pod/venv-qwen/bin/bench run --system ours --label ours-rtx4090 --hourly-usd 1.69 --only suite/calls', '/gpu-cli-workspaces/jameslal/path-3172b95136962215/.pod/venv-qwen/bin/bench run --system ours --label ours-p --hourly-usd 1.79 --only suite/modulate/clip/named_entities-MLCommons_TestPortion-gov,suite/modulate/clip/named_entities-MLCommons_TestPortion-hrs,suite/modulate/clip/named_entities-MLCommons_TestPortion-iRe,suite/modulate/clip/named_entities-MLCommons_TestPortion-kin,suite/modulate/clip/named_entities-MLCommons_TestPortion-tal']; started 2026-10-13T21:18:29+00:00
- **parakeet**: `parakeet` {"model": "nvidia/parakeet-tdt-0.6b-v2@ae9ad07059c7c739ffaf932226a8fe64ae2620b0", "runtime": "NeMo 3.0.0, torch 2.14.1+cu130", "device": "cuda", "decoding": "greedy_batch (TDT label looping)", "long_form": "over 20 min: rel_pos_local_attn [256, 256]", "list_feature": "GPU phrase boosting: decoding.greedy.boosting_tree.key_phrases_list", "boosting": {"boosting_tree_alpha": 2.0, "context_score": 1.0, "depth_scaling": 2.0, "alpha_chosen_on": "the chapters task: grid 0.25, 0.5, 1, 2, 4; 2 had the most names right less untaught overwritten (92.7% - 4.1%)"}, "fit": "all names"}; machine {"platform": "Linux-6.8.0-71-generic-x86_64-with-glibc2.35", "machine": "x86_64", "python": "3.12.15", "cpu": "AMD EPYC 7443 24-Core Processor", "memory_gb": 251.5, "os": "Ubuntu 22.04.5 LTS", "gpu": "NVIDIA GeForce RTX 4090, 580.126.09, 24564 MiB"}; code 8d8f168; dataset virgil-coach/own-names-bench@v1.1.0 (fingerprint 1625ef57df22); commands ['/gpu-cli-workspaces/jameslal/path-3b0609d92f9af37f/.pod/venv-parakeet/bin/bench run --system parakeet --label parakeet-a100 --hourly-usd 1.79', '/gpu-cli-workspaces/jameslal/path-3172b95136962215/.pod/venv-parakeet/bin/bench run --system parakeet --label parakeet-a100 --hourly-usd 0.89', '/gpu-cli-workspaces/jameslal/path-bdd62f593dfa015e/.pod/venv-parakeet/bin/bench run --system parakeet --label parakeet-d --hourly-usd 0.86', '/gpu-cli-workspaces/jameslal/path-bdd62f593dfa015e/.pod/venv-parakeet/bin/bench run --system parakeet --label parakeet-d --hourly-usd 0.86']; started 2026-10-13T22:12:57+00:00
- **qwen**: `qwen` {"model": "Qwen/Qwen3-ASR-1.7B-hf@bcd2b5b7f32b480ab5790554cfa8347f246a14f3", "runtime": "transformers 5.19.0, torch 2.14.1+cu130", "device": "cuda", "dtype": "float32", "decoding": "greedy, language English, at most 200 new tokens", "long_form": "chapters cut by the Detail Keeper window cutter", "list_feature": "none", "fit": "no list"}; machine {"platform": "Linux-6.8.0-124-generic-x86_64-with-glibc2.35", "machine": "x86_64", "python": "3.12.15", "cpu": "AMD Ryzen 9 7950X 16-Core Processor", "memory_gb": 187.8, "os": "Ubuntu 22.04.5 LTS", "gpu": "NVIDIA GeForce RTX 4090, 580.159.04, 24564 MiB"}; code 6a1f6ff; dataset virgil-coach/own-names-bench@v1.2.0 (fingerprint 1625ef57df22); commands ['/gpu-cli-workspaces/jameslal/path-3172b95136962215/.pod/venv-qwen/bin/bench run --system qwen --label qwen-rtx4090 --hourly-usd 0.89', '/gpu-cli-workspaces/jameslal/path-1cce88ab5e6729ec/.pod/venv-qwen/bin/bench run --system qwen --label qwen-rtx4090 --hourly-usd 1.79', '/gpu-cli-workspaces/jameslal/path-1c6919ab0d0f4cf1/.pod/venv-qwen/bin/bench run --system qwen --label qwen-h2 --hourly-usd 1.0 --only suite/calls']; started 2026-10-13T21:21:57+00:00
- **qwen-context**: `qwen-context` {"model": "Qwen/Qwen3-ASR-1.7B-hf@bcd2b5b7f32b480ab5790554cfa8347f246a14f3", "runtime": "transformers 5.19.0, torch 2.14.1+cu130", "device": "cuda", "dtype": "float32", "decoding": "greedy, language English, at most 200 new tokens", "long_form": "chapters cut by the Detail Keeper window cutter", "list_feature": "context (system prompt): names joined by ', '", "fit": "all names"}; machine {"platform": "Linux-6.8.0-71-generic-x86_64-with-glibc2.35", "machine": "x86_64", "python": "3.12.15", "cpu": "AMD EPYC 7443 24-Core Processor", "memory_gb": 251.5, "os": "Ubuntu 22.04.5 LTS", "gpu": "NVIDIA GeForce RTX 4090, 580.126.09, 24564 MiB"}; code 8d8f168; dataset virgil-coach/own-names-bench@v1.1.0 (fingerprint 1625ef57df22); commands ['/gpu-cli-workspaces/jameslal/path-3172b95136962215/.pod/venv-qwen/bin/bench run --system qwen-context --label qwen-context-rtx4090 --hourly-usd 0.89', '/gpu-cli-workspaces/jameslal/path-3172b95136962215/.pod/venv-qwen/bin/bench run --system qwen-context --label qwen-context-rtx4090 --hourly-usd 0.89', '/gpu-cli-workspaces/jameslal/path-86f6c6515c3164a6/.pod/venv-qwen/bin/bench run --system qwen-context --label qwen-context-f --hourly-usd 0.86 --only suite/svq,suite/ami,suite/modulate', '/gpu-cli-workspaces/jameslal/path-86f6c6515c3164a6/.pod/venv-qwen/bin/bench run --system qwen-context --label qwen-context-e --hourly-usd 0.86 --only suite/calls', '/gpu-cli-workspaces/jameslal/path-86f6c6515c3164a6/.pod/venv-qwen/bin/bench run --system qwen-context --label qwen-context-f2 --hourly-usd 1.0 --only suite/calls,suite/modulate']; started 2026-10-13T21:51:37+00:00
- **whisper**: `whisper` {"model": "openai/whisper-large-v3@06f233fe06e710322aca913c1bc4249a0d71fce1", "runtime": "transformers 5.19.0, torch 2.14.1+cu130", "device": "cuda", "dtype": "float16", "decoding": "greedy, language en, task transcribe", "long_form": "chapters cut by the Detail Keeper window cutter; every window decoded with the prompt", "list_feature": "prompt_ids (initial prompt): names joined by ', '", "limits": "223 prompt tokens", "fit": "longest prefix of the list (most frequent first) within the token limit"}; machine {"platform": "Linux-6.8.0-124-generic-x86_64-with-glibc2.35", "machine": "x86_64", "python": "3.12.15", "cpu": "AMD Ryzen 9 7950X 16-Core Processor", "memory_gb": 187.8, "os": "Ubuntu 22.04.5 LTS", "gpu": "NVIDIA GeForce RTX 4090, 580.159.04, 24564 MiB"}; code 1ba0dc2da466d4576e3b34d2efb94f41116f662b; dataset virgil-coach/own-names-bench@v1.0.0 (fingerprint 1625ef57df22); commands ['/gpu-cli-workspaces/jameslal/path-3172b95136962215/.pod/venv-whisper/bin/bench run --system whisper --label whisper-rtx4090 --hourly-usd 0.89', '/gpu-cli-workspaces/jameslal/path-3172b95136962215/.pod/venv-whisper/bin/bench run --system whisper --label whisper-chapterwin-rtx4090 --hourly-usd 0.89 --only chapter/', '/gpu-cli-workspaces/jameslal/path-d2b17c513287cc07/.pod/venv-whisper/bin/bench run --system whisper --label whisper-d --hourly-usd 0.86', '/gpu-cli-workspaces/jameslal/path-86f6c6515c3164a6/.pod/venv-whisper/bin/bench run --system whisper --label whisper-f2 --hourly-usd 1.0 --only suite/calls,suite/modulate']; started 2026-10-13T23:58:25+00:00; note: clip passes from the first run; chapter passes rerun with the windowed long-form (see config.long_form)

## Reproducibility: the same system on two machines

Identical text: passes whose transcript is the same string. Word difference: word error of one run's text against the other's. Paired difference: first minus second, same items, 95% bootstrap interval over books.

| Runs | Machines | Passes | Identical text | Word difference | Same shortlist (windows) | Items with the same outcome: right (own list) / overwritten | Names right (own list), difference | Untaught overwritten, difference | Chapter names right, difference |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| ours vs ours-mlx-macmini | NVIDIA GeForce RTX 4090, 580.126.09, 24564 MiB vs Apple M5 Pro | 6550 | 5361 (81.8%) | 0.55% | 4800/14182 (33.8%) | 1095/1107 / 1098/1107 | +0.00 [-0.43, +0.54] (6 vs 6) | +0.27 [-0.22, +0.67] (6 vs 3) | -0.29 [-1.05, +0.00] (0 vs 1) |
| whisper vs whisper-a100 | NVIDIA GeForce RTX 4090, 580.159.04, 24564 MiB vs NVIDIA A100-SXM4-80GB, 595.91.07, 81920 MiB | 4025 | 4007 (99.6%) | 0.01% | n/a | 1107/1107 / 1107/1107 | +0.00 [+0.00, +0.00] (0 vs 0) | +0.00 [+0.00, +0.00] (0 vs 0) | n/a |
