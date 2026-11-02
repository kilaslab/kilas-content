# X: single post, thread, long post

X rewards a post that stands on its own. In the X sample (`patterns-from-data.md`),
substantive posts and raw proof (screenshots, dashboards, a diagram) beat designed
graphics, and the most-saved posts were reference material.

## 1. Single post (≤ 280 characters)

- First line is the hook: the number or the named thing, then the scene. Same workshop
  as a cover.
- One image that proves it: the artefact screenshot (16:9 or 4:5), the chart, or the
  carousel's data slide. Up to 4 images; one is usually stronger.
- The link, if any, goes after the claim, with a sentence saying what it is. There is no
  official link penalty, but a bare link with no description gets weak distribution.
- Mentions only notify inside the first 280 characters.

```
Merge window Linux 7.4 menelan 19.671 commit dalam dua minggu, 3.404 lebih banyak dari
rekor sebelumnya. Grafik 85 merge window sejak 2011:
[image: data slide]
```

## 2. Thread (5–8 posts)

Use when the story has a ladder. Each post is one rung and must make sense quoted alone.

1. **Post 1**: the hook, with the strongest image. It carries the whole claim; many
   readers stop here.
2. **Posts 2–6**: one rung each (konteks, bukti, penyebab, komplikasi, sisi lain),
   each with its own image when it has proof.
3. **Last post**: what it means + the source links + the CTA from the brand pack.

Number the posts only if the brand does (`1/7`). No "🧵👇", no "A thread:". In
`copy.md`, write one `## ` section per post; the lint checks each against 280.

## 3. Long post (Premium, up to 25,000)

The creator posts that beat their accounts' usual numbers were often long posts: a
specific setup, what happened, pros, cons, and a verdict. Write it as a short article
with plain paragraphs, the hook as the first line (the timeline shows only the start),
and the image at the top. If the account has no Premium, make it a thread.

## 4. Repurposing a carousel

The cover becomes post 1's line and image; each interior slide's headline becomes a
post's first sentence; the body is rewritten as one or two sentences, not pasted.

## 5. Checklist

- [ ] Post 1 stands alone, with an image.
- [ ] Every post ≤ 280 (unless Premium long post), one idea each.
- [ ] Sources linked in the last post; numbers match `copy.md`.
- [ ] `lint_copy.py --format x` passes.
