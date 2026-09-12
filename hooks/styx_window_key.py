"""Resolve Styx window binding key from Cursor env (shared by launcher, hooks, doctor).

Prefer numeric VSCODE_PID when present. Otherwise bind on the UUID basename of
VSCODE_IPC_HOOK_CLI (hash → positive Int for PlutoMCP cursor_host_pid).

CLI (for bash): prints ``<int>\\t<source>`` and exits 0, or exits 1 when neither
identity is available.
"""
from __future__ import annotations

import hashlib
import os
import sys
from pathlib import Path
from typing import Mapping


def ipc_hook_cli_token(hook_path: str | None = None) -> str | None:
    """Return the basename token of VSCODE_IPC_HOOK_CLI (strip ``.sock``), or None."""
    raw = hook_path if hook_path is not None else os.environ.get("VSCODE_IPC_HOOK_CLI")
    if not raw or not str(raw).strip():
        return None
    name = Path(str(raw)).name
    if name.endswith(".sock"):
        name = name[: -len(".sock")]
    return name or None


def hash_window_token(token: str) -> int:
    """Deterministic positive Int for PlutoMCP ``cursor_host_pid`` (fits signed 63-bit)."""
    digest = hashlib.sha256(token.encode("utf-8")).hexdigest()
    return int(digest[:15], 16)


def resolve_window_key(
    environ: Mapping[str, str] | None = None,
) -> tuple[int, str] | None:
    """Return ``(window_key_int, source)`` or None when identity is unavailable.

    Sources: ``VSCODE_PID`` (preferred) or ``VSCODE_IPC_HOOK_CLI``.
    """
    env = os.environ if environ is None else environ
    pid = env.get("VSCODE_PID", "")
    if pid.isdigit():
        return int(pid), "VSCODE_PID"
    token = ipc_hook_cli_token(env.get("VSCODE_IPC_HOOK_CLI"))
    if token:
        return hash_window_token(token), "VSCODE_IPC_HOOK_CLI"
    return None


def main(argv: list[str] | None = None) -> int:
    _ = argv
    resolved = resolve_window_key()
    if resolved is None:
        return 1
    key, source = resolved
    sys.stdout.write(f"{key}\t{source}\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
