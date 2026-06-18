---
name: pluto-session
description: >-
  Start and open Pluto.jl notebook sessions from Cursor — lazy warm lifecycle,
  Glass browser navigation. Use when the user wants to work on Pluto notebooks,
  open a notebook, start Pluto, or begin notebook editing for the first time
  in a chat.
---

# Pluto session bootstrap

The user is a **Cursor user first**. Only start Pluto when they **request notebook work**. You handle setup — never ask them to run shell scripts.

## Two paths (pick from user message)

| User said | Path |
|-----------|------|
| Wants Pluto / notebooks, **no specific notebook** | **A — landing page** |
| Wants a **specific notebook** (path, name, or clear reference) | **B — direct open** |

Do **not** ask "which notebook?" on Path A — Pluto's UI is the picker.

---

## Path A — General Pluto intent (landing page)

**Examples:** "I want to work on my notebooks", "open Pluto", "let's use Pluto"

### Steps

1. `pluto_session_status` → if stopped, `start_pluto_session`
2. Open **Pluto landing page** in Agents Glass: `http://127.0.0.1:1234/`
3. Tell the user briefly:
   > Pluto is ready. Pick or create a notebook on this page. When you're in a notebook, send your next message — click a cell with **⌘⇧D** (Design Mode) or describe what you want.

4. **Stop.** Do not call `open_notebook`, `list_notebooks`, or ask which file.

### Next user prompt (notebook chosen in UI)

The user has selected a notebook in Pluto. Resolve context via **pluto-workflow**:

- Design Mode click → `resolve_pluto_context` → `read_cell`
- Glass URL `http://127.0.0.1:1234/edit?id=<notebook_id>` (or bare `/<notebook_id>` if that works in their Glass build)
- `list_notebooks` if needed

---

## Path B — Specific notebook intent

**Examples:** "Open `experiments/odes.jl` in Pluto", "work on my signal analysis notebook at `analysis/signal.jl`"

### Steps

1. `pluto_session_status` → if stopped, `start_pluto_session`
2. Open **landing page** first in Agents Glass: `http://127.0.0.1:1234/`  
   *(Sets loopback session cookies — required before notebook URLs work reliably, D14.)*
3. `open_notebook(path="<user-specified path>")` → record `notebook_id`  
   Default: safe preview (like Pluto UI — no auto-run). Use `run_notebook=true` only if user asked to run.
4. Open **notebook URL** in Agents Glass: `http://127.0.0.1:1234/edit?id=<notebook_id>`
5. Tell the user:
   > Your notebook is open in **Safe preview** — code won't run until you click **Run notebook code** in Glass (top right). I can still edit cells; you won't see outputs or widgets update until you run.

   Use `run_notebook=true` on `open_notebook` **only** if the user explicitly asked to open **and run**.

6. Proceed to **pluto-workflow** when they ask for edits (remind about preview if outputs matter).

**Never** `open_notebook` without a user-specified path. Do not scan the repo and pick a file.

---

## If Pluto is already running

| Situation | Action |
|-----------|--------|
| Path A, user wants Pluto again | Open landing page only |
| Path B, notebook may already be open | `list_notebooks` — if target is open, skip `open_notebook`; open notebook URL in Glass |
| User asks to edit cells | Skip bootstrap; use **pluto-workflow** |

---

## Glass navigation

- Use `open_resource` (cursor-app-control MCP) when available
- **Not** `cursor-ide-browser` MCP (D13)
- Path B: landing page **then** notebook URL (two navigations)

## Stopping (optional)

On "done with notebooks": `submit_changes` if staged; optional `stop_pluto_session`.

## Errors

| Error | Action |
|-------|--------|
| `pluto_not_running` | `start_pluto_session` |
| `notebook_not_found` | Confirm path with user |
| MCP unreachable | Enable **pluto** MCP in Cursor Settings |
