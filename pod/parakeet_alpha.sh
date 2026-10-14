#!/bin/bash
# Picks Parakeet's boosting weight on the chapters task: pod/parakeet_alpha.sh <machine tag> <$/h>
set -uo pipefail
tag=$1; rate=$2
command -v uv >/dev/null || pip install -q uv
export PYTHONWARNINGS=ignore OWN_NAMES_BENCH_DATA=$PWD/.pod/data UV_CACHE_DIR=$PWD/.pod/uvcache HF_HUB_CACHE=/tmp/hf UV_PROJECT_ENVIRONMENT=$PWD/.pod/venv-parakeet
unset VIRTUAL_ENV
uv sync -q --frozen --extra parakeet || { echo "SYNC FAILED"; exit 1; }
[ -f $OWN_NAMES_BENCH_DATA/manifest.json ] || uv run --frozen --extra parakeet bench --data $OWN_NAMES_BENCH_DATA fetch --revision "${BENCH_DATA_REVISION:-main}" || exit 1
for a in 0.25 0.5 1 2 4; do
  BENCH_PARAKEET_ALPHA=$a uv run --frozen --extra parakeet bench run --system parakeet --label parakeet-alpha$a-$tag --only chapter/ \
    --hourly-usd $rate && echo "ALPHA DONE $a" || echo "ALPHA FAILED $a"
done
echo "GRID DONE"
