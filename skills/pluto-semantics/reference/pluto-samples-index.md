# Pluto sample notebooks (local reference)

Ground agent cell-structure patterns in **published Pluto samples** shipped with Pluto.jl. Paths below use the Julia package cache; version hash (`d9Dpv`) may differ — glob `~/.julia/packages/Pluto/*/sample/` if needed.

**Do not** mimic `test_*.jl` or crash fixtures — those are editor/regression notebooks, not style guides.

---

## Primary corpus

| Path | Role |
|------|------|
| `~/.julia/packages/Pluto/*/sample/` | Bundled teaching + featured notebooks |
| `~/.julia/packages/PlutoUI/*/src/*.jl` | Widget implementations + inline demos (authoring style differs from user notebooks) |

Featured notebooks in `sample/` include frontmatter pointing at [JuliaPluto/featured](https://github.com/JuliaPluto/featured).

---

## Notebooks to study

| File | Study for |
|------|-----------|
| **`Getting started.jl`** | Parse errors; split **or** `begin`/`end` fix; `@bind` must return |
| **`Basic.jl`** | Simple reactive chains (`n` → `seq` → result) |
| **`Basic mathematics.jl`** | Pedagogical micro-cells (many single bindings) |
| **`Plots.jl.jl`** | `imports_cell` rhythm (`using Plots`); **`begin`/`end` plot chains**; reactive plotting pitfalls |
| **`PlutoUI.jl.jl`** | `@bind` → consumer; `md` + embedded `@bind`; `combine()`; `Button` + `let` |
| **`Interactivity.jl`** | `@bind` mechanics; `begin` + multiple bonds → one `md` layout |
| **`Markdown.jl`** | Prose as `md"…"` Julia cells |

---

## Patterns by source

| Pattern | Example location |
|---------|------------------|
| Dedicated `using` cell | `Plots.jl.jl` — `using Plots` before first plot |
| `begin`/`end` plot chain | `Plots.jl.jl` — `plot` + `plot!` + title in one cell |
| Standalone `@bind` | `PlutoUI.jl.jl` — `@bind x Slider(5:15)` then `x` |
| `@bind` in `md` | `PlutoUI.jl.jl` — `Scrubbable` in interpolated markdown |
| `combine()` forms | `PlutoUI.jl.jl` / `PlutoUI/.../Combine.jl` |
| `let` after `Button` | `PlutoUI.jl.jl` — recompute on button |
| RangeSlider API | `PlutoUI/.../RangeSlider.jl` — not in main `PlutoUI.jl.jl` tutorial |

---

## PlutoUI package demos

`PlutoUI/EAlc1/src/Builtins.jl`, `RangeSlider.jl`, etc. are **dual-purpose** notebook + module source. They use heavy `begin` blocks for **type definitions** — do not copy that style into user notebooks. Use the **demo sections** at the bottom of each file for widget usage (`@bind x RangeSlider(...)`).

---

## How agents should use this index

1. Before inventing layout, skim the relevant sample for the feature (plots, widgets, markdown).
2. Follow [cell-structure.md](cell-structure.md) for agent policy; use samples for idioms (widget types, `combine`, plot warnings).
3. Cite sample paths in review/debug when disputing cell-split vs wrap choices.
