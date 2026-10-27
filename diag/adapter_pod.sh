#!/bin/bash
# Candidate adapters on own-names-bench v1.2.0 (results/v07bench/PROTOCOL.md: the audiobook suite is a selection
# target; aggregates only) on a rented GPU on the EUR-IS-1 global volume. Generalises diag/final_pod.sh: any system,
# any adapter folder on the volume, checked against its SHA-256. v1.2.0 only: the sealed v1.3 suite is never read here.
#
# usage: diag/adapter_pod.sh <$/h> <out> <spec>...
#   out  = results/<out>/ in the workspace (e.g. v07bench)
#   spec = <system>:<label>:<podin file>:<adapter folder on the volume, or - for the system's own>:<adapter sha256, or ->
#   e.g. ours-reread:ours-reread-v7a--0:podin/bk-0.txt:/gpu-cli-workspaces/jameslal/v07-a/results/qwen17B_audio_heard_v7a:6453…
# The adapter is copied to the container disk once (by SHA-256) and checked; OURS_ADAPTER_VERSION = the folder's name.
# Every write goes to the container disk (/root/pod); results are copied into results/<out>/ for gpu-cli to bring back.
# CONC processes share the GPU at a time (default 6, at most 6). Runs resume: a pass already written is not sent again.
set -uo pipefail
rate=$1; out=$2; shift 2
WS=$PWD
P=/root/pod
CONC=${CONC:-6}; [ "$CONC" -le 6 ] || { echo "CONC $CONC > 6"; exit 1; }
mkdir -p $P/results/$out $WS/results/$out
export PATH=$HOME/.local/bin:/usr/local/bin:$PATH
command -v uv >/dev/null || pip install -q uv || python3 -m pip install -q --break-system-packages uv
command -v uv >/dev/null || { echo "NO UV ($(command -v pip) $(python3 --version))"; exit 1; }
export PYTHONWARNINGS=ignore UV_CACHE_DIR=$P/uvcache HF_HUB_CACHE=$P/hf UV_PROJECT_ENVIRONMENT=$P/venv-qwen NUMBA_CACHE_DIR=$P/numba
export BENCH_CODE_REVISION=${BENCH_CODE_REVISION:?}
unset VIRTUAL_ENV
df -h /root $WS | sed 's/^/disk: /'

# 1. write self-test, container disk and volume (a full or broken volume shows here, not in the results)
for d in $P $WS/results/$out; do
  head -c 67108864 /dev/urandom > $d/.selftest && a=$(sha256sum < $d/.selftest) && sync && b=$(cat $d/.selftest | sha256sum)
  [ "$a" = "$b" ] && [ "$(stat -c %s $d/.selftest)" = 67108864 ] && echo "SELFTEST OK $d" || { echo "SELFTEST FAILED $d"; exit 1; }
  rm -f $d/.selftest
done

command -v espeak-ng >/dev/null || (apt-get update -qq >/dev/null 2>&1; apt-get install -y -qq espeak-ng >/dev/null 2>&1)
uv sync -q --frozen --extra qwen || { echo "SYNC FAILED"; exit 1; }
uv run --frozen --extra qwen python -c "import torch, sys; sys.exit(0 if torch.cuda.is_available() else 3)" \
  || { echo "NO CUDA ($(nvidia-smi --query-gpu=name,driver_version --format=csv,noheader 2>&1 | head -1))"; exit 3; }

# 2. v1.2.0 data (bench load verifies every file against the manifest's SHA-256), and each adapter, checked
[ -f $P/data/.fetched ] || uv run --frozen --extra qwen bench --data $P/data fetch --token --revision v1.2.0 >/dev/null || { echo "FETCH FAILED"; exit 1; }
uv run --frozen --extra qwen python -c "
from pathlib import Path; from own_names_bench.data import load, manifest_sha256
b = load(Path('$P/data')); print('v1.2.0 data verified, manifest', manifest_sha256(b.root))" || { echo "V12 DATA FAILED"; exit 1; }
touch $P/data/.fetched
mkdir -p $P/adapters
for pair in $(printf '%s\n' "$@" | cut -d: -f4,5 | sort -u); do
  src=${pair%%:*}; want=${pair##*:}
  [ "$src" = - ] && continue
  dst=$P/adapters/$want/$(basename $src)
  [ -f $dst/adapter_model.safetensors ] || { mkdir -p $(dirname $dst) && cp -r $src $dst; } || { echo "ADAPTER COPY FAILED $src"; exit 1; }
  got=$(sha256sum $dst/adapter_model.safetensors | cut -d' ' -f1)
  [ "$got" = "$want" ] && echo "adapter $(basename $src) $got" || { echo "ADAPTER SHA MISMATCH $src $got"; exit 1; }
done

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
  IFS=: read -r sys label only src sha <<< "$spec"
  env=(); [ "$src" != - ] && env=(OURS_ADAPTER=$P/adapters/$sha/$(basename $src) OURS_ADAPTER_VERSION=$(basename $src))
  env "${env[@]}" uv run --frozen --extra qwen bench --data $P/data run --system $sys --label $label --out $P/results/$out --no-chapters \
      --hourly-usd $rate --only @$only > $P/results/$out/$label.log 2>&1 && echo "DONE $label" || echo "FAILED $label (see $label.log)"
  cp -r $P/results/$out/$label $P/results/$out/$label.log $WS/results/$out/ 2>/dev/null
}
export -f one; export P WS rate out
( while sleep 180; do
    echo "$(date +%H:%M) gpu: $(nvidia-smi --query-gpu=utilization.gpu,memory.used --format=csv,noheader) load: $(cut -d' ' -f1 /proc/loadavg) mem: $(free -g | awk '/Mem/{print $3"/"$2"G"}')"
    for f in $P/results/$out/*.log; do [ -f "$f" ] && echo "  $(basename $f .log): $(tr '\r' '\n' < $f | grep -E 'passes/s|passes,|Error|Traceback' | tail -1)"; done
  done ) &
mon=$!
printf '%s\n' "$@" | xargs -P $CONC -I{} bash -c 'one "$@"' _ {}
kill $mon 2>/dev/null
labels=$(printf '%s\n' "$@" | cut -d: -f2)
cd $P/results/$out && for l in $labels; do [ -d $l ] && find $l -type f | sort | xargs sha256sum; done > $WS/results/$out/SHA256SUMS.$(hostname) && cat $WS/results/$out/SHA256SUMS.$(hostname)
for f in $P/results/$out/*.log; do echo "== $f"; tail -2 "$f"; done
echo "POD DONE"
