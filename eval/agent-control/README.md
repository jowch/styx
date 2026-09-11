# Agent control — Pluto notebook interaction

Parent agents use these artifacts to grade whether **skills + PlutoMCP** are being used correctly (including when reviewing subagents).

| File | Purpose |
|------|---------|
| [CHECKLIST.md](CHECKLIST.md) | Binary must-pass gate before scoring |
| [RUBRIC.md](RUBRIC.md) | Scored dimensions (0–2) + parent/subagent protocol |
| [SCORECARD.template.md](SCORECARD.template.md) | Copy for a single graded run |

This is **behavioral** grading (skill adherence / MCP hygiene). It does **not** replace the deterministic CI reference runner in `eval/` (`run_reference.jl`).
