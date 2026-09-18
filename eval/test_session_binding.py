"""Unit tests for Styx window session binding helpers (no live Pluto required)."""
from __future__ import annotations

import json
import os
import threading
import unittest
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from unittest import mock

# Import from repo hooks/
ROOT = Path(__file__).resolve().parents[1]
import sys

sys.path.insert(0, str(ROOT / "hooks"))

import pluto_lib  # noqa: E402


class _HealthHandler(BaseHTTPRequestHandler):
    session_id = "aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa"
    body_mode = "json"

    def do_GET(self) -> None:  # noqa: N802
        if self.path.startswith("/health"):
            self.send_response(200)
            if self.body_mode == "json":
                payload = json.dumps(
                    {
                        "status": "ok",
                        "schema_version": 1,
                        "session_id": self.session_id,
                        "mcp_port": self.server.server_address[1],
                        "pluto_port": None,
                        "pluto": "stopped",
                    }
                ).encode()
                self.send_header("Content-Type", "application/json")
                self.send_header("Content-Length", str(len(payload)))
                self.end_headers()
                self.wfile.write(payload)
            else:
                payload = b"ok"
                self.send_header("Content-Length", str(len(payload)))
                self.end_headers()
                self.wfile.write(payload)
            return
        self.send_response(404)
        self.end_headers()

    def log_message(self, format: str, *args) -> None:  # noqa: A003
        return


class SessionBindingTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = Path(self._mkdtemp())
        self.runtime = self.tmp / "runtime"
        (self.runtime / "windows").mkdir(parents=True)
        (self.runtime / "sessions").mkdir(parents=True)
        self.pid = "424242"
        self.session_id = "aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa"
        self.server = HTTPServer(("127.0.0.1", 0), _HealthHandler)
        _HealthHandler.session_id = self.session_id
        _HealthHandler.body_mode = "json"
        self.port = self.server.server_address[1]
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        self.thread.start()
        self.binding_path = self.runtime / "windows" / f"{self.pid}.json"
        self.binding_path.write_text(
            json.dumps(
                {
                    "schema_version": 1,
                    "session_id": self.session_id,
                    "cursor_host_pid": int(self.pid),
                    "owner_pid": 1,
                    "mcp_port": self.port,
                    "pluto_port": None,
                    "pluto": "stopped",
                    "updated_at": "0",
                }
            ),
            encoding="utf-8",
        )
        self.env = {
            "STYX_RUNTIME_DIR": str(self.runtime),
            "VSCODE_PID": self.pid,
        }

    def tearDown(self) -> None:
        self.server.shutdown()
        self.server.server_close()
        import shutil

        shutil.rmtree(self.tmp, ignore_errors=True)

    def _mkdtemp(self) -> str:
        import tempfile

        return tempfile.mkdtemp(prefix="styx-bind-")

    def test_verified_binding_ok(self) -> None:
        with mock.patch.dict(os.environ, self.env, clear=False):
            b = pluto_lib.verified_binding()
            self.assertIsNotNone(b)
            assert b is not None
            self.assertEqual(b["session_id"], self.session_id)
            self.assertEqual(b["mcp_port"], self.port)

    def test_foreign_health_rejected(self) -> None:
        _HealthHandler.session_id = "bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb"
        with mock.patch.dict(os.environ, self.env, clear=False):
            self.assertIsNone(pluto_lib.verified_binding())

    def test_plain_ok_health_rejected(self) -> None:
        _HealthHandler.body_mode = "plain"
        with mock.patch.dict(os.environ, self.env, clear=False):
            self.assertIsNone(pluto_lib.verified_binding())

    def test_missing_binding_returns_none(self) -> None:
        self.binding_path.unlink()
        with mock.patch.dict(os.environ, self.env, clear=False):
            self.assertIsNone(pluto_lib.load_binding())
            self.assertFalse(pluto_lib.mcp_health_ok())

    def test_malformed_binding_ignored(self) -> None:
        self.binding_path.write_text("{not-json", encoding="utf-8")
        with mock.patch.dict(os.environ, self.env, clear=False):
            self.assertIsNone(pluto_lib.load_binding())

    def test_resolve_bridge_prefers_window(self) -> None:
        with mock.patch.dict(os.environ, self.env, clear=False):
            os.environ.pop("STYX_SESSION_ID", None)
            b = pluto_lib.resolve_bridge_binding()
            self.assertIsNotNone(b)
            assert b is not None
            self.assertEqual(b["session_id"], self.session_id)

    def test_resolve_bridge_by_session_id_env(self) -> None:
        other_sid = "bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb"
        other = self.runtime / "windows" / "999999.json"
        other.write_text(
            json.dumps(
                {
                    "schema_version": 1,
                    "session_id": other_sid,
                    "cursor_host_pid": 999999,
                    "owner_pid": 1,
                    "mcp_port": self.port,
                    "pluto_port": None,
                    "pluto": "stopped",
                    "updated_at": "0",
                }
            ),
            encoding="utf-8",
        )
        # Health handler still answers with self.session_id — other file is unhealthy.
        _HealthHandler.session_id = self.session_id
        env = {**self.env, "STYX_SESSION_ID": self.session_id}
        with mock.patch.dict(os.environ, env, clear=False):
            os.environ.pop("VSCODE_PID", None)
            os.environ.pop("VSCODE_IPC_HOOK_CLI", None)
            b = pluto_lib.resolve_bridge_binding()
            self.assertIsNotNone(b)
            assert b is not None
            self.assertEqual(b["session_id"], self.session_id)

    def test_resolve_bridge_sole_healthy_without_window(self) -> None:
        with mock.patch.dict(os.environ, {"STYX_RUNTIME_DIR": str(self.runtime)}, clear=False):
            os.environ.pop("VSCODE_PID", None)
            os.environ.pop("VSCODE_IPC_HOOK_CLI", None)
            os.environ.pop("STYX_SESSION_ID", None)
            b = pluto_lib.resolve_bridge_binding()
            self.assertIsNotNone(b)
            assert b is not None
            self.assertEqual(b["mcp_port"], self.port)

    def test_resolve_bridge_ambiguous_without_session_id(self) -> None:
        other_sid = "bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb"
        # Second healthy binding needs its own health server matching other_sid.
        server2 = HTTPServer(("127.0.0.1", 0), _HealthHandler)
        # Can't easily dual-session one handler — patch healthy_bindings instead.
        server2.server_close()
        fake = [
            {"session_id": self.session_id, "mcp_port": 1},
            {"session_id": other_sid, "mcp_port": 2},
        ]
        with mock.patch.object(pluto_lib, "verified_binding", return_value=None), mock.patch.object(
            pluto_lib, "healthy_bindings", return_value=fake
        ), mock.patch.dict(os.environ, {"STYX_RUNTIME_DIR": str(self.runtime)}, clear=False):
            os.environ.pop("STYX_SESSION_ID", None)
            self.assertIsNone(pluto_lib.resolve_bridge_binding())

    def test_session_scoped_receipts_and_concurrent_updates(self) -> None:
        with mock.patch.dict(os.environ, self.env, clear=False):
            path = pluto_lib.reads_path()
            self.assertIsNotNone(path)
            assert path is not None
            self.assertIn(self.session_id, path)

            errors: list[BaseException] = []

            def worker(n: int) -> None:
                try:
                    for i in range(20):
                        pluto_lib.record_read(f"nb-{n}", f"cell-{i}")
                except BaseException as e:  # noqa: BLE001
                    errors.append(e)

            threads = [threading.Thread(target=worker, args=(i,)) for i in range(4)]
            for t in threads:
                t.start()
            for t in threads:
                t.join()
            self.assertEqual(errors, [])
            reads = pluto_lib.load_reads()
            self.assertEqual(len(reads), 80)


class WindowKeyTests(unittest.TestCase):
    def test_prefers_vscode_pid(self) -> None:
        from styx_window_key import resolve_window_key

        env = {
            "VSCODE_PID": "12345",
            "VSCODE_IPC_HOOK_CLI": "/run/user/1000/vscode-ipc-aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee.sock",
        }
        self.assertEqual(resolve_window_key(env), (12345, "VSCODE_PID"))

    def test_ipc_hook_cli_hash_stable_and_distinct(self) -> None:
        from styx_window_key import hash_window_token, resolve_window_key

        a = "/run/user/1000/vscode-ipc-aaa09061-1111-2222-3333-444444444444.sock"
        b = "/run/user/1000/vscode-ipc-e357e9ad-5555-6666-7777-888888888888.sock"
        ka, sa = resolve_window_key({"VSCODE_IPC_HOOK_CLI": a})  # type: ignore[misc]
        kb, sb = resolve_window_key({"VSCODE_IPC_HOOK_CLI": b})  # type: ignore[misc]
        self.assertEqual(sa, "VSCODE_IPC_HOOK_CLI")
        self.assertEqual(sb, "VSCODE_IPC_HOOK_CLI")
        self.assertNotEqual(ka, kb)
        self.assertEqual(ka, hash_window_token("vscode-ipc-aaa09061-1111-2222-3333-444444444444"))
        self.assertGreater(ka, 0)
        self.assertLess(ka.bit_length(), 64)

    def test_neither_identity_returns_none(self) -> None:
        from styx_window_key import resolve_window_key

        self.assertIsNone(resolve_window_key({}))
        self.assertIsNone(resolve_window_key({"VSCODE_PID": "not-a-pid"}))

    def test_binding_load_via_ipc_key(self) -> None:
        from styx_window_key import resolve_window_key

        hook = "/tmp/vscode-ipc-deadbeef-aaaa-bbbb-cccc-ddddeeeeffff.sock"
        key, _source = resolve_window_key({"VSCODE_IPC_HOOK_CLI": hook})  # type: ignore[misc]
        tmp = Path(self._mkdtemp())
        runtime = tmp / "runtime"
        (runtime / "windows").mkdir(parents=True)
        session_id = "cccccccc-cccc-cccc-cccc-cccccccccccc"
        binding_path = runtime / "windows" / f"{key}.json"
        binding_path.write_text(
            json.dumps(
                {
                    "schema_version": 1,
                    "session_id": session_id,
                    "cursor_host_pid": key,
                    "owner_pid": 1,
                    "mcp_port": 9,
                    "pluto_port": None,
                    "pluto": "stopped",
                    "updated_at": "0",
                }
            ),
            encoding="utf-8",
        )
        env = {
            "STYX_RUNTIME_DIR": str(runtime),
            "VSCODE_IPC_HOOK_CLI": hook,
        }
        # Clear VSCODE_PID if inherited from the test runner.
        with mock.patch.dict(os.environ, env, clear=False):
            os.environ.pop("VSCODE_PID", None)
            loaded = pluto_lib.load_binding()
            self.assertIsNotNone(loaded)
            assert loaded is not None
            self.assertEqual(loaded["session_id"], session_id)
            self.assertEqual(loaded["cursor_host_pid"], key)
        import shutil

        shutil.rmtree(tmp, ignore_errors=True)

    def _mkdtemp(self) -> str:
        import tempfile

        return tempfile.mkdtemp(prefix="styx-wkey-")


if __name__ == "__main__":
    unittest.main()
