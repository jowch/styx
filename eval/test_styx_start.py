"""Unit tests for scripts/styx-start.py (no live Pluto)."""
from __future__ import annotations

import argparse
import importlib.util
import io
import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]


def _load_styx_start():
    spec = importlib.util.spec_from_file_location(
        "styx_start", ROOT / "scripts" / "styx-start.py"
    )
    assert spec is not None and spec.loader is not None
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


styx_start = _load_styx_start()


class StyxStartTests(unittest.TestCase):
    def test_open_flag_is_rejected(self) -> None:
        with mock.patch.object(sys, "stderr", io.StringIO()), self.assertRaises(SystemExit):
            styx_start.main(["--open"])

    def test_welcome_and_path_rejected(self) -> None:
        with mock.patch.object(sys, "stderr", io.StringIO()), self.assertRaises(SystemExit):
            styx_start.main(["--welcome", "--path", "note.jl"])

    def test_pick_path_welcome_skips_default(self) -> None:
        args = argparse.Namespace(welcome=True, path=None)
        self.assertIsNone(styx_start._pick_path(args))

    def test_pick_path_explicit_wins(self) -> None:
        args = argparse.Namespace(welcome=False, path="note.jl")
        self.assertEqual(styx_start._pick_path(args), "note.jl")

    def test_pick_path_default_analysis_jl_from_cwd(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            cwd = Path(tmp)
            (cwd / "analysis.jl").write_text("# notebook\n")
            args = argparse.Namespace(welcome=False, path=None)
            old = Path.cwd()
            os.chdir(cwd)
            try:
                picked = styx_start._pick_path(args)
            finally:
                os.chdir(old)
            self.assertEqual(picked, str((cwd / "analysis.jl").resolve()))

    def test_prints_exact_host_welcome_url(self) -> None:
        binding = {"session_id": "aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa", "mcp_port": 2346}

        def fake_call(name, arguments=None, timeout=30, binding=None):  # noqa: A002
            if name in ("start_pluto_session", "pluto_session_status"):
                return {
                    "ok": True,
                    "pluto_url": "http://localhost:1234",
                    "pluto_port": 1234,
                    "mcp_port": 2346,
                    "session_id": binding["session_id"] if binding else "",
                    "pluto": "running",
                }
            raise AssertionError(f"unexpected call {name}")

        buf = io.StringIO()
        with (
            mock.patch.object(styx_start.pluto_lib, "resolve_bridge_binding", return_value=binding),
            mock.patch.object(styx_start.pluto_lib, "mcp_call", side_effect=fake_call),
            mock.patch.object(sys, "stdout", buf),
        ):
            code = styx_start.main(["--welcome"])
        self.assertEqual(code, 0)
        out = buf.getvalue()
        self.assertIn("welcome_url=http://localhost:1234/", out)
        self.assertNotIn("127.0.0.1", out)
        self.assertNotIn("webbrowser", out)


if __name__ == "__main__":
    unittest.main()
