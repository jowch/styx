# Cleanup — stale Styx / PlutoMCP sessions

Use when runtime crumbs, foreign-session 409s, or dead bindings block a new session — **not** for Glass auth / Loading cells alone. Command entry: **styx-cleanup**.

Glass/auth/WS recovery → **styx-reconnect** (soft before hard). Fresh boot + Glass ready → **styx-start**. Health check only → `scripts/styx-doctor.sh`.

## When to use which

| Situation | Use |
|-----------|-----|
| Glass “Not yet authenticated”, Loading cells…, stale tab on a **live** Pluto | **styx-reconnect** (soft first) — [glass-navigation.md](glass-navigation.md) |
| Want notebooks; Pluto stopped / never started | **styx-start** or `start_pluto_session` — [lifecycle-tools.md](lifecycle-tools.md) |
| Doctor WARN: binding present but `/health` nonce mismatch; `foreign_session` 409; Reload left orphan `windows/*` / `sessions/*`; `notebook_in_use` from a dead peer; `styx_binding_in_use` / `stale_binding_unrecoverable` | **styx-cleanup** (this playbook) |
| Julia / plugin / MCP install broken | **styx-setup** + doctor — not cleanup |

Cleanup **clears dead state**. Reconnect **recovers a live session**. Start **boots**. Do not jump to cleanup (or kill Julia) for auth alone.

## What “stale” means today

Runtime root (walk in order): `$STYX_RUNTIME_DIR` → `$XDG_RUNTIME_DIR/styx-$UID` → `${TMPDIR:-/tmp}/styx-$UID`. Layout:

| Path | Role | Stale when |
|------|------|------------|
| `windows/<key>.json` | Per-Cursor-window binding (`session_id`, `mcp_port`, `pluto_port`, `owner_pid`) | File exists but `/health` unreachable **or** nonce ≠ `session_id` (doctor: “stale?”) |
| `sessions/<session_id>/` | Claim dir + `owner.json`; Glass cache `glass-views.json` | Session dir with no live health match; claim blocks new bind (`styx_binding_in_use` / `stale_binding_unrecoverable`) |
| `sessions/<id>/glass-views.json` | `(notebook_id\|_\_landing) → viewId` | Cached `viewId` fails “Browser view not found”; **delete that key only** — do not wipe the whole file while the session is live ([glass-navigation.md](glass-navigation.md)) |
| `notebooks/<uuid5>/` | Canonical-path leases (`notebook_in_use`) | Lease `owner.json` points at a dead session (health mismatch); live peer → do **not** steal |
| Orphan Julia / Pluto | Process still listening after MCP/window death | Only after binding says our ports/`owner_pid` and health is dead — never `pkill julia` |

### Unbound vs `foreign_session`

- **Unbound / no binding:** normal until **pluto** MCP connects. Doctor: “No window binding yet”.
- **Bound + matching header:** hooks/CLI send `X-Styx-Session-ID`; bridge accepts.
- **`foreign_session` (HTTP 409):** request hit a loopback bridge whose nonce/session is **not** this window’s binding — leftover bridge on a port, wrong binding file, or cross-window mix-up. Fix with cleanup of the **dead** side, then reconnect/start — do not POST through the foreign bridge.

Reload Window may mint a new window key / `session_id`; old `windows/*` and `sessions/*` can remain until cleaned or naturally replaced when health proves the owner dead (PlutoMCP already auto-replaces some stale claims).

## Safe ladder

Stop at the first step that restores a clean path. Prefer the script for crumbs: `scripts/styx-cleanup.sh` (dry-run) then `--apply`.

### 1. Status

1. Run `scripts/styx-doctor.sh` (binding + health).
2. Call `pluto_session_status` if MCP is up — record `session_id`, `managed`, `pluto`, ports, notebooks.
3. Inventory runtime (script does this): list `windows/*.json`, `sessions/*/`, `notebooks/*/`. For each binding, probe `http://127.0.0.1:<mcp_port>/health` and compare `session_id`.

### 2. Stop managed session

If this window still owns a **managed** Pluto (`pluto` running / tools work):

1. `stop_pluto_session` — tears down Pluto; bound mode **keeps** the control bridge.
2. Re-check status. Do **not** clear live bindings that still pass `/health`.

If MCP is dead but a binding file remains → skip to step 3 (do not invent a foreign `stop`).

### 3. Clear stale bindings / runtime crumbs

Only for entries that **fail** health (or have no reachable bridge):

1. Prefer: `scripts/styx-cleanup.sh --apply` (removes dead `windows/*.json`, matching dead `sessions/<id>/`, and dead notebook leases under this runtime root).
2. Manual equivalent: remove that window’s `windows/<key>.json`, then `sessions/<session_id>/` for the dead id, then `notebooks/<lease>/` whose `owner.json` `session_id` matches the dead session.
3. **Live Glass cache:** if only a viewId is bad, delete that key under `entries` in `glass-views.json` — never wipe the file for a live session.
4. After crumbs are gone: toggle **pluto** MCP off/on or Reload Window so the launcher reclaims a clean binding.

Do **not** delete another Cursor window’s **live** binding (health matches). Do **not** clear leases whose owner health still matches.

### 4. Optional: kill leftover Pluto/Julia (conservative)

**Default: skip.** Only when:

- A stale binding named `owner_pid` / ports, **and**
- `/health` on that `mcp_port` is dead, **and**
- The process still holds **those** ports or is clearly the old MCP owner from the binding,

then stop **that** PID only (`kill <owner_pid>` — escalate once if needed). Prefer `scripts/styx-cleanup.sh --apply --kill-orphans` so the script re-checks health before signal.

**Never:** `pkill -f julia`, killing every Pluto on the machine, or killing processes that are not tied to a **failed** binding in **this** runtime dir.

### 5. Resume

- Need Glass/auth recovery on a healthy stack → **styx-reconnect**.
- Need a fresh session → **styx-start** (or `start_pluto_session` + Glass path).
- Confirm with doctor + `pluto_session_status`.

## Script

```bash
scripts/styx-cleanup.sh              # dry-run inventory + stale classification
scripts/styx-cleanup.sh --apply      # remove dead windows/sessions/leases only
scripts/styx-cleanup.sh --apply --kill-orphans   # also signal dead binding owner_pid
```

Dry-run is the default. `--apply` never removes health-matching bindings. `--kill-orphans` requires `--apply` and never runs without a failed health check.

## Rules

- Soft reconnect before cleanup for auth / Loading cells.
- Conservative kills — orphan proof required; no blanket Julia nukes.
- One host per session — [glass-navigation.md](glass-navigation.md#one-host-per-session-localhost-vs-127001).
- One Cursor window = one Styx session — [lifecycle-tools.md](lifecycle-tools.md).
- Task child: leave Glass to the parent; cleanup of runtime files is parent/shell work.
