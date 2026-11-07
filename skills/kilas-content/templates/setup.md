# Setup

Written by the setup-content skill on <date> by <agent>. The content skill reads this
first; if it is missing, setup runs again.

- Brand: <name> · pack: `content/brand/` (or the skill's `brands/<name>/`)
- Renderer: <figma | html | both>
  - Figma: file <url> (key <key>); one new page per piece
  - HTML: `scripts/new_html.py` per item, `scripts/render_slides.py` with <playwright | chrome path>
- Language: <id> · address: <kamu>
- Images: generate automatically for metaphor slides: <yes | no> · tool: <the agent's own
  (Grok Imagine, Codex, ...) | agy | none> · paid APIs: <allowed: gemini first, then openai | not allowed>
  (<date>; the owner can change this by asking)
- Brainstorm partner: <codex (model) | gemini | none> for hooks, copy, and slide flow
  (`references/brainstorm-partner.md`)
- Default scheme: <name>; series schemes in `brand.md`
- Assets: `content/brand/assets/` · sources: <site, instagram, ...> · permission: <date, what, signed-in session yes/no>
- Not collected: <source and why: parked domain, login wall, robots.txt, none given>
- Tools found: <web search, fetch, browser, Figma MCP, agy, image API keys, ...> · missing: <...>
- Gallery: <Figma pages, or content/setup-gallery/*.jpg>
- Still proposed: <pillars, series, schemes, ... until the owner confirms>
