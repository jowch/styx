#!/usr/bin/env python3
"""sessionStart: inject Remote SSH + known Glass views. Never wipe glass-views.json."""
from __future__ import annotations

import json
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))

from pluto_lib import session_start_payload


def main() -> int:
    try:
        try:
            json.load(sys.stdin)
        except (json.JSONDecodeError, ValueError):
            pass
        print(json.dumps(session_start_payload()))
    except Exception:  # noqa: BLE001 — sessionStart must not block the agent
        print("{}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
