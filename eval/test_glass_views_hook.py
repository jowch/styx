"""Unit tests for Glass viewId cache hooks (no live Pluto / no browser tabs)."""
from __future__ import annotations

import importlib.util
import io
import json
import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "hooks"))

import pluto_lib  # noqa: E402

NB_A = "ba45d628-b0a1-11f1-979c-099c8dac4f28"
NB_B = "aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee"
SID = "aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa"
PLUTO = "http://127.0.0.1:1234"
LANDING = f"{PLUTO}/"
EDIT_A = f"{PLUTO}/edit?id={NB_A}"
EDIT_B = f"{PLUTO}/edit?id={NB_B}"


def _load_hook(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec is not None and spec.loader is not None
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _binding(**extra):
    data = {
        "schema_version": 1,
        "session_id": SID,
        "mcp_port": 2346,
        "pluto_port": 1234,
        "pluto_url": PLUTO,
        "pluto": "running",
    }
    data.update(extra)
    return data


class ParseGlassViewTests(unittest.TestCase):
    def test_notebook_key_from_edit_url(self) -> None:
        self.assertEqual(pluto_lib.notebook_key_from_url(EDIT_A), NB_A)

    def test_landing_key(self) -> None:
        self.assertEqual(pluto_lib.notebook_key_from_url(LANDING), pluto_lib.LANDING_KEY)
        self.assertEqual(pluto_lib.notebook_key_from_url(PLUTO), pluto_lib.LANDING_KEY)

    def test_view_id_from_json_metadata(self) -> None:
        result = {
            "content": [{"type": "text", "text": "ok"}],
            "metadata": {"viewId": "e7ffd6", "url": LANDING},
        }
        self.assertEqual(pluto_lib.parse_view_id(result, {}), "e7ffd6")
        self.assertEqual(pluto_lib.parse_result_url(result, {}), LANDING)

    def test_view_id_from_browser_view_id_text(self) -> None:
        result = {
            "content": [
                {
                    "type": "text",
                    "text": "### Action: snapshot\n- Browser View ID: e7ffd6\n",
                }
            ]
        }
        self.assertEqual(pluto_lib.parse_view_id(result, {}), "e7ffd6")

    def test_view_id_falls_back_to_tool_input(self) -> None:
        self.assertEqual(
            pluto_lib.parse_view_id({"content": [{"type": "text", "text": "ok"}]}, {"viewId": "abc123"}),
            "abc123",
        )

    def test_result_url_preferred_over_input(self) -> None:
        result = {"metadata": {"url": EDIT_A, "viewId": "e7ffd6"}}
        self.assertEqual(
            pluto_lib.parse_result_url(result, {"url": LANDING}),
            EDIT_A,
        )


class GlassViewStoreTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = Path(tempfile.mkdtemp(prefix="styx-glass-"))
        self.runtime = self.tmp / "runtime"
        (self.runtime / "sessions" / SID).mkdir(parents=True)
        self.binding = _binding()
        self.env = {"STYX_RUNTIME_DIR": str(self.runtime)}

    def tearDown(self) -> None:
        import shutil

        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_last_write_wins_same_notebook(self) -> None:
        with mock.patch.dict(os.environ, self.env, clear=False):
            pluto_lib.upsert_glass_view(
                NB_A, "view-one", EDIT_A, binding=self.binding, updated_at="1"
            )
            pluto_lib.upsert_glass_view(
                NB_A, "view-two", EDIT_A, binding=self.binding, updated_at="2"
            )
            views = pluto_lib.load_glass_views(self.binding)
        assert views is not None
        self.assertEqual(views["entries"][NB_A]["viewId"], "view-two")
        self.assertEqual(len(views["entries"]), 1)

    def test_two_notebooks_are_separate_keys(self) -> None:
        with mock.patch.dict(os.environ, self.env, clear=False):
            pluto_lib.upsert_glass_view(
                pluto_lib.LANDING_KEY, "v-land", LANDING, binding=self.binding
            )
            pluto_lib.upsert_glass_view(NB_A, "v-a", EDIT_A, binding=self.binding)
            pluto_lib.upsert_glass_view(NB_B, "v-b", EDIT_B, binding=self.binding)
            views = pluto_lib.load_glass_views(self.binding)
        assert views is not None
        self.assertEqual(set(views["entries"]), {pluto_lib.LANDING_KEY, NB_A, NB_B})
        self.assertEqual(views["session_id"], SID)

    def test_drop_one_entry_does_not_wipe_file(self) -> None:
        with mock.patch.dict(os.environ, self.env, clear=False):
            pluto_lib.upsert_glass_view(
                pluto_lib.LANDING_KEY, "v-land", LANDING, binding=self.binding
            )
            pluto_lib.upsert_glass_view(NB_A, "v-a", EDIT_A, binding=self.binding)
            path = pluto_lib.glass_views_path(self.binding)
            pluto_lib.drop_glass_view(NB_A, binding=self.binding)
            views = pluto_lib.load_glass_views(self.binding)
        assert views is not None
        self.assertIn(pluto_lib.LANDING_KEY, views["entries"])
        self.assertNotIn(NB_A, views["entries"])
        assert path is not None
        self.assertTrue(Path(path).is_file())

    def test_session_start_does_not_wipe_glass_views(self) -> None:
        with mock.patch.dict(os.environ, self.env, clear=False):
            pluto_lib.upsert_glass_view(
                pluto_lib.LANDING_KEY, "e7ffd6", LANDING, binding=self.binding
            )
            with mock.patch.object(pluto_lib, "load_binding", return_value=self.binding):
                payload = pluto_lib.session_start_payload()
            views = pluto_lib.load_glass_views(self.binding)
        assert views is not None
        self.assertEqual(views["entries"][pluto_lib.LANDING_KEY]["viewId"], "e7ffd6")
        ctx = payload["additional_context"]
        self.assertIn("e7ffd6", ctx)
        self.assertIn(pluto_lib.LANDING_KEY, ctx)
        self.assertIn("Never `newTab`", ctx)

    def test_foreign_origin_not_session_pluto(self) -> None:
        self.assertFalse(
            pluto_lib.url_is_session_pluto(
                "https://example.com/", self.binding, pluto_lib._empty_glass_views(self.binding)
            )
        )
        self.assertTrue(pluto_lib.url_is_session_pluto(LANDING, self.binding, None))
        self.assertTrue(pluto_lib.url_is_session_pluto(EDIT_A, self.binding, None))


class RecordGlassFromHookTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = Path(tempfile.mkdtemp(prefix="styx-glass-hook-"))
        self.runtime = self.tmp / "runtime"
        (self.runtime / "sessions" / SID).mkdir(parents=True)
        self.binding = _binding()
        self.env = {"STYX_RUNTIME_DIR": str(self.runtime)}

    def tearDown(self) -> None:
        import shutil

        shutil.rmtree(self.tmp, ignore_errors=True)

    def _record(self, payload: dict) -> None:
        with (
            mock.patch.dict(os.environ, self.env, clear=False),
            mock.patch.object(pluto_lib, "verified_binding", return_value=self.binding),
            mock.patch.object(pluto_lib, "load_binding", return_value=self.binding),
        ):
            pluto_lib.record_glass_from_hook(payload)

    def _views(self) -> dict:
        with mock.patch.dict(os.environ, self.env, clear=False):
            views = pluto_lib.load_glass_views(self.binding)
        assert views is not None
        return views

    def test_navigate_records_landing(self) -> None:
        self._record(
            {
                "tool_name": "browser_navigate",
                "mcp_server_name": "cursor-ide-browser",
                "tool_input": {"url": LANDING, "position": "active"},
                "result_json": json.dumps(
                    {"metadata": {"viewId": "e7ffd6", "url": LANDING}, "isError": False}
                ),
            }
        )
        views = self._views()
        self.assertEqual(views["entries"][pluto_lib.LANDING_KEY]["viewId"], "e7ffd6")
        self.assertEqual(views["entries"][pluto_lib.LANDING_KEY]["url"], LANDING)

    def test_snapshot_records_notebook_from_result_url(self) -> None:
        self._record(
            {
                "tool_name": "MCP:browser_snapshot",
                "tool_input": {"viewId": "e7ffd6"},
                "tool_output": json.dumps(
                    {
                        "content": [
                            {"type": "text", "text": "Browser View ID: e7ffd6"}
                        ],
                        "metadata": {"viewId": "e7ffd6", "url": EDIT_A},
                    }
                ),
            }
        )
        views = self._views()
        self.assertEqual(views["entries"][NB_A]["viewId"], "e7ffd6")

    def test_skips_new_tab_true(self) -> None:
        self._record(
            {
                "tool_name": "browser_navigate",
                "tool_input": {"url": LANDING, "newTab": True},
                "result_json": json.dumps({"metadata": {"viewId": "newone", "url": LANDING}}),
            }
        )
        self.assertEqual(self._views()["entries"], {})

    def test_skips_browser_tabs_action_new(self) -> None:
        self._record(
            {
                "tool_name": "browser_tabs",
                "tool_input": {"action": "new"},
                "result_json": json.dumps(
                    {"tabs": [{"url": LANDING, "viewId": "nope"}]}
                ),
            }
        )
        self.assertEqual(self._views()["entries"], {})

    def test_tabs_list_records_matching_url_only(self) -> None:
        self._record(
            {
                "tool_name": "browser_tabs",
                "tool_input": {"action": "list"},
                "result_json": json.dumps(
                    {
                        "tabs": [
                            {"url": "https://example.com/", "viewId": "other"},
                            {"url": EDIT_B, "viewId": "glass-b"},
                        ]
                    }
                ),
            }
        )
        views = self._views()
        self.assertNotIn(pluto_lib.LANDING_KEY, views["entries"])
        self.assertEqual(views["entries"][NB_B]["viewId"], "glass-b")
        self.assertNotIn("other", json.dumps(views["entries"]))

    def test_skips_failed_tool(self) -> None:
        self._record(
            {
                "tool_name": "browser_navigate",
                "tool_input": {"url": LANDING},
                "result_json": json.dumps(
                    {"isError": True, "metadata": {"viewId": "x", "url": LANDING}}
                ),
            }
        )
        self.assertEqual(self._views()["entries"], {})

    def test_skips_view_not_found_when_iserror_false(self) -> None:
        """Live afterMCPExecution: Cursor reports view-not-found with isError false."""
        self._record(
            {
                "tool_name": "browser_navigate",
                "mcp_server_name": "cursor-ide-browser",
                "hook_event_name": "afterMCPExecution",
                "tool_input": json.dumps(
                    {
                        "url": LANDING,
                        "viewId": "glass-browser-e7ffd6",
                        "position": "active",
                    }
                ),
                "result_json": json.dumps(
                    {
                        "content": [
                            {
                                "type": "text",
                                "text": (
                                    "Browser view not found: glass-browser-e7ffd6. "
                                    "Use browser_navigate without a viewId to create a new tab."
                                ),
                            }
                        ],
                        "isError": False,
                    }
                ),
            }
        )
        self.assertEqual(self._views()["entries"], {})

    def test_skips_no_tab_available_when_iserror_false(self) -> None:
        """Live postToolUse: no-tab error is also isError false."""
        self._record(
            {
                "tool_name": "MCP:browser_navigate",
                "hook_event_name": "postToolUse",
                "tool_input": {"url": LANDING, "position": "active"},
                "tool_output": json.dumps(
                    {
                        "content": [
                            {
                                "type": "text",
                                "text": "No browser tab available. Please navigate to a page first.",
                            }
                        ],
                        "isError": False,
                    }
                ),
            }
        )
        self.assertEqual(self._views()["entries"], {})

    def test_skips_snapshot_no_tab_even_with_input_url(self) -> None:
        """Same hole as navigate if snapshot/lock ever carry a URL plus viewId."""
        self._record(
            {
                "tool_name": "browser_snapshot",
                "tool_input": {"viewId": "glass-browser-e7ffd6", "url": LANDING},
                "result_json": json.dumps(
                    {
                        "content": [
                            {
                                "type": "text",
                                "text": "No browser tab available. Please navigate to a page first.",
                            }
                        ],
                        "isError": False,
                    }
                ),
            }
        )
        self.assertEqual(self._views()["entries"], {})

    def test_skips_lock_view_not_found_even_with_result_url(self) -> None:
        self._record(
            {
                "tool_name": "browser_lock",
                "tool_input": {"action": "lock", "viewId": "lock-id"},
                "result_json": json.dumps(
                    {
                        "content": [
                            {
                                "type": "text",
                                "text": (
                                    "Browser view not found: lock-id. "
                                    "Use browser_navigate without a viewId to create a new tab."
                                ),
                            }
                        ],
                        "metadata": {"url": EDIT_A},
                        "isError": False,
                    }
                ),
            }
        )
        self.assertEqual(self._views()["entries"], {})

    def test_input_view_id_when_result_has_no_id(self) -> None:
        self._record(
            {
                "tool_name": "browser_lock",
                "tool_input": {"action": "lock", "viewId": "lock-id"},
                "result_json": json.dumps({"metadata": {"url": EDIT_A}}),
            }
        )
        self.assertEqual(self._views()["entries"][NB_A]["viewId"], "lock-id")

    def test_no_binding_records_nothing(self) -> None:
        with (
            mock.patch.dict(os.environ, self.env, clear=False),
            mock.patch.object(pluto_lib, "verified_binding", return_value=None),
        ):
            pluto_lib.record_glass_from_hook(
                {
                    "tool_name": "browser_navigate",
                    "tool_input": {"url": LANDING},
                    "result_json": json.dumps(
                        {"metadata": {"viewId": "e7ffd6", "url": LANDING}}
                    ),
                }
            )
        self.assertEqual(self._views()["entries"], {})


class RecordGlassViewHookQuietTests(unittest.TestCase):
    def test_hook_prints_empty_json_on_success_and_error(self) -> None:
        mod = _load_hook("record_glass_view", ROOT / "hooks" / "record-glass-view.py")
        buf = io.StringIO()
        with (
            mock.patch.object(mod, "hook_input", return_value={"tool_name": "browser_navigate"}),
            mock.patch.object(mod, "record_glass_from_hook", side_effect=RuntimeError("boom")),
            mock.patch.object(sys, "stdout", buf),
        ):
            self.assertEqual(mod.main(), 0)
        self.assertEqual(json.loads(buf.getvalue()), {})


class SessionStartHookTests(unittest.TestCase):
    def test_empty_without_binding(self) -> None:
        mod = _load_hook("session_start", ROOT / "hooks" / "session-start.py")
        buf = io.StringIO()
        with (
            mock.patch.object(mod, "session_start_payload", return_value={}),
            mock.patch.object(sys, "stdin", io.StringIO("{}")),
            mock.patch.object(sys, "stdout", buf),
        ):
            self.assertEqual(mod.main(), 0)
        self.assertEqual(json.loads(buf.getvalue()), {})

    def test_remote_ssh_context_preserved(self) -> None:
        with mock.patch.dict(os.environ, {"CURSOR_CODE_REMOTE": "true"}, clear=False):
            with mock.patch.object(pluto_lib, "load_binding", return_value=None):
                payload = pluto_lib.session_start_payload()
        self.assertIn("Remote SSH", payload["additional_context"])
        self.assertNotIn("Known Glass views", payload["additional_context"])


if __name__ == "__main__":
    unittest.main()
