---
description: Open Pluto or a notebook in Agents Glass (after session is running)
---

# Pluto open

Open the Pluto UI in **Agents Glass**. If Pluto is not running, use **pluto-notebooks** first.

## Steps

1. `pluto_session_status` — if stopped, follow **pluto-session** skill.
2. Open in Glass:
   - Home: `http://127.0.0.1:1234/`
   - Notebook: `http://127.0.0.1:1234/edit?id=<notebook_id>` from `list_notebooks` or `open_notebook`

Path B opens in **Safe preview** by default — remind the user that edits won't execute until they click **Run notebook code** in Glass. If they ask you to run, point them to that button (MCP cannot).

Use `open_resource` when available. Not `cursor-ide-browser` MCP.
