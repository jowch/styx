# Remote SSH workspaces

Cursor owns the SSH session and **auto-forwards** ports when Pluto listens on the host (same as a remote `:3000` app). Styx does not create `ssh -L` tunnels.

Pluto must run **on the SSH host**, next to the files. Do not start a laptop Pluto against the remote mount.

## Bootstrap

1. **Julia 1.11+** must be on the **remote** `PATH` (workspace terminal). If missing → **styx-setup**.
2. `pluto_session_status`. If `pluto` is `running` and `open_notebook` accepts a **workspace path**, MCP is already on the host — continue Path A/B as usual.
3. If stopped, start on the host:
   - Prefer **`start_pluto_session`** (correct when plugin MCP stdio runs on the SSH host).
   - If that would bind laptop ports or `open_notebook` cannot see workspace files: **stop** it, then start the HTTP stack in the **workspace Shell** (remote PTY):

     ```julia
     using PlutoMCP
     PlutoMCP.serve(launch_browser=false, require_secret_for_access=false)
     ```

     Wait until `http://127.0.0.1:2346/health` answers. Stdio `connect()` attaches per call once the bridge is up (Cursor forwards `:2346` if MCP is on the laptop).
4. Glass: `http://127.0.0.1:1234/`. If that fails, use the **Ports** panel URL (auto-forward remaps when laptop `:1234` is taken). Do not ask the user for `LocalForward` unless Ports/auto-forward is off (`remote.autoForwardPorts: false`) or broken.

## Never

- `start_pluto_session` on the laptop as a fallback when the workspace is Remote SSH and host Pluto is not up yet — that starts the wrong Julia.
- Bind Pluto on `0.0.0.0`.
- Treat Cloud Agent forwarding as this path.
