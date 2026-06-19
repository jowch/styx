#!/usr/bin/env bash
# Pluto lifecycle preflight — ports, plugin files, optional session status.
set -euo pipefail

PLUGIN_ROOT="${CURSOR_PLUGIN_ROOT:-$(cd "$(dirname "$0")/.." && pwd)}"
MCP_PORT="${PLUTOMCP_MCP_PORT:-2346}"
PLUTO_PORT="${PLUTOMCP_PLUTO_PORT:-1234}"

EXPECT_RUNNING=0
REQUIRE_PORTS_FREE=0
NOTEBOOK_ID=""

usage() {
  cat <<EOF
Usage: $(basename "$0") [OPTIONS]

Check deferred-lifecycle preconditions (ports + optional MCP status).

Options:
  --expect-running       Fail if :2346 bridge is down (use after start_pluto_session)
  --require-ports-free   Fail if :2346 or :1234 are in use (for validate-pluto-lifecycle.sh)
  --notebook-id UUID     After --expect-running, verify notebook appears in status
  -h, --help             Show this help

Examples:
  $(basename "$0")                              # informational port check
  $(basename "$0") --require-ports-free         # before validate-pluto-lifecycle.sh
  $(basename "$0") --expect-running             # after agent start_pluto_session
  $(basename "$0") --expect-running --notebook-id <uuid>
EOF
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --expect-running) EXPECT_RUNNING=1; shift ;;
    --require-ports-free) REQUIRE_PORTS_FREE=1; shift ;;
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

echo "=== Pluto lifecycle preflight ==="
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

bridge_up=0
pluto_up=0
if health_ok; then
  bridge_up=1
  echo "OK  MCP bridge :${MCP_PORT}/health"
else
  echo "—   MCP bridge :${MCP_PORT}/health (down)"
fi

if pluto_ui_up; then
  pluto_up=1
  echo "OK  Pluto UI   :${PLUTO_PORT}/"
else
  echo "—   Pluto UI   :${PLUTO_PORT}/ (down)"
fi

if [[ "$REQUIRE_PORTS_FREE" -eq 1 ]]; then
  if [[ "$bridge_up" -eq 1 || "$pluto_up" -eq 1 ]]; then
    echo "FAIL :${MCP_PORT} or :${PLUTO_PORT} in use." >&2
    echo "     Toggle pluto MCP off in Cursor Settings (or stop pluto-serve.sh) and retry." >&2
    fail=1
  else
    echo "OK  ports free (:${MCP_PORT}, :${PLUTO_PORT})"
  fi
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
elif [[ "$REQUIRE_PORTS_FREE" -eq 0 ]]; then
  if [[ "$bridge_up" -eq 1 ]]; then
    echo "NOTE bridge already up (Cursor pluto MCP or dev serve?)"
  else
    echo "OK  deferred baseline (bridge down; Cursor stdio MCP may still be up)"
  fi
fi

echo
if [[ "$fail" -eq 0 ]]; then
  echo "Preflight passed."
  exit 0
fi
echo "Preflight failed." >&2
exit 1
