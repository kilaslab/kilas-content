#!/usr/bin/env bash
# SPDX-License-Identifier: GPL-3.0-or-later
# Ask a second model to critique, brainstorm, or score: copy, slide flow, or a Reel's stills.
# See references/brainstorm-partner.md.
#
#   bash scripts/brainstorm.sh detect [content] [--self claude|codex|gemini|grok|...]
#   bash scripts/brainstorm.sh run <dir>/brief-round1.md --self FAMILY [--partner NAME] [--model M] [--workspace content]
#
# detect lists every agent CLI on this machine in the default order
#   codex -> claude -> agy -> cursor-agent -> opencode -> gemini
# leaving out the one from the main model's own family (--self, or KILAS_SELF): the partner
# must be a different model from the one writing the content. It prints the partner the
# owner approved in content/setup.md ("Brainstorm partner:").
# With none approved yet it exits 4: ask the owner which one to use (it spends their
# subscription or quota), then write the line, e.g.
#   - Brainstorm partner: agy (approved by the owner 2026-11-10) · fallback: cursor-agent
#
# run sends the brief (a self-contained prompt file) to the approved partner, in a read-only
# mode, and writes <dir>/roundN.md (answer) and roundN.log, N taken from the brief's name.
# --partner overrides only with a partner the owner approved (the setup line or its fallback).
# Env: PARTNER_TIMEOUT seconds (default 600).
# Exit codes: 0 ok, 1 failure, 2 usage, 3 partner missing, 4 no approved partner, 5 timeout.
set -euo pipefail

ORDER=(codex claude agy cursor-agent opencode gemini)
cmd="${1:-}"; shift || true

family() {  # model family behind each CLI's default
  case "$1" in codex) echo openai ;; claude) echo claude ;; agy|gemini) echo gemini ;; *) echo mixed ;; esac
}
model_family() {  # family of an explicit model name, for the multi-vendor CLIs
  case "$(printf '%s' "$1" | tr 'A-Z' 'a-z')" in
    *claude*|*sonnet*|*opus*|*haiku*|*fable*) echo claude ;;
    *gpt*|o[0-9]*|*openai*|*codex*) echo openai ;;
    *gemini*) echo gemini ;; *grok*) echo xai ;; "") echo "" ;; *) echo other ;;
  esac
}
find_ws() {  # the content/ folder that holds setup.md: walk up from a path, else ./content
  local d; d="$(cd "$(dirname "$1")" && pwd)"
  while [ "$d" != "/" ]; do
    [ -f "$d/setup.md" ] && [ -d "$d/items" -o -d "$d/plan" ] && { echo "$d"; return; }
    [ -f "$d/content/setup.md" ] && { echo "$d/content"; return; }
    d="$(dirname "$d")"
  done
  echo content
}
self_family() {
  case "${1:-}" in claude*|anthropic) echo claude ;; codex|openai|gpt*) echo openai ;; gemini|google|agy) echo gemini ;; "") echo "" ;; *) echo "$1" ;; esac
}
available() {  # $1: the main model's family, left out
  for a in "${ORDER[@]}"; do
    [ -n "${1:-}" ] && [ "$(family "$a")" = "$1" ] && continue
    if command -v "$a" >/dev/null 2>&1; then printf '%s ' "$a"; fi
  done; return 0
}

approved_line() {  # the "Brainstorm partner:" line of content/setup.md, if any
  local setup="${1:-content}/setup.md"
  [ -f "$setup" ] && grep -m1 -i '^- Brainstorm partner:' "$setup" | sed 's/^- Brainstorm partner: *//' || true
}

approved_names() {  # first word of the line, plus anything after "fallback:"
  local line; line="$(approved_line "${1:-content}")"
  [ -z "$line" ] && return 0
  printf '%s\n' "$line" | awk '{print $1}'
  printf '%s\n' "$line" | sed -n 's/.*fallback: *//Ip' | tr ',' '\n' | awk '{print $1}'
}

codex_model() {
  local cfg="$HOME/.codex/config.toml"
  [ -f "$cfg" ] && sed -n 's/^model *= *"\(.*\)"/\1/p' "$cfg" | head -1 || true
}

with_timeout() {  # with_timeout SECONDS cmd...  (macOS has no coreutils timeout)
  local t="$1"; shift
  perl -e 'alarm shift; exec @ARGV or die "exec: $!"' "$t" "$@"
}

case "$cmd" in
  detect)
    ws="content"; self="${KILAS_SELF:-}"
    while [ $# -gt 0 ]; do
      case "$1" in --self) self="$2"; shift 2 ;; *) ws="$1"; shift ;; esac
    done
    fam="$(self_family "$self")"
    [ -n "$fam" ] || { echo "pass --self <your model family> (claude, codex, gemini, grok, ...): the partner must differ from you" >&2; exit 2; }
    found="$(available "$fam")"
    echo "available (main model family '${fam:-unknown}' left out): ${found:-none}"
    echo "mixed = Cursor agent and OpenCode run several vendors: pick a --model from another family"
    line="$(approved_line "$ws")"
    if [ -n "$line" ]; then
      echo "approved: $line"
      [ "$(printf '%s' "$line" | awk '{print $1}')" = "codex" ] && echo "codex model: $(codex_model || echo default)"
    else
      first="$(printf '%s' "$found" | awk '{print $1}')"
      echo "approved: none. Ask the owner before the first call; suggest '${first:-a fresh subagent}' and record the answer in $ws/setup.md"
      exit 4
    fi
    ;;
  run)
    brief="${1:?usage: brainstorm.sh run <brief.md> [--partner NAME] [--model M]}"; shift
    partner=""; model=""; ws=""
    while [ $# -gt 0 ]; do
      case "$1" in
        --partner) partner="$2"; shift 2 ;;
        --model) model="$2"; shift 2 ;;
        --self) KILAS_SELF="$2"; shift 2 ;;
        --workspace) ws="$2"; shift 2 ;;
        *) echo "unknown option $1" >&2; exit 2 ;;
      esac
    done
    fam="$(self_family "${KILAS_SELF:-}")"
    [ -n "$fam" ] || { echo "pass --self <your model family> (or set KILAS_SELF): the partner must differ from you" >&2; exit 2; }
    [ -f "$brief" ] || { echo "no such brief: $brief" >&2; exit 2; }
    ws="${ws:-$(find_ws "$brief")}"
    names="$(approved_names "$ws")"
    [ -n "$names" ] || { echo "no approved partner in content/setup.md; run detect and ask the owner" >&2; exit 4; }
    if [ -z "$partner" ]; then
      for n in $names; do
        [ -n "$fam" ] && [ "$(family "$n")" = "$fam" ] && continue
        if command -v "$n" >/dev/null 2>&1; then partner="$n"; break; fi
      done
      [ -n "$partner" ] || { echo "no approved partner outside the main model's family (${fam:-?}) is installed; run detect and ask the owner to approve one" >&2; exit 4; }
    elif ! printf '%s\n' $names | grep -qx "$partner"; then
      echo "$partner is not approved in content/setup.md" >&2; exit 4
    fi
    [ "$(family "$partner")" = "$fam" ] && { echo "$partner is the main model's own family; the partner must differ" >&2; exit 4; }
    if [ "$(family "$partner")" = mixed ]; then
      [ -n "$model" ] || { echo "$partner runs several vendors: pass --model from a family other than $fam" >&2; exit 2; }
      [ "$(model_family "$model")" = "$fam" ] && { echo "--model $model is the main model's own family ($fam)" >&2; exit 4; }
    fi
    [ -n "$partner" ] && command -v "$partner" >/dev/null 2>&1 || { echo "approved partner not installed: $names" >&2; exit 3; }
    dir="$(cd "$(dirname "$brief")" && pwd)"
    base="$(basename "$brief" .md)"
    n="${base##*round}"; [ "$n" = "$base" ] && n=1
    out="$dir/round$n.md"; log="$dir/round$n.log"
    prompt="$(cat "$brief")"
    t="${PARTNER_TIMEOUT:-600}"
    set +e
    case "$partner" in
      codex)
        [ -z "$model" ] && model="$(codex_model)"
        margs=(); [ -n "$model" ] && margs=(-m "$model")
        with_timeout "$t" codex exec "${margs[@]}" -s read-only --skip-git-repo-check --ephemeral -C "$dir" \
          -o "$out" - < "$brief" > "$log" 2>&1 ;;
      agy)
        margs=(); [ -n "$model" ] && margs=(--model "$model")
        with_timeout "$t" agy -p "$prompt" --mode plan --add-dir "$dir" "${margs[@]}" > "$out" 2> "$log" ;;
      cursor-agent)
        margs=(); [ -n "$model" ] && margs=(--model "$model")
        (cd "$dir" && with_timeout "$t" cursor-agent -p --mode ask --output-format text "${margs[@]}" "$prompt") > "$out" 2> "$log" ;;
      opencode)
        margs=(); [ -n "$model" ] && margs=(-m "$model")
        (cd "$dir" && with_timeout "$t" opencode run --agent plan "${margs[@]}" "$prompt") > "$out" 2> "$log" ;;
      claude)
        margs=(); [ -n "$model" ] && margs=(--model "$model")
        (cd "$dir" && with_timeout "$t" claude -p --permission-mode plan "${margs[@]}" "$prompt") > "$out" 2> "$log" ;;
      gemini)
        margs=(); [ -n "$model" ] && margs=(-m "$model")
        (cd "$dir" && with_timeout "$t" gemini "${margs[@]}" -p "$prompt") > "$out" 2> "$log" ;;
      *) echo "no recipe for $partner; add one here or use a fresh subagent" >&2; exit 3 ;;
    esac
    rc=$?
    set -e
    [ $rc -eq 142 ] && { echo "$partner stopped after ${t}s; narrow the brief ($log)" >&2; exit 5; }
    [ $rc -ne 0 ] && { echo "$partner failed (exit $rc); see $log" >&2; exit 1; }
    echo "partner: $partner · answer: $out ($(wc -w < "$out" | tr -d ' ') words) · log: $log"
    ;;
  *)
    echo "usage: brainstorm.sh detect [content] | run <brief.md> [--partner NAME] [--model M]" >&2; exit 2 ;;
esac
