# Pluto MCP Agent Eval

Deterministic reference runner for Pluto MCP golden-path scenarios. CI gate — no agent, no API key.

## Layout

```
eval/
  fixtures/           # notebooks with stable cell UUIDs
  scenarios/          # task specs + rubrics
  lib/EvalShared.jl   # HTTP client, outcome + trace scoring
  run_reference.jl    # golden-path runner (CI gate)
  score.jl            # re-score an existing trace
  results/            # gitignored run artifacts
```

## Prerequisites

- Julia with [PlutoMCP.jl](https://github.com/jowch/PlutoMCP.jl) at `PLUTOMCP_ROOT` (default: sibling `../../PlutoMCP.jl`)

## Reference runner (CI)

```bash
cd eval
julia run_reference.jl --all --strict-trace
julia run_reference.jl --scenario stage_and_run
```

Re-score an existing trace (dev): `julia score.jl --scenario <id> --log results/.../trace.jsonl`

## What gets measured

| Layer | Source | Gate |
|-------|--------|------|
| Outcome | `EvalShared.run_score` on live notebook state | Strict |
| Trace | Server-side `trace.jsonl` from `eval_log` | Advisory (`--strict-trace` gates CI) |

PlutoMCP provides the optional `EvalLog.jl` hook (`serve(eval_log=...)`). This repo owns scenarios, fixtures, runners, and scoring.

## Data handling

- `results/` and `*.jsonl` may contain notebook code — **do not commit**
- Use `eval_redact_code=true` / `PLUTOMCP_EVAL_REDACT_CODE=true` when sharing logs
