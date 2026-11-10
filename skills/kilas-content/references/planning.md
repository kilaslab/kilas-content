# Content planning

How to plan a month of content, run production in batches, and learn from the results.
Evidence from the scraped accounts is in `patterns-from-data.md`; this file turns it into
a method. Everything is markdown in the brand's workspace (`templates/workspace.md`), so
any agent can read and update it.

## 1. Inputs, before planning

Read, in this order:

1. The brand pack: pillars and their shares, series, channels, cadence, CTAs.
2. Last month's review (`content/reviews/YYYY-MM.md`), if any: what to keep, fix, stop.
3. The backlog (`content/ideas.md`).
4. Known moments for the month (section 5) and the owner's goals for the month.
5. Capacity: how many pieces the team can really finish per week, per format.

If any of these is missing, plan with what exists and list the gaps at the top of the
plan.

## 2. Pillars

Three to five topics the brand returns to, each with a goal and a share of the calendar.

| Field | Example |
|---|---|
| Pillar | Kabar teknologi dengan data |
| Goal | reach (new followers) / trust (saves, reads) / conversion (sign-ups, sales) |
| Share | 40% |
| What belongs | news explained with numbers and sources |

Shares add up to 100%. A plan that drifts more than 15 points from a share needs a
reason in the plan's notes. `scripts/check_plan.py` checks it.

## 3. Series

A series is a named, recurring format with a fixed template and its own tag. Every
large account in the Instagram sample ran them: Narasi's #JadiPaham explainers and the
daily "Kabar Lain" digest, Katadata's Databoks chart (always posted at a round hour),
Tirto's #CukupTau data card, Gojek's #PastiAdaJalan people stories. A series makes
production faster (the template and the rubric are decided), and the reader recognises
the format before reading.

Define each series in the brand pack:

| Field | Example |
|---|---|
| Name and tag | Satu Angka · #SatuAngka |
| Pillar | data |
| Format | single post (chart) or 2-slide carousel |
| Rubric | finding as headline → chart → source and n → CTA slide |
| Cadence | weekly, Tuesday |
| Scheme and template | a key of the `BRAND` block's `schemes`, plus any fixed cover or data variant |

Start with two or three series. Retire one that underperforms its pillar for two months
running, or that the team dreads making.

## 4. Mix, cadence, and slots

- **Evergreen vs reactive.** Plan most slots in advance and keep about one slot in four
  open for news and moments. In the sample, teknologi_id posted two iPhone carousels in
  two days when the phone reached Indonesia; DailySocial clustered posts around Bali Tech
  Week.
- **Cadence from capacity**, not ambition. A steady, smaller rhythm beats bursts. The
  sample ranged from hourly (Tirto, IDN Times on weekdays) to one carousel every one or
  two weeks (Gojek), and both worked for their size.
- **Posting time.** In the X sample, posts did no better or worse by hour (lift was flat
  across every three-hour block). Indonesian media mostly post 07–10, 13, and 16–18 WIB.
  Pick fixed slots the team can keep, then move them only when the brand's own analytics
  after 4–6 weeks show a difference.
- **One piece, several formats.** A strong item usually becomes 3–5 pieces (section 6).
  Count them as separate rows in the calendar.
- **Reels rotate kinds like the feed does** (`formats/reels-tiktok.md` section 0): news,
  explainer, story, demo. The product is the subject of at most every other Reel; in the
  rest it appears as a supporting role or in the last beat. A product brand's owner asked
  for this after a run of product Reels (Nov 2026): viewers tire of a channel that only
  sells.

## 4b. Product brands: show the product working

Lessons from a product brand's first month (2026-11): the owner rejected tips
any seller already knows and approved pieces that show the product doing one real thing.

- Give up to half the slots to the product at work, one capability per piece, so no two
  demos repeat (answer from the catalog, upload a file, CRM, settings, follow-up, channels).
  Fill the rest with what the audience follows the account for (news in the field,
  explainers, stories), each ending where the product fits naturally, if it does.
- A tip earns a slot only when it ends in the product ("put your shipping cutoff in the
  bot's data") or teaches something the reader cannot already do.
- Give the month one storyline (meet the product → the product during the big moment →
  how to start) instead of independent pieces.
- Demo carousels follow the "Demo Walkthrough" ladder: outcome on the cover, the problem,
  the steps listed before the detail, one real screenshot per step cropped to the action,
  the result. Mock-ups read as vaporware next to the real UI.

## 5. Moments

Keep a moments list per year in the brand pack, and check the coming month's when
planning. Kinds of moments:

- the industry's own: product launches, release cycles, conferences, earnings, reports;
- commerce: Harbolnas 11.11 and 12.12, payday at month end, Ramadan and Lebaran (dates
  move every year), year-end reviews;
- national and cultural days that fit the brand; skip the rest.

Verify each date for the current year before it goes in the plan. A moment earns a
slot only if the brand has something specific to say about it.

## 6. Repurposing map

Plan the cuts of a strong item together, and stagger them so each platform gets the
piece on a different day:

| Day | Piece | From |
|---|---|---|
| 0 | long form (blog, notes, newsletter) or the research doc | the item itself |
| 0–1 | carousel (Instagram, Threads, TikTok photo) | the ladder |
| 1 | X thread or long post | headings as posts |
| 1–2 | LinkedIn document or text post | the carousel as PDF, or the argument in prose |
| 2–4 | Reels/TikTok script | the result + one example |
| 3–5 | single post (chart or quote) | the strongest number |

In the sample, Narasi and Katadata turned articles into carousels, Katadata turned
surveys into single charts, and DailySocial turned a report into a teaser carousel with
a QR code. Every cut must say something whole on its own and link back.

## 7. Batch production

Produce in a weekly session, the way IDN Times queues its X posts every Monday at 09:00.
Each item moves through statuses, written in the plan's `Status` column:

| Status | Done when |
|---|---|
| `ide` | a row exists with pillar, format, and working title |
| `riset` | sources found; the five story questions answered in `brief.md` |
| `draf` | `copy.md` written and lint passes |
| `desain` | frames, storyboard, or images built |
| `review` | checked against the format checklist; waiting for the owner |
| `terjadwal` | `publish.md` complete with time and final text |
| `terbit` | posted (by the owner, or by you only when explicitly asked) |
| `batal` | dropped, with a one-line reason |

English equivalents (`idea`, `research`, `draft`, `design`, `review`, `scheduled`,
`published`, `dropped`) are accepted.

## 8. Collaborations and sponsored posts

- **Collab posts** reach two audiences with one upload; most large accounts in the
  sample used them (14 of 33 carousels), often with their own sub-brands.
- **Sponsored posts** are labelled from the first frame and in the caption, in the same
  template as organic posts. In the sample, Katadata's sponsored carousel drew 15 likes
  against 48–92 for its own data posts. Keep them to a share the brand pack sets
  (for example ≤ 1 in 5).
- A sponsor never takes over the close slide; the brand's own CTA does.

## 9. The calendar file

`content/plan/YYYY-MM.md`, from `templates/plan-month.md`: goals, slots, and one table
row per piece:

```markdown
| Tanggal | Jam | Pilar | Seri | Format | Kanal | Judul kerja | Sumber | Status |
|---|---|---|---|---|---|---|---|---|
| 2026-11-03 | 09:00 | Kabar teknologi | Rilis Mingguan | carousel | IG, Threads, LinkedIn | Merge window Linux 7.4 pecah rekor | phoronix.com/... | draf |
| 2026-11-05 | 16:00 | Data | Satu Angka | single | IG, X | ... | reaktif | ide |
```

`Sumber` is a URL, a file, `evergreen`, or `reaktif` (an open slot). Check it with:

```bash
python3 scripts/check_plan.py content/plan/2026-11.md --brand <brand pack>/brand.md
```

It checks dates, pillars and series against the brand pack, pillar shares, statuses,
pieces per day, and rows with no source. Create the item folder for a row with
`python3 scripts/new_item.py content <date> <slug> <format>`.

## 10. Community

Comments are part of the content. In the sample, Gojek's people stories drew thousands
of likes and a stream of service complaints in the comments. Plan:

- who answers comments, and within how many hours of posting;
- where complaints and questions go (support channel, DM template);
- which comments become new ideas in `ideas.md`.

## 11. Review loop

Weekly (15 minutes) and monthly (`templates/review-month.md`):

1. Pull each piece's numbers from the platform: reach, saves, shares, comments, follows
   from the piece. Date the snapshot.
2. Compare each piece with the brand's own median for that format, not with other
   accounts. A piece at 2× the median is a lift of 2.
3. Group by pillar and series: which earn their share, which do not.
4. Decide per series: keep, fix (one change, named), or stop. Carry the decisions into
   next month's plan inputs.
5. Note which hooks, topics, and formats won, with the post links, in the review.

Never invent numbers. If the owner has not shared analytics, the review lists what to
collect and stops there.
