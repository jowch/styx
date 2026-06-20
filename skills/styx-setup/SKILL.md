---
name: styx-setup
description: >-
  Use when the user installs Styx, asks how to set up Pluto in Cursor, sees pluto
  MCP errors, Julia not found, or first-run / onboarding questions before notebook work.
---

# Styx setup and onboarding

Marketplace install is **Settings → Plugins → search Styx → Install**. No shell scripts required for normal use.

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

| Symptom | Fix |
|---------|-----|
| pluto MCP red / won't start | `styx-doctor.sh`; install Julia; Reload Window |
| `julia: command not found` | Install Julia, add to PATH, Reload Window |
| New tool missing (e.g. `allow_execution`) | Toggle **pluto** MCP off/on or Reload Window (tools/list cache) |
| Ports busy | Quit other Pluto sessions; toggle pluto MCP off before validation scripts |

## Notebook work

Once setup passes → **pluto-session** (not this skill).

## Additional resources

- User install guide: [reference/install.md](reference/install.md)
