# Glass navigation

Open Pluto in **Agents Glass** — the right-hand browser in the Agents window (D13).

## Two browser surfaces (do not confuse)

| MCP | Glass? | Use for Pluto? |
|-----|--------|----------------|
| **`cursor-ide-browser`** (`browser_navigate`, `browser_click`, …) | Yes in **Agents Window** — MCP `viewId` is usually **6-hex** (e.g. `a1b2c3`); workbench pane ids are `glass-browser-<uuid>` | **Yes** — primary agent navigation |
| **`plugin-browse-browser`** | **No** — separate automation daemon | **Never** — no Design Mode `dom_path` in hooks |

Only Agents Glass participates in Design Mode → `resolve_pluto_context` → `read_cell`.

## Agent navigation: `cursor-ide-browser`

1. Call `pluto_session_status` (or use the `pluto_url` / `pluto_port` from `start_pluto_session`)
2. Resolve the Glass URL — see [Local vs Remote SSH](#local-vs-remote-ssh-glass-url)
3. **Reuse Glass first** — see [Tab reuse](#tab-reuse-no-newtab-by-default) (do **not** open a new tab by default)
4. **`browser_navigate`** — `{ url: "<glass_url>" }` plus cached `viewId` when known. **Omit `position`** unless the user explicitly asks to show/focus Glass (see below).
5. Confirm MCP `viewId` from the result (`Browser View ID:` / metadata) — typically **6-hex**, not `glass-browser-<hex>`
6. **`browser_snapshot`** → **`browser_click`** on links (Path B: notebook filename on landing)

### Local vs Remote SSH (Glass URL)

Agents Glass’s browser runs on the **laptop UI**. MCP/`pluto_url` are correct for the machine where Pluto listens.

| Session | Glass URL | Ask user? |
|---------|-----------|-----------|
| **Local** (not Remote SSH / not remote) | Host `pluto_session_status.pluto_url` | **No** — open Glass immediately |
| **Remote SSH** (or otherwise remote) | `http://127.0.0.1:<forwarded_port>/` from the user’s Ports answer | **Yes — every session** before first Glass navigate |

**Remote — one ask, then open:**

1. From status, name the **remote** Pluto port (`pluto_port` / host `pluto_url`).
2. Ask once, clearly, e.g.:  
   > Pluto is on remote port **\<N\>**. What is the **forwarded / local** port in Cursor **Ports** for that remote port? (port number or full URL is fine.)
3. Accept a bare port (`35721`) or a full URL. Normalize to `http://127.0.0.1:<port>/` (keep path if they pasted `/edit?id=…`).
4. **`browser_navigate`** that URL immediately (**omit `position`**) — do not lecture, do not retry host URL first, do not invent remaps.
5. Treat the answer as **session-scoped only**. Remaps differ per session; do **not** persist it as cross-session truth.

**Never:** invent client ports; hardcode lore ports; claim host `pluto_url` is Glass-authoritative on Remote SSH; require an Extension Host companion.

Do **not** use `plugin-browse-browser`. Do **not** hardcode `:1234`.

### Tab reuse (no `newTab`, no `position: "active"` by default)

Glass tab spam is a known failure mode ([issue #4](https://github.com/jowch/styx/issues/4)). Cursor keeps **two** ids: MCP Playwright **6-hex** vs workbench **`glass-browser-<uuid>`**. `browser_navigate` with **`position: "active"`** reveals Agents Glass via workbench `_reopenBrowserTab`, which **always mints a new** `glass-browser-<uuid>` pane even when a 6-hex tab already exists. Omit `position` unless the user explicitly asks to show/focus the browser.

1. **`browser_navigate({ url })`** (first pane) or **`browser_navigate({ url, viewId })`** (reuse). Never add `position` or `newTab` by default.
2. If tab APIs are available, **list tabs** and reuse any tab whose URL host/path looks like this session’s Pluto (landing or `/edit?id=`). Match on notebook id or path — not a guessed port alone. Prefer the **6-hex** `viewId` when both a hex id and a `glass-browser-<uuid>` point at the same Pluto URL.
3. Treat an **empty or stale tab list as unreliable**, not proof that no Glass tab exists. Ask the user which Glass tab is Pluto, or navigate to the best-known URL **with that tab’s `viewId`**, before creating anything. Empty list in a **Task child** often means that child does not own this chat’s panes — do not create a tab.
4. **Never** pass `newTab` / `new` / `tabs_new` by default. Open a new Glass tab only if the user explicitly asks, or after confirming there is truly no reusable Pluto Glass view.
5. After a failed navigate, **do not** retry by spawning another tab — fix the URL (local: host `pluto_url`; remote: re-ask Ports forwarded port) and reuse.

**Glass view cache:** After any successful Glass navigate/snapshot on this session’s Pluto URL, Styx hooks record `viewId` under `(session_id, notebook_id)` (`_landing` if no `edit?id=`). Before Glass work, use the injected map (or `$STYX_RUNTIME_DIR/sessions/<session_id>/glass-views.json`): look up by `notebook_id` / landing — never a single viewId for the whole session — and call `browser_navigate({ url, viewId })` (**no** `position`). If `browser_tabs` list is non-empty, confirm URL matches and refresh the map; if empty, still use the stored `viewId`. On failure, drop that entry only and **hard-stop** — ask the user; **never** `newTab` / `action: "new"`. One notebook → one remembered view (last success wins). Parent and Task children share the same file.

### Path A — landing only

**Local:**

```text
status = pluto_session_status()
browser_navigate({ url: status.pluto_url })
```

**Remote SSH:** ask for Ports forwarded port for `status.pluto_port` → navigate `http://127.0.0.1:<forwarded>/` (see above).

Tell user to pick a notebook; stop.

### Path B — after `open_notebook`

**Local:** `browser_navigate({ url: status.pluto_url })` then `open_notebook` → landing click.

**Remote SSH:** resolve Glass URL via the per-session Ports ask first, then the same Path B steps on that URL.

**Do not** `browser_navigate` to pasted `/edit?id=` after MCP `open_notebook` — cold loads hang on `Loading cells...`. Click the notebook on landing instead. Details: [path-b-open.md](path-b-open.md).

### Exit Safe preview in Glass

When the editor shows **Safe preview** / *Code not executed in Safe preview* and live outputs are needed:

1. `browser_snapshot` the open notebook tab (reuse existing Glass — no `newTab`)
2. `browser_click` **Run notebook code** (top right)
3. Or call MCP `allow_execution` instead when appropriate (risky remote sources need the Glass button)

Do not leave Safe preview on after staging edits that need live results. Details: **pluto-workflow** [safe-preview.md](../../pluto-workflow/reference/safe-preview.md).

## User handoff (last resort)

If `cursor-ide-browser` is unavailable:

1. **Local:** give landing URL from `pluto_session_status.pluto_url`
2. **Remote SSH:** give `http://127.0.0.1:<forwarded>/` after the Ports ask (same URL Glass would use)
3. Ask user to click the notebook on landing (Path B) or pick one (Path A)

## URL forms

| Page | URL |
|------|-----|
| Landing | `<glass_url>/` |
| Notebook editor (after loaded in Glass) | `<glass_url>/edit?id=<notebook_id>` |

Plain `http://127.0.0.1:<port>/<notebook_id>` is **not** a documented Pluto route.
