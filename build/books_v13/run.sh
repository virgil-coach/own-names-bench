#!/bin/bash
# The v1.3 audiobook test suite (books13), end to end. Each script documents itself.
#   here (light):            excl.py, find_books.py, rank_books.py, manifest.py
#   a Mac with MPS (heavy):  align_book.py (the only model: the forced aligner); calib.py on a dev book (bookdev Phantastes)
#   here (light):            curate.py, build.py, check.py, seal.py
# Refuses to run once the suite is sealed.
set -euo pipefail
cd "$(dirname "$0")"
ROOT=${BOOKS13_ROOT:-$HOME/workspace/jl/onb-v13-books-SEALED}
[ -e "$ROOT/SEALED.txt" ] && { echo "sealed: $(head -1 "$ROOT/SEALED.txt")"; exit 1; }
PY="uv run --frozen python"
case "${1:-}" in
  select) $PY excl.py && $PY find_books.py && $PY rank_books.py && $PY manifest.py ;;
  align)  # on the Mac mini: BOOKS13_ROOT=~/workroots/books13 (books.json and texts/ copied there), results copied back
          $PY align_book.py ;;
  build)  $PY curate.py && $PY build.py && $PY check.py ;;
  seal)   $PY seal.py ;;
  *) echo "usage: run.sh select | align | build | seal"; exit 2 ;;
esac
