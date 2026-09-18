#!/usr/bin/env python3
"""Shared Styx-managed stale-state helpers (bindings / sessions / leases only).

Never treats an unmanaged user Pluto (no Styx window binding) as debris.
"""
from __future__ import annotations

import json
import os
import subprocess
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


OFFER_SCHEMA = 1
OFFER_NAME = "cleanup-offer.json"


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
    """True only when loopback /health JSON nonce matches this Styx session_id."""
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


def window_key() -> str | None:
    """Numeric Cursor window key, or None when identity is unavailable."""
    env = os.environ.get("STYX_WINDOW_KEY")
    if env and env.isdigit():
        return env
    try:
        from styx_window_key import resolve_window_key  # type: ignore

        resolved = resolve_window_key()
        if resolved is None:
            return None
        return str(resolved[0])
    except Exception:
        pass
    # Fall back to hooks helper via subprocess when not on PYTHONPATH
    root = Path(__file__).resolve().parents[2]
    py = root / "hooks" / "styx_window_key.py"
    if not py.is_file():
        return None
    try:
        out = subprocess.check_output(["python3", str(py)], text=True, stderr=subprocess.DEVNULL)
    except (OSError, subprocess.CalledProcessError):
        return None
    key = out.split("\t", 1)[0].strip()
    return key if key.isdigit() else None


def offer_path(root: Path | None = None, key: str | None = None) -> Path:
    """Per-window offer bit: windows/<key>.cleanup-offer.json (Cursor window scope)."""
    root = root or runtime_dir()
    key = key if key is not None else window_key()
    if key:
        return root / "windows" / f"{key}.{OFFER_NAME}"
    return root / OFFER_NAME


def offer_recorded(root: Path | None = None, key: str | None = None) -> bool:
    path = offer_path(root, key)
    data = read_json(path)
    return isinstance(data, dict) and data.get("schema_version") == OFFER_SCHEMA


def mark_offer(
    *,
    stale_summary: str,
    stale_count: int,
    root: Path | None = None,
    key: str | None = None,
) -> Path:
    root = root or runtime_dir()
    path = offer_path(root, key)
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "schema_version": OFFER_SCHEMA,
        "offered_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "stale_count": stale_count,
        "summary": stale_summary,
        "window_key": key if key is not None else window_key(),
    }
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    tmp.replace(path)
    return path


def is_styx_binding(data: dict[str, Any] | None) -> bool:
    """Styx-managed window binding only (schema_version 1 + session_id + mcp_port)."""
    if not isinstance(data, dict):
        return False
    if data.get("schema_version") != 1:
        return False
    return bool(data.get("session_id")) and isinstance(data.get("mcp_port"), int)


def classify_binding(path: Path) -> dict[str, Any] | None:
    data = read_json(path)
    if not is_styx_binding(data):
        # Not a Styx binding — ignore (never treat as Styx debris)
        return None
    assert data is not None
    sid = data["session_id"]
    port = data["mcp_port"]
    owner = data.get("owner_pid")
    live = health_matches(port, sid)
    return {
        "kind": "window",
        "path": str(path),
        "session_id": sid if isinstance(sid, str) else None,
        "mcp_port": port,
        "pluto_port": data.get("pluto_port"),
        "owner_pid": owner if isinstance(owner, int) else None,
        "owner_alive": pid_alive(owner),
        "health_ok": live,
        "stale": not live,
        "styx_managed": True,
    }


def classify_session_dir(path: Path) -> dict[str, Any]:
    owner = read_json(path / "owner.json") or {}
    sid = owner.get("session_id") or path.name
    port = owner.get("mcp_port")
    if isinstance(port, int) and isinstance(sid, str):
        live = health_matches(port, sid)
    else:
        # Session crumb under Styx runtime with no live health → stale Styx crumb
        live = False
    glass = path / "glass-views.json"
    return {
        "kind": "session",
        "path": str(path),
        "session_id": sid if isinstance(sid, str) else path.name,
        "mcp_port": port if isinstance(port, int) else None,
        "health_ok": live,
        "stale": not live,
        "has_glass_views": glass.is_file(),
        "styx_managed": True,
    }


def classify_lease(path: Path) -> dict[str, Any] | None:
    owner = read_json(path / "owner.json")
    if not isinstance(owner, dict) or not owner.get("session_id"):
        # Lease dirs are Styx-only; missing owner → stale crumb under our runtime
        return {
            "kind": "lease",
            "path": str(path),
            "session_id": None,
            "mcp_port": None,
            "health_ok": False,
            "stale": True,
            "styx_managed": True,
        }
    sid = owner.get("session_id")
    port = owner.get("mcp_port")
    live = health_matches(port, sid)
    return {
        "kind": "lease",
        "path": str(path),
        "session_id": sid if isinstance(sid, str) else None,
        "mcp_port": port if isinstance(port, int) else None,
        "health_ok": live,
        "stale": not live,
        "styx_managed": True,
    }


def inventory(root: Path | None = None) -> dict[str, Any]:
    """Scan only `$STYX_RUNTIME_DIR` Styx artifacts — never port-scan user Pluto."""
    root = root or runtime_dir()
    bindings: list[dict[str, Any]] = []
    sessions: list[dict[str, Any]] = []
    leases: list[dict[str, Any]] = []

    windows_dir = root / "windows"
    if windows_dir.is_dir():
        for path in sorted(windows_dir.glob("*.json")):
            if path.name.endswith(f".{OFFER_NAME}") or path.name == OFFER_NAME:
                continue
            item = classify_binding(path)
            if item is not None:
                bindings.append(item)

    sessions_dir = root / "sessions"
    if sessions_dir.is_dir():
        for path in sorted(p for p in sessions_dir.iterdir() if p.is_dir()):
            sessions.append(classify_session_dir(path))

    notebooks_dir = root / "notebooks"
    if notebooks_dir.is_dir():
        for path in sorted(p for p in notebooks_dir.iterdir() if p.is_dir()):
            item = classify_lease(path)
            if item is not None:
                leases.append(item)

    live_sids = {b["session_id"] for b in bindings if b["health_ok"] and b["session_id"]}
    live_sids |= {s["session_id"] for s in sessions if s["health_ok"] and s["session_id"]}

    stale_bindings = [b for b in bindings if b["stale"]]
    stale_sessions = [s for s in sessions if s["stale"] and s["session_id"] not in live_sids]
    stale_leases = [lease for lease in leases if lease["stale"] and lease["session_id"] not in live_sids]

    return {
        "runtime_dir": str(root),
        "bindings": bindings,
        "sessions": sessions,
        "leases": leases,
        "stale_bindings": stale_bindings,
        "stale_sessions": stale_sessions,
        "stale_leases": stale_leases,
        "live_session_ids": sorted(live_sids),
        "stale_count": len(stale_bindings) + len(stale_sessions) + len(stale_leases),
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
