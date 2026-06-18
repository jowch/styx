#!/usr/bin/env python3
"""beforeSubmitPrompt: record Design Mode selection; warn if MCP bridge is down."""
from __future__ import annotations

import json
import os
import sys
from datetime import datetime, timezone

sys.path.insert(0, os.path.dirname(__file__))

from pluto_lib import mcp_health_ok, parse_prompt_text, save_selection


def main() -> int:
    payload = json.load(sys.stdin)
    prompt = payload.get("prompt") or ""
    parsed = parse_prompt_text(prompt)

    if parsed.get("ok"):
        save_selection(
            {
                "notebook_id": parsed.get("notebook_id"),
                "cell_id": parsed.get("cell_id"),
                "dom_path": parsed.get("dom_path"),
                "captured_at": datetime.now(timezone.utc).isoformat(),
            }
        )

    if "pluto-notebook#" in prompt.lower() or "localhost:1234" in prompt:
        if not mcp_health_ok():
            print(
                json.dumps(
                    {
                        "continue": False,
                        "user_message": (
                            "PlutoMCP bridge is not reachable at http://127.0.0.1:2346/health. "
                            "Enable the pluto MCP server in Cursor (plugin mcp.json) or run "
                            "PlutoMCP.serve() in a terminal, then retry."
                        ),
                    }
                )
            )
            return 0

    print(json.dumps({"continue": True}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
