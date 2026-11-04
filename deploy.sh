#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
# Other jobs commit to main (the Mac mini's nightly home-network update). This deploy is the only
# publisher, so it must build from the latest main or it overwrites their work on the live site.
# Discard generated diagrams from the previous build first so they cannot block the fast-forward.
git checkout -q -- assets/diagrams-pro/diagram-*.svg assets/diagrams-pro/diagram-*.png 2>/dev/null || true
git pull --ff-only -q origin main
[ -d node_modules ] || npm ci --silent
bash bin/sync-content.sh
# Architecture diagrams: counts and names come from the docs on every build.
python3 bin/fleet_facts.py || echo "WARNING: fleet facts failed; the page will say the diagrams are stale"
python3 assets/diagrams-pro/src/build_diagrams.py || echo "WARNING: diagram build failed; the page will say the diagrams are stale"
node build.mjs
remote=$(git remote get-url origin)
tmp=$(mktemp -d); trap 'rm -rf "$tmp"' EXIT
cp -R dist/. "$tmp/"
git -C "$tmp" init -q -b gh-pages; git -C "$tmp" add -A
git -C "$tmp" -c user.name="$(git config user.name)" -c user.email="$(git config user.email)" commit -q -m "Publish $(date +%F) wiki"
git -C "$tmp" push -q -f "$remote" gh-pages
echo "Deployed to https://wiki.remnantsecurity.com"
