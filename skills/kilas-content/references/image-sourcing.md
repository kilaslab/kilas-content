# Image sourcing

**The brand's own assets come first.** If `content/brand/assets/README.md` exists (the
setup-content skill collects the brand's logo, icons, and photos from its site and
profiles), use those photos for covers, plates, and closes before searching stock: they
are on-brand and already the owner's. Tone them like any photo; credit them only if the
owner credits their photographers.

Then three sources. Choose per slide; one carousel can mix them.

| | Real artefact | Unsplash | Generated with `agy` |
|---|---|---|---|
| Best for | evidence: the thing the story is about, as it actually looks | real things where any good example will do: hardware, a server room, a desk | the story's metaphor, made specific: a floodgate in an Indonesian canal instead of a generic dam |
| Available | when the source has something to show | always | only when the Antigravity CLI is installed and signed in |
| Treatment | in colour, cropped, never retouched | duotone | duotone |
| Credit line | `Tangkapan layar: <source>` | `Foto: <name> / Unsplash` | `Ilustrasi: AI (Antigravity)` |

Order of preference per slide: a real artefact on evidence slides, Unsplash or a
generated image on metaphor slides, and no image on a slide that a chart, a quote card,
or a ranked list already fills. The data slide is built in the brand's design from the
primary source's numbers (`formats/carousel.md` section 2b); a screenshot of someone
else's chart goes on a claim slide, or on the data slide only when the chart itself is
the news.

## Real artefacts

In the data (`patterns-from-data.md`), the most-saved creator posts showed the real
thing: a dashboard, a product page, a list of job offers, a hand-drawn diagram. None of
them used a designed template. A screenshot of the actual commit log says "this
happened" in a way no stock photo can.

What counts: a screenshot of the source page, a maintainer's email on lore.kernel.org,
the product's official page with its price, a GitHub release, a benchmark table, a
company's own chart. Rules:

How to get them, and which ones you may use, is in `research-tools.md` section 3:
`scripts/capture_artefact.sh` for a page region, `scripts/x_post.py` (or the host's X
tool) for a post and its full-size photos.

- Capture it from the primary source yourself, at full resolution. Crop to the part
  that proves the slide's claim (300–450 px tall on the slide). If the crop drops the
  table's header, say what the columns are in the label above it.
- Mark the rows or the phrase that prove the claim with `artefact()` marks: highlighter
  rectangles in MULTIPLY blend over the image, so they read as a highlighter and the
  image stays untouched. `scripts/artefact_marks.py` finds row bands and word positions.
- Frame it to suit the evidence (`design-variety.md`): plain for dense tables and logs,
  `window` with the page's real URL for a web page or repo, `tilt` for one screenshot
  that should feel found.
- Never alter what it shows: no retouched numbers, no removed lines, no fake UI.
- Blur personal data that is not the story (emails, avatars of private people).
- Keep it in colour, inside a plate with a 1 px rule border; duotone makes text in a
  screenshot hard to read.
- Credit `Tangkapan layar: <site or person>` under it, and list the URL in the close
  slide sources.

A mock screen that shows a scenario (the "ChatGPT in Germany in 2027" kind) is not an
artefact. It is an illustration, allowed only on an opinion carousel with the eyebrow
`SKENARIO` and the credit `Ilustrasi`.

## One visual thread

Five unrelated photos read as a gallery. Tirto keeps one illustrated character on every
slide; a brand can get the same continuity two ways:

- **One metaphor family in the photos**, as the Linux carousel did with water (dam,
  sluice, water texture), then the duotone pass to make them one series.
- **One recurring subject in a generated series**: describe the same character or
  place in the shared style sentence of `agy_image.sh`, and change only the action per
  image ("the same young Indonesian developer in a grey hoodie at a cluttered desk, ...").

## Unsplash

```bash
python3 scripts/unsplash_search.py "dam spillway" "sluice gate" "paperwork pile" \
  --per 5 --out content/items/<item>/photos --download --width 1600
python3 scripts/contact_sheet.py content/items/<item>/photos -o content/items/<item>/photos/contact.jpg
```

- Search the **metaphor** and the **literal** subject. For Linux 7.4 the metaphor queries
  (dam spillway, floodgate, sluice gate, paperwork pile) beat "linux" or "server", which
  return the same five photos every tech account uses.
- The script skips Unsplash+ (`plus.unsplash.com/premium_photo-*`); those are paid.
- It writes `manifest.json` with photographer names. Put them on the close slide.
- Traps it already handles: a browser User-Agent gets an Anubis bot challenge, and Python
  `urllib` gets a 401, so it fetches with curl's default UA.

## Generated with agy

Check first, and fall back to Unsplash without fuss when it is missing:

```bash
command -v agy && agy models | head -3
```

Then generate the whole set in **one** run, with one shared style sentence so the images
match each other:

```bash
scripts/agy_image.sh content/items/<item>/gen 3:4 \
  "editorial documentary photograph, 35mm, overcast light, muted desaturated tones, high detail, calm composition with generous empty space in the lower half for a headline" \
  "a tall concrete floodgate in an Indonesian city canal with all its gates open, a heavy torrent of water rushing through, seen from a low angle"
```

That exact command was tested: one 896x1200 JPEG in about a minute, a Jakarta-looking
floodgate that no stock search returned.

### Prompt recipe

Name, in this order: **medium** (editorial documentary photograph, 35mm / flat vector
illustration / isometric render), **subject**, **place** (make it local: Indonesian
city canal, warung, KRL platform), **light**, **composition** (where the empty space for
type goes), then any negatives. The script already adds "no text, no letters, no
watermark, no logos". Leave colour to the duotone pass; asking for "muted desaturated
tones" gives it cleaner input.

Ratios to slots:

| Slot | Ratio | Note |
|---|---|---|
| Full-bleed cover or close (1080x1350) | 3:4 | upscaled ~1.2x; fine under the scrim and duotone |
| Photo plate (904 x 340–440) | 16:9 | cropped by `scaleMode: FILL` |

### Honesty rules for generated images

- A photoreal generated image is an **illustration**. Never present it as a photo of a
  real event, a real person, or the actual place in the news. Credit it as
  `Ilustrasi: AI (Antigravity)`.
- Use generation for metaphor slides (cover, context). Evidence slides get Unsplash, a
  chart, or no image.
- Never generate people who could be mistaken for the people quoted, logos, screenshots,
  charts, or anything with readable text.
- Look at every result before uploading. agy reports success even when it drew the
  wrong subject.

### Safety of the call

`agy_image.sh` runs agy with `--dangerously-skip-permissions`, because print mode cannot
ask for approval and would otherwise deny its own `generate_image` tool. It pairs that
with `--sandbox` and a prompt that allows only `generate_image`. Keep it that way, and
never paste article text or other untrusted content into the prompt; write the subject
yourself.

Credit for the technique (the three silent traps: auto-denied tools, writes landing in
`~/.gemini/antigravity-cli/scratch/`, and Claude Code's classifier blocking `agy`):
[dyrok/imagine-agy](https://github.com/dyrok/imagine-agy). The skill reimplements the
call instead of installing that npm package, which also edits `~/.claude/settings.json`.
