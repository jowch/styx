#!/usr/bin/env bash
# Curl entrypoint: bash <(curl -fsSL https://raw.githubusercontent.com/jowch/styx/main/scripts/install.sh)
set -euo pipefail

REPO="${STYX_REPO:-jowch/styx}"
REF="${STYX_REF:-main}"
TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT

need() {
  command -v "$1" >/dev/null || {
    echo "Styx install: missing required command: $1" >&2
    exit 1
  }
}

need curl
need bash

BASE="https://raw.githubusercontent.com/${REPO}/${REF}/scripts"
echo "Fetching install scripts from ${REPO}@${REF}..."
mkdir -p "${TMP}/lib"
curl -fsSL "${BASE}/install-styx.sh" -o "${TMP}/install-styx.sh"
curl -fsSL "${BASE}/lib/copy-plugin-tree.sh" -o "${TMP}/lib/copy-plugin-tree.sh"
chmod +x "${TMP}/install-styx.sh"
exec bash "${TMP}/install-styx.sh" "$@"
