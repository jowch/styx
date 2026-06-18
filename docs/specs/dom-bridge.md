# DOM Bridge Spec — Phase 3 (complete)

> **Click delivery (D13):** **Design Mode** — Glass `dom_path` in hook `prompt` → MCP **`resolve_pluto_context`** → **`read_cell`**. See [DECISIONS.md § D13](../DECISIONS.md), [spike-results.md](../spikes/spike-results.md).

## Goal

Structured `notebook_id` + `cell_id` context when the user selects a Pluto cell — without manual UUID copy-paste.

## Delivery paths

| Path | Role | When |
|------|------|------|
| **A — Design Mode** (primary) | Parse `pluto-cell#` / `pluto-notebook#` from Glass Design Mode `dom_path` in hook `prompt`; agent calls MCP | Production plugin |
| **B — Manual `@pluto-context`** | User or command pastes IDs | Fallback when Design Mode is ambiguous |

Phase 3 originally shipped a dev inject+queue harness (Path C). **Removed** — superseded by Design Mode + MCP `resolve_pluto_context`.

## Runtime components

| Artifact | Role |
|----------|------|
| `hooks/check-design-mode.py` | MCP health gate when prompt contains Pluto context |
| `hooks/pluto_lib.py` | `parse_dom_path` / `parse_prompt_text` for hook helpers |
| `rules/pluto-notebook-workflow.mdc` | Agent instructions: Design Mode → **`resolve_pluto_context`** |
| PlutoMCP `resolve_pluto_context` | Canonical server-side parser (URL, dom_path, browser block) |
| `docs/dom-bridge-test-checklist.md` | Manual validation |

---

## Path A — Design Mode (primary)

Validated in spike H1. User toggles Design Mode (**Cmd+Shift+D**) in **Agents Glass**, clicks a cell. Hook stdin includes `browser_element` / `dom_path`:

```text
… > pluto-notebook#836a54be-… > pluto-cell#98b9ea94-… > pluto-output… > bond > input
```

Agent resolves IDs via MCP:

```text
resolve_pluto_context(context=<browser_element block>)
→ read_cell(notebook_id, cell_id)
```

### Path A acceptance

| Target | `pluto-cell#` in `dom_path`? |
|--------|------------------------------|
| CodeMirror line (`pluto-input`) | ✅ |
| Plain text output | ✅ |
| Markdown rendered HTML | ✅ |
| `@bind` slider | ✅ |
| Plot (`img` / SVG in output) | ✅ |
| Between-cells chrome (add button) | ✅ (attached cell) |
| Bare `main` / helpbox / header | ❌ — re-click cell or use `@pluto-context` |
| Drawing annotation on screenshot | ❌ — vision-only, no structured ID |

### Path A fallback rules

| Condition | Action |
|-----------|--------|
| No `pluto-cell#` in `dom_path` | Reject; user re-clicks a cell or uses `@pluto-context` |
| `notebook_id` missing from path | URL `?id=` or MCP `list_notebooks` |
| MCP `read_cell` fails | Wrong session — notebook must be from `PlutoMCP.serve()` |
| Ambiguous gap (notebook id only) | Advisory; agent uses `read_notebook_code` |

---

## DOM facts (Pluto frontend)

- `<pluto-cell id="{cell_id}">` from Julia UUID
- `<pluto-notebook id="{notebook_id}">` container
- Markdown, `@bind` (`<bond def="...">`), plots under `pluto-output`
- Do not use `bond[def]` or variable span IDs as `cell_id`
- Do not use `cursor-ide-browser` MCP for Pluto (D13) — use Agents Glass

## Constraints

- Target live hydrated DOM in Agents Glass / user's Pluto tab — not static export HTML
- MCP session must be Pluto instance from `PlutoMCP.serve()` — document clearly

## Gates

**Phase 3:** Design Mode `dom_path` → MCP `read_cell` succeeds (see checklist).

**Phase 4:** Install plugin → Design Mode click → agent chat has context → edit via MCP without UUID paste. See [cursor-plugin.md](./cursor-plugin.md).
