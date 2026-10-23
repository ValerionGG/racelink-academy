# Source Notes

## Summary

This repository is an attributed snapshot derived from the public website [designprompts.dev](https://www.designprompts.dev/).

The prompt and theme data in this repo were extracted from the publicly served frontend bundle and validated against the public sitemap.

## What was verified

### 1. Public site identity

The homepage describes the site as:

- "Design Prompts - AI-Powered Design Style Explorer"
- "Explore 31+ stunning design styles rendered from the same data. Get AI-ready prompts to recreate any aesthetic in your own projects."

Source:

- [Homepage](https://www.designprompts.dev/)

### 2. Deployment / protocol

When checked on 2026-04-23, the site responded over HTTPS and returned `Server: Vercel` headers.

Observed via:

- `curl -I -L https://www.designprompts.dev/`

This means the public site was reachable via standard HTTPS and was hosted behind Vercel at the time of capture.

### 3. Origin story from the creator's public post

In a public Reddit post, user `mellowkenneth` described `designprompts.dev` as:

- a side project
- "a sort of modern take on the old CSS Zen Garden idea, but for AI prompts"
- a gallery using one shared `data.json` across 31 styles
- rebuilt around Claude Opus 4.5
- "100% free"
- "mostly a passion project"

Source:

- [Reddit post in r/vibecoding](https://www.reddit.com/r/vibecoding/comments/1pcy8bi/i_made_a_free_gallery_of_31_actuallygood_ui/)

### 4. Extraction source used in this repo

This repo extracts from:

- Homepage: [https://www.designprompts.dev/](https://www.designprompts.dev/)
- Bundle: [https://www.designprompts.dev/assets/index-FHds4wvP.js](https://www.designprompts.dev/assets/index-FHds4wvP.js)
- Sitemap: [https://www.designprompts.dev/sitemap.xml](https://www.designprompts.dev/sitemap.xml)

The extraction logic lives in:

- `scripts/sync_designprompts.py`

## License status

As of 2026-04-23, I did not find any explicit:

- open-source license for the site content
- public source repository link on the homepage
- reuse terms or content license statement on the homepage

This note is a factual status note, not legal advice.

## Repository policy

Because the upstream license is currently unknown, this repo is published as:

- an attributed reference snapshot
- a convenience packaging of publicly accessible material
- not an official mirror
- not a relicensed upstream project

If the upstream author later publishes a license, repository link, or takedown request, this repo should be updated accordingly.
