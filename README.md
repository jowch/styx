# pluto-cursor-bridge

Bridge Pluto.jl notebooks to Cursor agent workflows via [PlutoMCP.jl](https://github.com/jowch/PlutoMCP.jl) and Glass Design Mode click context.

## Planning (read before building)

| Doc | Purpose |
|-----|---------|
| **[PLAN.md](docs/PLAN.md)** | Integrated phase map, architecture, build sequence |
| **[DECISIONS.md](docs/DECISIONS.md)** | Running decision log (D13: Design Mode = primary click path) |
| **[specs/](docs/specs/)** | Detailed specs per phase |
| **[Pluto agent primer](docs/pluto-agent-primer.md)** | Agent training: browser-first, staging, errors, tools |
| **[Pluto semantics](docs/pluto-semantics.md)** | Cell grammar and reactivity reference |
| **[PlutoMCP architecture](docs/specs/plutomcp-architecture.md)** | How serve/connect works; full frontend; session model |

Fork MCP semantics: PlutoMCP.jl `AGENTS.md`.

## Quick reference

- MCP endpoint: `http://localhost:2346/sse` (wired by plugin `mcp.json` + launcher)
- Click context: **Glass Design Mode** (`Cmd+Shift+D`, then click) → `pluto-cell#` in hook `prompt` (D13 Path A)
- Dev fallback: inject + queue at `http://127.0.0.1:3457` (`npm run bridge`) — not production UX
- Plugin install: `~/.cursor/plugins/local/pluto-cursor-bridge/` (symlink to this repo for dev)

---

## Cursor plugin (Phase 4)

Install for local development (Cursor 3.x):

```bash
./scripts/sync-local-plugin.sh   # copies into ~/.cursor/plugins/local/
```

Then **Developer: Reload Window** (`Cmd+Shift+P`).

**Cursor 3 note:** External symlinks into `~/.cursor/plugins/local/` are **rejected** (security). Use `sync-local-plugin.sh` after each change, or copy manually — do not `ln -s` from `~/projects/...`.

Verify under **Cursor Settings (`Cmd+Shift+J`) → Plugins → Installed**. Toggle MCP under **Features → Model Context Protocol** if needed.

### What ships

| Component | Role |
|-----------|------|
| `mcp.json` + `scripts/pluto-mcp-launcher.sh` | Cursor spawns MCP; launcher bootstraps plugin-root Julia env, ensures `serve()` bridge, then `connect()` stdio proxy |
| `rules/pluto-notebook-workflow.mdc` | Stage-first workflow + Design Mode `dom_path` parsing instructions |
| `commands/pluto-*-cell` | Read / edit / explain intent commands (manual ID fallback) |
| `hooks/` | Design Mode selection tracking, bridge health check, read-before-edit guard (H4) |

Dev env: copy `.env.dev.example` → `.env.dev` (gitignored), set `PLUTOMCP_SOURCE`, then `./scripts/sync-local-plugin.sh` and reload Cursor. The launcher loads `.env.dev` automatically.

### End-to-end (Path A)

1. Enable plugin → Cursor starts `pluto` MCP via launcher (Pluto UI at `http://localhost:1234`).
2. Open a notebook in **Agents Glass**.
3. In Glass: **Cmd+Shift+D** to toggle Design Mode, click a cell, then send a prompt.
4. Agent parses `pluto-cell#` from the `browser_element` block → `read_cell` → staged edits → `submit_changes`.

See [docs/specs/cursor-plugin.md](docs/specs/cursor-plugin.md) for full spec.

---

## Click context — Path A (primary)

**Production flow (D13):** Open Pluto in **Agents Glass** (`PlutoMCP.serve(require_secret_for_access=false)` on loopback). User toggles Design Mode (**Cmd+Shift+D**), clicks a cell, and sends a prompt. Hook `prompt` includes `dom_path` with `pluto-notebook#…` and `pluto-cell#…`. Plugin parses IDs and the agent calls MCP `read_cell`.

Spike evidence: [docs/spikes/spike-results.md](docs/spikes/spike-results.md).

Phase 4 ships plugin hooks/commands that wire this automatically. Until then, test the parser manually:

```javascript
// Node or browser with dom-resolver loaded
import { parseDomPath, formatPlutoContext, buildContextPacket } from "./src/dom-resolver.js";

const domPath =
  "main > pluto-editor > pluto-notebook#836a54be-… > pluto-cell#98b9ea94-… > pluto-output";
const packet = buildContextPacket(parseDomPath(domPath), "read");
console.log(formatPlutoContext(packet));
// Paste @pluto-context block into Cursor → agent calls read_cell
```

---

## Click context — Path C (dev / fallback only)

Optional harness for testing packet format before Phase 4. **Not the production click path.**

Requires a notebook opened via `PlutoMCP.serve()` — MCP session and browser tab must be the same Pluto instance.

### 1. Start the dev queue (optional)

```bash
npm run bridge
# → http://127.0.0.1:3457/health
```

### 2. Activate inject on the Pluto tab

Open notebook at `http://localhost:1234`, then in devtools console:

```javascript
fetch("http://127.0.0.1:3457/inject.js")
  .then((r) => r.text())
  .then(eval);
```

Or paste [`src/inject.js`](src/inject.js) directly.

### 3. Test a click

Click a cell, then:

```bash
curl -s http://127.0.0.1:3457/click/format
```

Paste the `@pluto-context` block into Cursor chat.

See [docs/dom-bridge-test-checklist.md](docs/dom-bridge-test-checklist.md) for the full matrix (Path A + Path C).

### Artifacts

| File | Role |
|------|------|
| [`src/dom-resolver.js`](src/dom-resolver.js) | **`parseDomPath`** (Path A), `formatPlutoContext`, `resolvePlutoClick` (Path C dev) |
| [`src/inject.js`](src/inject.js) | Dev-only browser listener (Path C) |
| [`bridge/server.js`](bridge/server.js) | Dev-only HTTP queue (Path C) |
