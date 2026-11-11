# Worked example: a 60 s 3D explainer Reel ("what happens when a buyer chats at night")

The reference 3D explainer for this skill: how a shop's chat assistant answers a buyer while the
owner sleeps, with three capabilities (the shop's notes, a courier API, a payment gateway). The
first cut passed every measured check and still lost a lay viewer; two rebuilds later the owner
approved it and it shipped. This file walks the line that worked, with the command and the
done-check of every step. Follow it in order; adapt the story, keep the moves.

`<skill>` is this skill's folder, `<item>` the item folder, `<BRAND>` the product, `<MASCOT>` its
mascot. Every number below is the real one from that film.

## 0. Before anything

- Kind: **explainer** of the brand's own product. Check the plan's Reels rotation
  (`planning.md`): two product Reels side by side need the owner's yes.
- `python3 <skill>/scripts/lessons.py rules content`. Done when: you can name the rules on
  video, voice, claims, and posting.
- Read the product's code for every capability the film shows (`research-tools.md` 2, item 9):
  a light subagent returns each claim with file:line and live / flagged / roadmap. Anything the
  brand pack says differently goes to the owner. Done when: every on-screen claim has a source
  note in `copy.md`. (Here: notes search and hand-over were built in; shipping cost and payment
  run through APIs the seller connects.)

## 1. Story: one lived scene, one grammar

Shape for a lay viewer (owner and spouse could not follow a turning island with 12 headlines):

| Part | Seconds | What the viewer sees | Words on screen |
|---|---|---|---|
| Hook | 0–4.5 | POV: a buyer types to the shop at 23.47, sends; ticks turn blue | "Pembeli chat, kamu lagi tidur" |
| Intro | 4.5–12 | Dark bedroom, owner asleep; the shop's phone lights; `<MASCOT>` hops out of it, hushes, the chat grows out of the phone | "Asisten yang baca, asisten yang balas" |
| 1 | 12–25 | Question 1 lands in the chat; the mascot opens a binder of notes; the matching note rises as a card; the card flies into the chat as the reply | "Jawab dari catatanmu" |
| 2 | 25–37 | Question 2; "?" (not in the notes); courier box, parcel on the scale, price rolls; card flies into the chat | "Ongkir dicek langsung" |
| 3 | 37–48 | Buyer says yes; payment terminal; the QR flies into the chat; scanned, paid, receipt stamped | "Tagihan QRIS, langsung lunas" |
| Morning | 48–55 | Room turns cream; owner wakes; summary card: paid order, one chat waiting | "Bangun, udah lunas" |
| End card | 55–60 | Logo lockup fades in, mascot waves | CTA from the brand pack |

Rules the table follows (`motion-video.md` 2e): the chat is on screen from 10.8 s to the
morning; every step is *question arrives → one prop → result card → card flies into the chat*;
an everyday case (exchange within 7 days), not a clever one; jargon (RAG) only in the caption.

Write `copy.md` with one section per part (`shot:`, `onscreen:`, `vo:`, `>` source notes), then
`python3 <skill>/scripts/lint_copy.py <item>/copy.md --format reels --brand <pack>/brand.md` and
`lessons.py check`. Done when: both exit 0 and the VO is ≤ 115 words.

Second opinion on the concept, two partners at once on the same brief:

```bash
bash <skill>/scripts/brainstorm.sh run <item>/partner/brief-rework.md --self claude --partner codex &
bash <skill>/scripts/brainstorm.sh run <item>/partner/brief-rework.md --self claude --partner agy &
wait   # answers: brief-rework-codex.md, brief-rework-agy.md
```

Done when: you have written under "Brainstorm" in `brief.md` what you took from each and why.

## 2. Scene from the template

```bash
bash <skill>/scripts/new_scene3d.sh <item> content/brand/assets/logos/<logo>.svg
(cd <item>/scene && python3 -m http.server 8792) &
```

- `beats.js`: COPY (every word, in the shapes its comment lists), MASCOT (every colour key,
  from the brand's renders), T (times, set in step 4). Brand colours go in three places, listed
  at the top of `beats.js`. `scene.js`: the set and the three props, if the story needs others.
- Mascot first: compare `mascot-test.html` with every mascot render the brand publishes.
  `SIZE=1440,900 bash <skill>/scripts/scene_stills.sh "http://localhost:8792/mascot-test.html" <item>/frames/pose 0.6`
  (add `?view=3q` for a three-quarter view). Done when: face panel, tails, hands, boots, and
  colour match the renders side by side, and the eight poses read at 360 px.
- Props that open (the binder): stills at 4 moments of the opening. Done when: the cover lifts
  and falls to the hinge side, clear of the mascot.

## 3. Voice-over

1. Voice: 2–3 native voices from the ElevenLabs shared library read the same line; transcribe
   each (`vo_elevenlabs.py --verify <sample>.mp3`); the owner picks. Record it in `design.md`.
2. Clips, one per part, on v3 when the script holds English acronyms (AI, API):
   `python3 <skill>/scripts/vo_elevenlabs.py <item>/copy.md <item>/vo --voice <id> --model eleven_v3 --speed 1.0`
3. Every clip: `vo_elevenlabs.py --verify <item>/vo/voN.mp3 --words <item>/vo/wN.json`; read the
   HEARD line. A garbled word ("catatan toko" heard as "chat token toko") → regenerate only that
   clip: `--only N`. A brand name that keeps breaking → write it as said (two words instead of one).
4. Acronyms: `python3 <skill>/scripts/vo_acronym_check.py <item>/vo/voN.mp3 <item>/vo/wN.json AI API`.

Done when: every HEARD line matches the script (spoken spellings aside) and the acronym check
exits 0 for every clip that holds one. Then play the acronyms to the owner: the ear decides.

## 4. Timing on the words

From the word timings, place each clip (`VO_STARTS` in `beats.js`) and each event (`T`): the
note lights up on "tukar ukuran", the card rises on "Ketemu", the courier card on "API kurir",
the stamp on "lunas". Here: clips at 0.3, 4.5, 12.2, 25.8, 37.0, 48.8, 55.6 s; question 2 at
25.4, question 3 at 36.6. Leave 1–2 s after each reply for reading.

Done when: `python3 <skill>/scripts/scene3d_video.py <item>/scene <item>/video --vo <item>/vo`
prints every clip with no overlap and none past 60 s.

## 5. Stills, motion, owner

- Story stills at the moments that explain something:
  `bash <skill>/scripts/scene_stills.sh http://localhost:8792/index.html <item>/frames/f 1.5 8.9 9.6 13.2 17 20 24 27.8 31.6 34.6 41.3 47 51.2 57.8`
- Motion: stills every 0.1 s across the mascot's hop out of the phone and its first walk.
  Done when: no frame jumps and the silhouette stays two-legged.
- Close-ups: the mascot is ~100 px tall on a phone in the working shot, so each reaction
  (surprise, thumbs-up, confused, success) gets a camera push-in (`SHOT.cuMascot` in `CAMK`).
- Show the animatic to one person who has not seen the brief. Done when: they can retell
  "notes → courier API → QRIS until paid" in their own words, and the owner approves the
  storyboard page (stills, script, voice samples).

## 6. Render and check the file

```bash
python3 <skill>/scripts/scene3d_video.py <item>/scene <item>/video --vo <item>/vo
cd <item>/video && npx hyperframes check
npx hyperframes render -q delivery -o ../export/raw.mp4
ffmpeg -i ../export/raw.mp4 -c:v copy -af loudnorm=I=-14:TP=-1.5:LRA=11 -c:a aac -b:a 192k ../export/film.mp4
python3 <skill>/scripts/reel_qa.py ../export/film.mp4 --hold 35.0-36.6,59.4-60
```

- `check` flags text in chat lines that have scrolled out of the panel (occluded, low
  contrast): they are clipped on purpose; `data-layout-allow-occlusion` on the chat items and
  the headline band clears the layout ones. Fix every other error.
- `reel_qa.py` frozen spans: a camera move that ends exactly where a hold begins reads as a
  freeze; end the move later, give the held card a float, or a reaction. Declare only real
  reading holds with `--hold`.
- Transcript of the film and the acronym check on the film:
  `vo_elevenlabs.py --verify ../export/film.mp4 <item>/copy.md --words ../export/words.json`, then
  `vo_acronym_check.py ../export/film.mp4 ../export/words.json AI API`.

Done when: `reel_qa.py` exits 0, the transcript matches, the acronym check exits 0.

## 7. Critique, then post

- Send every page of `phone*.png` (30 s each) to the approved partner, naming each page's
  seconds; at most four rounds (`motion-video.md` 2c). Here the last round scored brand 9,
  sync 9, lay understanding 8, mascot expression 8, and variety 7 until the push-ins went in.
- Post on the owner's explicit go (`publishing.md`, Reels): crop Original, caption pasted with
  a trailing space so the hashtag suggestions close, AI label on (synthetic voice), automatic
  captions on, Facebook share off; open the new reel and check the caption.

## What the owner's feedback changed, round by round

| Round | Owner said | Change |
|---|---|---|
| Island cut | "I and my wife did not get what each move means; too fast?" | One set, chat always on screen, one idea per 12–15 s, literal props |
| Island cut | "the mascot has one leg, moves choppily" | Symmetric mascot, tails at the side, eased weights, 0.1 s motion strips |
| Island cut | "VO is bad, use a male voice" | Native male voice from the shared library, picked from samples |
| v2 | "AI / API still read with an Indonesian accent" | `eleven_v3`, measured with `vo_acronym_check.py` |
| v2 | "polish the mascot from the site's renders; more expressive" | Rig from every brand render; faces and gestures; push-ins on reactions |
| v2 | "'is typing' belongs on the right" | The brand's side (typing, replies) on the right |
| v2 | "the notes part is confusing; use a normal case" | Everyday question; one grammar: the result card flies into the chat |
| v2 | "the book opens upside down" | Hinge check stills before rendering |
| v2 | "say API (or plugin), not 'tool'" | The audience's term on the prop label |
