#!/bin/bash
# v1.2 build, align stage: pod/align.sh  (reads podin/align_jobs.json, writes results/align/v12_align.json)
set -uo pipefail
command -v uv >/dev/null || pip install -q uv
export PYTHONWARNINGS=ignore UV_CACHE_DIR=$PWD/.pod/uvcache HF_HUB_CACHE=/tmp/hf UV_PROJECT_ENVIRONMENT=$PWD/.pod/venv-qwen
unset VIRTUAL_ENV
uv sync -q --frozen --extra qwen --extra build || { echo "SYNC FAILED"; exit 1; }
uv run --frozen --extra qwen --extra build python build/align.py podin/align_jobs.json results/align/v12_align.json && echo "ALIGN DONE" || echo "ALIGN FAILED"
