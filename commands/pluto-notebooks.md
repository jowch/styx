---
description: User wants to work on Pluto notebooks — agent invokes pluto-session
---

# Pluto notebooks

Invoke **pluto-session** and follow it.

- **No specific notebook** (Path A): start session if needed → open landing in Glass → user picks notebook on next prompt.
- **Named notebook** (Path B): landing in Glass → `open_notebook(path=…)` → agent clicks notebook on landing via `cursor-ide-browser` → safe-preview reminder.

Glass navigation: **`cursor-ide-browser`** — not `plugin-browse-browser`. Full steps: **pluto-session**.
