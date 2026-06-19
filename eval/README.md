# Pluto MCP Agent Eval

Evaluation harness for Pluto MCP agent workflows: deterministic reference runner (CI), Cursor SDK orchestration (manual), and shared scoring.

## Layout

```
eval/
  SDK_WORKFLOW_PREFIX.md     # minimal MCP workflow for SDK runs (no plugin rules)
  PLUTO_WORKFLOW_PREFIX.md   # plugin session-start prefix (Design Mode / Styx)
  SKILL_BASELINE_SCENARIOS.md  # TDD pressure scenarios for pluto-* skills
  fixtures/                  # notebooks with stable cell UUIDs
  scenarios/                 # task specs + rubrics
  lib/EvalShared.jl          # HTTP client, outcome + trace scoring
  run_reference.jl           # golden-path runner (no agent, CI gate)
  score.jl                   # re-score an existing trace
  run.ts                     # Cursor SDK orchestrator
  results/                   # gitignored run artifacts
```

## Prerequisites

- Julia with [PlutoMCP.jl](https://github.com/jowch/PlutoMCP.jl) at `PLUTOMCP_ROOT` (default: sibling `../../PlutoMCP.jl`)
- Node.js 20+ (SDK eval only)
- `CURSOR_API_KEY` for SDK runs ([Cursor Dashboard → Integrations](https://cursor.com/dashboard/integrations))

## Reference runner (CI)

Deterministic golden-path tool sequences via HTTP `/call` — no agent, no API key:

```bash
cd eval
julia run_reference.jl --all --strict-trace
julia run_reference.jl --scenario stage_and_run
```

Or via npm:

```bash
npm run eval:reference
```

## SDK agent eval (manual)

```bash
cd eval
npm install
cp .env.example .env          # set CURSOR_API_KEY
npm run eval:stage              # Phase 1 gate scenario
npm run eval -- --scenario batch_edit
npm run eval -- --all
```

SDK runs use `settingSources: []` + `SDK_WORKFLOW_PREFIX.md` — not plugin rules.

## What gets measured

| Layer | Source | Gate |
|-------|--------|------|
| Outcome | `EvalShared.run_score` on live notebook state | Strict |
| Trace | Server-side `trace.jsonl` from `eval_log` | Advisory (`--strict-trace` to gate CI) |

PlutoMCP provides the optional `EvalLog.jl` hook (`serve(eval_log=...)`). This repo owns scenarios, fixtures, runners, and scoring.

## Phase 1 gate

| Tier | Criterion |
|------|-----------|
| CI | `run_reference.jl --all --strict-trace` |
| Manual | SDK `stage_and_run` outcome pass@1 |
| Skills | [SKILL_BASELINE_SCENARIOS.md](./SKILL_BASELINE_SCENARIOS.md) — five pressure scenarios after skill changes |

## Data handling

- `results/` and `*.jsonl` may contain notebook code — **do not commit**
- Use `eval_redact_code=true` / `PLUTOMCP_EVAL_REDACT_CODE=true` when sharing logs

## mcp.json

Reference-only for IDE/manual MCP setup. **`run.ts` uses inline MCP** because `settingSources: []` does not load project config.
