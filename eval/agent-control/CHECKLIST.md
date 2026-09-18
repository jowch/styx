# Pluto interaction checklist (must-pass)

Grade **Fail** overall if any item is **No** without an explicit, justified exception. Parents require subagents to answer each row with **evidence** (tool name + args, URL, `notebook_id` / `cell_id`, or quote).

Canonical MCP names (PlutoMCP): `pluto_session_status`, `start_pluto_session`, `open_notebook`, `read_cell`, `edit_cell` / `add_cell` (`run_after=false`, `folded` for markdown), `fold_cell`, `submit_changes` (`wait_for_completion`), `resolve_pluto_context`.

| # | Check | Pass looks like | Common fail |
|---|--------|-----------------|-------------|
| C1 | **Skill routing** | Notebook intent → `pluto-session` then `pluto-workflow` / `pluto-semantics`; `styx-setup` only when install/Julia/MCP is broken | Raw MCP / shell `serve` without skills |
| C2 | **Session ownership** | `pluto_session_status` → `start_pluto_session` if stopped; one window owns one Pluto (local XOR remote) | Second stack, fixed `:1234`/`:2346`, or local+SSH mix |
| C3 | **URL resolution** | Local Glass uses **exact** host from `pluto_url` (no `localhost`↔`127.0.0.1` rewrite); Remote SSH: remember last-good for session+port → same-port Glass probe → ask Ports **only if** probe fails; keep that host | Hardcodes `:1234`, invents remaps, asks Ports when remember/probe would work, remote `curl` as Glass proof, or mixes loopback hosts mid-session |
| C4 | **Tab reuse** | **Parent:** Reads `glass-views.json` (not sessionStart injection) then `browser_navigate({ url, viewId })`; omit `position` and `newTab`. **Task child:** empty `browser_tabs` + cached `viewId` → “Browser view not found” is expected; notebook work via inherited MCP | Child `newTab` / `position: "active"`; parent tab spam after empty list |
| C5 | **Path B open** | After `open_notebook`, `browser_click` notebook on landing — no pasted `/edit?id=` cold navigate | Pastes `/edit?id=` → hangs on Loading cells |
| C6 | **Identity before edit** | `notebook_id` / `cell_id` from Glass URL or Design Mode → `resolve_pluto_context` / `read_cell` before writes | `list_notebooks` fishing; edit without read |
| C7 | **MCP read receipt** | Fresh `read_cell` (or receipt) on the target cell before `edit_cell` / `add_cell`; respects MCP/hook rejection | Writes after stale/missing read; fights read-before-edit |
| C8 | **Stage → submit** | Stage with `run_after=false`; call `submit_changes` before end of turn when work should land; batch stages then one submit | Staged-only drift; “done” without submit; per-cell `run_after=true` spam |
| C9 | **Wait / stdio safety** | `submit_changes(wait_for_completion=false)` on stdio-bound sessions; never block MCP stdio for long runs | Blocking wait starves stdio / kills in-process Pluto ([#3](https://github.com/jowch/styx/issues/3)) |
| C10 | **Pending run honesty** | Tracks `pending_run` / dirty state from tools or hooks; does not claim clean when staged | Ignores pending_run; parent/child handoff leaves silent staged cells |
| C11 | **Safe preview honesty** | When outputs aren't live, exits Safe preview (**Run notebook code** in Glass or `allow_execution`) rather than stopping at staged edits; does not claim live outputs while still gated | Claims live outputs while still in safe preview; only reminds and leaves the gate on |
| C12 | **Notebook lease / sharing** | Does not reopen a path already owned; respects `notebook_in_use` / leases | Re-`open_notebook` mints new id / resets safe preview |
| C13 | **Cell grammar** | Structure-first cells per `pluto-semantics` (`imports_cell`, `begin`/`end`, `@bind` last) | Multi-statement soup / Jupyter mutation assumptions |
| C14 | **Presentation fold** | New prose / section `md` cells use `add_cell(..., folded=true)` (or `fold_cell`); verify `code_folded` via `read_cell` — no `submit_changes` for fold alone | Leaves markdown source visible; confuses “fold into compute” with Pluto `code_folded` |
| C15 | **Ground truth** | Re-reads via MCP after submit (`read_cell` / `read_notebook_code`); chat memory ≠ notebook state | “Already changed” without notebook evidence |

**Exception rule:** mark **N/A** only with a one-line reason (e.g. “Path A landing only — no edits”). N/A does not count as Fail.
