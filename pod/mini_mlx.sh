#!/bin/bash
# ours-mlx on a shared Mac (our Mac mini), everything inside one folder ($W), niced, offline, with
# the load average logged once a minute beside the results (the machine is busy with other work,
# so its latency numbers are labelled with the load and are not headline latency).
# usage (on the Mac): bash $W/code/pod/mini_mlx.sh <engine commit> [label] [--limit N]
set -uo pipefail
W=${W:-$HOME/workroots/own-names-bench}
commit=$1; label=${2:-ours-mlx-macmini}; shift 2 || true
export HF_HUB_CACHE=$W/hf HF_HUB_OFFLINE=1 DETAILKEEPER_BUILT=$W/built DETAILKEEPER_BENCH=$W/bin/detailkeeper-bench \
  DETAILKEEPER_ENGINE_COMMIT=$commit OWN_NAMES_BENCH_DATA=$W/data BENCH_WAV_CACHE=$W/wav UV_CACHE_DIR=$W/uvcache \
  UV_PYTHON_INSTALL_DIR=$W/python UV_PROJECT_ENVIRONMENT=$W/venv PATH=$W/stub:$PATH
mkdir -p "$W/results/$label"
(while true; do echo "$(date -u +%FT%TZ) $(sysctl -n vm.loadavg)"; sleep 60; done) >> "$W/results/$label/loadavg.log" &
logger=$!
trap 'kill $logger 2>/dev/null' EXIT
df -h "$W" | tail -1
cd "$W/code" && nice -n 10 uv run --frozen bench run --system ours-mlx --label "$label" --out "$W/results" "$@"
status=$?
df -h "$W" | tail -1
exit $status
