# Styx

**Styx** bridges [Pluto.jl](https://github.com/fonsp/Pluto.jl) notebooks and Cursor agent workflows via [PlutoMCP.jl](https://github.com/jowch/PlutoMCP.jl) and Glass Design Mode click context.

Repository: [github.com/jowch/styx](https://github.com/jowch/styx)

## Install

**Prerequisites:** Cursor 3 (Plugins + MCP) and **Julia 1.9+** on your `PATH`.

```bash
curl -fsSL https://raw.githubusercontent.com/jowch/styx/main/scripts/install.sh | bash
```

Then **Reload Window** → **Settings → MCP** → enable **pluto**.

Say **"Run Styx doctor"** or **"styx-setup"** to verify. **Update:** re-run the same command. **Uninstall:** Settings → Plugins → Styx → Uninstall.

Full guide: [skills/styx-setup/reference/install.md](skills/styx-setup/reference/install.md)

## Quick start

1. Complete [Install](#install).
2. Say **"I want to work on my notebooks"** — the agent starts Pluto and opens the landing page in Glass; you pick a notebook (or name a `.jl` for direct open).
3. **Next prompt:** ⌘⇧D (Design Mode) → click a cell → describe edits.

Pluto starts only when you request notebook work, not at Cursor launch.

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

## Workflow

```
User requests notebooks → pluto-session
  → start_pluto_session → choose notebook → open Glass
  → Design Mode click → pluto-workflow (edit cells)
```

Skills hold the full bootstrap and edit flows. MCP server key: **`pluto`**.

## Click context (Design Mode)

Toggle **Cmd+Shift+D** in Agents Glass, click a cell, send a prompt. The hook `prompt` includes `dom_path` with `pluto-notebook#…` and `pluto-cell#…`. The agent calls **`resolve_pluto_context`** and **`read_cell`**.

Glass navigation uses **`cursor-ide-browser`** in the Agents Window — not `plugin-browse-browser`.

## Development

Local install (Cursor rejects symlinks for plugins):

```bash
./scripts/sync-local-plugin.sh   # copy → ~/.cursor/plugins/local/styx/
# Developer: Reload Window
```

Release-shaped tree:

```bash
./scripts/package-plugin.sh    # → dist/styx/
```

Optional local fork (non-sibling path): `echo 'PLUTOMCP_SOURCE=/path/to/PlutoMCP.jl' > .env.dev` in the plugin root (gitignored).

See [CHANGELOG.md](CHANGELOG.md) for release notes. Validation: `eval/run_reference.jl --all --strict-trace` and `scripts/validate-pluto-lifecycle.sh`.
