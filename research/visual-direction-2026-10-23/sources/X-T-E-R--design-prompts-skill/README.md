# Frontend Design Prompts Skill

[简体中文](./README.zh-CN.md)

`frontend-design-prompts` is a Codex skill that packages the public theme descriptions and prompt texts from [designprompts.dev](https://www.designprompts.dev/) into a local, searchable skill.

It is meant for one job: help an agent infer a suitable frontend visual direction, load the right prompt files, and turn them into implementation-ready design guidance.

## What this repo contains

- `SKILL.md`: the skill entry point.
- `references/theme-overview.md`: one-file summary of all upstream theme introductions.
- `references/themes/*.md`: one file per theme with metadata, layout ideas, and prompt text.
- `references/designprompts.json`: machine-readable snapshot.
- `scripts/sync_designprompts.py`: refreshes the snapshot from the upstream site.

## How the skill behaves

- Read the aggregated theme overview first.
- Infer the best theme from the user's tone, product type, references, and constraints.
- Ask one short follow-up only if the theme is still ambiguous.
- If the request is still too vague, offer `Flat Design`, `Enterprise`, and `Bauhaus`.
- If no signal is available after that, default to `Flat Design`.

## Refresh the snapshot

```bash
python scripts/sync_designprompts.py
```

The script rewrites:

- `references/home.md`
- `references/theme-overview.md`
- `references/catalog.md`
- `references/designprompts.json`
- every file under `references/themes/`

## Provenance

This repository is derived from the public website [designprompts.dev](https://www.designprompts.dev/) and its published frontend bundle:

- Homepage: [https://www.designprompts.dev/](https://www.designprompts.dev/)
- Bundle used for extraction: [https://www.designprompts.dev/assets/index-FHds4wvP.js](https://www.designprompts.dev/assets/index-FHds4wvP.js)
- Sitemap used for route validation: [https://www.designprompts.dev/sitemap.xml](https://www.designprompts.dev/sitemap.xml)

Read [SOURCE.md](./SOURCE.md) for the research notes, attribution details, and the current license status caveat.

## Important license note

As of 2026-04-23, I did not find an explicit open-source license, public source repository link, or reuse terms on the site homepage or shipped frontend bundle.

Because of that, this repo should be treated as an attributed reference snapshot of publicly accessible material, not as a relicensed upstream work. If you want to redistribute it broadly or use it commercially, verify permission from the original author first.

## Friendly Links

- [linux.do](https://linux.do/)
