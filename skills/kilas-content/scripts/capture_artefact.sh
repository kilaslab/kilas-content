#!/usr/bin/env bash
# SPDX-License-Identifier: GPL-3.0-or-later
# Capture part of a web page as a sharp PNG for an evidence slide (a "real artefact").
#
# Usage:
#   scripts/capture_artefact.sh <url> <out.png> [css selector] [max height in css px]
#   selector defaults to "article" (then "main", then the page body); height to 700.
#
# Uses ego-browser, a real Chromium: it passed the Cloudflare check on phoronix.com
# that blocks headless Playwright ("Just a moment...", HTTP 403). Output is 2x the CSS
# size (a 745 px wide article becomes 1490 px), padded 16 px so edge glyphs survive.
# Exit 3: ego-browser is missing. Use the host's own browser tool, or skip the artefact.
#
# Only capture public pages. Never alter the image afterwards; crop by choosing the
# selector and height instead.
set -euo pipefail

[ $# -ge 2 ] || { sed -n '2,14p' "$0"; exit 2; }
command -v ego-browser >/dev/null || { echo "ego-browser not found; use the host's browser tool or skip the artefact" >&2; exit 3; }

url="$1"; sel="${3:-article}"; maxh="${4:-700}"
case "$url" in http://*|https://*) ;; *) echo "url must start with http(s)://" >&2; exit 2 ;; esac
case "$maxh" in ''|*[!0-9]*) echo "max height must be a number" >&2; exit 2 ;; esac
maxh=$((10#$maxh))   # 0300 and 09 are decimal, not octal or a JS syntax error
mkdir -p "$(dirname "$2")"
out="$(cd "$(dirname "$2")" && pwd)/$(basename "$2")"

# JSON-encode every value that goes into the script, so a URL or selector cannot break out.
q() { python3 -I -c 'import json, sys; print(json.dumps(sys.argv[1]))' "$1"; }

ego-browser nodejs <<EOF
const fs = await import("node:fs/promises");
const task = await taskSpace("content artefact capture");
const page = task.page("p1");
await page.goto($(q "$url"));
await page.waitForLoadState();
const clip = await page.evaluate(({ sel, maxh }) => {
  const el = document.querySelector(sel) || document.querySelector("main") || document.body;
  const r = el.getBoundingClientRect(), pad = 16;
  return {
    x: Math.max(0, r.left + window.scrollX - pad),
    y: Math.max(0, r.top + window.scrollY - pad),
    width: Math.min(r.width + 2 * pad, 1100),
    height: Math.min(r.height + 2 * pad, maxh),
    scale: 2 / (window.devicePixelRatio || 1),
  };
}, { sel: $(q "$sel"), maxh: $maxh });
const shot = await page.cdp("Page.captureScreenshot", { format: "png", clip, captureBeyondViewport: true });
await fs.writeFile($(q "$out"), Buffer.from(shot.data, "base64"));
console.log(JSON.stringify({ out: $(q "$out"), title: await page.title(), url: await page.url(), captured: new Date().toISOString() }));
await task.finish({ keep: [] });
EOF
