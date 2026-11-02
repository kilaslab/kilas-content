# English

Rules for copy in English. Register comes from the brand pack. If the `humanizer` and
`copywriting` companion skills are installed, they go deeper.

## Sentences and words

- Plain words, short sentences, one idea each, lengths varied.
- Verbs over nouns: "we cut support tickets in half", not "a reduction in support
  ticket volume was achieved".
- Concrete nouns and real numbers: "a bot that binds random drivers", not "problematic
  automated activity".
- Numbers: `19,671`, `9.43%`, `$299`; ranges `12–14k`.
- "We" only for what the brand did; "you" only where you speak to the reader.

## AI tells and stock lines

Act on one sighting. `scripts/lint_copy.py --lang en` catches most of these.

| Tell | Example | Fix |
|---|---|---|
| Contrast reveal | "It's not X, it's Y"; "not just X, but Y" | state Y with its reason |
| Negation list | "No X. No Y. No Z." | say what does happen |
| Colon reveal | "The result? 3x faster." | "It runs three times faster." |
| One-line closer | "And that changes everything." | cut it |
| Forced triad | "fast, simple, and powerful" | keep what the meaning needs |
| Em dashes as connectors | "— and that's the point" | a period or a comma |
| Stock openers | "In today's fast-paced world", "Let's dive in", "Here's the thing" | start with the fact |
| Inflated significance | "a pivotal moment", "game-changer", "landscape", "revolutionary", "delve", "unlock", "seamless" | keep the fact |
| Sales language | "incredible", "stunning", "unforgettable" | show it with a number |
| Engagement bait | "Agree?", "Tag a friend", "Save this for later" | a real question, or nothing |
| Broetry | one short line per paragraph for the whole post | write paragraphs |
| Exclamation marks | "Sign up now!" | a period |
