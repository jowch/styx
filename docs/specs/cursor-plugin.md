# Cursor Plugin Spec — Phase 4

## Goal

First-class Cursor integration: workflow rules, commands, click context delivery — not MCP config docs alone.

## Plugin structure

```
pluto-cursor-bridge/
  .cursor-plugin/plugin.json
  mcp.json                          # documents PlutoMCP SSE wiring
  commands/
    pluto-select-cell.md            # read queue → inject context (intent=read)
    pluto-edit-cell.md              # intent=edit
    pluto-explain-cell.md           # intent=explain
  rules/
    pluto-notebook-workflow.mdc     # stage → submit_changes
  hooks/
    hooks.json                      # optional sessionStart bootstrap
    session-start.sh                # static MCP workflow context
  src/
    dom-resolver.js                 # shared with Phase 3
    inject.js
  bridge/
    server.js                       # local click queue (~/.cursor/.../pluto-click.json)
  README.md
```

**Install:** `~/.cursor/plugins/local/pluto-cursor-bridge/`

## Component responsibilities

| Component | Role |
|-----------|------|
| `rules/pluto-notebook-workflow.mdc` | Always-on: stage-first, `submit_changes`, read before edit, draft-buffer warning |
| `commands/pluto-*-cell` | Read click queue → format `@pluto-context` block into chat |
| `hooks/sessionStart` | Optional: inject static workflow + MCP endpoint via `additional_context` |
| `mcp.json` | Pointer to `http://localhost:2346/sse` (PlutoMCP runs separately) |
| `bridge/server.js` | Receives packets from injected JS; persists latest selection |
| `src/dom-resolver.js` | Posts to bridge server on click |

## Context injection format (O3 — resolved)

**Decision:** Commands are primary delivery mechanism for MVP. No reliance on undocumented `beforeSubmitPrompt` rewriting.

```
@pluto-context
notebook_id: ...
cell_id: ...
intent: edit
in_output: true
---
User selected this cell. read_cell for detail; read_notebook_code for full context.
Stage edits with edit_cell (run_after=false); submit_changes when ready.
```

Flow:
1. User activates inject script once per Pluto tab (bookmarklet / console)
2. User clicks cell → packet queued locally
3. User runs command (`Pluto: Edit selected cell`) → chat prefilled with block above
4. Agent follows rule → MCP tools

## Intent UX (O6 — resolved)

**Decision:** Intent set by command choice, not modifier keys.

| Command | `intent` |
|---------|----------|
| `pluto-select-cell` | `read` |
| `pluto-edit-cell` | `edit` |
| `pluto-explain-cell` | `explain` |

Future: `pluto-refactor-cell` command if needed.

## Phased plugin delivery

### Phase 4a — MVP (no DOM inject)

- Workflow rule + MCP wiring docs
- Commands accept manual `cell_id` / `notebook_id` args (paste from browser devtools)
- Validates MCP workflow before click automation

### Phase 4b — Click queue

- `dom-resolver.js` + `bridge/server.js`
- Commands read queue
- Dev inject via bookmarklet

### Phase 4c — Production inject

- Plugin documents one-click activation
- Optional screenshot for figure targets (not MVP)

## What the plugin does NOT do

- Start Julia / `PlutoMCP.serve()` (user responsibility)
- Implement MCP tools (fork)
- Bundle Browse MCP (wrong browser; agent-automation only)

## Acceptance

- Install locally; configure MCP; `serve()` running; notebook open
- Phase 4a: manual cell_id → command → agent edits via MCP
- Phase 4b: click → command → agent chat has context → edit without UUID paste

## MCP connection

```json
{
  "mcpServers": {
    "pluto": {
      "url": "http://localhost:2346/sse"
    }
  }
}
```

Notebooks must be opened in the Pluto session owned by `serve()`, not a separate `Pluto.run()`.
