#!/usr/bin/env python3
"""preToolUse: deny Pluto write MCP tools without a prior read_cell receipt in this chat."""
from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.dirname(__file__))

from pluto_lib import (
    EDIT_TOOLS_PRE,
    allow,
    deny_edit,
    has_read,
    hook_input,
    load_reads,
    tool_input,
)


def main() -> int:
    payload = hook_input()
    tool_name = payload.get("tool_name", "")
    if tool_name not in EDIT_TOOLS_PRE:
        allow()
        return 0

    inp = tool_input(payload)
    notebook_id = inp.get("notebook_id")
    cell_id = inp.get("cell_id")

    # add_cell / move_cell may omit cell_id; notebook-level read is enough for add_cell.
    if tool_name in {"MCP:add_cell", "add_cell"} and notebook_id:
        reads_ok = any(r.get("notebook_id") == notebook_id for r in load_reads())
        if reads_ok:
            allow()
            return 0

    if has_read(notebook_id, cell_id):
        allow()
        return 0

    deny_edit(
        "Pluto read-before-edit: call read_cell (or read_notebook_code) for this cell "
        "before edit_cell / add_cell / delete_cell / move_cell."
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
