#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
"""Turn a brand pack's BRAND block into brand.css for the HTML renderer.

    python3 scripts/brand_css.py brands/<brand>/design.md -o content/items/<item>/html/brand.css

Reads the same 'const BRAND = { ... };' block that figma-helpers.js uses (schemes, fonts,
site, handle, logo, swipe and end words) and writes:

- Google Fonts imports for the brand's families (one import per family, so an unknown
  family cannot break the others; --no-google-fonts to skip)
- :root variables for fonts and the brand's words, read by templates/html/kit.js
- one [data-scheme="<name>"] block per scheme with its colours, duotone pairs, and every
  contrast decision precomputed for each ground (ground, dark, highlight, primary): text
  colour, soft text, rules, progress bar, accent, and how headline marks render. This is
  the same logic as inkOn/accentOn in figma-helpers.js, so both renderers agree.
"""
import argparse
import json
import re
import sys
import urllib.parse

WEIGHTS = {"thin": 100, "extralight": 200, "light": 300, "regular": 400, "book": 400, "medium": 500,
           "semibold": 600, "bold": 700, "extrabold": 800, "black": 900}
GROUNDS = ("ground", "dark", "highlight", "primary")


def strip_comment(line):
    """Drop a // comment that is not inside a quoted string."""
    quote = None
    for i, ch in enumerate(line):
        if quote:
            if ch == quote and line[i - 1] != "\\":
                quote = None
        elif ch in "'\"":
            quote = ch
        elif line.startswith("//", i):
            return line[:i]
    return line


def parse_brand(text):
    m = re.search(r"const BRAND = (\{[\s\S]*?\n\});", text)
    if not m:
        raise SystemExit("no 'const BRAND = { ... };' block found")
    js = "\n".join(strip_comment(l) for l in m.group(1).splitlines())
    # set every string literal aside first, so a ':' or a quote inside one cannot be taken
    # for a key or a delimiter; then quote the bare keys and put the strings back as JSON
    strings = []

    def keep(mt):
        body = mt.group(0)[1:-1]
        strings.append(re.sub(r"\\(.)", lambda e: {"n": "\n", "t": "\t"}.get(e.group(1), e.group(1)), body))
        return f"\x00{len(strings) - 1}\x00"

    js = re.sub(r"'(?:[^'\\\n]|\\.)*'|\"(?:[^\"\\\n]|\\.)*\"|`(?:[^`\\]|\\.)*`", keep, js)
    js = re.sub(r"([{,]\s*)([A-Za-z_$][\w$]*)\s*:", r'\1"\2":', js)
    js = re.sub(r",(\s*[}\]])", r"\1", js)
    js = re.sub(r"\x00(\d+)\x00", lambda mt: json.dumps(strings[int(mt.group(1))]), js)
    try:
        b = json.loads(js)
    except ValueError as e:
        raise SystemExit(f"the BRAND block could not be read ({e}); keep it to plain keys, strings, numbers, arrays, and objects")
    if "schemes" not in b:
        b["schemes"] = {"base": b.get("colors", {})}
        b["scheme"] = "base"
    return b


def rgb(h):
    h = h.strip().lstrip("#")
    if len(h) in (3, 4):  # #FD4 -> #FFDD44 (a 4th digit is alpha, ignored)
        h = "".join(c * 2 for c in h[:3])
    if not re.fullmatch(r"[0-9A-Fa-f]{6}([0-9A-Fa-f]{2})?", h):
        raise SystemExit(f"not a hex colour: #{h}")
    return tuple(int(h[i:i + 2], 16) / 255 for i in (0, 2, 4))


def lum(h):
    f = lambda c: c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4
    r, g, b = (f(c) for c in rgb(h))
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def contrast(a, b):
    x, y = lum(a), lum(b)
    return (max(x, y) + 0.05) / (min(x, y) + 0.05)


def rgba(h, a):
    r, g, b = (round(c * 255) for c in rgb(h))
    return f"rgba({r}, {g}, {b}, {a})"


def scheme_vars(sc):
    c = {k: v for k, v in sc.items() if k != "duotone"}
    c.setdefault("onDark", c["ground"])
    duo = sc.get("duotone") or {}
    light, dark = duo.get("light") or [c["surface"], c["primary"]], duo.get("dark") or [c["mutedDark"], c["dark"]]
    ink_on = lambda bg: max((c["text"], c["onDark"], c["dark"], c["ground"]), key=lambda x: contrast(x, bg))
    accent_on = lambda bg, mn=3: c["highlight"] if contrast(c["highlight"], bg) >= mn else ink_on(bg)
    out = {
        "--c-ground": c["ground"], "--c-text": c["text"], "--c-dark": c["dark"], "--c-ondark": c["onDark"],
        "--c-primary": c["primary"], "--c-surface": c["surface"], "--c-highlight": c["highlight"],
        "--c-muted": c["muted"], "--c-muted-dark": c["mutedDark"], "--c-rule": c["rule"],
        "--c-dark-rgb": " ".join(str(round(x * 255)) for x in rgb(c["dark"])),
        "--duo-light-hi": light[0], "--duo-light-lo": light[1], "--duo-dark-hi": dark[0], "--duo-dark-lo": dark[1],
        "--on-primary": ink_on(c["primary"]), "--on-highlight": ink_on(c["highlight"]), "--on-surface": ink_on(c["surface"]),
        "--label-on-primary": accent_on(c["primary"]),
        "--accent-on-surface": c["primary"] if contrast(c["primary"], c["surface"]) >= 3 else ink_on(c["surface"]),
        "--accent-on-primary": accent_on(c["primary"]),
        "--art-mark": next((x for x in (c["highlight"], c["ground"], c["surface"]) if 0.2 < lum(x) < 0.85), c["highlight"]),
    }
    light_text = lum(c["text"]) > 0.4
    out["--best-bg"] = "transparent" if light_text else c["highlight"]
    out["--best-color"] = c["highlight"] if light_text else c["text"]
    for g in GROUNDS:
        bg = c[g]
        p = f"--g-{g}-"
        ink = c["text"] if g == "ground" else ink_on(bg)
        if g == "ground":
            soft, rule, done, rest = c["muted"], c["rule"], c["primary"], c["rule"]
            cur = c["text"] if contrast(c["highlight"], c["primary"]) < 1.5 else c["highlight"]
            cue = c["primary"] if contrast(c["primary"], bg) >= 3 else c["text"]
            accent = c["primary"] if contrast(c["primary"], bg) >= 3 else c["text"]
            faint = c["surface"]
        else:
            soft = c["mutedDark"] if contrast(c["mutedDark"], bg) >= 3 else rgba(ink, 0.7)
            rule, done, rest = rgba(ink, 0.2), rgba(ink, 0.6), rgba(ink, 0.18)
            cur, cue, accent = accent_on(bg, 2), accent_on(bg, 3), accent_on(bg, 3)
            faint = rgba(ink, 0.08)
        light_ink = lum(ink) > 0.4
        cands = [c["highlight"], c["primary"]] if light_ink else [c["primary"], c["highlight"]]
        acc = next((x for x in cands if contrast(x, ink) >= 1.15 and contrast(x, bg) >= 2.5), None)
        if light_ink:
            mk = {"bg": "transparent", "color": acc or ink, "style": "normal" if acc else "italic", "line": "none"}
        elif contrast(c["highlight"], bg) < 1.25:
            mk = {"bg": "transparent", "color": "inherit", "style": "normal", "line": "underline"}
        else:
            mk = {"bg": c["highlight"], "color": "inherit", "style": "normal", "line": "none"}
        out.update({p + "bg": bg, p + "ink": ink, p + "soft": soft, p + "rule": rule, p + "done": done, p + "rest": rest,
                    p + "cur": cur, p + "cue": cue, p + "accent": accent, p + "faint": faint,
                    p + "mk-bg": mk["bg"], p + "mk-color": mk["color"], p + "mk-style": mk["style"], p + "mk-line": mk["line"],
                    p + "c-color": acc or ink, p + "c-style": "normal" if acc else "italic",
                    p + "u-color": acc if (acc and not light_ink) else ink,
                    p + "pill-bg": c["highlight"] if g != "ground" else c["primary"],
                    p + "pill-ink": ink_on(c["highlight"] if g != "ground" else c["primary"])})
    return out


def font_parts(f):
    style = f.get("style", "Regular").lower().replace(" ", "")
    italic = "italic" in style
    weight = WEIGHTS.get(style.replace("italic", "") or "regular", 400)
    return f["family"], weight, italic


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("design")
    ap.add_argument("-o", "--out", required=True)
    ap.add_argument("--no-google-fonts", action="store_true")
    a = ap.parse_args()
    b = parse_brand(open(a.design, encoding="utf-8").read())

    lines = ["/* SPDX-License-Identifier: GPL-3.0-or-later */", "/* generated by scripts/brand_css.py from " + a.design.split("/")[-1] + "; do not edit by hand */"]
    fonts, need = b.get("fonts", {}), {}
    for f in fonts.values():
        fam, w, it = font_parts(f)
        need.setdefault(fam, set()).add((1 if it else 0, w))
    if not a.no_google_fonts:
        for fam, axes in need.items():
            axes = sorted(axes)
            if any(i for i, _ in axes):
                spec = "ital,wght@" + ";".join(f"{i},{w}" for i, w in axes)
            else:
                spec = "wght@" + ";".join(str(w) for _, w in axes)
            lines.append(f"@import url('https://fonts.googleapis.com/css2?family={urllib.parse.quote_plus(fam)}:{spec}&display=swap');")
    root = {}
    for role, var in (("display", "display"), ("displayRegular", "display-regular"), ("displayItalic", "display-italic"),
                      ("body", "body"), ("bodyMedium", "body-medium"), ("bodyBold", "body-bold"), ("label", "label"), ("arrow", "arrow")):
        f = fonts.get(role) or fonts.get("body") or {"family": "system-ui", "style": "Regular"}
        fam, w, it = font_parts(f)
        generic = "ui-monospace, monospace" if role == "label" else "system-ui, sans-serif"
        root[f"--f-{var}"] = f"'{fam}', {generic}"  # a fallback, so a missing font is not Times
        root[f"--w-{var}"] = str(w)
    logo = b.get("logo") or {}
    for k, v in (("site", b.get("site", "")), ("handle", b.get("handle", "")), ("swipe", b.get("swipe", "→")),
                 ("end", b.get("end", "")), ("sources", b.get("sourcesLabel", "SUMBER")),
                 ("logo-letter", logo.get("letter", "")), ("wordmark", logo.get("wordmark", "")),
                 ("schemes", " ".join(b["schemes"])), ("scheme", b.get("scheme") or next(iter(b["schemes"]))),
                 ("fonts", "|".join(need))):
        root[f"--brand-{k}"] = json.dumps(v, ensure_ascii=False)
    default = b.get("scheme") or next(iter(b["schemes"]))
    lines.append(":root {\n" + "\n".join(f"  {k}: {v};" for k, v in root.items()) + "\n}")
    for name, sc in b["schemes"].items():
        sel = f'[data-scheme="{name}"]' + (", :root" if name == default else "")
        lines.append(sel + " {\n" + "\n".join(f"  {k}: {v};" for k, v in scheme_vars(sc).items()) + "\n}")
    with open(a.out, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")
    print(f"{a.out}: {len(b['schemes'])} schemes ({', '.join(b['schemes'])}), fonts: {', '.join(need)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
