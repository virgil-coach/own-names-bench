#!/bin/bash
# ours-mlx (the Detail Keeper engine's detailkeeper-bench: MLX, writer merged + affine 8-bit, guard + re-read) on one of
# our Macs, everything inside one folder ($W), niced, offline, with the load average logged beside the results.
# The same passes as ours-reread (OURS_MLX_VARIANTS=none,own); one shard of them per call.
#
# usage (on the Mac): W=... bash $W/code/pod/mac_mlx.sh <engine commit> <label> <podin file> <adapter> <version> <sha256|->
#   adapter: hf://OWNER/REPO@REV/FOLDER or a folder under $W/adapters (checked against sha256 before it runs)
# One heavy model process per machine: run the shards of a machine one after the other, never side by side.
# v1.2.0 only. The sealed v1.3 conversation suite is never on these machines.
set -uo pipefail
W=${W:-$HOME/workroots/v7c-release}
commit=$1; label=$2; only=$3; adapter=$4; version=$5; sha=$6
if [ "$sha" != - ]; then
  got=$(shasum -a 256 "$adapter/adapter_model.safetensors" | cut -d' ' -f1)
  [ "$got" = "$sha" ] || { echo "ADAPTER SHA MISMATCH $adapter $got"; exit 1; }
fi
export HF_HUB_CACHE=$W/hf HF_HUB_OFFLINE=1 DETAILKEEPER_BUILT=$W/built DETAILKEEPER_BENCH=$W/bin/detailkeeper-bench \
  DETAILKEEPER_ENGINE_COMMIT=$commit OWN_NAMES_BENCH_DATA=$W/data BENCH_WAV_CACHE=$W/wav UV_CACHE_DIR=$W/uvcache \
  UV_PYTHON_INSTALL_DIR=$W/python UV_PROJECT_ENVIRONMENT=$W/venv PATH=$W/bin:$PATH \
  OURS_MLX_VARIANTS=none,own OURS_MLX_ADAPTER=$adapter OURS_MLX_ADAPTER_VERSION=$version OURS_MLX_ADAPTER_SHA256=$sha
mkdir -p "$W/results/$label"
(while true; do echo "$(date -u +%FT%TZ) $(sysctl -n vm.loadavg)"; sleep 60; done) >> "$W/results/$label/loadavg.log" &
logger=$!
trap 'kill $logger 2>/dev/null' EXIT
cd "$W/code" && nice -n 10 uv run --frozen bench run --system ours-mlx --label "$label" --out "$W/results" --no-chapters \
  --only "@$only"
