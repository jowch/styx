#!/usr/bin/env bash
# Sideload the styx-ports Extension Host companion (issue #15 spike).
# Run on the machine where the Cursor extension host lives (Remote SSH host when remote).
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
SRC="${STYX_PORTS_SRC:-${ROOT}/extensions/styx-ports}"

if [[ ! -f "${SRC}/package.json" || ! -f "${SRC}/extension.js" ]]; then
  echo "install-styx-ports: missing ${SRC}/package.json or extension.js" >&2
  exit 1
fi

VERSION="$(python3 -c 'import json,sys; print(json.load(open(sys.argv[1]))["version"])' "${SRC}/package.json")"
EXT_ID="jowch.styx-ports-${VERSION}"

# Prefer cursor-server (Remote SSH EH) when present; else local Cursor extensions.
if [[ -d "${HOME}/.cursor-server" ]] || [[ "${CURSOR_CODE_REMOTE:-}" == "true" ]]; then
  DEST_ROOT="${HOME}/.cursor-server/extensions"
elif [[ -d "${HOME}/.vscode-server" ]]; then
  DEST_ROOT="${HOME}/.vscode-server/extensions"
else
  DEST_ROOT="${HOME}/.cursor/extensions"
fi

mkdir -p "${DEST_ROOT}"
DEST="${DEST_ROOT}/${EXT_ID}"
TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT

# Fresh copy (no symlink — Cursor often rejects external links).
mkdir -p "${TMP}/${EXT_ID}"
cp -R "${SRC}/." "${TMP}/${EXT_ID}/"
rm -rf "${DEST}"
mv "${TMP}/${EXT_ID}" "${DEST}"

echo "Installed Styx Ports spike → ${DEST}"
echo "Reload Window in an Editor / Open IDE remote window (agent-exec EH does not load user extensions)."
echo "Confirm Styx Ports under remote Extensions, then: Styx: Resolve Pluto Client URL (or wait for binding-scan watcher)."
