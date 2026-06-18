---
name: pluto-semantics
description: >-
  Pluto.jl cell grammar and reactivity — one expression per cell, begin/end wraps,
  @bind rules, multi_expression errors. Use when fixing parse errors, splitting cells,
  or reasoning about Pluto reactivity.
---

# Pluto cell semantics

## One expression per cell (critical)

Each code cell = **exactly one Julia expression**.

**Invalid:**
```julia
using Plots
plot(sin, 0, 2pi)
```

Pluto returns `pluto_multi_expression` or `syntax: extra token after end of expression`. `error.boundaries` marks where extra statements start.

### Fix errors: wrap `begin`/`end` (default)

```julia
begin
    using Plots
    plot(sin, 0, 2pi)
end
```

Use **`let`/`end`** when temporaries must not become notebook globals.

When a user asks to **fix** a multi-expression error, default to **`begin`/`end`** in the **same cell** unless separate reactive steps are intended.

### Split cells (intentional reactive steps)

| Cell | Code |
|------|------|
| 1 | `using Plots` |
| 2 | `plot(sin, 0, 2pi)` |

## New code structure

| Pattern | Guidance |
|---------|----------|
| `using` / `import` | Own cell at top |
| Constants / inputs | One binding per cell, or one `let` block |
| Derived values | Separate cells |
| Plots | Last expression is displayed |
| `@bind` | **`@bind` must be last** in cell; bound value in next cell |

## Reactivity

- Shared notebook module scope.
- Edit upstream → downstream cells re-run.
- `read_notebook_code` = execution order; `get_cell_order` = visual order.

## MCP edit semantics

| Tool | Behavior |
|------|----------|
| `edit_cell` | Replaces entire body; default `run_after=false` |
| `submit_changes` | Batch run staged cells (Cmd+S) |
| `validate_cell` | Pre-check; returns `multi_expression` when invalid |

## Error kinds

| `error.kind` | Default action |
|--------------|----------------|
| `pluto_multi_expression` | `edit_cell` with `begin`/`end`, then `submit_changes` |
| `runtime` | Read `msg`, fix code |

`error.fixes` order: `wrap_begin_end` first, `split_cells` second.
