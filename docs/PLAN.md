# Integrated Plan

Master planning doc for Pluto ↔ Cursor integration. **Decisions** live in [DECISIONS.md](./DECISIONS.md); detailed specs in [specs/](./specs/).

## Design principles

| Idea | Implication |
|------|-------------|
| Live notebook graph, not raw file bytes | Agents mutate `Pluto.Notebook` via MCP; Pluto owns persistence, reactivity, browser sync |
| Read as file, edit as cell | Agents read a linear code projection; mutations keyed by stable `cell_id`, never line offsets |
| Whole-code read beats neighborhood retrieval | Reactive notebooks make local context misleading; most notebooks fit one projection |
| Two API layers | Layer 1: file-shaped CRUD + order; Layer 2: graph/validation diagnostics |
| Blocking tools + mutation receipts | Mutations return post-change context so agents avoid 5–10 follow-up calls |
| Fork PlutoMCP, keep Cursor separate | In-process Pluto session in fork; browser/DOM in this repo |

**Out of scope (for now):** `auto_reload_from_file`, Pluto on-disk format changes, line-based file patching.

---

## Architecture

```mermaid
flowchart TB
  subgraph client [Agent clients]
    Cursor[Cursor agent]
    CLI[CLI agent]
  end

  subgraph bridge [pluto-cursor-bridge]
    Plugin[Cursor plugin]
    DomParser[parseDomPath from Design Mode]
    DevQueue[Dev inject queue optional]
  end

  subgraph mcp [PlutoMCP.jl fork]
    L1[Layer 1: read_notebook_code CRUD staging]
    L2[Layer 2: deps symbols validate]
    Receipts[Mutation receipts]
  end

  Pluto[Pluto.ServerSession]
  Browser[Pluto UI pluto-cell]

  Browser -->|Design Mode dom_path| Plugin
  Plugin --> DomParser
  DomParser -->|@pluto-context| Cursor
  DevQueue -.->|dev fallback| Cursor
  Cursor --> L1
  CLI --> L1
  L1 --> Receipts
  L2 --> Receipts
  Receipts --> Pluto
  Pluto --> Browser
```

**Identity everywhere:** `notebook_id` + `cell_id`.

---

## Phase map

| Phase | Repo | Goal | Depends on |
|-------|------|------|------------|
| **0** | PlutoMCP.jl | Reference artifacts + taxonomy | — |
| **1** | PlutoMCP.jl | MCP v2: projection, staging, receipts, renames | 0 |
| **2** | PlutoMCP.jl | Graph/validation (Layer 2) | 1 gate |
| **3** | pluto-cursor-bridge | Shared resolver (`parseDomPath`, packet format); dev inject harness | 1 gate |
| **4** | pluto-cursor-bridge | Cursor plugin — Design Mode hooks, commands, rules (D13 Path A) | 3 |
| **5** | both | Snapshots, restore workflow, concurrency docs | 1 |

Phases **2 and 3 run in parallel** after Phase 1 gate. Phase 4 needs Phase 3. Phase 5 can start lightly after Phase 1.

**Spec links:**
- [PlutoMCP architecture](./specs/plutomcp-architecture.md)
- [MCP Phase 1](./specs/mcp-phase-1.md)
- [MCP Phase 2](./specs/mcp-phase-2.md)
- [DOM bridge](./specs/dom-bridge.md)
- [Cursor plugin](./specs/cursor-plugin.md)
- [Safety & rollback](./specs/safety.md)
- [**Spike:** Design Mode + hooks](./spikes/design-mode-hook.md) *(run before finalizing click delivery)*

---

## Build sequence

```
Phase 0 ──► Phase 1 (1A→1B→1C→tests→Cursor validate)
                    │
            ┌───────┴───────┐
            ▼               ▼
        Phase 2         Phase 3
        (graph)         (DOM bridge)
            │               │
            └───────┬───────┘
                    ▼
                Phase 4 (plugin)
                    ▼
                Phase 5 (safety)
```

### Phase 0 — Reference artifacts

Add gitignored `PlutoMCP.jl/reference/` with real notebooks (e.g. `turtles.jl` from JuliaPluto/featured) + committed `docs/reference-taxonomy.md` in fork.

Ground projection rules: cell types, manifest blobs, `@bind` shims, markdown cells, empty cells, cell-order footer vs execution order.

### Phase 1 — MCP v2 core

See [specs/mcp-phase-1.md](./specs/mcp-phase-1.md).

**Gate:** See eval harness — CI runs [`run_reference.jl --all`](../../PlutoMCP.jl/eval/README.md) (deterministic); manual SDK `stage_and_run` outcome pass@1 via [bridge/eval](../eval/README.md).

### Phase 2 — Graph / validation

See [specs/mcp-phase-2.md](./specs/mcp-phase-2.md). Trigger: agents need "why did this re-run?" or "where is `foo` defined?"

### Phase 3 — DOM bridge utilities

See [specs/dom-bridge.md](./specs/dom-bridge.md). **Primary delivery is Path A (Design Mode), not inject** — D13.

Ships `parseDomPath`, `formatPlutoContext`, shared packet schema. Optional dev inject+queue for pre-plugin testing.

**Gate:** `parseDomPath` on representative Design Mode `dom_path` strings → `@pluto-context` → MCP `read_cell` succeeds.

### Phase 4 — Cursor plugin

See [specs/cursor-plugin.md](./specs/cursor-plugin.md). Wire **Path A**: Design Mode `dom_path` in hook `prompt` → parse → MCP.

**Gate:** Install plugin → Design Mode click in Glass → agent chat has context → edit via MCP without pasting UUID.

### Phase 5 — Safety

See [specs/safety.md](./specs/safety.md).

---

## Current state (2026-06-17)

| Component | State |
|-----------|-------|
| PlutoMCP fork — Phase 1 MCP tools | ✅ Implemented |
| PlutoMCP fork — Phase 2 graph/validation tools | ✅ `Graph.jl` — 6 tools ([spec](./specs/mcp-phase-2.md)) |
| PlutoMCP fork — agent eval harness | ✅ Reference runner + score.jl ([eval README](../../PlutoMCP.jl/eval/README.md)) |
| Bridge — SDK eval orchestrator | ✅ [`eval/`](../eval/README.md) (manual, `CURSOR_API_KEY`) |
| Bridge — DOM resolver utilities (Phase 3) | ✅ `parseDomPath`, `formatPlutoContext` + dev inject harness ([spec](./specs/dom-bridge.md)) |
| Bridge — Design Mode plugin wiring (Phase 4) | ✅ Plugin scaffold: `mcp.json`, rules, commands, hooks ([spec](./specs/cursor-plugin.md)) |

---

## Upstreaming

| Upstreamable to mthelm85/PlutoMCP.jl | Stays in fork / bridge |
|--------------------------------------|------------------------|
| `read_notebook_code`, order tools | Cursor plugin, DOM bridge |
| Mutation receipts, staging | Screenshot / intent UX |
| Graph + validation tools | Context packet conventions |

Prove API in real Cursor workflows first; open focused upstream PRs for generic tools only.
