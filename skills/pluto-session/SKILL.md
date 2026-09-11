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

**Path A:** `pluto_session_status` → `start_pluto_session` if stopped → `cursor-ide-browser` → **reuse Glass** → **`pluto_url`** landing (`position: "active"`) → tell user to pick a notebook → **stop**.

**Path B:** `start_pluto_session` if needed → **reuse Glass** → landing via **`pluto_url`** → `open_notebook(path=…)` → **`browser_click` notebook on landing** (not pasted `/edit?id=`) → safe-preview reminder → **pluto-workflow** for edits.

Glass: never hardcode `:1234`; never `newTab` by default — see [reference/glass-navigation.md](reference/glass-navigation.md).

**Already running:** Path A → landing only. Path B → `list_notebooks`; skip `open_notebook` if target is open. Same path open in another Styx session → `notebook_in_use`.

**Remote SSH:** this window owns Pluto on the SSH host (local XOR remote). See [reference/remote-ssh.md](reference/remote-ssh.md).

**Local Task child:** use the inherited `plugin-styx-pluto` server — do not pass ports or binding paths in prompts.

## REQUIRED chain

- Cell edits → **pluto-workflow**
- Lifecycle tools may be hidden in MCP picker — **invoke by name** anyway

## Common mistakes

| Mistake | Fix |
|---------|-----|
| Ask which notebook on Path A | Stop after landing |
| `open_notebook` without user path | Never scan repo and pick |
| Bare `/<notebook_id>` URL | Use `/edit?id=<notebook_id>` only when notebook opened in Glass (Path A); after MCP `open_notebook`, click on landing |
| Hardcode `:1234` / spam `newTab` | Use `pluto_url` (or Ports client URL); reuse Glass — [glass-navigation.md](reference/glass-navigation.md) |
| User runs `pluto-serve.sh` | Use `start_pluto_session` |

## Additional resources

- **Path A steps:** [reference/path-a-landing.md](reference/path-a-landing.md)
- **Path B + cookies + safe preview:** [reference/path-b-open.md](reference/path-b-open.md)
- **Glass navigation (`cursor-ide-browser`):** [reference/glass-navigation.md](reference/glass-navigation.md)
- **Lifecycle tools + MCP picker quirk:** [reference/lifecycle-tools.md](reference/lifecycle-tools.md)
- **Bootstrap errors:** [pluto-workflow/reference/errors.md](../pluto-workflow/reference/errors.md)
- **Remote SSH:** [reference/remote-ssh.md](reference/remote-ssh.md)
- **Parent/subagent grading:** [../../eval/agent-control/README.md](../../eval/agent-control/README.md)
