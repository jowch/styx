#!/usr/bin/env bash
# Source plugin-root .env.dev (dev-only; gitignored). No-op if missing.
load_env_dev() {
  local root="${1:-}"
  [[ -n "$root" ]] || return 0
  local file="${root}/.env.dev"
  [[ -f "$file" ]] || return 0
  set -a
  # shellcheck disable=SC1090
  source "$file"
  set +a
}
