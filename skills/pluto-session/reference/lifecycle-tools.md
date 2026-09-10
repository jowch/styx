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

**After upgrading PlutoMCP:** toggle **pluto** MCP off/on in Cursor Settings (or Reload Window) so `tools/list` refreshes — e.g. `allow_execution` won't be callable until the cache updates.

After `start_pluto_session`, the HTTP bridge on `:2346` is up (hooks use this for health checks).

Stdio `connect()` **re-checks** `/health` on each tool call. If this process has not started Pluto but a bridge is already up (including one Cursor forwarded from a Remote SSH host), calls go to that bridge.

## Never ask the user to run

- `scripts/pluto-serve.sh` (dev-only)
- `PlutoMCP.serve()` **themselves**

Use lifecycle tools instead. On Remote SSH the **agent** may run `PlutoMCP.serve()` in the workspace Shell — [remote-ssh.md](remote-ssh.md).
