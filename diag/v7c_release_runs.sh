#!/bin/bash
# Everything the v7c release check runs once the adapter is on this Mac, driven from here over ssh:
#   1. the adapter to both bench Macs, SHA-256 checked there
#   2. the 8-bit writer built by the engine on each Mac (must be bit-identical; that file is the runtime bundle's)
#   3. writer parity on the 400 calls: torch on the Studio, MLX on the mini (diag/writer_parity.py)
#   4. ours-mlx on every v1.2.0 suite, shards 0-6 on the Studio and 7-11 on the mini, one at a time per machine
# Then score with diag/mlx_score.py and log the audiobook look in results/v07bench/LOOKS.md.
# Tailscale SSH returns 0 whatever the remote command does: every check here reads printed output.
#
# usage: diag/v7c_release_runs.sh <local v7c adapter folder>
set -uo pipefail
SRC=${1:?adapter folder}
SHA=de91437d4fc828b49605e6482a32b817d55ac4853d1714ac1e2bf9be8f61226c
ST=james@jamess-mac-studio MINI=virgil@virgils-mac-mini
ENGINE=af939d6
[ "$(shasum -a 256 "$SRC/adapter_model.safetensors" | cut -d' ' -f1)" = $SHA ] || { echo "local adapter SHA mismatch"; exit 1; }
for h in $ST $MINI; do
  rsync -a "$SRC/" $h:workroots/v7c-release/adapters/qwen17B_audio_heard_v7c/
  got=$(ssh $h 'shasum -a 256 ~/workroots/v7c-release/adapters/qwen17B_audio_heard_v7c/adapter_model.safetensors' | cut -d' ' -f1)
  [ "$got" = $SHA ] || { echo "$h adapter SHA mismatch: $got"; exit 1; }
done
# 2. build (the engine builds a folder adapter on first load; stdin closed: load, report ready, exit)
for h in $ST $MINI; do
  ssh $h 'W=$HOME/workroots/v7c-release; export HF_HUB_CACHE=$W/hf HF_HUB_OFFLINE=1 DETAILKEEPER_BUILT=$W/built;
    echo -n | $W/bin/detailkeeper-bench --adapter $W/adapters/qwen17B_audio_heard_v7c --format audio_heard 2>&1 | tail -1;
    ls -t $W/built/mlx-rs/*.safetensors | head -1 | xargs shasum -a 256; ls -t $W/built/mlx-rs/*.safetensors | head -1 | xargs stat -f %z'
done
# 3. parity (both sides at once: one heavy process per machine)
ssh $ST 'W=$HOME/workroots/v7c-release; cd $W/code && HF_HUB_CACHE=$W/hf HF_HUB_OFFLINE=1 UV_CACHE_DIR=$W/uvcache UV_PYTHON_INSTALL_DIR=$W/python UV_PROJECT_ENVIRONMENT=$W/venv-qwen
  $W/bin/uv run --frozen --extra qwen python diag/writer_parity.py torch $W/parity $W/adapters/qwen17B_audio_heard_v7c --device mps > $W/parity/torch_v7c.log 2>&1; mv $W/parity/torch.json $W/parity/torch_v7c.json' &
ssh $MINI 'W=$HOME/workroots/v7c-release; B=$(ls -d $W/hf/models--mlx-community--Qwen3-ASR-1.7B-bf16/snapshots/*); T=$(ls $W/hf/models--virgil-coach--detailkeeper-runtime/snapshots/*/writer/tokenizer.json);
  $W/bin/writer_replay --calls $W/parity/calls.json --audio $W/parity/audio --base $B --tokenizer $T --adapter $W/adapters/qwen17B_audio_heard_v7c --cache $W/built --out $W/parity/mlx_v7c.json > $W/parity/mlx_v7c.log 2>&1' &
wait
P=results/v7crel/parity; mkdir -p $P
scp -q $ST:workroots/v7c-release/parity/torch_v7c.json $P/ && scp -q $MINI:workroots/v7c-release/parity/mlx_v7c.json $P/ || { echo "parity outputs missing"; exit 1; }
uv run --frozen python -I diag/writer_parity.py score $P $P/mlx_v7c.json $P/torch_v7c.json | tee results/v7crel/parity_v7c.md
# 4. full suite, the shards of each machine one after the other
A='$HOME/workroots/v7c-release/adapters/qwen17B_audio_heard_v7c'
run() {  # host, shard list
  ssh $1 "W=\$HOME/workroots/v7c-release; for k in $2; do W=\$W bash \$W/code/pod/mac_mlx.sh $ENGINE v7c-mlx--\$k \$W/code/podin/mlx-\$k.txt $A v0.7.0-rc-v7c $SHA > \$W/results/v7c-mlx--\$k.log 2>&1; echo \"\$k exit \$?\" >> \$W/results/v7c-queue.log; done"
}
run $ST "0 1 2 3 4 5 6" & run $MINI "7 8 9 10 11" & wait
for h in $ST $MINI; do rsync -a --include='v7c-mlx--*/***' --exclude='*' $h:workroots/v7c-release/results/ results/v7crel/; ssh $h 'cat ~/workroots/v7c-release/results/v7c-queue.log'; done
n=$(cat results/v7crel/v7c-mlx--*/passes.jsonl | wc -l | tr -d ' '); echo "v7c passes: $n / 13670"
uv run --frozen python diag/mlx_score.py --v12 "${V12:-$HOME/workspace/jl/own-names-bench-src/dataset}" \
  --sys 'v030-mlx=v0.3.0 + guard + re-read, MLX 8-bit (Detail Keeper 0.1.1)=v7crel/v030-mlx' \
  --sys 'v7c-mlx=v7c (v0.7.0 candidate) + guard + re-read, MLX 8-bit=v7crel/v7c-mlx' \
  --base v030-mlx --md results/v7crel/TABLES.md --json results/v7crel/scores.json > /dev/null
echo "scored: results/v7crel/TABLES.md (log the audiobook look in results/v07bench/LOOKS.md)"
