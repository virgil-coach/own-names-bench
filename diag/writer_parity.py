"""Writer parity for a release: the same writer calls through the torch reference (ours_ref.Writer: Qwen3-ASR-1.7B in
float32 + the LoRA adapter through peft, unmerged) and through the shipped writer (the engine's writer_replay: the adapter
merged in float32, text decoder MLX affine 8-bit, audio encoder bf16). The calls are lore-poc's bigspot pool/test --sub 200
export (LibriVox audiobook pieces and YODAS clips with their taught recordings; the set detailkeeper docs/results
parity.json used for v0.3.0), not own-names-bench data. Each call: the piece, its shortlist (written, heard as) and
taught recordings, trimmed as the engine trims them; level-matching is the writer's own on both sides.

  prep  EXPORT_DIR OUT_DIR [--n N]   jobs -> OUT/calls.json + OUT/audio/*.f32 (little-endian float32, 16 kHz)
  torch OUT_DIR ADAPTER_DIR [--device mps]   -> OUT/torch.json  (texts, one per call)
  score OUT_DIR MLX_JSON TORCH_JSON          -> aggregates: same text, names right by group, name-free listed name written

usage: uv run --extra qwen python diag/writer_parity.py prep ~/export /tmp/par --n 400
"""

import argparse
import json
import random
import re
import sys
import time
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np
import soundfile as sf



def trim(x: np.ndarray, floor: float = 0.01, pad: int = 800) -> np.ndarray:
    """audio.rs trim (the engine's trim of a taught recording), as lore-poc ft.trim."""
    loud = np.flatnonzero(np.abs(x) > floor * max(1e-6, float(np.abs(x).max())) * 5)
    if loud.size == 0:
        return x
    return x[max(0, loud[0] - pad) : loud[-1] + pad]


def read(path: Path) -> np.ndarray:
    x, rate = sf.read(path, dtype="float32")
    assert rate == 16000, (path, rate)
    return x if x.ndim == 1 else x.mean(axis=1)


def prep(export: Path, out: Path, n: int) -> None:
    jobs = json.loads((export / "jobs.json").read_text())["jobs"]
    by: dict[tuple, list] = defaultdict(list)
    for j in jobs:
        by[(j["set"], j["group"])].append(j)
    rng = random.Random(17)
    share = n / len(jobs)
    pick = [j for k in sorted(by) for j in rng.sample(by[k], max(1, round(share * len(by[k]))))]
    (out / "audio").mkdir(parents=True, exist_ok=True)
    calls, meta = [], []
    for j in pick:
        entries = json.loads(j["entries"].replace("'", '"')) if isinstance(j["entries"], str) else j["entries"]
        files = []
        for k, src in enumerate([j["audio"]] + [e[2] for e in entries]):
            x = read(export / src)
            if k:
                x = trim(x)
            f = f"{j['id']}_{k}.f32"
            x.astype("<f4").tofile(out / "audio" / f)
            files.append(f)
        calls.append({"kind": "list" if entries else "plain", "audio": files[0], "clips": files[1:],
                      "entries": [[e[0], e[1]] for e in entries]})
        meta.append({"id": j["id"], "set": j["set"], "group": j["group"], "cond": j["cond"], "want": j["want"],
                     "reference": j["reference"], "listed": [e[0] for e in entries]})
    (out / "calls.json").write_text(json.dumps(calls))
    (out / "meta.json").write_text(json.dumps(meta))
    print(f"{len(calls)} calls from {len(jobs)} jobs: {Counter((m['set'], m['group']) for m in meta)}")


def torch_run(out: Path, adapter: Path, device: str) -> None:
    from own_names_bench.ours_ref.writer import Writer, level_matched

    calls = json.loads((out / "calls.json").read_text())
    w = Writer(device, (str(adapter), None, None))
    w.load()
    texts, t0 = [], time.time()
    for i, c in enumerate(calls):
        wav = np.fromfile(out / "audio" / c["audio"], dtype="<f4")
        if c["kind"] == "plain":
            texts.append(w.plain(wav))
        else:
            clips = [level_matched(np.fromfile(out / "audio" / f, dtype="<f4"), wav) for f in c["clips"]]
            texts.append(w.write(wav, [(e[0], e[1], clip) for e, clip in zip(c["entries"], clips)]))
        if i % 50 == 0:
            print(f"{i}/{len(calls)} {time.time() - t0:.0f}s", flush=True)
    (out / "torch.json").write_text(json.dumps([{"text": t} for t in texts]))
    print(f"{len(calls)} calls in {time.time() - t0:.0f}s")


def norm(t: str) -> str:
    return " ".join(re.sub(r"[^\w' ]+", " ", t.lower().replace("’", "'")).split())


def has(text: str, name: str) -> bool:
    return re.search(r"(?<!\w)" + re.escape(norm(name)) + r"(?!\w)", norm(text)) is not None


def score(out: Path, mlx: Path, ref: Path) -> None:
    meta = json.loads((out / "meta.json").read_text())
    a = [r["text"] for r in json.loads(mlx.read_text())]
    b = [r["text"] for r in json.loads(ref.read_text())]
    assert len(a) == len(b) == len(meta)
    same = sum(norm(x) == norm(y) for x, y in zip(a, b))
    print(f"same text (normalized): {same}/{len(meta)} = {same / len(meta):.1%}")
    groups: dict[str, list[int]] = defaultdict(list)
    for i, m in enumerate(meta):
        groups[f"{m['set']}, {m['group']}, {m['cond']}"].append(i)
    print("| group | calls | names right MLX 8-bit | names right torch | right on one side only (MLX / torch) | a listed name not in the reference written (MLX / torch) |")
    print("| --- | --- | --- | --- | --- | --- |")
    for g, ids in sorted(groups.items()):
        def right(t: list[str]) -> list[bool]:
            return [bool(meta[i]["want"]) and meta[i]["want"] in meta[i]["listed"] and has(t[i], meta[i]["want"]) for i in ids]

        def wrong(t: list[str]) -> int:
            return sum(any(has(t[i], n) and not has(meta[i]["reference"], n) for n in meta[i]["listed"]) for i in ids)

        ra, rb = right(a), right(b)
        only = (sum(x and not y for x, y in zip(ra, rb)), sum(y and not x for x, y in zip(ra, rb)))
        print(f"| {g} | {len(ids)} | {sum(ra)} | {sum(rb)} | {only[0]} / {only[1]} | {wrong(a)} / {wrong(b)} |")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=["prep", "torch", "score"])
    ap.add_argument("args", nargs="+")
    ap.add_argument("--n", type=int, default=400)
    ap.add_argument("--device", default="mps")
    x = ap.parse_args()
    if x.cmd == "prep":
        prep(Path(x.args[0]), Path(x.args[1]), x.n)
    elif x.cmd == "torch":
        torch_run(Path(x.args[0]), Path(x.args[1]), x.device)
    else:
        score(Path(x.args[0]), Path(x.args[1]), Path(x.args[2]))


if __name__ == "__main__":
    sys.exit(main())
