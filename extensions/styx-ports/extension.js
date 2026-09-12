// Spike (#15): thin remote EH companion — Cursor owns auto-forward; we only read
// the client URI via vscode.env.asExternalUri. Never invent ports.
"use strict";

const fs = require("fs");
const fsp = require("fs/promises");
const os = require("os");
const path = require("path");
const crypto = require("crypto");

/** @type {typeof import("vscode") | null} */
let vscode = null;
function vs() {
  if (!vscode) {
    vscode = require("vscode");
  }
  return vscode;
}

const SCHEMA_VERSION = 1;

/**
 * @param {NodeJS.ProcessEnv} [env]
 * @returns {{ key: number, source: string } | null}
 */
function resolveWindowKey(env = process.env) {
  const pid = env.VSCODE_PID || "";
  if (/^\d+$/.test(pid)) {
    return { key: Number(pid), source: "VSCODE_PID" };
  }
  const hook = env.VSCODE_IPC_HOOK_CLI;
  if (!hook || !String(hook).trim()) {
    return null;
  }
  let token = path.basename(String(hook));
  if (token.endsWith(".sock")) {
    token = token.slice(0, -".sock".length);
  }
  if (!token) {
    return null;
  }
  const digest = crypto.createHash("sha256").update(token, "utf8").digest("hex");
  return { key: parseInt(digest.slice(0, 15), 16), source: "VSCODE_IPC_HOOK_CLI" };
}

/**
 * @param {NodeJS.ProcessEnv} [env]
 * @returns {string}
 */
function resolveRuntimeDir(env = process.env) {
  if (env.STYX_RUNTIME_DIR) {
    return env.STYX_RUNTIME_DIR;
  }
  const uid = typeof process.getuid === "function" ? process.getuid() : os.userInfo().uid;
  if (env.XDG_RUNTIME_DIR) {
    return path.join(env.XDG_RUNTIME_DIR, `styx-${uid}`);
  }
  const tmp = env.TMPDIR || os.tmpdir();
  return path.join(tmp, `styx-${uid}`);
}

/**
 * @param {string} runtimeDir
 * @param {number} windowKey
 */
function bindingPath(runtimeDir, windowKey) {
  return path.join(runtimeDir, "windows", `${windowKey}.json`);
}

/**
 * @param {string} runtimeDir
 * @param {number} windowKey
 */
function sidecarPath(runtimeDir, windowKey) {
  return path.join(runtimeDir, "windows", `${windowKey}.client.json`);
}

/**
 * @param {string} hostUrl
 * @returns {Promise<string>}
 */
async function resolveClientUrl(hostUrl) {
  const v = vs();
  const external = await v.env.asExternalUri(v.Uri.parse(hostUrl));
  // Prefer exact string form (preserve authority Cursor returns; may not be localhost).
  return external.toString(true);
}

/**
 * @param {string} filePath
 * @param {object} obj
 */
async function atomicWriteJson(filePath, obj) {
  await fsp.mkdir(path.dirname(filePath), { recursive: true });
  const tmp = path.join(
    path.dirname(filePath),
    `.${path.basename(filePath)}.${process.pid}.${Date.now()}.tmp`
  );
  await fsp.writeFile(tmp, JSON.stringify(obj, null, 2), "utf8");
  await fsp.rename(tmp, filePath);
}

/**
 * @param {string} hostUrl
 * @param {string} clientUrl
 * @param {string} runtimeDir
 * @param {number} windowKey
 * @param {string} source
 */
async function writeSidecar(hostUrl, clientUrl, runtimeDir, windowKey, source) {
  const payload = {
    schema_version: SCHEMA_VERSION,
    host_url: hostUrl,
    client_url: clientUrl,
    resolved_at: new Date().toISOString(),
    window_key: windowKey,
    window_key_source: source,
    remote_name: vs().env.remoteName || null,
  };
  await atomicWriteJson(sidecarPath(runtimeDir, windowKey), payload);
  return payload;
}

/**
 * Host pluto_url from binding JSON or explicit argument.
 * @param {string | undefined} hostUrlArg
 * @param {string} runtimeDir
 * @param {number} windowKey
 * @returns {Promise<string | undefined>}
 */
async function resolveHostUrl(hostUrlArg, runtimeDir, windowKey) {
  if (hostUrlArg && String(hostUrlArg).trim()) {
    return String(hostUrlArg).trim();
  }
  const bp = bindingPath(runtimeDir, windowKey);
  try {
    const raw = await fsp.readFile(bp, "utf8");
    const data = JSON.parse(raw);
    const port = data.pluto_port;
    if (data.pluto === "running" && typeof port === "number" && port > 0) {
      return `http://127.0.0.1:${port}`;
    }
  } catch {
    // no binding yet
  }
  return undefined;
}

/**
 * @param {string | undefined} hostUrlArg
 * @returns {Promise<string | undefined>}
 */
async function resolveAndWrite(hostUrlArg) {
  const identity = resolveWindowKey();
  const v = vs();
  if (!identity) {
    v.window.showErrorMessage(
      "Styx Ports: no VSCODE_PID or VSCODE_IPC_HOOK_CLI — cannot locate window binding."
    );
    return undefined;
  }
  const runtimeDir = resolveRuntimeDir();
  let hostUrl = await resolveHostUrl(hostUrlArg, runtimeDir, identity.key);
  if (!hostUrl) {
    hostUrl = await v.window.showInputBox({
      prompt: "Host pluto_url (from pluto_session_status)",
      placeHolder: "http://127.0.0.1:<pluto_port>",
    });
  }
  if (!hostUrl) {
    return undefined;
  }
  try {
    const clientUrl = await resolveClientUrl(hostUrl);
    await writeSidecar(hostUrl, clientUrl, runtimeDir, identity.key, identity.source);
    return clientUrl;
  } catch (err) {
    const msg = err instanceof Error ? err.message : String(err);
    v.window.showErrorMessage(`Styx Ports: asExternalUri failed: ${msg}`);
    return undefined;
  }
}

/**
 * Auto-resolve when binding shows a running Pluto (no invented URLs — omit on failure).
 * @param {import("vscode").ExtensionContext} ctx
 */
function watchBinding(ctx) {
  const identity = resolveWindowKey();
  if (!identity) {
    return;
  }
  const runtimeDir = resolveRuntimeDir();
  const bp = bindingPath(runtimeDir, identity.key);
  const windowsDir = path.dirname(bp);

  let lastHost = null;
  let inflight = false;

  const maybeResolve = async () => {
    if (inflight) {
      return;
    }
    inflight = true;
    try {
      const hostUrl = await resolveHostUrl(undefined, runtimeDir, identity.key);
      if (!hostUrl || hostUrl === lastHost) {
        return;
      }
      const clientUrl = await resolveClientUrl(hostUrl);
      await writeSidecar(hostUrl, clientUrl, runtimeDir, identity.key, identity.source);
      lastHost = hostUrl;
    } catch {
      // Fail closed: leave sidecar absent / stale unmatched; MCP omits client_url.
    } finally {
      inflight = false;
    }
  };

  try {
    fs.mkdirSync(windowsDir, { recursive: true });
  } catch {
    // ignore
  }

  const v = vs();
  const watcher = v.workspace.createFileSystemWatcher(
    new v.RelativePattern(windowsDir, `${identity.key}.json`)
  );
  ctx.subscriptions.push(watcher);
  ctx.subscriptions.push(watcher.onDidCreate(() => void maybeResolve()));
  ctx.subscriptions.push(watcher.onDidChange(() => void maybeResolve()));
  // Also poll lightly — binding writes may not always fire create/change in all EH setups.
  const timer = setInterval(() => void maybeResolve(), 5000);
  ctx.subscriptions.push({ dispose: () => clearInterval(timer) });
  void maybeResolve();
}

/**
 * @param {import("vscode").ExtensionContext} ctx
 */
function activate(ctx) {
  const v = vs();
  ctx.subscriptions.push(
    v.commands.registerCommand("styx.resolvePlutoClientUrl", async (hostUrl) => {
      const clientUrl = await resolveAndWrite(
        typeof hostUrl === "string" ? hostUrl : undefined
      );
      if (clientUrl) {
        v.window.showInformationMessage(`Styx client URL: ${clientUrl}`);
      }
      return clientUrl;
    })
  );
  watchBinding(ctx);
}

function deactivate() {}

module.exports = { activate, deactivate, resolveWindowKey, resolveRuntimeDir, sidecarPath };
