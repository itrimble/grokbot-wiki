#!/usr/bin/env bash
# Alerts if the nightly update has not succeeded for 36 hours. Runs from its own LaunchAgent.
set -uo pipefail
LOGDIR="${HOME_NETWORK_LOGS:-$HOME/Library/Logs/home-network-facts}"
NOTIFY="${NOTIFY:-$HOME/bin/notify.sh}"
LAST="$LOGDIR/last-success"
now=$(date +%s)
last=$(cat "$LAST" 2>/dev/null || echo 0)
age=$(( (now - last) / 3600 ))
if [ "$last" -eq 0 ] || [ "$age" -ge 36 ]; then
  msg="The home-network wiki update has not succeeded for ${age}h (or has never run). Check $LOGDIR/nightly.log."
  echo "$(date '+%F %T') $msg" >>"$LOGDIR/watchdog.log"
  [ -x "$NOTIFY" ] && "$NOTIFY" -t "Home network wiki update is stale" -p high -g warning "$msg"
else
  echo "$(date '+%F %T') ok, last success ${age}h ago" >>"$LOGDIR/watchdog.log"
fi
