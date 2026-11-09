#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
"""Build the owner's preview of a piece: an Instagram post mock (swipeable carousel, caption
with "more", dots), the slide strip, the Threads text with a copy button, and the checklist
the owner should see before posting. Any agent can make it; nothing is posted.

    python3 scripts/make_preview.py content/items/<item> --brand content/brand/design.md
        [--artifact] [--lang id|en] [--state "DRAF · BELUM DIPOSTING"]

Reads from the item folder:
  export/*.png          the rendered slides, in name order (contact sheets are skipped)
  copy.md               "## Caption" → the caption; a last paragraph of #tags becomes the tags
  publish.md (optional) "Kapan"/"When" table row → banner; "## Threads" section → the thread
                        (`post:` / `reply:` lines, `media: slides` to attach the carousel);
                        "## Alt text" numbered list → alt text; "## Cek sebelum posting" /
                        "## Before posting" bullets → checklist
Writes <item>/preview/index.html and preview/slides/NN.png (a self-contained folder).

View it: python3 -m http.server -d content/items/<item>/preview 8765, then open
http://127.0.0.1:8765/ (file:// may block the slides in some browsers). In Claude, build with
--artifact (no doctype; the Artifact wraps the page) and publish index.html with
files={"slides/01.png": ".../preview/slides/01.png", ...}.
"""
import argparse
import base64
import glob
import json
import os
import re
import shutil
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from brand_css import parse_brand  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
TEMPLATE = os.path.join(HERE, "..", "templates", "preview", "preview.html")
LABELS = {
    "id": {"slides": "Semua slide", "thread": "Threads", "copy": "Salin teks Threads", "copied": "Tersalin",
           "selected": "Teks dipilih, tekan salin", "checks": "Sebelum posting", "more": "lainnya",
           "state": "DRAF · BELUM DIPOSTING", "short": "Draf", "banner": "Posting setelah owner setuju."},
    "en": {"slides": "All slides", "thread": "Threads", "copy": "Copy Threads text", "copied": "Copied",
           "selected": "Text selected, press copy", "checks": "Before posting", "more": "more",
           "state": "DRAFT · NOT POSTED", "short": "Draft", "banner": "Post after the owner approves."},
}


def section(text, names):
    for name in names:
        m = re.search(rf"^## {re.escape(name)}[^\n]*\n(.*?)(?=^## |\Z)", text, flags=re.M | re.S)
        if m:
            return m.group(1).strip("\n")
    return ""


def caption_of(copy_text):
    body = section(copy_text, ["Caption"])
    lines = [l for l in body.splitlines() if not l.startswith(">")]
    text = "\n".join(lines).strip()
    text = re.sub(r"^post:\s?", "", text)
    paras = [p.strip() for p in re.split(r"\n\s*\n", text) if p.strip()]
    tags = ""
    if paras and all(w.startswith("#") for w in paras[-1].split()):
        tags = paras.pop()
    return "\n\n".join(paras), tags


def thread_of(text):
    """`post:`/`reply:` lines start a post of the thread; other lines continue it; `media: slides`
    attaches the carousel to the post above. Plain text without markers is one post."""
    posts = []
    for line in text.splitlines():
        if line.startswith(">"):
            continue
        m = re.match(r"^(post|reply):\s?(.*)$", line)
        if m:
            posts.append({"text": m.group(2), "media": False})
        elif re.match(r"^media:\s*slides\s*$", line) and posts:
            posts[-1]["media"] = True
        elif posts:
            posts[-1]["text"] += "\n" + line
        elif line.strip():
            posts.append({"text": line, "media": False})
    for p in posts:
        p["text"] = p["text"].strip()
    return [p for p in posts if p["text"]]


def bullets(text):
    out = []
    for l in text.splitlines():
        m = re.match(r"^\s*(?:[-*]|\d+\.)\s+(?:\[[ xX]\]\s+)?(.*)$", l)
        if m and m.group(1).strip():
            out.append(m.group(1).strip())
    return out


def table_value(text, keys):
    for l in text.splitlines():
        cells = [c.strip() for c in l.strip().strip("|").split("|")]
        if len(cells) >= 2 and cells[0].lower() in keys:
            return cells[1]
    return ""


def data_uri(path):
    ext = os.path.splitext(path)[1].lower()
    mime = {".svg": "image/svg+xml", ".png": "image/png", ".jpg": "image/jpeg", ".jpeg": "image/jpeg", ".webp": "image/webp"}.get(ext)
    if not mime or not os.path.exists(path):
        return ""
    return f"data:{mime};base64," + base64.b64encode(open(path, "rb").read()).decode()


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("item")
    ap.add_argument("--brand", required=True, help="the brand pack's design.md (BRAND block)")
    ap.add_argument("--artifact", action="store_true", help="omit the doctype (for a Claude Artifact)")
    ap.add_argument("--lang", default="id", choices=sorted(LABELS))
    ap.add_argument("--state", help="banner label, default DRAF · BELUM DIPOSTING")
    args = ap.parse_args()

    L = LABELS[args.lang]
    item = args.item.rstrip("/")
    slides = sorted(p for p in glob.glob(os.path.join(item, "export", "*.png")))
    if not slides:
        sys.exit(f"no PNG in {item}/export: render the slides first")
    copy_path = os.path.join(item, "copy.md")
    if not os.path.exists(copy_path):
        sys.exit(f"missing {copy_path}")
    copy_text = open(copy_path, encoding="utf-8").read()
    pub_path = os.path.join(item, "publish.md")
    pub = open(pub_path, encoding="utf-8").read() if os.path.exists(pub_path) else ""

    brand = parse_brand(open(args.brand, encoding="utf-8").read())
    scheme = brand["schemes"].get(brand.get("scheme"), next(iter(brand["schemes"].values())))
    pack = os.path.dirname(os.path.abspath(args.brand))
    logo = (brand.get("logo") or {}).get("image", "")
    avatar = data_uri(os.path.join(pack, logo)) if logo else ""

    caption, tags = caption_of(copy_text)
    when = table_value(pub, {"kapan", "when"})
    out = os.path.join(item, "preview")
    shutil.rmtree(os.path.join(out, "slides"), ignore_errors=True)
    os.makedirs(os.path.join(out, "slides"))
    rel = []
    for n, p in enumerate(slides, 1):
        name = f"{n:02d}.png"
        shutil.copyfile(p, os.path.join(out, "slides", name))
        rel.append(f"slides/{name}")

    data = {
        "state": args.state or L["state"],
        "banner": (when + ". " if when else "") + L["banner"],
        "statusShort": L["short"],
        "handle": brand.get("handle", "").lstrip("@") or os.path.basename(item),
        "avatar": avatar,
        "slides": rel,
        "alts": bullets(section(pub, ["Alt text"])),
        "caption": caption,
        "tags": tags,
        "thread": thread_of(section(pub, ["Threads"])),
        "checks": bullets(section(pub, ["Cek sebelum posting", "Before posting"])),
        "labels": {"slides": L["slides"], "thread": L["thread"], "copy": L["copy"], "copied": L["copied"],
                   "selected": L["selected"], "checks": L["checks"], "more": L["more"]},
    }
    html = open(TEMPLATE, encoding="utf-8").read()
    title = "Preview " + os.path.basename(item)
    html = (html.replace("__TITLE__", title)
            .replace("__ACCENT__", scheme.get("primary", "#14786B"))
            .replace("__ACCENT_DARK__", scheme.get("mutedDark", scheme.get("primary", "#3DDC97")))
            .replace("__FRAME__", scheme.get("ground", "#FFFFFF"))
            .replace("__RATIO__", "4 / 5")
            .replace("__DATA__", json.dumps(data, ensure_ascii=False).replace("</", "<\\/")))
    if not args.artifact:
        html = "<!doctype html>\n<html lang=\"" + args.lang + "\">\n" + html + "\n</html>\n"
    open(os.path.join(out, "index.html"), "w", encoding="utf-8").write(html)
    print(os.path.join(out, "index.html"))
    print(f"{len(rel)} slides · caption {len(caption)} chars · threads {len(data['thread'])} post(s) · "
          f"alt {len(data['alts'])} · checklist {len(data['checks'])}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
