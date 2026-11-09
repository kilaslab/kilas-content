# Threads

Threads reads like conversation: shorter, more direct, more opinion than a carousel
caption. A post is up to 500 characters, with one topic tag.

## Kinds

| Kind | What | Use when |
|---|---|---|
| **Short take** | one sentence of claim + one of evidence + a question that offers a real choice | the brand has a view on today's news |
| **Carousel post** | the carousel frames (up to 20) + a ≤500-character text | repurposing a carousel |
| **Chain** | 3–6 replies under the first post, one idea each | the story has a ladder, like an X thread |
| **Long text** | a text attachment (up to 10,000 characters) | a longer explanation that should stay on Threads |

## Rules

- First sentence = the hook, written for Threads, not pasted from the caption.
- One topic tag that matches the series or the topic.
- A link preview shows only on posts without media; with images, put the link in a
  reply.
- Replies are part of the content: plan who answers comments and how fast
  (`planning.md` section 10).

## Checklist

- [ ] ≤ 500 characters per post; `lint_copy.py --format threads` passes.
- [ ] One topic tag.
- [ ] Source in the post or the first reply.

## What drew replies (Indonesian Threads, 2026-11-09)

From 45 posts read for a seller brand: the posts with the most replies asked the community a
question ("Modal 100 juta usaha apa yg cocok ya.. Bolehkah teman2 berbagi") or told a short
first-person story with a number; a founder's complaint ("capek balesin satu satu") drew the
most relevant replies. Lower case, short lines, no numbered list, no CTA in the first post.
Write the first post as a conversation opener and bring the product in the second post of
the thread, in one or two plain sentences, with the example written out and the images
attached (`media: slides`). A thread is complete on its own: never send the reader to
Instagram, the bio, or a link for the main point (owner feedback, 2026-11-09). Record it in `publish.md` as `post:` and `reply:`
lines so `make_preview.py` shows it as a thread.
