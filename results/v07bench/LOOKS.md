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
| 6 | v8b (v0.8: v7c recipe + same-voice dense rows) + guard + re-read (`ours-reread`), lore-poc train/v08-adapter | 84669398fc1a6b010035a83c5918b212e4de02920f1aa41ecce848de726feebe | 2026-10-18 | 1.7 [0.0, 4.9] (7/408) | 92.2 [88.7, 95.8] (1021/1107) | 3.7 [1.1, 6.3] (41/1107) | 2.7 [2.3, 3.1] |
| 7 | d9a (v0.9: DPO from v7c, (a):(b) mix 1:1) + guard + re-read (`ours-reread`), lore-poc train/v09-dpo | cc1c7a906b289d456d0c159ea0ab9f95748e1e2e872e81cfd09a781eebf06fdc | 2026-10-19 | 0.0 [0.0, 0.0] (0/408) | 77.0 [70.5, 84.6] (852/1107) | 2.3 [0.6, 4.1] (26/1107) | 3.3 [2.8, 3.8] |
| 8 | d9b (v0.9: DPO from v7c, (a):(b) mix 2:1) + guard + re-read (`ours-reread`), lore-poc train/v09-dpo | 8d96aff217c9ffe5ea6b2ce6acd055b8f6622d43cc2f16d6596b2369cbfad8cd | 2026-10-19 | 0.0 [0.0, 0.0] (0/408) | 68.6 [61.9, 76.5] (759/1107) | 1.7 [0.1, 3.3] (19/1107) | 3.8 [3.2, 4.2] |
| 9 | g10b (v0.10: GRPO from v7c, k 4; selected by the pre-registered rule with the dev bars ignored, no arm passed dev) + guard + re-read (`ours-reread`), lore-poc train/v10-grpo | 6665d2edc59fdf83e6d61ad78db614aa3bbc993993094b20f3e1bafc7a8688dd | 2026-10-19 | 0.0 [0.0, 0.0] (0/408) | 61.2 [55.0, 68.4] (678/1107) | 1.3 [0.0, 2.8] (14/1107) | 3.8 [3.3, 4.3] |
| 10 | v0.3.0 (published, `audio-text-note` e02efd5e) + guard + re-read on the shipped path: Detail Keeper engine af939d6 `detailkeeper-bench`, MLX, writer merged + affine 8-bit (`ours-mlx`, own-names-bench v7c/mlx-suites, Mac Studio + Mac mini), the app as it ships (0.1.1) | 67dbabef14851e89ad1b62d509e595713d4a2b6254fbc26cdb700fca1e097f55 | 2026-10-19 | 4.4 [0.7, 10.5] (18/408) | 95.9 [93.7, 98.5] (1062/1107) | 7.0 [2.3, 11.3] (78/1107) | 2.6 [2.3, 3.0] |
| 11 | v7c (v0.7.0 candidate) + guard + re-read on the shipped path: Detail Keeper engine af939d6 `detailkeeper-bench`, MLX, writer merged + affine 8-bit (d7109615…6162; `ours-mlx`, own-names-bench v7c/mlx-suites, Mac Studio + Mac mini) | de91437d4fc828b49605e6482a32b817d55ac4853d1714ac1e2bf9be8f61226c | 2026-10-20 | 1.2 [0.2, 2.5] (5/408) | 92.6 [88.8, 96.5] (1025/1107) | 4.6 [1.1, 8.0] (51/1107) | 2.8 [2.3, 3.3] |
| 12 | v7c, the same passes as look 11 (no new inference), re-scored paired against the hosted re-runs `elevenlabs-2026-10-26` and `deepgram-2026-10-26` for the Detail Keeper benchmark page draft (release check's `diag/mlx_score.py`) | de91437d4fc828b49605e6482a32b817d55ac4853d1714ac1e2bf9be8f61226c | 2026-10-26 | 1.2 [0.2, 2.5] (5/408) | 92.6 [88.8, 96.5] (1025/1107) | 4.6 [1.1, 8.0] (51/1107) | 2.8 [2.3, 3.3] |

## Reference runs scored on the clips after the protocol (not candidates)

| System | Date | Names right | Untaught overwritten | False insertions | Source |
| --- | --- | --- | --- | --- | --- |
| ElevenLabs Scribe v2 (keyterms), `elevenlabs-2026-10-26` | 2026-10-26 | 92.8 [88.5, 97.2] | 2.9 [1.2, 4.8] | 0.2 [0.0, 0.7] (1/408) | launch/hosted-2026-10-26, results/scores/HOSTED_RERUN_2026-10-26.md |
| Deepgram Nova-3 (keyterm), `deepgram-2026-10-26` | 2026-10-26 | 75.1 [61.8, 89.5] | 8.5 [5.9, 11.1] | see HOSTED_RERUN_2026-10-26.md | same |
