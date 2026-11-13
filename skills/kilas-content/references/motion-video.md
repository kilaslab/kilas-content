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
the production line. Fill `video-racikan.md` first and keep that table in `brief.md`;
the line below starts after the owner has seen it, or had already named the preset.
`examples/reels-character-story.md` runs that line once on the real
film, with every command, done-check, and the audit that scored it 6/10.

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
| `elevenlabs` skills (`sound-effects`, `music`, `text-to-speech`, `speech-to-text`) | sound | official ElevenLabs: SFX and music from a prompt, the VO, the transcript check |
| `gsap-timeline`, `gsap-core` (GreenSock) | animatic, render | the official GSAP reference for timelines, eases, and SVG |
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
   a draft render, the **critique loop** (section 2c) until every score is 8+, then
   `render -q delivery`.
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

## 2b. Motion language, review, and decisions

Adapted from "Design Engineering: Build a Motion Studio Around Opus 5.5" (@dyfwsammy on X,
4 Nov 2026), which sets up UI motion the same way.

- **Motion language per brand**, written once in `design.md` under "Motion" and passed to
  the rig as tokens: durations (fast, base, slow), named eases (enter, exit, emphasis), the
  take timings, spring limits (the mascot's squash), transitions in use, and what never
  animates (the logo, a line the viewer is reading, product UI shown as proof). Every film
  then moves like the same brand.
- **Describe the feel, then the numbers**: "Mira lands light and settles once" becomes
  `back.out(1.7)` over 0.4 s; "the panic shakes the whole desk" becomes a ±6° jitter at
  0.07 s steps. Write the feel in the beat table so the owner approves the feel, not the
  curve.
- **A motion review before the render**: send the beat stills and the timing table to the
  second model as "a skeptical senior motion designer": readability per beat, holds that
  are too short, parts moving in unison, off-model poses, a transition without a cause.
  Treat it as a first pass, like the copy partner round.
- **Decision records**: under "Motion decisions" in `brief.md`, one line per choice that
  will be argued again (why 1.05× VO, why the mascot moved left in two beats, which ease
  was rejected and why). They feed the brand's "Motion" block when they repeat.

## 2c. Director's brief, references, and the critique loop

Adapted from "How to build motion design studio with Opus 5.5" (@0xMovez on X, 27 Sep 2026),
a study of the code-rendered films that went viral that month. Its finding: the prompt is
10 % of the film; the harness (reference, render engine, a model that looks at its own
frames) is the rest.

- **Brief like a director**, in `brief.md` before any code: the film in one line (what the
  viewer feels at the end); references (what to keep, what to push); tools and keys; a
  **character bible** (proportions, palette, expressions, an identity lock that holds in
  every beat, kept in `design.md`); the beat sheet with a payoff every 3–5 s; when text
  is huge and when it sits like a caption; the gates; the deliverables (MP4, poster frame,
  contact sheet).
- **Name a look and feed it a frame.** Without a reference the model falls back to its
  defaults. Give one frame (say what to take: palette, type, grain; and what not: the
  subject), a video (`ffmpeg -i ref.mp4 -vf fps=2 refs/frames/%03d.png`, then describe the
  pacing shot by shot), or the brand's own library; write `style_guide.md` from it. Take
  the grammar, never the content, logos, or characters.
- **Looks that read as generated**, to design away from: a centred title on a gradient,
  every element fading in, labels and frames in the corners, glow on UI, generic particle
  bursts, a beat where nothing happens.
- **Critique loop before the full render** (every new film, at least two rounds):

  ```bash
  ffmpeg -i out.mp4 -vf "fps=2,scale=270:-1,tile=6x5" -frames:v 1 contact.png       # 2 frames a second
  ffmpeg -ss 4.1 -i out.mp4 -vf "scale=320:-1,tile=12x1" -frames:v 1 strip.png      # 12 frames round a fast action
  ffmpeg -i out.mp4 -vf "fps=1,scale=360:-1,tile=5x3" -frames:v 1 phone.png         # how it reads 360 px wide
  ffmpeg -stream_loop 1 -i out.mp4 -c copy loop_check.mp4                            # watch the seam
  ```

  Score 1–10: hook in the first 2 s, readability at phone size, motion quality, variety
  (something new every 2–4 s), composition, brand accuracy, sound sync. **Every criterion
  must reach 8**; an average hides the one that loses the viewer (the first film averaged
  6 with readability at 4). The approved partner scores (`brainstorm-partner.md` section 2:
  send the sheets and the beat table as "a harsh motion director, not a proud author");
  when no partner is approved or installed, score it yourself, write "self-scored" next
  to the scores in `brief.md`, and say so in the report (the same rule as the gate in
  `SKILL.md`). Write
  the three worst problems with timestamps, fix them, re-render the affected seconds,
  score again. Before the owner sees it, the measured checks pass too: text ≥34 px, no
  dead beat mid-film (mean frame difference per second, `fps=4`, above the quiet floor
  except intended holds), −14 LUFS, transcript equal to the script. Hunt for text overlapping during swaps, anything that
  slides instead of easing, scaled blurry text, a dead beat, a stutter at the loop seam.
- **Sound on the picture's timeline**: the VO clips, plus short SFX on visible actions
  (a pop for each bubble, a whoosh on a move, a thump on a stamp) from `media-use` or
  synthesised in code; with a supplied track, measure its beats first and cut on them.
- **One timeline, several formats**: lay scenes out against the frame size, not fixed
  pixels, when the owner wants 1:1 or 16:9 too; reframe, never crop a 9:16 render.

## 2d. Camera, timing, and the one-command QA

Adapted from the measured style study in mromidev/claude-animated-shorts (20 viral story
shorts, Oct 2026; ideas paraphrased, no text or code copied).

- **The camera is almost never still**: wrap the scene in one `<g>` and use the rig's
  `camera()`, `creep()` (a push-in of 0.15–0.35 % a frame on every hold), `glide()` (ease in
  and out over 18–40 frames), `kick()` (an impact shake that flips every frame and fades in
  7). A static camera made the first film's dead beats.
- **Time reactions to words**: `vo_elevenlabs.py --verify film.mp4 --words words.json` gives
  every word's start; land each reaction 0–3 frames before its word. Blink every 0.5–2.3 s
  over 4 frames, plus one on each expression swap.
- **Story script formula** (story and explainer Reels): sentence 1 is the paradox stated as
  a fact; setting in 1–2 lines; 3–6 escalating beats; one mystery beat; a pivot ("Ternyata",
  "You see") into the mechanism through an everyday analogy; an ironic payoff; the film
  ends on the last word. Never narrate what the viewer already sees.
- **Mix**: VO on top, music 5–10 dB under it, SFX under the VO; −14 LUFS.
- **QA in one command**: `python3 <skill>/scripts/reel_qa.py out.mp4 --hold 0-1,29-33`
  (format, loudness, frozen runs ≥12 frames, dead seconds, flash frames, contact and phone
  sheets). It must exit 0 before the critique scores; on the first film it found the same
  dead seconds as the audit (6, 8, 17, 18, 22, 23) and −19 LUFS.

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
- Every word in a bubble, chip, or badge is at least 34 px on the 1080 canvas, and the
  characters fill their panel; the first film used 26 px bubbles that were close to
  unreadable at 360 px wide. The phone sheet (section 2c) decides.
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
