#!/usr/bin/env bash
# Nightly home-network update: collect -> render -> validate -> commit -> push.
# Runs on the Mac mini under launchd (see install-on-mini.sh). Nothing is committed unless the
# validator passes. A failure restores the working tree, alerts the phone and publishes nothing.
#
#   bin/home-network/nightly.sh              # the real run
#   NIGHTLY_DRY=1 bin/home-network/nightly.sh  # everything except commit, push and alerts
set -uo pipefail

REPO="${WIKI_FACTS_REPO:-$HOME/wiki-facts/grokbot-wiki}"
TARGETS="${HOME_NETWORK_TARGETS:-$HOME/.config/home-network/targets.json}"
LOGDIR="${HOME_NETWORK_LOGS:-$HOME/Library/Logs/home-network-facts}"
NOTIFY="${NOTIFY:-$HOME/bin/notify.sh}"
BRANCH="${WIKI_FACTS_BRANCH:-main}"
REMOTE="${WIKI_FACTS_REMOTE:-origin}"
PY_COLLECT="${PY_COLLECT:-/usr/bin/python3}"   # Apple's Python: it can read the ARP table; Homebrew's cannot here
PY="${PY:-python3}"
DRY="${NIGHTLY_DRY:-0}"
OWNED="facts pages assets/home-network/physical.svg assets/home-network/logical.svg assets/home-network/relationships.svg"

mkdir -p "$LOGDIR"
LOG="$LOGDIR/nightly.log"
LOCK="$LOGDIR/lock"

say() { echo "$(date '+%F %T') $*" | tee -a "$LOG"; }

alert() { # title priority tags message
  if [ "$DRY" = 1 ]; then say "[dry run] would alert: $1 / $4"; return; fi
  if [ -x "$NOTIFY" ]; then "$NOTIFY" -t "$1" -p "$2" -g "$3" "$4" >>"$LOG" 2>&1 || say "ntfy delivery failed"
  else say "no notifier at $NOTIFY; would have sent: $1 / $4"; fi
}

# One run at a time. A lock older than 90 minutes is stale (a crashed run) and is cleared.
if ! mkdir "$LOCK" 2>/dev/null; then
  if [ -n "$(find "$LOCK" -maxdepth 0 -mmin +90 2>/dev/null)" ]; then
    say "clearing a stale lock"; rmdir "$LOCK" 2>/dev/null; mkdir "$LOCK" || exit 1
  else
    say "another run is in progress; exiting"; exit 0
  fi
fi
cleanup() { rmdir "$LOCK" 2>/dev/null; }
trap cleanup EXIT

fail() { # step name
  say "FAILED at: $1"
  # Put the working tree back so tomorrow starts clean. Only the paths this job owns are touched.
  git -C "$REPO" checkout -q -- $OWNED 2>/dev/null
  git -C "$REPO" clean -fdq -- $OWNED 2>/dev/null
  alert "Home network wiki update failed" high warning "Stopped at: $1. Nothing was published. Log: $LOG"
  exit 1
}

say "start (dry=$DRY, repo=$REPO)"
cd "$REPO" || fail "cd to the repo"

git fetch -q "$REMOTE" "$BRANCH" || fail "git fetch"
git checkout -q "$BRANCH" || fail "git checkout $BRANCH"
git merge -q --ff-only "$REMOTE/$BRANCH" || fail "fast-forward to $REMOTE/$BRANCH (has the local clone diverged?)"

OLD="$(mktemp)"
git show HEAD:facts/home-network.json >"$OLD" 2>/dev/null || : >"$OLD"

"$PY_COLLECT" bin/home-network/collect.py --targets "$TARGETS" >>"$LOG" 2>&1 || fail "collect"
"$PY" bin/home-network/render.py >>"$LOG" 2>&1 || fail "render"
"$PY" bin/home-network/validate.py >>"$LOG" 2>&1 || fail "validate"

NOTES="$("$PY" bin/home-network/changes.py "$OLD" facts/home-network.json 2>>"$LOG")"
rm -f "$OLD"
[ -n "$NOTES" ] && say "changes: $(echo "$NOTES" | tr '\n' ';')"

# shellcheck disable=SC2086
if git diff --quiet -- $OWNED && [ -z "$(git ls-files --others --exclude-standard -- $OWNED)" ]; then
  say "nothing to commit"
elif [ "$DRY" = 1 ]; then
  say "[dry run] would commit: $(git status --short -- $OWNED | wc -l | tr -d ' ') file(s)"
  git checkout -q -- $OWNED; git clean -fdq -- $OWNED
else
  DATE="$("$PY" -c 'import json;print(json.load(open("facts/home-network.json"))["collected_date"])')"
  # shellcheck disable=SC2086
  git add -- $OWNED
  {
    echo "facts: home network $DATE"; echo; echo "Automatic nightly update from the read-only collector."
    if [ -n "$NOTES" ]; then echo; echo "$NOTES"; fi
  } | git commit -q -F - || fail "git commit"
  pushed=0
  for attempt in 1 2 3; do
    if git push -q "$REMOTE" "$BRANCH" 2>>"$LOG"; then pushed=1; break; fi
    say "push rejected (attempt $attempt); rebasing"
    git pull -q --rebase "$REMOTE" "$BRANCH" 2>>"$LOG" || { git rebase --abort 2>/dev/null; fail "rebase after a rejected push"; }
  done
  [ "$pushed" = 1 ] || fail "git push"
  say "pushed $(git rev-parse --short HEAD)"
fi

date +%s >"$LOGDIR/last-success"

if echo "$NOTES" | grep -q '^NOTABLE'; then
  alert "Home network: notable change" high warning "$(echo "$NOTES" | grep '^NOTABLE' | sed 's/^NOTABLE //' | head -5 | tr '\n' ';') Published to the wiki repo; the site updates at the next deploy."
fi
say "done"
