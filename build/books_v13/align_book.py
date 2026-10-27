#!/usr/bin/env python3
"""LibriVox sections -> aligned 3.5-15 s pieces of the v1.3 audiobook test suite, with no recognizer.

The v1.2.0 clips' source (lore-poc books/pipeline.py) cut chapters at pauses, *recognized* each piece and matched the
recognizer's words to the book. Here no recognizer runs on the audio: the book text is placed on the audio by forced
alignment alone, and the only model is the CTC character aligner (wav2vec2-large-960h-lv60-self, Apache 2.0, the
v1.3 conversation suite's aligner). Its posteriors are used only along the forced path of the known text and to find
audio the text does not explain; no transcript is ever decoded.

Per book (build/books.json and build/texts/<key>.txt from manifest.py), per section read by the book's reader:
  fetch     LibriVox 64 kb/s mp3 from archive.org -> 16 kHz mono FLAC (build/books/<key>/src/<n>.flac)
  emit      the aligner's log posteriors, 20 s windows with 1 s of context on each side (src/<n>.lp.npy, float16)
  align     long-form forced alignment, chunk by chunk (30 s): a semi-global CTC Viterbi over the book's words, which
            may start at any word of a text window near the cursor (skipping text costs SKIP nats a word) and may begin
            and end in a garbage state (the LibriVox preamble and credits, text not in the Gutenberg edition), whose
            frames cost GARBAGE nats more than the best symbol. Words that end MARGIN before a chunk's end are kept and
            the next chunk starts after them; a chunk whose words mostly score badly is not kept, and the next one looks
            for the text again over a wide window (lost).
  cut       the section cut at pauses into 5-15 s pieces (lore_text.segment, the v1.2 cutter, unchanged); a piece is
            kept when every book word inside it is aligned inside it, its words are consecutive in the book, no word
            straddles a cut, its reference has no digits, its mean word score is >= PIECE_MEAN, every non-name word
            >= WORD_MIN, every name word >= NAME_MIN, and at most UNEXPLAINED frames of it show a letter (posterior >= 0.5)
            that the aligned text does not account for (speech the reference does not hold)
  names     invented names of the book text (lore_text.find_names, the v1.2 rule) and their mentions in kept pieces
  write     build/books/<key>/{pieces.jsonl, names.json, summary.json, audio/<piece>.flac}

usage: align_book.py <key> [<key> ...]      (on a Mac with MPS, or CPU; one process per machine)
"""
import concurrent.futures
import json
import os
import re
import subprocess
import sys
import time
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np
import soundfile as sf

from common import WORK, log
from lore_text import RATE, Lexicon, find_names, fold, mentions, parse, reference, segment

ALIGNER = {"repo": "facebook/wav2vec2-large-960h-lv60-self", "revision": "54074b1c16f4de6a5ad59affb4caa8f2ea03a119",
           "licence": "Apache 2.0"}
HOP = 320                # samples per aligner frame (20 ms)
WIN_S, CTX_S = 20.0, 1.0
CHUNK = 1500             # frames per alignment chunk (30 s)
MARGIN = 300             # frames: words ending this close to a chunk's end wait for the next chunk
GARBAGE = 0.5            # nats per frame a garbage frame costs over the frame's best symbol
SKIP = 0.5               # nats per book word skipped at a chunk's start (in step)
SKIP_LOST = 0.002        # ... when the text is being looked for again (first chunk of a section, or lost)
FWD, FWD_LOST, BACK_LOST = 220, 6000, 60   # text window, in words
CHUNK_OK = 0.6           # share of a chunk's words scoring >= 0.5 for its words to be kept
PIECE_MEAN, WORD_MIN, NAME_MIN = 0.70, 0.50, 0.10   # calibrated on a dev book: calib.py
UNEXPLAINED = 1
LETTER_P = 0.5
PROBE, LOCATE_SKIP, LOCATE_OK, LOCATE_BACK = 1500, 1500, 0.8, 150  # locate: probe frames, frames skipped, quality, words back
LOST_RELOCATE = 3
NEG = -1e30


# ---------------------------------------------------------------- fetch

def fetch_section(key: str, s: dict) -> Path | None:
    d = WORK / "books" / key / "src"
    d.mkdir(parents=True, exist_ok=True)
    flac = d / f"{s['n']:03d}.flac"
    if flac.exists():
        return flac
    mp3 = d / f"{s['n']:03d}.mp3"
    got = subprocess.run(["curl", "-sSfL", "--retry", "8", "--retry-all-errors", "--retry-delay", "5", "--connect-timeout", "30",
                          "-m", "1800", "-o", str(mp3), s["url"]], capture_output=True, text=True)
    if got.returncode != 0:
        log(f"download failed {s['url']}: {got.stderr.strip()[-200:]}")
        return None
    part = d / f"{s['n']:03d}.part.flac"
    made = subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-i", str(mp3), "-ac", "1", "-ar", str(RATE), "-sample_fmt", "s16",
                           str(part)], capture_output=True, text=True)
    sha = subprocess.run(["shasum", "-a", "256", str(mp3)], capture_output=True, text=True).stdout.split()[0]
    mp3.unlink(missing_ok=True)
    if made.returncode != 0:
        log(f"decode failed {s['url']}: {made.stderr.strip()[-200:]}")
        return None
    (d / f"{s['n']:03d}.mp3.sha256").write_text(sha + "\n")
    part.rename(flac)
    return flac


# ---------------------------------------------------------------- aligner posteriors

class Emitter:
    def __init__(self) -> None:
        import torch
        from transformers import Wav2Vec2ForCTC, Wav2Vec2Processor
        self.torch = torch
        self.device = "mps" if torch.backends.mps.is_available() else "cpu"
        torch.set_num_threads(4)
        self.proc = Wav2Vec2Processor.from_pretrained(ALIGNER["repo"], revision=ALIGNER["revision"])
        self.model = Wav2Vec2ForCTC.from_pretrained(ALIGNER["repo"], revision=ALIGNER["revision"]).to(self.device).eval()
        self.vocab = self.proc.tokenizer.get_vocab()
        self.blank = self.proc.tokenizer.pad_token_id
        self.sep = self.vocab["|"]
        self.letters = np.array(sorted(v for k, v in self.vocab.items() if len(k) == 1 and (k.isalpha() or k == "'")))

    def __call__(self, x: np.ndarray) -> np.ndarray:
        """Log posteriors (T, V) at 20 ms for the whole section, frame f covering samples [f*HOP, f*HOP + 400)."""
        torch = self.torch
        T = max(0, (len(x) - 400) // HOP + 1)
        out = np.zeros((T, len(self.vocab)), dtype=np.float32)
        win, ctx = int(WIN_S * RATE), int(CTX_S * RATE)
        for a in range(0, len(x), win):
            b = min(len(x), a + win)
            lo, hi = max(0, a - ctx), min(len(x), b + ctx)
            seg = x[lo:hi]
            seg = (seg - seg.mean()) / (seg.std() + 1e-7)
            with torch.inference_mode():
                lp = torch.log_softmax(self.model(torch.from_numpy(seg.astype(np.float32))[None].to(self.device)).logits[0].float(), -1)
            lp = lp.cpu().numpy()
            f0, f1 = a // HOP, min(T, (b + HOP - 1) // HOP)
            off = lo // HOP
            take = lp[f0 - off:f1 - off]  # lo is a multiple of HOP (window and context are)
            n = min(len(take), f1 - f0)
            out[f0:f0 + n] = take[:n]
            if n < f1 - f0:  # the window's tail frames: repeat the last (only at the very end of a section)
                out[f0 + n:f1] = take[n - 1:n] if n else 0
        return out


# ---------------------------------------------------------------- semi-global CTC Viterbi

def viterbi(lp: np.ndarray, tokens: np.ndarray, words: list[tuple[int, int]], entry_cost: np.ndarray, blank: int) -> np.ndarray:
    """Per frame: CTC state (index into the blank-interleaved token sequence) or -1 (garbage before the text) / -2
    (garbage after). words: (first token, last token) per word; the path enters at a word's start (paying entry_cost
    of that word) and leaves after a word's end."""
    T = lp.shape[0]
    S = 2 * len(tokens) + 1
    lab = np.full(S, blank, dtype=np.int64)
    lab[1::2] = tokens
    emit = lp[:, lab]
    garbage = lp.max(axis=1) - GARBAGE
    can2 = np.zeros(S, dtype=bool)
    can2[3::2] = tokens[1:] != tokens[:-1]
    entry = np.full(S, NEG)
    exitm = np.zeros(S, dtype=bool)
    for k, (f, l) in enumerate(words):
        entry[2 * f] = max(entry[2 * f], -entry_cost[k])
        entry[2 * f + 1] = max(entry[2 * f + 1], -entry_cost[k])
        exitm[2 * l + 1] = exitm[2 * l + 2] = True
    back = np.zeros((T, S), dtype=np.int8)
    g1_from = np.full(T, -1, dtype=np.int64)
    dp = emit[0] + entry
    g0, g1 = garbage[0], NEG
    exit_idx = np.flatnonzero(exitm)
    for t in range(1, T):
        stay = dp
        one = np.empty(S)
        one[0], one[1:] = NEG, dp[:-1]
        two = np.full(S, NEG)
        two[2:] = np.where(can2[2:], dp[:-2], NEG)
        ent = entry + g0
        best = stay
        choice = np.zeros(S, dtype=np.int8)
        for c, v in ((1, one), (2, two), (3, ent)):
            m = v > best
            best = np.where(m, v, best)
            choice[m] = c
        back[t] = choice
        ex = dp[exit_idx]
        j = int(ex.argmax())
        if ex[j] > g1:
            g1 = ex[j] + garbage[t]
            g1_from[t] = exit_idx[j]
        else:
            g1 = g1 + garbage[t]
        g0 = g0 + garbage[t]
        dp = best + emit[t]
    # end: in the garbage after, or in an exit state, or never entered
    ex = np.where(exitm, dp, NEG)
    s_end = int(ex.argmax())
    states = np.full(T, -1, dtype=np.int64)
    if max(ex[s_end], g1) < g0:
        return states
    t = T - 1
    if g1 >= ex[s_end]:
        while t >= 0 and g1_from[t] < 0:
            states[t] = -2
            t -= 1
        if t < 0:
            return states  # cannot happen: g1 > NEG needs an entry
        states[t] = -2
        s = int(g1_from[t])
        t -= 1
    else:
        s = s_end
    while t >= 0:
        states[t] = s
        c = back[t, s]
        if c == 3:
            states[:t] = -1
            break
        s -= int(c)
        t -= 1
    return states


# ---------------------------------------------------------------- one section

def spell(unit_norm: str, vocab: dict) -> list[int]:
    return [vocab[c] for c in unit_norm.upper() if c in vocab]


def chunk_words(lp: np.ndarray, t0: int, t1: int, lo: int, hi: int, cursor: int, skip: float, spelled: list[list[int]],
                em: "Emitter", letters_p: np.ndarray) -> tuple[list[dict], np.ndarray]:
    """One chunk [t0, t1) aligned against book words [lo, hi): its words [{unit, f0, f1, score}] and its mask of frames
    with a letter (posterior >= LETTER_P) on a blank, separator or garbage state."""
    toks: list[int] = []
    wr: list[tuple[int, int]] = []
    for k in range(lo, hi):
        if toks:
            toks.append(em.sep)
        f = len(toks)
        toks += spelled[k]
        wr.append((f, len(toks) - 1))
    cost = np.array([skip * abs(k - cursor) for k in range(lo, hi)])
    states = viterbi(lp[t0:t1], np.array(toks, dtype=np.int64), wr, cost, em.blank)
    tok_word = np.full(len(toks), -1, dtype=np.int64)
    for i, (f, l) in enumerate(wr):
        tok_word[f:l + 1] = i
    got: dict[int, dict] = {}
    mask = np.zeros(t1 - t0, dtype=bool)
    for t, s in enumerate(states.tolist()):
        if s >= 0 and s % 2 == 1:
            ci = (s - 1) // 2
            i = int(tok_word[ci])
            if i >= 0:
                g = got.setdefault(i, {"f0": t0 + t, "f1": t0 + t + 1, "chars": {}})
                g["f1"] = t0 + t + 1
                g["chars"][ci] = max(g["chars"].get(ci, 0.0), float(np.exp(lp[t0 + t, toks[ci]])))
        elif letters_p[t0 + t] >= LETTER_P:
            mask[t] = True
    ws = []
    for i in sorted(got):
        f, l = wr[i]
        sc = [got[i]["chars"].get(c, 0.0) for c in range(f, l + 1)]
        ws.append({"unit": lo + i, "f0": got[i]["f0"], "f1": got[i]["f1"], "score": round(float(np.mean(sc)), 3)})
    return ws, mask


def quality(ws: list[dict]) -> float:
    return sum(w["score"] >= 0.5 for w in ws) / len(ws) if ws else 0.0


def locate(lp: np.ndarray, t0: int, spelled: list[list[int]], hints: list[int], em: "Emitter", letters_p: np.ndarray) -> int | None:
    """Where in the book the audio after frame t0 is: a probe of PROBE frames (starting LOCATE_SKIP frames on, past a
    LibriVox preamble when there is room) aligned against a window at each hint (the cursor, the section title's places
    in the text), then, if none fits, against every window of the book. Returns the probe's first aligned word, or None."""
    T = lp.shape[0]
    a = t0 + LOCATE_SKIP if T - t0 > LOCATE_SKIP + PROBE else t0
    b = min(T, a + PROBE)
    if b - a < 250:
        return None
    n = len(spelled)

    def probe(lo: int) -> tuple[float, int | None]:
        lo = max(0, lo)
        hi = min(n, lo + FWD_LOST)
        ws, _ = chunk_words(lp, a, b, lo, hi, lo, SKIP_LOST, spelled, em, letters_p)
        if len(ws) < 20:
            return 0.0, None
        return quality(ws), ws[0]["unit"]

    for h in hints:
        q, u = probe(h - BACK_LOST)
        if q >= LOCATE_OK:
            return u
    best = (0.0, None)
    for lo in range(0, n, FWD_LOST - 400):
        q, u = probe(lo)
        if q > best[0]:
            best = (q, u)
    return best[1] if best[0] >= LOCATE_OK else None


def align_section(lp: np.ndarray, units: list[dict], spelled: list[list[int]], cursor: int, em: "Emitter",
                  hints: list[int]) -> tuple[list[dict], np.ndarray, int, dict]:
    """Aligned words of one section: [{unit, f0, f1, score}], the per-frame unexplained-letter mask, the new cursor,
    and counts. The section's place in the book is located first (locate), and again after LOST_RELOCATE chunks in a row
    are lost."""
    T = lp.shape[0]
    letters_p = np.exp(lp[:, em.letters]).max(axis=1)
    unexplained = np.zeros(T, dtype=bool)
    words_out: list[dict] = []
    stats: Counter = Counter()
    u = locate(lp, 0, spelled, [cursor] + hints, em, letters_p)
    stats["sections located" if u is not None else "sections not located"] += 1
    if u is not None:
        cursor = max(0, u - LOCATE_BACK)
    t0, lost, lost_run = 0, True, 0
    while t0 < T - 25:
        t1 = min(T, t0 + CHUNK)
        final = t1 == T
        lo = max(0, cursor - (BACK_LOST if lost else 0))
        hi = min(len(units), cursor + (FWD_LOST if lost else FWD))
        if hi <= lo:
            break
        ws, mask = chunk_words(lp, t0, t1, lo, hi, cursor, SKIP_LOST if lost else SKIP, spelled, em, letters_p)
        unexplained[t0:t1] = mask  # a later chunk re-aligns the frames after the words kept here
        keep = ws if final else [w for w in ws if w["f1"] <= t1 - MARGIN]
        if keep and quality(keep) >= CHUNK_OK:
            words_out += keep
            cursor = keep[-1]["unit"] + 1
            t0 = keep[-1]["f1"] if not final else T
            lost, lost_run = False, 0
            stats["chunks kept"] += 1
        else:
            stats["chunks lost"] += 1
            t0 = t1 if final else max(t0 + 1, t1 - MARGIN)
            lost = True
            lost_run += 1
            if lost_run == LOST_RELOCATE and t0 < T - 25:
                u = locate(lp, t0, spelled, [cursor], em, letters_p)
                stats["relocated" if u is not None else "relocation failed"] += 1
                if u is not None:
                    cursor = max(0, u - LOCATE_BACK)
    return words_out, unexplained, cursor, stats


def title_hints(title: str, units: list[dict]) -> list[int]:
    """Places in the book where a section's title is printed (its words in a row), as locate hints."""
    words = [w for w in (fold(x) for x in re.split(r"[\s\-]+", re.sub(r"\b(part|chapter|book|section)\s+\w+\b", " ", title, flags=re.I)))
             if w and not re.fullmatch(r"[ivxlc]+|\d+", w)]
    words = [w for w in words if w not in ("the", "of", "a", "and", "an", "in")]
    if not words:
        return []
    norms = [u["norm"] for u in units]
    out = []
    for i, w in enumerate(norms):
        if w == words[0] and all(x in norms[i:i + 3 * len(words) + 3] for x in words):
            out.append(i)
    return out[:8]


def extend_ends(x: np.ndarray, words: list[dict], total: float) -> None:
    """Each word end extended until the audio goes quiet or the next word starts (as lore pipeline.py's Aligner)."""
    level = float(np.sqrt(np.mean(x ** 2))) + 1e-9
    hop = RATE // 100
    frames = len(x) // hop
    loud = (np.sqrt((x[:frames * hop].reshape(frames, hop) ** 2).mean(axis=1)) / level >= 0.2).tolist()
    for i, w in enumerate(words):
        limit = words[i + 1]["start"] if i + 1 < len(words) else total
        f = int(round(w["end"] * 100))
        while f < int(limit * 100) and f < len(loud) and (loud[f] or (f + 1 < len(loud) and loud[f + 1])):
            f += 1
        w["end"] = round(max(w["end"], min(limit, f / 100)), 3)


# ---------------------------------------------------------------- one book

def process(book: dict, em: Emitter, lex: Lexicon) -> dict:
    key = book["key"]
    began = time.time()
    out = WORK / "books" / key
    (out / "audio").mkdir(parents=True, exist_ok=True)
    units, tokens = parse((WORK / "texts" / f"{key}.txt").read_text())
    spelled = [spell(u["norm"], em.vocab) for u in units]
    names = find_names(units, lex)
    name_units = set()
    for n in names.values():
        for s, e in n["runs"]:
            name_units.update(range(s, e))
    with concurrent.futures.ThreadPoolExecutor(4) as pool:
        flacs = dict(zip([s["n"] for s in book["sections"]], pool.map(lambda s: fetch_section(key, s), book["sections"])))
    t_fetch = time.time() - began
    why: Counter = Counter()
    why_s: Counter = Counter()
    rows, stats, cursor = [], Counter(), 0
    hours_in = 0.0
    t_emit = t_align = 0.0
    for s in book["sections"]:
        if flacs.get(s["n"]) is None:
            stats["sections missing"] += 1
            continue
        x, rate = sf.read(flacs[s["n"]], dtype="float32")
        assert rate == RATE and x.ndim == 1
        hours_in += len(x) / RATE / 3600
        lp_path = out / "src" / f"{s['n']:03d}.lp.npy"
        t = time.time()
        if lp_path.exists():
            lp = np.load(lp_path).astype(np.float32)
        else:
            lp = em(x)
            np.save(lp_path, lp.astype(np.float16))
        t_emit += time.time() - t
        t = time.time()
        words, unexplained, cursor, st = align_section(lp, units, spelled, cursor, em, title_hints(s["title"], units))
        t_align += time.time() - t
        stats.update(st)
        by_unit = {w["unit"]: w for w in words}
        pieces = segment(x)
        for k, (a, b) in enumerate(pieces):
            pid = f"{key}_{s['n']:03d}_{k:04d}"
            sec = (b - a) / RATE
            fa, fb = a // HOP, b // HOP
            inside = [w for w in words if w["f0"] >= fa and w["f1"] <= fb]
            straddle = any(w["f0"] < fb and w["f1"] > fa for w in words if not (w["f0"] >= fa and w["f1"] <= fb))

            def reject(r: str) -> None:
                why[r] += 1
                why_s[r] += sec

            if not inside:
                reject("no aligned book words")
                continue
            r0, r1 = inside[0]["unit"], inside[-1]["unit"] + 1
            if straddle:
                reject("a word straddles a cut")
                continue
            if [w["unit"] for w in inside] != list(range(r0, r1)):
                reject("words not consecutive in the book")
                continue
            if (r0 - 1 in by_unit and by_unit[r0 - 1]["f1"] > fa) or (r1 in by_unit and by_unit[r1]["f0"] < fb):
                reject("a word straddles a cut")
                continue
            if r0 - 1 not in by_unit or r1 not in by_unit:
                reject("a neighbouring book word is not aligned")  # the text around the piece must be placed too
                continue
            if units[r0]["hyph"] or (r1 < len(units) and units[r1]["hyph"]):
                reject("cut falls inside a hyphenated word")
                continue
            if not 3.5 <= sec <= 15.0:
                reject("outside 3.5-15 s")
                continue
            text, spans = reference(units, tokens, r0, r1)
            if any(ch.isdigit() for ch in text):
                reject("digits in the reference")
                continue
            sc = [w["score"] for w in inside]
            nonname = [w["score"] for w in inside if w["unit"] not in name_units]
            nm = [w["score"] for w in inside if w["unit"] in name_units]
            unexp = int(unexplained[fa:fb].sum())
            if float(np.mean(sc)) < PIECE_MEAN:
                reject("low mean word score")
                continue
            if (nonname and min(nonname) < WORD_MIN) or (nm and min(nm) < NAME_MIN):
                reject("a word scores low")
                continue
            if unexp > UNEXPLAINED:
                reject("speech the reference does not hold")
                continue
            ws = [{"word": u["raw"], "span": list(sp), "start": round((w["f0"] * HOP - a) / RATE, 3),
                   "end": round((w["f1"] * HOP - a) / RATE, 3), "score": w["score"]}
                  for u, sp, w in zip(units[r0:r1], spans, inside)]
            extend_ends(x[a:b], ws, sec)
            found = []
            for n, s0, e0 in mentions(names, units, r0, r1):
                i, j = s0 - r0, e0 - r0
                w = ws[i:j]
                found.append({"name": n["spelling"], "text": text[spans[i][0]:spans[j - 1][1]], "span": [spans[i][0], spans[j - 1][1]],
                              "start": w[0]["start"], "end": w[-1]["end"], "score": round(float(np.mean([q["score"] for q in w])), 3)})
            sf.write(out / "audio" / f"{pid}.flac", x[a:b], RATE, format="FLAC", subtype="PCM_16")
            rows.append({"id": pid, "book": key, "reader": book["reader"], "chapter": s["n"], "chapter_title": s["title"],
                         "chapter_url": s["url"], "start": round(a / RATE, 3), "end": round(b / RATE, 3), "seconds": round(sec, 3),
                         "audio": f"audio/{pid}.flac", "reference": text, "align_score": round(float(np.mean(sc)), 3),
                         "min_word_score": round(min(sc), 3), "unexplained_frames": unexp, "units": [r0, r1],
                         "words": ws, "names": found})
        log(f"{key} §{s['n']}: {len(words)} words aligned, cursor {cursor}/{len(units)}, {len(rows)} pieces so far")
    with (out / "pieces.jsonl").open("w") as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    per_name = defaultdict(list)
    for r in rows:
        for m in r["names"]:
            per_name[m["name"]].append(r["id"])
    name_rows = [{"name": n["spelling"], "key": " ".join(k), "words": len(k), "spellings": dict(n["spellings"].most_common()),
                  "count_in_text": len(n["runs"]), "mentions_kept": len(per_name.get(n["spelling"], [])),
                  "pieces": len(set(per_name.get(n["spelling"], [])))}
                 for k, n in sorted(names.items(), key=lambda kv: -len(kv[1]["runs"]))]
    (out / "names.json").write_text(json.dumps(name_rows, indent=1, ensure_ascii=False))
    summary = {"key": key, "title": book["title"], "reader": book["reader"], "hours_in": round(hours_in, 3),
               "hours_kept": round(sum(r["seconds"] for r in rows) / 3600, 3), "pieces": len(rows),
               "names_in_text": len(names), "names_heard": sum(1 for n in name_rows if n["mentions_kept"]),
               "mentions": sum(len(r["names"]) for r in rows), "pieces_with_name": sum(1 for r in rows if r["names"]),
               "rejected_pieces": dict(why), "rejected_hours": {k: round(v / 3600, 3) for k, v in why_s.items()},
               "alignment": dict(stats), "book_units": len(units), "cursor_end": cursor,
               "seconds": {"fetch": round(t_fetch), "emit": round(t_emit), "align": round(t_align), "total": round(time.time() - began)},
               "aligner": ALIGNER, "params": {"CHUNK": CHUNK, "MARGIN": MARGIN, "GARBAGE": GARBAGE, "SKIP": SKIP, "SKIP_LOST": SKIP_LOST,
                                              "FWD": FWD, "FWD_LOST": FWD_LOST, "BACK_LOST": BACK_LOST, "CHUNK_OK": CHUNK_OK,
                                              "PIECE_MEAN": PIECE_MEAN, "WORD_MIN": WORD_MIN, "NAME_MIN": NAME_MIN,
                                              "UNEXPLAINED": UNEXPLAINED, "LETTER_P": LETTER_P}}
    (out / "summary.json").write_text(json.dumps(summary, indent=1, ensure_ascii=False))
    log(f"{key}: kept {summary['hours_kept']:.2f} of {hours_in:.2f} h, {len(rows)} pieces, {summary['names_heard']} names, "
        f"{summary['mentions']} mentions; {json.dumps(summary['seconds'])}")
    return summary


def main() -> None:
    books = {b["key"]: b for b in json.loads((WORK / "books.json").read_text())["books"]}
    em, lex = Emitter(), Lexicon()
    failed = 0
    for key in sys.argv[1:] or sorted(books):
        if (WORK / "books" / key / "summary.json").exists() and not os.environ.get("REDO"):
            continue
        try:
            process(books[key], em, lex)
        except Exception as e:  # noqa: BLE001 - one bad book must not stop the others
            failed += 1
            log(f"{key}: FAILED {type(e).__name__}: {e}")
            import traceback
            traceback.print_exc()
    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    main()
