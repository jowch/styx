# PlutoMCP: MCP structural edits desync browser DOM

**Status:** Fixed in [PlutoMCP.jl#6](https://github.com/mthelm85/PlutoMCP.jl/pull/6); verify in browser after merge.  
**Discovered:** Design Mode spike (2026-06-17).

## Summary

`add_cell`, `delete_cell`, and `move_cell` can update server/file state while the Pluto browser tab still renders the old cell list. MCP reads and `read_notebook_code` reflect server truth; `document.querySelectorAll('pluto-notebook pluto-cell')` does not.

`set_cell_code` / `edit_cell` on **existing** cells are unaffected (output patches via `cell_results`).

## Symptom

```text
list_notebooks.cell_count  >  DOM pluto-cell count
```

Bind cell invisible during spike H1c: server had 4 cells, Glass DOM had 3 until hard reload.

## Root cause

PlutoMCP mutates `notebook.cell_order` **in place** (`push!`, `insert!`, `deleteat!`), then calls `Pluto.send_notebook_changes!`.

Pluto caches per-client notebook state for Firebasey diffs. `cell_order` is stored by reference; in-place mutation updates both server notebook and cached client snapshot simultaneously, so the differencer emits **no `cell_order` replace patch**. The client may receive `cell_inputs` / `cell_results` adds for the new cell but never updates `notebook.cell_order`, which drives `<pluto-cell>` rendering.

## Reproduction

1. Open notebook in Glass at `http://localhost:1234/edit?id=…` (synced baseline).
2. MCP `add_cell` with `run_after=true`.
3. Server: `list_notebooks` → `cell_count` incremented.
4. Browser console:

   ```javascript
   [...document.querySelectorAll('pluto-notebook pluto-cell')].map(c => c.id)
   // count unchanged; new id missing
   ```

5. `window.pluto_get_message_log()` → `cell_inputs` add for new id; **zero** `cell_order` patches.
6. Hard reload Pluto tab → DOM matches server.

## Workaround (until fix ships)

Hard-reload the Pluto tab (`⌘⇧R`) after MCP `add_cell`, `delete_cell`, or `move_cell`.

Agent/plugin rule: treat MCP/server reads as authoritative; do not infer notebook shape from DOM cell count after structural edits.

## Fix (fork, pre-upstream)

**Owner:** PlutoMCP.jl `Tools.jl`.

Replace in-place `cell_order` mutation with **new vector assignment** so Firebasey sees a reference change and emits a `cell_order` replace patch:

```julia
# Before (broken)
insert!(nb.cell_order, target_idx + 1, new_cell.cell_id)

# After
nb.cell_order = [nb.cell_order[1:target_idx]..., new_cell.cell_id, nb.cell_order[target_idx+1:end]...]
```

Apply the same pattern in `tool_add_cell`, `tool_delete_cell`, and `tool_move_cell`.

Optional hardening: integration test with connected WebSocket client asserting a `cell_order` patch after `add_cell`.

## Plan intersections

| Area | Impact |
|------|--------|
| [plutomcp-architecture.md](../specs/plutomcp-architecture.md) | "Browser stays in sync via WebSocket" — true for code/output edits; structural MCP edits need caveat until fix |
| [mcp-phase-1.md](../specs/mcp-phase-1.md) | `add_cell` / `move_cell` / `get_cell_order` — server order may diverge from DOM until fix |
| Path A click bridge (D13) | User cannot ⌥+click agent-added cells until DOM syncs |
| D9 draft buffer | Separate concern (unsaved browser typing vs server code) |
| 50/50 collaboration | Narrow gap: structural agent edits invisible in UI until reload |

Not a new DECISIONS entry — implementation bug in fork, not an integration architecture choice.
