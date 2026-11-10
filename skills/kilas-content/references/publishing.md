# Publishing through a signed-in browser (only on the owner's explicit go)

Publishing is the owner's step. When the owner explicitly says to post a specific piece
("posting", "share sekarang"), post that piece only, with the text in `publish.md`.

## Instagram web (tested 2026-11-09, ego-browser)

1. Create → Post → "Select from computer" → all slides at once (`preview/slides/*.png`).
2. Crop: the default is 1:1 and cuts a 4:5 slide; set **4:5** (crop icon, bottom left) and
   look at the frame before "Next".
3. Caption from `copy.md`; check the counter (≤2,200).
4. **Share to**: Threads and the owner's personal Facebook are on by default. Turn both off
   for this post; on the Facebook prompt choose "Don't share this post" (never change the
   owner's global setting). Threads gets its own text, posted separately.
5. Accessibility → alt text per slide from `publish.md`. Fill each field by clicking it, then
   read every field back; scripted fills can land in the wrong field.
6. AI label: only for realistic AI photos or video; a 3D mascot does not need it.
7. Screenshot the final screen. Share (or Schedule content) only as the owner chose.
8. Open the profile, confirm the newest post and its caption, record the link in
   `publish.md`, set the brief status to `terbit`.

## Instagram Reels from a video (tested 2026-11-10)

1. Create → Post → set the MP4 on the hidden file input → "Video posts are now shared as
   reels" → OK.
2. Crop: choose **Original** (keeps 9:16); look at the frame before "Next".
3. Edit: the cover defaults to frame 0 (make frame 0 the hook still); check the trim shows
   the full length.
4. Caption from `publish.md`; read the field back. Share to Facebook off, schedule off.
5. Accessibility: Reels on the web has no alt-text field, only auto-generated captions; turn
   those on. Keep the alt text in `publish.md` for the app.
6. AI label: on when the video carries a synthetic voice or realistic AI footage (Meta asks
   for it on realistic AI audio); say so to the owner, who can switch it off from the
   post's ··· menu.
7. Share, wait for "Your reel has been shared", open `/<handle>/reels/`, open the newest
   reel, confirm the caption, record the link.

## Threads web

New thread → first post → "Add to thread" for each reply → media icon on the post that
carries `media: slides` (or the video: set it on that post's own file input, the second one
in a two-post thread) → read back every post's text and the media count → Post → open the
profile and record the link.

- A link in the text (a source such as `tencent.com`) turns into a preview card that takes
  the media button's place, one card per link. Close each card (× on the card) before
  attaching the slides, then count the attached images.
- ego-browser selectors are CSS plus `:has-text()`; `:text("Add to thread")` is rejected.
  Mark the leaf element whose text is "Add to thread" with a `data-*` attribute in
  `page.evaluate()` and click that; mark the newest `[contenteditable=true]` the same way.
- Instagram's file input is hidden: wait for the file chooser and click "Select from
  computer" (in ego-browser `page.waitForFileChooser()` then `chooser.setFiles(paths)`).
