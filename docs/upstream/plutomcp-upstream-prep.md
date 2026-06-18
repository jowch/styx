# PlutoMCP upstream prep (2026-06-17)

Target: [mthelm85/PlutoMCP.jl](https://github.com/mthelm85/PlutoMCP.jl)  
Fork: [jowch/PlutoMCP.jl](https://github.com/jowch/PlutoMCP.jl)

## Issues

| # | Title |
|---|-------|
| [#4](https://github.com/mthelm85/PlutoMCP.jl/issues/4) | Structural MCP edits do not sync `cell_order` to browser |
| [#5](https://github.com/mthelm85/PlutoMCP.jl/issues/5) | Expose `require_secret_for_access` on `serve()` / `connect()` |

## Pull requests

| # | Branch | Version | Notes |
|---|--------|---------|-------|
| [#6](https://github.com/mthelm85/PlutoMCP.jl/pull/6) | `fix/cell-order-browser-sync` | 1.1.9 | Fixes #4 — `Tools.jl`, `PlutoMCP.jl`, tests |
| [#7](https://github.com/mthelm85/PlutoMCP.jl/pull/7) | `feat/require-secret-kwarg` | 1.1.10 | Fixes #5 — stacks #6; rebase onto `main` after #6 merges |

## Merge order

1. Review and merge **#6** (cell_order browser sync + `using Pluto`).
2. Rebase **#7** onto upstream `main` if needed, then merge (kwarg only).

## Fork-local (not upstreamed)

- `.gitignore` (`reference/`, `.cursor/hooks/state/`)
- `AGENTS.md`
