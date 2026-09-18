---
description: Clear stale Styx-managed session crumbs — check first, then optional reclaim; never touch user Pluto
---

# Styx cleanup

Invoke **pluto-session** and follow [skills/pluto-session/reference/cleanup.md](../skills/pluto-session/reference/cleanup.md).

**Wire:** `scripts/styx-check-stale.sh` (report; exit 1 if stale) → if `offer_cleanup=yes`, ask once → `--mark-offer` → optional `scripts/styx-cleanup.sh --apply` → continue. Glass/auth → **styx-reconnect**. Boot → **styx-start** (includes this check). Never reclaim unmanaged user Pluto.
