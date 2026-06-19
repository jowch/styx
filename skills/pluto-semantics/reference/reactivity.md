# Pluto reactivity

## Module scope

- All cells share one notebook module scope (`workspace#N`, bumped on reactive runs).
- Edit upstream → downstream cells re-run automatically.
- Deleting/overwriting upstream definitions removes stale globals.

## Order semantics

| Concept | Source | Effect |
|---------|--------|--------|
| **Visual order** | `cell_order` | UI layout only |
| **Execution order** | dependency graph / topological sort | What runs when |
| **Disabled cells** | `metadata["disabled"]` | Cell + downstream skipped |

Use `read_notebook_code` for execution/dependency order. Use `get_cell_order` for visual placement (`add_cell` / `move_cell`).

## Multiple definitions

Two cells defining the same global → `MultipleDefinitionsError` by default.

## Cycles

Non-function dependency cycles → cyclic reference error.

## MCP edit semantics

| Tool | Behavior |
|------|----------|
| `edit_cell` | Replaces entire body; default `run_after=false` |
| `submit_changes` | Batch run staged cells (Cmd+S) |
| `validate_cell` | Pre-check; returns `multi_expression` when invalid |

## Pluto source

- `src/evaluation/Run.jl` — `run_reactive!`, topological execution
- `src/evaluation/RunBonds.jl` — bond changes → downstream re-run
- `PlutoDependencyExplorer` — dependency graph, topological order
