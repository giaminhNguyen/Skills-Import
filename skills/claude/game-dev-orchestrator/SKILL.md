---
name: game-dev-orchestrator
description: Orchestrate day-to-day game development work from feature requests, GDD items, bugs, code changes, asset integration, performance problems, tests, builds, and release checks — and, for Unity projects, build or refresh a local read-only AI Knowledge Pack (project profile, system index, architecture map, technical review, knowledge summary) by scanning the project, indexing code/systems, mapping architecture, and reviewing technical debt and reusable patterns. Use when ChatGPT/Claude is working as a game developer or technical lead and needs to classify a task, read project rules, choose the correct engineering workflow, chain related workflows, implement or review changes, validate results, and report completion; or when starting AI-assisted work on a Unity project, onboarding a completed or developing Unity codebase, or rebuilding project knowledge after major changes. Supports engine-agnostic projects with project-specific Unity, Unreal, custom-engine, platform, architecture, coding, performance, and build rules loaded from the repository when available, and supports completed/developing Unity project modes with unapproved Studio Knowledge candidate extraction.
---

# Game Dev Orchestrator

Use this skill as the control plane for game-development work. Route each request to the smallest workflow that can complete it, load only the references needed for that workflow, and enforce project rules before generic engine best practices.

## Operating model

1. Inspect the user's request and available project context.
2. Read `references/routing.md` to select the primary workflow and any required chained workflows — including whether this is a project-knowledge bootstrap/refresh request rather than a code-changing one.
3. Discover project-specific rules before changing code or assets. Read `references/project-context.md` and the repository files it points to when they exist. For a Unity project, also check whether a knowledge pack already exists (see `references/project-knowledge.md`) and use it as context instead of re-reading the whole codebase.
4. Load only the relevant workflow reference files.
5. Execute the workflow, including its validation gates and stop conditions.
6. Chain follow-up workflows only when their trigger conditions are met.
7. Return the workflow output contract from `references/output-contracts.md`.

## Workflow modules

Use these modules:

- Technical design: `references/technical-design.md`
- Task breakdown: `references/task-breakdown.md`
- Feature implementation: `references/feature-implementation.md`
- Debugging: `references/debugging.md`
- Code review and refactoring: `references/code-review.md`
- Automated testing: `references/automated-testing.md`
- Asset integration: `references/asset-integration.md`
- Performance optimization: `references/performance-optimization.md`
- Build and release engineering: `references/build-release.md`
- Release readiness review: `references/release-readiness.md`
- Project knowledge bootstrap/refresh (Unity): `references/project-knowledge.md`

## Routing principles

- Choose one primary workflow. Do not run every workflow by default.
- Treat technical design as required when a change affects architecture, public interfaces, persistence, networking, threading, platform APIs, or more than one major subsystem.
- Treat task breakdown as required for multi-file, multi-system, or multi-person work that cannot be safely completed as one atomic change.
- For ordinary feature work, prefer: technical design when needed -> task breakdown when needed -> feature implementation -> code review -> targeted tests.
- For bugs, prefer: debugging -> fix through feature implementation conventions -> code review -> regression tests.
- For performance issues, prefer: debugging only if the problem is not yet reproducible -> performance optimization -> targeted regression/performance tests.
- For asset problems, prefer: asset integration -> targeted validation -> performance optimization only if budgets are at risk.
- For release work, prefer: build and release engineering -> release readiness review.
- For a Unity project, route to project knowledge bootstrap/refresh only when: the user explicitly asks for it, no knowledge pack exists yet and the task is substantial, or the existing pack is stale relative to the change. It is a standalone, read-only pass — never combine it with a code-changing workflow in the same pass. Once it finishes (or an up-to-date pack already exists), route the actual request through the normal workflow using the pack as context.

Read `references/routing.md` for the complete decision table and chaining rules.

## Project-specific rules take precedence

Before writing or changing implementation details, search the repository for project guidance. Follow the precedence rules in `references/project-context.md`.

Use this order when instructions conflict:

1. Explicit user instruction for the current task.
2. Repository/project-specific rules and technical decisions.
3. Existing codebase patterns and neighboring implementations.
4. Engine/framework official conventions already adopted by the project.
5. Generic best practices.

Do not introduce a new framework, architecture, package, plugin, abstraction, or dependency merely because it is generally considered better. Preserve local conventions unless the task explicitly asks for architectural change.

## Autonomy rules

Proceed without asking for confirmation when the change is local, reversible, and supported by the request and project conventions.

Stop and surface a decision instead of guessing when any of these are true:

- Multiple materially different product behaviors are plausible and the requirement does not resolve them.
- A change would delete or irreversibly migrate player data.
- A change would alter a public/network protocol or serialized format without a compatibility plan.
- A new paid service, proprietary SDK, engine plugin, or external dependency is required.
- A release or destructive operation would affect production/live users and no explicit authorization exists.

When blocked, still provide the best completed analysis, implementation plan, or safe partial change possible.

## Change discipline

- Prefer the smallest coherent change that satisfies the requirement.
- Inspect existing implementations before creating new abstractions.
- Keep gameplay behavior, data ownership, rendering, persistence, networking, and editor tooling boundaries explicit.
- Do not hide failures with broad exception handling, silent fallbacks, disabled tests, or relaxed validation.
- When fixing bugs, preserve a reproducible case or regression test whenever practical.
- When optimizing, measure before and after. Do not claim an improvement without evidence.
- When changing assets or import settings, record the affected asset classes and budgets.
- When touching build/release configuration, preserve reproducibility and identify platform-specific effects.

## Completion standard

A task is complete only when:

- The requested behavior or engineering outcome is implemented or fully analyzed.
- Relevant project rules were followed.
- Validation appropriate to the risk was performed or clearly marked as unavailable.
- Known edge cases, risks, migrations, and follow-up work are surfaced.
- The final response uses the concise completion report in `references/output-contracts.md`.

## Examples

**Request:** "Add health regeneration after five seconds without taking damage."

Route to feature implementation. Add technical design first only if the health/damage system boundaries are unclear or the change affects replication/persistence. Finish with code review and targeted gameplay tests.

**Request:** "FPS drops from 60 to 35 when 50 enemies spawn."

Route to performance optimization. If the issue is not reproducible, start with debugging. Measure CPU/GPU/memory before changes, isolate the bottleneck, optimize the dominant cause, then re-measure and run regression checks.

**Request:** "Android build fails after updating the ads SDK."

Route to build and release engineering. Inspect dependency/version changes and build logs. Add code review only when source/config changes are made. Run release readiness only when preparing a distributable candidate.

**Request:** "Onboard this Unity project" / "Refresh the knowledge pack, we refactored the save system."

Route to project knowledge bootstrap/refresh (`references/project-knowledge.md`). Read-only scan, no code changes. Stop after the completion summary — do not chain into feature implementation or code review unless the user separately asks for a change.
