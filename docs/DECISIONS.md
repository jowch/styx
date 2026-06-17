# Decision Record

Running log of architectural and workflow decisions for the Pluto ↔ Cursor integration.
This is **not** a task list — it records *what we decided, what we target, and what exists today*.

| Repo | Role |
|------|------|
| **pluto-cursor-bridge** (this repo) | Cursor plugin, DOM click bridge, integration planning |
| **[PlutoMCP.jl](https://github.com/jowch/PlutoMCP.jl)** fork | MCP tool surface, server-side notebook mutation (may upstream) |

**Doc split (D1):** MCP tool semantics and implementation details live in the fork's `AGENTS.md`. This doc covers cross-repo integration only; fork decisions are summarized here for context.

---

## D1 — Repo split

**Decision:** Keep planning docs here unless they are purely MCP-server internals.

**Why:** The fork may upstream; plugin and bridge work stay portable.

---

## D2 — Identity primitives

**Decision:** `notebook_id` + `cell_id` everywhere — MCP tools, DOM bridge, plugin context.

**Why:** Pluto sets `<pluto-cell id="{cell_id}">` and `<pluto-notebook id="{notebook_id}">` from Julia UUIDs (confirmed in Pluto frontend `Cell.js` / `Notebook.js`).

---

## D3 — MCP tool surface *(target; fork work)*

**Decision:** One canonical name per operation; no parallel aliases. Full inventory:

| Operation | Target name | Today (upstream) | Stage-first? |
|-----------|-------------|------------------|--------------|
| List notebooks | `list_notebooks` | `list_notebooks` | — |
| Read one cell | `read_cell` | `get_cell` | — |
| Edit code | `edit_cell` | `set_cell_code` | yes; `run_after=false` default |
| Run one cell | `execute_cell` | `run_cell` | — |
| Batch run staged | `submit_changes` | — (not `run_all_cells`) | — |
| Notebook code view | `read_notebook_code` | — | replaces `get_notebook_state` |
| Add cell | `add_cell` | `add_cell` | yes; `run_after=false` default |
| Delete cell | `delete_cell` | `delete_cell` | immediate run (reactive cleanup) |
| Move cell | `move_cell` | `move_cell` | — |

**Remove from agent surface:** `get_notebook_state`, `run_all_cells` (unless explicitly kept as escape hatch).

**Response fields (new tools):** `pending_run`, `stale_cell_ids` on server — do not rely on agent instructions alone.

**Interim workflow (until fork Phase 1 ships):** use `set_cell_code(..., run_after=false)` + manual `run_cell`/`run_all_cells` with documented limitations. Do not treat rename as current policy for agents.

Details: fork `AGENTS.md`.

---

## D4 — Stage-first agent workflow *(target)*

**Decision:** Agents edit with `run_after=false`, then call `submit_changes` once.

**Why:** Matches Pluto save/run UX; avoids partial reactive runs mid-edit.

**Blocked on:** dirty tracking + `submit_changes` implementation in fork. Today `run_after` defaults to `true` in code.

---

## D5 — Click-to-context bridge

**Decision:** Resolve IDs from click events on the live hydrated Pluto DOM.

**Primary resolution** (prefer `composedPath()` over bare `closest()` for shadow-DOM widget output):

```javascript
const path = event.composedPath();
const cell = path.find(el => el.tagName === "PLUTO-CELL" && el.id);
const notebook = path.find(el => el.tagName === "PLUTO-NOTEBOOK" && el.id);
```

**Context packet:**

```json
{
  "cell_id": "uuid",
  "notebook_id": "uuid",
  "in_output": true,
  "in_input": false,
  "inside_iframe": false,
  "target_tag": "IMG",
  "text_snippet": "…",
  "intent": "read|edit|explain|refactor"
}
```

**Fallbacks:**
- No `pluto-cell` in path → reject; prompt user
- Click inside iframe contentDocument → reject or screenshot/advisory mode
- MCP read fails → verify `notebook_id` via URL `?id=` or `list_notebooks`
- Rich output (plots/HTML): MCP returns opaque placeholders today — see O5

**Status:** Spec only. No injected script or bridge server yet.

---

## D6 — Cursor plugin scope

**Decision:** Full plugin — commands, rules, optional hooks — not rules-only.

**Phased delivery:**
1. **MVP** — workflow rule + commands (`pluto-select-cell`) + `mcp.json` pointer to `:2346/sse`
2. **Later** — injected `dom-resolver.js` + local click queue + command reads queue into `@pluto-context` chat block

There is no native Cursor "browser hook" component; click capture requires injected DOM script + local bridge (superpowers-style pattern).

**Install path:** `~/.cursor/plugins/local/pluto-cursor-bridge/`

**Status:** Docs only; no plugin scaffold.

---

## D7 — Parallel tracks after Phase 1 gate

**Decision:** Layer 2 graph/validation MCP tools (fork) and DOM bridge + plugin (here) proceed **only after** Phase 1 gate passes.

**Phase 1 gate:** agent can stage edits and run via target tool surface on a live notebook with verifiable output.

---

## Open questions

| # | Question | Blocks |
|---|----------|--------|
| O1 | `submit_changes` exact Pluto API mapping (dirty subset vs full re-run)? | D4, fork Phase 1 |
| O2 | Draft-buffer conflict policy when user edits browser while agent writes MCP? | D5 edit workflow |
| O3 | Click packet → agent delivery: command vs `beforeSubmitPrompt` hook vs paste? | D6 MVP |
| O4 | Upstream PR: hard rename vs alias period? | D3 rollout |
| O5 | Rich output strategy (plots, HTML, `@bind`) — MCP read path vs screenshot-only? | D5 explain/refactor |
| O6 | Who sets `intent` — modifier key, menu, command? | D6 UX |

---

## Status snapshot (2026-06-17)

| Component | State |
|-----------|-------|
| PlutoMCP fork — basic tools (old names) | ✅ Works |
| PlutoMCP fork — dirty tracking | ❌ Not started |
| PlutoMCP fork — rename + `submit_changes` + `read_notebook_code` | ❌ Not started |
| Browser → cell_id bridge | ❌ Spec only |
| Cursor plugin | ❌ Docs only |
| This repo | ✅ Decision record |

### Fork Phase 1 implementation order

1. Dirty tracking (`pending_run`, `stale_cell_ids`)
2. Rename tools; flip `run_after` default
3. `submit_changes`
4. `read_notebook_code`; remove `get_notebook_state`
5. Tests + `reference/` fixtures
