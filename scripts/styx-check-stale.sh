#!/usr/bin/env bash
# Report-only stale Styx state. Exit 0=clean, 1=stale, 2=error.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")" && pwd)"
export PYTHONPATH="${ROOT}/lib${PYTHONPATH:+:$PYTHONPATH}"
# Window key helper lives in hooks/
export PYTHONPATH="${ROOT}/../hooks:${PYTHONPATH}"
exec python3 "${ROOT}/styx-check-stale.py" "$@"
