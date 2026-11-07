#!/usr/bin/env bash
# SPDX-License-Identifier: GPL-3.0-or-later
# Ask a second model (Codex CLI by default) to critique and brainstorm copy.
# See references/brainstorm-partner.md.
#
#   bash scripts/brainstorm.sh detect
#   bash scripts/brainstorm.sh run <item>/codex/brief-round1.md [--model gpt-6-luna]
#
# run writes <brief dir>/roundN.md (the answer) and roundN.log, where N comes from the
# brief's file name (brief-round2.md -> round2.md). Codex runs read-only and ephemeral:
# it can read files but cannot change the item.
set -euo pipefail

cmd="${1:-}"; shift || true

default_model() {
  local cfg="$HOME/.codex/config.toml"
  [ -f "$cfg" ] && sed -n 's/^model *= *"\(.*\)"/\1/p' "$cfg" | head -1
}

case "$cmd" in
  detect)
    if command -v codex >/dev/null 2>&1; then
      echo "partner: codex ($(codex --version 2>/dev/null | head -1)), model: $(default_model || echo default)"
    elif command -v gemini >/dev/null 2>&1; then
      echo "partner: gemini CLI (no codex found)"
    else
      echo "partner: none (no codex or gemini CLI); use a fresh subagent and report the gap"
      exit 1
    fi
    ;;
  run)
    brief="${1:?usage: brainstorm.sh run <brief.md> [--model M]}"; shift
    model="$(default_model || true)"
    while [ $# -gt 0 ]; do
      case "$1" in
        --model) model="$2"; shift 2 ;;
        *) echo "unknown option $1" >&2; exit 2 ;;
      esac
    done
    [ -f "$brief" ] || { echo "no such brief: $brief" >&2; exit 2; }
    dir="$(cd "$(dirname "$brief")" && pwd)"
    base="$(basename "$brief" .md)"
    n="${base##*round}"; [ "$n" = "$base" ] && n=1
    out="$dir/round$n.md"; log="$dir/round$n.log"
    command -v codex >/dev/null 2>&1 || { echo "codex not found; see brainstorm-partner.md section 2" >&2; exit 1; }
    margs=(); [ -n "$model" ] && margs=(-m "$model")
    codex exec "${margs[@]}" -s read-only --skip-git-repo-check --ephemeral -C "$dir" \
      -o "$out" - < "$brief" > "$log" 2>&1
    echo "answer: $out ($(wc -w < "$out" | tr -d ' ') words) · log: $log"
    ;;
  *)
    echo "usage: brainstorm.sh detect | run <brief.md> [--model M]" >&2; exit 2 ;;
esac
