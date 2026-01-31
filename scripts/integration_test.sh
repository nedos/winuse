#!/usr/bin/env bash
set -euo pipefail

HOST="${WINUSE_HOST:-http://10.7.17.5:8080}"
WINUSE_BIN="${WINUSE_BIN:-/home/nedos/dev/windowsuse/.venv/bin/winuse}"

if [[ ! -x "$WINUSE_BIN" ]]; then
  echo "winuse CLI not found at $WINUSE_BIN" >&2
  exit 2
fi

TS=$(date +%Y%m%d-%H%M%S)
MSG="integration-test-$TS"

# Bypass proxies for direct LAN access
export NO_PROXY='*'
export no_proxy='*'
export WINUSE_HOST="$HOST"

"$WINUSE_BIN" press winleft r
sleep 1
"$WINUSE_BIN" type cmd --mode paste
sleep 0.5
"$WINUSE_BIN" press enter
sleep 1
"$WINUSE_BIN" type "$MSG" --mode paste
"$WINUSE_BIN" press enter
sleep 0.5

# Full screenshot for spot-checking
"$WINUSE_BIN" screenshot

echo "Sent: $MSG"
