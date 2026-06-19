# Parse and runtime error kinds

## `pluto_multi_expression`

**Symptom:** `extra token after end of expression` + `Boundaries: [...]`

**Default fix:** `edit_cell` with `begin`/`end` wrap in same cell → `submit_changes`

**Alternative:** split cells using `error.boundaries` when separate reactive steps are intended

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
