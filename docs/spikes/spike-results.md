# Design Mode + Hook Spike Results

- Date: 2026-06-17 (H1 matrix completed in follow-up session)
- Cursor version: 3.7.42
- Julia version: 1.12.6
- MCP mode: HTTP SSE (`http://localhost:2346/sse`)
- Trusted workspace: yes (hooks fired on user submit)
- notebook_id: `836a54be-6ab0-11f1-a5c6-edcac3c06aa0` (`/tmp/spike-notebook.jl`)

## Hypothesis outcomes

| ID | Result | Evidence |
|----|--------|----------|
| H1 | **PASS** | Design Mode `browser_element` in hook `prompt` includes `dom_path` with `pluto-notebook#` + `pluto-cell#` for code, output, plot, and `@bind` widget clicks. |
| H2 | **FAIL** (expected) | `spike-token.mdc` edited ALPHA→BETA mid-session; agent context not reloaded from file edit alone (session-cached rules). |
| H3 | **FAIL** (expected) | C1: `additional_context` in hook stdout does not reach agent. C2: `user_message` rewrite not verified in-agent. |
| H4 | **PASS** | `guard-edit.sh` (preToolUse) and `guard-mcp.sh` (beforeMCPExecution) both deny without read; allow after `pluto-reads.json` match. |

## H1 tier matrix (Glass Design Mode: ⌘⇧D + click)

| Tier | Target | `pluto-cell#`? | Source field | Notes |
|------|--------|----------------|--------------|-------|
| H1a (code) | `div.cm-line` (per-line CodeMirror) | yes | `prompt` | Same cell id for each line in a `begin/end` block |
| H1b (output) | `pluto-output` (text/plain) | yes | `prompt` | |
| H1c (plot) | `img` in `pluto-output` (SVG blob) | yes | `prompt` | Plots.jl renders as `<img>`, not iframe |
| H1 bind | `bond > input[type=range]` | yes | `prompt` | `@bind` must be **last expression** in cell so widget renders in output |
| Between-cells | `button.add_cell.before`, shoulder | yes | `prompt` | Attached to adjacent cell |
| Vague gap | `pluto-notebook` only | notebook id only | `prompt` | No `pluto-cell#` |
| Chrome | `main`, helpbox (Live docs) | no | `prompt` | Outside notebook cells |
| Drawing | Pen annotation on screenshot | no | image only | Visual hint for model; not `browser_element` / `dom_path` |
| A₀ control | Plain prompt (no Design Mode) | no | `prompt` | No DOM identity in hook stdin |

### Example `dom_path` (bind slider)

```text
… > pluto-notebook#836a54be-… > pluto-cell#98b9ea94-… > pluto-output… > bond > input
```

Parser: extract `pluto-cell#([0-9a-f-]+)` from `dom_path` — depth of leaf node does not matter.

## Test notes

### A₀ (negative control)

Plain prompts: `attachments` has rules only; no xpath / `pluto-cell` / UUID.

### B (H2 rule reload)

Turn 1: `SPIKE_TOKEN=ALPHA`. Turn 2: file edited to `BETA` — agent still saw ALPHA.

### C1/C2 (H3 injection)

Hook scripts emit `additional_context` / `user_message`; agent does not receive injected text.

### D (positive control)

**NOT RUN** — `@pluto-context` manual block documented as fallback in [cursor-plugin.md](../specs/cursor-plugin.md).

### E (MCP latency)

`/call` `get_cell` ~26 ms via curl.

### F (edit guard)

preToolUse + beforeMCPExecution deny/allow validated. Reference scripts: `.cursor/hooks/guard-*.sh`.

### Browser MCP

**Do not use** `cursor-ide-browser` for Pluto — hangs on auth gate. Use **Agents Glass** with terminal `?secret=…` URL.

## Architecture decision

- [x] **Path A** — parse `dom_path` from Design Mode `prompt` → MCP `read_cell` / `resolve_pluto_context`; H4 edit guard
- [ ] Path B — agent-first MCP only (superseded by H1 PASS)
- [ ] Path C — dynamic rule injection (falsified by H2)
- [ ] Path D — inject+queue (H3 falsified)

**Rationale:** H1 PASS on all targets that matter for click-bridge. H3/H2 falsified injection paths. H4 guard validated. Drawing is screenshot-only (vision), not structured click context.

**Decision record:** [D13](../DECISIONS.md).

## Side findings

### MCP `add_cell` / browser DOM desync

Structural MCP edits (`add_cell`, `delete_cell`, `move_cell`) could leave server ahead of Glass DOM when `cell_order` was mutated in place. `set_cell_code` on existing cells synced normally. Fix in PlutoMCP.jl fork: assign new `cell_order` vector before `_notify_browser`. See [known-issues/plutomcp-cell-order-sync.md](../known-issues/plutomcp-cell-order-sync.md).

### `@bind` cell layout

Last expression in a cell becomes `pluto-output`. Put `@bind …` last; put `n` in a separate cell if you want the bound value as text output.

## Follow-ups (post-spike)

1. Ship plugin Phase 4a (rules, `mcp.json`, staging workflow).
2. Implement `resolve_pluto_context` + Path A prompt parsing (Phase 4b).
3. Ship edit guard in plugin `hooks.json`.
4. Phase 1 MCP v2 in fork (`read_notebook_code`, staging, receipts).
