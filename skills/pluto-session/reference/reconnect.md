# Reconnect — soft then hard

Use when Glass ↔ Pluto drops: empty title, **Loading cells…**, **Not yet authenticated**, stale port after restart, or “notebook on a new/different server”. One ladder — do not improvise restarts. Command entry: **styx-reconnect**.

Boot Pluto without Glass first → [styx-start.md](styx-start.md) (**styx-start**). Do not change Pluto cookie/origin behavior in Pluto itself.

## Symptom → first fix

| Symptom | Likely cause | First fix |
|---------|--------------|-----------|
| **Not yet authenticated** | Host mix (`localhost` ≠ `127.0.0.1`) or missing secret cookie | Soft reconnect on exact `pluto_session_status.pluto_url` host — [one host per session](glass-navigation.md#one-host-per-session-localhost-vs-127001) |
| Empty title / **Loading cells…** forever | Stale WS; cold `/edit?id=` | Soft reconnect via **welcome → click notebook** (same as Path B) |
| “New / different server” dialog | Pluto restarted; port/session changed | Stay if URL matches live port; else soft reconnect to current landing |
| MCP `pluto_not_running` / tools fail | Pluto process down | **Hard restart** (or **styx-start** after stop) |
| Glass on old port while status moved | Stale tab | Soft reconnect to current `pluto_url` / Ports URL |

## 1. Diagnose

1. `pluto_session_status` — record `pluto`, `session_id`, `pluto_url` / `pluto_port`, open notebooks.
2. **Parent:** Read glass-views cache + `browser_tabs` (see [glass-navigation.md](glass-navigation.md)). Note the Glass URL currently shown.
3. Classify:
   - **Pluto/MCP dead** (`pluto` stopped, `pluto_not_running`, bridge unreachable) → skip to [Hard restart](#3-hard-restart).
   - **Otherwise** → [Soft reconnect](#2-soft-reconnect).

## 2. Soft reconnect

Do this **before** stop/start. Reuse Glass — no `newTab` / `action: "new"`.

1. **Resolve Glass URL**
   - **Local:** exact host string from `status.pluto_url` — do **not** rewrite `127.0.0.1` ↔ `localhost` mid-session (chat may say `localhost`; Glass must use the status host).
   - **Remote SSH:** same Ports-forwarded origin already chosen this session; re-ask Ports only if the remote `pluto_port` changed.
2. **Navigate to landing** — `browser_navigate({ url: <glass_url>/, viewId })` (reuse omit `position`; reveal once with `position: "active"` only if the pane is closed). Prefer landing over cold `/edit?id=` after MCP open — Path B lesson: cold edit URLs hang on **Loading cells…**.
3. **Re-enter the notebook** — `browser_snapshot` → `browser_click` the notebook on landing (filename / known open notebook). If Path A and the user has no target yet, stop at landing.
4. **Auth recovery** (“Not yet authenticated”):
   - First: reopen landing with the **status / Ports host** above.
   - Only then: try the *other* loopback host **once** (`localhost` ↔ `127.0.0.1` on the same port) — then **keep that host** for the rest of the session.
   - Do **not** hunt for `?secret=` before those steps.
5. **“New / different server”:** if Glass URL host+port already matches live `pluto_url` (local) or the Ports URL (remote), stay and click through; if the tab is on a dead/old port, navigate to the current landing (step 2).
6. Confirm editor hydrates (title / cells appear). If soft reconnect fails after one clean pass → [Hard restart](#3-hard-restart).

## 3. Hard restart

Only when Pluto/MCP is dead or soft reconnect failed.

1. `stop_pluto_session` (if a managed session is up).
2. Restart Pluto:
   - Prefer **`scripts/styx-start.sh`** (or `--path` if known) — prints welcome URL, no Glass.
   - Or MCP `start_pluto_session` → new `pluto_url` / port.
3. If the user needs Glass again: open landing with the **new** URL (Remote SSH: re-ask Ports for the new remote port), then Path B click — not pasted `/edit?id=`.
4. Resume **pluto-workflow** for edits.

## Rules

- Soft before hard — never jump to stop/start for auth or Loading-cells alone.
- One host per session — [glass-navigation.md](glass-navigation.md#one-host-per-session-localhost-vs-127001).
- Landing click after MCP `open_notebook` — [path-b-open.md](path-b-open.md).
- Reuse Glass; never invent Ports remaps or hardcode `:1234`.
- Task child: notebook tools via inherited MCP; leave Glass to the parent.
