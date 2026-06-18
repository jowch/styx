#!/usr/bin/env python3
"""stop: warn when staged Pluto edits were not submitted (pending_run non-empty)."""
from __future__ import annotations

import json
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))

from pluto_lib import PendingRunError, pending_run_notebooks


def main() -> int:
    try:
        pending = pending_run_notebooks()
    except PendingRunError as e:
        print(
            json.dumps(
                {
                    "followup_message": (
                        "Could not verify Pluto pending_run state (MCP slow or unreachable). "
                        "If you staged edits, call submit_changes before ending the turn.\n"
                        f"({e})"
                    )
                }
            )
        )
        return 0

    if not pending:
        print("{}")
        return 0

    lines = [
        "Pluto notebook edits are still staged and were not run via submit_changes:",
    ]
    for nb in pending:
        path = nb.get("path") or nb.get("notebook_id")
        ids = ", ".join(nb.get("pending_run") or [])
        lines.append(f"- {path}: pending_run=[{ids}]")
    lines.append("Call submit_changes on each notebook above, or discard staged edits.")

    print(json.dumps({"followup_message": "\n".join(lines)}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
