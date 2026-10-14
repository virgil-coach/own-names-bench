# Headline numbers, v1.0.0 → v1.1.0

v1.0.0: Wilson intervals for rates, windows could reuse a hypothesis name, all-books untaught lists could keep another book's entry of the same spelling (65 passes). v1.1.0: one-to-one matching, untaught lists drop every same-spelled entry (those 65 passes rerun for every system that takes the all-books list), every interval a bootstrap over books (clips) or chapters. Percent, 95% interval.

| System | Measure | v1.0.0 | v1.1.0 |
| --- | --- | --- | --- |
| ours-rtx4090 | Clips, own list: names right | 96.7 [95.4, 97.6] | 96.7 [94.9, 98.6] |
| ours-rtx4090 | Clips, own list: untaught overwritten | 7.0 [5.7, 8.7] | 7.0 [2.3, 11.3] |
| ours-rtx4090 | Clips, own list: name-free inserted | 3.9 [2.4, 6.3] | 3.9 [0.5, 9.6] |
| ours-rtx4090 | Clips, own list: ordinary-word error | 2.7 [2.4, 3.0] | 2.7 [2.4, 3.0] |
| ours-rtx4090 | Clips, all-books: names right | 95.6 [94.2, 96.6] | 95.6 [93.7, 97.8] |
| ours-rtx4090 | Clips, all-books: untaught overwritten | 11.4 [9.6, 13.4] | 12.3 [7.1, 16.9] |
| ours-rtx4090 | Clips, no list: names right | 37.0 [34.2, 39.9] | 37.0 [31.4, 42.5] |
| ours-rtx4090 | Chapters: names right | 99.4 [97.9, 99.8] | 99.4 [98.6, 100.0] |
| ours-rtx4090 | Chapters: untaught overwritten | 1.8 [0.6, 5.0] | 1.8 [0.0, 3.4] |
| ours-rtx4090 | Chapters: ordinary-word error | 2.8 [1.7, 4.4] | 2.8 [1.7, 4.4] |
| elevenlabs | Clips, own list: names right | 92.2 [90.5, 93.7] | 92.2 [87.6, 97.2] |
| elevenlabs | Clips, own list: untaught overwritten | 3.3 [2.4, 4.6] | 3.3 [1.1, 5.8] |
| elevenlabs | Clips, own list: name-free inserted | 0.2 [0.0, 1.4] | 0.2 [0.0, 0.7] |
| elevenlabs | Clips, own list: ordinary-word error | 1.7 [1.4, 1.9] | 1.7 [1.4, 1.9] |
| elevenlabs | Clips, all-books: names right | 90.1 [88.2, 91.7] | 90.1 [86.0, 94.8] |
| elevenlabs | Clips, all-books: untaught overwritten | 3.7 [2.7, 5.0] | 3.7 [1.6, 5.8] |
| elevenlabs | Clips, no list: names right | 59.5 [56.6, 62.4] | 59.5 [52.7, 64.5] |
| elevenlabs | Chapters: names right | 98.5 [96.6, 99.4] | 98.5 [95.2, 100.0] |
| elevenlabs | Chapters: untaught overwritten | 1.8 [0.6, 5.0] | 1.8 [0.0, 3.4] |
| elevenlabs | Chapters: ordinary-word error | 2.0 [1.1, 3.5] | 2.0 [1.1, 3.5] |
| deepgram | Clips, own list: names right | 75.2 [72.6, 77.7] | 75.2 [62.0, 89.7] |
| deepgram | Clips, own list: untaught overwritten | 8.2 [6.7, 10.0] | 8.4 [5.7, 11.0] |
| deepgram | Clips, own list: name-free inserted | 1.7 [0.8, 3.5] | 1.7 [0.5, 2.9] |
| deepgram | Clips, own list: ordinary-word error | 4.1 [3.1, 5.0] | 4.1 [3.1, 5.0] |
| deepgram | Clips, no list: names right | 26.0 [23.5, 28.7] | 26.0 [23.0, 29.8] |
| deepgram | Chapters: names right | 83.4 [79.1, 86.9] | 83.4 [76.1, 91.4] |
| deepgram | Chapters: untaught overwritten | 5.3 [2.8, 9.7] | 5.3 [0.6, 10.0] |
| deepgram | Chapters: ordinary-word error | 3.2 [2.2, 4.7] | 3.2 [2.2, 4.7] |
| whisper-rtx4090 | Clips, own list: names right | 74.3 [71.7, 76.8] | 74.3 [63.7, 88.6] |
| whisper-rtx4090 | Clips, own list: untaught overwritten | 1.6 [1.0, 2.6] | 1.6 [0.2, 3.4] |
| whisper-rtx4090 | Clips, own list: name-free inserted | 0.2 [0.0, 1.4] | 0.2 [0.0, 0.7] |
| whisper-rtx4090 | Clips, own list: ordinary-word error | 3.0 [2.4, 3.4] | 3.0 [2.4, 3.4] |
| whisper-rtx4090 | Clips, no list: names right | 49.8 [46.8, 52.7] | 49.8 [44.0, 57.0] |
| whisper-rtx4090 | Chapters: names right | 77.0 [72.2, 81.1] | 77.0 [54.5, 93.8] |
| whisper-rtx4090 | Chapters: untaught overwritten | 1.8 [0.6, 5.0] | 1.8 [0.0, 3.4] |
| whisper-rtx4090 | Chapters: ordinary-word error | 3.6 [2.4, 5.3] | 3.6 [2.4, 5.3] |
| parakeet-a100 | Clips, own list: names right | 78.5 [76.0, 80.8] | 78.5 [72.3, 85.3] |
| parakeet-a100 | Clips, own list: untaught overwritten | 27.2 [24.7, 29.9] | 27.2 [15.9, 37.3] |
| parakeet-a100 | Clips, own list: name-free inserted | 7.1 [5.0, 10.0] | 7.1 [4.2, 10.3] |
| parakeet-a100 | Clips, own list: ordinary-word error | 3.5 [2.9, 4.0] | 3.5 [2.9, 4.0] |
| parakeet-a100 | Clips, all-books: names right | 69.4 [66.6, 72.0] | 69.4 [64.3, 75.0] |
| parakeet-a100 | Clips, all-books: untaught overwritten | 40.3 [37.4, 43.2] | 42.4 [34.8, 48.4] |
| parakeet-a100 | Clips, no list: names right | 39.4 [36.5, 42.3] | 39.4 [35.2, 44.9] |
| parakeet-a100 | Chapters: names right | 91.8 [88.5, 94.3] | 91.8 [87.5, 97.9] |
| parakeet-a100 | Chapters: untaught overwritten | 4.7 [2.4, 9.0] | 4.7 [0.0, 10.0] |
| parakeet-a100 | Chapters: ordinary-word error | 2.8 [1.7, 4.3] | 2.8 [1.7, 4.3] |
| qwen-context-rtx4090 | Clips, own list: names right | 63.9 [61.0, 66.6] | 63.9 [54.6, 75.2] |
| qwen-context-rtx4090 | Clips, own list: untaught overwritten | 4.3 [3.3, 5.7] | 4.3 [1.6, 7.2] |
| qwen-context-rtx4090 | Clips, own list: name-free inserted | 0.2 [0.0, 1.4] | 0.2 [0.0, 0.7] |
| qwen-context-rtx4090 | Clips, own list: ordinary-word error | 3.6 [2.6, 4.5] | 3.6 [2.6, 4.5] |
| qwen-context-rtx4090 | Clips, all-books: names right | 57.1 [54.2, 60.0] | 57.1 [50.4, 65.8] |
| qwen-context-rtx4090 | Clips, all-books: untaught overwritten | 5.2 [4.1, 6.7] | 5.2 [3.2, 7.7] |
| qwen-context-rtx4090 | Clips, no list: names right | 41.8 [39.0, 44.8] | 41.8 [35.4, 47.5] |
| qwen-context-rtx4090 | Chapters: names right | 89.2 [85.5, 92.1] | 89.2 [85.4, 94.6] |
| qwen-context-rtx4090 | Chapters: untaught overwritten | 2.9 [1.3, 6.7] | 2.9 [0.0, 5.9] |
| qwen-context-rtx4090 | Chapters: ordinary-word error | 2.9 [1.9, 4.6] | 2.9 [1.9, 4.6] |
| qwen-rtx4090 | Clips, no list: names right | 41.8 [39.0, 44.8] | 41.8 [35.4, 47.5] |
| qwen-rtx4090 | Chapters: names right | 22.7 [18.6, 27.5] | 22.2 [10.4, 37.6] |
| qwen-rtx4090 | Chapters: untaught overwritten | 1.2 [0.3, 4.2] | 1.2 [0.0, 2.7] |
| qwen-rtx4090 | Chapters: ordinary-word error | 4.5 [2.9, 6.6] | 4.5 [2.9, 6.6] |
