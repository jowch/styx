#!/usr/bin/env bash
# Regenerate plugin-root Manifest.toml (commit for marketplace reproducible installs).
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
"${ROOT}/scripts/check-julia.sh"
rm -f "${ROOT}/.julia-env-instantiated"
PLUTOMCP_ENV_FORCE=1 "${ROOT}/scripts/ensure-julia-env.sh"
echo "Wrote ${ROOT}/Manifest.toml — commit with Project.toml when deps change."
