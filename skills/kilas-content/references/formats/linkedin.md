# LinkedIn: text post and document post

LinkedIn readers give a post a few lines before "…see more" (about 140 characters on
mobile, 210 on desktop, at most three lines, blank lines included). Those lines decide
whether the rest is read.

## 1. Text post (≤ 3,000 characters)

- **Lines 1–2**: the hook as a complete statement with the number or the named thing.
  No greeting, no "I'm excited to share".
- **Body**: short paragraphs of 1–3 sentences. Tell the ladder in prose: context, proof,
  the turn, what it means for the reader's work.
- **Close**: one takeaway or one question that offers a real choice, then the source.
- **Links**: a post carries either a link preview or images, not both. Put the source
  link in the text near the end.
- **Hashtags**: 0–3. LinkedIn removed hashtag following in 2024; they add little.
- **Voice**: the brand's voice, but professional readers expect the "so what for my
  team" answer stated plainly. That is the fifth story question.

## 2. Document post (the carousel as a PDF)

- Upload the carousel frames as one PDF: every page the same size (1080×1350), up to 300
  pages, 100 MB. `python3 scripts/slides_to_pdf.py <png dir> -o export/<slug>.pdf` (run
  it without `-I`: it needs Pillow), or Figma's PDF export.
- Give the document a title (shown on the cover of the viewer): the cover headline.
- The post text above it is a short version of the text post: hook, two sentences, "the
  data is in the document", source.
- Remove Instagram-only cues if they would confuse ("Geser" works; "link di bio" does
  not; replace it with the actual link in the post text).

## 3. Article or newsletter

For long pieces, publish the long-form source (`long-form.md`) as a LinkedIn article
(up to 125,000 characters) only if the brand has no site of its own, or repost a
summary that links to the site.

## 4. Checklist

- [ ] First two lines carry the whole claim (≤ ~140 characters to be safe on mobile).
- [ ] Paragraphs, not one-line broetry.
- [ ] One link, near the end; 0–3 hashtags.
- [ ] Document: same page size, titled, no "link di bio".
