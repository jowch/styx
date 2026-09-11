# Safe preview (execution gated)

Path B `open_notebook` defaults to **Safe preview** (`run_notebook=false`). Pluto sets `process_status = waiting_for_permission` — cells load but **do not execute**.

**Not an edit gate:** still stage and `submit_changes(wait_for_completion=false)`. Do **not** stop the turn with Safe preview still on when the user needs live outputs, widgets, or plots.

`run_all_cells` / `execute_cell` alone do **not** bypass Safe preview — exit first (below).

## Pluto source (durable)

- `SessionActions.open` sets `process_status = waiting_for_permission` when `execution_allowed=false`
- `will_run_code(notebook)` returns false in Safe preview
- Permission via Glass **Run notebook code** (`restart_process`) or MCP **`allow_execution`**

## Detect safe preview

On first `read_cell` / notebook contact (and when relevant after Path B open):

| Signal | Meaning |
|--------|---------|
| Notebook opened via Path B default `open_notebook` | Likely safe preview |
| `read_cell` → empty `output` on cells that should have values | Safe preview |
| Glass **Safe preview** banner or *Code not executed in Safe preview* on cells | Confirmed |

No dedicated MCP field flags `execution_allowed=false` — infer from context above.

## Exit Safe preview yourself (preferred)

When Safe preview is active and outputs/reactivity are needed (user expects live results, or you need to verify after staging), **exit it yourself** — do not only remind and leave the gate on.

| Path | When |
|------|------|
| **Glass:** `browser_snapshot` → `browser_click` **Run notebook code** (Agents Glass / `cursor-ide-browser`) | Prefer when Glass is already open; required for **risky remote sources** (`risky_source` from `allow_execution`) |
| **MCP (fast path):** `allow_execution(notebook_id=…, run_notebook=false)` then `submit_changes(wait_for_completion=false)` / `execute_cell` for the staged cells | Prefer when you already staged edits and only need those cells — exits the gate without queueing a full-notebook restart/run |
| **MCP (full run):** `allow_execution(notebook_id=…)` (default `run_notebook=true`) | When the whole notebook should run after exit; invoke **by name** even if hidden in the picker |

After exit, runs are **non-blocking** by default (PlutoMCP wait defaults / [#3](https://github.com/jowch/styx/issues/3)). Poll `read_cell` / `read_notebook_code` until `!running && !queued` if you need outputs. Prefer `submit_changes(wait_for_completion=false)` for staged batches.

Do **not** call `run_all_cells` / `execute_cell` **before** exiting Safe preview — they do not bypass the gate.

Use `open_notebook(..., run_notebook=true)` **only** when the user explicitly asked to open **and run** at open time.

## Still edit; stay honest

When Safe preview is active, **still stage edits** as usual. Briefly note Safe preview once if relevant, then **exit it** (table above) before claiming live outputs:

> Notebook was in **Safe preview** — exiting so cells can run (Glass **Run notebook code** or `allow_execution`).

Do **not** claim outputs/widgets are live until execution is allowed and cells have actually run. Do **not** pretend `submit_changes` executed anything while still gated.
