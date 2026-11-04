# Worked example: a research paper made plain (8 slides)

The third reference carousel. Linux 7.4 is a news record and the AI-cost carousel is
someone else's benchmark; this one is a research blog post full of its field's
vocabulary. The facts were right on the first draft. The owner still said the Indonesian
was hard to follow, four times: once for the jargon, once for a phrase that sounded
concrete and was not, once because the slides jumped topic ("tiba-tiba bahas game"), and once because the
doctor metaphor was pushed onto slides where it no longer fit ("bedah serupa ini ga
nyambung", "rontgen dulu juga ga masuk").
The lessons are the plain-language pass in `writing-craft.md` section 10b and the
"no detours" and "bridge" rules in section 2. The built version has 7 slides.

`<handle>` and `<BRAND>` stand for the brand's handle and name. Built with the layout
functions in `scripts/figma-helpers.js`, black-and-white scheme, underline mark.

## Story notes

- Source: Takehi, Teoh, Zhang, Khattab (MIT CSAIL), "Sparks of Weight-Space Programming",
  2 Nov 2026. Every number was checked against the downloaded page; no independent
  replication existed when the piece was made.
- What changed: GPT-6 Astra read raw network weights and edited 131.072 of Qwen3.5-0.8B's
  800 million (0,016%) without training; MATH-500 rose 7,9% → 48,1%.
- Why: the model looped. 93% of its MATH-500 answers ran to the 32.768-token limit, and
  the edit removed what triggered the loop.
- Turn: on Gemma 3 270M, which rarely loops, the same approach did nothing (6,8% → at
  most 7,7%). In the authors' words, editing weights "could not add an ability the model
  lacked".
- So what for the reader: a small model that scores badly may only be looping. Count the
  truncated answers before replacing it.
- Metaphor: rontgen and bedah. Shape: read the inside without running it, find one
  fault, make a small cut. Verbs: rontgen, sayatan, diagnosis (slides 02–04 only).
- Slide worth saving: 06, a three-item checklist.

## Hook workshop

| # | Hook | Shape | Gates |
|---|---|---|---|
| A | 0,016% bobot model AI diubah AI lain, tanpa dilatih ulang. / Nilai matematika Qwen3.5-0.8B naik dari 7,9% menjadi 48,1%. | number + scene + stakes | pass |
| B | Peneliti MIT memberi GPT-6 Astra bobot mentah sebuah model kecil dan satu tugas: buat ia lebih jago matematika. | experiment | pass |
| C | 0,016% bobot berubah, skor matematika naik enam kali lipat. | paradox | pass |
| D | Model AI sekarang bisa membedah model AI lain. | stakes | fails Honest (one lab, "very early") and Tension (no number) |
| E | 131.072 dari 800 juta bobot diubah. MATH-500 naik dari 7,9% ke 48,1%. | comparison | fails Plain (MATH-500) |

A beat B (B withholds anything checkable) and C (C has no actor; "diubah AI lain, tanpa
dilatih ulang" is the news).

## Three drafts of the same slides

| Slide | Draft 1 (facts right, jargon) | Draft 2 (plainer, one phrase unclear) | Built |
|---|---|---|---|
| 03 headline | Sayatan 0,016% bobot, skor matematika naik enam kali lipat. | Sayatan kecil, nilai matematikanya naik enam kali lipat. | same as draft 2 |
| 03 body | Astra hanya boleh menguji hasil editnya lewat forward pass… Gradient dan training dilarang. | Astra dilarang melatih ulang model. Ia hanya boleh mencoba hasil editnya beberapa kali: 10, 25, atau 50 putaran uji. | same |
| 03 table | MATH-500 · GSM8K · IFEVAL · MENTOK; rows "Edit · 10 pass" | MATEMATIKA · HITUNGAN · PERINTAH · MACET; rows "Diedit, uji 10×" | last column TERPOTONG, defined in the note as answers that repeat until they run out of room |
| 04 headline | Diagnosisnya: model macet berputar, bukan tidak mampu. | Diagnosisnya: model ini macet berputar sebelum menjawab. | Diagnosisnya: model ini mengulang kalimat sampai kuotanya habis. |
| 04 steps | thinking loop yang diperingatkan model card; satu arah di MLP layer 15 dan 19; dikurangkan dari 64 kolom output | mengulang kalimat terus sampai terpotong; satu pola kecil di dalam model | 85 dari 96 jawaban berisi kalimat yang diulang terus; kuota 32.768 token habis sebelum jawaban akhir; satu pola kecil; dihapus, 131.072 dari 800 juta bobot berubah |
| 05 (game) | Jaringan tulisan Astra mengalahkan PPO 100 juta langkah. | Model game buatan Astra mengalahkan hasil 100 juta langkah latihan. | cut: a different experiment in the middle of the Qwen story; the owner read it as a jump |
| 07 body | …Pelajaran soal loop-nya bisa kamu pakai sekarang. | …model kecil yang nilainya jelek bisa jadi cuma macet. | …bisa jadi cuma terjebak mengulang kalimat. |

Why draft 2 still failed, twice over: the game slide was a detour, and the phrase "macet berputar" borrows the feel of a stuck machine but does
not say what the reader would see. "Mengulang kalimat sampai kuotanya habis" names the
output itself. Ask of every key phrase: could someone who has never run a model
describe what happened?

## Metaphor headlines that did not survive

| Slide | Forced | Built | Why |
|---|---|---|---|
| 05 | Bedah serupa gagal membuat Gemma lebih pintar. | Dicoba pada model lain, hasilnya nyaris tidak berubah. | a different model; "bedah serupa" needs slide 2 to decode |
| 06 | Rontgen dulu sebelum mengganti model kecilmu. | Cek pengulangannya dulu sebelum mengganti model. | the reader's action; nobody "rontgen" a model |

The metaphor stays on 02 (rontgen), 03 (sayatan), and 04 (diagnosis), where the subject
is still Astra reading and fixing Qwen.

## Bridge sentences (built)

Read only the first sentence of each interior body:

> Bobot adalah jutaan angka di dalam model AI… Setelah terbukti bisa membaca, Astra
> diberi tugas yang lebih berat… Lompatan sebesar itu berasal dari satu masalah yang
> sudah diperingatkan pembuat Qwen sendiri. Peneliti lalu mencoba cara yang sama pada
> Gemma 3 270M… Jadi, nilai jelek pada model kecil belum tentu berarti modelnya bodoh.

## Headline-only read (built)

> 0,016% bobot model AI diubah AI lain, tanpa dilatih ulang. Anggap saja dokter
> membaca rontgen. Sayatan kecil, nilai matematikanya naik enam kali lipat.
> Diagnosisnya: model ini mengulang kalimat sampai kuotanya habis. Dicoba pada model
> lain, hasilnya nyaris tidak berubah. Cek pengulangannya dulu sebelum mengganti model.
> Ikuti @<handle>.

## Caveats and fairness

- "Klaim penulis, belum diuji pihak lain" sits in the table note and on the opinion
  slide, never on the cover.
- Gemma's failure is the turn, not a footnote.

## Design notes

| Slide | Layout | Note |
|---|---|---|
| 01 | `coverType` dark, size 112, four short lines | underline under "0,016%" moved up after building (`figma-mechanics.md`) |
| 02 | headline + `splitPlate` | generated x-ray on a lightbox, cropped square, credited `Ilustrasi AI` |
| 03 | `table`, 4 rows × 4 values, bar on the first | headers ≤ 8–9 characters at size 17, 0% tracking |
| 04 | bridge body + `steps`, gap 44 | three steps: gejala, sumber, tindakan |
| 05 | `fullBleed` | generated empty operating room; the turn |
| 06 | `checklist` | the action, phrased for someone who runs small models |
| 07 | `closeSlide` light | `Gambar slide 02 dan 05: ilustrasi AI.` without the tool's name |
