/**
 * Pluto click bridge — **dev/fallback only** (Path C). Not production UX.
 *
 * Primary click delivery is D13 Path A: Glass Design Mode → parseDomPath(dom_path).
 * Use this for local packet testing before Phase 4 plugin hooks exist.
 *
 * Usage:
 * 1. Start the dev queue: `npm run bridge` (default http://127.0.0.1:3457)
 * 2. Open a live Pluto notebook tab from PlutoMCP.serve()
 * 3. Paste this file into devtools console (or fetch from bridge):
 *      fetch('http://127.0.0.1:3457/inject.js').then(r => r.text()).then(eval)
 * 4. Click a cell — toast confirms capture or rejection
 * 5. Pull packet: `curl http://127.0.0.1:3457/click/format`
 *
 * Resolver logic mirrors src/dom-resolver.js — keep in sync when editing.
 */
(function plutoClickBridgeInject() {
  const BRIDGE_URL =
    (typeof window !== "undefined" && window.PLUTO_CLICK_BRIDGE_URL) ||
    "http://127.0.0.1:3457";
  const CLICK_ENDPOINT = `${BRIDGE_URL.replace(/\/$/, "")}/click`;
  const DEFAULT_INTENT = "read";

  function resolvePlutoClick(event) {
    const path = event.composedPath();
    const cell = path.find(
      (el) => el instanceof Element && el.tagName === "PLUTO-CELL" && el.id
    );
    if (!cell) return { ok: false, reason: "no_pluto_cell" };

    const notebook =
      path.find(
        (el) =>
          el instanceof Element && el.tagName === "PLUTO-NOTEBOOK" && el.id
      ) ?? document.querySelector("pluto-notebook");

    const inside_iframe = event.target?.ownerDocument !== document;
    if (inside_iframe) return { ok: false, reason: "inside_iframe" };

    return {
      ok: true,
      cell_id: cell.id,
      notebook_id:
        notebook?.id ?? new URLSearchParams(location.search).get("id"),
      in_output: path.some(
        (el) => el instanceof Element && el.tagName === "PLUTO-OUTPUT"
      ),
      in_input: path.some(
        (el) => el instanceof Element && el.tagName === "PLUTO-INPUT"
      ),
      inside_iframe: false,
      inside_shadow_root: path.some((el) => el instanceof ShadowRoot),
      target_tag: event.target?.tagName ?? null,
      text_snippet: (event.target?.textContent ?? "").slice(0, 500),
    };
  }

  function buildContextPacket(resolved, intent = DEFAULT_INTENT) {
    if (!resolved?.ok) throw new Error(resolved?.reason ?? "unresolved_click");
    return {
      notebook_id: resolved.notebook_id,
      cell_id: resolved.cell_id,
      in_output: Boolean(resolved.in_output),
      in_input: Boolean(resolved.in_input),
      inside_iframe: Boolean(resolved.inside_iframe),
      inside_shadow_root: Boolean(resolved.inside_shadow_root),
      target_tag: resolved.target_tag ?? null,
      text_snippet: resolved.text_snippet ?? "",
      intent,
      screenshot_path: null,
      captured_at: new Date().toISOString(),
    };
  }

  const REJECTION_MESSAGES = {
    no_pluto_cell:
      "No Pluto cell — click inside a cell (code or output), not header/chrome.",
    inside_iframe:
      "Inside plot/HTML iframe — click the frame border, or paste @pluto-context manually.",
  };

  function showToast(message, isError) {
    const id = "pluto-click-bridge-toast";
    let el = document.getElementById(id);
    if (!el) {
      el = document.createElement("div");
      el.id = id;
      Object.assign(el.style, {
        position: "fixed",
        bottom: "24px",
        right: "24px",
        zIndex: "2147483647",
        maxWidth: "420px",
        padding: "12px 16px",
        borderRadius: "8px",
        fontFamily: "system-ui, sans-serif",
        fontSize: "14px",
        lineHeight: "1.4",
        boxShadow: "0 4px 24px rgba(0,0,0,0.18)",
        transition: "opacity 0.2s ease",
        pointerEvents: "none",
      });
      document.body.appendChild(el);
    }
    el.textContent = message;
    el.style.background = isError ? "#fde8e8" : "#e8f5e9";
    el.style.color = isError ? "#8b1a1a" : "#1b5e20";
    el.style.border = isError ? "1px solid #f5c2c2" : "1px solid #a5d6a7";
    el.style.opacity = "1";
    clearTimeout(el._hideTimer);
    el._hideTimer = setTimeout(() => {
      el.style.opacity = "0";
    }, 3500);
  }

  function isPlutoReady() {
    const editor = document.querySelector("pluto-editor");
    return Boolean(editor && !editor.classList.contains("loading"));
  }

  if (!isPlutoReady()) {
    showToast(
      "Pluto editor not ready — open a live notebook (pluto-editor, not .loading).",
      true
    );
    return;
  }

  if (window.__plutoClickBridgeActive) {
    showToast("Pluto click bridge already active on this tab.", false);
    return;
  }

  async function postPacket(packet) {
    const res = await fetch(CLICK_ENDPOINT, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(packet),
    });
    if (!res.ok) {
      const detail = await res.text().catch(() => "");
      throw new Error(`Bridge ${res.status}${detail ? `: ${detail}` : ""}`);
    }
    return res.json();
  }

  function onClick(event) {
    if (!isPlutoReady()) return;

    const resolved = resolvePlutoClick(event);
    if (!resolved.ok) {
      const msg =
        REJECTION_MESSAGES[resolved.reason] ??
        `Click rejected: ${resolved.reason}`;
      showToast(msg, true);
      return;
    }

    const packet = buildContextPacket(resolved, DEFAULT_INTENT);

    postPacket(packet)
      .then(() => {
        const where = packet.in_input
          ? "input"
          : packet.in_output
            ? "output"
            : "cell";
        showToast(
          `Captured ${where} · cell ${packet.cell_id.slice(0, 8)}…`,
          false
        );
      })
      .catch((err) => {
        showToast(
          `Bridge unreachable (${CLICK_ENDPOINT}) — is npm run bridge running?`,
          true
        );
        console.error("[pluto-click-bridge]", err);
      });
  }

  document.addEventListener("click", onClick, true);
  window.__plutoClickBridgeActive = true;
  window.__plutoClickBridgeTeardown = () => {
    document.removeEventListener("click", onClick, true);
    delete window.__plutoClickBridgeActive;
    delete window.__plutoClickBridgeTeardown;
    showToast("Pluto click bridge deactivated.", false);
  };

  showToast("Pluto click bridge active — click a cell.", false);
  console.info(
    "[pluto-click-bridge] Active. Teardown: __plutoClickBridgeTeardown()"
  );
})();
