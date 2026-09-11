# Lifecycle MCP tools

## Ownership

One Cursor window = one Styx/PlutoMCP/Pluto. Parent + local Task children share that MCP stdio connection. Chat switches keep the same session; Reload Window mints a new `session_id`.

## Tools (invoke by name)

| Tool | Purpose |
|------|---------|
| `pluto_session_status` | `pluto`, `session_id`, `managed`, `mcp_port`/`mcp_url`, `pluto_port`/`pluto_url`, notebooks |
| `start_pluto_session` | Start deferred Pluto (bound mode allocates UI port; ignore port args) |
| `stop_pluto_session` | Tear down Pluto; bound mode keeps the control bridge |
| `open_notebook` | Load a `.jl` file (Path B); may return `notebook_in_use` |
| `allow_execution` | Exit Safe preview (agent should call this or Glass **Run notebook code** when outputs need to be live); optional `run_notebook` (default true, non-blocking) |

## MCP tool picker quirk

Lifecycle tools may be **hidden** in Cursor's MCP tool picker. **Invoke by name anyway.**

**After upgrading PlutoMCP:** toggle **pluto** MCP off/on (or Reload Window) so `tools/list` and the launcher refresh.

## Glass URL

Always navigate with **`pluto_url` from status/start** — never hardcode `:1234`.

## Never ask the user to run

- `scripts/pluto-serve.sh` (dev-only)
- `PlutoMCP.serve()` / curl port probes

Use lifecycle tools. Local children must not discover bridges over HTTP or start shell servers.
