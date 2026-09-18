---
description: Glass/Pluto dropped — auth, Loading cells, stale port — soft reconnect then hard restart
---

# Styx reconnect

Invoke **pluto-session** and follow [skills/pluto-session/reference/reconnect.md](../skills/pluto-session/reference/reconnect.md).

**Soft reconnect first** (resolve Glass URL → landing → click notebook). Remote: remember → same-port probe → ask Ports only if needed. **Hard restart** then **styx-start** (boot + Glass ready in one turn) only when Pluto/MCP is dead or soft reconnect fails.
