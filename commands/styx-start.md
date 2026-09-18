---
description: Boot Pluto (+ optional notebook), open Agents Glass, Path B click when known — same turn, ready to work
---

# Styx start

**Success:** one `/styx-start` → user returns to Pluto **open and ready to work** (no second ask). Prefer the script for boot; MCP tools are the fallback. Complete the full chain in **this agent turn**.

## 1. Boot (script or MCP)

From the plugin root (or repo):

```bash
scripts/styx-start.sh                  # start; open ./analysis.jl if present
scripts/styx-start.sh --welcome        # start only
scripts/styx-start.sh --path note.jl   # start + open_notebook
scripts/styx-start.sh --path note.jl --run
scripts/styx-start.sh --open           # local: also OS default browser (human handoff)
```

Parse stdout for `welcome_url=` / `pluto_port=` / `session_id=` / optional `notebook_id=` + `path=` (exact host — do not rewrite `localhost` ↔ `127.0.0.1`).

**Agent fallback** (no script / no binding): `start_pluto_session` → optional `open_notebook(path=…)` → read welcome URL from status.

## 2. Same turn — Glass ready to work

Do not stop after printing the URL. Immediately:

1. **Resolve Glass URL** — [glass-navigation.md](../skills/pluto-session/reference/glass-navigation.md#local-vs-remote-ssh-glass-url):
   - **Local:** exact `welcome_url` / `pluto_url` (no ask).
   - **Remote SSH:** remember last-good for this session+port → else Glass-probe `http://127.0.0.1:<pluto_port>/` → ask Ports **only if** probe fails.
2. **Reuse or reveal** Glass — [reuse rules](../skills/pluto-session/reference/glass-navigation.md#reuse-vs-reveal) (`cursor-ide-browser` only; never `plugin-browse-browser` / `newTab`).
3. `browser_navigate` to the **landing** (`welcome_url` / resolved origin `/`). Snapshot if needed.
4. **If a notebook was opened / known** (`path` / `notebook_id` from boot): Path B — `browser_snapshot` → `browser_click` that notebook on landing. **Never** cold-navigate `/edit?id=` after MCP open.
5. **Stop** when Glass shows the notebook editor (or landing if `--welcome` / no notebook). Brief confirm; do not ask the user to open a URL.

`--open` is optional **extra** human handoff (OS browser, local only). Agents Glass + Path B via this command is the required seamless path.

Full notes: [skills/pluto-session/reference/styx-start.md](../skills/pluto-session/reference/styx-start.md). Glass already open but broken → **styx-reconnect**.
