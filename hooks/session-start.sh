#!/usr/bin/env bash
# Clear per-session read receipts (edit guard scopes to current chat).
set -euo pipefail

ROOT="${CURSOR_PLUGIN_ROOT:-$(cd "$(dirname "$0")/.." && pwd)}"
python3 -c "import sys; sys.path.insert(0, '${ROOT}/hooks'); from pluto_lib import clear_reads" 2>/dev/null || true

if [[ "${CURSOR_CODE_REMOTE:-}" == "true" ]]; then
  python3 -c 'import json; print(json.dumps({"additional_context": "Remote SSH workspace. Start Pluto on the SSH host (workspace files), not on the laptop. Cursor auto-forwards ports — Glass is http://127.0.0.1:1234/ or the Ports panel URL if remapped. See pluto-session remote-ssh.md."}))'
else
  echo '{}'
fi
