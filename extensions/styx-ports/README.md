# Styx Ports (spike — issue #15)

Thin **workspace** Extension Host companion. Cursor owns Remote SSH auto-forward and clash remaps; this extension only calls `vscode.env.asExternalUri(host_pluto_url)` and writes the result for MCP/agents.

**Does not:** invent client ports, run a parallel remapper, or guess from Ports lore.

## Install (Remote SSH host)

From a **remote** terminal (extension host machine), after installing/updating the Styx plugin from this branch:

```bash
# Plugin already on this branch (STYX_REF=…), then:
bash ~/.cursor/plugins/local/styx/scripts/install-styx-ports.sh
# or from a repo checkout:
bash scripts/install-styx-ports.sh
```

Reload Window. Confirm **Styx Ports** appears under Extensions (remote / SSH).

## Resolve

1. Start Pluto (`start_pluto_session`) so host `pluto_url` exists.
2. Companion auto-watches `$STYX_RUNTIME_DIR/windows/<window_key>.json` and writes:
   `$STYX_RUNTIME_DIR/windows/<window_key>.client.json`
3. Or run Command Palette → **Styx: Resolve Pluto Client URL** (optional host URL arg).

Sidecar fields: `host_url`, `client_url`, `resolved_at` (omit / leave unmatched if resolve fails — never invent).

## Agents / MCP

With PlutoMCP that reads the sidecar: `pluto_session_status` includes optional **`client_url`** only when the sidecar matches the current host `pluto_url`. Otherwise the field is **absent**.

| Audience | URL |
|----------|-----|
| Agents Glass (`cursor-ide-browser` on remote EH) | Prefer host `pluto_url` |
| Laptop browser / human handoff | `client_url` when present |
| Unknown | Never invent a remap |

## Verify on Remote SSH

See the draft PR checklist / `docs/issue-15-asexternaluri-spike.md` in the Styx project store.
