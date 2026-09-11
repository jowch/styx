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

- Julia 1.11+ with a **combined** project at `PLUTOMCP_ROOT` that develops [PlutoMCP.jl](https://github.com/jowch/PlutoMCP.jl) and adds `JSON3`, `HTTP`, and `UUIDs` (PlutoMCP alone is not enough — the harness imports `JSON3`, which PlutoMCP does not depend on):

```bash
mkdir -p ~/.styx-eval-env
julia --project=$HOME/.styx-eval-env -e 'using Pkg; Pkg.develop(path="/path/to/PlutoMCP.jl"); Pkg.add(["JSON3","HTTP","UUIDs"])'
```

CI builds the same combined env in `.github/workflows/eval-reference.yml`.

## Reference runner (CI)

```bash
cd eval
PLUTOMCP_ROOT=$HOME/.styx-eval-env julia run_reference.jl --all --strict-trace
PLUTOMCP_ROOT=$HOME/.styx-eval-env julia run_reference.jl --scenario stage_and_run
```

Re-score an existing trace (dev): `julia score.jl --scenario <id> --log results/.../trace.jsonl`

## What gets measured

| Layer | Source | Gate |
|-------|--------|------|
| Outcome | `EvalShared.run_score` on live notebook state | Strict |
| Trace | Server-side `trace.jsonl` from `eval_log` | Advisory (`--strict-trace` gates CI) |

PlutoMCP provides the optional `EvalLog.jl` hook (`serve(eval_log=...)`). This repo owns scenarios, fixtures, runners, and scoring.

## Agent control (behavioral grading)

Deterministic CI above does **not** score how agents use skills/Glass. For parent→subagent review of Pluto MCP work, use:

- [`agent-control/CHECKLIST.md`](agent-control/CHECKLIST.md) — must-pass gate
- [`agent-control/RUBRIC.md`](agent-control/RUBRIC.md) — scored dimensions + parent protocol
- [`agent-control/SCORECARD.template.md`](agent-control/SCORECARD.template.md) — per-run scorecard

## Data handling

- `results/` and `*.jsonl` may contain notebook code — **do not commit**
- Use `eval_redact_code=true` / `PLUTOMCP_EVAL_REDACT_CODE=true` when sharing logs
