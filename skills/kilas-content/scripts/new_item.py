#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
"""Create an item folder in the content workspace, from the skill's templates.

    python3 scripts/new_item.py <workspace> <YYYY-MM-DD> <slug> <format> [--title "..."]
    python3 scripts/new_item.py content 2026-11-03 linux-7-4 carousel

Creates <workspace>/items/<date>-<slug>/ with brief.md, copy.md (sections for the
format), publish.md, storyboard.md for reels, and the folders sources/, artefacts/,
photos/, gen/, export/. Never overwrites an existing folder.
"""
import argparse
import datetime as dt
import os
import re
import sys

TEMPLATES = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "templates")
COPY = {
    "carousel": ["01 Cover", "02", "03", "04", "05", "06", "07", "08 Ajakan", "Caption"],
    "single": ["01", "Caption"],
    "reels": ["Hook (0-3 s)", "Konteks", "Beat 1", "Beat 2", "Beat 3", "Payoff", "CTA", "Caption"],
    "x": ["1", "2", "3", "4", "5"],
    "thread": ["1", "2", "3", "4", "5", "6"],
    "threads": ["1", "2"],
    "linkedin": ["Post"],
    "document": ["Post"],
    "long": ["Title", "Excerpt", "Body"],
}
KEYS = {
    "carousel": "eyebrow: \nheadline: \nbody: \n",
    "single": "headline: \nbody: \nsource: \n",
    "reels": "shot: \nonscreen: \nvo: \n",
    "long": "",
}


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("workspace")
    ap.add_argument("date")
    ap.add_argument("slug")
    ap.add_argument("format", choices=sorted(COPY))
    ap.add_argument("--title", default="")
    a = ap.parse_args()
    try:
        dt.date.fromisoformat(a.date)
    except ValueError:
        print(f"date '{a.date}': use an existing YYYY-MM-DD date", file=sys.stderr)
        return 2
    if not re.fullmatch(r"[a-z0-9]+(-[a-z0-9]+)*", a.slug):
        print("slug: lowercase letters, digits, and hyphens only", file=sys.stderr)
        return 2
    item = os.path.join(a.workspace, "items", f"{a.date}-{a.slug}")
    if os.path.exists(item):
        print(f"exists, not touched: {item}", file=sys.stderr)
        return 1
    for d in ("sources", "artefacts", "photos", "gen", "export"):
        os.makedirs(os.path.join(item, d))
    title = a.title or a.slug.replace("-", " ")

    def tpl(name):
        with open(os.path.join(TEMPLATES, name), encoding="utf-8") as f:
            return f.read().replace("<working title>", title)

    with open(os.path.join(item, "brief.md"), "w", encoding="utf-8") as f:
        f.write(tpl("brief.md").replace("<format>", a.format, 1))
    with open(os.path.join(item, "publish.md"), "w", encoding="utf-8") as f:
        f.write(tpl("publish.md"))
    keys = KEYS.get(a.format, "")
    with open(os.path.join(item, "copy.md"), "w", encoding="utf-8") as f:
        f.write(f"# {title}\n\n<!-- format: {a.format}. key: value lines are published; > lines are source notes. -->\n\n")
        for s in COPY[a.format]:
            f.write(f"## {s}\n{'' if s == 'Caption' else keys}> \n\n")
    if a.format == "reels":
        with open(os.path.join(item, "storyboard.md"), "w", encoding="utf-8") as f:
            f.write(f"# Storyboard: {title}\n\n| # | Time | Shot (what we see) | On-screen text | Voice-over | Asset / source |\n|---|---|---|---|---|---|\n| 1 | 0–3 s | | | | |\n")
    print(item)
    lint = {"thread": "x", "document": "linkedin"}.get(a.format, a.format)
    print(f"lint it with: python3 {os.path.join(os.path.dirname(os.path.abspath(__file__)), 'lint_copy.py')} "
          f"{os.path.join(item, 'copy.md')} --format {lint} --brand <pack>/brand.md")
    return 0


if __name__ == "__main__":
    sys.exit(main())
