You are editing a live Pluto notebook via MCP tools.

## Find the notebook (browser first)

1. Parse `pluto-notebook#<uuid>` from Design Mode `browser_element` / `dom_path` (or Glass URL `http://127.0.0.1:1234/<uuid>`).
2. Use `@pluto-context` if pasted.
3. Call `list_notebooks` only when no browser context exists.

## Workflow

1. Resolve `notebook_id` (browser → context → list_notebooks).
2. `read_cell` or `read_notebook_code` before any edit.
3. Stage with `edit_cell` / `edit_cells` / `add_cell` (`run_after=false`).
4. `submit_changes` once to run.
5. `read_cell` to verify — check `output` and structured `error` when `errored=true`.

## Cell grammar

One expression per cell. Split multi-step code across cells or wrap in `begin`/`let`.
On error: `error.kind=pluto_multi_expression` → split at `error.boundaries` or wrap begin/end.

Full primer: `docs/pluto-agent-primer.md`.
