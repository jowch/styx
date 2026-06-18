"""Shared helpers for Styx (Pluto ↔ Cursor) plugin hooks."""
from __future__ import annotations

import json
import os
import re
import sys
import urllib.error
import urllib.request
from typing import Any

RE_CELL_ID = re.compile(r"pluto-cell#([0-9a-f-]+)", re.I)
RE_NOTEBOOK_ID = re.compile(r"pluto-notebook#([0-9a-f-]+)", re.I)

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


def plugin_root() -> str:
    return os.environ.get(
        "CURSOR_PLUGIN_ROOT",
        os.path.abspath(os.path.join(os.path.dirname(__file__), "..")),
    )


def state_dir() -> str:
    path = os.path.join(plugin_root(), "hooks", "state")
    os.makedirs(path, exist_ok=True)
    return path


def reads_path() -> str:
    return os.path.join(state_dir(), "pluto-reads.json")


def parse_dom_path(dom_path: str) -> dict[str, Any]:
    if not dom_path or not isinstance(dom_path, str):
        return {"ok": False, "reason": "invalid_dom_path"}
    cell = RE_CELL_ID.search(dom_path)
    if not cell:
        return {"ok": False, "reason": "no_pluto_cell_in_dom_path"}
    notebook = RE_NOTEBOOK_ID.search(dom_path)
    return {
        "ok": True,
        "cell_id": cell.group(1),
        "notebook_id": notebook.group(1) if notebook else None,
    }


def parse_prompt_text(text: str) -> dict[str, Any]:
    if not text:
        return {"ok": False, "reason": "empty_prompt"}
    dom_path = None
    for line in text.splitlines():
        if line.strip().lower().startswith("dom_path:"):
            dom_path = line.split(":", 1)[1].strip()
            break
    if dom_path:
        parsed = parse_dom_path(dom_path)
        if parsed.get("ok"):
            return {**parsed, "dom_path": dom_path}
    cell = RE_CELL_ID.search(text)
    if not cell:
        return {"ok": False, "reason": "no_pluto_cell_in_prompt"}
    notebook = RE_NOTEBOOK_ID.search(text)
    return {
        "ok": True,
        "cell_id": cell.group(1),
        "notebook_id": notebook.group(1) if notebook else None,
        "dom_path": dom_path,
    }


def load_reads() -> list[dict[str, Any]]:
    path = reads_path()
    if not os.path.exists(path):
        return []
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def save_reads(reads: list[dict[str, Any]]) -> None:
    with open(reads_path(), "w", encoding="utf-8") as f:
        json.dump(reads, f, indent=2)


def clear_reads() -> None:
    save_reads([])


def record_read(notebook_id: str | None, cell_id: str | None) -> None:
    if not notebook_id or not cell_id:
        return
    reads = load_reads()
    reads.append({"notebook_id": notebook_id, "cell_id": cell_id})
    save_reads(reads)


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
    """POST tools/call to the PlutoMCP HTTP bridge."""
    port = int(os.environ.get("PLUTOMCP_MCP_PORT", "2346"))
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
        headers={"Content-Type": "application/json"},
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
        raise PendingRunError("Pluto MCP bridge not healthy")
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
    port = port or int(os.environ.get("PLUTOMCP_MCP_PORT", "2346"))
    url = f"http://127.0.0.1:{port}/health"
    try:
        with urllib.request.urlopen(url, timeout=2) as resp:
            return resp.status == 200
    except (urllib.error.URLError, TimeoutError, OSError):
        return False


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
