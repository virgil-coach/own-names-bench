#!/bin/bash
# ours-mlx (v7c + guard + re-read, Detail Keeper engine af939d6, MLX 8-bit) once on a sealed v1.3 launch suite, on a
# bench Mac, everything in $W, niced, offline, load average logged beside the results. As pod/mac_mlx.sh, but the
# whole suite in one process (no shards) and the suite's own WAV cache. The suite's seal is checked before this runs.
# Writes $W/results/<suite>/<label>/ and, when done, $W/results/<suite>/<label>.exit (wait on it with wait4path).
#
# usage (on the Mac): W=... bash $W/code/diag/sealed_mlx.sh <suite>     suite = books13 | conv13 (data in $W/<suite>)
# One heavy model process per machine.
set -uo pipefail
W=${W:-$HOME/workroots/v7c-release}
suite=$1
label=$suite-v7c-mlx
SHA=de91437d4fc828b49605e6482a32b817d55ac4853d1714ac1e2bf9be8f61226c
A=$W/adapters/qwen17B_audio_heard_v7c
out=$W/results/$suite
mkdir -p "$out/$label"
done_file=$out/$label.exit
rm -f "$done_file"
got=$(shasum -a 256 "$A/adapter_model.safetensors" | cut -d' ' -f1)
[ "$got" = "$SHA" ] || { echo "ADAPTER SHA MISMATCH $got"; echo 90 > "$done_file"; exit 1; }
export HF_HUB_CACHE=$W/hf HF_HUB_OFFLINE=1 DETAILKEEPER_BUILT=$W/built DETAILKEEPER_BENCH=$W/bin/detailkeeper-bench \
  DETAILKEEPER_ENGINE_COMMIT=af939d6 BENCH_WAV_CACHE=$W/wav-$suite UV_CACHE_DIR=$W/uvcache \
  UV_PYTHON_INSTALL_DIR=$W/python UV_PROJECT_ENVIRONMENT=$W/venv PATH=$W/bin:$PATH \
  OURS_MLX_VARIANTS=none,own OURS_MLX_ADAPTER=$A OURS_MLX_ADAPTER_VERSION=v0.7.0 OURS_MLX_ADAPTER_SHA256=$SHA
(while true; do echo "$(date -u +%FT%TZ) $(sysctl -n vm.loadavg)"; sleep 60; done) >> "$out/$label/loadavg.log" &
logger=$!
trap 'kill $logger 2>/dev/null' EXIT
cd "$W/code" && nice -n 10 uv run --frozen bench --data "$W/$suite" run --system ours-mlx --label "$label" --out "$out" --no-chapters
echo $? > "$done_file"
