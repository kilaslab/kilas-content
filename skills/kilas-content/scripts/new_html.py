#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
"""Set up the HTML renderer for one item: <item>/html/ with the kit, the brand's CSS, and
a slides.html to edit.

    python3 scripts/new_html.py content/items/<item> --brand <pack>/design.md [--scheme kertas] [--blank]
    python3 scripts/new_html.py content/items/<item> --brand <pack>/design.md --refresh

Copies templates/html/kit.css and kit.js, writes brand.css (scripts/brand_css.py), and
creates slides.html from templates/html/example.html (an 8-slide carousel showing the
layouts) or, with --blank, a one-slide skeleton. Images go in <item>/html/img/. Never
overwrites slides.html; --refresh updates only the kit and brand.css.
"""
import argparse
import os
import re
import shutil
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from brand_css import parse_brand  # noqa: E402  (our own module, next to this script)
TPL = os.path.join(os.path.dirname(HERE), "templates", "html")
BLANK = """<!doctype html>
<html lang="id">
<head>
<meta charset="utf-8">
<title>slides</title>
<link rel="stylesheet" href="brand.css">
<link rel="stylesheet" href="kit.css">
<script src="kit.js" defer></script>
</head>
<body data-scheme="SCHEME">

<section class="slide cover-type" data-bg="dark" data-eyebrow="EYEBROW">
  <div class="content bottom">
    <h1 class="h1 s120">Headline <mark>yang</mark> diklaim.</h1>
    <p class="lede">Satu kalimat taruhan.</p>
  </div>
</section>

</body>
</html>
"""


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("item")
    ap.add_argument("--brand", required=True, help="the brand pack's design.md")
    ap.add_argument("--scheme", help="default: the brand's default scheme")
    ap.add_argument("--blank", action="store_true")
    ap.add_argument("--refresh", action="store_true")
    a = ap.parse_args()
    d = os.path.join(a.item, "html")
    os.makedirs(os.path.join(d, "img"), exist_ok=True)
    for f in ("kit.css", "kit.js"):
        shutil.copy(os.path.join(TPL, f), os.path.join(d, f))
    r = subprocess.run([sys.executable, os.path.join(HERE, "brand_css.py"), a.brand, "-o", os.path.join(d, "brand.css")], capture_output=True, text=True)
    if r.returncode:
        print(r.stderr, file=sys.stderr)
        return r.returncode
    print(r.stdout.strip())
    # the brand's own logo files (BRAND.logo.image / imageOnDark, relative to the pack folder)
    logo = parse_brand(open(a.brand, encoding="utf-8").read()).get("logo") or {}
    extra = []
    for key, var, name in (("image", "--brand-logo-image", "logo"), ("imageOnDark", "--brand-logo-image-dark", "logo-dark")):
        if logo.get(key):
            src = os.path.join(os.path.dirname(os.path.abspath(a.brand)), logo[key])
            if os.path.exists(src):
                dst = os.path.join(d, "img", name + os.path.splitext(src)[1].lower())
                shutil.copy(src, dst)
                extra.append(f'  {var}: "img/{os.path.basename(dst)}";')
            else:
                print(f"logo file not found: {src}", file=sys.stderr)
    if extra:
        with open(os.path.join(d, "brand.css"), "a", encoding="utf-8") as f:
            f.write(":root {\n" + "\n".join(extra) + "\n}\n")
        print("logo: " + ", ".join(e.split('"')[1] for e in extra))
    slides = os.path.join(d, "slides.html")
    if a.refresh or os.path.exists(slides):
        print(f"kit and brand.css refreshed in {d}" + ("" if a.refresh else "; slides.html exists, not touched"))
        return 0
    scheme = a.scheme or re.search(r"--brand-scheme:\s*\"([^\"]+)\"", open(os.path.join(d, "brand.css"), encoding="utf-8").read()).group(1)
    text = BLANK if a.blank else open(os.path.join(TPL, "example.html"), encoding="utf-8").read()
    text = re.sub(r'data-scheme="[^"]*"', f'data-scheme="{scheme}"', text, count=1)
    with open(slides, "w", encoding="utf-8") as f:
        f.write(text)
    print(f"{slides} (scheme {scheme}); put images in {os.path.join(d, 'img')}/, then: python3 {os.path.join(HERE, 'render_slides.py')} {slides}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
