# Styx

**Styx** bridges [Pluto.jl](https://github.com/fonsp/Pluto.jl) notebooks and Cursor agent workflows via [PlutoMCP.jl](https://github.com/jowch/PlutoMCP.jl) and Glass Design Mode click context.

Repository: [github.com/jowch/styx](https://github.com/jowch/styx)

## Install

### Prerequisites

- **Cursor 3** with Plugins and MCP enabled
- **Julia 1.9+** on your system `PATH` — [julialang.org/downloads](https://julialang.org/downloads/)

### One-line install (local plugin)

```bash
curl -fsSL https://raw.githubusercontent.com/jowch/styx/main/scripts/install.sh | bash
```

Then **Reload Window** → **Settings → MCP** → enable **pluto**.

Say **"Run Styx doctor"** in chat to verify setup, or **"styx-setup"** for the full checklist.

**Update:** re-run the same command, or `./scripts/update.sh` from a clone.

**Uninstall:** **Settings → Plugins → Installed → Styx → Uninstall**, then Reload Window.

Full steps: [skills/styx-setup/reference/install.md](skills/styx-setup/reference/install.md)

### Without Julia

If Julia is not installed, the **pluto** MCP server will not start. Install Julia first, then Reload Window. The agent's **styx-setup** skill walks through this — you never need to run shell scripts manually.

## Quick start

1. Complete [Install](#install) above.
2. Say **"I want to work on my notebooks"** — agent starts Pluto and opens the **landing page** in Glass; you pick a notebook (or name a specific `.jl` for direct open).
3. **Next prompt:** ⌘⇧D → click a cell → describe edits.

Pluto starts only when you request notebook work (not at Cursor launch).

## What ships

| Component | Role |
|-----------|------|
| `skills/styx-setup` | Install, Julia prerequisite, MCP troubleshooting |
| `skills/pluto-session` | Agent bootstrap: start Pluto, choose notebook, open Glass |
| `skills/pluto-workflow`, `pluto-semantics` | Cell editing and grammar |
| `commands/pluto-notebooks`, `styx-setup` | User entry points |
| `mcp.json` + launcher | Deferred Pluto MCP (`connect()` until notebook intent) |
| `rules/pluto-notebook-workflow.mdc` | Short guardrails |
| `hooks/` | Read-before-edit, `pending_run` warning, Design Mode hints |
| `scripts/styx-doctor.sh` | Health check (Julia, env, ports) |

## Workflow (D15)

```
User requests notebooks → pluto-session (agent)
  → start_pluto_session → choose notebook → open Glass
  → Design Mode click → pluto-workflow (edit cells)
```

See [docs/specs/pluto-lifecycle.md](docs/specs/pluto-lifecycle.md) for the full spec.

MCP server key: **`pluto`**

## Development

Local install (Cursor rejects symlinks for plugins):

```bash
./scripts/sync-local-plugin.sh   # copy → ~/.cursor/plugins/local/styx/
# Developer: Reload Window
```

Release-shaped tree for marketplace review:

```bash
./scripts/package-plugin.sh    # → dist/styx/
```

Optional: copy `.env.dev.example` → `.env.dev`, set `PLUTOMCP_SOURCE` to your PlutoMCP.jl fork.

**Release pin:** `STYX_REF=v0.1.0 curl -fsSL …/install.sh | bash`

## Planning (contributors)

| Doc | Purpose |
|-----|---------|
| [PLAN.md](docs/PLAN.md) | Phase map |
| [DECISIONS.md](docs/DECISIONS.md) | Decision log |
| [CHANGELOG.md](CHANGELOG.md) | Release notes |

## Click context (Design Mode)

Toggle **Cmd+Shift+D** in Agents Glass, click a cell, send a prompt. Hook `prompt` includes `dom_path` with `pluto-notebook#…` and `pluto-cell#…`. Agent calls MCP **`resolve_pluto_context`** and **`read_cell`**.

Glass navigation: **`cursor-ide-browser`** in the Agents Window — not `plugin-browse-browser`.
