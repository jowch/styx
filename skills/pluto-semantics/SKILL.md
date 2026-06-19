---
name: pluto-semantics
description: >-
  Use when fixing pluto_multi_expression or extra-token parse errors,
  deciding begin/end wrap vs splitting cells, placing @bind, or reasoning
  about Pluto reactivity and cell execution order.
---

# Pluto cell semantics

## One expression per cell (critical)

Each code cell = **exactly one Julia expression**. Multiple statements → `pluto_multi_expression` or `extra token after end of expression`.

### Fix errors: wrap `begin`/`end` (default)

```julia
begin
    using Plots
    plot(sin, 0, 2pi)
end
```

Default to **`begin`/`end`** in the **same cell** when fixing errors. Split only when separate reactive steps are intended.

Use **`let`/`end`** when temporaries must not become notebook globals.

## Quick rules

- `@bind` must be the **returning expression** (last in cell, or inside `md"…"`)
- Visual `cell_order` ≠ execution order — use `read_notebook_code`
- `error.fixes` order: `wrap_begin_end` first, `split_cells` second

## REQUIRED chain

- Session bootstrap → **pluto-session**
- MCP edit pipeline → **pluto-workflow**

## Additional resources

- **Full grammar + `@bind`:** [reference/grammar.md](reference/grammar.md)
- **Reactivity + order:** [reference/reactivity.md](reference/reactivity.md)
- **Error kinds:** [reference/error-kinds.md](reference/error-kinds.md)
- **Pluto.jl source citations:** [reference/pluto-sources.md](reference/pluto-sources.md)
- Human-readable mirror: `docs/pluto-semantics.md`
