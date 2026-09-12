# Changelog

All notable changes to **Styx** are documented here.

[Keep a Changelog](https://keepachangelog.com/en/1.1.0/) · [Semantic Versioning](https://semver.org/spec/v2.0.0.html)

## [Unreleased]

### Added

- **Styx Ports companion (spike, [#15](https://github.com/jowch/styx/issues/15)):** `extensions/styx-ports/` + `scripts/install-styx-ports.sh` — remote EH uses `vscode.env.asExternalUri` (Cursor auto-forward) and writes `windows/<key>.client.json`; optional `client_url` on `pluto_session_status` when PlutoMCP reads a matching sidecar

### Fixed

- **Remote SSH MCP identity ([#13](https://github.com/jowch/styx/issues/13)):** bound launcher / hooks / doctor resolve a window key from `VSCODE_PID` when set, else hash the UUID basename of `VSCODE_IPC_HOOK_CLI` → Int for PlutoMCP `cursor_host_pid`; doctor **FAIL**s when neither is available (no shared-port fallback)

### Changed

- **Remote SSH URL guidance ([#15](https://github.com/jowch/styx/issues/15)):** scrub invented Ports lore (`51708`, `remote_forward_unresolved`); Glass prefers host `pluto_url`; laptop handoff uses optional `client_url` only when resolved — never invent remaps
- **Docs:** dedicated README **Update** section (curl one-liner / `./scripts/update.sh`) plus force Julia env refresh (`rm` marker/Manifest + `PLUTOMCP_ENV_FORCE=1`); install guide + styx-setup skill aligned
- **Safe preview fast path:** prefer `allow_execution(run_notebook=false)` then `submit_changes` / `execute_cell` for staged cells when exiting Safe preview after edits (avoids default full-notebook restart/run); Glass **Run notebook code** and default `allow_execution` still valid ([#3](https://github.com/jowch/styx/issues/3) polish)
- **Remote SSH skill:** document window identity (`VSCODE_PID` / `VSCODE_IPC_HOOK_CLI`) and doctor vs MCP-child env asymmetry

## [0.2.0] — 2026-09-11

Install channel: default curl uses **`STYX_REF=main`** (no `v0.2.0` git tag / no GitHub Release). Fresh installs from `main` after this merge get 0.2.0 content. PlutoMCP is pinned by commit SHA (no PlutoMCP tag).

### Fixed

- **Remote SSH Glass tab reuse ([#4](https://github.com/jowch/styx/issues/4)):** housekeeping close — work shipped in [#7](https://github.com/jowch/styx/pull/7)

### Added

- **Agent control rubric:** `eval/agent-control/` checklist + scored rubric + scorecard; parent→subagent protocol and skill-improvement feedback loop for grading Pluto skill/MCP use

- **Independent Styx sessions:** one Cursor window owns one PlutoMCP/Pluto; concurrent windows get distinct ports and session nonces
- **Window binding:** launcher requires `VSCODE_PID`; hooks resolve `STYX_RUNTIME_DIR/windows/<pid>.json` and send `X-Styx-Session-ID`
- **Notebook path leases:** two bound sessions cannot open the same canonical `.jl` (`notebook_in_use`)
- **Hook tests:** `eval/test_session_binding.py`
- **Demo notebook:** `examples/styx-demo.jl` — reactive sinc plot for README and hero recording
- **README:** B-primary curation, hero video embed, demo notebook section
- **Recording guide:** `scripts/record-hero-demo.md`
- **Remote SSH:** start Pluto on the SSH host; Cursor auto-forwards Ports. Skill: `skills/pluto-session/reference/remote-ssh.md`

### Changed

- **pluto-workflow / pluto-semantics:** `edit-loop.md` and related skill examples show `submit_changes(wait_for_completion=false)` (align with SKILL prefer-false / [#3](https://github.com/jowch/styx/issues/3))
- **Safe preview:** agents exit the gate themselves (Glass **Run notebook code** or `allow_execution`) when outputs need to be live — not remind-only; skills + workflow rule + AGENTS aligned
- **Glass / Remote SSH ([#4](https://github.com/jowch/styx/issues/4)):** tab reuse (no `newTab` by default); host `pluto_url` vs Ports client URL; scrub leftover hardcoded `:1234` guidance in `AGENTS.md`
- **pluto-workflow:** prefer `submit_changes(wait_for_completion=false)` on stdio-bound sessions ([#3](https://github.com/jowch/styx/issues/3) mitigation)
- **Bound PlutoMCP:** launcher passes binding kwargs; no foreign-bridge proxy; dynamic `listenany` ports; JSON `/health` (requires PlutoMCP with bound `connect()` at the pinned fork SHA / sibling checkout)
- **Glass URL:** agents must use `pluto_session_status.pluto_url` (no hardcoded `:1234`)
- **Remote SSH:** remove `PlutoMCP.serve()` / late-attach fallback; local XOR remote
- **Doctor / lifecycle validation:** binding-aware; two-session concurrency checks
- **Install tree:** drop `generate-manifest.sh`; exclude dev/maintainer scripts from shipped plugin (`pluto-serve`, lifecycle validate/preflight, `record-hero-demo.md`)
- **Julia env:** `Project.toml` `[sources]` pins **PlutoMCP** to [jowch/PlutoMCP.jl](https://github.com/jowch/PlutoMCP.jl) commit **`26c4cfbc4a852fadce409dbe94862d14637a175a`** (fork tip at cut; package still **1.4.1**, `compat = "1.4.1"`); `Manifest.toml` is gitignored (fresh `Pkg.resolve` on first MCP connect)
- **Julia prerequisite:** 1.11+ (required for `[sources]`)

### Notes

- **No Styx `v0.2.0` tag / no GitHub Release** — `main` is the install channel for this content.
- **No PlutoMCP tag** — pin by SHA only; includes session binding, wait defaults flip, and PlutoMCP #4 stdio-stall polish.
- Upgraders: re-run the install one-liner, then force Julia env refresh (`PLUTOMCP_ENV_FORCE=1` or wipe `.julia-env-instantiated` + `Manifest.toml`) to pick up the new pin. Toggle **pluto** MCP or Reload Window after upgrade.

## [0.1.0] — 2026-06-21

First release. Cursor 3 plugin for Pluto.jl notebooks via [PlutoMCP.jl](https://github.com/jowch/PlutoMCP.jl).

### Added

- **Install:** `curl | bash` → `~/.cursor/plugins/local/styx/`; re-run or `scripts/update.sh` to update
- **styx-setup** skill, **styx-doctor** — Julia prerequisite and MCP health checks
- **pluto-session**, **pluto-workflow**, **pluto-semantics** — bootstrap, cell edits, cell grammar
- Glass **Design Mode** click context → `resolve_pluto_context` / `read_cell`
- Deferred Pluto lifecycle — MCP `connect()` at launch; full stack on notebook intent
- Read-before-edit hooks and `pending_run` stop warning
- Plugin logo (`assets/styx-logo.svg`)

### Notes

- Shipped requiring **Cursor 3** and Julia on `PATH` (historical note said 1.9+; **current tree requires Julia 1.11+** for `[sources]`)
- Lifecycle MCP tools may be hidden in the tool picker — agents invoke by name
- After a PlutoMCP upgrade, toggle **pluto** MCP or Reload Window to refresh the cached tool list
