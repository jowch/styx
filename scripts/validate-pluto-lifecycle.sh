#!/usr/bin/env bash
# Automated bound-session lifecycle checks (two concurrent owners + leases).
# Toggle pluto MCP off in Cursor before running so this machine is free of live bindings.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

echo "=== Pluto lifecycle validation (bound sessions) ==="

echo
echo "--- Preflight ---"
./scripts/pluto-lifecycle-preflight.sh --require-clean-runtime

RUNTIME="$(mktemp -d "${TMPDIR:-/tmp}/styx-lifecycle.XXXXXX")"
FIX_SRC="${ROOT}/eval/fixtures/reactive_xy.jl"
FIX_A="$(mktemp "${TMPDIR:-/tmp}/styx-nb-a.XXXXXX.jl")"
FIX_B="$(mktemp "${TMPDIR:-/tmp}/styx-nb-b.XXXXXX.jl")"
cp "$FIX_SRC" "$FIX_A"
cp "$FIX_SRC" "$FIX_B"
cleanup() {
  rm -rf "$RUNTIME" "$FIX_A" "$FIX_B"
}
trap cleanup EXIT

echo
echo "--- Two bound sessions: distinct ids/ports, lease conflict, stale recovery ---"
STYX_RUNTIME_DIR="$RUNTIME" FIX_A="$FIX_A" FIX_B="$FIX_B" julia --project=. <<'JULIA'
using PlutoMCP
using JSON
using HTTP
using UUIDs

function setup(host_pid::Int, hint::Int)
    binding = PlutoMCP.SessionBinding(;
        runtime_dir = ENV["STYX_RUNTIME_DIR"],
        binding_file = joinpath(ENV["STYX_RUNTIME_DIR"], "windows", "$(host_pid).json"),
        cursor_host_pid = host_pid,
    )
    PlutoMCP.configure_session_binding!(binding)
    PlutoMCP.claim_window_binding!(binding)
    PlutoMCP.configure_standalone!(;
        pluto_port_hint = hint + 1000,
        mcp_port_hint = hint,
        require_secret_for_access = false,
    )
    port = Int(PlutoMCP.start_control_bridge!(; mcp_port_hint = hint, listenany = true))
    return binding, port
end

function teardown!()
    PlutoMCP.stop_pluto_stack!(; close_control_bridge = true)
    PlutoMCP.cleanup_session_binding!()
end

# Session A
binding_a, port_a = setup(930001, 29000 + rand(0:200))
status_a = PlutoMCP.start_pluto_stack!()
@assert status_a["managed"] == true
@assert status_a["pluto"] == "running"
@assert status_a["session_id"] == binding_a.session_id
@assert status_a["mcp_port"] == port_a
@assert status_a["pluto_port"] isa Integer
open_a = PlutoMCP.tool_open_notebook(Dict("path" => ENV["FIX_A"], "run_notebook" => false))
sid_a, mcp_a, pluto_a = binding_a.session_id, port_a, status_a["pluto_port"]
# Keep A's servers alive by NOT tearing down yet — snapshot then install B in-process.
# In-process we can only own one module binding; simulate B as a second claim+lease check
# against A's live health, then recover after A stops.

binding_b = PlutoMCP.SessionBinding(;
    runtime_dir = ENV["STYX_RUNTIME_DIR"],
    binding_file = joinpath(ENV["STYX_RUNTIME_DIR"], "windows", "930002.json"),
    cursor_host_pid = 930002,
)
PlutoMCP.configure_session_binding!(binding_b)
err = try
    PlutoMCP.acquire_notebook_lease!(ENV["FIX_A"])
    nothing
catch e
    e
end
@assert err isa ArgumentError
@assert occursin("notebook_in_use", sprint(showerror, err))
println("lease conflict OK")

# Foreign plain-ok bridge must not be adopted while bound
foreign = HTTP.serve!(function (http::HTTP.Stream)
    if http.message.method == "GET" && startswith(http.message.target, "/health")
        HTTP.setstatus(http, 200)
        HTTP.startwrite(http)
        write(http, "ok")
    else
        HTTP.setstatus(http, 404)
        HTTP.startwrite(http)
    end
end, "127.0.0.1", 0; stream=true, verbose=false, listenany=true)
try
    fport = HTTP.port(foreign)
    @assert PlutoMCP.bridge_running(fport)
    # Restore A binding for dispatch test
    PlutoMCP.configure_session_binding!(binding_a)
    msg = Dict{String,Any}(
        "jsonrpc" => "2.0",
        "id" => 1,
        "method" => "tools/call",
        "params" => Dict{String,Any}(
            "name" => "pluto_session_status",
            "arguments" => Dict{String,Any}(),
        ),
    )
    resp = PlutoMCP.dispatch_stdio_message(msg; mcp_port = fport)
    st = JSON.parse(resp["result"]["content"][1]["text"])
    @assert st["session_id"] == sid_a
    @assert !haskey(resp["result"], "from")
    println("foreign bridge refusal OK")
finally
    close(foreign)
end

# Stop A → stale lease recovery for B on same path; B opens FIX_B independently after
PlutoMCP.configure_session_binding!(binding_a)
PlutoMCP.stop_pluto_stack!(; close_control_bridge = true)
PlutoMCP.cleanup_session_binding!()

binding_b2, port_b = setup(930002, 29200 + rand(0:200))
@assert binding_b2.session_id != sid_a
@assert port_b != mcp_a
status_b = PlutoMCP.start_pluto_stack!()
@assert status_b["pluto_port"] != pluto_a
lease = PlutoMCP.acquire_notebook_lease!(ENV["FIX_A"])
@assert lease.canonical_path == realpath(ENV["FIX_A"])
PlutoMCP._release_lease_dir_if_ours!(binding_b2, lease.lease_dir)
open_b = PlutoMCP.tool_open_notebook(Dict("path" => ENV["FIX_B"], "run_notebook" => false))
@assert open_b["notebook_id"] != open_a["notebook_id"]
nbs = PlutoMCP.tool_pluto_session_status(Dict{String,Any}())["notebooks"]
@assert length(nbs) == 1
@assert nbs[1]["notebook_id"] == open_b["notebook_id"]
println("distinct sessions + stale recovery OK")

teardown!()
println("Scenario bound dual-session OK")
JULIA

echo
echo "--- Hook binding isolation (empty runtime) ---"
STYX_RUNTIME_DIR="$RUNTIME" VSCODE_PID=999001 python3 - <<'PY'
import json, os, sys
sys.path.insert(0, "hooks")
import pluto_lib
assert pluto_lib.load_binding() is None
assert pluto_lib.verified_binding() is None
assert pluto_lib.mcp_health_ok() is False
print("{}")
PY

echo
echo "--- Python session binding unit tests ---"
python3 -m unittest eval.test_session_binding eval.test_pending_run_hook eval.test_glass_views_hook -v

echo
echo "All automated lifecycle checks passed."
echo "Manual: two Cursor windows, chat switch, Reload, local+Remote SSH, Ports-panel remap"
