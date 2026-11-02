#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
"""Render slides.html (templates/html kit) to one PNG per slide, and report layout issues.

    python3 scripts/render_slides.py content/items/<item>/html/slides.html -o content/items/<item>/export
    python3 scripts/render_slides.py slides.html -o out --scale 2 --scheme kertas
    python3 scripts/render_slides.py slides.html -o out --issues-only

Uses Python Playwright when it is installed (pip install playwright; playwright install
chromium), otherwise a Chrome, Chromium, Edge, or Brave binary in headless mode (found
on PATH, in the usual app folders, in Playwright's browser cache, or from $CHROME).
Writes 01.png, 02.png, ... at 1080×1350 × --scale, and prints the issues kit.js found
(text past the margins or into the footer, slides that end high, small type, a cover with
no visual, a long run of plain slides). Exit 1 when issues were found, 3 when no browser
is available. Fonts load from Google Fonts, so rendering needs the network.
"""
import argparse
import glob
import html
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import urllib.parse

W, H = 1080, 1350


def find_chrome(explicit=None):
    cands = [explicit, os.environ.get("CHROME")]
    cands += [shutil.which(n) for n in ("google-chrome", "google-chrome-stable", "chromium", "chromium-browser", "microsoft-edge", "brave-browser", "chrome")]
    cands += ["/Applications/Google Chrome.app/Contents/MacOS/Google Chrome", "/Applications/Chromium.app/Contents/MacOS/Chromium",
              "/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge", "/Applications/Brave Browser.app/Contents/MacOS/Brave Browser",
              r"C:\Program Files\Google\Chrome\Application\chrome.exe", r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe"]
    for cache in (os.path.expanduser("~/Library/Caches/ms-playwright"), os.path.expanduser("~/.cache/ms-playwright")):
        cands += sorted(glob.glob(cache + "/chromium-*/chrome-*/*.app/Contents/MacOS/*"), reverse=True)
        cands += sorted(glob.glob(cache + "/chromium-*/chrome-linux*/chrome"), reverse=True)
    return next((c for c in cands if c and os.path.isfile(c) and os.access(c, os.X_OK)), None)


def url_for(path, **params):
    u = "file://" + urllib.parse.quote(os.path.abspath(path))
    qs = urllib.parse.urlencode({k: v for k, v in params.items() if v})
    return u + ("?" + qs if qs else "")


def with_playwright(src, out, scale, scheme, issues_only):
    from playwright.sync_api import sync_playwright  # noqa: import only when used
    with sync_playwright() as p:
        b = p.chromium.launch()
        pg = b.new_page(viewport={"width": W + 120, "height": H + 120}, device_scale_factor=scale)
        pg.goto(url_for(src, scheme=scheme))
        pg.wait_for_function("document.documentElement.dataset.ready === '1'", timeout=30000)
        issues = pg.evaluate("window.__issues || []")
        n = pg.locator("section.slide").count()
        files = []
        if not issues_only:
            for i in range(n):
                f = os.path.join(out, f"{i + 1:02d}.png")
                pg.locator("section.slide").nth(i).screenshot(path=f)
                files.append(f)
        b.close()
    return issues, files


def with_chrome(chrome, src, out, scale, scheme, issues_only):
    prof = tempfile.mkdtemp(prefix="render-slides-")
    base = [chrome, "--headless=new", "--disable-gpu", "--hide-scrollbars", "--no-first-run", "--no-default-browser-check",
            "--allow-file-access-from-files", f"--user-data-dir={prof}", "--virtual-time-budget=12000", "--run-all-compositor-stages-before-draw"]
    try:
        dom = subprocess.run(base + [f"--window-size={W + 120},{H + 120}", "--dump-dom", url_for(src, scheme=scheme)],
                             capture_output=True, text=True, timeout=120).stdout
        m = re.search(r'<pre id="kit-issues"[^>]*>(.*?)</pre>', dom, re.S)
        issues = json.loads(html.unescape(m.group(1))) if m else [{"issue": "kit.js did not finish (no #kit-issues); check the page in a browser"}]
        n = len(re.findall(r'<section[^>]*class="[^"]*\bslide\b', dom))
        files = []
        if not issues_only:
            for i in range(n):
                f = os.path.join(out, f"{i + 1:02d}.png")
                subprocess.run(base + [f"--window-size={W},{H}", f"--force-device-scale-factor={scale}", f"--screenshot={os.path.abspath(f)}",
                                       url_for(src, only=i + 1, scheme=scheme)], capture_output=True, timeout=120)
                if os.path.exists(f):
                    files.append(f)
        return issues, files
    finally:
        shutil.rmtree(prof, ignore_errors=True)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("html")
    ap.add_argument("-o", "--out", default=None, help="folder for the PNGs (default: export/ next to the html folder)")
    ap.add_argument("--scale", type=float, default=1, help="2 for 2160×2700 files")
    ap.add_argument("--scheme", help="render with another colour scheme of the brand")
    ap.add_argument("--browser", choices=["auto", "playwright", "chrome"], default="auto")
    ap.add_argument("--chrome", help="path to a Chrome/Chromium binary")
    ap.add_argument("--issues-only", action="store_true")
    a = ap.parse_args()
    out = a.out or os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(a.html))), "export")
    os.makedirs(out, exist_ok=True)
    use_pw = a.browser == "playwright"
    if a.browser == "auto":
        try:
            import playwright  # noqa: F401
            use_pw = True
        except ImportError:
            use_pw = False
    if use_pw:
        issues, files = with_playwright(a.html, out, a.scale, a.scheme, a.issues_only)
        engine = "playwright"
    else:
        chrome = find_chrome(a.chrome)
        if not chrome:
            print("no browser: install Playwright (pip install playwright && playwright install chromium) or Chrome, or pass --chrome", file=sys.stderr)
            return 3
        issues, files = with_chrome(chrome, a.html, out, a.scale, a.scheme, a.issues_only)
        engine = os.path.basename(chrome)
    print(f"{engine}: {len(files)} PNG in {out}" + (f" (scheme {a.scheme})" if a.scheme else ""))
    for i in issues:
        print("issue:", json.dumps(i, ensure_ascii=False))
    if not issues:
        print("layout: no issues")
    return 1 if issues else 0


if __name__ == "__main__":
    sys.exit(main())
