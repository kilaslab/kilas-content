<!-- The block setup-content adds to the project's AGENTS.md (create the file if missing; keep
     what is there). Replace <skill> with the skill's path from the project root. -->
## Lessons come first

`content/lessons.md` holds what the owner, reviewers, and our own mistakes taught us
(`<skill>/references/self-improvement.md`).

1. Before planning or writing: `python3 <skill>/scripts/lessons.py rules content`. Active
   rules bind like the brand pack.
2. Before showing a draft: `lessons.py check content <item>/copy.md` (and `publish.md`) and
   `lint_copy.py` exit 0, and the render matches the design lessons.
3. The moment the owner gives feedback, a review finding is acted on, or you find your own
   mistake: `lessons.py add content ...`, then move the rule to its home.
4. Before calling any work done: `lessons.py audit content` exits 0 (every active rule has a home).
5. When the skill itself is wrong (a script fails, a reference contradicts a newer lesson, a
   pointer leads nowhere): heal it at its source (its repository, when it was installed from
   one), copy the fix back here, and run `python3 <skill>/scripts/skill_check.py` until it
   exits 0.
