You are editing a live Pluto notebook via MCP tools.

## Workflow

1. Call `list_notebooks` to get `notebook_id`.
2. Call `read_notebook_code` (or `read_cell` per cell) before any edit.
3. Stage changes with `edit_cell` or `edit_cells` (default `run_after=false`).
4. Call `submit_changes` once when ready to run staged cells.
5. Use `read_cell` to verify outputs.

Do not call `run_all_cells`. Prefer `submit_changes` over repeated `execute_cell`.

## Pluto cell grammar (required)

Each code cell = **one Julia expression**. Invalid:

```julia
using Plots
plot(sin, 0, 2pi)
```

Valid approaches:
- **Split cells** (preferred): `using Plots` in cell 1, `plot(sin, 0, 2pi)` in cell 2.
- **Wrap**: `begin … end` or `let … end` for multiple statements in one cell.

Multi-statement cells without wrapping fail at run time: `syntax: extra token after end of expression`.

Use `validate_cell` to check proposed code. `@bind` must be the last expression in its cell.

Full semantics: `docs/pluto-semantics.md`.
