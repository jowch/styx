---
description: Explain a Pluto cell — parse Design Mode dom_path or use manual IDs
---

# Pluto explain cell (explain intent)

The user wants an **explanation** of a Pluto notebook cell (code, output, or plot).

## Resolve IDs

1. **Design Mode (preferred):** Parse `pluto-notebook#` and `pluto-cell#` from `dom_path` / `browser_element` in the prompt.
2. **Glass browser URL:** `http://127.0.0.1:1234/<notebook_id>`.
3. **Manual fallback:** Use `$ARGUMENTS` or `@pluto-context` for IDs.
4. **`list_notebooks`** only if no browser/context ids are available.
5. If missing, ask the user to ⌥+click the cell or provide IDs.

## Agent actions

1. Call MCP **`read_cell`** for the target cell.
2. Explain what the cell does, its output, and how it fits the notebook.
3. If dependencies matter, call **`get_cell_dependencies`** or **`read_notebook_code`** (Layer 2 graph tools).

Do not edit unless the user explicitly asks to change code afterward.
