---
name: kilas-content
description: "Plan and create social content end to end for any brand: a monthly content plan with pillars, series, and a calendar; researched pieces with a hook that earns attention; Instagram carousels and single posts built in Figma or rendered from HTML to PNG; Reels/TikTok scripts and storyboards; X posts and threads; LinkedIn posts and documents; Threads; and long-form posts that feed them. Use it whenever someone asks to plan content, make a content calendar, write or design a carousel, slides, a post, a thread, a Reels script, or repurpose an article into social posts, says \"buat konten\", \"bikin carousel\", \"rencana konten\", \"content plan\", or asks for a stronger hook. Each brand lives in a brand pack (voice, pillars, series, design tokens); on first use in a project it runs the setup-content skill (brand, assets, renderer)."
license: GPL-3.0-or-later
---

# Content: plan and create

Plan a brand's content and produce it end to end: a researched story, a hook that earns
attention, copy without AI tells, a build in the brand's design, and a publish sheet per
channel. Everything brand-specific lives in a **brand pack**; the method here works for
any brand. Frames are built in Figma or written as HTML and rendered to PNG, whichever
the brand chose at setup.

**The words decide whether anyone stops.** Most effort goes into research and writing,
before Figma or a camera. Read `references/writing-craft.md` and the three worked examples
before writing anything: `references/examples/linux-7.4-carousel.md` (a news record),
`references/examples/ai-cost-js-carousel.md` (someone else's experiment), and
`references/examples/weight-space-carousel.md` (a research paper made plain). Each lists the
drafts that lost and why; imitate the moves, not the sentences.

## Start here, every run

Paths to `scripts/`, `references/`, `templates/`, and `brands/` are inside this skill's
folder; `content/` is in the project you work in. Run commands from the project root
with the skill's path, for example `python3 <skill>/scripts/new_item.py content ...`
(`<skill>` is the folder this file is in). Scripts that use Pillow (`contact_sheet.py`,
`slides_to_pdf.py`, `artefact_marks.py`, `ref_sheets.py`) run without `python3 -I`.

0. **Setup check.** Read `content/setup.md` in the project. If it does not exist, this
   is the first run: run the **setup-content** skill (installed alongside; in this repository at
   `../setup-content/SKILL.md`; invoke it, or follow it by hand) before anything else. It
   asks which brand, collects the brand's own assets from its site and profiles with
   permission, chooses the renderer (Figma or HTML → PNG), and writes the brand pack.
1. **Find the brand pack** (`brands/README.md`): `content/brand/` in the project, else
   `brands/<name>/` in this skill. Read `brand.md`, `design.md`, and
   `content/brand/assets/README.md` if it exists (the brand's own photos and logos come
   before stock). Anything marked `(proposed)` is not settled; ask before a plan
   depends on it.
2. **Take stock of tools** and use every one that helps (`references/research-tools.md`):
   web search, page fetch, a real browser (`ego-browser`), social-media MCPs or built-in
   X access, Figma MCP, and image generation: your own image tool if you have one (Grok
   Bot's Grok Imagine, Codex, ChatGPT, Antigravity), then `python3 <skill>/scripts/gen_image.py
   detect` (agy, OpenAI, Gemini, xAI keys). Note what is missing.
3. **Find the workspace** (`templates/workspace.md`): `content/` with `plan/`, `items/`,
   `reviews/`, `ideas.md`, `design-log.md`. Create it the first time.
4. **Pick the mode** below.

| The user wants | Mode |
|---|---|
| a plan, a calendar, "rencana konten bulan ini" | Plan |
| one piece: carousel, single post, thread, Reels script, LinkedIn post, article | Create |
| several pieces from one source | Repurpose |
| to know what worked and what to change | Review |
| to set up a new brand, change the renderer, or refresh assets | Setup (the setup-content skill) |

## Plan

1. Read the inputs (`references/planning.md` section 1): brand pack, last review,
   `ideas.md`, the month's moments (verify dates), capacity, the owner's goal.
2. Write `content/plan/YYYY-MM.md` from `templates/plan-month.md`: pillars at their
   shares, series on their cadence, about a quarter of slots reactive, each strong item
   cut into 3–5 formats on different days.
3. `python3 <skill>/scripts/check_plan.py content/plan/YYYY-MM.md --brand <pack>/brand.md` until
   no FAIL; explain any warning you keep in the plan's notes.
4. Report: the month in three lines, what is proposed and needs a yes, the gaps.

## Create

1. **Item folder**: `python3 <skill>/scripts/new_item.py content <date> <slug> <format>`.
2. **Research** (`research-tools.md`): primary source, one link deep, corrections since
   publication, named people's own words, the local angle, a second source per number.
3. **Story** in `brief.md` (`writing-craft.md` sections 1–4): five questions, the turn,
   the ladder (berita, uji coba, daftar referensi, or a rubric from
   `copy-playbook.md`), the slide or post worth saving, five hooks in at least three
   shapes put through the gates and the duels, one metaphor family with its `Verbs:`
   line.
4. **Copy** in `copy.md` for the format (`references/formats/`: `carousel.md`,
   `single-post.md`, `x.md`, `threads.md`, `linkedin.md`, `reels-tiktok.md`,
   `long-form.md`), a `>` source
   note under every number, name, and quote. Every headline passes "lalu kenapa?" and
   the metaphor is in at least three of them; caveats go where `writing-craft.md` 7b
   puts them; the action passes "who, with what, when". Then
   `python3 <skill>/scripts/lint_copy.py <item>/copy.md --format <format> --brand <pack>/brand.md`
   must exit 0 (`new_item.py` prints the right `--format`: `thread` lints as `x`,
   `document` as `linkedin`). Read its warnings and its headline-only read; write that read into
   `brief.md`, and read the copy aloud once. Then the **reader pass**, as someone who has
   never seen the source: every key phrase describes what happens, not a term or a
   label for it (`writing-craft.md` 10b); each body opens with a sentence that links to
   the slide before, and no slide changes the subject (section 2); every metaphor
   headline still makes sense without slide 2 (section 4).
5. **Images** (`image-sourcing.md`): real artefacts on evidence frames; for metaphor
   frames the brand's own photos, then a generated image made automatically when
   nothing fits (your own image tool first, then `agy`, then a paid API only if
   `content/setup.md` allows it), then Unsplash; one visual thread, credits kept from
   the manifest. The owner can switch the image tool or stop generating at any time.
6. **Choose the scheme and the layouts** (`design-variety.md`): the series' colour
   scheme, or for a one-off piece one the previous pieces did not use; then a variant per
   slide by the slide's job and by what `content/design-log.md` says was used recently,
   so no two pieces look alike. Write them in the "Design" table of `brief.md`, with one
   headline mark style and one slide that breaks the pattern. The brand pack's gallery
   pages (Figma) or `content/setup-gallery/*.jpg` (HTML), and `refs/` when the pack has
   them, show the options.
7. **Build** with the renderer in `content/setup.md` (`design-system.md`); when it says
   both, follow its rule for which pieces go where, else ask:
   - **Figma** (`figma-mechanics.md`): the layout functions in
     `scripts/figma-helpers.js`, bundled with the pack's `BRAND` block by
     `scripts/figma_bundle.py --brand <pack>/design.md --page "<name>" --scheme <scheme>
     --n <frames>` (the tool takes 50,000 characters), on
     a new page of the brand's Figma file; never touch other pages. Upload images, then
     tone them in a second call with the scheme's pairs (`duotone(id, 'light' | 'dark')`).
   - **HTML → PNG** (`html-render.md`): `scripts/new_html.py` sets up the item's
     `html/` folder with the kit and the brand's CSS; write `slides.html` with the
     kit's layouts, with the chosen photos and generated images copied into `html/img/`;
     `scripts/render_slides.py` renders one PNG per slide.
   Reels: `storyboard.md` + a 1080×1920 cover frame (Figma, or a separate HTML page as
   `html-render.md` section 4 says).
8. **Verify cheaply**: the layout check first (`layoutCheck()` in Figma, the issues
   `render_slides.py` prints in HTML) and fix what it reports; then look at the cover,
   the data frame, and what changed (screenshots one at a time in Figma; the PNGs in
   HTML). If the user stops screenshots, stop and say which frames went unchecked.
9. **Publish sheet**: `publish.md` with the text per channel, hashtags within limits,
   alt text, time, links, credits; add a row to `content/design-log.md`. Publishing is
   the owner's step unless they explicitly ask you to post a specific piece through a
   connected tool; confirm first.
10. **Report**: where it is, the direction in two lines, the layouts chosen, what was and
    was not verified, which research tools you had and lacked, and the caption.

## Repurpose

Plan the cuts together (`planning.md` section 6), one item folder, one row per cut in
the plan. Each cut is rewritten for its format (`references/formats/`), says something
whole on its own, and links back. The carousel frames double as the LinkedIn document
(`scripts/slides_to_pdf.py`) and the Threads/TikTok photo post.

## Review

Write `content/reviews/YYYY-MM.md` from `templates/review-month.md`: numbers only from
the platform or the owner, dated;
compare each piece with the brand's own median for its format; decide keep, fix, or stop
per series; carry the decisions into next month's plan. No numbers shared: list what to
collect, and stop.

## Writing rules that carry the most weight

Full method in `writing-craft.md`, rules in `copy-playbook.md`, language in
`language/<lang>.md`.

- **Hook = exact number + scene + stakes**, or one of the six shapes in
  `writing-craft.md` section 3b. Write five in three shapes, gate them (≤30 words,
  plain, no caveat, honest, the answer held back, tension), duel the survivors, and
  write why each loser lost. Do not score them: self-scores tie.
- **Headlines are claims with a consequence**: each passes "lalu kenapa?". Topic words go
  in the eyebrow. Mark the one or two words that carry the claim.
- **One metaphor family**, said once, then carried in the verbs of at least three
  headlines, and only where the subject is still the same; a metaphor headline must read
  literally to someone who skipped slide 2.
- **Plain words**: describe what happens ("mengulang kalimat sampai kuotanya habis"),
  not the paper's term (thinking loop) or a label that sounds vivid ("macet berputar").
  Jargon goes to `>` notes or a table note.
- **One thread**: every slide answers the previous one and opens with a bridge
  sentence; a true but off-topic finding goes to the caption or its own post.
- **A turn late in the story**; **one frame or post worth saving**.
- **Bring it home**: the audience's own price, date, place, company, or action.
- **Numbers compare fairly**, charts start at zero, **hedges are copied** from the
  source, **first person** only for what the brand did.
- **Hedges stay in the sentence; caveats have a budget**: none on the cover or in a
  headline, one on the data slide, one on the opinion slide, the rest in the caption.
- **Opinion is labelled** and ends in an action that passes "who, with what, when".
- **One CTA** from the brand pack; the promise describes what the piece just did.
- **Language from the brand pack**; another language only when the user explicitly asks
  for it for that piece.
- **No stock openers, no AI tells**; the lint catches most.

## Quality gate

- [ ] Brand pack read; nothing `(proposed)` used as settled without asking.
- [ ] Every research tool available was used where it helps; gaps reported.
- [ ] Five story questions answered with the local angle; the turn placed.
- [ ] Hook workshop done with gates and duels; the cover is ≤30 words with no caveat
      and works alone.
- [ ] Headline-only read written in `brief.md` and tells the story; the metaphor is in
      at least three headlines; one piece worth saving, named.
- [ ] Reader pass done: plain words, bridge sentences, no detour, metaphor headlines
      read literally (owner feedback on the weight-space carousel, 4 Nov 2026).
- [ ] The action passes "who, with what, when".
- [ ] `lint_copy.py` exits 0 for the format; every number, name, and quote has a note.
- [ ] Platform limits respected (`formats/specs.md`): hashtags, characters, safe zones.
- [ ] Layouts chosen per slide in `brief.md`; cover and headline mark differ from the
      previous piece in `content/design-log.md`; one slide breaks the pattern.
- [ ] One scheme applied; the brand's own photos used where they fit; photos toned;
      screenshots in colour, unaltered, credited, marked with highlighter marks.
- [ ] Layout check clean (`layoutCheck()` in Figma, `render_slides.py` in HTML) or each
      note explained; cover and data frame seen (or the gap reported).
- [ ] Close: one CTA, all sources and credits; generated images labelled as illustrations.
- [ ] `publish.md` complete and a row added to `content/design-log.md`; nothing
      posted, liked, or followed without explicit consent.
- [ ] Plans pass `check_plan.py`.

## File map

| File | Read when |
|---|---|
| `brands/README.md`, `brands/<brand>/brand.md`, `design.md` | every run |
| `../setup-content/SKILL.md`, `references/brand-onboarding.md` | first run (no `content/setup.md`), a new brand, a new renderer |
| `references/planning.md` | planning, repurposing, reviewing |
| `references/writing-craft.md`, `references/examples/*.md` (three worked carousels with rejected drafts) | before writing anything |
| `references/copy-playbook.md` | frameworks, copy.md format, CTA, caption |
| `references/language/id.md`, `en.md` | the brand's language |
| `references/formats/*.md` | the format being made; `specs.md` for limits |
| `references/design-system.md`, `design-variety.md`, `design-references.md` | before building frames: roles, layout variants and how to choose them, patterns from other accounts |
| `references/figma-mechanics.md` | before the first `use_figma`; upload, duotone, screenshots |
| `references/html-render.md`, `templates/html/` | the HTML → PNG renderer: setup, class reference, render, check |
| `references/image-sourcing.md`, `research-tools.md` | research and images |
| `references/patterns-from-data.md` | why the rules are what they are |
| `references/prerequisites.md` | installing companions and optional tools |
| `templates/` | workspace, setup, plan, brief, publish, review, ideas, design log; `html/` (slide kit and example) |
| `scripts/` | `lint_copy.py`, `check_plan.py`, `new_item.py`, `figma-helpers.js` (layouts, schemes), `figma_bundle.py`, `figma-gallery.js` + `figma-gallery-2.js`, `figma-gallery-schemes.js`, `brand_css.py`, `new_html.py`, `render_slides.py`, `crawl_site.py`, `capture_profile.sh`, `artefact_marks.py`, `ref_sheets.py`, `slides_to_pdf.py`, `capture_artefact.sh`, `x_post.py`, `scan_site_tokens.sh`, `unsplash_search.py`, `gen_image.py`, `agy_image.sh`, `contact_sheet.py`, `export_oss.sh` |

## When not to use this

Not for a slide deck or presentation (use a slides skill), not for building a website,
and not for a one-word fix in an existing post (edit it directly).
