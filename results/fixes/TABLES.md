
## calls

| Configuration | Names right | Untaught overwritten | Name-free items, a listed name inserted | … a name from another recording | Ordinary-word error | Mentions scored (own / untaught) | Names right − ElevenLabs | Untaught overwritten − ElevenLabs | Ordinary-word error − ElevenLabs | Names right − ours (trace; books: published) | Overwritten − ours | Inserted − ours | Ordinary-word error − ours |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| elevenlabs | 95.5 [93.5, 97.2] | 1.6 [0.5, 2.9] | 1.7 [0.7, 2.9] | 0.0 [0.0, 0.0] | 9.1 [8.4, 9.9] | 706 / 706 | n/a | n/a | n/a | n/a | n/a | n/a | n/a |
| qwen-context | 94.6 [92.6, 96.4] | 1.3 [0.5, 2.1] | 4.1 [2.2, 6.2] | 2.6 [1.2, 4.4] | 10.3 [9.4, 11.2] | 706 / 706 | -0.8 [-2.9, +1.4] | -0.3 [-1.7, +0.8] | **+1.1 [+0.7, +1.6]** | n/a | n/a | n/a | n/a |
| ours | 92.8 [90.8, 94.6] | 3.4 [1.7, 5.4] | 2.6 [1.0, 4.6] | 1.2 [0.2, 2.6] | 10.7 [9.8, 11.6] | 706 / 706 | **-2.7 [-4.7, -0.6]** | **+1.8 [+0.2, +3.6]** | **+1.5 [+1.1, +2.1]** | n/a | n/a | n/a | n/a |
| ours-trace | 92.8 [90.8, 94.6] | 3.4 [1.7, 5.4] | 2.6 [1.0, 4.6] | 1.2 [0.2, 2.6] | 10.7 [9.8, 11.6] | 706 / 706 | **-2.7 [-4.7, -0.6]** | **+1.8 [+0.2, +3.6]** | **+1.5 [+1.1, +2.1]** | n/a | n/a | n/a | n/a |
| ours-trace+empty | 95.9 [94.4, 97.2] | 3.4 [1.7, 5.4] | 2.6 [1.0, 4.6] | 1.2 [0.2, 2.6] | 10.2 [9.4, 11.1] | 706 / 706 | +0.4 [-1.4, +2.4] | **+1.8 [+0.2, +3.6]** | **+1.1 [+0.7, +1.6]** | **+3.1 [+1.8, +4.7]** | +0.0 [+0.0, +0.0] | +0.0 [+0.0, +0.0] | **-0.4 [-0.6, -0.3]** |
| ours-fixed | 95.6 [93.9, 97.1] | 3.4 [1.5, 5.6] | 1.9 [0.7, 3.3] | 0.7 [0.0, 1.7] | 10.2 [9.4, 11.1] | 706 / 706 | +0.1 [-1.8, +2.2] | **+1.8 [+0.2, +3.7]** | **+1.1 [+0.6, +1.5]** | **+2.8 [+1.2, +4.5]** | +0.0 [-0.6, +0.5] | -0.7 [-1.9, +0.2] | **-0.5 [-0.7, -0.2]** |

## svq

| Configuration | Names right | Untaught overwritten | Name-free items, a listed name inserted | … a name from another recording | Ordinary-word error | Mentions scored (own / untaught) | Names right − ElevenLabs | Untaught overwritten − ElevenLabs | Ordinary-word error − ElevenLabs | Names right − ours (trace; books: published) | Overwritten − ours | Inserted − ours | Ordinary-word error − ours |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| elevenlabs | 98.6 [97.7, 99.3] | 0.6 [0.1, 1.3] | 0.6 [0.0, 1.6] | 0.6 [0.0, 1.6] | 14.5 [12.2, 17.0] | 1420 / 1420 | n/a | n/a | n/a | n/a | n/a | n/a | n/a |
| qwen-context | 95.4 [93.7, 97.0] | 0.7 [0.3, 1.3] | 0.0 [0.0, 0.0] | 0.0 [0.0, 0.0] | 6.4 [5.5, 7.5] | 1420 / 1420 | **-3.2 [-4.8, -1.7]** | +0.1 [-0.6, +0.8] | **-8.1 [-10.4, -5.9]** | n/a | n/a | n/a | n/a |
| ours | 91.4 [89.6, 93.2] | 0.3 [0.1, 0.6] | 0.0 [0.0, 0.0] | 0.0 [0.0, 0.0] | 8.1 [7.0, 9.2] | 1420 / 1420 | **-7.2 [-9.0, -5.4]** | -0.4 [-1.0, +0.1] | **-6.5 [-8.9, -4.2]** | n/a | n/a | n/a | n/a |
| ours-trace | 91.4 [89.6, 93.2] | 0.3 [0.1, 0.6] | 0.0 [0.0, 0.0] | 0.0 [0.0, 0.0] | 8.1 [7.0, 9.2] | 1420 / 1420 | **-7.2 [-9.0, -5.4]** | -0.4 [-1.0, +0.1] | **-6.5 [-8.9, -4.2]** | n/a | n/a | n/a | n/a |
| ours-trace+empty | 93.5 [91.7, 95.1] | 0.3 [0.1, 0.6] | 0.0 [0.0, 0.0] | 0.0 [0.0, 0.0] | 8.4 [7.4, 9.6] | 1420 / 1420 | **-5.1 [-6.8, -3.5]** | -0.4 [-1.0, +0.1] | **-6.1 [-8.4, -4.0]** | **+2.0 [+1.3, +2.9]** | +0.0 [+0.0, +0.0] | +0.0 [+0.0, +0.0] | +0.4 [-0.3, +1.1] |
| ours-fixed | 94.6 [93.0, 96.1] | 0.3 [0.1, 0.6] | 0.0 [0.0, 0.0] | 0.0 [0.0, 0.0] | 7.2 [6.2, 8.2] | 1420 / 1420 | **-3.9 [-5.5, -2.5]** | -0.4 [-1.0, +0.1] | **-7.4 [-9.7, -5.2]** | **+3.2 [+2.2, +4.4]** | +0.0 [-0.2, +0.2] | +0.0 [+0.0, +0.0] | **-0.9 [-1.6, -0.2]** |

## modulate

| Configuration | Names right | Untaught overwritten | Name-free items, a listed name inserted | … a name from another recording | Ordinary-word error | Mentions scored (own / untaught) | Names right − ElevenLabs | Untaught overwritten − ElevenLabs | Ordinary-word error − ElevenLabs | Names right − ours (trace; books: published) | Overwritten − ours | Inserted − ours | Ordinary-word error − ours |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| elevenlabs | 93.0 [88.6, 96.3] | 0.3 [0.0, 0.8] | n/a | n/a | 11.6 [9.7, 14.4] | 714 / 714 | n/a | n/a | n/a | n/a | n/a | n/a | n/a |
| qwen-context | 89.6 [84.5, 93.4] | 0.8 [0.1, 1.9] | n/a | n/a | 11.5 [9.4, 14.5] | 714 / 714 | **-3.4 [-5.2, -1.9]** | +0.6 [+0.0, +1.4] | -0.1 [-0.6, +0.7] | n/a | n/a | n/a | n/a |
| ours | 88.7 [84.0, 92.6] | 0.4 [0.0, 1.1] | n/a | n/a | 12.1 [10.1, 15.1] | 714 / 714 | **-4.3 [-6.9, -1.7]** | +0.1 [+0.0, +0.6] | +0.5 [-0.1, +1.5] | n/a | n/a | n/a | n/a |
| ours-trace | 88.7 [84.0, 92.6] | 0.4 [0.0, 1.1] | n/a | n/a | 12.1 [10.1, 15.1] | 714 / 714 | **-4.3 [-6.9, -1.7]** | +0.1 [+0.0, +0.6] | +0.5 [-0.1, +1.5] | n/a | n/a | n/a | n/a |
| ours-trace+empty | 90.5 [86.5, 93.7] | 0.4 [0.0, 1.1] | n/a | n/a | 11.9 [9.9, 14.8] | 714 / 714 | **-2.5 [-4.5, -0.1]** | +0.1 [+0.0, +0.6] | +0.3 [-0.3, +1.3] | **+1.8 [+0.8, +3.2]** | +0.0 [+0.0, +0.0] | n/a | **-0.2 [-0.4, -0.1]** |
| ours-fixed | 90.9 [87.0, 94.1] | 0.4 [0.0, 1.1] | n/a | n/a | 11.8 [9.9, 14.7] | 714 / 714 | -2.1 [-3.9, +0.2] | +0.1 [+0.0, +0.6] | +0.2 [-0.3, +1.2] | **+2.2 [+1.1, +3.7]** | +0.0 [+0.0, +0.0] | n/a | -0.3 [-0.8, +0.0] |

## ami

| Configuration | Names right | Untaught overwritten | Name-free items, a listed name inserted | … a name from another recording | Ordinary-word error | Mentions scored (own / untaught) | Names right − ElevenLabs | Untaught overwritten − ElevenLabs | Ordinary-word error − ElevenLabs | Names right − ours (trace; books: published) | Overwritten − ours | Inserted − ours | Ordinary-word error − ours |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| elevenlabs | n/a | n/a | 0.8 [0.0, 2.5] | 0.8 [0.0, 2.5] | 16.7 [14.9, 18.2] | 0 / 0 | n/a | n/a | n/a | n/a | n/a | n/a | n/a |
| qwen-context | n/a | n/a | 5.9 [1.7, 10.8] | 5.9 [1.7, 10.8] | 17.5 [16.1, 18.8] | 0 / 0 | n/a | n/a | **+0.8 [+0.6, +1.2]** | n/a | n/a | n/a | n/a |
| ours | n/a | n/a | 1.7 [0.0, 3.3] | 1.7 [0.0, 3.3] | 28.2 [26.5, 30.1] | 0 / 0 | n/a | n/a | **+11.5 [+10.6, +12.2]** | n/a | n/a | n/a | n/a |
| ours-trace | n/a | n/a | 1.7 [0.0, 3.3] | 1.7 [0.0, 3.3] | 28.2 [26.5, 30.1] | 0 / 0 | n/a | n/a | **+11.5 [+10.6, +12.2]** | n/a | n/a | n/a | n/a |
| ours-trace+empty | n/a | n/a | 1.7 [0.0, 3.3] | 1.7 [0.0, 3.3] | 20.6 [18.4, 22.5] | 0 / 0 | n/a | n/a | **+4.0 [+3.1, +5.3]** | n/a | n/a | +0.0 [+0.0, +0.0] | **-7.5 [-8.9, -6.1]** |
| ours-fixed | n/a | n/a | 1.7 [0.0, 3.3] | 1.7 [0.0, 3.3] | 18.2 [16.4, 19.9] | 0 / 0 | n/a | n/a | **+1.5 [+1.1, +1.8]** | n/a | n/a | +0.0 [+0.0, +0.0] | **-10.0 [-10.7, -8.9]** |

## books

| Configuration | Names right | Untaught overwritten | Name-free items, a listed name inserted | … a name from another recording | Ordinary-word error | Mentions scored (own / untaught) | Names right − ElevenLabs | Untaught overwritten − ElevenLabs | Ordinary-word error − ElevenLabs | Names right − ours (trace; books: published) | Overwritten − ours | Inserted − ours | Ordinary-word error − ours |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| elevenlabs | 92.2 [87.6, 97.2] | 3.3 [1.1, 5.8] | 0.2 [0.0, 0.7] | n/a | 1.7 [1.4, 1.9] | 1107 / 1107 | n/a | n/a | n/a | n/a | n/a | n/a | n/a |
| qwen-context | 63.9 [54.6, 75.2] | 4.3 [1.6, 7.2] | 0.2 [0.0, 0.7] | n/a | 3.6 [2.6, 4.5] | 1107 / 1107 | **-28.4 [-34.0, -20.3]** | +1.0 [-2.0, +3.1] | **+1.9 [+1.1, +2.7]** | n/a | n/a | n/a | n/a |
| ours | 96.7 [94.9, 98.6] | 7.0 [2.3, 11.3] | 3.9 [0.5, 9.6] | n/a | 2.7 [2.4, 3.0] | 1107 / 1107 | **+4.4 [+0.5, +7.6]** | **+3.7 [+1.0, +6.4]** | **+1.0 [+0.7, +1.3]** | n/a | n/a | n/a | n/a |
| ours-trace | 98.5 [98.5, 98.5] | 7.7 [7.7, 7.7] | 5.9 [5.9, 5.9] | n/a | 3.8 [3.8, 3.8] | 130 / 130 | **+4.6 [+4.6, +4.6]** | **+3.8 [+3.8, +3.8]** | **+1.4 [+1.4, +1.4]** | +0.0 [+0.0, +0.0] | +0.0 [+0.0, +0.0] | +0.0 [+0.0, +0.0] | +0.0 [+0.0, +0.0] |
| ours-trace+empty | 98.5 [98.5, 98.5] | 7.7 [7.7, 7.7] | 5.9 [5.9, 5.9] | n/a | 3.8 [3.8, 3.8] | 130 / 130 | **+4.6 [+4.6, +4.6]** | **+3.8 [+3.8, +3.8]** | **+1.4 [+1.4, +1.4]** | +0.0 [+0.0, +0.0] | +0.0 [+0.0, +0.0] | +0.0 [+0.0, +0.0] | +0.0 [+0.0, +0.0] |
| ours-fixed | 96.4 [94.7, 98.4] | 6.8 [2.4, 10.7] | 4.4 [0.7, 10.5] | n/a | 2.7 [2.4, 3.1] | 1107 / 1107 | **+4.2 [+0.3, +7.4]** | **+3.4 [+1.1, +5.7]** | **+1.1 [+0.7, +1.4]** | -0.3 [-0.6, +0.0] | -0.3 [-0.9, +0.5] | +0.5 [+0.0, +1.2] | +0.0 [-0.0, +0.1] |

## calls by who taught the name, and svq by recording condition (names right)

| Configuration | calls: other speaker | calls: same speaker | svq: clean | svq: background speech | svq: media noise | svq: traffic noise |
| --- | --- | --- | --- | --- | --- | --- |
| elevenlabs | 96.6 [94.1, 98.6] | 94.1 [90.9, 96.8] | 99.4 [98.6, 100.0] | 97.7 [96.1, 99.2] | 99.2 [98.1, 100.0] | 98.0 [96.4, 99.4] |
| qwen-context | 94.5 [91.8, 97.0] | 94.7 [91.5, 97.6] | 95.5 [93.1, 97.7] | 97.5 [95.7, 98.9] | 96.1 [93.9, 98.0] | 92.7 [89.7, 95.3] |
| ours | 91.9 [89.0, 94.5] | 93.8 [90.9, 96.5] | 92.1 [88.7, 95.2] | 93.2 [90.6, 95.7] | 95.8 [93.5, 97.8] | 84.5 [80.3, 88.5] |
| ours-trace | 91.9 [89.0, 94.5] | 93.8 [90.9, 96.5] | 92.1 [88.7, 95.2] | 93.2 [90.6, 95.7] | 95.8 [93.5, 97.8] | 84.5 [80.3, 88.5] |
| ours-trace+empty | 95.0 [92.5, 97.2] | 96.9 [95.1, 98.7] | 93.8 [90.8, 96.5] | 94.9 [92.6, 97.1] | 96.3 [94.3, 98.1] | 88.7 [85.1, 92.2] |
| ours-fixed | 94.5 [91.6, 96.9] | 96.9 [95.1, 98.6] | 95.5 [93.0, 97.7] | 94.6 [92.3, 96.9] | 97.5 [95.7, 98.9] | 91.0 [87.6, 94.1] |
