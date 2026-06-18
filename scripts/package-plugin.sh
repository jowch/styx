#!/usr/bin/env bash
# Build a release-shaped plugin tree (excludes dev-only artifacts).
set -euo pipefail

SRC="$(cd "$(dirname "$0")/.." && pwd)"
DEST="${1:-${SRC}/dist/styx}"

rm -rf "${DEST}"
mkdir -p "$(dirname "${DEST}")"

rsync -a \
  --exclude .git \
  --exclude .cursor \
  --exclude .github \
  --exclude .git-template \
  --exclude dist \
  --exclude eval \
  --exclude AGENTS.md \
  --exclude .env.dev \
  --exclude .env.dev.example \
  --exclude docs/PLAN.md \
  --exclude docs/DECISIONS.md \
  --exclude docs/dom-bridge-test-checklist.md \
  --exclude docs/spikes \
  --exclude docs/upstream \
  --exclude docs/specs/mcp-phase-1.md \
  --exclude docs/specs/mcp-phase-2.md \
  --exclude docs/specs/dom-bridge.md \
  --exclude docs/specs/cursor-plugin.md \
  --exclude scripts/sync-local-plugin.sh \
  --exclude scripts/package-plugin.sh \
  --exclude 'hooks/__pycache__' \
  --exclude Manifest.toml \
  --exclude .julia-env-instantiated \
  --exclude node_modules \
  "${SRC}/" "${DEST}/"

chmod +x "${DEST}/scripts/"*.sh "${DEST}/hooks/"*.sh 2>/dev/null || true

echo "Release tree: ${DEST}"
echo "Install manually to ~/.cursor/plugins/local/styx/ or publish via marketplace."
