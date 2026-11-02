#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
"""Join slide images into one PDF for a LinkedIn document post.

    python3 scripts/slides_to_pdf.py <folder or images...> -o export/<slug>.pdf

Pages are ordered by file name (name exports 01.png, 02.png, ...). LinkedIn needs every
page the same size, so images that differ from the first are fitted onto a canvas of
the first page's size, centred, on the first page's corner colour. Needs Pillow; run
without -I if Pillow lives in user site-packages.
"""
import argparse
import os
import re
import sys

from PIL import Image

EXT = (".png", ".jpg", ".jpeg", ".webp")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("inputs", nargs="+")
    ap.add_argument("-o", "--out", required=True)
    a = ap.parse_args()
    files = []
    natural = lambda f: [int(t) if t.isdigit() else t.lower() for t in re.split(r"(\d+)", os.path.basename(f))]
    for p in a.inputs:
        if os.path.isdir(p):
            files += sorted((os.path.join(p, f) for f in os.listdir(p) if f.lower().endswith(EXT)), key=natural)
        elif os.path.isfile(p):
            files.append(p)
        else:
            print(f"not found: {p}", file=sys.stderr)
            return 2
    if not files:
        print("no images found", file=sys.stderr)
        return 2
    def flat(f):  # transparent areas become white, not black
        im = Image.open(f)
        if im.mode in ("RGBA", "LA", "P"):
            im = im.convert("RGBA")
            bg = Image.new("RGB", im.size, (255, 255, 255))
            bg.paste(im, mask=im.split()[-1])
            return bg
        return im.convert("RGB")

    pages = [flat(f) for f in files]
    w, h = pages[0].size
    fixed = []
    for f, im in zip(files, pages):
        if im.size != (w, h):
            canvas = Image.new("RGB", (w, h), pages[0].getpixel((0, 0)))
            im.thumbnail((w, h))
            canvas.paste(im, ((w - im.width) // 2, (h - im.height) // 2))
            print(f"fitted {os.path.basename(f)} {im.size} into {w}x{h}")
            im = canvas
        fixed.append(im)
    os.makedirs(os.path.dirname(os.path.abspath(a.out)), exist_ok=True)
    fixed[0].save(a.out, save_all=True, append_images=fixed[1:], resolution=72)
    print(f"{a.out}: {len(fixed)} pages, {w}x{h}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
