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
3. **`browser_navigate`** — `{ url: "<pluto_url_or_ports_url>", position: "active" }` (reveal / focus Glass)
4. Confirm view ID starts with **`glass-browser-`**
5. **`browser_snapshot`** → **`browser_click`** on links (Path B: notebook filename on landing)

### Host URL vs Ports (client) URL

| Audience | Source | Notes |
|----------|--------|-------|
| MCP / host tools | `pluto_session_status.pluto_url` | Host-local (`127.0.0.1:<pluto_port>`). Correct for the SSH/remote extension host. |
| Glass on the **laptop** (Remote SSH remap) | Cursor **Ports** panel forwarded URL (`remote_forward_unresolved` when status notes it) | Laptop port may differ (e.g. host `1234` → client `51708`). Use this when host `pluto_url` fails to load in Glass. |

Do **not** use `plugin-browse-browser`. Do **not** hardcode `:1234`.

### Tab reuse (no `newTab` by default)

Glass tab spam is a known failure mode when Ports remaps or `browser_tabs` is incomplete ([issue #4](https://github.com/jowch/styx/issues/4)).

1. Prefer **`position: "active"`** navigation into the existing Agents Glass pane.
2. If tab APIs are available, **list tabs** and reuse any tab whose URL host/path looks like this session’s Pluto (landing or `/edit?id=`). Match on notebook id or path — not a guessed port alone.
3. Treat an **empty or stale tab list as unreliable**, not proof that no Glass tab exists. Ask the user which Glass tab is Pluto, or navigate `position: "active"` to the best-known URL, before creating anything.
4. **Never** pass `newTab` / `new` / `tabs_new` by default. Open a new Glass tab only if the user explicitly asks, or after confirming there is truly no reusable Pluto Glass view.
5. After a failed navigate, **do not** retry by spawning another tab — fix the URL (host `pluto_url` vs Ports client URL) and reuse.

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

## User handoff (last resort)

If `cursor-ide-browser` is unavailable:

1. Give landing URL from `pluto_session_status.pluto_url`
2. Ask user to click the notebook on landing (Path B) or pick one (Path A)

## URL forms

| Page | URL |
|------|-----|
| Landing | `<pluto_url>/` from `pluto_session_status` |
| Notebook editor (after loaded in Glass) | `<pluto_url>/edit?id=<notebook_id>` |

Plain `http://127.0.0.1:<port>/<notebook_id>` is **not** a documented Pluto route.
