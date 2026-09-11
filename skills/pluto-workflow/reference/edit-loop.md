# Stage-first edit loop

Pluto is a **live reactive session**, not a `.jl` file to patch. MCP writes **server state**; the browser editor has a separate draft buffer (last-write-wins).

## Pipeline

```
resolve notebook_id → read_cell (note Safe preview if active)
  → read_cell / read_notebook_code
  → edit_cell / edit_cells / add_cell  (run_after=false)
  → submit_changes(wait_for_completion=false)
  → if Safe preview and outputs needed: exit it (Glass Run notebook code or allow_execution)
  → read_cell (verify; poll until !running && !queued if you need outputs)
```

| Step | Tool | Notes |
|------|------|-------|
| Read | `read_cell`, `read_notebook_code` | Required before writes (MCP + hooks enforce) |
| Stage | `edit_cell`, `edit_cells`, `add_cell` | Default `run_after=false` |
| Validate | `validate_cell` | Optional |
| Run | `submit_changes` | Once per batch (Pluto Cmd+S); prefer `wait_for_completion=false` |
| Exit gate | Glass **Run notebook code** or `allow_execution` | When Safe preview is on and live outputs are needed — exit yourself |
| Verify | `read_cell` | Check `output`, `errored`, `error`; re-read if still `running`/`queued` |

## Safety

- Re-read before overwriting if the user was typing in the browser.
- Call **`submit_changes(wait_for_completion=false)`** before ending the turn if edits were staged (stdio-bound sessions; see SKILL.md / [#3](https://github.com/jowch/styx/issues/3)).
- Do **not** end the turn with Safe preview still on when the user needs live outputs — exit via Glass or `allow_execution` ([safe-preview.md](safe-preview.md)).

## Cell structure

Follow **pluto-semantics** [cell-structure.md](../../pluto-semantics/reference/cell-structure.md): `imports_cell`, `widget_cell`, `compute_cell` with `begin`/`end` by default, `let`/`end` for scoped temps.

## When fixing parse errors

Wrap **`begin`/`end`** in place or split at reactive boundaries. See **pluto-semantics** [grammar.md](../../pluto-semantics/reference/grammar.md).
