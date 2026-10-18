# Looks at the v1.2.0 audiobook suite (results/v07bench/PROTOCOL.md)

Every scoring of a system on the own-names-bench v1.2.0 audiobook clips under the 2026-10-17 protocol is a row here.
These numbers are a selection target, not an unbiased held-out estimate. Aggregates only: false insertions = name-free
items with a listed name inserted (of 408), names right (of 1,107 mentions), untaught overwritten (of 1,107), ordinary-word
error; 95% intervals clustered by book.

## Before the protocol (reference rows, reused, not re-run)

| System | Adapter SHA-256 | Date | False insertions | Names right | Untaught overwritten | Word error |
| --- | --- | --- | --- | --- | --- | --- |
| ElevenLabs Scribe v2 (keyterms) | n/a | published v1.2.0 run | 0.2 [0.0, 0.7] (1/408) | 92.2 [87.6, 97.2] | 3.3 [1.1, 5.8] | 1.7 [1.4, 1.9] |
| v0.3.0 + fixes (ours-fixed) | v0.3.0 hub adapter | results/diag | 4.4 [0.7, 10.5] (18/408) | 96.4 [94.7, 98.4] | 6.8 [2.4, 10.7] | 2.7 [2.4, 3.1] |
| v6j finalist + guard + re-read | f4f39c56f8d3535bb25e01e215f4431591e480688ee293fe96522fb41415706d | 2026-10-16 (v0.6 final) | 3.4 [0.5, 8.6] (14/408) | 94.9 [92.7, 97.2] | 4.7 [1.5, 7.6] | 2.7 [2.3, 3.1] |

## Under the protocol

| # | System | Adapter SHA-256 | Date | False insertions | Names right | Untaught overwritten | Word error |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | v7a (1:1 decoys) + guard + re-read (`ours-reread`) | 6453003345b92482dd899ab90d42482358069aafa160219d71c02c7c07d337df | 2026-10-17 | 2.5 [0.2, 6.1] (10/408) | 94.1 [91.1, 97.1] (1042/1107) | 5.7 [1.9, 9.2] (63/1107) | 2.7 [2.3, 3.2] |
| 2 | v7b (2:1 decoys) + guard + re-read (`ours-reread`) | 192e7fec3a6a48ed7e7d4ed3e6cf5a3e9174729114aba57d4b2f0ad74c570a01 | 2026-10-17 | 2.5 [0.0, 6.6] (10/408) | 94.5 [91.0, 98.0] (1046/1107) | 4.5 [0.9, 7.9] (50/1107) | 2.7 [2.3, 3.2] |
| 3 | v7c (+ phoneme-edit rows) + guard + re-read (`ours-reread`) | de91437d4fc828b49605e6482a32b817d55ac4853d1714ac1e2bf9be8f61226c | 2026-10-17 | 1.2 [0.2, 2.5] (5/408) | 93.0 [89.7, 96.3] (1029/1107) | 4.9 [1.1, 8.5] (54/1107) | 2.8 [2.3, 3.3] |
| 4 | v8c (v0.8: v7c recipe + respellings + same-voice dense rows) + guard + re-read (`ours-reread`), lore-poc train/v08-adapter | 1b05ca0b1e239421a8dc41c9b42675133c60a5b2fb9c3070200bd878a5f9370d | 2026-10-18 | 1.0 [0.2, 1.7] (4/408) | 88.1 [84.5, 91.7] (975/1107) | 4.2 [0.9, 7.2] (46/1107) | 2.9 [2.5, 3.3] |
| 5 | v8a (v0.8: v7c recipe + respelling rows) + guard + re-read (`ours-reread`), lore-poc train/v08-adapter | c4852ba0f0a1e2d95cd1c5cf76b1daadc5346438024148742dec11bafbf11b03 | 2026-10-18 | 0.5 [0.0, 1.2] (2/408) | 86.8 [83.3, 90.7] (961/1107) | 2.9 [0.6, 5.3] (32/1107) | 3.0 [2.6, 3.5] |
