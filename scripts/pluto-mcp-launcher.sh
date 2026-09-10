#!/usr/bin/env bash
# Cursor spawns this via mcp.json — deferred Pluto (D15): stdio MCP up; Pluto on start_pluto_session.
# Bound mode: one Cursor window (VSCODE_PID) → one owned PlutoMCP session.
set -euo pipefail

PLUGIN_ROOT="${CURSOR_PLUGIN_ROOT:-$(cd "$(dirname "$0")/.." && pwd)}"
# shellcheck source=load-env-dev.sh
source "$(dirname "$0")/load-env-dev.sh"
load_env_dev "$PLUGIN_ROOT"

if [[ -z "${VSCODE_PID:-}" ]] || ! [[ "${VSCODE_PID}" =~ ^[0-9]+$ ]]; then
  echo "styx_identity_unavailable::VSCODE_PID is unavailable; refusing shared-port fallback. Reload the Cursor window and re-enable the pluto MCP server." >&2
  exit 1
fi

# Host-local runtime root shared by all Styx windows on this machine (notebook leases).
if [[ -n "${STYX_RUNTIME_DIR:-}" ]]; then
  RUNTIME_DIR="${STYX_RUNTIME_DIR}"
elif [[ -n "${XDG_RUNTIME_DIR:-}" ]]; then
  RUNTIME_DIR="${XDG_RUNTIME_DIR}/styx-${UID:-$(id -u)}"
else
  RUNTIME_DIR="${TMPDIR:-/tmp}/styx-${UID:-$(id -u)}"
fi
mkdir -p "${RUNTIME_DIR}/windows" "${RUNTIME_DIR}/notebooks" "${RUNTIME_DIR}/sessions"
BINDING_FILE="${RUNTIME_DIR}/windows/${VSCODE_PID}.json"
export STYX_RUNTIME_DIR="${RUNTIME_DIR}"
export STYX_BINDING_FILE="${BINDING_FILE}"

# Hints only — bound connect() uses listenany.
MCP_PORT_HINT="${PLUTOMCP_MCP_PORT:-2346}"
PLUTO_PORT_HINT="${PLUTOMCP_PLUTO_PORT:-1234}"
JULIA="${JULIA:-julia}"

"${PLUGIN_ROOT}/scripts/check-julia.sh"
"${PLUGIN_ROOT}/scripts/ensure-julia-env.sh"

exec "$JULIA" --project="$PLUGIN_ROOT" -e "
using PlutoMCP
PlutoMCP.connect(
    binding_file=ENV[\"STYX_BINDING_FILE\"],
    runtime_dir=ENV[\"STYX_RUNTIME_DIR\"],
    cursor_host_pid=parse(Int, ENV[\"VSCODE_PID\"]),
    pluto_port_hint=parse(Int, get(ENV, \"PLUTOMCP_PLUTO_PORT\", \"${PLUTO_PORT_HINT}\")),
    mcp_port_hint=parse(Int, get(ENV, \"PLUTOMCP_MCP_PORT\", \"${MCP_PORT_HINT}\")),
    require_secret_for_access=false,
)
"
