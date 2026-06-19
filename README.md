# Styx

**Styx** is a Cursor plugin that bridges [Pluto.jl](https://github.com/fonsp/Pluto.jl) notebooks and Cursor agent workflows via [PlutoMCP.jl](https://github.com/jowch/PlutoMCP.jl) and Glass Design Mode click context.

Repository: [github.com/jowch/styx](https://github.com/jowch/styx)

## Quick start

1. Install the plugin (see **Development** below until marketplace publish).
2. Enable the **pluto** MCP server in Cursor Settings.
3. Say **"I want to work on my notebooks"** — agent starts Pluto and opens the **landing page** in Glass; you pick a notebook there (or name a specific file for direct open).
4. **Next prompt:** ⌘⇧D → click a cell → describe edits.

No shell scripts required (D15). Pluto starts only when you request notebook work.

## What ships

| Component | Role |
|-----------|------|
| `skills/pluto-session` | Agent bootstrap: start Pluto, choose notebook, open Glass |
| `skills/pluto-workflow`, `pluto-semantics` | Cell editing and grammar |
| `commands/pluto-notebooks` | User entry: "work on notebooks" |
| `mcp.json` + launcher | MCP stdio (D15: standalone `connect()` when implemented) |
| `rules/pluto-notebook-workflow.mdc` | Short guardrails |
| `hooks/` | Health gate, read-before-edit, `pending_run` warning |

## Workflow (D15)

```
User requests notebooks → pluto-session (agent)
  → start_pluto_session → choose notebook → open Glass
  → Design Mode click → pluto-workflow (edit cells)
```

See [docs/specs/pluto-lifecycle.md](docs/specs/pluto-lifecycle.md) for full spec and simulated UX.

MCP server key: **`pluto`**

## Development

Local install (Cursor 3.x — symlinks rejected):

```bash
./scripts/sync-local-plugin.sh   # full dev copy → ~/.cursor/plugins/local/styx/
# Developer: Reload Window
```

Release-shaped tree (excludes `eval/`, planning docs):

```bash
./scripts/package-plugin.sh    # → dist/styx/
```

Optional: copy `.env.dev.example` → `.env.dev`, set `PLUTOMCP_SOURCE` to your PlutoMCP.jl fork.

## Planning (contributors)

| Doc | Purpose |
|-----|---------|
| [PLAN.md](docs/PLAN.md) | Phase map |
| [DECISIONS.md](docs/DECISIONS.md) | Decision log |
| [CHANGELOG.md](CHANGELOG.md) | Release notes |

## Click context (Design Mode)

Toggle **Cmd+Shift+D** in Agents Glass, click a cell, send a prompt. Hook `prompt` includes `dom_path` with `pluto-notebook#…` and `pluto-cell#…`. Agent calls MCP **`resolve_pluto_context`** and **`read_cell`**.

Do not use `plugin-browse-browser` for Pluto. Glass: **`cursor-ide-browser`** in Agents Window.
