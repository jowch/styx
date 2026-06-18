#!/usr/bin/env python3
"""postToolUse: record read_cell / read_notebook_code for hook edit guard."""
from __future__ import annotations

import json
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))

from pluto_lib import READ_TOOLS, hook_input, load_reads, record_read, save_reads, tool_input


def main() -> int:
    payload = hook_input()
    tool_name = payload.get("tool_name", "")
    if tool_name not in READ_TOOLS:
        print("{}")
        return 0

    inp = tool_input(payload)
    notebook_id = inp.get("notebook_id")
    cell_id = inp.get("cell_id")

    if tool_name in {"MCP:read_notebook_code", "read_notebook_code"} and notebook_id:
        reads = load_reads()
        reads.append({"notebook_id": notebook_id, "cell_id": "*"})
        save_reads(reads)
    else:
        record_read(notebook_id, cell_id)

    print("{}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
