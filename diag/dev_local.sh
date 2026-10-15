#!/bin/bash
# Dev runs with every write on the container disk (the network volume's quota was full, and files synced to it came
# out corrupt): the code arrives by `gpu cp` as /root/code.tgz; results in /root/w/results/dev, fetched by gpu cp.
# usage (on the pod): bash /root/w/diag/dev_local.sh K/N
set -uo pipefail
part=$1
W=/root/w; cd $W; mkdir -p results/dev
command -v uv >/dev/null || pip install -q uv
export PYTHONWARNINGS=ignore UV_CACHE_DIR=/root/pod/uvcache UV_PROJECT_ENVIRONMENT=/root/pod/venv-qwen
export HF_HUB_CACHE=/root/hf DEV=/gpu-cli-workspaces/jameslal/fixes-v12-dev
unset VIRTUAL_ENV
df -h /root | tail -1
command -v espeak-ng >/dev/null || (apt-get update -qq >/dev/null 2>&1; apt-get install -y -qq espeak-ng >/dev/null 2>&1)
uv sync -q --frozen --extra qwen > results/dev/sync.log 2>&1 || { echo "SYNC FAILED"; tail results/dev/sync.log; exit 1; }
uv run --frozen --extra qwen python -c "
from own_names_bench.ours_ref.writer import Writer
from own_names_bench.ours_ref.spotter import Spotter
from own_names_bench.systems.ours_torch import ADAPTER
Writer('cpu', ADAPTER).load(); Spotter('cpu').load()" > results/dev/models.log 2>&1 || { echo "MODEL LOAD FAILED"; tail results/dev/models.log; exit 1; }
df -h /root | tail -1
export OMP_NUM_THREADS=3 MKL_NUM_THREADS=3 NUMBA_NUM_THREADS=3
pids=()
for spec in base=- level=--level s25=--min-speech,2.5 s40=--min-speech,4.0 level_s25=--level,--min-speech,2.5 level_s40=--level,--min-speech,4.0; do
  name=${spec%%=*}; flags=${spec#*=}; flags=${flags//,/ }; [ "$flags" = "-" ] && flags=""
  ( uv run --frozen --extra qwen python diag/dev.py $DEV/items.jsonl results/dev/$name.jsonl $flags --part $part --skip podin/devdone_$name.txt \
      > results/dev/$name.log 2>&1 && echo "DONE $name" || { echo "FAILED $name"; tail -5 results/dev/$name.log; } ) &
  pids+=($!)
done
( while sleep 300; do echo "$(date +%H:%M) gpu $(nvidia-smi --query-gpu=utilization.gpu --format=csv,noheader) $(for c in base level s25 s40 level_s25 level_s40; do echo -n "$c:$(grep -c . results/dev/$c.jsonl 2>/dev/null) "; done)"; done ) &
mon=$!
for p in "${pids[@]}"; do wait $p; done
kill $mon
echo "POD DONE"
