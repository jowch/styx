# Styx Ports (spike — issue #15)

Thin **workspace** Extension Host companion. Cursor owns Remote SSH auto-forward and clash remaps; this extension only calls `vscode.env.asExternalUri(host_pluto_url)` and writes the result for MCP/agents.

**Does not:** invent client ports, run a parallel remapper, or guess from Ports lore.

## Install (Remote SSH host — Editor remote EH required)

**Agents-only limitation:** Agents Window **agent-exec** Extension Host does **not** load user extensions. `jowch.styx-ports` must load on a classic **Open IDE / Editor remote EH** (or equivalent full remote workspace EH) on the SSH host. A laptop-only Local/UI install is useless — `asExternalUri` is a no-op there for remote localhost.

From a **remote** terminal (extension host machine), after installing/updating the Styx plugin from this branch:

```bash
# Plugin already on this branch (STYX_REF=…), then:
bash ~/.cursor/plugins/local/styx/scripts/install-styx-ports.sh
# or from a repo checkout:
bash scripts/install-styx-ports.sh
```

Reload Window. Confirm **Styx Ports** appears under **remote** Extensions (`extensionKind: workspace` → `~/.cursor-server/extensions/…`), not only under local/UI.

## Resolve (binding-scan)

1. Start Pluto (`start_pluto_session`) so host `pluto_url` exists (Agents MCP may own the binding).
2. Companion watches **all** `$STYX_RUNTIME_DIR/windows/*.json` bindings (EH often lacks `VSCODE_PID` / `VSCODE_IPC_HOOK_CLI`) and writes matching:
   `$STYX_RUNTIME_DIR/windows/<window_key>.client.json`
   (`window_key_source` is `binding_scan` when env identity is absent or does not match that key).
3. Or run Command Palette → **Styx: Resolve Pluto Client URL** (optional host URL arg) — same all-bindings scan.

Sidecar fields: `host_url`, `client_url`, `resolved_at`, `window_key_source` (omit / leave unmatched if resolve fails — never invent).

## Agents / MCP

With PlutoMCP that reads the sidecar: `pluto_session_status` includes optional **`client_url`** only when the sidecar matches the current host `pluto_url` for **that MCP window key**. Otherwise the field is **absent**.

| Audience | URL |
|----------|-----|
| Agents Glass (`cursor-ide-browser` on remote EH) | Prefer host `pluto_url` |
| Laptop browser / human handoff | `client_url` when present |
| Unknown | Never invent a remap |

**Agents Window alone is not enough for Ports:** agent-exec EH will not load this companion. Keep an Editor remote window (same SSH host) with Styx Ports enabled so binding-scan can write sidecars that Agents MCP reads.

## Verify on Remote SSH

See the draft PR checklist / project-store spike docs (`issue-15-asexternaluri-spike.md`, `issue-16-validation-path.md`).
