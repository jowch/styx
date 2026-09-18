---
description: Boot Pluto (+ optional notebook) via control bridge — no Glass; print welcome URL
---

# Styx start

Programmatic session boot (**no Agents Glass**). Prefer the script; MCP tools are the fallback.

## Prefer script

From the plugin root (or repo):

```bash
scripts/styx-start.sh                  # start; open ./analysis.jl if present
scripts/styx-start.sh --welcome        # start only
scripts/styx-start.sh --path note.jl   # start + open_notebook
scripts/styx-start.sh --path note.jl --run
```

Prints `welcome_url=` from exact `pluto_session_status.pluto_url` (one host per session — do not rewrite `localhost` ↔ `127.0.0.1`). User opens that landing URL and clicks the notebook. **Do not** navigate Glass to cold `/edit?id=` after MCP open.

## Agent fallback (no script / no binding)

1. `start_pluto_session` (by name)
2. Optional `open_notebook(path=…)` if the user named a file
3. Tell the user the **welcome** URL from status — exact host string
4. **Never** call `cursor-ide-browser` / `plugin-browse-browser` for this command

Full notes: [skills/pluto-session/reference/styx-start.md](../skills/pluto-session/reference/styx-start.md). Glass already open but broken → **styx-reconnect**.
