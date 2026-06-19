You are editing a live Pluto notebook via MCP tools.

## Session (D15)

Notebook work is **on demand**. If the user wants Pluto notebooks, use skill **pluto-session** — do not ask them to run shell scripts.

Lifecycle tools (`start_pluto_session`, `open_notebook`, etc.) may be hidden in the MCP picker — **invoke by name**.

Glass: **`cursor-ide-browser`** in Agents Window (`glass-browser-*`). Path B: landing → `open_notebook` → `browser_click` notebook on landing (not pasted `/edit?id=`). Not `plugin-browse-browser`.

## Cell edits

Once a notebook is open, use skill **pluto-workflow**. Design Mode: **Cmd+Shift+D** → click → `resolve_pluto_context` → `read_cell` → stage → `submit_changes`.

**Safe preview:** Path B default — remind user to click **Run notebook code** in Glass; still edit when asked. Do not use `run_all_cells` as a substitute.

Parse errors: default `begin`/`end` wrap — skill **pluto-semantics**.
