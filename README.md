# kilas-content

Two agent skills that plan a brand's social content and produce it end to end: a monthly
plan with pillars, series, and a calendar; researched pieces with hooks that earn
attention; Instagram carousels and single posts built in Figma or rendered from HTML to
PNG; Reels/TikTok scripts; X threads; LinkedIn posts and documents; Threads.

| Skill | What it does |
|---|---|
| [`kilas-content`](skills/kilas-content/) | plans and creates the content; every brand detail lives in a brand pack |
| [`setup-content`](skills/setup-content/) | first run: asks which brand, collects the brand's own logo, colours, fonts, and photos from its site and profiles (with permission), chooses Figma or HTML → PNG, and writes the brand pack |

## Install

With the [skills CLI](https://github.com/vercel-labs/skills), both skills together (the
content skill runs setup-content on first use):

```bash
npx skills add kilaslab/kilas-content --skill kilas-content --skill setup-content
npx skills add kilaslab/kilas-content --skill kilas-content --skill setup-content -g -a claude-code   # global, one agent
```

Or by hand: copy `skills/kilas-content/` and `skills/setup-content/` side by side into your
agent's skills folder (`~/.claude/skills/`, `~/.agents/skills/`, `~/.grok/skills/` for Grok
Build and Grok Bot, ...).

Needs Python 3.9+. Optional, detected at run time: the Figma MCP (Figma frames), Python
Playwright or Chrome/Chromium (HTML → PNG frames), web search and fetch, a real browser
for profile capture, and image generation: the agent's own image tool (Grok Bot's Grok
Imagine, Codex, ChatGPT, Antigravity), the Antigravity CLI `agy`, or an OpenAI, Gemini,
or xAI key the owner allows at setup. Companion skills (`copywriting`,
`social`, `humanizer`, `bahasa-indonesia`) are listed in
`skills/kilas-content/references/prerequisites.md`.

## Use

> setup content untuk brand kami: <website>, instagram <link>
>
> rencana konten bulan ini
>
> bikin carousel dari artikel ini <link>

Start with `skills/kilas-content/README.md` and `skills/kilas-content/SKILL.md`; a new brand pack starts
from `skills/kilas-content/brands/_template/`.

## License

Copyright (C) 2026 Kilaslab

GPL-3.0-or-later: see [LICENSE](LICENSE). You may use, study, change, and share
these skills; copies and modified versions you distribute must stay under the GPL and
ship their source.
