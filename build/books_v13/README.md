# own-names-bench v1.3 audiobook test suite, `books13` (held out, sealed)

A frozen audiobook test suite for the Detail Keeper launch claim, from 20 LibriVox books and 20 readers that no
benchmark, dev set, lore set or adapter training set (v0.3.0 to v0.7.0) has used. It replaces the v1.2.0 audiobook clips
as the held-out audiobook number: under the 2026-10-17 protocol those became a selection target
(`results/v07bench/PROTOCOL.md` §4, 11 looks in `LOOKS.md`, branch `v7c/mlx-suites`). It is in the benchmark's dataset
format and is scored **once per final system** by the benchmark's own code as the clips task. Nothing was scored on it
while it was built.

**Rule.** Do not read, train, tune, select or smoke-test on this data. No recognizer, spotter, system or API was run on
its audio during the build. The only model that touched the audio is the forced aligner that placed the book's own
words on it (`align_book.py`). Validity was checked with data tooling only: hashes, levels, alignment scores, and the
benchmark's scorer given the references as transcripts.

**Deviation: sealed after the final choice.** The conversation suite was sealed before any final adapter existed.
This suite was sealed on 2026-10-27, after the final system had been chosen and frozen: v7c (HF
`virgil-coach/own-names-qwen3-asr` v0.7.0, `audio-text-note`, adapter SHA-256 `de91437d…1226c`) with the name guard and
re-read, in Detail Keeper's MLX engine. Nothing about the suite could feed back into that system, and no system was run
on it. The suite measures a frozen system. It did not help choose one.

## Where it is

| Path (this Mac, `Jamess-MacBook-Pro-2`; outside every repo) | What |
| --- | --- |
| `~/workspace/jl/onb-v13-books-SEALED/data/` | the suite, read-only: `manifest.json` (entries, lists, clips, mentions, name-free items, attribution), `audio/clips/<book>/*.flac`, `audio/enroll/<book>/*.flac`, `LICENCE.txt`, `ATTRIBUTION.csv` |
| `~/workspace/jl/onb-v13-books-SEALED/MANIFEST.json`, `SHA256SUMS`, `SEALED.txt` | the seal: every file's SHA-256 and the suite hash |
| `~/workspace/jl/onb-v13-books-SEALED/build/` | build files: exclusion lists, candidates, aligned pieces, name plans, build stats, the contamination and validity reports |
| Mac mini `~/workroots/books13/` | the alignment run's section audio and aligner posteriors (not part of the suite) |

**Suite hash `3d6d8b65d4810c4f9571e8274bf02659a1bb507e65c7d0c333a48145a41e202f`** (3,154 files, 373 MB), sealed
2026-10-27T00:34:29Z from build commit `380deec`. `data/manifest.json` SHA-256 `e02be6a4…8257c8`. The suite hash is
the SHA-256 of `SHA256SUMS`. Check a copy with `cd data && shasum -a 256 -c ../SHA256SUMS`.

In git: this card, the build code and `sealed/`: the seal manifest, `SHA256SUMS`, the contamination and validity
reports, build and curation counts, and the aligner gate calibration on a dev book. They hold counts and hashes only.
The audio, references and name lists are not in git, and nothing has been uploaded. At launch the `data/` folder is
meant for HF `virgil-coach/own-names-bench` under its `LICENCE.txt` and `ATTRIBUTION.csv`.

## What is in it

The benchmark's clips task: every mention is run with its book's own list (9 to 176 names, most frequent first), and
again with the spoken name taken off it (`own-minus`). Every name-free clip is run with the list. Every system also
runs with no list. Mentions are grouped `invented` / `traditional` by book, as in v1.2.0.

| Group | Books | Readers | List entries | Mentions | Names mentioned | Name-free clips | Clip hours |
| --- | --- | --- | --- | --- | --- | --- | --- |
| invented | 11 | 11 | 395 | 777 | 315 | 660 | 3.88 |
| traditional | 9 | 9 | 500 | 323 | 323 | 540 | 2.33 |
| **total** | **20** | **20** | **895** | **1,100** | **638** | **1,200** | **6.21** |

There are 2,256 clips of 3.5-15 s. The name-free clips add up to 193.2 minutes, so one insertion is 0.083% of them.
That is small enough to tell 0.2% from 1%.

| Book (key) | Group | Reader | Entries | Mentions | Name-free | Clip h |
| --- | --- | --- | --- | --- | --- | --- |
| The Antiquary, Scott (`antiquary_sk`) | invented | skoval | 66 | 97 | 60 | 0.43 |
| The Devolutionist and the Emancipatrix, Flint (`devolutioniste_1212`) | invented | klbonds | 11 | 26 | 60 | 0.23 |
| The Mouthpiece of Zitu, Giesy (`mouthpiece_of_zitu_2209`) | invented | tjfria | 30 | 66 | 60 | 0.33 |
| The Old-Fashioned Fairy Book, Harrison (`oldfashionedfairybook_cb`) | invented | Carol Box | 26 | 67 | 60 | 0.34 |
| The Perfect World, Scrymsour (`perfect_world_2006`) | invented | MrsLSid | 37 | 69 | 60 | 0.34 |
| Plain Tales from the Hills, Kipling (`plain_tales_hill_1008`) | invented | Mike Harris | 67 | 136 | 60 | 0.51 |
| The Princess Galva, Whitelaw (`princess_galva_ma_1110`) | invented | MaryAnn | 29 | 59 | 60 | 0.33 |
| The Romance of a Mummy, Gautier (`romanceofamummy_1410`) | invented | Deon Gines | 27 | 54 | 60 | 0.32 |
| The Rulers of the Lakes, Altsheler (`rulers_of_the_lakes_kg_1704`) | invented | Kenneth Sergeant Gaghan | 27 | 49 | 60 | 0.29 |
| South Sea Tales, London (`southseatales_2011`) | invented | Warren Kati | 53 | 103 | 60 | 0.44 |
| The Virgin of the Sun, Haggard (`virginofthesun_2402`) | invented | Andy Sames | 22 | 51 | 60 | 0.31 |
| The Legends and Myths of Hawaii, Kalakaua (`legendsd_myths_hawaii_1903`) | traditional | Lynda Marie Neilson | 176 | 137 | 60 | 0.54 |
| Mexican Archaeology, Joyce (`mexicanarcaeology_2603`) | traditional | Katharina21 | 159 | 60 | 60 | 0.31 |
| Typee, Melville (`typee`) | traditional | Michael Scherer | 28 | 27 | 60 | 0.24 |
| Legends of Charlemagne, Bulfinch (`legends_charlemagne_1002`) | traditional | Jacquerie | 33 | 20 | 60 | 0.22 |
| Japanese Fairy Tales, Ozaki (`jap_fairytales_0808`) | traditional | Scott Robbins | 28 | 25 | 60 | 0.23 |
| Indian Fairy Tales, Jacobs (`indian_fairy_tales_1304`) | traditional | Gabriela Cowan | 21 | 18 | 60 | 0.22 |
| The Tale of Genji, Murasaki / Suematsu (`genji_monogatori_1305`) | traditional | meyerli | 26 | 15 | 60 | 0.20 |
| The Swedish Fairy Book, Stroebe (`theswedishfairybook_2607`) | traditional | Hox | 20 | 14 | 60 | 0.20 |
| Tales from Silver Lands, Finger (`silverlands_2404`) | traditional | Lynette Caulkins | 9 | 7 | 60 | 0.17 |

The traditions here are Hawaiian, Aztec and Maya, Marquesan, Carolingian, Japanese, Indian, Swedish and South
American. None of them is Homer, Virgil, Norse myth or Malory, which are the v1.2.0 traditional books.

## How it was built (`run.sh`; each script documents itself)

1. **Exclusions** (`excl.py`). The suite may not use any reader, LibriVox project, archive.org item, Gutenberg text or
   work (a title across readings and volumes) of these sources:
   - own-names-bench v1.2.0 (clips and chapters);
   - own-names-bench `dev/bookdev` and `dev/bigcast`;
   - the 70 lore books (train, dev and test), lore's 80 audited candidates and the lore eval sets (`littlebearlabs/lore-*`);
   - every adapter training attribution in the 13 lore-poc worktrees (`train/*`, `release/v0.7.0`,
     `data/conv-names-v1`): LibriVox training books and readers, LibriTTS speakers and their books, and LibriTTS-R
     train-clean-100 speakers and books;
   - the v0.3.0 template books;
   - every LibriSpeech dev and test speaker and book, which is where the sealed conversation suite's readers come from.

   That is 532 readers, 624 projects, 420 Gutenberg texts and 146 works. Names are excluded in two ways. A name is
   dropped if it matches exactly a training-book list name, a generated training name (`ctxft/gen.py`) or a
   synthetic-set term (11,294 names). It is also dropped by the bookdev collision rule: equal, within 25% letter
   distance of, or sharing a 4+ letter word with any of 11,086 held names.
2. **Books** (`find_books.py`, `rank_books.py`, `manifest.py`). The LibriVox API was searched by 114 authors and 8
   genres: 4,805 projects and 677 usable (project, reader) pairs. A pair is usable when the book was first published
   before 1931, has a Gutenberg text, and the reader read at least 2 h of it alone. The pairs were ranked by how many
   invented names their text gives after the collision rule (text only). Picks are one book per reader, invented
   books first, and no shared series. Only the sections the picked reader read alone are used.
3. **Alignment, with no recognizer** (`align_book.py`, on the Mac mini, MPS). The v1.2.0 clips' source matched a
   recognizer's transcript to the book. Here the book text is placed on the audio by forced alignment alone, with
   `facebook/wav2vec2-large-960h-lv60-self` (Apache 2.0, rev `54074b1c`, the conversation suite's aligner):
   - Each section is located in the book: a 30 s probe is tried at the cursor and at the places where the section
     title is printed, then over the whole book.
   - It is then aligned chunk by chunk (30 s) with a semi-global CTC Viterbi. The path may start at any word near the
     cursor, and a garbage state absorbs the LibriVox preamble and credits.
   - Sections are cut at pauses by the v1.2 cutter (`lore_text.segment`, vendored unchanged).

   A piece is kept only when all of these hold:
   - every book word inside it is aligned inside it, its words are consecutive, and no word straddles a cut;
   - its neighbouring words are aligned;
   - it has no digits;
   - every non-name word scores at least 0.5, every name word at least 0.1, and the mean is at least 0.7;
   - at most one frame shows a letter the text does not account for. A name-free clip may have none, and every one of
     its words must score at least 0.5.

   136.0 h went in and 102.3 h were kept.
4. **Gate calibration on a dev book** (`calib.py`, `sealed/calib_dev_phantastes.json`). The book was bookdev's
   Phantastes, never a suite book. 200 pieces were aligned against their true text and against corrupted text. With
   the gates above, the true text was kept for 190 of 200. A word the audio says but the reference lacks got through
   18 of 200 times, and only once for a word of three letters or more; names are longer than that. A replaced word got
   through 8 of 200 times, and an inserted word 3 of 200. The stricter name-free gate kept 179, 11, 4 and 3.
5. **Names** (`lore_text.find_names`, the v1.2 rule; `curate.py`; hand list `curation.json`, read as text). 1,298 names
   were found. 21 were removed as Latin, foreign or common nouns and misprints, and 23 were merged as plurals or
   variants. 223 were dropped by the collision rule (190 close to a held name, 23 training or generated names, 10
   sharing a word), and every piece that says a dropped name is left out (2,530 pieces). 1,031 names were kept.
6. **Suite** (`build.py`, build_dataset.py's protocol):
   - Taught recording: one per name, the reader's best isolated occurrence, cut with lore `enroll.py`'s rules (score
     at least 0.3, 0.25-1.4 s, no possessive or variant, 60 ms margins). 79 names have no usable cut and are not listed.
   - Mentions: 3 distinct pieces per invented name and 1 per traditional name, never the piece a taught recording came
     from.
   - Name-free clips: 60 per book, 4-15 s. Their reference holds no listed name of any books13 book.
   - Any piece whose reference shares an 8-word run with a held text is left out (142 pieces). The held texts are the
     70 lore books' full texts, bookdev and bigcast texts, v1.2.0 references and chapters, and lore eval-set
     references.

## Contamination (`check.py`, `sealed/contamination.json`): **PASS**

Every failure count is 0:
- readers excluded: 0 of 20;
- books whose project, archive item, Gutenberg text or work is excluded: 0. No book is of a held series, and no two
  suite books share a work;
- listed names that are training or generated names: 0 of 895. Names that are equal, close or share a word with a held
  name: 0;
- suite audio files equal to a held file by file or PCM SHA-256: 0 of 3,151, against 11,896 hashes from v1.2.0,
  bookdev and bigcast. No two clips are the same file;
- clip references that share an 8-word run with a held text: 0 of 2,256, against 9.88 M runs.

Reported, not failed:
- 32 of the 895 listed names (27 mentions) are in the Wikidata name lists (`lore-name-lists`), which fed YODAS and
  synthetic data.
- 11 of the 20 readers are LibriSpeech train-clean-360 / train-other-500 speakers. 9 suite books have a LibriVox
  project in LibriSpeech, and 5 of them through the suite reader's own reading (9 LibriSpeech chapters). None of this
  is in any of our training data, which used LibriTTS-R train-clean-100 and LibriTTS dev only. The base Qwen3-ASR, the
  aligner and the hosted systems may have trained on LibriSpeech, as they may have on the v1.2.0 books.
- YODAS voices cannot be checked by name.

## Validity (`seal.py`, `sealed/validity.json`): **PASS**

No problem was found:
- Every file has its hash. Every clip decodes at 16 kHz mono, is 3.5-15 s as listed, and is not clipped, silent or
  below -60 dBFS (median -26.6 dBFS).
- Every mention span reads as its entry's spelling, the entry is on the clip's list, and the aligned name lies inside
  the clip at a median 1.0 dB above the clip's level (p5 -3.6 dB).
- No listed name is in a name-free reference. Taught recordings are 0.15-2.6 s.
- The benchmark's loader reads the folder with every hash checked and builds 5,612 passes (none / own / own-minus).
- Given the references as transcripts, the benchmark's scorer finds:

  | Measure | Result |
  | --- | --- |
  | Names right | 1,100 of 1,100 |
  | Overwritten, wrong name or insertion | 0 |
  | Word errors | 0 of 55,743 |

  The invented / traditional split is reported. A dry `bench report` on those transcripts produced the scores.

## Deviations from the conversation v1.3 recipe

- **Sealed after the final system was chosen.** See the top of this card.
- **Source and references.** The source is held-out LibriVox books, not a corpus's test split. References are the
  Gutenberg text placed by forced alignment, not human transcripts of the recording. The places where a reader departs
  from the text are caught by alignment gates, calibrated on a dev book above. They are not checked by listening.
- **Storage.** The suite is stored on this Mac, not on the RunPod volume. No pod was used, and the spend was $0.
- **No augmentation and no conditions.** The clips are the recordings as LibriVox published them, at 16 kHz.
- **Lists are each book's own names**, as in the v1.2.0 clips, not 40-name lists. There is no `name_seen_in_train`
  group, because every name seen in training was excluded outright.

## Deviations from the v1.2.0 clips

- No recognizer in the cut, which costs yield. The aligner is wav2vec2-large-960h-lv60-self, not MMS_FA. The cutter and
  the name finder are the same code.
- Name-free clips: 60 per book against 34, with stricter alignment gates.
- No all-books list and no chapters task. Every system runs none / own / own-minus (and `ours` `own-xr`, 1 pass).
- Multi-reader LibriVox projects were used where one reader read 2 h or more alone, and only that reader's sections.
  One pick, Four and Twenty Fairy Tales (SaraHale), was dropped after alignment: her sections are one tale with no
  names. South Sea Tales was added to reach 1,000 mentions.
- The collision rule is bookdev's, which is stricter than v1.2's 5-name `TRAINED_NAMES`. It drops a name's every
  piece, so some books lose their main names (Oldbuck and Lovel in The Antiquary, for example).
- Pools: the invented group includes period adventure fiction whose names the author made up (Scott, Kipling,
  Altsheler, London, Haggard). The traditional group includes one non-fiction book (Mexican Archaeology) and Typee
  (Marquesan names).
- `manifest.json` says `"version": "1.2.0"` because that is the data format the benchmark code accepts. The suite
  itself is `suite: books13`, `suite_version: 1.3.0-test`. A run's `run.json` will still name
  `virgil-coach/own-names-bench@v1.2.0` as its dataset, which is a constant in the code. The run is identified by its
  `dataset_fingerprint` and `manifest_sha256` (`e02be6a4…`).

## Scoring it once

Use the code and engine of the frozen system: own-names-bench `v7c/mlx-suites` @ `1d205d1` (as `pod/mac_mlx.sh`),
Detail Keeper engine `af939d6`, on a bench Mac with the v7c adapter folder.

Before the run:
1. Copy `data/` and check it with `shasum -a 256 -c ../SHA256SUMS`.
2. The spotter's pronunciation table (`own_names_bench/ours_ref/g2p.json`) holds only v1.2.0 names. Add the books13
   names to it with `build/g2p_table.py` (espeak-ng 1.52.0, text only), or the run needs espeak-ng installed.

Then run and report:

```bash
W=$HOME/workroots/v7c-release
cd $W/code   # own-names-bench @ 1d205d1
HF_HUB_CACHE=$W/hf HF_HUB_OFFLINE=1 DETAILKEEPER_BUILT=$W/built DETAILKEEPER_BENCH=$W/bin/detailkeeper-bench \
DETAILKEEPER_ENGINE_COMMIT=af939d6 BENCH_WAV_CACHE=$W/wav-books13 OURS_MLX_VARIANTS=none,own \
OURS_MLX_ADAPTER=$W/adapters/qwen17B_audio_heard_v7c OURS_MLX_ADAPTER_VERSION=v0.7.0 \
OURS_MLX_ADAPTER_SHA256=de91437d4fc828b49605e6482a32b817d55ac4853d1714ac1e2bf9be8f61226c \
  uv run --frozen bench --data $W/books13 run --system ours-mlx --label books13-v7c-mlx --out results/books13 --no-chapters
op run --env-file keys.env -- uv run --frozen bench --data $W/books13 run --system elevenlabs --label books13-elevenlabs \
  --out results/books13 --no-chapters
uv run --frozen bench --data $W/books13 report --runs results/books13 --out results/books13/scores --baseline books13-v7c-mlx
```

## Licence and attribution

- Audio: LibriVox recordings, public domain in the US.
- Texts: Project Gutenberg, public domain in the US.
- Annotations: CC BY 4.0, (c) 2026 Little Bear Labs, Inc.

Every book, reader, LibriVox page, archive.org item, Gutenberg id and public-domain basis is in `data/ATTRIBUTION.csv`
and in the manifest's `attribution`. The aligner (Apache 2.0) is not distributed.
