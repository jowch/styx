# Path B — open a specific notebook

Use when the user names a **specific notebook** (path, name, or clear reference).

## Examples

- "Open `experiments/odes.jl` in Pluto"
- "work on my signal analysis notebook at `analysis/signal.jl`"

## Steps

1. `pluto_session_status` → if stopped, `start_pluto_session`
2. Open **landing** in Agents Glass — [glass-navigation.md](glass-navigation.md): `browser_navigate({ url: "http://127.0.0.1:1234/", position: "active" })`
3. `open_notebook(path="<user-specified path>")` → record `notebook_id` and basename (e.g. `reactive_xy.jl`)  
   Default: safe preview. Use `run_notebook=true` only if user asked to run.
4. **`browser_snapshot`** → **`browser_click`** the notebook link on landing (match filename).  
   **Do not** navigate to `/edit?id=` directly after MCP open — hangs on `Loading cells...` ([known issue](../../../docs/known-issues/path-b-edit-url-loading.md)).
5. Safe-preview reminder:

   > Your notebook is open in **Safe preview** — code won't run until you click **Run notebook code** in Glass (top right). I can still edit cells; you won't see outputs or widgets update until you run.

6. Proceed to **pluto-workflow** when they ask for edits.

## Rules

- **Never** `open_notebook` without a user-specified path.
- If target may already be open: `list_notebooks` — if open, skip `open_notebook`; click it on landing.

## Safe preview

Path B default: `execution_allowed=false`. See **pluto-workflow** → [safe-preview.md](../../pluto-workflow/reference/safe-preview.md).
