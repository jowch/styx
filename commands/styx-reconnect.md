---
description: Glass/Pluto dropped — auth, Loading cells, stale port — soft reconnect then hard restart
---

# Styx reconnect

Invoke **pluto-session** and follow [skills/pluto-session/reference/reconnect.md](../skills/pluto-session/reference/reconnect.md).

**Soft reconnect first** (landing → click notebook; exact `pluto_url` host). **Hard restart** (`stop_pluto_session` / `start_pluto_session`, or **styx-start** after stop) only when Pluto/MCP is dead or soft reconnect fails.
