# Design system

One layout system for every frame the skill builds (carousel slides, single posts,
Reels covers, X images, LinkedIn documents). It is written in **roles**; the brand
pack's `design.md` maps each role to a colour and a font, and may define several
schemes. `scripts/figma-helpers.js` (Figma) and `templates/html/kit.css` + `kit.js`
(HTML, `html-render.md`) implement it, and `scripts/figma_bundle.py` joins
the helpers, the brand's `BRAND` block, and your build code into one `use_figma` call
under the tool's 50,000-character limit.

## 1. Roles

### Colour

| Role | Used for |
|---|---|
| `ground` | light interior background |
| `text` | text on `ground` |
| `dark` | dark background of covers, closes, and dark schemes |
| `onDark` | text on `dark` and on photos (usually the light ground colour) |
| `primary` | big stats, the highlighted bar, tip cards, quote bars |
| `surface` | photo placeholders, quote cards, chips |
| `highlight` | marker behind key words, current progress segment, CTA pill, big number on `dark` |
| `muted` | labels, eyebrows, credits on `ground` |
| `mutedDark` | secondary text and plain chart bars on `dark` |
| `rule` | hairlines, gridlines, future progress segments |

Check contrast: text on `ground` and `onDark` on `dark` at 4.5:1 or better. A light
`highlight` (yellow, lime) never carries text on `ground` by itself; it sits behind
`text` as a marker.

A brand pack can define several **schemes**, each a full set of these roles plus a
duotone pair (`design-variety.md` section 2b). In a dark scheme `ground` is dark and
`text` light; the helpers choose text colours by contrast (`inkOn`, `accentOn`) and turn
a highlighter on light text into accent-coloured text, so every layout works on every
scheme.

### Type

| Role | Used for | Size at 1080 wide |
|---|---|---|
| `display` | headlines, cover number | 84–96 (cover number up to 290) |
| `displayItalic` | quotes, one accent line | 46–104 |
| `body` | paragraphs | 30–34, line height 145% |
| `bodyMedium`, `bodyBold` | names, emphasis | as body |
| `label` | eyebrows, index, footer, credits (often a mono) | 20–22, credits 18, uppercase, tracking 4–6% |
| `arrow` | a font that has `→` if `label` does not | as label |

Floors: body 30, labels 20, credits 18. A slide that needs smaller text has too much.

## 2. Grid (1080×1350)

| | |
|---|---|
| Margin / content width | 88 / 904 (keeps text clear of the 3:4 grid crop) |
| Header | eyebrow left + `03 / 08` right at y=70; hairline at y=116 |
| Content zone | y=150 to ≈1180 |
| Footer | site left + swipe cue right at y=1208; progress bar at y=1262 |
| Canvas placement | frame i at x = i×1200, y = 0, on the item's own page |

Other canvases: Reels cover 1080×1920 (text in x=100–880, y=270–1430; title in the
grid band y=240–1680); X landscape image 1600×900 (margin 80). See `formats/specs.md`.

## 3. Layouts

Every layout is a function in `scripts/figma-helpers.js`; do not redraw them by hand.
The HTML equivalents are classes in the slide kit (`html-render.md` section 2).
Which one to use for which slide, and how to vary them between pieces, is in
`design-variety.md`; `scripts/figma-gallery.js` shows them all in the brand's design.

| Role | Layouts (helpers) |
|---|---|
| Cover | `coverDark` (photo under a scrim + big number), `coverSplit` (photo top, text below), `coverType` (type on a coloured ground), `coverChart` (finding + bars), `coverQuote` |
| Data | `table` (consolidated, the save slide), `barChart`, `columnChart`, `bigStat`, `versus`, `dots`, `statCards` |
| Interior | `plate` + `headline` + `body`, `splitPlate`, `fullBleed`, `labelledItems`, `steps`, `quote` |
| Evidence | `artefact` (`plain`, `window`, `tilt`) with MULTIPLY highlighter marks |
| Opinion | `tipCard`, `checklist`, `statement` |
| Close | `closeSlide` (`dark`, `light`) |
| Accents | `decor` (`bigIndex`, `dots`, `ticks`) |

The ranked-list layout for a daftar referensi is `table` without bars: rank, name, a
one-line detail in the name column if needed, value columns right-aligned.

### Fill the frame

A phone shows the whole slide at once, so empty space reads as unfinished, not as calm.

- Interior content reaches about y = 1050–1150. `layoutCheck()` reports a slide that ends
  above y = 945: enlarge the proof element (a taller chart, larger numbers), raise the
  type size, or merge the slide into its neighbour.
- Headlines 72–84 px (cover and statement up to 120), body 30–32, labels 18–22. A slide
  whose largest text is under 64 px is reported.
- The open space a layout intends (the top of a `statement`, the scrim above a cover's
  text) is part of the design; fill it with an accent (`decor`) only when it looks empty
  in the screenshot.

Alternate grounds and layouts so a carousel has rhythm (`design-variety.md` section 4).
More layout patterns from other accounts, with when to use each, in
`design-references.md`.

## 4. Signature moves

- **A headline mark** on the one or two words that carry each headline's claim: the
  highlighter by default, or italic, accent colour, or underline (one style per
  carousel; `design-variety.md`). It is the visual twin of the writing rule in
  `writing-craft.md` section 5.
- **Segmented progress bar** in every carousel footer: done segments `primary`, current
  `highlight`, rest `rule`. Readers commit when they can see the length.
- **Duotone photos**: every stock or generated photo is greyscaled and toned between
  two brand colours, so photos from many sources read as one series
  (`figma-mechanics.md`, or the `.duo` classes in HTML). Screenshots stay in colour.
- **Honest chart**: bars from zero, the previous record as a dashed line, the record bar
  in `primary` with its label on the highlighter.

A brand pack may replace or add moves (a motif, a texture); it says so in `design.md`.

## 5. Chart recipe

- Left gutter 78 for axis labels, right-aligned, so labels never sit under bars.
- Gridlines in `rule`; baseline 2 px `text`; bars `mutedDark`, the previous record
  `muted`, the record `primary`.
- Dashed line (`figma.createLine`, `dashPattern [8, 6]`) at the old record, labelled at
  its left end where bars are low.
- Horizontal bar charts (surveys): sorted descending, value labels at the bar end, one
  bar in `primary`, the rest `mutedDark`.
- Two stat cells under a chart: number in `display` 80 `primary`, label in `body` 26
  `muted`.

## 6. No design pack yet

If the brand has no `design.md`, run the setup-content skill, which derives the schemes
(`brand-onboarding.md` section 3): take colours and fonts from the brand's site CSS or logo, map them to the
roles above, check contrast, and write `design.md` before building. Show the owner one
cover before building a whole set.
