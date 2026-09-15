# Path B — open a specific notebook

Use when the user names a **specific notebook** (path, name, or clear reference).

## Examples

- "Open `experiments/odes.jl` in Pluto"
- "work on my signal analysis notebook at `analysis/signal.jl`"

## Steps

1. `pluto_session_status` → if stopped, `start_pluto_session`
2. Open **landing** in Agents Glass — [glass-navigation.md](glass-navigation.md): local → `browser_navigate({ url: status.pluto_url })`; Remote SSH → ask for Ports forwarded port for `status.pluto_port`, then navigate `http://127.0.0.1:<forwarded>/`
3. `open_notebook(path="<user-specified path>")` → record `notebook_id` and basename (e.g. `reactive_xy.jl`)  
   Default: safe preview. Use `run_notebook=true` only if user asked to run.
4. **`browser_snapshot`** → **`browser_click`** the notebook link on landing (match filename).  
   **Do not** `browser_navigate` to `/edit?id=` right after MCP `open_notebook` — Glass often sticks on `Loading cells...`. The landing page has a live WebSocket; clicking the notebook uses in-app navigation that hydrates correctly. A cold `/edit?id=` load waits for WebSocket hydration and often never completes in Glass.
5. **Safe preview:** default is gated. Still proceed to edits. When the user needs live outputs/widgets (or after staging when verify needs them), **exit Safe preview yourself** — Glass `browser_click` **Run notebook code**, or MCP `allow_execution` — see **pluto-workflow** [safe-preview.md](../../pluto-workflow/reference/safe-preview.md). Don't leave the gate on and only remind.

6. Proceed to **pluto-workflow** when they ask for edits.

## Rules

- **Never** `open_notebook` without a user-specified path.
- If target may already be open: `list_notebooks` — if open, skip `open_notebook`; click it on landing.
- **`/edit?id=` after MCP open:** always use landing click (step 4). **`/edit?id=` is fine** when the user opened the notebook from landing in Glass (Path A) or the editor loaded entirely through the browser without a prior MCP `open_notebook` for that navigation.

## Safe preview

Path B default: `execution_allowed=false`. See **pluto-workflow** → [safe-preview.md](../../pluto-workflow/reference/safe-preview.md).
