# Pluto MCP SDK Agent Eval

Runs Cursor SDK agents against live `PlutoMCP.serve()` sessions and scores outcome + trace.

## Prerequisites

- Julia with [PlutoMCP.jl](https://github.com/jowch/PlutoMCP.jl) at `PLUTOMCP_ROOT` (default: sibling `../PlutoMCP.jl`)
- Node.js 20+
- `CURSOR_API_KEY` from [Cursor Dashboard → Integrations](https://cursor.com/dashboard/integrations)

## Setup

```bash
cd eval
npm install
```

## Run

```bash
export CURSOR_API_KEY="cursor_..."
export PLUTOMCP_ROOT="/path/to/PlutoMCP.jl"   # optional

# Phase 1 gate scenario
npm run eval:stage

# Single scenario
npm run eval -- --scenario batch_edit

# All scenarios (outcome strict per run)
npm run eval -- --all
```

## What gets measured

| Layer | Source | Gate |
|-------|--------|------|
| Outcome | `score.jl` on notebook server state | Strict |
| Trace | Server-side `trace.jsonl` from `eval_log` | Advisory (warnings only) |

SDK runs use `settingSources: []` + [`PLUTO_WORKFLOW_PREFIX.md`](../PlutoMCP.jl/eval/PLUTO_WORKFLOW_PREFIX.md) — not plugin rules. See PlutoMCP [`eval/README.md`](../PlutoMCP.jl/eval/README.md) for the full harness.

## Non-determinism policy

- Phase 1 gate: **pass@1** on `stage_and_run` outcome
- Optional calibration: run `--scenario stage_and_run` multiple times manually
- CI gates on the deterministic reference runner in PlutoMCP (`run_reference.jl --all`), not SDK runs

## Data handling

- `results/` and `*.jsonl` may contain notebook code — **do not commit**
- Logs are written under `eval/results/<run_id>/`

## mcp.json

Reference-only for IDE/manual MCP setup. **`run.ts` uses inline MCP** (`mcpServers.pluto.url`) because `settingSources: []` does not load project config.
