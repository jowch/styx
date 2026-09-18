#!/usr/bin/env bash
# Inventory / clear stale Styx runtime crumbs. Dry-run unless --apply.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")" && pwd)"
exec python3 "${ROOT}/styx-cleanup.py" "$@"
