#!/bin/bash
# Dev runs on a rented GPU: diag/dev_pod.sh <config>=<dev.py flags>...   (each config one process, sharing the GPU)
# Items are built once into $DEV on the network volume; results land in results/dev/<config>.jsonl.
set -uo pipefail
command -v uv >/dev/null || pip install -q uv
export PYTHONWARNINGS=ignore UV_CACHE_DIR=$PWD/.pod/uvcache HF_HUB_CACHE=$PWD/.pod/hf UV_PROJECT_ENVIRONMENT=$PWD/.pod/venv-qwen
export DEV=${DEV:-/gpu-cli-workspaces/jameslal/fixes-v12-dev}
unset VIRTUAL_ENV
command -v espeak-ng >/dev/null || (apt-get update -qq >/dev/null 2>&1; apt-get install -y -qq espeak-ng >/dev/null 2>&1)
uv sync -q --frozen --extra qwen || { echo "SYNC FAILED"; exit 1; }
mkdir -p results/dev
[ -s $DEV/items.jsonl ] || uv run --frozen --extra qwen python diag/dev_build.py $DEV > results/dev/build.log 2>&1 || { echo "BUILD FAILED"; tail -30 results/dev/build.log; exit 1; }
tail -25 results/dev/build.log
uv run --frozen --extra qwen python -c "
from own_names_bench.ours_ref.writer import Writer
from own_names_bench.ours_ref.spotter import Spotter
from own_names_bench.systems.ours_torch import ADAPTER
Writer('cpu', ADAPTER).load(); Spotter('cpu').load()" >/dev/null 2>&1 || { echo "MODEL LOAD FAILED"; exit 1; }
export OMP_NUM_THREADS=${THREADS:-3} MKL_NUM_THREADS=${THREADS:-3} NUMBA_NUM_THREADS=${THREADS:-3}
pids=()
for spec in "$@"; do
  name=${spec%%=*}; flags=${spec#*=}; flags=${flags//,/ }
  [ "$flags" = "-" ] && flags=""
  ( uv run --frozen --extra qwen python diag/dev.py $DEV/items.jsonl results/dev/$name.jsonl $flags > results/dev/$name.log 2>&1 \
    && echo "DONE $name" || echo "FAILED $name" ) &
  pids+=($!)
done
( while sleep 180; do
    echo "$(date +%H:%M) gpu: $(nvidia-smi --query-gpu=utilization.gpu,memory.used --format=csv,noheader)"
    for f in results/dev/*.log; do echo "  $(basename $f .log): $(grep -E 'items/s|Error|Traceback' $f | tail -1)"; done
  done ) &
mon=$!
for p in "${pids[@]}"; do wait $p; done
kill $mon 2>/dev/null
for f in results/dev/*.log; do echo "== $f"; tail -3 "$f"; done
echo "POD DONE"
