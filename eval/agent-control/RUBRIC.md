# Pluto agent performance rubric

Use after [CHECKLIST.md](CHECKLIST.md). Checklist Fail → overall **Fail** (do not average away).

## Scoring scale (per dimension)

| Score | Meaning |
|------:|---------|
| **0** | Missing or actively harmful |
| **1** | Partial / recovered after mistakes |
| **2** | Correct on first pass with clear evidence |

## Dimensions

| ID | Dimension | 0 | 1 | 2 |
|----|-----------|---|---|---|
| D1 | **Skill selection** | Ignores Styx skills | Finds skill late or mixes conflicting guidance | Loads the right skill(s) before acting |
| D2 | **MCP sequencing** | Random / write-first tool spam | Right tools, wrong order, then recovers | Status → open/read → stage (`run_after=false`) → `submit_changes` → verify |
| D3 | **MCP arg hygiene** | Wrong/missing ids; blocking wait; skips read guard | One bad arg, then corrects | Correct `notebook_id`/`cell_id`; non-blocking wait; honors read-before-edit |
| D4 | **Glass hygiene** | Hardcoded ports + tab spam | Eventual correct URL; extra tabs or retries | Host `pluto_url` (+ optional `client_url`); tab reuse; no `newTab`; no invented remaps |
| D5 | **Edit discipline** | Blind edits / no submit | Read or submit missing once | Fresh read → stage → submit → re-read |
| D6 | **Session safety** | Blocks stdio wait / kills Pluto / duplicate sessions | Risky wait or reopen, then corrects | Non-blocking wait; preserves session + notebook id |
| D7 | **Recovery & honesty** | Hides failures / invents state | Reports error but weak fix | Accurate status; user-visible next step; pending_run called out |

**Total:** sum D1–D7 (max **14**).

| Total | Grade |
|------:|-------|
| 13–14 | Excellent |
| 10–12 | Acceptable |
| 6–9 | Weak — revise skills or agent instructions |
| 0–5 | Fail — stop and remediate before more notebook work |

## Parent ↔ subagent protocol

When a parent dispatches Pluto notebook work to a subagent:

1. **Attach** this rubric + checklist (or link `eval/agent-control/`).
2. Require the subagent’s final message to include a filled [SCORECARD.template.md](SCORECARD.template.md):
   - Checklist C1–C14 with **Yes / No / N/A** + evidence
   - Self-scores D1–D7 with one evidence line each
   - **Skill gaps** table (what failed → which file to patch)
3. **Parent re-grades** from the tool trace (do not trust self-score alone). Prefer evidence:
   - `pluto_session_status` / `pluto_url` / optional `client_url`
   - Glass tab actions / view ids
   - `read_cell` → `edit_cell`/`add_cell` → `submit_changes` arg values (`run_after`, `wait_for_completion`, ids)
   - `pending_run` / Safe preview exit (Glass **Run notebook code** or `allow_execution`)
4. If parent grade < 10 or any checklist **No**, run the **skill-improvement loop** below before more notebook work.
5. File durable product gaps as Styx issues (PlutoMCP fork issues disabled) — e.g. tab-list reliability is upstream Cursor; stdio wait death is [#3](https://github.com/jowch/styx/issues/3).

## Skill-improvement feedback loop

Failures are **inputs to skill/docs edits**, not only a grade. Map checklist/rubric fails → files:

| Symptom / fail | First place to patch |
|----------------|----------------------|
| Wrong bootstrap / Path A vs B / reopen | `skills/pluto-session/SKILL.md`, `path-a-landing.md`, `path-b-open.md` |
| `:1234`, invented Ports remap, `newTab` spam | `skills/pluto-session/reference/glass-navigation.md`, `remote-ssh.md`, `AGENTS.md`, `rules/pluto-notebook-workflow.mdc` |
| Edit without read / no submit / `run_after=true` spam | `skills/pluto-workflow/SKILL.md`, `reference/edit-loop.md` |
| Blocking `wait_for_completion` / session death | `skills/pluto-workflow/SKILL.md` (+ product work on [#3](https://github.com/jowch/styx/issues/3)) |
| Cell structure / `@bind` / parse errors | `skills/pluto-semantics/` (`cell-structure.md`, `agent-examples.md`) |
| Install / Julia / MCP missing | `skills/styx-setup/` |
| Tool semantics disagree with skills | PlutoMCP fork `AGENTS.md` / tools — then update Styx skills to match |

**Loop:** grade → name failing C#/D# → patch the mapped file in the same PR or a follow-up → re-run a short notebook task → re-score. Stop when parent grade ≥ 10 and checklist is clean (or remaining Nos are filed issues).

## What this is not

- Not a substitute for `eval/run_reference.jl` golden-path CI.
- Not a claim that Cursor Glass tab APIs are complete — grade agents on **fallback behavior** when lists are empty.
