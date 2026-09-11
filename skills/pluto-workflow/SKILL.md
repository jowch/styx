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

Notebook open in Glass at the session's `pluto_url` (`…/edit?id=<notebook_id>`). Resolve URL from `pluto_session_status` — never assume `:1234`. If not bootstrapped, use **pluto-session** first.

Local Task children use the parent's MCP server; do not curl bridges or run `PlutoMCP.serve()`.

## Find the notebook (browser first)

| Priority | Source |
|----------|--------|
| 1 | Design Mode (**⌘⇧D**) click → `resolve_pluto_context` → `read_cell` |
| 2 | Glass URL `/edit?id=<notebook_id>` |
| 3 | `list_notebooks` — only when no browser context |

## Edit loop

```
read → stage (run_after=false) → submit_changes(wait_for_completion=false) → read (verify)
```

Default **`wait_for_completion=false`** on `submit_changes` for stdio-bound sessions so MCP stays responsive ([issue #3](https://github.com/jowch/styx/issues/3)). Only block when the user explicitly needs a synchronous result and the session is known durable.

**Safe preview:** still edit + `submit_changes(wait_for_completion=false)`. When outputs aren't live, **exit Safe preview yourself** — Glass **Run notebook code** (`browser_click`), or MCP `allow_execution(run_notebook=false)` then re-`submit_changes` / `execute_cell` for staged cells (faster than default full-notebook run). See [safe-preview.md](reference/safe-preview.md).

**Cell structure / parse errors:** **pluto-semantics** — [cell-structure.md](../pluto-semantics/reference/cell-structure.md).

## REQUIRED chain

- Bootstrap → **pluto-session**
- Cell layout, `@bind`, `pluto_multi_expression` → **pluto-semantics**

## Common mistakes

| Mistake | Fix |
|---------|-----|
| `list_notebooks` before browser context | Design Mode or Glass URL |
| Edit without `read_cell` | Read first (MCP enforces) |
| Leave Safe preview on after edits needing outputs | Exit yourself: Glass **Run notebook code**, or `allow_execution(run_notebook=false)` then submit/execute staged cells |
| `run_all_cells` / `execute_cell` before exit | Exit Safe preview first — they do not bypass the gate |
| End turn with staged edits | `submit_changes(wait_for_completion=false)` first |
| `submit_changes(wait_for_completion=true)` on stdio | Prefer `false` — blocking wait can kill in-process Pluto |

## Additional resources

- **Pluto mental model:** [reference/pluto-mental-model.md](reference/pluto-mental-model.md)
- **Safe preview detect/remind:** [reference/safe-preview.md](reference/safe-preview.md)
- **Design Mode + `resolve_pluto_context`:** [reference/design-mode.md](reference/design-mode.md)
- **Full edit pipeline:** [reference/edit-loop.md](reference/edit-loop.md)
- **Error fields + kinds:** [reference/errors.md](reference/errors.md)
- **Canonical MCP tool names:** [PlutoMCP.jl AGENTS.md](https://github.com/jowch/PlutoMCP.jl/blob/main/AGENTS.md)
- **Notebook cell structure:** [pluto-semantics/reference/cell-structure.md](../pluto-semantics/reference/cell-structure.md)
- **Parent/subagent grading:** [../../eval/agent-control/README.md](../../eval/agent-control/README.md)
