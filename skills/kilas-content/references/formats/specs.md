# Platform specs (checked 2 Nov 2026)

Platforms change these numbers often. Use this table, and when a number matters for a
build (a hashtag count, a video length), re-check it with web search if you have it and
update the row with the new date. "Unofficial" means the platform publishes no figure;
the value comes from dated third-party measurements.

## Instagram

| Spec | Value | Source |
|---|---|---|
| Carousel items | up to 20 in the app; scheduling tools using Meta's API may allow only 10 | help.instagram.com/269314186824048 |
| One ratio per carousel | every item in a post shares one orientation | same |
| Feed photo ratios | 1.91:1 to 3:4; width stored at 1080 px | help.instagram.com/1631821640426723 |
| Sizes | 1080×1440 (3:4, app uploads since May 2025), 1080×1350 (4:5), 1080×1080 | same; The Verge 2025-05-29 |
| Profile grid | 3:4 tiles since Jan 2025. A 4:5 post shows about 1012×1350 in the grid, losing ~34 px each side | unofficial: Inquirer 2025-01-20, Hootsuite 2026-10 |
| Caption | 2,200 characters; about 125 show before "more" (unofficial) | Meta API reference |
| Hashtags | **5 per post or Reel** (from Dec 2025) | @creators 2025-12-18; The Verge |
| Alt text | supported per image, editable after posting | help.instagram.com/503708446705527 |
| Reels length | help center: up to 20 min, but over 3 min is not recommended to new audiences | help.instagram.com/2720958398006062 |
| Reels canvas | 9:16, 1080×1920 standard export | help.instagram.com/1038071743007909 |
| Reels cover in grid | centred 3:4 crop: on 1080×1920 the band y=240–1680 survives (unofficial) | zeroshotstudio 2026-10 |
| Reels safe zone | ads guide: keep 14% top, 35% bottom, 6% sides clear (≈269 / 672 / 65 px). Measured organic UI: 87 top, 486 bottom, 98 left, 202 right | Meta Ads Guide; fooh.com 2026-10 |
| Trial reels | shown to non-followers only; needs a public account (pro ≥200 followers) | help.instagram.com/1013292530224018 |

## TikTok

| Spec | Value | Source |
|---|---|---|
| Video length | 10 min recorded in app, up to 60 min uploaded in app; web 30–60 min (pages conflict) | support.tiktok.com |
| Photo post | up to 35 photos; size unofficial (1080×1920, 4:5 and 1:1 also work) | support.tiktok.com; developers.tiktok.com |
| Caption | photo posts 4,000; video 2,200 or 4,000 (sources conflict) | Creator Academy; API docs |
| Alt text | 300 characters per photo | tiktok.com/support |
| Safe zone | official templates only, no pixel numbers; plan for ~130 px top, ~250+ px bottom, ~60 px sides plus caption growth | ads.tiktok.com (Jun 2026); unofficial blogs |

## X

| Spec | Value | Source |
|---|---|---|
| Post length | 280 (free); up to 25,000 with Premium. Mentions notify only within the first 280 | help.x.com |
| Media | up to 4 items per post | help.x.com/en/using-x/how-to-post |
| Image crop in timeline | no official figure. 16:9 always shows whole; tall singles up to about 3:4–4:5 show uncropped in recent apps (unofficial) | konvrt.dev 2026-04; socialk.it 2026-06 |
| Video | 140 s free; hours with Premium (pages conflict) | help.x.com |
| Links and reach | no official deboost. X's then head of product said in Apr 2026 that links are not deboosted; a bare link with no description gets weak distribution | x.com/nikitabier 2026-04-08 |

## LinkedIn

| Spec | Value | Source |
|---|---|---|
| Post length | 3,000 characters | linkedin.com/help answer a522483 |
| Before "…see more" | about 140 characters on mobile, about 210 on desktop, at most ~3 lines; blank lines count (unofficial) | postformatter.com 2026-07 |
| Document post (PDF carousel) | up to 300 pages, 100 MB; every page the same size, flattened. 1080×1350 or 1080×1080 pages are common | linkedin.com/help answer a564109 |
| Multi-image post | up to 20 images, 3:1 to 4:5; a post has a link or images, not both | linkedin.com/help answer a527230 |
| Hashtags | no official count; hashtag following was removed in late 2024. Use 0–3 | Sprout Social 2026-05 |
| Articles / newsletters | up to 125,000 characters | linkedin.com/help answer a522483 |

## Threads

| Spec | Value | Source |
|---|---|---|
| Post length | 500 characters | developers.facebook.com/documentation/threads/posts (2026-10-30) |
| Carousel | up to 20 photos/videos | @threads 2025-08-19; Threads API |
| Video | up to 5 min | Threads API |
| Links | link preview shows only on posts without media | Later help 2026-01 |
| Long text | text attachment up to 10,000 characters | about.fb.com 2025-09-04 |
| Topic tag | 1 per post | Threads API |

## Defaults this skill uses

| Piece | Size | Why |
|---|---|---|
| Carousel / single image | **1080×1350 (4:5)** | reusable on Instagram, LinkedIn documents, Threads, X, and through scheduling tools; keep cover text 90+ px from the sides for the 3:4 grid crop |
| Instagram-only carousel | 1080×1440 (3:4) optional | fills the grid tile; app upload only |
| Reels / TikTok / Shorts | 1080×1920 | text inside x=100–880, y=270–1430; cover title inside y=240–1680 |
| X single image | 1080×1350 or 1600×900 | 4:5 for a slide, 16:9 for a screenshot or chart |
| LinkedIn document | the carousel's own 1080×1350 frames as a PDF | same pages, no rework |
