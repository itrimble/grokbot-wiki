#!/usr/bin/env bash
# One-time setup on the Mac mini. Run it ON the mini, as the user that owns the jobs.
#
#   bash install-on-mini.sh            # install or refresh
#   bash install-on-mini.sh --dry-run  # show what it would do, change nothing
#
# It creates a private clone outside the synced ~/projects tree (like the product diary does),
# checks the private targets file exists, installs two LaunchAgents and loads them. It does not
# run the update itself: do a NIGHTLY_DRY=1 run first (see README.md).
set -euo pipefail

DRY=0; [ "${1:-}" = "--dry-run" ] && DRY=1
DEST="$HOME/wiki-facts/grokbot-wiki"
SRC_DIR="$DEST/bin/home-network"
TARGETS="$HOME/.config/home-network/targets.json"
LA="$HOME/Library/LaunchAgents"
LOGS="$HOME/Library/Logs/home-network-facts"
UID_NUM="$(id -u)"

do_it() { if [ "$DRY" = 1 ]; then echo "[dry run] $*"; else "$@"; fi; }

echo "== 1. private clone at $DEST (outside the synced projects tree)"
if [ -d "$DEST/.git" ]; then do_it git -C "$DEST" fetch -q origin main
else do_it mkdir -p "$(dirname "$DEST")"; do_it gh repo clone itrimble/grokbot-wiki "$DEST"; fi

echo "== 2. private targets file"
if [ -f "$TARGETS" ]; then echo "found $TARGETS"
else
  do_it mkdir -p "$(dirname "$TARGETS")"
  do_it cp "$SRC_DIR/targets.example.json" "$TARGETS"
  echo "Created $TARGETS from the example. EDIT IT with the real addresses before the first run."
  echo "It is private: it holds addresses and MACs and must never be committed."
fi

echo "== 3. log folder and LaunchAgents"
do_it mkdir -p "$LOGS" "$LA"
for label in com.ian.home-network-facts com.ian.home-network-facts-watchdog; do
  plist="$LA/$label.plist"
  if [ "$DRY" = 1 ]; then echo "[dry run] would write $plist and load it"; continue; fi
  sed "s#__HOME__#$HOME#g" "$SRC_DIR/$label.plist" >"$plist"
  launchctl bootout "gui/$UID_NUM/$label" 2>/dev/null || true
  launchctl bootstrap "gui/$UID_NUM" "$plist"
  echo "loaded $label"
done

echo "== done. Next: NIGHTLY_DRY=1 bash $SRC_DIR/nightly.sh   (collect, render, validate; no commit)"
