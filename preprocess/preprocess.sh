#!/usr/bin/env bash
set -euo pipefail

INPUT="$1"
OUTPUT="$2"
LAYER="$3"

# ensure files and folders exist
stat "$INPUT" >/dev/null
mkdir -p "$(dirname "$OUTPUT")" > /dev/null

SCRIPT_DIR="$(realpath "$(dirname "$0")")"

STEP_0="preprocess-0-input.svg"
STEP_1="preprocess-1-convert-to-path.svg"
STEP_2="preprocess-2-postscript-path.svg"
STEP_3="preprocess-3-remove-transforms.svg"

cp "$INPUT" "$STEP_0"
inkscape \
  --export-id="$LAYER" \
  --export-id-only \
  --export-area-page \
  --export-text-to-path \
  --export-ignore-filters \
  "$STEP_0" \
  -o "$STEP_1"
stat "$STEP_1" > /dev/null
cairosvg \
  -f svg \
  --output-width 210 \
  --output-height 297 \
  --dpi 72 \
  "$STEP_1" \
  -o "$STEP_2"
stat "$STEP_2" > /dev/null
"$SCRIPT_DIR/node_modules/svgo/bin/svgo" \
  --config "$SCRIPT_DIR/svgo.config.mjs" \
  "$STEP_2" \
  -o "$STEP_3"
stat "$STEP_3" > /dev/null
cp "$STEP_3" "$OUTPUT"
