# Carousel (Instagram, LinkedIn document, Threads, TikTok photo)

One set of 1080×1350 frames serves four platforms: an Instagram carousel, a LinkedIn
document (the same frames as a PDF), a Threads carousel, and a TikTok photo post. Build
once with the renderer in `content/setup.md` (Figma or HTML → PNG), export per platform
(section 6).

## 1. Length

In the Instagram sample (`patterns-from-data.md`), 33 carousels from 8 Indonesian
accounts averaged 4.6 slides, range 2–9:

| Kind | Slides | Example in the data |
|---|---|---|
| Fast news with a price or date | 2 | cover + price list in Rupiah |
| One chart | 2 | chart cover + the brand's own CTA slide |
| Explainer, news story | 5–9 | fixed rubric: apa yang terjadi, fakta, respons, imbauan |
| Story of a person | 3–4 | one sentence per slide over a real photo |
| Learning path | 6–7 | what it is, what it is for, where to start, practice, CTA |

Cut to the real count. A padded slide costs more swipes than it earns.

## 2. Ladder and slide roles

Pick the ladder in `writing-craft.md` section 2 (berita, uji coba, daftar referensi),
or one of the rubrics in `design-references.md` (explainer, digest, learning path,
people story, report teaser). The default 8-slide news ladder:

1. **Hook**: exact number + scene + stakes. Works alone as a feed post.
2. **Konteks**: the mechanism in one everyday metaphor, plus what "normal" looks like.
3. **Bukti**: the data slide (section 2b), or a real artefact when the evidence is a
   document rather than numbers.
4. **Penyebab**: the driver, in a named person's own words.
5. **Komplikasi**: the irony or the thing that went wrong.
6. **Sisi lain**: the turn.
7. **Makna**: the brand's analysis, labelled as opinion, ending in an action. Usually
   the slide worth saving.
8. **Ajakan**: one CTA from the brand pack + every source and image credit.

## 2b. The data slide

| The source gives you | Build |
|---|---|
| one metric for several items | `barChart`, sorted, from zero; `ref` for a threshold |
| one metric over time or versions | `columnChart` with the old record as a dashed line |
| three or more metrics for the same items | `table`: rank, name, a bar for the main metric, value columns, the highlighter on each column's best, one caveat as the note. This is the slide worth saving |
| one ratio or share | `bigStat`, or `dots` for a percentage |
| two things on one metric | `versus` |

Build it in the brand's design from the primary source's numbers, with the source in the
note. A screenshot of someone else's chart belongs on a claim slide, or on the data slide
only when the chart itself is the news. A draft that put a screenshot of the source's
cost chart on its data slide lost the four other metrics and the brand's look; the
consolidated table is what readers save.

## 2c. Choose the layouts

Before building, fill the "Design" table in `brief.md`: a variant per slide from
`design-variety.md`, chosen by the slide's job, then by what `content/design-log.md` says
was used recently. Plan one slide that breaks the pattern, and one headline mark style
for the whole carousel.

## 3. copy.md

One `## ` section per slide, `key: value` lines for text on the slide, `>` lines for
source notes that are never drawn (format in `copy-playbook.md` section 2). Then:

```bash
python3 scripts/lint_copy.py copy.md --format carousel --brand <brand pack>/brand.md
```

## 4. The close slide

Two jobs:

1. **One CTA** from the brand pack's CTA list, matched to the pillar's goal (follow for
   reach, newsletter or site for trust, product for conversion). Headline = the CTA
   ("Ikuti @<handle>"), one line that describes what this piece just did, one button or
   pill. Do not promise a frequency or format you cannot verify. Big media accounts
   reuse one standard CTA slide for months (Katadata's Databoks offer, Tirto's
   "Traktir Kopi"); a brand can keep one per CTA and reuse it.
2. **Credits**: every source with its date, every photographer, `Tangkapan layar: ...`
   for artefacts, `Ilustrasi: AI (...)` for generated images.

The footer cue on the last slide reads the brand's "end" word (`SELESAI`), not the swipe
cue. A sponsor's ad is never the close; sponsored pieces are labelled from the cover
(`planning.md` section 8).

## 5. Caption, hashtags, alt text

- **Caption** as a standalone post (`copy-playbook.md` section 6): a first sentence that
  hooks on its own (only ~125 characters show before "more"), two or three sentences
  with the whole story, one line into the slides, the source.
- **One question at the end is allowed** when it offers a real choice about this topic
  ("Ikut pre-order atau tunggu harga turun?"). Generic bait ("Setuju?") is not.
- **Hashtags**: Instagram allows 5. Use the series tag from the brand pack plus one or
  two topic tags; Threads takes one topic tag.
- **Alt text** for every slide: what the slide says and shows, in one or two sentences.
  Write them in `publish.md`.

## 6. Export per platform

| Platform | What to post |
|---|---|
| Instagram | the frames as images, caption, ≤5 hashtags, alt text |
| LinkedIn | the frames as one PDF (`scripts/slides_to_pdf.py`, or Figma's export), a post written for LinkedIn (`linkedin.md`), document title = the cover headline |
| Threads | the frames (up to 20), a ≤500-character post, one topic tag |
| TikTok | photo post (up to 35), caption, add music in the app |
| X | not a carousel: post the cover or the data slide with a thread (`x.md`) |

## 7. Checklist

- [ ] Slide count fits the kind; no padding.
- [ ] Cover passed the gates and won its duels; at most 30 words, no caveat.
- [ ] The metaphor is in at least three interior headlines; each passes "lalu kenapa?".
- [ ] Caveats are where section 7b of `writing-craft.md` puts them; the action passes
      "who, with what, when".
- [ ] Layouts chosen in `brief.md` (`design-variety.md`): the cover and headline mark
      differ from the previous piece; one slide breaks the pattern.
- [ ] `layoutCheck()` (Figma) or `render_slides.py` (HTML) reported no issues, or each
      one is explained.
- [ ] Headline-only read tells the story.
- [ ] One slide worth saving, and you can name it.
- [ ] Cover works as a thumbnail in a 3:4 grid tile (nothing important in the outer
      90 px).
- [ ] Close: one CTA, all credits.
- [ ] Caption, hashtags (≤5), and alt text written in `publish.md`.
- [ ] A row added to `content/design-log.md`.
