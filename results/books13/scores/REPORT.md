# own-names-bench v1.3.0 results

Scored 2026-10-27. Rates in percent with 95% intervals from a bootstrap over clusters: books for clips (each clip book has one reader), chapters for chapters. Name matches are one to one. Every system got the same names in the same order through its own custom-vocabulary feature.

## Runs: expected, completed and failed passes

| Run | System | List variants | Expected | Completed | Failed | Stale (made from an older list) | Complete |
| --- | --- | --- | --- | --- | --- | --- | --- |
| books13-deepgram | deepgram | none, own (no chapters) | 5612 | 5612 | 0 | 0 | yes |
| books13-elevenlabs | elevenlabs | none, own, all | 5612 | 5612 | 0 | 0 | yes |
| books13-v7c-mlx | ours-mlx | none, own | 5612 | 5612 | 0 | 0 | yes |

## Clips, the book's own name list

| System | Names right, invented | Names right, traditional | Names right, all | Untaught overwritten | Wrong name written | Name-free: a listed name inserted | Ordinary-word error | Full-transcript error | Spoken name among the names sent |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| books13-deepgram | 86.7 [82.7, 90.3] | 59.1 [41.5, 92.3] | 78.6 [65.1, 88.9] | 5.9 [3.9, 7.6] | 1.9 [0.7, 2.9] | 1.3 [0.4, 2.7] | 3.1 [2.4, 3.8] | 3.1 [2.4, 3.8] | 95.4 [88.4, 100.0] |
| books13-elevenlabs | 92.4 [88.6, 96.1] | 78.0 [64.1, 97.5] | 88.2 [79.4, 95.1] | 1.5 [0.5, 2.4] | 0.9 [0.0, 2.0] | 0.2 [0.0, 0.4] | 1.5 [1.2, 1.9] | 1.5 [1.2, 1.9] | 100.0 [100.0, 100.0] |
| books13-v7c-mlx | 92.9 [91.2, 95.1] | 81.7 [71.8, 96.1] | 89.6 [83.4, 94.4] | 3.6 [1.1, 6.6] | 0.8 [0.0, 1.8] | 0.2 [0.0, 0.4] | 2.1 [1.7, 2.6] | 2.1 [1.7, 2.6] | 100.0 [100.0, 100.0] |

## Clips, all-books list (902 entries)

| System | Names right, invented | Names right, traditional | Names right, all | Untaught overwritten | Wrong name written | Name-free: a listed name inserted | Ordinary-word error | Full-transcript error | Spoken name among the names sent |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| books13-deepgram | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a | its feature cannot take this list |
| books13-elevenlabs | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a | this dataset has no such list |
| books13-v7c-mlx | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a | not run (this run made only the none, own lists) |

## Clips, no list

| System | Names right, invented | Names right, traditional | Names right, all | Name-free: a book name inserted | Ordinary-word error | Full-transcript error |
| --- | --- | --- | --- | --- | --- | --- |
| books13-deepgram | 15.8 [12.5, 19.0] | 19.5 [13.2, 31.2] | 16.9 [13.9, 20.6] | 0.0 [0.0, 0.0] | 4.8 [3.9, 5.6] | 4.8 [4.0, 5.7] |
| books13-elevenlabs | 29.7 [21.6, 38.8] | 30.0 [18.5, 48.0] | 29.8 [22.7, 38.4] | 0.1 [0.0, 0.2] | 3.4 [2.7, 4.2] | 3.4 [2.7, 4.1] |
| books13-v7c-mlx | 23.2 [15.2, 31.4] | 19.2 [11.3, 32.3] | 22.0 [15.6, 29.1] | 0.0 [0.0, 0.0] | 3.9 [3.1, 4.8] | 3.9 [3.1, 4.7] |

## Continuous chapters

| System | Names right (taught) | same reader taught it | another reader taught it | Wrong names per minute | Untaught overwritten | Ordinary-word error | Full-transcript error | Names right, no list |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| books13-deepgram | not run (made without the chapters task) | | | | | | | | |
| books13-elevenlabs | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a |
| books13-v7c-mlx | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a |

## Speed and cost

| System | Machine | Clip latency p50 / p90 (s) | Real-time factor (clips) | Cost per audio hour: nominal | Cost per audio hour: this workload |
| --- | --- | --- | --- | --- | --- |
| books13-deepgram | Apple M4 Max | 0.44 / 0.78 | 0.052 | $0.336 with a list, $0.258 without (2026-10-13) | clips, no list $0.258; clips, own list $0.336 |
| books13-elevenlabs | Apple M4 Max | 0.79 / 1.16 | 0.086 | $0.270 with a list, $0.220 without (2026-10-13) | clips, no list $0.220; clips, own list $0.311 |
| books13-v7c-mlx | Apple M5 Ultra (shared; 1-min load 6–32, median 14: not for latency claims) | 0.52 / 1.15 | 0.062 | n/a | real-time factor on the recorded machine only |

## Paired differences: books13-v7c-mlx minus each system, same items

Points, 95% bootstrap interval over books (clips) or chapters; **holds** when the interval excludes zero. In brackets: items only the first system / only the second got (no item-level test; it would ignore the clustering).

| Measure | books13-v7c-mlx − books13-deepgram | books13-v7c-mlx − books13-elevenlabs |
| --- | --- | --- |
| Names right, own list | +11.0 [+3.8, +19.1] (171 vs 50) **holds** | +1.5 [-1.9, +4.7] (78 vs 62) |
|   invented | +6.2 [+2.6, +10.2] (83 vs 35) **holds** | +0.5 [-2.1, +3.6] (42 vs 38) |
|   traditional | +22.6 [-1.3, +32.1] (88 vs 15) | +3.7 [-7.5, +8.4] (36 vs 24) |
| Untaught overwritten, own list | -2.3 [-4.6, +0.0] (29 vs 54) | +2.2 [+0.1, +4.6] (31 vs 7) **holds** |
| Wrong name written, own list | -1.1 [-1.9, -0.3] (5 vs 17) **holds** | -0.1 [-0.4, +0.2] (5 vs 6) |
| Name-free inserted, own list | -1.2 [-2.3, -0.3] (1 vs 15) **holds** | +0.0 [-0.2, +0.2] (1 vs 1) |
| Ordinary-word error, own list | -0.9 [-1.4, -0.5] **holds** | +0.6 [+0.4, +0.7] **holds** |
| Full-transcript error, own list | -1.0 [-1.4, -0.6] **holds** | +0.6 [+0.4, +0.7] **holds** |
| Names right, all-books list | n/a | n/a |
| Untaught overwritten, all-books list | n/a | n/a |
| Chapters: names right | n/a | n/a |
| Chapters: untaught overwritten | n/a | n/a |
| Chapters: ordinary-word error | n/a | n/a |
| Chapters: full-transcript error | n/a | n/a |

## How each system took the names

- **books13-deepgram**: keyterm; limits: 500 keyterm tokens per request (Deepgram's tokenizer, unpublished); fit: the longest prefix of the list (most frequent first) the service accepts, found by binary search with half a second of silence (refused requests are not billed)
- **books13-elevenlabs**: keyterms; limits: <=1000 terms, each <50 chars and <=5 words, no <>{}[]\; fit: drop terms that break a per-term rule, then keep the first 1000 (most frequent in the book first)
- **books13-v7c-mlx**: spotter shortlist of the whole list -> writer prompt + taught recordings; limits: none; fit: no limit: the spotter ranks every name

## Runs

- **books13-deepgram**: `deepgram` {"service": "Deepgram pre-recorded", "endpoint": "https://api.deepgram.com/v1/listen", "model": "nova-3", "language": "en", "smart_format": true, "list_feature": "keyterm", "limits": "500 keyterm tokens per request (Deepgram's tokenizer, unpublished)", "fit": "the longest prefix of the list (most frequent first) the service accepts, found by binary search with half a second of silence (refused requests are not billed)"}; machine {"platform": "macOS-26.3.1-arm64-arm-64bit", "machine": "arm64", "python": "3.12.13", "cpu": "Apple M4 Max", "memory_gb": 128.0, "os": "macOS 26.3.1 (25D771280a)"}; code fcbf4d63b531e54125015868100215c2e648253b; dataset virgil-coach/own-names-bench@v1.3.0 (fingerprint 455a97ea1575); commands ['/Users/jameslal/workspace/jl/own-names-bench/.venv/bin/bench --data /Users/jameslal/workspace/jl/onb-v13-books-SEALED/data run --system deepgram --label books13-deepgram --out results/books13 --no-chapters']; code per command ['fcbf4d63b531e54125015868100215c2e648253b']; machine per command ['Apple M4 Max']; started 2026-10-27T21:04:04+00:00
- **books13-elevenlabs**: `elevenlabs` {"service": "ElevenLabs Speech to Text", "endpoint": "https://api.elevenlabs.io/v1/speech-to-text", "model_id": "scribe_v2", "language_code": "en", "tag_audio_events": false, "temperature": 0.0, "seed": 0, "list_feature": "keyterms", "limits": "<=1000 terms, each <50 chars and <=5 words, no <>{}[]\\", "fit": "drop terms that break a per-term rule, then keep the first 1000 (most frequent in the book first)"}; machine {"platform": "macOS-26.3.1-arm64-arm-64bit", "machine": "arm64", "python": "3.12.13", "cpu": "Apple M4 Max", "memory_gb": 128.0, "os": "macOS 26.3.1 (25D771280a)"}; code 51848f128c244536529c548b122d59b50aaaaef4; dataset virgil-coach/own-names-bench@v1.3.0 books13/ (fingerprint 455a97ea1575); commands ['/Users/jameslal/workspace/jl/own-names-bench-wt-v7crel/.venv/bin/bench --data /Users/jameslal/workspace/jl/onb-v13-books-SEALED/data run --system elevenlabs --label books13-elevenlabs --out results/books13 --no-chapters']; code per command ['51848f128c244536529c548b122d59b50aaaaef4']; machine per command ['Apple M4 Max']; started 2026-10-27T10:16:38+00:00; metadata corrected: dataset was "virgil-coach/own-names-bench@v1.2.0" (the code's constant at the time; the run was made on a local copy of the sealed books13 folder, which v1.3.0 publishes unchanged (the run's manifest_sha256 e02be6a4 and dataset_fingerprint 455a97ea15754481 are the published folder's))
- **books13-v7c-mlx**: `ours-mlx` {"runtime": "Detail Keeper engine (Rust, MLX), detailkeeper-bench", "engine_commit": "af939d6", "binary": "/Users/james/workroots/v7c-release/bin/detailkeeper-bench", "adapter": "/Users/james/workroots/v7c-release/adapters/qwen17B_audio_heard_v7c", "adapter_version": "v0.7.0", "adapter_sha256": "de91437d4fc828b49605e6482a32b817d55ac4853d1714ac1e2bf9be8f61226c", "writer": "merged adapter, text decoder affine 8-bit, audio encoder bf16", "g2p": "own_names_bench/ours_ref/g2p.json (espeak-ng 1.52.0, every benchmark name)", "shortlist": 10, "prune": "off", "gate": "none", "engine": {"adapter": "qwen17B_audio_heard_v7c", "device": "metal", "model": "Qwen/Qwen3-ASR-1.7B-hf", "ready": true}, "list_feature": "spotter shortlist of the whole list -> writer prompt + taught recordings", "fit": "no limit: the spotter ranks every name"}; machine {"platform": "macOS-27.0.1-arm64-arm-64bit", "machine": "arm64", "python": "3.12.13", "cpu": "Apple M5 Ultra", "memory_gb": 256.0, "os": "macOS 27.0.1 (26A434)"}; code unknown; dataset virgil-coach/own-names-bench@v1.3.0 books13/ (fingerprint 455a97ea1575); commands ['/Users/james/workroots/v7c-release/venv/bin/bench --data /Users/james/workroots/v7c-release/books13 run --system ours-mlx --label books13-v7c-mlx --out /Users/james/workroots/v7c-release/results/books13 --no-chapters']; code per command ['unknown']; machine per command ['Apple M5 Ultra']; started 2026-10-27T00:45:17+00:00; metadata corrected: dataset was "virgil-coach/own-names-bench@v1.2.0" (the code's constant at the time; the run was made on a local copy of the sealed books13 folder, which v1.3.0 publishes unchanged (the run's manifest_sha256 e02be6a4 and dataset_fingerprint 455a97ea15754481 are the published folder's))
