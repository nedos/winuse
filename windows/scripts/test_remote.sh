#!/usr/bin/env bash
set -euo pipefail

HOST="${1:-}"
PORT="${2:-8080}"

if [[ -z "$HOST" ]]; then
  echo "Usage: ./scripts/test_remote.sh HOST [PORT]"
  exit 1
fi

export WINUSE_HOST="http://$HOST:$PORT"
pytest -q tests/test_api.py
