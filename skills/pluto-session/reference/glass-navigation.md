# Glass navigation

Open Pluto in **Agents Glass** — the right-hand browser in the Agents window (D13).

## Two browser surfaces (do not confuse)

| MCP | Glass? | Use for Pluto? |
|-----|--------|----------------|
| **`cursor-ide-browser`** (`browser_navigate`, `browser_click`, …) | Yes in **Agents Window** — view IDs are `glass-browser-*` | **Yes** — primary agent navigation |
| **`plugin-browse-browser`** | **No** — separate automation daemon | **Never** — no Design Mode `dom_path` in hooks |

Only Agents Glass participates in Design Mode → `resolve_pluto_context` → `read_cell`.

## Agent navigation: `cursor-ide-browser`

1. Call `pluto_session_status` (or use the `pluto_url` from `start_pluto_session`)
2. **Reuse Glass first** — see [Tab reuse](#tab-reuse-no-newtab-by-default) (do **not** open a new tab by default)
3. **`browser_navigate`** — `{ url: "<pluto_url>", position: "active" }` (reveal / focus Glass)
4. Confirm view ID starts with **`glass-browser-`**
5. **`browser_snapshot`** → **`browser_click`** on links (Path B: notebook filename on landing)

### Host URL vs client URL

| Audience | Source | Notes |
|----------|--------|-------|
| MCP / host tools | `pluto_session_status.pluto_url` | Host-local (`127.0.0.1:<pluto_port>`). Correct for the SSH/remote extension host. |
| Agents Glass (`cursor-ide-browser`) | Prefer **`pluto_url`** | Usually enough on remote-aware Glass — do not invent a laptop remap. |
| Laptop browser / human handoff | Optional **`client_url`** from status when present | Resolved by the **Styx Ports** companion via `asExternalUri` (Cursor auto-forward). **Omit** if unresolved — never guess Ports numbers. |

Do **not** use `plugin-browse-browser`. Do **not** hardcode `:1234`. Do **not** invent client ports from docs or prior sessions.

### Tab reuse (no `newTab` by default)

Glass tab spam is a known failure mode when Ports remaps or `browser_tabs` is incomplete ([issue #4](https://github.com/jowch/styx/issues/4)).

1. Prefer **`position: "active"`** navigation into the existing Agents Glass pane.
2. If tab APIs are available, **list tabs** and reuse any tab whose URL host/path looks like this session’s Pluto (landing or `/edit?id=`). Match on notebook id or path — not a guessed port alone.
3. Treat an **empty or stale tab list as unreliable**, not proof that no Glass tab exists. Ask the user which Glass tab is Pluto, or navigate `position: "active"` to the best-known URL, before creating anything.
4. **Never** pass `newTab` / `new` / `tabs_new` by default. Open a new Glass tab only if the user explicitly asks, or after confirming there is truly no reusable Pluto Glass view.
5. After a failed navigate, **do not** retry by spawning another tab — stick to host `pluto_url` (or status `client_url` when present for laptop handoff) and reuse.

### Path A — landing only

```text
status = pluto_session_status()
browser_navigate({ url: status.pluto_url, position: "active" })
```

Tell user to pick a notebook; stop.

### Path B — after `open_notebook`

```text
browser_navigate({ url: status.pluto_url, position: "active" })
open_notebook({ path: "…" })
browser_snapshot → browser_click({ ref: "<notebook filename link>" })
```

**Do not** `browser_navigate` to pasted `/edit?id=` after MCP `open_notebook` — cold loads hang on `Loading cells...`. Click the notebook on landing instead. Details: [path-b-open.md](path-b-open.md).

### Exit Safe preview in Glass

When the editor shows **Safe preview** / *Code not executed in Safe preview* and live outputs are needed:

1. `browser_snapshot` the open notebook tab (reuse existing Glass — no `newTab`)
2. `browser_click` **Run notebook code** (top right)
3. Or call MCP `allow_execution` instead when appropriate (risky remote sources need the Glass button)

Do not leave Safe preview on after staging edits that need live results. Details: **pluto-workflow** [safe-preview.md](../../pluto-workflow/reference/safe-preview.md).

## User handoff (last resort)

If `cursor-ide-browser` is unavailable:

1. Prefer landing URL from `pluto_session_status.client_url` when present (laptop-reachable); else `pluto_url`
2. Ask user to click the notebook on landing (Path B) or pick one (Path A)
3. If neither URL works for the user’s browser, stop and ask — **never invent** a remapped port

## URL forms

| Page | URL |
|------|-----|
| Landing | `<pluto_url>/` from `pluto_session_status` |
| Notebook editor (after loaded in Glass) | `<pluto_url>/edit?id=<notebook_id>` |

Plain `http://127.0.0.1:<port>/<notebook_id>` is **not** a documented Pluto route.
