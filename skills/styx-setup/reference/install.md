# Install Styx (local plugin)

Styx installs as a **Cursor 3 local plugin** at `~/.cursor/plugins/local/styx/`. No other agent harness (Claude Code, Codex, etc.) is required.

## 1. Install Julia

Styx requires **Julia 1.11 or newer** on your system `PATH` (`[sources]` in the plugin `Project.toml` needs Julia 1.11+).

- **Download:** https://julialang.org/downloads/
- **macOS:** `brew install julia` (or use the official `.dmg`)
- **Windows:** use the installer and check **Add Julia to PATH**
- **Linux:** official binaries or your distro; ensure `julia --version` works in a terminal

## 2. Install Styx

**One line** (fresh install or update) — installs the **latest tagged release**; `STYX_REF=main` for the development tip, `STYX_REF=<tag>` to pin one:

```bash
curl -fsSL https://raw.githubusercontent.com/jowch/styx/main/scripts/install.sh | bash
```

Optional historical pin (0.1.0 tag only):

```bash
STYX_REF=v0.1.0 curl -fsSL https://raw.githubusercontent.com/jowch/styx/main/scripts/install.sh | bash
```

Plugin `Project.toml` pins PlutoMCP to a **commit SHA** on [jowch/PlutoMCP.jl](https://github.com/jowch/PlutoMCP.jl) (not floating `main`). After updating Styx, see [Update](#update) if the pin changed.

**Already cloned the repo:**

```bash
./scripts/install-styx.sh
# or update only:
./scripts/update.sh
```

## 3. Enable in Cursor

1. **Reload Window** — Cmd+Shift+P → **Developer: Reload Window**
2. **Settings → MCP** → enable **pluto** (bundled with Styx)
3. Confirm **Settings → Plugins → Installed** lists **Styx**

First MCP connect downloads **PlutoMCP.jl** into the plugin Julia environment (network; may take a few minutes).

## 4. Verify

```bash
julia --version   # must be 1.11+
```

In Cursor chat: **"Run Styx doctor"** — the agent runs `scripts/styx-doctor.sh`.

## 5. Start using Pluto

Say **"I want to work on my Pluto notebooks"**. The agent starts Pluto when you ask — not at Cursor launch.

- **No notebook named:** landing page in Glass → you pick a notebook
- **Specific file:** name the `.jl` path → agent opens it (safe preview by default)

Design Mode (**⌘⇧D**) → click a cell → describe edits.

## Remote SSH

Cursor forwards ports when Pluto listens on the host. Install Julia **on the SSH machine**, enable Styx, then ask to work on notebooks — the agent starts Pluto **there**. MCP uses host `pluto_url`; Agents Glass resolves the laptop origin via remember → same-port probe → Ports ask only if needed. Details: `skills/pluto-session/reference/remote-ssh.md`.

## Update

Cursor does **not** auto-update local plugins under `~/.cursor/plugins/local/`.

**Refresh plugin files** (same as install — either works):

```bash
curl -fsSL https://raw.githubusercontent.com/jowch/styx/main/scripts/install.sh | bash
```

```bash
# From a clone:
./scripts/update.sh
```

`update.sh` calls `install-styx.sh --update`. The installer preserves `.julia-env-instantiated`, so plugin files refresh but the Julia / PlutoMCP env is **not** re-resolved by default.

**Force Julia / PlutoMCP re-resolve** when the pinned PlutoMCP SHA in `Project.toml` changed (or MCP looks stale after upgrade):

```bash
cd ~/.cursor/plugins/local/styx
rm -f .julia-env-instantiated Manifest.toml
PLUTOMCP_ENV_FORCE=1 ./scripts/ensure-julia-env.sh
```

(`PLUTOMCP_ENV_FORCE=1` alone also bypasses the marker skip in `ensure-julia-env.sh`; wiping the marker and `Manifest.toml` is the reliable full refresh.)

After updating:

1. **Reload Window**
2. Toggle **pluto** MCP off/on if new MCP tools were added

Check for updates: `~/.cursor/plugins/local/styx/scripts/styx-doctor.sh --check-updates` (or ask the agent to run Styx doctor with update check).

## Uninstall

**Preferred (IDE):** **Settings → Plugins → Installed → Styx → Uninstall**, then **Reload Window**.

Local plugins should appear under Installed after install. If **Uninstall** redirects to Rules/Skills instead of removing the plugin (known Cursor bug for some imported plugins), either:

- Toggle Styx **off** in Settings → Plugins, or
- Remove the folder manually: `rm -rf ~/.cursor/plugins/local/styx/` then **Reload Window**

Disable **pluto** in **Settings → MCP** if it still appears after uninstall.

Styx does not remove Julia packages from `~/.julia/` (shared with other Julia work).

## Troubleshooting

| Problem | What to do |
|---------|------------|
| Styx missing from Plugins | Wrong path — must be `~/.cursor/plugins/local/styx/.cursor-plugin/plugin.json`, not under `cache/` |
| MCP won't connect | Install Julia, Reload Window, re-enable **pluto** |
| Slow first start | Normal — Julia is downloading and precompiling PlutoMCP |
| Outputs don't update | Click **Run notebook code** in Glass (safe preview) |
| Plugin hidden in Settings | **Include third-party Plugins…** toggle can hide local plugins in some builds — turn on and Reload Window |

Contributors: `./scripts/sync-local-plugin.sh` copies this repo into the same local path for dev iteration. Lifecycle validation and other maintainer scripts stay repo-only (see README **Development**).
