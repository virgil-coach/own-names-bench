# own-names-bench v1.1.0 → v1.2.0

## What did not change

The audiobook data (clips, chapters, lists, references, mentions, taught recordings) and the way
it is scored. Rescored with the v1.2.0 code, every system's clip and chapter summary is identical,
number for number, to its v1.1.0 `results/scores/<run>.json`. Only the hosted services' cost lines
changed (they now include the suites).

## Data: four suites

Each in its own dataset folder `suites/<name>/` with the source's licence for its audio and for our
annotations. Every name is taught with one recording of it; lists are 40 names per recording (its
taught names, then names taught elsewhere in the suite).

| Suite | Source (pinned revision) | Licence | Scored mentions | Name-free items |
| --- | --- | --- | --- | --- |
| `calls` | AppTek Call-Center Dialogues (`b98967d`) | CC BY-SA 4.0 | 706 in 142 calls (323 taught by the same speaker, 383 by the other party) | 417 stretches of 30–60 s, 6.0 h |
| `svq` | Google Simple Voice Questions (`74f17ec`) | CC BY 4.0 | 1,424, taught by one person, said by four others | 320 questions |
| `ami` | AMI Meeting Corpus, single distant mic (`46f28f2`) | CC BY 4.0 | none (insertions only) | 119 stretches, 1.1 h |
| `modulate` | Modulate Entity Transcription Benchmark, People's Speech part (`45b2f14`) | CC BY-SA 4.0, audio not re-hosted | 714 | none |

Names in `calls` and `svq` were found automatically. A hand review of every `calls` spelling found
26 that are ordinary words (Avenue, Bravo, Celiac, Celsius, DJs, Eco, Euros, Expressway, Fridays,
Hill, K-pop, Lacto-Ovo, Mam, Matinee, Metro, Pennies, Raffle, Sierra Tango Charlie, Streamer,
Sundays, Symphony, T-shirt(s), Theatre, Valley, X-Ray). They stay on the lists the systems were given
(the runs are unchanged) and each `suite.json` lists them as `not_names`. Scoring leaves them out:
none of their mentions is scored (34 calls mentions), and writing one is neither an insertion nor a
wrong name.

## Scoring: what is new

- Suites are scored like clips, clustered by recording, with names right by group (same or other
  speaker; noise condition), untaught overwritten, wrong name, ordinary-word and full-transcript error.
- Name-free insertions are also reported **per minute**, and **apart for names taught from other
  recordings**. Those are never said in the recording; a recording's own name may be said in a
  stretch whose reference missed it. AppTek's references do miss names: in stretches marked
  name-free, "And I appreciate that, Marlon" is written "...that, man", and "Okay, Miss Jennifer
  Cole" is left out, while ElevenLabs and ours both write the name.

Effect of the two changes on `calls` (percent; with the 26 non-names scored → left out):

| System | Names right | Name-free stretches, a listed name inserted | … a name from other calls |
| --- | --- | --- | --- |
| ours | 92.8 → 92.8 | 3.8 → 2.6 | 2.4 → 1.2 |
| elevenlabs | 94.6 → 95.5 | 1.7 → 1.7 | 0.0 → 0.0 |
| deepgram | 91.1 → 91.9 | 1.2 → 1.2 | 0.2 → 0.2 |
| whisper | 89.9 → 90.4 | 2.6 → 2.2 | 1.4 → 1.0 |
| parakeet | 87.7 → 88.1 | 16.3 → 15.6 | 15.1 → 13.9 |
| qwen-context | 94.1 → 94.6 | 4.3 → 4.1 | 2.9 → 2.6 |

Before the non-names were left out, five of ours' ten stretches with a name from another call were
"Mam" (its spelling of "ma'am"), "Theatre" and "Fridays". The five that remain are real names from
other calls (Walker, Sarah, Willie, and Minnie twice).

## Runs

- Labels lost their machine names (the runs now span machines): `ours-rtx4090` → `ours`,
  `whisper-rtx4090` → `whisper`, `parakeet-a100` → `parakeet`, `qwen-rtx4090` → `qwen`,
  `qwen-context-rtx4090` → `qwen-context`. `ours-mlx-macmini` and `whisper-a100` keep theirs (they
  exist to compare machines).
- Suite passes ran on rented RTX PRO 6000 and RTX 4090 GPUs, several machines per system, and were
  merged into one run per system with `build/merge_runs.py` (each command in `run.json` records its
  machine). The cost line keeps the v1.1.0 basis (the clip latencies, measured on the RTX 4090 at
  $0.89/h).
- Hosted services: ElevenLabs Scribe v2 and Deepgram Nova-3 ran the suites on 2026-10-14 with the same
  configuration as v1.1.0.
- `ours-mlx-macmini` was not extended to the suites and stays out of the tables.

## Not in v1.2.0

- Earnings-21 (reference-only, scores and item IDs without audio) and ICSI: not built. Both need
  long-form alignment of hour-long recordings; left for v1.3.
- The self-recorded fresh-name protocol was not selected.
