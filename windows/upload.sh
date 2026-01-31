#!/usr/bin/env bash
set -euo pipefail

HOST="${1:-}"
DEST="${2:-}"

if [[ -z "$HOST" || -z "$DEST" ]]; then
  echo "Usage: ./upload.sh user@host 'C:/path/to/dir'"
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

echo "Uploaded to $HOST:$DEST/winuse.zip"
