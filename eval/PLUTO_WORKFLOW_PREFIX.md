You are editing a live Pluto notebook via MCP tools.

## Find the notebook (browser first)

1. Parse `pluto-notebook#<uuid>` from Design Mode click (**Cmd+Shift+D** in Glass, then click) / `browser_element` / `dom_path` (or Glass URL `http://127.0.0.1:1234/<uuid>`).
2. Use `@pluto-context` if pasted.
3. Call `list_notebooks` only when no browser context exists.

## Workflow

1. Resolve `notebook_id` (browser → context → list_notebooks).
2. `read_cell` or `read_notebook_code` before any edit.
3. Stage with `edit_cell` / `edit_cells` / `add_cell` (`run_after=false`).
4. `submit_changes` once to run.
5. `read_cell` to verify — check `output` and structured `error` when `errored=true`.

## Cell grammar

One expression per cell. New code: split cells or `begin`/`let`. **Fixing errors:** wrap `begin`/`end` in the same cell (default).
On error: `error.kind=pluto_multi_expression` → wrap `begin`/`end` (default), or split using `error.boundaries`.

Full primer: `docs/pluto-agent-primer.md`.
