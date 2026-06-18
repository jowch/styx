#!/usr/bin/env bash
# Cursor spawns this via mcp.json — deferred Pluto (D15): stdio MCP up; Pluto on start_pluto_session.
set -euo pipefail

PLUGIN_ROOT="${CURSOR_PLUGIN_ROOT:-$(cd "$(dirname "$0")/.." && pwd)}"
# shellcheck source=load-env-dev.sh
source "$(dirname "$0")/load-env-dev.sh"
load_env_dev "$PLUGIN_ROOT"

MCP_PORT="${PLUTOMCP_MCP_PORT:-2346}"
PLUTO_PORT="${PLUTOMCP_PLUTO_PORT:-1234}"
JULIA="${JULIA:-julia}"

"${PLUGIN_ROOT}/scripts/ensure-julia-env.sh"

exec "$JULIA" --project="$PLUGIN_ROOT" -e \
  "using PlutoMCP; PlutoMCP.connect(pluto_port=${PLUTO_PORT}, mcp_port=${MCP_PORT}, require_secret_for_access=false)"
