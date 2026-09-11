# Agent control — Pluto notebook interaction

Parent agents use these artifacts to **grade** whether Styx skills + PlutoMCP are working in practice — including when reviewing **subagents** — and to **feed failures back into skill/docs** improvements.

| File | Purpose |
|------|---------|
| [CHECKLIST.md](CHECKLIST.md) | Binary must-pass gate (MCP + Glass + skill routing) |
| [RUBRIC.md](RUBRIC.md) | Scored dimensions (0–2), parent↔subagent protocol, skill-improvement loop |
| [SCORECARD.template.md](SCORECARD.template.md) | Copy for one graded run (self-score + parent override + skill patches) |

**Intent:** If agents misuse tools or skills, the scorecard should name the failing criterion and the skill/doc file to patch — not only a numeric grade.

This is **behavioral** grading. It does **not** replace the deterministic CI reference runner (`run_reference.jl` / Reference runner workflow).
