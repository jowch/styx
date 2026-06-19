# Pluto mental model (for agents)

Curated from Pluto.jl source and docs. Pluto is **not** a file you patch — it is a **reactive Julia session**.

## Core facts

- Each **cell** is one node in a dependency graph; cells share one notebook module scope.
- Pluto owns parsing, dependency analysis, execution, persistence, and browser sync.
- Notebooks save as `.jl` files, but **runtime state is in-memory** — re-read before edit.
- MCP writes **server state**; the browser editor has a separate draft buffer (last-write-wins).
- **No hidden workspace state:** Pluto deletes/redefines globals on reactive runs (`bump_workspace_module`).
- **Visual order ≠ execution order** — use `read_notebook_code` (execution order) or dependency graph.

## What triggers re-run

Editing a cell re-runs that cell and all **downstream** dependents in topological order. Bond value changes also trigger downstream re-run.

## Agent anti-patterns (Pluto warns about these)

1. Patching `.jl` files directly — bypasses dependency analysis and browser sync
2. Assuming visual `cell_order` = execution order
3. Defining the same global in multiple cells — `MultipleDefinitionsError`
4. Expecting Jupyter-style mutable kernel state — Pluto deletes stale globals
5. Ignoring Safe preview — staged edits won't execute until user runs in Glass

## Pluto source citations

| Path (Pluto 0.20.x) | Topic |
|---------------------|-------|
| `src/analysis/Parse.jl` | `parse_custom`, `is_single_expression`, multi-expression error |
| `src/evaluation/Run.jl` | `run_reactive!`, `will_run_code`, `set_output!` |
| `src/notebook/Notebook.jl` | `ProcessStatus`, `cell_order` |
| `src/webserver/SessionActions.jl` | Safe preview gate on `open` |
| `src/runner/PlutoRunner/src/bonds.jl` | `@bind` macro, `Bond` HTML |

Full citations: **pluto-semantics** → [pluto-sources.md](../../pluto-semantics/reference/pluto-sources.md).
