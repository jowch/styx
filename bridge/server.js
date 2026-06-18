#!/usr/bin/env node
/**
 * Dev/fallback HTTP queue for Pluto click packets (Path C only).
 * Primary click delivery: Glass Design Mode → parseDomPath (D13 Path A).
 * Default: http://127.0.0.1:3457
 */

import http from "node:http";
import fs from "node:fs";
import path from "node:path";
import os from "node:os";
import { fileURLToPath } from "node:url";
import { formatPlutoContext } from "../src/dom-resolver.js";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const ROOT = path.resolve(__dirname, "..");
const PORT = Number(process.env.PLUTO_CLICK_PORT) || 3457;
const HOST = process.env.PLUTO_CLICK_HOST || "127.0.0.1";
const QUEUE_PATH =
  process.env.PLUTO_CLICK_QUEUE ||
  path.join(os.homedir(), ".cursor", "pluto-click-queue.json");

const CORS_HEADERS = {
  "Access-Control-Allow-Origin": "*",
  "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
  "Access-Control-Allow-Headers": "Content-Type",
};

function json(res, status, body) {
  const payload = JSON.stringify(body, null, 2);
  res.writeHead(status, {
    ...CORS_HEADERS,
    "Content-Type": "application/json; charset=utf-8",
    "Content-Length": Buffer.byteLength(payload),
  });
  res.end(payload);
}

function text(res, status, body, contentType = "text/plain; charset=utf-8") {
  res.writeHead(status, {
    ...CORS_HEADERS,
    "Content-Type": contentType,
    "Content-Length": Buffer.byteLength(body),
  });
  res.end(body);
}

function ensureQueueFile() {
  const dir = path.dirname(QUEUE_PATH);
  fs.mkdirSync(dir, { recursive: true });
  if (!fs.existsSync(QUEUE_PATH)) {
    fs.writeFileSync(QUEUE_PATH, "[]\n", "utf8");
  }
}

function readQueue() {
  ensureQueueFile();
  try {
    const raw = fs.readFileSync(QUEUE_PATH, "utf8");
    const parsed = JSON.parse(raw);
    return Array.isArray(parsed) ? parsed : [];
  } catch {
    return [];
  }
}

function writeQueue(queue) {
  ensureQueueFile();
  const tmp = `${QUEUE_PATH}.tmp`;
  fs.writeFileSync(tmp, `${JSON.stringify(queue, null, 2)}\n`, "utf8");
  fs.renameSync(tmp, QUEUE_PATH);
}

function readBody(req) {
  return new Promise((resolve, reject) => {
    const chunks = [];
    req.on("data", (chunk) => chunks.push(chunk));
    req.on("end", () => resolve(Buffer.concat(chunks).toString("utf8")));
    req.on("error", reject);
  });
}

function serveStaticFile(res, filePath, contentType) {
  if (!fs.existsSync(filePath)) {
    json(res, 404, { error: "not_found" });
    return;
  }
  const body = fs.readFileSync(filePath, "utf8");
  text(res, 200, body, contentType);
}

const server = http.createServer(async (req, res) => {
  const url = new URL(req.url || "/", `http://${req.headers.host || "localhost"}`);
  const { pathname } = url;

  if (req.method === "OPTIONS") {
    res.writeHead(204, CORS_HEADERS);
    res.end();
    return;
  }

  if (pathname === "/health" && req.method === "GET") {
    json(res, 200, { ok: true, queue_path: QUEUE_PATH });
    return;
  }

  if (pathname === "/click" && req.method === "POST") {
    try {
      const raw = await readBody(req);
      const packet = raw ? JSON.parse(raw) : {};
      if (!packet.cell_id) {
        json(res, 400, { error: "missing_cell_id" });
        return;
      }
      const queue = readQueue();
      queue.push(packet);
      writeQueue(queue);
      json(res, 200, { ok: true, queued: queue.length });
    } catch (err) {
      json(res, 400, { error: "invalid_json", message: String(err.message) });
    }
    return;
  }

  if (pathname === "/click/latest" && req.method === "GET") {
    const queue = readQueue();
    if (queue.length === 0) {
      json(res, 404, { error: "empty_queue" });
      return;
    }
    json(res, 200, queue[queue.length - 1]);
    return;
  }

  if (pathname === "/click/pop" && req.method === "GET") {
    const queue = readQueue();
    if (queue.length === 0) {
      json(res, 404, { error: "empty_queue" });
      return;
    }
    const packet = queue.pop();
    writeQueue(queue);
    json(res, 200, packet);
    return;
  }

  if (pathname === "/click/format" && req.method === "GET") {
    const queue = readQueue();
    if (queue.length === 0) {
      json(res, 404, { error: "empty_queue" });
      return;
    }
    const block = formatPlutoContext(queue[queue.length - 1]);
    text(res, 200, block, "text/plain; charset=utf-8");
    return;
  }

  if (pathname === "/dom-resolver.js" && req.method === "GET") {
    serveStaticFile(
      res,
      path.join(ROOT, "src", "dom-resolver.js"),
      "text/javascript; charset=utf-8"
    );
    return;
  }

  if (pathname === "/inject.js" && req.method === "GET") {
    serveStaticFile(
      res,
      path.join(ROOT, "src", "inject.js"),
      "text/javascript; charset=utf-8"
    );
    return;
  }

  json(res, 404, { error: "not_found" });
});

server.listen(PORT, HOST, () => {
  console.log(`Pluto click bridge listening on http://${HOST}:${PORT}`);
  console.log(`Queue file: ${QUEUE_PATH}`);
});
