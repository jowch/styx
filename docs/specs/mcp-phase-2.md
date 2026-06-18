# MCP Phase 2 Spec — Graph & Validation

> Staging doc for PlutoMCP.jl fork. **Implemented** in `src/Graph.jl` (Phase 1 gate passed).

## Goal

LSP-like diagnostics when reactivity debugging is needed. Not part of the default read/edit loop — listed in MCP schema only, not injected into agent system prompts.

## Trigger to implement

Phase 1 works but agents hit: "why did this re-run?", "where is `foo` defined?", "is this valid Pluto cell syntax?"

## Tools

| Tool | Input | Returns |
|------|-------|---------|
| `get_cell_dependencies` | `notebook_id`, `cell_id` | `{upstream: [cell_ids], symbols: [...]}` |
| `get_cell_dependents` | `notebook_id`, `cell_id` | `{downstream: [cell_ids]}` |
| `find_symbol_definitions` | `notebook_id`, `symbol` | `[{cell_id, line_hint}]` |
| `find_symbol_references` | `notebook_id`, `symbol` | `[{cell_id, line_hint}]` |
| `validate_cell` | `notebook_id`, `cell_id`, `code` | `{valid, errors[]}` |
| `search_code` | `notebook_id`, `query` | `[{cell_id, snippet}]` — text only |

## Implementation notes

- Source: `nb.topology` / Pluto `ExpressionExplorer`
- `validate_cell`: parse + single-expression-unit rules (catch multi-top-level mistakes)
- `search_code` vs symbol tools: different results for shadowed names

## Acceptance

- After editing cell A, `get_cell_dependents(A)` lists cells that would re-run on `submit_changes`
- `validate_cell` rejects invalid code before `edit_cell`
- `search_code("foo")` ≠ `find_symbol_references("foo")` when shadowed
