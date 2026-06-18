#!/usr/bin/env bash
# Start PlutoMCP serve() in the background (on-demand Pluto + MCP bridge).
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

if health_ok; then
  echo "PlutoMCP already running — Pluto: http://127.0.0.1:${PLUTO_PORT}  MCP: http://127.0.0.1:${MCP_PORT}"
  exit 0
fi

LOG="${TMPDIR:-/tmp}/plutomcp-serve.log"
echo "Starting PlutoMCP serve() (log: ${LOG})" >&2
"$JULIA" --project="$PLUGIN_ROOT" -e \
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

echo "PlutoMCP ready — Pluto: http://127.0.0.1:${PLUTO_PORT}  MCP: http://127.0.0.1:${MCP_PORT}"
