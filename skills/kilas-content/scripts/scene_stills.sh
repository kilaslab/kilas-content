#!/usr/bin/env bash
# SPDX-License-Identifier: GPL-3.0-or-later
# Stills from a live scene page that renders a given time from its URL (?t=12.5), for a
# Reels beat map or animatic (references/motion-video.md 2e). Headless Chrome with
# SwiftShader, so WebGL (three.js) works without a GPU. Writes <prefix>NN.png and a sheet.
#
#   scripts/scene_stills.sh <page url> <out prefix> [times...]
#   scripts/scene_stills.sh http://localhost:8791/index.html frames/f              # 2.5, 7.5, ... 57.5
#   scripts/scene_stills.sh http://localhost:8791/index.html frames/a 0.5 1.5 2.5  # first seconds
# Still NN is the NN-th time given (frames/a01.png is 0.5 s above); the prefix may be relative
# or absolute.
#
# Serve the scene folder first (python3 -m http.server <port>): module imports fail from
# file://, and a port already in use serves someone else's folder, so check the page title.
# Env: SIZE=1080,1920 (window), BUDGET=4000 (virtual ms to settle), DUR=60 (default times),
#      TIMEOUT=60 (seconds before a hung still is stopped), JOBS=4 (stills taken at once).
set -euo pipefail
[ $# -ge 2 ] || { sed -n '3,16p' "$0"; exit 2; }
url="$1"; pfx="$2"; shift 2
CH="${CHROME:-/Applications/Google Chrome.app/Contents/MacOS/Google Chrome}"
command -v google-chrome >/dev/null 2>&1 && [ ! -x "$CH" ] && CH="$(command -v google-chrome)"
[ -x "$CH" ] || { echo "Chrome not found; set CHROME=/path/to/chrome" >&2; exit 3; }
if [ $# -eq 0 ]; then
  set -- $(python3 -c "print(' '.join(str(i*5+2.5) for i in range(int(${DUR:-60})//5)))")
fi
# Chrome writes where --screenshot says, relative to its own cwd: make the prefix absolute
case "$pfx" in /*) ;; *) pfx="$PWD/$pfx" ;; esac
mkdir -p "$(dirname "$pfx")"
sep='?'; case "$url" in *\?*) sep='&' ;; esac
# JOBS stills at a time: twenty headless Chromes at once starve each other and some write
# nothing (a 24-still animatic lost a third of its frames, Nov 2026). A still that is missing
# after its batch is taken once more on its own.
shoot() { # <index> <time>
  "$CH" --headless=new --use-angle=swiftshader --enable-unsafe-swiftshader --hide-scrollbars \
    --window-size="${SIZE:-1080,1920}" --virtual-time-budget="${BUDGET:-4000}" \
    --screenshot="$pfx$(printf %02d "$1").png" "$url${sep}t=$2" >/dev/null 2>&1 &
}
batch() { # waits for the stills started since the last call, stopping any that hang
  [ -n "$pids" ] || return 0
  ( sleep "${TIMEOUT:-60}"; kill $pids 2>/dev/null ) & dog=$!
  wait $pids 2>/dev/null || true
  kill $dog 2>/dev/null; wait $dog 2>/dev/null || true
  pids=""
}
i=0; pids=""; n=0
for t in "$@"; do
  i=$((i+1)); rm -f "$pfx$(printf %02d $i).png"
  shoot $i "$t"; pids="$pids $!"; n=$((n+1))
  [ $n -lt "${JOBS:-4}" ] || { batch; n=0; }
done
batch
k=0
for t in "$@"; do
  k=$((k+1))
  [ -s "$pfx$(printf %02d $k).png" ] && continue
  shoot $k "$t"; pids="$!"; batch
  [ -s "$pfx$(printf %02d $k).png" ] || echo "missing still $k (t=$t) after a second try: open $url${sep}t=$t in a browser and read its console" >&2
done
python3 - "$pfx" <<'PY'
import glob, sys
from PIL import Image
fs = sorted(glob.glob(sys.argv[1] + "[0-9][0-9].png"))
if not fs: sys.exit("no stills written; check the url and that the page renders ?t=")
cols = min(6, len(fs)); rows = (len(fs) + cols - 1) // cols
im = [Image.open(f).convert("RGB").resize((270, 480)) for f in fs]
sheet = Image.new("RGB", (270 * cols, 480 * rows), "white")
for k, a in enumerate(im): sheet.paste(a, ((k % cols) * 270, (k // cols) * 480))
sheet.save(sys.argv[1] + "sheet.jpg", quality=85)
print(f"{len(fs)} stills, sheet: {sys.argv[1]}sheet.jpg")
PY
