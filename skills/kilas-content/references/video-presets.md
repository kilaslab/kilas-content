# Video presets

Eight cards. Pick one in `video-racikan.md`. A card sets defaults. The owner's
words and the brand pack's `design.md` "Video" section override a default.

Each card names the production route. A character film and a diorama both use
`motion-video.md` (`templates/video/`). A demo uses a screen recording. Do not
mix a diorama and a screen recording in one film unless the owner asks for both.

Hook shape is a pointer into `writing-craft.md`, not the line itself.

A public shelf of code-animation prompts, for when the owner wants a look none
of these cards cover: [awesome-opus5-5-videos](https://github.com/yihui-dev/awesome-opus5-5-videos)
(creator-credited prompts; HTML, Canvas, SVG, GSAP, Three.js). Credit the file
you copy. It is not a ninth preset.

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

## isometric-diorama

- When: a system, a place, or a product explained as a small world on a block.
- Aspect / length: 9:16, 45–60 s.
- First 3 s: the camera already on the world, one object moving.
- Visual / edit: isometric diorama, one continuous scene.
- Structure: three acts. Hook shape: compression promise.
- Captions: title card at the open, then lower third.
- Route: `motion-video.md`. Build the world from the vector rig in
  `templates/video/rig.js`: a block, a few objects, the cast standing on it.

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
