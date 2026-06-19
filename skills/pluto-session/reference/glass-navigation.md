# Glass navigation

Open Pluto in **Agents Glass** — not `cursor-ide-browser` MCP (D13).

## Preferred: `open_resource`

Use `open_resource` (cursor-app-control MCP) when available.

## Fallback when `open_resource` unavailable

Do **not** dump a bare link and stop. Instead:

1. Tell the user the exact URL to open in Agents Glass.
2. Ask them to confirm when the page is visible, **or** retry `open_resource` if the tool becomes available.

Do **not** use `cursor-ide-browser` MCP for Pluto.

## URL forms

| Page | URL |
|------|-----|
| Landing | `http://127.0.0.1:1234/` |
| Notebook editor | `http://127.0.0.1:1234/edit?id=<notebook_id>` |

Plain `http://127.0.0.1:1234/<notebook_id>` is **not** a documented Pluto route and fails in Glass.

## Path B: two navigations

1. Landing page first (cookies)
2. Notebook URL after `open_notebook`
