# pluto-cursor-bridge

Bridge Pluto.jl notebooks to Cursor agent workflows via [PlutoMCP.jl](https://github.com/jowch/PlutoMCP.jl) and browser click context.

## What this is

Users click code or output in a Pluto notebook; the bridge resolves `cell_id`, packages context, and hands it to a Cursor agent that reads/edits/runs cells through MCP.

## Docs

- **[Decision record](docs/DECISIONS.md)** — running log of what we decided and why
- **PlutoMCP fork `AGENTS.md`** — MCP tool semantics (stage-first, projections, naming)

## Quick reference

- MCP endpoint: `http://localhost:2346/sse`
- DOM resolution: `event.target.closest("pluto-cell")`
- Plugin install target: `~/.cursor/plugins/local/pluto-cursor-bridge/`
