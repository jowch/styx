#!/usr/bin/env bash
# Preflight for lifecycle validation — no longer requires fixed ports free.
# shellcheck shell=bash
set -euo pipefail

REQUIRE_CLEAN=0
while [[ $# -gt 0 ]]; do
  case "$1" in
    --require-ports-free|--require-clean-runtime)
      REQUIRE_CLEAN=1
      shift
      ;;
    *)
      echo "Unknown option: $1" >&2
      exit 2
      ;;
  esac
done

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
# shellcheck source=lib/port-probe.sh
source "${ROOT}/scripts/lib/port-probe.sh"

if [[ "$REQUIRE_CLEAN" -eq 1 ]]; then
  if resolve_styx_window_key >/dev/null && load_styx_binding >/dev/null 2>&1 && mcp_health_ok; then
    echo "FAIL: live Styx binding for window key ${STYX_WINDOW_KEY} (${STYX_WINDOW_KEY_SOURCE}) — toggle pluto MCP off first" >&2
    exit 1
  fi
  echo "OK: no live binding for this window key (or identity unset)"
else
  echo "OK: preflight (binding-aware; fixed ports not required)"
fi
