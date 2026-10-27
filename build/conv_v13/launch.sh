#!/bin/bash
# launch.sh [STAGES]: runs run.sh on a pod of this gpu-cli project (EUR-IS-1), with the benchmark's text module copied
# next to the build (_onb/, not in git) and the build commit passed in. Log: out/launch.log (appended).
set -e
cd "$(dirname "$0")"
rm -rf _onb && mkdir -p _onb/own_names_bench out
cp -R ../../own_names_bench/text.py ../../own_names_bench/whisper_normalizer _onb/own_names_bench/
printf '' > _onb/own_names_bench/__init__.py
commit=$(git rev-parse HEAD)
git diff --quiet HEAD -- . || commit="$commit+dirty"
gpu config validate 2>&1 | grep -E "valid|warn|rror" || true
gpu run --sync --sync-conflict-policy local-wins --no-auto-update -y -e BUILD_COMMIT=$commit -e STAGES="${1:-fetch prep build check seal}" \
  bash run.sh 2>&1 | tee -a out/launch.log
