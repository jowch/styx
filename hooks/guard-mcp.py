#!/usr/bin/env python3
"""beforeMCPExecution: deny Pluto write tools without prior read_cell in this chat."""
from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.dirname(__file__))

from pluto_lib import allow, deny_edit, hook_input, tool_input, write_allowed


WRITE_TOOLS = {"edit_cell", "edit_cells", "add_cell", "delete_cell", "move_cell"}


def main() -> int:
    payload = hook_input()
    tool_name = payload.get("tool_name", "")
    if tool_name not in WRITE_TOOLS:
        allow()
        return 0

    inp = tool_input(payload)
    if write_allowed(tool_name, inp):
        allow()
        return 0

    deny_edit(
        "Pluto read-before-edit: call read_cell before mutating this notebook cell."
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
