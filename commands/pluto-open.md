---
description: User wants Pluto or a notebook opened in Agents Glass — pluto-session if not running
---

# Pluto open

1. `pluto_session_status` — if stopped, invoke **pluto-session**.
2. Open in Agents Glass — [glass-navigation](../skills/pluto-session/reference/glass-navigation.md): `cursor-ide-browser` → `browser_navigate({ position: "active" })`; Path B: `browser_click` notebook on landing after `open_notebook`.
3. Safe preview → **pluto-workflow**. Not `plugin-browse-browser`.
