#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
"""Search Unsplash, keep free photos only, record credits, optionally download.

Reads the public search page (https://unsplash.com/s/photos/<query>). Two traps:

- Fetch with curl's default User-Agent. A browser ("Mozilla/...") UA gets an
  Anubis bot challenge, and Python's urllib is redirected to a 401.
- Results mix in Unsplash+ (plus.unsplash.com/premium_photo-*). Those are
  paid; this script skips them and keeps only images.unsplash.com/photo-*.

    python3 scripts/unsplash_search.py "dam spillway" "server rack" \
        --per 6 --out content/items/<item>/photos --download

Writes <out>/manifest.json with id, alt text, photographer, page URL and the
local file, so the close slide can credit photographers.
"""
import argparse
import html
import json
import os
import re
import subprocess
import urllib.parse

FIGURE = re.compile(r'<figure data-testid="asset-grid-list-figure".*?</figure>', re.S)
AUTHOR = re.compile(r'class="name-[^"]*"[^>]*href="/@([^"]+)"[^>]*>([^<]+)</a>')
PHOTO = re.compile(r'href="(/photos/[^"]+)"[^>]*>\s*<img alt="([^"]*)"[^>]*?src="https://images\.unsplash\.com/(photo-[A-Za-z0-9_-]+)\?[^"]*"[^>]*?width="(\d+)" height="(\d+)"', re.S)


def fetch(url: str) -> bytes:
    # curl's default UA gets the real page; Python's urllib is redirected to a 401
    # and a browser UA gets the Anubis challenge.
    return subprocess.run(
        ["curl", "-s", "-L", "--fail", "--max-time", "90", url],
        check=True, capture_output=True,
    ).stdout


def search(query: str, per: int) -> list[dict]:
    slug = urllib.parse.quote(query.strip().lower().replace(" ", "-"))
    page = fetch(f"https://unsplash.com/s/photos/{slug}").decode("utf-8", "ignore")
    if "anubis_challenge" in page:
        raise SystemExit("Unsplash returned a bot challenge; retry without a browser User-Agent")
    out = []
    for block in FIGURE.findall(page):
        if "plus.unsplash.com" in block or "premium_photo" in block:
            continue
        p, a = PHOTO.search(block), AUTHOR.search(block)
        if not p:
            continue
        href, alt, pid, w, h = p.groups()
        out.append({
            "query": query,
            "id": pid,
            "alt": html.unescape(alt),
            "author": html.unescape(a.group(2)) if a else "",
            "handle": a.group(1) if a else "",
            "page": "https://unsplash.com" + href,
            "width": int(w),
            "height": int(h),
            "orientation": "portrait" if int(h) > int(w) else "landscape",
        })
        if len(out) >= per:
            break
    return out


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("queries", nargs="+")
    ap.add_argument("--per", type=int, default=6)
    ap.add_argument("--out", default=".")
    ap.add_argument("--download", action="store_true")
    ap.add_argument("--width", type=int, default=1600, help="download width in px")
    args = ap.parse_args()

    os.makedirs(args.out, exist_ok=True)
    results = []
    for q in args.queries:
        found = search(q, args.per)
        print(f"== {q}: {len(found)} free photos")
        for i, item in enumerate(found, 1):
            stem = re.sub(r"[^a-z0-9]+", "-", q.lower()).strip("-") + f"-{i}"
            if args.download:
                item["file"] = os.path.join(args.out, stem + ".jpg")
                url = f"https://images.unsplash.com/{item['id']}?w={args.width}&q=80&fm=jpg&fit=crop"
                with open(item["file"], "wb") as fh:
                    fh.write(fetch(url))
            print(f"  {stem:28} {item['orientation']:9} {item['author'][:24]:24} {item['alt'][:70]}")
            results.append(item)

    # keep the credits of earlier searches in the same folder; a photo found again replaces its entry
    path = os.path.join(args.out, "manifest.json")
    old = []
    if os.path.exists(path):
        try:
            old = json.load(open(path, encoding="utf-8"))
        except ValueError:
            old = []
    ids = {r["id"] for r in results}
    results = [r for r in old if isinstance(r, dict) and r.get("id") not in ids] + results
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(results, fh, indent=2, ensure_ascii=False)
    print(f"\n{len(results)} photos -> {os.path.join(args.out, 'manifest.json')}")


if __name__ == "__main__":
    main()
