## Learned User Preferences

- Full Cursor plugin (commands, rules, browser hook) — not rules-only lightweight integration.
- Plugin workflow rule should reference PlutoMCP.jl for MCP tool semantics (stage → `submit_changes`).
- When fixing `pluto_multi_expression`, default to `begin`/`end` wrap; split cells only for intentional reactive steps.
- Resolve `notebook_id` from Glass browser URL or Design Mode click before `list_notebooks`.
- **Planning up front:** **DECISIONS.md** running decision log + **PLAN.md**/specs in this repo before implementation; MCP-only details in fork (`AGENTS.md`).
- 50/50 user+agent Pluto collaboration — user edits freely in browser; chat memory is not notebook ground truth.
- Freshness at write boundaries and user handoffs (click/command), not background polling.
- Read-before-edit enforced at MCP layer (Claude Code style), not rules-only.
- Click delivery: **D13 Path A** — Glass Design Mode `dom_path` in hook `prompt` → MCP **`resolve_pluto_context`** / **`read_cell`**.
- Open Pluto in Agents Glass (`?secret=` from terminal by default; plugin launcher passes `require_secret_for_access=false`) — not `cursor-ide-browser` MCP.
- **Commit hygiene:** commit at logical boundaries as you go — one focused commit per feature/doc slice, not large uncommitted batches. Split mixed files when needed (e.g. eval harness vs graph tools). Ask before pushing.

## Learned Workspace Facts

- **Styx** (this repo, [github.com/jowch/styx](https://github.com/jowch/styx)) — Cursor plugin bridging Pluto.jl and Cursor; MCP tools live in PlutoMCP.jl.
- **PLAN.md** — phase map; **DECISIONS.md** — decision log; **docs/specs/** — detailed specs including plutomcp-architecture.md.
- MCP lifecycle: bundled `mcp.json` + launcher; Cursor spawns; plugin-root `Project.toml`/`Manifest.toml` Julia env (not user's default project).
- **D13 Path A (spike):** Design Mode (**Cmd+Shift+D**, then click) — `browser_element` in hook `prompt` includes `pluto-cell#<uuid>` in `dom_path` for in-cell clicks (code lines, output, plot, bind widgets).
- Ambiguous Design Mode clicks (no `pluto-cell#` in `dom_path`, e.g. bare `main`) — enable Design Mode (Cmd+Shift+D) and re-click a cell, or use `@pluto-context`.
- Design Mode drawing/annotations: screenshot to model only; no structured `browser_element` / `dom_path`.
- **Path C removed:** no `src/dom-resolver.js`, `inject.js`, or `bridge/server.js`; click parsing is Design Mode → MCP **`resolve_pluto_context`** + hook **`pluto_lib.py`**.
- Plugin install path: `~/.cursor/plugins/local/styx/`.
- MCP client: `http://localhost:2346/sse` (`PlutoMCP.serve()`); MCP server key in `mcp.json` is **`pluto`**.
- Phases 1–4 complete; Styx plugin validated through 4c (`resolve_pluto_context`, `pending_run` `stop` hook).
- **Eval harness** (`eval/`): scenarios, fixtures, reference runner, SDK orchestrator; CI gate via `run_reference.jl --all --strict-trace`. PlutoMCP keeps optional `EvalLog.jl` hook only.
