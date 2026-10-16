"""Detail Keeper's name spotter in PyTorch: for a window of speech, ranks the taught names by
whether they were said. This is the engine's original Python spotter (detailkeeper@5f7ebf6^,
services/engine/detailkeeper/spotter.py), which the Rust engine's spotter was ported from and
checked against; only the on-disk caches are gone.

Every entry is scored three ways and the standardized scores are summed:
  phon   phoneme-CTC alignment of the entry's pronunciations (espeak-ng g2p of the spelling, and
         the taught recording's soft phoneme distributions) against the window's phoneme
         posteriors (wav2vec2 espeak phoneme recognizer)
  emb    subsequence DTW between WavLM-base-plus layer-12 frames of the taught recording and the window
  text   letter similarity between 1-4 word runs of the recognizer's text of the window and the
         spelling / how the recognizer heard the taught recording
"""

import hashlib
import json
import re
import time
from collections import OrderedDict
from pathlib import Path
import shutil
import subprocess
import unicodedata
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass

import numba
import numpy as np
import torch
from rapidfuzz.distance import Levenshtein
from rapidfuzz.process import cdist

PHON = ("facebook/wav2vec2-lv-60-espeak-cv-ft", "0c380a877907192512147c466ead03055f200cad")
WAVLM = ("microsoft/wavlm-base-plus", "98fd61b9c652129c839c0a25a05987d8f59256a4")
WAVLM_LAYER = 12
BLANK, V = 0, 392
FLOOR, SKIP, BONUS = -8.0, -6.0, 3.0
STEP = 0.02
THREADS = 4
# espeak-ng 1.52.0 pronunciations of every benchmark name (build/g2p_table.py), so every machine
# uses the same ones; espeak-ng is only asked for a name that is not in it
G2P_TABLE = Path(__file__).with_name("g2p.json")


@numba.njit(cache=True)
def spot(em, blank, skip):
    L, T = em.shape
    NEG = -1e9
    prev = np.full(2 * L, NEG)
    prev_from = np.zeros(2 * L, dtype=np.int64)
    best, best_from, best_to = NEG, 0, 0
    for t in range(T):
        cur = np.full(2 * L, NEG)
        cur_from = np.zeros(2 * L, dtype=np.int64)
        for j in range(L):
            if j == 0:
                enter, origin = 0.0, t
            elif prev[2 * j - 2] >= prev[2 * j - 1]:
                enter, origin = prev[2 * j - 2], prev_from[2 * j - 2]
            else:
                enter, origin = prev[2 * j - 1], prev_from[2 * j - 1]
            if enter >= prev[2 * j]:
                cur[2 * j], cur_from[2 * j] = enter + em[j, t], origin
            else:
                cur[2 * j], cur_from[2 * j] = prev[2 * j] + em[j, t], prev_from[2 * j]
            if prev[2 * j] >= prev[2 * j + 1]:
                cur[2 * j + 1], cur_from[2 * j + 1] = prev[2 * j] + blank[t], prev_from[2 * j]
            else:
                cur[2 * j + 1], cur_from[2 * j + 1] = prev[2 * j + 1] + blank[t], prev_from[2 * j + 1]
        for j in range(1, L):
            if cur[2 * j - 2] >= cur[2 * j - 1]:
                a, origin = cur[2 * j - 2] + skip, cur_from[2 * j - 2]
            else:
                a, origin = cur[2 * j - 1] + skip, cur_from[2 * j - 1]
            if a > cur[2 * j]:
                cur[2 * j], cur_from[2 * j] = a, origin
        if cur[2 * L - 2] > best:
            best, best_from, best_to = cur[2 * L - 2], cur_from[2 * L - 2], t
        prev, prev_from = cur, cur_from
    return best, best_from, best_to


@numba.njit(parallel=True, cache=True)
def spot_all(em, blank, starts, lens, skip, bonus):
    out = np.full(starts.shape[0], -1e9)
    spans = np.zeros((starts.shape[0], 2), dtype=np.int64)
    for i in numba.prange(starts.shape[0]):
        L = lens[i]
        if L > 0:
            score, first, last = spot(em[starts[i] : starts[i] + L], blank, skip)
            out[i] = score + bonus * L
            spans[i, 0], spans[i, 1] = first, last
    return out, spans


@numba.njit(parallel=True, fastmath=True, cache=True)
def subseq_dtw(cost, starts, lens):
    n_terms = starts.shape[0]
    m = cost.shape[1]
    out = np.empty(n_terms, dtype=np.float32)
    for t in numba.prange(n_terms):
        c = cost[starts[t] : starts[t] + lens[t]]
        n = c.shape[0]
        prev = c[0].copy()
        prev_len = np.ones(m, dtype=np.float32)
        cur = np.empty(m, dtype=np.float32)
        cur_len = np.empty(m, dtype=np.float32)
        for i in range(1, n):
            cur[0] = prev[0] + c[i, 0]
            cur_len[0] = prev_len[0] + 1
            for j in range(1, m):
                best, length = prev[j - 1], prev_len[j - 1]
                if prev[j] / prev_len[j] < best / length:
                    best, length = prev[j], prev_len[j]
                if cur[j - 1] / cur_len[j - 1] < best / length:
                    best, length = cur[j - 1], cur_len[j - 1]
                cur[j] = best + c[i, j]
                cur_len[j] = length + 1
            prev, cur = cur, prev
            prev_len, cur_len = cur_len, prev_len
        best = np.inf
        for j in range(m):
            v = prev[j] / prev_len[j]
            if v < best:
                best = v
        out[t] = best
    return out


def standardize(x: np.ndarray) -> np.ndarray:
    x = np.where(x < -1e8, np.nan, x.astype(np.float64))
    if np.isnan(x).all():
        return np.zeros(len(x))
    x = np.where(np.isnan(x), np.nanpercentile(x, 1), x)
    med = np.median(x)
    return (x - med) / (np.percentile(x, 90) - med + 1e-6)


def soft(logp: np.ndarray) -> np.ndarray:
    p = np.exp(logp)
    win = p.argmax(axis=1)
    rows, group, prev = [], [], -1
    for t, tok in enumerate(win):
        if tok != prev and group:
            rows.append(np.mean(group, axis=0))
            group = []
        if tok != BLANK:
            group.append(p[t])
        prev = tok
    if group:
        rows.append(np.mean(group, axis=0))
    if not rows:
        return np.zeros((0, V), dtype=np.float32)
    out = np.stack(rows)
    out[:, BLANK] = 0
    return (out / out.sum(axis=1, keepdims=True)).astype(np.float32)


def text_windows(text: str, max_words: int = 4) -> list[str]:
    words = re.findall(r"[A-Za-z']+", text)
    return [" ".join(words[i : i + n]) for n in range(1, max_words + 1) for i in range(len(words) - n + 1)]


def letters(s: str) -> str:
    s = unicodedata.normalize("NFKD", s.replace("æ", "ae").replace("Æ", "Ae"))
    return "".join(c for c in s.lower() if "a" <= c <= "z")


def trim(x: np.ndarray, floor: float = 0.01, pad: int = 800) -> np.ndarray:
    loud = np.flatnonzero(np.abs(x) > floor * max(1e-6, float(np.abs(x).max())) * 5)
    if loud.size == 0:
        return x
    return x[max(0, loud[0] - pad) : loud[-1] + pad]


def offsets(lens: list[int]) -> tuple[np.ndarray, np.ndarray]:
    arr = np.array(lens, dtype=np.int64)
    return np.concatenate([[0], np.cumsum(arr)[:-1]]).astype(np.int64), arr


@dataclass(frozen=True)
class Term:
    key: str          # stable id of the entry and its one taught recording
    written: str
    heard_as: str


@dataclass
class Hit:
    term: Term
    score: float
    # minus the best WavLM DTW cost of the entry's taught recording in this window (engine Hit::emb); None with none
    emb: float | None = None


@dataclass
class Bank:
    matrix: torch.Tensor
    pstart: np.ndarray
    plen: np.ndarray
    powner: np.ndarray
    frames: torch.Tensor
    sstart: np.ndarray
    slen: np.ndarray
    sowner: np.ndarray
    forms: list[str]
    fowner: np.ndarray


class Spotter:
    def __init__(self, device: str) -> None:
        self.device = device
        self.feats: dict[str, tuple[np.ndarray, np.ndarray]] = {}
        self.g2p: dict[str, list[int]] = json.loads(G2P_TABLE.read_text(encoding="utf-8")) if G2P_TABLE.exists() else {}
        self.bank_for: tuple[Term, ...] = ()
        self.bank: Bank | None = None
        # a window's phoneme posteriors and WavLM frames, reused across lists (see ours_torch)
        self.window_cache: OrderedDict[str, tuple[torch.Tensor, torch.Tensor, float]] = OrderedDict()
        self.reused_s = 0.0

    def load(self) -> None:
        from huggingface_hub import snapshot_download
        from transformers import AutoModel, Wav2Vec2ForCTC

        numba.set_num_threads(min(THREADS, numba.config.NUMBA_NUM_THREADS))
        phon = snapshot_download(PHON[0], revision=PHON[1], allow_patterns=["config.json", "vocab.json", "model.safetensors"])
        self.phon = Wav2Vec2ForCTC.from_pretrained(phon).to(self.device).eval()
        with open(f"{phon}/vocab.json") as f:
            self.vocab: dict[str, int] = json.load(f)
        wavlm = snapshot_download(WAVLM[0], revision=WAVLM[1], allow_patterns=["config.json", "model.safetensors"])
        self.wavlm = AutoModel.from_pretrained(wavlm).to(self.device).eval()

    @torch.inference_mode()
    def logp(self, wav: np.ndarray) -> torch.Tensor:
        if len(wav) < 1600:
            wav = np.pad(wav, (0, 1600 - len(wav)))
        x = (wav - wav.mean()) / (wav.std() + 1e-7)
        return torch.log_softmax(self.phon(torch.from_numpy(x.astype(np.float32))[None].to(self.device)).logits[0].float(), -1)

    @torch.inference_mode()
    def wavlm_frames(self, wav: np.ndarray) -> torch.Tensor:
        x = torch.from_numpy(wav.astype(np.float32))
        if len(x) < 800:
            x = torch.nn.functional.pad(x, (0, 800 - len(x)))
        return self.wavlm(x[None].to(self.device), output_hidden_states=True).hidden_states[WAVLM_LAYER][0].float()

    def learn(self, key: str, wav: np.ndarray) -> None:
        pad = (np.random.default_rng(0).standard_normal(8000) * 1e-4).astype(np.float32)
        lp = self.logp(np.concatenate([pad, wav, pad])).cpu().numpy().astype(np.float16).astype(np.float32)
        self.feats[key] = (soft(lp), self.wavlm_frames(trim(wav)).cpu().numpy().astype(np.float16))

    def pronounce(self, spellings: list[str]) -> None:
        need = sorted(set(spellings) - set(self.g2p))
        if not need:
            return
        if shutil.which("espeak-ng") is None:
            raise RuntimeError(f"espeak-ng is not installed, and {len(need)} names are not in {G2P_TABLE.name}")

        def one(text: str) -> list[int]:
            ipa = subprocess.run(["espeak-ng", "-q", "--ipa", "-v", "en-us", "--", text], capture_output=True, text=True).stdout
            ipa = "".join(ch for ch in ipa if ch not in "ˈˌ \n_-")
            out, i = [], 0
            while i < len(ipa):
                for size in (3, 2, 1):
                    piece = ipa[i : i + size]
                    if piece in self.vocab and len(piece) == size:
                        out.append(self.vocab[piece])
                        i += size
                        break
                else:
                    i += 1
            return out

        with ThreadPoolExecutor(8) as pool:
            self.g2p.update(zip(need, pool.map(one, need), strict=True))

    def build(self, terms: tuple[Term, ...]) -> Bank:
        self.pronounce([t.written for t in terms])
        prons, powner, seqs, sowner, forms, fowner = [], [], [], [], [], []
        for e, term in enumerate(terms):
            ids = self.g2p[term.written]
            if ids:
                one_hot = np.zeros((len(ids), V), dtype=np.float32)
                one_hot[np.arange(len(ids)), ids] = 1.0
                prons.append(one_hot)
                powner.append(e)
            if letters(term.written):
                forms.append(letters(term.written))
                fowner.append(e)
            soft_pron, frames = self.feats[term.key]
            if len(soft_pron):
                prons.append(soft_pron)
                powner.append(e)
            if len(frames):
                seqs.append(frames.astype(np.float32))
                sowner.append(e)
            if letters(term.heard_as):
                forms.append(letters(term.heard_as))
                fowner.append(e)
        pstart, plen = offsets([len(p) for p in prons])
        sstart, slen = offsets([len(s) for s in seqs])
        matrix = torch.from_numpy(np.concatenate(prons) if prons else np.zeros((0, V), dtype=np.float32)).to(self.device)
        flat = torch.from_numpy(np.concatenate(seqs) if seqs else np.zeros((0, 768), dtype=np.float32)).to(self.device)
        return Bank(matrix, pstart, plen, np.array(powner, dtype=np.int64), flat / flat.norm(dim=-1, keepdim=True).clamp_min(1e-8),
                    sstart, slen, np.array(sowner, dtype=np.int64), forms, np.array(fowner, dtype=np.int64))

    def align(self, logp: torch.Tensor, matrix: torch.Tensor, pstart: np.ndarray, plen: np.ndarray):
        top = logp.max(dim=1).values
        em = torch.log(matrix @ torch.exp(logp).T + 1e-9)
        em = torch.clamp_min(em - top[None, :], FLOOR).cpu().numpy()
        blank = torch.clamp_min(logp[:, BLANK] - top, FLOOR).cpu().numpy().astype(np.float64)
        return spot_all(np.ascontiguousarray(em), blank, pstart, plen, SKIP, BONUS)

    @torch.inference_mode()
    def rank(self, terms: list[Term], wav: np.ndarray, text: str, k: int) -> list[Hit]:
        terms_t = tuple(terms)
        if not terms_t:
            return []
        if self.bank is None or self.bank_for != terms_t:
            self.bank, self.bank_for = self.build(terms_t), terms_t
        b, n = self.bank, len(terms_t)
        key = hashlib.sha1(wav.tobytes()).hexdigest()
        got = self.window_cache.get(key)
        if got is None:
            t = time.perf_counter()
            got = (self.logp(wav), self.wavlm_frames(wav), 0.0)
            if self.device == "cuda":
                torch.cuda.synchronize()
            got = (got[0], got[1], time.perf_counter() - t)
            self.window_cache[key] = got
            if len(self.window_cache) > 512:
                self.window_cache.popitem(last=False)
            self.reused_s = 0.0
        else:
            self.reused_s = got[2]
        window_logp, window_frames = got[0], got[1]
        phon = np.full(n, -1e9)
        if len(b.powner):
            scores, _ = self.align(window_logp, b.matrix, b.pstart, b.plen)
            np.maximum.at(phon, b.powner, scores)
        emb = np.full(n, -1e9)
        if len(b.sowner):
            fr = window_frames
            cu = fr / fr.norm(dim=-1, keepdim=True).clamp_min(1e-8)
            cost = (1.0 - b.frames @ cu.T).cpu().numpy()
            np.maximum.at(emb, b.sowner, -subseq_dtw(np.ascontiguousarray(cost, dtype=np.float32), b.sstart, b.slen).astype(np.float64))
        sim = np.zeros(n)
        qs = [q for q in (letters(w) for w in text_windows(text)) if q]
        if qs and b.forms:
            np.maximum.at(sim, b.fowner, cdist(qs, b.forms, scorer=Levenshtein.normalized_similarity, workers=THREADS).max(axis=0))
        fused = standardize(phon) + standardize(emb) + standardize(sim)
        return [Hit(terms_t[i], float(fused[i]), float(emb[i]) if emb[i] > -1e8 else None) for i in np.argsort(-fused, kind="stable")[:k]]
