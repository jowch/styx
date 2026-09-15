#!/usr/bin/env bash
# Session start guidance. Do not wipe glass-views.json (or reads.json).
set -euo pipefail

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
python3 "${DIR}/session-start.py" || echo '{}'
