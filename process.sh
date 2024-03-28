#!/usr/bin/env bash
set -euo pipefail

INPUT="$(realpath "$1")"
SCAN="$(realpath "$2")"

# ensure files and folders exist
stat "$INPUT" >/dev/null
stat "$SCAN" >/dev/null

PREPROCESS="$(realpath "preprocess/preprocess.sh")"
WORKDIR="/tmp/svgalign-$(uuidgen)"
mkdir "$WORKDIR"

(cd align; pipenv run python main.py "$INPUT" "$SCAN" "$WORKDIR/align.svg")
cd "$WORKDIR"
"$PREPROCESS" "align.svg" "$(dirname "$INPUT")/$(basename "$INPUT" .svg)_cut_kiss.svg" "cut_kiss" || true
#rm "$WORKDIR"/preprocess-*.svg || true
#"$PREPROCESS" "align.svg" "$(dirname "$INPUT")/$(basename "$INPUT" .svg)_cut_die.svg" "cut_die" || true
#rm "$WORKDIR"/preprocess-*.svg || true
#rm "$WORKDIR/align.svg"
#rmdir "$WORKDIR"
