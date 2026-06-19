# Changelog

All notable changes to the **Styx** Cursor plugin are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

**Nothing has been released yet.** Target first release: **0.1.0**.

## [Unreleased]

### Added

- **D15** lazy warm lifecycle — [docs/specs/pluto-lifecycle.md](docs/specs/pluto-lifecycle.md); PlutoMCP lifecycle tools implemented
- **Skills:** `pluto-session`, `pluto-workflow`, `pluto-semantics` with progressive-disclosure `reference/` files
- **Docs:** [docs/skill-architecture.md](docs/skill-architecture.md), [eval/SKILL_BASELINE_SCENARIOS.md](eval/SKILL_BASELINE_SCENARIOS.md) (TDD pressure scenarios)
- **PlutoMCP:** `allow_execution` — exit safe preview on open notebook when user asks to run
- `package-plugin.sh` — release tree without dev artifacts
- Cursor plugin: rules, hooks, bundled `mcp.json`, eval harness, Design Mode (D13)

### Changed

- **Rule** — agent-driven lifecycle; thin router to skills (D15)
- **Skills** — CSO descriptions (triggers only); Pluto.jl research in `reference/`; canonical Glass URL `/edit?id=`
- Launcher — `connect()` only (D15); `pluto-serve.sh` dev-only
- Version **0.1.0** pre-release; D15 acceptance signed off 2026-06-18

### Removed

- Path C DOM bridge (`bridge/`, `src/`)
- `commands/pluto-start.md`, legacy `pluto-*-cell` commands — replaced by D15 agent lifecycle + skills

### Known gaps before 0.1.0

- Marketplace install path
- Lifecycle tools not always visible in Cursor MCP tool picker (invoke by name)
- Pure deferred Scenario 0 (stdio-only, no proxy `serve()`) — automated via `scripts/d15-validate-deferred.sh`; manual 0.2/C.1 agent chat checks remain

[Unreleased]: https://github.com/jowch/styx/compare/HEAD...HEAD
