# Skill baseline scenarios (TDD for agent training)

Pressure scenarios for validating **pluto-session**, **pluto-workflow**, and **pluto-semantics**. Per Superpowers `writing-skills`: run **RED** (agent without skills or with old docs) before changing skills, then **GREEN** (with skills loaded).

## How to run

| Mode | Setup | Pass criterion |
|------|-------|----------------|
| **Manual** | Fresh chat; invoke skill by name or user command | Agent behavior matches **Expected** column |
| **SDK eval** | `PLUTO_WORKFLOW_PREFIX.md` + scenario prompt + fixture when noted | Outcome + trace claims pass |
| **Regression** | After skill edit, re-run all five | No new rationalizations |

Record baseline rationalizations verbatim in `eval/results/skill-baseline-<date>.md` (gitignored).

---

## Scenario 1 — Path A bootstrap

**User prompt:** `I want to work on my Pluto notebooks`

| | |
|--|--|
| **Skills** | **pluto-session** (required) |
| **Expected** | `pluto_session_status` → `start_pluto_session` if stopped; open `http://127.0.0.1:1234/` in Glass; tell user to pick notebook; **stop** |
| **Must NOT** | `open_notebook`, `list_notebooks`, ask "which notebook?" in chat, `pluto-serve.sh` |
| **Common rationalizations** | "I need notebook_id first" → Path A defers id to next prompt |

---

## Scenario 2 — Path B + safe preview

**User prompt:** `Open eval/fixtures/reactive_xy.jl in Pluto`

| | |
|--|--|
| **Skills** | **pluto-session** → **pluto-workflow** on edits |
| **Expected** | `start_pluto_session` if needed; landing `http://127.0.0.1:1234/` **first**; `open_notebook(path=…)`; open `http://127.0.0.1:1234/edit?id=<id>`; safe-preview reminder |
| **Must NOT** | Bare `/<notebook_id>` URL; skip landing; `run_all_cells` at open |
| **Common rationalizations** | "I'll open notebook URL directly" → cookies fail; "I'll run cells to verify" → safe preview blocks |

---

## Scenario 3 — Ambiguous Design Mode click

**Context:** `browser_element` with `dom_path` ending at `main` (no `pluto-cell#`)

**User prompt:** `What does this cell do?`

| | |
|--|--|
| **Skills** | **pluto-workflow** |
| **Expected** | Ask user to enable Design Mode (**⌘⇧D**) and re-click inside a cell; **not** `list_notebooks` first |
| **Must NOT** | Guess cell from `list_notebooks`; use `cursor-ide-browser` |
| **Common rationalizations** | "list_notebooks is faster" → browser-first rule |

---

## Scenario 4 — Multi-expression fix

**Context:** Cell with `using Plots` + `plot(...)` on separate lines; `error.kind = pluto_multi_expression`

**User prompt:** `Fix this cell`

| | |
|--|--|
| **Skills** | **pluto-workflow** → **pluto-semantics** |
| **Expected** | `read_cell` → `edit_cell` with `begin`/`end` wrap in **same cell** → `submit_changes` |
| **Must NOT** | Split into two cells by default; patch `.jl` on disk |
| **Common rationalizations** | "Splitting is cleaner" → default is wrap unless reactive steps intended |

**SDK eval:** extend `stage_and_run` fixture with a multi-expr cell or add dedicated fixture later.

---

## Scenario 5 — Safe preview run request

**Context:** Notebook opened via Path B default (`open_notebook` without `run_notebook=true`)

**User prompt:** `Run the notebook so I can see the plot`

| | |
|--|--|
| **Skills** | **pluto-workflow** |
| **Expected** | Direct user to **Run notebook code** in Glass (top right); explain MCP cannot exit safe preview |
| **Must NOT** | `run_all_cells`, `execute_cell` as substitute; refuse to edit code |
| **Common rationalizations** | "submit_changes will run it" → false in safe preview |

---

## Trace checklist (when MCP available)

| Scenario | `must_include_subsequence` | `must_not_include` |
|----------|---------------------------|-------------------|
| 1 Path A | `pluto_session_status`, `start_pluto_session` | `open_notebook`, `list_notebooks` |
| 2 Path B | `start_pluto_session`, `open_notebook` | `run_all_cells` |
| 4 Multi-expr | `read_cell`, `edit_cell`, `submit_changes` | (split via second `add_cell` without wrap) |
| 5 Run request | — | `run_all_cells`, `execute_cell` |

---

## Refactor gate

Before merging skill changes:

1. Run all five scenarios with skills loaded → **GREEN**
2. Spot-check one scenario without skill (optional RED) after major rewrites
3. Update skill `reference/` files if a new rationalization appears

See [docs/skill-architecture.md](../docs/skill-architecture.md) for surface map.
