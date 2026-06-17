# DOM Bridge Spec — Phase 3

## Goal

User clicks Pluto code or output in the live browser; structured `cell_id` context is captured without manual UUID copy-paste.

## Deliverables

| Artifact | Description |
|----------|-------------|
| `src/dom-resolver.js` | Click resolution + packet builder |
| `src/inject.js` | Dev loader (bookmarklet / console paste) |
| `bridge/server.js` | Local HTTP/WS queue for click packets |
| Manual test checklist | Code, text output, plot, markdown, `@bind`, iframe |

## Click resolution

Prefer `composedPath()` over bare `closest()` for shadow-DOM widget output:

```javascript
function resolvePlutoClick(event) {
  const path = event.composedPath();
  const cell = path.find(el =>
    el instanceof Element && el.tagName === "PLUTO-CELL" && el.id
  );
  if (!cell) return { ok: false, reason: "no_pluto_cell" };

  const notebook = path.find(el =>
    el instanceof Element && el.tagName === "PLUTO-NOTEBOOK" && el.id
  ) ?? document.querySelector("pluto-notebook");

  return {
    ok: true,
    cell_id: cell.id,
    notebook_id: notebook?.id ?? new URLSearchParams(location.search).get("id"),
    in_output: path.some(el => el.tagName === "PLUTO-OUTPUT"),
    in_input: path.some(el => el.tagName === "PLUTO-INPUT"),
    inside_iframe: event.target.ownerDocument !== document,
    target_tag: event.target?.tagName ?? null,
    text_snippet: (event.target?.textContent ?? "").slice(0, 500),
  };
}
```

Attach listener on `document` or `pluto-editor` in capture phase. Require `pluto-editor` present and not `.loading`.

## Context packet

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

## Fallback rules

| Condition | Action |
|-----------|--------|
| No `pluto-cell` in path | Reject; user-visible error |
| Click inside iframe `contentDocument` | Reject; suggest click outside frame or advisory mode |
| `notebook_id` missing | URL `?id=` → `list_notebooks` |
| MCP `read_cell` fails | Wrong session — user must open notebook via `PlutoMCP.serve()` |
| Ambiguous figure (iframe interior) | `cell_id` + advisory mode; screenshot deferred to plugin |

## DOM facts (Pluto frontend)

- `<pluto-cell id="{cell_id}">` from Julia UUID
- `<pluto-notebook id="{notebook_id}">` container
- Markdown, `@bind` (`<bond def="...">`), plots all under `pluto-output` inside cell
- Core Pluto chrome is light DOM; user HTML may use declarative shadow roots
- Iframe outputs (Plotly, full HTML): parent resolves iframe element; inner clicks unreachable

## Constraints

- Target live hydrated DOM (user's Pluto tab), not static export HTML
- MCP session must be Pluto instance from `PlutoMCP.serve()` — document clearly
- Do not use `bond[def]` or variable span IDs as `cell_id`

## Acceptance

- Click code, text output, plot chrome in live notebook → valid `cell_id`
- Hand-built `@pluto-context` + MCP `read_cell` succeeds without typing UUID
- `@bind` widget click resolves to owning cell
- Iframe interior click rejected with clear message

## Test matrix

| Target | Expected `cell_id` | Notes |
|--------|-------------------|-------|
| CodeMirror (`pluto-input`) | ✅ | `in_input=true` |
| Plain text output | ✅ | |
| Markdown rendered HTML | ✅ | |
| `@bind` slider | ✅ | use `composedPath()` |
| Plot iframe border | ✅ | |
| Plot iframe interior | ❌ | reject |
| Header/settings chrome | ❌ | reject |
