# Safe preview (execution gated)

Path B `open_notebook` defaults to **Safe preview** (`run_notebook=false`). Pluto sets `process_status = waiting_for_permission` — cells load but **do not execute**.

**You cannot exit safe preview via MCP.** Do not call `run_all_cells` or `execute_cell` expecting execution — they do not bypass safe preview.

## Pluto source (durable)

- `SessionActions.open` sets `process_status = waiting_for_permission` when `execution_allowed=false`
- `will_run_code(notebook)` returns false in Safe preview
- User grants permission via **Run notebook code** in Glass → `restart_process` WebSocket message

## Detect safe preview

On first `read_cell` / notebook contact (and when relevant after Path B open):

| Signal | Meaning |
|--------|---------|
| Notebook opened via Path B default `open_notebook` | Likely safe preview |
| `read_cell` → empty `output` on cells that should have values | Safe preview |
| Glass **Safe preview** banner or *Code not executed in Safe preview* on cells | Confirmed |

No dedicated MCP field flags `execution_allowed=false` — infer from context above.

## Remind the user — do not block edits

When safe preview is active, **still stage edits** as usual. **Also** tell the user (once per notebook session, or when they expect live output):

> This notebook is in **Safe preview** — I can change code, but cells won't run and you won't see outputs, sliders, or plots update until you click **Run notebook code** in Glass (top right).

Do **not** claim outputs/widgets are live until they have run. Do **not** pretend `submit_changes` or `run_all_cells` executed anything in preview mode.

## When the user asks you to run

If they say *run the notebook*, *execute cells*, *run it*, etc.:

1. **`allow_execution(notebook_id=…)`** — exits safe preview and runs cells (default `run_notebook=true`).
2. **Or** ask them to click **Run notebook code** in Glass if they prefer the UI.

Do **not** call `run_all_cells` / `execute_cell` **before** `allow_execution` — they do not bypass safe preview.

Use `open_notebook(..., run_notebook=true)` **only** when the user explicitly asked to open **and run** at open time.
