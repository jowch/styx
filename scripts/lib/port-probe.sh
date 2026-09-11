# Shared binding-aware health probes for styx-doctor and lifecycle scripts.
# shellcheck shell=bash

# shellcheck source=styx-window-key.sh
source "$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/styx-window-key.sh"

styx_runtime_dir() {
  if [[ -n "${STYX_RUNTIME_DIR:-}" ]]; then
    echo "${STYX_RUNTIME_DIR}"
  elif [[ -n "${XDG_RUNTIME_DIR:-}" ]]; then
    echo "${XDG_RUNTIME_DIR}/styx-${UID:-$(id -u)}"
  else
    echo "${TMPDIR:-/tmp}/styx-${UID:-$(id -u)}"
  fi
}

styx_binding_file() {
  local key
  key="$(resolve_styx_window_key 2>/dev/null)" || return 1
  echo "$(styx_runtime_dir)/windows/${key}.json"
}

# Prints binding JSON on stdout when present and schema-valid; else returns 1.
load_styx_binding() {
  local f
  f="$(styx_binding_file 2>/dev/null)" || return 1
  [[ -f "$f" ]] || return 1
  python3 - "$f" <<'PY'
import json, sys
path = sys.argv[1]
try:
    data = json.load(open(path, encoding="utf-8"))
except Exception:
    sys.exit(1)
if not isinstance(data, dict) or data.get("schema_version") != 1:
    sys.exit(1)
if not data.get("session_id") or not data.get("mcp_port"):
    sys.exit(1)
json.dump(data, sys.stdout)
PY
}

mcp_health_ok() {
  local binding port sid body
  binding="$(load_styx_binding 2>/dev/null)" || return 1
  port="$(python3 -c 'import json,sys; print(json.load(sys.stdin)["mcp_port"])' <<<"$binding")"
  sid="$(python3 -c 'import json,sys; print(json.load(sys.stdin)["session_id"])' <<<"$binding")"
  body="$(curl -sf --max-time 2 "http://127.0.0.1:${port}/health" 2>/dev/null)" || return 1
  python3 -c 'import json,sys; d=json.loads(sys.argv[1]); raise SystemExit(0 if d.get("session_id")==sys.argv[2] else 1)' "$body" "$sid"
}

pluto_ui_ok() {
  local binding port
  binding="$(load_styx_binding 2>/dev/null)" || return 1
  port="$(python3 -c 'import json,sys; print(json.load(sys.stdin).get("pluto_port") or "")' <<<"$binding")"
  [[ -n "$port" && "$port" != "None" && "$port" != "null" ]] || return 1
  curl -sf --max-time 2 -o /dev/null "http://127.0.0.1:${port}/" 2>/dev/null
}
