#!/usr/bin/env bash
# Continuous runner. Default interval 2700 seconds (45 minutes).
# Usage: ./scripts/loop.sh            (45 min sprint mode)
#        INTERVAL=259200 ./scripts/loop.sh   (every 3 days, the playbook floor)
set -euo pipefail
cd "$(dirname "$0")/.."
INTERVAL="${INTERVAL:-2700}"
echo "Wagner Prep Opportunity Engine loop. Interval: ${INTERVAL}s. Ctrl+C to stop."
while true; do
  echo "=== Cycle starting $(date) ==="
  claude -p "/cycle" --permission-mode acceptEdits || echo "Cycle failed, will retry next interval."
  echo "=== Cycle done. Sleeping ${INTERVAL}s ==="
  sleep "$INTERVAL"
done
