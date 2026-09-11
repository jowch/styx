# Pluto interaction checklist (must-pass)

Grade **Fail** overall if any item is **No** without an explicit, justified exception. Parents should require subagents to answer each row with evidence (tool name, URL, cell id, or quote).

| # | Check | Pass looks like | Common fail |
|---|--------|-----------------|-------------|
| C1 | **Skill routing** | Notebook intent → `pluto-session` then `pluto-workflow` / `pluto-semantics` as needed; `styx-setup` only when install/Julia/MCP is broken | Jumps straight to raw MCP / shell `serve` |
| C2 | **Session ownership** | `pluto_session_status` → `start_pluto_session` if stopped; one window owns one Pluto (local XOR remote) | Starts a second stack, probes fixed `:1234`/`:2346`, or mixes local+SSH Pluto |
| C3 | **URL resolution** | Glass uses `pluto_url` from status; on Remote SSH remap failure uses **Ports** client URL | Hardcodes `:1234` or invents ports |
| C4 | **Tab reuse** | Reuses Agents Glass / `position: "active"`; no `newTab`/`new` by default | Spams Glass tabs after empty tab list or failed navigate |
| C5 | **Path B open** | After `open_notebook`, `browser_click` notebook on landing — no pasted `/edit?id=` cold navigate | Pastes `/edit?id=` and hangs on Loading cells |
| C6 | **Identity before edit** | `notebook_id` / `cell_id` from Glass URL or Design Mode → `resolve_pluto_context` / `read_cell` before writes | `list_notebooks` fishing or edit without read |
| C7 | **Stage → submit** | Edits with `run_after=false` then `submit_changes` before end of turn when work should land | Leaves staged-only drift; chat claims "done" |
| C8 | **Wait policy** | Prefer non-blocking submit (`wait_for_completion=false` when the tool exposes it) on stdio-bound sessions; never block MCP stdio for long runs | Blocking wait starves stdio / kills in-process Pluto ([issue #3](https://github.com/jowch/styx/issues/3)) |
| C9 | **Safe preview honesty** | Reminds user outputs/widgets need **Run notebook code** in Glass when execution is not allowed | Claims live outputs while still in safe preview |
| C10 | **Notebook lease / sharing** | Does not reopen a path already owned; respects `notebook_in_use` / leases | Re-`open_notebook` mints a new id and resets safe preview |
| C11 | **Cell grammar** | Structure-first cells per `pluto-semantics` (`imports_cell`, `begin`/`end`, `@bind` last) | Multi-statement soup / Jupyter-style mutation assumptions |
| C12 | **Ground truth** | Re-reads notebook via MCP after submit; does not treat chat memory as notebook state | "I already changed that" without `read_cell` / notebook code |

**Exception rule:** mark **N/A** only with a one-line reason (e.g. "Path A landing only — no edits"). N/A does not count as Fail.
