# Eval prompts (core)

Brand-agnostic asks the skill should handle. Run one against a brand pack, then judge
the output against the quality gate in `SKILL.md`. Brand packs can add their own evals
in `brands/<brand>/evals/`.

## 1 — Onboard a new brand

> aku punya toko roti di Bandung, @<handle>, websitenya <url>. bantu bikin rencana konten

Good: no `content/setup.md`, so the setup-content skill runs first; one round of ≤ 8
questions that includes permission to collect assets and the renderer choice; with
permission, `crawl_site.py` and `capture_profile.sh` fill `content/brand/assets/` and
its README (a parked site or empty profile is reported, not hidden; partner logos are
not downloaded); `content/brand/brand.md` and `design.md` in the template's format, the
colours and fonts taken from the site, at least three schemes, the brand's logo in
`logo.image`; pillars and series marked `(proposed)`; a gallery before any full build;
`content/setup.md` written; no tech-brand vocabulary leaking in.

## 1b — No Figma

> kami tidak pakai figma, langsung jadi gambar saja

Good: setup records the HTML renderer; a carousel is written as
`content/items/<item>/html/slides.html` with the kit's classes (no inline layout hacks
where a class exists); `render_slides.py` prints no issues; the PNGs are 1080×1350, one
per slide, in `export/`; the scheme is one of the pack's.

## 1c — Images without asking

> bikin carousel dari artikel ini <url>  (run in Grok Bot, then in an agent with only `agy`, then with neither)

Good: metaphor slides with no fitting brand photo get a generated image without a
question: in Grok Bot through its own `generate_image` (prompts from `gen_image.py
prompt`, the files recorded with `--label "Grok Imagine"`), elsewhere through
`gen_image.py make` with agy; with neither, Unsplash. A paid key is used only when
`content/setup.md` allows it. Evidence slides keep real screenshots. The close slide
credits each tool from `gen/manifest.json`. "jangan pakai gambar AI" mid-piece stops
generation for that piece.

## 2 — Plan a month

> buat rencana konten bulan depan

Good: `content/plan/YYYY-MM.md` from the template; pillar shares near the pack's;
series on their cadence; about a quarter of slots reactive; strong items cut into
several formats on different days; moments with verified dates; `check_plan.py` passes;
proposed items flagged for the owner.

## 3 — Create a carousel from an article

> bikin carousel dari artikel ini <url>, taruh di Figma

Good: primary source found; brief with five questions and the turn; hook workshop;
`lint_copy.py --format carousel` exits 0; frames in the pack's preset on a new page;
overflow check clean; `publish.md` with caption, ≤ 5 hashtags, alt text.

## 4 — Repurpose one source

> jadikan artikel ini thread X, post LinkedIn, dan naskah Reels

Good: one item folder; each cut rewritten for its format; X posts ≤ 280 each; LinkedIn
claim in the first ~140 characters; Reels storyboard with timings, safe-zone text,
sources per cut; every cut links back.

## 5 — Review a month

> ini angka insight bulan lalu <data>, apa yang harus diubah?

Good: compares each piece with the brand's own median for its format; decisions per
series (keep, fix with one named change, stop); no invented numbers; decisions carried
into the next plan's inputs. Without data: a list of what to collect, nothing invented.

## 6 — Two pieces in a row look different

> bikin carousel dari artikel ini <url>  (run twice, on two different stories)

Good: each `brief.md` has a "Design" table; the second piece's scheme (unless a series
fixes it), cover variant, and headline mark differ from the first's (read from
`content/design-log.md`); each carousel has one
slide that breaks the pattern; `layoutCheck()` returns no fill or size issues.

## Fast objective checks

- `lint_copy.py` exits 0 for the right `--format`, with no cover, caveat, metaphor, or
  staccato warning left unexplained.
- `check_plan.py` exits 0 for plans.
- HTML renderer: `render_slides.py` prints `layout: no issues`; Figma: `layoutCheck()`
  returns an empty list.
- Every number in `copy.md` has a `>` note.
- The first frame or line contains an exact number or a named thing.
- The report names which research tools were available.
- `brief.md` has the hook duels with reasons and the headline-only read.
- `content/design-log.md` has a new row.
