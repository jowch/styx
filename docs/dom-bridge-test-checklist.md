# DOM Bridge — Manual Test Checklist

**Primary path (D13):** Glass Design Mode → `dom_path` in hook `prompt` → MCP **`resolve_pluto_context`** → **`read_cell`**.

**D15 lifecycle manual checks:** [d15-lifecycle-manual-checklist.md](./d15-lifecycle-manual-checklist.md)

---

## Prerequisites (D15)

- [ ] **pluto** MCP enabled in Cursor (stdio up; Pluto may be stopped)
- [ ] Agent has called `start_pluto_session` (or dev `pluto-serve.sh` for legacy serve path)
- [ ] Notebook in **Agents Glass** at `http://127.0.0.1:1234/<notebook_id>`
- [ ] MCP HTTP bridge at `:2346` on same session (`./scripts/d15-preflight.sh --expect-running`)
- [ ] Design Mode active in Glass (**Cmd+Shift+D**)

## After each Design Mode click on a cell target

1. Confirm hook `prompt` includes `dom_path` with `pluto-cell#<uuid>`
2. Agent calls MCP **`resolve_pluto_context`** with the `browser_element` block (or regexes IDs from `dom_path`)
3. Agent calls **`read_cell`** without manual UUID paste

### Design Mode test matrix (from spike H1)

| # | Target | Expected `pluto-cell#` in `dom_path`? | Notes |
|---|--------|--------------------------------------|-------|
| 1 | CodeMirror line (`pluto-input`) | ✅ | Per-line clicks same cell id |
| 2 | Plain text output | ✅ | |
| 3 | Markdown rendered HTML | ✅ | |
| 4 | `@bind` slider | ✅ | |
| 5 | Plot (`img` / SVG in output) | ✅ | Plots.jl often `<img>`, not iframe |
| 6 | Between-cells (add button) | ✅ | Attached to adjacent cell |
| 7 | Bare `main` / helpbox / header | ❌ | Re-click cell or `@pluto-context` |
| 8 | Drawing on screenshot | ❌ | Vision-only, no structured ID |

### ID extraction checks

Use MCP **`resolve_pluto_context`** or hook helper `parse_dom_path` semantics:

| Input | Expected |
|-------|----------|
| Contains `pluto-cell#<uuid>` | ✅ `cell_id` extracted |
| Contains `pluto-notebook#<uuid>` | ✅ `notebook_id` extracted |
| No `pluto-cell#` | ❌ reject / ask user to re-click |

---

## MCP end-to-end gate

- [ ] Design Mode click → agent chat resolves context without UUID paste
- [ ] Agent calls `read_cell` with `notebook_id` + `cell_id`
- [ ] Returns current cell code/output
- [ ] Stage-first `edit_cell` → `submit_changes` → browser sync

---

## Phase 4 validation log (2026-06-18)

| Check | Result |
|-------|--------|
| Bridge health `:2346` + Pluto `:1234` | ✅ |
| Reference eval `run_reference.jl --all` | ✅ 4/4 |
| Design Mode → hook → agent without UUID paste | ✅ |
| Stage-first `edit_cell` → `submit_changes` → browser sync | ✅ |
| Multi-expression → structured `error.kind` + boundaries | ✅ |
| SDK eval `eval:stage` | ✅ pass@1 (local `CURSOR_API_KEY`) |
| Styx Phase 4c (`resolve_pluto_context`, `pending_run` stop hook) | ✅ |
