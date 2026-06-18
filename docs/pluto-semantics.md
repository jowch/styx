# Pluto cell semantics (reference)

Deep reference for Pluto's cell grammar and reactivity. For the full agent training guide (browser-first discovery, staging workflow, error fields), start with **[pluto-agent-primer.md](./pluto-agent-primer.md)**.

---

## One expression per cell (critical)

A Pluto code cell must contain **exactly one Julia expression**.

These are **invalid** (multiple top-level statements):

```julia
using Plots
plot(sin, 0, 2pi)
```

Pluto rejects them with `pluto_multi_expression` (MCP) or `syntax: extra token after end of expression` (raw runner). **`Boundaries: […]`** marks byte positions where extra statements start.

### Fix: wrap in `begin … end` or `let … end`

```julia
begin
    using Plots
    plot(sin, 0, 2pi)
end
```

### Better fix: split across cells (preferred)

| Cell | Code |
|------|------|
| 1 | `using Plots` |
| 2 | `plot(sin, 0, 2pi)` |

---

## Recommended cell structure

| Pattern | Guidance |
|---------|----------|
| `using` / `import` | Own cell at the top |
| Constants / inputs | One binding per cell, or one `let` block |
| Derived values | Separate cells — downstream auto-updates |
| Plots / rich output | Last expression is displayed |
| `@bind` widgets | **`@bind` must be last**; bound value in next cell |

---

## Reactivity

- Shared notebook module scope.
- Edit upstream → downstream cells re-run.
- Execution order ≠ visual order (`read_notebook_code` vs `get_cell_order`).

---

## Validate before edit

`validate_cell(notebook_id, cell_id, code)` returns `multi_expression` when the body is not a single expression.

---

## MCP edit semantics

| Tool | Behavior |
|------|----------|
| `edit_cell` | Replaces entire cell body; default `run_after=false` |
| `submit_changes` | Batch run staged cells (Cmd+S) |
| `read_cell` | Returns `output` + structured `error` when errored |

---

## Error field reference (PlutoMCP)

When `read_cell` returns `errored: true`, check `error`:

| `error.kind` | Meaning | Agent action |
|--------------|---------|--------------|
| `pluto_multi_expression` | Multiple top-level statements | Split at `boundaries` or wrap `begin`/`let` |
| `runtime` | Ordinary exception | Read `msg`, use graph tools / fix code |

The `output` string mirrors the browser hint text for known Pluto parse errors.
