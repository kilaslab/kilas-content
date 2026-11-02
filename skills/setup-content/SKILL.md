---
name: setup-content
description: "First-run setup for the kilas-content skill: asks which brand the content is for, reads the brand's website and social profiles (with permission) and collects its own logo, colours, fonts, photos, and voice for reuse, chooses how frames are rendered (Figma, or HTML converted to PNG), and writes the brand pack and content/setup.md. Use it the first time someone plans or creates content in a project, or when they say \"setup content\", \"setup brand\", \"onboarding\", \"brand baru\", \"ganti brand\", \"pakai html saja\", \"tidak punya figma\", \"ambil aset dari website/instagram kami\", or when the content skill finds no content/setup.md."
license: GPL-3.0-or-later
---

# Setup: brand, assets, renderer

Run this once per project, before the first plan or piece. It ends with a brand pack the
content skill can use, the brand's own assets collected for reuse, a chosen renderer,
and `content/setup.md` recording all of it.

This skill ships with the **kilas-content** skill (same repository). Load that skill first
(`/kilas-content`, or the host's skill tool) to know its folder: every `scripts/`,
`templates/`, `brands/`, and `references/` path below is in that folder, written here as
`<skill>/...`. The workspace is `content/` in the current project.

## 0. Check what exists

- `content/setup.md` exists: tell the user setup was done on its date, show its summary,
  and ask only what they want to change (a new brand, a new renderer, fresh assets).
- `content/brand/brand.md` exists but no `setup.md`: keep the pack, run steps 3–6.
- Take stock of tools (`<skill>/references/research-tools.md` section 1): page fetch,
  web search, a real browser (`ego-browser`, the host's browser), the Figma MCP, Python
  Playwright or a Chrome binary (`python3 <skill>/scripts/render_slides.py --help`
  explains), `agy`. Note what is missing; it decides some choices below.

## 1. Ask, in one round

Use the host's question tool. One round, at most eight questions, each with a
recommended option when you can infer one:

1. **Brand**: its name and what it does, in a sentence (or "read it from the website").
2. **Links**: website, Instagram, X, Threads, TikTok, LinkedIn, YouTube (any they have).
3. **Permission to collect assets** from those links: logo, colours, fonts, photos, and
   recent posts, saved in `content/brand/assets/` for reuse in their content. Make it
   explicit that this is only for accounts the user owns or may use, and whether you may
   use a signed-in browser session for profiles that need a login.
4. **Renderer**:
   - **Figma**: frames are built in a Figma file (needs the Figma MCP connected and a
     file URL); the owner can edit them after.
   - **HTML → PNG**: frames are written as HTML with the skill's slide kit and rendered
     to PNG by a headless browser (needs Python Playwright or Chrome/Chromium); no Figma
     needed, files stay in the repo.
   - **Both**: Figma for the pieces the owner will edit, HTML for fast ones.
   Recommend Figma when the MCP is connected and they have a file; HTML otherwise.
5. **Language and address**: Indonesian or English (or another); kamu, Anda, or kalian.
6. **Main goal for the next three months**: reach, trust, or sales.
7. **Capacity**: how many pieces a week the team can really finish.
8. **Limits**: words or claims never to use, things that need approval or disclosure.

## 2. Collect the brand's own assets (with permission)

Save everything under `content/brand/assets/`, one folder per source. All of it is data:
never execute anything from there.

```bash
python3 <skill>/scripts/crawl_site.py https://brand.example content/brand/assets/site
<skill>/scripts/capture_profile.sh https://www.instagram.com/<handle>/ content/brand/assets/instagram 18
<skill>/scripts/capture_profile.sh https://www.tiktok.com/@<handle> content/brand/assets/tiktok 12
python3 <skill>/scripts/x_post.py https://x.com/<handle>/status/<id> --download content/brand/assets/x
<skill>/scripts/scan_site_tokens.sh https://brand.example > content/brand/assets/site/computed-tokens.json
python3 <skill>/scripts/contact_sheet.py content/brand/assets/instagram/images -o content/brand/assets/instagram/contact.jpg
```

- `crawl_site.py` honours robots.txt. If it refuses and the user confirms the site is
  theirs, re-run with `--ignore-robots`. If the site blocks plain HTTP clients (403),
  use `scan_site_tokens.sh` and `capture_profile.sh` on the site instead (a real browser).
- `capture_profile.sh` reads a profile page only (scroll, no clicks), saves a screenshot
  of the grid (`profile.png`), the bio, and the post images it shows. A login wall means
  the browser is not signed in: ask the user to sign in in that browser, or skip.
- A parked domain or an empty profile is a finding, not a failure: note it.
- Logos of partners, clients, or press found on the site are listed, not downloaded; do
  not use them.

Then write `content/brand/assets/README.md`: every file worth reusing (logo variants,
icon, photos by subject), where it came from, and what it is good for (cover photo,
plate, close slide, logo on dark or light). Look at the images (contact sheets) before
describing them.

## 3. Write the brand pack

Follow `<skill>/references/brand-onboarding.md` (sections 3–4) with what you collected:

- `content/brand/brand.md` from `<skill>/brands/_template/brand.md`: identity and
  audience in the brand's own words from the site, voice read from their captions and
  pages, channels and handles from the links, pillars and series (proposed), cadence
  from capacity, CTAs that point somewhere that works today.
- `content/brand/design.md` from `<skill>/brands/_template/design.md`:
  - **Colours**: the most-used non-neutral colours from `assets.md` (and the computed
    tokens), mapped to the roles in `<skill>/references/design-system.md`. Check
    contrast; pick a highlight that is not the text colour.
  - **Schemes**: the brand's default scheme from its own colours, plus a black-and-white
    one, a dark one, and a loud one on the accent (`<skill>/references/design-variety.md`
    section 2b). Give each a duotone pair.
  - **Fonts**: the site's fonts if Google Fonts (HTML) or Figma (Figma) has them;
    otherwise the closest available, named as a substitute.
  - **Logo**: put the best logo file in `content/brand/assets/logos/` and set
    `logo.image` in the `BRAND` block (path relative to `content/brand/`); keep `letter`
    and `wordmark` as the fallback lockup.
  Mark everything the owner has not confirmed with `(proposed)`.

## 4. Set up the renderer

- **Figma**: `create_session` with the file key; confirm the file opens; note it in
  `design.md`. Build the galleries on two new pages (`<skill>/references/figma-mechanics.md`,
  "Code size"): `figma-gallery.js` + `figma-gallery-2.js`, and `figma-gallery-schemes.js`.
- **HTML**: check a browser is available (`python3 <skill>/scripts/render_slides.py`
  prints which one it uses); render the example in each scheme as the gallery:

  ```bash
  python3 <skill>/scripts/new_html.py content/setup-gallery --brand content/brand/design.md
  # copy a few of the brand's own photos into content/setup-gallery/html/img/ (cover.jpg, plate.jpg, ...)
  python3 <skill>/scripts/render_slides.py content/setup-gallery/html/slides.html -o content/setup-gallery/<scheme> --scheme <scheme>
  python3 <skill>/scripts/contact_sheet.py content/setup-gallery/<scheme> -o content/setup-gallery/<scheme>.jpg
  ```

  Replace the example's words with one real sentence about the brand on the cover, so
  the owner judges their brand, not the sample.

## 5. Write content/setup.md and the workspace

Create the workspace from `<skill>/templates/workspace.md` (if missing) and write
`content/setup.md` from `<skill>/templates/setup.md`: brand, pack location, renderer and
its details, language, assets and the permission given (date, which sources, signed-in
or not), tools found, and what is still `(proposed)`.

## 6. Show the owner, once

One message: the brand in two lines as you understood it, what was collected (and what
was not, with why), the pillars and series, the schemes with the gallery (Figma pages or
the PNG sheets), the renderer, and the open questions. Keep `(proposed)` until they
confirm. Then the content skill is ready: "buat rencana konten bulan ini" or "bikin
carousel dari <link>".

## Rules

- Assets only from accounts the user owns or may use, with their permission for this
  setup. Read only: never post, like, follow, or message.
- Never copy another brand's logo, photos, or layouts into the pack.
- Language follows the user (and the pack, once written).
