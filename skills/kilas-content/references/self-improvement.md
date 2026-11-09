# Self-improvement: every lesson changes the next run

The skill gets better for a brand only if what the owner, reviewers, and our own mistakes
teach us is written down where the next run (yours, Codex's, another agent's) will read
it. The record is `content/lessons.md`, kept with `scripts/lessons.py`.

## The loop

1. **Read** before any plan or piece: `python3 <skill>/scripts/lessons.py rules content`.
   Treat every active rule as binding as the brand pack.
2. **Check** every piece: `python3 <skill>/scripts/lessons.py check content <item>/copy.md`
   next to `lint_copy.py`; both must exit 0. Rules without a `Check:` pattern (visual,
   process) are checked by eye against the render before showing the owner.
3. **Capture** the moment a lesson appears, before continuing the work:
   - owner feedback of any size: a rejection, a "jangan", a preference, a "kenapa";
   - a review finding (Codex `review`, your own reader pass) that you acted on;
   - your own mistake found in verification (a broken page, a wrong number, a stale date);
   - a result: a piece the owner approved or rejected, and a metric from the monthly review.

   `python3 <skill>/scripts/lessons.py add content --source <owner|review|codex|mistake|metric> --area <tone|copy|design|research|process|tools> --lesson "<what happened>" --rule "<what to do from now on>" [--check "<regex>"] [--applied "<where else>"]`

   Write the rule positively (the behaviour to produce). Add a `--check` regex only for a
   phrase or pattern that can be caught in published text.
4. **Promote** the rule to its home, then name it under `Applied:`:
   - brand voice or claims → `brand.md` (Banned phrases, Compliance, Voice);
   - colours, layouts, mascot use → `design.md`;
   - a method that holds for any brand → the skill's own reference or script, so other
     brands inherit it;
   - the agent's own working habit → the agent's memory and `AGENTS.md`.
5. **Retire** a lesson the owner reverses: `Status: retired` plus one line why. Keep it;
   the history explains later choices.

## In the monthly review

Count lessons by area. An area that keeps growing is a weak spot in the method: fix the
reference or script behind it rather than adding more rules. Merge lessons that say the
same thing into one.

## Done when

The lesson is in `content/lessons.md`, its rule is in its home (or `Applied: lessons.md
only` with a reason), and the piece in progress already follows it.
