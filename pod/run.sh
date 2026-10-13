#!/bin/bash
# Runs local systems on a rented GPU: pod/run.sh <machine tag> <machine $/h> <system>...
# Each system's pinned stack is installed from uv.lock into its own environment. Caches, models
# and environments live in .pod/ in the job folder (the pod's large volume), and each
# environment is removed once its systems are done.
set -uo pipefail
tag=$1; rate=$2; shift 2
command -v uv >/dev/null || pip install -q uv
export PYTHONWARNINGS=ignore OWN_NAMES_BENCH_DATA=$PWD/.pod/data UV_CACHE_DIR=$PWD/.pod/uvcache HF_HOME=$PWD/.pod/hf
unset VIRTUAL_ENV
df -h . /tmp | sed 's/^/disk: /'
status=0
prev=""
for sys in "$@"; do
  case $sys in
    ours|qwen|qwen-context) extra=qwen ;;
    whisper) extra=whisper ;;
    parakeet) extra=parakeet ;;
    *) echo "unknown system $sys"; exit 2 ;;
  esac
  if [ -n "$prev" ] && [ "$prev" != "$extra" ]; then rm -rf "$PWD/.pod/venv-$prev"; uv cache clean -q || true; fi
  prev=$extra
  export UV_PROJECT_ENVIRONMENT=$PWD/.pod/venv-$extra
  uv sync -q --frozen --extra $extra || { echo "SYNC FAILED $extra"; status=1; continue; }
  if [ ! -f $OWN_NAMES_BENCH_DATA/manifest.json ]; then
    uv run --frozen --extra $extra bench --data $OWN_NAMES_BENCH_DATA fetch --revision "${BENCH_DATA_REVISION:-main}" || exit 1
  fi
  uv run --frozen --extra $extra bench run --system $sys --label $sys-$tag --hourly-usd $rate ${BENCH_LIMIT:+--limit $BENCH_LIMIT} \
    && echo "SYSTEM DONE $sys" || { echo "SYSTEM FAILED $sys"; status=1; }
  df -h . | tail -1 | sed 's/^/disk: /'
done
[ $status = 0 ] && echo "POD DONE" || echo "POD FAILED"
exit $status
