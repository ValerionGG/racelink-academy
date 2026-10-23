---
name: frontend-design-prompts
description: Frontend UI prompt library sourced from DesignPrompts.dev. Use when Codex needs ready-made visual direction, themed design prompts, or style comparisons for websites, landing pages, dashboards, and product UIs across aesthetics such as SaaS, enterprise, cyberpunk, terminal, brutalism, vaporwave, academia, botanical, and art deco. Also use when refreshing the local snapshot from the upstream homepage, sitemap, and JS bundle.
---

# Frontend Design Prompts

Use this skill to pick a design direction quickly and turn it into a frontend brief or prompt without re-browsing the source site.

## Quick Start

1. Read `references/home.md` for source status and snapshot scope.
2. Read `references/theme-overview.md` to absorb all theme introductions in one pass.
3. Infer the most likely theme from the user's tone, product type, reference sites, adjectives, and constraints.
4. Open one or two matching files under `references/themes/`.
5. Reuse the `Prompt Source` section as the base prompt.
6. Replace only the product-specific parts: app type, information architecture, feature blocks, CTA copy, and framework constraints.

## Theme Inference

- Do not rely on a fixed mapping table. Read `references/theme-overview.md` and decide from the actual theme descriptions.
- If the user explicitly names a theme, use it directly.
- If the request already implies a clear direction, choose the theme without asking for confirmation.
- If multiple themes fit and confidence is low, ask one short question about the desired visual feel before locking a theme.
- If the user still gives too little signal, offer `Flat Design`, `Enterprise`, and `Bauhaus` as concrete fallback options.
- If the user does not choose after that, default to `Flat Design`.
- Prefer reading at most three detailed theme files unless the user asks for a broader comparison.

## Working With The Prompt Files

- Treat each `Prompt Source` block as a design-system seed, not a rigid spec.
- Preserve the theme's visual logic: color system, typography pairing, layout metaphor, motion style, and standout rules.
- Rewrite product nouns, feature modules, content structure, data examples, and stack-specific implementation details.
- If the codebase already has an existing design system, adapt the prompt to that system instead of copying the source wording blindly.
- If the user wants code, turn the selected theme into concrete tokens, layout sections, and component guidance before implementation.

## References

- `references/home.md`: overview of the snapshot and source URLs.
- `references/theme-overview.md`: one-file introduction summary for all themes.
- `references/catalog.md`: theme index with quick filters.
- `references/themes/<slug>.md`: one theme per file with metadata, layout ideas, and raw prompt text.
- `references/designprompts.json`: machine-readable snapshot for scripts or bulk lookup.

## Refreshing The Snapshot

Run the sync script when the upstream site adds, removes, or edits themes:

```bash
python scripts/sync_designprompts.py
```

This rewrites `references/home.md`, `references/theme-overview.md`, `references/catalog.md`, `references/designprompts.json`, and every file under `references/themes/`.
