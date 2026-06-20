# Install Styx (marketplace)

## 1. Install Julia

Styx requires **Julia 1.9 or newer** on your system `PATH`.

- **Download:** https://julialang.org/downloads/
- **macOS:** `brew install julia` (or use the official `.dmg`)
- **Windows:** use the installer and check **Add Julia to PATH**
- **Linux:** official binaries or your distro; ensure `julia --version` works in a terminal

## 2. Install the plugin

1. Open **Cursor Settings → Plugins**
2. Search **Styx** in the marketplace (or browse https://cursor.com/marketplace)
3. Click **Install**
4. **Reload Window**

## 3. Enable MCP

1. **Settings → MCP**
2. Enable the **pluto** server (bundled with Styx)
3. First connection installs **PlutoMCP.jl** into the plugin's Julia environment (needs network; can take a few minutes)

## 4. Verify

In a terminal:

```bash
julia --version   # must be 1.9+
```

In Cursor chat, ask: **"Run Styx doctor"** — the agent runs `scripts/styx-doctor.sh`.

## 5. Start using Pluto

Say **"I want to work on my Pluto notebooks"**. The agent starts Pluto when you ask — not at Cursor launch.

- **No notebook named:** landing page in Glass → you pick a notebook
- **Specific file:** name the `.jl` path → agent opens it (safe preview by default)

Design Mode (**⌘⇧D**) → click a cell → describe edits.

## Troubleshooting

| Problem | What to do |
|---------|------------|
| MCP won't connect | Install Julia, Reload Window, re-enable **pluto** |
| Slow first start | Normal — Julia is downloading and precompiling PlutoMCP |
| Outputs don't update | Click **Run notebook code** in Glass (safe preview) |

Contributors: local dev copy via `scripts/sync-local-plugin.sh` (not required for marketplace users).
