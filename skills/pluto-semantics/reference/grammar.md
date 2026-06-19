# Cell grammar (Pluto authoritative)

Enforced in Pluto `parse_custom` (`src/analysis/Parse.jl`):

- Each code cell = **exactly one Julia expression**
- Multiple expressions → `extra token after end of expression` + `Boundaries: [...]`
- MCP maps this to `error.kind = pluto_multi_expression`

## Valid single-expression forms

| Form | Valid? |
|------|--------|
| `begin … end` / `let … end` | Yes — one compound expression |
| `a; b` (semicolon chain) | Yes — last value is cell output |
| `function f() … end` | Yes |
| Two statements on separate lines | **No** |

## Fix errors: wrap `begin`/`end` (default)

```julia
begin
    using Plots
    plot(sin, 0, 2pi)
end
```

Use **`let`/`end`** when temporaries must not become notebook globals.

When a user asks to **fix** a multi-expression error, default to **`begin`/`end`** in the **same cell** unless separate reactive steps are intended.

## Split cells (intentional reactive steps)

| Cell | Code |
|------|------|
| 1 | `using Plots` |
| 2 | `plot(sin, 0, 2pi)` |

## New code structure

| Pattern | Guidance |
|---------|----------|
| `using` / `import` | Own cell at top |
| Constants / inputs | One binding per cell, or one `let` block |
| Derived values | Separate cells |
| Plots | Last expression is displayed |
| `@bind` | **`@bind` must be last** in cell (or embedded in `md"…$(@bind x …)…"`) |

## `@bind` rule (from Pluto source)

`@bind` expands to `create_bond(...)` which returns a `Bond` object — that **is** the cell output. Code after `@bind` without `begin`/`end` → parse error. Bound variable usage belongs in **downstream cells**.

## Trailing semicolon

`ends_with_semicolon` suppresses output display.
