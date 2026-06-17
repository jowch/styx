# pluto-cursor-bridge

Bridge Pluto.jl notebooks to Cursor agent workflows via [PlutoMCP.jl](https://github.com/jowch/PlutoMCP.jl) and browser click context.

## Planning (read before building)

| Doc | Purpose |
|-----|---------|
| **[PLAN.md](docs/PLAN.md)** | Integrated phase map, architecture, build sequence |
| **[DECISIONS.md](docs/DECISIONS.md)** | Running decision log (what we decided and why) |
| **[specs/](docs/specs/)** | Detailed specs per phase |

Fork MCP semantics: PlutoMCP.jl `AGENTS.md`.

## Quick reference

- MCP endpoint: `http://localhost:2346/sse`
- DOM resolution: `composedPath()` → `PLUTO-CELL`
- Plugin install: `~/.cursor/plugins/local/pluto-cursor-bridge/`
