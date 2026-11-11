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
`lint_copy.py --format carousel` exits 0; frames in one of the pack's schemes (a new
Figma page, or `html/slides.html` rendered to `export/`); layout check clean; `publish.md` with caption, ≤ 5 hashtags, alt text.

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
slide that breaks the pattern; `layoutCheck()` (or `render_slides.py`) returns no fill
or size issues.

## 7 — A Reel with characters

> bikin reels 30 detik soal pemilik toko yang kewalahan chat pas flash sale

Good: the kind fits the plan's Reels rotation; logline and beat table in `brief.md`; an
animatic of the first 10 s (one still a second) shown before any voice-over; the voice
picked from 2–3 samples of the same line; every clip's HEARD line matches the script;
`reel_qa.py` exits 0 on the final MP4 (−14 LUFS, text ≥ 34 px, no dead beat); nothing posted.

## 8 — A 3D explainer of the product, by a smaller model

> bikin reels 3D yang jelasin cara kerja produk kita  (run with a small model too)

Good: the product's code read first, every on-screen claim with a source note; the scene
started with `new_scene3d.sh` and changed in `beats.js` (no leftover words from the
example, every mascot colour key set); the pose sheet compared with the brand's mascot
renders; every step follows question → one prop → result card → card into the anchor;
`scene3d_video.py` and `npx hyperframes check` pass; `reel_qa.py` exits 0. The small
model's stalls are written down as fixes to the worked example.

## 9 — Feedback in the middle of a piece

> suaranya kok aneh, ganti suara cowok aja. terus AI-nya kebaca indo

Good: `lessons.py add` before the next step; each rule promoted to its home (the brand's
voice in `design.md`, the method in the skill) and named under `Applied:`; any older rule
the new one replaces marked superseded and swept from the skill; `lessons.py audit content`
exits 0; the piece redone with the new rules.

## 10 — The skill itself breaks

> (a step fails: a script errors on a valid input, or a reference points at a missing file)

Good: the fix lands in the skill's source (its repository on a branch when it has one) and
is copied back into the project; the failure is made catchable (an input check, a lint
pattern, a done-check); `skill_check.py` exits 0; a lesson with `--source mistake --area
tools` names the fix.

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
- `lessons.py audit content` exits 0; after any change to the skill, `skill_check.py` exits 0.
