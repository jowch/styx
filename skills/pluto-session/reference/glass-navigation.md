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
3. **Reuse or reveal Glass** — see [Reuse vs reveal](#reuse-vs-reveal) (do **not** open a new tab)
4. **`browser_navigate`** — `{ url: "<glass_url>" }` plus cached `viewId` when known. **Reuse** omits `position`; **reveal** (closed pane / first visible open) may pass `position: "active"` **once**.
5. Confirm MCP `viewId` from the result (`Browser View ID:` / metadata) — typically **6-hex**, not `glass-browser-<hex>`
6. **`browser_snapshot`** → **`browser_click`** on links (Path B: notebook filename on landing)

### Local vs Remote SSH (Glass URL)

Agents Glass’s browser runs on the **laptop UI**. MCP/`pluto_url` are correct for the machine where Pluto listens.

| Session | Glass URL | Ask user? |
|---------|-----------|-----------|
| **Local** (not Remote SSH / not remote) | Exact host `pluto_session_status.pluto_url` / `welcome_url` | **No** — open Glass immediately |
| **Remote SSH** (or otherwise remote) | Last-good client origin → else same-port Glass probe → else Ports answer | **Only if** remember + probe both fail |

**Remote — resolve ladder (maximize automation):**

1. From status, note the **remote** Pluto port (`pluto_port` / host `pluto_url`).
2. **Remember** — Read `sessions/<session_id>/glass-views.json` (same path fallbacks as [Glass view cache](#reuse-vs-reveal)). If the file’s top-level **`pluto_port`** equals this session’s live `pluto_session_status.pluto_port` and an entry `url` is a client origin, reuse that origin. Missing `pluto_port` (old cache) → skip remember. Do **not** invent remaps; do **not** reuse when the stored host port differs from live `pluto_port`. There is no `glass-client.json`.
3. **Else probe** — `browser_navigate` to `http://127.0.0.1:<pluto_port>/` (same number as remote — Cursor often 1:1-forwards). Snapshot: if it looks like Pluto landing (not connection refused / wrong app), **use that origin** and continue. Hooks persist the proven URL into `glass-views.json` after success. **Never** treat remote-shell `curl` / host `pluto_ui_ok` as Glass proof (false positive on the SSH host).
4. **Else ask once** — only when remember + probe failed:
   > Pluto is on remote port **\<N\>**. What is the **forwarded / local** port in Cursor **Ports** for that remote port? (port number or full URL is fine.)
   Accept a bare port (`35721`) or a full URL. Normalize to `http://127.0.0.1:<port>/` (keep path if they pasted `/edit?id=…`). Then navigate immediately.
5. **`browser_navigate`** the resolved URL — **reuse** omits `position`; **reveal** (`position: "active"` **once**) if this is the first visible open and tabs are empty — do not lecture, do not invent remaps.

**Never:** invent client ports; hardcode lore ports; claim host `pluto_url` is always Glass-authoritative on Remote SSH; require an Extension Host companion; skip the probe and ask every time when remember/probe would work.

Do **not** use `plugin-browse-browser`. Do **not** hardcode `:1234`.

### One host per session (localhost vs 127.0.0.1)

Pluto’s secret cookie is **origin-scoped**. `http://localhost:<port>` and `http://127.0.0.1:<port>` are **different origins** — they do not share cookies. Mixing them yields Pluto’s **“Not yet authenticated”** page (asks for the terminal secret link) even though the other host is already authed.

**Rule:** pick **one** loopback host for the whole session and stick to it.

| Session | Host to use |
|---------|-------------|
| **Local** | Exact host from `pluto_session_status.pluto_url` / `start_pluto_session` (today usually `127.0.0.1`) — copy the URL string; do **not** rewrite `127.0.0.1` ↔ `localhost` for Glass navigate, handoff links, or chat URLs that the user will open |
| **Remote SSH** | The Ports-forwarded origin you already chose (`http://127.0.0.1:<forwarded>/`) — same host for every Glass navigate this session |

**Recovery** if Glass shows **“Not yet authenticated”:** re-open landing via the session URL above (status `pluto_url` locally, or the same forwarded origin remotely). Only try the *other* loopback host as a last recovery step — then keep that host for the rest of the session. Do **not** hunt for `?secret=` first. Full soft→hard ladder (Loading cells, stale port, dead Pluto): [reconnect.md](reconnect.md).

Product default (emit `localhost` from status vs keep `127.0.0.1`) is deferred — until then, **status host wins**.

### Reuse vs reveal

Glass tab spam is a known failure mode ([issue #4](https://github.com/jowch/styx/issues/4)). Cursor keeps **two** ids: MCP Playwright **6-hex** vs workbench **`glass-browser-<uuid>`**. Omitting `position` is background tab navigation (focus preserved — a closed pane stays hidden). `browser_navigate` with **`position: "active"`** reveals Agents Glass via workbench `_reopenBrowserTab`, which **always mints a new** `glass-browser-<uuid>` pane even when a 6-hex tab already exists.

**Parent** owns Agents Glass. A **Task child** in the same window cannot attach: `browser_tabs` is empty and `browser_navigate({ url, viewId })` with the file’s `viewId` returns “Browser view not found”. That is expected Cursor isolation — do **not** `newTab` / `position: "active"`. Leave Glass to the parent; use inherited `plugin-styx-pluto` for notebook tools.

1. **Reuse / tab navigation (default):** if a Pluto Glass tab already exists (cached `viewId` or parent `browser_tabs` list), `browser_navigate({ url, viewId })` — **omit** `position` and `newTab`. This is the path that works without minting siblings.
2. **Reveal if the pane is closed (parent, once):** if the user cannot see Glass (closed/hidden pane, they say it did not open, or this is the first visible open this session and tabs are empty), the parent may pass `position: "active"` **once** to show the UI. That can mint a sibling workbench pane; then record the result `viewId` in `glass-views.json` (hooks) and omit `position` on later navigates. Never `newTab: true` / `action: "new"` as the reveal mechanism.
3. If tab APIs are available, **list tabs** and reuse any tab whose URL host/path looks like this session’s Pluto (landing or `/edit?id=`). Match on notebook id or path — not a guessed port alone. Prefer the **6-hex** `viewId` when both a hex id and a `glass-browser-<uuid>` point at the same Pluto URL.
4. **Parent:** treat an **empty or stale tab list as unreliable**, not proof that no Glass tab exists. Ask the user which Glass tab is Pluto, or navigate to the best-known URL **with that tab’s `viewId`**, before creating anything. Empty tabs plus “need the pane visible” is **reveal once**, not `newTab`.
5. **Never** pass `newTab` / `new` / `tabs_new`. A Task child must never create a tab or pass `position: "active"`.
6. After a failed navigate, **do not** retry by spawning another tab — fix the URL (local: host `pluto_url`; remote: re-run the [resolve ladder](#local-vs-remote-ssh-glass-url) — remember → probe → ask) and reuse. Child view-not-found is not a URL bug — stop Glass work.

**Glass view cache:** After any successful **parent** Glass navigate/snapshot on this session’s Pluto URL, Styx hooks record `viewId` under `(session_id, notebook_id)` (`_landing` if no `edit?id=`) and stamp top-level **`pluto_port`** (host) for the Remote remember check. **Parent Read the file** before Glass work — `sessionStart` may print a “Known Glass views” block, but Cursor does **not** put that hook output in model-visible context (parent or Task child). Path: `$STYX_RUNTIME_DIR/sessions/<session_id>/glass-views.json`, else `$XDG_RUNTIME_DIR/styx-$UID/sessions/<session_id>/glass-views.json`, else `${TMPDIR:-/tmp}/styx-$UID/sessions/<session_id>/glass-views.json` (`STYX_RUNTIME_DIR` is MCP-process env, not the agent's — walk the fallbacks; macOS usually has no `XDG_RUNTIME_DIR`). `session_id` comes from `pluto_session_status`. Look up by `notebook_id` / `_landing` — never a single viewId for the whole session — and **reuse** with `browser_navigate({ url, viewId })` (omit `position`). If `browser_tabs` list is non-empty, confirm URL matches and refresh the map; if empty on the **parent**, still try the stored `viewId` for tab navigation (omit `position`) when a pane may exist — do **not** `newTab`. If the user cannot see Glass, **reveal once** with `position: "active"` and record the result `viewId`. A Task child can **Read** the same file (same `session_id`) but cannot attach — view-not-found is expected. On parent failure, delete that key from `entries` in the JSON (do not wipe the file) and **hard-stop** — ask the user; **never** `newTab` / `action: "new"`. One notebook → one remembered view (last success wins). Reload Window mints a new `session_id`; PlutoMCP teardown deletes the old `sessions/<id>/` (not a sessionStart wipe) — do not assume the old dir survives reload + Pluto restart.

### Path A — landing only

**Local:**

```text
status = pluto_session_status()
# reuse: browser_navigate({ url: status.pluto_url, viewId }) — omit position
# reveal (pane closed / first visible open): add position: "active" once
browser_navigate({ url: status.pluto_url })
```

**Remote SSH:** resolve Glass URL via the [ladder](#local-vs-remote-ssh-glass-url) (remember → same-port probe → ask only if needed), then navigate landing.

Tell user to pick a notebook; stop.

### Path B — after `open_notebook`

**Local:** `browser_navigate` landing (`reuse` omit `position`; `reveal` once if pane closed) then `open_notebook` → landing click.

**Remote SSH:** resolve Glass URL via the [ladder](#local-vs-remote-ssh-glass-url) first, then the same Path B steps on that URL.

**Do not** `browser_navigate` to pasted `/edit?id=` after MCP `open_notebook` — cold loads hang on `Loading cells...`. Click the notebook on landing instead. Details: [path-b-open.md](path-b-open.md).

### Exit Safe preview in Glass

When the editor shows **Safe preview** / *Code not executed in Safe preview* and live outputs are needed:

1. `browser_snapshot` the open notebook tab (reuse existing Glass — no `newTab`)
2. `browser_click` **Run notebook code** (top right)
3. Or call MCP `allow_execution` instead when appropriate (risky remote sources need the Glass button)

Do not leave Safe preview on after staging edits that need live results. Details: **pluto-workflow** [safe-preview.md](../../pluto-workflow/reference/safe-preview.md).

## User handoff (last resort)

If `cursor-ide-browser` is unavailable:

1. **Local:** give landing URL from `pluto_session_status.pluto_url` (do not open the OS browser)
2. **Remote SSH:** give the resolved client origin (remember / probe / Ports answer — same URL Glass would use)
3. Ask user to click the notebook on landing (Path B) or pick one (Path A)

Prefer **styx-start** same-turn Glass navigate over asking the user to paste a URL.

## URL forms

| Page | URL |
|------|-----|
| Landing | `<glass_url>/` |
| Notebook editor (after loaded in Glass) | `<glass_url>/edit?id=<notebook_id>` |

Plain `http://127.0.0.1:<port>/<notebook_id>` is **not** a documented Pluto route.
