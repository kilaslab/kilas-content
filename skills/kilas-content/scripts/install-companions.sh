#!/usr/bin/env bash
# SPDX-License-Identifier: GPL-3.0-or-later
# Install the companion skills this content skill depends on.
# They land in ~/.agents/skills (the shared hub) and are symlinked into every
# agent the `skills` CLI knows (Claude, Cursor, OpenCode, omp, Antigravity/agy, ...).
#
# Usage: scripts/install-companions.sh [--project]
#   --project  install to ./.agents/skills (travels with this repo) instead of -g
set -euo pipefail

SCOPE="-g"
[ "${1:-}" = "--project" ] && SCOPE="-p"

install() { # <repo-url> <skill>
  echo "== $2"
  npx -y skills@latest add "$1" --skill "$2" --agent '*' "$SCOPE" -y
}

install https://github.com/coreyhaines31/marketingskills --skill copywriting
install https://github.com/coreyhaines31/marketingskills --skill social
install https://github.com/blader/humanizer                --skill humanizer
install https://github.com/ajipurn/bahasa-indonesia-skill  --skill bahasa-indonesia

echo
echo "Installed into ${SCOPE} scope. Verify:"
echo "  ls ~/.agents/skills | grep -E 'copywriting|social|humanizer|bahasa-indonesia'"
echo
echo "Not installed here (ships with the Figma MCP server):"
echo "  figma-use, figma-generate-design  ->  skill://figma/<name>/SKILL.md"
