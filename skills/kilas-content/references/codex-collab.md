# Working with Codex: a second brain for ideas, copy, and research

When the Codex CLI is installed and signed in, and it still has quota, ask it for a
second pass at the steps where two minds beat one: brainstorming, copywriting, and
research. You stay the editor. Codex's answer is a file of options and leads; you
check it, pick, and rewrite in the brand's voice. Nothing Codex writes goes into
`copy.md` or a plan unchecked.

Skip this section when you are Codex yourself.

## 1. Check it once per run

```bash
command -v codex && codex login status
```

`content/setup.md` says whether the owner allows it (`Codex: yes | no`). No line, or
`yes`: use it. The owner can switch it off or on any time by asking ("jangan pakai
Codex", "minta Codex juga").

## 2. When to ask

| Step | Task | What to send | What to take from it |
|---|---|---|---|
| Plan, ideas for the month | `brainstorm` | goal, pillars, the month's moments, `ideas.md` | angles and series ideas you had not listed; merge into `ideas.md`, then plan as usual |
| Create, research (step 2) | `research` | the question and the source you already have | primary sources, corrections, an Indonesian angle; open every link and check it yourself before a number goes in |
| Create, story (step 3) | `brainstorm` | `brief.md` with the five questions answered | extra hooks in other shapes; put them through the same gates and duels as yours |
| Create, copy (step 4) | `copy` | `brief.md`, your draft `copy.md` | alternative headlines or captions for the weak spots only |
| Create, before lint | `review` | `copy.md` | a strict editor's notes; fix what holds up, ignore the rest |

Run research while you write something else. A narrow question takes 1–3 minutes; a broad one
(several competitors × several questions, with browsing) ran 25+ minutes on 2026-11-09. Ask one
competitor or one question per call and run calls in parallel; the script stops Codex after
`CODEX_TIMEOUT` seconds (default 600, exit 5). One or two calls
per item is usually enough; do not ask Codex for what you can settle in one search.

## 3. How

```bash
echo "Riset: berapa persen UMKM Indonesia jualan lewat WhatsApp? Sumber primer, tanggal." \
  | <skill>/scripts/ask_codex.sh research content/items/<item>/codex content/items/<item>/brief.md
```

The script runs Codex read-only from the project root (it can read the brand pack and
this skill, never write), with web search for `brainstorm` and `research`, and prints
the path of `codex-<task>-<time>.md`. Pass the sources you already verified as context files, or Codex will flag checked facts as
unsourced. Write the request as you would brief a colleague:
the audience, what you already have, what you need back, and the format.

Exit codes: `0` done; `3` Codex missing or signed out; `4` quota or rate limit reached;
`1` other failure. On `3` or `4`, carry on alone and say so in the report ("Codex: kuota
habis, riset tanpa second opinion"). Never wait or retry in a loop.

## 4. Using the answer

- **Facts**: every number, name, and quote Codex found gets the same treatment as your
  own: open the link, check the date and the hedge, then the `>` source note. A link you
  could not open is not a source.
- **Ideas and hooks**: they enter the workshop on equal terms; the duel decides, not
  who wrote it. Note in `brief.md` which survivor came from Codex.
- **Copy**: take a line, never a whole draft; rewrite it in the pack's voice and run
  `lint_copy.py` as usual.
- Keep the `codex/` files in the item folder; they are the record of what was suggested.
- Report which steps used Codex, and which ran without it and why.
