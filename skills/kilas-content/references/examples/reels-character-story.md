# Worked example: a 33 s character Reel ("panicked seller vs calm seller")

The reference Reel for this skill: a product story acted by two vector characters, with an
ElevenLabs voice-over, rendered with HyperFrames. It shipped, was audited on a phone, and
scored 6/10. This file walks the whole line in order, with the command and the done-check
of every step, then the audit findings and what each one changed. Read it before your first
Reel; imitate the moves, not the words.

Written for an Indonesian chat-commerce product. `<BRAND>` is the product, `<MASCOT>` its
mascot (an AI chat assistant), `<SELLER>` the human character, `<skill>` the path of this
skill, `<item>` the item folder. Every number below is the real one from that film.

## 0. Before anything: kind and slot

- Kind: **story** with a product turn (the demo kind). The plan rotates Reels kinds (news,
  explainer, story, demo); the next Reel after this one was AI news. Two product Reels never
  sit side by side (`planning.md`).
- Run `python3 <skill>/scripts/lessons.py rules content` and read every active rule.
  Done when: you can name the rules that touch video (text size, loudness, crop, claims).
- Product claims shown in the film (shipping-cost check, automatic QRIS payment, owner
  watches a dashboard) were **confirmed by the owner** first and written in `brand.md`.
  A claim the owner has not confirmed stays out of the film.

## 1. Brief and logline

```
Logline: Two seller inboxes on the first minute of the 11.11 sale. Top: the seller answers
every chat by hand and falls apart. Bottom: <MASCOT> answers, checks shipping, sends QRIS,
and the seller drinks tea. Twist: it is the same shop, last year and this year.
Viewer: online sellers who have lived through a flash-sale night.
Feeling: "that's me" laugh in the first 3 s, relief at the twist.
One idea: the same chat flood is calm when an assistant answers it.
Ends on: the CTA line, then a cut back to 00:00 so the loop replays.
```

Done when: the logline fits in five lines, names the viewer, the feeling, and the ending.
Then run the brief past the approved partner (section 2c of `motion-video.md`):
`bash <skill>/scripts/brainstorm.sh run <item>/brainstorm/brief-round1.md --self claude`.
Keep the brief narrow (one question per round); a broad brief timed out at 600 s.

## 2. Beat map (the whole film, before any animation)

| Time (s) | Beat | VO (as written for the voice) | On screen | Action |
|---|---|---|---|---|
| 0–3.3 | hook | Promo sebelas-sebelas baru semenit, chat udah empat puluh delapan. | Promo 11.11 baru semenit. Chat udah 48. | clock 23:59→00:00, both phones buzz, counter 0→48, top seller's eyes go big |
| 3.45–7.4 | context | Chatnya sama banyak. Bedanya, yang bawah dibantu <MASCOT>. | Chatnya sama banyak. | bubbles burst in both panels; bottom: mascot pops up and catches them |
| 7.5–12.5 | beat 1 | Yang atas copas "ready kak" satu-satu. Yang bawah? <MASCOT> cek ongkir, kirim kris, lunas. | Atas copas. Bawah udah lunas. | top: pastes "ready kak", gets bonked by a wrong-variant reply; bottom: shipping card, QRIS card, LUNAS stamp lands on "lunas" |
| 14–18.8 | beat 2 | Nego atau komplain tetap dioper ke kamu. Sisanya, tinggal pantau dashboard. | Nego dioper ke kamu. Sisanya pantau dashboard. | haggling bubble; mascot hands it to the seller; dashboard card counts up |
| 19.1–23.9 | beat 3 | Jam tiga pagi, yang atas baru bales. Pembelinya udah checkout di toko sebelah. | Dibales jam 3. Pembelinya udah pindah. | sky goes navy, clock spins to 03:12; top finally replies, buyer bubble walks off; bottom seller asleep, mascot answers |
| 24.1–27.9 | twist | Plot twist. Tokonya sama, tahun lalu dan tahun ini. | Tokonya sama. Tahun ini dibantu <MASCOT>. | both shop names become the same name with a highlighter; labels "tahun lalu" / "tahun ini" stamp in |
| 28.05–33 | CTA | Cobain <MASCOT>, asisten chat ei-ai untuk tokomu, dari <BRAND>. | Cobain <MASCOT>. Asisten chat AI untuk tokomu, dari <BRAND>. | end card, mascot waves, clock back to 00:00 |

Rules this table follows:
- **Write the VO the way it is said.** QRIS → "kris" (the first take said "queries"),
  11.11 → "sebelas-sebelas", 48 → "empat puluh delapan", a domain `.id` → "titik
  i-d". The on-screen line keeps the normal spelling. This film wrote AI as "ei-ai"; a later
  film found that respelling read letter by letter, so English acronyms now stay in English on
  `eleven_v3` (`motion-video.md` 5).
- **Budget every beat**: VO seconds ≈ words ÷ 2.5, plus 0.3–0.6 s of reaction hold. Beat 1
  has 14 words → 5.6 s at ×1 speed, 5.0 s at ×1.05: it fits 7.5–14 with a 1 s hold. An
  on-screen line needs 0.5 s + 0.3 s a word (6 words → 2.3 s). Cut words from a beat that
  does not fit; never squeeze the speech.
- **Story formula**: the paradox stated as a fact (48 chats in one minute), escalating
  beats (copy-paste, haggling, 3 a.m.), the pivot (plot twist), an ironic payoff (same shop),
  the film ends on the last word.
- Total VO here: 75 words for 33 s, right at the ±75-word target of `lint_copy.py`.

Done when: every beat has VO, on-screen text, an action, and a time that passes the budget.

## 3. Animatic of the first 10 s (gate 1)

Build the scene once and use it for both the animatic and the film: one SVG stage, one
paused GSAP timeline, the rig from `templates/video/rig.js`.

```js
const R = KilasRig.create(svg, { palette: { accent: "#14786B", mascot: "#22A08F" } });
const tl = gsap.timeline({ paused: true });
const A = KilasRig.acting(tl);
const cam = A.camera(R.el(svg, "g", {}));          // every visible thing goes inside cam
const top = R.person(cam, 120, {}), bottom = R.person(cam, 120, {});
const mascot = R.mascot(cam, 860, 1500, {});

// hook: on frame 0 something already moves
A.face(top, 0, "normal", "smile");
A.jitter(top.armR, 28, 22, 0.0, 0.04, 8);           // phone buzzing from frame 0
A.creep(0, 1.0);                                    // slow push-in on the hold
A.face(top, 1.08, "big", "o"); A.take(top, 1.08, 0.08);
A.kick(1.08, 10);                                   // the impact of "00:00"
A.count(counterText, [[1.3, 0], [2.6, 48]], " belum dibalas");
A.blink(top, 0.45); A.blink(bottom, 0.7);
// ... the remaining beats ...
A.finish();                                         // counters stay right in stills and renders
```

- The animatic is an artifact: the live 10 s, one still per second from the same timeline
  (`tl.seek(t)`), the full beat table above with one key still per later beat, and the VO
  table with a copy button.
- Show it to the owner. In this film the owner sent back: the mascot is out of proportion
  in some frames, and add the three product features. Both were fixed in the animatic, not
  after the render.

Done when: **the owner approves the beat map, the animatic, and the VO script.** No VO and
no render before that.

## 4. Voice-over

```bash
python3 <skill>/scripts/vo_elevenlabs.py <item>/copy.md <item>/audio      # one clip per vo: line
python3 <skill>/scripts/vo_elevenlabs.py --verify <item>/audio <item>/copy.md
```

- Voice: a young, conversational female voice, `eleven_multilingual_v2`, speed ×1.05.
  Neighbouring lines go along as context, so the seven clips sound like one take.
- Exit 3 means the key lacks `text_to_speech` (or `speech_to_text` for `--verify`): ask the
  owner to enable it; do not work around it.
- Put each clip on the timeline at its beat start with its **measured** duration
  (the script prints it), e.g.
  `<audio id="vo2" class="clip" src="assets/vo2.mp3" data-start="7.5" data-duration="5.011" ...>`.

Done when: `--verify` shows the transcript equal to the script in order (a misheard word
means rewrite the spelling and generate that clip again).

## 5. Animate the rest, timed to the words

- Write every beat **at its VO time from the start**. This film first animated to guessed
  times, then shifted every tween after 6 s by +1.25 s (and the bottom panel's payment block
  by +5.2 s) so "lunas" landed on its word. That retiming loop is fragile; do not repeat it.
- Word times: `vo_elevenlabs.py --verify <item>/audio/vo2.mp3 --words words.json`. Land each
  reaction 0–3 frames **before** its word (the stamp hits at the start of "lunas").
- Every hold gets a `creep`; every cut between beats a `glide` of 18–40 frames; every
  impact a `kick`. Something new appears every 2–4 s. Blink every 0.5–2.3 s.
- Panels: wide (about 960 px) and centred; characters at least a third of the panel height;
  chat text 34 px or more (26 px read as about 9 px on a phone); nothing under the bottom
  UI band (`motion-video.md` 4).

Done when: you can play the timeline and name, for each second, what is new on screen.

## 6. Render and the measured check

```bash
cd <item>/video
npx hyperframes check --json                      # until 0 errors
npx hyperframes snapshot --at 0,3,7.5,14,19,24,28 # look at every still
npx hyperframes render -q draft -o ../export/draft.mp4
python3 <skill>/scripts/reel_qa.py ../export/draft.mp4 --hold 0-0.3,29-33
```

`reel_qa.py` must exit 0. On this film it failed three checks (it was written after the film
shipped, and it reproduced the audit):

```
PASS format: 1080x1920, 30.00 fps, 33.00 s, audio yes
FAIL loudness: -19.1 LUFS (target -14 ±1), true peak -2.5 dBTP (≤ -1)
FAIL frozen: frozen spans ≥12 f outside holds: [(0.03, 1.0), (5.93, 7.33), (8.6, 9.07),
  (10.27, 11.3), ... 15 spans in all, (28.87, 32.97)]
PASS flash: single black/white frames at: none
FAIL dead: dead seconds (motion < 1.5): [6, 8, 17, 18, 22, 23]
```

Read it like this: the first span means the hook frame sat still for a whole second; the
last one starts at 28.87, just before the 29 s hold, so the end card needs its hold window
to start at the cut (`--hold 0-0.3,28.8-33`) or a creep. The middle spans are the still
camera: a `creep` on every hold clears them.

Fixes, in that order: loudness with
`ffmpeg -i in.mp4 -c:v copy -af loudnorm=I=-14:TP=-1.5:LRA=11 -c:a aac -b:a 192k out.mp4`
(this film went to −14.9 LUFS, peak −1.3); each dead second gets a reaction, a push-in, or
a shorter beat.

Done when: `reel_qa.py` exits 0 and you have looked at every page of `contact*.png` and `phone*.png`.

## 7. Critique loop (gate 2)

Send every `phone*.png` page and the contact sheets with a narrow brief to the approved partner
(`brainstorm.sh run ... --self <your family>`), scoring the seven criteria 1–10 with
evidence. Every criterion needs **8 or more**; below that, fix and score again. The first
film, scored after it shipped:

| Criterion | Score | Evidence | Fix that is now a rule |
|---|---|---|---|
| Hook in 2 s | 7 | frame 0 clear, first motion only at 0.5 s | something moves on frame 0 |
| Phone readability | 4 | 26 px bubbles ≈ 9 px at 360 px; chips unreadable | text ≥ 34 px, fewer and bigger bubbles |
| Motion quality | 6 | expressions and arm pivots clean, holds too long | `creep` on every hold |
| Variety every 2–4 s | 6 | dead at 6, 8, 17–18, 22–23 s | a reaction or a shorter beat in each |
| Composition | 6 | characters ≈ 25 % of the panel height, empty desk | characters ≥ a third of the panel |
| Brand fit | 8 | colours, on-model mascot, confirmed claims | keep |
| Sound sync | 7 | VO 100 % match and on the beats, but −19 LUFS, no SFX | −14 LUFS, SFX on visible actions |

Average 6.3; six of seven below 8. Under the gate it would not have rendered at delivery
quality. When no partner is available, write the scores as "self-scored" and say so to the
owner.

Done when: every criterion is 8 or more, scored by the partner (or marked self-scored).

## 8. Delivery render, file check, preview, post

```bash
npx hyperframes render -q delivery -o ../export/<name>.mp4
python3 <skill>/scripts/reel_qa.py ../export/<name>.mp4 --hold 0-0.3,29-33
python3 <skill>/scripts/vo_elevenlabs.py --verify ../export/<name>.mp4 <item>/copy.md
```

- Preview artifact: the MP4, the caption, and the posting steps. The owner asked for two
  layout fixes after the first render (wider centred panels, a smaller watermark, chat text
  cut off, the closing line). Each one became a lesson the same hour.
- Posting only on the owner's explicit go (`publishing.md`): Instagram Reels with crop
  **Original**, the AI label on (synthetic voice), auto captions on; Threads with the video
  attached after closing the link preview.

Done when: the film is live, its links are in `publish.md`, and every owner remark is a
lesson.

## What to copy from this example, and what not

Copy: the contrast plus twist structure, writing the VO for the ear, the per-beat budget,
the animatic gate, the measured check before taste, scoring with a different model.
Do not copy: animating before the VO times are known, small chat text, a still camera,
seconds where nothing changes, and a quiet mix.
