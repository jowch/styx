# Stage-first edit loop

Pluto is a **live reactive session**, not a `.jl` file to patch. MCP writes **server state**; the browser editor has a separate draft buffer (last-write-wins).

## Pipeline

```
resolve notebook_id → read_cell (note safe preview; remind if active)
  → read_cell / read_notebook_code
  → edit_cell / edit_cells / add_cell  (run_after=false)
  → submit_changes
  → read_cell (verify code staged; remind again if outputs empty in preview)
```

| Step | Tool | Notes |
|------|------|-------|
| Read | `read_cell`, `read_notebook_code` | Required before writes (MCP + hooks enforce) |
| Stage | `edit_cell`, `edit_cells`, `add_cell` | Default `run_after=false` |
| Validate | `validate_cell` | Optional |
| Run | `submit_changes` | Once per batch (Pluto Cmd+S) |
| Verify | `read_cell` | Check `output`, `errored`, `error` |

## Safety

- Re-read before overwriting if the user was typing in the browser.
- Call **`submit_changes`** before ending the turn if edits were staged.

## When fixing parse errors

Default to **`begin`/`end`** in the same cell. See **pluto-semantics**.
