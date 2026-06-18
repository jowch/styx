---
name: pluto-workflow
description: >-
  Edit live Pluto.jl notebooks via PlutoMCP — Design Mode clicks, stage-first
  edits, submit_changes, and error recovery. Use after a notebook is open in
  the Pluto session, or when editing cells with browser context.
---

# Pluto workflow (cell editing)

Pluto is a **live reactive session**, not a `.jl` file to patch. MCP writes **server state**; the browser editor has a separate draft buffer (last-write-wins).

## Prerequisites

If the user wants notebook work and Pluto may not be running, use **pluto-session** first. This skill assumes a notebook is **open in the live session** (Glass tab at `http://127.0.0.1:1234/<notebook_id>`).

## Find the notebook (browser first)

Do **not** start with `list_notebooks` when browser context exists.

| Priority | Source |
|----------|--------|
| 1 | **Design Mode** — **Cmd+Shift+D** in Glass, click cell. `resolve_pluto_context` → `read_cell`. |
| 2 | Glass URL `http://127.0.0.1:1234/edit?id=<notebook_id>` |
| 3 | `@pluto-context` block in prompt |
| 4 | `list_notebooks` — when no browser context |

If `pluto-cell#` is missing, ask user to enable Design Mode and re-click inside a cell.

## Safe preview (execution gated)

Path B `open_notebook` defaults to **Safe preview** (`run_notebook=false`). Pluto sets `process_status = waiting_for_permission` — cells load but **do not execute**.

**You cannot exit safe preview via MCP.** Do not call `run_all_cells` or `execute_cell` expecting execution — they do not bypass safe preview.

### Detect safe preview

On first `read_cell` / notebook contact (and when relevant after Path B open):

| Signal | Meaning |
|--------|---------|
| Notebook opened via Path B default `open_notebook` | Likely safe preview |
| `read_cell` → empty `output` on cells that should have values | Safe preview |
| Glass **Safe preview** banner or *Code not executed in Safe preview* on cells | Confirmed |

### Remind the user — do not block edits

When safe preview is active, **still stage edits** as usual. **Also** tell the user (once per notebook session, or when they expect live output):

> This notebook is in **Safe preview** — I can change code, but cells won't run and you won't see outputs, sliders, or plots update until you click **Run notebook code** in Glass (top right).

Do **not** claim outputs/widgets are live until they have run. Do **not** pretend `submit_changes` or `run_all_cells` executed anything in preview mode.

### When the user asks you to run

If they say *run the notebook*, *execute cells*, *run it*, etc.:

> I can't trigger **Run notebook code** from here — please click **Run notebook code** in Glass (top right). Until then, staged code won't execute.

Do **not** use `run_all_cells` / `execute_cell` as a substitute.

Use `open_notebook(..., run_notebook=true)` **only** when the user explicitly asked to open **and run** at open time.

---

## Edit workflow (stage-first)

```
resolve notebook_id → read_cell (note safe preview; remind user if active)
  → read_cell / read_notebook_code
  → edit_cell / edit_cells / add_cell  (run_after=false)
  → submit_changes
  → read_cell (verify code staged; remind again if outputs still empty in preview)
```

| Step | Tool | Notes |
|------|------|-------|
| Read | `read_cell`, `read_notebook_code` | Required before writes (MCP + hooks enforce) |
| Stage | `edit_cell`, `edit_cells`, `add_cell` | Default `run_after=false` |
| Validate | `validate_cell` | Optional |
| Run | `submit_changes` | Once per batch |
| Verify | `read_cell` | Check `output`, `errored`, `error` |

When **fixing** `pluto_multi_expression`, default to **`begin`/`end`** in the same cell. See **pluto-semantics**.

## Reading errors

| Field | Use |
|-------|-----|
| `error.kind` | e.g. `pluto_multi_expression` |
| `error.hint` | Default fix text |
| `error.boundaries` | Byte positions for splits |
| `error.fixes` | `wrap_begin_end` first, then `split_cells` |

## Tool names (canonical)

- Read: `read_cell`, `read_notebook_code`, `resolve_pluto_context`, `list_notebooks`
- Write: `edit_cell`, `edit_cells`, `add_cell`, `delete_cell`, `move_cell`, `submit_changes`
- Lifecycle: `pluto_session_status`, `start_pluto_session`, `open_notebook` (see **pluto-session**)

## Safety

- Re-read before overwriting if the user was typing in the browser.
- Call **`submit_changes`** before ending the turn if edits were staged.

## Common mistakes

| Mistake | Fix |
|---------|-----|
| Edit before session bootstrap | **pluto-session** first |
| `list_notebooks` before browser context | Design Mode click or Glass URL |
| Edit without read | `read_cell` first |
| Patch `.jl` on disk | MCP only |
| Forget safe preview reminder | Note preview mode; outputs won't update until **Run notebook code** |
| User asks to run notebook | Direct to **Run notebook code** in Glass; no `run_all_cells` |
| Claim `submit_changes` ran cells in safe preview | Remind user to run in Glass to see results |
