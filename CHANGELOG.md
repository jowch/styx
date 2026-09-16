# Changelog

All notable changes to **Styx** are documented here.

[Keep a Changelog](https://keepachangelog.com/en/1.1.0/) · [Semantic Versioning](https://semver.org/spec/v2.0.0.html)

Each release is a git tag and GitHub Release; the installer targets the latest release by default. PlutoMCP is pinned by commit SHA in `Project.toml`.

## [Unreleased]

### Added

- **Glass viewId cache:** hooks persist `(session_id, notebook_id | _landing) → { viewId, url }` in `$STYX_RUNTIME_DIR/sessions/<session_id>/glass-views.json` after successful `cursor-ide-browser` navigate/snapshot/lock (and `browser_tabs` list when a Pluto URL matches, including live prose `Open tabs:` lines). Agents **Read that file** before Glass work — Cursor does not put `sessionStart` `additional_context` in the model (parent or Task child). Never `newTab` / `action: "new"`. Skill: `pluto-session` glass-navigation.

### Fixed

- **Glass viewId cache:** do not persist a `viewId` when `cursor-ide-browser` returns `Browser view not found` or `No browser tab available` as content text with `isError: false`. Those failures previously poisoned `_landing` from `tool_input`.
- **Glass view map delivery:** `sessionStart` still emits “Known Glass views”, but Cursor does not put that `additional_context` in the model (parent or Task child). Skills/rules now require a **Read** of `glass-views.json`; the hook text includes the file path and omits `position: "active"`.
- **`browser_tabs` list refresh:** `iter_tab_matches` parses live prose (`Open tabs:\n[0] … (viewId: hex)`), not only `{tabs:[…]}` JSON.

### Changed

- **Task child Glass:** Agents Glass (`cursor-ide-browser`) is parent-only. Child empty `browser_tabs` + cached `viewId` → “Browser view not found” is expected Cursor isolation — do not `newTab`. Skills, workflow rule, and eval C4/D4 updated.

- **Glass navigate:** parent **reuse** is `browser_navigate({ url, viewId })` with `position` omitted (tab navigation without minting siblings). Parent **reveal** may pass `position: "active"` **once** when Glass is closed/hidden, the user says it did not open, or this is the first visible open and tabs are empty — that can mint a sibling workbench pane via `_reopenBrowserTab`; record the result `viewId` and omit `position` afterward. Never `newTab` / `action: "new"` to reveal. Task children still never pass `position` or `newTab`.

- **Install target:** `install.sh` / `install-styx.sh` default to the latest GitHub Release tag (resolved via `releases/latest`) instead of `main`; `STYX_REF=main` installs the development tip. Doctor no longer prints a redundant `STYX_REF=<tag>` hint.

## [0.2.2] — 2026-09-14

### Changed

- **PlutoMCP pin:** `Project.toml` `[sources]` now pins [jowch/PlutoMCP.jl](https://github.com/jowch/PlutoMCP.jl) commit **`e840947c5d46f05c702480ada8df1874255cd5ca`** (PlutoMCP [#7](https://github.com/jowch/PlutoMCP.jl/pull/7) control bridge refuses browser-origin / non-loopback requests; [#8](https://github.com/jowch/PlutoMCP.jl/pull/8) `pending_run` no longer clears before cells run, safe preview keeps it with `execution_blocked::`, orphan ids pruned). Reference eval gate passes at this pin.

## [0.2.1] — 2026-09-12

### Fixed

- **`pending_run` stop hook spam ([#17](https://github.com/jowch/styx/pull/17)):** fail quiet on MCP unreachable / unexpected `list_notebooks` payload / no session — only warn when `pending_run` is positively non-empty (aligns with Phase 5 / D15 silent-when-unverifiable intent)
- **Remote SSH MCP identity ([#13](https://github.com/jowch/styx/issues/13) / [#14](https://github.com/jowch/styx/pull/14)):** bound launcher / hooks / doctor resolve a window key from `VSCODE_PID` when set, else hash the UUID basename of `VSCODE_IPC_HOOK_CLI` → Int for PlutoMCP `cursor_host_pid`; doctor **FAIL**s when neither is available (no shared-port fallback)

### Changed

- **Remote SSH Glass Ports ask ([#15](https://github.com/jowch/styx/issues/15) / [#18](https://github.com/jowch/styx/pull/18)):** under Remote SSH, agent asks once per session for the Cursor **Ports** forwarded/local port for remote `pluto_port` before opening Glass; local sessions keep host `pluto_url` with no ask
- **Docs:** dedicated README **Update** section (curl one-liner / `./scripts/update.sh`) plus force Julia env refresh (`rm` marker/Manifest + `PLUTOMCP_ENV_FORCE=1`); install guide + styx-setup skill aligned ([#12](https://github.com/jowch/styx/pull/12))
- **Safe preview fast path:** prefer `allow_execution(run_notebook=false)` then `submit_changes` / `execute_cell` for staged cells when exiting Safe preview after edits (avoids default full-notebook restart/run); Glass **Run notebook code** and default `allow_execution` still valid ([#10](https://github.com/jowch/styx/pull/10))
- **Remote SSH skill:** document window identity (`VSCODE_PID` / `VSCODE_IPC_HOOK_CLI`) and doctor vs MCP-child env asymmetry
- **Julia env:** `Project.toml` `[sources]` pins **PlutoMCP** to [jowch/PlutoMCP.jl](https://github.com/jowch/PlutoMCP.jl) commit **`1b88eb430839a680cefdd46f8cd9a8317857268f`** (0.2.0 pin + PlutoMCP [#5](https://github.com/jowch/PlutoMCP.jl/pull/5) Safe-preview AGENTS docs; package still **1.4.1**)

### Notes

- Upgraders: re-run the install one-liner. Force Julia env refresh (`PLUTOMCP_ENV_FORCE=1` or wipe `.julia-env-instantiated` + `Manifest.toml`) to pick up the new PlutoMCP pin. Toggle **pluto** MCP or Reload Window after upgrade.

## [0.2.0] — 2026-09-11

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
