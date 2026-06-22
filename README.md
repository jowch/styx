# Styx

<video src="assets/hero-demo.mp4" autoplay loop muted playsinline width="100%"></video>

Edit live [Pluto.jl](https://github.com/fonsp/Pluto.jl) notebooks from [Cursor](https://cursor.com) — click a cell in Glass Design Mode, describe the change, and the agent stages it via [PlutoMCP.jl](https://github.com/jowch/PlutoMCP.jl).

Repository: [github.com/jowch/styx](https://github.com/jowch/styx)

## Install

**Prerequisites:** Cursor 3 (Plugins + MCP) and **Julia 1.11+** on your `PATH`.

```bash
curl -fsSL https://raw.githubusercontent.com/jowch/styx/main/scripts/install.sh | bash
```

Then **Reload Window** → **Settings → MCP** → enable **pluto**.

Say **"Run Styx doctor"** or **"styx-setup"** to verify. **Update:** re-run the same command. **Uninstall:** Settings → Plugins → Styx → Uninstall.

Full guide: [skills/styx-setup/reference/install.md](skills/styx-setup/reference/install.md)

## Demo notebook

Try the included demo after install:

- **File:** [`examples/styx-demo.jl`](examples/styx-demo.jl) — reactive sinc plot with a range slider, laid out for agent edits.
- **Open:** ask the agent to *"open the Styx demo notebook"*, or pick it from the Pluto landing page in Glass.
- **Safe preview:** click **Run notebook code** in Glass if widgets or plots look stale.

Then **⌘⇧D** (Design Mode) → click the plot cell → describe an edit (e.g. change color or title).

## Quick start

1. Complete [Install](#install).
2. Open a notebook in Glass — the demo above, your own `.jl`, or say *"I want to work on my notebooks"* to start Pluto and choose one.
3. **⌘⇧D** → click a cell → describe edits in chat. The agent reads the cell, stages changes, and runs them when you ask.

Pluto starts when you request notebook work, not at Cursor launch.

## What ships

| Component | Role |
|-----------|------|
| `examples/styx-demo.jl` | Demo notebook (reactive plot + agent cell layout) |
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
Open notebook in Glass → Design Mode click → pluto-workflow (read → stage → submit_changes)
```

On first notebook intent, the agent runs **pluto-session** (`start_pluto_session`, open Glass). Skills hold the full bootstrap and edit flows. MCP server key: **`pluto`**.

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

**Repo-only scripts** (not copied by install/package): `pluto-serve.sh`, `pluto-lifecycle-preflight.sh`, `validate-pluto-lifecycle.sh`, `record-hero-demo.md` (hero video recording guide). Fresh Julia lockfile: `rm -f .julia-env-instantiated Manifest.toml && PLUTOMCP_ENV_FORCE=1 ./scripts/ensure-julia-env.sh`.

Optional local fork (non-sibling path): `echo 'PLUTOMCP_SOURCE=/path/to/PlutoMCP.jl' > .env.dev` in the plugin root (gitignored).

See [CHANGELOG.md](CHANGELOG.md) for release notes. **Contributors:** `eval/run_reference.jl --all --strict-trace` and `scripts/validate-pluto-lifecycle.sh` (toggle **pluto** MCP off first).
