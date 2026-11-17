#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
"""Measure the text a 3D scene shows, before any render: size, safe zone, contrast.

  overlay_audit.py <page url> [times...] [--out DIR] [--min-px 34] [--fine-px 24]
                   [--safe 168,1330] [--margin 40] [--contrast 4.5] [--jobs 4]
  overlay_audit.py http://localhost:8792/index.html 1.5 9.6 17 24 31.6 41 47 51 57.8

The page is a scene from templates/video3d (it loads audit.js on ?audit and renders ?t=).
Without times: one every 2.5 s over the film (--dur, default 60). For each second it asks the
page where every visible piece of overlay text sits and how tall its letters are after every
scale, takes a still of the same second, and reads the real pixels behind the letters.

Each text is checked, on the 1080 x 1920 frame:
  size      letters >= --min-px (34); text marked data-audit="fine" (a timestamp in a bubble)
            >= --fine-px (24)
  safe      inside y --safe (168..1330, clear of the app's top bar and caption) and --margin
            px from the left and right edges; the end card and anything marked
            data-audit-skip="<reason>" are listed, not failed
  contrast  the letters' colour against the pixels really behind them (5th percentile, so a
            line or a prop crossing the text counts): >= --contrast (4.5), or 3.0 for text of
            48 px and up and for fine print. A see-through card over a busy 3D set fails here.
Text that is fading (opacity under 0.9), scrolled out of a clipped panel, off the frame, or
covered by another overlay is left out: pick seconds where each beat has settled.
Exit codes: 0 all pass, 1 a check failed, 2 usage, 3 Chrome or the page did not answer.
Writes <out>/overlay-audit.json and report.md (default out: ./overlay_audit/). Needs Chrome and
Pillow. Serve the scene folder first (python3 -m http.server <port>).
"""
import argparse, html, json, os, re, subprocess, sys, tempfile
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path


def chrome():
    ch = os.environ.get("CHROME", "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome")
    if not os.access(ch, os.X_OK):
        import shutil
        ch = shutil.which("google-chrome") or shutil.which("chromium") or ""
    return ch


def lum(rgb):
    def f(c):
        c /= 255
        return c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4
    r, g, b = rgb[:3]
    return 0.2126 * f(r) + 0.7152 * f(g) + 0.0722 * f(b)


def ratio(a, b):
    la, lb = lum(a), lum(b)
    return (max(la, lb) + 0.05) / (min(la, lb) + 0.05)


def measure(ch, url, t, tmp, budget):
    sep = "&" if "?" in url else "?"
    base = [ch, "--headless=new", "--use-angle=swiftshader", "--enable-unsafe-swiftshader", "--hide-scrollbars",
            "--window-size=1080,1920", f"--virtual-time-budget={budget}"]
    shot = Path(tmp) / f"s{t}.png"
    try:
        dom = subprocess.run(base + ["--dump-dom", f"{url}{sep}t={t}&audit=1&ss=1"], capture_output=True, text=True, timeout=120).stdout
        subprocess.run(base + [f"--screenshot={shot}", f"{url}{sep}t={t}&ss=1"], capture_output=True, timeout=120)
    except subprocess.TimeoutExpired:
        return t, None, None
    m = re.search(r'<script type="application/json" id="overlay-audit">(.*?)</script>', dom, re.S)
    return t, (json.loads(html.unescape(m.group(1))) if m else None), (shot if shot.exists() else None)


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("url"); p.add_argument("times", nargs="*", type=float)
    p.add_argument("--out", default="overlay_audit"); p.add_argument("--dur", type=float, default=60)
    p.add_argument("--min-px", type=float, default=34); p.add_argument("--fine-px", type=float, default=24)
    p.add_argument("--safe", default="168,1330"); p.add_argument("--margin", type=float, default=40)
    p.add_argument("--contrast", type=float, default=4.5); p.add_argument("--jobs", type=int, default=4)
    p.add_argument("--budget", type=int, default=5000)
    a = p.parse_args()
    ch = chrome()
    if not ch:
        print("Chrome not found; set CHROME=/path/to/chrome", file=sys.stderr); sys.exit(3)
    try:
        from PIL import Image, ImageFilter
    except ImportError:
        print("Pillow not found (pip install pillow)", file=sys.stderr); sys.exit(3)
    times = a.times or [round(2.5 * i + 1.25, 2) for i in range(int(a.dur / 2.5))]
    y0, y1 = (float(v) for v in a.safe.split(","))
    out = Path(a.out); out.mkdir(parents=True, exist_ok=True)
    tmp = tempfile.mkdtemp()
    with ThreadPoolExecutor(max_workers=max(1, a.jobs)) as ex:
        got = list(ex.map(lambda t: measure(ch, a.url, t, tmp, a.budget), times))

    fails, notes, rows, dead = [], [], [], []
    for t, items, shot in got:
        if items is None or shot is None:
            dead.append(t); continue
        im = Image.open(shot).convert("RGB")
        sx = im.width / 1080
        def lines(it):
            # one box per line of the text's own letters. A line of tall display type has a box
            # much taller than its letters, reaching into the next line: keep the letters' band.
            out = []
            for x, y, w, h in it.get("rects") or [[it["x"], it["y"], it["w"], it["h"]]]:
                if h > it["px"] * 1.15:
                    y, h = y + (h - it["px"]) / 2, it["px"]
                q = [int(max(0, x) * sx), int(max(0, y) * sx), int(min(1080, x + w) * sx), int(min(1920, y + h) * sx)]
                if q[2] - q[0] > 2 and q[3] - q[1] > 2:
                    out.append(q)
            return out
        boxes = [lines(it) for it in items]
        for n, it in enumerate(items):
            col = [int(float(v)) for v in re.findall(r"[\d.]+", it["color"])[:3]]
            rs_all, bg = [], []
            for box in boxes[n]:
                crop = im.crop(box)
                # another text's line crossing this box (a timestamp in a bubble) is not its background
                for m, obs in enumerate(boxes):
                    for ob in (obs if m != n else []):
                        if ob[0] < box[2] and ob[2] > box[0] and ob[1] < box[3] and ob[3] > box[1]:
                            crop.paste(tuple(col), (ob[0] - box[0] - 2, ob[1] - box[1] - 2, ob[2] - box[0] + 2, ob[3] - box[1] + 2))
                rs = [ratio(col, q) for q in crop.getdata()]
                # the letters, then a 1 px ring round them (their soft edges are neither letter nor ground)
                ink = Image.new("L", crop.size); ink.putdata([255 if r < 1.5 else 0 for r in rs])
                ring = ink.filter(ImageFilter.MaxFilter(3)).getdata()
                rs_all += rs; bg += [r for r, m in zip(rs, ring) if not m]
            cr = None
            if rs_all:
                bg.sort()
                # hardly any ground left = the box is mostly the letters' own colour: no contrast to speak of
                cr = bg[int(len(bg) * 0.05)] if len(bg) >= 0.08 * len(rs_all) else sorted(rs_all)[len(rs_all) // 2]
            need_px = a.fine_px if it["fine"] else a.min_px
            need_cr = 3.0 if (it["px"] >= 48 or it["fine"]) else a.contrast
            row = {"t": t, "text": it["text"], "cls": it["cls"], "px": round(it["px"], 1), "y": [round(it["y"]), round(it["y"] + it["h"])],
                   "x": [round(it["x"]), round(it["x"] + it["w"])], "contrast": cr and round(cr, 2), "fine": it["fine"], "skip": it["skip"]}
            rows.append(row)
            who = f'{t:g} s  "{it["text"]}" (.{it["cls"].split()[0]})'
            if it["skip"]:
                notes.append(f"{who}: skipped, {it['skip']}"); continue
            if it["px"] + 0.5 < need_px:
                fails.append(f"size      {who}: {it['px']:.0f} px, needs {need_px:g}")
            if row["y"][0] < y0 - 1 or row["y"][1] > y1 + 1:
                fails.append(f"safe      {who}: y {row['y'][0]}-{row['y'][1]}, keep text inside {y0:g}-{y1:g}")
            if row["x"][0] < a.margin - 1 or row["x"][1] > 1080 - a.margin + 1:
                fails.append(f"safe      {who}: x {row['x'][0]}-{row['x'][1]}, keep {a.margin:g} px from each side")
            if cr is not None and cr + 0.05 < need_cr:
                fails.append(f"contrast  {who}: {cr:.1f}:1 behind the letters, needs {need_cr:g}:1 (make the card opaque or move it off the busy part)")
    if not rows and not dead:
        print("no text measured at any second: the page did not list its overlay (check ?audit loads audit.js, and the seconds given)", file=sys.stderr); sys.exit(3)
    (out / "overlay-audit.json").write_text(json.dumps(rows, ensure_ascii=False, indent=1))
    uniq = list(dict.fromkeys(fails))
    lines = [f"# Overlay audit: {a.url}", "", f"{len(times)} seconds, {len(rows)} texts measured; size >= {a.min_px:g} px (fine print {a.fine_px:g}), "
             f"safe y {y0:g}-{y1:g}, contrast >= {a.contrast:g} (3.0 from 48 px).", ""]
    lines += [f"- FAIL {f}" for f in uniq] or ["- PASS every text"]
    skipped = {}
    for n in notes:
        skipped[n.split(": skipped, ", 1)[1]] = skipped.get(n.split(": skipped, ", 1)[1], 0) + 1
    lines += [f"- note {c} text(s) left out as marked: {r}" for r, c in skipped.items()]
    lines += [f"- FAIL no answer at {t:g} s (the page did not load audit.js or Chrome hung): run that second again" for t in dead]
    (out / "report.md").write_text("\n".join(lines) + "\n")
    print("\n".join(lines[2:]))
    print(f"report: {out / 'report.md'}")
    sys.exit(3 if dead and not rows else 1 if (uniq or dead) else 0)


if __name__ == "__main__":
    main()
