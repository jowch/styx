"""Shared helpers for Styx (Pluto ↔ Cursor) plugin hooks."""
from __future__ import annotations

import json
import os
import re
import sys
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone
from typing import Any
from urllib.parse import parse_qs, urlparse

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

LANDING_KEY = "_landing"
GLASS_VIEW_SCHEMA = 1
GLASS_BROWSER_TOOLS = {
    "browser_navigate",
    "browser_snapshot",
    "browser_lock",
    "browser_tabs",
}
_GLASS_TOOL_NAMES = GLASS_BROWSER_TOOLS | {f"MCP:{t}" for t in GLASS_BROWSER_TOOLS}
_UUID_RE = re.compile(
    r"[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}"
)
_BROWSER_VIEW_ID_RE = re.compile(r"Browser View ID:\s*([A-Za-z0-9_-]+)", re.I)
# Live browser_tabs list: `Open tabs:\n[0] "name" - http://… (viewId: c28e15)`
_PROSE_TAB_RE = re.compile(
    r"(https?://[^\s)]+)\s*\(viewId:\s*([A-Za-z0-9_-]+)\)",
    re.I,
)
_REMOTE_SSH_CONTEXT = (
    "Remote SSH workspace. This Cursor window owns its own Styx/PlutoMCP/Pluto on "
    "the SSH host (local XOR remote). MCP uses host pluto_url/pluto_port. Before "
    "Agents Glass this session: ask the user for the Cursor Ports forwarded/local "
    "port for that remote Pluto port; open http://127.0.0.1:<forwarded>/ — do not "
    "invent remaps or probe fixed :1234/:2346. See pluto-session "
    "glass-navigation.md / remote-ssh.md."
)


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
    if not isinstance(sid, str) or not _UUID_RE.fullmatch(sid):
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


def glass_views_path(binding: dict[str, Any] | None = None) -> str | None:
    """Path to this Pluto session's glass-views.json (does not create the file)."""
    b = binding if binding is not None else load_binding()
    if b is None:
        return None
    sid = b.get("session_id")
    if not isinstance(sid, str) or not _UUID_RE.fullmatch(sid):
        return None
    path = os.path.join(runtime_dir(), "sessions", sid, "glass-views.json")
    os.makedirs(os.path.dirname(path), exist_ok=True)
    return path


def _empty_glass_views(binding: dict[str, Any]) -> dict[str, Any]:
    pluto_url = binding.get("pluto_url")
    if not isinstance(pluto_url, str) or not pluto_url:
        port = binding.get("pluto_port")
        pluto_url = f"http://127.0.0.1:{port}" if isinstance(port, int) else ""
    return {
        "schema_version": GLASS_VIEW_SCHEMA,
        "session_id": binding.get("session_id"),
        "pluto_url": pluto_url,
        "entries": {},
    }


def _iso_now() -> str:
    return (
        datetime.now(timezone.utc)
        .replace(microsecond=0)
        .isoformat()
        .replace("+00:00", "Z")
    )


def _origin_tuple(url: str) -> tuple[str, str, int] | None:
    try:
        parsed = urlparse(url)
    except ValueError:
        return None
    if parsed.scheme not in ("http", "https") or not parsed.hostname:
        return None
    host = parsed.hostname.lower()
    if host == "localhost":
        host = "127.0.0.1"
    port = parsed.port or (443 if parsed.scheme == "https" else 80)
    return (parsed.scheme, host, port)


def origin_url(url: str) -> str | None:
    origin = _origin_tuple(url)
    if origin is None:
        return None
    scheme, host, port = origin
    return f"{scheme}://{host}:{port}"


def notebook_key_from_url(url: str | None) -> str | None:
    """Return `_landing` or a notebook UUID; None if URL is unusable."""
    if not isinstance(url, str) or not url.strip():
        return None
    raw = url.strip()
    try:
        parsed = urlparse(raw)
    except ValueError:
        return None
    if parsed.scheme not in ("http", "https"):
        return None
    qs = parse_qs(parsed.query)
    nid = (qs.get("id") or [None])[0]
    if isinstance(nid, str) and _UUID_RE.fullmatch(nid):
        return nid
    return LANDING_KEY


def looks_like_pluto_page(url: str | None) -> bool:
    if not isinstance(url, str) or not url.strip():
        return False
    try:
        parsed = urlparse(url.strip())
    except ValueError:
        return False
    path = parsed.path or "/"
    qs = parse_qs(parsed.query)
    nid = (qs.get("id") or [None])[0]
    if isinstance(nid, str) and _UUID_RE.fullmatch(nid):
        return True
    if path.rstrip("/") in ("",) or path in ("/", "/index.html"):
        return True
    return path == "/edit" or path.startswith("/edit/") or path.startswith("/edit?")


def _parse_jsonish(raw: Any) -> Any:
    if raw is None:
        return None
    if isinstance(raw, (dict, list)):
        return raw
    if not isinstance(raw, str):
        return None
    text = raw.strip()
    if not text:
        return None
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        return text


def result_blob(payload: dict[str, Any]) -> Any:
    """Prefer afterMCPExecution result_json, then postToolUse tool_output."""
    for key in ("result_json", "tool_output", "result"):
        if key in payload and payload.get(key) not in (None, ""):
            return _parse_jsonish(payload.get(key))
    return None


# Cursor ide-browser returns these as content text with isError:false (live hook logs).
_GLASS_FAILURE_LINE_PREFIXES = (
    "browser view not found",
    "no browser tab available",
)


def _mcp_content_texts(result: Any) -> list[str]:
    """Text from an MCP tool result (`content[].text` or a bare string)."""
    parsed = _parse_jsonish(result)
    if isinstance(parsed, str):
        return [parsed]
    if not isinstance(parsed, dict):
        return []
    content = parsed.get("content")
    if not isinstance(content, list):
        return []
    texts: list[str] = []
    for item in content:
        if isinstance(item, dict) and isinstance(item.get("text"), str):
            texts.append(item["text"])
    return texts


def _content_looks_failed(result: Any) -> bool:
    """True when MCP content text is a known Glass failure, even if isError is false."""
    for blob in _mcp_content_texts(result):
        for line in blob.splitlines():
            low = line.strip().lower()
            if any(low.startswith(prefix) for prefix in _GLASS_FAILURE_LINE_PREFIXES):
                return True
    return False


def _tool_failed(payload: dict[str, Any], result: Any) -> bool:
    if payload.get("isError") is True or payload.get("is_error") is True:
        return True
    if isinstance(result, dict) and result.get("isError") is True:
        return True
    if _content_looks_failed(result):
        return True
    return False


def _is_ide_browser_tool(payload: dict[str, Any], tool_name: str) -> bool:
    server = str(payload.get("mcp_server_name") or "")
    if "browse-browser" in server and "ide-browser" not in server:
        return False
    return tool_name.removeprefix("MCP:") in GLASS_BROWSER_TOOLS or tool_name in _GLASS_TOOL_NAMES


def is_forbidden_new_tab(tool_name: str, inp: dict[str, Any]) -> bool:
    """True for newTab:true, or any browser_tabs action other than list (including missing action)."""
    if inp.get("newTab") is True:
        return True
    if str(inp.get("newTab")).lower() == "true":
        return True
    bare = tool_name.removeprefix("MCP:")
    if bare == "browser_tabs":
        action = inp.get("action")
        if action in ("new", "tabs_new"):
            return True
        if action != "list":
            return True
    return False


def _walk_view_ids_and_urls(obj: Any, view_ids: list[str], urls: list[str], depth: int = 0) -> None:
    if depth > 12 or obj is None:
        return
    if isinstance(obj, dict):
        for key, value in obj.items():
            if key in {"viewId", "view_id", "browserViewId"} and isinstance(value, str):
                token = value.strip()
                if token:
                    view_ids.append(token)
            if key in {"url", "pageUrl", "page_url", "currentUrl"} and isinstance(value, str):
                if "://" in value:
                    urls.append(value.strip())
            _walk_view_ids_and_urls(value, view_ids, urls, depth + 1)
        return
    if isinstance(obj, list):
        for item in obj:
            _walk_view_ids_and_urls(item, view_ids, urls, depth + 1)
        return
    if isinstance(obj, str):
        for match in _BROWSER_VIEW_ID_RE.finditer(obj):
            view_ids.append(match.group(1).rstrip(".,);"))
        text = obj.strip()
        if text[:1] in "[{" and len(text) < 1_000_000:
            try:
                nested = json.loads(text)
            except json.JSONDecodeError:
                nested = None
            if nested is not None:
                _walk_view_ids_and_urls(nested, view_ids, urls, depth + 1)


def parse_view_id(result: Any, inp: dict[str, Any] | None = None) -> str | None:
    """Spike parser: JSON metadata viewId, `Browser View ID:` text, else tool_input.viewId."""
    view_ids: list[str] = []
    urls: list[str] = []
    _walk_view_ids_and_urls(result, view_ids, urls)
    if view_ids:
        return view_ids[0]
    if isinstance(inp, dict):
        raw = inp.get("viewId") or inp.get("view_id")
        if isinstance(raw, str) and raw.strip():
            return raw.strip()
    return None


def parse_result_url(result: Any, inp: dict[str, Any] | None = None) -> str | None:
    """Prefer URL from the tool result; fall back to tool_input.url."""
    urls: list[str] = []
    view_ids: list[str] = []
    _walk_view_ids_and_urls(result, view_ids, urls)
    if urls:
        return urls[0]
    if isinstance(inp, dict):
        raw = inp.get("url")
        if isinstance(raw, str) and "://" in raw:
            return raw.strip()
    return None


def _prose_tab_pairs(text: str) -> list[tuple[str, str]]:
    """Parse `Open tabs:\\n[0] title - url (viewId: hex)` lines."""
    pairs: list[tuple[str, str]] = []
    for url, vid in _PROSE_TAB_RE.findall(text):
        pairs.append((url.rstrip(".,);"), vid.strip()))
    return pairs


def iter_tab_matches(result: Any) -> list[tuple[str, str]]:
    """(url, viewId) pairs from a browser_tabs list payload (JSON or prose)."""
    found: list[tuple[str, str]] = []

    def _walk(obj: Any, depth: int = 0) -> None:
        if depth > 12 or obj is None:
            return
        if isinstance(obj, dict):
            url = obj.get("url") or obj.get("pageUrl")
            vid = obj.get("viewId") or obj.get("view_id")
            if isinstance(url, str) and isinstance(vid, str) and "://" in url and vid.strip():
                found.append((url.strip(), vid.strip()))
            for value in obj.values():
                _walk(value, depth + 1)
            return
        if isinstance(obj, list):
            for item in obj:
                _walk(item, depth + 1)
            return
        if isinstance(obj, str):
            text = obj.strip()
            if text[:1] in "[{":
                try:
                    _walk(json.loads(text), depth + 1)
                    return
                except json.JSONDecodeError:
                    pass
            found.extend(_prose_tab_pairs(text))

    _walk(result)
    return found


def _allowed_origins(binding: dict[str, Any], views: dict[str, Any] | None) -> set[tuple[str, str, int]]:
    origins: set[tuple[str, str, int]] = set()
    candidates: list[Any] = [
        binding.get("pluto_url"),
        binding.get("client_url"),
    ]
    port = binding.get("pluto_port")
    if isinstance(port, int):
        candidates.extend(
            (f"http://127.0.0.1:{port}", f"http://localhost:{port}")
        )
    if isinstance(views, dict):
        candidates.append(views.get("pluto_url"))
        entries = views.get("entries") or {}
        if isinstance(entries, dict):
            for entry in entries.values():
                if isinstance(entry, dict):
                    candidates.append(entry.get("url"))
    for raw in candidates:
        if isinstance(raw, str):
            origin = _origin_tuple(raw)
            if origin is not None:
                origins.add(origin)
    return origins


def url_is_session_pluto(
    url: str | None,
    binding: dict[str, Any],
    views: dict[str, Any] | None = None,
) -> bool:
    if not isinstance(url, str) or not looks_like_pluto_page(url):
        return False
    origin = _origin_tuple(url)
    if origin is None:
        return False
    if origin in _allowed_origins(binding, views):
        return True
    # Remote SSH first touch: Glass uses a forwarded loopback port, not host pluto_url.
    # Local sessions already have pluto_url/pluto_port in the binding — do not treat
    # every 127.0.0.1 tab as this session's Pluto.
    if os.environ.get("CURSOR_CODE_REMOTE") != "true":
        return False
    _scheme, host, _port = origin
    return host == "127.0.0.1"


def load_glass_views(binding: dict[str, Any] | None = None) -> dict[str, Any] | None:
    b = binding if binding is not None else load_binding()
    if b is None:
        return None
    path = glass_views_path(b)
    if path is None:
        return None
    empty = _empty_glass_views(b)
    if not os.path.isfile(path):
        return empty

    def _load() -> dict[str, Any]:
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
        if not isinstance(data, dict) or data.get("schema_version") != GLASS_VIEW_SCHEMA:
            return empty
        if data.get("session_id") != b.get("session_id"):
            return empty
        entries = data.get("entries")
        if not isinstance(entries, dict):
            data = dict(data)
            data["entries"] = {}
        return data

    try:
        return _with_reads_lock(path, _load)
    except (OSError, json.JSONDecodeError):
        return empty


def upsert_glass_view(
    key: str,
    view_id: str,
    url: str,
    *,
    binding: dict[str, Any] | None = None,
    updated_at: str | None = None,
) -> None:
    if not key or not view_id or not url:
        return
    b = binding if binding is not None else verified_binding()
    if b is None:
        return
    path = glass_views_path(b)
    if path is None:
        return
    stamp = updated_at or _iso_now()

    def _upsert() -> None:
        data = _empty_glass_views(b)
        if os.path.isfile(path):
            try:
                with open(path, encoding="utf-8") as f:
                    loaded = json.load(f)
                if (
                    isinstance(loaded, dict)
                    and loaded.get("schema_version") == GLASS_VIEW_SCHEMA
                    and loaded.get("session_id") == b.get("session_id")
                ):
                    data = loaded
                    if not isinstance(data.get("entries"), dict):
                        data["entries"] = {}
            except (OSError, json.JSONDecodeError):
                pass
        if not data.get("pluto_url"):
            data["pluto_url"] = origin_url(url) or url
        entries = data.setdefault("entries", {})
        entries[key] = {"viewId": view_id, "url": url, "updated_at": stamp}
        _atomic_write_json(path, data)

    _with_reads_lock(path, _upsert)


def drop_glass_view(key: str, *, binding: dict[str, Any] | None = None) -> None:
    """Remove one notebook/_landing entry (stale viewId). Never wipes the file."""
    b = binding if binding is not None else load_binding()
    if b is None or not key:
        return
    path = glass_views_path(b)
    if path is None or not os.path.isfile(path):
        return

    def _drop() -> None:
        try:
            with open(path, encoding="utf-8") as f:
                data = json.load(f)
        except (OSError, json.JSONDecodeError):
            return
        if not isinstance(data, dict):
            return
        entries = data.get("entries")
        if not isinstance(entries, dict) or key not in entries:
            return
        del entries[key]
        _atomic_write_json(path, data)

    _with_reads_lock(path, _drop)


def glass_views_additional_context(binding: dict[str, Any] | None = None) -> str | None:
    b = binding if binding is not None else load_binding()
    if b is None:
        return None
    views = load_glass_views(b)
    if not views:
        return None
    entries = views.get("entries") or {}
    if not isinstance(entries, dict) or not entries:
        return None
    sid = views.get("session_id") or b.get("session_id")
    parts: list[str] = []
    keys = []
    if LANDING_KEY in entries:
        keys.append(LANDING_KEY)
    keys.extend(sorted(k for k in entries if k != LANDING_KEY))
    for key in keys:
        entry = entries.get(key)
        if not isinstance(entry, dict):
            continue
        vid = entry.get("viewId")
        url = entry.get("url")
        if not vid or not url:
            continue
        parts.append(f"{key} → viewId `{vid}` (url {url})")
    if not parts:
        return None
    path = glass_views_path(b)
    path_bit = f" (file `{path}`)" if path else ""
    return (
        f"Known Glass views for session {sid}{path_bit}: "
        + "; ".join(parts)
        + ". Cursor does not inject this block into the model — Read that file before Glass work. "
        "Reuse with `browser_navigate({ url, viewId })` (omit `position`). "
        "Empty `browser_tabs` list is unreliable. Never `newTab` / `action: \"new\"`. "
        "On a stale viewId, delete that key from `entries` in the JSON (do not wipe the file) "
        "and hard-stop — never open a new tab."
    )


def session_start_payload() -> dict[str, Any]:
    """sessionStart JSON. Does not wipe glass-views.json."""
    chunks: list[str] = []
    if os.environ.get("CURSOR_CODE_REMOTE") == "true":
        chunks.append(_REMOTE_SSH_CONTEXT)
    glass = glass_views_additional_context()
    if glass:
        chunks.append(glass)
    if not chunks:
        return {}
    return {"additional_context": "\n\n".join(chunks)}


def _record_one_view(
    *,
    binding: dict[str, Any],
    views: dict[str, Any],
    url: str,
    view_id: str,
) -> None:
    if not url_is_session_pluto(url, binding, views):
        return
    key = notebook_key_from_url(url)
    if not key:
        return
    upsert_glass_view(key, view_id, url, binding=binding)


def record_glass_from_hook(payload: dict[str, Any]) -> None:
    """Write glass-views.json from afterMCPExecution / postToolUse. Fail quiet."""
    tool_name = str(payload.get("tool_name") or "")
    if not _is_ide_browser_tool(payload, tool_name):
        return
    inp = tool_input(payload)
    if is_forbidden_new_tab(tool_name, inp):
        return
    result = result_blob(payload)
    if _tool_failed(payload, result):
        return
    binding = verified_binding()
    if binding is None:
        return
    views = load_glass_views(binding) or _empty_glass_views(binding)
    bare = tool_name.removeprefix("MCP:")
    if bare == "browser_tabs":
        for url, view_id in iter_tab_matches(result):
            _record_one_view(binding=binding, views=views, url=url, view_id=view_id)
        return
    view_id = parse_view_id(result, inp)
    url = parse_result_url(result, inp)
    if not view_id or not url:
        return
    _record_one_view(binding=binding, views=views, url=url, view_id=view_id)


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
    """Return notebooks with non-empty pending_run from the live bridge.

    Fail quiet: bridge down, MCP unreachable/slow, tool errors, or malformed
    payloads return []. Only positively observed pending_run entries are kept
    (Phase 5 / D15 — stop hook must not spam when state is unverifiable).
    """
    if not mcp_health_ok():
        # Bound deferred: control bridge may be up with Pluto stopped, or missing entirely.
        return []
    out: list[dict[str, Any]] = []
    try:
        notebooks = mcp_call("list_notebooks", timeout=3)
        if not isinstance(notebooks, list):
            # Tool error / unexpected shape — not evidence of staged edits.
            return []
        for nb in notebooks:
            if not isinstance(nb, dict):
                continue
            nb_id = nb.get("notebook_id")
            if not nb_id:
                continue
            proj = mcp_call("read_notebook_code", {"notebook_id": nb_id}, timeout=4)
            if not isinstance(proj, dict):
                continue
            pending = proj.get("pending_run") or []
            if pending:
                out.append(
                    {
                        "notebook_id": nb_id,
                        "path": proj.get("path"),
                        "pending_run": pending,
                    }
                )
    except (
        urllib.error.URLError,
        TimeoutError,
        OSError,
        json.JSONDecodeError,
        KeyError,
        IndexError,
        TypeError,
        ValueError,
    ):
        return []
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
