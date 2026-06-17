# Safety & Rollback Spec — Phase 5

## Goal

Recover from bad agent edits without git-level file surgery. Document human+agent concurrency limits.

## Scope (minimal)

| Capability | Approach |
|------------|----------|
| Pre-edit snapshot | Before batch edit or on plugin command: `read_notebook_code` or targeted `read_cell` → store `{cell_id, code}[]` in chat or temp file |
| Restore | `edit_cell(cell_id, old_code)` per cell + optional `submit_changes` |
| Concurrency warning | Rule/docs: browser draft vs MCP server; agent must read before edit |
| Long-run guard | Rule: confirm before `submit_changes` on notebooks with expensive cells |
| Session end | Rule warns if `pending_run` non-empty |

## Not in scope

- Full notebook version history
- OT/CRDT for simultaneous human+agent edit
- Automatic rollback without user invoking restore
- Detecting browser-only unsaved drafts from MCP

## Acceptance

- Documented workflow restores single cell after bad `edit_cell`
- Plugin rule surfaces non-empty `pending_run` before session close
