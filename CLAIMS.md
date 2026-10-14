# Making claims with own-names-bench

Anyone may quote this benchmark, including us. These rules apply to every claim, ours first.

## The rules

1. **Only claim what a published results file shows.** Every number must come from a
   `results/scores/<run>.json` in this repository (or a fork that publishes its runs the same
   way), produced by `bench report` from a `results/runs/<run>/` that anyone can inspect.
2. **Give the clustered interval.** Quote the 95% interval next to every rate, and for a
   comparison quote the paired difference with its interval (the "Paired differences" table of
   `REPORT.md`). Intervals are bootstraps over books (clips) or chapters, because mentions in one
   book share a reader, a text and names; do not substitute an item-level interval or test. A
   difference is a claim only where `REPORT.md` marks it **holds** (its interval excludes zero);
   otherwise the claim is "no measurable difference", not "better" or "worse".
3. **Complete runs only.** Quote only runs that `REPORT.md` lists as complete (every expected
   pass made from the current lists, none failed).
4. **Name the benchmark version and the run date.** For example, "own-names-bench v1.1.0, runs of
   2026-10-13/14". A claim about a different version is a different claim.
5. **Name the competitor's configuration.** The model or API model id, how the names were
   given to it (its custom-vocabulary feature), how many it accepted (the `fit` line of the
   run), and the date. "ElevenLabs Scribe v2 with keyterms (all names, 2026-10-13)" and "Deepgram
   Nova-3 with keyterm prompting (the 126 most frequent of 151 names that fit its 500-token
   limit)" are different claims.
6. **Name the task and the list.** Clips with the book's own list, clips with the all-books
   list, or continuous chapters; invented names, traditional names, or both; or a suite (`calls`,
   `svq`, `ami`, `modulate`), and for suites whether the name was taught by the same speaker or
   another one. Audiobook results do not speak for conversation, and the reverse.
7. **Say what ours was given.** Our system is taught each name with a recording of it
   (as Detail Keeper users teach names); hosted services take only the spelling. Every claim
   comparing them says so.
8. **No cherry-picking.** A claim about one metric must not hide a worse result on another
   metric of the same table (for example, names right without untaught names overwritten).
9. **Hosted services change.** A hosted result is a measurement of the service on the date of
   the run. Re-run before repeating an old claim, or date it.

## Template

> On own-names-bench v1.1.0 (clips, the book's own name list, *N* name mentions from *B*
> public-domain audiobooks), *System A* wrote the spoken name right *x*% of the time
> (95% CI *a*–*b*, bootstrap over books), against *y*% (*c*–*d*) for *System B*
> (*configuration*, *date*). Paired difference: *+z* points (95% CI *e* to *f*). With the name
> taken off the list, *System A* wrote another listed name in its place *u*% of the time
> (*g*–*h*), *System B* *v*% (*i*–*j*); ordinary-word error *p*% against *q*%. *System A* is
> taught each name with one recording; *System B* takes the spelling only. Results:
> `results/scores/<run>.json`, `REPORT.md`.

## Not allowed

- Rounding an interval away, or quoting the better end of it.
- Comparing numbers from different benchmark versions, lists or tasks.
- Calling a system "better" on a difference whose interval includes zero, or citing an
  item-level significance test.
- Quoting a run that `REPORT.md` lists as incomplete.
- Quoting the all-books list for a service that could not take it (marked n/a).
