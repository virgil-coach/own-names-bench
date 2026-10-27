#!/bin/bash
# diag/adapter_pod.sh with its specs read from a file, one per line (long spec lists through gpu run were split).
# usage: diag/adapter_pod_file.sh <$/h> <out> <spec file>
rate=$1; out=$2; f=$3
mapfile -t specs < <(grep -v '^\s*$' "$f")
echo "${#specs[@]} specs from $f"
exec bash diag/adapter_pod.sh "$rate" "$out" "${specs[@]}"
