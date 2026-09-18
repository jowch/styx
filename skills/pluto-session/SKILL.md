---
name: pluto-session
description: >-
  Use when the user mentions Pluto.jl notebooks, wants to start or open Pluto,
  open a specific .jl notebook in Glass, begins notebook work with no
  notebook_id yet, wants one-shot boot + Glass ready (/styx-start), or needs
  Glass/Pluto reconnect (auth, Loading cells, stale port — /styx-reconnect).
---

# Pluto session bootstrap

The user is a **Cursor user first**. Only start Pluto when they **request notebook work**. You handle setup — never ask them to run `pluto-serve.sh` / raw `PlutoMCP.serve()`.

**styx-start** (boot + Glass ready in one turn) and **styx-reconnect** (Glass/auth/WS recovery) are first-class commands — follow their playbooks.

## Pick a path

| User said | Path |
|-----------|------|
| Wants Pluto / notebooks, **no specific notebook** | **A — landing page** |
| Wants a **specific notebook** (path, name, or clear reference) | **B — direct open** |

Do **not** ask "which notebook?" on Path A — Pluto's UI is the picker.

## Quick start

**Path A:** `pluto_session_status` → `start_pluto_session` if stopped → `cursor-ide-browser` → **reuse or reveal Glass** → landing → tell user to pick a notebook → **stop**.

**Path B:** `start_pluto_session` if needed → **reuse or reveal Glass** → landing → `open_notebook(path=…)` → **`browser_click` notebook on landing** (not pasted `/edit?id=`) → exit Safe preview when outputs need to be live (Glass **Run notebook code** or `allow_execution`) → **pluto-workflow** for edits.

**styx-start:** boot script/MCP → resolve Glass URL → navigate landing → Path B click if notebook known → stop when Glass shows notebook (or landing if welcome-only). **No second ask** to open a URL. [reference/styx-start.md](reference/styx-start.md).

**Glass URL:** **local** → host `pluto_url` (no ask). **Remote SSH** → remember last-good for this session+port → Glass-probe `http://127.0.0.1:<pluto_port>/` → ask Ports **only if** probe fails. Never invent remaps; never `newTab` / `action: "new"`. **Parent before Glass work:** `pluto_session_status` → Read `$STYX_RUNTIME_DIR/sessions/<session_id>/glass-views.json` (else `$XDG_RUNTIME_DIR/styx-$UID/sessions/<session_id>/glass-views.json`, else `${TMPDIR:-/tmp}/styx-$UID/sessions/<session_id>/glass-views.json`) → `browser_tabs`. **Reuse:** existing Pluto tab (cached `viewId` or parent tab list) → `browser_navigate({ url, viewId })` — omit `position` and `newTab`. **Reveal (parent, once):** pane closed/hidden, user says it did not open, or first visible open this session and tabs empty → `browser_navigate({ url })` with `position: "active"`; record result `viewId` and omit `position` later. Do not wait for sessionStart “Known Glass views” — Cursor does not put that hook output in the model (parent or child). [reference/glass-navigation.md](reference/glass-navigation.md).

**Already running:** Path A → landing only. Path B → `list_notebooks`; skip `open_notebook` if target is open. Same path open in another Styx session → `notebook_in_use`.

**Remote SSH:** this window owns Pluto on the SSH host (local XOR remote). Glass URL ladder (remember → probe → ask) — [reference/remote-ssh.md](reference/remote-ssh.md).

**Local Task child:** inherit `plugin-styx-pluto` for notebook tools (`read_cell` / `edit_cell` / `submit_changes`) — do not pass MCP ports. Agents Glass (`cursor-ide-browser`) is **parent-only**: `browser_tabs` is empty; a cached `viewId` fails “Browser view not found”. Do **not** `newTab` / `position: "active"`. Leave Glass to the parent. [reference/glass-navigation.md](reference/glass-navigation.md).

## REQUIRED chain

- Cell edits → **pluto-workflow**
- Lifecycle tools may be hidden in MCP picker — **invoke by name** anyway

## Common mistakes

| Mistake | Fix |
|---------|-----|
| Ask which notebook on Path A | Stop after landing |
| `open_notebook` without user path | Never scan repo and pick |
| Bare `/<notebook_id>` URL | Use `/edit?id=<notebook_id>` only when notebook opened in Glass (Path A); after MCP `open_notebook`, click on landing |
| Hardcode `:1234` / invent Ports remaps / spam `newTab` | Local: host `pluto_url`. Remote: remember → probe → ask — [glass-navigation.md](reference/glass-navigation.md) |
| Rewrite `127.0.0.1` ↔ `localhost` mid-session | Same port ≠ same origin — cookie fails (“Not yet authenticated”). One host per session: exact host from `pluto_url` (local) or the resolved Ports/probe origin (remote) — [glass-navigation.md](reference/glass-navigation.md#one-host-per-session-localhost-vs-127001) |
| Jump to `stop`/`start_pluto_session` for auth or Loading cells | Soft reconnect first — **styx-reconnect** / [reconnect.md](reference/reconnect.md) |
| Print welcome URL and ask user to open it after **styx-start** | Same turn: Glass navigate + Path B click — [styx-start.md](reference/styx-start.md) |
| Task child `newTab` after empty tabs / view-not-found | Expected isolation — notebook tools via inherited MCP; parent owns Glass |
| User runs `pluto-serve.sh` | Use `start_pluto_session` or **styx-start** |

## Additional resources

- **Path A steps:** [reference/path-a-landing.md](reference/path-a-landing.md)
- **Path B + cookies + safe preview:** [reference/path-b-open.md](reference/path-b-open.md)
- **styx-start (boot + Glass ready):** [reference/styx-start.md](reference/styx-start.md)
- **styx-reconnect (auth / WS / stale port):** [reference/reconnect.md](reference/reconnect.md)
- **Glass navigation (`cursor-ide-browser`):** [reference/glass-navigation.md](reference/glass-navigation.md)
- **Lifecycle tools + MCP picker quirk:** [reference/lifecycle-tools.md](reference/lifecycle-tools.md)
- **Bootstrap errors:** [pluto-workflow/reference/errors.md](../pluto-workflow/reference/errors.md)
- **Remote SSH:** [reference/remote-ssh.md](reference/remote-ssh.md)
- **Parent/subagent grading:** [../../eval/agent-control/README.md](../../eval/agent-control/README.md)
