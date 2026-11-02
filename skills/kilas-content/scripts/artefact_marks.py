#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
"""Find highlighter coordinates in a screenshot, for artefact() marks in figma-helpers.js.

    python3 scripts/artefact_marks.py shot.png rows [--x 12]
        Row bands of a striped or bordered table, read down one pixel column (x).
        Prints [y0, y1] pairs to use as whole-row marks.
    python3 scripts/artefact_marks.py shot.png lines [--x0 0 --x1 W]
        Text line bands: rows of pixels with dark ink between x0 and x1.
    python3 scripts/artefact_marks.py shot.png words Y0 Y1 [--gap 9]
        Word boxes on the text line between Y0 and Y1. Pick the words of the phrase and
        use { x0: first word's x0, x1: last word's x1, y0, y1 } as a phrase mark.

All values are in the image's own pixels; artefact() scales them with the image. Needs
Pillow (run without -I if Pillow lives in user site-packages). The screenshot is only
read, never changed.
"""
import argparse
import json
import sys

from PIL import Image


def bands(flags, min_len=1, max_gap=0):
    """Runs of True in a list, as [start, end] pairs, merging gaps up to max_gap."""
    out, start, last = [], None, None
    for i, f in enumerate(flags):
        if f:
            if start is None:
                start = i
            elif i - last - 1 > max_gap:
                out.append([start, last])
                start = i
            last = i
    if start is not None:
        out.append([start, last])
    return [b for b in out if b[1] - b[0] + 1 >= min_len]


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("image")
    ap.add_argument("mode", choices=["rows", "lines", "words"])
    ap.add_argument("y", nargs="*", type=int, help="Y0 Y1 for words")
    ap.add_argument("--x", type=int, default=12, help="pixel column for rows (inside the table, left of the text)")
    ap.add_argument("--x0", type=int, default=0)
    ap.add_argument("--x1", type=int)
    ap.add_argument("--ink", type=int, default=140, help="grey level below which a pixel counts as ink")
    ap.add_argument("--gap", type=int, default=9, help="blank columns that separate two words")
    a = ap.parse_args()

    im = Image.open(a.image).convert("RGB")
    w, h = im.size
    grey = im.convert("L")
    out = {"image": a.image, "size": [w, h], "mode": a.mode}

    if a.mode == "rows":
        col = [im.getpixel((a.x, y)) for y in range(h)]
        rows, start = [], 0
        for y in range(1, h + 1):
            if y == h or sum(abs(p - q) for p, q in zip(col[y], col[start])) > 6:
                if y - start >= 10:
                    rows.append([start, y - 1])
                start = y
        out["rows"] = rows
    elif a.mode == "lines":
        x1 = a.x1 or w
        flags = [min(grey.getpixel((x, y)) for x in range(a.x0, x1, 2)) < a.ink for y in range(h)]
        out["lines"] = bands(flags, min_len=4, max_gap=2)
    else:
        if len(a.y) != 2:
            ap.error("words needs Y0 Y1")
        y0, y1 = a.y
        flags = [min(grey.getpixel((x, y)) for y in range(y0, y1 + 1)) < a.ink for x in range(w)]
        out["line"] = [y0, y1]
        out["words"] = [[b[0], b[1]] for b in bands(flags, max_gap=a.gap - 1)]
    print(json.dumps(out))
    return 0


if __name__ == "__main__":
    sys.exit(main())
