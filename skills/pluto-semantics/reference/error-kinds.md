# Parse and runtime error kinds

## `pluto_multi_expression`

**Symptom:** `extra token after end of expression` + `Boundaries: [...]`

**Default fix (repair):** `edit_cell` with `begin`/`end` wrap in same cell → `submit_changes`

**Alternative:** split at reactive boundaries using `error.boundaries` — see [cell-structure.md](cell-structure.md)

**Authoring:** avoid the error by following structure patterns (`imports_cell`, `widget_cell`, `compute_cell`) in [cell-structure.md](cell-structure.md).

**`error.fixes` order:** `wrap_begin_end` first, `split_cells` second

## `runtime`

Read `error.msg`, fix code, `submit_changes`, re-read.

## Other Pluto errors agents see

| Error | Cause | Fix |
|-------|-------|-----|
| Multiple definitions | Same global in two cells | Disable one or merge |
| Cyclic reference | Dependency cycle | Break cycle |
| `@bind` widget missing | `@bind` not returning expression | Move to end or embed in `md`/`html` |

## Design Mode error clicks

Clicking `jlerror` in Design Mode includes `pluto-cell#` in `dom_path`; `visible_text` may contain Pluto's friendly split/wrap offer.
