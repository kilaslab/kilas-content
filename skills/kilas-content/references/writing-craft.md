# Writing craft: story, hook, headlines

`copy-playbook.md` lists the rules. This file teaches the moves behind a carousel that
people swipe to the end, step by step, so any agent can repeat them. Two worked
examples, each with its rejected drafts: the Linux 7.4 carousel, a news record
(`examples/linux-7.4-carousel.md`), and the AI-cost-of-JS-frameworks carousel, someone
else's experiment (`examples/ai-cost-js-carousel.md`). The extra hook shapes and ladders
come from a scrape of tech posts, with the evidence in `patterns-from-data.md`.

Work through the sections in order. Each one ends with something you write down before
moving on: story work in the item's `brief.md`, published text in `copy.md`. The method
is the same for every format; `formats/` says how a ladder becomes slides, posts, or
video beats.

## 1. Find the story before writing a word

Read the source article, then open the articles it links. The best material is usually
one link deep: in the Linux 7.4 case the maintainer quote, the reverted anti-bot feature,
and the bugs found by AI review were all in linked articles, not in the main one.

Then answer five questions, one sentence each:

| Question | Linux 7.4 answer |
|---|---|
| What changed? | 19.671 commit in one merge window, a record |
| Compared with what? | normal is 12–14 ribu; the old record was 16.267 (7.3) |
| Why? | AI-generated bug reports and patches; a maintainer says "completely overwhelmed" |
| What complicates it? | the anti-noise feature got reverted; AI review also found real bugs |
| So what for an Indonesian reader? | reviewer time is the bottleneck; check your AI-assisted patch before sending |

If you can only answer the first question, you have a stat post, not a carousel. Go back
to the links.

**Bring it home.** Most sources are written for American or European readers. The fifth
answer is where the story becomes Indonesian. Look for, in this order: the price in
Rupiah and the date it applies ("naik di Indonesia per 1 Juli 2026"), availability or a
launch date here, an Indonesian company or user affected, an Indonesian contributor, and
last, a local metaphor (Pintu Air Manggarai). Convert currencies only with the rate and
its date in a `>` note; an official Rupiah price beats any conversion. If nothing local
exists, say what the reader can do, as the Linux tip did. Never invent a local angle.

**Look for the turn.** A story with a turn beats a story with a villain. "AI floods the
kernel" is one note. "AI floods it, and AI is also what the maintainers use to hold the
water back" gives the reader a reason to reach slide 6. When a source is one-sided, the
turn is often in a linked article or in what the people involved say they will do next.

Write down: the five answers, and one sentence naming the turn.

## 2. Build the ladder

Order the slides so each one answers a question the previous one raised:

```
angka (hook) → konteks → bukti → penyebab → ironi/komplikasi → sisi lain → makna → ajakan
19.671         pintu air  grafik   AI patch   fitur di-revert     AI review  reviewer  ikuti
```

Rules for the ladder:

- The hook raises a question, and the middle slides answer it in order of surprise,
  smallest first, so the swipe keeps paying off.
- Put the turn late (slide 5 or 6 of 8). Too early and there is nothing left to swipe for.
- One slide per rung. If a rung needs two slides, the second one is usually a detail
  that belongs in the caption.

**Pick the ladder for the kind of story.** The one above is the news ladder. Two more
held up in the data:

| Story | Ladder | Notes |
|---|---|---|
| A news beat, a stat, a finding | **Berita**: angka → konteks → bukti → penyebab → komplikasi → sisi lain → makna → ajakan | the default; Problem-Proof |
| Someone tested a tool, model, or device (the brand, or a named person or lab) | **Uji coba**: setup and constraint → what happened → yang berhasil → yang gagal → pelajaran → vonis → ajakan | give the failures their own slide; the verdict may be "not worth it" |
| A set of things the reader will want to keep | **Daftar referensi**: count + threshold → items ranked by one value → how it was picked and the source → ajakan | 5–6 rows per slide, value column right-aligned, `1/2`, `2/2` in the eyebrow; Value-Stack |

The uji coba shape comes from a thread that reported pros, cons, and learnings and then
admitted "I had to send more apologies for the AI's behavior than it would have taken
for me to just plan the afternoon myself". The honest verdict is what makes the earlier
slides believable.

**One slide worth saving.** Every carousel needs one slide a reader would screenshot:
a checklist, a comparison table, a ranked list, a diagram, or steps. In the data, the
posts saved about as often as they were liked were all reference material. In the Linux
carousel it is the tip on slide 7; in a daftar referensi it is every slide.

Write down: the ladder, one rung per slide, and which slide is the one worth saving.

## 3. Write the hook (slide 1)

Formula: **exact number** + **a line that turns it into a scene** (what, where, how
fast) + **one sentence of stakes that names the cause without explaining it**.

```
19.671
commit masuk ke kernel Linux dalam dua minggu.
Merge window terbesar sepanjang sejarah Linux. Banyak di antaranya dipicu laporan bug dan patch hasil AI.
```

Why each part works:

- **19.671, exact.** An exact number reads as reported fact; "hampir 20 ribu" reads as a
  headline someone rounded up. Exactness also lets a reader check you.
- **The scene line** gives the number a unit (commit), a place (kernel Linux), and a time
  window (dua minggu). The time window is what creates scale.
- **The stakes line** says "record" and "AI" and stops. The reader now has a question
  (how did AI do that?) and the slides answer it.

**Workshop it in three steps: five shapes, gates, duels.**

1. **Write five hooks in at least three shapes.** Five variations of one shape is one
   hook. Shapes: number + scene (above), paradox (two facts that pull against each
   other: "biaya beda 86%, skor nyaris sama"), experiment ("60 kali agent AI membangun
   aplikasi yang sama"), stakes for the reader, a concrete comparison, or a shape from
   section 3b.
2. **Gate each one, pass or fail, with the reason written down.**

   | Gate | Fails when |
   |---|---|
   | Short | more than 30 words on the cover, eyebrow excluded |
   | Plain | the reader must know a term to care (median, run, MCP, API cost) that the audience does not say daily |
   | Clean | a caveat sits on the cover ("harga API, bukan tagihan", "satu aplikasi kecil"); caveats have their own places (section 7b) |
   | Honest | a word is stronger than the source ("tagihan" when the source says API list price) |
   | Open | the cover gives away what the slides reveal: the winner, the cause, the turn |
   | Tension | nothing pulls against anything: no paradox, no stakes, only a number |

3. **Duel the survivors as a stranger scrolling past.** Take them in pairs: which one
   would make someone who has never heard of the story stop? Write one sentence on why
   the loser loses. The hook that wins the most duels is the cover. On a tie, keep the
   one that leaves more for the slides.

Why not score them: self-scores saturate. In a test run a model gave four of its five
hooks the maximum score, broke the tie on length, and put the flattest one on the
cover ("US$4,97 median biaya API untuk satu app Pokémon di Angular", with a disclaimer
under it). A duel with a written reason cannot end in a five-way tie. The full workshop
for that story is in `examples/ai-cost-js-carousel.md`.

Rejected drafts from the Linux carousel, and why:

| Draft | Problem |
|---|---|
| "Linux 7.4 Pecahkan Rekor!" | a category, not a number; exclamation mark |
| "Hampir 20 ribu commit" | rounded, so it reads as hype |
| "AI menghancurkan kernel Linux" | the source never says this: an invented, stronger claim |
| "Tahukah kamu soal merge window?" | stock opener, and it opens on jargon |
| "Kernel Linux kebanjiran" | a good metaphor without the number has nothing to check |

Write down: the five hooks with their shapes, the gate results, the duels with the
loser's reason, and the winner.

## 3b. Other hook shapes

The number + scene + stakes formula is the default. These six shapes each beat their
own account's usual post by a wide margin in the data (`patterns-from-data.md`). Use one
when the story has that shape; never bend a story to fit one. The gates and duels still
apply.

| Shape | Source post | Indonesian version | Only when |
|---|---|---|---|
| Experiment with a constraint | "I gave my Dot a $500 budget and 24 hours to plan an entire afternoon" | "Peneliti MIT meninggalkan 13 agen AI di pulau virtual tanpa tugas. Mereka mulai melakukan sesuatu yang mirip bermain." | the test really ran; name who ran it |
| Switch | "I stopped using CCleaner after finding a free open-source cleaner" | "Kami berhenti memakai <alat lama> setelah mencoba <alat baru>, yang gratis dan open source." | the brand actually switched; otherwise quote who did |
| Product + price | "Apple Homeview is official. $299" | "<Produk> resmi. Rp<harga> di Indonesia." | price and market are confirmed; two facts, no adjectives |
| Compression promise | "This is the future of SaaS in 1 image" | "Arsitektur agen AI dalam satu gambar." | a slide really holds the whole idea as one diagram |
| Ranked list with a threshold | "22 remote roles paying $300K+" | "<n> model AI open source dengan skor di atas <ambang> di <benchmark>." | every item meets the threshold, from one source |
| Absurd concrete comparison | a GPU in a grocery bag: "this is what $4000 gets you" | "Harga satu GPU ini setara <n> bulan UMR Jakarta." | the arithmetic is in a `>` note, with the year of the UMR |

The angle-bracket parts are slots, not facts: fill them from the source, with a `>`
note. The MIT line restates the source post and keeps its hedge: the post says the
agents did "things that look a lot like play", so the slide says "mirip bermain", not
"bermain".

First person ("kami", "aku") appears only when the brand did the thing. A borrowed
experiment written in first person is a fabrication.

**Stock openers to avoid.** Indonesian media carousels open with the same lines: "Mau
X? Cek 3 Hal Ini Dulu!", "Yuk, kenali ...", "Siapa bilang ...", "Masih bingung ...",
"Jangan buru-buru beli!", "Bukan Cuma X, Ini Rahasia Y". A reader has seen each of them
a thousand times, so they mark the post as one more of the same. `lint_copy.py` flags
them.

## 4. Pick one metaphor family and carry it

An analogy the reader already lives with makes jargon land in one line. Pick it, say it
once explicitly, then reuse its verbs.

How to find it:

1. Describe the mechanism's shape in plain words. A merge window *opens for a fixed time,
   lets a volume through, then closes.*
2. List local, everyday things with the same shape: pintu air, jam buka loket, gerbang
   tol, pintu kereta.
3. Pick the one whose verbs fit the rest of the story. Pintu air wins because the story
   also has a flood (banjir), a surge (meluap), and an attempt to hold it back
   (membendung). For Jakarta readers it also comes loaded: Pintu Air Manggarai.

How to carry it:

- Introduce once, plainly: "Anggap saja pintu air."
- After that, use it only in verbs and nouns of the headlines: "datang tanpa henti",
  "membendungnya". **At least three interior headlines carry it.** A metaphor named on
  slide 2 and never seen again is decoration; one that returns in the headlines is how
  the reader keeps the story in one picture. The AI-cost carousel's "argo taksi" came
  back as "Argo Angular 86% lebih mahal", "membuka peta", "Navigasi resmi", and "Argo
  jalan lagi". A draft of the same story named "argo taksi" on slide 2 and dropped it
  until slide 7.
- Put the verbs on their own line in `brief.md` (`Verbs: argo, peta, navigasi`).
  `lint_copy.py` reads that line and counts the headlines that use them.
- Let the photos follow it (dam, sluice gate, water texture), so image and text say the
  same thing.
- Never mix families. Pintu air plus "bom waktu" plus "tsunami" reads as filler.
- Drop it on data and quote slides; facts carry those on their own.

Write down: the mechanism's shape, the candidates, the pick, and the verbs it gives you.

## 5. Headlines that tell the story alone

Each interior headline is a sentence with a verb, 3–7 words, that makes a claim the slide
body proves. Topic labels ("Data", "Penyebab") go in the eyebrow above it.

**Headline-only test.** Read only the headlines in order. They must tell the story:

> 19.671 commit dalam dua minggu. Anggap saja pintu air. Rekor lama dilewati 3.404
> commit. Patch hasil AI datang tanpa henti. Penyaringnya sendiri sudah di-revert. AI
> juga dipakai untuk membendungnya. Waktu reviewer jadi barang langka. Ikuti @<handle>.

If a headline could sit on any slide ("Ini faktanya", "Lihat datanya"), rewrite it with
the fact in it.

**The "lalu kenapa?" test.** A headline that only reports an event makes the reader
ask "lalu kenapa?" (so what?). Put the answer in the headline: a consequence, a cause,
or a comparison the reader can feel.

| Event only (rejected) | Claim with a consequence |
|---|---|
| Panduan v3 dibaca di setiap run. | Jalan baru membuat agent membuka peta. |
| Selisih ujungnya US$2,30. | Argo Angular 86% lebih mahal dari Hono+htmx. |
| MCP Nuxt tidak pernah dibuka. | Navigasi resmi tidak menjamin argo murah. |
| Linux 7.4 dirilis dengan banyak commit. | Rekor lama dilewati 3.404 commit. |

The left column is accurate and still loses: each line is a fact with nothing at stake.
The right column names who wins, who pays, or what follows.

**Write the headline-only read into `brief.md`** before building. `lint_copy.py` prints
it too; read it once as a stranger would. If it does not tell the story, or the
metaphor vanishes after slide 2, fix the headlines before touching Figma.

Then mark the one or two words that carry the claim (in Figma they get the
highlighter): *pintu air*, *3.404 commit*, *tanpa henti*, *di-revert*, *membendungnya*,
*Waktu reviewer*. If you cannot pick the words, the headline has no claim yet.

Headlines end with a period. They are statements.

## 6. Make numbers do the comparing

- **Derive the number the reader would compute.** Raw values go in the chart; the
  headline gets the difference (3.404) and a stat cell gets the ratio (+21%).
- **Compare fairly.** Against the previous record (7.3, 16.267), not the smallest year.
  The fair comparison is still dramatic, and it survives a reader checking.
- **Indonesian format** in prose: 19.671, +21%, 455 ribu, 12–14 ribu.
- **Charts start at zero.** A chart scaled from the minimum turns +21% into a cliff; a
  reader who notices stops trusting every other slide. Mark the old record with a dashed
  line so the one bar that crosses it is the story.
- **Show the arithmetic** in a `>` note in `copy.md`: `19.671 − 16.267 = 3.404`.

## 7. Quotes and hedges

- **Keep a short quote in its original language** when its voice is the point: "We are
  completely overwhelmed, of course." Put the attribution and the explanation in
  Indonesian. Long quotes get paraphrased.
- **Name and role, never "para ahli":** "Jakub Kicinski · maintainer jaringan Linux".
- **Copy the source's certainty exactly.** "*seem* like AI-driven" becomes "tampak seperti
  ... buatan AI"; "a lot of the uptick" becomes "banyak di antaranya", never "sebagian
  besar". Upgrading a hedge is the same as inventing a fact.

## 7b. Hedges stay, caveats get a budget

Two kinds of honesty, two places:

- **A hedge** is the source's own certainty: "kemungkinan", "tampaknya", "menduga". It
  stays inside the sentence that makes the claim, on whatever slide that is.
- **A caveat** is a limit of the method or the data: "harga API, bukan tagihan", "satu
  aplikasi kecil", "sampel 4–5 post per akun", "median 5 run". It is true and it
  matters, and it still has a budget:

| Place | Caveats allowed |
|---|---|
| Cover and every headline | none |
| The data slide | one, as a small note under the chart or table |
| The opinion slide | one, as the reason the action is phrased the way it is |
| Caption and `>` notes | the rest |

A draft of the AI-cost carousel put "Ini harga yang dikutip Claude Code, bukan uang yang
dibayar" on the cover and "Rentang run-nya saling tindih" above the chart. Both are
true; on the cover they told the reader not to care before the story started. The
built version keeps both facts: the price caveat in the table note, the variance as
the opinion slide's reason ("Biaya Angular saja berkisar $3,19 sampai $6,82
antar-build"), the rest in the caption.

## 8. Opinion slide and takeaway

Put your own analysis on its own slide and label it in the eyebrow ("CATATAN
<BRAND>"). Give it one claim and one action:

- claim: "Waktu reviewer jadi barang langka."
- action: "Kalau patch-mu dibantu AI, baca ulang dan uji sendiri sebelum dikirim."

The action is what earns the save. An opinion slide without an action is a closer that
repeats the story.

**Test the action with three questions.** Who does it: the reader, not a vendor or a
maintainer? With what: tools or access the reader has today? When: could they start
this week? Fail one and rewrite.

| Action | Result |
|---|---|
| "Kalau patch-mu dibantu AI, baca ulang dan uji sendiri sebelum dikirim." | passes |
| "Uji kandidatnya dengan tugas yang sama, minimal 3 build per framework, lalu bandingkan angkanya." | passes |
| "Pastikan dokumen versi itu ada di data latih." | fails "with what": no reader can inspect a model's training data |
| "Mari bijak menggunakan AI." | fails all three: no step to take |

When you can, prove the action is possible. The AI-cost carousel put a screenshot of
the benchmark's README ("please open an issue or create a fork") above its tip.

## 9. The close

CTA = verb + handle + what they get, and the promise must describe what this carousel
just did:

```
Ikuti @<handle>
Kabar teknologi seperti ini, lengkap dengan angka dan sumbernya.
```

Do not promise a frequency or a format you cannot verify ("tiap hari", "eksklusif").

## 10. Sentence-level voice

- Short declaratives, one idea per sentence, lengths varied. Varied is the key word:
  three sentences of five words in a row read as notes, not prose ("Rentang run-nya
  saling tindih. React Router sempat US$2,82. Hono+htmx sempat US$3,19."). Join two of
  them with the relation between them.
- Verbs over nominalisations: "menandai", not "melakukan penandaan".
- Concrete nouns: "bot yang memasang driver sembarangan", not "aktivitas otomatis yang
  bermasalah".
- Technical terms stay in English when developers say them in English (merge window,
  patch, maintainer, revert, use-after-free, passthrough). Everything around them is
  Indonesian.
- "Kamu" only where you speak to the reader directly (the tip). The rest is report voice.

## 11. Before building

1. Headline-only test (section 5), written in `brief.md`; the metaphor is in at least
   three interior headlines; every headline passes "lalu kenapa?".
2. Thumbnail test: would the cover alone stop you at phone size? It passed the gates
   and won its duels (section 3).
3. Caveat budget (section 7b) and the action test (section 8).
4. Source test: every number, name, and quote has a `>` note.
5. `python3 scripts/lint_copy.py copy.md --format <format> --brand <pack>/brand.md` exits
   0. Read its warnings yourself; the cover, caveat, metaphor, and staccato warnings are
   the ones that most often mark a weak draft.
6. Read the whole thing aloud once. Rewrite any sentence you stumble on, and join
   sentences that sound like a list of notes.
