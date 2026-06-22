#!/usr/bin/env bash
# ponytail: PATH-only probe; does not resolve JULIAUP or custom install dirs beyond JULIA env.
# Exit 0 when Julia >= 1.11 is invocable; otherwise print install guidance and exit 1.
set -euo pipefail

JULIA="${JULIA:-julia}"
MIN_VERSION="1.11"

install_help() {
  echo "Styx needs Julia ${MIN_VERSION}+ on PATH — https://julialang.org/downloads/" >&2
  echo "Then Reload Window and enable **pluto** MCP. See styx-setup skill for full steps." >&2
}

if ! command -v "$JULIA" >/dev/null 2>&1; then
  echo "Styx: Julia not found (looked for: ${JULIA})." >&2
  install_help
  exit 1
fi

version_line="$("$JULIA" --version 2>&1)" || {
  echo "Styx: '${JULIA}' is on PATH but failed to run." >&2
  install_help
  exit 1
}

if ! "$JULIA" -e "using InteractiveUtils; VersionNumber(string(VERSION)) >= v\"${MIN_VERSION}\" || exit(1)" 2>/dev/null; then
  echo "Styx: Julia ${MIN_VERSION}+ required (found: ${version_line})." >&2
  install_help
  exit 1
fi
