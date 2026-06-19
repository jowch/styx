---
name: pluto-session
description: >-
  Use when the user mentions Pluto.jl notebooks, wants to start or open Pluto,
  open a specific .jl notebook in Glass, or begins notebook work with no
  notebook_id yet in browser context or chat.
---

# Pluto session bootstrap

The user is a **Cursor user first**. Only start Pluto when they **request notebook work**. You handle setup — never ask them to run shell scripts.

## Pick a path

| User said | Path |
|-----------|------|
| Wants Pluto / notebooks, **no specific notebook** | **A — landing page** |
| Wants a **specific notebook** (path, name, or clear reference) | **B — direct open** |

Do **not** ask "which notebook?" on Path A — Pluto's UI is the picker.

## Quick start

**Path A:** `pluto_session_status` → `start_pluto_session` if stopped → open landing `http://127.0.0.1:1234/` in Glass → tell user to pick a notebook → **stop** (no `open_notebook`, no `list_notebooks`).

**Path B:** `start_pluto_session` if needed → landing first (cookies) → `open_notebook(path=…)` → open `http://127.0.0.1:1234/edit?id=<notebook_id>` → safe-preview reminder → **pluto-workflow** for edits.

**Already running:** Path A → landing only. Path B → `list_notebooks`; skip `open_notebook` if target is open.

## REQUIRED chain

- Cell edits → **pluto-workflow**
- Lifecycle tools may be hidden in MCP picker — **invoke by name** anyway

## Common mistakes

| Mistake | Fix |
|---------|-----|
| Ask which notebook on Path A | Stop after landing |
| `open_notebook` without user path | Never scan repo and pick |
| Bare `/<notebook_id>` URL | Use `/edit?id=<notebook_id>` |
| User runs `pluto-serve.sh` | Use `start_pluto_session` |

## Additional resources

- **Path A steps:** [reference/path-a-landing.md](reference/path-a-landing.md)
- **Path B + cookies + safe preview:** [reference/path-b-open.md](reference/path-b-open.md)
- **Glass navigation + `open_resource` fallback:** [reference/glass-navigation.md](reference/glass-navigation.md)
- **Lifecycle tools + MCP picker quirk:** [reference/lifecycle-tools.md](reference/lifecycle-tools.md)
- **Bootstrap errors:** [reference/errors.md](reference/errors.md)
