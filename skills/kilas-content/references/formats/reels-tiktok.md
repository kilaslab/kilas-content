# Reels, TikTok, Shorts: script, storyboard, cover

The deliverable is everything a person or a video tool needs to produce the video: a
script, a shot-by-shot storyboard, on-screen text, an asset list with sources, a cover
frame (Figma, or a separate HTML page: `html-render.md` section 4), and the caption. Two
routes to the video:

- **Motion film**, made by the agent: a character animatic the owner approves, then a
  voice-over and a HyperFrames render (`motion-video.md`). Characters act the story; a
  still illustration with small moving parts reads as stiff, and UI alone has no one to
  care about.
- **Shoot**, made by the owner: they record and edit from the storyboard below.

## 0. Kinds of Reel, and the mix

Pick the kind before the script; rotate kinds across the month so the channel is not a
string of ads. A video the agent will render takes its kind from the racikan
(`video-racikan.md`, cards in `video-presets.md`) and writes that table in `brief.md`
before this script. A storyboard the owner will shoot still picks a kind from the
table below.

| Kind | What carries it | Visual route | Product's place |
|---|---|---|---|
| News | the event, its number, its source on screen | artefact captures, kinetic type, charts; a presenter if the brand has one | an aside or the last beat ("what it means for you") |
| Explainer | one idea made plain with one metaphor | characters or objects acting the metaphor | an example, if it fits |
| Story | a scene the viewer has lived (a contrast, a POV, a twist) | acting characters (`motion-video.md`) | supporting role, or the turn |
| Demo | the product doing one real thing | screen recording of the real UI, cropped to the action | the subject |

At most every other Reel is a Demo or a story whose turn is the product.

## 1. Length and shape

Aim for 30 seconds for a one-idea story (a contrast, a demo, a joke); go to 60 only when
the piece teaches steps. Write for the numbers that spread a Reel: watch time, replays, comments,
and shares; a fast payoff and a quiet CTA. Shorter often wins: one creator took a Reel
from 12.6K to 2.1M views by cutting it from 9 to 7 seconds, making the hook easier to
read, and moving the full payoff into the caption (@louiseivan on X, Nov 2026). Past 30 s,
give the viewer a new hook about every 15 s, where retention curves keep dipping
(@kuswanto, Nov 2026). Instagram does not recommend Reels over 3 minutes to new
audiences. Speaking pace is roughly 130–150 words per minute, so 45 seconds holds about
100 spoken words. Read the script aloud with a timer; that number beats any estimate.

| Time | Beat | Job |
|---|---|---|
| 0–3 s | **Hook** | the claim, said and shown at once: the number on screen, the voice saying it, a visual already moving |
| 3–8 s | Context | what it is, in the everyday metaphor |
| 8–35 s | Three beats | one idea per beat, each with its own visual: proof, cause, turn |
| 35–45 s | Payoff | what it means for the viewer, or the action to take |
| last 3 s | CTA | one, from the brand pack; no "like, comment, share, follow" stack |

The writing method is the same as for a carousel (`writing-craft.md`): find the story,
workshop the hook, one metaphor family, a turn. A carousel's ladder compresses to these
five beats.

## 2. The first three seconds

- Start mid-action or on the number. No logo intro, no "Halo semuanya".
- Say and show the same words: on-screen text is the hook line, ≤ 8 words.
- Make the first frame readable as a still: it is also what people see while scrolling.
- Workshop it like a cover: five versions, scored specific / scene / open loop / honest.
  With Instagram trial reels (public pro account, ≥200 followers), two hooks can be
  tested on non-followers before choosing.

## 3. Storyboard format

Write `storyboard.md` in the item folder:

```markdown
| # | Time | Shot (what we see) | On-screen text | Voice-over | Asset / source |
|---|---|---|---|---|---|
| 1 | 0–3 s | screen recording: commit counter ticking up to 19.671 | 19.671 commit. Dua minggu. | Sembilan belas ribu commit masuk ke kernel Linux dalam dua minggu. | capture: lore.kernel.org, 1 Nov 2026 |
| 2 | 3–8 s | B-roll: floodgate opening | Anggap saja pintu air | ... | Unsplash: <photographer> |
```

For a motion film, the storyboard is the animatic itself: one still per second for the
first 10 s, then one per 5 s, each with the action (per side in a split screen), the
on-screen line, and the VO slice, plus the full VO script as a table. **Render only after
the owner approves it**; a change after the render costs a rebuild.

In `copy.md`, every beat has `onscreen:` and `vo:`; `lint_copy.py` counts the VO words and
`scripts/vo_elevenlabs.py` turns the `vo:` lines into one clip per beat.

Rules:
- One row per cut. A new idea gets a new visual.
- On-screen text ≤ 8 words per card; burn in captions for the voice-over too, because
  many people watch without sound.
- Every number on screen has a `>` source note in `copy.md`, as on a carousel.
- Visual sources: screen recordings and artefact captures (`research-tools.md`) for
  proof; the presenter on camera for opinion; stock or generated stills with a slow
  zoom for metaphor (credit them; generated ones as `Ilustrasi: AI`).
- No copyrighted music in an exported file; music is chosen in the app.

## 4. Safe zones (1080×1920)

Keep text and faces inside **x = 100–880, y = 270–1430**. The right edge carries the
like/comment buttons and the bottom carries the caption and audio line. Numbers and
sources in `specs.md`.

## 5. Cover

Build a 1080×1920 cover frame in the brand's style (Figma, or a separate HTML page): the hook line and one
visual. The profile grid shows only the centred band **y = 240–1680** (3:4), so the
title must sit inside it. Instagram also accepts a separate cover image (420×654
minimum); upload the frame at full size.

## 6. Caption and posting

- First line restates the hook in new words; the rest adds the source and context.
- Hashtags: up to 5 on Instagram (series tag + 1–2 topic tags).
- TikTok: same video, the caption may be longer; add the source in the caption.
- Cross-post to Shorts if the brand uses YouTube; remove other platforms' watermarks.

## 7. Checklist

- [ ] Hook works muted and as a still.
- [ ] 30–60 s when read aloud; one CTA at the end.
- [ ] Every cut has a visual and a source; every number has a note.
- [ ] Text inside the safe zone; cover title inside y = 240–1680.
- [ ] Captions burned in; no music in the export.
- [ ] `storyboard.md`, `copy.md`, cover frame, asset list, and caption delivered.
- [ ] Motion film: animatic and VO script approved before the render; the MP4 passed
      `motion-video.md` step 6 (size, audio in every beat, stills, transcript = script).
