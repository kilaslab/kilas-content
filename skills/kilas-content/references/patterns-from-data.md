# Patterns from data: X and Instagram, 2 Nov 2026

What the skill adopted from two scrapes of public posts, what it rejected, and how sure
each finding is. The rules themselves live in `writing-craft.md`, `copy-playbook.md`,
`planning.md`, `design-references.md`, and `image-sourcing.md`; this file says why.

Part 1 is 533 X posts from 42 tech accounts. Part 2 is 33 Instagram carousels (152
slides) from 8 Indonesian accounts, scraped later the same day.

# Part 1: X

## The dataset and how it was read

- `tech-carousel-dataset-lite-2026-11-02`: 533 public X posts with images from 42 tech
  accounts (32 international, 10 Indonesian), up to ~100 recent posts per account.
  52 multi-image posts, 53 long posts. No Instagram or Threads data (both need a login).
- Raw likes mostly measure account size, so every post was compared with its own
  account: **lift** = (likes + 2×reposts + 2×bookmarks + replies + 1) / (the account's
  median of the same + 1). Only accounts with 5 or more posts: 295 international posts,
  207 Indonesian.
- **Save-worthy** = bookmarks at least half the likes, with 50 or more bookmarks. Saves
  are the closest thing on X to a carousel being kept.
- The dataset's own `hook_type` labels are heuristic and often wrong (a headline with no
  number was labelled "angka"); they were not used.

## What the numbers say

| Finding | Evidence | Confidence |
|---|---|---|
| Substantive long posts beat short link posts | Indonesian long posts: median lift 2.37, 12 of 24 at 3× or more. International: median 1.16, 8 of 22 at 3× or more | medium: the Indonesian ones are mostly kumparan news, so topic is mixed in |
| More images do not help by themselves | multi-image median lift 1.00 in both regions | medium |
| A number in the first line helps a little, at most | international 1.08 vs 0.99; Indonesian 1.00 vs 1.00 | low |
| Posting hour does not matter here | Indonesian median lift 1.00 in every 3-hour block | medium |
| What gets saved is reference material | ranked list (bookmarks/likes 1.55), "in 1 image" framework (1.37), tips (1.46; 82,261 bookmarks), copy-paste instructions (1.62), a tool you switch to (0.96) | medium |
| Indonesian media carousels are 4:5 | detikinet, Tirto, SINDOnews cross-posts are 576x720 | high |
| Those carousels barely register on X | 0–1 likes each | says nothing about Instagram, where they were made |

## Adopted

Each line names the post it came from, the lift, and where the rule now lives.

1. **Six more hook shapes** (`writing-craft.md` section 3b):
   - experiment with a constraint: "I gave my Dot a $500 budget and 24 hours to plan an
     entire afternoon" (@alliekmiller, 15.7×); "MIT researchers left 13 AI agents on
     their own virtual islands with nothing to do, and they started playing" (36.8×);
   - switch: "I stopped using CCleaner after finding a free open-source cleaner that
     finds more junk" (@xdadevelopers, 12.8×, saved almost as often as liked);
   - product + price, two short facts: "Apple Homeview is official. $299" (@MKBHD);
   - compression promise: "This is the future of SaaS in 1 image" (@gregisenberg, saved
     1.37× as often as liked);
   - ranked list with a threshold: "22 remote roles paying $300K+" (@lennysan, saved
     1.55× as often as liked);
   - absurd concrete comparison: "can't believe this is what $4000 gets you at the
     grocery store now", a GPU in a grocery bag (@LinusTech, 10.8×).
2. **Two more ladders** (`writing-craft.md` section 2): *uji coba* from @alliekmiller's
   thread (setup, results, pros, cons, learnings, honest verdict) and *daftar referensi*
   from @lennysan (count and threshold on the cover, ranked rows with a value column,
   paginated "1/2", "2/2").
3. **One save-worthy slide per carousel** (`writing-craft.md` section 2): a checklist,
   table, ranked list, or diagram a reader would screenshot. That is what got saved.
4. **Real artefacts on evidence slides** (`image-sourcing.md`): the creators with the
   most saves showed raw screenshots, dashboards, and a hand-drawn diagram, not designed
   templates.
5. **Bring it home** (`writing-craft.md` section 1): kumparan's MacBook post led with
   the Indonesian price rise and its date ("naik di Indonesia per 1 Juli 2026"). Give a
   global story its Indonesian price, date, availability, company, or user.
6. **Caption as a standalone long post** (`copy-playbook.md` section 6): the one clear
   signal above. Hashtags stay few (Instagram has allowed only 5 since Dec 2025); only
   5% of international and 13% of Indonesian posts used any.
7. **A visual thread across slides** (`image-sourcing.md`): Tirto keeps one illustrated
   character through every slide. A brand can do the same with one metaphor family in the
   photos, or one recurring subject in a generated series.

### Adopted with conditions

- **Scenario mock.** The top post in the set (@levelsio, 46.7×) is a fake ChatGPT
  screen: "ChatGPT in Germany in 2027", charging a tax per answer. A news brand can use
  this only on an opinion carousel, with the eyebrow `SKENARIO` and the credit
  `Ilustrasi`, and never with a real company's logo or a real person in it.
- **First person.** The experiment hooks are first person. The brand writes "kami" only
  when it ran the test; otherwise name who did ("Peneliti MIT ...").

## Rejected

- **Posting-time rules.** The `analysis.md` in the dataset lists Indonesian posting hours
  (09–10, 13, 16–17 WIB). Those are when media accounts post, not when posts do better;
  lift is flat across hours.
- **Indonesian media stock openers**: "Mau X? Cek 3 Hal Ini Dulu!", "Yuk, kenali ...",
  "Siapa bilang ...", "Masih bingung ...", "Jangan buru-buru beli!", "Bukan Cuma X, Ini
  Rahasia Y". They are the default of every Indonesian media carousel, so they make
  a brand look like the rest. `lint_copy.py` warns on them; "bukan cuma X, ini Y" fails
  as a contrast reveal.
- **Paragraphs in small type** on 4:5 slides (detikinet interior slides). The skill's
  body floor stays at 30 px.
- **A sponsor's ad or an unrelated house ad as the last slide** (SINDOnews, detikinet).
  The close is the brand's own single CTA and the sources. (Part 2 refines this: a
  brand's own offer as the CTA slide is fine.)
- **The product section** of `analysis.md`; it is about another product.

# Part 2: Instagram

## The dataset

- 33 recent carousels, 152 slides, from tirtoid, katadatacoid, narasinewsroom,
  teknologi_id, dailysocial.id, idntimes, gojekindonesia, and dicoding, read with a
  logged-in session (read-only). Four or five carousels per account; Reels and single
  posts were not collected.
- Engagement is a raw, unlabeled snapshot (the first number is probably likes). Only
  compare posts within one account. Long captions were summarised, not copied.
- Four dicoding posts have no date or caption, and half the dailysocial.id and idntimes
  entries were collab posts uploaded by another account.

## What the numbers say (within each account)

| Account | Best in the sample | Rest |
|---|---|---|
| narasinewsroom | explainer of a coffee chain's data breach, 11.4K; sweetener lab test, 4.6K | sanitary-pad tax explainer 1.7K; daily digest 875 |
| gojekindonesia | people stories and a fashion collab, 2.9K–4.2K | |
| dicoding | "Kamu pake bahasa pemrograman apa?" + C++ learning path, 4.5K | bootcamp promo 204 |
| teknologi_id | iPhone arrives in Indonesia with a pre-order date, 559 | price list 177; sponsored AI tool 115; Indosat AI explainer 91 |
| tirtoid | IKN tree-planting news, 987 | motivational set (sub-brand) 301; crab evolution explainer 149 |
| idntimes | K-pop story (sub-brand), 431 | travel and food tips 57–151 |
| katadatacoid | survey chart, 92 | sponsored app tour 15 |
| dailysocial.id | report teaser, 62 | event photos with no text 23–43 |

Readings, all low to medium confidence on a sample this small:

- **A case that touches the reader** (their data, their health, their money) beat
  everything else at the account that explains news.
- **Real people** beat product at the brand account.
- **A learning path that opens with a question to the reader** beat the promo at the
  education account.
- **The local date and Rupiah price** in the headline beat the same account's
  explainers.
- **Sponsored posts drew the least** at Katadata, in the same template as organic ones.
- **Event photos without text** drew the least at DailySocial.

## How the big accounts run their content

- **Series with fixed templates and tags**: Narasi #JadiPaham and "Kabar Lain" (daily
  digest), Katadata Databoks (posted at round hours), Tirto #CukupTau, Gojek
  #PastiAdaJalan, IDN Times channel tags (#IDNTimesTravel).
- **Rhythm**: Tirto and IDN Times posted about once an hour on a weekday morning;
  Katadata about twice a day; Gojek one carousel every one or two weeks.
- **Sub-brands and collabs**: 14 of 33 carousels were collab posts (databoks.id,
  tirtofy, diajengtirto, idntimes.hype/korea, partners).
- **Repurposing**: articles into carousels (Narasi, Katadata), surveys into one chart
  (Tirto, Katadata), a report into a teaser with a QR code (DailySocial).
- **Moments**: two iPhone carousels in two days (teknologi_id); posts clustered around
  Bali Tech Week (DailySocial).
- **Own offer on the last slide**: Tirto "Traktir Kopi", Katadata's Databoks
  subscription (one slide reused across posts), Dicoding's bootcamp.
- **Caption questions with a real choice**: "ikut pre-order atau mikir-mikir?",
  "wajar atau mengkhawatirkan?".
- **Hashtags**: 1–9 per post; series tags repeat on every post of the series.

## Adopted from Part 2

| Pattern | Where it lives now |
|---|---|
| Series with a template, rubric, tag, cadence | `planning.md` section 3; brand pack "Series" |
| Explainer rubric, digest, chart cover, fast news, learning path, people story, report teaser | `copy-playbook.md` section 1; `design-references.md` |
| About a quarter of slots reactive; ride moments | `planning.md` sections 4–5 |
| Repurposing map and weekly batches | `planning.md` sections 6–7 |
| Own offer as the reusable CTA slide | `formats/carousel.md` section 4 |
| Sponsored posts labelled and capped | `planning.md` section 8 |
| One real-choice question in the caption | `copy-playbook.md` section 6 |
| Comments as part of the content | `planning.md` section 10 |
| Slide counts by kind (2 for fast news, 5–9 for explainers) | `formats/carousel.md` section 1 |

## Rejected or adapted from Part 2

- **Posting-time rules** again: the sample shows when accounts post, not what works.
- **Narasi's 80–100 words per slide**: it works for a news brand with a reading
  audience; the skill keeps its 45-word warning and moves detail to the caption.
- **Hourly cadence**: a newsroom's capacity; cadence comes from the brand's own.
- **The dataset's own recommendations** for another product: not used.

## Refreshing this file

Re-run the same reading on a new scrape: lift within account, save ratio, then look at
the top posts by lift and the save-worthy list before trusting any feature average. The
Instagram sample is small (4–5 carousels per account); a larger one, with Reels and
single posts, and the brand's own insights after a few months, should replace these
readings as they come in.
