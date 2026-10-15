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
