#!/usr/bin/env bash
set -euo pipefail

INPUT="$(realpath "$1")"
SCAN="$(realpath "$2")"

# ensure files and folders exist
stat "$INPUT" >/dev/null
stat "$SCAN" >/dev/null

PREPROCESS="$(realpath "preprocess/preprocess.sh")"
SVG_TO_JSON="$(realpath "svg_to_json/main.py")"
JSON_TO_FCM="$(realpath "json_to_fcm/target/release/fcm-converter")"
WORKDIR="/tmp/svgalign-$(uuidgen)"
mkdir "$WORKDIR"

(cd align; pipenv run python main.py "$INPUT" "$SCAN" "$WORKDIR/align.svg")
cd "$WORKDIR"

("$PREPROCESS" align.svg preprocess-output.svg cut && \
  "$SVG_TO_JSON" preprocess-output.svg preprocess-output.json && \
  "$JSON_TO_FCM" preprocess-output.json "$(dirname "$INPUT")/$(basename "$INPUT" .svg)_cut.fcm") || true
if [ -z "$FCM_DEBUG_PATH" ]; then
  rm "$WORKDIR"/preprocess-* || true
fi

("$PREPROCESS" align.svg preprocess-output.svg cut_kiss && \
  "$SVG_TO_JSON" preprocess-output.svg preprocess-output.json && \
  "$JSON_TO_FCM" preprocess-output.json "$(dirname "$INPUT")/$(basename "$INPUT" .svg)_cut_kiss.fcm") || true
if [ -z "$FCM_DEBUG_PATH" ]; then
  rm "$WORKDIR"/preprocess-* || true
fi

("$PREPROCESS" align.svg preprocess-output.svg cut_die && \
  "$SVG_TO_JSON" preprocess-output.svg preprocess-output.json && \
  "$JSON_TO_FCM" preprocess-output.json "$(dirname "$INPUT")/$(basename "$INPUT" .svg)_cut_die.fcm") || true
if [ -z "$FCM_DEBUG_PATH" ]; then
  rm "$WORKDIR"/preprocess-* || true
  rm "$WORKDIR/align.svg"
fi
rmdir "$WORKDIR"
