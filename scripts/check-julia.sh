#!/usr/bin/env bash
# ponytail: PATH-only probe; does not resolve JULIAUP or custom install dirs beyond JULIA env.
# Exit 0 when Julia >= 1.9 is invocable; otherwise print install guidance and exit 1.
set -euo pipefail

JULIA="${JULIA:-julia}"
MIN_VERSION="1.9"

install_help() {
  cat >&2 <<'EOF'

Styx needs Julia 1.9+ on your PATH.

Install:
  • All platforms: https://julialang.org/downloads/
  • macOS (Homebrew): brew install julia
  • Windows: run the installer and enable "Add Julia to PATH"

Then:
  1. Verify in a terminal: julia --version
  2. In Cursor: Reload Window
  3. Settings → MCP → enable the **pluto** server (bundled with Styx)

First MCP connect downloads PlutoMCP.jl (one-time; needs network).
EOF
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
