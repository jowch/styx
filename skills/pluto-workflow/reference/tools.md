# Canonical MCP tool names

Do not use legacy aliases (`get_cell`, `set_cell_code`, `run_cell`).

## Read

- `read_cell`
- `read_notebook_code`
- `resolve_pluto_context`
- `list_notebooks`

## Write

- `edit_cell`
- `edit_cells`
- `add_cell`
- `delete_cell`
- `move_cell`
- `submit_changes`

## Lifecycle (see **pluto-session**)

- `pluto_session_status`
- `start_pluto_session`
- `stop_pluto_session`
- `open_notebook`

## Projection rules

See PlutoMCP `AGENTS.md` for `read_notebook_code` shape (`code`, `cell_ids`, `stale_cell_ids` — not `cells[]`).
