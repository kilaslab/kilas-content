# Prerequisites: companion skills

This skill orchestrates four companion skills plus one renderer: the Figma MCP or the
HTML → PNG kit. Install them once;
after that every agent on the machine sees them through the shared hub.

## The hub

`~/.agents/skills/` is the single source of truth on this machine. The `skills` CLI
stores each skill there and **symlinks** it into every agent's own directory, so one
install covers all of them:

```
~/.agents/skills/<skill>/          ← real files (the hub)
~/.claude/skills/<skill>           → ../../.agents/skills/<skill>
~/.cursor/skills/<skill>           → …
~/.config/opencode/skills/<skill>  → …
~/.gemini/skills/<skill>           → …        (Antigravity CLI / agy)
~/.grok/skills/<skill>             → …        (Grok Build CLI and Grok Bot)
~/.omp/…                           (omp reads ~/.agents/skills directly)
```

`omp` lists them as `source: agents:user`; OpenCode and Claude read the same hub.

## Install (one command per companion)

```bash
npx skills@latest add https://github.com/coreyhaines31/marketingskills --skill copywriting     --agent '*' -g -y
npx skills@latest add https://github.com/coreyhaines31/marketingskills --skill social          --agent '*' -g -y
npx skills@latest add https://github.com/blader/humanizer               --skill humanizer       --agent '*' -g -y
npx skills@latest add https://github.com/ajipurn/bahasa-indonesia-skill --skill bahasa-indonesia --agent '*' -g -y
```

Or run them all: `scripts/install-companions.sh`

### Which one does what

| Skill | Source | Needed for |
|---|---|---|
| `copywriting` | `coreyhaines31/marketingskills` | headline/CTA craft, AI-tells blacklist |
| `social` | `coreyhaines31/marketingskills` | `social/references/carousel-frameworks.md` — pick the framework |
| `humanizer` | `blader/humanizer` | strip structural AI tells from the copy |
| `bahasa-indonesia` | `ajipurn/bahasa-indonesia-skill` | Indonesian register, orthography, no calques |
| `copy-editing` *(optional)* | `coreyhaines31/marketingskills` | final line-by-line polish |

Useful flags:

- `--agent '*'` → install for every agent the CLI knows (default is to ask).
- `-g` → user-global (`~/.agents/skills`), not just this project.
- `-s '*'` / `--all` → take every skill in a repo.
- `-l` → list what a repo offers without installing.
- `--copy` → copy instead of symlinking (use if an agent cannot follow symlinks).
- `-p` instead of `-g` → project scope (`./.agents/skills`), which travels with the repo.

Caveat: two agents (Eve, PromptScript) refuse global installs and print
`does not support global skill installation`. That is expected; the other agents and the
hub still get the files.

## Video companions (for a Reels video)

Install when the brand makes Reels videos (`motion-video.md` says which step uses each):

```bash
npx skills@latest add heygen-com/hyperframes -s '*' --agent '*' -g -y          # hyperframes, -cli, -registry, media-use, ...
npx skills@latest add iart-ai/tiktok-video-skills -s short-form-video --agent '*' -g -y
npx skills@latest add lottiefiles/motion-design-skill -s motion-design --agent '*' -g -y
npx skills@latest add iart-ai/kinetic-typography-skills -s kinetic-typography --agent '*' -g -y
npx skills@latest add elevenlabs/skills -s sound-effects -s music -s text-to-speech -s speech-to-text --agent '*' -g -y
npx skills@latest add greensock/gsap-skills -s gsap-core -s gsap-timeline --agent '*' -g -y
npx skills@latest add remotion-dev/skills -s '*' --agent '*' -g -y              # optional: only for Remotion builds
brew install ffmpeg                                                              # ffprobe is required by the HyperFrames render
```

Voice-over: an ElevenLabs API key in the project's `.env` as `ELEVENLABS_API_KEY`, with the
permissions `text_to_speech` and `speech_to_text` (`scripts/vo_elevenlabs.py`). An agent's
classifier may block installing third-party skills until the owner asks for it in so many
words; then run the command again or hand it to the owner.

## The Figma MCP skills are not installable

`figma-use` and `figma-generate-design` ship with the **Figma MCP server**, not the
`skills` CLI. Read them as MCP resources before the first `use_figma` call:

```
skill://figma/figma-use/SKILL.md
skill://figma/figma-generate-design/SKILL.md
```

then pass `skillNames: "resource:figma-use,resource:figma-generate-design"`.

If the Figma MCP is not connected, Figma builds are blocked: say so and offer the HTML
renderer (`html-render.md`); never draw a placeholder.

## HTML renderer

`scripts/render_slides.py` uses Python Playwright when it is installed (`pip install
playwright && playwright install chromium`), otherwise Chrome, Chromium, Edge, or Brave in
headless mode. Rendering loads the brand's fonts from Google Fonts, so it needs the
network.

## Optional: image generation

The skill generates metaphor images with whatever is there, in this order
(`image-sourcing.md`):

1. The agent's own image tool: Grok Bot (Grok Imagine), Codex, ChatGPT, Antigravity,
   and Grok Build when its tools include image generation. Nothing to install.
2. The Antigravity CLI `agy`: install from https://antigravity.google and sign in once
   (`command -v agy && agy models`). In Claude Code, allow `Bash(agy:*)` if the command
   classifier blocks it.
3. A paid image API, used only after the owner allows it at setup: `OPENAI_API_KEY`
   (OpenAI), `GEMINI_API_KEY` or `GOOGLE_API_KEY` (Gemini), `XAI_API_KEY` (Grok
   Imagine). Optional model overrides: `OPENAI_IMAGE_MODEL`, `GEMINI_IMAGE_MODEL`,
   `XAI_IMAGE_MODEL`.

`python3 scripts/gen_image.py detect` shows what it finds. With none of them, the skill
uses Unsplash.

Python scripts need Pillow (`pip install pillow`) for `contact_sheet.py`,
`slides_to_pdf.py`, `artefact_marks.py`, and `ref_sheets.py`, and `curl` for Unsplash.

## Optional: research tools

None are required; each one makes the research or the artefacts better. See
`research-tools.md`.

- Web search and page fetch: built into Claude Code, OpenCode, Cursor, and Gemini-based
  CLIs. Nothing to install.
- `ego-browser` (Ego Lite): a real Chromium the agent can drive. Needed by
  `scripts/capture_artefact.sh`, `capture_profile.sh`, and `scan_site_tokens.sh`; it
  passes bot checks that block headless browsers.
- An MCP server or built-in tool for X, Instagram, or Threads, if the host has one.
  Use it read-only.
- `scripts/x_post.py` needs only `curl` and Python 3.9+.

## Verify

```bash
ls ~/.agents/skills | grep -E 'copywriting|social|humanizer|bahasa-indonesia'
omp skill list --json | grep -o '"name":"[^"]*"' | grep -E 'copywriting|social|humanizer|bahasa'
npx skills@latest list
```

If an agent misses them, symlink the hub entry into that agent's own skills directory by
hand:

```bash
ln -s ~/.agents/skills/copywriting ~/.cursor/skills/copywriting
```

## Update

```bash
npx skills@latest update          # all of them
npx skills@latest update social   # one
```

Project copies: a project may keep its own copy in `.agents/skills/<name>` with a symlink in
`.claude/skills/<name>` so Claude and Codex both load it (tested with humanizer and social, 2026-11).
