#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
[ -d node_modules ] || npm ci --silent
bash bin/sync-content.sh
node build.mjs
remote=$(git remote get-url origin)
tmp=$(mktemp -d); trap 'rm -rf "$tmp"' EXIT
cp -R dist/. "$tmp/"
git -C "$tmp" init -q -b gh-pages; git -C "$tmp" add -A
git -C "$tmp" -c user.name="$(git config user.name)" -c user.email="$(git config user.email)" commit -q -m "Publish $(date +%F) wiki"
git -C "$tmp" push -q -f "$remote" gh-pages
echo "Deployed to https://wiki.remnantsecurity.com"
