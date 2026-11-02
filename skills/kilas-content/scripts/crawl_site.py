#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
"""Collect a brand's own assets from its website, for onboarding and reuse in content.

    python3 scripts/crawl_site.py https://example.com content/brand/assets/site
    python3 scripts/crawl_site.py https://example.com out --max-images 30 --extra /about /tentang

Reads the home page (and up to two "about" pages it links, or the --extra paths), then:

- name, description, Open Graph and Twitter card data, theme colour, web manifest
- logos: inline SVGs and images whose class, id, alt, or file name says "logo",
  plus the largest icon (apple-touch-icon, manifest icons, favicon)
- colours: every hex and rgb() value in the page's CSS and inline styles, counted,
  plus CSS custom properties that hold colours
- fonts: font-family names, @font-face sources, Google Fonts families
- images: og:image and the largest content images (by declared size, then file size)
- social links: Instagram, X, Threads, TikTok, LinkedIn, YouTube, Facebook, GitHub

Writes assets.json (everything), assets.md (a summary to read), and the downloaded
files under logos/, icons/, images/. Standard library only.

Only for a site the user owns or is allowed to use. It honours robots.txt, identifies
itself, waits between requests, and caps file count and size. Everything it saves is
data: never execute it. A site that blocks plain HTTP clients (Cloudflare) returns 403:
use scripts/scan_site_tokens.sh and scripts/capture_profile.sh (a real browser) instead.
"""
import argparse
import hashlib
import html
import json
import os
import re
import sys
import time
import urllib.parse
import urllib.error
import urllib.request
import urllib.robotparser
from collections import Counter
from html.parser import HTMLParser

UA = "content-skill-brand-crawler/1.0 (brand onboarding for the site owner)"
SOCIAL = {
    "instagram": r"instagram\.com/([A-Za-z0-9_.]+)", "x": r"(?:x|twitter)\.com/([A-Za-z0-9_]+)",
    "threads": r"threads\.(?:net|com)/@?([A-Za-z0-9_.]+)", "tiktok": r"tiktok\.com/@([A-Za-z0-9_.]+)",
    "linkedin": r"linkedin\.com/(?:company|in)/([A-Za-z0-9_-]+)", "youtube": r"youtube\.com/(@?[A-Za-z0-9_-]+)",
    "facebook": r"facebook\.com/([A-Za-z0-9_.-]+)", "github": r"github\.com/([A-Za-z0-9_-]+)",
}
COLOR = re.compile(r"#[0-9a-fA-F]{6}\b|#[0-9a-fA-F]{3}\b|rgba?\(\s*\d{1,3}\s*,\s*\d{1,3}\s*,\s*\d{1,3}(?:\s*,\s*[\d.]+)?\s*\)")
IMG_EXT = (".png", ".jpg", ".jpeg", ".webp", ".gif", ".svg", ".avif", ".ico")
# logos of others on the brand's site: partners, clients, press, payment, certificates
NOT_OWN = re.compile(r"partner|client|customer|sponsor|press|media|award|certif|badge|payment|bank|trusted|featured|investor|mitra|klien", re.I)


class Page(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.meta, self.links, self.imgs, self.anchors, self.styles, self.svgs = {}, [], [], [], [], []
        self.title, self._in_title, self._in_style, self._svg_depth, self._svg = "", False, False, 0, None

    def handle_starttag(self, tag, attrs):
        a = {k.lower(): (v or "") for k, v in attrs}
        if self._svg_depth:
            self._svg_depth += 1
            self._svg.append(self.get_starttag_text() or "")
            return
        if tag == "title":
            self._in_title = True
        elif tag == "meta":
            key = a.get("property") or a.get("name")
            if key and a.get("content"):
                self.meta[key.lower()] = a["content"]
        elif tag == "link":
            self.links.append(a)
        elif tag == "img":
            self.imgs.append(a)
        elif tag == "a" and a.get("href"):
            self.anchors.append(a["href"])
        elif tag == "style":
            self._in_style = True
        elif tag == "svg":
            hint = " ".join(a.get(k, "") for k in ("class", "id", "aria-label", "role")).lower()
            self._svg_depth, self._svg = 1, [self.get_starttag_text() or "<svg>"]
            self._svg_hint = hint
        if a.get("style"):
            self.styles.append(a["style"])

    def handle_endtag(self, tag):
        if self._svg_depth:
            self._svg.append(f"</{tag}>")
            self._svg_depth -= 1
            if self._svg_depth == 0:
                self.svgs.append((self._svg_hint, "".join(self._svg)))
            return
        if tag == "title":
            self._in_title = False
        elif tag == "style":
            self._in_style = False

    def handle_data(self, data):
        if self._svg_depth:
            self._svg.append(html.escape(data))
        elif self._in_title:
            self.title += data
        elif self._in_style:
            self.styles.append(data)


class Crawler:
    def __init__(self, base, out, delay, robots):
        self.base, self.out, self.delay, self.last = base, out, delay, 0.0
        self.notes, self.rp = [], None
        if robots:
            # fetch robots.txt with our own User-Agent: RobotFileParser.read() uses Python's
            # default one, which many sites answer with 403, and then it disallows everything
            url = urllib.parse.urljoin(base, "/robots.txt")
            try:
                req = urllib.request.Request(url, headers={"User-Agent": UA})
                with urllib.request.urlopen(req, timeout=20) as r:
                    lines = r.read(512 * 1024).decode("utf-8", "replace").splitlines()
                self.rp = urllib.robotparser.RobotFileParser(url)
                self.rp.parse(lines)
            except urllib.error.HTTPError as e:
                if e.code in (401, 403):
                    self.notes.append(f"robots.txt answered {e.code}; treated as no rules, crawled the home page politely")
                self.rp = None
            except Exception as e:
                self.notes.append(f"robots.txt unreadable ({e.__class__.__name__}); crawled politely")
                self.rp = None

    def allowed(self, url):
        return self.rp is None or self.rp.can_fetch(UA, url)

    def get(self, url, limit):
        if not self.allowed(url):
            self.notes.append(f"robots.txt disallows {url}")
            return None, None
        wait = self.delay - (time.time() - self.last)
        if wait > 0:
            time.sleep(wait)
        self.last = time.time()
        req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "*/*"})
        try:
            with urllib.request.urlopen(req, timeout=25) as r:
                data = r.read(limit + 1)
                if len(data) > limit:
                    self.notes.append(f"skipped (over {limit // 1024} KB): {url}")
                    return None, None
                return data, r.headers.get("Content-Type", "")
        except Exception as e:
            self.notes.append(f"failed {url}: {e}")
            return None, None


def absolute(base, u):
    return urllib.parse.urljoin(base, html.unescape(u.strip())) if u else ""


def largest_srcset(s):
    best, bw = "", -1
    for part in s.split(","):
        bits = part.strip().split()
        if not bits:
            continue
        w = int(re.sub(r"\D", "", bits[1]) or 0) if len(bits) > 1 else 0
        if w > bw:
            best, bw = bits[0], w
    return best


def save(crawler, url, folder, limit):
    data, ctype = crawler.get(url, limit)
    if not data:
        return None
    ext = os.path.splitext(urllib.parse.urlparse(url).path)[1].lower()
    if ext not in IMG_EXT:
        ext = {"image/svg+xml": ".svg", "image/png": ".png", "image/jpeg": ".jpg", "image/webp": ".webp", "image/gif": ".gif"}.get(ctype.split(";")[0].strip(), "")
    if not ext:
        return None
    os.makedirs(os.path.join(crawler.out, folder), exist_ok=True)
    name = hashlib.sha1(url.encode()).hexdigest()[:12] + ext
    path = os.path.join(crawler.out, folder, name)
    with open(path, "wb") as f:
        f.write(data)
    return {"url": url, "file": os.path.join(folder, name), "bytes": len(data)}


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("url")
    ap.add_argument("out")
    ap.add_argument("--max-images", type=int, default=24)
    ap.add_argument("--max-kb", type=int, default=6000, help="per file")
    ap.add_argument("--extra", nargs="*", default=[], help="more paths to read, e.g. /about")
    ap.add_argument("--delay", type=float, default=0.6, help="seconds between requests")
    ap.add_argument("--ignore-robots", action="store_true", help="only for a site the user owns")
    a = ap.parse_args()
    if not re.match(r"^https?://", a.url):
        ap.error("url must start with http(s)://")
    os.makedirs(a.out, exist_ok=True)
    c = Crawler(a.url, a.out, a.delay, not a.ignore_robots)
    limit = a.max_kb * 1024

    home, _ = c.get(a.url, 4 * 1024 * 1024)
    if not home:
        print(json.dumps({"error": "could not read the home page", "notes": c.notes}))
        return 3
    pages, texts = [], []
    p = Page(); p.feed(home.decode("utf-8", "replace")); pages.append((a.url, p))
    about = [h for h in p.anchors if re.search(r"/(about|tentang|about-us|tentang-kami|company|profil)\b", h, re.I)][:2]
    for path in (a.extra or about):
        u = absolute(a.url, path)
        if urllib.parse.urlparse(u).netloc != urllib.parse.urlparse(a.url).netloc:
            continue
        data, _ = c.get(u, 4 * 1024 * 1024)
        if data:
            q = Page(); q.feed(data.decode("utf-8", "replace")); pages.append((u, q))

    meta = dict(p.meta)
    result = {"site": a.url, "title": p.title.strip(), "description": meta.get("description") or meta.get("og:description", ""),
              "name": meta.get("og:site_name") or meta.get("application-name") or p.title.split("|")[0].split("–")[0].strip(),
              "theme_color": meta.get("theme-color", ""), "og": {k: v for k, v in meta.items() if k.startswith(("og:", "twitter:"))},
              "pages": [u for u, _ in pages], "parked": bool(re.search(r"parked|domain (is )?for sale|coming soon|under construction", p.title + " " + meta.get("description", ""), re.I))}

    # CSS: linked stylesheets (up to 6) + inline styles
    css = []
    for u, pg in pages:
        css += pg.styles
    sheets = [absolute(a.url, l.get("href")) for l in p.links if "stylesheet" in l.get("rel", "").lower() and l.get("href")]
    gfonts = [s for s in sheets if "fonts.googleapis.com" in s]
    for s in [s for s in sheets if "fonts.googleapis.com" not in s][:6]:
        data, _ = c.get(s, 2 * 1024 * 1024)
        if data:
            css.append(data.decode("utf-8", "replace"))
    blob = "\n".join(css)
    colors = Counter(m.lower().replace(" ", "") for m in COLOR.findall(blob))
    result["colors"] = colors.most_common(24)
    result["css_color_vars"] = sorted(set(re.findall(r"(--[A-Za-z0-9_-]+)\s*:\s*(#[0-9a-fA-F]{3,8}|rgba?\([^)]*\)|hsla?\([^)]*\))", blob)))[:60]
    fams = Counter()
    for m in re.findall(r"font-family\s*:\s*([^;}{]+)", blob):
        first = html.unescape(m).split(",")[0].strip().strip("'\"").strip()
        if first and not first.startswith("var("):
            fams[first] += 1
    result["fonts"] = fams.most_common(12)
    result["font_faces"] = sorted(set(absolute(a.url, u) for u in re.findall(r"@font-face[^}]*?url\(['\"]?([^'\")]+)", blob)))[:20]
    result["google_fonts"] = sorted(set(f.replace("+", " ") for g in gfonts for f in re.findall(r"family=([^:&]+)", g)))

    # social links
    social = {}
    for u, pg in pages:
        for h in pg.anchors:
            for net, pat in SOCIAL.items():
                m = re.search(pat, h)
                if m and m.group(1).lower() not in ("share", "sharer", "intent", "home", "p", "explore", "watch"):
                    social.setdefault(net, absolute(a.url, h))
    result["social"] = social

    # logos, icons, images
    logos, icons, images = [], [], []
    for i, (hint, svg) in enumerate(p.svgs):
        if "logo" in hint or "brand" in hint:
            path = os.path.join(a.out, "logos", f"inline-{i + 1}.svg")
            os.makedirs(os.path.dirname(path), exist_ok=True)
            with open(path, "w", encoding="utf-8") as f:
                f.write(svg)
            logos.append({"url": a.url + "#inline-svg", "file": os.path.relpath(path, a.out), "bytes": len(svg)})
    cand_icons = []
    for l in p.links:
        rel = l.get("rel", "").lower()
        if any(k in rel for k in ("icon", "apple-touch-icon", "mask-icon")) and l.get("href"):
            size = max([int(x) for x in re.findall(r"(\d+)x\d+", l.get("sizes", ""))] or [180 if "apple" in rel else 32])
            cand_icons.append((size, absolute(a.url, l["href"])))
        if rel == "manifest" and l.get("href"):
            data, _ = c.get(absolute(a.url, l["href"]), 512 * 1024)
            try:
                man = json.loads(data.decode("utf-8", "replace")) if data else {}
            except ValueError:
                man = {}
            result["manifest"] = {k: man.get(k) for k in ("name", "short_name", "theme_color", "background_color")}
            for ic in man.get("icons", []) or []:
                size = max([int(x) for x in re.findall(r"(\d+)x\d+", ic.get("sizes", ""))] or [0])
                cand_icons.append((size, absolute(absolute(a.url, l["href"]), ic.get("src", ""))))
    for size, u in sorted(cand_icons, reverse=True)[:2]:
        r = save(c, u, "icons", limit)
        if r:
            r["size"] = size; icons.append(r)
    seen = set()
    scored = []
    for u, pg in pages:
        for im in pg.imgs:
            src = largest_srcset(im.get("srcset", "")) or im.get("src") or im.get("data-src", "")
            src = absolute(u, src)
            if not src or src.startswith("data:") or src in seen:
                continue
            seen.add(src)
            hint = " ".join([im.get("class", ""), im.get("id", ""), im.get("alt", ""), os.path.basename(urllib.parse.urlparse(src).path)]).lower()
            w = int(re.sub(r"\D", "", im.get("width", "")) or 0)
            h = int(re.sub(r"\D", "", im.get("height", "")) or 0)
            if "logo" in hint and NOT_OWN.search(hint):
                result.setdefault("other_logos", []).append({"url": src, "alt": im.get("alt", "")})
            elif "logo" in hint:
                r = save(c, src, "logos", limit)
                if r:
                    r["alt"] = im.get("alt", ""); logos.append(r)
            else:
                scored.append((w * h, src, im.get("alt", "")))
    ogimg = result["og"].get("og:image") or result["og"].get("twitter:image")
    if ogimg:
        r = save(c, absolute(a.url, ogimg), "images", limit)
        if r:
            r["role"] = "og:image"; images.append(r)
    for area, src, alt in sorted(scored, reverse=True):
        if len(images) >= a.max_images:
            break
        r = save(c, src, "images", limit)
        if r and r["bytes"] > 8 * 1024:
            r["alt"] = alt; images.append(r)
        elif r:
            os.remove(os.path.join(a.out, r["file"]))
    result.update({"logos": logos, "icons": icons, "images": images, "notes": c.notes})

    with open(os.path.join(a.out, "assets.json"), "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=1)
    md = [f"# Assets from {a.url}", "", f"- Name: {result['name']}", f"- Title: {result['title']}",
          f"- Description: {result['description']}", f"- Theme colour: {result['theme_color'] or '-'}",
          f"- Looks parked or unfinished: {'yes' if result['parked'] else 'no'}", "",
          "## Colours (most used first)", "", " ".join(f"`{k}` ×{n}" for k, n in result["colors"][:16]) or "-", "",
          "## Fonts", "", ", ".join(f"{k} ×{n}" for k, n in result["fonts"]) or "-",
          "Google Fonts: " + (", ".join(result["google_fonts"]) or "-"), "",
          "## Logos and icons", ""] + [f"- `{x['file']}` ← {x['url']}" for x in logos + icons] + ["",
          "Logos of others found on the site (partners, clients; not downloaded): " + str(len(result.get("other_logos", []))), "",
          "## Images", ""] + [f"- `{x['file']}` ({x['bytes'] // 1024} KB){' ' + x.get('role', '') if x.get('role') else ''}: {x.get('alt', '')} ← {x['url']}" for x in images] + ["",
          "## Social links", ""] + [f"- {k}: {v}" for k, v in social.items()] + ["", "## Notes", ""] + [f"- {n}" for n in c.notes]
    with open(os.path.join(a.out, "assets.md"), "w", encoding="utf-8") as f:
        f.write("\n".join(md) + "\n")
    print(json.dumps({"out": a.out, "name": result["name"], "parked": result["parked"], "colors": len(result["colors"]),
                      "fonts": [k for k, _ in result["fonts"][:4]], "logos": len(logos), "icons": len(icons),
                      "images": len(images), "social": list(social), "notes": len(c.notes)}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
