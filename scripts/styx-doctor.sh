#!/usr/bin/env bash
# Quick install / runtime checks for Styx (agent or user). Exits non-zero on hard blockers.
set -euo pipefail

PLUGIN_ROOT="${CURSOR_PLUGIN_ROOT:-$(cd "$(dirname "$0")/.." && pwd)}"
MCP_PORT="${PLUTOMCP_MCP_PORT:-2346}"
PLUTO_PORT="${PLUTOMCP_PLUTO_PORT:-1234}"
FAIL=0

say_ok() { echo "OK  $*"; }
say_warn() { echo "WARN  $*"; }
say_fail() { echo "FAIL  $*"; FAIL=1; }

echo "Styx doctor (plugin: ${PLUGIN_ROOT})"
echo

if "${PLUGIN_ROOT}/scripts/check-julia.sh"; then
  say_ok "Julia $( "${JULIA:-julia}" --version 2>&1 | sed 's/^julia version //' )"
else
  say_fail "Julia missing or too old — see messages above"
fi

if [[ -f "${PLUGIN_ROOT}/Project.toml" ]]; then
  say_ok "Plugin Julia project (Project.toml)"
else
  say_fail "Missing Project.toml in plugin root"
fi

if [[ -f "${PLUGIN_ROOT}/.julia-env-instantiated" ]] && command -v "${JULIA:-julia}" >/dev/null 2>&1; then
  if "${JULIA:-julia}" --project="$PLUGIN_ROOT" -e 'using PlutoMCP' >/dev/null 2>&1; then
    say_ok "PlutoMCP env ready"
  else
    say_warn "PlutoMCP env incomplete — re-enable **pluto** MCP or delete .julia-env-instantiated"
    FAIL=1
  fi
else
  say_ok "PlutoMCP not installed yet — normal until first **pluto** MCP connect"
fi

if command -v curl >/dev/null 2>&1; then
  if curl -sf --max-time 2 "http://127.0.0.1:${MCP_PORT}/health" >/dev/null 2>&1; then
    say_ok "MCP bridge listening on :${MCP_PORT}"
  else
    say_ok "MCP bridge not running on :${MCP_PORT} (normal until notebook work or MCP connects)"
  fi
else
  say_warn "curl not found — skipped MCP health probe"
fi

if command -v lsof >/dev/null 2>&1; then
  for port in "$PLUTO_PORT" "$MCP_PORT"; do
    if lsof -nP -iTCP:"$port" -sTCP:LISTEN >/dev/null 2>&1; then
      say_ok "Port :${port} in use (Pluto session or MCP may be up)"
    fi
  done
fi

echo
if [[ "$FAIL" -eq 0 ]]; then
  echo "Doctor: ready for notebook work (enable **pluto** MCP if not already)."
  exit 0
fi
echo "Doctor: fix FAIL items, then Reload Window and retry."
exit 1
