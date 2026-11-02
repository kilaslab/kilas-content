# Design variety

Every piece should look like the brand and not like the last piece. The constants carry
recognition; the variables keep the feed fresh. Variety follows the content: a variant
is chosen because its "use when" fits the slide's job, and among the variants that fit,
the one used least recently wins. Random variety looks like a template shop; chosen
variety looks like an editor.

`scripts/figma-helpers.js` implements every variant and every colour scheme below.
`scripts/figma-gallery.js` (with `figma-gallery-2.js`) draws all the layouts, and
`scripts/figma-gallery-schemes.js` one carousel in each scheme, in the brand's design;
the brand pack's `design.md` says where its gallery pages are. If the pack has a `refs/`
folder, it holds screenshots of how other accounts vary their designs. Look at both
before choosing.

## 1. Constants: never vary within a brand

- the fonts, and the colour roles inside each scheme (`design.md`)
- margins and grid: 88 px sides, 904 px content width, 1080×1350 frames
- the header (eyebrow, `03 / 08`, hairline) and the footer (site, swipe cue, progress bar)
- the logo lockup on the close, the credit style, the highlighter colour
- a series' own template (section 5)

## 2. Variables

| Knob | Options | Helper |
|---|---|---|
| Colour scheme | the brand pack's schemes (for example a default, a black-and-white, a dark, a loud accent, and a warm one) | `SCHEME`, `useScheme()`; `duotone(id, 'light' or 'dark')` uses the scheme's pairs |
| Cover | dark photo + number, split photo/text, type only on a coloured ground, chart, quote | `coverDark`, `coverSplit`, `coverType`, `coverChart`, `coverQuote` |
| Data | table, horizontal bars, columns over time, one big number, two-way versus, 100 dots, stat cards | `table`, `barChart`, `columnChart`, `bigStat`, `versus`, `dots`, `statCards` |
| Interior | plate + text, image beside text (left or right), full-bleed photo, labelled items, numbered steps, quote | `plate`, `splitPlate`, `fullBleed`, `labelledItems`, `steps`, `quote` |
| Evidence | screenshot plain, in a browser window with the real URL, tilted with a shadow | `artefact` with `style` |
| Opinion | action card, checklist, statement on a coloured ground | `tipCard`, `checklist`, `statement` |
| Close | dark with the photo thread, light | `closeSlide` with `variant` |
| Headline mark | highlighter, italic, accent colour, underline | `headline` marks `'hl'`, `'italic'`, `'color'`, `'underline'` |
| Ground | light, dark, primary, highlight | slide fills, `coverType`, `statement` |
| Accent | giant faint number, dot grid, tick strip | `decor` |

## 2b. Colour schemes

Large accounts do not post in one colour. Tirto's data cards are white and blue, its
photo news has a black headline box, its explainers are illustrated beige, and its own
offer is a blue gradient; the logo and its corner never change. Each look belongs to a
series, so a reader knows the series before reading.

A brand pack defines several schemes over the same roles (a light one, a black-and-white
one, a dark one, a loud one on the accent colour). The rules:

- **One scheme per piece.** Never switch schemes between slides of one carousel; vary
  the grounds inside it instead (`fullBleed`, `statement`, `coverType`).
- **A series keeps its scheme**, written in the brand pack.
- **One-off pieces rotate**: not the previous piece's scheme, the least recent among
  those that suit the story (a black-and-white newspaper look for a hard number, a dark
  terminal look for a test, the loud accent scheme for a list people save).
- **Photos follow the scheme**: tone them with the scheme's duotone pairs, so a
  black-and-white scheme gets black-and-white photos.
- Every helper picks its text colours by contrast, so every layout reads on every
  scheme; still look at the cover and the data slide after building.

## 3. What each variant is for

### Covers

| Variant | Use when |
|---|---|
| `coverDark` | an exact number with a scene, and a photo or illustration that can sit under a scrim (news with a record) |
| `coverSplit` | the image is part of the hook and should not be darkened (a product, a place, a person's work); a number or short claim below |
| `coverType` | a paradox, an opinion, or a question, and no image says it better; `bg: 'highlight'` for the loudest pieces, `'dark'` or `'primary'` for serious ones |
| `coverChart` | one finding from a dataset or survey; data series |
| `coverQuote` | a named person's words are the story (a portrait only with consent or an official press photo) |

### Data slides

| Variant | Use when |
|---|---|
| `table` | three or more metrics for the same items; the slide worth saving |
| `barChart` | one metric across items, ranked; `ref` for a threshold or average |
| `columnChart` | one metric over time or versions; a record against its history |
| `bigStat` | one ratio or share carries the slide, with two or three comparison bars |
| `versus` | exactly two things on one metric |
| `dots` | a percentage the reader should feel (share of people, share of code) |
| `statCards` | two or three numbers from different metrics, side by side |

### Interior, evidence, opinion, close

| Variant | Use when |
|---|---|
| `plate` + text | the default explaining slide |
| `splitPlate` | image and text matter equally; alternate `side` if used twice |
| `fullBleed` | the turn or the most emotional beat; one or two per carousel |
| `labelledItems` | causes, reasons, examples, each with a label |
| `steps` | a process, a learning path, how to do the action |
| `quote` | a person's own words carry the slide |
| `artefact` plain | dense evidence: a table, a log, text |
| `artefact` window | a web page or repo, so the URL is part of the proof |
| `artefact` tilt | one screenshot that should feel found (a post, a product page); not for dense tables |
| `tipCard` | one action |
| `checklist` | two to five checks the reader keeps |
| `statement` | one strong claim; the carousel's loud slide, usually the opinion |
| `closeSlide` dark | the default; continues the photo thread |
| `closeSlide` light | the slide before it is dark or loud, or the carousel ends quietly |

## 4. Rules

1. **Content first.** Only variants whose "use when" fits the slide's job are candidates.
2. **Then freshness.** Read `content/design-log.md`. Do not reuse the previous piece's
   scheme (unless the series fixes it), cover variant, or headline mark; among the
   candidates, take the one used least recently.
3. **Rhythm inside a carousel.**
   - No more than four slides in a row on a light ground. `layoutCheck()` notes five.
   - At least one slide breaks the pattern: `fullBleed`, `statement`, `coverType`'s
     ground, or a tilted artefact.
   - No two adjacent slides with the same layout, unless the carousel is a digest of
     equal items.
4. **One headline mark per carousel.** Switch between carousels: highlighter, then
   underline, then italic.
5. **Accents on at most two slides**, never on evidence slides, never two kinds on one
   slide except the tick strip under a dot grid.
6. **Bookends may differ.** A type cover with a dark close, or a dark cover with a light
   close.
7. **Write the plan first.** Fill the "Design" table in `brief.md` with a variant per
   slide, before building. After building, append a line to `content/design-log.md`.

## 5. Series keep their template

A series is recognised by its template (`planning.md` section 3). Its cover and its data
slide stay the same across episodes; vary only the headline mark, the accent, and the
interior slides. Variety rules apply to one-off pieces and between series, not inside a
series' fixed parts.

## 6. The same brand, four different carousels

| Story | Plan |
|---|---|
| News record (Linux 7.4) | default scheme · `coverDark` 19.671 · `plate` · `columnChart` with the old record · `quote` · `fullBleed` (the irony) · `splitPlate` (the turn) · `statement` (opinion) · `closeSlide` light; mark: highlighter |
| Benchmark (AI cost) | black-and-white scheme · `coverType` highlight (the paradox) · `splitPlate` · `table` · `labelledItems` · `artefact` window · `fullBleed` (the turn) · `checklist` · `closeSlide` dark; mark: underline |
| Survey finding (2 slides) | black-and-white scheme (its data series) · `coverChart` · `closeSlide` light; mark: italic |
| A tool test | dark scheme (its test series) · `coverType` dark · `steps` · `artefact` tilt · `versus` · `checklist` · `closeSlide` dark; mark: color |
| Story of a person (4 slides) | warm scheme · `coverQuote` with portrait · `fullBleed` · `fullBleed` · `closeSlide` dark; mark: none |

## 7. The design log

`content/design-log.md`, one row per piece, newest last (`templates/design-log.md`):

```markdown
| Date | Item | Scheme | Cover | Data | Opinion | Close | Mark | Accents | Breaks the pattern |
|---|---|---|---|---|---|---|---|---|---|
| 2026-11-02 | biaya-ai-framework-js | default | coverDark | table | tipCard | dark | hl | - | - |
```
