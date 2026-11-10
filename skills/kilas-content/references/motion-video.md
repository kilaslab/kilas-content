# Motion video: a Reels film from storyboard to post

A Reel that tells a small story or an explainer is a **character animatic** first and a
rendered film last. News and demo Reels use the same render and checks with other actors
(artefact captures, kinetic type, a screen recording; `formats/reels-tiktok.md` section 0).
The owner approves the animatic before anything is rendered, because a change after the
render costs a full rebuild, while a change in the animatic costs one line.

Learned on a 33-second product Reel (Nov 2026), in four rounds the owner rejected or
corrected: a still AI illustration with small moving parts read as stiff; a
UI-only motion piece (chat bubbles and kinetic type) had no one to care about; the mascot
squashed too far looked off-model; the layout left the lower third empty under a huge
watermark. What finally shipped: two cartoon characters (the same customer of the brand, last year
and this year) acting out the story beside the brand mascot, a voice-over, and one twist.

Read `formats/reels-tiktok.md` for the script, the beats, and the safe zones; this file is
the production line.

## 1. Companion skills

Load each when its step comes; none replaces this file's order.

| Skill | Step | What it gives |
|---|---|---|
| `short-form-video` | story, beats | hook in frame 0, a visual change every 2–4 s, loop seam, 9:16 safe areas |
| `motion-design` (LottieFiles) | animatic | timing, easing, the animation principles (squash, anticipation, follow-through) |
| `kinetic-typography` | animatic | headline reveals per word or line |
| `hyperframes` | render | the render contract, `references/types/character.md` (acting), `references/motion.md` (eases, holds, cuts), `references/types/vertical.md` |
| `hyperframes-cli` | render | `init`, `check`, `snapshot`, `render`, `timeline` |
| `hyperframes-registry` | render | ready blocks (transitions, captions) before you hand-build one |
| `media-use` | sound | music, SFX, voice when HeyGen or local tools are the route |
| `remotion-best-practices`, `remotion-captions` | render (alternative) | only when the owner asks for Remotion |
| `humanizer`, `social` | script | the voice-over and caption pass, like any copy |
| `ego-browser` | research, publish | read-only feed scroll; posting on the owner's go (`publishing.md`) |

Install: `prerequisites.md`, section "Video companions".

## 2. The line, with its gates

1. **Story** (`formats/reels-tiktok.md` 1–2): one idea, ±30 s. A product story is
   a contrast the viewer recognises (the struggling user vs the calm one) plus a turn
   (both are the same person, before and after the product). Write the beats in `copy.md` with an
   `onscreen:` line and a `vo:` line each; `lint_copy.py` reports the VO word count
   (±75 words for 30 s).
2. **Cast and rig.** Characters are vector rigs in SVG: a person (head, brows, eye states,
   mouth states, arms on shoulder pivots, props in hand) and the brand mascot. Start from
   `templates/video/rig.js`. Generated images are small props at most; the actors are
   drawn so they can act.
3. **Beat map and animatic**, published as one artifact: the whole film as a beat table
   (time, VO, on-screen text, action, one key still per beat, sketch-level is fine) so the
   turn and the ending are seen too, and the first 10 s fully animated, live in the
   browser (GSAP), with one still per second taken from the same timeline (`tl.seek(t)`).
   Budget every beat before animating: VO seconds (words ÷ 2.5) plus the reaction hold
   must fit the beat, and the on-screen line needs 0.5 s + 0.3 s a word; cut words from a
   beat that does not fit. The VO table carries a copy button: it is the dubbing brief.
   **Gate: the owner approves the beat map, the animatic, and the script.** No render
   before that.
4. **Animate the rest** in the same timeline; then **voice-over** (`scripts/vo_elevenlabs.py`):
   one clip per beat, speed ×1.05 for a conversational pace, and retime the animation to
   the VO so each visual lands on its word (a "paid" stamp on the word "paid").
5. **Render** with HyperFrames (`templates/video/index.html`): `check` until 0 errors,
   `snapshot` at every beat and read the sheet, then `render -q delivery`.
6. **Verify the file, not the source**: `ffprobe` (1080×1920, 30 fps, duration, an audio
   stream); `ffmpeg -af volumedetect` per beat window (VO present in every beat, silence
   after the last); loudness with `ffmpeg -i film.mp4 -af loudnorm=print_format=summary -f
   null -` (aim −14 LUFS integrated, true peak ≤ −1 dBTP; the first film shipped at −19 LUFS,
   quiet next to other Reels; fix with `ffmpeg -i in.mp4 -c:v copy -af
   loudnorm=I=-14:TP=-1.5:LRA=11 -c:a aac -b:a 192k out.mp4`; one pass lands within
   about 1 LU, and TP −1.5 keeps the peak under −1, then measure again); stills pulled
   from the MP4; **transcribe the audio** (`vo_elevenlabs.py --verify`) and compare it
   with the script word by word; play it once on a phone speaker if a person can, since
   music added later in the app must sit well under the VO.
7. **Preview** in the item's artifact: the MP4 (as a data URI under 16 MB), the caption, and
   the posting steps. Then `publish.md` and, on the owner's go, `publishing.md`.

## 3. Acting rules

- Every mood change is a **take**: anticipation (a small squash), the new face, overshoot,
  settle. Eyes and mouth swap at the take, never mid-air.
- Offset the parts: the head leads, arms follow; left and right arms never move in unison.
- One read per beat: lead the eye to where the action happens, play it fast, hold the
  reaction at least 0.5 s plus 0.3 s a word on screen.
- The mascot stays **on-model**: squash and stretch within ±12 %; check every still.
- Keep the mascot clear of chat bubbles; move it to open space when a beat fills the
  panel.
- Every product capability a scene shows comes from `brand.md` "Product facts"; ask the
  owner before a scene shows one that is not listed there, and show the limits too (what
  the product hands back to a human).

## 4. Layout for 9:16

- Centre the content block (headline, panels, any clock or counter) vertically and make the panels as
  wide as the safe area allows; split-screen stories stack two panels.
- Spend empty space on the story, not on a giant watermark.
- Every bubble sits whole inside its panel: check the top edge in each still.
- Text and faces inside y 168–1330; below that, panel bottoms and props only.

## 5. Voice-over (ElevenLabs)

- Key in `.env` as `ELEVENLABS_API_KEY`, never printed. The key needs the
  `text_to_speech` permission (and `speech_to_text` for the check); a 401 with
  `missing_permissions` means the owner must tick it in the ElevenLabs key settings.
  Without `voices_read`, use a premade voice id directly.
- Model `eleven_multilingual_v2`; pass `previous_text` and `next_text` so the clips
  sound like one take. Pick the voice with the owner and record it in `content/setup.md`.
  Premade voices that read Indonesian well: Jessica `cgSgspJ2msm6clMCkdW9` (young female,
  conversational), Laura `FGY2WhTYpPnrIDTdsKH5`, Matilda `XrExE9yKIg1WjnnlVkGX`.
- Write the VO for the ear, in the brand's language: numbers in words, acronyms and
  domains as people say them (Indonesian: "11.11" → "sebelas-sebelas", "QRIS" → "kris",
  "AI" → "ei-ai", ".id" → "titik i-d"). The multilingual model reads unknown acronyms in
  English; the transcript check caught "QRIS" heard as "queries".
- Put each clip on the timeline as its own `<audio>` with its measured duration; a film
  over 15 s with no sound fails HyperFrames' review, and Instagram music can be added at
  low volume by the owner.

## 6. Technical traps (GSAP, SVG, HyperFrames)

- **Arm pivots**: rotate with the attribute `transform: "rotate(a sx sy)"` around the
  shoulder in the element's own coordinates. GSAP's `svgOrigin` is global, so nested
  groups swing around the wrong point.
- Elements moved by `attr: { transform }` keep one string shape for every tween
  (`translate(x,y) scale(s) rotate(r)`), and get no GSAP `x/y/scale` on the same node.
- **Counters** (unread badges, dashboard numbers) are a pure function of time, written in
  the timeline's `onUpdate` and after every seek: `tl.seek()` suppresses callbacks, so
  tween `onUpdate` counters freeze in stills and renders.
- HyperFrames lint wants the timeline built and registered in the **same** `<script>`
  (`window.__timelines["main"] = tl`).
- Fonts outside the bundled list (Anton) need `@font-face` to a file in `assets/fonts/`.
- Headless Chrome screenshots are at least 500 px wide; a port already in use serves
  someone else's folder, so read the page title before trusting a screenshot.
- `brew install ffmpeg` provides `ffprobe`, which HyperFrames needs to render.

## Done when

The beat map, animatic, and script were approved, the MP4 passed step 6 (dimensions,
audio in every beat, loudness, stills, transcript matching the script), the artifact shows the final file and
caption, and every correction the owner made is in `content/lessons.md`.
