#!/usr/bin/env bash
# Daily check, from its own LaunchAgent at 08:00. Alerts the phone if either of these is true:
#   1. the nightly update has not succeeded for 36 hours, or
#   2. the LIVE wiki page is missing or stale. The box is the only publisher, so if it stops
#      pulling main, this section silently disappears or freezes. This is the check that notices.
# The live-page check tolerates weekends: the box deploys Monday to Friday, so a page up to 3 days
# old is normal on a Monday morning.
set -uo pipefail
export PYTHONDONTWRITEBYTECODE=1

LOGDIR="${HOME_NETWORK_LOGS:-$HOME/Library/Logs/home-network-facts}"
NOTIFY="${NOTIFY:-$HOME/bin/notify.sh}"
LIVE_URL="${HOME_NETWORK_LIVE_URL:-https://wiki.remnantsecurity.com/home-network/overview/}"
MAX_LIVE_AGE_DAYS="${HOME_NETWORK_MAX_LIVE_AGE_DAYS:-4}"
mkdir -p "$LOGDIR"
log() { echo "$(date '+%F %T') $*" >>"$LOGDIR/watchdog.log"; }

problems=()

# 1. the nightly job
now=$(date +%s)
last=$(cat "$LOGDIR/last-success" 2>/dev/null || echo 0)
age_h=$(( (now - last) / 3600 ))
if [ "$last" -eq 0 ]; then problems+=("The nightly update has never succeeded.")
elif [ "$age_h" -ge 36 ]; then problems+=("The nightly update has not succeeded for ${age_h}h.")
fi

# 2. the live page
resp="$(curl -s -m 25 -w $'\n%{http_code}' "$LIVE_URL" 2>/dev/null || true)"
code="${resp##*$'\n'}"
page="${resp%$'\n'*}"
if [ "$code" != "200" ]; then
  problems+=("The live wiki has no home-network page (HTTP ${code:-none}). The box is probably not pulling main. It needs: git pull --ff-only before its build.")
else
  live_date="$(printf '%s' "$page" | grep -o 'I last checked the details on [0-9]\{4\}-[0-9]\{2\}-[0-9]\{2\}' | head -1 | grep -o '[0-9]\{4\}-[0-9]\{2\}-[0-9]\{2\}')"
  if [ -z "$live_date" ]; then
    problems+=("The live home-network page has no check date, so it is not the generated version. The box may be building from an old copy.")
  else
    live_age="$(python3 -c 'import datetime,sys; print((datetime.date.today()-datetime.date.fromisoformat(sys.argv[1])).days)' "$live_date" 2>/dev/null || echo 999)"
    if [ "$live_age" -ge "$MAX_LIVE_AGE_DAYS" ]; then
      problems+=("The live home-network page is ${live_age} days old (checked ${live_date}). The box may have stopped deploying or pulling.")
    fi
  fi
fi

if [ "${#problems[@]}" -gt 0 ]; then
  msg="${problems[*]}"
  log "PROBLEM: $msg"
  if [ -x "$NOTIFY" ]; then "$NOTIFY" -t "Home network wiki: needs attention" -p high -g warning "$msg"; else log "no notifier at $NOTIFY"; fi
  exit 1
fi
log "ok: last success ${age_h}h ago; live page checked ${live_date} (${live_age} day(s) old)"
