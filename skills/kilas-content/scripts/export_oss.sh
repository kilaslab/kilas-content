#!/usr/bin/env bash
# SPDX-License-Identifier: GPL-3.0-or-later
# Export a brand-agnostic copy of this skill as a repository, for open-source release.
#
# Usage: scripts/export_oss.sh [--holder "Name"] [--repo owner/repo] <dest-dir> <skill-name> [private-word ...]
#   scripts/export_oss.sh --holder "Jane Doe" --repo jane/content-studio ~/oss content-studio
#
# Writes <dest-dir>/<skill-name>/ in the layout `npx skills add` discovers:
#   LICENSE, README.md          GPL-3.0-or-later text; install instructions
#   skills/<skill-name>/        this skill, without .git, caches, setup-content/, and every
#                               brand pack except brands/_template
#   skills/setup-content/       the first-run setup skill, pointed at <skill-name>
# Each skill folder gets its own LICENSE copy. The front matter keeps `license:`; the
# main skill gets a generic name and description. Then it fails if any exported file
# still mentions a private word (the removed packs' names, the source skill's name, and
# the extra arguments) or holds an image (private reference sheets).
# --holder adds a copyright line to the README; --repo fills the install commands.
# Nothing is published: review the folder, then create the repo yourself.
set -euo pipefail

holder=""; repo="OWNER/REPO"
while [ $# -gt 0 ]; do
  case "$1" in
    --holder) holder="${2:?--holder needs a name}"; shift 2 ;;
    --repo) repo="${2:?--repo needs owner/repo}"; shift 2 ;;
    --) shift; break ;;
    -*) echo "unknown option $1" >&2; exit 2 ;;
    *) break ;;
  esac
done
[ $# -ge 2 ] || { sed -n '2,19p' "$0"; exit 2; }
src="$(cd "$(dirname "$0")/.." && pwd)"
dest_root="$1"; name="$2"; shift 2
case "$name" in *[!a-z0-9-]*|"") echo "skill name: lowercase letters, digits, hyphens" >&2; exit 2 ;; esac
[ "$name" != "setup-content" ] || { echo "skill name: pick another than setup-content" >&2; exit 2; }
src_name="$(sed -n 's/^name: *//p' "$src/SKILL.md" | head -1)"
setup_src="$src/setup-content"
[ -d "$setup_src" ] || setup_src="$src/../setup-content"   # run from an exported copy
[ -f "$setup_src/SKILL.md" ] || { echo "setup-content skill not found next to $src" >&2; exit 1; }
dest="$dest_root/$name"
[ ! -e "$dest" ] || { echo "$dest exists; remove it or pick another place" >&2; exit 1; }

words=("$@")
for pack in "$src"/brands/*/; do
  p="$(basename "$pack")"
  [ "$p" = "_template" ] || words+=("$p")
done
[ -z "$src_name" ] || [ "$src_name" = "$name" ] || words+=("$src_name")

main="$dest/skills/$name"; setup="$dest/skills/setup-content"
mkdir -p "$main" "$setup"
rsync -a --exclude '.git' --exclude '__pycache__' --exclude '*.pyc' --exclude '.DS_Store' \
  --exclude '/brands/*/' --exclude '/setup-content/' "$src/" "$main/"
mkdir -p "$main/brands"
rsync -a --exclude '.DS_Store' "$src/brands/_template" "$main/brands/"
cp "$src/brands/README.md" "$main/brands/README.md"
rsync -a --exclude '.DS_Store' --exclude '__pycache__' "$setup_src/" "$setup/"
cp "$src/LICENSE" "$dest/LICENSE"
cp "$src/.gitignore" "$dest/.gitignore"
cp "$src/LICENSE" "$setup/LICENSE"

python3 -I - "$dest" "$name" "$src_name" "$repo" "$holder" <<'PY'
import os, re, sys
dest, name, src_name, repo, holder = sys.argv[1:6]
main = os.path.join(dest, "skills", name)
setup = os.path.join(dest, "skills", "setup-content")

def rw(path, fn):
    s = open(path, encoding="utf-8").read()
    t = fn(s)
    if t != s:
        open(path, "w", encoding="utf-8").write(t)

# brands/README.md: drop the rows of the removed packs
rw(os.path.join(main, "brands", "README.md"), lambda s: re.sub(r"\| `(?!_template)[^`]+/` \|[^\n]*\n", "", s))

# the main skill: generic front matter, license kept
desc = ("Plan and create social content end to end for any brand: a monthly content plan with pillars, "
        "series, and a calendar; researched pieces with a hook that earns attention; Instagram carousels and "
        "single posts built in Figma or rendered from HTML to PNG; Reels/TikTok scripts and storyboards; X posts "
        "and threads; LinkedIn posts and documents; Threads; and long-form posts that feed them. Use it whenever "
        "someone asks to plan content, make a content calendar, write or design a carousel, slides, a post, a "
        "thread, a Reels script, or repurpose an article into social posts, says \\\"buat konten\\\", "
        "\\\"bikin carousel\\\", \\\"rencana konten\\\", \\\"content plan\\\", or asks for a stronger hook. Each "
        "brand lives in a brand pack (voice, pillars, series, design tokens); on first use in a project it runs "
        "the setup-content skill (brand, assets, renderer).")
rw(os.path.join(main, "SKILL.md"), lambda s: re.sub(
    r"\A---\n.*?\n---\n", f"---\nname: {name}\ndescription: \"{desc}\"\nlicense: GPL-3.0-or-later\n---\n",
    s, count=1, flags=re.S))

# setup-content is a sibling folder in the published layout, not a subfolder
for root, _, files in os.walk(main):
    for f in files:
        if f.endswith(".md"):
            rw(os.path.join(root, f), lambda s: s.replace("(in this repository at\n   `setup-content/SKILL.md`",
                                                         "(installed alongside; in this repository at\n   `../setup-content/SKILL.md`")
                                             .replace("`setup-content/SKILL.md`", "`../setup-content/SKILL.md`")
                                             .replace("(in\n`setup-content/`, installed alongside)", "(in\n`../setup-content/`, installed alongside)"))
rw(os.path.join(main, "README.md"), lambda s: re.sub(r"\nsetup-content/ +[^\n]*", "", s))

# setup-content points at the new name
if src_name and src_name != name:
    for root, _, files in os.walk(setup):
        for f in files:
            if f.endswith(".md"):
                rw(os.path.join(root, f), lambda s: s.replace(src_name, name))

# the holder and the repo go in after the leak check (either may share a pack's name)
copyright = "@@COPYRIGHT@@\n\n" if holder else ""
readme = f"""# {name}

Two agent skills that plan a brand's social content and produce it end to end: a monthly
plan with pillars, series, and a calendar; researched pieces with hooks that earn
attention; Instagram carousels and single posts built in Figma or rendered from HTML to
PNG; Reels/TikTok scripts; X threads; LinkedIn posts and documents; Threads.

| Skill | What it does |
|---|---|
| [`{name}`](skills/{name}/) | plans and creates the content; every brand detail lives in a brand pack |
| [`setup-content`](skills/setup-content/) | first run: asks which brand, collects the brand's own logo, colours, fonts, and photos from its site and profiles (with permission), chooses Figma or HTML → PNG, and writes the brand pack |

## Install

With the [skills CLI](https://github.com/vercel-labs/skills), both skills together (the
content skill runs setup-content on first use):

```bash
npx skills add @@REPO@@ --skill {name} --skill setup-content
npx skills add @@REPO@@ --skill {name} --skill setup-content -g -a claude-code   # global, one agent
```

Or by hand: copy `skills/{name}/` and `skills/setup-content/` side by side into your
agent's skills folder (`~/.claude/skills/`, `~/.agents/skills/`, `~/.grok/skills/` for Grok
Build and Grok Bot, ...).

Needs Python 3.9+. Optional, detected at run time: the Figma MCP (Figma frames), Python
Playwright or Chrome/Chromium (HTML → PNG frames), web search and fetch, a real browser
for profile capture, and image generation: the agent's own image tool (Grok Bot's Grok
Imagine, Codex, ChatGPT, Antigravity), the Antigravity CLI `agy`, or an OpenAI, Gemini,
or xAI key the owner allows at setup. Companion skills (`copywriting`,
`social`, `humanizer`, `bahasa-indonesia`) are listed in
`skills/{name}/references/prerequisites.md`.

## Use

> setup content untuk brand kami: <website>, instagram <link>
>
> rencana konten bulan ini
>
> bikin carousel dari artikel ini <link>

Start with `skills/{name}/README.md` and `skills/{name}/SKILL.md`; a new brand pack starts
from `skills/{name}/brands/_template/`.

## License

{copyright}GPL-3.0-or-later: see [LICENSE](LICENSE). You may use, study, change, and share
these skills; copies and modified versions you distribute must stay under the GPL and
ship their source.
"""
open(os.path.join(dest, "README.md"), "w", encoding="utf-8").write(readme)
PY

leaks=0
for w in "${words[@]}"; do
  if grep -rIilF -- "$w" "$dest" >/dev/null 2>&1; then
    echo "private word '$w' found in:" >&2
    grep -rIilF -- "$w" "$dest" | sed "s#^$dest/#  #" >&2
    leaks=1
  fi
done
imgs="$(find "$dest" -type f \( -iname '*.jpg' -o -iname '*.jpeg' -o -iname '*.png' -o -iname '*.webp' -o -iname '*.gif' \) | sed "s#^$dest/#  #")"
if [ -n "$imgs" ]; then
  echo "images in the export (reference sheets stay private):" >&2
  echo "$imgs" >&2
  leaks=1
fi
for f in "$dest/LICENSE" "$main/LICENSE" "$setup/LICENSE"; do
  grep -q "GNU GENERAL PUBLIC LICENSE" "$f" || { echo "missing or wrong license: $f" >&2; leaks=1; }
done
for f in "$main/SKILL.md" "$setup/SKILL.md"; do
  grep -q "^license: GPL-3.0-or-later" "$f" || { echo "no license field: $f" >&2; leaks=1; }
done
if [ $leaks -ne 0 ]; then
  echo "export left in $dest for inspection; fix the core files, delete it, and run again" >&2
  exit 1
fi
python3 -I -c 'import datetime, sys
p, holder, repo = sys.argv[1:4]
s = open(p, encoding="utf-8").read().replace("@@REPO@@", repo)
s = s.replace("@@COPYRIGHT@@", "Copyright (C) %d %s" % (datetime.date.today().year, holder))
open(p, "w", encoding="utf-8").write(s)' "$dest/README.md" "$holder" "$repo"
echo "exported to $dest ($(find "$dest" -type f | wc -l | tr -d ' ') files): skills/$name, skills/setup-content; private words checked: ${words[*]}"
