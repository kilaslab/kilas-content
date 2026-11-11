#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
"""Check the skill itself, so a broken pointer or script is found by a run, not by the owner.

  skill_check.py [skill dir]        (default: the skill this script belongs to)

- SKILL.md front matter parses as YAML and has a name and a description (a stray quote in
  the description once stopped another agent from loading the skill);
- every path the docs point at exists: `references/...`, `scripts/...`, `templates/...`,
  `evals/...` in SKILL.md and references/ (globs allowed, <placeholders> skipped);
- every file in scripts/ is listed in SKILL.md's scripts row, and every listed one exists;
- every script and template parses: .py (py_compile), .sh (bash -n), .js (node --check,
  when node is installed).
Exit 0 clean, 1 problems found. Run it after every change to the skill
(references/self-improvement.md, "When the skill itself is wrong").
"""
import glob
import os
import re
import shutil
import subprocess
import sys

ROOTS = ("references/", "scripts/", "templates/", "evals/")


def front_matter(skill, problems):
    text = open(os.path.join(skill, "SKILL.md"), encoding="utf-8").read()
    m = re.match(r"^---\n(.*?)\n---\n", text, re.S)
    if not m:
        problems.append("SKILL.md: no front matter between --- lines")
        return text
    try:
        import yaml
    except ImportError:
        print("note: PyYAML not installed, front matter checked for keys only")
        meta = dict(re.findall(r"^(\w[\w-]*):\s*(.*)$", m[1], re.M))
    else:
        try:
            meta = yaml.safe_load(m[1]) or {}
        except yaml.YAMLError as e:
            problems.append(f"SKILL.md: front matter is not valid YAML: {str(e).splitlines()[0]}")
            return text
    for key in ("name", "description"):
        if not meta.get(key):
            problems.append(f"SKILL.md: front matter has no {key}")
    return text


def pointers(skill, problems):
    # a companion skill (setup-content) points into its sibling's folders, so siblings count too
    bases = [skill] + sorted(glob.glob(os.path.join(os.path.dirname(skill), "*", "")))
    docs = [os.path.join(skill, "SKILL.md")] + glob.glob(os.path.join(skill, "references", "**", "*.md"), recursive=True)
    for doc in docs:
        rel = os.path.relpath(doc, skill)
        for n, line in enumerate(open(doc, encoding="utf-8"), 1):
            for span in re.findall(r"`([^`]+)`", line):
                tok = span.split()[0] if span.split() else ""
                tok = re.sub(r"^<skill>/", "", tok).rstrip(".,;:)")
                if not tok.startswith(ROOTS) or "<" in tok or "{" in tok:
                    continue
                if not any(glob.glob(os.path.join(b, tok)) for b in bases):
                    problems.append(f"{rel}:{n}: points at {tok}, which does not exist")


def scripts_listed(skill, text, problems):
    if not os.path.isdir(os.path.join(skill, "scripts")):
        return
    row = next((l for l in text.splitlines() if l.startswith("| `scripts/`")), None)
    if row is None:
        problems.append("SKILL.md: no '| `scripts/` |' row listing the scripts")
        return
    listed = set(re.findall(r"`([\w.-]+\.(?:py|sh|js))`", row))
    have = {f for f in os.listdir(os.path.join(skill, "scripts")) if f.endswith((".py", ".sh", ".js"))}
    for f in sorted(have - listed):
        problems.append(f"SKILL.md scripts row: {f} is in scripts/ but not listed")
    for f in sorted(listed - have):
        problems.append(f"SKILL.md scripts row: {f} is listed but not in scripts/")


def parses(skill, problems):
    node = shutil.which("node")
    files = glob.glob(os.path.join(skill, "scripts", "*")) + glob.glob(os.path.join(skill, "templates", "**", "*.js"), recursive=True)
    for f in sorted(files):
        rel = os.path.relpath(f, skill)
        if f.endswith(".py"):
            try:
                compile(open(f, encoding="utf-8").read(), f, "exec")
            except SyntaxError as e:
                problems.append(f"{rel}:{e.lineno}: {e.msg}")
        elif f.endswith(".sh"):
            r = subprocess.run(["bash", "-n", f], capture_output=True, text=True)
            if r.returncode:
                problems.append(f"{rel}: {r.stderr.strip().splitlines()[0]}")
        elif f.endswith(".js") and node:
            r = subprocess.run([node, "--check", f], capture_output=True, text=True)
            if r.returncode:
                err = [l for l in r.stderr.splitlines() if "Error" in l] or r.stderr.splitlines()
                problems.append(f"{rel}: {err[0] if err else 'node --check failed'}")
    if not node:
        print("note: node not installed, .js files not checked")


def main():
    skill = os.path.abspath(sys.argv[1] if len(sys.argv) > 1 else os.path.join(os.path.dirname(__file__), ".."))
    if not os.path.exists(os.path.join(skill, "SKILL.md")):
        print(f"no SKILL.md in {skill}", file=sys.stderr)
        return 2
    problems = []
    text = front_matter(skill, problems)
    pointers(skill, problems)
    scripts_listed(skill, text, problems)
    parses(skill, problems)
    for p in problems:
        print("FAIL", p)
    print(f"skill_check: {os.path.basename(skill)}: " + ("clean" if not problems else f"{len(problems)} problem(s)"))
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
