#!/usr/bin/env bash
# Session start guidance. Read receipts are session-scoped under STYX_RUNTIME_DIR.
set -euo pipefail

if [[ "${CURSOR_CODE_REMOTE:-}" == "true" ]]; then
  python3 -c 'import json; print(json.dumps({"additional_context": "Remote SSH workspace. This Cursor window owns its own Styx/PlutoMCP/Pluto on the SSH host (local XOR remote). Use pluto_session_status.pluto_url for Glass — Cursor auto-forwards ports; if remapped, use the Ports panel URL. Do not probe fixed :1234/:2346. See pluto-session remote-ssh.md."}))'
else
  echo '{}'
fi
