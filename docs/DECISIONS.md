# Decision Record

Running log of architectural and workflow decisions. **Planning details:** [PLAN.md](./PLAN.md) and [specs/](./specs/).

| Repo | Role |
|------|------|
| **Styx** (this repo) | Cursor plugin bridging Pluto.jl ↔ Cursor; DOM resolver; integration planning |
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

**Shipped (Phase 1):** canonical names (`read_cell`, `edit_cell`, `submit_changes`, …). No parallel legacy aliases.

---

## D4 — Stage-first workflow *(target)*

Edit with `run_after=false` → `submit_changes` once. Server tracks `pending_run` / `stale_cell_ids`.

---

## D5 — Click-to-context bridge *(target)*

**Primary (D13):** Glass Design Mode → MCP **`resolve_pluto_context`** / **`read_cell`** from `dom_path` in hook `prompt`. Spec: [specs/dom-bridge.md](./specs/dom-bridge.md).

---

## D6 — Cursor plugin *(target)*

Full plugin; commands deliver click context (no native browser hook). Spec: [specs/cursor-plugin.md](./specs/cursor-plugin.md).

Phased: 4a manual cell_id → 4b Design Mode (Path A) → 4c polish (screenshots, resolve_pluto_context).

---

## D12 — MCP lifecycle via `mcp.json`, not plugin commands

**Decision:** Plugin declares MCP in bundled `mcp.json`; **Cursor** spawns the entrypoint; **PlutoMCP** owns `serve()` / `connect()`; plugin rules/commands **do not** supervise Julia processes.

**Primary entry:** stdio launcher script → ensure bridge (`serve()`) → `connect()` proxy to shared session.

**Alternative:** HTTP URL to `:2346/sse` for users who run `serve()` manually.

**Why:** Matches Browse/Context7 plugin patterns; keeps click-bridge session aligned with MCP session. Details: [specs/plutomcp-architecture.md](./specs/plutomcp-architecture.md), [specs/cursor-plugin.md § MCP lifecycle](./specs/cursor-plugin.md#mcp-lifecycle-d12).

---

## D7 — Parallel tracks after Phase 1 gate

Layer 2 graph tools (fork) ∥ DOM bridge (here). Plugin Phase 4 after Phase 3.

**Phase 1 gate:**

| Tier | Criterion | Enforced by |
|------|-----------|-------------|
| CI | Reference runner: all 4 v1 scenarios via HTTP `/call` | [`eval/run_reference.jl --all`](./eval/run_reference.jl) |
| Manual | SDK `stage_and_run` outcome pass@1 | [`eval/run.ts`](./eval/run.ts) + `EvalShared.run_score` |
| Baseline | SDK trace score recorded (advisory) | `eval/results/` |

Details: [`eval/README.md`](./eval/README.md). PlutoMCP provides optional `EvalLog.jl` trace hook only.

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

## D13 — Click delivery: Path A (spike 2026-06-17, revised)

**Decision:** Glass Design Mode → `browser_element` / `dom_path` in hook `prompt` carries `pluto-notebook#` + `pluto-cell#` IDs → `resolve_pluto_context` or parse → MCP `read_cell`; **`preToolUse` + `beforeMCPExecution` edit guard**; **`@pluto-context` command** as fallback.

**Spike results:** [spikes/spike-results.md](./spikes/spike-results.md)

| Hypothesis | Outcome |
|------------|---------|
| H1 Design Mode → hook stdin | **Pass (H1a)** — `dom_path` in `prompt` with parseable notebook + cell UUIDs (Glass retest) |
| H2 mid-session rule reload | **Fail** — session-cached `alwaysApply` |
| H3 hook context injection | **Fail** — `beforeSubmitPrompt` block-only |
| H4 edit guard | **Pass** — both hook events deny without `read_cell` receipt |

**Not primary:** inject+queue dom-bridge (Path D).

**Do not use** `cursor-ide-browser` MCP for Pluto — use Agents Glass (`PlutoMCP.serve(require_secret_for_access=false)` for seamless loopback open).

---

## D14 — Loopback auth kwarg (2026-06-17)

**Decision:** Expose `require_secret_for_access` on `PlutoMCP.serve()` and standalone `connect()`; **default stays `true`** (Pluto-compatible) for upstream PRs. Cursor plugin launcher passes `require_secret_for_access=false` on loopback for seamless Glass open without `?secret=` URLs.

**Rationale:** Cursor auto-review blocks agent navigation to secret URLs; loopback trust comes from `127.0.0.1` bind or SSH tunnel. Default unchanged so fork fixes upstream cleanly.

**Plugin:** `serve(require_secret_for_access=false)` — local machine or SSH port-forward only. `require_secret_for_open_links` stays `true`.

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

## Status snapshot (2026-06-18)

| Component | State |
|-----------|-------|
| Planning docs | ✅ [PLAN.md](./PLAN.md) + specs |
| PlutoMCP fork — Phase 1 | ✅ Implemented |
| PlutoMCP fork — Phase 2 | ✅ Graph tools |
| Bridge — DOM resolver (Phase 3) | ✅ **Gated** |
| Cursor plugin Phase 4a–4b | ✅ **Gated** — Design Mode Path A, MCP staging workflow |
| Cursor plugin Phase 4c | ✅ `resolve_pluto_context`; `pending_run` stop hook |
| SDK agent eval | ✅ `eval:stage` pass@1 (local `CURSOR_API_KEY`) |
| Upstream PRs (#6/#7) | 📋 open on mthelm85/PlutoMCP.jl |
