#!/usr/bin/env bash
# Bootstrap the plugin Julia env (@pluto-mcp). Idempotent; runs before MCP launcher.
set -euo pipefail

PLUGIN_ROOT="${CURSOR_PLUGIN_ROOT:-$(cd "$(dirname "$0")/.." && pwd)}"
ENV_DIR="${PLUGIN_ROOT}/@pluto-mcp"
JULIA="${JULIA:-julia}"
MARKER="${ENV_DIR}/.instantiated"

if [[ ! -f "${ENV_DIR}/Project.toml" ]]; then
  echo "Missing ${ENV_DIR}/Project.toml" >&2
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
  if "$JULIA" --project="$ENV_DIR" -e 'using PlutoMCP' >/dev/null 2>&1; then
    exit 0
  fi
fi

LOCAL=""
if LOCAL="$(resolve_local_plutomcp)"; then
  echo "Pluto MCP env: developing local PlutoMCP at ${LOCAL}" >&2
else
  echo "Pluto MCP env: installing PlutoMCP from Project.toml [sources]" >&2
fi

PLUTOMCP_LOCAL="${LOCAL}" "$JULIA" --project="$ENV_DIR" -e '
using Pkg
local_path = get(ENV, "PLUTOMCP_LOCAL", "")
if !isempty(local_path) && isdir(local_path)
    Pkg.develop(PackageSpec(path=local_path))
else
    manifest = joinpath(dirname(Base.active_project()), "Manifest.toml")
    if !isfile(manifest)
        Pkg.add(PackageSpec(url="https://github.com/jowch/PlutoMCP.jl.git"))
    end
end
Pkg.instantiate()
'

touch "$MARKER"
