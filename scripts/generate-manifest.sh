#!/usr/bin/env bash
# Regenerate local Manifest.toml (gitignored; optional lockfile for dev).
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
"${ROOT}/scripts/check-julia.sh"
rm -f "${ROOT}/.julia-env-instantiated"
PLUTOMCP_ENV_FORCE=1 "${ROOT}/scripts/ensure-julia-env.sh"
echo "Wrote ${ROOT}/Manifest.toml (local only; fork source is Project.toml [sources])."
