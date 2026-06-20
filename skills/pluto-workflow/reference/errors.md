# MCP error fields

## Session bootstrap errors

| Error | Action |
|-------|--------|
| `pluto_not_running` | `start_pluto_session` |
| `notebook_not_found` | Confirm path with user |
| MCP unreachable | Enable **pluto** MCP in Cursor Settings → retry |
| `julia: command not found` / MCP exits immediately | Install Julia 1.9+ (https://julialang.org/downloads/), Reload Window → **styx-setup** |

If cell edits fail before bootstrap, return to **pluto-session** first.

## Cell error fields

| Field | Use |
|-------|-----|
| `error.kind` | e.g. `pluto_multi_expression` |
| `error.hint` | Default fix text |
| `error.boundaries` | Byte positions for splits |
| `error.fixes` | `wrap_begin_end` first, then `split_cells` |

## Error kinds

| `error.kind` | Default action |
|--------------|----------------|
| `pluto_multi_expression` | `edit_cell` with `begin`/`end`, then `submit_changes` |
| `runtime` | Read `msg`, fix code |

## Common mistakes

| Mistake | Fix |
|---------|-----|
| Edit before session bootstrap | **pluto-session** first |
| `list_notebooks` before browser context | Design Mode click or Glass URL |
| Edit without read | `read_cell` first |
| Patch `.jl` on disk | MCP only |
| Forget safe preview reminder | See [safe-preview.md](safe-preview.md) |
| User asks to run notebook | `allow_execution` or direct to **Run notebook code** in Glass |
| Claim `submit_changes` ran cells in safe preview | Remind user to run in Glass |
