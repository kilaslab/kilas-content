#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
"""Turn a scraped carousel dataset into reference sheets an agent can look at.

    python3 scripts/ref_sheets.py <posts.jsonl> <out dir> [--images DIR] [--thumb 220]

posts.jsonl: one post per line with 'account', 'shortcode', 'date_wib', 'slide_count',
'likes_comments_raw', 'caption_abridged', 'collab', and 'slides' [{'n', 'image'}], where
'image' is relative to --images (default: the folder of posts.jsonl). This is the format
of the Instagram part of the tech-carousel dataset.

Writes one JPEG per account (every carousel as a row: a label, then its slides) and
index.md listing each post with its date, slide count, engagement snapshot, and a short
caption, so the sheets can be read with their context. Accounts annotated like
"name (collab, posted by x)" are grouped under "name".

The sheets are screenshots of other accounts' posts: keep them in a private brand pack
(brands/<brand>/refs/), never in the core skill or an open-source export. Use them to
study layout and pacing, never to copy a design. Needs Pillow (run without -I if Pillow
lives in user site-packages).
"""
import argparse
import json
import os
import re
import sys

from PIL import Image, ImageDraw, ImageFont

FONTS = ["/System/Library/Fonts/Supplemental/Arial.ttf", "/System/Library/Fonts/Helvetica.ttc",
         "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", "C:/Windows/Fonts/arial.ttf"]


def font(size):
    for p in FONTS:
        if os.path.exists(p):
            try:
                return ImageFont.truetype(p, size)
            except OSError:
                pass
    return ImageFont.load_default()


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("posts")
    ap.add_argument("out")
    ap.add_argument("--images")
    ap.add_argument("--thumb", type=int, default=220, help="thumbnail height in px")
    a = ap.parse_args()

    base = a.images or os.path.dirname(os.path.abspath(a.posts))
    posts = [json.loads(l) for l in open(a.posts, encoding="utf-8") if l.strip()]
    groups = {}
    for p in posts:
        acc = re.sub(r"\s*\(.*\)$", "", p.get("account", "?")).strip()
        groups.setdefault(acc, []).append(p)
    os.makedirs(a.out, exist_ok=True)
    f_label, f_small = font(22), font(16)
    index = ["# Reference sheets", "", f"Generated from `{os.path.basename(a.posts)}`: {len(posts)} posts, {len(groups)} accounts.",
             "Snapshots of engagement are raw strings from the scrape; compare only within one account.", ""]
    for acc, items in sorted(groups.items()):
        items.sort(key=lambda p: p.get("date_wib") or "", reverse=True)
        rows = []
        for p in items:
            thumbs = []
            for s in p.get("slides", []):
                path = os.path.join(base, s.get("image") or "")
                if s.get("image") and os.path.exists(path):
                    im = Image.open(path).convert("RGB")
                    im.thumbnail((int(a.thumb * 0.9), a.thumb))
                    thumbs.append(im)
            if thumbs:
                rows.append((p, thumbs))
        if not rows:
            continue
        width = max(sum(t.width + 8 for t in th) for _, th in rows) + 24
        height = sum(max(t.height for t in th) + 58 for _, th in rows) + 16
        sheet = Image.new("RGB", (max(width, 900), height), (246, 246, 242))
        d = ImageDraw.Draw(sheet)
        y = 12
        for p, th in rows:
            collab = " · collab" if p.get("collab") or "collab" in p.get("account", "") else ""
            label = f"{p.get('shortcode', '?')} · {p.get('date_wib') or 'tanpa tanggal'} · {p.get('slide_count', len(th))} slide{collab}"
            d.text((12, y), label, fill=(17, 17, 17), font=f_label)
            d.text((12, y + 26), (p.get("likes_comments_raw") or "")[:110], fill=(110, 110, 105), font=f_small)
            y += 50
            x = 12
            for t in th:
                sheet.paste(t, (x, y))
                x += t.width + 8
            y += max(t.height for t in th) + 8
        name = "ig-" + re.sub(r"[^a-z0-9]+", "-", acc.lower()).strip("-") + ".jpg"
        sheet.save(os.path.join(a.out, name), quality=82, optimize=True)
        index += [f"## {acc}", "", f"`{name}`, {len(rows)} carousels, newest first.", "",
                  "| Post | Date | Slides | Engagement (raw) | Caption, abridged |", "|---|---|---|---|---|"]
        for p, th in rows:
            cap = (p.get("caption_abridged") or "").replace("|", "/").replace("\n", " ")
            cap = cap[:140] + ("…" if len(cap) > 140 else "")
            eng = (p.get("likes_comments_raw") or "").replace("|", "/")[:60]
            index.append(f"| [{p.get('shortcode')}]({p.get('url', '')}) | {p.get('date_wib') or '-'} | {p.get('slide_count', len(th))} | {eng} | {cap} |")
        index.append("")
        print(f"{name}: {len(rows)} carousels, {sheet.size[0]}x{sheet.size[1]}")
    with open(os.path.join(a.out, "index.md"), "w", encoding="utf-8") as f:
        f.write("\n".join(index))
    return 0


if __name__ == "__main__":
    sys.exit(main())
