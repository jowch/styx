#!/usr/bin/env python3
"""beforeSubmitPrompt: hint when Pluto context present but session not started (D15)."""
from __future__ import annotations

import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(__file__))

from pluto_lib import pluto_session_running, verified_binding

_LOCALHOST_URL = re.compile(
    r"(?:localhost|127\.0\.0\.1):\d+",
    re.IGNORECASE,
)


def _has_pluto_context(prompt: str) -> bool:
    lower = prompt.lower()
    if "pluto-notebook#" in lower or "pluto-cell#" in lower:
        return True
    if _LOCALHOST_URL.search(prompt):
        return True
    binding = verified_binding()
    if binding and binding.get("pluto_port"):
        port = str(binding["pluto_port"])
        if f":{port}" in prompt:
            return True
    return False


def main() -> int:
    payload = json.load(sys.stdin)
    prompt = payload.get("prompt") or ""

    if _has_pluto_context(prompt) and not pluto_session_running():
        print(
            json.dumps(
                {
                    "continue": True,
                    "user_message": (
                        "Pluto notebook context detected, but the Pluto session is not running yet. "
                        "Ask the agent to start Pluto (say you want to work on notebooks). "
                        "Do not reload MCP or run pluto-serve.sh — the agent calls start_pluto_session "
                        "and navigates using pluto_session_status.pluto_url."
                    ),
                }
            )
        )
        return 0

    print(json.dumps({"continue": True}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
