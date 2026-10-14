# own-names-bench v1.0.0 results

Scored 2026-10-14. Percentages with 95% intervals: Wilson for shares of items; bootstrap over books (clips) or chapters for word error and wrong writes per minute. Every system got the same names in the same order through its own custom-vocabulary feature; `list fit` says how each fitted them to its limits.

## Clips, the book's own name list

| System | Names right, invented | Names right, traditional | Names right, all | Untaught overwritten | Wrong name written | Name-free: a listed name inserted | Ordinary-word error | Spoken name among the names sent |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| deepgram | 92.2 [89.5, 94.2] | 61.3 [57.4, 65.1] | 75.2 [72.6, 77.7] | 8.2 [6.7, 10.0] | 3.1 [2.2, 4.3] | 1.7 [0.8, 3.5] | 4.1 [3.1, 5.0] | 85.8% |
| elevenlabs | 96.6 [94.6, 97.9] | 88.7 [85.9, 90.9] | 92.2 [90.5, 93.7] | 3.3 [2.4, 4.6] | 1.8 [1.2, 2.8] | 0.2 [0.0, 1.4] | 1.7 [1.4, 1.9] | 100.0% |
| ours-mlx-macmini | 97.4 [95.6, 98.5] | 96.1 [94.2, 97.3] | 96.7 [95.4, 97.6] | 6.8 [5.4, 8.4] | 0.7 [0.4, 1.4] | 4.4 [2.8, 6.9] | 2.7 [2.3, 3.1] | 100.0% |
| ours-rtx4090 | 97.8 [96.1, 98.8] | 95.7 [93.8, 97.1] | 96.7 [95.4, 97.6] | 7.0 [5.7, 8.7] | 0.8 [0.4, 1.5] | 3.9 [2.4, 6.3] | 2.7 [2.4, 3.0] | 100.0% |
| parakeet-a100 | 82.4 [78.8, 85.5] | 75.3 [71.8, 78.6] | 78.5 [76.0, 80.8] | 27.2 [24.7, 29.9] | 7.6 [6.2, 9.3] | 7.1 [5.0, 10.0] | 3.5 [2.9, 4.0] | 100.0% |
| qwen-context-rtx4090 | 76.4 [72.4, 79.9] | 53.6 [49.6, 57.5] | 63.9 [61.0, 66.6] | 4.3 [3.3, 5.7] | 3.0 [2.1, 4.2] | 0.2 [0.0, 1.4] | 3.6 [2.6, 4.5] | 100.0% |
| qwen-rtx4090 | n/a | n/a | n/a | n/a | n/a | n/a | n/a | its feature cannot take this list |
| whisper-rtx4090 | 92.4 [89.7, 94.4] | 59.5 [55.6, 63.4] | 74.3 [71.7, 76.8] | 1.6 [1.0, 2.6] | 1.0 [0.6, 1.8] | 0.2 [0.0, 1.4] | 3.0 [2.4, 3.4] | 65.6% |

## Clips, all-books list (902 names)

| System | Names right, invented | Names right, traditional | Names right, all | Untaught overwritten | Wrong name written | Name-free: a listed name inserted | Ordinary-word error | Spoken name among the names sent |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| deepgram | n/a | n/a | n/a | n/a | n/a | n/a | n/a | its feature cannot take this list |
| elevenlabs | 94.0 [91.5, 95.8] | 86.8 [83.9, 89.3] | 90.1 [88.2, 91.7] | 3.7 [2.7, 5.0] | 1.6 [1.0, 2.6] | 0.5 [0.1, 1.8] | 1.8 [1.5, 2.1] | 100.0% |
| ours-mlx-macmini | 96.4 [94.4, 97.7] | 94.9 [92.9, 96.4] | 95.6 [94.2, 96.6] | 10.8 [9.1, 12.8] | 1.3 [0.8, 2.1] | 5.6 [3.8, 8.3] | 2.8 [2.4, 3.2] | 100.0% |
| ours-rtx4090 | 96.4 [94.4, 97.7] | 94.9 [92.9, 96.4] | 95.6 [94.2, 96.6] | 11.4 [9.6, 13.4] | 1.4 [0.8, 2.2] | 5.4 [3.6, 8.0] | 2.8 [2.4, 3.2] | 100.0% |
| parakeet-a100 | 71.3 [67.2, 75.1] | 67.8 [63.9, 71.4] | 69.4 [66.6, 72.0] | 40.3 [37.4, 43.2] | 14.5 [12.5, 16.6] | 23.3 [19.4, 27.6] | 5.2 [4.7, 5.8] | 100.0% |
| qwen-context-rtx4090 | 66.7 [62.5, 70.7] | 49.2 [45.2, 53.1] | 57.1 [54.2, 60.0] | 5.2 [4.1, 6.7] | 3.9 [2.9, 5.2] | 0.2 [0.0, 1.4] | 4.0 [3.1, 4.7] | 100.0% |
| qwen-rtx4090 | n/a | n/a | n/a | n/a | n/a | n/a | n/a | its feature cannot take this list |
| whisper-rtx4090 | n/a | n/a | n/a | n/a | n/a | n/a | n/a | its feature cannot take this list |

## Clips, no list

| System | Names right, invented | Names right, traditional | Names right, all | Name-free: a book name inserted | Ordinary-word error |
| --- | --- | --- | --- | --- | --- |
| deepgram | 28.1 [24.3, 32.2] | 24.3 [21.1, 27.9] | 26.0 [23.5, 28.7] | 0.0 [0.0, 0.9] | 6.0 [5.2, 6.6] |
| elevenlabs | 56.1 [51.7, 60.4] | 62.3 [58.4, 66.1] | 59.5 [56.6, 62.4] | 0.0 [0.0, 0.9] | 3.1 [2.7, 3.6] |
| ours-mlx-macmini | 34.7 [30.6, 38.9] | 39.3 [35.5, 43.2] | 37.2 [34.4, 40.1] | 0.0 [0.0, 0.9] | 4.9 [4.3, 5.4] |
| ours-rtx4090 | 34.3 [30.2, 38.5] | 39.3 [35.5, 43.2] | 37.0 [34.2, 39.9] | 0.0 [0.0, 0.9] | 4.9 [4.3, 5.4] |
| parakeet-a100 | 39.7 [35.5, 44.0] | 39.1 [35.3, 43.1] | 39.4 [36.5, 42.3] | 0.0 [0.0, 0.9] | 4.3 [3.8, 4.7] |
| qwen-context-rtx4090 | 39.5 [35.3, 43.8] | 43.8 [39.9, 47.7] | 41.8 [39.0, 44.8] | 0.0 [0.0, 0.9] | 4.3 [3.8, 4.8] |
| qwen-rtx4090 | 39.5 [35.3, 43.8] | 43.8 [39.9, 47.7] | 41.8 [39.0, 44.8] | 0.0 [0.0, 0.9] | 4.3 [3.8, 4.8] |
| whisper-rtx4090 | 51.3 [46.9, 55.7] | 48.5 [44.6, 52.5] | 49.8 [46.8, 52.7] | 0.0 [0.0, 0.9] | 3.7 [3.3, 4.0] |

## Continuous chapters

| System | Names right (taught) | Wrong names per minute (taught) | Untaught overwritten | Ordinary-word error (taught) | Names right, no list | Ordinary-word error, no list |
| --- | --- | --- | --- | --- | --- | --- |
| deepgram | 83.4 [79.1, 86.9] | 0.04 [0.00, 0.10] | 5.3 [2.8, 9.7] | 3.2 [2.2, 4.7] | 14.9 [11.5, 19.0] | 4.8 [3.2, 7.0] |
| elevenlabs | 98.5 [96.6, 99.4] | 0.00 [0.00, 0.00] | 1.8 [0.6, 5.0] | 2.0 [1.1, 3.5] | 63.6 [58.3, 68.5] | 2.8 [1.5, 4.7] |
| ours-mlx-macmini | 99.7 [98.4, 99.9] | 0.01 [0.00, 0.02] | 1.8 [0.6, 5.0] | 2.8 [1.7, 4.4] | 26.2 [21.9, 31.1] | 4.4 [2.8, 6.6] |
| ours-rtx4090 | 99.4 [97.9, 99.8] | 0.01 [0.00, 0.02] | 1.8 [0.6, 5.0] | 2.8 [1.7, 4.4] | 26.5 [22.1, 31.4] | 4.4 [2.8, 6.6] |
| parakeet-a100 | 91.8 [88.5, 94.3] | 0.01 [0.00, 0.02] | 4.7 [2.4, 9.0] | 2.8 [1.7, 4.3] | 39.7 [34.6, 44.9] | 3.7 [2.6, 5.4] |
| qwen-context-rtx4090 | 89.2 [85.5, 92.1] | 0.83 [0.04, 2.04] | 2.9 [1.3, 6.7] | 2.9 [1.9, 4.6] | 22.7 [18.6, 27.5] | 4.5 [2.9, 6.6] |
| qwen-rtx4090 | 22.7 [18.6, 27.5] | 0.00 [0.00, 0.00] | 1.2 [0.3, 4.2] | 4.5 [2.9, 6.6] | 22.7 [18.6, 27.5] | 4.5 [2.9, 6.6] |
| whisper-rtx4090 | 77.0 [72.2, 81.1] | 0.01 [0.00, 0.02] | 1.8 [0.6, 5.0] | 3.6 [2.4, 5.3] | 26.5 [22.1, 31.4] | 4.5 [3.1, 6.5] |

## Speed and cost

| System | Machine | Clip latency p50 / p90 (s) | Real-time factor (clips) | Chapter latency p50 (s) | Cost per audio hour |
| --- | --- | --- | --- | --- | --- |
| deepgram | Apple M4 Max | 0.41 / 0.67 | 0.044 | 1.1 | $0.336 with list, $0.258 without (list price, 2026-10-13) |
| elevenlabs | Apple M4 Max | 1.07 / 1.76 | 0.114 | 11.3 | $0.270 with list, $0.220 without (list price, 2026-10-13) |
| ours-mlx-macmini | Apple M5 Pro (shared; 1-min load 14–166, median 75: not for latency claims) | 1.88 / 7.99 | 0.325 | 110.5 | local; real-time factor on the recorded machine |
| ours-rtx4090 | NVIDIA GeForce RTX 4090, 580.159.04, 24564 MiB | 2.32 / 3.35 | 0.218 | 166.7 | $0.194 (measured real-time factor 0.218 x $0.89/h for the machine) |
| parakeet-a100 | NVIDIA A100-SXM4-80GB, 595.91.07, 81920 MiB | 0.23 / 0.43 | 0.029 | 3.7 | $0.052 (measured real-time factor 0.029 x $1.79/h for the machine) |
| qwen-context-rtx4090 | NVIDIA GeForce RTX 4090, 580.159.04, 24564 MiB | 0.69 / 1.65 | 0.089 | 34.5 | $0.079 (measured real-time factor 0.089 x $0.89/h for the machine) |
| qwen-rtx4090 | NVIDIA GeForce RTX 4090, 580.159.04, 24564 MiB | 0.47 / 0.64 | 0.046 | 33.6 | $0.041 (measured real-time factor 0.046 x $0.89/h for the machine) |
| whisper-rtx4090 | NVIDIA GeForce RTX 4090, 580.159.04, 24564 MiB | 0.34 / 0.46 | 0.033 | 26.8 | $0.030 (measured real-time factor 0.033 x $0.89/h for the machine) |

## Paired differences: ours-rtx4090 minus each system, same items

Points, 95% bootstrap interval over books (chapters for chapter mentions); McNemar exact p on discordant items.

| Comparison | Names right (own list) | Untaught overwritten (own list) | Ordinary-word error (own list) | Name-free inserted (own list) | Chapter names right |
| --- | --- | --- | --- | --- | --- |
| ours-rtx4090 − deepgram | +21.4 [+8.0, +33.2], p=2.6e-60 (247 vs 10) | -1.2 [-4.1, +1.4], p=0.25 (47 vs 60) | -1.4 [-2.1, -0.6] | +2.2 [-1.2, +8.1], p=0.064 (14 vs 5) | +16.0 [+7.9, +23.4], p=6.1e-15 (57 vs 2) |
| ours-rtx4090 − elevenlabs | +4.4 [+0.5, +7.6], p=8.4e-08 (67 vs 18) | +3.7 [+1.0, +6.4], p=9.6e-08 (51 vs 10) | +1.0 [+0.7, +1.3] | +3.7 [+0.0, +9.6], p=0.00027 (16 vs 1) | +0.9 [-1.3, +4.4], p=0.45 (5 vs 2) |
| ours-rtx4090 − ours-mlx-macmini | +0.0 [-0.4, +0.5], p=1 (6 vs 6) | +0.3 [-0.2, +0.7], p=0.51 (6 vs 3) | -0.0 [-0.1, +0.0] | -0.5 [-1.2, +0.0], p=0.5 (0 vs 2) | -0.3 [-1.1, +0.0], p=1 (0 vs 1) |
| ours-rtx4090 − parakeet-a100 | +18.2 [+12.3, +23.3], p=2.1e-47 (215 vs 14) | -20.1 [-26.8, -11.3], p=5.6e-46 (28 vs 251) | -0.8 [-1.2, -0.3] | -3.2 [-8.3, +3.9], p=0.053 (13 vs 26) | +7.6 [+1.1, +12.2], p=8.7e-07 (28 vs 2) |
| ours-rtx4090 − qwen-context-rtx4090 | +32.8 [+22.9, +40.5], p=1.3e-99 (370 vs 7) | +2.7 [+0.3, +5.1], p=0.0014 (57 vs 27) | -0.9 [-1.7, -0.2] | +3.7 [+0.0, +9.6], p=0.00027 (16 vs 1) | +10.2 [+4.6, +14.4], p=2.8e-09 (37 vs 2) |
| ours-rtx4090 − qwen-rtx4090 | n/a | n/a | n/a | n/a | +76.7 [+60.2, +89.3], p=1.3e-79 (263 vs 0) |
| ours-rtx4090 − whisper-rtx4090 | +22.3 [+9.1, +31.6], p=1.4e-61 (259 vs 12) | +5.4 [+2.0, +8.7], p=2.2e-14 (65 vs 5) | -0.3 [-0.6, +0.2] | +3.7 [+0.0, +9.6], p=6.1e-05 (15 vs 0) | +22.4 [+6.1, +44.6], p=2.6e-22 (78 vs 1) |

## How each system took the names

- **deepgram**: keyterm; limits: 500 keyterm tokens per request (Deepgram's tokenizer, unpublished); fit: the longest prefix of the list (most frequent first) the service accepts, found by binary search with half a second of silence (refused requests are not billed)
- **elevenlabs**: keyterms; limits: <=1000 terms, each <50 chars and <=5 words, no <>{}[]\; fit: drop terms that break a per-term rule, then keep the first 1000 (most frequent in the book first)
- **ours-mlx-macmini**: spotter shortlist of the whole list -> writer prompt + taught recordings; limits: none; fit: no limit: the spotter ranks every name
- **ours-rtx4090**: spotter shortlist of the whole list -> writer prompt + taught recordings; limits: none; fit: no limit: the spotter ranks every name
- **parakeet-a100**: GPU phrase boosting: decoding.greedy.boosting_tree.key_phrases_list; limits: none; fit: all names
- **qwen-context-rtx4090**: context (system prompt): names joined by ', '; limits: none; fit: all names
- **qwen-rtx4090**: none; limits: none; fit: no list
- **whisper-rtx4090**: prompt_ids (initial prompt): names joined by ', '; limits: 223 prompt tokens; fit: longest prefix of the list (most frequent first) within the token limit

## Runs

- **deepgram**: `deepgram` {"service": "Deepgram pre-recorded", "endpoint": "https://api.deepgram.com/v1/listen", "model": "nova-3", "language": "en", "smart_format": true, "list_feature": "keyterm", "limits": "500 keyterm tokens per request (Deepgram's tokenizer, unpublished)", "fit": "the longest prefix of the list (most frequent first) the service accepts, found by binary search with half a second of silence (refused requests are not billed)"}; machine {"platform": "macOS-26.3.1-arm64-arm-64bit", "machine": "arm64", "python": "3.12.13", "cpu": "Apple M4 Max", "memory_gb": 128.0, "os": "macOS 26.3.1 (25D771280a)"}; code HEAD; dataset virgil-coach/own-names-bench@v1.0.0 (manifest sha256 7b0adf32c2c7); commands ['/Users/jameslal/workspace/jl/own-names-bench/.venv/bin/bench run --system deepgram']; started 2026-10-13T20:02:28+00:00
- **elevenlabs**: `elevenlabs` {"service": "ElevenLabs Speech to Text", "endpoint": "https://api.elevenlabs.io/v1/speech-to-text", "model_id": "scribe_v2", "language_code": "en", "tag_audio_events": false, "temperature": 0.0, "seed": 0, "list_feature": "keyterms", "limits": "<=1000 terms, each <50 chars and <=5 words, no <>{}[]\\", "fit": "drop terms that break a per-term rule, then keep the first 1000 (most frequent in the book first)"}; machine {"platform": "macOS-26.3.1-arm64-arm-64bit", "machine": "arm64", "python": "3.12.13", "cpu": "Apple M4 Max", "memory_gb": 128.0, "os": "macOS 26.3.1 (25D771280a)"}; code HEAD; dataset virgil-coach/own-names-bench@v1.0.0 (manifest sha256 7b0adf32c2c7); commands ['/Users/jameslal/workspace/jl/own-names-bench/.venv/bin/bench run --system elevenlabs']; started 2026-10-13T20:02:34+00:00
- **ours-mlx-macmini**: `ours-mlx` {"runtime": "Detail Keeper engine (Rust, MLX), detailkeeper-bench", "engine_commit": "e5ef807a0429a8bb2c3d3fae56afd7cb2bf05730", "binary": "/Users/virgil/workroots/own-names-bench/bin/detailkeeper-bench", "adapter": "hf://littlebearlabs/own-names-qwen3-asr-lora@8ab4e83aec0debdb268ff4e21d19a63311acb516/audio-text-note", "adapter_version": "v0.3.0", "writer": "merged adapter, text decoder affine 8-bit, audio encoder bf16", "g2p": "own_names_bench/ours_ref/g2p.json (espeak-ng 1.52.0, every benchmark name)", "shortlist": 10, "prune": "off", "gate": "none", "engine": {"adapter": "audio-text-note", "device": "metal", "model": "Qwen/Qwen3-ASR-1.7B-hf", "ready": true}, "list_feature": "spotter shortlist of the whole list -> writer prompt + taught recordings", "fit": "no limit: the spotter ranks every name"}; machine {"platform": "macOS-27.0-arm64-arm-64bit", "machine": "arm64", "python": "3.12.14", "cpu": "Apple M5 Pro", "memory_gb": 64.0, "os": "macOS 27.0 (26A428)"}; code 1587f590d0c4a09560b4b91209fd5fa40173ac35-dirty; dataset virgil-coach/own-names-bench@v1.0.0 (manifest sha256 7b0adf32c2c7); commands ['/Users/virgil/workroots/own-names-bench/venv/bin/bench run --system ours-mlx --label ours-mlx-macmini --out /Users/virgil/workroots/own-names-bench/results']; started 2026-10-13T20:53:09+00:00
- **ours-rtx4090**: `ours` {"runtime": "PyTorch reference (own_names_bench/ours_ref)", "device": "cuda", "torch": "2.14.1+cu130", "transformers": "5.19.0", "cuda_device": "NVIDIA GeForce RTX 4090", "base": "Qwen/Qwen3-ASR-1.7B-hf@bcd2b5b7f32b480ab5790554cfa8347f246a14f3", "adapter": "virgil-coach/own-names-qwen3-asr@e02efd5e0db0f357f7ada3caf18e1ca293528098/audio-text-note", "adapter_version": "v0.3.0", "adapter_sha256": "67dbabef14851e89ad1b62d509e595713d4a2b6254fbc26cdb700fca1e097f55", "dtype": "float32", "decoding": "greedy, at most 200 new tokens", "spotter_phon": "facebook/wav2vec2-lv-60-espeak-cv-ft@0c380a877907192512147c466ead03055f200cad", "spotter_wavlm": "microsoft/wavlm-base-plus@98fd61b9c652129c839c0a25a05987d8f59256a4", "g2p": "own_names_bench/ours_ref/g2p.json (espeak-ng 1.52.0, every benchmark name)", "shortlist": 10, "prune": "off", "gate": "none", "windows": "Detail Keeper Segmenter (pause 0.45 s after 2 s, cap 8 s), fed 0.1 s at a time", "list_feature": "spotter shortlist of the whole list -> writer prompt + taught recordings", "fit": "no limit: the spotter ranks every name", "platform": "Linux-6.8.0-124-generic-x86_64-with-glibc2.35"}; machine {"platform": "Linux-6.8.0-124-generic-x86_64-with-glibc2.35", "machine": "x86_64", "python": "3.12.15", "cpu": "AMD Ryzen 9 7950X 16-Core Processor", "memory_gb": 187.8, "os": "Ubuntu 22.04.5 LTS", "gpu": "NVIDIA GeForce RTX 4090, 580.159.04, 24564 MiB"}; code f80ac02; dataset virgil-coach/own-names-bench@v1.0.0 (manifest sha256 7b0adf32c2c7); commands ['/gpu-cli-workspaces/jameslal/path-3172b95136962215/.pod/venv-qwen/bin/bench run --system ours --label ours-rtx4090 --hourly-usd 0.89', '/gpu-cli-workspaces/jameslal/path-3172b95136962215/.pod/venv-qwen/bin/bench run --system ours --label ours-rtx4090 --hourly-usd 0.89']; started 2026-10-13T21:18:29+00:00
- **parakeet-a100**: `parakeet` {"model": "nvidia/parakeet-tdt-0.6b-v2@ae9ad07059c7c739ffaf932226a8fe64ae2620b0", "runtime": "NeMo 3.0.0, torch 2.14.1+cu130", "device": "cuda", "decoding": "greedy_batch (TDT label looping)", "long_form": "over 20 min: rel_pos_local_attn [256, 256]", "list_feature": "GPU phrase boosting: decoding.greedy.boosting_tree.key_phrases_list", "boosting": {"boosting_tree_alpha": 2.0, "context_score": 1.0, "depth_scaling": 2.0, "alpha_chosen_on": "the chapters task: grid 0.25, 0.5, 1, 2, 4; 2 had the most names right less untaught overwritten (92.7% - 4.1%)"}, "fit": "all names"}; machine {"platform": "Linux-6.8.0-138-generic-x86_64-with-glibc2.35", "machine": "x86_64", "python": "3.12.15", "cpu": "AMD EPYC 7763 64-Core Processor", "memory_gb": 2003.8, "os": "Ubuntu 22.04.5 LTS", "gpu": "NVIDIA A100-SXM4-80GB, 595.91.07, 81920 MiB"}; code b1c28c3; dataset virgil-coach/own-names-bench@v1.0.0 (manifest sha256 7b0adf32c2c7); commands ['/gpu-cli-workspaces/jameslal/path-3b0609d92f9af37f/.pod/venv-parakeet/bin/bench run --system parakeet --label parakeet-a100 --hourly-usd 1.79']; started 2026-10-13T22:12:57+00:00
- **qwen-context-rtx4090**: `qwen-context` {"model": "Qwen/Qwen3-ASR-1.7B-hf@bcd2b5b7f32b480ab5790554cfa8347f246a14f3", "runtime": "transformers 5.19.0, torch 2.14.1+cu130", "device": "cuda", "dtype": "float32", "decoding": "greedy, language English, at most 200 new tokens", "long_form": "chapters cut by the Detail Keeper window cutter", "list_feature": "context (system prompt): names joined by ', '", "fit": "all names"}; machine {"platform": "Linux-6.8.0-124-generic-x86_64-with-glibc2.35", "machine": "x86_64", "python": "3.12.15", "cpu": "AMD Ryzen 9 7950X 16-Core Processor", "memory_gb": 187.8, "os": "Ubuntu 22.04.5 LTS", "gpu": "NVIDIA GeForce RTX 4090, 580.159.04, 24564 MiB"}; code 1ba0dc2da466d4576e3b34d2efb94f41116f662b; dataset virgil-coach/own-names-bench@v1.0.0 (manifest sha256 7b0adf32c2c7); commands ['/gpu-cli-workspaces/jameslal/path-3172b95136962215/.pod/venv-qwen/bin/bench run --system qwen-context --label qwen-context-rtx4090 --hourly-usd 0.89']; started 2026-10-13T21:51:37+00:00
- **qwen-rtx4090**: `qwen` {"model": "Qwen/Qwen3-ASR-1.7B-hf@bcd2b5b7f32b480ab5790554cfa8347f246a14f3", "runtime": "transformers 5.19.0, torch 2.14.1+cu130", "device": "cuda", "dtype": "float32", "decoding": "greedy, language English, at most 200 new tokens", "long_form": "chapters cut by the Detail Keeper window cutter", "list_feature": "none", "fit": "no list"}; machine {"platform": "Linux-6.8.0-124-generic-x86_64-with-glibc2.35", "machine": "x86_64", "python": "3.12.15", "cpu": "AMD Ryzen 9 7950X 16-Core Processor", "memory_gb": 187.8, "os": "Ubuntu 22.04.5 LTS", "gpu": "NVIDIA GeForce RTX 4090, 580.159.04, 24564 MiB"}; code 1ba0dc2da466d4576e3b34d2efb94f41116f662b; dataset virgil-coach/own-names-bench@v1.0.0 (manifest sha256 7b0adf32c2c7); commands ['/gpu-cli-workspaces/jameslal/path-3172b95136962215/.pod/venv-qwen/bin/bench run --system qwen --label qwen-rtx4090 --hourly-usd 0.89']; started 2026-10-13T21:21:57+00:00
- **whisper-rtx4090**: `whisper` {"model": "openai/whisper-large-v3@06f233fe06e710322aca913c1bc4249a0d71fce1", "runtime": "transformers 5.19.0, torch 2.14.1+cu130", "device": "cuda", "dtype": "float16", "decoding": "greedy, language en, task transcribe", "long_form": "chapters cut by the Detail Keeper window cutter; every window decoded with the prompt", "list_feature": "prompt_ids (initial prompt): names joined by ', '", "limits": "223 prompt tokens", "fit": "longest prefix of the list (most frequent first) within the token limit"}; machine {"platform": "Linux-6.8.0-124-generic-x86_64-with-glibc2.35", "machine": "x86_64", "python": "3.12.15", "cpu": "AMD Ryzen 9 7950X 16-Core Processor", "memory_gb": 187.8, "os": "Ubuntu 22.04.5 LTS", "gpu": "NVIDIA GeForce RTX 4090, 580.159.04, 24564 MiB"}; code 1ba0dc2da466d4576e3b34d2efb94f41116f662b; dataset virgil-coach/own-names-bench@v1.0.0 (manifest sha256 7b0adf32c2c7); commands ['/gpu-cli-workspaces/jameslal/path-3172b95136962215/.pod/venv-whisper/bin/bench run --system whisper --label whisper-rtx4090 --hourly-usd 0.89', '/gpu-cli-workspaces/jameslal/path-3172b95136962215/.pod/venv-whisper/bin/bench run --system whisper --label whisper-chapterwin-rtx4090 --hourly-usd 0.89 --only chapter/']; started 2026-10-13T23:58:25+00:00

## Reproducibility: the same system on two machines

Identical text: passes whose transcript is the same string. Word difference: word error of one run's text against the other's. Paired difference: first minus second, same items, 95% bootstrap interval over books.

| Runs | Machines | Passes | Identical text | Word difference | Same shortlist (windows) | Items with the same outcome: right (own list) / overwritten | Names right (own list), difference | Untaught overwritten, difference | Chapter names right, difference |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| ours-rtx4090 vs ours-mlx-macmini | NVIDIA GeForce RTX 4090, 580.159.04, 24564 MiB vs Apple M5 Pro | 6615 | 5406 (81.7%) | 0.55% | 4846/14322 (33.8%) | 1095/1107 / 1098/1107 | +0.00 [-0.43, +0.54] (6 vs 6) | +0.27 [-0.22, +0.67] (6 vs 3) | -0.29 [-1.05, +0.00] (0 vs 1) |
| whisper-rtx4090 vs whisper-a100 | NVIDIA GeForce RTX 4090, 580.159.04, 24564 MiB vs NVIDIA A100-SXM4-80GB, 595.91.07, 81920 MiB | 4025 | 4007 (99.6%) | 0.01% | n/a | 1107/1107 / 1107/1107 | +0.00 [+0.00, +0.00] (0 vs 0) | +0.00 [+0.00, +0.00] (0 vs 0) | n/a |
