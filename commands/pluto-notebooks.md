---
description: Start a Pluto notebook session — agent handles setup and Glass navigation
---

# Pluto notebooks

The user wants to **work on Pluto notebooks**. They should not run shell scripts.

## Agent actions

1. Invoke **pluto-session** and follow it.

**If no specific notebook named** (Path A):
- `start_pluto_session` if needed
- Open `http://127.0.0.1:1234/` in Agents Glass
- Tell user to pick a notebook there; resolve `notebook_id` on their **next** prompt

**If user named a specific notebook** (Path B):
- `start_pluto_session` if needed
- Open landing page `http://127.0.0.1:1234/` first (cookies)
- `open_notebook(path=…)` → open `http://127.0.0.1:1234/<notebook_id>` in Glass

After bootstrap, use **pluto-workflow** for cell edits.
