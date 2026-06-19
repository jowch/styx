# Notebook cell structure (agent authoring)

Pluto enforces **one expression per cell** (parse). This doc is the **structure model** for how agents should organize notebooks — not the same as pedagogy notebooks that split every line for learners.

**Samples index:** [pluto-samples-index.md](pluto-samples-index.md)

---

## Two layers

| Layer | Rule |
|-------|------|
| **Parse** | One Julia expression per cell (`begin`/`end`, `let`/`end`, `md"…"`, `@bind`, `function`… all count) |
| **Structure** | Group by **reactive role**; use `begin`/`end` inside a cell for multi-statement **conceptual blocks** |

**Split cells at reactive boundaries** (imports → widget → compute → output). **Do not** split every statement into its own cell when those statements share one reactive step.

---

## Structure patterns

### `imports_cell` — dedicated package loading

One early cell owns all `using` / `import`, wrapped in `begin`/`end`:

```julia
begin
    using Plots
    using PlutoUI
end
```

Add new packages here — not scattered through the notebook. Comma-import (`using A, B`) is one expression and also valid; prefer the block when the list may grow.

---

### `widget_cell` — interactive input

One reactive input per cell. **`@bind` must be the returning expression.**

**Standalone:**

```julia
@bind xrange RangeSlider(-10:0.25:10; default=-5:5)
```

**Embedded in prose:**

```julia
md"""
Range: $(@bind xrange RangeSlider(-10:0.25:10; default=-5:5))
"""
```

**Multi-widget form** — prefer `PlutoUI.combine()` when controls belong to one form (see `PlutoUI.jl.jl`, `Combine.jl`).

Do **not** put bare `using` and `@bind` as adjacent top-level statements — that is `pluto_multi_expression`. Imports belong in `imports_cell`; or wrap in `begin`/`end` if truly one self-contained widget cell.

---

### `compute_cell` — multi-step logic (default: `begin`/`end`)

When several statements must re-run **together** as one reactive step, prefer **one cell** with `begin`/`end` over many single-line cells:

```julia
begin
    lo, hi = first(xrange), last(xrange)
    plot(sinc, lo, hi, color=:red, xlabel="x", title="sinc")
end
```

**Plot chains** — official pattern from `Plots.jl.jl`: `plot` + `plot!` + styling in one `begin` block so partial updates do not leave stale series.

**Rule of thumb:** if editing one line would always require editing the others, keep them in one `begin` cell.

---

### `output_cell` — display result

Single expression whose value is the cell output: `plot(...)`, `md"…$(x)…"`, bare variable name, `HTML(...)`.

Pedagogy notebooks often use a bare `x` cell after `@bind x` — valid for teaching; agents may fold display into `compute_cell` when it is not a separate reactive step.

---

### `scoped_cell` — `let`/`end` for locals

Use **`let`/`end`** (not `begin`/`end`) when temporaries must **not** become notebook globals:

```julia
let
    url = "https://example.com/data.csv"
    data = CSV.read(download(url), DataFrame)
    nrow(data)
end
```

**Button triggers** — `PlutoUI.jl.jl` pattern: `@bind go Button("Recompute")` in `widget_cell`, then:

```julia
let
    go
    md"Result: $(rand(1:100))"
end
```

Prefer `let` over `begin` when the only goal is hiding intermediates.

---

## Reactive boundaries (when to split cells)

| Boundary | Split? | Why |
|----------|--------|-----|
| Imports vs rest of notebook | **Yes** | `imports_cell` runs once; clear dependency root |
| Each `@bind` / form | **Yes** | Bond output is the cell value; downstream cells consume bound vars |
| Derived computation vs input | **Often** | Separate reactive steps (e.g. `x` → `y = f(x)`) |
| Statements in one plot/setup chain | **No** — use `begin` | Must re-run atomically (`Plots.jl.jl`) |
| Prose vs code | **Yes** | `md"…"` cells alternate with executable cells (`Plots.jl.jl` rhythm) |

---

## Agent vs pedagogy notebooks

Official samples (`Pluto/d9Dpv/sample/`) often use **many tiny cells** so learners see each reactive step (`Basic.jl`, `PlutoUI.jl.jl` — `@bind` then `x` then consumer).

**Agents should:**

- Consolidate with `begin`/`end` inside a cell for cohesive blocks
- Still split at **widget** and **import** boundaries
- Not copy empty spacer cells or over-split identical logic unless teaching

---

## Quick decision table

| Situation | Action |
|-----------|--------|
| Adding packages | Append to `imports_cell` (`begin`/`end`) |
| Adding slider / control | New `widget_cell` (`@bind` or `md` + `@bind`) |
| Multi-line plot or setup | One `compute_cell` with `begin`/`end` |
| Local temps, no new globals | `let`/`end` |
| `pluto_multi_expression` on existing cell | `begin`/`end` wrap in place **or** split at reactive boundaries — see [grammar.md](grammar.md) |
| Unsure if steps share one reactive step | `read_notebook_code` for dependency order |
