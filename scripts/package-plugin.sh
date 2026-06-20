#!/usr/bin/env bash
# Build a release-shaped plugin tree (excludes dev-only artifacts).
set -euo pipefail

SRC="$(cd "$(dirname "$0")/.." && pwd)"
DEST="${1:-${SRC}/dist/styx}"
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

# shellcheck source=lib/copy-plugin-tree.sh
source "${SCRIPT_DIR}/lib/copy-plugin-tree.sh"

mkdir -p "$(dirname "${DEST}")"
copy_plugin_tree "$SRC" "$DEST" 0

chmod +x "${DEST}/scripts/"*.sh "${DEST}/hooks/"*.sh 2>/dev/null || true

echo "Release tree: ${DEST}"
echo "Install: curl -fsSL https://raw.githubusercontent.com/jowch/styx/main/scripts/install.sh | bash"
