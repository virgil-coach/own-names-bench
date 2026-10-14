#!/usr/bin/env python3
"""Word times for the names that enrollment recordings are cut from (v1.2 build, `align` stage).

CTC forced alignment of the reference text against facebook/wav2vec2-base-960h (Apache 2.0, pinned)
character posteriors, by plain Viterbi over the blank-interleaved character sequence. Only the
target span's time is kept. Runs on a GPU machine; reads align_jobs.json from build_v12.py plan.

usage: python build/align.py JOBS.json OUT.json
"""

import io
import json
import re
import sys
from pathlib import Path

import numpy as np
import soundfile as sf
import torch
from huggingface_hub import hf_hub_download, snapshot_download
from transformers import Wav2Vec2ForCTC, Wav2Vec2Processor

MODEL = ("facebook/wav2vec2-base-960h", "22aad52d435eb6dbaf354bdad9b0da84ce7d6156")
APPTEK = ("apptek-com/apptek_callcenter_dialogues", "b98967d9946f7f59f58d08624a2a00fe98fe0219")
MODULATE = ("modulate/entity-transcription-benchmark", "45b2f1411ff15a6598b68db1ec8423b9965153e5")
FRAME_S = 0.02


def viterbi(logp: np.ndarray, tokens: list[int], blank: int) -> list[tuple[int, int]]:
    """Frames [first, last] of each token, best path through blank-interleaved tokens."""
    seq = [blank]
    for t in tokens:
        seq += [t, blank]
    S, T = len(seq), logp.shape[0]
    neg = -1e18
    dp = np.full((T, S), neg)
    bp = np.zeros((T, S), dtype=np.int64)
    dp[0, 0] = logp[0, seq[0]]
    if S > 1:
        dp[0, 1] = logp[0, seq[1]]
    for t in range(1, T):
        for s in range(S):
            best, arg = dp[t - 1, s], s
            if s >= 1 and dp[t - 1, s - 1] > best:
                best, arg = dp[t - 1, s - 1], s - 1
            if s >= 2 and seq[s] != blank and seq[s] != seq[s - 2] and dp[t - 1, s - 2] > best:
                best, arg = dp[t - 1, s - 2], s - 2
            dp[t, s] = best + logp[t, seq[s]]
            bp[t, s] = arg
    s = S - 1 if S == 1 or dp[T - 1, S - 1] >= dp[T - 1, S - 2] else S - 2
    path = [0] * T
    for t in range(T - 1, -1, -1):
        path[t] = s
        s = bp[t, s]
    spans: list[tuple[int, int]] = [(-1, -1)] * len(tokens)
    for t, s in enumerate(path):
        if s % 2 == 1:
            k = s // 2
            a, b = spans[k]
            spans[k] = (t if a < 0 else a, t)
    return spans


def main() -> None:
    jobs = json.loads(Path(sys.argv[1]).read_text())
    device = "cuda" if torch.cuda.is_available() else "cpu"
    path = snapshot_download(MODEL[0], revision=MODEL[1], allow_patterns=["*.json", "model.safetensors", "*.txt"])
    proc = Wav2Vec2Processor.from_pretrained(path)
    model = Wav2Vec2ForCTC.from_pretrained(path).to(device).eval()
    vocab = proc.tokenizer.get_vocab()
    blank = vocab["<pad>"]
    modulate_audio: dict[str, bytes] = {}
    if any(j["source"] == "modulate" for j in jobs):
        import pyarrow.parquet as pq

        for i in range(3):
            p = hf_hub_download(MODULATE[0], f"data/test-0000{i}-of-00003.parquet", repo_type="dataset", revision=MODULATE[1])
            t = pq.read_table(p, columns=["id", "audio"])
            for r in t.to_pylist():
                modulate_audio[r["id"]] = r["audio"]["bytes"]
    out = {}
    for n, j in enumerate(jobs):
        if j["source"] == "calls":
            f = hf_hub_download(APPTEK[0], f"diarization/{j['accent']}/{j['file']}", repo_type="dataset", revision=APPTEK[1])
            info = sf.info(f)
            x, _ = sf.read(f, start=int(j["start"] * info.samplerate), stop=int(j["end"] * info.samplerate), dtype="float32")
            offset = j["start"]
        else:
            x, _ = sf.read(io.BytesIO(modulate_audio[j["clip"]]), dtype="float32")
            offset = 0.0
        if x.ndim > 1:
            x = x.mean(axis=1)
        text = j["text"]
        # characters the model knows; keep a map from each kept character to its place in the text
        chars, where = [], []
        for i, ch in enumerate(text.upper()):
            if ch in vocab and ch not in ("<pad>", "<s>", "</s>", "<unk>"):
                chars.append(ch)
                where.append(i)
            elif ch.isspace() and chars and chars[-1] != "|":
                chars.append("|")
                where.append(i)
        tokens = [vocab[c] for c in chars]
        with torch.inference_mode():
            inp = proc(x, sampling_rate=16000, return_tensors="pt").input_values.to(device)
            logp = torch.log_softmax(model(inp).logits[0].float(), -1).cpu().numpy()
        spans = viterbi(logp, tokens, blank)
        a, b = j["span"]
        inside = [k for k, w in enumerate(where) if a <= w < b and chars[k] != "|" and spans[k][0] >= 0]
        if not inside:
            out[j["job"]] = None
            continue
        t0 = spans[inside[0]][0] * FRAME_S
        t1 = (spans[inside[-1]][1] + 1) * FRAME_S
        out[j["job"]] = {"start": round(offset + t0, 3), "end": round(offset + t1, 3), "frames": len(logp)}
        if n % 50 == 0:
            print(f"{n}/{len(jobs)}", flush=True)
    Path(sys.argv[2]).parent.mkdir(parents=True, exist_ok=True)
    Path(sys.argv[2]).write_text(json.dumps({"model": f"{MODEL[0]}@{MODEL[1]}", "spans": out}, ensure_ascii=False))
    print(f"ALIGNED {sum(v is not None for v in out.values())}/{len(jobs)}", flush=True)


if __name__ == "__main__":
    main()
