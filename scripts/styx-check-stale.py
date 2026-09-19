#!/usr/bin/env python3
"""Report-only check for stale Styx-managed runtime state.

Exit codes (agent-friendly):
  0 — no stale Styx state
  1 — stale Styx state found
  2 — check error

Does not modify anything except --mark-offer (records one-offer bit for this window).
Never flags an unmanaged user Pluto (no Styx binding under the runtime dir).
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

_LIB = Path(__file__).resolve().parent / "lib"
if str(_LIB) not in sys.path:
    sys.path.insert(0, str(_LIB))

import styx_stale  # noqa: E402


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument(
        "--mark-offer",
        action="store_true",
        help="Record that cleanup was offered this Cursor window (no-nag bit)",
    )
    ap.add_argument(
        "--json",
        action="store_true",
        help="Print full inventory JSON on stderr (key=value trailer stays on stdout)",
    )
    args = ap.parse_args()

    try:
        inv = styx_stale.inventory()
    except OSError as e:
        print(f"styx-check-stale: error: {e}", file=sys.stderr)
        print("stale=error")
        print("offer_cleanup=no")
        return 2

    root = inv["runtime_dir"]
    count = inv["stale_count"]
    key = styx_stale.window_key()
    offered = styx_stale.offer_recorded(Path(root), key)
    offer_file = styx_stale.offer_path(Path(root), key)

    print(f"Styx check-stale (runtime: {root})")
    print()
    print("## Scope")
    print("Styx-managed only: windows/*.json bindings, sessions/<id>/, notebooks/ leases.")
    print("Unmanaged user Pluto (no Styx binding) is ignored — never reported as stale.")
    print()

    print("## windows/")
    if not inv["bindings"]:
        print("(none)")
    for b in inv["bindings"]:
        tag = "LIVE" if b["health_ok"] else "STALE"
        print(
            f"  [{tag}] {b['path']} sid={b['session_id']} "
            f"mcp={b['mcp_port']} pluto={b['pluto_port']} "
            f"owner_pid={b['owner_pid']} owner_alive={b['owner_alive']}"
        )

    print("## sessions/")
    if not inv["sessions"]:
        print("(none)")
    for s in inv["sessions"]:
        tag = "LIVE" if s["health_ok"] else "STALE"
        glass = " glass-views" if s["has_glass_views"] else ""
        print(f"  [{tag}] {s['path']} sid={s['session_id']} mcp={s['mcp_port']}{glass}")

    print("## notebooks/ (leases)")
    if not inv["leases"]:
        print("(none)")
    for lease in inv["leases"]:
        tag = "LIVE" if lease["health_ok"] else "STALE"
        print(f"  [{tag}] {lease['path']} sid={lease['session_id']} mcp={lease['mcp_port']}")

    summary = (
        f"{len(inv['stale_bindings'])} stale window(s), "
        f"{len(inv['stale_sessions'])} stale session dir(s), "
        f"{len(inv['stale_leases'])} stale lease(s)"
    )
    print()
    print(f"summary: {summary}; {len(inv['live_session_ids'])} live session id(s)")

    if args.mark_offer:
        path = styx_stale.mark_offer(
            stale_summary=summary,
            stale_count=count,
            root=Path(root),
            key=key,
        )
        offered = True
        print(f"offer_recorded={path}")

    # Machine-readable trailer for agents / styx-start
    print(f"stale={'yes' if count else 'no'}")
    print(f"stale_count={count}")
    print(f"offer_cleanup={'yes' if count and not offered else 'no'}")
    print(f"offer_already={'yes' if offered else 'no'}")
    print(f"offer_file={offer_file}")
    print(f"window_key={key or ''}")

    if args.json:
        import json

        print(json.dumps(inv, indent=2), file=sys.stderr)

    if count:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
