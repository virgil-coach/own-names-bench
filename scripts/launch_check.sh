#!/bin/bash
# Launch-day check: what a stranger does, with no credentials. Run it once the GitHub repo and
# the Hugging Face dataset are public. It clones the code anonymously into a fresh folder, uses a
# fresh HOME (no Hugging Face login, no git credentials, no uv cache), fetches the pinned dataset
# anonymously, runs the tests, rebuilds the report from the published runs and checks it matches
# the committed one, and verifies the sealed suites and their published results.
#
# usage: scripts/launch_check.sh [git ref, default v1.3.0]
set -euo pipefail
ref=${1:-v1.3.0}
work=$(mktemp -d)
export HOME=$work/home XDG_CACHE_HOME=$work/cache HF_HOME=$work/hf UV_CACHE_DIR=$work/uv GIT_TERMINAL_PROMPT=0
mkdir -p "$HOME"
unset HF_TOKEN HUGGING_FACE_HUB_TOKEN GH_TOKEN GITHUB_TOKEN
echo "== anonymous clone"
git clone -q --depth 1 --branch "$ref" https://github.com/virgil-coach/own-names-bench.git "$work/repo"
cd "$work/repo"
echo "== anonymous fetch"
uv run bench --data "$work/data" fetch
export OWN_NAMES_BENCH_DATA=$work/data
echo "== tests"
uv run --with pytest==8.4.2 pytest -q tests
echo "== report from the published runs"
cp results/scores/REPORT.md "$work/REPORT.committed.md"
uv run bench report $(sed -n 's/^# report-args: //p' results/scores/REPORT_ARGS 2>/dev/null)
diff <(grep -v '^Scored' "$work/REPORT.committed.md") <(grep -v '^Scored' results/scores/REPORT.md) && echo "REPORT REPRODUCED"
echo "== sealed suites"
uv run python scripts/verify_sealed.py "$work/data"
echo "LAUNCH CHECK PASSED ($work)"
