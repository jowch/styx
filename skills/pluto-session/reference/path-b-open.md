# Path B — open a specific notebook

Use when the user names a **specific notebook** (path, name, or clear reference).

## Examples

- "Open `experiments/odes.jl` in Pluto"
- "work on my signal analysis notebook at `analysis/signal.jl`"

## Steps

1. `pluto_session_status` → if stopped, `start_pluto_session`
2. Open **landing page** first in Agents Glass: `http://127.0.0.1:1234/`  
   *(Sets loopback session cookies — required before notebook URLs work reliably, D14.)*
3. `open_notebook(path="<user-specified path>")` → record `notebook_id`  
   Default: safe preview (like Pluto UI — no auto-run). Use `run_notebook=true` only if user asked to run.
4. Open **notebook URL** in Agents Glass: `http://127.0.0.1:1234/edit?id=<notebook_id>`  
   **Not** bare `http://127.0.0.1:1234/<notebook_id>` — that fails in Glass.
5. Tell the user:

   > Your notebook is open in **Safe preview** — code won't run until you click **Run notebook code** in Glass (top right). I can still edit cells; you won't see outputs or widgets update until you run.

   Use `run_notebook=true` on `open_notebook` **only** if the user explicitly asked to open **and run**.

6. Proceed to **pluto-workflow** when they ask for edits (remind about preview if outputs matter).

## Rules

- **Never** `open_notebook` without a user-specified path. Do not scan the repo and pick a file.
- If target notebook may already be open: `list_notebooks` — if open, skip `open_notebook`; open notebook URL in Glass.

## Safe preview

Path B default opens in Safe preview (`execution_allowed=false`). See **pluto-workflow** → [safe-preview.md](../../pluto-workflow/reference/safe-preview.md).
