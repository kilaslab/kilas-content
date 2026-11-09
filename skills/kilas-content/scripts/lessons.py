#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
"""Keep the brand's lessons: owner feedback, review findings, and mistakes, turned into
rules every later run reads and checks. The lessons live in content/lessons.md, one
"## L-NNN" block each:

    ## L-003 · 2026-11-09 · owner · tone
    Lesson: what happened, in one or two sentences.
    Rule: what to do from now on, stated positively.
    Check: regex|regex          (optional; matched against published copy, case-insensitive)
    Applied: where the rule now also lives (brand.md, design.md, a reference, a script)
    Status: active               (active | retired)

    python3 scripts/lessons.py rules content                 # print active rules (read before planning or writing)
    python3 scripts/lessons.py check content content/items/<item>/copy.md   # exit 1 if a Check pattern hits
    python3 scripts/lessons.py add content --source owner --area tone \
        --lesson "..." --rule "..." [--check "a|b"] [--applied "..."]

check reads only published text in copy.md (key: value lines and the caption), skipping
"> " source notes and builder keys, so a lesson can name a phrase without tripping itself.
"""
import argparse
import datetime as dt
import os
import re
import sys

HEAD = re.compile(r"^## (L-\d+) · (\S+) · ([^·]+) · (.+)$")
BUILDER = {"chart", "sources", "photos", "credit", "note", "image", "shot"}
TEMPLATE = """# Lessons

What this brand's owner, reviewers, and our own mistakes taught us. Every run reads the
active rules first (`lessons.py rules`), and every piece is checked against them
(`lessons.py check`). Add a lesson the moment feedback arrives (`lessons.py add`), then
move the rule to where it belongs (brand pack, design pack, a skill reference) and note
it under Applied. Retire a lesson by setting `Status: retired`; never delete it.
"""


def path_of(ws):
    return os.path.join(ws, "lessons.md")


def parse(ws):
    p = path_of(ws)
    if not os.path.exists(p):
        return []
    out, cur = [], None
    for line in open(p, encoding="utf-8"):
        m = HEAD.match(line.rstrip("\n"))
        if m:
            cur = {"id": m[1], "date": m[2], "source": m[3].strip(), "area": m[4].strip()}
            out.append(cur)
            continue
        if cur is not None and ":" in line and not line.startswith(" "):
            k, v = line.split(":", 1)
            cur[k.strip().lower()] = v.strip()
    return out


def published(copy_path):
    lines = []
    for line in open(copy_path, encoding="utf-8"):
        s = line.rstrip("\n")
        if not s or s.startswith(">") or s.startswith("#") or s.startswith("<!--"):
            continue
        m = re.match(r"^([a-z0-9_]+):\s?(.*)$", s)
        if m:
            if m[1] in BUILDER:
                continue
            s = m[2]
        lines.append(s)
    return lines


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    r = sub.add_parser("rules"); r.add_argument("workspace")
    c = sub.add_parser("check"); c.add_argument("workspace"); c.add_argument("copy")
    a = sub.add_parser("add"); a.add_argument("workspace")
    for k in ("source", "area", "lesson", "rule"):
        a.add_argument("--" + k, required=True)
    a.add_argument("--check", default=""); a.add_argument("--applied", default="")
    args = ap.parse_args()

    if args.cmd == "rules":
        active = [l for l in parse(args.workspace) if l.get("status", "active") == "active"]
        if not active:
            print("no lessons yet:", path_of(args.workspace)); return 0
        for l in active:
            print(f"{l['id']} [{l['area']}] {l.get('rule', '')}")
        return 0

    if args.cmd == "check":
        text = published(args.copy)
        hits = 0
        for l in parse(args.workspace):
            pat = l.get("check", "")
            if l.get("status", "active") != "active" or not pat:
                continue
            rx = re.compile(pat, re.I)
            for s in text:
                if rx.search(s):
                    hits += 1
                    print(f"FAIL {l['id']} [{l['area']}] {l.get('rule', '')}\n     > {s[:140]}")
        print("lessons: no hits" if not hits else f"lessons: {hits} hit(s)")
        return 1 if hits else 0

    p = path_of(args.workspace)
    if not os.path.exists(p):
        open(p, "w", encoding="utf-8").write(TEMPLATE)
    n = max([int(l["id"][2:]) for l in parse(args.workspace)] or [0]) + 1
    if args.check:
        re.compile(args.check)
    block = f"\n## L-{n:03d} · {dt.date.today().isoformat()} · {args.source} · {args.area}\n"
    block += f"Lesson: {args.lesson}\nRule: {args.rule}\n"
    if args.check:
        block += f"Check: {args.check}\n"
    block += f"Applied: {args.applied or '-'}\nStatus: active\n"
    open(p, "a", encoding="utf-8").write(block)
    print(f"added L-{n:03d} to {p}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
