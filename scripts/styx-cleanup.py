#!/usr/bin/env python3
"""Inventory / clear stale Styx runtime crumbs (windows, sessions, notebook leases).

Dry-run by default. Never removes health-matching bindings. Optional --kill-orphans
only signals owner_pid from bindings that already failed health.
"""
from __future__ import annotations

import argparse
import json
import os
import signal
import sys
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any


def runtime_dir() -> Path:
    env = os.environ.get("STYX_RUNTIME_DIR")
    if env:
        return Path(env)
    uid = os.environ.get("UID") or str(os.getuid())
    xdg = os.environ.get("XDG_RUNTIME_DIR")
    if xdg:
        return Path(xdg) / f"styx-{uid}"
    tmp = os.environ.get("TMPDIR") or "/tmp"
    return Path(tmp) / f"styx-{uid}"


def read_json(path: Path) -> dict[str, Any] | None:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
    return data if isinstance(data, dict) else None


def health_matches(mcp_port: Any, session_id: Any, timeout: float = 2.0) -> bool:
    if not isinstance(mcp_port, int) or not isinstance(session_id, str) or not session_id:
        return False
    url = f"http://127.0.0.1:{mcp_port}/health"
    try:
        with urllib.request.urlopen(url, timeout=timeout) as resp:
            body = resp.read().decode("utf-8", errors="replace")
    except (urllib.error.URLError, TimeoutError, OSError):
        return False
    body = body.strip()
    if not body.startswith("{"):
        return False
    try:
        data = json.loads(body)
    except json.JSONDecodeError:
        return False
    return isinstance(data, dict) and data.get("session_id") == session_id


def pid_alive(pid: Any) -> bool:
    if not isinstance(pid, int) or pid <= 1:
        return False
    try:
        os.kill(pid, 0)
    except ProcessLookupError:
        return False
    except PermissionError:
        return True
    return True


def classify_binding(path: Path) -> dict[str, Any]:
    data = read_json(path) or {}
    sid = data.get("session_id")
    port = data.get("mcp_port")
    owner = data.get("owner_pid")
    live = health_matches(port, sid)
    return {
        "path": str(path),
        "session_id": sid if isinstance(sid, str) else None,
        "mcp_port": port if isinstance(port, int) else None,
        "pluto_port": data.get("pluto_port"),
        "owner_pid": owner if isinstance(owner, int) else None,
        "owner_alive": pid_alive(owner),
        "health_ok": live,
        "stale": not live,
    }


def classify_lease(path: Path) -> dict[str, Any]:
    owner = read_json(path / "owner.json") or {}
    sid = owner.get("session_id")
    port = owner.get("mcp_port")
    live = health_matches(port, sid)
    return {
        "path": str(path),
        "session_id": sid if isinstance(sid, str) else None,
        "mcp_port": port if isinstance(port, int) else None,
        "health_ok": live,
        "stale": not live,
    }


def classify_session_dir(path: Path) -> dict[str, Any]:
    owner = read_json(path / "owner.json") or {}
    sid = owner.get("session_id") or path.name
    port = owner.get("mcp_port")
    # Prefer owner.json health; if missing owner, treat as stale crumb
    if isinstance(port, int) and isinstance(sid, str):
        live = health_matches(port, sid)
    else:
        live = False
    glass = path / "glass-views.json"
    return {
        "path": str(path),
        "session_id": sid if isinstance(sid, str) else path.name,
        "mcp_port": port if isinstance(port, int) else None,
        "health_ok": live,
        "stale": not live,
        "has_glass_views": glass.is_file(),
    }


def rm_tree(path: Path) -> None:
    if path.is_file() or path.is_symlink():
        path.unlink(missing_ok=True)
        return
    if not path.is_dir():
        return
    for child in sorted(path.rglob("*"), reverse=True):
        if child.is_file() or child.is_symlink():
            child.unlink(missing_ok=True)
        elif child.is_dir():
            try:
                child.rmdir()
            except OSError:
                pass
    try:
        path.rmdir()
    except OSError:
        pass


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument(
        "--apply",
        action="store_true",
        help="Remove stale windows/sessions/leases (default is dry-run)",
    )
    ap.add_argument(
        "--kill-orphans",
        action="store_true",
        help="With --apply: SIGTERM owner_pid of stale bindings that fail health",
    )
    args = ap.parse_args()
    if args.kill_orphans and not args.apply:
        print("error: --kill-orphans requires --apply", file=sys.stderr)
        return 2

    root = runtime_dir()
    print(f"Styx cleanup (runtime: {root})")
    print(f"mode: {'apply' if args.apply else 'dry-run'}"
          + (" + kill-orphans" if args.kill_orphans else ""))
    print()

    if not root.is_dir():
        print("OK  no runtime directory — nothing to clean")
        return 0

    windows_dir = root / "windows"
    sessions_dir = root / "sessions"
    notebooks_dir = root / "notebooks"

    bindings = []
    if windows_dir.is_dir():
        for path in sorted(windows_dir.glob("*.json")):
            bindings.append(classify_binding(path))

    sessions = []
    if sessions_dir.is_dir():
        for path in sorted(p for p in sessions_dir.iterdir() if p.is_dir()):
            sessions.append(classify_session_dir(path))

    leases = []
    if notebooks_dir.is_dir():
        for path in sorted(p for p in notebooks_dir.iterdir() if p.is_dir()):
            leases.append(classify_lease(path))

    live_sids = {b["session_id"] for b in bindings if b["health_ok"] and b["session_id"]}
    live_sids |= {s["session_id"] for s in sessions if s["health_ok"] and s["session_id"]}

    print("## windows/")
    if not bindings:
        print("(none)")
    for b in bindings:
        tag = "LIVE" if b["health_ok"] else "STALE"
        print(
            f"  [{tag}] {b['path']} sid={b['session_id']} "
            f"mcp={b['mcp_port']} pluto={b['pluto_port']} "
            f"owner_pid={b['owner_pid']} owner_alive={b['owner_alive']}"
        )

    print("## sessions/")
    if not sessions:
        print("(none)")
    for s in sessions:
        tag = "LIVE" if s["health_ok"] else "STALE"
        glass = " glass-views" if s["has_glass_views"] else ""
        print(f"  [{tag}] {s['path']} sid={s['session_id']} mcp={s['mcp_port']}{glass}")

    print("## notebooks/ (leases)")
    if not leases:
        print("(none)")
    for lease in leases:
        tag = "LIVE" if lease["health_ok"] else "STALE"
        print(f"  [{tag}] {lease['path']} sid={lease['session_id']} mcp={lease['mcp_port']}")

    stale_bindings = [b for b in bindings if b["stale"]]
    stale_sessions = [s for s in sessions if s["stale"]]
    stale_leases = [lease for lease in leases if lease["stale"]]

    print()
    print(
        f"summary: {len(stale_bindings)} stale window(s), "
        f"{len(stale_sessions)} stale session dir(s), "
        f"{len(stale_leases)} stale lease(s); "
        f"{len(live_sids)} live session id(s) kept"
    )

    if not args.apply:
        if stale_bindings or stale_sessions or stale_leases:
            print("dry-run only — re-run with --apply to remove STALE entries")
        else:
            print("nothing stale")
        return 0

    removed = 0
    for b in stale_bindings:
        path = Path(b["path"])
        print(f"remove {path}")
        path.unlink(missing_ok=True)
        removed += 1
        if args.kill_orphans:
            pid = b["owner_pid"]
            # Re-check health immediately before signal
            if b["mcp_port"] and b["session_id"] and health_matches(b["mcp_port"], b["session_id"]):
                print(f"  skip kill {pid}: health became live")
            elif pid and pid_alive(pid):
                try:
                    os.kill(pid, signal.SIGTERM)
                    print(f"  SIGTERM owner_pid={pid}")
                except OSError as e:
                    print(f"  skip kill {pid}: {e}")
            else:
                print(f"  skip kill: owner_pid={pid} not alive")

    for s in stale_sessions:
        # Never remove a session dir whose id is still live via another binding
        if s["session_id"] in live_sids:
            print(f"keep {s['path']} (session still live)")
            continue
        path = Path(s["path"])
        print(f"remove {path}")
        rm_tree(path)
        removed += 1

    for lease in stale_leases:
        if lease["session_id"] in live_sids:
            print(f"keep {lease['path']} (owner session still live)")
            continue
        path = Path(lease["path"])
        print(f"remove {path}")
        rm_tree(path)
        removed += 1

    print(f"done: removed {removed} stale path(s)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
