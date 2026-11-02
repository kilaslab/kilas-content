#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
"""Bundle figma-helpers.js with a brand's BRAND block and your build code into one
use_figma `code` string, small enough to send (the tool takes at most 50,000 characters).

    python3 scripts/figma_bundle.py --brand brands/<brand>/design.md --page "Carousel — <item>" \
        --scheme gelap build.js -o bundle.js
    python3 scripts/figma_bundle.py --brand brands/<brand>/design.md --page "Galeri layout" \
        scripts/figma-gallery.js -o gallery.js --tail "return { issues: layoutCheck() };"

It replaces the helpers' BRAND block with the one in the design pack, sets PAGE (and N
with --n, SCHEME with --scheme), drops the layout functions the build never calls
(--no-shake keeps them), drops comment-only lines and indentation, appends the build files in order,
then checks: no backticks or dollar-brace (so the bundle embeds in a template literal),
it parses as an async function body (if node is installed), and its size. Exit 1 when it
is over the limit: split the build into two calls (frames 1–4, then 5–8 with REBUILD false)
or drop layouts you do not use.
"""
import argparse
import os
import re
import shutil
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
LIMIT = 50000
BRAND_RE = r"const BRAND = \{[\s\S]*?\n\};"
# Layout functions dropped from the bundle when the build never calls them (directly or
# through another kept layout). Everything else in the helpers is always kept.
LAYOUTS = ["coverDark", "coverSplit", "coverType", "coverChart", "coverQuote", "table", "barChart",
           "columnChart", "bigStat", "versus", "dots", "statCards", "labelledItems", "splitPlate",
           "fullBleed", "steps", "quote", "artefact", "tipCard", "checklist", "statement",
           "closeSlide", "decor", "seeded"]


def functions(js: str):
    """Top-level function blocks: name -> (first line, last line), by brace counting."""
    lines, out, i = js.splitlines(), {}, 0
    while i < len(lines):
        m = re.match(r"^(?:async )?function (\w+)\(", lines[i])
        if m:
            depth, j = 0, i
            while True:
                depth += lines[j].count("{") - lines[j].count("}")
                if depth <= 0 and "{" in "".join(lines[i:j + 1]):
                    break
                j += 1
            out[m.group(1)] = (i, j)
            i = j
        i += 1
    return out


def shake(helpers: str, build: str):
    """Drop layout functions the build does not use. Returns (code, dropped names)."""
    blocks, lines = functions(helpers), helpers.splitlines()
    body = {n: "\n".join(lines[a:b + 1]) for n, (a, b) in blocks.items()}
    # any mention counts (a call, `{ dark: coverDark }`, `pick[k](...)` via a map), not only `name(`
    calls = lambda text: {n for n in LAYOUTS if re.search(r"\b" + n + r"\b", text)}
    keep, todo = set(), calls(build)
    while todo:
        n = todo.pop()
        if n in keep or n not in body:
            continue
        keep.add(n)
        todo |= calls(body[n]) - keep
    drop = [n for n in LAYOUTS if n in blocks and n not in keep]
    gone = set()
    for n in drop:
        a, b = blocks[n]
        gone.update(range(a, b + 1))
    return "\n".join(l for k, l in enumerate(lines) if k not in gone), drop


def strip(js: str) -> str:
    out = []
    for line in js.splitlines():
        s = line.strip()
        if not s or s.startswith("//"):
            continue
        out.append(s)
    return "\n".join(out)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("build", nargs="*", help="your build code, appended after the helpers")
    ap.add_argument("--brand", required=True, help="the brand pack's design.md (holds the BRAND block)")
    ap.add_argument("--page", required=True, help="the Figma page name")
    ap.add_argument("--n", type=int, help="frame count for the index and progress bar (default 8)")
    ap.add_argument("--keep-page", action="store_true", help="REBUILD = false: do not clear the page")
    ap.add_argument("--scheme", help="a key of BRAND.schemes for this piece (default: BRAND.scheme)")
    ap.add_argument("--tail", default="", help="code to append last, e.g. a return statement")
    ap.add_argument("--no-shake", action="store_true", help="keep every layout function")
    ap.add_argument("-o", "--out", required=True)
    a = ap.parse_args()

    helpers = open(os.path.join(HERE, "figma-helpers.js"), encoding="utf-8").read()
    m = re.search(BRAND_RE, open(a.brand, encoding="utf-8").read())
    if not m:
        print(f"no 'const BRAND = {{ ... }};' block in {a.brand}", file=sys.stderr)
        return 2
    helpers, n = re.subn(BRAND_RE, lambda _: m.group(0), helpers, count=1)
    assert n == 1
    page = a.page.replace("\\", "\\\\").replace("'", "\\'")
    helpers = re.sub(r"^const PAGE = .*$", f"const PAGE = '{page}';", helpers, count=1, flags=re.M)
    if a.n:
        helpers = re.sub(r"^const N = \d+;", f"const N = {a.n};", helpers, count=1, flags=re.M)
    if a.scheme:
        if not re.fullmatch(r"[A-Za-z0-9_-]+", a.scheme):
            ap.error("--scheme must be a key of BRAND.schemes (letters, digits, - and _)")
        helpers = re.sub(r"^const SCHEME = .*$", f"const SCHEME = '{a.scheme}';", helpers, count=1, flags=re.M)
    if a.keep_page:
        helpers = re.sub(r"^const REBUILD = true;", "const REBUILD = false;", helpers, count=1, flags=re.M)
    builds = [open(p, encoding="utf-8").read() for p in a.build]
    dropped = []
    if not a.no_shake:
        helpers, dropped = shake(helpers, "\n".join(builds) + "\n" + a.tail)
    parts = [strip(helpers)] + [strip(b) for b in builds]
    if a.tail:
        parts.append(a.tail)
    code = "\n".join(parts) + "\n"

    problems = []
    if "`" in code or "${" in code:
        problems.append("contains a backtick or dollar-brace")
    if shutil.which("node"):
        with tempfile.NamedTemporaryFile("w", suffix=".js", delete=False, encoding="utf-8") as f:
            f.write(code)
        r = subprocess.run(["node", "-e", "const AF=Object.getPrototypeOf(async function(){}).constructor;new AF(require('fs').readFileSync(process.argv[1],'utf8'))", f.name], capture_output=True, text=True)
        os.unlink(f.name)
        if r.returncode:
            err = [l for l in r.stderr.splitlines() if "Error" in l] or r.stderr.strip().splitlines() or ["?"]
            problems.append("does not parse: " + err[0].strip())
    with open(a.out, "w", encoding="utf-8") as f:
        f.write(code)
    print(f"{a.out}: {len(code)} characters (limit {LIMIT})" + (f"; unused layouts dropped: {', '.join(dropped)}" if dropped else ""))
    if len(code) > LIMIT:
        problems.append("over the limit: split the build into two calls or drop unused layouts")
    for p in problems:
        print("FAIL:", p, file=sys.stderr)
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
