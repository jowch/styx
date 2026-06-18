#!/usr/bin/env bash
# Cursor spawns this via mcp.json. Ensures Julia env + PlutoMCP bridge, then stdio-proxies.
set -euo pipefail

PLUGIN_ROOT="${CURSOR_PLUGIN_ROOT:-$(cd "$(dirname "$0")/.." && pwd)}"
# shellcheck source=load-env-dev.sh
source "$(dirname "$0")/load-env-dev.sh"
load_env_dev "$PLUGIN_ROOT"

MCP_PORT="${PLUTOMCP_MCP_PORT:-2346}"
PLUTO_PORT="${PLUTOMCP_PLUTO_PORT:-1234}"
JULIA="${JULIA:-julia}"

"${PLUGIN_ROOT}/scripts/ensure-julia-env.sh"

health_ok() {
  curl -sf --max-time 2 "http://127.0.0.1:${MCP_PORT}/health" >/dev/null 2>&1
}

julia_cmd() {
  "$JULIA" --project="$PLUGIN_ROOT" "$@"
}

if ! health_ok; then
  LOG="${TMPDIR:-/tmp}/plutomcp-serve.log"
  echo "PlutoMCP bridge not detected on :${MCP_PORT}; starting serve() (log: ${LOG})" >&2
  julia_cmd -e \
    "using PlutoMCP; PlutoMCP.serve(pluto_port=${PLUTO_PORT}, mcp_port=${MCP_PORT}, launch_browser=false, require_secret_for_access=false)" \
    >>"$LOG" 2>&1 &
  for _ in $(seq 1 90); do
    health_ok && break
    sleep 1
  done
  if ! health_ok; then
    echo "PlutoMCP bridge failed to start within 90s. Check ${LOG}" >&2
    exit 1
  fi
fi

exec "$JULIA" --project="$PLUGIN_ROOT" -e \
  "using PlutoMCP; PlutoMCP.connect(pluto_port=${PLUTO_PORT}, mcp_port=${MCP_PORT}, require_secret_for_access=false)"
