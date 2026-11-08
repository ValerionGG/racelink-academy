#!/usr/bin/env bash
# Builds the GitHub Pages output: the site at its root, plus a copy under /v2/.
set -euo pipefail
dest="${1:-_site}"
node scripts/build_home_snapshot.mjs
rm -rf "$dest"
mkdir -p "$dest"
cp -r site/. "$dest/"
mkdir -p "$dest/v2"
cp -r site/. "$dest/v2/"
find "$dest/v2" -path "$dest/v2/catalog" -prune -o -type f \( -name '*.html' -o -name '*.js' \) -print0 \
  | xargs -0 sed -i 's#/racelink-academy/#/racelink-academy/v2/#g'
du -sh "$dest"
