"""Unit tests for pending_run stop-hook fail-quiet behavior (no live Pluto)."""
from __future__ import annotations

import importlib.util
import io
import json
import os
import sys
import unittest
import urllib.error
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "hooks"))

import pluto_lib  # noqa: E402


def _load_warn_pending_run():
    path = ROOT / "hooks" / "warn-pending-run.py"
    spec = importlib.util.spec_from_file_location("warn_pending_run", path)
    assert spec is not None and spec.loader is not None
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


class PendingRunQuietTests(unittest.TestCase):
    def test_health_down_returns_empty(self) -> None:
        with mock.patch.object(pluto_lib, "mcp_health_ok", return_value=False):
            self.assertEqual(pluto_lib.pending_run_notebooks(), [])

    def test_unexpected_list_notebooks_payload_returns_empty(self) -> None:
        with (
            mock.patch.object(pluto_lib, "mcp_health_ok", return_value=True),
            mock.patch.object(
                pluto_lib,
                "mcp_call",
                return_value={"ok": False, "error": {"error": "tool_error"}},
            ),
        ):
            self.assertEqual(pluto_lib.pending_run_notebooks(), [])

    def test_mcp_call_failure_returns_empty(self) -> None:
        with (
            mock.patch.object(pluto_lib, "mcp_health_ok", return_value=True),
            mock.patch.object(
                pluto_lib,
                "mcp_call",
                side_effect=urllib.error.URLError("timed out"),
            ),
        ):
            self.assertEqual(pluto_lib.pending_run_notebooks(), [])

    def test_positive_pending_run_returned(self) -> None:
        def _call(name: str, arguments=None, *, timeout: float = 5):
            if name == "list_notebooks":
                return [{"notebook_id": "nb-1", "path": "/tmp/x.jl"}]
            if name == "read_notebook_code":
                return {
                    "notebook_id": "nb-1",
                    "path": "/tmp/x.jl",
                    "pending_run": ["cell-a"],
                }
            raise AssertionError(f"unexpected tool {name}")

        with (
            mock.patch.object(pluto_lib, "mcp_health_ok", return_value=True),
            mock.patch.object(pluto_lib, "mcp_call", side_effect=_call),
        ):
            pending = pluto_lib.pending_run_notebooks()
        self.assertEqual(len(pending), 1)
        self.assertEqual(pending[0]["notebook_id"], "nb-1")
        self.assertEqual(pending[0]["pending_run"], ["cell-a"])

    def test_empty_notebooks_returns_empty(self) -> None:
        with (
            mock.patch.object(pluto_lib, "mcp_health_ok", return_value=True),
            mock.patch.object(pluto_lib, "mcp_call", return_value=[]),
        ):
            self.assertEqual(pluto_lib.pending_run_notebooks(), [])


class WarnPendingRunHookTests(unittest.TestCase):
    def test_quiet_when_no_pending(self) -> None:
        mod = _load_warn_pending_run()
        buf = io.StringIO()
        with (
            mock.patch.object(mod, "pending_run_notebooks", return_value=[]),
            mock.patch.object(sys, "stdout", buf),
        ):
            self.assertEqual(mod.main(), 0)
        self.assertEqual(json.loads(buf.getvalue()), {})

    def test_quiet_when_probe_raises(self) -> None:
        mod = _load_warn_pending_run()
        buf = io.StringIO()
        with (
            mock.patch.object(
                mod, "pending_run_notebooks", side_effect=RuntimeError("boom")
            ),
            mock.patch.object(sys, "stdout", buf),
        ):
            self.assertEqual(mod.main(), 0)
        self.assertEqual(json.loads(buf.getvalue()), {})

    def test_followup_only_when_pending_true(self) -> None:
        mod = _load_warn_pending_run()
        buf = io.StringIO()
        pending = [
            {
                "notebook_id": "nb-1",
                "path": "/tmp/x.jl",
                "pending_run": ["cell-a"],
            }
        ]
        with (
            mock.patch.object(mod, "pending_run_notebooks", return_value=pending),
            mock.patch.object(sys, "stdout", buf),
        ):
            self.assertEqual(mod.main(), 0)
        payload = json.loads(buf.getvalue())
        self.assertIn("followup_message", payload)
        self.assertIn("pending_run=[cell-a]", payload["followup_message"])
        self.assertNotIn("Could not verify", payload["followup_message"])


if __name__ == "__main__":
    unittest.main()
