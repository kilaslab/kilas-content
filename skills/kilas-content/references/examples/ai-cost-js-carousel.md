# Worked example: the AI cost of JavaScript frameworks (8 slides)

The second reference carousel. The Linux example is a news record; this one is someone
else's experiment: a benchmark with 12 contenders, five metrics, and honest limits. It
shows the hook workshop with gates and duels, headlines that carry a metaphor, a caveat
budget, a consolidated data table, screenshots with marks, and an action that passes
the test.

A second draft of the same story was written from the same research with the same
skill. Its facts were right and its lint passed; its choices were weaker. Its lines
appear below as the rejected drafts, so you can see exactly where the difference is.

`<handle>` and `<BRAND>` stand for the brand's handle and name. Built in the brand
pack's default preset with the layout functions in `scripts/figma-helpers.js`.

## Story notes

- What changed: Nolan Lawson had Opus 5.5 build the same Pokédex app with 12 JavaScript
  frameworks, five times each. Median API cost per build: $2,67 (Hono+htmx) to $4,97
  (Angular).
- Compared with what: quality was nearly equal. Lighthouse Performance 97–100 and
  Accessibility 100 for every framework, so the difference is cost, time, tokens, code,
  and JavaScript shipped.
- Why: SvelteKit 3 was likely too new for the model's training data, so the agent read
  the migration guide in every build; agents did not know Gracile and cloned its repo;
  Angular's cost seems to follow its code size.
- Complication: the official MCP servers and skills did not predict cost. SvelteKit's
  agent used its MCP in 5 of 5 builds and was still third most expensive; Nuxt's MCP
  was never used, and Nuxt used the fewest tokens.
- Turn: the build is paid once; the code size keeps costing tokens in every later edit,
  and the JavaScript is sent to every visitor.
- So what for an Indonesian reader: no official Rupiah price exists, so the dollar
  figures are converted with the JISDOR rate and its date in a `>` note (about Rp48
  ribu vs Rp90 ribu per build). The action: test candidates before migrating "for the
  agent"; the harness is open to fork.
- Slide worth saving: 03, a table of 12 frameworks × 5 metrics.
- Metaphor: argo taksi. Shape: same destination, a meter that runs along the route and
  keeps running after you arrive. Verbs: argo, jalan baru, membuka peta, navigasi, argo
  jalan lagi.

Sources: Nolan Lawson, "The AI cost of JavaScript frameworks" (28 Okt 2026); the
benchmark's README; `report.md` in the results repo (every number was checked against
it); JISDOR, Bank Indonesia (30 Okt 2026).

## Hook workshop

| # | Hook | Shape | Gates |
|---|---|---|---|
| A | 60 / kali agent AI membangun aplikasi yang sama dengan 12 framework JavaScript. Biaya per build berkisar $2,67 sampai $4,97, padahal skor Lighthouse-nya nyaris sama. | experiment + paradox | pass (24 words) |
| B | US$4,97 / median biaya API untuk satu app Pokémon di Angular. Hono+htmx selesai di US$2,67. Ini harga yang dikutip Claude Code, bukan uang yang dibayar. | number | fails Plain (median, API), Clean (a caveat on the cover), Open (names the cheapest) |
| C | Biaya beda 86%, skor nyaris sama. / 12 framework JavaScript, satu aplikasi, dibangun agent AI. | paradox | pass |
| D | Framework pilihanmu bisa membuat tagihan agent AI hampir dua kali lipat. | stakes | fails Honest: the source quotes API list prices, not bills |
| E | 142 KiB vs 0 KiB / JavaScript yang dikirim dua framework untuk aplikasi yang sama. | concrete comparison | pass |

Duels among the survivors:

- **A beats C.** C has the paradox and no scene; nobody pictures "biaya beda 86%". "60
  kali agent AI membangun aplikasi yang sama" is something you can see.
- **A beats E.** E spends slide 6's surprise on the cover and is not the source's main
  claim.
- **C beats E.** E asks the reader to know what a KiB of JavaScript costs them.

Winner: A, two wins. The rejected draft scored B, C, D, and E at the maximum on the
old 0–2 rubric and chose B for being shortest.

## copy.md

```markdown
## 01 Cover
eyebrow: BENCHMARK · NOLAN LAWSON · OKT 2026
number: 60
headline: kali agent AI membangun aplikasi yang sama dengan 12 framework JavaScript.
body: Biaya per build berkisar $2,67 sampai $4,97, padahal skor Lighthouse-nya nyaris sama.
> 12 frameworks × 5 iterations = 60. $2,67 / $4,97 and Lighthouse 97–100: report.md.

## 02 Konteks
eyebrow: KONTEKS
headline: Anggap saja argo taksi.
body: Nolan Lawson memberi Opus 5.5 tujuan yang sama: aplikasi Pokédex berdata PokéAPI, plus test yang wajib lulus. Hanya framework-nya yang diganti. Argonya mencatat dolar, menit, token, dan baris kode.
stat: 97–100
statlabel: skor Performance Lighthouse di 12 framework. Accessibility: 100 semua.

## 03 Data
eyebrow: DATA · MEDIAN 5 BUILD PER FRAMEWORK
headline: Argo Angular 86% lebih mahal dari Hono+htmx.
sub: Hono+htmx $2,67 (sekitar Rp48 ribu) per build. Angular $4,97 (sekitar Rp90 ribu).
chart: table(), 12 rows sorted by cost: rank, framework, cost bar + value, menit, token, baris, JS; highlighter on the best value per column.
note: Biaya = harga API menurut Claude Code, bukan tagihan sebenarnya. Token dalam juta, JS dalam KiB. Stabilo kuning = terbaik di kolomnya. Baris kode dan JS Angular dari 3 aplikasi.
> 4,97 / 2,67 = 1,861. 2,67 × 18.138 = 48.428; 4,97 × 18.138 = 90.146 (JISDOR, 30 Okt 2026).

## 04 Penyebab
eyebrow: PENYEBAB
headline: Jalan baru membuat agent membuka peta.
item1label: SVELTEKIT · $4,28
item1: Kemungkinan terlalu baru untuk data latih Opus 5.5. Agent membaca panduan migrasinya di setiap build.
item2label: GRACILE+LIT · $4,65
item2: Agent kurang mengenalnya, lalu meng-clone repo atau membaca source di node_modules.
item3label: ANGULAR · $4,97
item3: Tampaknya karena kodenya paling besar: 2.009 baris.
> Hedges copied: "likely because it's too new", "it seems to be a function of the total code size".

## 05 Komplikasi
eyebrow: KOMPLIKASI
headline: Navigasi resmi tidak menjamin argo murah.
body: SvelteKit memakai MCP-nya di 5 dari 5 build dan tetap termahal ketiga. MCP Nuxt tidak pernah dipakai, padahal Nuxt paling hemat token.
label: TANGKAPAN LAYAR · ALAT RESMI · DIPAKAI AGENT?
quote: “the current crop of MCPs and skills may be doing more harm than good”
attribution: NOLAN LAWSON · DUGAANNYA DI PENUTUP TULISAN
> The source's "AI tool usage" table, inside a <details> element; marks on the Nuxt and SvelteKit rows.

## 06 Sisi lain
eyebrow: SISI LAIN
headline: Argo jalan lagi di setiap revisi.
body: Biaya build dibayar sekali. Ukuran kode ikut menentukan token di setiap revisi berikutnya, dan JavaScript-nya dikirim ke setiap pengunjung.
card1: BARIS KODE · 1.370 · Hono+htmx · vs 2.009 baris di Angular
card2: JAVASCRIPT KE HP · 0 KiB · Astro · vs 142 KiB di Next.js
note: Uji Lighthouse: mode HP, CPU diperlambat 4×, jaringan Slow 4G.
> "the code size ultimately impacts the number of tokens, including in future edits".

## 07 Catatan
eyebrow: CATATAN <BRAND>
headline: Sebelum pindah framework, minta angkanya.
body: Ini satu aplikasi kecil yang mirip Wikipedia. Biaya Angular saja berkisar $3,19 sampai $6,82 antar-build.
tiplabel: BUAT TIM YANG MAU MIGRASI DEMI AGENT
tip: Uji kandidatnya dengan tugas yang sama, minimal 3 build per framework, lalu bandingkan angkanya.
credit: Tangkapan layar: github.com/nolanlawson/agent-framework-benchmark, with a mark on "please open an issue or create a fork."
> README: "One iteration is an anecdote ... use 3 or more iterations".

## 08 Ikuti
eyebrow: <BRAND>
headline: Ikuti @<handle>
body: Kabar teknologi seperti ini, lengkap dengan angka dan sumbernya.
cta: IKUTI @<HANDLE>
sources: the article, both GitHub repos, the JISDOR rate with its date
credit: Ilustrasi sampul: AI (Antigravity) · Foto Unsplash: four photographers · Tangkapan layar: nolanlawson.com, github.com
```

## Why each line, and what it replaced

| Slide | Line | Why it works | Rejected draft |
|---|---|---|---|
| 01 | 60 / kali agent AI membangun aplikasi yang sama… | A scene (one app, built 60 times) plus a paradox (cost differs, quality does not); the winner is held back for slide 3 | "US$4,97 / median biaya API untuk satu app Pokémon di Angular." Jargon, the answer on the cover, and a disclaimer under it |
| 02 | Anggap saja argo taksi. | Explains "cost per build" with a meter every reader has watched | "Rutenya sama… Sopirnya yang ganti" (good metaphor, then never used in a headline again until slide 7) |
| 02 | 97–100 | Sets the "normal" (quality is equal) before the cost gap, so slide 3 lands | "12 · framework, app yang sama" (a count, no comparison) |
| 03 | Argo Angular 86% lebih mahal dari Hono+htmx. | Names both ends, does the division, keeps the metaphor | "Selisih ujungnya US$2,30." ("ujung" is vague; a dollar gap with no base) |
| 03 | a table of 12 × 5 metrics, best value highlighted | The slide worth saving: every number in one place, in the brand's design | A screenshot of the source's cost chart: one metric, the source's colours, small labels |
| 03 | the caveat in the table note | One caveat on the data slide, in small type | "Rentang run-nya saling tindih. React Router sempat US$2,82. Hono+htmx sempat US$3,19." above the chart, three short sentences in a row |
| 04 | Jalan baru membuat agent membuka peta. | The cause, in the metaphor's verbs; "kemungkinan" kept from the source | "Panduan v3 dibaca di setiap run." (an event, passive, no consequence) |
| 05 | Navigasi resmi tidak menjamin argo murah. | The complication as a claim; the screenshot proves it with two marked rows | "MCP Nuxt tidak pernah dibuka." (true, and nothing at stake) |
| 06 | Argo jalan lagi di setiap revisi. | The turn is about the reader's own ongoing cost | "Mahal dibangun, belum tentu berat." (a real finding, about the frameworks, not the reader) |
| 07 | Uji kandidatnya dengan tugas yang sama, minimal 3 build… | Passes who, with what, when; the README screenshot shows forking is welcome | "Pastikan dokumen versi itu ada di data latih." (no reader can inspect training data) |
| all | $2,67, build, aplikasi | Words the Indonesian reader uses | US$, run, app |

## Headline-only read

> 60 kali agent AI membangun aplikasi yang sama dengan 12 framework JavaScript. Anggap
> saja argo taksi. Argo Angular 86% lebih mahal dari Hono+htmx. Jalan baru membuat
> agent membuka peta. Navigasi resmi tidak menjamin argo murah. Argo jalan lagi di
> setiap revisi. Sebelum pindah framework, minta angkanya. Ikuti @<handle>.

The rejected draft's read, for contrast:

> US$4,97 median biaya API untuk satu app Pokémon di Angular. Anggap saja argo taksi.
> Selisih ujungnya US$2,30. Panduan v3 dibaca di setiap run. MCP Nuxt tidak pernah
> dibuka. Mahal dibangun, belum tentu berat. Cek petanya sebelum argo jalan. Ikuti
> @<handle>.

Every sentence in it is accurate. It reads as a list of findings: the metaphor
disappears for four slides, and no headline says who pays or what follows.

## Design notes

| Slide | Layout (helper) | Note |
|---|---|---|
| 01 | `coverDark()` | Generated illustration of a Jakarta taxi interior at night, credited as an illustration, duotone; the gold number is the thumbnail |
| 02 | `plate()` + stat row | Taxi-meter photo, duotone |
| 03 | `table()` | Bars for the main metric, right-aligned values, highlighter on each column's best, the caveat as the note |
| 04 | `plate()` + three labelled items | Navigation-screen photo, cropped so the map shows |
| 05 | `artefact()` + `quote()` | The source's own table, cropped to six rows; MULTIPLY marks on two rows found with `scripts/artefact_marks.py` |
| 06 | `plate()` + `statCards()` | Two numbers the reader compares at a glance |
| 07 | `artefact()` + `tipCard()` | The README with one marked phrase proves the action is welcome |
| 08 | `closeSlide()` | Dark bookend with the logo, one CTA, sources, and credits |

Every interior slide fills the frame to about y=1100. The rejected draft's slides ended
around two thirds of the height with body text near 26 px, which reads as unfinished on
a phone.

## Caption

```
Nolan Lawson menyuruh Opus 5.5 membangun aplikasi Pokédex yang sama dengan 12 framework
JavaScript, masing-masing 5 kali. Biaya median per build berkisar $2,67 (Hono+htmx)
sampai $4,97 (Angular), sementara skor Lighthouse-nya hampir sama semua.

Agent SvelteKit membaca panduan migrasi di setiap build karena versinya kemungkinan
terlalu baru untuk data latih model. MCP resmi Nuxt tidak pernah dipakai agent, padahal
Nuxt yang paling hemat token. Geser untuk tabel lengkapnya.

Ini satu aplikasi kecil, jadi pemenangnya bisa berubah di aplikasi lain. Framework apa
yang dipakai timmu bersama agent sekarang, dan pernah diukur?

Sumber: Nolan Lawson, nolanlawson.com, 28 Okt 2026.
#<SeriesTag> #javascript #webdev #ai
```
