# MCP error fields

## Session bootstrap errors

| Error | Action |
|-------|--------|
| `pluto_not_running` | `start_pluto_session` |
| `notebook_not_found` | Confirm path with user |
| MCP unreachable | Enable **pluto** MCP in Cursor Settings → retry |
| `julia: command not found` / MCP exits immediately | Install Julia 1.11+ (https://julialang.org/downloads/), Reload Window → **styx-setup** |
| Glass **“Not yet authenticated”** | Soft reconnect on exact `pluto_url` host (do not swap `localhost`/`127.0.0.1`) — [reconnect.md](../../pluto-session/reference/reconnect.md) / [one host](../../pluto-session/reference/glass-navigation.md#one-host-per-session-localhost-vs-127001) |
| Empty title / **Loading cells…** / stale port | Soft reconnect (landing → click) before hard restart — [reconnect.md](../../pluto-session/reference/reconnect.md) |
| `foreign_session` (409) | Wrong/stale bridge vs this window’s binding — check then **styx-cleanup** — [cleanup.md](../../pluto-session/reference/cleanup.md) |
| `notebook_in_use` / `styx_binding_in_use` / `stale_binding_unrecoverable` | Live peer → use another window; dead peer → check then **styx-cleanup** — [cleanup.md](../../pluto-session/reference/cleanup.md) |
| Doctor: binding present, `/health` nonce mismatch | Stale Styx binding — `styx-check-stale` then optional cleanup — [cleanup.md](../../pluto-session/reference/cleanup.md) |

If cell edits fail before bootstrap, return to **pluto-session** first. Glass/auth/WS drops → **styx-reconnect** / [reconnect.md](../../pluto-session/reference/reconnect.md). One-shot boot + Glass ready → **styx-start** / [styx-start.md](../../pluto-session/reference/styx-start.md).

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
| `pluto_multi_expression` | `edit_cell` with `begin`/`end`, then `submit_changes(wait_for_completion=false)` |
| `runtime` | Read `msg`, fix code |

## Common mistakes

| Mistake | Fix |
|---------|-----|
| Edit before session bootstrap | **pluto-session** first |
| `list_notebooks` before browser context | Design Mode click or Glass URL |
| Edit without read | `read_cell` first |
| Patch `.jl` on disk | MCP only |
| Leave Safe preview on when outputs are needed | Exit yourself: Glass **Run notebook code** or `allow_execution` — [safe-preview.md](safe-preview.md) |
| User asks to run / needs live widgets | Same — agent exits; don't only remind |
| Claim `submit_changes` ran cells while still gated | Exit Safe preview first; then poll for outputs |
