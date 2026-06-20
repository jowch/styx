# Portable plugin tree copy (tar; rsync not required).
# shellcheck shell=bash
COPY_PLUGIN_TREE_EXCLUDES=(
  .git .cursor .github .git-template dist eval AGENTS.md
  .env.dev .env.dev.example docs/PLAN.md docs/DECISIONS.md
  docs/spikes docs/upstream node_modules hooks/__pycache__
  scripts/sync-local-plugin.sh scripts/package-plugin.sh
)

COPY_PLUGIN_PROTECTED=(
  .julia-env-instantiated
  hooks/state/pluto-reads.json
)

copy_plugin_tree() {
  local src="$1" dest="$2" preserve="${3:-0}"
  local prot_tmp="" x

  if [[ "$preserve" -eq 1 ]]; then
    prot_tmp="$(mktemp -d)"
    for x in "${COPY_PLUGIN_PROTECTED[@]}"; do
      if [[ -f "$dest/$x" ]]; then
        mkdir -p "$prot_tmp/$(dirname "$x")"
        cp "$dest/$x" "$prot_tmp/$x"
      fi
    done
  fi

  rm -rf "$dest"
  mkdir -p "$dest"

  local -a tar_excludes=()
  for x in "${COPY_PLUGIN_TREE_EXCLUDES[@]}"; do
    tar_excludes+=(--exclude "$x")
  done

  (cd "$src" && tar "${tar_excludes[@]}" -cf - .) | (cd "$dest" && tar -xf -)

  if [[ -n "$prot_tmp" ]]; then
    for x in "${COPY_PLUGIN_PROTECTED[@]}"; do
      if [[ -f "$prot_tmp/$x" ]]; then
        mkdir -p "$dest/$(dirname "$x")"
        cp "$prot_tmp/$x" "$dest/$x"
      fi
    done
    rm -rf "$prot_tmp"
  fi
}
