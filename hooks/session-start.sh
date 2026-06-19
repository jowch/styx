#!/usr/bin/env bash
# Clear per-session read receipts (edit guard scopes to current chat).
set -euo pipefail

ROOT="${CURSOR_PLUGIN_ROOT:-$(cd "$(dirname "$0")/.." && pwd)}"
python3 -c "import sys; sys.path.insert(0, '${ROOT}/hooks'); from pluto_lib import clear_reads" 2>/dev/null || true
echo '{}'
