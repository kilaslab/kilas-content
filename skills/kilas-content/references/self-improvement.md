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
5. **Supersede or retire.** A newer lesson that replaces part of an older one:
   `Status: active; partly superseded by L-NNN (what changed)` on the old one, which still
   binds for the rest. One that replaces all of it: `Status: superseded by L-NNN (why)`. A
   lesson the owner reverses: `Status: retired` plus one line why. Keep them all; the
   history explains later choices. Then sweep: search the skill and the brand pack for the
   old rule's words and change every place that still says it ("AI → ei-ai" outlived the
   rule that replaced it in an example and in a script message, Nov 2026).
6. **Audit** before calling the work done: `python3 <skill>/scripts/lessons.py audit content`
   exits 0. It fails when an active lesson names no home outside its item, when a file it
   names is gone, or when a status points at a lesson that does not exist. Twenty-six rules
   once sat in `lessons.md` naming only the piece or plan they came from, so no other brand
   and no later piece would have read them; this check exists for that.

## When the skill itself is wrong (self-heal)

The signs: a script fails on a valid input (`scene_stills.sh` wrote nothing when given an
absolute output prefix), a reference contradicts a newer lesson, a pointer leads to a file that
is not there, a check passes what the owner then catches, a small model following the
steps gets stuck. Then, before the piece goes on:

1. Fix it where the skill comes from. If the project holds a copy of a skill kept in its
   own repository, fix it there on a branch and copy the change back into the project, so
   the next install does not bring the bug back.
2. Make it catchable: a script's own input check, a `lint_copy.py` pattern, a `Check:` on
   the lesson, or a done-check in the worked example.
3. Run `python3 <skill>/scripts/skill_check.py`: front matter, every pointer, every script
   listed and parsing. Exit 0.
4. Record a lesson (`--source mistake --area tools`) whose `Applied:` names the fix.

## In the monthly review

Count lessons by area. An area that keeps growing is a weak spot in the method: fix the
reference or script behind it rather than adding more rules. Merge lessons that say the
same thing into one. Run `lessons.py audit content` and `skill_check.py`; fix what fails.
Give one worked example to a smaller model and note where it stalls: each stall is a
missing step, a vague done-check, or a template that hides a rule.

## Done when

The lesson is in `content/lessons.md`, its rule is in its home (or `Applied: lessons.md
only: <reason>`), `lessons.py audit content` exits 0, and the piece in progress already
follows it. After a fix to the skill, `skill_check.py` exits 0 as well.
