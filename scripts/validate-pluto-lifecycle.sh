#!/usr/bin/env bash
# Automated deferred Pluto lifecycle checks (start/stop, pending_run hook).
# Requires :1234 and :2346 free — toggle pluto MCP off in Cursor before running.
# Live agent behavior (Scenarios 0.2, C.1) still needs manual chat validation.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

echo "=== Pluto lifecycle validation ==="

echo
echo "--- Preflight: ports free ---"
./scripts/pluto-lifecycle-preflight.sh --require-ports-free

echo
echo "--- Scenario 0 / E: deferred lifecycle (Julia) ---"
julia --project=. -e '
using PlutoMCP
PlutoMCP.stop_pluto_stack!()
st = PlutoMCP.tool_pluto_session_status(Dict{String,Any}())
@assert st["pluto"] == "stopped"
PlutoMCP.tool_start_pluto_session(Dict{String,Any}())
@assert PlutoMCP.tool_pluto_session_status(Dict{String,Any}())["pluto"] == "running"
println("Scenario 0.3 + C.2 OK")
PlutoMCP.tool_stop_pluto_session(Dict{String,Any}())
@assert PlutoMCP.tool_pluto_session_status(Dict{String,Any}())["pluto"] == "stopped"
println("Scenario E.2 OK")
'

echo
echo "--- Scenario 0: post-stop baseline (ports down) ---"
./scripts/pluto-lifecycle-preflight.sh --require-ports-free

echo
echo "--- Scenario D: pending_run stop hook ---"
julia --project=. -e '
using PlutoMCP
PlutoMCP.stop_pluto_stack!()
PlutoMCP.tool_start_pluto_session(Dict{String,Any}())
fixture = abspath("eval/fixtures/reactive_xy.jl")
tmp = joinpath(tempdir(), "reactive_xy-pending_run-$(rand(UInt32)).jl")
cp(fixture, tmp)
nb = PlutoMCP.tool_open_notebook(Dict("path" => tmp, "run_notebook" => false))
nid, cid = nb["notebook_id"], "11111111-1111-1111-1111-111111111111"
sess = PlutoMCP.standalone_session()
PlutoMCP.call_tool_with_session(sess, "read_cell", Dict("notebook_id" => nid, "cell_id" => cid))
PlutoMCP.call_tool_with_session(sess, "edit_cell", Dict("notebook_id" => nid, "cell_id" => cid, "code" => "x = 99", "run_after" => false))
@assert !isempty(PlutoMCP.call_tool_with_session(sess, "read_notebook_code", Dict("notebook_id" => nid))["pending_run"])
out = read(`python3 hooks/warn-pending-run.py`, String)
@assert occursin("pending_run", out)
PlutoMCP.call_tool_with_session(sess, "submit_changes", Dict("notebook_id" => nid))
@assert isempty(PlutoMCP.call_tool_with_session(sess, "read_notebook_code", Dict("notebook_id" => nid))["pending_run"])
@assert strip(read(`python3 hooks/warn-pending-run.py`, String)) == "{}"
rm(tmp; force=true)
PlutoMCP.stop_pluto_stack!()
println("Scenario D OK")
'

echo
echo "All automated lifecycle checks passed."
echo "Manual: Scenario 0.2 (non-notebook chat), C.1 (agent skips start_pluto_session) — see docs/d15-lifecycle-manual-checklist.md"
