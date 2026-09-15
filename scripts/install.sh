#!/usr/bin/env bash
# Curl entrypoint: bash <(curl -fsSL https://raw.githubusercontent.com/jowch/styx/main/scripts/install.sh)
set -euo pipefail

REPO="${STYX_REPO:-jowch/styx}"
REF="${STYX_REF:-}"
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

# Default: latest GitHub Release. STYX_REF=main installs the development tip.
latest_release() {
  curl -fsSL --max-time 10 "https://api.github.com/repos/${REPO}/releases/latest" \
    | sed -n 's/^[[:space:]]*"tag_name"[[:space:]]*:[[:space:]]*"\([^"]*\)".*/\1/p' | head -1
}
if [[ -z "$REF" ]]; then
  REF="$(latest_release)" || true
  [[ -n "$REF" ]] || { echo "Styx install: could not resolve the latest release; set STYX_REF (a tag, or main)." >&2; exit 1; }
fi
export STYX_REF="$REF"

BASE="https://raw.githubusercontent.com/${REPO}/${REF}/scripts"
echo "Fetching install scripts from ${REPO}@${REF}..."
mkdir -p "${TMP}/lib"
curl -fsSL "${BASE}/install-styx.sh" -o "${TMP}/install-styx.sh"
curl -fsSL "${BASE}/lib/copy-plugin-tree.sh" -o "${TMP}/lib/copy-plugin-tree.sh"
chmod +x "${TMP}/install-styx.sh"
exec bash "${TMP}/install-styx.sh" "$@"
