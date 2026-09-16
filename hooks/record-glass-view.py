#!/usr/bin/env python3
"""afterMCPExecution + postToolUse: cache Glass viewId per notebook / landing.

Silent and non-blocking: never fail the agent turn.
"""
from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.dirname(__file__))

from pluto_lib import hook_input, record_glass_from_hook


def main() -> int:
    try:
        payload = hook_input()
        record_glass_from_hook(payload)
    except Exception:  # noqa: BLE001 — glass cache must not break the turn
        pass
    print("{}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
