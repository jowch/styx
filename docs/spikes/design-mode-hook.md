# Spike: Glass Design Mode + Hooks + MCP-first

**Status:** Complete (2026-06-17) — results in [spike-results.md](./spike-results.md). **Path A** chosen (D13).  
**Unblocks:** Phase 4b/4c click delivery; Phase 3 DOM bridge is lighter (parse `dom_path`, not inject).  
**Related:** [cursor-plugin.md](../specs/cursor-plugin.md) · [dom-bridge.md](../specs/dom-bridge.md) · [plutomcp-architecture.md](../specs/plutomcp-architecture.md)

## Why this spike exists

We want **Glass + Design Mode** as the primary click UX (not arbitrary-browser inject), with notebook mutations flowing through **PlutoMCP** before the agent acts on stale assumptions.

Open questions that planning cannot answer from docs alone:

1. Does Design Mode put **parseable Pluto identity** (`pluto-cell` id, xpath) into hook-visible `prompt` text?
2. Can **`alwaysApply` rules** be updated mid-chat and picked up on the next turn?
3. Can **`beforeSubmitPrompt`** do anything beyond block/allow (inject context, rewrite prompt)?
4. Is a **`preToolUse` / `beforeMCPExecution`** edit guard sufficient for read-before-edit?

This spike is a **falsification suite** (~30–45 min). It does not ship production behavior.

---

## Hypotheses

| ID | Hypothesis | If confirmed | If falsified |
|----|------------|--------------|--------------|
| **H1** | Design Mode inlines xpath / `pluto-cell` `@id` into `beforeSubmitPrompt` `prompt` | Hook or agent can regex → MCP `read_cell` / future `resolve_pluto_context` | Design Mode context is model-only; need agent-first MCP or dom-resolver |
| **H2** | Rewriting an `alwaysApply` `.mdc` mid-chat updates agent context next turn | Dynamic rule file as MCP result carrier might work | Rules are session-cached; abandon hook→rule injection |
| **H3** | `beforeSubmitPrompt` supports context injection (`additional_context`, etc.) | Expand spike scope | Confirmed block-only; use agent-first MCP + edit guards |
| **H4** | `preToolUse` can reliably deny `MCP:edit_cell` without `read_cell` receipt | Ship edit guard in plugin hooks | Rely on MCP server enforcement only |

**Explorer prior (2026-06-17):** H1 unknown (needs empirics); H2 ~15% likely; H3 ~0% likely; H4 likely yes.

---

## Prerequisites

| Requirement | Notes |
|-------------|-------|
| Cursor with **Agents Window** + **Glass browser** | Design Mode is ⌘⇧D in integrated browser, not classic IDE browser pane |
| `PlutoMCP.serve()` running | Notebook at `http://localhost:1234`; bridge at `:2346` |
| Known `cell_id` | Pick a cell; note `<pluto-cell id="…">` in devtools |
| Spike hook plugin or project hooks | Temporary; remove or gate after spike |

Record Cursor version: `_______`

---

## Spike artifacts (temporary)

Create under plugin dev install or project `.cursor/`:

```
hooks/
  hooks.json
  log-submit.sh           # append beforeSubmitPrompt stdin
  log-post-tool.sh        # append postToolUse on Write (screenshot path)
  spike-results.md        # human fills during tests
rules/   (or .cursor/rules/)
  spike-token.mdc         # Test B only
```

### `hooks.json`

```json
{
  "version": 1,
  "hooks": {
    "beforeSubmitPrompt": [
      {
        "command": "${CURSOR_PLUGIN_ROOT}/hooks/log-submit.sh",
        "matcher": "UserPromptSubmit",
        "timeout": 5
      }
    ],
    "postToolUse": [
      {
        "command": "${CURSOR_PLUGIN_ROOT}/hooks/log-post-tool.sh",
        "matcher": "Write",
        "timeout": 5
      }
    ]
  }
}
```

### `log-submit.sh`

```bash
#!/bin/bash
input=$(cat)
ts=$(date -Iseconds)
log="${CURSOR_PLUGIN_ROOT:-.}/hooks/spike-submit.log"
mkdir -p "$(dirname "$log")"
echo "[$ts] $input" >> "$log"
echo '{"continue": true}'
```

### `log-post-tool.sh`

```bash
#!/bin/bash
input=$(cat)
ts=$(date -Iseconds)
log="${CURSOR_PLUGIN_ROOT:-.}/hooks/spike-post-tool.log"
echo "[$ts] $input" >> "$log"
echo '{}'
```

Make scripts executable: `chmod +x hooks/*.sh`

---

## Test matrix

### Test A — What does `beforeSubmitPrompt` see from Design Mode?

**Goal:** Validate or falsify **H1**.

**Steps:**

1. Open notebook in **Glass** at `localhost:1234` (from `serve()` session).
2. Enable Design Mode (⌘⇧D).
3. Click a **known** `pluto-cell` (note `id` from devtools). *(Earlier drafts said ⌥+click; Cursor 3.x uses ⌘⇧D to toggle Design Mode, then a normal click.)*
4. Type short prompt: `SPIKE_A: explain this cell`
5. Send.
6. Open `hooks/spike-submit.log`.

**Record:**

| Field | Observed |
|-------|----------|
| `prompt` full text | |
| Contains xpath? | yes / no |
| Contains `pluto-cell`? | yes / no |
| Contains expected `@id='…'` or UUID? | yes / no |
| `attachments[]` types | |
| Any non-`file`/`rule` attachment types? | |

**Repeat** with: (a) click on **code** (`pluto-input`), (b) click on **text output**, (c) click on **plot chrome** (not iframe interior), (d) ⌘+L multi-reference if available.

**Pass H1:** At least one scenario yields parseable `cell_id` in `prompt`.  
**Fail H1:** `prompt` is only user-typed text; element identity not in hook payload.

---

### Test A′ — Screenshot / image path

**Goal:** See if Design Mode screenshots appear in hook-visible paths.

**Steps:** Same as Test A; check `spike-post-tool.log` for `Write` to `.../assets/image-*.png`.

**Record:** Screenshot file path pattern: `_______`  
**Note:** Images are reported **not** in `beforeSubmitPrompt.attachments` (forum); this confirms parallel pipeline.

---

### Test B — Mid-session `alwaysApply` rule reload

**Goal:** Validate or falsify **H2**.

**Setup** — `rules/spike-token.mdc`:

```markdown
---
description: spike token test
alwaysApply: true
---
SPIKE_TOKEN=ALPHA
```

**Steps:**

1. **New chat** → ask: `What is SPIKE_TOKEN? Reply with only the value.`
2. Agent reply: `_______`
3. Edit file to `SPIKE_TOKEN=BETA` (same chat; do not reload window).
4. Ask same question again.
5. Agent reply: `_______`

**Pass H2:** Turn 2 answers `BETA`.  
**Fail H2 (expected):** Turn 2 still `ALPHA` or unknown.

---

### Test B′ — Hook writes dynamic selection rule

**Goal:** Falsify hook → `pluto-live-selection.mdc` carrier.

**Steps:**

1. Extend `log-submit.sh`: if `prompt` contains `localhost:1234`, write `rules/pluto-live-selection.mdc` with `SELECTED_CELL_ID=<parsed or timestamp>`.
2. New chat; Design Mode click cell A; send prompt.
3. Ask: `What SELECTED_CELL_ID is in your rules?`
4. Click cell B; send again; ask again.

**Pass:** Agent tracks B after second click.  
**Fail (expected):** Stale or missing — rules session-cached.

---

### Test C — Negative control: hook injection

**Goal:** Confirm **H3** falsified.

**Steps:**

1. Change `log-submit.sh` output to:
   `{"continue": true, "additional_context": "INJECTED_XYZ"}`
2. New chat → ask: `Do you see INJECTED_XYZ in your context? yes/no only`

**Expected:** `no` — `beforeSubmitPrompt` output is `continue` + `user_message` only per [Cursor hooks docs](https://cursor.com/docs/hooks).

---

### Test D — Positive control: prompt delivery

**Goal:** Baseline for reliable per-turn context.

**Steps:**

1. New chat; user message only:
   ```
   @pluto-context
   notebook_id: <uuid>
   cell_id: <uuid>
   intent: read
   ---
   SPIKE_D positive control
   ```
2. Ask: `What cell_id did I give you?`

**Expected:** Agent cites `cell_id` — this is the command/prompt path we can always ship.

---

### Test E — Sync MCP from hook (only if H1 passes)

**Goal:** Measure latency; confirm hook **cannot** inject MCP result even if call succeeds.

**Steps:**

1. Parse `cell_id` from logged `prompt`.
2. In hook (or manual terminal):
   ```bash
   curl -sf --max-time 2 'http://127.0.0.1:2346/health'
   curl -sS --max-time 2 -X POST 'http://127.0.0.1:2346/call' \
     -H 'Content-Type: application/json' \
     -d '{"jsonrpc":"2.0","id":1,"method":"tools/call","params":{"name":"get_cell","arguments":{"notebook_id":"<id>","cell_id":"<id>"}}}'
   ```
3. Record wall time: `_______ ms`
4. Same chat without putting curl result in prompt — ask agent for cell code.

**Expected:** MCP returns fast; agent **does not** see result unless it's in the user message.

---

### Test F — `preToolUse` edit guard

**Goal:** Validate **H4** for read-before-edit.

**Setup:** Add to `hooks.json`:

```json
"preToolUse": [
  {
    "command": "${CURSOR_PLUGIN_ROOT}/hooks/guard-edit.sh",
    "matcher": "MCP:edit_cell|MCP:set_cell_code|MCP:add_cell",
    "timeout": 5
  }
],
"postToolUse": [
  {
    "command": "${CURSOR_PLUGIN_ROOT}/hooks/record-read.sh",
    "matcher": "MCP:read_cell|MCP:get_cell|MCP:read_notebook_code",
    "timeout": 5
  }
]
```

(`guard-edit.sh` / `record-read.sh` — minimal spike scripts using `.cursor/hooks/state/pluto-reads.json`)

**Steps:**

1. New chat; ask agent to `edit_cell` / `set_cell_code` without reading.
2. Record: denied? `agent_message` visible?
3. `read_cell` then `edit_cell` — allowed?

**Pass H4:** Deny without read; allow after read.

---

## Results template

Copy into `hooks/spike-results.md` when done:

```markdown
# Design Mode + Hook Spike Results

- Date:
- Cursor version:
- PlutoMCP commit / version:

## Hypothesis outcomes

| ID | Result | Evidence |
|----|--------|----------|
| H1 | PASS / FAIL | |
| H2 | PASS / FAIL | |
| H3 | PASS / FAIL | |
| H4 | PASS / FAIL | |

## Test A notes
- prompt shape:
- parseable cell_id scenarios:

## Architecture decision
- [ ] A path (see decision tree)
- [ ] B path
- [ ] C path
- [ ] D path

## Follow-ups
```

---

## Decision tree

```
                    Run Tests A, B, C (+ D always)
                              │
              ┌───────────────┴───────────────┐
              │                               │
         H1: xpath/id                    H1: not in prompt
         in prompt                             │
              │                               │
    ┌─────────┴─────────┐                     │
    │                   │                     │
 H2: rule reload    H2: fail              Path B
    works?          (expected)         Design Mode → model
    │                   │              Agent 1st MCP tool
 Path C            Path A              + preToolUse guard
 (surprise)        xpath parse         (+ dom-resolver if
 dynamic rule       in hook or agent      deep clicks fail)
 + MCP gate         first tool
```

### Path A — Prompt-parse + agent-first MCP (H1 pass, H2 fail)

- Design Mode for pointing; **first agent tool** = `resolve_pluto_context` (xpath/url string → `cell_id` + `read_cell`).
- Optional `beforeSubmitPrompt`: block if `/health` fails (`continue: false`).
- `preToolUse`: edit guard (Test F).
- **No** inject+queue as primary path; Glass-only.

### Path B — Model-only Design Mode (H1 fail)

- Design Mode enriches **model** (xpath + screenshot); not hook-visible.
- Plugin rule: first MCP call mandatory; agent uses visual + user text.
- May need **minimal dom-resolver** for reliable `cell_id` on deep clicks, or user selects cell chrome.
- `preToolUse` edit guard.
- Commands with manual `@pluto-context` remain fallback (Test D).

### Path C — Dynamic rule carrier (H2 pass — unlikely)

- `beforeSubmitPrompt` calls MCP `/call`, writes `pluto-live-selection.mdc`.
- Re-validate every Cursor upgrade; document version dependency.
- Still ship edit guard.

### Path D — Status quo inject+queue (H1 fail + Path B unsatisfying)

- Keep [dom-bridge.md](../specs/dom-bridge.md) inject + queue + commands.
- Design Mode optional; not primary.
- Revisit when/if Cursor exposes browser-selection hook attachments.

**Default if spike inconclusive:** Path B + Test D command fallback + Test F edit guard. Do not block Phase 4a (manual `cell_id` + rules + MCP).

---

## What we already know (pre-spike)

| Topic | Finding | Source |
|-------|---------|--------|
| `beforeSubmitPrompt` output | `continue`, `user_message` only | Cursor hooks docs |
| Design Mode identity | xpath, attributes, styles, screenshot → **model** | [Design Mode blog](https://cursor.com/blog/design-mode) |
| `alwaysApply` rules | Documented as per **session** | Cursor rules docs |
| `resolve_pluto_context` | Does not exist in PlutoMCP | Repo grep |
| MCP `/call` | Sync JSON-RPC on `127.0.0.1:2346`, no auth | `PlutoMCP.jl` `Server.jl` |
| Cloud agents | `beforeSubmitPrompt` does not run | Hooks docs |

---

## Out of scope for this spike

- Production `resolve_pluto_context` implementation
- Full dom-bridge / inject.js build
- OT/CRDT or polling staleness
- Browse plugin / separate-browser automation
- Committing D6 click-delivery decision before results filed

---

## After the spike

1. Fill `spike-results.md` and check a hypothesis row in this doc (or link PR).
2. Update [cursor-plugin.md](../specs/cursor-plugin.md) phased delivery per chosen path.
3. If Path A/B: add `resolve_pluto_context` to [mcp-phase-1.md](../specs/mcp-phase-1.md) or a small Phase 4 addendum.
4. Record decision in [DECISIONS.md](../DECISIONS.md) (e.g. D13 click delivery).
5. Remove or feature-flag spike hooks from production plugin manifest.
