# Routing and Workflow Composition

Use this file to classify the request and decide which modules to load.

## Primary routing table

| Signal in request or evidence | Primary workflow | Common chained workflows |
|---|---|---|
| New gameplay/system behavior, feature request, GDD item | Feature implementation | Technical design, task breakdown, code review, automated testing |
| Architecture question, interface change, system ownership, data flow | Technical design | Task breakdown, feature implementation |
| Large feature, milestone item, multiple dependencies, handoff plan | Task breakdown | Technical design, feature implementation |
| Wrong behavior, crash, exception, inconsistent state, reproduction report | Debugging | Feature implementation conventions, code review, automated testing |
| PR/diff/review request, maintainability concern, technical debt | Code review | Refactoring, automated testing |
| Missing coverage, regression suite, smoke test, deterministic validation | Automated testing | Feature implementation or debugging when failures are found |
| Model/texture/animation/audio/VFX import or runtime asset issue | Asset integration | Automated testing, performance optimization |
| FPS, frame-time, hitch, memory, GC, GPU, loading, draw-call, bandwidth issue | Performance optimization | Debugging if not reproducible, automated testing |
| Build failure, packaging, CI, signing, versioning, platform configuration | Build and release engineering | Code review, automated testing, release readiness |
| Candidate build, ship/no-ship decision, release checklist | Release readiness review | Build and release engineering, automated testing, performance optimization |
| Onboard/scan a Unity project, build or refresh an AI knowledge pack, unfamiliar codebase before a large change | Project knowledge bootstrap/refresh | None by default — a standalone read-only pass; chain into the real workflow afterward only if the user also asked for a change |

## Classification rules

1. Select the workflow that owns the **engineering outcome**, not merely a symptom word.
2. If a bug report is specifically a measured frame-time problem, prefer performance optimization over generic debugging.
3. If an import issue is caused by asset settings or content structure, prefer asset integration over debugging.
4. If the user asks for review only, do not silently modify code unless they ask for fixes or the environment clearly supports applying accepted fixes.
5. If the user asks to implement a well-scoped local feature, do not force a separate technical-design artifact.
6. For a Unity project, prefer project knowledge bootstrap/refresh over silently re-reading the whole codebase from scratch when a knowledge pack already exists and is current — read it instead. Only re-run bootstrap/refresh when it is missing, stale, or explicitly requested.

## Chaining rules

### Feature path

Use:

`technical-design? -> task-breakdown? -> feature-implementation -> code-review -> automated-testing`

`?` means conditional.

Require technical design when any of these apply:
- New subsystem or ownership boundary.
- Public API or shared interface change.
- Save format, database schema, replication, protocol, threading, platform API, or security-sensitive change.
- At least two plausible implementation approaches have materially different maintenance/performance consequences.

Require task breakdown when any of these apply:
- More than one engineer/discipline is likely to contribute.
- Work spans multiple major systems or packages.
- The task has independently testable milestones.
- The implementation should be staged to reduce integration risk.

### Bug path

Use:

`debugging -> implementation fix -> code-review -> regression testing`

Do not jump from symptom to patch without identifying a credible root cause unless the user explicitly requests a temporary mitigation.

### Performance path

Use:

`reproduce? -> performance-optimization -> performance regression check`

Do not optimize based on intuition alone. Establish a baseline and identify the dominant bottleneck first.

### Asset path

Use:

`asset-integration -> asset validation -> performance check?`

Add performance optimization when the asset violates or threatens memory, size, draw-call, shader, animation, or loading budgets.

### Release path

Use:

`build-release -> release-readiness`

A successful local build does not imply release readiness.

### Project knowledge path

Use:

`project-knowledge-bootstrap-or-refresh -> stop` (own pass), then, only if the
user also asked for a change: `route through the normal table above`.

Never run this path implicitly on every request — only per the trigger
conditions in `references/project-knowledge.md`.

## Multi-intent requests

If the request clearly contains multiple independent outcomes, handle them in dependency order and report each separately. Example:

"Implement inventory sorting and fix Android packaging" -> implement and validate inventory first, then build/release work unless the packaging problem blocks all validation.
