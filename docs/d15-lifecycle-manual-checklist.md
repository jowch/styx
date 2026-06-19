# D15 Lifecycle — Manual Validation Checklist

After automated gates (`scripts/d15-validate-deferred.sh`, `eval/run_reference.jl --all --strict-trace`). Spec: [pluto-lifecycle.md](./specs/pluto-lifecycle.md).

## Preflight

```bash
./scripts/ensure-julia-env.sh          # first run
./scripts/d15-preflight.sh             # baseline: :2346 and :1234 down
./scripts/d15-validate-deferred.sh     # Scenarios 0, C.2, D, E
```

Styx at `~/.cursor/plugins/local/styx/`; **pluto** MCP enabled.

## Scenario A — Landing (Path A)

**Prompt:** *"I want to work on my Pluto notebooks"* (or **pluto-notebooks**)

| Pass criteria |
|---------------|
| `start_pluto_session` → landing `http://127.0.0.1:1234/` in Glass via `cursor-ide-browser` |
| No chat prompt for which notebook; no `open_notebook` on bootstrap |
| **Next prompt:** ⌘⇧D → click cell → `resolve_pluto_context` → `read_cell` → edit works |

## Scenario B — Named notebook (Path B)

**Prompt:** *"Open `eval/fixtures/reactive_xy.jl` in Pluto"* (or **pluto-notebooks** with path)

| Pass criteria |
|---------------|
| Landing in Glass → `open_notebook` → **`browser_click` notebook on landing** (not pasted `/edit?id=`) |
| Safe-preview banner; agent reminds **Run notebook code** for outputs |
| Design Mode edit on opened notebook |

See [path-b-edit-url-loading.md](./known-issues/path-b-edit-url-loading.md) if `Loading cells...` hangs.

## Scenario C — Already running

After A or B: *"Add a cell at the end"* → agent skips `start_pluto_session`; `pluto_session_status` → `running`.

## Failure triage

| Symptom | Fix |
|---------|-----|
| MCP won't connect | `./scripts/ensure-julia-env.sh`; toggle **pluto** MCP |
| No `pluto-cell#` in click | ⌘⇧D, re-click inside cell |
| `Loading cells...` forever | Click notebook on landing — [path-b-edit-url-loading.md](./known-issues/path-b-edit-url-loading.md) |
| Bridge dead after killing `serve()` | Toggle **pluto** MCP off/on |

## Validation log

| Date | 0 | A | B | C | D | Notes |
|------|---|---|---|---|---|-------|
| 2026-06-18 | ☑ | ☑ | ☑ | ☑ | ☑ | Automated 0/C/D/E + live Glass Path A/B |
