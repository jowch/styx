# styx-start — boot + Glass ready (same turn)

Programmatic lifecycle boot for [#26](https://github.com/jowch/styx/issues/26).

**Success bar:** one `/styx-start` → user comes back to Pluto **open and ready to work** (no second ask). That means boot, resolve Glass URL, navigate landing, and (when a notebook is known) Path B click — all in **this agent turn**.

Use when the user wants “get Pluto running / open this notebook” as a one-shot setup. For Glass already open but broken → [reconnect.md](reconnect.md) (**styx-reconnect**).

## Script (boot only)

```bash
"${CURSOR_PLUGIN_ROOT}/scripts/styx-start.sh"                  # start; open ./analysis.jl if present
"${CURSOR_PLUGIN_ROOT}/scripts/styx-start.sh" --welcome        # Pluto only
"${CURSOR_PLUGIN_ROOT}/scripts/styx-start.sh" -p path/to.jl    # start + open_notebook
"${CURSOR_PLUGIN_ROOT}/scripts/styx-start.sh" -p path/to.jl --run
```

`scripts/styx-start.py` is the implementation; the `.sh` wrapper sets `PYTHONPATH` to `hooks/`. Run from the **workspace** (so `./analysis.jl` is the notebook cwd). Do not `cd` to the plugin tree. In this repo checkout, `scripts/styx-start.sh` is equivalent.

The script does **not** drive Agents Glass (plugins cannot). The **command** path must finish Glass + Path B after the script returns.

### Binding resolution

Same bridge hooks use (`hooks/pluto_lib.py` → `resolve_bridge_binding`):

1. This Cursor window (`VSCODE_PID` / `VSCODE_IPC_HOOK_CLI` → `windows/<key>.json`) when healthy
2. `--session-id` / `STYX_SESSION_ID` matching exactly one healthy binding
3. Exactly one healthy binding under `$STYX_RUNTIME_DIR/windows/`

Multiple healthy bridges without a session id → error (do not guess).

### Output

Prints `stale_check=` / `offer_cleanup=` / `offer_file=` first (report-only; see [cleanup.md](cleanup.md)), then `welcome_url=` from **exact** `pluto_url` (one host per session — [glass-navigation.md](glass-navigation.md#one-host-per-session-localhost-vs-127001)). Also session/ports and optional `notebook_id` / `path`.

**Do not** print or navigate to `/edit?id=` as the handoff URL after MCP open — open landing, then click (Path B hydration). Never open the OS default browser.

## Agent path (required — same turn)

Command **styx-start** — complete all of this before stopping:

0. **Stale check** — `scripts/styx-check-stale.sh`. If `stale=yes` and `offer_cleanup=yes`: ask once to reclaim → `styx-check-stale.sh --mark-offer` → optional `styx-cleanup.sh --apply`. If declined/ignored or `offer_cleanup=no`, do not re-nag. Styx-managed only — [cleanup.md](cleanup.md).
1. **Boot** — run the script when possible (else MCP `start_pluto_session` + optional `open_notebook` by name).
2. Read `welcome_url=` / `pluto_port=` / `session_id=` / optional `notebook_id=` + `path=` from stdout or status (also `stale_check=` lines if the script emitted them).
3. **Resolve Glass URL** — [Local vs Remote SSH](glass-navigation.md#local-vs-remote-ssh-glass-url):
   - **Local:** exact `welcome_url` / `pluto_url`.
   - **Remote SSH:** remember last-good for this session+port → same-port Glass probe → ask Ports **only if** needed.
4. **Reuse or reveal** Glass — [Reuse vs reveal](glass-navigation.md#reuse-vs-reveal); `cursor-ide-browser` only.
5. `browser_navigate` to **landing**; snapshot to confirm Pluto welcome / My work.
6. **If a notebook was opened / known** — Path B: `browser_snapshot` → `browser_click` the notebook on landing ([path-b-open.md](path-b-open.md)). **Never** cold `/edit?id=` after MCP open.
7. **Stop** when Glass shows the notebook editor (or landing if welcome-only). Do **not** ask the user to open a URL.

## Defaults

| Flag | Effect |
|------|--------|
| (none) | Start; open `./analysis.jl` if that file exists, else welcome-only |
| `--welcome` | Start only |
| `--path` / `-p` | Open that notebook |
| `--run` | `open_notebook(..., run_notebook=true)` |

Cold start timeout defaults to 180s (`STYX_START_TIMEOUT`).
