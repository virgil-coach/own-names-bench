#!/usr/bin/env python3
"""Sensitivity of align_book.py's piece gates, measured on a DEV book (bookdev's Phantastes, never a suite book).

Kept pieces are re-aligned (the same semi-global Viterbi over the same posteriors) against their reference and against
corrupted references: one word deleted (the audio says a word the reference lacks: the case that would make a
name-free clip unsafe), one word replaced by a random word of the book, one word inserted. A gate that works rejects
the corrupted references and keeps the true ones. Data tooling only: no transcript is decoded.

usage: calib.py <key> [n]    (BOOKS13_ROOT pointing at the calibration root)
"""
import json
import random
import sys

import numpy as np

from align_book import HOP, LETTER_P, NAME_MIN, PIECE_MEAN, UNEXPLAINED, WORD_MIN, Emitter, spell, viterbi
from common import WORK
from lore_text import fold


def gate(lp: np.ndarray, words: list[str], em: Emitter, letters: np.ndarray) -> tuple[bool, dict]:
    sp = [spell(fold(w), em.vocab) for w in words]
    sp = [s for s in sp if s]
    toks, wr = [], []
    for s in sp:
        if toks:
            toks.append(em.sep)
        f = len(toks)
        toks += s
        wr.append((f, len(toks) - 1))
    cost = np.full(len(wr), 1e6)
    cost[0] = 0.0  # enter only at the first word
    states = viterbi(lp, np.array(toks), wr, cost, em.blank)
    lastok = 2 * wr[-1][1] + 1
    chars: dict[int, float] = {}
    unexp = 0
    for t, s in enumerate(states.tolist()):
        if s >= 0 and s % 2 == 1:
            ci = (s - 1) // 2
            chars[ci] = max(chars.get(ci, 0.0), float(np.exp(lp[t, toks[ci]])))
        elif letters[t] >= LETTER_P:
            unexp += 1
    scores = [float(np.mean([chars.get(c, 0.0) for c in range(f, l + 1)])) for f, l in wr]
    reached = max(states.tolist()) >= lastok
    ok = reached and np.mean(scores) >= PIECE_MEAN and min(scores) >= WORD_MIN and unexp <= UNEXPLAINED
    return ok, {"mean": round(float(np.mean(scores)), 3), "min": round(min(scores), 3), "unexplained": unexp, "reached": reached}


def main() -> None:
    key = sys.argv[1]
    n = int(sys.argv[2]) if len(sys.argv) > 2 else 150
    em = Emitter.__new__(Emitter)
    from transformers import Wav2Vec2Processor
    from align_book import ALIGNER
    em.proc = Wav2Vec2Processor.from_pretrained(ALIGNER["repo"], revision=ALIGNER["revision"])
    em.vocab = em.proc.tokenizer.get_vocab()
    em.blank = em.proc.tokenizer.pad_token_id
    em.sep = em.vocab["|"]
    em.letters = np.array(sorted(v for k, v in em.vocab.items() if len(k) == 1 and (k.isalpha() or k == "'")))
    rows = [json.loads(line) for line in (WORK / "books" / key / "pieces.jsonl").open()]
    rng = random.Random(5)
    rows = rng.sample(rows, min(n, len(rows)))
    vocab_words = [w["word"] for r in rows for w in r["words"]]
    lps: dict[int, np.ndarray] = {}
    res: dict[str, list] = {"true": [], "deleted": [], "replaced": [], "inserted": []}
    for r in rows:
        if r["chapter"] not in lps:
            lps[r["chapter"]] = np.load(WORK / "books" / key / "src" / f"{r['chapter']:03d}.lp.npy").astype(np.float32)
        lp = lps[r["chapter"]][int(r["start"] * 16000) // HOP:int(r["end"] * 16000) // HOP]
        letters = np.exp(lp[:, em.letters]).max(axis=1)
        words = [w["word"] for w in r["words"]]
        if len(words) < 4:
            continue
        i = rng.randrange(1, len(words) - 1)
        variants = {"true": words, "deleted": words[:i] + words[i + 1:],
                    "replaced": words[:i] + [rng.choice([v for v in vocab_words if fold(v) != fold(words[i])])] + words[i + 1:],
                    "inserted": words[:i] + [rng.choice(vocab_words)] + words[i:]}
        for k, v in variants.items():
            ok, d = gate(lp, v, em, letters)
            res[k].append((ok, d, len(fold(words[i]))))
    out = {}
    for k, v in res.items():
        out[k] = {"n": len(v), "kept": sum(ok for ok, _, _ in v),
                  "kept_when_changed_word_has_3plus_letters": sum(ok for ok, _, L in v if L >= 3),
                  "n_3plus": sum(L >= 3 for _, _, L in v)}
    print(json.dumps(out, indent=1))
    (WORK / f"calib_{key}.json").write_text(json.dumps({"summary": out, "rows": {k: [d for _, d, _ in v] for k, v in res.items()}}, indent=1))


if __name__ == "__main__":
    main()
