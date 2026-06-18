---
description: Focus on a Pluto cell for reading — parse Design Mode dom_path or use manual IDs
---

# Pluto select cell (read intent)

The user wants to **read / inspect** a Pluto notebook cell.

## Resolve IDs

1. **Design Mode (preferred):** If the conversation includes a `browser_element` block or `dom_path` line, extract:
   - `pluto-notebook#([0-9a-f-]+)` → `notebook_id`
   - `pluto-cell#([0-9a-f-]+)` → `cell_id`
2. **Manual fallback:** If the user provided `$ARGUMENTS`, parse `notebook_id` and `cell_id` from there.
3. **@pluto-context block:** Use IDs from a pasted context block.
4. If still unknown, call `list_notebooks` and ask which cell.

## Agent actions

1. Call MCP **`read_cell`** with the resolved IDs.
2. Summarize the cell code and output for the user.
3. Use **`read_notebook_code`** only if broader notebook context is needed.

Do not edit in this command — read only.
