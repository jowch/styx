# Changelog

All notable changes to **Styx** are documented here.

[Keep a Changelog](https://keepachangelog.com/en/1.1.0/) · [Semantic Versioning](https://semver.org/spec/v2.0.0.html)

## [Unreleased]

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
- **Bound PlutoMCP:** launcher passes binding kwargs; no foreign-bridge proxy; dynamic `listenany` ports; JSON `/health` (requires PlutoMCP with bound `connect()` on fork `main` / sibling checkout)
- **Glass URL:** agents must use `pluto_session_status.pluto_url` (no hardcoded `:1234`)
- **Remote SSH:** remove `PlutoMCP.serve()` / late-attach fallback; local XOR remote
- **Doctor / lifecycle validation:** binding-aware; two-session concurrency checks
- **Install tree:** drop `generate-manifest.sh`; exclude dev/maintainer scripts from shipped plugin (`pluto-serve`, lifecycle validate/preflight, `record-hero-demo.md`)
- **Julia env:** `Project.toml` `[sources]` pins **PlutoMCP** to [jowch/PlutoMCP.jl](https://github.com/jowch/PlutoMCP.jl) **`main`** at **1.4.1** (`compat = "1.4.1"`); `Manifest.toml` is gitignored (fresh `Pkg.resolve` on first MCP connect)
- **Julia prerequisite:** 1.11+ (required for `[sources]`)

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

- Requires **Cursor 3** and **Julia 1.9+** on `PATH`
- Lifecycle MCP tools may be hidden in the tool picker — agents invoke by name
- After a PlutoMCP upgrade, toggle **pluto** MCP or Reload Window to refresh the cached tool list
