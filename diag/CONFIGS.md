# Diagnosis configurations (branch diag/v12-conversation, local only)

Scoring is the benchmark's own code, unchanged (score.score_clips, report.prop/ratio/paired_suite);
tables are in results/diag/TABLES.md (`python diag/score.py --md results/diag/TABLES.md`).
Nothing below was tuned on test items. Every configuration that was run is listed, losers included.

| Config | What changed vs ours | Scope run | Result in one line |
| --- | --- | --- | --- |
| ours-trace | nothing; logs each window's no-list text, list answer, final text | 4 suites, none+own+untaught | reproduces the published ours run exactly on every suite |
| ours-trace+empty | derived offline from ours-trace: a window whose list answer is empty while its no-list text has words gets the no-list text (rule fixed before scoring; motivated by empty answers seen in the published outputs) | 4 suites | calls +3.1, svq +2.0, modulate +1.8 names right; AMI word error -7.5 |
| ours-top40 | shortlist 40 (every name of a suite list; audiobooks: the spotter's best 40) | 4 suites + audiobook clips (own) | loses badly: the writer drops 17-48% of windows with 40 recordings in the prompt |
| ours-top40+empty | ours-top40 with the empty-window rule | same | still loses on every suite |
| ours-wholeclip | qwen-context's cutter: whole recording when <= 30 s, else the Segmenter (passes over 30 s are ours-trace's, identical by construction) | 4 suites none+own+untaught (<= 30 s) + audiobook clips | calls +1.6, svq +2.0, AMI -3.5 word error; audiobooks no measurable cost |
| ours-wholeclip+empty | both | same | calls 95.6, svq 94.6, AMI 19.4 |
| ours-adapter-context | adapter with qwen-context's prompt (names joined by ", "), no recordings, no spotter, qwen-context's cutter | 4 suites + audiobook clips | about qwen-context on suites (svq 95.7); audiobooks 73.4 (-23.2): the recordings carry the audiobook lead |
| ours-level | taught recordings scaled to the window's speech level (RMS of the louder half of 20 ms frames) | AMI, svq, modulate, calls mention clips (not calls name-free) | AMI word error 28.2 -> 20.8; small gains elsewhere |
| ours-level+empty | both | same | AMI 18.7 (ours with no list: 18.1); calls 95.9, modulate 90.8 |

Not run (budget): the three engine fixes together (level + wholeclip-style windows + empty rule).

## Fixes (branch fix/v12-pipeline): how the dev sets decide, written before any full dev number

Dev sets: diag/dev_build.py (lore dev split books, the same pieces through a simulated far field, LibriSpeech
test-other short utterances and joined turns, both also through the far field). Scored by diag/devscore.py.
Each fix is kept only if dev says so; the benchmark is then run once with what was kept.

- Guard (empty list answer -> no-list text): kept if, with it, no dev set loses names right or gains untaught
  overwrites / name-free inserts beyond its paired interval, and ordinary-word error does not rise on any set.
  The "suspiciously short" extension (+short) is kept only if it lowers ordinary-word error on the LibriSpeech sets
  pooled without costing names right on books / books_far; otherwise the guard fires on empty answers only.
- Level-match: kept on the same terms (no set worse beyond its interval; expected gain on the far sets).
- Short windows: MIN_SPEECH_S from {off, 2.5, 4.0} (hold 1.0 s, fixed by the latency budget, not tuned), with
  level-match and guard on: the value with the lowest ordinary-word error on ls_turns + ls_turns_far pooled,
  provided books names right is not more than 1.0 point below off and books overwrites / inserts not more than 1.0
  point above; within 0.1 point of word error the smaller value wins (less waiting in the live engine).

### Dev outcome (results/devall/DEV.md; 2,000 items per configuration, every configuration on the same items)

- Guard: kept. Fires on 0.2-0.3% of listed windows on clean books/turns, 44-54% on the simulated far field without
  level-match, 3-7% with it; no set worse beyond its interval. +short never fired beyond the empty cases: not adopted.
- Level-match: kept. books_far names right 54.7 -> 86.7 (+32.0 [+20.2, +46.2]); far word error 36.9 -> 11.0; books
  overwrites +0.3 [+0.0, +0.7] (one item), not beyond its interval.
- Short windows: 4.0 s. ls_turns + ls_turns_far word error with level + guard: off 4.6 / 16.0, 2.5 s 4.5 / 15.3,
  4.0 s 4.5 / 14.5; books names right 94.0 vs 93.7 (off), overwrites 9.0 vs 8.7: within the 1.0-point limits.
- Benchmark configuration: ours-fixed = guard + level + MIN_SPEECH_S 4.0, HOLD_S 1.0. Run once.
