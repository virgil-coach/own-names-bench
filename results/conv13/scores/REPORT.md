# own-names-bench v1.2.0 results

Scored 2026-10-27. Rates in percent with 95% intervals from a bootstrap over clusters: books for clips (each clip book has one reader), chapters for chapters. Name matches are one to one. Every system got the same names in the same order through its own custom-vocabulary feature.

## Runs: expected, completed and failed passes

| Run | System | List variants | Expected | Completed | Failed | Stale (made from an older list) | Complete |
| --- | --- | --- | --- | --- | --- | --- | --- |
| conv13-elevenlabs-2026-10-16 | elevenlabs | none, own, all | 9373 | 9373 | 0 | 0 | yes |
| conv13-v7c-mlx | ours-mlx | none, own | 9373 | 9373 | 0 | 0 | yes |

## Clips, the book's own name list

| System | Names right, invented | Names right, traditional | Names right, all | Untaught overwritten | Wrong name written | Name-free: a listed name inserted | Ordinary-word error | Full-transcript error | Spoken name among the names sent |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| conv13-elevenlabs-2026-10-16 | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a | its feature cannot take this list |
| conv13-v7c-mlx | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a | its feature cannot take this list |

## Clips, all-books list (902 entries)

| System | Names right, invented | Names right, traditional | Names right, all | Untaught overwritten | Wrong name written | Name-free: a listed name inserted | Ordinary-word error | Full-transcript error | Spoken name among the names sent |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| conv13-elevenlabs-2026-10-16 | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a | its feature cannot take this list |
| conv13-v7c-mlx | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a | its feature cannot take this list |

## Clips, no list

| System | Names right, invented | Names right, traditional | Names right, all | Name-free: a book name inserted | Ordinary-word error | Full-transcript error |
| --- | --- | --- | --- | --- | --- | --- |

## Continuous chapters

| System | Names right (taught) | same reader taught it | another reader taught it | Wrong names per minute | Untaught overwritten | Ordinary-word error | Full-transcript error | Names right, no list |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| conv13-elevenlabs-2026-10-16 | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a |
| conv13-v7c-mlx | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a |

## Suite: conv13-conv



132 name mentions; 200 name-free items (25.7 min). Own list per recording (its taught names, then names taught elsewhere in the suite, 40 in all); untaught = the spoken name removed.

| System | Names right | right: name never seen in training | right: name seen in training | Untaught overwritten | Wrong name written | Name-free: items with a listed name inserted | Listed names inserted per minute (name-free) | Name-free: items with a name from another recording inserted | Names from other recordings inserted per minute | Ordinary-word error | Full-transcript error | Names right, no list |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| conv13-elevenlabs-2026-10-16 | 97.7 [94.8, 100.0] | 96.3 [88.0, 100.0] | 98.1 [95.1, 100.0] | 0.8 [0.0, 2.4] | 1.5 [0.0, 3.9] | 0.0 [0.0, 0.0] | 0.00 [0.00, 0.00] | 0.0 [0.0, 0.0] | 0.00 [0.00, 0.00] | 7.0 [6.0, 8.1] | 6.8 [5.8, 7.9] | 96.2 [92.5, 99.2] |
| conv13-v7c-mlx | 98.5 [96.2, 100.0] | 96.3 [88.9, 100.0] | 99.0 [97.0, 100.0] | 0.0 [0.0, 0.0] | 0.0 [0.0, 0.0] | 0.0 [0.0, 0.0] | 0.00 [0.00, 0.00] | 0.0 [0.0, 0.0] | 0.00 [0.00, 0.00] | 6.3 [5.6, 7.1] | 6.1 [5.4, 6.8] | 90.2 [84.8, 94.8] |

Paired, conv13-v7c-mlx minus each system (points; per-minute rows in names per minute):

| Measure | conv13-v7c-mlx − conv13-elevenlabs-2026-10-16 |
| --- | --- |
| Names right | +0.8 [-2.3, +4.2] (3 vs 2) |
| Untaught overwritten | -0.8 [-2.4, +0.0] (0 vs 1) |
| Wrong name written | -1.5 [-3.9, +0.0] (0 vs 2) |
| Name-free items with an insertion | +0.0 [+0.0, +0.0] (0 vs 0) |
| Name-free items with a name from another recording | +0.0 [+0.0, +0.0] (0 vs 0) |
| Ordinary-word error | -0.7 [-1.7, +0.1] |
| Full-transcript error | -0.7 [-1.7, +0.0] |
| Listed names inserted per minute | +0.00 [+0.00, +0.00] |
| Names from other recordings inserted per minute | +0.00 [+0.00, +0.00] |

## Suite: conv13-far



333 name mentions; 150 name-free items (16.8 min). Own list per recording (its taught names, then names taught elsewhere in the suite, 40 in all); untaught = the spoken name removed.

| System | Names right | right: name never seen in training | right: name seen in training | Untaught overwritten | Wrong name written | Name-free: items with a listed name inserted | Listed names inserted per minute (name-free) | Name-free: items with a name from another recording inserted | Names from other recordings inserted per minute | Ordinary-word error | Full-transcript error | Names right, no list |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| conv13-elevenlabs-2026-10-16 | 88.0 [84.4, 91.5] | 85.9 [81.1, 90.5] | 92.5 [87.7, 97.0] | 11.4 [8.3, 14.8] | 2.4 [0.9, 4.1] | 1.3 [0.0, 3.4] | 0.12 [0.00, 0.31] | 0.0 [0.0, 0.0] | 0.00 [0.00, 0.00] | 19.1 [13.6, 28.5] | 17.6 [12.9, 25.4] | 55.0 [48.6, 61.2] |
| conv13-v7c-mlx | 82.9 [78.3, 87.2] | 80.2 [74.1, 85.8] | 88.7 [82.7, 94.1] | 5.4 [3.1, 7.9] | 0.9 [0.0, 2.1] | 0.0 [0.0, 0.0] | 0.00 [0.00, 0.00] | 0.0 [0.0, 0.0] | 0.00 [0.00, 0.00] | 20.2 [17.6, 22.9] | 18.9 [16.4, 21.5] | 55.9 [50.1, 61.5] |

Paired, conv13-v7c-mlx minus each system (points; per-minute rows in names per minute):

| Measure | conv13-v7c-mlx − conv13-elevenlabs-2026-10-16 |
| --- | --- |
| Names right | -5.1 [-9.1, -1.4] (16 vs 33) **holds** |
| Untaught overwritten | -6.0 [-9.4, -2.7] (8 vs 28) **holds** |
| Wrong name written | -1.5 [-3.5, +0.3] (3 vs 8) |
| Name-free items with an insertion | -1.3 [-3.4, +0.0] (0 vs 2) |
| Name-free items with a name from another recording | +0.0 [+0.0, +0.0] (0 vs 0) |
| Ordinary-word error | +1.1 [-7.9, +6.1] |
| Full-transcript error | +1.3 [-6.1, +5.5] |
| Listed names inserted per minute | -0.12 [-0.31, +0.00] |
| Names from other recordings inserted per minute | +0.00 [+0.00, +0.00] |

## Suite: conv13-level



300 name mentions; 120 name-free items (14.0 min). Own list per recording (its taught names, then names taught elsewhere in the suite, 40 in all); untaught = the spoken name removed.

| System | Names right | right: name never seen in training | right: name seen in training | Untaught overwritten | Wrong name written | Name-free: items with a listed name inserted | Listed names inserted per minute (name-free) | Name-free: items with a name from another recording inserted | Names from other recordings inserted per minute | Ordinary-word error | Full-transcript error | Names right, no list |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| conv13-elevenlabs-2026-10-16 | 84.3 [79.8, 88.7] | 80.2 [74.3, 85.7] | 93.5 [88.2, 97.9] | 11.0 [7.8, 14.4] | 5.0 [2.7, 7.5] | 1.7 [0.0, 4.2] | 0.14 [0.00, 0.38] | 0.0 [0.0, 0.0] | 0.00 [0.00, 0.00] | 14.7 [12.8, 16.8] | 13.6 [11.9, 15.5] | 55.0 [48.6, 61.1] |
| conv13-v7c-mlx | 78.7 [73.7, 83.5] | 73.4 [67.3, 79.6] | 90.3 [84.3, 95.7] | 5.3 [3.0, 7.9] | 3.7 [1.7, 5.8] | 1.7 [0.0, 4.2] | 0.21 [0.00, 0.59] | 0.0 [0.0, 0.0] | 0.00 [0.00, 0.00] | 18.8 [16.4, 21.4] | 17.6 [15.4, 20.0] | 48.7 [42.8, 54.5] |

Paired, conv13-v7c-mlx minus each system (points; per-minute rows in names per minute):

| Measure | conv13-v7c-mlx − conv13-elevenlabs-2026-10-16 |
| --- | --- |
| Names right | -5.7 [-9.9, -1.4] (12 vs 29) **holds** |
| Untaught overwritten | -5.7 [-8.9, -2.5] (5 vs 22) **holds** |
| Wrong name written | -1.3 [-4.2, +1.4] (7 vs 11) |
| Name-free items with an insertion | +0.0 [-3.4, +3.3] (2 vs 2) |
| Name-free items with a name from another recording | +0.0 [+0.0, +0.0] (0 vs 0) |
| Ordinary-word error | +4.1 [+2.7, +5.5] **holds** |
| Full-transcript error | +4.1 [+2.8, +5.3] **holds** |
| Listed names inserted per minute | +0.07 [-0.27, +0.48] |
| Names from other recordings inserted per minute | +0.00 [+0.00, +0.00] |

## Suite: conv13-near



280 name mentions; 0 name-free items (0 min). Own list per recording (its taught names, then names taught elsewhere in the suite, 40 in all); untaught = the spoken name removed.

| System | Names right | right: name never seen in training | right: name seen in training | Untaught overwritten | Wrong name written | Name-free: items with a listed name inserted | Listed names inserted per minute (name-free) | Name-free: items with a name from another recording inserted | Names from other recordings inserted per minute | Ordinary-word error | Full-transcript error | Names right, no list |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| conv13-elevenlabs-2026-10-16 | 92.5 [89.3, 95.4] | 91.6 [87.8, 95.2] | 95.4 [89.4, 100.0] | 12.5 [8.6, 16.9] | 4.6 [2.4, 7.3] | n/a | n/a | n/a | n/a | 6.0 [4.6, 7.7] | 5.7 [4.4, 7.3] | 72.5 [66.7, 78.2] |
| conv13-v7c-mlx | 92.1 [88.9, 95.1] | 89.8 [85.7, 93.5] | 100.0 [100.0, 100.0] | 5.4 [2.8, 8.2] | 1.1 [0.0, 2.5] | n/a | n/a | n/a | n/a | 7.4 [5.9, 9.2] | 6.7 [5.4, 8.3] | 68.2 [62.2, 74.2] |

Paired, conv13-v7c-mlx minus each system (points; per-minute rows in names per minute):

| Measure | conv13-v7c-mlx − conv13-elevenlabs-2026-10-16 |
| --- | --- |
| Names right | -0.4 [-3.9, +3.2] (13 vs 14) |
| Untaught overwritten | -7.1 [-11.9, -2.8] (6 vs 26) **holds** |
| Wrong name written | -3.6 [-6.3, -1.1] (2 vs 12) **holds** |
| Name-free items with an insertion | n/a |
| Name-free items with a name from another recording | n/a |
| Ordinary-word error | +1.4 [+0.5, +2.3] **holds** |
| Full-transcript error | +1.0 [+0.1, +1.9] **holds** |
| Listed names inserted per minute | n/a |
| Names from other recordings inserted per minute | n/a |

## Suite: conv13-short



344 name mentions; 376 name-free items (5.7 min). Own list per recording (its taught names, then names taught elsewhere in the suite, 40 in all); untaught = the spoken name removed.

| System | Names right | right: name never seen in training | right: name seen in training | Untaught overwritten | Wrong name written | Name-free: items with a listed name inserted | Listed names inserted per minute (name-free) | Name-free: items with a name from another recording inserted | Names from other recordings inserted per minute | Ordinary-word error | Full-transcript error | Names right, no list |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| conv13-elevenlabs-2026-10-16 | 84.6 [80.2, 88.8] | 84.0 [78.5, 89.3] | 86.0 [78.4, 92.9] | 13.7 [10.1, 17.4] | 4.9 [2.7, 7.4] | 6.4 [3.8, 9.2] | 4.25 [2.52, 6.17] | 0.0 [0.0, 0.0] | 0.00 [0.00, 0.00] | 52.9 [48.3, 57.7] | 44.6 [40.8, 48.4] | 39.2 [33.6, 44.8] |
| conv13-v7c-mlx | 85.2 [81.1, 89.0] | 86.1 [81.0, 90.9] | 83.2 [76.1, 89.7] | 4.9 [2.8, 7.3] | 1.7 [0.6, 3.3] | 1.1 [0.2, 2.2] | 0.71 [0.17, 1.45] | 0.0 [0.0, 0.0] | 0.00 [0.00, 0.00] | 41.1 [36.5, 45.9] | 34.1 [30.4, 38.0] | 48.5 [42.9, 54.4] |

Paired, conv13-v7c-mlx minus each system (points; per-minute rows in names per minute):

| Measure | conv13-v7c-mlx − conv13-elevenlabs-2026-10-16 |
| --- | --- |
| Names right | +0.6 [-4.2, +5.4] (33 vs 31) |
| Untaught overwritten | -8.7 [-12.5, -5.1] (8 vs 38) **holds** |
| Wrong name written | -3.2 [-5.9, -0.6] (5 vs 16) **holds** |
| Name-free items with an insertion | -5.3 [-8.3, -2.6] (3 vs 23) **holds** |
| Name-free items with a name from another recording | +0.0 [+0.0, +0.0] (0 vs 0) |
| Ordinary-word error | -11.8 [-15.7, -7.9] **holds** |
| Full-transcript error | -10.5 [-13.5, -7.4] **holds** |
| Listed names inserted per minute | -3.54 [-5.58, -1.68] **holds** |
| Names from other recordings inserted per minute | +0.00 [+0.00, +0.00] |

## Suite: conv13-street



320 name mentions; 150 name-free items (18.7 min). Own list per recording (its taught names, then names taught elsewhere in the suite, 40 in all); untaught = the spoken name removed.

| System | Names right | right: name never seen in training | right: name seen in training | Untaught overwritten | Wrong name written | Name-free: items with a listed name inserted | Listed names inserted per minute (name-free) | Name-free: items with a name from another recording inserted | Names from other recordings inserted per minute | Ordinary-word error | Full-transcript error | Names right, no list |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| conv13-elevenlabs-2026-10-16 | 95.6 [93.3, 97.7] | 95.6 [92.9, 97.9] | 95.7 [91.0, 99.0] | 6.9 [4.3, 9.6] | 1.6 [0.3, 3.0] | 0.0 [0.0, 0.0] | 0.00 [0.00, 0.00] | 0.0 [0.0, 0.0] | 0.00 [0.00, 0.00] | 6.1 [5.2, 7.1] | 5.8 [4.9, 6.7] | 72.8 [67.7, 78.1] |
| conv13-v7c-mlx | 93.8 [90.9, 96.4] | 92.1 [88.4, 95.5] | 97.8 [94.4, 100.0] | 5.6 [3.3, 8.3] | 1.2 [0.3, 2.6] | 0.0 [0.0, 0.0] | 0.00 [0.00, 0.00] | 0.0 [0.0, 0.0] | 0.00 [0.00, 0.00] | 7.2 [6.4, 8.1] | 6.8 [6.0, 7.6] | 65.3 [59.8, 71.0] |

Paired, conv13-v7c-mlx minus each system (points; per-minute rows in names per minute):

| Measure | conv13-v7c-mlx − conv13-elevenlabs-2026-10-16 |
| --- | --- |
| Names right | -1.9 [-4.9, +1.2] (9 vs 15) |
| Untaught overwritten | -1.2 [-4.0, +1.6] (9 vs 13) |
| Wrong name written | -0.3 [-2.1, +1.6] (4 vs 5) |
| Name-free items with an insertion | +0.0 [+0.0, +0.0] (0 vs 0) |
| Name-free items with a name from another recording | +0.0 [+0.0, +0.0] (0 vs 0) |
| Ordinary-word error | +1.1 [+0.3, +1.9] **holds** |
| Full-transcript error | +1.0 [+0.3, +1.7] **holds** |
| Listed names inserted per minute | +0.00 [+0.00, +0.00] |
| Names from other recordings inserted per minute | +0.00 [+0.00, +0.00] |

## Suite: conv13-tel



270 name mentions; 200 name-free items (22.0 min). Own list per recording (its taught names, then names taught elsewhere in the suite, 40 in all); untaught = the spoken name removed.

| System | Names right | right: name never seen in training | right: name seen in training | Untaught overwritten | Wrong name written | Name-free: items with a listed name inserted | Listed names inserted per minute (name-free) | Name-free: items with a name from another recording inserted | Names from other recordings inserted per minute | Ordinary-word error | Full-transcript error | Names right, no list |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| conv13-elevenlabs-2026-10-16 | 97.0 [94.9, 98.9] | 98.3 [96.2, 100.0] | 94.6 [89.4, 98.9] | 8.1 [5.1, 11.4] | 2.2 [0.7, 4.2] | 0.5 [0.0, 1.6] | 0.05 [0.00, 0.15] | 0.0 [0.0, 0.0] | 0.00 [0.00, 0.00] | 4.7 [3.9, 5.6] | 4.6 [3.8, 5.4] | 79.6 [74.3, 84.6] |
| conv13-v7c-mlx | 98.1 [96.3, 99.6] | 98.3 [96.1, 100.0] | 97.8 [94.3, 100.0] | 2.6 [0.8, 4.7] | 0.4 [0.0, 1.2] | 0.0 [0.0, 0.0] | 0.00 [0.00, 0.00] | 0.0 [0.0, 0.0] | 0.00 [0.00, 0.00] | 5.0 [4.2, 5.7] | 4.7 [4.0, 5.4] | 73.3 [67.7, 78.9] |

Paired, conv13-v7c-mlx minus each system (points; per-minute rows in names per minute):

| Measure | conv13-v7c-mlx − conv13-elevenlabs-2026-10-16 |
| --- | --- |
| Names right | +1.1 [-1.1, +3.4] (6 vs 3) |
| Untaught overwritten | -5.6 [-8.8, -2.4] (3 vs 18) **holds** |
| Wrong name written | -1.9 [-3.9, +0.0] (1 vs 6) |
| Name-free items with an insertion | -0.5 [-1.6, +0.0] (0 vs 1) |
| Name-free items with a name from another recording | +0.0 [+0.0, +0.0] (0 vs 0) |
| Ordinary-word error | +0.3 [-0.3, +0.8] |
| Full-transcript error | +0.1 [-0.5, +0.6] |
| Listed names inserted per minute | -0.05 [-0.15, +0.00] |
| Names from other recordings inserted per minute | +0.00 [+0.00, +0.00] |

## Suite: conv13-xspk



348 name mentions; 0 name-free items (0 min). Own list per recording (its taught names, then names taught elsewhere in the suite, 40 in all); untaught = the spoken name removed.

| System | Names right | right: name never seen in training | right: name seen in training | Untaught overwritten | Wrong name written | Name-free: items with a listed name inserted | Listed names inserted per minute (name-free) | Name-free: items with a name from another recording inserted | Names from other recordings inserted per minute | Ordinary-word error | Full-transcript error | Names right, no list |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| conv13-elevenlabs-2026-10-16 | 99.4 [98.5, 100.0] | 100.0 [100.0, 100.0] | 99.3 [98.2, 100.0] | 1.7 [0.6, 3.2] | 0.3 [0.0, 0.9] | n/a | n/a | n/a | n/a | 4.4 [3.4, 5.8] | 4.1 [3.1, 5.6] | 95.7 [93.5, 97.7] |
| conv13-v7c-mlx | 99.1 [98.0, 100.0] | 100.0 [100.0, 100.0] | 99.0 [97.6, 100.0] | 0.6 [0.0, 1.5] | 0.0 [0.0, 0.0] | n/a | n/a | n/a | n/a | 5.0 [4.3, 5.9] | 4.5 [3.8, 5.3] | 96.6 [94.6, 98.3] |

Paired, conv13-v7c-mlx minus each system (points; per-minute rows in names per minute):

| Measure | conv13-v7c-mlx − conv13-elevenlabs-2026-10-16 |
| --- | --- |
| Names right | -0.3 [-1.5, +0.9] (2 vs 3) |
| Untaught overwritten | -1.1 [-2.8, +0.3] (2 vs 6) |
| Wrong name written | -0.3 [-0.9, +0.0] (0 vs 1) |
| Name-free items with an insertion | n/a |
| Name-free items with a name from another recording | n/a |
| Ordinary-word error | +0.6 [-0.5, +1.5] |
| Full-transcript error | +0.4 [-0.8, +1.2] |
| Listed names inserted per minute | n/a |
| Names from other recordings inserted per minute | n/a |

## Speed and cost

| System | Machine | Clip latency p50 / p90 (s) | Real-time factor (clips) | Cost per audio hour: nominal | Cost per audio hour: this workload |
| --- | --- | --- | --- | --- | --- |
| conv13-elevenlabs-2026-10-16 | Apple M4 Max | nan / nan | nan | $0.270 with a list, $0.220 without (2026-10-13) | conv13-conv: no list $0.220; conv13-conv: own list $0.270; conv13-far: no list $0.220; conv13-far: own list $0.270; conv13-level: no list $0.220; conv13-level: own list $0.270; conv13-near: no list $0.220; conv13-near: own list $0.270; conv13-short: no list $0.220; conv13-short: own list $0.270; conv13-street: no list $0.220; conv13-street: own list $0.270; conv13-tel: no list $0.220; conv13-tel: own list $0.270; conv13-xspk: no list $0.220; conv13-xspk: own list $0.270 |
| conv13-v7c-mlx | Apple M5 Pro (shared; 1-min load 2–7, median 2: not for latency claims) | nan / nan | nan | n/a | real-time factor on the recorded machine only |

## Paired differences: conv13-v7c-mlx minus each system, same items

Points, 95% bootstrap interval over books (clips) or chapters; **holds** when the interval excludes zero. In brackets: items only the first system / only the second got (no item-level test; it would ignore the clustering).

| Measure | conv13-v7c-mlx − conv13-elevenlabs-2026-10-16 |
| --- | --- |
| Names right, own list | n/a |
|   invented | n/a |
|   traditional | n/a |
| Untaught overwritten, own list | n/a |
| Wrong name written, own list | n/a |
| Name-free inserted, own list | n/a |
| Ordinary-word error, own list | n/a |
| Full-transcript error, own list | n/a |
| Names right, all-books list | n/a |
| Untaught overwritten, all-books list | n/a |
| Chapters: names right | n/a |
| Chapters: untaught overwritten | n/a |
| Chapters: ordinary-word error | n/a |
| Chapters: full-transcript error | n/a |

## How each system took the names

- **conv13-elevenlabs-2026-10-16**: keyterms; limits: <=1000 terms, each <50 chars and <=5 words, no <>{}[]\; fit: drop terms that break a per-term rule, then keep the first 1000 (most frequent in the book first)
- **conv13-v7c-mlx**: spotter shortlist of the whole list -> writer prompt + taught recordings; limits: none; fit: no limit: the spotter ranks every name

## Runs

- **conv13-elevenlabs-2026-10-16**: `elevenlabs` {"service": "ElevenLabs Speech to Text", "endpoint": "https://api.elevenlabs.io/v1/speech-to-text", "model_id": "scribe_v2", "language_code": "en", "tag_audio_events": false, "temperature": 0.0, "seed": 0, "list_feature": "keyterms", "limits": "<=1000 terms, each <50 chars and <=5 words, no <>{}[]\\", "fit": "drop terms that break a per-term rule, then keep the first 1000 (most frequent in the book first)"}; machine {"platform": "macOS-26.3.1-arm64-arm-64bit", "machine": "arm64", "python": "3.12.13", "cpu": "Apple M4 Max", "memory_gb": 128.0, "os": "macOS 26.3.1 (25D771280a)"}; code v06/final@b086d92; dataset virgil-coach/own-names-bench@v1.2.0 (fingerprint 54d0fa007c55); commands ['/Users/jameslal/workspace/jl/own-names-bench-wt-final/.venv/bin/bench --data /private/tmp/claude-501/-Users-jameslal-workspace-jl/1530f64d-f911-490c-b89a-551312343212/scratchpad/c13asm/data run --system elevenlabs --label c13-elevenlabs --out results/v06final --no-chapters --no-sample-files']; started 2026-10-16T19:33:42+00:00
- **conv13-v7c-mlx**: `ours-mlx` {"runtime": "Detail Keeper engine (Rust, MLX), detailkeeper-bench", "engine_commit": "af939d6", "binary": "/Users/virgil/workroots/v7c-release/bin/detailkeeper-bench", "adapter": "/Users/virgil/workroots/v7c-release/adapters/qwen17B_audio_heard_v7c", "adapter_version": "v0.7.0", "adapter_sha256": "de91437d4fc828b49605e6482a32b817d55ac4853d1714ac1e2bf9be8f61226c", "writer": "merged adapter, text decoder affine 8-bit, audio encoder bf16", "g2p": "own_names_bench/ours_ref/g2p.json (espeak-ng 1.52.0, every benchmark name)", "shortlist": 10, "prune": "off", "gate": "none", "engine": {"adapter": "qwen17B_audio_heard_v7c", "device": "metal", "model": "Qwen/Qwen3-ASR-1.7B-hf", "ready": true}, "list_feature": "spotter shortlist of the whole list -> writer prompt + taught recordings", "fit": "no limit: the spotter ranks every name"}; machine {"platform": "macOS-27.0-arm64-arm-64bit", "machine": "arm64", "python": "3.12.13", "cpu": "Apple M5 Pro", "memory_gb": 64.0, "os": "macOS 27.0 (26A428)"}; code unknown; dataset virgil-coach/own-names-bench@v1.2.0 (fingerprint 54d0fa007c55); commands ['/Users/virgil/workroots/v7c-release/venv/bin/bench --data /Users/virgil/workroots/v7c-release/conv13 run --system ours-mlx --label conv13-v7c-mlx --out /Users/virgil/workroots/v7c-release/results/conv13 --no-chapters']; started 2026-10-27T11:20:52+00:00
