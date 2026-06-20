#!/usr/bin/env bash
# Install or update Styx under ~/.cursor/plugins/local/styx/ (Cursor 3 local plugin).
set -euo pipefail

REPO="${STYX_REPO:-jowch/styx}"
REF="${STYX_REF:-main}"
DEST="${STYX_DEST:-${HOME}/.cursor/plugins/local/styx}"
SRC=""
FROM_DEV=0
ACTION=install

usage() {
  cat <<'EOF'
Usage: install-styx.sh [options]

Options:
  --src PATH     Install from a local tree (dev); default clones from GitHub
  --update       Same as default; kept for update.sh wrapper
  -h, --help     Show this help

Environment:
  STYX_REPO   GitHub repo (default: jowch/styx)
  STYX_REF    Branch or tag (default: main)
  STYX_DEST   Install path (default: ~/.cursor/plugins/local/styx)

One-liner (fresh install or update):
  curl -fsSL https://raw.githubusercontent.com/jowch/styx/main/scripts/install.sh | bash

Pin a release:
  STYX_REF=v0.1.0 curl -fsSL https://raw.githubusercontent.com/jowch/styx/main/scripts/install.sh | bash
EOF
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --src)
      SRC="${2:?--src requires a path}"
      FROM_DEV=1
      shift 2
      ;;
    --update) ACTION=update; shift ;;
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

need rsync
need chmod

TMP=""
cleanup() {
  [[ -n "$TMP" && -d "$TMP" ]] && rm -rf "$TMP"
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

# ponytail: P rules keep dest-only runtime files when --delete runs on update.
RSYNC_FILTERS=(
  --filter 'P .julia-env-instantiated'
  --filter 'P hooks/state/pluto-reads.json'
)

echo "$([[ "$ACTION" == update ]] && echo Updating || echo Installing) Styx → ${DEST}"

rsync -a --delete \
  "${RSYNC_FILTERS[@]}" \
  --exclude .git \
  --exclude .cursor \
  --exclude .github \
  --exclude .git-template \
  --exclude dist \
  --exclude eval \
  --exclude AGENTS.md \
  --exclude .env.dev \
  --exclude .env.dev.example \
  --exclude docs/PLAN.md \
  --exclude docs/DECISIONS.md \
  --exclude docs/spikes \
  --exclude docs/upstream \
  --exclude node_modules \
  --exclude 'hooks/__pycache__' \
  --exclude scripts/sync-local-plugin.sh \
  --exclude scripts/package-plugin.sh \
  "${SRC}/" "${DEST}/"

chmod +x "${DEST}/scripts/"*.sh "${DEST}/hooks/"*.sh 2>/dev/null || true

if ! "${DEST}/scripts/check-julia.sh"; then
  echo
  echo "Styx is installed but Julia is required before MCP will work."
  exit 1
fi

cat <<EOF

Styx ${ACTION} complete: ${DEST}

Next steps:
  1. Reload Window (Cmd+Shift+P → Developer: Reload Window)
  2. Settings → MCP → enable **pluto**
  3. In chat: "Run Styx doctor"

Uninstall: Settings → Plugins → Installed → Styx → Uninstall, then Reload Window.
  (If Uninstall misbehaves, remove the folder above manually.)

EOF
