#!/usr/bin/env python3
"""Reclaim stale Styx-managed runtime crumbs (bindings / sessions / leases).

Re-validates health before every delete. Never touches unmanaged user Pluto.
Optional --kill-orphans only signals owner_pid from health-failed Styx bindings.
"""
from __future__ import annotations

import argparse
import os
import signal
import sys
from pathlib import Path

_LIB = Path(__file__).resolve().parent / "lib"
if str(_LIB) not in sys.path:
    sys.path.insert(0, str(_LIB))

import styx_stale  # noqa: E402


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument(
        "--apply",
        action="store_true",
        help="Required to delete — without it, refuse (use styx-check-stale for report-only)",
    )
    ap.add_argument(
        "--kill-orphans",
        action="store_true",
        help="With --apply: SIGTERM owner_pid of stale Styx bindings that fail health",
    )
    args = ap.parse_args()

    if not args.apply:
        print(
            "styx-cleanup: refusing without --apply "
            "(report-only → scripts/styx-check-stale.sh)",
            file=sys.stderr,
        )
        return 2
    if args.kill_orphans and not args.apply:
        print("error: --kill-orphans requires --apply", file=sys.stderr)
        return 2

    inv = styx_stale.inventory()
    root = inv["runtime_dir"]
    print(f"Styx cleanup (runtime: {root})")
    print("mode: apply" + (" + kill-orphans" if args.kill_orphans else ""))
    print("scope: Styx-managed bindings/sessions/leases only — not user Pluto")
    print()

    live_sids = set(inv["live_session_ids"])
    stale_bindings = inv["stale_bindings"]
    stale_sessions = inv["stale_sessions"]
    stale_leases = inv["stale_leases"]

    if not (stale_bindings or stale_sessions or stale_leases):
        print("nothing stale — nothing to reclaim")
        return 0

    removed = 0
    for b in stale_bindings:
        path = Path(b["path"])
        # Re-check immediately before delete
        data = styx_stale.read_json(path)
        if styx_stale.is_styx_binding(data) and data is not None:
            if styx_stale.health_matches(data.get("mcp_port"), data.get("session_id")):
                print(f"keep {path} (became live)")
                continue
        print(f"remove {path}")
        path.unlink(missing_ok=True)
        removed += 1
        if args.kill_orphans:
            pid = b["owner_pid"]
            port, sid = b["mcp_port"], b["session_id"]
            if port and sid and styx_stale.health_matches(port, sid):
                print(f"  skip kill {pid}: health became live")
            elif pid and styx_stale.pid_alive(pid):
                try:
                    os.kill(pid, signal.SIGTERM)
                    print(f"  SIGTERM owner_pid={pid} (Styx binding owner only)")
                except OSError as e:
                    print(f"  skip kill {pid}: {e}")
            else:
                print(f"  skip kill: owner_pid={pid} not alive")

    for s in stale_sessions:
        if s["session_id"] in live_sids:
            print(f"keep {s['path']} (session still live)")
            continue
        path = Path(s["path"])
        # Re-classify
        again = styx_stale.classify_session_dir(path)
        if not again["stale"] or again["session_id"] in live_sids:
            print(f"keep {path} (became live)")
            continue
        print(f"remove {path}")
        styx_stale.rm_tree(path)
        removed += 1

    for lease in stale_leases:
        if lease["session_id"] in live_sids:
            print(f"keep {lease['path']} (owner session still live)")
            continue
        path = Path(lease["path"])
        again = styx_stale.classify_lease(path)
        if again is None or not again["stale"] or again["session_id"] in live_sids:
            print(f"keep {path} (became live)")
            continue
        print(f"remove {path}")
        styx_stale.rm_tree(path)
        removed += 1

    print(f"done: removed {removed} stale Styx path(s)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
