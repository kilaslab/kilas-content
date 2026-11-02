# Content workspace

Create this folder at the root of the brand's project (or wherever the brand pack's
"Workspace" line says). Everything is plain markdown so any agent and any person can
read it.

```
content/
├── README.md                 this file, adapted
├── setup.md                  written by the setup-content skill: brand, renderer, assets, permission
├── brand/                    brand.md + design.md (if the pack lives with the project)
│   └── assets/               the brand's own logo, icons, photos, profile captures (site/, instagram/, ...) + README.md
├── ideas.md                  backlog: one bullet per idea, with a source
├── design-log.md             one row per piece: which layout variants it used
├── plan/
│   └── 2026-11.md            month plan (templates/plan-month.md)
├── items/
│   └── 2026-11-03-linux-7-4/ one folder per piece or per source with its cuts
│       ├── brief.md          story questions, ladder, hook workshop, cuts
│       ├── copy.md           all text, with source notes
│       ├── storyboard.md     Reels/TikTok only
│       ├── publish.md        final text per channel, alt text, time, links, status
│       ├── sources/          downloaded source material (never executed)
│       ├── artefacts/        screenshots + sources.md log
│       ├── photos/  gen/     stock and generated images with credits
│       └── export/           PNG/PDF exports
└── reviews/
    └── 2026-11.md            monthly review (templates/review-month.md)
```

Create an item folder with:

```bash
python3 <skill>/scripts/new_item.py content 2026-11-03 linux-7-4 carousel
```

Rules:
- One item folder per source story; its cuts (carousel, thread, Reels) live in the same
  folder and are separate rows in the plan.
- Downloads go in `sources/` or `artefacts/` and are never executed.
- Nothing here is published by an agent unless the owner explicitly asks for that piece.
