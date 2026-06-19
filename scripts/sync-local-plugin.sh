#!/usr/bin/env bash
# Copy plugin into ~/.cursor/plugins/local/ for Cursor 3.x (external symlinks are rejected).
set -euo pipefail

SRC="$(cd "$(dirname "$0")/.." && pwd)"
DEST="${HOME}/.cursor/plugins/local/styx"

mkdir -p "${HOME}/.cursor/plugins/local"
rsync -a --delete \
  --exclude dist \
  --exclude .git \
  --exclude .cursor \
  --exclude eval/node_modules \
  --exclude eval/results \
  --exclude 'hooks/__pycache__' \
  --exclude Manifest.toml \
  --exclude .julia-env-instantiated \
  --exclude node_modules \
  "${SRC}/" "${DEST}/"

echo "Synced to ${DEST}"
chmod +x "${DEST}/scripts/"*.sh 2>/dev/null || true
echo "Reload Cursor: Cmd+Shift+P → Developer: Reload Window"
