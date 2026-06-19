# D15 Lifecycle — Manual Validation Checklist

Walk **Path A**, **Path B**, and hook integration in a real Cursor + Agents Glass session. Use this after automated gates pass (`Pkg.test()`, `eval/run_reference.jl --all`).

**Related:** [pluto-lifecycle.md](./specs/pluto-lifecycle.md) · [dom-bridge-test-checklist.md](./dom-bridge-test-checklist.md)

---

## Before you start

### Environment

- [ ] Styx plugin installed at `~/.cursor/plugins/local/styx/` (or dev symlink from this repo)
- [ ] **pluto** MCP enabled in Cursor Settings → MCP shows **connected** (stdio up; Pluto may still be stopped)
- [ ] No dev `pluto-serve.sh` running unless you are explicitly testing proxy mode
- [ ] If MCP calls fail with `Bridge proxy error` / `ECONNREFUSED`, toggle **pluto** MCP off/on (proxy attach survives after `serve()` dies)
- [ ] Julia env bootstrapped: `./scripts/ensure-julia-env.sh` (first run only)

### Preflight script (terminal)

```bash
./scripts/d15-preflight.sh
./scripts/d15-validate-deferred.sh   # automated Scenarios 0, C.2, D, E
```

| Check | Expected (baseline) |
|-------|---------------------|
| `:2346/health` | **down** (deferred mode — Pluto not started yet) |
| `:1234` Pluto UI | **down** |
| Plugin `mcp.json` + launcher | present |

Record baseline in the log table at the bottom.

### Agent sanity (optional, same chat)

Ask: *"What is pluto_session_status?"*

| Expected | |
|----------|--|
| `pluto: "stopped"` | Before any notebook work |
| No shell script instructions | Agent uses MCP only |

---

## Scenario 0 — Deferred MCP (no Pluto yet)

**Goal:** Confirm MCP handshake works without starting Pluto.

| Step | You do | Pass criteria |
|------|--------|---------------|
| 0.1 | Enable **pluto** MCP; open a **new** agent chat | Cursor MCP panel shows pluto connected |
| 0.2 | Ask about a normal `.jl` file (not notebooks) | Agent does **not** call `start_pluto_session` |
| 0.3 | Run `./scripts/d15-preflight.sh` | `:2346` and `:1234` still down |

- [x] Scenario 0 pass *(automated 2026-06-18: preflight baseline + PlutoMCP deferred protocol tests + `d15-validate-deferred.sh`; manual 0.2 = agent must not start Pluto on non-notebook chat)*

---

## Scenario A — General intent (landing page)

**User prompt:** use command **pluto-notebooks** or say *"I want to work on my Pluto notebooks"*

### Bootstrap (first message)

| Step | Actor | Pass criteria |
|------|-------|---------------|
| A.1 | Agent | Calls `pluto_session_status` → `stopped` |
| A.2 | Agent | Calls `start_pluto_session` |
| A.3 | Agent | Opens `http://127.0.0.1:1234/` in **Agents Glass** (`cursor-ide-browser`) |
| A.4 | Agent | Short message: pick notebook on page; **does not** ask which file in chat |
| A.5 | Agent | Does **not** call `open_notebook` or `list_notebooks` during bootstrap |

- [x] A.1–A.5 pass *(proxy `serve()` session; landing opened in Glass)*

**Terminal after A.2:**

```bash
./scripts/d15-preflight.sh --expect-running
```

| Expected | |
|----------|--|
| `:2346/health` | **up** |
| `pluto_session_status` | `pluto: "running"` |

### User picks notebook (you, in Glass)

| Step | You do | Pass criteria |
|------|--------|---------------|
| A.6 | On landing page, open or create a notebook | Notebook URL is `http://127.0.0.1:1234/edit?id=<notebook_id>` |
| A.7 | Note the `notebook_id` from the Glass URL bar (for verification only) | UUID visible |

- [x] A.6–A.7 pass

### Follow-up (second message) — Design Mode edit

**User prompt:** **⌘⇧D** (Design Mode on), click a cell code line, then *"What does this cell do?"* or *"Change x to 10"*

| Step | Actor | Pass criteria |
|------|-------|---------------|
| A.8 | Hook | Submit allowed; if Pluto was stopped, hint says ask agent to start — **not** "reload MCP" / `pluto-serve.sh` |
| A.9 | Agent | `resolve_pluto_context` from `browser_element` / `dom_path` |
| A.10 | Agent | `read_cell` with resolved `notebook_id` + `cell_id` — **no UUID paste** |
| A.11 | Agent | `notebook_id` matches Glass URL from A.6 |

- [x] A.8–A.11 pass (**acceptance:** Path A follow-up resolves id via Design Mode)

### Optional edit sync

| Step | Actor | Pass criteria |
|------|-------|---------------|
| A.12 | Agent | Edits allowed; if safe preview, remind user **Run notebook code** to see outputs → `edit_cell` → `submit_changes` |
| A.13 | You | Browser cell updates without manual refresh |

- [x] A.12–A.13 pass (**acceptance:** Design Mode click → edit works — red plot line)

---

## Scenario B — Specific notebook path

**User prompt:** use command **pluto-open** or say *"Open `eval/fixtures/reactive_xy.jl` in Pluto"* (adjust path to your workspace)

### Bootstrap

| Step | Actor | Pass criteria |
|------|-------|---------------|
| B.1 | Agent | `start_pluto_session` if not already running |
| B.2 | Agent | Opens landing `http://127.0.0.1:1234/` in Glass **first** |
| B.3 | Agent | `open_notebook(path=…)` with your path |
| B.4 | Agent | Opens `http://127.0.0.1:1234/edit?id=<notebook_id>` in Glass |
| B.5 | You | Notebook visible; **blue safe-preview / Run notebook banner** (cells not auto-run) |
| B.6 | Agent | Does **not** call `run_all_cells` unless you asked to run |

- [x] B.1–B.6 pass *(safe preview banner on `reactive_xy.jl`)*

**Verify preview mode (agent or terminal):**

```bash
./scripts/d15-preflight.sh --expect-running --notebook-id <uuid>
```

Optional: agent `read_cell` on cell `11111111-1111-1111-1111-111111111111` — output should **not** show `42` until you or agent runs cells.

### Design Mode on opened notebook

| Step | You do | Pass criteria |
|------|--------|---------------|
| B.7 | ⌘⇧D, click cell `y = x * 7`, ask for a small edit | Agent resolves context + stages edit |
| B.8 | Agent `submit_changes` | Cell runs; `y` updates if `x` changed |

- [x] B.7–B.8 pass *(slider `@bind` edit; safe-preview reminder)*

---

## Scenario C — Session already running

**Context:** After A or B, Pluto still running.

| Step | User prompt | Pass criteria |
|------|-------------|---------------|
| C.1 | *"Add a cell at the end that prints hello"* | Agent skips `start_pluto_session`; uses `pluto-workflow` |
| C.2 | `pluto_session_status` | `pluto: "running"`, notebook listed |

- [x] Scenario C pass *(automated C.2: session stays running; manual C.1: agent skips `start_pluto_session` when Pluto already up)*

---

## Scenario D — Pending run stop hook

| Step | You do | Pass criteria |
|------|--------|---------------|
| D.1 | Agent stages edit (`edit_cell`, no `submit_changes`) | `pending_run` non-empty |
| D.2 | Send **next** message without submitting | Stop hook warns about staged changes (or blocks per hook config) |
| D.3 | Agent `submit_changes` | Warning clears |

- [x] Scenario D pass *(automated 2026-06-18: `warn-pending-run.py` + `d15-validate-deferred.sh`)*

---

## Scenario E — Stop session (optional)

**User prompt:** *"I'm done with notebooks for now"*

| Step | Pass criteria |
|------|---------------|
| E.1 | Agent `submit_changes` if staged |
| E.2 | Optional `stop_pluto_session` |
| E.3 | `./scripts/d15-preflight.sh` → `:2346` down, MCP still connected in Cursor |

- [x] Scenario E pass *(automated 2026-06-18: `stop_pluto_session` + preflight baseline in `d15-validate-deferred.sh`)*

---

## Failure triage

| Symptom | Likely cause | Fix |
|---------|--------------|-----|
| MCP won't connect | Julia env / launcher | `./scripts/ensure-julia-env.sh`; check Cursor MCP logs |
| Hook says "reload MCP" | Old hook copy | Reinstall/sync plugin; hook should mention `start_pluto_session` |
| `pluto_not_running` on edit | Session not started | Agent calls `start_pluto_session` first |
| Design Mode click, no `pluto-cell#` | Design Mode off or bare `main` click | ⌘⇧D, re-click inside cell |
| Notebook URL 403 / secret | Skipped landing (Path B) | Open `http://127.0.0.1:1234/` first, then click notebook on landing |
| `Loading cells...` forever | Pasted `/edit?id=` after MCP `open_notebook` | Click notebook on landing instead — see [path-b-edit-url-loading.md](../known-issues/path-b-edit-url-loading.md) |
| MCP tools fail after killing `serve()` | `connect()` was in **proxy** mode; bridge died | Toggle **pluto** MCP off/on in Cursor Settings (restart with no `serve()` running) |

---

## Validation log

| Date | Tester | 0 deferred | A bootstrap | A Design Mode | B open + preview | C skip start | D pending_run | Notes |
|------|--------|------------|-------------|---------------|------------------|--------------|---------------|-------|
| 2026-06-18 | live session | ☑ | ☑ | ☑ | ☑ | ☑ | ☑ | Path A/B Glass; automated 0/C/D/E via `scripts/d15-validate-deferred.sh` |
| 2026-06-18 | live session | ☐ | ☑ | ☑ | ☑ | ☐ | ☐ | Proxy `serve()`; Path A plot edit; Path B `reactive_xy.jl`; acceptance signed off |

When all rows pass, check the two remaining boxes in [pluto-lifecycle.md § Acceptance](./specs/pluto-lifecycle.md#acceptance-010):

- [x] Next prompt after Path A resolves `notebook_id` via Design Mode / URL
- [x] Design Mode click → edit works on opened notebook
