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
    Status: active               (active | active; partly superseded by L-NNN (what changed)
                                  | superseded by L-NNN (why) | retired (why))

    python3 scripts/lessons.py rules content                 # print active rules (read before planning or writing)
    python3 scripts/lessons.py check content content/items/<item>/copy.md   # exit 1 if a Check pattern hits
    python3 scripts/lessons.py add content --source owner --area tone \
        --lesson "..." --rule "..." [--check "a|b"] [--applied "..."]
    python3 scripts/lessons.py audit content                 # exit 1 if a rule has no home yet

audit is the self-heal check: every active lesson's Applied names a home outside the item it
came from (brand.md, design.md, a skill reference, script or template, AGENTS.md, the agent's
memory, or "lessons.md only: <reason>"), every file it names exists, every superseded-by
points at a real lesson, and every Check pattern compiles. Run it before calling work done.

check reads only published text in copy.md (key: value lines and the caption), skipping
"> " source notes and builder keys, so a lesson can name a phrase without tripping itself.
"""
import argparse
import datetime as dt
import glob
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


def active(l):
    # "active; partly superseded by L-049 ..." still binds for the part that was not replaced
    return l.get("status", "active").startswith("active")


SKILL = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HOME_WORDS = re.compile(r"brand\.md|design\.md|AGENTS\.md|CLAUDE\.md|memory|SKILL\.md|"
                        r"references/|scripts/|templates/|lessons\.md only", re.I)
# a file (name.ext, maybe with folders) or a folder under a known root; "a/b" in prose is not a path
FILE_TOKEN = re.compile(r"(?:[\w.-]+/)*[\w*-]+\.(?:md|py|sh|js|html|css|json)\b|"
                        r"(?:content|references|scripts|templates|brands|evals|\.agents)/[\w./*-]*")


def audit(ws):
    lessons = parse(ws)
    ids = {l["id"] for l in lessons}
    root = os.path.dirname(os.path.abspath(ws))
    # a name in Applied may be relative to the project, the workspace, the brand pack, or the skill
    bases = [root, os.path.abspath(ws), os.path.join(os.path.abspath(ws), "brand"), SKILL]
    problems = []
    for l in lessons:
        status = l.get("status", "active")
        for ref in re.findall(r"superseded by (L-\d+)|digantikan (L-\d+)|digabung ke (L-\d+)", status):
            ref = next(r for r in ref if r)
            if ref not in ids:
                problems.append((l["id"], f"status points at {ref}, which does not exist"))
        if not active(l):
            continue
        if l.get("check"):
            try:
                re.compile(l["check"])
            except re.error as e:
                problems.append((l["id"], f"Check does not compile: {e}"))
        applied = l.get("applied", "").strip()
        if not applied or applied == "-" or not HOME_WORDS.search(applied):
            problems.append((l["id"], f"no home yet (Applied: {applied or '-'}); promote the rule "
                                      "(references/self-improvement.md, step 4)"))
            continue
        for tok in FILE_TOKEN.findall(applied):
            tok = tok.rstrip("/.")
            if tok.startswith(("http", "www.", "/")) or "*" in tok or "/" not in tok and "." not in tok:
                continue
            if not any(glob.glob(os.path.join(b, tok)) or glob.glob(os.path.join(b, "**", tok), recursive=True)
                       for b in bases):
                problems.append((l["id"], f"Applied names {tok}, which is not in the project, the brand "
                                          "pack, or the skill"))
    return problems


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
    u = sub.add_parser("audit"); u.add_argument("workspace")
    args = ap.parse_args()

    if args.cmd == "rules":
        rules = [l for l in parse(args.workspace) if active(l)]
        if not rules:
            print("no lessons yet:", path_of(args.workspace)); return 0
        for l in rules:
            note = l.get("status", "active")[len("active"):].lstrip("; ")
            print(f"{l['id']} [{l['area']}] {l.get('rule', '')}" + (f"  ({note})" if note else ""))
        return 0

    if args.cmd == "audit":
        problems = audit(args.workspace)
        for lid, msg in problems:
            print(f"FAIL {lid}: {msg}")
        n = len([l for l in parse(args.workspace) if active(l)])
        print(f"audit: {n} active lessons, " + ("every rule has a home" if not problems else f"{len(problems)} problem(s)"))
        return 1 if problems else 0

    if args.cmd == "check":
        text = published(args.copy)
        hits = 0
        for l in parse(args.workspace):
            pat = l.get("check", "")
            if not active(l) or not pat:
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
