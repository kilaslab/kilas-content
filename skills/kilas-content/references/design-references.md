# Design references

Layout patterns seen in 33 Instagram carousels from Indonesian media, education, and
brand accounts (2 Nov 2026), plus creator posts on X. They are patterns to adapt in the
brand's own tokens and type (`design-system.md`), never templates to copy: no other
account's layout, illustration style, assets, or wording goes into a brand's piece.

Engagement figures are the first unlabeled number on the post (likely likes), a snapshot,
and only comparable within one account.

A brand pack may keep screenshots of these accounts in a private `refs/` folder (made
with `scripts/ref_sheets.py`, one sheet per account with an index). When it exists, look
at the sheet before adapting a pattern: the pacing and density are easier to see than to
describe. Never put such screenshots in the core skill or an open-source copy.

## 1. Explainer with a fixed rubric

Seen in: Narasi #JadiPaham. Its two best posts in the sample were explainers of viral
consumer cases: a data breach at a coffee chain (11.4K) and a sweetener lab test (4.6K),
against 875 for its daily digest.

Use for a case that touches the reader directly (their data, their money, their health,
their tools).

```
cover            1 apa yang terjadi   2 fakta / bukti      3 respons pihak     4 imbauan
┌──────────┐    ┌──────────┐         ┌──────────┐         ┌──────────┐        ┌──────────┐
│  photo   │    │ photo    │         │screenshot│         │ quote of │        │ 3 icons +│
│          │    │──────────│         │ (blurred │         │ official │        │ short    │
│HEADLINE  │    │subhead   │         │  names)  │         │ + photo  │        │ actions  │
│with 2    │    │paragraph,│         │ subhead  │         │          │        │ for the  │
│highlights│    │key words │         │ text     │         │          │        │ reader   │
└──────────┘    │highlight │         └──────────┘         └──────────┘        └──────────┘
```

Adopt: the same subheads in the same order every time, so readers know where they are;
key phrases highlighted in the accent; evidence as screenshots; the last slide tells the
reader what to do. Avoid: their density of 80–100 words per slide; keep to the brand's
limit and move detail to the caption.

## 2. Daily or weekly digest

Seen in: Narasi "Kabar Lain" (date label + lead headline + "Dan sejumlah kabar lain").

```
cover                      each item
┌──────────────┐          ┌──────────────┐
│ photo        │          │ photo        │
│ [30 OKT 2026]│          │ HEADLINE with│
│ LEAD STORY   │          │ highlight    │
│ HEADLINE     │          │ 3-line body  │
│ Dan sejumlah │          │ source       │
│ kabar lain.  │          └──────────────┘
└──────────────┘
```

Adopt for a weekly "rangkuman minggu ini": cheap to make once the template exists. Expect
less engagement than explainers; it is a habit format, not a reach format.

## 3. Chart as the cover

Seen in: Tirto #CukupTau, Katadata Databoks. Two slides: the chart, then the brand's own
offer.

```
┌────────────────────────┐
│ #SERIES          logo  │
│ Title as a finding     │
│ ▇▇▇▇▇▇▇▇▇▇▇▇ 51%       │  ← highlighted bar
│ ▇▇▇▇▇▇▇▇ 36,6%         │
│ ▇▇ 9,4%                │
│ ▇ 1%                   │
│ illustration (small)   │
│ Sumber: X, n=1.294     │
└────────────────────────┘
```

Adopt: sorted bars, direct labels, one highlight, source and n on the frame. Avoid:
titles that are topic labels ("Proporsi tugas ..."); make the title the finding.

## 4. Fast news with a local price

Seen in: teknologi_id. "iPhone 18 Pro dan Pro Max Masuk Indonesia, Siap Pre-order 7
Oktober" (559) against 91–177 for its other posts.

```
cover                         slide 2
┌──────────────────┐         ┌──────────────────┐
│ product photo    │         │ Harga di Indonesia│
│                  │         │ • 256 GB  Rp...   │
│ ┌──────────────┐ │         │ • 512 GB  Rp...   │
│ │HEADLINE with │ │         │ • 1 TB    Rp...   │
│ │date + Rp     │ │         │ warna: ...        │
│ └──────────────┘ │         │ sumber, tanggal   │
└──────────────────┘         └──────────────────┘
```

Adopt: the local date and Rupiah price in the headline; a plain list slide. Fast to
make, so it can fill reactive slots.

## 5. Learning path

Seen in: Dicoding. "Kamu pake bahasa pemrograman apa?" over a film-still meme, then what
C++ is, what it is for, start with fundamentals, practise with small projects, read
other people's code, a course CTA (4.5K, its best in the sample).

```
cover (dark, giant keyword)   interior (light)            last
┌──────────────┐             ┌──────────────┐            ┌──────────────┐
│ Apa itu      │             │ Apa itu ███  │ ← keyword  │ question to  │
│ TECH         │             │ short text   │   in a box │ the reader + │
│ DEBT         │             │ ① step  icon │            │ pill CTA     │
│ dan cara...  │             │ ② step  icon │            │              │
└──────────────┘             │ ③ step  icon │            └──────────────┘
                             └──────────────┘
```

Adopt: a dark, high-contrast cover with one giant keyword; light interiors; the keyword
in a filled box (the brand's highlighter); numbered steps with icons; a last slide that
asks the reader something and offers the next step. A meme cover works only if the
brand's voice allows humour and the image is licensed.

## 6. Story of a person

Seen in: Gojek #PastiAdaJalan (2.9K–4.2K, the account's best), Dicoding alumni story
(editorial serif on cream, first person, portrait photos, pull quote).

```
┌──────────────┐
│              │
│ real photo   │
│ of the person│
│              │
│ one sentence │
│ in their own │
│ words        │
└──────────────┘  × 3–4
```

Adopt: real people, real photos, one sentence per frame, the person's own words, a
series tag. Only with the person's consent, and no invented numbers. Plan for comments
that are complaints (`planning.md` section 10).

## 7. Report teaser

Seen in: DailySocial's AI Startups Compendium: a cover card, a thesis quote with one
coloured phrase, two "spotlight" slides each with two stat cards, a QR slide: "40
startups. 7 verticals. One report."

```
spotlight
┌──────────────────────┐
│ [VERTICAL]  [STAGE]  │
│ Company name         │
│ one-line what it does│
│ ┌────────┐┌────────┐ │
│ │ 60–70% │ │ 400+  │ │
│ │ label  │ │ label │ │
│ └────────┘└────────┘ │
└──────────────────────┘
```

Adopt for the brand's own reports, long pieces, or open-source releases: two stats per
spotlight, the full thing one scan away.

## 8. Uniform newsroom template

Seen in: IDN Times: photo on top, a black panel with bold white text below, slide index
`2/7`, watermark, on every post of every sub-brand.

Adopt the idea, not the look: one template per series makes hourly production possible
and makes the account recognisable. Avoid photo-on-top-of-text for data; it leaves
little room for numbers.

## 9. What drew least

- **Event photos with no text** (DailySocial partner posts: 23–62): nobody knows what
  happened or why it matters. Add a headline and one fact per photo, or skip.
- **Sponsored product tours** (Katadata myGarda: 15): the same template did not save it.
- **Motivational quote sets** (Tirto via a sub-brand: 301): fine for a lifestyle
  sub-brand, off-pillar for a news or tech brand.

## 10. From X: raw proof

The creator posts with the most saves showed real artefacts: a dashboard, a product
page, a ranked list of job offers, a hand-drawn diagram ("the future of SaaS in 1
image"). For evidence slides and X posts, a real capture in colour beats a designed
graphic (`image-sourcing.md`).
