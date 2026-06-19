# Lifecycle MCP tools

## Tools (invoke by name)

| Tool | Purpose |
|------|---------|
| `pluto_session_status` | Check if Pluto stack is running |
| `start_pluto_session` | Start deferred Pluto + HTTP bridge on `:2346` |
| `stop_pluto_session` | Tear down Pluto stack |
| `open_notebook` | Load a `.jl` file into the session (Path B) |
| `allow_execution` | Exit safe preview on open notebook; optional `run_notebook` (default true) |

## MCP tool picker quirk

Lifecycle tools are registered on the **pluto** MCP server but **may not appear in Cursor's MCP tool picker UI**.

**Invoke by name anyway** — the agent can call `start_pluto_session`, `open_notebook`, etc. even when they are hidden from the picker.

After `start_pluto_session`, the HTTP bridge on `:2346` is up (hooks use this for health checks).

## Never ask the user to run

- `scripts/pluto-serve.sh` (dev-only)
- `PlutoMCP.serve()` manually

Use lifecycle tools instead.
