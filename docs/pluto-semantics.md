# Pluto cell semantics (reference)

Human-readable mirror of **`skills/pluto-semantics/`**. Agents should use the skill and its `reference/` files (especially [pluto-sources.md](../skills/pluto-semantics/reference/pluto-sources.md) for Pluto.jl citations).

---

## One expression per cell (critical)

A Pluto code cell must contain **exactly one Julia expression**.

These are **invalid** (multiple top-level statements):

```julia
using Plots
plot(sin, 0, 2pi)
```

Pluto rejects them with `pluto_multi_expression` (MCP) or `syntax: extra token after end of expression` (raw runner). **`Boundaries: […]`** marks byte positions where extra statements start.

### Fix: wrap in `begin … end` or `let … end` (preferred when fixing errors)

```julia
begin
    x = 1
    y = x + 1
    y
end
```

Use **`let`** when temporaries should not become notebook globals.

When a user asks to **fix** this error, default to **`begin`/`end`** in the same cell — most users want the code kept together.

### Alternative: split across cells

Use when each step should be a separate reactive node:

| Cell | Code |
|------|------|
| 1 | `x = 1` |
| 2 | `y = x + 1` |
| 3 | `y` |

---

## Recommended cell structure (new code, not error recovery)

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

| `error.kind` | Meaning | Agent action (default) |
|--------------|---------|------------------------|
| `pluto_multi_expression` | Multiple top-level statements | **`edit_cell` with `begin`/`end` wrap**, then `submit_changes` |
| `runtime` | Ordinary exception | Read `msg`, fix code |

`error.fixes` is ordered: `wrap_begin_end` first, `split_cells` second.
