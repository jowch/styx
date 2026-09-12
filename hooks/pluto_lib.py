"""Shared helpers for Styx (Pluto ↔ Cursor) plugin hooks."""
from __future__ import annotations

import json
import os
import sys
import time
import urllib.error
import urllib.request
from typing import Any

from styx_window_key import resolve_window_key

EDIT_TOOLS_PRE = {
    "MCP:edit_cell",
    "MCP:edit_cells",
    "MCP:add_cell",
    "MCP:delete_cell",
    "MCP:move_cell",
    "edit_cell",
    "edit_cells",
    "add_cell",
    "delete_cell",
    "move_cell",
}

READ_TOOLS = {
    "MCP:read_cell",
    "MCP:read_notebook_code",
    "read_cell",
    "read_notebook_code",
}

STYX_SESSION_HEADER = "X-Styx-Session-ID"


def plugin_root() -> str:
    return os.environ.get(
        "CURSOR_PLUGIN_ROOT",
        os.path.abspath(os.path.join(os.path.dirname(__file__), "..")),
    )


def runtime_dir() -> str:
    env = os.environ.get("STYX_RUNTIME_DIR")
    if env:
        return env
    uid = os.environ.get("UID") or str(os.getuid())
    xdg = os.environ.get("XDG_RUNTIME_DIR")
    if xdg:
        return os.path.join(xdg, f"styx-{uid}")
    tmp = os.environ.get("TMPDIR") or "/tmp"
    return os.path.join(tmp, f"styx-{uid}")


def _window_key() -> str | None:
    """Numeric window binding key (VSCODE_PID or hashed VSCODE_IPC_HOOK_CLI)."""
    resolved = resolve_window_key()
    if resolved is None:
        return None
    return str(resolved[0])


def load_binding() -> dict[str, Any] | None:
    key = _window_key()
    if not key:
        return None
    path = os.path.join(runtime_dir(), "windows", f"{key}.json")
    if not os.path.isfile(path):
        return None
    try:
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
    except (OSError, json.JSONDecodeError):
        return None
    if not isinstance(data, dict):
        return None
    if data.get("schema_version") != 1:
        return None
    if not data.get("session_id") or not data.get("mcp_port"):
        return None
    return data


def _health_matches(binding: dict[str, Any], timeout: float = 2) -> bool:
    port = binding.get("mcp_port")
    sid = binding.get("session_id")
    if not isinstance(port, int) or not isinstance(sid, str):
        return False
    url = f"http://127.0.0.1:{port}/health"
    try:
        with urllib.request.urlopen(url, timeout=timeout) as resp:
            if resp.status != 200:
                return False
            body = resp.read().decode("utf-8", errors="replace").strip()
            if not body.startswith("{"):
                return False
            health = json.loads(body)
            return isinstance(health, dict) and health.get("session_id") == sid
    except (
        urllib.error.URLError,
        TimeoutError,
        OSError,
        json.JSONDecodeError,
        ValueError,
    ):
        return False


def verified_binding(timeout: float = 2) -> dict[str, Any] | None:
    binding = load_binding()
    if binding is None:
        return None
    if not _health_matches(binding, timeout=timeout):
        return None
    return binding


def reads_path(binding: dict[str, Any] | None = None) -> str | None:
    b = binding if binding is not None else verified_binding()
    if b is None:
        return None
    sid = b.get("session_id")
    if not isinstance(sid, str):
        return None
    path = os.path.join(runtime_dir(), "sessions", sid, "reads.json")
    os.makedirs(os.path.dirname(path), exist_ok=True)
    return path


def _atomic_write_json(path: str, obj: Any) -> None:
    directory = os.path.dirname(path)
    os.makedirs(directory, exist_ok=True)
    tmp = f"{path}.{os.getpid()}.{time.time_ns()}.tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(obj, f, indent=2)
    os.replace(tmp, path)


def _with_reads_lock(path: str, fn: Any) -> Any:
    """Serialize read-modify-write with an atomic lock directory."""
    lock_dir = path + ".lock"
    deadline = time.time() + 5.0
    while True:
        try:
            os.mkdir(lock_dir)
            break
        except FileExistsError:
            if time.time() > deadline:
                # ponytail: stale lock takeover after timeout; fine for local hooks
                try:
                    os.rmdir(lock_dir)
                except OSError:
                    pass
                continue
            time.sleep(0.02)
    try:
        return fn()
    finally:
        try:
            os.rmdir(lock_dir)
        except OSError:
            pass


def load_reads() -> list[dict[str, Any]]:
    path = reads_path()
    if path is None or not os.path.exists(path):
        return []

    def _load() -> list[dict[str, Any]]:
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
        return data if isinstance(data, list) else []

    try:
        return _with_reads_lock(path, _load)
    except (OSError, json.JSONDecodeError):
        return []


def save_reads(reads: list[dict[str, Any]]) -> None:
    path = reads_path()
    if path is None:
        return

    def _save() -> None:
        _atomic_write_json(path, reads)

    _with_reads_lock(path, _save)


def clear_reads() -> None:
    # Bound sessions use a fresh session_id directory; nothing global to clear.
    path = reads_path()
    if path is None:
        return
    save_reads([])


def record_read(notebook_id: str | None, cell_id: str | None) -> None:
    if not notebook_id or not cell_id:
        return
    path = reads_path()
    if path is None:
        return

    def _record() -> None:
        reads: list[dict[str, Any]] = []
        if os.path.exists(path):
            try:
                with open(path, encoding="utf-8") as f:
                    data = json.load(f)
                if isinstance(data, list):
                    reads = data
            except (OSError, json.JSONDecodeError):
                reads = []
        reads.append({"notebook_id": notebook_id, "cell_id": cell_id})
        _atomic_write_json(path, reads)

    _with_reads_lock(path, _record)


def has_read(notebook_id: str | None, cell_id: str | None) -> bool:
    if not notebook_id:
        return False
    for r in load_reads():
        if r.get("notebook_id") != notebook_id:
            continue
        rid = r.get("cell_id")
        if rid == "*" or (cell_id and rid == cell_id):
            return True
    return False


def edit_target_cell_ids(tool_name: str, inp: dict[str, Any]) -> list[str]:
    """Cell ids targeted by a write tool (edit_cells uses cells[], not top-level cell_id)."""
    bare = tool_name.removeprefix("MCP:")
    if bare == "edit_cells":
        cells = inp.get("cells") or []
        return [c["cell_id"] for c in cells if isinstance(c, dict) and c.get("cell_id")]
    cid = inp.get("cell_id")
    return [cid] if cid else []


def write_allowed(tool_name: str, inp: dict[str, Any]) -> bool:
    """True when read receipts cover this write (read-before-edit guard)."""
    notebook_id = inp.get("notebook_id")
    if not notebook_id:
        return False
    bare = tool_name.removeprefix("MCP:")
    if bare == "add_cell":
        return any(r.get("notebook_id") == notebook_id for r in load_reads())
    if bare == "edit_cells":
        ids = edit_target_cell_ids(tool_name, inp)
        if not ids:
            return False
        return all(has_read(notebook_id, cid) for cid in ids)
    ids = edit_target_cell_ids(tool_name, inp)
    if len(ids) == 1:
        return has_read(notebook_id, ids[0])
    return has_read(notebook_id, inp.get("cell_id"))


class PendingRunError(Exception):
    """MCP pending_run check failed (bridge down, timeout, or malformed response)."""


def mcp_call(
    name: str, arguments: dict[str, Any] | None = None, *, timeout: float = 5
) -> dict[str, Any]:
    """POST tools/call to this window's verified PlutoMCP control bridge."""
    binding = verified_binding(timeout=min(timeout, 2))
    if binding is None:
        raise urllib.error.URLError("styx_binding_unavailable")
    port = int(binding["mcp_port"])
    sid = str(binding["session_id"])
    body = json.dumps(
        {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tools/call",
            "params": {"name": name, "arguments": arguments or {}},
        }
    ).encode("utf-8")
    req = urllib.request.Request(
        f"http://127.0.0.1:{port}/call",
        data=body,
        headers={
            "Content-Type": "application/json",
            STYX_SESSION_HEADER: sid,
        },
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        payload = json.load(resp)
    result = payload.get("result") or {}
    text = (result.get("content") or [{}])[0].get("text") or "{}"
    parsed = json.loads(text)
    if result.get("isError"):
        return {"ok": False, "error": parsed}
    return parsed


def pending_run_notebooks() -> list[dict[str, Any]]:
    """Return notebooks with non-empty pending_run from the live bridge."""
    if not mcp_health_ok():
        # Bound deferred: control bridge may be up with Pluto stopped, or missing entirely.
        return []
    out: list[dict[str, Any]] = []
    try:
        notebooks = mcp_call("list_notebooks", timeout=3)
        if not isinstance(notebooks, list):
            raise PendingRunError("list_notebooks returned unexpected payload")
        for nb in notebooks:
            nb_id = nb.get("notebook_id")
            if not nb_id:
                continue
            proj = mcp_call("read_notebook_code", {"notebook_id": nb_id}, timeout=4)
            pending = proj.get("pending_run") or []
            if pending:
                out.append(
                    {
                        "notebook_id": nb_id,
                        "path": proj.get("path"),
                        "pending_run": pending,
                    }
                )
    except PendingRunError:
        raise
    except (
        urllib.error.URLError,
        TimeoutError,
        OSError,
        json.JSONDecodeError,
        KeyError,
        IndexError,
        TypeError,
    ) as e:
        raise PendingRunError(f"pending_run check failed: {e}") from e
    return out


def mcp_health_ok(port: int | None = None) -> bool:
    binding = verified_binding()
    if binding is None:
        return False
    if port is not None and int(binding["mcp_port"]) != int(port):
        return False
    return True


def pluto_session_running() -> bool:
    """True when the HTTP bridge is up and Pluto reports running."""
    if not mcp_health_ok():
        return False
    try:
        status = mcp_call("pluto_session_status", timeout=3)
    except (
        urllib.error.URLError,
        TimeoutError,
        OSError,
        json.JSONDecodeError,
        KeyError,
        IndexError,
        TypeError,
    ):
        return False
    return isinstance(status, dict) and status.get("pluto") == "running"


def hook_input() -> dict[str, Any]:
    return json.load(sys.stdin)


def tool_input(payload: dict[str, Any]) -> dict[str, Any]:
    raw = payload.get("tool_input") or {}
    if isinstance(raw, str):
        try:
            return json.loads(raw)
        except json.JSONDecodeError:
            return {}
    return raw if isinstance(raw, dict) else {}


def deny_edit(agent_message: str) -> None:
    print(json.dumps({"permission": "deny", "agent_message": agent_message}))


def allow() -> None:
    print(json.dumps({"permission": "allow"}))
