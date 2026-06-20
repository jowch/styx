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

One canonical name per operation. Full catalog: [PlutoMCP.jl AGENTS.md](https://github.com/jowch/PlutoMCP.jl/blob/main/AGENTS.md) and `skills/pluto-workflow/reference/tools.md`.

**Shipped (Phase 1):** canonical names (`read_cell`, `edit_cell`, `submit_changes`, …). No parallel legacy aliases.

---

## D4 — Stage-first workflow *(target)*

Edit with `run_after=false` → `submit_changes` once. Server tracks `pending_run` / `stale_cell_ids`.

---

## D5 — Click-to-context bridge *(target)*

**Primary (D13):** Glass Design Mode → MCP **`resolve_pluto_context`** / **`read_cell`** from `dom_path` in hook `prompt`. Details: `skills/pluto-workflow/reference/design-mode.md`.

---

## D6 — Cursor plugin *(target)*

Full plugin; skills + commands deliver workflow (no native browser hook). Lifecycle: [specs/pluto-lifecycle.md](./specs/pluto-lifecycle.md).

Phased: 4a manual cell_id → 4b Design Mode (Path A) → 4c polish (screenshots, resolve_pluto_context).

---

## D12 — MCP lifecycle via `mcp.json`, not plugin commands

**Decision:** Plugin declares MCP in bundled `mcp.json`; **Cursor** spawns the entrypoint; **PlutoMCP** owns `serve()` / `connect()`; plugin rules/commands **do not** supervise Julia processes.

**Primary entry:** stdio launcher script → ensure bridge (`serve()`) → `connect()` proxy to shared session.

**Alternative:** HTTP URL to `:2346/sse` for users who run `serve()` manually.

**Why:** Matches Browse/Context7 plugin patterns; keeps click-bridge session aligned with MCP session. Amended by D15: launcher → standalone `connect()`; Pluto starts via `start_pluto_session`.

---

## D7 — Parallel tracks after Phase 1 gate

Layer 2 graph tools (fork) ∥ DOM bridge (here). Plugin Phase 4 after Phase 3.

**Phase 1 gate:**

| Tier | Criterion | Enforced by |
|------|-----------|-------------|
| CI | Reference runner: all v1 scenarios via HTTP `/call` | [`eval/run_reference.jl --all --strict-trace`](./eval/run_reference.jl) |
| D15 | Deferred lifecycle scenarios 0/C/D/E | [`scripts/validate-pluto-lifecycle.sh`](../scripts/validate-pluto-lifecycle.sh) |

Details: [`eval/README.md`](./eval/README.md). PlutoMCP provides optional `EvalLog.jl` trace hook only.

---

## D8 — Hard rename, no aliases

Remove old tool names from MCP schema when Phase 1 ships. No parallel `get_cell`/`read_cell` registrations. Upstream PRs are clean breaks.

---

## D9 — Draft-buffer policy

MCP tracks server-side dirty only. Agent reads before edit. Server wins on conflict. Document in plugin rule; no OT in Phase 1. Browser editor has a separate draft buffer (last-write-wins on server).

---

## D10 — Rich output deferred

MCP returns text placeholders for images/HTML in Phase 1. Click bridge provides `cell_id`; explain/refactor on plots is advisory until plugin screenshots (Phase 4c+).

---

## D11 — Intent via commands

`pluto-select-cell` / `pluto-edit-cell` / `pluto-explain-cell` set intent — not modifier keys.

---

## D13 — Click delivery: Path A (spike 2026-06-17, revised)

**Decision:** Glass Design Mode → `browser_element` / `dom_path` in hook `prompt` carries `pluto-notebook#` + `pluto-cell#` IDs → `resolve_pluto_context` → MCP `read_cell`; **`preToolUse` + `beforeMCPExecution` edit guard** (`guard-write.py`).

| Hypothesis | Outcome |
|------------|---------|
| H1 Design Mode → hook stdin | **Pass (H1a)** — `dom_path` in `prompt` with parseable notebook + cell UUIDs (Glass retest) |
| H2 mid-session rule reload | **Fail** — session-cached `alwaysApply` |
| H3 hook context injection | **Fail** — `beforeSubmitPrompt` block-only |
| H4 edit guard | **Pass** — both hook events deny without `read_cell` receipt |

**Not primary:** inject+queue dom-bridge (Path D).

**Do not use** `plugin-browse-browser` for Pluto — separate automation daemon, not Agents Glass.

**Glass navigation (D13, amended 2026-06-18):** **`cursor-ide-browser`** in **Agents Window** (`browser_navigate` / `browser_click`) — view IDs are `glass-browser-*`, same panel as Design Mode. Do not use `plugin-browse-browser`. Legacy spike: Editor-only chat hung on auth; Agents Window path is fine with `require_secret_for_access=false`.

---

## D14 — Loopback auth kwarg (2026-06-17)

**Decision:** Expose `require_secret_for_access` on `PlutoMCP.serve()` and standalone `connect()`; **default stays `true`** (Pluto-compatible) for upstream PRs. Cursor plugin launcher passes `require_secret_for_access=false` on loopback for seamless Glass open without `?secret=` URLs.

**Rationale:** Cursor auto-review blocks agent navigation to secret URLs; loopback trust comes from `127.0.0.1` bind or SSH tunnel. Default unchanged so fork fixes upstream cleanly.

**Plugin:** `serve(require_secret_for_access=false)` — local machine or SSH port-forward only. `require_secret_for_open_links` stays `true`.

---

## D15 — Lazy warm lifecycle; agent-owned bootstrap (2026-06-18)

**Decision:** **Option C** — MCP stdio (`connect()` standalone) is always up when **pluto** MCP is enabled; **Pluto does not start** until the user requests notebook work. The **agent** runs lifecycle MCP tools — not shell scripts.

| Principle | Choice |
|-----------|--------|
| Cursor-first | Ordinary Julia work does not start Pluto |
| Notebook intent | User says "work on notebooks" → agent bootstraps session |
| Notebook on disk | **Opt-in** — agent asks which file; never auto-`open_notebook` |
| User scripts | **Not** user-facing (`pluto-serve.sh` dev-only) |
| Auto-serve on MCP connect | **Off** default; `PLUTOMCP_AUTO_SERVE=1` opt-in |

**Flow:**
- **Path A** (no notebook named): `start_pluto_session` → landing page in Glass → user picks notebook → agent resolves id on **next** prompt.
- **Path B** (specific path): `start_pluto_session` → landing page (cookies) → `open_notebook` → notebook URL in Glass.

**Skills:** `pluto-session` (bootstrap), `pluto-workflow` (edits), `pluto-semantics` (grammar).

**Spec:** [specs/pluto-lifecycle.md](./specs/pluto-lifecycle.md)

**Amends D12:** Launcher targets standalone `connect()` only; lifecycle via MCP tools replaces shell `serve()` + proxy as the primary user path.

**PlutoMCP (implemented):** `pluto_session_status`, `start_pluto_session`, `stop_pluto_session`, `open_notebook`; deferred standalone `connect()` until `start_pluto_session`. Acceptance signed off 2026-06-18 (`scripts/validate-pluto-lifecycle.sh`).

---

## D16 — Cursor 3 only; no cross-harness dependency (2026-06-20)

**Decision:** Styx is a **Cursor 3 plugin only**. Users must not need Claude Code, Codex, OpenCode, or any other agent harness installed or configured.

| Principle | Choice |
|-----------|--------|
| Install surface | `curl \| bash` / `scripts/install-styx.sh` → `~/.cursor/plugins/local/styx/` — not Claude `/plugin marketplace add` |
| Manifest | `.cursor-plugin/plugin.json` only — no `.claude-plugin/` sidecar for distribution |
| Runtime | All behavior via Cursor-native components: `mcp.json`, `hooks/hooks.json`, rules, skills, `cursor-ide-browser` |
| Third-party skills | **Not** a supported install path — Cursor may load `~/.claude/plugins/cache/` when that toggle is on; we do not document or depend on it |
| Prerequisites | **Cursor 3** + **Julia 1.9+** on PATH — nothing else |

**Rationale:** Cursor's third-party-skills bridge can make Claude-installed plugins appear to work in Cursor, but that is undocumented, partial (hooks/skills ≠ full MCP bundle), and creates a false "install once, use everywhere" story. Styx ships a complete Cursor plugin bundle; distribution and support assume Cursor alone.

**Amends D6:** Plugin target is Cursor 3 local install via `scripts/install.sh` — not multi-harness marketplace repos.
