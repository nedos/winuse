#!/usr/bin/env bash
set -euo pipefail

HOST="${1:-}"
DEST="${2:-}"

if [[ -z "$HOST" || -z "$DEST" ]]; then
  echo "Usage: ./scripts/deploy.sh user@host 'C:/path/to/dir'"
  exit 1
fi

ARCHIVE="/tmp/winuse.zip"
rm -f "$ARCHIVE"

zip -r "$ARCHIVE" . \
  -x "*.git*" \
  -x "*/__pycache__/*" \
  -x "*.pyc" \
  -x ".venv/*" \
  -x "venv/*" \
  -x "dist/*" \
  -x "build/*"

scp "$ARCHIVE" "$HOST":"$DEST"/winuse.zip

ssh "$HOST" "powershell -NoProfile -Command \"\
  \$dest='$DEST'; \
  if (!(Test-Path \$dest)) { New-Item -ItemType Directory -Path \$dest | Out-Null }; \
  Expand-Archive -Force -Path (Join-Path \$dest 'winuse.zip') -DestinationPath \$dest; \
  Set-Location \$dest; \
  python -m pip install -r requirements.txt; \
\""

echo "Deployed to $HOST:$DEST"
