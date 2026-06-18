# MCP Phase 1 Spec

> Staging doc for [PlutoMCP.jl](https://github.com/jowch/PlutoMCP.jl) fork. Canonical agent semantics: fork `AGENTS.md`.

## Goal

Agent-grade MCP surface: file-shaped read, cell-ID edit, stage-first workflow, mutation receipts. Validate in Cursor + CLI before browser UX.

---

## Tool catalog (after Phase 1)

### Layer 1 — agent surface

| Tool | Purpose |
|------|---------|
| `list_notebooks` | Discover open notebooks |
| `read_notebook_code` | Whole notebook as execution-order code projection |
| `read_cell` | Single cell code + output + stale flag |
| `edit_cell` | Stage or run one cell (`run_after` default `false`) |
| `edit_cells` | Batch stage `{cell_id, code}[]`; never runs |
| `add_cell` | Insert cell (`after_cell_id` required when non-empty) |
| `move_cell` | Reorder visually |
| `delete_cell` | Remove cell (immediate reactive cleanup) |
| `submit_changes` | Cmd+S batch run of dirty cells |
| `execute_cell` | Run one cell (Shift+Enter) |
| `get_cell_order` | Visual order |
| `get_execution_order` | Dependency order |
| `resolve_pluto_context` | *(Phase 4 addendum, D13)* Map Design Mode xpath/URL hint → `notebook_id` + `cell_id`; agent calls before `read_cell` |

### Removed from agent surface

- `get_notebook_state` → `read_notebook_code` + `read_cell`
- `get_cell` → `read_cell`
- `set_cell_code` → `edit_cell`
- `run_cell` → `execute_cell`
- `run_all_cells` → not on agent surface (internal/debug only if kept)

**Rename policy:** hard break, no parallel aliases (see DECISIONS D8).

---

## 1A — `read_notebook_code`

### Why execution order default

Models reason about definitions-before-uses. Reactive semantics care about run order, not UI layout. Visual order remains available via `get_cell_order` and `order=visual` param.

### Projection rules

| Include | Exclude (default) |
|---------|-------------------|
| Code cells (even empty → `# (empty)`) | Frontmatter, header boilerplate |
| Pluto-style markers `# ╔═╡ <cell_id>` | `@bind` shim macro |
| | `PLUTO_PROJECT_TOML_CONTENTS`, manifest blobs |
| | Cell-order footer `# ╔═╡ Cell order:` |
| | Markdown cells (opt-in: `include_markdown=true` → `# md:\n...`) |

Parse via Pluto internals (live session), not raw-file regex.

### Response shape

```json
{
  "notebook_id": "...",
  "path": "...",
  "order": "execution",
  "cell_ids": ["...", "..."],
  "stale_cell_ids": ["..."],
  "pending_run": ["..."],
  "code": "# ╔═╡ 30543e65-...\nusing Foo\n\n# ╔═╡ e814a124-...\n# (empty)\n..."
}
```

- Primary read surface: `code` string (linear, marker-embedded)
- `cell_ids`: ordered, for placement without parsing
- `stale_cell_ids` / `pending_run`: staging awareness without duplicating bodies
- No duplicate `cells[]` array in default response

Optional later: `format=structured` if a consumer needs split bodies.

---

## 1B — Staging & dirty tracking

### Session state (per notebook)

```julia
pending_run::Set{UUID}  # staged but not executed
```

**Add to set:** `edit_cell`/`edit_cells`/`add_cell` when `run_after=false`
**Remove from set:** successful run via `submit_changes`, `execute_cell`, or `edit_cell(run_after=true)`

### `submit_changes`

```json
{
  "notebook_id": "...",
  "cell_ids": ["optional", "subset"],
  "wait_for_completion": true
}
```

**Pluto API mapping (resolves O1):**
1. Collect target cells: `cell_ids` arg if provided, else all `pending_run`
2. Expand to reactive closure: include downstream dependents Pluto would re-run (via `update_save_run!` on changed cells — Pluto scheduler handles transitive deps)
3. Single `Pluto.update_save_run!(session, nb, cells; run_async=false, save=true)`
4. Clear `pending_run` for successfully queued/ran cells
5. `_notify_browser(session, nb)`
6. Return mutation receipt

**Differs from `run_all_cells`:** runs dirty/staged subset + reactive dependents, not every cell in notebook.

### Defaults flip

| Tool | `run_after` default |
|------|---------------------|
| `edit_cell` | `false` |
| `add_cell` | `false` |

### Agent workflow (tool descriptions + plugin rule)

1. `read_notebook_code`
2. `edit_cell` / `edit_cells` (stage)
3. `submit_changes` when ready
4. `execute_cell` only for intentional mid-edit single run

---

## 1C — Mutation receipts

Shared `_mutation_receipt(session, nb, meta; context="compact")` for all write tools.

### Compact receipt fields

| Field | Purpose |
|-------|---------|
| `applied` | mutation succeeded |
| `mutation` | `{type, cell_id, ...}` |
| `cell_order` | visual order after change |
| `execution_order` | dependency order after change |
| `affected_cells` | IDs touched by reactivity |
| `execution.status` | `completed` / `running` / `errored` |
| `outputs.changed` | `{cell_id, output_summary}[]` |
| `pending_run` | staged, not yet executed |
| `warnings` | placement / validation notes |

**Blocking:** `submit_changes` and `execute_cell` wait for completion (60s timeout). `edit_cell` default returns immediately (staged).

Graduated modes later: `context=none|compact|local|full`.

---

## 1D — Tool adjustments

| Tool | Change |
|------|--------|
| `add_cell` | Require `after_cell_id` when notebook non-empty |
| `read_cell` | Rename from `get_cell`; include `stale: bool` |
| `edit_cell` | Rename from `set_cell_code`; receipt + `pending_run` |
| `edit_cells` | New batch stage |
| `submit_changes` | New |
| `execute_cell` | Rename from `run_cell` |
| `move_cell` | Receipt with old/new visual index |
| `get_cell_order` | New |
| `get_execution_order` | New |
| `get_notebook_state` | Remove from MCP schema |

---

## 1E — Draft-buffer policy (O2)

MCP writes server `Notebook` directly; browser editor has a separate draft buffer.

| Layer | Policy |
|-------|--------|
| Server (MCP) | Tracks `pending_run` for server-side staged edits only |
| Agent rule | Always `read_cell` immediately before `edit_cell` on same cell |
| Conflict | Server wins (last MCP write); no OT/CRDT |
| User UX | Plugin rule warns: "Close/save browser edits before agent edits" |
| Browser-only drafts | Invisible to MCP until user submits in Pluto UI |

**Phase 1 scope:** document limits; no draft detection API.

---

## 1F — Rich output (O5)

| Output type | Phase 1 behavior |
|-------------|------------------|
| `text/plain` | Return text |
| Images, HTML, binary | Placeholder: `[mime output, N bytes]` |
| Click on plot | Bridge provides `cell_id` + `in_output`; agent uses `read_cell` (text only) |
| Explain/refactor plots | Advisory mode: agent acknowledges visual output not machine-readable; screenshot deferred to plugin Phase 4+ |

---

## 1G — Tests

Extend `test/runtests.jl` + minimal committed fixtures:

- Projection strips manifest/frontmatter; preserves markers; execution order
- Empty cells included with marker
- Receipt on all write tools
- `edit_cell` default does not execute; `submit_changes` runs dirty batch
- `add_cell` rejects missing placement on non-empty notebook
- `get_notebook_state` removed from `tools/list`

---

## Implementation order

1. Dirty tracking infrastructure
2. Renames + default flip
3. `submit_changes`
4. `read_notebook_code` + order tools
5. Mutation receipts
6. `edit_cells` (optional within 1B)
7. Remove `get_notebook_state`; update tests/README
8. Cursor end-to-end validation
