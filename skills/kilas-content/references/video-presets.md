# Video presets

Nine cards. Pick one in `video-racikan.md`. A card sets defaults. The owner's
words and the brand pack's `design.md` "Video" section override a default.

Each card names the production route. A flat character film uses `motion-video.md`
and `templates/video/`. A polygon film uses `templates/video3d/` (section
`poly-3d` below). A demo uses a screen recording. Do not mix a polygon scene
and a screen recording in one film unless the owner asks for both.

Hook shape is a pointer into `writing-craft.md`, not the line itself.

A public shelf of code-animation prompts, for when the owner wants a look none
of these cards cover: [awesome-opus5-5-videos](https://github.com/yihui-dev/awesome-opus5-5-videos)
(creator-credited prompts; HTML, Canvas, SVG, GSAP, Three.js). Credit the file
you copy. It is not one of these cards.

## short-reel

- When: one claim, one contrast, about 30 s.
- Aspect / length: 9:16, 30 s. Go under 30 s when the claim fits; do not pad.
- First 3 s: the claim on screen and in the voice, already moving. No logo open.
- Visual / edit: vector characters, fast cuts.
- Structure: before/after. Hook shape: number + scene + stakes.
- Captions: lower third.
- Route: `motion-video.md`.

## explainer

- When: one idea, one metaphor, taught in steps.
- Aspect / length: 9:16, 45–60 s. Past 30 s, a new hook about every 15 s
  (`formats/reels-tiktok.md`).
- First 3 s: the metaphor already happening, not a title.
- Visual / edit: vector characters or objects, one continuous scene per step.
- Structure: three acts. Hook shape: compression promise, when one frame can
  hold the idea; otherwise number + scene + stakes.
- Captions: a word on the beat of the voice.
- Route: `motion-video.md`.

## story

- When: a scene the viewer has lived. A contrast, a point of view, or a twist.
  The product is a supporting role, or the turn, not the opening claim.
- Aspect / length: 9:16, about 30 s. 45 s only when the twist needs the extra beat.
- First 3 s: already inside the scene. No logo open, no "let me tell you".
- Visual / edit: vector characters, fast cuts. Two people, or the same person
  in two states.
- Structure: before/after. Hook shape: number + scene + stakes.
- Captions: lower third.
- Route: `motion-video.md`, worked once in `references/examples/reels-character-story.md`.
  At most every other Reel is a story whose turn is the product
  (`formats/reels-tiktok.md` section 0).

## poly-3d

- When: the picture is a polygon world. A small world on a block (a diorama),
  a room the camera moves through, or a mascot and props that need depth.
- Aspect / length: 9:16, 45–60 s.
- First 3 s: the camera already in the world, one object moving. No title card
  before the world is visible.
- Visual / edit: polygon scene, one continuous move per beat.
- Structure: three acts. Hook shape: compression promise, when one frame holds
  the idea; otherwise number + scene + stakes.
- Captions: title card at the open, then lower third.
- Route: `references/examples/reels-3d-explainer.md`, then
  `scripts/new_scene3d.sh` into the item folder. The scene, the mascot rig, and
  the pose sheet live in `templates/video3d/`.

## product-demo

- When: the product does one real thing, on its real UI.
- Aspect / length: 9:16, 30–45 s.
- First 3 s: the screen already on the action. Crop to the control that moves.
- Visual / edit: screen recording, a screen tutorial (one action, then the result).
- Structure: before/after. Hook shape: product + price, only when the price is
  confirmed; otherwise number + scene + stakes.
- Captions: lower third.
- Route: a capture of the real product (`formats/reels-tiktok.md`, Demo). At most
  every other Reel is a demo.

## news

- When: an event, a number, a named source.
- Aspect / length: 9:16, 20–30 s.
- First 3 s: the number, full frame, with the source named on screen.
- Visual / edit: artefact captures and kinetic type, fast cuts.
- Structure: a list only when every item meets one threshold from one source;
  otherwise three acts (what changed, why, so what).
- Hook shape: number + scene + stakes, or ranked list with a threshold.
- Captions: kinetic type is the caption. No second caption track.
- Route: `formats/reels-tiktok.md`, News. A presenter only when `design.md`
  "Video" names one.

## music

- When: the picture is cut to a track the owner supplied, or a beat they named.
- Aspect / length: 9:16, the length of the phrase they named. Default 15–30 s.
- First 3 s: a hit on the first downbeat. No spoken open.
- Visual / edit: kinetic type or vector characters, fast cuts on the beat.
- Structure: a list of hits, or one loop that returns to frame 1.
- Hook shape: the first on-screen line is the hook; workshop it like any cover.
- Captions: a word on the beat, or none when the type is the picture.
- Route: `motion-video.md` for the picture. Voice-over is optional and sits under
  the track. Do not invent a song.

## kinetic-list

- When: a ranked list, and every item clears one threshold from one source.
- Aspect / length: 9:16, 20–30 s.
- First 3 s: the count and the threshold, then the first item.
- Visual / edit: kinetic type, fast cuts, one item per cut.
- Structure: a list. Hook shape: ranked list with a threshold.
- Captions: the type is the caption.
- Route: kinetic type (`motion-video.md` companion `kinetic-typography`). Not a
  character film.

## screen-tutorial

- When: the viewer repeats one task in the product after watching.
- Aspect / length: 9:16, or 16:9 when the UI will not survive a crop. 60–90 s.
- First 3 s: the finished result, then the rewind into step 1.
- Visual / edit: screen recording, a screen tutorial.
- Structure: a list of steps. Hook shape: compression promise ("the whole task
  in one minute") only when the film really is that task.
- Captions: lower third, one step name at a time.
- Route: a capture of the real UI. Check every control against the product.
