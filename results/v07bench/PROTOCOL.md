# v0.7 bench protocol: the v1.2.0 audiobook suite as a selection target

Changed by James on 2026-10-17, written down here before any v0.7 adapter was scored on it:

> "we need to change the protocol as this is the number we're chasing now so we can't skip running it"

The number being chased is **false name insertions on the v1.2.0 audiobook clips** (name-free items where a listed
name is written): under 1%, ideally ElevenLabs Scribe v2's 0.2% (1/408).

## 1. The v1.2.0 audiobook suite is now a selection target

Any candidate may be scored on the own-names-bench v1.2.0 audiobook clips. From this change on, its numbers are **not
an unbiased held-out estimate**: they are used to choose between candidates, so the chosen candidate's figure on it is
optimistic. Every report that uses v1.2.0 audiobook numbers produced under this protocol says so.

## 2. Aggregates only

Only aggregate counts and rates are read: names right, false insertions (name-free items with a listed name inserted),
untaught names overwritten, ordinary-word error, and their clustered confidence intervals and paired differences.

Never read: per-clip outputs, references, audio, or which clips failed. Code may compute the aggregates from the pass
outputs; no human or agent reads individual outputs, lists failing clips, or prints per-clip rows. This limits
overfitting to the 408 name-free items and 1,107 name mentions.

## 3. Every look is logged

Each time any system is scored on the v1.2.0 audiobook clips under this protocol, a row goes into
`results/v07bench/LOOKS.md`: system, adapter SHA-256, date, and the numbers read. A look not in that table did not
happen under this protocol.

## 4. The launch claim needs a fresh held-out test

Because the v1.2.0 audiobook suite is now a selection target, the launch claim cannot rest on it. It needs a **sealed
audiobook suite** built like the sealed v1.3 conversation suite: from held-out books, sealed before the final choice
is made, and run once on the chosen system. Building it is a separate task.

The sealed v1.3 conversation suite (`onb-v13-conv-SEALED`, suite hash dbff73e6…0fdd3) stays once-only and is not run
under this protocol.
