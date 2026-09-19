"""Unit tests for styx-check-stale / styx-cleanup / styx_stale (no live Pluto)."""
from __future__ import annotations

import importlib.util
import io
import json
import os
import shutil
import sys
import tempfile
import threading
import unittest
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts" / "lib"))

import styx_stale  # noqa: E402


def _load_script(name: str):
    path = ROOT / "scripts" / name
    spec = importlib.util.spec_from_file_location(name.replace(".py", ""), path)
    assert spec is not None and spec.loader is not None
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


check_stale = _load_script("styx-check-stale.py")
cleanup = _load_script("styx-cleanup.py")


class _HealthHandler(BaseHTTPRequestHandler):
    session_id = "aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa"

    def do_GET(self) -> None:  # noqa: N802
        if self.path.startswith("/health"):
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
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(payload)))
            self.end_headers()
            self.wfile.write(payload)
            return
        self.send_response(404)
        self.end_headers()

    def log_message(self, format: str, *args) -> None:  # noqa: A003
        return


class StyxStaleTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = Path(tempfile.mkdtemp(prefix="styx-stale-"))
        self.runtime = self.tmp / "runtime"
        (self.runtime / "windows").mkdir(parents=True)
        (self.runtime / "sessions").mkdir(parents=True)
        (self.runtime / "notebooks").mkdir(parents=True)
        self.session_id = "aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa"
        self.dead_sid = "bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb"
        self.window_key = "424242"
        self.server = HTTPServer(("127.0.0.1", 0), _HealthHandler)
        _HealthHandler.session_id = self.session_id
        self.port = self.server.server_address[1]
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        self.thread.start()
        self.env = {
            "STYX_RUNTIME_DIR": str(self.runtime),
            "STYX_WINDOW_KEY": self.window_key,
        }

    def tearDown(self) -> None:
        self.server.shutdown()
        self.server.server_close()
        shutil.rmtree(self.tmp, ignore_errors=True)

    def _write_binding(
        self,
        key: str,
        *,
        sid: str,
        port: int,
        owner_pid: int = 1,
    ) -> Path:
        path = self.runtime / "windows" / f"{key}.json"
        path.write_text(
            json.dumps(
                {
                    "schema_version": 1,
                    "session_id": sid,
                    "cursor_host_pid": int(key) if key.isdigit() else 0,
                    "owner_pid": owner_pid,
                    "mcp_port": port,
                    "pluto_port": None,
                    "pluto": "stopped",
                    "updated_at": "0",
                }
            ),
            encoding="utf-8",
        )
        return path

    def test_clean_inventory_exit_0(self) -> None:
        self._write_binding(self.window_key, sid=self.session_id, port=self.port)
        with mock.patch.dict(os.environ, self.env, clear=False):
            inv = styx_stale.inventory()
            self.assertEqual(inv["stale_count"], 0)
            self.assertEqual(inv["live_session_ids"], [self.session_id])
            out = io.StringIO()
            with mock.patch.object(sys, "stdout", out), mock.patch.object(
                sys, "argv", ["styx-check-stale"]
            ):
                code = check_stale.main()
            self.assertEqual(code, 0)
            self.assertIn("stale=no", out.getvalue())
            self.assertIn("offer_cleanup=no", out.getvalue())

    def test_stale_binding_exit_1(self) -> None:
        # Dead port — nothing listening
        self._write_binding("111111", sid=self.dead_sid, port=9)
        with mock.patch.dict(os.environ, self.env, clear=False):
            inv = styx_stale.inventory()
            self.assertEqual(inv["stale_count"], 1)
            self.assertEqual(len(inv["stale_bindings"]), 1)
            out = io.StringIO()
            with mock.patch.object(sys, "stdout", out), mock.patch.object(sys, "argv", ["styx-check-stale"]):
                code = check_stale.main()
            self.assertEqual(code, 1)
            self.assertIn("stale=yes", out.getvalue())
            self.assertIn("offer_cleanup=yes", out.getvalue())

    def test_cleanup_refuses_without_apply(self) -> None:
        self._write_binding("111111", sid=self.dead_sid, port=9)
        err = io.StringIO()
        with (
            mock.patch.dict(os.environ, self.env, clear=False),
            mock.patch.object(sys, "stderr", err),
            mock.patch.object(sys, "argv", ["styx-cleanup"]),
        ):
            code = cleanup.main()
        self.assertEqual(code, 2)
        self.assertIn("refusing without --apply", err.getvalue())
        self.assertTrue((self.runtime / "windows" / "111111.json").is_file())

    def test_keep_live_binding_on_apply(self) -> None:
        live = self._write_binding(self.window_key, sid=self.session_id, port=self.port)
        dead = self._write_binding("111111", sid=self.dead_sid, port=9)
        with (
            mock.patch.dict(os.environ, self.env, clear=False),
            mock.patch.object(sys, "argv", ["styx-cleanup", "--apply"]),
            mock.patch.object(sys, "stdout", io.StringIO()),
        ):
            code = cleanup.main()
        self.assertEqual(code, 0)
        self.assertTrue(live.is_file())
        self.assertFalse(dead.is_file())

    def test_remove_dead_binding_on_apply(self) -> None:
        dead = self._write_binding("111111", sid=self.dead_sid, port=9)
        with (
            mock.patch.dict(os.environ, self.env, clear=False),
            mock.patch.object(sys, "argv", ["styx-cleanup", "--apply"]),
            mock.patch.object(sys, "stdout", io.StringIO()),
        ):
            code = cleanup.main()
        self.assertEqual(code, 0)
        self.assertFalse(dead.is_file())

    def test_offer_flip_no_renag(self) -> None:
        self._write_binding("111111", sid=self.dead_sid, port=9)
        with mock.patch.dict(os.environ, self.env, clear=False):
            out1 = io.StringIO()
            with (
                mock.patch.object(sys, "stdout", out1),
                mock.patch.object(sys, "argv", ["styx-check-stale", "--mark-offer"]),
            ):
                code1 = check_stale.main()
            self.assertEqual(code1, 1)
            self.assertIn("offer_cleanup=no", out1.getvalue())  # marked → no further offer
            offer = styx_stale.offer_path(self.runtime, self.window_key)
            self.assertTrue(offer.is_file())

            out2 = io.StringIO()
            with (
                mock.patch.object(sys, "stdout", out2),
                mock.patch.object(sys, "argv", ["styx-check-stale"]),
            ):
                code2 = check_stale.main()
            self.assertEqual(code2, 1)  # still stale
            self.assertIn("stale=yes", out2.getvalue())
            self.assertIn("offer_cleanup=no", out2.getvalue())
            self.assertIn("offer_already=yes", out2.getvalue())

    def test_ignore_non_styx_json(self) -> None:
        junk = self.runtime / "windows" / "junk.json"
        junk.write_text(json.dumps({"hello": "world"}), encoding="utf-8")
        malformed = self.runtime / "windows" / "bad.json"
        malformed.write_text("{not-json", encoding="utf-8")
        no_schema = self.runtime / "windows" / "noschema.json"
        no_schema.write_text(
            json.dumps({"session_id": self.dead_sid, "mcp_port": 9}),
            encoding="utf-8",
        )
        with mock.patch.dict(os.environ, self.env, clear=False):
            inv = styx_stale.inventory()
            self.assertEqual(inv["bindings"], [])
            self.assertEqual(inv["stale_count"], 0)
            out = io.StringIO()
            with mock.patch.object(sys, "stdout", out), mock.patch.object(sys, "argv", ["styx-check-stale"]):
                code = check_stale.main()
            self.assertEqual(code, 0)
            self.assertIn("stale=no", out.getvalue())

    def test_pid_looks_like_styx_owner_guard(self) -> None:
        with mock.patch.object(styx_stale, "pid_alive", return_value=True), mock.patch.object(
            styx_stale, "pid_cmdline", return_value="/usr/bin/julia --project PlutoMCP"
        ):
            self.assertTrue(styx_stale.pid_looks_like_styx_owner(12345))
        with mock.patch.object(styx_stale, "pid_alive", return_value=True), mock.patch.object(
            styx_stale, "pid_cmdline", return_value="/usr/bin/sleep 3600"
        ):
            self.assertFalse(styx_stale.pid_looks_like_styx_owner(12345))
        with mock.patch.object(styx_stale, "pid_alive", return_value=False):
            self.assertFalse(styx_stale.pid_looks_like_styx_owner(12345))


if __name__ == "__main__":
    unittest.main()
