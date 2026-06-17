## Learned User Preferences

- Full Cursor plugin (commands, rules, browser hook) — not rules-only lightweight integration.
- Plugin workflow rule should reference PlutoMCP.jl for MCP tool semantics (stage → `submit_changes`).
- Planning docs live in this repo unless MCP-server-specific; fork may upstream.

## Learned Workspace Facts

- This repo holds the Cursor plugin and DOM click bridge; MCP tools live in PlutoMCP.jl.
- Decision record: `docs/DECISIONS.md` (not a declarative phase plan).
- Click context resolves `cell_id` via `closest("pluto-cell")` on the live hydrated Pluto DOM.
- Plugin install path: `~/.cursor/plugins/local/pluto-cursor-bridge/` per Cursor plugin conventions.
- MCP client connects to `PlutoMCP.serve()` bridge at `http://localhost:2346/sse`.
- After Phase 1 MCP validation: graph MCP tools (fork) and DOM bridge + plugin (here) run in parallel.
