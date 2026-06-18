#!/usr/bin/env bash
# Inject static Pluto MCP workflow hints at session start.
set -euo pipefail

ROOT="${CURSOR_PLUGIN_ROOT:-$(cd "$(dirname "$0")/.." && pwd)}"
PREFIX="${ROOT}/eval/PLUTO_WORKFLOW_PREFIX.md"

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
