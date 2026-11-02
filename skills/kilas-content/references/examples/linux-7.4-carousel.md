# Worked example: Linux 7.4 merge window (8 slides)

The reference carousel for this skill. It shows a finished `copy.md` (the format to
use), why each line is written the way it is, and the drafts that were rejected. Read it
before writing your first carousel; imitate the moves, not the words.

Written for an Indonesian developer-tech account; `<handle>` and `<BRAND>` stand for
the brand's own handle and name. The design was the brand pack's default carousel
preset (light editorial, highlighter behind key words, duotone photo plates).

## Story notes (section 1 of writing-craft.md)

- What changed: 19.671 commit in the Linux 7.4 merge window, the largest on record.
- Compared with what: usually 12–14 ribu; old record 16.267 (Linux 7.3).
- Why: AI-generated bug reports and patches. Networking maintainer: "completely overwhelmed".
- Complication: the anti-bot-noise feature (TAINT_FORCED_BIND) was reverted before rc1.
- Turn: AI review also found real OverlayFS bugs; networking now reviews each patch with several models.
- So what for an Indonesian reader: no Rupiah price or local company here, so the local
  angle is the metaphor (Pintu Air Manggarai) and an action for contributors: reviewer
  time is the scarce resource; check AI-assisted patches yourself.
- Slide worth saving: 07, the tip for contributors.
- Metaphor: merge window = pintu air (opens, lets volume through, closes). Verbs: banjir, membendung.

Sources (all Phoronix, Michael Larabel): Linux-7.4-Massive-Window and
Linux-7.4-Merge-Window (1 Nov 2026), Linux-7.3-Networking (20 Aug 2026),
Linux-7.4-Drops-Taint-Bind (31 Oct 2026), OverlayFS-Many-Fixes (1 Nov 2026).

## copy.md

```markdown
## 01 Cover
eyebrow: LINUX 7.4 · LAPORAN KERNEL
number: 19.671
headline: commit masuk ke kernel Linux dalam dua minggu.
body: Merge window terbesar sepanjang sejarah Linux. Banyak di antaranya dipicu laporan bug dan patch hasil AI.
> 19.671: Massive-Window. "two weeks": Merge-Window. "a lot of the uptick ... due to AI/LLMs": Massive-Window.

## 02 Konteks
eyebrow: KONTEKS
headline: Anggap saja pintu air.
body: Setiap rilis kernel dibuka dengan merge window, dua minggu ketika fitur dan perbaikan baru boleh masuk. Setelah itu pintunya ditutup dan sisa siklus dipakai untuk menstabilkan kode.
stat: 12–14 ribu
statlabel: commit yang biasanya lewat dalam satu merge window
> "13~14k commits or less": Massive-Window. Data 6.0–7.2: quartiles 12.402–13.805.

## 03 Data
eyebrow: DATA · 85 MERGE WINDOW SEJAK 2011
headline: Rekor lama dilewati 3.404 commit.
chart: 85 bars from zero; dashed line at 16.267 (old record); 7.4 bar darkest, labelled.
stat1: +21%
stat1label: dibanding rekor sebelumnya, Linux 7.3
stat2: 455 ribu
stat2label: baris kode baru, di luar komentar dan baris kosong
> 19.671 − 16.267 = 3.404; 19.671 / 16.267 = 1,209. 31.417.938 − 30.962.306 = 455.632 (cloc): Merge-Window.

## 04 Penyebab
eyebrow: PENYEBAB
headline: Patch hasil AI datang tanpa henti.
quote: “We are completely overwhelmed, of course.”
attribution: JAKUB KICINSKI · MAINTAINER JARINGAN LINUX · AGU 2026
body: Di siklus Linux 7.3 ia memperkirakan sepertiga sampai separuh patch net-next tampak seperti perbaikan prioritas rendah buatan AI.
> Quote and "1/3 to 1/2 ... *seem* like AI-driven low priority fixes": Linux-7.3-Networking.

## 05 Ironi
eyebrow: IRONI
headline: Penyaringnya sendiri sudah di-revert.
body: Greg Kroah-Hartman menambahkan TAINT_FORCED_BIND untuk menandai laporan bug dari bot yang memasang driver sembarangan. Ternyata VFIO memakai jalur yang sama untuk passthrough perangkat ke VM.
quote: “vfio is a crazy beast”
attribution: GREG KROAH-HARTMAN · DI PATCH REVERT-NYA, OKT 2026
> Linux-7.4-Drops-Taint-Bind.

## 06 Sisi lain
eyebrow: SISI LAIN
headline: AI juga dipakai untuk membendungnya.
item1label: OVERLAYFS
item1: Review AI dari Chris Mason menghasilkan lebih dari selusin patch. Sebagian bug-nya bisa dipicu user biasa, termasuk info leak dan use-after-free.
item2label: JARINGAN
item2: Setiap patch kini di-review beberapa model frontier sekaligus, dengan anggaran LLM dari Meta.
> OverlayFS-Many-Fixes; "LLM budget ... (thank you Meta!) ... multiple frontier models on each patch": Linux-7.3-Networking.

## 07 Catatan
eyebrow: CATATAN <BRAND>
headline: Waktu reviewer jadi barang langka.
body: Menulis patch makin murah. Membaca, menguji, lalu memutuskan menerima atau menolaknya tetap jadi pekerjaan maintainer manusia.
tiplabel: BUAT KONTRIBUTOR
tip: Kalau patch-mu dibantu AI, baca ulang dan uji sendiri sebelum dikirim.
> Opinion, labelled. Direction of the networking team (LLMs for busy work): Linux-7.3-Networking.

## 08 Ikuti
eyebrow: <BRAND>
headline: Ikuti @<handle>
body: Kabar teknologi seperti ini, lengkap dengan angka dan sumbernya.
cta: IKUTI @<HANDLE>
sources: five Phoronix titles with dates
photos: Foto Unsplash: shiva Mangena, krzhck, Christa Dodoo, Agence Olloweb, Ben Marler
```

## Why each line, and what it replaced

| Slide | Line | Why it works | Rejected draft |
|---|---|---|---|
| 01 | 19.671 / commit masuk ke kernel Linux dalam dua minggu. | Exact number, then a scene with a time window | "Linux 7.4 Pecahkan Rekor!" |
| 01 | Banyak di antaranya dipicu laporan bug dan patch hasil AI. | Names the cause, keeps the source's strength ("a lot of") | "Sebagian besar ditulis AI." (stronger than the source) |
| 02 | Anggap saja pintu air. | Explains jargon with a thing every Jakarta reader knows; sets up later verbs | "Apa itu merge window?" (opens on jargon) |
| 02 | 12–14 ribu | Gives the reader the "normal" before the record, so slide 3 lands | "Biasanya cukup banyak." |
| 03 | Rekor lama dilewati 3.404 commit. | Headline does the subtraction for the reader | "Lima belas tahun, satu lonjakan." (pretty, no fact) |
| 03 | Chart from zero with dashed old-record line | Honest scale; only one bar crosses the line | Bars scaled from the minimum |
| 04 | Patch hasil AI datang tanpa henti. | Continues the flood metaphor as a verb; mirrors "relentless" | "Banjir dari mesin." (fragment, no verb) |
| 04 | “We are completely overwhelmed, of course.” | Short quote kept in English; "of course" carries his tiredness | Full paragraph of the pull request |
| 04 | tampak seperti ... buatan AI | Mirrors "*seem* like" | "adalah buatan AI" |
| 05 | Penyaringnya sendiri sudah di-revert. | The irony is in the fact; no need to call it ironic | "Ironisnya, fitur anti-AI gagal total." (inflated) |
| 05 | bot yang memasang driver sembarangan | Concrete picture of the problem | "aktivitas fuzzing yang tidak relevan" |
| 06 | AI juga dipakai untuk membendungnya. | The turn, in the metaphor's own verb | "Tapi AI tidak selalu buruk." (contrast reveal) |
| 06 | lebih dari selusin patch | Source says patches, not bugs; counted the right thing | "selusin bug" |
| 07 | Waktu reviewer jadi barang langka. | One claim, labelled as opinion by the eyebrow | "Yang sebenarnya penting adalah..." (staged reveal) |
| 07 | Kalau patch-mu dibantu AI, baca ulang dan uji sendiri sebelum dikirim. | An action the reader can take; earns the save | "Mari bijak menggunakan AI." (vague) |
| 08 | Kabar teknologi seperti ini, lengkap dengan angka dan sumbernya. | Promise matches what the carousel just did | "Update teknologi tiap hari!" (unverifiable) |

## Headline-only read

> 19.671 commit dalam dua minggu. Anggap saja pintu air. Rekor lama dilewati 3.404
> commit. Patch hasil AI datang tanpa henti. Penyaringnya sendiri sudah di-revert. AI
> juga dipakai untuk membendungnya. Waktu reviewer jadi barang langka. Ikuti @<handle>.

## Caption (feed text, its own hook)

```
Merge window Linux 7.4 menelan 19.671 commit, 3.404 lebih banyak dari rekor sebelumnya.
Phoronix mengaitkan lonjakan ini dengan banjir laporan bug dan patch hasil AI. Di saat
yang sama, review berbantuan AI menemukan bug OverlayFS yang bisa dipicu user biasa.
Geser untuk lihat datanya.

Sumber: Phoronix (link di slide terakhir).
#linux #kernel #opensource #ai
```
