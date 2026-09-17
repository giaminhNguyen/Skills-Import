# Project Context Discovery

Before changing a game project, discover the project's own rules. Do not assume these exact files exist; search for equivalents.

## Preferred repository context

Look for files such as:

- `AGENTS.md`, `CLAUDE.md`, `CONTRIBUTING.md`, `README.md`
- `Docs/Architecture.md`, `Docs/TechnicalDesign.md`, ADRs, RFCs
- coding standards, naming conventions, folder/module ownership docs
- engine version and package/plugin manifests
- gameplay framework or ECS conventions
- networking/replication rules
- save/data/schema/versioning rules
- asset import and content pipeline rules
- performance budgets and target hardware
- testing conventions and commands
- CI/build/release documentation
- platform requirements and SDK versions

## Context extraction checklist

Capture only what affects the current task:

1. Engine and exact version when available.
2. Language/runtime and major framework/package versions.
3. Module/folder ownership and dependency direction.
4. Existing patterns for the subsystem being changed.
5. Test framework and commands.
6. Target platforms relevant to the task.
7. Performance or memory budgets if relevant.
8. Serialization/network/save compatibility rules if relevant.
9. Build/release constraints if relevant.

## Unity knowledge pack (if one exists)

For Unity projects, check for an existing AI Knowledge Pack before reading the
whole codebase from scratch — see `references/project-knowledge.md` for where
it lives (Claude Code: `<memory-dir>/gameai/`; other agents: `GameAI/Projects/<project-name>/`).
Start from `knowledge-summary.md` when present and current; treat it as a
snapshot that can go stale, and verify anything load-bearing against the
current source before acting on it. If it is missing or stale, consider
running the project knowledge bootstrap/refresh workflow first.

## Existing-code evidence

When documentation is absent or stale, inspect neighboring production code and recent analogous implementations. Prefer consistent local patterns over generic tutorials.

Do not infer a broad architectural rule from one isolated file when several examples are available.

## Recommended project knowledge layer

For teams adopting this skill, create repository files equivalent to:

- `Docs/AI/project-context.md` — engine, platforms, repository map, key commands.
- `Docs/AI/architecture.md` — boundaries, dependency direction, core frameworks.
- `Docs/AI/coding-standards.md` — naming, formatting, error handling, logging.
- `Docs/AI/gameplay-framework.md` — entity/component/ability/event/state conventions.
- `Docs/AI/asset-pipeline.md` — import settings, naming, LOD/compression rules.
- `Docs/AI/performance-budget.md` — frame, memory, loading, draw-call budgets by platform.
- `Docs/AI/testing.md` — unit/integration/playmode/smoke conventions.
- `Docs/AI/build-release.md` — CI, versioning, signing, branch and release rules.

These files are project knowledge, not duplicated inside the reusable skill.
