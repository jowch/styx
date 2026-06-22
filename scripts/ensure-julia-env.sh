#!/usr/bin/env bash
# Bootstrap plugin-root Julia env (Project.toml). Idempotent; runs before MCP launcher.
set -euo pipefail

PLUGIN_ROOT="${CURSOR_PLUGIN_ROOT:-$(cd "$(dirname "$0")/.." && pwd)}"
# shellcheck source=load-env-dev.sh
source "$(dirname "$0")/load-env-dev.sh"
load_env_dev "$PLUGIN_ROOT"

JULIA="${JULIA:-julia}"
MARKER="${PLUGIN_ROOT}/.julia-env-instantiated"

"${PLUGIN_ROOT}/scripts/check-julia.sh"

if [[ ! -f "${PLUGIN_ROOT}/Project.toml" ]]; then
  echo "Missing ${PLUGIN_ROOT}/Project.toml" >&2
  exit 1
fi

resolve_local_plutomcp() {
  if [[ -n "${PLUTOMCP_SOURCE:-}" && -f "${PLUTOMCP_SOURCE}/Project.toml" ]]; then
    printf '%s' "${PLUTOMCP_SOURCE}"
    return 0
  fi
  local sibling="${PLUGIN_ROOT}/../PlutoMCP.jl"
  if [[ -f "${sibling}/Project.toml" ]]; then
    printf '%s' "${sibling}"
    return 0
  fi
  return 1
}

if [[ -f "$MARKER" && "${PLUTOMCP_ENV_FORCE:-}" != "1" ]]; then
  if "$JULIA" --project="$PLUGIN_ROOT" -e 'using PlutoMCP' >/dev/null 2>&1; then
    exit 0
  fi
fi

LOCAL=""
if LOCAL="$(resolve_local_plutomcp)"; then
  echo "Pluto MCP env: developing local PlutoMCP at ${LOCAL}" >&2
else
  echo "Styx: first MCP connect — installing PlutoMCP (network; may take several minutes)…" >&2
fi

PLUTOMCP_LOCAL="${LOCAL}" "$JULIA" --project="$PLUGIN_ROOT" -e '
using Pkg, TOML
local_path = get(ENV, "PLUTOMCP_LOCAL", "")
project_file = Base.active_project()
project = TOML.parsefile(project_file)
saved = deepcopy(project)
try
    if !isempty(local_path) && isdir(local_path)
        # url and path cannot coexist in [sources]; swap to path for resolve, restore after.
        project["sources"]["PlutoMCP"] = Dict("path" => local_path)
        open(project_file, "w") do io
            TOML.print(io, project)
        end
    end
    Pkg.resolve()
    Pkg.instantiate()
finally
    if !isempty(local_path) && isdir(local_path)
        open(project_file, "w") do io
            TOML.print(io, saved)
        end
    end
end
'

touch "$MARKER"
