## Learned User Preferences

- Full Cursor plugin (commands, rules, browser hook) — not rules-only lightweight integration.
- Plugin workflow rule should reference PlutoMCP.jl for MCP tool semantics (stage → `submit_changes`).
- **Pluto cell authoring (structure-first):** dedicated `imports_cell` with `begin`/`end`; default `begin`/`end` for multi-statement conceptual blocks (`compute_cell`); `let`/`end` for locals; split at reactive boundaries (`widget_cell`, etc.); copy layouts from **pluto-semantics** `reference/agent-examples.md` + `cell-structure.md`.
- Resolve `notebook_id` from Glass browser URL or Design Mode click before `list_notebooks`; skills **`styx-setup`** (install/Julia/MCP before notebook work), **`pluto-session`** / **`pluto-workflow`** / **`pluto-semantics`** are primary onboarding (lean SKILL.md + `reference/` deep-dives); no `@pluto-context` or **`pluto-open`** commands.
- **Release docs:** planning artifacts (DECISIONS, PLAN, lifecycle specs) are pruned at release; shipped onboarding lives in skills + README; MCP-only details in fork (`AGENTS.md`).
- 50/50 user+agent Pluto collaboration — user edits freely in browser; chat memory is not notebook ground truth.
- **0.1.0 release:** marketplace install + onboarding UX (Julia prerequisite, **styx-setup**) are ship blockers — not post-release deferrals.
- **Cursor 3 only (D16):** no Claude/Codex/OpenCode harness required; no `.claude-plugin/` distribution; do not document third-party-skills bridge as an install path.
- **Freshness + read-before-edit:** freshness at write boundaries and user handoffs (click/command), not background polling; read-before-edit enforced at MCP layer (Claude Code style), not rules-only.
- Click delivery: **D13 Path A** — Glass Design Mode `dom_path` in hook `prompt` → MCP **`resolve_pluto_context`** / **`read_cell`**.
- **Cursor-first:** no background Pluto for non-notebook work; agent bootstraps session on notebook intent — not user shell scripts; **`scripts/pluto-serve.sh` dev-only**; deferred `connect()` launcher is default; agent opens Glass via **`cursor-ide-browser`** in Agents Window (`glass-browser-*` view IDs) — **not** `plugin-browse-browser` or `cursor-app-control` **`open_resource`**.
- **Safe preview:** remind user to **Run notebook code** in Glass for live outputs/reactivity — not a hard edit gate; still stage edits when asked.
- **Commit hygiene:** commit at logical boundaries as you go — one focused commit per feature/doc slice, not large uncommitted batches. Split mixed files when needed (e.g. eval harness vs graph tools). Ask before pushing.

## Learned Workspace Facts

- **Styx** (this repo, [github.com/jowch/styx](https://github.com/jowch/styx)) — Cursor plugin bridging Pluto.jl and Cursor; MCP tools live in PlutoMCP.jl.
- MCP semantics in PlutoMCP.jl `AGENTS.md`; agent bootstrap/edits in `skills/pluto-session`, `pluto-workflow`, `pluto-semantics`.
- **D15 lazy warm lifecycle:** MCP stdio `connect()` always via launcher when **pluto** MCP enabled; full Pluto deferred until `start_pluto_session` on notebook intent; lifecycle tools on HTTP `:2346` (not always in Cursor stdio MCP tool picker); Cursor caches `tools/list` at connect — toggle **pluto** MCP or Reload Window after PlutoMCP upgrade for new tools (e.g. `allow_execution`); auto-serve on connect off by default (amends D12); **`pending_run` stop hook** silent when bridge down.
- **D13 Path A (spike):** Design Mode (**Cmd+Shift+D**, then click) — `browser_element` in hook `prompt` includes `pluto-cell#<uuid>` in `dom_path` for in-cell clicks (code lines, output, plot, bind widgets).
- **Design Mode limits:** ambiguous clicks (no `pluto-cell#` in `dom_path`, e.g. bare `main`) — enable Design Mode (⌘⇧D) and re-click inside a cell; drawings/annotations are screenshot-only, no structured `dom_path`.
- **Path C removed:** no `src/dom-resolver.js`, `inject.js`, or `bridge/server.js`; click parsing is Design Mode → MCP **`resolve_pluto_context`** + hook **`pluto_lib.py`**; read-before-edit hook **`guard-write.py`** (merged `preToolUse` + `beforeMCPExecution`); **`session-start.sh`** clears read receipts only.
- **Release/install:** **0.1.0** ships via **local plugin** (`scripts/install.sh` one-liner → `~/.cursor/plugins/local/styx/`); **`styx-setup`** + **`scripts/check-julia.sh`** + **`scripts/styx-doctor.sh`**; committed **Manifest.toml**; dev copy via **`sync-local-plugin.sh`**; **`package-plugin.sh`** → `dist/styx/`.
- **D15 session paths:** Path A = landing in Agents Glass → user picks notebook; Path B = landing → **`open_notebook`** → agent **`browser_click`** notebook on landing (not pasted `/edit?id=` — can hang; see **`docs/known-issues/path-b-edit-url-loading.md`**); canonical URL after load `http://127.0.0.1:1234/edit?id=<uuid>`. Glass: **`cursor-ide-browser`** (not `plugin-browse-browser`).
- **`open_notebook`:** server-side notebook load; safe preview default (`execution_allowed=false`); **`run_notebook`** opt-in at open time; **`allow_execution`** exits safe preview when user asks to run.
- Phases 1–4c complete; Phase 5 safety partial (pending_run hook + draft-buffer docs; snapshot/restore not done); **D15 lifecycle implemented** (acceptance signed off 2026-06-18; Path A/B validated in Glass).
- **Eval harness** (`eval/`): Julia-only CI gate via `run_reference.jl --all --strict-trace` (SDK `run.ts` removed); GHA cold-start needs `julia-actions/cache`, workflow precompile (`using PlutoMCP; using Pluto`), and **180s** health timeout when `CI=true`; lifecycle validation via **`scripts/pluto-lifecycle-preflight.sh --require-ports-free`** then **`scripts/validate-pluto-lifecycle.sh`** (toggle pluto MCP off first). PlutoMCP keeps optional `EvalLog.jl` hook only.
- **pluto-semantics references:** `reference/cell-structure.md` + `reference/agent-examples.md` — curated agent layouts (do not browse Pluto `sample/` for style).
