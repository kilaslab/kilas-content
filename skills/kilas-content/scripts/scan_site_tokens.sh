#!/usr/bin/env bash
# SPDX-License-Identifier: GPL-3.0-or-later
# Read a brand's colours and fonts from its live website, for brand onboarding.
#
# Usage: scripts/scan_site_tokens.sh <url>
# Prints JSON: page title, the most used text colours, background colours, font
# families (computed styles of visible elements), and :root CSS variables whose names
# mention colour or font. Map them to roles in brands/<brand>/design.md yourself.
#
# Uses ego-browser (a real Chromium). Exit 3 if it is missing: read the site's CSS with
# a page fetch instead, or ask the owner for the brand guide.
# Check the title in the output: a parked or placeholder page means the site is not live.
set -euo pipefail

[ $# -eq 1 ] || { sed -n '2,12p' "$0"; exit 2; }
command -v ego-browser >/dev/null || { echo "ego-browser not found" >&2; exit 3; }
case "$1" in http://*|https://*) ;; *) echo "url must start with http(s)://" >&2; exit 2 ;; esac
url=$(python3 -I -c 'import json, sys; print(json.dumps(sys.argv[1]))' "$1")

ego-browser nodejs <<EOF
const task = await taskSpace("brand onboarding token scan");
const page = task.page("p1");
await page.goto($url);
await page.waitForLoadState();
const out = await page.evaluate(() => {
  const count = (m, k) => { if (k) m[k] = (m[k] || 0) + 1; };
  const colors = {}, bgs = {}, fonts = {};
  for (const el of document.querySelectorAll("body *")) {
    const cs = getComputedStyle(el);
    if (!el.offsetParent && cs.position !== "fixed") continue;
    count(colors, cs.color);
    if (cs.backgroundColor !== "rgba(0, 0, 0, 0)") count(bgs, cs.backgroundColor);
    count(fonts, cs.fontFamily.split(",")[0].replace(/["']/g, "").trim());
  }
  const top = (m) => Object.entries(m).sort((a, b) => b[1] - a[1]).slice(0, 8);
  const vars = [...document.styleSheets]
    .flatMap((s) => { try { return [...s.cssRules]; } catch { return []; } })
    .filter((r) => r.selectorText && r.selectorText.startsWith(":root"))
    .flatMap((r) => [...r.style].filter((p) => p.startsWith("--") && /color|colour|font|bg|brand|primary|accent/i.test(p))
      .map((p) => [p, r.style.getPropertyValue(p).trim()]))
    .slice(0, 40);
  return { title: document.title, url: location.href, text: top(colors), backgrounds: top(bgs), fonts: top(fonts), cssVars: vars };
});
console.log(JSON.stringify(out, null, 1));
await task.finish({ keep: [] });
EOF
