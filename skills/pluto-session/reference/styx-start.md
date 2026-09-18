# styx-start — boot without Glass

Programmatic lifecycle boot for [#26](https://github.com/jowch/styx/issues/26). Starts Pluto (and optionally `open_notebook`) via the window **control bridge** — no Agents Glass, no landing click, no cold `/edit?id=`.

Use when the user wants “get Pluto running / open this notebook” as a one-shot setup. For Glass already open but broken → [reconnect.md](reconnect.md) (**styx-reconnect**).

## Script

```bash
scripts/styx-start.sh                  # start; open ./analysis.jl if present
scripts/styx-start.sh --welcome        # Pluto only
scripts/styx-start.sh -p path/to.jl    # start + open_notebook
scripts/styx-start.sh -p path/to.jl --run
```

`scripts/styx-start.py` is the implementation; the `.sh` wrapper sets `PYTHONPATH` to `hooks/`.

### Binding resolution

Same bridge hooks use (`hooks/pluto_lib.py` → `resolve_bridge_binding`):

1. This Cursor window (`VSCODE_PID` / `VSCODE_IPC_HOOK_CLI` → `windows/<key>.json`) when healthy
2. `--session-id` / `STYX_SESSION_ID` matching exactly one healthy binding
3. Exactly one healthy binding under `$STYX_RUNTIME_DIR/windows/`

Multiple healthy bridges without a session id → error (do not guess).

### Output

Prints `welcome_url=` from **exact** `pluto_url` (one host per session — [glass-navigation.md](glass-navigation.md#one-host-per-session-localhost-vs-127001)). Also session/ports and optional `notebook_id` / `path`.

**Do not** print or open `/edit?id=` as the handoff URL after MCP open — user opens landing and clicks (Path B hydration).

## Agent path

Command **styx-start**: run the script when possible. If the bridge is unavailable, call MCP `start_pluto_session` (+ optional `open_notebook`) **by name** and print the welcome URL. **Never** use `cursor-ide-browser` for this command.

## Defaults

| Flag | Effect |
|------|--------|
| (none) | Start; open `./analysis.jl` if that file exists, else welcome-only |
| `--welcome` | Start only |
| `--path` / `-p` | Open that notebook |
| `--run` | `open_notebook(..., run_notebook=true)` |

Cold start timeout defaults to 180s (`STYX_START_TIMEOUT`).
