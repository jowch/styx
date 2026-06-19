# Skill architecture (Pluto agent training)

Agent-facing Pluto training uses **three skills** with progressive disclosure. Each `SKILL.md` is a cold-start path (~150–300 words); detail lives in `reference/` files loaded on demand.

## Skill chain

```
User intent → pluto-session → (notebook open) → pluto-workflow → pluto-semantics (on parse errors)
```

| Skill | Owns | Reference files |
|-------|------|-----------------|
| **pluto-session** | Path A/B bootstrap, Glass URLs, lifecycle MCP | `path-a-landing`, `path-b-open`, `glass-navigation`, `lifecycle-tools`, `errors` |
| **pluto-workflow** | Browser-first discovery, stage-first edits, safe preview | `pluto-mental-model`, `safe-preview`, `design-mode`, `edit-loop`, `errors`, `tools` |
| **pluto-semantics** | Cell grammar, reactivity, parse errors | `grammar`, `reactivity`, `error-kinds`, `pluto-sources` |

## Other surfaces

| Surface | Role |
|---------|------|
| `rules/pluto-notebook-workflow.mdc` | Always-on router (~170 words) — skill pointers only |
| `commands/pluto-notebooks.md`, `pluto-open.md` | User triggers → invoke skill |
| `docs/pluto-agent-primer.md` | **Deprecated** — long JSON examples only |
| `docs/specs/pluto-lifecycle.md` | D15 spec + acceptance (implementers) |

## Pluto.jl research

Pluto source citations and durable semantics are curated in `skills/pluto-semantics/reference/pluto-sources.md` and cross-linked from workflow/semantics skills. Research drawn from Pluto 0.20.x (`Parse.jl`, `Run.jl`, `bonds.jl`, `SessionActions.jl`).

## Authoring principles

- **Description = triggers only** (no workflow summary — agents may skip the body)
- **One level deep** — `SKILL.md` → `reference/*.md` only
- **Cross-skill by name** — `**pluto-session**`, not `@` force-load
- **Rule/commands delegate** — no duplicate Path A/B prose
- **TDD gate:** [eval/SKILL_BASELINE_SCENARIOS.md](../eval/SKILL_BASELINE_SCENARIOS.md) — run after skill edits
