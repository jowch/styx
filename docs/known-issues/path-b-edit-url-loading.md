# Path B: `/edit?id=` hangs after MCP `open_notebook`

**Symptom:** Glass shows `Loading...` / `Loading cells...` when navigating directly to `http://127.0.0.1:1234/edit?id=<notebook_id>` after the agent called `open_notebook`. Clicking the same notebook from the **landing page** loads normally.

**Cause:** MCP `open_notebook` loads the notebook server-side (`SessionActions.open`). A **cold** navigation to `/edit?id=` starts a fresh editor page with empty `cell_order` and waits for WebSocket hydration — in Glass this often never completes. The landing page already has a live WebSocket; clicking a running notebook uses in-app navigation that hydrates correctly.

**Agent fix (Path B):**

1. `start_pluto_session` if needed
2. Open landing in Glass — `cursor-ide-browser` → `browser_navigate({ position: "active" })`
3. `open_notebook(path=…)`
4. `browser_snapshot` → `browser_click` notebook link on landing — **not** `browser_navigate` to `/edit?id=`
5. Safe-preview reminder

**When `/edit?id=` is fine:** Path A follow-up (user picked notebook in Glass), or notebook was opened entirely through the browser (no prior MCP `open_notebook` for that navigation).

**Alternative (browser-only open, no MCP preload):** From landing, `http://127.0.0.1:1234/open?path=<abs-path>&execution_allowed=false` — still prefer landing click when MCP already called `open_notebook`.

**Tracked:** Styx skills `pluto-session` → `path-b-open.md`, `glass-navigation.md`.
