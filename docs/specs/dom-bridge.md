# DOM Bridge Spec — Phase 3

> **Click delivery (D13):** **Path A** — Glass Design Mode → `dom_path` in hook `prompt` → `parseDomPath()` → MCP `read_cell`. See [DECISIONS.md § D13](../DECISIONS.md), [spike-results.md](../spikes/spike-results.md).

## Goal

Structured `notebook_id` + `cell_id` context when the user selects a Pluto cell — without manual UUID copy-paste.

## Delivery paths

| Path | Role | When |
|------|------|------|
| **A — Design Mode** (primary) | Parse `pluto-cell#` / `pluto-notebook#` from Glass Design Mode `dom_path` in hook `prompt` | Production plugin (Phase 4b) |
| **B — Manual `@pluto-context`** | User or command pastes formatted block with IDs | Fallback when Design Mode is ambiguous |
| **C — Inject + queue** (dev only) | `inject.js` listener → `bridge/server.js` queue | Local dev, pre-plugin testing, inject-path regression |

**Not primary:** Path C (inject+queue). Do not ship inject-as-default UX in the plugin.

## Phase 3 deliverables

Shared resolver utilities + optional dev harness:

| Artifact | Role |
|----------|------|
| `src/dom-resolver.js` | **`parseDomPath`** (Path A), **`formatPlutoContext`**, `buildContextPacket`; `resolvePlutoClick` for Path C dev |
| `src/inject.js` | **Dev/fallback only** — console paste listener (Path C) |
| `bridge/server.js` | **Dev/fallback only** — local HTTP queue for Path C |
| `docs/dom-bridge-test-checklist.md` | Manual tests for Path A + Path C |

Phase 4 wires Path A into plugin hooks/commands. Phase 3 ships the shared parser and packet format.

---

## Path A — Design Mode (primary)

Validated in spike H1. User toggles Design Mode (**Cmd+Shift+D**) in **Agents Glass**, clicks a cell. Hook stdin includes `browser_element` / `dom_path`:

```text
… > pluto-notebook#836a54be-… > pluto-cell#98b9ea94-… > pluto-output… > bond > input
```

Plugin hook or command extracts IDs:

```javascript
import { parseDomPath, buildContextPacket, formatPlutoContext } from "./dom-resolver.js";

const resolved = parseDomPath(domPathFromHookPrompt);
const packet = buildContextPacket(resolved, intent);
const block = formatPlutoContext(packet);
// → agent calls MCP read_cell(notebook_id, cell_id)
```

### Path A acceptance

| Target | `pluto-cell#` in `dom_path`? |
|--------|------------------------------|
| CodeMirror line (`pluto-input`) | ✅ |
| Plain text output | ✅ |
| Markdown rendered HTML | ✅ |
| `@bind` slider | ✅ |
| Plot (`img` / SVG in output) | ✅ |
| Between-cells chrome (add button) | ✅ (attached cell) |
| Bare `main` / helpbox / header | ❌ — re-click cell or use `@pluto-context` |
| Drawing annotation on screenshot | ❌ — vision-only, no structured ID |

### Path A fallback rules

| Condition | Action |
|-----------|--------|
| No `pluto-cell#` in `dom_path` | Reject; user re-clicks a cell or uses `@pluto-context` |
| `notebook_id` missing from path | URL `?id=` or MCP `list_notebooks` |
| MCP `read_cell` fails | Wrong session — notebook must be from `PlutoMCP.serve()` |
| Ambiguous gap (notebook id only) | Advisory; agent uses `read_notebook_code` |

---

## Context packet

Shared format for Path A, B, and C:

```json
{
  "notebook_id": "uuid",
  "cell_id": "uuid",
  "in_output": true,
  "in_input": false,
  "inside_iframe": false,
  "inside_shadow_root": false,
  "target_tag": "IMG",
  "text_snippet": "...",
  "intent": "read|edit|explain|refactor",
  "screenshot_path": null
}
```

`formatPlutoContext(packet)` produces the `@pluto-context` chat block.

---

## Path C — Inject + queue (dev / fallback only)

For local testing of Path C packet format. **Not the production click path** — Styx plugin hooks handle Path A.

`resolvePlutoClick` uses `composedPath()` (not bare `closest()`) for shadow-DOM widgets:

```javascript
function resolvePlutoClick(event) {
  const path = event.composedPath();
  const cell = path.find(el =>
    el instanceof Element && el.tagName === "PLUTO-CELL" && el.id
  );
  if (!cell) return { ok: false, reason: "no_pluto_cell" };
  // ...
}
```

Attach via `inject.js` on `document` capture phase. Requires `pluto-editor` present and not `.loading`.

### Path C rejection rules

| Condition | Action |
|-----------|--------|
| No `pluto-cell` in path | Reject; user-visible error |
| Click inside iframe `contentDocument` | Reject; suggest border click or Path A |
| Plot iframe interior | ❌ reject (Path A may still work on frame chrome in Glass) |

---

## DOM facts (Pluto frontend)

- `<pluto-cell id="{cell_id}">` from Julia UUID
- `<pluto-notebook id="{notebook_id}">` container
- Markdown, `@bind` (`<bond def="...">`), plots under `pluto-output`
- Core Pluto chrome is light DOM; user HTML may use declarative shadow roots
- Iframe outputs (Plotly): inject path rejects interior; Design Mode often resolves parent cell from frame chrome

## Constraints

- Target live hydrated DOM in Agents Glass / user's Pluto tab — not static export HTML
- MCP session must be Pluto instance from `PlutoMCP.serve()` — document clearly
- Do not use `bond[def]` or variable span IDs as `cell_id`
- Do not use `cursor-ide-browser` MCP for Pluto (D13) — use Agents Glass

## Phase 3 gate

- [ ] `parseDomPath` extracts IDs from representative Design Mode `dom_path` strings
- [ ] `formatPlutoContext` → paste → MCP `read_cell` succeeds
- [ ] (Optional dev) Path C inject captures code/output/`@bind` clicks per test matrix

## Phase 4 gate (plugin)

Install plugin → Design Mode click → hook/command → agent chat has context → edit via MCP without UUID paste. See [cursor-plugin.md](./cursor-plugin.md).
