#!/bin/bash
# Diagnosis runs on a rented GPU: diag/pod.sh <$/h> <system>:<label>:<only prefixes, ';'-separated>...
# Every spec runs at the same time (one process each, sharing the GPU); results in results/diag/<label>.
set -uo pipefail
rate=$1; shift
command -v uv >/dev/null || pip install -q uv
export PYTHONWARNINGS=ignore OWN_NAMES_BENCH_DATA=$PWD/.pod/data UV_CACHE_DIR=$PWD/.pod/uvcache HF_HUB_CACHE=$PWD/.pod/hf
export UV_PROJECT_ENVIRONMENT=$PWD/.pod/venv-qwen BENCH_CODE_REVISION=${BENCH_CODE_REVISION:-diag}
unset VIRTUAL_ENV
command -v espeak-ng >/dev/null || (apt-get update -qq >/dev/null 2>&1; apt-get install -y -qq espeak-ng >/dev/null 2>&1)
uv sync -q --frozen --extra qwen || { echo "SYNC FAILED"; exit 1; }
uv run --frozen --extra qwen python -c "import torch, sys; sys.exit(0 if torch.cuda.is_available() else 3)" \
  || { echo "NO CUDA ($(nvidia-smi --query-gpu=name,driver_version --format=csv,noheader 2>&1 | head -1))"; exit 3; }
uv run --frozen --extra qwen bench --data $OWN_NAMES_BENCH_DATA fetch --token --revision v1.2.0 >/dev/null || { echo "FETCH FAILED"; exit 1; }
# load the models once so concurrent processes do not race on the download
uv run --frozen --extra qwen python -c "
from own_names_bench.ours_ref.writer import Writer
from own_names_bench.ours_ref.spotter import Spotter
from own_names_bench.systems.ours_torch import ADAPTER
Writer('cpu', ADAPTER).load(); Spotter('cpu').load()" >/dev/null 2>&1 || { echo "MODEL LOAD FAILED"; exit 1; }
# every process reads the models from the cache (no hub calls: unauthenticated calls get rate-limited); few CPU threads each
export HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1 OMP_NUM_THREADS=${THREADS:-2} MKL_NUM_THREADS=${THREADS:-2} NUMBA_NUM_THREADS=${THREADS:-2}
mkdir -p results/diag
pids=()
for spec in "$@"; do
  sys=${spec%%:*}; rest=${spec#*:}; label=${rest%%:*}; only=${rest#*:}; only=${only//;/,}
  [ "${only:0:1}" = "@" ] && only=$(paste -sd, "${only:1}")
  ( uv run --frozen --extra qwen bench run --system $sys --label $label --out results/diag --no-chapters --hourly-usd $rate \
      ${BENCH_LIMIT:+--limit $BENCH_LIMIT} ${only:+--only $only} > results/diag/$label.log 2>&1 \
    && echo "DONE $label" || echo "FAILED $label (see results/diag/$label.log)" ) &
  pids+=($!)
done
( while sleep 120; do
    echo "$(date +%H:%M) gpu: $(nvidia-smi --query-gpu=utilization.gpu,memory.used --format=csv,noheader) load: $(cut -d' ' -f1 /proc/loadavg) mem: $(free -g | awk '/Mem/{print $3"/"$2"G"}')"
    for f in results/diag/*.log; do echo "  $(basename $f .log): $(tr '\r' '\n' < $f | grep -E 'passes/s|passes,|Error|Traceback' | tail -1)"; done
  done ) &
mon=$!
for p in "${pids[@]}"; do wait $p; done
kill $mon 2>/dev/null
for f in results/diag/*.log; do echo "== $f"; tail -3 "$f"; done
echo "POD DONE"
