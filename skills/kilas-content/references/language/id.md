# Bahasa Indonesia

Rules for copy in Indonesian. The register (formal, santai, campur) comes from the brand
pack; these hold for every register. If the `bahasa-indonesia` companion skill is
installed, it goes deeper.

## Sentences and words

- Write like a colleague explaining something clearly: short, correct, concrete.
- **No calques.** "hal ini dikarenakan oleh" → "ini terjadi karena"; "melakukan
  pengecekan" → "mengecek"; "pada saat ini" → "sekarang"; "dalam rangka untuk" →
  "untuk".
- **No `yang mana` / `di mana`** as a relative connector. Split the sentence.
- **Verbs over nominalisations**: "menandai", not "melakukan penandaan".
- **Hyphenate blends** with foreign words: `commit-nya`, `di-revert`, `patch-mu`.
- **Keep English terms** the audience says in English (for developers: merge window,
  patch, maintainer, deploy; for marketers: funnel, CTR). Translate the sentence around
  them, not the term.
- **Kamu / Anda / kalian**: one choice per brand (brand pack), used only where you speak
  to the reader directly.
- **English words the reader does not say.** Developers say build, deploy, merge; they
  say "aplikasi", not "app", and "percobaan" or "build", not "run". Write `$4,97` or the
  Rupiah amount, not `US$4,97`. `lint_copy.py` warns on US$, run, and app.
- **Rhythm.** Short sentences are good; three short ones in a row read as notes. Join two
  with the relation between them: "Rentang run-nya saling tindih. React Router sempat
  US$2,82. Hono+htmx sempat US$3,19." becomes "Hasilnya acak: build React Router yang
  termurah ($2,82) masih lebih murah dari build Hono+htmx yang termahal ($3,19)."
- **Describe the behaviour, not a label for it.** "macet berputar" made the owner ask
  what it meant; "mengulang kalimat sampai kuotanya habis" did not. Research jargon
  (forward pass, gradient, MLP layer, PPO, benchmark names) goes to `>` notes or a small
  table note; the slide says what happens (`writing-craft.md` 10b).
- **Plain Indonesian over half-translated terms.** "nilai ujian matematika" over "skor
  MATH-500", "dilatih ulang" over "training", "putaran uji" over "forward pass",
  "terpotong" over "hit token limit".


## Numbers

- Thousands with a dot, decimals with a comma: `19.671`, `9,43%`, `Rp5,6 juta`.
- Ranges with an en dash: `12–14 ribu`.
- Rupiah: `Rp27 juta`, `Rp5.600.000`; no space after `Rp` in short form.
- Dates: `1 November 2026`, `Sen 2/11` in tight spaces.

## AI tells and stock lines

Act on one sighting. `scripts/lint_copy.py` catches most of these.

| Tell | Example | Fix |
|---|---|---|
| Contrast reveal | "bukan X, tapi Y"; "Bukan cuma X, ini Y" | state Y with its reason |
| Negation list | "tanpa X, tanpa Y, tanpa Z" | say what does happen |
| Colon reveal | "Hasilnya: 3x lebih cepat." | "Waktunya turun jadi sepertiga." |
| One-line closer | "Itulah kenapa X penting." | cut it |
| Forced triad | three parallel items where two were meant | keep what the meaning needs |
| Dashes as connectors | "— dan itu masalahnya" | a period or a comma |
| Stock openers | "Di era serba digital ini", "Mari kita bahas", "Tanpa basa-basi" | start with the fact |
| Media-carousel openers | "Cek 3 hal ini dulu!", "Yuk, kenali", "Siapa bilang", "Masih bingung", "Jangan buru-buru", "Tahukah kamu" | start with the fact |
| Inflated significance | "menjadi tonggak", "momen penting", "lanskap", "revolusioner" | keep the fact, drop the weight |
| Sales language | "luar biasa", "fantastis", "tak terlupakan" | show it with a number |
| Engagement bait | "Setuju?", "Tag temanmu", "Simpan dulu biar nggak lupa" | a real question with a real choice, or nothing |
| Manufactured vulnerability | "jujur, aku takut banget…" with no story | cut it |
| Exclamation marks | "Daftar sekarang!" | a period; the brand pack may allow one in promos |
