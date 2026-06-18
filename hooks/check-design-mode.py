#!/usr/bin/env python3
"""beforeSubmitPrompt: hint when Pluto context present but session not started (D15)."""
from __future__ import annotations

import json
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))

from pluto_lib import pluto_session_running


def _has_pluto_context(prompt: str) -> bool:
    lower = prompt.lower()
    return "pluto-notebook#" in lower or "localhost:1234" in lower


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
                        "Ask the agent to start Pluto (pluto-notebooks command or say you want to work on notebooks). "
                        "Do not reload MCP or run pluto-serve.sh — the agent calls start_pluto_session."
                    ),
                }
            )
        )
        return 0

    print(json.dumps({"continue": True}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
