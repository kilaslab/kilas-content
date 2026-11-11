#!/usr/bin/env bash
# SPDX-License-Identifier: GPL-3.0-or-later
# Start a 3D explainer scene for a Reel from templates/video3d (references/motion-video.md 2e,
# worked example references/examples/reels-3d-explainer.md).
#
#   scripts/new_scene3d.sh <item> [brand-logo.svg]
#   scripts/new_scene3d.sh content/items/2026-11-16-explainer content/brand/assets/logos/logo.svg
#
# Writes <item>/scene/: index.html (dev page), scene.js, beats.js, mascot.js, style.css,
# mascot-test.html, lib/ (three.js r178 from jsDelivr), img/logo.svg (the logo given, else the
# first SVG in content/brand/assets/logos/). Fails if <item>/scene exists.
# Then: edit beats.js (words and times) and the props in scene.js; serve the folder and look.
set -euo pipefail
[ $# -ge 1 ] || { sed -n '3,12p' "$0"; exit 2; }
item="$1"; logo="${2:-}"
skill="$(cd "$(dirname "$0")/.." && pwd)"
dest="$item/scene"
[ -d "$item" ] || { echo "no item folder: $item (scripts/new_item.py makes one)" >&2; exit 1; }
[ ! -e "$dest" ] || { echo "$dest exists; edit it or move it away" >&2; exit 1; }

cp -R "$skill/templates/video3d" "$dest"
mkdir -p "$dest/lib" "$dest/img"
for f in three.module.js three.core.js; do
  curl -fsSL "https://cdn.jsdelivr.net/npm/three@0.178.0/build/$f" -o "$dest/lib/$f" \
    || { echo "download failed: three@0.178.0/build/$f (copy it into $dest/lib/ by hand)" >&2; exit 1; }
done
grep -q "REVISION = '178'" "$dest/lib/three.core.js" || { echo "lib/three.core.js is not r178" >&2; exit 1; }

if [ -z "$logo" ]; then
  logo="$(ls content/brand/assets/logos/*.svg 2>/dev/null | head -1 || true)"
fi
if [ -n "$logo" ] && [ -f "$logo" ]; then
  cp "$logo" "$dest/img/logo.svg"
else
  echo "warning: no logo found; put the brand's icon at $dest/img/logo.svg for the end card" >&2
fi

cat <<EOF
scene ready: $dest
next:
  1. beats.js: the story's words (COPY), the mascot's colours (MASCOT), the times (T)
  2. serve and look:   (cd $dest && python3 -m http.server 8792)
     live loop:        http://localhost:8792/index.html        (?from=10&to=25 loops a part)
     mascot poses:     SIZE=1440,900 bash $skill/scripts/scene_stills.sh "http://localhost:8792/mascot-test.html" $item/frames/pose 0.6
     story stills:     bash $skill/scripts/scene_stills.sh http://localhost:8792/index.html $item/frames/f 1.5 9.6 17 24 28 31.6 41 47 51 57.8
  3. after the voice-over: set VO_STARTS in beats.js, then
     python3 $skill/scripts/scene3d_video.py $dest $item/video --vo <vo dir>
EOF
