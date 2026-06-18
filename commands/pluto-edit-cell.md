---
description: Edit a Pluto cell — parse Design Mode dom_path or use manual IDs (stage-first)
---

# Pluto edit cell (edit intent)

The user wants to **change code** in a Pluto notebook cell.

## Resolve IDs

1. **Design Mode (preferred):** Parse `pluto-notebook#` and `pluto-cell#` from any `dom_path` / `browser_element` block in the prompt.
2. **Glass browser URL:** `http://127.0.0.1:1234/<notebook_id>`.
3. **Manual fallback:** Use `$ARGUMENTS` or an `@pluto-context` block for `notebook_id` and `cell_id`.
4. **`list_notebooks`** only if no browser/context ids are available.
5. If still missing, ask the user to ⌥+click the cell in Glass Design Mode or paste IDs.

## Agent actions

1. **`read_cell`** first (required — MCP read-before-edit guard).
2. Apply changes with **`edit_cell`** and **`run_after=false`** (default).
3. Call **`submit_changes`** when the user is ready to run staged cells — do not auto-run unless asked.
4. Return the mutation receipt summary (`pending_run`, affected cells).

If the user's edit request spans multiple cells, use **`edit_cells`** and one **`submit_changes`**.
