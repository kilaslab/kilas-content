# Brand onboarding: writing a brand pack

The setup-content skill (`../setup-content/SKILL.md` in this repository) runs the whole
first-run flow: the interview, collecting the brand's own assets, the renderer, and
`content/setup.md`. This file is the method behind its step 3: how to turn what was
collected into `content/brand/brand.md` and `content/brand/design.md` in the format of
`brands/_template/`. If the setup skill is not installed, follow its SKILL.md by hand.

## 1. Read before asking

Collect what you can without the owner, so the interview only asks what is missing:

- **The site** (`scripts/crawl_site.py <url> content/brand/assets/site`): its name and
  description in its own words, what it sells and for whom (from the home and about
  pages), colours, fonts, logo, icon, photos, and the social links it lists. A parked or
  placeholder page means the site is not live: note it and do not use the domain in CTAs.
- **Computed styles** (`scripts/scan_site_tokens.sh <url>`): the colours and fonts the
  page actually renders, which catches what CSS files hide (variables, frameworks).
- **Profiles** (`scripts/capture_profile.sh <profile url> content/brand/assets/<network>`):
  a screenshot of the grid, the bio, the post images. Read the grid as a designer: which
  formats recur (series), which colours, type, and photo style, how dense the text is.
- **Posts and captions**: the last 10–20 per channel, through a social tool, a signed-in
  browser with the owner's consent, or `scripts/x_post.py` for public X posts. Note voice
  (formal or casual, kamu or Anda, emoji, length), recurring series, hashtags, and what
  drew the most response within the account.
- **Existing long form**: blog, notes, newsletter: where, which language, how often.

## 2. Interview

One round, at most eight questions, with the host's question tool;
`../setup-content/SKILL.md` step 1 is the list. Fill the reader, the channels, and who
answers comments from what you read, and mark them `(proposed)`. Offer a recommended
option for every question from what you read.

## 3. Draft the pack

- **Pillars**: 3–5, where what the brand offers meets what the reader needs; a goal and
  a share each, adding to 100%. Mark them `(proposed)`.
- **Series**: 2–3 to start, each with a tag, rubric, format, cadence, and scheme
  (`planning.md` section 3). Check each tag on the platform first: an existing tag with
  other content is a bad series tag.
- **Cadence** from the stated capacity, with about a quarter of slots reactive.
- **CTAs**: one per goal, each pointing somewhere that works today.
- **Voice**: three sentences in the brand's own register, with two lines from their
  captions that show it; the banned phrases they named.
- **Design** (`design.md`):
  - Map the collected colours to the roles in `design-system.md` section 1. The most
    used saturated colour is usually `primary`; the light background `ground`; the
    darkest text `text`; an accent the brand uses for emphasis `highlight`. Check
    contrast: text on ground and muted on ground 4.5:1, big numbers 3:1.
  - Build **schemes** (`design-variety.md` section 2b): the brand's default from its own
    colours, plus black-and-white, dark, and loud-accent schemes from the same roles.
    Each gets `onDark` and a duotone pair. `scripts/brand_css.py` will refuse nothing,
    so check the gallery by eye.
  - **Fonts**: use the site's fonts when the renderer has them (Google Fonts for HTML,
    the Figma file's fonts for Figma); otherwise name the closest available as a
    substitute in `design.md`.
  - **Logo**: copy the best logo (SVG first, then the largest PNG) to
    `content/brand/assets/logos/` and set `logo.image` in the `BRAND` block, relative to
    the pack folder. Keep `letter` and `wordmark` as the fallback lockup.
  - Fill the `BRAND` block for `figma-helpers.js` and `brand_css.py`.
- **Assets README** (`content/brand/assets/README.md`): which photos suit covers, plates,
  and closes, which logo variant goes on dark and on light. The skill reuses these before
  searching stock photos (`image-sourcing.md`).
- **Language** file: `language/id.md` or `language/en.md`; for other languages, write a
  short `language/<code>.md` with the same sections.

## 4. Confirm

Show the owner the pillars, series, schemes (the gallery), CTAs, and the renderer in one
message. Keep `(proposed)` on anything they have not confirmed, and ask again before a
plan relies on it.
