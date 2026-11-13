# Video racikan

Before a Reels video is scripted, fill a racikan: the format, the look, and the
gate. A carousel, a single post, a thread, and a shoot-only storyboard skip this
file. A script the owner will film themselves uses `formats/reels-tiktok.md` and
skips it too.

The racikan is a short table in the item's `brief.md`. It is not a second skill,
and it does not replace `writing-craft.md`, `formats/reels-tiktok.md`, or
`motion-video.md`. Those still run, in that order, after the table is settled.

## 1. Fill it in one pass

Read what the owner already said. Anything they named is settled: format, length,
aspect, look, or a line from `design.md` "Video". Do not ask again for a value
they gave.

For the rest, pick the closest card in `video-presets.md` and fill the table.
Show the table once, name the preset, and say in one line why that card and not
the next closest. Then ask once: keep this, or switch to the other card. A reply
that only adds a fact ("make it 20 seconds") changes that row and does not
restart the questions.

When the request already names the preset ("the diorama one", "a screen demo"),
write the table and go on to the script. Do not ask.

## 2. The table

Write this under `## Racikan` in `brief.md`, above the story questions when the
piece is a video, using the headings in `templates/brief.md`.

| Field | What to write |
|---|---|
| Preset | the card id from `video-presets.md` |
| Format | short reel, explainer, product demo, news, or music |
| Aspect | a ratio the preset names, unless the owner named one |
| Length | seconds, from the preset, unless the owner named one |
| Visual style | vector characters, kinetic type, isometric diorama, or screen recording |
| Edit style | fast cuts, one continuous scene, or a screen tutorial |
| Hook shape | a shape from `writing-craft.md` section 3 or 3b; the workshop still happens |
| Structure | before/after, three acts, or a list |
| Captions | lower third, a word on the beat, a title card, or none |
| Gate | the owner approves the beat map and the 10 s animatic before any render |
| Who chose | `owner` or `skill` on every row the owner did not name |

The hook row picks a shape. It does not write the hook. Five hooks, the gates,
and the duels stay in `writing-craft.md`.

## 3. What a blank means

A field the owner left blank is the skill's to fill from the preset, then from
the brand pack:

1. The preset's own default for that field.
2. `design.md` "Video", when the pack has one: cast, mascot, voice, and any
   look it names beat the preset's visual style.
3. `formats/reels-tiktok.md` section 0, so the kind still rotates and two product
   Reels do not run back to back.

Write `skill` in Who chose, and the one-line reason next to the row. A blank
cell, or the words "the skill will decide" with no choice written down, is
not a fill.

## 4. Then the film

After the owner has seen the table (or had already named the preset):

1. Story, hook workshop, and beats: `writing-craft.md` and `formats/reels-tiktok.md`.
2. Production: `motion-video.md`. The gate row is the existing gate there. A
   render does not start before the owner approves the beat map, the animatic,
   and the script.

Open prompt collections are a shelf, not a preset. `video-presets.md` names one.
Copy a prompt from it only when the owner points at that file, keep the creator's
credit in `brief.md`, and still run this table. Do not vendor a collection into
the skill.
