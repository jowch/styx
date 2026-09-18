#!/usr/bin/env python3
"""styx-start — boot Pluto via the window control bridge.

Starts Pluto (idempotent), optionally opens a notebook, prints the welcome URL.
Agents Glass is driven by the /styx-start command after this script returns —
not by this CLI. Never opens the OS browser.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import urllib.error
from pathlib import Path
from typing import Any

_HOOKS = Path(__file__).resolve().parents[1] / "hooks"
if str(_HOOKS) not in sys.path:
    sys.path.insert(0, str(_HOOKS))

import pluto_lib  # noqa: E402

# Cold Pluto start can exceed hook defaults (CI uses ~180s).
START_TIMEOUT = float(os.environ.get("STYX_START_TIMEOUT", "180"))
CALL_TIMEOUT = float(os.environ.get("STYX_START_CALL_TIMEOUT", "30"))


def _die(msg: str, code: int = 1) -> None:
    print(f"styx-start: {msg}", file=sys.stderr)
    raise SystemExit(code)


def _pick_path(args: argparse.Namespace) -> str | None:
    if args.welcome:
        return None
    if args.path:
        return args.path
    default = Path("analysis.jl")
    if default.is_file():
        return str(default.resolve())
    return None


def _call(
    binding: dict[str, Any], name: str, arguments: dict[str, Any] | None = None, *, timeout: float
) -> dict[str, Any]:
    try:
        return pluto_lib.mcp_call(name, arguments, timeout=timeout, binding=binding)
    except urllib.error.URLError as e:
        _die(f"bridge call failed ({name}): {e}")
    except (TimeoutError, OSError, json.JSONDecodeError, KeyError, TypeError, ValueError) as e:
        _die(f"bridge call failed ({name}): {e}")


def _print_result(status: dict[str, Any], opened: dict[str, Any] | None) -> None:
    url = status.get("pluto_url")
    if not isinstance(url, str) or not url:
        port = status.get("pluto_port")
        url = f"http://127.0.0.1:{port}/" if port else None
    if not url:
        _die("Pluto started but pluto_url missing — check pluto_session_status")

    # Exact status host — do not rewrite localhost ↔ 127.0.0.1 (#25).
    if not url.endswith("/"):
        url = url + "/"

    print(f"welcome_url={url}")
    print(f"session_id={status.get('session_id', '')}")
    print(f"pluto_port={status.get('pluto_port', '')}")
    print(f"mcp_port={status.get('mcp_port', '')}")
    print(f"pluto={status.get('pluto', '')}")
    if opened:
        print(f"notebook_id={opened.get('notebook_id', '')}")
        print(f"path={opened.get('path', '')}")
        print(f"execution_allowed={opened.get('execution_allowed', False)}")
    print()
    print(
        "Command path: open Agents Glass to welcome_url (reuse/reveal), then "
        "Path B click the notebook on landing if one was opened — do not paste "
        "/edit?id=. Use /styx-reconnect if Glass auth/WS drops."
    )


def _emit_stale_check() -> None:
    """Run report-only stale check; print agent lines. Never blocks boot."""
    scripts = Path(__file__).resolve().parent
    lib = scripts / "lib"
    hooks = scripts.parent / "hooks"
    for p in (str(lib), str(hooks)):
        if p not in sys.path:
            sys.path.insert(0, p)
    try:
        import styx_stale  # noqa: WPS433
    except ImportError as e:
        print(f"stale_check=error")
        print(f"stale_check_error={e}")
        return
    try:
        inv = styx_stale.inventory()
    except OSError as e:
        print("stale_check=error")
        print(f"stale_check_error={e}")
        return
    count = inv["stale_count"]
    key = styx_stale.window_key()
    offered = styx_stale.offer_recorded(Path(inv["runtime_dir"]), key)
    print(f"stale_check={'stale' if count else 'clean'}")
    print(f"stale_count={count}")
    print(f"offer_cleanup={'yes' if count and not offered else 'no'}")
    print(f"offer_file={styx_stale.offer_path(Path(inv['runtime_dir']), key)}")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Start Pluto via Styx control bridge; print welcome URL."
    )
    parser.add_argument(
        "--path",
        "-p",
        help="Notebook path to open_notebook (server-side). Default: ./analysis.jl if present.",
    )
    parser.add_argument(
        "--welcome",
        action="store_true",
        help="Start Pluto only — do not open a notebook.",
    )
    parser.add_argument(
        "--run",
        action="store_true",
        help="Pass run_notebook=true to open_notebook (queue execution).",
    )
    parser.add_argument(
        "--session-id",
        help="Prefer this session_id (else STYX_SESSION_ID, else this window / sole healthy bridge).",
    )
    args = parser.parse_args(argv)

    if args.welcome and args.path:
        _die("use either --welcome or --path, not both")

    # Report-only; agent offers cleanup once when offer_cleanup=yes (see styx-start.md).
    _emit_stale_check()

    binding = pluto_lib.resolve_bridge_binding(session_id=args.session_id)
    if binding is None:
        healthy = pluto_lib.healthy_bindings()
        if len(healthy) > 1:
            _die(
                "multiple healthy Styx bridges; set --session-id or STYX_SESSION_ID, "
                "or run from the Cursor window that owns the session"
            )
        _die(
            "no healthy Styx control bridge — enable pluto MCP in this Cursor window "
            "(or set STYX_SESSION_ID to a live session)"
        )

    status = _call(binding, "start_pluto_session", timeout=START_TIMEOUT)
    if not isinstance(status, dict) or status.get("ok") is False:
        _die(f"start_pluto_session failed: {status}")

    # Refresh status for authoritative pluto_url / ports after start.
    refreshed = _call(binding, "pluto_session_status", timeout=CALL_TIMEOUT)
    if isinstance(refreshed, dict) and refreshed.get("ok") is not False:
        status = refreshed

    opened: dict[str, Any] | None = None
    path = _pick_path(args)
    if path is not None:
        if not os.path.isfile(path):
            _die(f"notebook not found: {path}")
        opened = _call(
            binding,
            "open_notebook",
            {"path": os.path.abspath(path), "run_notebook": bool(args.run)},
            timeout=CALL_TIMEOUT,
        )
        if not isinstance(opened, dict) or opened.get("ok") is False:
            err = opened.get("error") if isinstance(opened, dict) else opened
            _die(f"open_notebook failed: {err}")

    _print_result(status, opened)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
