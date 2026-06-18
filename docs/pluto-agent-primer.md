# Pluto agent primer

Training guide for AI agents editing live Pluto.jl notebooks via PlutoMCP. Read this before your first edit session.

| Also see | Purpose |
|----------|---------|
| [pluto-semantics.md](./pluto-semantics.md) | Cell grammar deep-dive |
| [rules/pluto-notebook-workflow.mdc](../rules/pluto-notebook-workflow.mdc) | Always-on Cursor rule |
| PlutoMCP.jl `AGENTS.md` | MCP tool API conventions |

---

## 1. Mental model

Pluto is **not** a `.jl` file you patch. It is a **live reactive session**:

- Each **cell** is one node in a dependency graph.
- Cells share one notebook module scope.
- Pluto owns persistence, execution order, and browser sync.
- MCP writes **server state**; the browser editor has a separate draft buffer (last-write-wins).

Your job: use MCP tools to read, stage, and run cells — never edit the notebook file on disk directly.

---

## 2. Find the notebook (browser first)

**Do not start with `list_notebooks`** unless you truly have no context. Resolve `notebook_id` from what the user is already looking at:

### Priority order

1. **Design Mode click** — **Cmd+Shift+D** in Glass to toggle Design Mode, then click an element. Extract ids from `browser_element` / `dom_path`:
   ```text
   dom_path: … > pluto-notebook#<notebook_id> > pluto-cell#<cell_id> > …
   ```
   **Not** Option/Alt+click — toggle Design Mode with **Cmd+Shift+D** (`⌘⇧D`), then click.
   Regex: `pluto-notebook#([0-9a-f-]+)` and `pluto-cell#([0-9a-f-]+)`.

2. **Glass browser URL** — Pluto notebook URLs embed the id:
   ```text
   http://127.0.0.1:1234/<notebook_id>
   ```
   Check the active Glass tab before calling MCP.

3. **`@pluto-context` block** — user or command pasted structured ids.

4. **Error/output click** — clicking `jlerror` or cell output still includes `pluto-cell#` in `dom_path`; `visible_text` may contain the human-friendly Pluto error UI.

5. **`list_notebooks`** — fallback when no browser context exists (headless session, user hasn't opened a tab, ambiguous workspace).

### After resolving ids

- Call **`read_cell`** (single cell) or **`read_notebook_code`** (full notebook) before any edit.
- If `pluto-cell#` is missing from a click, ask the user to re-click inside a cell body or output.

---

## 3. Edit workflow (stage-first)

```text
resolve notebook_id (browser → context → list_notebooks)
    → read_cell / read_notebook_code
    → edit_cell / edit_cells / add_cell  (run_after=false)
    → submit_changes
    → read_cell (verify output + error fields)
```

| Step | Tool | Notes |
|------|------|-------|
| Discover | Browser URL / Design Mode | Prefer over `list_notebooks` |
| Read | `read_cell`, `read_notebook_code` | Required before writes |
| Stage | `edit_cell`, `edit_cells`, `add_cell` | Default `run_after=false` |
| Validate | `validate_cell` | Optional; catches `multi_expression` |
| Run | `submit_changes` | Pluto Cmd+S — batch run staged cells |
| Verify | `read_cell` | Check `output`, `error`, `errored` |

Do **not** spam `execute_cell` or `run_all_cells`. Stage multiple edits, then one `submit_changes`.

---

## 4. Cell grammar (one expression per cell)

Each code cell = **exactly one Julia expression**.

**Invalid:**
```julia
using Plots
plot(sin, 0, 2pi)
```

**Valid — split cells (preferred):**
```julia
# cell 1
using Plots
```
```julia
# cell 2
plot(sin, 0, 2pi)
```

**Valid — wrap in one cell:**
```julia
begin
    using Plots
    plot(sin, 0, 2pi)
end
```

See [pluto-semantics.md](./pluto-semantics.md) for `let/end`, `@bind`, and reactivity details.

---

## 5. Reading errors

Pluto surfaces errors differently in the browser vs MCP. Use **both**.

### MCP `read_cell` (after run)

Errored cells return:

```json
{
  "errored": true,
  "output": "Multiple expressions in one cell. Split this cell into 2 cells, or wrap all code in a begin ... end block.",
  "error": {
    "kind": "pluto_multi_expression",
    "msg": "syntax: extra token after end of expression",
    "boundaries": [13, 30],
    "split_count": 2,
    "fixes": ["split_cells", "wrap_begin_end"],
    "hint": "Multiple expressions in one cell. Split this cell into 2 cells, or wrap all code in a begin ... end block."
  }
}
```

| Field | Use |
|-------|-----|
| `output` | Human-readable summary (matches browser intent) |
| `error.kind` | Machine classification |
| `error.boundaries` | Byte positions to split cell |
| `error.fixes` | `split_cells` or `wrap_begin_end` |
| `error.hint` | What to tell the user / how to fix |

### Design Mode click on `jlerror`

The `visible_text` in `browser_element` shows Pluto's rendered UI ("Split this cell into 2 cells, or Wrap all code in a begin ... end block."). Use when the user points at an error.

### Raw runner message (legacy)

Older payloads only had `:msg` with `Boundaries: [...]`. If you see `syntax: extra token after end of expression`, treat as **multi-expression** — split or wrap.

---

## 6. Reactivity essentials

- Assignment in cell A (`x = 1`) defines a global used by downstream cells.
- Editing A re-runs A and all transitive dependents.
- **`read_notebook_code`** defaults to **execution (dependency) order**, not visual layout.
- **`get_cell_order`** = visual; **`get_execution_order`** = run order.
- Use graph tools (`get_cell_dependencies`, `validate_cell`, `find_symbol_definitions`) for debugging.

---

## 7. Tool cheat sheet

| Read | Write | Graph / debug |
|------|-------|---------------|
| `read_cell` | `edit_cell` | `get_cell_dependencies` |
| `read_notebook_code` | `edit_cells` | `get_cell_dependents` |
| `list_notebooks` | `add_cell` | `find_symbol_definitions` |
| | `delete_cell` | `find_symbol_references` |
| | `move_cell` | `validate_cell` |
| | `submit_changes` | `search_code` |
| | `execute_cell` | |

Canonical names only — no `get_cell`, `set_cell_code`, `run_cell`.

---

## 8. Common mistakes

| Mistake | Symptom | Fix |
|---------|---------|-----|
| `list_notebooks` first | Wrong/missing context | Browser URL / Design Mode click |
| Multi-statement cell | `pluto_multi_expression` | Split cells or `begin`/`let` |
| Edit without read | `read_required` | `read_cell` first |
| Run after every edit | Slow, fights staging | `submit_changes` once |
| Patch `.jl` on disk | Desync | MCP only |
| Ignore `error` field | Misdiagnose failures | Read `error.kind` + `hint` |
| Same-cell browser edit | Overwrite user draft | Re-read before write |

---

## 9. End-to-end example

User enables Design Mode (**Cmd+Shift+D**), clicks empty cell, asks: "plot sin(x)".

1. Parse `notebook_id` + `cell_id` from `dom_path`.
2. `read_cell` — confirm empty.
3. `edit_cell` cell 1 → `using Plots` (or `add_cell` if cell already has other code).
4. `add_cell` after → `plot(sin, 0, 2pi)`.
5. `submit_changes`.
6. `read_cell` on plot cell — expect SVG/plain output, `errored: false`.

If step 3 used a multi-line script in one cell, step 6 returns `error.kind == "pluto_multi_expression"` — split and retry.
