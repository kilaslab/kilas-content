#!/usr/bin/env bash
# SPDX-License-Identifier: GPL-3.0-or-later
# Generate carousel images with the Antigravity CLI (agy) and its generate_image tool.
#
# The technique (three silent failure traps) comes from github.com/dyrok/imagine-agy;
# this is a small reimplementation so the skill does not need that npm package, which
# also edits ~/.claude/settings.json on install.
#
#   1. Print mode cannot ask for tool approval, so agy denies generate_image and writes
#      nothing. Needs --dangerously-skip-permissions (kept inside --sandbox here).
#   2. agy ignores the shell's working directory: relative paths land in
#      ~/.gemini/antigravity-cli/scratch/. Pass --add-dir <abs dir> AND absolute paths
#      in the prompt.
#   3. Claude Code's Bash classifier may block `agy` until `Bash(agy:*)` is allowed.
#
# Usage:
#   scripts/agy_image.sh <outdir> <ratio> "<shared style>" "<subject 1>" ["<subject 2>" ...]
#   ratio: 1:1 | 3:4 | 4:3 | 9:16 | 16:9
# All subjects go in ONE agy run with one shared style sentence, so the set comes out
# coherent. Expect 30-60 s per image. Output is always JPEG, at most ~1376 px on the
# long side. Exit 3 means agy is unavailable: fall back to Unsplash.
#
# Env: AGY_BIN (path to agy), AGY_MODEL (driver model, default gemini-3.8-flash-low;
# the driver only calls the tool, image quality does not depend on it).
set -euo pipefail

[ $# -ge 4 ] || { sed -n '2,25p' "$0"; exit 2; }

AGY="${AGY_BIN:-$(command -v agy || true)}"
[ -n "$AGY" ] || AGY="$HOME/.local/bin/agy"
[ -x "$AGY" ] || { echo "agy not found (install Antigravity CLI or set AGY_BIN). Use Unsplash instead." >&2; exit 3; }

mkdir -p "$1"
out="$(cd "$1" && pwd)"
ratio="$2"; style="$3"; shift 3
model="${AGY_MODEL:-gemini-3.8-flash-low}"

case "$ratio" in
  1:1)  words="1:1 square" ;;
  3:4)  words="3:4 vertical portrait" ;;
  4:3)  words="4:3 landscape" ;;
  9:16) words="9:16 vertical portrait" ;;
  16:9) words="16:9 widescreen" ;;
  *) echo "ratio must be 1:1, 3:4, 4:3, 9:16 or 16:9" >&2; exit 2 ;;
esac

stamp="$(date +%H%M%S)"
list=""; paths=()
i=1
for subject in "$@"; do
  p="$out/gen-$stamp-$i.jpg"
  paths+=("$p")
  list+="$i. Save to exactly this absolute path: $p
   Subject: $subject
"
  i=$((i+1))
done

prompt="Use the generate_image tool to create ${#paths[@]} image(s). Do not write code, do not run shell commands; only call generate_image.
Shared style for every image: $style
Aspect ratio for every image: $words ($ratio).
Every image: no text, no letters, no numbers, no watermark, no signature, no logos.
$list
When done, reply with the saved paths only."

echo "agy: ${#paths[@]} image(s), ratio $ratio, driver $model -> $out" >&2
"$AGY" -p "$prompt" --add-dir "$out" --dangerously-skip-permissions --sandbox \
  --model "$model" --print-timeout 12m >&2 || echo "agy exited non-zero; checking files anyway" >&2

missing=0
for p in "${paths[@]}"; do
  if [ ! -s "$p" ]; then
    # trap 2: look for it in agy's scratch dir
    alt="$(find "$HOME/.gemini/antigravity-cli/scratch" -name "$(basename "$p")" -newer "$0" 2>/dev/null | head -1 || true)"
    if [ -n "$alt" ]; then cp "$alt" "$p"; echo "recovered from scratch: $alt" >&2; fi
  fi
  if [ -s "$p" ]; then
    dims="$(sips -g pixelWidth -g pixelHeight "$p" 2>/dev/null | awk '/pixel/{printf "%s ", $2}')"
    echo "$p  ${dims}"
  else
    echo "MISSING $p" >&2; missing=1
  fi
done
exit $missing
