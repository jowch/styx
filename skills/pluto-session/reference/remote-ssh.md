# Remote SSH workspaces

Cursor owns the SSH session and **auto-forwards** ports when Pluto listens on the host. Styx does not create `ssh -L` tunnels.

**Local XOR remote:** this Cursor window's Styx launcher and runtime directory live where the extension host runs. Never probe a laptop `:2346` hoping to find the SSH session, and never start a laptop Pluto against a remote mount.

## Bootstrap

1. **Julia 1.11+** must be on the **remote** `PATH` (workspace terminal). If missing → **styx-setup**.
2. `pluto_session_status`. Read `pluto_url` / `mcp_port` from the result — ports are dynamic.
3. If stopped → **`start_pluto_session`** (bound MCP stdio on the SSH host owns the stack). Do **not** fall back to `PlutoMCP.serve()` or fixed `:1234`/`:2346`.
4. Glass: navigate to **`pluto_session_status.pluto_url`**. If that fails because Cursor remapped the laptop-side port, use the **Ports** panel URL (`remote_forward_unresolved`). Do not try another localhost Pluto or adopt a page that merely responds.
5. Local Task children inherit this window's `plugin-styx-pluto` MCP — do not pass ports in prompts.

## Never

- `PlutoMCP.serve()` / `pluto-serve.sh` / curl discovery as an alternate transport.
- Bind Pluto on `0.0.0.0`.
- Treat Cloud Agent forwarding as this path.
- Open the same canonical notebook path in two Styx sessions (`notebook_in_use`).
