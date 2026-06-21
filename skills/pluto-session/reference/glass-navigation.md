# Glass navigation

Open Pluto in **Agents Glass** — the right-hand browser in the Agents window (D13).

## Two browser surfaces (do not confuse)

| MCP | Glass? | Use for Pluto? |
|-----|--------|----------------|
| **`cursor-ide-browser`** (`browser_navigate`, `browser_click`, …) | Yes in **Agents Window** — view IDs are `glass-browser-*` | **Yes** — primary agent navigation |
| **`plugin-browse-browser`** | **No** — separate automation daemon | **Never** — no Design Mode `dom_path` in hooks |

Only Agents Glass participates in Design Mode → `resolve_pluto_context` → `read_cell`.

## Agent navigation: `cursor-ide-browser`

1. **`browser_navigate`** — `{ url: "http://127.0.0.1:1234/", position: "active" }` (reveal Glass)
2. Confirm view ID starts with **`glass-browser-`**
3. **`browser_snapshot`** → **`browser_click`** on links (Path B: notebook filename on landing)

Do **not** use `plugin-browse-browser`.

### Path A — landing only

```text
browser_navigate({ url: "http://127.0.0.1:1234/", position: "active" })
```

Tell user to pick a notebook; stop.

### Path B — after `open_notebook`

```text
browser_navigate({ url: "http://127.0.0.1:1234/", position: "active" })
open_notebook({ path: "…" })
browser_snapshot → browser_click({ ref: "<notebook filename link>" })
```

**Do not** `browser_navigate` to pasted `/edit?id=` after MCP `open_notebook` — cold loads hang on `Loading cells...`. Click the notebook on landing instead. Details: [path-b-open.md](path-b-open.md).

## User handoff (last resort)

If `cursor-ide-browser` is unavailable:

1. Give landing URL `http://127.0.0.1:1234/`
2. Ask user to click the notebook on landing (Path B) or pick one (Path A)

## URL forms

| Page | URL |
|------|-----|
| Landing | `http://127.0.0.1:1234/` |
| Notebook editor (after loaded in Glass) | `http://127.0.0.1:1234/edit?id=<notebook_id>` |

Plain `http://127.0.0.1:1234/<notebook_id>` is **not** a documented Pluto route.
