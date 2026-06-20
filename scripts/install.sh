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

CORE_URL="https://raw.githubusercontent.com/${REPO}/${REF}/scripts/install-styx.sh"
echo "Fetching install-styx.sh from ${REPO}@${REF}..."
curl -fsSL "$CORE_URL" -o "${TMP}/install-styx.sh"
chmod +x "${TMP}/install-styx.sh"
exec bash "${TMP}/install-styx.sh" "$@"
