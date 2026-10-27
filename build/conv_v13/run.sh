#!/bin/bash
# Runs on a RunPod pod in EUR-IS-1 with the global volume: builds, checks and seals the own-names-bench v1.3
# conversation test suite under $ONB_SEALED. STAGES (default: all) picks stages: fetch prep build check seal (noise: only the noise clips again).
# Prints counts only: no transcript or name list is printed or copied to out/.
set -o pipefail
export ONB_SEALED=${ONB_SEALED:-/gpu-cli-workspaces/jameslal/onb-v13-conv-SEALED}
export CONV_TRAINDEV=${CONV_TRAINDEV:-/gpu-cli-workspaces/jameslal/v06-conv/lore-conv}
STAGES=${STAGES:-fetch prep build check seal}
mkdir -p out/logs
echo "host $(hostname) ONB_SEALED=$ONB_SEALED CONV_TRAINDEV=$CONV_TRAINDEV STAGES=$STAGES commit=${BUILD_COMMIT:-?}"
[ -e "$ONB_SEALED/SEALED.txt" ] && { echo "ALREADY SEALED: $(head -1 $ONB_SEALED/SEALED.txt); nothing to do"; exit 0; }
mkdir -p $ONB_SEALED/build
# the volume has had a host writing zero-filled files: refuse to run on one
python3 - <<'PY' || { echo "VOLUME WRITE TEST FAILED on $(hostname)"; exit 3; }
import os, hashlib, sys
bad = 0
for base in (os.environ["ONB_SEALED"] + "/build", os.environ["ONB_SEALED"]):
    d = f"{base}/.iotest_{os.uname().nodename}"; os.makedirs(d, exist_ok=True)
    for i in range(24):
        b = os.urandom(1000 + i * 7919 + (1 << 20) * (i % 3)); p = f"{d}/f{i}.bin"
        with open(p, "wb") as f:
            f.write(b); f.flush(); os.fsync(f.fileno())
        bad += hashlib.sha256(open(p, "rb").read()).digest() != hashlib.sha256(b).digest()
        os.remove(p)
    os.rmdir(d)
print("volume write test: bad", bad); sys.exit(1 if bad else 0)
PY
df -h /gpu-cli-workspaces | tail -1
[ -f $CONV_TRAINDEV/rows/train.jsonl ] && [ -f $CONV_TRAINDEV/rows/dev.jsonl ] || { echo "train/dev data not found at $CONV_TRAINDEV"; exit 4; }
export PATH="$HOME/.local/bin:$PATH"; command -v uv >/dev/null || pip install -q uv
command -v ffmpeg >/dev/null || (apt-get update -qq && apt-get install -y -qq ffmpeg >/dev/null) || echo "ffmpeg install failed"
nvidia-smi --query-gpu=name,memory.total --format=csv,noheader
uv sync -q || exit 5
step() { local name=$1; shift; echo "== $name $(date -u +%H:%M:%S)"; "$@" > out/logs/$name.log 2>&1; local rc=$?; grep -v "it/s\|Fetching\|Download" out/logs/$name.log | tail -8; [ $rc = 0 ] || { echo "FAILED $name ($rc)"; exit $rc; }; }
has() { [[ " $STAGES " == *" $1 "* ]]; }
if has fetch; then step fetch uv run python fetch.py; fi
if has noise; then  # the noise clips alone (refetched if removed)
  step fetch_fsd uv run python fetch.py fsd
  step prep_noise uv run python prep.py noise
  rm -rf $ONB_SEALED/build/src/fsd/clips
fi
if has prep; then
  step prep_noise uv run python prep.py noise
  step prep_voxpopuli uv run python prep.py voxpopuli
  step prep_libritts uv run python prep.py libritts
  # raw downloads are not kept (fetched.json records what and its hashes); refetch with fetch.py
  find $ONB_SEALED/build/src -name "*.parquet" -delete; rm -rf $ONB_SEALED/build/src/fsd/clips
  cp $ONB_SEALED/build/utts/*_stats.json $ONB_SEALED/build/src/fetched.json out/ 2>/dev/null
fi
if has build; then
  [ -d $ONB_SEALED/suite ] && rm -rf $ONB_SEALED/suite
  step build uv run python build.py
  cp $ONB_SEALED/build/build_stats.json out/
fi
if has check; then step check uv run python check.py; cp $ONB_SEALED/build/contamination.json out/; fi
if has seal; then
  step seal uv run python seal.py
  cp $ONB_SEALED/MANIFEST.json $ONB_SEALED/SHA256SUMS $ONB_SEALED/build/validity.json out/
  du -sh $ONB_SEALED/suite $ONB_SEALED/build
fi
echo "ALL DONE"
