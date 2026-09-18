# Cleanup — stale Styx-managed sessions

Use when **Styx** runtime crumbs, `foreign_session` 409s, or dead bindings block a new session — **not** for Glass auth / Loading cells alone, and **not** against a user’s own unmanaged Pluto. Command entry: **styx-cleanup**.

Glass/auth/WS recovery → **styx-reconnect**. Fresh boot + Glass ready → **styx-start** (runs check + one cleanup offer). Health check only → `scripts/styx-doctor.sh`.

## Scripts (two, not one)

| Script | Role | Exit |
|--------|------|------|
| `scripts/styx-check-stale.sh` | **Report only** — inventory Styx-managed stale state | `0` clean · `1` stale found · `2` error |
| `scripts/styx-cleanup.sh --apply` | **Reclaim** — delete only what check would classify stale (re-validates health first) | `0` ok · `2` refused without `--apply` |

```bash
scripts/styx-check-stale.sh                 # report; parse stale= / offer_cleanup=
scripts/styx-check-stale.sh --mark-offer    # record one-offer bit (no-nag this window)
scripts/styx-cleanup.sh --apply             # reclaim stale Styx crumbs
scripts/styx-cleanup.sh --apply --kill-orphans   # also SIGTERM dead Styx binding owner_pid
```

Shared logic: `scripts/lib/styx_stale.py`.

## Styx-managed vs user Pluto

| | Styx-managed | User’s own Pluto |
|--|--------------|------------------|
| How it appears | `windows/<key>.json` binding (`schema_version: 1`, `session_id`, `mcp_port`) under `$STYX_RUNTIME_DIR` | `Pluto.run()` / browser UI with **no** Styx binding |
| Check/cleanup | May report STALE and reclaim | **Never** inventoried, never killed, never “cleaned” |
| Orphan Julia | Only `owner_pid` from a **failed-health Styx binding** with `--kill-orphans` | Untouched |

Check **does not** port-scan `:1234` or guess Pluto processes. If there is no Styx binding file, there is no Styx debris.

## When to use which

| Situation | Use |
|-----------|-----|
| Glass “Not yet authenticated”, Loading cells…, stale tab on a **live** Pluto | **styx-reconnect** (soft first) |
| Want notebooks; Pluto stopped / never started | **styx-start** (includes check → one offer) |
| Check found stale Styx state; user agreed to reclaim | **styx-cleanup** (`--apply`) |
| User’s unmanaged Pluto still running | Leave it alone — not Styx debris |
| Install / Julia | **styx-setup** + doctor |

## Offer once (boot)

Agents run **check** as part of **styx-start** / boot ([styx-start.md](styx-start.md)):

1. `scripts/styx-check-stale.sh` — read `stale=` and `offer_cleanup=`.
2. If `stale=yes` and `offer_cleanup=yes` → **ask the user once** this turn whether to run cleanup.
3. Immediately `scripts/styx-check-stale.sh --mark-offer` (records the offer **before** waiting on the answer).
4. If user accepts → `scripts/styx-cleanup.sh --apply` (optional `--kill-orphans` only when clearly Styx orphan).
5. If user declines or ignores → **do not ask again** this Cursor window — continue boot.
6. If `offer_cleanup=no` (bit already set) → skip the ask; continue boot even if still stale.

### Where the bit lives

`$STYX_RUNTIME_DIR/windows/<window_key>.cleanup-offer.json`  
(fallback if no window key: `$STYX_RUNTIME_DIR/cleanup-offer.json`). Path is printed as `offer_file=`.

Schema: `{ "schema_version": 1, "offered_at", "stale_count", "summary", "window_key" }`. Scoped to the **Cursor window key** (`VSCODE_PID` / IPC hook hash) so a Reload that mints a new key can offer again; the same window does not re-nag.

## What “stale” means (Styx only)

Runtime root: `$STYX_RUNTIME_DIR` → `$XDG_RUNTIME_DIR/styx-$UID` → `${TMPDIR:-/tmp}/styx-$UID`.

| Path | Stale when |
|------|------------|
| `windows/<key>.json` | Valid Styx binding but `/health` unreachable or nonce ≠ `session_id` |
| `sessions/<session_id>/` | Claim / glass-views crumb whose owner health does not match |
| `notebooks/<uuid5>/` | Lease whose owner session health is dead |
| Glass `viewId` only | Delete that key in `glass-views.json` — not a full cleanup |

### Unbound vs `foreign_session`

- **Unbound:** no binding yet — normal until **pluto** MCP connects. Not stale.
- **`foreign_session` (409):** request hit a loopback bridge that is not this window’s binding — leftover **Styx** bridge/binding mismatch. Check → optional cleanup → restart. Do not POST through the foreign bridge.

## Safe ladder

1. **Check** — `styx-check-stale.sh` (or doctor + status).
2. **Stop managed** — if this window still owns a live managed Pluto and you intend a full reclaim of *its* dead peers only, `stop_pluto_session` first when appropriate; never stop another window’s live session.
3. **Cleanup** — `styx-cleanup.sh --apply` after user consent (or explicit `/styx-cleanup`).
4. **Optional kill** — `--kill-orphans` only for Styx binding `owner_pid` after failed health.
5. **Resume** — **styx-start** / reconnect as needed.

## Rules

- Soft reconnect before cleanup for auth / Loading cells.
- Never treat unmanaged user Pluto as Styx debris.
- Conservative kills — Styx binding proof required; no `pkill julia`.
- Offer once per window — mark offer before the user’s answer; never re-nag.
- One host per session — [glass-navigation.md](glass-navigation.md#one-host-per-session-localhost-vs-127001).
