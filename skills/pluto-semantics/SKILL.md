---
name: pluto-semantics
description: >-
  Use when structuring Pluto notebook cells, fixing pluto_multi_expression
  errors, placing @bind widgets, or choosing begin/end vs let/end vs cell splits.
---

# Pluto cell semantics

## Parse rule (hard)

Each cell = **exactly one Julia expression**. Bare multiple statements → `pluto_multi_expression`.

## Structure defaults (agent authoring)

| Primitive | Shape |
|-----------|--------|
| **imports_cell** | `begin; using …; end` — one dedicated early cell for all packages |
| **widget_cell** | `@bind var Widget(...)` or `md"…$(@bind …)…"` — one bond per reactive input |
| **compute_cell** | `begin … end` — multi-statement blocks that re-run together |
| **scoped_cell** | `let … end` — locals that must not become globals |
| **output_cell** | Single expression display (`plot`, `md`, bare value) |

**Default:** prefer **`begin`/`end`** inside a cell for a conceptual block instead of many single-line cells.

**Still split** at reactive boundaries: imports | widgets | distinct downstream steps.

Full patterns + decision table: [reference/cell-structure.md](reference/cell-structure.md). Curated layouts: [reference/agent-examples.md](reference/agent-examples.md).

## `@bind`

- Must be the **returning expression** of its cell (standalone, in `md"…"`, or last in `begin`/`end`).
- Bound variable is consumed in **downstream** cells — not followed by more statements unless wrapped.

## Fixing `pluto_multi_expression`

Wrap in **`begin`/`end`** in the same cell **or** split at reactive boundaries — see [agent-examples.md](reference/agent-examples.md) ex. 8. Prefer wrap for minimal diff; split when separate reactive steps are intended.

## REQUIRED chain

- Session bootstrap → **pluto-session**
- MCP edit pipeline → **pluto-workflow**

## Additional resources

- **Structure patterns:** [reference/cell-structure.md](reference/cell-structure.md)
- **Curated examples:** [reference/agent-examples.md](reference/agent-examples.md)
- **Parse grammar:** [reference/grammar.md](reference/grammar.md)
- **Reactivity + order:** [reference/reactivity.md](reference/reactivity.md)
- **Error kinds:** [reference/error-kinds.md](reference/error-kinds.md)
- **Pluto.jl source citations:** [reference/pluto-sources.md](reference/pluto-sources.md)
