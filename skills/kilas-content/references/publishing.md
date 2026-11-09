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

## Threads web

New thread → first post → "Add to thread" for each reply → media icon on the post that
carries `media: slides` → read back every post's text and the image count → Post → open
the profile and record the link.

- A link in the text (a source such as `tencent.com`) turns into a preview card that takes
  the media button's place, one card per link. Close each card (× on the card) before
  attaching the slides, then count the attached images.
- Instagram's file input is hidden: wait for the file chooser and click "Select from
  computer" (in ego-browser `page.waitForFileChooser()` then `chooser.setFiles(paths)`).
