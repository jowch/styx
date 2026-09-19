#!/usr/bin/env bash
# Reclaim stale Styx-managed crumbs. Requires --apply. Report-only → styx-check-stale.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")" && pwd)"
export PYTHONPATH="${ROOT}/lib${PYTHONPATH:+:$PYTHONPATH}"
export PYTHONPATH="${ROOT}/../hooks:${PYTHONPATH}"
exec python3 "${ROOT}/styx-cleanup.py" "$@"
