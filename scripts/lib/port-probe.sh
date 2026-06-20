# Shared loopback health probes for styx-doctor and pluto-lifecycle-preflight.
# shellcheck shell=bash

mcp_health_ok() {
  local port="${MCP_PORT:-2346}"
  curl -sf --max-time 2 "http://127.0.0.1:${port}/health" >/dev/null 2>&1
}

pluto_ui_ok() {
  local port="${PLUTO_PORT:-1234}"
  curl -sf --max-time 2 -o /dev/null "http://127.0.0.1:${port}/" 2>/dev/null
}
