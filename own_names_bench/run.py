"""Runs one system over the benchmark's passes and writes what it wrote, pass by pass.

results/runs/<label>/run.json      what ran: system config, benchmark and data version, machine, command, dates
results/runs/<label>/passes.jsonl  one line per pass: id, text, names sent, how they were fitted, seconds

A run resumes: passes already written without an error are not sent again.
"""

import gzip
import hashlib
import json
import os
import platform
import shlex
import subprocess
import sys
import threading
import time
from concurrent.futures import ThreadPoolExecutor
from datetime import UTC, datetime
from pathlib import Path

from . import BENCH_NAME, BENCH_VERSION
from .data import DATASET_REPO, DATASET_REVISION, Bench, dataset_fingerprint, manifest_sha256
from .passes import Pass, all_passes
from .systems.base import System


def _cmd(args: list[str]) -> str:
    try:
        return subprocess.run(args, capture_output=True, text=True, timeout=20, check=False).stdout.strip()
    except (OSError, subprocess.SubprocessError):
        return ""


def machine() -> dict:
    info = {"platform": platform.platform(), "machine": platform.machine(), "python": sys.version.split()[0],
            "cpu": platform.processor()}
    if sys.platform == "darwin":
        info["cpu"] = _cmd(["sysctl", "-n", "machdep.cpu.brand_string"])
        info["memory_gb"] = round(int(_cmd(["sysctl", "-n", "hw.memsize"]) or 0) / 2**30, 1)
        info["os"] = f"macOS {_cmd(['sw_vers', '-productVersion'])} ({_cmd(['sw_vers', '-buildVersion'])})"
    else:
        try:
            with open("/proc/meminfo") as f:
                info["memory_gb"] = round(int(f.readline().split()[1]) / 2**20, 1)
            with open("/proc/cpuinfo") as f:
                info["cpu"] = next((ln.split(":", 1)[1].strip() for ln in f if ln.startswith("model name")), info["cpu"])
        except OSError:
            pass
        info["os"] = _cmd(["sh", "-c", ". /etc/os-release && echo $PRETTY_NAME"]) or platform.platform()
    gpu = _cmd(["nvidia-smi", "--query-gpu=name,driver_version,memory.total", "--format=csv,noheader"])
    if gpu:
        info["gpu"] = gpu
    return info


def code_revision() -> str:
    if os.environ.get("BENCH_CODE_REVISION"):  # a machine that got the code without its git history
        return os.environ["BENCH_CODE_REVISION"]
    here = Path(__file__).resolve().parent.parent
    rev = _cmd(["git", "-C", str(here), "rev-parse", "HEAD"])
    dirty = _cmd(["git", "-C", str(here), "status", "--porcelain", "--untracked-files=no"])
    return (rev + ("-dirty" if dirty else "")) if rev else "unknown"


VOLATILE_CONFIG = {"engine"}  # filled in once a system has loaded; not part of what fixes its behaviour


def config_fingerprint(system_name: str, config: dict, dataset_fp: str) -> str:
    stable = {k: v for k, v in config.items() if k not in VOLATILE_CONFIG}
    blob = json.dumps({"system": system_name, "config": stable, "dataset": dataset_fp}, sort_keys=True, ensure_ascii=False)
    return hashlib.sha256(blob.encode()).hexdigest()[:16]


def run(b: Bench, system: System, out: Path, *, chapters: bool, limit: int, only: str, hourly_usd: float | None,
        accept_config_change: str = "") -> Path:
    out.mkdir(parents=True, exist_ok=True)
    passes = [p for p in all_passes(b, system.variants, chapters) if not only or p.id.startswith(only)]
    if limit:
        passes = passes[:limit]
    meta_path = out / "run.json"
    meta = json.loads(meta_path.read_text()) if meta_path.exists() else {}
    dataset_fp = dataset_fingerprint(b)
    config = system.config()
    fp = config_fingerprint(system.name, config, dataset_fp)
    if meta:
        # a folder holds one system, one configuration, one dataset: never mix runs
        if meta.get("system") != system.name or meta.get("dataset_fingerprint") != dataset_fp:
            raise SystemExit(f"{out} holds a run of {meta.get('system')} on dataset {meta.get('dataset_fingerprint')}; "
                             f"this is {system.name} on {dataset_fp}. Use another --label.")
        if meta.get("fingerprint") != fp:
            old = meta.get("config", {})
            changed = sorted(k for k in set(old) | set(config) if k not in VOLATILE_CONFIG and old.get(k) != config.get(k))
            if not accept_config_change:
                raise SystemExit(f"{out} was made with another configuration of {system.name} (changed: {', '.join(changed)}). "
                                 "Use another --label, or --accept-config-change REASON if the change cannot alter a transcript.")
            meta.setdefault("config_changes", []).append({"from": meta.get("fingerprint"), "to": fp, "changed": changed,
                                                          "previous": {k: old.get(k) for k in changed}, "reason": accept_config_change,
                                                          "at": datetime.now(UTC).isoformat(timespec="seconds")})
    log = out / "passes.jsonl"
    packed = out / "passes.jsonl.gz"
    if packed.exists() and not log.exists():  # a published run being resumed
        log.write_bytes(gzip.decompress(packed.read_bytes()))
        packed.unlink()
    want = {p.id: p.list_sha for p in passes}
    done: dict[str, dict] = {}
    if log.exists():
        for line in log.read_text().splitlines():
            r = json.loads(line)
            if not r.get("error") and r.get("list_sha") == want.get(r["id"]):
                done[r["id"]] = r
    todo = [p for p in passes if p.id not in done]
    meta.update({
        "benchmark": BENCH_NAME, "benchmark_version": BENCH_VERSION, "dataset": f"{DATASET_REPO}@{DATASET_REVISION}",
        "dataset_fingerprint": dataset_fp, "manifest_sha256": manifest_sha256(b.root), "code_revision": code_revision(),
        "system": system.name, "variants": list(system.variants), "kind": system.kind, "config": config, "fingerprint": fp,
        "price": system.price(), "machine": machine(), "hourly_usd": hourly_usd,
    })
    meta.setdefault("commands", []).append({"argv": " ".join(shlex.quote(a) for a in sys.argv),
                                           "started": datetime.now(UTC).isoformat(timespec="seconds")})
    meta_path.write_text(json.dumps(meta, indent=1) + "\n")
    print(f"{system.name}: {len(passes)} passes, {len(done)} already done, {len(todo)} to go", flush=True)
    if not todo:
        return out
    if os.environ.get("BENCH_TRACEBACK_EVERY"):  # diagnosing a stall: dump every thread's stack now and then
        import faulthandler

        faulthandler.dump_traceback_later(float(os.environ["BENCH_TRACEBACK_EVERY"]), repeat=True)
    system.start()
    meta["config"] = {**config, **{k: v for k, v in system.config().items() if k in VOLATILE_CONFIG}}
    meta_path.write_text(json.dumps(meta, indent=1) + "\n")
    lock = threading.Lock()
    started = time.time()
    count = [0, 0]

    def one(p: Pass) -> None:
        names = b.written(list(p.entries))
        fit = system.fit(names)
        row = {"id": p.id, "list_sha": p.list_sha, "audio_s": p.seconds, "listed": len(names), "sent": fit.sent, "fit": fit.how}
        t0 = time.perf_counter()
        try:
            swap = dict(p.samples)  # cross-reader passes: the name taught by another reader's recording
            ents = []
            for e in p.entries:
                src = b.entries[swap.get(e, e)]
                ents.append({**b.entries[e], "id": src["id"], "sample": src["sample"], "sample_path": b.path(src["sample"])})
            o = system.transcribe(b.path(p.audio), fit.sent, ents)
            row["latency_s"] = round(o.latency_s if o.latency_s is not None else time.perf_counter() - t0, 4)
            row["text"] = o.text
            if o.sent is not None:
                row["sent"], row["fit"] = o.sent, o.how
            if o.extra:
                row["extra"] = o.extra
        except Exception as e:  # recorded and retried on the next run; never stops the others
            row["error"] = f"{type(e).__name__}: {str(e)[:300]}"
        with lock, log.open("a") as f:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")
            count[0] += 1
            count[1] += "error" in row
            if count[0] % 50 == 0 or count[0] == len(todo):
                rate = count[0] / (time.time() - started)
                print(f"  {count[0]}/{len(todo)} ({count[1]} errors), {rate:.2f} passes/s", flush=True)

    try:
        if system.workers > 1:
            with ThreadPoolExecutor(system.workers) as pool:
                list(pool.map(one, todo))
        else:
            for p in todo:
                one(p)
    finally:
        system.stop()
    meta = json.loads(meta_path.read_text())
    meta["commands"][-1]["finished"] = datetime.now(UTC).isoformat(timespec="seconds")
    meta_path.write_text(json.dumps(meta, indent=1) + "\n")
    if os.environ.get("BENCH_STRICT") and count[1]:
        raise SystemExit(f"{count[1]} passes failed")
    return out


def passes_file(run_dir: Path) -> Path:
    """passes.jsonl while a run is going; published runs are gzipped (passes.jsonl.gz)."""
    plain = run_dir / "passes.jsonl"
    return plain if plain.exists() else run_dir / "passes.jsonl.gz"


def load_rows(run_dir: Path) -> tuple[dict, dict[str, dict], dict[str, dict]]:
    """run.json, the last good row of each pass, and the passes whose last attempt failed."""
    meta = json.loads((run_dir / "run.json").read_text())
    rows: dict[str, dict] = {}
    failed: dict[str, dict] = {}
    f = passes_file(run_dir)
    text = gzip.decompress(f.read_bytes()).decode() if f.suffix == ".gz" else f.read_text()
    for line in text.splitlines():
        r = json.loads(line)
        if r.get("error"):
            if r["id"] not in rows:
                failed[r["id"]] = r
        else:
            rows[r["id"]] = r
            failed.pop(r["id"], None)
    return meta, rows, failed


def load_texts(run_dir: Path) -> tuple[dict, dict[str, dict]]:
    meta, rows, _ = load_rows(run_dir)
    return meta, rows
