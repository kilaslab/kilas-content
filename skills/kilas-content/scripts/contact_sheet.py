#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
"""Build a labelled contact sheet from a directory of images.

Pick carousel photos by looking at the whole set at once instead of opening
files one by one.

    python3 scripts/contact_sheet.py content/items/<item>/photos -o contact.jpg --cols 5 --cell 240
"""
import argparse
import glob
import os

from PIL import Image, ImageDraw


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("directory")
    ap.add_argument("-o", "--out", default="contact.jpg")
    ap.add_argument("--cols", type=int, default=5)
    ap.add_argument("--cell", type=int, default=240)
    ap.add_argument("--exclude", default="contact")
    args = ap.parse_args()

    files = sorted(
        f for f in glob.glob(os.path.join(args.directory, "*"))
        if os.path.splitext(f)[1].lower() in {".jpg", ".jpeg", ".png", ".webp"}
        and args.exclude not in os.path.basename(f)
    )
    if not files:
        raise SystemExit(f"no images in {args.directory}")

    cell = args.cell
    rows = (len(files) + args.cols - 1) // args.cols
    sheet = Image.new("RGB", (args.cols * cell, rows * (cell + 20)), "white")
    draw = ImageDraw.Draw(sheet)

    for i, path in enumerate(files):
        im = Image.open(path).convert("RGB")
        w, h = im.size
        scale = max(cell / w, cell / h)
        im = im.resize((int(w * scale), int(h * scale)))
        left, top = (im.width - cell) // 2, (im.height - cell) // 2
        im = im.crop((left, top, left + cell, top + cell))
        x, y = (i % args.cols) * cell, (i // args.cols) * (cell + 20)
        sheet.paste(im, (x, y))
        draw.text((x + 4, y + cell + 3), os.path.splitext(os.path.basename(path))[0], fill="black")

    sheet.save(args.out, quality=82)
    print(f"{len(files)} images -> {args.out} {sheet.size}")


if __name__ == "__main__":
    main()
