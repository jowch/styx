# Design Mode and context resolution

## Toggle Design Mode

**Cmd+Shift+D** (`⌘⇧D`) in Agents Glass — not Option/Alt+click.

Once active, click the target cell, code line, output, or error; the blue outline confirms selection.

## On every message with `browser_element`

1. Call **`resolve_pluto_context`** with the block (or parse `dom_path` yourself)
2. Call **`read_cell`** with resolved ids before answering or editing

## Regex from `dom_path`

```text
pluto-notebook#([0-9a-f-]+)
pluto-cell#([0-9a-f-]+)
```

## Ambiguous clicks

If `pluto-cell#` is missing (e.g. bare `main` click):

- Ask user to enable Design Mode (**Cmd+Shift+D**) and re-click inside a cell
- Or use `@pluto-context` if pasted

Drawings/annotations in Design Mode are screenshot-only — no structured `dom_path`.

## Glass URL resolution

Notebook URL form: `http://127.0.0.1:1234/edit?id=<notebook_id>`

`resolve_pluto_context` accepts Glass URL, `dom_path`, or `browser_element` block.

## Discovery priority

| Priority | Source |
|----------|--------|
| 1 | Design Mode click → `resolve_pluto_context` |
| 2 | Glass URL `/edit?id=<notebook_id>` |
| 3 | `@pluto-context` block |
| 4 | `list_notebooks` — only when no browser context |
