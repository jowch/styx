#!/usr/bin/env bash
# Inject static Pluto MCP workflow hints at session start.
set -euo pipefail

ROOT="${CURSOR_PLUGIN_ROOT:-$(cd "$(dirname "$0")/.." && pwd)}"
PREFIX="${ROOT}/eval/PLUTO_WORKFLOW_PREFIX.md"

# Fresh read receipts each agent session (edit guard scopes to current chat).
python3 -c "import sys; sys.path.insert(0, '${ROOT}/hooks'); from pluto_lib import clear_reads; clear_reads()" 2>/dev/null || true

escape_for_json() {
  local s="$1"
  s="${s//\\/\\\\}"
  s="${s//\"/\\\"}"
  s="${s//$'\n'/\\n}"
  s="${s//$'\r'/\\r}"
  s="${s//$'\t'/\\t}"
  printf '%s' "$s"
}

if [[ ! -f "$PREFIX" ]]; then
  echo '{}'
  exit 0
fi

content=$(cat "$PREFIX")
escaped=$(escape_for_json "$content")
printf '{\n  "additional_context": "%s"\n}\n' "$escaped"
exit 0
