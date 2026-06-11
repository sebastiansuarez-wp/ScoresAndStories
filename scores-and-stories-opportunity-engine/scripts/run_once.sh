#!/usr/bin/env bash
# Single cycle, for cron/launchd scheduling instead of the loop.
set -euo pipefail
cd "$(dirname "$0")/.."
claude -p "/cycle" --permission-mode acceptEdits
