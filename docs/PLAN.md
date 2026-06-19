# Integrated Plan (status)

**Decisions:** [DECISIONS.md](./DECISIONS.md) · **Lifecycle spec:** [specs/pluto-lifecycle.md](./specs/pluto-lifecycle.md)

## Phase status (2026-06-18)

| Phase | Repo | Status |
|-------|------|--------|
| 0–1 | PlutoMCP.jl | ✅ MCP v2 core (projection, staging, receipts) |
| 2 | PlutoMCP.jl | ✅ Graph / validation tools |
| 3–4c | Styx | ✅ Design Mode Path A, plugin, hooks, `resolve_pluto_context` |
| 5 | both | ⚠️ Partial — `pending_run` hook + draft-buffer policy; no snapshot/restore |
| 5b (D15) | both | ✅ Lazy warm lifecycle — acceptance signed off 2026-06-18 |

## Validation gates

| Gate | Command |
|------|---------|
| Reference scenarios (CI) | `eval/run_reference.jl --all --strict-trace` |
| D15 deferred lifecycle | `scripts/validate-pluto-lifecycle.sh` |
| Manual Glass walkthrough | [d15-lifecycle-manual-checklist.md](./d15-lifecycle-manual-checklist.md) |

## Where details live

| Topic | Location |
|-------|----------|
| MCP tool semantics | [PlutoMCP.jl](https://github.com/jowch/PlutoMCP.jl) `AGENTS.md` |
| Agent bootstrap + edits | `skills/pluto-session`, `pluto-workflow`, `pluto-semantics` |
| Path B landing-click hang | [known-issues/path-b-edit-url-loading.md](./known-issues/path-b-edit-url-loading.md) |
