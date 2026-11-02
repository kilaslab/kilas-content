# Copy playbook

Every piece is written before it is drawn, filmed, or posted. This file holds the rules
that apply to all formats; `writing-craft.md` teaches the method, `formats/` the shape
of each format, `language/` the rules of each language.

## 1. Pick a framework

Match the story; never force it.

| The content is… | Framework | Shape |
|---|---|---|
| A stat, a news beat, a finding | **Problem-Proof** (berita ladder) | hook with the number → context → proof → cause → complication → turn → meaning → CTA |
| A list of tools or tips | **Value-Stack** | exact count + exact deliverable on the cover, one item per slide or post |
| A ranked set the reader will keep | **Daftar referensi** | count + threshold, ranked rows with a value column, method and source |
| Someone tested a tool, model, or device | **Uji coba** | setup and constraint → what happened → what worked → what failed → lessons → verdict |
| A viral case that touches the reader | **Explainer rubric** | apa yang terjadi → fakta → respons pihak terkait → imbauan (what to do) |
| Several small news items | **Digest** | date + lead story + "dan sejumlah kabar lain", one item per slide or post |
| A skill the reader wants | **Learning path** | what it is → what it is for → where to start → practice → next step |
| A person's story | **People story** | one sentence per frame over a real photo; the person's words, with permission |
| A report or long piece the brand made | **Report teaser** | thesis → 2–3 spotlights with stats → where to get the full thing |
| An opinion about a common practice | **Rant Callout** | provocative claim → specifics → fairness pivot → signed close |
| A product or workflow | **Demo Walkthrough** | result first → the pain → steps → positioning |

Ladders and hook shapes are in `writing-craft.md` sections 2 and 3b; visual layouts for
each framework in `design-references.md`.

## 2. copy.md format

Write the whole piece as text first, in the item folder's `copy.md`. One `## ` section
per slide, post, scene, or section:

```markdown
## 03 Data
eyebrow: DATA · 85 MERGE WINDOW SEJAK 2011
headline: Rekor lama dilewati 3.404 commit.
stat1: +21%
stat1label: dibanding rekor sebelumnya, Linux 7.3
> 19.671 − 16.267 = 3.404; 19.671 / 16.267 = 1,209. Source: Phoronix, 1 Nov 2026.
```

- `key: value` lines are text the audience sees. Use any keys the format needs
  (`headline`, `body`, `post`, `vo` for voice-over, `onscreen`).
- `>` lines are source notes for you, never published. Every number, name, and quote
  gets one; derived numbers show the arithmetic.
- `chart:`, `sources:`, `photos:`, `credit:`, `note:`, `image:`, `shot:` are builder
  notes; the lint skips them.
- A `## Caption` section holds the caption so the lint checks it too.

Then:

```bash
python3 scripts/lint_copy.py copy.md --format <carousel|single|x|threads|linkedin|reels|long> \
  --brand <brand pack>/brand.md
```

It detects Indonesian or English (or take `--lang`), fails on the hard tells in
`language/<lang>.md`, checks the format's length limits, and adds the brand's banned
phrases.

## 3. Language

Follow `language/<lang>.md` for the brand's language and the register in the brand
pack. A brand may write social in one language and long form in another; the brand
pack says which. Write in another language only when the user explicitly asks for it
for that piece; existing material in another language is not a reason to switch.

## 4. Hooks and headlines

The method (five questions, the ladder, the hook workshop with gates and duels, the
metaphor family carried in at least three headlines, the "lalu kenapa?" test, the
headline-only read) is in `writing-craft.md`. Patterns that worked, with real numbers:

- Exact number alone, then a scene line: **"19.671 / commit masuk ke kernel Linux dalam
  dua minggu."**
- A metaphor stated plainly: **"Anggap saja pintu air."**
- A headline that does the reader's arithmetic: **"Rekor lama dilewati 3.404 commit."**
- The irony as a fact, without the word "ironis": **"Penyaringnya sendiri sudah
  di-revert."**
- The local angle in the headline: **"iPhone 18 Pro Masuk Indonesia, Pre-order 7
  Oktober"** (the account's best post in the sample).

Avoid: "5 hal tentang X", "Kenali Y lebih dekat", a category instead of a number, and
anything a competitor could paste unchanged onto their own post.

## 5. CTA

- **One CTA per piece**, from the brand pack's CTA list, chosen by the pillar's goal:
  reach → follow; trust → read the long piece or subscribe; conversion → the product.
- The promise describes what this piece just did ("Kabar teknologi seperti ini, lengkap
  dengan angka dan sumbernya."). Never promise a frequency or a format you cannot keep.
- No stacked asks ("like, comment, share, save, follow").
- A reused CTA slide or line is fine and builds recognition; keep it current.

## 6. Caption (and post text around media)

A second chance at the same reader. Write it as a standalone post:

1. A first sentence that hooks on its own, in new words, with the key number. Only the
   start shows before "more" (~125 characters on Instagram, ~140 on LinkedIn mobile).
2. Two or three sentences that tell the whole story, including the turn.
3. One line pointing into the media ("Geser untuk lihat datanya.").
4. The source, and the caveats that had no place on the slides (`writing-craft.md`
   section 7b); then one question **only** if it offers a real choice about this topic.
5. Hashtags within the platform's limit (`formats/specs.md`): series tag + 1–2 topics.

## 7. Before delivering

Run the headline-only test, the lint, and read the copy aloud. Read every hook as if it
were the only thing in the feed. If a line would work unchanged on another account,
rewrite it or cut it.
