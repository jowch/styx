---
description: Clear stale Styx/PlutoMCP runtime crumbs — dead bindings, sessions, leases — after stop; never nuke unrelated Julias
---

# Styx cleanup

Invoke **pluto-session** and follow [skills/pluto-session/reference/cleanup.md](../skills/pluto-session/reference/cleanup.md).

**Ladder:** status → `stop_pluto_session` (managed) → clear stale `windows/*` / `sessions/*` / notebook leases → optional orphan kill **only** when clearly ours. Glass/auth/WS issues → **styx-reconnect** first. Fresh boot → **styx-start** (or `start_pluto_session`). Prefer `scripts/styx-cleanup.sh` (dry-run default) for runtime crumbs.
