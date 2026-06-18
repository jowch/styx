## Learned User Preferences

- Full Cursor plugin (commands, rules, browser hook) — not rules-only lightweight integration.
- Plugin workflow rule should reference PlutoMCP.jl for MCP tool semantics (stage → `submit_changes`).
- When fixing `pluto_multi_expression`, default to `begin`/`end` wrap; split cells only for intentional reactive steps.
- Resolve `notebook_id` from Glass browser URL or Design Mode click before `list_notebooks`.
- **Planning up front:** integrated plan + phase specs in this repo before implementation.
- Planning docs live here unless MCP-server-specific; fork may upstream.
- 50/50 user+agent Pluto collaboration — user edits freely in browser; chat memory is not notebook ground truth.
- Freshness at write boundaries and user handoffs (click/command), not background polling.
- Read-before-edit enforced at MCP layer (Claude Code style), not rules-only.
- Click delivery: **D13 Path A** — parse `pluto-cell#` from Glass Design Mode `dom_path` in hook `prompt`. Path C inject+queue is dev/fallback only.
- Open Pluto in Agents Glass (`?secret=` from terminal by default; plugin launcher passes `require_secret_for_access=false`) — not `cursor-ide-browser` MCP.
- **Commit hygiene:** commit at logical boundaries as you go — one focused commit per feature/doc slice, not large uncommitted batches. Split mixed files when needed (e.g. eval harness vs graph tools). Ask before pushing.

## Learned Workspace Facts

- This repo holds the Cursor plugin and DOM click bridge; MCP tools live in PlutoMCP.jl.
- **PLAN.md** — phase map; **DECISIONS.md** — decision log; **docs/specs/** — detailed specs including plutomcp-architecture.md.
- MCP lifecycle: bundled `mcp.json` + launcher; Cursor spawns; plugin-root `Project.toml`/`Manifest.toml` Julia env (not user's default project).
- **D13 Path A (spike):** Design Mode (**Cmd+Shift+D**, then click) — `browser_element` in hook `prompt` includes `pluto-cell#<uuid>` in `dom_path` for in-cell clicks (code lines, output, plot, bind widgets).
- Ambiguous Design Mode clicks (no `pluto-cell#` in `dom_path`, e.g. bare `main`) — enable Design Mode (Cmd+Shift+D) and re-click a cell, or use `@pluto-context`.
- Design Mode drawing/annotations: screenshot to model only; no structured `browser_element` / `dom_path`.
- Spike H2/H3 falsified: `alwaysApply` rules session-cached; `beforeSubmitPrompt` block-only (no context injection).
- Click context (Path C dev fallback): `composedPath()` → `PLUTO-CELL` via inject.js; production uses `parseDomPath` on Design Mode `dom_path`.
- Plugin install path: `~/.cursor/plugins/local/pluto-cursor-bridge/`.
- MCP client: `http://localhost:2346/sse` (`PlutoMCP.serve()`).
- Phase 1 gate before parallel Phase 2 (graph MCP) + Phase 3 (DOM bridge).
