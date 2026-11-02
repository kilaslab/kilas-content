#!/usr/bin/env bash
# SPDX-License-Identifier: GPL-3.0-or-later
# Install the companion skills this content skill depends on.
# They land in ~/.agents/skills (the shared hub) and are symlinked into every
# agent the `skills` CLI knows (Claude, Cursor, OpenCode, omp, Antigravity/agy, Grok, ...).
#
# Usage: scripts/install-companions.sh [--project]
#   --project  install into the current project (the skills CLI's default) instead of -g
set -euo pipefail

scope=(-g); where="global"
[ "${1:-}" = "--project" ] && { scope=(); where="project"; }

install() { # <repo-url> <skill>
  echo "== $2"
  npx -y skills@latest add "$1" --skill "$2" --agent '*' ${scope[@]+"${scope[@]}"} -y
}

install https://github.com/coreyhaines31/marketingskills copywriting
install https://github.com/coreyhaines31/marketingskills social
install https://github.com/blader/humanizer                humanizer
install https://github.com/ajipurn/bahasa-indonesia-skill  bahasa-indonesia

echo
echo "Installed into the ${where} scope. Verify:"
echo "  ls ~/.agents/skills | grep -E 'copywriting|social|humanizer|bahasa-indonesia'"
echo
echo "Not installed here (ships with the Figma MCP server):"
echo "  figma-use, figma-generate-design  ->  skill://figma/<name>/SKILL.md"
