## Learned User Preferences

- Full Cursor plugin (commands, rules, browser hook) — not rules-only lightweight integration.
- Plugin workflow rule should reference PlutoMCP.jl for MCP tool semantics (stage → `submit_changes`).
- **Planning up front:** integrated plan + phase specs in this repo before implementation.
- Planning docs live here unless MCP-server-specific; fork may upstream.

## Learned Workspace Facts

- This repo holds the Cursor plugin and DOM click bridge; MCP tools live in PlutoMCP.jl.
- **PLAN.md** — phase map and build sequence; **DECISIONS.md** — decision log; **docs/specs/** — detailed specs.
- Click context: `composedPath()` → `PLUTO-CELL` (not bare `closest()`).
- Plugin install path: `~/.cursor/plugins/local/pluto-cursor-bridge/`.
- MCP client: `http://localhost:2346/sse` (`PlutoMCP.serve()`).
- Phase 1 gate before parallel Phase 2 (graph MCP) + Phase 3 (DOM bridge).
