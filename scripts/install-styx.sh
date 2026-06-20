#!/usr/bin/env bash
# Install or update Styx under ~/.cursor/plugins/local/styx/ (Cursor 3 local plugin).
set -euo pipefail

REPO="${STYX_REPO:-jowch/styx}"
REF="${STYX_REF:-main}"
DEST="${STYX_DEST:-${HOME}/.cursor/plugins/local/styx}"
SRC=""
FROM_DEV=0

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
# shellcheck source=lib/copy-plugin-tree.sh
source "${SCRIPT_DIR}/lib/copy-plugin-tree.sh"

usage() {
  cat <<EOF
Usage: install-styx.sh [options]

Options:
  --src PATH   Install from a local tree (dev); default clones from GitHub
  -h, --help   Show this help

Environment:
  STYX_REPO   GitHub repo (default: jowch/styx)
  STYX_REF    Branch or tag (default: main)
  STYX_DEST   Install path (default: ~/.cursor/plugins/local/styx)

Install docs: skills/styx-setup/reference/install.md (in repo) or README on GitHub.
EOF
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --src)
      SRC="${2:?--src requires a path}"
      FROM_DEV=1
      shift 2
      ;;
    --update) shift ;; # ponytail: no-op; update.sh wrapper only
    -h|--help) usage; exit 0 ;;
    *) echo "Unknown option: $1" >&2; usage >&2; exit 1 ;;
  esac
done

need() {
  command -v "$1" >/dev/null || {
    echo "Styx install: missing required command: $1" >&2
    exit 1
  }
}

need tar
need chmod

TMP=""
cleanup() {
  if [[ -n "$TMP" && -d "$TMP" ]]; then
    rm -rf "$TMP"
  fi
}
trap cleanup EXIT

if [[ "$FROM_DEV" -eq 0 ]]; then
  need git
  TMP="$(mktemp -d)"
  echo "Cloning ${REPO}@${REF}..."
  git clone --depth 1 --branch "$REF" "https://github.com/${REPO}.git" "$TMP"
  SRC="$TMP"
else
  SRC="$(cd "$SRC" && pwd)"
fi

if [[ ! -f "${SRC}/.cursor-plugin/plugin.json" ]]; then
  echo "Styx install: missing ${SRC}/.cursor-plugin/plugin.json" >&2
  exit 1
fi

mkdir -p "$(dirname "$DEST")"

echo "Installing Styx → ${DEST}"
copy_plugin_tree "$SRC" "$DEST" 1

chmod +x "${DEST}/scripts/"*.sh "${DEST}/hooks/"*.sh 2>/dev/null || true

if ! "${DEST}/scripts/check-julia.sh"; then
  echo
  echo "Styx is installed but Julia is required before MCP will work."
  exit 1
fi

cat <<EOF

Styx installed: ${DEST}

Next: Reload Window → Settings → MCP → enable **pluto** → "Run Styx doctor"
Uninstall: Settings → Plugins → Installed → Styx → Uninstall (see install.md)

EOF
exit 0
