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
2. **`browser_navigate`** — `{ url: "<pluto_url>", position: "active" }` (reveal Glass)
3. Confirm view ID starts with **`glass-browser-`**
4. **`browser_snapshot`** → **`browser_click`** on links (Path B: notebook filename on landing)

If landing fails on Remote SSH, Cursor may have remapped the port — use the **Ports** panel URL (`remote_forward_unresolved`). See [remote-ssh.md](remote-ssh.md).

Do **not** use `plugin-browse-browser`. Do **not** hardcode `:1234`.

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
