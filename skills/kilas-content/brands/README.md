# Brand packs

Everything brand-specific lives in a brand pack: identity, audience, language and
voice, channels, pillars, series, cadence, CTAs, moments, long-form format, banned
phrases, compliance, sources (`brand.md`), and colours, fonts, schemes, logo
(`design.md`). The rest of the skill is brand-agnostic and reads these files.

## Where the skill looks

1. `content/brand/brand.md` in the current project (the brand's workspace).
2. `brands/<name>/brand.md` in this skill, when the user names the brand or only one
   pack besides `_template` exists.
3. Neither: run the setup-content skill (`../setup-content/SKILL.md`; method in
   `references/brand-onboarding.md`), which writes the pack to `content/brand/` in the
   current project, the brand's own assets to `content/brand/assets/`, and
   `content/setup.md`.

The `BRAND` block in `design.md` feeds both renderers: `scripts/figma_bundle.py` for
Figma and `scripts/brand_css.py` for HTML → PNG. Its `logo.image` and
`logo.imageOnDark` (paths relative to the pack folder) put the brand's own logo file on
the close slide; without them the `letter` + `wordmark` lockup is drawn.

## Packs here

| Pack | What |
|---|---|
| `_template/` | the empty format; copy it to start a new brand |

A pack may add `examples/` (finished pieces with notes) and `evals/` (test prompts).
`scripts/export_oss.sh` copies the skill without any pack except `_template`.
