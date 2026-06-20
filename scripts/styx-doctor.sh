#!/usr/bin/env bash
# Quick install / runtime checks for Styx (agent or user). Exits non-zero on hard blockers.
set -euo pipefail

PLUGIN_ROOT="${CURSOR_PLUGIN_ROOT:-$(cd "$(dirname "$0")/.." && pwd)}"
MCP_PORT="${PLUTOMCP_MCP_PORT:-2346}"
PLUTO_PORT="${PLUTOMCP_PLUTO_PORT:-1234}"
STYX_REPO="${STYX_REPO:-jowch/styx}"
CHECK_UPDATES=0
FAIL=0

# shellcheck source=lib/port-probe.sh
source "$(cd "$(dirname "$0")" && pwd)/lib/port-probe.sh"

say_ok() { echo "OK  $*"; }
say_warn() { echo "WARN  $*"; }
say_fail() { echo "FAIL  $*"; FAIL=1; }

usage() {
  cat <<'EOF'
Usage: styx-doctor.sh [--check-updates]

  --check-updates   Compare installed plugin.json version to latest GitHub release
EOF
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --check-updates) CHECK_UPDATES=1; shift ;;
    -h|--help) usage; exit 0 ;;
    *) echo "Unknown option: $1" >&2; usage >&2; exit 1 ;;
  esac
done

# ponytail: strip optional leading v for semver-ish compare via sort -V
normalize_version() {
  echo "${1#v}"
}

read_plugin_version() {
  local manifest="$1"
  sed -n 's/^[[:space:]]*"version"[[:space:]]*:[[:space:]]*"\([^"]*\)".*/\1/p' "$manifest" | head -1
}

check_updates() {
  local manifest="${PLUGIN_ROOT}/.cursor-plugin/plugin.json"
  local installed latest api_url

  if [[ ! -f "$manifest" ]]; then
    say_warn "Update check skipped — missing .cursor-plugin/plugin.json"
    return
  fi
  if ! command -v curl >/dev/null 2>&1; then
    say_warn "Update check skipped — curl not found"
    return
  fi

  installed="$(read_plugin_version "$manifest")"
  if [[ -z "$installed" ]]; then
    say_warn "Update check skipped — could not read installed version"
    return
  fi

  latest=""
  api_url="https://api.github.com/repos/${STYX_REPO}/releases/latest"
  if raw="$(curl -sf --max-time 8 -H "Accept: application/vnd.github+json" "$api_url" 2>/dev/null)"; then
    latest="$(echo "$raw" | sed -n 's/^[[:space:]]*"tag_name"[[:space:]]*:[[:space:]]*"\([^"]*\)".*/\1/p' | head -1)"
  fi

  if [[ -z "$latest" ]]; then
    if raw="$(curl -sf --max-time 8 \
      "https://raw.githubusercontent.com/${STYX_REPO}/main/.cursor-plugin/plugin.json" 2>/dev/null)"; then
      latest="$(echo "$raw" | sed -n 's/^[[:space:]]*"version"[[:space:]]*:[[:space:]]*"\([^"]*\)".*/\1/p' | head -1)"
    fi
  fi

  if [[ -z "$latest" ]]; then
    say_warn "Update check skipped — could not reach GitHub (no release or network)"
    return
  fi

  if [[ "$(normalize_version "$installed")" == "$(normalize_version "$latest")" ]]; then
    say_ok "Styx up to date (${installed})"
    return
  fi

  if [[ "$(printf '%s\n' "$(normalize_version "$installed")" "$(normalize_version "$latest")" | sort -V | tail -1)" == "$(normalize_version "$installed")" ]]; then
    say_ok "Styx ${installed} (latest release: ${latest})"
    return
  fi

  say_warn "Update available: installed ${installed}, latest ${latest}"
  echo "      Re-run: curl -fsSL https://raw.githubusercontent.com/${STYX_REPO}/main/scripts/install.sh | bash"
  echo "      Or: STYX_REF=${latest} curl -fsSL https://raw.githubusercontent.com/${STYX_REPO}/main/scripts/install.sh | bash"
}

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
  if mcp_health_ok; then
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
elif command -v curl >/dev/null 2>&1 && pluto_ui_ok; then
  say_ok "Port :${PLUTO_PORT} in use (Pluto UI responding)"
fi

if [[ "$CHECK_UPDATES" -eq 1 ]]; then
  echo
  check_updates
fi

echo
if [[ "$FAIL" -eq 0 ]]; then
  echo "Doctor: ready for notebook work (enable **pluto** MCP if not already)."
  exit 0
fi
echo "Doctor: fix FAIL items, then Reload Window and retry."
exit 1
