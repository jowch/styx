---
name: pluto-workflow
description: >-
  Use when editing Pluto notebook cells via MCP, resolving Design Mode or
  Glass URL context, staging changes before submit_changes, or when cell
  outputs are empty due to Safe preview on an already-open notebook.
---

# Pluto workflow (cell editing)

Live reactive session — not a `.jl` file to patch. See [pluto-mental-model.md](reference/pluto-mental-model.md) for Pluto semantics.

## Prerequisites

Notebook open in Glass at `http://127.0.0.1:1234/edit?id=<notebook_id>`. If not bootstrapped, use **pluto-session** first.

## Find the notebook (browser first)

| Priority | Source |
|----------|--------|
| 1 | Design Mode (**⌘⇧D**) click → `resolve_pluto_context` → `read_cell` |
| 2 | Glass URL `/edit?id=<notebook_id>` |
| 3 | `list_notebooks` — only when no browser context |

## Edit loop

```
read → stage (run_after=false) → submit_changes → read (verify)
```

**Safe preview:** still edit; remind user outputs won't update until **Run notebook code** in Glass. See [safe-preview.md](reference/safe-preview.md).

**Cell structure / parse errors:** **pluto-semantics** — [cell-structure.md](../pluto-semantics/reference/cell-structure.md).

## REQUIRED chain

- Bootstrap → **pluto-session**
- Cell layout, `@bind`, `pluto_multi_expression` → **pluto-semantics**

## Common mistakes

| Mistake | Fix |
|---------|-----|
| `list_notebooks` before browser context | Design Mode or Glass URL |
| Edit without `read_cell` | Read first (MCP enforces) |
| `run_all_cells` in safe preview | Direct user to Glass button |
| End turn with staged edits | `submit_changes` first |

## Additional resources

- **Pluto mental model:** [reference/pluto-mental-model.md](reference/pluto-mental-model.md)
- **Safe preview detect/remind:** [reference/safe-preview.md](reference/safe-preview.md)
- **Design Mode + `resolve_pluto_context`:** [reference/design-mode.md](reference/design-mode.md)
- **Full edit pipeline:** [reference/edit-loop.md](reference/edit-loop.md)
- **Error fields + kinds:** [reference/errors.md](reference/errors.md)
- **Canonical MCP tool names:** [reference/tools.md](reference/tools.md)
- **Notebook cell structure:** [pluto-semantics/reference/cell-structure.md](../pluto-semantics/reference/cell-structure.md)
