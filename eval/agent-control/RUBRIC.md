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
| D2 | **MCP sequencing** | Random / write-first tool spam | Right tools, wrong order, then recovers | Status → open/read → stage → `submit_changes` → verify |
| D3 | **Glass hygiene** | Hardcoded ports + tab spam | Eventual correct URL; extra tabs or retries | Host vs Ports correct; tab reuse; no `newTab` |
| D4 | **Edit discipline** | Blind edits / no submit | Read or submit missing once | `read_cell` before edit + `submit_changes` + verify |
| D5 | **Session safety** | Blocks stdio wait / kills Pluto / duplicate sessions | Risky wait or reopen, then corrects | Non-blocking wait; preserves session + notebook id |
| D6 | **Recovery & honesty** | Hides failures / invents state | Reports error but weak fix | Accurate status; user-visible next step |

**Total:** sum D1–D6 (max **12**).

| Total | Grade |
|------:|-------|
| 11–12 | Excellent |
| 8–10 | Acceptable |
| 5–7 | Weak — revise skills or agent instructions |
| 0–4 | Fail — stop and remediate before more notebook work |

## Parent ↔ subagent protocol

When a parent dispatches Pluto notebook work to a subagent:

1. **Attach** this rubric + checklist (or link `eval/agent-control/`).
2. Require the subagent’s final message to include a filled [SCORECARD.template.md](SCORECARD.template.md):
   - Checklist C1–C12 with **Yes / No / N/A** + evidence
   - Self-scores D1–D6 with one evidence line each
3. **Parent re-grades** from the tool trace (do not trust self-score alone). Prefer evidence: `pluto_session_status`, `pluto_url` / Ports URL used, tab actions, `read_cell` / `edit_cell` / `submit_changes` args (`wait_for_completion` / `run_after`), Glass view ids.
4. If parent grade < 8 or any checklist **No**, either:
   - patch skills/rules that misled the agent, or
   - re-run with explicit constraints (no `newTab`; non-blocking submit; reuse Glass).
5. File durable gaps as Styx issues (PlutoMCP fork issues are disabled) — e.g. tab-list reliability is upstream Cursor; stdio wait death is [#3](https://github.com/jowch/styx/issues/3).

## What this is not

- Not a substitute for `eval/run_reference.jl` golden-path CI.
- Not a claim that Cursor Glass tab APIs are complete — grade agents on **fallback behavior** when lists are empty.
