# Figma mechanics

Hard-won details from building frames (carousels, single posts, covers) through the Figma MCP. Skipping these causes
the failures listed.

## Session

1. Extract `fileKey` from the Figma URL (`figma.com/design/<fileKey>/…`).
2. `create_session({ fileKey, description })` once, before the first read or write.
3. Pass the returned `sessionId` to **every** file tool call after that.
4. On `use_figma`, always send `skillNames: "resource:figma-use,resource:figma-generate-design"`
   after loading those skills.

## Pages

- Build on a **new page** (`figma.createPage()`, then name it). Never edit another page's
  carousel — the user may be comparing against it.
- Page context resets to the first page on every `use_figma` call. Re-select the page at
  the top of each call:

```js
const page = figma.root.children.find(p => p.name === PAGE);
await figma.setCurrentPageAsync(page);   // figma.currentPage = page does NOT work
```

- Make the build **idempotent**: clear the page's children at the start, then rebuild.
  Never clear a rect named `IMG-*` if you want to keep an uploaded photo (its `imageHash`
  lives on the node).

## Code size: bundle the helpers

`use_figma` takes at most 50,000 characters of code. The helpers with their comments are
larger than that; without comments they are about 31,000, which leaves room for one
carousel. Write your slides in a file and bundle:

```bash
python3 scripts/figma_bundle.py --brand <pack>/design.md --page "Carousel — <item>" \
  build.js -o bundle.js --tail "return { media, issues: layoutCheck() };"
```

It inlines the brand's `BRAND` block, sets the page name, strips comment lines, checks
that the result parses and has no backtick, and fails over the limit. Then send the
file's text as the `code` argument. Over the limit: build frames 1–4 in one call, then
5–8 with `--keep-page` (`REBUILD = false`), calling `slide(i, ...)` with the real index.

If your host runs tool calls from a JavaScript runtime with `fetch` (Code Mode in
OpenCode does), serve the bundle locally instead of pasting it:
`python3 -m http.server 8765 --bind 127.0.0.1` in the bundle's folder, then
`const code = await (await fetch('http://127.0.0.1:8765/bundle.js')).text()` inside
the call. Stop the server afterwards.

The bundler drops layout functions your build never calls, which keeps a typical
carousel near 20,000 characters of helpers. To see every layout in a brand's design,
bundle `scripts/figma-gallery.js` onto a page of its own, then `figma-gallery-2.js` with
`--keep-page` (two calls, because the gallery uses every layout); and
`figma-gallery-schemes.js` on another page for one carousel in every scheme. Rebuild
them once per brand, or after changing the helpers or the schemes.

## API rules that bite

- Colours are 0–1 floats; paints have no `a` field, opacity goes on the paint.
- `fills`/`strokes` are read-only arrays — clone, modify, reassign.
- Every text edit needs its font loaded first, via the node's own
  `getStyledTextSegments(['fontName'])` when editing existing text.
- Text helper order: set `characters` → `textAutoResize='HEIGHT'` → `resize(w, height)` →
  position. Reversed, the node collapses to a near-zero-width thread.
- A wrapping text block needs an explicit `resize(w, …)`; `FILL` alone is not enough.
- Never call `setPluginData`, `createImageAsync`, `loadAllPagesAsync`, or `figma.notify`.
- Return every created/mutated node id from each call — state does not persist between
  calls, so pass ids back as string literals.

## Images: download first, then upload, then tone

The Plugin API cannot fetch a URL. Photos must exist as local bytes first.

1. **Get images.** Three sources, see `image-sourcing.md`:
   - Real artefacts (evidence slides): a screenshot of the source page, saved as PNG.
     Upload it the same way, but skip the duotone pass so its text stays readable.
   - Unsplash: `python3 scripts/unsplash_search.py "<query>" ... --out <dir> --download`
     writes the photos plus `manifest.json` with photographer names for the credits.
   - Generated: your own image tool, or `scripts/gen_image.py make` (agy, or a paid API
     the owner allowed); order and rules in `image-sourcing.md`.
2. **Look at them.** `python3 scripts/contact_sheet.py <dir>` builds a labelled grid.
   Choose from the sheet. (Run it without `-I`: Pillow lives in user site-packages.)
3. **Create the target rects** in the build call, named `IMG-1 … IMG-n`, filled with
   the `surface` colour as a placeholder.
4. **Reserve upload URLs** with `upload_assets({ fileKey, sessionId, currentPageId, count: n, scaleMode: 'FILL', nodeIds: [...] })`.
   The `nodeIds` order matches the returned `uploads[].submitUrl` order.
5. **POST the bytes** in parallel, multipart, so the filename names the layer:

```bash
curl -s -X POST -F "file=@img1.jpg;type=image/jpeg" "<submitUrl>" &
```

Each URL is single-use, expires in ~10 minutes, and self-commits into the node. A POST
can come back as a CloudFront `504 Gateway Timeout` HTML page instead of JSON. Reserve a
fresh URL for **that node only** and POST it again; the others are already placed.

6. **Tone the photos (duotone)** in a separate `use_figma` call, after the uploads. The
   upload replaces the node's fills, so toning applied earlier is lost.

**The brand's logo.** With `logo.image` in the `BRAND` block, `closeSlide` draws an empty
360×100 rect named `LOGO` instead of the letter badge. A PNG, JPEG, or WebP logo is
uploaded like a photo but with `scaleMode: 'FIT'` (a logo is never cropped) and never
toned; on a dark close use `logo.imageOnDark` when the pack has it. An SVG logo cannot
be an image fill: read the file, pass its text to `figma.createNodeFromSvg(svg)` in a
`use_figma` call, scale it to fit the `LOGO` rect (keep its aspect ratio, left-aligned),
place it at the rect's position, and remove the rect.

## Duotone recipe

One series of photos from five photographers looks random. Greyscale them and map them
between two brand colours, and they read as one set. All of it lives in the node's
fills; no extra layers:

```js
const img = n.fills.filter(f => f.type === 'IMAGE').pop();
n.fills = [
  Object.assign({}, img, { scaleMode: 'FILL', filters: { saturation: -1, contrast: 0.2, exposure: 0.1 } }),
  { type: 'SOLID', color: HIGHLIGHT, blendMode: 'MULTIPLY' }, // whites become this colour
  { type: 'SOLID', color: SHADOW,    blendMode: 'LIGHTEN'  }, // blacks become this colour
];
```

`fills[0]` is the bottom paint. Pick the pairs from the brand pack's `design.md`: each
scheme carries them, and `duotone(id, 'light')` (plates) or `duotone(id, 'dark')`
(full-bleed photos) uses the current scheme's pair. The
pattern that worked: light plates toned from the `surface` colour (highlights) to the
`primary` colour (shadows); dark full-bleed photos from `mutedDark` to `dark`, then a
`dark` gradient scrim on top for the text.
`duotone()` in `scripts/figma-helpers.js` does this per node id.

Generated images get the same treatment, so one piece can mix both sources.

## Verify cheaply, and only as much as needed

Screenshots are the slow, failure-prone part of this workflow. Do the cheap checks first
so a screenshot confirms instead of discovers.

1. **Structural check inside the build call.** End the build with `layoutCheck()` from
   the helpers and return its result: text past the right margin or into the footer, a
   cover with no image or display type, a slide whose content stops above y = 945, type
   that is too small, and a run of five light slides all show up as data, no image
   needed.
2. **Then screenshots, sequentially.** `get_screenshot` calls made in parallel
   (`Promise.all`) abort. A plain `for` loop awaiting one call at a time worked for four
   slides in one `execute`. Each returns a short-lived PNG URL.
3. **Download right away and review as one image.** `curl -f -L -o s1.png <url>` per
   slide, then paste them side by side with Pillow into one sheet and read that once.
   Four slides per sheet stays legible.
4. **Shoot only what you are unsure about**: the cover, the data slide, and any slide you
   changed. The user may stop a screenshot run. Respect that and report exactly which
   slides were and were not checked visually.

`use_figma` scripts can also call `await node.screenshot()`, which returns the image
inline in the tool result. Untested through the Code Mode `execute` wrapper; prefer the
URL route above until it is.

## Rebuild vs patch

- Copy changes on 1–2 text nodes: patch them (`find` the node, load font, set
  `characters`).
- A template, palette, or layout change: rebuild the page. Patching geometry across many
  slides is slower and leaves drift.
- A palette swap is a safe mechanical pass: walk `page.findAll(() => true)`, replace any
  `SOLID` paint whose colour matches the old accent.

## Errors

On a `use_figma` failure, obey `safeToRetryWithoutCanvasRead`. Mid-build failures leave
a partial page — because the build is idempotent (clear-then-build), just fix the bug and
re-run the whole call.
