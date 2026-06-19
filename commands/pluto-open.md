---
description: User wants Pluto or a notebook opened in Agents Glass — pluto-session if not running
---

# Pluto open

1. `pluto_session_status` — if stopped, invoke **pluto-session**.
2. Open in Agents Glass (`open_resource` when available; otherwise ask user to open URL):
   - Home: `http://127.0.0.1:1234/`
   - Notebook: `http://127.0.0.1:1234/edit?id=<notebook_id>` (required form; bare `/<id>` fails)

Safe preview → **pluto-workflow**. Not `cursor-ide-browser` MCP.
