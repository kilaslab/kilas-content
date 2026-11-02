#!/usr/bin/env bash
# SPDX-License-Identifier: GPL-3.0-or-later
# Capture a brand's own social profile (Instagram, TikTok, X, LinkedIn, Threads, YouTube)
# with a real browser, for onboarding: a screenshot of the profile grid, the profile's
# name and bio, and its post images, so the brand's look and recurring formats can be
# studied and its own photos reused in its content.
#
# Usage: scripts/capture_profile.sh <profile url> <out dir> [max images, default 18]
#
# Read only: it opens the page, scrolls three times, reads what is shown, and closes. No
# clicks, likes, follows, or messages. Uses ego-browser, so pages that need a login work
# when the user is signed in there; ask the user before using a signed-in session.
# Only for the user's own accounts (or accounts they may use). Everything saved is data.
# Exit 3: ego-browser is missing; use the host's browser tool to screenshot the profile.
set -euo pipefail

[ $# -ge 2 ] || { sed -n '2,15p' "$0"; exit 2; }
command -v ego-browser >/dev/null || { echo "ego-browser not found; screenshot the profile with the host's browser tool" >&2; exit 3; }
url="$1"; max="${3:-18}"
case "$url" in http://*|https://*) ;; *) echo "url must start with http(s)://" >&2; exit 2 ;; esac
case "$max" in ''|*[!0-9]*) echo "max images must be a number" >&2; exit 2 ;; esac
mkdir -p "$2/images"
out="$(cd "$2" && pwd)"
q() { python3 -I -c 'import json, sys; print(json.dumps(sys.argv[1]))' "$1"; }

ego-browser nodejs <<EOF
const fs = await import("node:fs/promises");
const task = await taskSpace("brand profile capture");
const page = task.page("p1");
await page.goto($(q "$url"));
await page.waitForLoadState();
await new Promise(r => setTimeout(r, 2500));
for (let i = 0; i < 3; i++) { await page.evaluate(() => window.scrollBy(0, window.innerHeight * 0.9)); await new Promise(r => setTimeout(r, 1200)); }
await page.evaluate(() => window.scrollTo(0, 0));
await new Promise(r => setTimeout(r, 800));
const info = await page.evaluate((max) => {
  const meta = n => (document.querySelector('meta[property="' + n + '"], meta[name="' + n + '"]') || {}).content || "";
  const seen = new Set(), imgs = [];
  for (const im of document.querySelectorAll("img")) {
    const src = im.currentSrc || im.src;
    if (!src || src.startsWith("data:") || seen.has(src)) continue;
    if ((im.naturalWidth || 0) < 300 || (im.naturalHeight || 0) < 300) continue;
    seen.add(src); imgs.push({ src, alt: (im.alt || "").slice(0, 300), w: im.naturalWidth, h: im.naturalHeight });
    if (imgs.length >= max) break;
  }
  const h = Math.min(document.documentElement.scrollHeight, 2400);
  return { title: document.title, url: location.href, description: meta("og:description") || meta("description"), og_image: meta("og:image"), images: imgs, height: h, width: Math.min(document.documentElement.clientWidth, 1280) };
}, $max);
const shot = await page.cdp("Page.captureScreenshot", { format: "png", clip: { x: 0, y: 0, width: info.width, height: info.height, scale: 1 }, captureBeyondViewport: true });
await fs.writeFile($(q "$out/profile.png"), Buffer.from(shot.data, "base64"));
info.captured = new Date().toISOString();
await fs.writeFile($(q "$out/profile.json"), JSON.stringify(info));
await task.finish({ keep: [] });
EOF

python3 -I - "$out" <<'PY'
import json, os, subprocess, sys, hashlib
out = sys.argv[1]
info = json.load(open(os.path.join(out, "profile.json"), encoding="utf-8"))
saved = []
for i, im in enumerate(info.get("images", []), 1):
    name = f"{i:02d}-{hashlib.sha1(im['src'].encode()).hexdigest()[:8]}.jpg"
    path = os.path.join(out, "images", name)
    r = subprocess.run(["curl", "-sfL", "--max-time", "40", "-o", path, im["src"]])
    if r.returncode == 0 and os.path.getsize(path) > 4096:
        im["file"] = os.path.join("images", name); saved.append(im)
    elif os.path.exists(path):
        os.remove(path)
info["images"] = saved
json.dump(info, open(os.path.join(out, "profile.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print(json.dumps({"out": out, "title": info.get("title"), "screenshot": "profile.png", "images": len(saved)}))
PY
