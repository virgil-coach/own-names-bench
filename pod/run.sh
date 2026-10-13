#!/bin/bash
# Runs local systems on a rented GPU: pod/run.sh <machine tag> <machine $/h> <system>...
# Each system's pinned stack is installed from uv.lock into its own environment on local disk.
set -uo pipefail
tag=$1; rate=$2; shift 2
command -v uv >/dev/null || pip install -q uv
command -v espeak-ng >/dev/null || (apt-get update -qq >/dev/null 2>&1; apt-get install -y -qq espeak-ng >/dev/null 2>&1)
export UV_CACHE_DIR=/tmp/uvcache PYTHONWARNINGS=ignore OWN_NAMES_BENCH_DATA=/tmp/own-names-bench-data
status=0
for sys in "$@"; do
  case $sys in
    ours|qwen|qwen-context) extra=qwen ;;
    whisper) extra=whisper ;;
    parakeet) extra=parakeet ;;
    *) echo "unknown system $sys"; exit 2 ;;
  esac
  export UV_PROJECT_ENVIRONMENT=/tmp/venv-$extra
  uv sync -q --frozen --extra $extra || { echo "SYNC FAILED $extra"; status=1; continue; }
  if [ ! -f $OWN_NAMES_BENCH_DATA/manifest.json ]; then
    uv run --frozen --extra $extra bench fetch --revision "${BENCH_DATA_REVISION:-main}" || exit 1
  fi
  uv run --frozen --extra $extra bench run --system $sys --label $sys-$tag --hourly-usd $rate ${BENCH_LIMIT:+--limit $BENCH_LIMIT} \
    && echo "SYSTEM DONE $sys" || { echo "SYSTEM FAILED $sys"; status=1; }
done
[ $status = 0 ] && echo "POD DONE" || echo "POD FAILED"
exit $status
