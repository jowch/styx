#!/usr/bin/env bash
# D15 lifecycle preflight — check ports and optional pluto_session_status via HTTP bridge.
set -euo pipefail

PLUGIN_ROOT="${CURSOR_PLUGIN_ROOT:-$(cd "$(dirname "$0")/.." && pwd)}"
MCP_PORT="${PLUTOMCP_MCP_PORT:-2346}"
PLUTO_PORT="${PLUTOMCP_PLUTO_PORT:-1234}"

EXPECT_RUNNING=0
NOTEBOOK_ID=""

usage() {
  cat <<EOF
Usage: $(basename "$0") [OPTIONS]

Check D15 deferred-lifecycle preconditions (ports + optional MCP status).

Options:
  --expect-running       Fail if :2346 bridge is down (use after start_pluto_session)
  --notebook-id UUID     After --expect-running, verify notebook appears in status
  -h, --help             Show this help

Examples:
  $(basename "$0")                              # baseline: bridge should be down
  $(basename "$0") --expect-running             # after agent start_pluto_session
  $(basename "$0") --expect-running --notebook-id <uuid>
EOF
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --expect-running) EXPECT_RUNNING=1; shift ;;
    --notebook-id) NOTEBOOK_ID="${2:?--notebook-id requires UUID}"; shift 2 ;;
    -h|--help) usage; exit 0 ;;
    *) echo "Unknown option: $1" >&2; usage >&2; exit 1 ;;
  esac
done

health_ok() {
  curl -sf --max-time 2 "http://127.0.0.1:${MCP_PORT}/health" >/dev/null 2>&1
}

pluto_ui_up() {
  curl -sf --max-time 2 -o /dev/null "http://127.0.0.1:${PLUTO_PORT}/" 2>/dev/null
}

mcp_call() {
  local name="$1"
  curl -sf --max-time 5 -X POST "http://127.0.0.1:${MCP_PORT}/call" \
    -H 'Content-Type: application/json' \
    -d "{\"jsonrpc\":\"2.0\",\"id\":1,\"method\":\"tools/call\",\"params\":{\"name\":\"${name}\",\"arguments\":{}}}"
}

echo "=== D15 preflight ==="
echo "Plugin root: ${PLUGIN_ROOT}"
echo "Pluto port:  ${PLUTO_PORT}"
echo "MCP port:    ${MCP_PORT}"
echo

fail=0

for f in "${PLUGIN_ROOT}/mcp.json" "${PLUGIN_ROOT}/scripts/pluto-mcp-launcher.sh"; do
  if [[ -f "$f" ]]; then
    echo "OK  file $(basename "$f")"
  else
    echo "FAIL missing $f" >&2
    fail=1
  fi
done

if health_ok; then
  echo "OK  MCP bridge :${MCP_PORT}/health"
else
  echo "—   MCP bridge :${MCP_PORT}/health (down)"
fi

if pluto_ui_up; then
  echo "OK  Pluto UI   :${PLUTO_PORT}/"
else
  echo "—   Pluto UI   :${PLUTO_PORT}/ (down)"
fi

if [[ "$EXPECT_RUNNING" -eq 1 ]]; then
  if ! health_ok; then
    echo "FAIL expected bridge up (--expect-running)" >&2
    fail=1
  else
  resp="$(mcp_call pluto_session_status || true)"
  if [[ -z "$resp" ]]; then
    echo "FAIL pluto_session_status HTTP call" >&2
    fail=1
  else
    pluto_state="$(printf '%s' "$resp" | python3 -c "
import json, sys
p = json.load(sys.stdin)
text = p.get('result', {}).get('content', [{}])[0].get('text', '{}')
d = json.loads(text)
print(d.get('pluto', '?'))
" 2>/dev/null || echo "?")"
    echo "OK  pluto_session_status → pluto=${pluto_state}"
    if [[ "$pluto_state" != "running" ]]; then
      echo "FAIL expected pluto=running" >&2
      fail=1
    fi
    if [[ -n "$NOTEBOOK_ID" ]]; then
      found="$(printf '%s' "$resp" | python3 -c "
import json, sys
p = json.load(sys.stdin)
text = p.get('result', {}).get('content', [{}])[0].get('text', '{}')
d = json.loads(text)
ids = [n.get('notebook_id') for n in d.get('notebooks', [])]
print('yes' if '${NOTEBOOK_ID}' in ids else 'no')
" 2>/dev/null || echo "no")"
      if [[ "$found" == "yes" ]]; then
        echo "OK  notebook ${NOTEBOOK_ID} in session"
      else
        echo "FAIL notebook ${NOTEBOOK_ID} not in pluto_session_status" >&2
        fail=1
      fi
    fi
  fi
  fi
else
  if health_ok; then
    echo "NOTE bridge already up (proxy/dev serve?) — baseline deferred test expects down"
  else
    echo "OK  deferred baseline (bridge down, MCP stdio may still be up in Cursor)"
  fi
fi

echo
if [[ "$fail" -eq 0 ]]; then
  echo "Preflight passed."
  exit 0
fi
echo "Preflight failed." >&2
exit 1
