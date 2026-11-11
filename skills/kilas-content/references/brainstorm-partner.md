# Brainstorm partner: a second model for copy and slide flow

One model writing and judging its own copy misses its own habits: translated-sounding
sentences, a jump between slides, a term only the writer understands. A second model
from a different family catches these, because it was trained differently. Owner feedback
on the pay-to-win carousel (7 Nov 2026) prompted this: the first draft passed the lint
and the reader pass and still "ga enak dibaca" for both beginners and seniors, so the
owner asked for Codex as a standing partner for copy and flow.

The partner advises; you decide. It never writes files in the item, never edits Figma,
and its suggestions pass the same rules as yours (`writing-craft.md`, `copy-playbook.md`,
`language/<lang>.md`, the lint). It knows only the brief you send. When it misreads the
story or invents a fact, that is a gap in your brief, or an idea to throw away.

## 1. When to call it

| Moment | What to ask | Why |
|---|---|---|
| Hook workshop (Create step 3) | five more hooks in shapes you did not use, then duel yours against theirs | your five hooks share your blind spots |
| After the first full `copy.md` passes the lint (Create step 4) | the full round in section 3 | catches translation, jargon, and flow problems before Figma, where text changes are slow |
| The owner says the copy reads badly | the full round, with the owner's words quoted | a fresh read finds what you stopped seeing |
| A plan's series names, pillars, or a rubric | two alternatives and the weakest point of yours | names stick for months |

Skip it for a one-word fix, for numbers and facts (those come from sources), and for
design choices (the brand pack and `design-variety.md` decide those).

## 2. Find the partner, with the owner's yes

Not every machine has Codex. The partner is always a **different model from the one writing the content**: two reads
by the same model share its blind spots. `bash <skill>/scripts/brainstorm.sh detect --self
<your family>` lists every agent CLI it finds, in this order, leaves out your own family,
and prints the partner the owner approved:

1. **Codex CLI** (`codex`, read-only `exec`; model from `~/.codex/config.toml`)
2. **Claude Code** (`claude -p --permission-mode plan`), the second choice whenever the
   main model is not Claude
3. **Antigravity CLI** (`agy -p --mode plan`, Gemini models)
4. **Cursor agent** (`cursor-agent -p --mode ask`) and 5. **OpenCode** (`opencode run
   --agent plan`): both run several vendors (Grok, GPT, Claude, ...), so pass a `--model`
   from a family other than yours
6. **Gemini CLI**, or any other agent CLI on the machine (add its read-only recipe to
   `brainstorm.sh`)

So with Claude writing: Codex, agy, Cursor agent, OpenCode, Gemini. With Codex or another
GPT writing: Claude, agy, Cursor agent, ... With Gemini or agy writing: Codex, Claude, ...

Each one spends the owner's subscription or quota, so **the first call needs the owner's
yes**: show what `detect` found, recommend the first one it lists, and write the answer as one line in `content/setup.md`:

```
- Brainstorm partner: agy (approved by the owner 2026-11-10) · fallback: cursor-agent, opencode
```

`brainstorm.sh run` only calls a partner named on that line (the first one installed, or
`--partner` with an approved name) and exits 4 otherwise. When the owner says no to all of
them, or none is installed, use a fresh subagent without this conversation's context if
your host has one, and say in the report that the partner was missing. The owner can
change the line any time ("pakai agy aja", "jangan pakai Cursor").

## 3. One round

1. **Write the brief** in the item's `codex/brief-round<N>.md` from
   `templates/brainstorm-brief.md`. Self-contained: brand voice and audience from the
   pack, the owner's thesis and limits, the writing rules that matter for this piece,
   the layout limits per frame (lines per headline, characters per label), what each
   illustration shows, the current copy without `>` notes, and the owner's own words if
   they gave feedback. The partner has no other context; whatever you leave out it will
   guess.
2. **Run it** read-only, in the background (high reasoning takes minutes):

   ```bash
   bash <skill>/scripts/brainstorm.sh run content/items/<item>/codex/brief-round1.md
   ```

   The answer lands in `codex/round1.md`, the log in `codex/round1.log`. Any other brief name
   (a second opinion, two partners on one question) answers in `<brief>-<partner>.md`, so
   nothing overwrites an earlier round; run two partners in parallel with `--partner`.
3. **Ask for reads, not only rewrites.** The template asks for: a slide-by-slide read
   by two readers (a beginner on free tools and a skeptical senior), flow breaks between
   slides, two options per frame within the layout limits, its pick with one reason, the
   headline-only read of its picks, and a caption.
4. **Judge every suggestion yourself.** For each frame write in `brief.md` under
   "Brainstorm": what the partner flagged, which option you took (yours, theirs, or a
   merge), and why. Reject a suggestion that breaks a rule, overstates the source, adds a
   number, changes the story, or does not fit the layout. Take a criticism even when you
   reject its rewrite: the problem it points at is usually real.
5. **Second round only on disagreement.** If you rejected its pick on a frame where the
   problem is real, send that frame back with your version and the reason, and ask it to
   attack it. Two rounds is enough; after that the owner decides.
6. **Lint and reader pass again** on the merged copy. The partner's text is not exempt.

## 4. What it is good and bad at

Good: hearing translation ("ikut menambah keunggulan"), spotting a term a beginner
cannot picture, finding the slide where the story jumps, offering a plainer verb,
writing alternatives in a register you did not try.

Weak: it does not see the frames, so it misjudges length; it may add numbers or claims
the source does not have; it likes slogans and "bukan X, tapi Y" reveals as much as any
model. Check each against the lint and the source notes.

## 5. Report it

Say in the report which partner you used (tool and model), how many rounds, and two or
three changes that came from it. Keep the brief and answer files in the item's `codex/`
folder; they show the owner why the copy changed.
