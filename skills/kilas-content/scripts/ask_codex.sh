#!/usr/bin/env bash
# SPDX-License-Identifier: GPL-3.0-or-later
# Ask Codex (OpenAI's Codex CLI) for a second pass while planning or writing: content
# brainstorming, alternative copy, or research. The calling agent stays the editor:
# Codex's answer is saved as a file to read, check, and pick from, never pasted as is.
#
# Usage: scripts/ask_codex.sh <brainstorm|copy|research|review> <out dir> [context file ...] < prompt
#        CODEX_TIMEOUT=<seconds> (default 600) stops Codex and exits 5, keeping its log.
#
#   echo "10 ide konten untuk pemilik toko online" | scripts/ask_codex.sh brainstorm content/plan content/brand/brand.md
#   scripts/ask_codex.sh research content/items/<item>/codex content/items/<item>/brief.md < question.txt
#
# Runs `codex exec` read-only from the project root (it can read content/ and the skill,
# never write), with live web search for brainstorm and research. Writes
# <out dir>/codex-<task>-<time>.md and prints its path. 1–3 minutes for a narrow request.
# Exit 5: time limit reached (narrow the request). Exit 3: Codex missing or not signed in. Exit 4: Codex quota or rate limit reached; carry
# on without it and say so in the report. Exit 1: any other failure (log kept next to it).
set -euo pipefail

[ $# -ge 2 ] || { sed -n '2,17p' "$0"; exit 2; }
task="$1"; outdir="$2"; shift 2
case "$task" in brainstorm|copy|research|review) ;; *) echo "task must be brainstorm, copy, research, or review" >&2; exit 2 ;; esac
command -v codex >/dev/null || { echo "codex not found; continue without it" >&2; exit 3; }
codex login status >/dev/null 2>&1 || { echo "codex is not signed in (codex login); continue without it" >&2; exit 3; }
for f in "$@"; do [ -f "$f" ] || { echo "context file not found: $f" >&2; exit 2; }; done

ask="$(cat)"
[ -n "$ask" ] || { echo "write the request on stdin" >&2; exit 2; }
# Five numbered questions in one research call ran past 600 s twice on 2026-11-09: warn early.
nq="$(printf '%s\n' "$ask" | grep -cE '^[[:space:]]*[0-9]+[.)][[:space:]]' || true)"
if [ "$task" = research ] && [ "$nq" -gt 2 ]; then
  echo "warning: $nq numbered questions in one research call; split them into parallel calls (one question each) or it may hit CODEX_TIMEOUT" >&2
fi
mkdir -p "$outdir"
# The PID keeps parallel calls started in the same second from writing one file (2026-11-11).
stamp="$(date +%Y%m%d-%H%M%S)-$$"
out="$outdir/codex-$task-$stamp.md"
log="$outdir/.codex-$task-$stamp.log"

case "$task" in
  brainstorm) role="Brainstorm content ideas. Give many distinct options (angles, hooks, series ideas, formats), each in one or two lines with why it would stop this audience. Mark which need a source before use. Search the web for what is current when it helps." ;;
  copy) role="Write alternative copy for the brief: hooks, headlines, slide text, or captions as asked. Follow the brand pack's voice, address, banned phrases, and CTAs. Plain words, no AI tells, no invented numbers: leave [sumber?] where a fact is needed." ;;
  research) role="Research the question on the web. Prefer primary sources (official pages, papers, filings, the person's own post). For every fact give the link, the publisher, and the date, and copy hedges as written. Say what changed since publication and what you could not verify. Look for an Indonesian angle." ;;
  review) role="Review the draft as a strict editor: weak hook, claims without a source, jargon, slides that change the subject, AI tells, a CTA that does not fit. Quote the line, say the problem, suggest a fix." ;;
esac

skill_dir="$(cd "$(dirname "$0")/.." && pwd)"
prompt="You are helping another agent make social content with the content skill in $skill_dir. The brand pack is content/brand/brand.md and content/brand/design.md; read them first if they exist.
Task: $task. $role
Rules: read only, do not create or edit files, do not post anything anywhere. Answer in the brand pack's language (Indonesian unless it says otherwise), in Markdown.

Request:
$ask"
for f in "$@"; do prompt="$prompt

Context file $f:
$(cat "$f")"; done

args=(exec -s read-only --skip-git-repo-check --ephemeral --color never -o "$out")
case "$task" in brainstorm|research) args+=(-c 'web_search="live"') ;; esac

limit="${CODEX_TIMEOUT:-600}"
codex "${args[@]}" "$prompt" </dev/null >"$log" 2>&1 &
pid=$!
( sleep "$limit"; kill "$pid" 2>/dev/null && echo "time limit ${limit}s reached" >>"$log" ) &
watcher=$!
disown "$watcher" 2>/dev/null || true
status=0; wait "$pid" || status=$?
kill "$watcher" 2>/dev/null || true
if grep -q "time limit ${limit}s reached" "$log"; then
  rm -f "$out"; echo "codex stopped after ${limit}s; narrow the request ($log)" >&2; exit 5
fi
if [ "$status" -eq 0 ] && [ -s "$out" ]; then
  { printf '\n\n---\n> codex %s · %s · data to check, not settled copy\n' "$task" "$(date '+%Y-%m-%d %H:%M')"; } >>"$out"
  rm -f "$log"
  echo "$out"
  exit 0
fi
rm -f "$out"
if grep -qiE 'usage limit|rate limit|quota|429|too many requests|credits' "$log"; then
  echo "codex quota or rate limit reached; continue without it ($log)" >&2; exit 4
fi
echo "codex failed; see $log" >&2; exit 1
