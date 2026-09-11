# Shared Styx window identity for launcher / doctor / lifecycle scripts.
# Prefer VSCODE_PID; else hash basename of VSCODE_IPC_HOOK_CLI → positive Int.
# shellcheck shell=bash

# Resolve plugin root for the Python helper (caller may set CURSOR_PLUGIN_ROOT).
_styx_window_key_py() {
  local root="${CURSOR_PLUGIN_ROOT:-}"
  if [[ -z "$root" ]]; then
    # scripts/lib → repo root
    root="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
  fi
  echo "${root}/hooks/styx_window_key.py"
}

# Sets STYX_WINDOW_KEY and STYX_WINDOW_KEY_SOURCE; prints key on stdout.
# Returns 1 when neither VSCODE_PID nor VSCODE_IPC_HOOK_CLI is available.
resolve_styx_window_key() {
  local out py
  py="$(_styx_window_key_py)"
  if [[ ! -f "$py" ]]; then
    return 1
  fi
  out="$(python3 "$py" 2>/dev/null)" || return 1
  STYX_WINDOW_KEY="${out%%$'\t'*}"
  STYX_WINDOW_KEY_SOURCE="${out#*$'\t'}"
  STYX_WINDOW_KEY_SOURCE="${STYX_WINDOW_KEY_SOURCE%%$'\n'*}"
  if [[ -z "${STYX_WINDOW_KEY}" ]] || ! [[ "${STYX_WINDOW_KEY}" =~ ^[0-9]+$ ]]; then
    return 1
  fi
  echo "${STYX_WINDOW_KEY}"
}
