# Changelog

All notable changes to **Styx** are documented here.

[Keep a Changelog](https://keepachangelog.com/en/1.1.0/) · [Semantic Versioning](https://semver.org/spec/v2.0.0.html)

## [Unreleased]

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

[Unreleased]: https://github.com/jowch/styx/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/jowch/styx/releases/tag/v0.1.0
