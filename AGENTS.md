## Learned User Preferences

- Full Cursor plugin (commands, rules, browser hook) — not rules-only lightweight integration.
- Plugin workflow rule should reference PlutoMCP.jl for MCP tool semantics (stage → `submit_changes`).
- When fixing `pluto_multi_expression`, default to `begin`/`end` wrap; split cells only for intentional reactive steps.
- Resolve `notebook_id` from Glass browser URL or Design Mode click before `list_notebooks`; skills **`pluto-session`** / **`pluto-workflow`** / **`pluto-semantics`** are primary onboarding.
- **Planning up front:** **DECISIONS.md** running decision log + **PLAN.md**/specs in this repo before implementation; MCP-only details in fork (`AGENTS.md`).
- 50/50 user+agent Pluto collaboration — user edits freely in browser; chat memory is not notebook ground truth.
- Freshness at write boundaries and user handoffs (click/command), not background polling.
- Read-before-edit enforced at MCP layer (Claude Code style), not rules-only.
- Click delivery: **D13 Path A** — Glass Design Mode `dom_path` in hook `prompt` → MCP **`resolve_pluto_context`** / **`read_cell`**.
- **Cursor-first:** no background Pluto for non-notebook work; agent bootstraps session on notebook intent — not user shell scripts; **`scripts/pluto-serve.sh` dev-only**; deferred `connect()` launcher is default; agent opens landing/notebook URLs in Glass (not link-only; browser navigate when `open_resource` unavailable).
- **Safe preview:** remind user to **Run notebook code** in Glass for live outputs/reactivity — not a hard edit gate; still stage edits when asked.
- **Commit hygiene:** commit at logical boundaries as you go — one focused commit per feature/doc slice, not large uncommitted batches. Split mixed files when needed (e.g. eval harness vs graph tools). Ask before pushing.

## Learned Workspace Facts

- **Styx** (this repo, [github.com/jowch/styx](https://github.com/jowch/styx)) — Cursor plugin bridging Pluto.jl and Cursor; MCP tools live in PlutoMCP.jl.
- **PLAN.md** — phase map; **DECISIONS.md** — decision log; **docs/specs/** — detailed specs including plutomcp-architecture.md and pluto-lifecycle.md (D15).
- **D15 lazy warm lifecycle:** MCP stdio `connect()` always via launcher when **pluto** MCP enabled; full Pluto deferred until `start_pluto_session` on notebook intent; lifecycle tools on HTTP `:2346` (not always in Cursor stdio MCP tool picker); auto-serve on connect off by default (amends D12).
- **D13 Path A (spike):** Design Mode (**Cmd+Shift+D**, then click) — `browser_element` in hook `prompt` includes `pluto-cell#<uuid>` in `dom_path` for in-cell clicks (code lines, output, plot, bind widgets).
- **Design Mode limits:** ambiguous clicks (no `pluto-cell#` in `dom_path`, e.g. bare `main`) — re-click a cell or `@pluto-context`; drawings/annotations are screenshot-only, no structured `dom_path`.
- **Path C removed:** no `src/dom-resolver.js`, `inject.js`, or `bridge/server.js`; click parsing is Design Mode → MCP **`resolve_pluto_context`** + hook **`pluto_lib.py`**.
- **Release/install:** nothing published yet; first release **0.1.0**; CHANGELOG **`[Unreleased]`** until first tag; dev install via **`sync-local-plugin.sh`** only (not user-facing).
- **D15 session paths:** Path A = general Pluto intent → landing page in Agents Glass (not `cursor-ide-browser` MCP), user picks notebook, `notebook_id` on next prompt; Path B = named `.jl` path → landing (cookies) → **`open_notebook`** → notebook URL `http://127.0.0.1:1234/edit?id=<uuid>` (plain `/<uuid>` fails). Commands **`pluto-notebooks`** / **`pluto-open`** for session entry (`pluto-start` removed).
- **`open_notebook`:** server-side notebook load; safe preview default (`execution_allowed=false`); **`run_notebook`** opt-in at open time; **`allow_execution`** exits safe preview when user asks to run.
- Phases 1–4c and Phase 5 safety complete; **D15 lifecycle implemented** (acceptance signed off 2026-06-18; Path A/B validated in Glass).
- **Eval harness** (`eval/`): scenarios, fixtures, reference runner, SDK orchestrator; CI gate via `run_reference.jl --all --strict-trace`. PlutoMCP keeps optional `EvalLog.jl` hook only.
