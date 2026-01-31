#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

# Load .env if present
if [[ -f "$ROOT_DIR/.env" ]]; then
  # shellcheck disable=SC1091
  source "$ROOT_DIR/.env"
fi

HOST="${WINUSE_HOST:-http://10.7.17.5:8080}"
WINUSE_BIN="${WINUSE_BIN:-$ROOT_DIR/.venv/bin/winuse}"

if [[ ! -x "$WINUSE_BIN" ]]; then
  echo "winuse CLI not found at $WINUSE_BIN" >&2
  exit 2
fi

export NO_PROXY='*'
export no_proxy='*'
export WINUSE_HOST="$HOST"

TS=$(date +%Y%m%d-%H%M%S)
MSG="integration-test-$TS"

"$WINUSE_BIN" press winleft r
sleep 1
"$WINUSE_BIN" type notepad --mode paste
sleep 0.5
"$WINUSE_BIN" press enter
sleep 5

# Use active window after launch (should be Notepad)
ACTIVE_JSON=$("$WINUSE_BIN" active)
export ACTIVE_JSON
HWND=$(
  python3 - <<'PY'
import json, os, sys

raw = os.environ.get("ACTIVE_JSON", "")
try:
    data = json.loads(raw)
except Exception:
    print("")
    sys.exit(0)

w = data.get("data") or {}
print(w.get("hwnd", ""))
PY
)

if [[ -z "$HWND" ]]; then
  echo "Could not find cmd window" >&2
  exit 3
fi

"$WINUSE_BIN" focus "$HWND" >/dev/null
sleep 0.4

BEFORE=$($WINUSE_BIN screenshot --hwnd "$HWND")

"$WINUSE_BIN" press ctrl n
sleep 0.3
"$WINUSE_BIN" type "$MSG" --mode paste
sleep 0.3

# Refocus, then type character-by-character
"$WINUSE_BIN" focus "$HWND" >/dev/null
sleep 0.3
"$WINUSE_BIN" type " typing this too." --mode type --interval 0.1

AFTER=$($WINUSE_BIN screenshot --hwnd "$HWND")

echo "HWND: $HWND"
echo "Before: $BEFORE"
echo "After: $AFTER"
echo "Sent: $MSG"
