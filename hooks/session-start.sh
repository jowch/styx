#!/usr/bin/env bash
# Session start guidance. Read receipts are session-scoped under STYX_RUNTIME_DIR.
set -euo pipefail

if [[ "${CURSOR_CODE_REMOTE:-}" == "true" ]]; then
  python3 -c 'import json; print(json.dumps({"additional_context": "Remote SSH workspace. This Cursor window owns its own Styx/PlutoMCP/Pluto on the SSH host (local XOR remote). MCP uses host pluto_url/pluto_port. Before Agents Glass this session: ask the user for the Cursor Ports forwarded/local port for that remote Pluto port; open http://127.0.0.1:<forwarded>/ — do not invent remaps or probe fixed :1234/:2346. See pluto-session glass-navigation.md / remote-ssh.md."}))'
else
  echo '{}'
fi
