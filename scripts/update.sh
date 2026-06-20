#!/usr/bin/env bash
# Re-fetch and sync Styx into ~/.cursor/plugins/local/styx/ (preserves Julia env marker).
set -euo pipefail
ROOT="$(cd "$(dirname "$0")" && pwd)"
exec bash "${ROOT}/install-styx.sh" --update "$@"
