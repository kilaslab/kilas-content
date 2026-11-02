# HTML renderer: slides as HTML, rendered to PNG

For brands without Figma, or for pieces that do not need editing by hand. The same
layouts, schemes, and checks as the Figma helpers, written as HTML with the slide kit in
`templates/html/` and rendered to 1080×1350 PNGs by a headless browser.
`content/setup.md` says which renderer a brand uses.

## 1. Set up an item

```bash
python3 scripts/new_html.py content/items/<item> --brand <pack>/design.md [--scheme <scheme>]
```

It creates `content/items/<item>/html/` with `kit.css`, `kit.js`, `brand.css` (from the
pack's `BRAND` block, with every contrast decision per scheme precomputed), the brand's
logo files when `logo.image` is set, and `slides.html` copied from
`templates/html/example.html`, an 8-slide carousel showing the layouts. Edit
`slides.html`; put images in `html/img/`. `--blank` starts from one slide; `--refresh`
updates the kit and `brand.css` without touching `slides.html`.

## 2. Write the slides

One `<section class="slide ...">` per frame. The scheme is `data-scheme` on `<body>` (one
per piece). The kit adds the header (`data-eyebrow`, index), footer, progress bar,
scrims, the logo, and the handle; you write the content inside `<div class="content">`.

| Figma helper | HTML |
|---|---|
| `coverDark` | `section.slide.cover-dark` with `.duo.dark.bg > img`, `.content.bottom` holding `.big-number`, `p.lines`, `p.lede` |
| `coverSplit` | `section.slide.cover-split` with `.duo.light.top-photo > img` (+ `.credit`), `.content.bottom` holding `.big-number`, `.h1.s64`, `.body` |
| `coverType` | `section.slide.cover-type[data-bg=dark|highlight|primary|ground]`, `.content.bottom` holding `.kicker`, `.h1.s120`, `.lede`; optional `.decor-index` |
| `coverChart` | `section.slide.cover-chart` with `.h1.s72` and `.bars` |
| `coverQuote` | `section.slide.cover-quote`, `.content.center` holding `.qmark` (“), `p.quote`, `.who` (optional `.duo` portrait) |
| `table` | `table.data[data-max]`; rows `tr.hl` / `tr.pr` / `tr.strong`; `td.name`, `td.bar[data-v]`, `td.best` for the best value of a column; `p.table-note` |
| `barChart` | `.bars[data-max][data-ref][data-ref-label][data-row-h]` with `.bar-row[data-v](.hl|.pr) > b + .track > i + span` |
| `columnChart` | `.columns[data-values][data-ref][data-ref-label][data-hl][data-h][data-first][data-last][data-sep]` (built by the kit) |
| `bigStat` | `.bigstat` then `.body`, then a `.bars` for the comparison |
| `versus` | `.versus` with two `div`s (`.k`, `.num`, `p`) and `.vs` |
| `dots` | `.dots[data-pct][data-cols][data-width]` |
| `statCards` | `.cards` with `div`s (`.k`, `.num`, `b`, `p`) |
| `plate` | `.duo.light.plate` (height inline) + `p.credit` |
| `labelledItems` | `.items` with `div`s of `p.label` + `p` |
| `splitPlate` | `.split` (or `.split.right`) with `.duo.light` + a text `div` |
| `fullBleed` | `section.slide.full-bleed` with `.duo.dark.bg`, `.content.bottom` |
| `steps` | `ol.steps > li > b + p` |
| `quote` | `blockquote.q > p + cite` (`.q.big` for a larger one) |
| `artefact` | `figure.artefact(.window|.tilt)[data-url][data-marks] > .frame > img` + `figcaption.credit`; marks are image pixels from `scripts/artefact_marks.py` |
| `tipCard` | `.tip > p.label + p` |
| `checklist` | `.checklist > p.label + ul > li` |
| `statement` | `section.slide.statement[data-bg=highlight|primary|dark]`, `.content.bottom` holding `.h1`, `.body`, `.rule-mark`, `.tip-line`; optional `.decor-index.top` |
| `closeSlide` | `section.slide.close` (dark, with `.duo.dark.bg`) or `.close.light`: `.logo` (empty: filled by the kit), `h2.cta-head` with `span.handle`, `.promise`, `.pill` with `span.handle-up`, `.sources > p.label + ol + p.credits` |
| `decor` | `.decor-index(.top)`, `.decor-dots`, `.decor-ticks[data-values]` |

Headline marks inside `.h1`: `<mark>` (highlighter), `<em>` (italic), `<span class="c">`
(accent colour), `<u>` (underline). Like the Figma helpers, the kit adapts them to the
ground: on light text a highlighter becomes accent-coloured text, on a highlight ground
an underline. Images: `.duo.light` (plates) and `.duo.dark` (full-bleed) take the scheme's
duotone; `.duo.raw` keeps colour. Screenshots stay in colour inside `figure.artefact`.

Type classes: `.h1` (84; `.s64`, `.s72`, `.s96`, `.s110`, `.s120`), `.lines`, `.body`
(`.s28`, `.s30`, `.s34`), `.lede`, `.label`, `.credit`, `.soft`, `.kicker`. Layout:
`.content` (`.bottom`, `.center`, `.tight`, `.loose`), `.grow` to push a block down.

## 3. Render and check

```bash
python3 scripts/render_slides.py content/items/<item>/html/slides.html -o content/items/<item>/export
python3 scripts/render_slides.py .../slides.html -o .../export-2x --scale 2
python3 scripts/render_slides.py .../slides.html -o /tmp/try --scheme kertas   # try another scheme
```

It uses Python Playwright when installed, otherwise Chrome/Chromium headless, and prints
the kit's layout check (the same as `layoutCheck()` in Figma: text past the margins or
into the footer, slides that end above y = 945, type under 64 px, a cover with no visual,
five plain slides in a row). Fix every issue, render again, then look at the cover and
the data slide (`scripts/contact_sheet.py export -o export/sheet.jpg`).

Fonts load from Google Fonts, so rendering needs the network. A font that Google Fonts
does not have falls back to the system font: name a substitute in `design.md`.

## 4. Export

The PNGs are the Instagram, Threads, and TikTok photo frames. For a LinkedIn document:
`python3 scripts/slides_to_pdf.py content/items/<item>/export -o content/items/<item>/export/<slug>.pdf`.
The kit is built for 1080×1350 frames (header, footer, and checks assume that height).
For a 1080×1920 Reels cover, use the Figma renderer, or write a separate page without
the kit and screenshot it with your browser tool; keep text inside x = 100–880,
y = 270–1430 (`formats/reels-tiktok.md`).
