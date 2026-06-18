/**
 * Pluto click resolution and context packet utilities.
 *
 * **Path A (primary, D13):** `parseDomPath`, `buildContextPacket`, `formatPlutoContext`
 *   — parse Glass Design Mode `dom_path` from hook prompt.
 *
 * **Path C (dev/fallback only):** `resolvePlutoClick` — used by inject.js + dev queue.
 *   Not production click UX; see docs/specs/dom-bridge.md.
 */

const RE_CELL_ID = /pluto-cell#([0-9a-f-]+)/i;
const RE_NOTEBOOK_ID = /pluto-notebook#([0-9a-f-]+)/i;

const VALID_INTENTS = new Set(["read", "edit", "explain", "refactor"]);

/**
 * Resolve a click event to Pluto cell context using composedPath().
 * @param {MouseEvent} event
 * @returns {{ ok: true, cell_id: string, notebook_id: string|null, in_output: boolean, in_input: boolean, inside_iframe: boolean, inside_shadow_root: boolean, target_tag: string|null, text_snippet: string } | { ok: false, reason: string }}
 */
export function resolvePlutoClick(event) {
  const path = event.composedPath();
  const cell = path.find(
    (el) => el instanceof Element && el.tagName === "PLUTO-CELL" && el.id
  );
  if (!cell) return { ok: false, reason: "no_pluto_cell" };

  const notebook =
    path.find(
      (el) => el instanceof Element && el.tagName === "PLUTO-NOTEBOOK" && el.id
    ) ?? document.querySelector("pluto-notebook");

  const inside_iframe = event.target?.ownerDocument !== document;
  if (inside_iframe) {
    return { ok: false, reason: "inside_iframe" };
  }

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

/**
 * Build a context packet from a resolved click (or parseDomPath result).
 * @param {object} resolved
 * @param {string} [intent="read"]
 */
export function buildContextPacket(resolved, intent = "read") {
  if (!resolved?.ok) {
    throw new Error(resolved?.reason ?? "unresolved_click");
  }
  const safeIntent = VALID_INTENTS.has(intent) ? intent : "read";
  return {
    notebook_id: resolved.notebook_id,
    cell_id: resolved.cell_id,
    in_output: Boolean(resolved.in_output),
    in_input: Boolean(resolved.in_input),
    inside_iframe: Boolean(resolved.inside_iframe),
    inside_shadow_root: Boolean(resolved.inside_shadow_root),
    target_tag: resolved.target_tag ?? null,
    text_snippet: resolved.text_snippet ?? "",
    intent: safeIntent,
    screenshot_path: null,
    captured_at: new Date().toISOString(),
  };
}

/**
 * Extract notebook_id and cell_id from Design Mode dom_path (Path A / D13).
 * @param {string} domPathString
 */
export function parseDomPath(domPathString) {
  if (!domPathString || typeof domPathString !== "string") {
    return { ok: false, reason: "invalid_dom_path" };
  }
  const cellMatch = domPathString.match(RE_CELL_ID);
  const notebookMatch = domPathString.match(RE_NOTEBOOK_ID);
  if (!cellMatch) {
    return { ok: false, reason: "no_pluto_cell_in_dom_path" };
  }
  return {
    ok: true,
    cell_id: cellMatch[1],
    notebook_id: notebookMatch?.[1] ?? null,
    in_output: true,
    in_input: false,
    inside_iframe: false,
    inside_shadow_root: false,
    target_tag: null,
    text_snippet: "",
  };
}

const INTENT_HINTS = {
  read: "User selected this cell. read_cell for detail; read_notebook_code for full context.",
  edit: "User wants to edit this cell. read_cell first, then stage edits with edit_cell (run_after=false); submit_changes when ready.",
  explain:
    "User wants an explanation of this cell. read_cell for code/output; read_notebook_code for dependencies.",
  refactor:
    "User wants to refactor this cell. read_cell + read_notebook_code before structural edits.",
};

/**
 * Format a context packet as an @pluto-context block for chat paste.
 * @param {object} packet
 */
export function formatPlutoContext(packet) {
  const intent = VALID_INTENTS.has(packet?.intent) ? packet.intent : "read";
  const lines = [
    "@pluto-context",
    `notebook_id: ${packet.notebook_id ?? "(missing — use list_notebooks or URL ?id=)"}`,
    `cell_id: ${packet.cell_id}`,
    `intent: ${intent}`,
    `in_output: ${Boolean(packet.in_output)}`,
    `in_input: ${Boolean(packet.in_input)}`,
  ];
  if (packet.inside_shadow_root) {
    lines.push("inside_shadow_root: true");
  }
  lines.push("---");
  lines.push(INTENT_HINTS[intent] ?? INTENT_HINTS.read);
  if (packet.text_snippet?.trim()) {
    lines.push("");
    lines.push(
      `Selection snippet: ${packet.text_snippet.trim().slice(0, 200)}`
    );
  }
  return lines.join("\n");
}

/** User-visible rejection text for inject toasts and dev UX. */
export function rejectionMessage(reason) {
  const messages = {
    no_pluto_cell:
      "No Pluto cell in click path — click inside a cell (code or output), not header/chrome.",
    inside_iframe:
      "Inside plot/HTML iframe — click the frame border in the cell output, or paste @pluto-context manually.",
    invalid_dom_path: "Invalid dom_path string.",
    no_pluto_cell_in_dom_path:
      "No pluto-cell# id in dom_path — re-click the cell or use @pluto-context.",
  };
  return messages[reason] ?? `Click rejected: ${reason}`;
}
