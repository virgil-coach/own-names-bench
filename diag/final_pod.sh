#!/bin/bash
# The v0.6 finalist benchmark run (lore-poc ctxft/v06_amendment4_c3.md) on a rented GPU on the EUR-IS-1 global volume.
# usage: diag/final_pod.sh <$/h> <spec>...      spec = <system>:<label>:<podin file>:<v12|conv13>:<v030|v6j>
# Every write goes to the container disk (/root/pod); the volume is read (the sealed suite, the synced code) and, at the
# end, the results are copied into results/v06final/ in the workspace for gpu-cli to bring back, with their SHA-256.
# CONC processes share the GPU at a time (default 6). Runs resume: a pass already written is not sent again.
set -uo pipefail
rate=$1; shift
WS=$PWD
P=/root/pod
SEALED=/gpu-cli-workspaces/jameslal/onb-v13-conv-SEALED
SUITE_HASH=dbff73e6e5785d0efcf36be582af061b63d59d351cd655ccb6e153ffa850fdd3
V6J_SHA=f4f39c56f8d3535bb25e01e215f4431591e480688ee293fe96522fb41415706d
mkdir -p $P/results/v06final $WS/results/v06final
command -v uv >/dev/null || pip install -q uv
export PYTHONWARNINGS=ignore UV_CACHE_DIR=$P/uvcache HF_HUB_CACHE=$P/hf UV_PROJECT_ENVIRONMENT=$P/venv-qwen NUMBA_CACHE_DIR=$P/numba
export BENCH_CODE_REVISION=${BENCH_CODE_REVISION:?}
unset VIRTUAL_ENV
df -h /root $WS | sed 's/^/disk: /'

# 1. write self-test, container disk and volume (a full or broken volume shows here, not in the results)
for d in $P $WS/results/v06final; do
  head -c 67108864 /dev/urandom > $d/.selftest && a=$(sha256sum < $d/.selftest) && sync && b=$(cat $d/.selftest | sha256sum)
  [ "$a" = "$b" ] && [ "$(stat -c %s $d/.selftest)" = 67108864 ] && echo "SELFTEST OK $d" || { echo "SELFTEST FAILED $d"; exit 1; }
  rm -f $d/.selftest
done

command -v espeak-ng >/dev/null || (apt-get update -qq >/dev/null 2>&1; apt-get install -y -qq espeak-ng >/dev/null 2>&1)
uv sync -q --frozen --extra qwen || { echo "SYNC FAILED"; exit 1; }
uv run --frozen --extra qwen python -c "import torch, sys; sys.exit(0 if torch.cuda.is_available() else 3)" \
  || { echo "NO CUDA ($(nvidia-smi --query-gpu=name,driver_version --format=csv,noheader 2>&1 | head -1))"; exit 3; }

# 2. the data each spec needs, checked
need=" $* "
if [[ $need == *":v12:"* ]]; then
  [ -f $P/data/.fetched ] || uv run --frozen --extra qwen bench --data $P/data fetch --token --revision v1.2.0 >/dev/null || { echo "FETCH FAILED"; exit 1; }
  # bench load verifies every file against the manifest's SHA-256
  uv run --frozen --extra qwen python -c "
from pathlib import Path; from own_names_bench.data import load, manifest_sha256
b = load(Path('$P/data')); print('v1.2.0 data verified, manifest', manifest_sha256(b.root))" || { echo "V12 DATA FAILED"; exit 1; }
  touch $P/data/.fetched
fi
if [[ $need == *":conv13:"* ]]; then
  if [ ! -f $P/conv13/.verified ]; then
    rm -rf $P/conv13 && mkdir -p $P/conv13
    cp -r $SEALED/suite $P/conv13/suites || { echo "SUITE COPY FAILED"; exit 1; }
    uv run --frozen --extra qwen python - "$P/conv13" "$SEALED/SHA256SUMS" "$SUITE_HASH" <<'EOF' || { echo "SUITE HASH FAILED"; exit 1; }
import hashlib, json, sys
from pathlib import Path
root, sums, want = Path(sys.argv[1]), Path(sys.argv[2]), sys.argv[3]
suite = root / "suites"
def sha(p):
    h = hashlib.sha256()
    with p.open("rb") as f:
        for blk in iter(lambda: f.read(1 << 20), b""):
            h.update(blk)
    return h.hexdigest()
files = {str(p.relative_to(suite)): sha(p) for p in sorted(suite.rglob("*")) if p.is_file()}
blob = "".join(f"{h}  {p}\n" for p, h in sorted(files.items()))
got = hashlib.sha256(blob.encode()).hexdigest()
vol = hashlib.sha256(sums.read_bytes()).hexdigest()
print(f"conv13: {len(files)} files, suite hash of the copy {got}, of the volume's SHA256SUMS {vol}")
if got != want or vol != want:
    raise SystemExit("suite hash mismatch")
from own_names_bench import BENCH_VERSION
suites = sorted(d.name for d in suite.iterdir() if (d / "suite.json").is_file())
# the sealed suites wrapped as a benchmark dataset: no audiobooks, one suite per condition (plumbing only)
m = {"version": BENCH_VERSION, "name": "own-names-bench v1.3 conversation test suite (sealed), wrapped for bench run",
     "suite_hash": want, "files": {}, "entries": {}, "lists": {}, "clips": {}, "mentions": [], "name_free": [], "chapters": [],
     "name_words": [], "suites": [{"name": s, "file": f"suites/{s}/suite.json", "sha256": files[f"{s}/suite.json"]} for s in suites]}
(root / "manifest.json").write_text(json.dumps(m, indent=1))
print("suites:", suites)
EOF
    uv run --frozen --extra qwen python -c "
from pathlib import Path; from own_names_bench.data import load
b = load(Path('$P/conv13')); print('conv13 loaded and verified:', {k: len(s.clips) for k, s in b.suites.items()})" || { echo "CONV13 LOAD FAILED"; exit 1; }
    touch $P/conv13/.verified
  fi
  if [ -n "${PACK_SUITE:-}" ] && [ ! -f $WS/results/v06final/conv13_suite.tar ]; then
    tar -C $P/conv13 -cf $WS/results/v06final/conv13_suite.tar manifest.json suites && sha256sum $WS/results/v06final/conv13_suite.tar
  fi
fi
if [[ $need == *":v6j"* ]]; then
  # V6J_SRC: the adapter folder on the volume (another pod's synced copy), else this workspace's
  mkdir -p $P/adapters && cp -r ${V6J_SRC:-$WS/adapters/qwen17B_audio_heard_v6j} $P/adapters/qwen17B_audio_heard_v6j
  got=$(sha256sum $P/adapters/qwen17B_audio_heard_v6j/adapter_model.safetensors | cut -d' ' -f1)
  [ "$got" = "$V6J_SHA" ] && echo "v6j adapter $got" || { echo "V6J SHA MISMATCH $got"; exit 1; }
fi

# 3. load the models once so concurrent processes do not race on the download
uv run --frozen --extra qwen python -c "
from own_names_bench.ours_ref.writer import Writer
from own_names_bench.ours_ref.spotter import Spotter
from own_names_bench.systems.ours_torch import ADAPTER
Writer('cpu', ADAPTER).load(); Spotter('cpu').load()" >/dev/null 2>&1 || { echo "MODEL LOAD FAILED"; exit 1; }
# (not HF_HUB_OFFLINE: peft then looks for adapter_model.bin and fails on the hub adapter; the models are cached)
export OMP_NUM_THREADS=${THREADS:-2} MKL_NUM_THREADS=${THREADS:-2} NUMBA_NUM_THREADS=${THREADS:-2}

# 4. the specs, CONC at a time
one() {
  spec=$1
  IFS=: read -r sys label only data adapter <<< "$spec"
  root=$P/data; [ "$data" = conv13 ] && root=$P/conv13
  env=(); [ "$adapter" = v6j ] && env=(OURS_ADAPTER=$P/adapters/qwen17B_audio_heard_v6j OURS_ADAPTER_VERSION=v6j)
  env "${env[@]}" uv run --frozen --extra qwen bench --data $root run --system $sys --label $label --out $P/results/v06final --no-chapters \
      --hourly-usd $rate --only @$only > $P/results/v06final/$label.log 2>&1 && echo "DONE $label" || echo "FAILED $label (see $label.log)"
  cp -r $P/results/v06final/$label $P/results/v06final/$label.log $WS/results/v06final/ 2>/dev/null
}
export -f one; export P WS rate
( while sleep 180; do
    echo "$(date +%H:%M) gpu: $(nvidia-smi --query-gpu=utilization.gpu,memory.used --format=csv,noheader) load: $(cut -d' ' -f1 /proc/loadavg) mem: $(free -g | awk '/Mem/{print $3"/"$2"G"}')"
    for f in $P/results/v06final/*.log; do [ -f "$f" ] && echo "  $(basename $f .log): $(tr '\r' '\n' < $f | grep -E 'passes/s|passes,|Error|Traceback' | tail -1)"; done
  done ) &
mon=$!
printf '%s\n' "$@" | xargs -P ${CONC:-6} -I{} bash -c 'one "$@"' _ {}
kill $mon 2>/dev/null
labels=$(printf '%s\n' "$@" | cut -d: -f2)
cd $P/results/v06final && for l in $labels; do [ -d $l ] && find $l -type f | sort | xargs sha256sum; done > $WS/results/v06final/SHA256SUMS.$(hostname) && cat $WS/results/v06final/SHA256SUMS.$(hostname)
for f in $P/results/v06final/*.log; do echo "== $f"; tail -2 "$f"; done
echo "POD DONE"
