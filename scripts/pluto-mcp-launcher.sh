#!/usr/bin/env bash
# Cursor spawns this via mcp.json — deferred Pluto (D15): stdio MCP up; Pluto on start_pluto_session.
# Bound mode: one Cursor window → one owned PlutoMCP session.
# Identity: VSCODE_PID when numeric; else hash(basename(VSCODE_IPC_HOOK_CLI)) → Int.
set -euo pipefail

PLUGIN_ROOT="${CURSOR_PLUGIN_ROOT:-$(cd "$(dirname "$0")/.." && pwd)}"
export CURSOR_PLUGIN_ROOT="${PLUGIN_ROOT}"
# shellcheck source=load-env-dev.sh
source "$(dirname "$0")/load-env-dev.sh"
load_env_dev "$PLUGIN_ROOT"
# shellcheck source=lib/styx-window-key.sh
source "$(dirname "$0")/lib/styx-window-key.sh"

if ! resolve_styx_window_key >/dev/null; then
  echo "styx_identity_unavailable::need VSCODE_PID or VSCODE_IPC_HOOK_CLI; refusing shared-port fallback. Reload the Cursor window and re-enable the pluto MCP server." >&2
  exit 1
fi
# resolve_styx_window_key sets STYX_WINDOW_KEY + STYX_WINDOW_KEY_SOURCE in this shell.
echo "styx_window_key::${STYX_WINDOW_KEY_SOURCE}=${STYX_WINDOW_KEY}" >&2

# Host-local runtime root shared by all Styx windows on this machine (notebook leases).
if [[ -n "${STYX_RUNTIME_DIR:-}" ]]; then
  RUNTIME_DIR="${STYX_RUNTIME_DIR}"
elif [[ -n "${XDG_RUNTIME_DIR:-}" ]]; then
  RUNTIME_DIR="${XDG_RUNTIME_DIR}/styx-${UID:-$(id -u)}"
else
  RUNTIME_DIR="${TMPDIR:-/tmp}/styx-${UID:-$(id -u)}"
fi
mkdir -p "${RUNTIME_DIR}/windows" "${RUNTIME_DIR}/notebooks" "${RUNTIME_DIR}/sessions"
BINDING_FILE="${RUNTIME_DIR}/windows/${STYX_WINDOW_KEY}.json"
export STYX_RUNTIME_DIR="${RUNTIME_DIR}"
export STYX_BINDING_FILE="${BINDING_FILE}"
export STYX_WINDOW_KEY

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
    cursor_host_pid=parse(Int, ENV[\"STYX_WINDOW_KEY\"]),
    pluto_port_hint=parse(Int, get(ENV, \"PLUTOMCP_PLUTO_PORT\", \"${PLUTO_PORT_HINT}\")),
    mcp_port_hint=parse(Int, get(ENV, \"PLUTOMCP_MCP_PORT\", \"${MCP_PORT_HINT}\")),
    require_secret_for_access=false,
)
"
