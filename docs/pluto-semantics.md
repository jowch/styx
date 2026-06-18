# Pluto semantics for agents

Pluto notebooks are **not** scripts or `.jl` files. Each cell is a reactive node in a dependency graph. MCP tools write **whole cell bodies**; agents must respect Pluto's cell grammar and reactivity model.

Canonical MCP workflow: [rules/pluto-notebook-workflow.mdc](../rules/pluto-notebook-workflow.mdc). Tool API: PlutoMCP.jl `AGENTS.md`.

---

## 1. One expression per cell (critical)

A Pluto code cell must contain **exactly one Julia expression**.

These are **invalid** (multiple top-level statements):

```julia
using Plots
plot(sin, 0, 2pi)
```

```julia
x = 1
y = x + 1
```

Pluto will reject them at run time with errors like:

```text
syntax: extra token after end of expression
```

Boundaries in the message mark where the parser saw a second top-level statement.

### Fix: wrap in `begin … end` or `let … end`

```julia
begin
    using Plots
    plot(sin, 0, 2pi)
end
```

```julia
let
    x = 1
    y = x + 1
    y
end
```

`let` creates a local scope; `begin` does not. Prefer **`let`** when introducing temporary locals that should not become notebook globals.

### Better fix: split across cells (preferred)

Pluto's reactivity works best when each cell has one clear job:

| Cell | Code |
|------|------|
| 1 | `using Plots` |
| 2 | `plot(sin, 0, 2pi)` |

Use **`add_cell`** / **`edit_cell`** per cell, then **`submit_changes`** once.

---

## 2. Recommended cell structure

| Pattern | Guidance |
|---------|----------|
| `using` / `import` | Own cell at the top (or a dedicated setup section) |
| Constants / inputs | One binding per cell, or one `let` block |
| Derived values | Separate cells — downstream cells auto-update |
| Side effects (`println`, I/O) | Own cell; expect re-runs when upstream changes |
| Plots / rich output | Last expression in the cell is displayed |
| `@bind` widgets | **`@bind` must be the last expression** in the cell; show the bound value in a **separate** cell |

Do not paste multi-line script blocks into a single cell unless wrapped.

---

## 3. Reactivity (brief)

- All cells share one notebook module scope.
- An assignment `x = …` in cell A defines a global `x` every downstream cell may read.
- Editing cell A re-runs A and all cells that **transitively depend** on A's definitions.
- **Execution order** ≠ visual order. Use `read_notebook_code` (default) for dependency order; `get_execution_order` / `get_cell_dependencies` for debugging.
- **Visual order** matters for `add_cell` / `move_cell` placement only.

---

## 4. Markdown vs code

- Markdown cells are not code cells. Default `read_notebook_code` omits them (`include_markdown=true` to include as `# md:` blocks).
- Do not put executable Julia in markdown cells via MCP unless the user explicitly wants markdown.

---

## 5. Validate before edit (optional but useful)

`validate_cell(notebook_id, cell_id, code)` checks proposed code **without** writing it.

It returns `multi_expression` when the body is not a single expression, and `syntax_error` for parse failures.

Use it for generated code or multi-line payloads before `edit_cell`.

---

## 6. MCP edit semantics

| Tool | Behavior |
|------|----------|
| `edit_cell` | Replaces the **entire** cell body. Default `run_after=false` (stage only). |
| `edit_cells` | Batch replace; never runs. |
| `add_cell` | New cell; `after_cell_id` required when notebook is non-empty. |
| `submit_changes` | Runs all staged (dirty) cells — Pluto Cmd+S. |
| `read_cell` | Required before edit (enforced server-side). |

After staging, check receipts for `pending_run` and `stale_cell_ids`.

---

## 7. Common agent mistakes

| Mistake | Symptom | Fix |
|---------|---------|-----|
| Multi-line script in one cell | `extra token after end of expression` | Split cells or `begin`/`let` |
| Edit without read | `read_required` error | `read_cell` first |
| Run per edit | Slow, fights staging | Stage, then `submit_changes` |
| Patch `.jl` file on disk | Desync from live session | MCP tools only |
| `@bind` not last | Widget / display bugs | Move bind to last line; value in next cell |
| Ignore `stale_cell_ids` | Edit stale content | Re-read before overwrite |

---

## 8. Minimal sin(x) example (correct)

**Cell 1**

```julia
using Plots
```

**Cell 2**

```julia
plot(sin, 0, 2pi)
```

Then `submit_changes(notebook_id)`.
