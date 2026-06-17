# Decision Record

Running log of architectural and workflow decisions. **Planning details:** [PLAN.md](./PLAN.md) and [specs/](./specs/).

| Repo | Role |
|------|------|
| **pluto-cursor-bridge** (this repo) | Cursor plugin, DOM click bridge, integration planning |
| **[PlutoMCP.jl](https://github.com/jowch/PlutoMCP.jl)** fork | MCP tool surface (may upstream) |

**Doc split (D1):** Planning docs live here unless purely MCP-server internals. Fork `AGENTS.md` holds canonical MCP agent semantics.

---

## D1 — Repo split

Planning and integration specs in this repo. Fork implements MCP; may upstream generic tools.

---

## D2 — Identity primitives

`notebook_id` + `cell_id` everywhere. Matches `<pluto-cell id="…">` and `<pluto-notebook id="…">` in Pluto frontend.

---

## D3 — MCP tool surface *(target)*

One canonical name per operation. Full catalog: [specs/mcp-phase-1.md](./specs/mcp-phase-1.md).

**Interim (today):** upstream names (`get_cell`, `set_cell_code`, `run_cell`); use `run_after=false` explicitly until Phase 1 ships.

---

## D4 — Stage-first workflow *(target)*

Edit with `run_after=false` → `submit_changes` once. Server tracks `pending_run` / `stale_cell_ids`.

---

## D5 — Click-to-context bridge *(target)*

`composedPath()` resolution; iframe interior rejected. Spec: [specs/dom-bridge.md](./specs/dom-bridge.md).

---

## D6 — Cursor plugin *(target)*

Full plugin; commands deliver click context (no native browser hook). Spec: [specs/cursor-plugin.md](./specs/cursor-plugin.md).

Phased: 4a manual cell_id → 4b click queue → 4c production inject.

---

## D12 — MCP lifecycle via `mcp.json`, not plugin commands

**Decision:** Plugin declares MCP in bundled `mcp.json`; **Cursor** spawns the entrypoint; **PlutoMCP** owns `serve()` / `connect()`; plugin rules/commands **do not** supervise Julia processes.

**Primary entry:** stdio launcher script → ensure bridge (`serve()`) → `connect()` proxy to shared session.

**Alternative:** HTTP URL to `:2346/sse` for users who run `serve()` manually.

**Why:** Matches Browse/Context7 plugin patterns; keeps click-bridge session aligned with MCP session. Details: [specs/plutomcp-architecture.md](./specs/plutomcp-architecture.md), [specs/cursor-plugin.md § MCP lifecycle](./specs/cursor-plugin.md#mcp-lifecycle-d12).

---

## D7 — Parallel tracks after Phase 1 gate

Layer 2 graph tools (fork) ∥ DOM bridge (here). Plugin Phase 4 after Phase 3.

**Phase 1 gate:** `read_notebook_code` → stage → `submit_changes` → verifiable output in Cursor against `serve()`.

---

## D8 — Hard rename, no aliases

Remove old tool names from MCP schema when Phase 1 ships. No parallel `get_cell`/`read_cell` registrations. Upstream PRs are clean breaks.

---

## D9 — Draft-buffer policy

MCP tracks server-side dirty only. Agent reads before edit. Server wins on conflict. Document in plugin rule; no OT in Phase 1. Details: [specs/mcp-phase-1.md §1E](./specs/mcp-phase-1.md).

---

## D10 — Rich output deferred

MCP returns text placeholders for images/HTML in Phase 1. Click bridge provides `cell_id`; explain/refactor on plots is advisory until plugin screenshots (Phase 4c+).

---

## D11 — Intent via commands

`pluto-select-cell` / `pluto-edit-cell` / `pluto-explain-cell` set intent — not modifier keys.

---

## Resolved questions (formerly open)

| Was | Resolution |
|-----|------------|
| O1 `submit_changes` API | Dirty set → `update_save_run!` on subset + deps; see [mcp-phase-1 §1B](./specs/mcp-phase-1.md) |
| O2 Draft buffer | D9 |
| O3 Context delivery | Commands (MVP); see [cursor-plugin](./specs/cursor-plugin.md) |
| O4 Upstream rename | D8 hard break |
| O5 Rich output | D10 |
| O6 Intent UX | D11 |

---

## Status snapshot (2026-06-17)

| Component | State |
|-----------|-------|
| Planning docs | ✅ [PLAN.md](./PLAN.md) + specs |
| PlutoMCP fork — Phase 1 | 📋 Spec ready; not implemented |
| DOM bridge | 📋 Spec ready |
| Cursor plugin | 📋 Spec ready |
