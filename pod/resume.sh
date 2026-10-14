#!/bin/bash
# Finishes published runs on a rented GPU: pod/resume.sh <$/h> <label>:<system>...
# resume/<label>/ holds the run as published (run.json, passes.jsonl.gz); only passes missing from
# it, or made from an older list, are run. Each system's stack comes from uv.lock.
set -uo pipefail
rate=$1; shift
command -v uv >/dev/null || pip install -q uv
export PYTHONWARNINGS=ignore OWN_NAMES_BENCH_DATA=$PWD/.pod/data UV_CACHE_DIR=$PWD/.pod/uvcache HF_HUB_CACHE=/tmp/hf
unset VIRTUAL_ENV
status=0
for spec in "$@"; do
  label=${spec%%:*}; sys=${spec#*:}
  case $sys in ours|qwen|qwen-context) extra=qwen ;; whisper) extra=whisper ;; parakeet) extra=parakeet ;; *) echo "unknown $sys"; exit 2 ;; esac
  export UV_PROJECT_ENVIRONMENT=$PWD/.pod/venv-$extra
  uv sync -q --frozen --extra $extra || { echo "SYNC FAILED $extra"; status=1; continue; }
  if [ ! -f $OWN_NAMES_BENCH_DATA/manifest.json ] || ! grep -q '"version": "1.1.0"' $OWN_NAMES_BENCH_DATA/manifest.json; then
    rm -rf $OWN_NAMES_BENCH_DATA
    uv run --frozen --extra $extra bench --data $OWN_NAMES_BENCH_DATA fetch --token --revision "${BENCH_DATA_REVISION:-main}" || exit 1
  fi
  mkdir -p results/runs && rm -rf results/runs/$label && cp -r resume/$label results/runs/$label
  uv run --frozen --extra $extra bench run --system $sys --label $label --hourly-usd $rate ${BENCH_ACCEPT:+--accept-config-change "$BENCH_ACCEPT"} \
    && echo "SYSTEM DONE $label" || { echo "SYSTEM FAILED $label"; status=1; }
done
[ $status = 0 ] && echo "POD DONE" || echo "POD FAILED"
exit $status
