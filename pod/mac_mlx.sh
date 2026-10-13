#!/bin/bash
# The whole benchmark on this Mac with the Detail Keeper engine itself (Rust, MLX).
# One heavy model process at a time: the owner's engine on :8787 is stopped first, only when it
# has no ESTABLISHED connection, and restarted afterwards (waiting for "ready": true).
#
# usage: pod/mac_mlx.sh <label>      (DETAILKEEPER_BENCH defaults to the bench worktree's build)
set -uo pipefail
label=${1:-ours-mlx-mac}
here=$(cd "$(dirname "$0")/.." && pwd)
dk=/Users/jameslal/workspace/jl/detailkeeper/services/engine
export DETAILKEEPER_BENCH=${DETAILKEEPER_BENCH:-/Users/jameslal/workspace/jl/detailkeeper-wt-bench/services/engine/target/release/detailkeeper-bench}
export OWN_NAMES_BENCH_DATA=${OWN_NAMES_BENCH_DATA:-/Users/jameslal/workspace/jl/own-names-bench-src/dataset}
export BENCH_WAV_CACHE=${BENCH_WAV_CACHE:-/Users/jameslal/workspace/jl/own-names-bench-src/wav-cache}
test -x "$DETAILKEEPER_BENCH" || { echo "no binary at $DETAILKEEPER_BENCH"; exit 1; }
test -f "$(dirname "$DETAILKEEPER_BENCH")/mlx.metallib" || { echo "mlx.metallib missing beside the binary"; exit 1; }

pid=$(lsof -nP -iTCP:8787 -sTCP:LISTEN -t 2>/dev/null | head -1)
restart=0
if [ -n "$pid" ]; then
  if lsof -nP -iTCP:8787 -sTCP:ESTABLISHED 2>/dev/null | grep -q .; then
    echo "the engine on :8787 has an ESTABLISHED connection; not stopping it"; exit 3
  fi
  kill "$pid"
  while kill -0 "$pid" 2>/dev/null; do sleep 0.5; done
  restart=1
  echo "stopped the engine on :8787 (pid $pid)"
fi

cd "$here"
uv run bench run --system ours-mlx --label "$label"
status=$?

if [ $restart = 1 ]; then
  cd "$dk" && (nohup target/release/detailkeeper --data ../../.data > ../../.data/engine.log 2>&1 &)
  until curl -sf http://127.0.0.1:8787/api/status | grep -q '"ready":true'; do sleep 2; done
  echo "engine on :8787 is back (ready)"
fi
exit $status
