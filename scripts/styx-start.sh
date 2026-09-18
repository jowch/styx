#!/usr/bin/env bash
# styx-start — thin wrapper around scripts/styx-start.py
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
export PYTHONPATH="${ROOT}/hooks${PYTHONPATH:+:${PYTHONPATH}}"
exec python3 "${ROOT}/scripts/styx-start.py" "$@"
