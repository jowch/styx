# Changelog

All notable changes to the **Styx** Cursor plugin are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

**Nothing has been released yet.** Target first release: **0.1.0**.

## [Unreleased]

### Added

- **D15** lazy warm lifecycle — [docs/specs/pluto-lifecycle.md](docs/specs/pluto-lifecycle.md)
- **Skill:** `pluto-session` — agent-owned bootstrap (start Pluto, choose notebook, open Glass)
- **Skills:** `pluto-workflow`, `pluto-semantics` — cell editing and grammar
- **Command:** `pluto-notebooks` — user entry for notebook work
- `package-plugin.sh` — release tree without dev artifacts
- Cursor plugin: rules, hooks, bundled `mcp.json`, eval harness, Design Mode (D13)

### Changed

- **Rule** — agent-driven lifecycle; no user shell scripts (D15)
- **pluto-workflow** — defers session setup to pluto-session
- Launcher connect-only (interim until D15 PlutoMCP tools ship)
- Version **0.1.0** pre-release

### Removed

- Path C DOM bridge (`bridge/`, `src/`)
- `commands/pluto-start.md` — replaced by D15 agent lifecycle

### Known gaps before 0.1.0

- **PlutoMCP:** `pluto_session_status`, `start_pluto_session`, `open_notebook` not implemented
- Launcher needs standalone `connect()` per D15
- Legacy `pluto-*-cell` commands still present
- Marketplace install path

[Unreleased]: https://github.com/jowch/styx/compare/HEAD...HEAD
