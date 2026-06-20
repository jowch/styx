---
name: styx-setup
description: >-
  Use when the user installs Styx, asks how to set up Pluto in Cursor, sees pluto
  MCP errors, Julia not found, or first-run / onboarding questions before notebook work.
---

# Styx setup and onboarding

**Install:** one-liner `curl -fsSL https://raw.githubusercontent.com/jowch/styx/main/scripts/install.sh | bash` → Reload Window → enable **pluto** MCP. Details: [reference/install.md](reference/install.md).

## Prerequisites

| Requirement | Notes |
|-------------|--------|
| **Julia 1.9+** on `PATH` | https://julialang.org/downloads/ |
| **Cursor** with Plugins + MCP | Enable bundled **pluto** MCP after install |
| Network (first run) | First MCP connect installs PlutoMCP.jl into the plugin env |

## REQUIRED checks

Run (or ask user to run in terminal):

```bash
"${CURSOR_PLUGIN_ROOT}/scripts/styx-doctor.sh"
```

If Julia is missing, **stop** and give install steps from doctor output — do not ask the user to run `pluto-serve.sh` or clone repos.

## After install (user checklist)

1. **Reload Window** (Cursor)
2. **Settings → MCP** → enable **pluto** (from Styx)
3. Wait for first connect (may take 1–2 min while PlutoMCP installs)
4. Say **"I want to work on my notebooks"** or use **styx-setup** / **pluto-notebooks**

## Common issues

Run `styx-doctor.sh` first. Full troubleshooting: [reference/install.md](reference/install.md).

## Notebook work

Once setup passes → **pluto-session** (not this skill).

## Additional resources

- User install guide: [reference/install.md](reference/install.md)
