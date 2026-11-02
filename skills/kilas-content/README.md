# Content skill: plan and create

An agent skill that plans a brand's social content and produces it end to end: a monthly
plan with pillars, series, and a calendar; researched pieces with hooks that earn
attention; Instagram carousels and single posts built in Figma or rendered from HTML to
PNG; Reels/TikTok scripts and storyboards; X posts and threads; LinkedIn posts and
documents; Threads; and the long-form pieces that feed them.

The method is brand-agnostic. Everything about one brand (voice, audience, pillars,
series, cadence, CTAs, colours, fonts, logo) lives in a **brand pack** under `brands/`
or in the brand's own project at `content/brand/`.

## First run

The first time the skill is used in a project, the **setup-content** skill (in
`../setup-content/`, installed alongside) asks which brand the content is for, reads the
brand's website and social profiles with permission and collects its own logo, colours,
fonts, photos, and voice for reuse (`scripts/crawl_site.py`, `scripts/capture_profile.sh`),
and asks how frames should be made: in **Figma** (Figma MCP) or as **HTML rendered to
PNG** (`templates/html/` kit, `scripts/render_slides.py`, Playwright or Chrome). It
writes the brand pack and `content/setup.md`.

## Install

Put this folder in `~/.agents/skills/` (or symlink it there) and link it into each
agent's skills directory; see `references/prerequisites.md` for the hub layout and the
companion skills (`copywriting`, `social`, `humanizer`, `bahasa-indonesia`), installed
with `scripts/install-companions.sh`.

Optional tools make it better and are detected at run time: web search and fetch,
`ego-browser`, social-media MCPs, the Figma MCP (for Figma frames), Python Playwright or
Chrome/Chromium (for HTML → PNG frames), and the Antigravity CLI `agy` for generated
images.

## Use it

> rencana konten bulan November buat brand ini
>
> bikin carousel dari artikel ini <link>, taruh di Figma
>
> jadikan catatan ini thread X, post LinkedIn, dan naskah Reels
>
> review konten bulan lalu, apa yang harus diubah

A new brand starts with onboarding: the skill reads the brand's site and posts, asks up
to eight questions, and writes the brand pack.

## Layout

```
SKILL.md                          modes (plan, create, repurpose, review, onboard), workflow, quality gate
brands/
  README.md                       what a brand pack is and where the skill looks
  _template/                      brand.md + design.md to copy for a new brand
  <brand>/                        private packs (not exported)
references/
  planning.md                     pillars, series, cadence, moments, repurposing, batching, review loop
  brand-onboarding.md             writing a brand pack
  writing-craft.md                story, ladder, hook workshop, metaphor, headlines, numbers, hedges
  examples/                       two finished carousels, why each line works, and the drafts that lost
  copy-playbook.md                frameworks, copy.md format, CTA, caption
  language/id.md, en.md           language rules and AI tells
  formats/                        carousel, single post, Reels/TikTok, X, LinkedIn, Threads, long form, specs
  design-system.md                roles, grid, layouts, fill rules, signature moves, chart recipe
  design-variety.md               layout variants per slide role and how to vary them between pieces
  html-render.md                  the HTML → PNG renderer: class reference, render, check
  design-references.md            layout patterns from Indonesian media and creator accounts
  figma-mechanics.md              session, pages, upload, duotone, cheap verification
  image-sourcing.md               artefacts, Unsplash, generated images, honesty rules
  research-tools.md               web search, browsers, social tools, image rights
  patterns-from-data.md           what scraped X and Instagram posts taught, and what they did not
  prerequisites.md                companion skills and optional tools
templates/                        workspace, setup, plan-month, brief, publish, review-month, ideas, design-log
  html/                           slide kit (kit.css, kit.js) and an 8-slide example for the HTML renderer
scripts/
  lint_copy.py                    AI tells, language slips, platform limits, brand banned phrases
  check_plan.py                   a month plan against the brand pack
  new_item.py                     an item folder from the templates
  figma-helpers.js                layouts for use_figma: 5 covers, 7 data views, interiors, evidence frames, opinion, close, accents; colour schemes; layoutCheck
  figma_bundle.py                 helpers + BRAND + your build, unused layouts dropped, under use_figma's 50,000-character limit
  figma-gallery.js, -2.js         every layout variant on one page, spread across the brand's schemes
  figma-gallery-schemes.js        one carousel in each of the brand's colour schemes
  ref_sheets.py                   reference sheets from a scraped carousel dataset (for a private brand pack)
  crawl_site.py                   the brand's own logo, icons, colours, fonts, photos, social links from its website
  capture_profile.sh              a social profile's grid screenshot, bio, and post images (real browser, read only)
  brand_css.py                    a brand pack's BRAND block as CSS for the HTML renderer
  new_html.py                     an item's html/ folder with the slide kit, the brand's CSS, and an example
  render_slides.py                slides.html to one PNG per slide (Playwright or Chrome), with the layout check
  artefact_marks.py               row and word coordinates for highlighter marks on screenshots
  slides_to_pdf.py                frames to a LinkedIn document PDF
  capture_artefact.sh             a page region at 2x with ego-browser
  x_post.py                       a public X post and its full-size photos, no login
  scan_site_tokens.sh             a site's colours and fonts, for onboarding
  unsplash_search.py              Unsplash search with credits
  agy_image.sh                    generated images with the Antigravity CLI
  contact_sheet.py                labelled grid for choosing images
  install-companions.sh           install the companion skills
  export_oss.sh                   a brand-free copy of the skill
evals/                            test prompts for the core skill
```

## License

GPL-3.0-or-later. See `LICENSE`. Copies and modified versions you distribute must stay
under the GPL and ship their source.

## Export a brand-free copy

```bash
scripts/export_oss.sh <dest-dir> <skill-name>
```

Copies the skill without private brand packs, rewrites the front matter, and fails if a
private brand name is still mentioned anywhere.
