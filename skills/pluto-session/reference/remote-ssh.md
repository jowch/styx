# Remote SSH workspaces

Cursor owns the SSH session and **auto-forwards** ports when Pluto listens on the host. Styx does not create `ssh -L` tunnels.

**Local XOR remote:** this Cursor window's Styx launcher and runtime directory live where the extension host runs. Never probe a laptop `:2346` hoping to find the SSH session, and never start a laptop Pluto against a remote mount.

## Bootstrap

1. **Julia 1.11+** must be on the **remote** `PATH` (workspace terminal). If missing → **styx-setup**.
2. `pluto_session_status`. Read `pluto_url` / `mcp_port` from the result — ports are dynamic.
3. If stopped → **`start_pluto_session`** (bound MCP stdio on the SSH host owns the stack). Do **not** fall back to `PlutoMCP.serve()` or fixed `:1234`/`:2346`.
4. Glass: **reuse** the existing Agents Glass Pluto tab when present ([glass-navigation.md](glass-navigation.md#tab-reuse-no-newtab-by-default)). Navigate to **`pluto_session_status.pluto_url`** with `position: "active"`. If that fails because Cursor remapped the laptop-side port, use the **Ports** panel client URL (`remote_forward_unresolved`) — MCP still talks host ports; only Glass/human URLs need the remap. Do not try another localhost Pluto, adopt a page that merely responds, or open extra Glass tabs to “retry.”
5. Local Task children inherit this window's `plugin-styx-pluto` MCP — do not pass ports in prompts.

## Host vs laptop ports

- **MCP lifecycle** uses host-local ports from status (`pluto_url`, `mcp_port`). No laptop remap required.
- **Glass / links you give the user** must survive Ports remapping. Prefer status `pluto_url` first; on load failure, switch to the Ports forwarded URL. Never hardcode `:1234` in skills, prompts, or handoff text.

## Never

- `PlutoMCP.serve()` / `pluto-serve.sh` / curl discovery as an alternate transport.
- Bind Pluto on `0.0.0.0`.
- Treat Cloud Agent forwarding as this path.
- Open the same canonical notebook path in two Styx sessions (`notebook_in_use`).
- Spam `newTab` / new Glass views when tab list is empty or navigate fails ([issue #4](https://github.com/jowch/styx/issues/4)).
