# Pluto.jl source citations

Curated references for agent skill authors. Package version at research time: **Pluto 0.20.28**.

| Path | Description |
|------|-------------|
| `src/analysis/Parse.jl` | `parse_custom`, `is_single_expression`, `preprocess_expr`, multi-expression error |
| `src/runner/PlutoRunner/src/bonds.jl` | `@bind` macro, `Bond`, `create_bond`, HTML `<bond>` rendering |
| `src/evaluation/Run.jl` | `run_reactive!`, `update_save_run!`, `will_run_code`, `set_output!` |
| `src/evaluation/RunBonds.jl` | Bond value changes → reactive downstream re-run |
| `src/evaluation/WorkspaceManager.jl` | `bump_workspace_module`, workspace lifecycle |
| `src/notebook/Notebook.jl` | `Notebook` struct, `ProcessStatus`, `cell_order` |
| `src/notebook/Cell.jl` | `Cell` struct, `cell_id`, disabled/skip metadata |
| `src/webserver/SessionActions.jl` | Safe preview gate on `open`, `execution_allowed` |
| `src/webserver/Router.jl` | HTTP routes, `execution_allowed` query param |
| `src/webserver/Dynamic.jl` | Notebook state payload, `restart_process`, Safe preview prerender |
| `src/analysis/is_just_text.jl` | Which cells can run in Safe preview |
| `sample/Interactivity.jl` | `@bind` patterns and pedagogy |
| `sample/Getting started.jl` | One-expression-per-cell pedagogy |

Local package path (Julia depot): `~/.julia/packages/Pluto/*/`

Upstream: [github.com/JuliaPluto/Pluto.jl](https://github.com/JuliaPluto/Pluto.jl)

## URL patterns (browser)

| URL | Purpose |
|-----|---------|
| `/` | Landing |
| `/edit?id=<notebook_id>` | **Canonical editor URL** |
| `/open?path=<abs-path>&execution_allowed=<bool>` | Open local file |

Plain `/<notebook_id>` alone is not a documented route.
