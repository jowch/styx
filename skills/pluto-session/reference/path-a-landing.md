# Path A — landing page bootstrap

Use when the user wants Pluto/notebooks but **does not name a specific file**.

## Examples

- "I want to work on my notebooks"
- "open Pluto"
- "let's use Pluto"

## Steps

1. `pluto_session_status` → if stopped, `start_pluto_session`
2. Open **Pluto landing page** in Agents Glass: `http://127.0.0.1:1234/`
3. Tell the user briefly:

   > Pluto is ready. Pick or create a notebook on this page. When you're in a notebook, send your next message — click a cell with **⌘⇧D** (Design Mode) or describe what you want.

4. **Stop.** Do not call `open_notebook`, `list_notebooks`, or ask which file.

## Next user prompt (notebook chosen in UI)

Resolve context via **pluto-workflow**:

- Design Mode click → `resolve_pluto_context` → `read_cell`
- Glass URL `http://127.0.0.1:1234/edit?id=<notebook_id>`
- `list_notebooks` only if needed

## If Pluto is already running

Open landing page only. Do not re-bootstrap unless session is stopped.
