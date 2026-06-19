#!/usr/bin/env bash
# Automated D15 deferred lifecycle checks (Scenarios 0, C, D, E at protocol/hook layer).
# Live Cursor agent behavior (0.2, C.1) still requires manual chat validation.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

echo "=== D15 automated validation ==="

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
echo "--- Scenario 0: preflight baseline (ports down) ---"
./scripts/d15-preflight.sh

echo
echo "--- Scenario D: pending_run stop hook ---"
julia --project=. -e '
using PlutoMCP
PlutoMCP.stop_pluto_stack!()
PlutoMCP.tool_start_pluto_session(Dict{String,Any}())
nb = PlutoMCP.tool_open_notebook(Dict("path" => abspath("eval/fixtures/reactive_xy.jl"), "run_notebook" => false))
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
PlutoMCP.stop_pluto_stack!()
println("Scenario D OK")
'

echo
echo "All automated D15 checks passed."
echo "Manual: Scenario 0.2 (non-notebook chat), C.1 (agent skips start_pluto_session) — see docs/d15-lifecycle-manual-checklist.md"
