# DOM Bridge — Manual Test Checklist

Two paths — **Path A is primary** (D13); Path C is dev/fallback only.

---

## Path A — Design Mode (primary)

**Prerequisites**

- [ ] `PlutoMCP.serve(require_secret_for_access=false)` — notebook in **Agents Glass** at `http://localhost:1234`
- [ ] MCP at `:2346` on same session
- [ ] Design Mode active in Glass (**Cmd+Shift+D** — not Option/Alt+click)

**After each Design Mode click on a cell target:**

1. Confirm hook `prompt` includes `dom_path` with `pluto-cell#<uuid>`
2. Run parser (Node or pasted in devtools):

```javascript
import { parseDomPath, buildContextPacket, formatPlutoContext } from "./src/dom-resolver.js";
// Or copy dom_path string from hook prompt:
const domPath = "… > pluto-notebook#… > pluto-cell#… > pluto-output …";
formatPlutoContext(buildContextPacket(parseDomPath(domPath), "read"));
```

3. Paste `@pluto-context` block into Cursor → agent calls MCP `read_cell` without manual UUIDs

### Path A test matrix (from spike H1)

| # | Target | Expected `pluto-cell#` in `dom_path`? | Notes |
|---|--------|--------------------------------------|-------|
| 1 | CodeMirror line (`pluto-input`) | ✅ | Per-line clicks same cell id |
| 2 | Plain text output | ✅ | |
| 3 | Markdown rendered HTML | ✅ | |
| 4 | `@bind` slider | ✅ | |
| 5 | Plot (`img` / SVG in output) | ✅ | Plots.jl often `<img>`, not iframe |
| 6 | Between-cells (add button) | ✅ | Attached to adjacent cell |
| 7 | Bare `main` / helpbox / header | ❌ | Re-click cell or `@pluto-context` |
| 8 | Drawing on screenshot | ❌ | Vision-only, no structured ID |

### parseDomPath unit checks

| Input | Expected |
|-------|----------|
| Contains `pluto-cell#<uuid>` | ✅ `cell_id` extracted |
| Contains `pluto-notebook#<uuid>` | ✅ `notebook_id` extracted |
| No `pluto-cell#` | ❌ `no_pluto_cell_in_dom_path` |

---

## Path C — Inject + queue (dev / fallback only)

**Not production UX.** Use to test packet format before Phase 4 plugin hooks.

**Prerequisites**

- [ ] `PlutoMCP.serve()` — notebook at `http://localhost:1234`
- [ ] Click bridge: `npm run bridge` → `http://127.0.0.1:3457/health`
- [ ] Inject active: `fetch('http://127.0.0.1:3457/inject.js').then(r=>r.text()).then(eval)`
- [ ] Toast: "Pluto click bridge active"

**After each click:**

```bash
curl -s http://127.0.0.1:3457/click/format
```

### Path C test matrix

| # | Target | Expected | Notes |
|---|--------|----------|-------|
| 1 | CodeMirror / `pluto-input` | ✅ capture | `in_input=true` |
| 2 | Plain text output | ✅ capture | |
| 3 | Markdown HTML | ✅ capture | |
| 4 | `@bind` slider | ✅ capture | `composedPath()` |
| 5 | Plot iframe **border** | ✅ capture | |
| 6 | Plot iframe **interior** | ❌ reject | Toast: inside iframe |
| 7 | Header / settings chrome | ❌ reject | Toast: no Pluto cell |

### Bridge API smoke tests

```bash
curl -s http://127.0.0.1:3457/health
curl -s http://127.0.0.1:3457/click/latest | jq .
curl -s http://127.0.0.1:3457/click/pop | jq .
```

Teardown: `__plutoClickBridgeTeardown()` in console; Ctrl+C on bridge.

---

## MCP end-to-end gate (both paths)

- [ ] `@pluto-context` block in Cursor chat (from Path A parser or Path C `/click/format`)
- [ ] Agent calls `read_cell` with `notebook_id` + `cell_id`
- [ ] Returns current cell code/output without user pasting UUIDs
