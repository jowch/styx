#!/usr/bin/env tsx
/**
 * Cursor SDK orchestrator for Pluto MCP agent eval.
 * Requires CURSOR_API_KEY. Uses inline MCP (not mcp.json — settingSources: []).
 */

import { spawn, execFile, type ChildProcess } from "node:child_process";
import { createServer } from "node:net";
import {
  copyFileSync,
  mkdirSync,
  mkdtempSync,
  readFileSync,
  writeFileSync,
  rmSync,
} from "node:fs";
import { tmpdir } from "node:os";
import { join, dirname, resolve } from "node:path";
import { fileURLToPath } from "node:url";
import { promisify } from "node:util";
import { Agent, CursorAgentError } from "@cursor/sdk";

const execFileAsync = promisify(execFile);
const __dirname = dirname(fileURLToPath(import.meta.url));

interface Scenario {
  id: string;
  prompt: string;
  fixture: string;
  orchestrator?: {
    workflow_prefix?: boolean;
    max_duration_ms?: number;
  };
  setup?: {
    require_secret_for_access?: boolean;
    launch_browser?: boolean;
  };
  readiness?: {
    cell_id: string;
    output_equals: string;
    timeout_sec?: number;
  };
}

function parseArgs(argv: string[]) {
  const opts: Record<string, string | boolean> = {};
  for (let i = 0; i < argv.length; i++) {
    const a = argv[i];
    if (a === "--all") opts.all = true;
    else if (a.startsWith("--")) {
      const key = a.slice(2);
      const next = argv[i + 1];
      if (next && !next.startsWith("--")) {
        opts[key] = next;
        i++;
      } else {
        opts[key] = true;
      }
    }
  }
  return opts;
}

function plutomcpRoot(): string {
  return resolve(
    process.env.PLUTOMCP_ROOT ??
      join(__dirname, "..", "..", "PlutoMCP.jl"),
  );
}

async function freePort(): Promise<number> {
  return new Promise((resolvePort, reject) => {
    const srv = createServer();
    srv.listen(0, "127.0.0.1", () => {
      const addr = srv.address();
      if (!addr || typeof addr === "string") {
        reject(new Error("freePort failed"));
        return;
      }
      const port = addr.port;
      srv.close(() => resolvePort(port));
    });
    srv.on("error", reject);
  });
}

async function waitHealth(mcpUrl: string, timeoutMs = 60_000): Promise<void> {
  const deadline = Date.now() + timeoutMs;
  while (Date.now() < deadline) {
    try {
      const r = await fetch(`${mcpUrl}/health`);
      if (r.ok) return;
    } catch {
      /* retry */
    }
    await new Promise((r) => setTimeout(r, 500));
  }
  throw new Error(`Health check failed: ${mcpUrl}`);
}

async function mcpCall(
  mcpUrl: string,
  name: string,
  args: Record<string, unknown>,
): Promise<{ isError: boolean; parsed: unknown }> {
  const body = {
    jsonrpc: "2.0",
    id: 1,
    method: "tools/call",
    params: { name, arguments: args },
  };
  const r = await fetch(`${mcpUrl}/call`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
  const resp = (await r.json()) as {
    result?: { isError?: boolean; content?: { text?: string }[] };
  };
  const result = resp.result;
  if (!result) throw new Error(`MCP call failed: ${name}`);
  const text = result.content?.[0]?.text ?? "{}";
  const parsed = JSON.parse(text);
  return { isError: !!result.isError, parsed };
}

async function waitReadiness(
  mcpUrl: string,
  scenario: Scenario,
): Promise<string> {
  const readiness = scenario.readiness;
  const timeoutSec = readiness?.timeout_sec ?? 90;
  const deadline = Date.now() + timeoutSec * 1000;
  while (Date.now() < deadline) {
    const { isError, parsed } = await mcpCall(mcpUrl, "list_notebooks", {});
    if (!isError && Array.isArray(parsed) && parsed.length === 1) {
      const notebookId = (parsed[0] as { notebook_id: string }).notebook_id;
      if (readiness) {
        const cell = await mcpCall(mcpUrl, "read_cell", {
          notebook_id: notebookId,
          cell_id: readiness.cell_id,
        });
        if (
          !cell.isError &&
          (cell.parsed as { output?: string }).output === readiness.output_equals
        ) {
          return notebookId;
        }
      } else {
        return notebookId;
      }
    }
    await new Promise((r) => setTimeout(r, 500));
  }
  throw new Error(`Readiness timeout for scenario ${scenario.id}`);
}

function spawnServe(
  plutomcp: string,
  opts: {
    fixturePath: string;
    plutoPort: number;
    mcpPort: number;
    evalLog: string;
    runId: string;
    setup: Scenario["setup"];
  },
): ChildProcess {
  const reqSecret = opts.setup?.require_secret_for_access ?? false;
  const launchBrowser = opts.setup?.launch_browser ?? false;
  const code = `
using PlutoMCP
PlutoMCP.serve(
    pluto_port = ${opts.plutoPort},
    mcp_port = ${opts.mcpPort},
    notebook = $(JSON.stringify(opts.fixturePath)),
    launch_browser = ${launchBrowser},
    require_secret_for_access = ${reqSecret},
    eval_log = $(JSON.stringify(opts.evalLog)),
    eval_run_id = $(JSON.stringify(opts.runId)),
)
`;
  return spawn("julia", ["--project=" + plutomcp, "-e", code], {
    stdio: "ignore",
    detached: true,
  });
}

function killServe(proc: ChildProcess | null) {
  if (!proc?.pid) return;
  try {
    process.kill(-proc.pid, "SIGTERM");
  } catch {
    try {
      proc.kill("SIGTERM");
    } catch {
      /* already dead */
    }
  }
}

function loadScenario(idOrPath: string): Scenario {
  const plutomcp = plutomcpRoot();
  const path = idOrPath.endsWith(".json")
    ? idOrPath
    : join(plutomcp, "eval", "scenarios", `${idOrPath}.json`);
  return JSON.parse(readFileSync(path, "utf8")) as Scenario;
}

function scenarioFiles(): string[] {
  const dir = join(plutomcpRoot(), "eval", "scenarios");
  return ["stage_and_run", "batch_edit", "read_guard_recovery", "add_cell_placement"].map(
    (id) => join(dir, `${id}.json`),
  );
}

async function runScenario(scenarioPath: string): Promise<boolean> {
  const plutomcp = plutomcpRoot();
  const scenario = loadScenario(scenarioPath);
  const apiKey = process.env.CURSOR_API_KEY;
  if (!apiKey) {
    throw new Error("CURSOR_API_KEY is required for SDK eval runs");
  }

  const fixtureSrc = join(plutomcp, "eval", "fixtures", scenario.fixture);
  const tmpDir = mkdtempSync(join(tmpdir(), "pluto-eval-"));
  const fixturePath = join(tmpDir, scenario.fixture);
  copyFileSync(fixtureSrc, fixturePath);

  const plutoPort = await freePort();
  const mcpPort = await freePort();
  const mcpUrl = `http://127.0.0.1:${mcpPort}`;
  const runId = `sdk-${scenario.id}-${Date.now()}`;
  const resultsDir = join(__dirname, "results", runId);
  mkdirSync(resultsDir, { recursive: true });
  const evalLog = join(resultsDir, "trace.jsonl");

  const proc = spawnServe(plutomcp, {
    fixturePath,
    plutoPort,
    mcpPort,
    evalLog,
    runId,
    setup: scenario.setup,
  });

  try {
    await waitHealth(mcpUrl);
    const notebookId = await waitReadiness(mcpUrl, scenario);

    const prefixPath = join(plutomcp, "eval", "PLUTO_WORKFLOW_PREFIX.md");
    const prefix =
      scenario.orchestrator?.workflow_prefix !== false
        ? readFileSync(prefixPath, "utf8") + "\n\n"
        : "";
    const prompt = prefix + scenario.prompt;

    writeFileSync(
      join(resultsDir, "meta.json"),
      JSON.stringify({ notebook_id: notebookId, run_id: runId, mcp_port: mcpPort, scenario_id: scenario.id }, null, 2),
    );

    const model = process.env.PLUTO_EVAL_MODEL ?? "composer-2.5";
    let result;
    try {
      result = await Agent.prompt(prompt, {
        apiKey,
        model: { id: model },
        local: { cwd: plutomcp, settingSources: [] },
        mcpServers: {
          pluto: { url: `${mcpUrl}/sse` },
        },
      });
    } catch (err) {
      if (err instanceof CursorAgentError) {
        console.error("SDK startup failed:", err.message);
        process.exit(1);
      }
      throw err;
    }

    if (result.status === "error") {
      console.error("Agent run failed:", result.id);
      process.exit(2);
    }

    writeFileSync(
      join(resultsDir, "agent-result.json"),
      JSON.stringify({ status: result.status, id: result.id, model }, null, 2),
    );

    const { stdout } = await execFileAsync(
      "julia",
      [
        "--project=" + plutomcp,
        join(plutomcp, "eval", "score.jl"),
        "--scenario",
        scenarioPath.endsWith(".json")
          ? scenarioPath
          : join(plutomcp, "eval", "scenarios", `${scenario.id}.json`),
        "--log",
        evalLog,
        "--mcp-url",
        mcpUrl,
        "--meta",
        join(resultsDir, "meta.json"),
      ],
      { timeout: 120_000 },
    );

    const report = JSON.parse(stdout);
    writeFileSync(join(resultsDir, "summary.json"), JSON.stringify(report, null, 2));
    console.log(
      `[${scenario.id}] outcome=${report.outcome.pass} trace=${report.trace.pass} → ${resultsDir}`,
    );
    return report.outcome.pass === true;
  } finally {
    killServe(proc);
    rmSync(tmpDir, { recursive: true, force: true });
  }
}

async function main() {
  const opts = parseArgs(process.argv.slice(2));
  if (opts.all) {
    let passed = 0;
    for (const f of scenarioFiles()) {
      if (await runScenario(f)) passed++;
    }
    console.log(`SDK eval: ${passed}/${scenarioFiles().length} scenarios passed (outcome)`);
    if (passed < scenarioFiles().length) process.exit(1);
    return;
  }
  const scenario = (opts.scenario as string) ?? "stage_and_run";
  const plutomcp = plutomcpRoot();
  const path = scenario.endsWith(".json")
    ? scenario
    : join(plutomcp, "eval", "scenarios", `${scenario}.json`);
  const ok = await runScenario(path);
  if (!ok) process.exit(1);
}

main().catch((err) => {
  console.error(err);
  process.exit(1);
});
