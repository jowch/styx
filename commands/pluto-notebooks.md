---
description: User wants to work on Pluto notebooks — agent invokes pluto-session
---

# Pluto notebooks

Invoke **pluto-session** and follow it.

- **No specific notebook** (Path A): start session if needed → open `http://127.0.0.1:1234/` in Glass → user picks notebook on next prompt.
- **Named notebook** (Path B): landing first (cookies) → `open_notebook(path=…)` → open `http://127.0.0.1:1234/edit?id=<notebook_id>` → safe-preview reminder.

Lifecycle tools may be hidden in the MCP picker — invoke by name. Full steps: **pluto-session**. Cell edits: **pluto-workflow**.
