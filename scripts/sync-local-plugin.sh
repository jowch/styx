#!/usr/bin/env bash
# Dev: copy this repo into ~/.cursor/plugins/local/styx/ (Cursor 3 rejects external symlinks).
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
exec bash "${ROOT}/scripts/install-styx.sh" --src "$ROOT"
