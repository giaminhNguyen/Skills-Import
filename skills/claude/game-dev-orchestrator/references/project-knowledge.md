# Workflow: Project Knowledge Bootstrap / Refresh

Build or refresh a local, read-only AI Knowledge Pack for a Unity project so
every other workflow in this skill has fast, reliable project context instead
of re-scanning the whole codebase each time.

This workflow is standalone: it never edits game code or assets. When the
user's request also asks for a change, finish this pass first, then route the
change through the normal workflow modules (`references/routing.md`) using the
knowledge pack as context.

## When to run this workflow

Run it when:

- The user explicitly asks to bootstrap/onboard/scan the project or build/refresh
  an AI knowledge pack.
- Work is starting on a Unity codebase with no existing knowledge pack (see
  "Resolve the knowledge pack location" below) and the task is large enough
  (new subsystem, unfamiliar area, multi-file change) to benefit from one.
- An existing knowledge pack is stale relative to the change being made (major
  refactor landed, new systems added since the last bootstrap/refresh timestamp).

Do not run it when:

- The task is small and local, and current project context already answers it.
- A knowledge pack already exists and is not stale — read `knowledge-summary.md`
  instead of re-running the scan.
- The user asked only for a code change, not project onboarding — chain this
  workflow in only if the change touches an area the knowledge pack cannot
  currently explain.

## Core contract

- Treat the Unity project as READ-ONLY during bootstrap/refresh.
- Never create, modify, move, rename, or delete files under the Unity project.
- Store generated knowledge in the local GameAI workspace outside the Unity repository.
- Prefer one end-to-end run over asking the user to trigger separate phases.
- Mark findings as `Observed`, `Inferred`, or `Unknown` when confidence matters.
- Never convert an existing project pattern directly into an approved Studio standard.
- Never write to `Studio/approved/` during bootstrap.

## Inputs

Resolve these inputs with minimal user interaction:

1. **Unity project source**
   - Use an explicit path when supplied.
   - Otherwise, if the current working directory is a Unity project root containing `Assets/`, `Packages/`, and `ProjectSettings/`, use it.
   - If neither is available, ask only for the project path.

2. **Project status**
   - Accept `completed` or `developing`.
   - Reuse the status from an existing project profile when refreshing.
   - If this is a first bootstrap and status is omitted, default to `developing` and record that assumption.

3. **Knowledge pack location**
   Resolve in this order:
   - explicit workspace path supplied by the user;
   - when the running agent is Claude Code: use the Claude Code layout below (no `GameAI/` folder, no further resolution needed);
   - `GAMEAI_HOME` environment variable;
   - `~/GameAI` if it exists.
   If none resolves, ask for the GameAI workspace once.

## Workspace layout

Generic layout (non-Claude-Code agents):

```text
GameAI/
├── Studio/
│   ├── approved/
│   └── candidates/
└── Projects/
    └── <project-name>/
```

Write project outputs to `GameAI/Projects/<project-name>/`.

For a completed project, write Studio candidates only to `GameAI/Studio/candidates/<project-name>/`.
Do not write Studio candidates for a developing project unless the user explicitly asks.

### Claude Code layout

Claude Code carries a per-project auto-memory directory (the folder holding that
project's `MEMORY.md`, path given to the agent at session start). Reuse it instead
of a separate `GameAI/` tree so project knowledge never needs an out-of-repo path
kept in the human's head:

```text
<memory-dir>/gameai/            <- project outputs (same file set as generic layout)
~/.claude/GameAI-Studio/
├── approved/
└── candidates/
    └── <project-name>/
```

- Project outputs go to `<memory-dir>/gameai/`, where `<memory-dir>` is this session's own auto-memory directory.
- Add or update one `reference`-type memory file pointing to `gameai/knowledge-summary.md`, and add its line to that project's `MEMORY.md`, so future sessions discover the pack automatically instead of being told the path manually.
- Studio candidates/approved are shared across every project, so they never go under a single project's memory — always `~/.claude/GameAI-Studio/`.
- To decide whether a knowledge pack already exists (see "When to run this workflow"), check `<memory-dir>/gameai/knowledge-summary.md` first.

## Workflow phases

Execute all phases in one run.

### 1. Resolve and verify project

A valid Unity project root should contain `Assets/`, `Packages/`, `ProjectSettings/`.
Read Unity version only from `ProjectSettings/ProjectVersion.txt`.
Resolve the knowledge output outside the Unity project — never inside the project root.

### 2. Deterministic inventory

Run:

```bash
python scripts/collect_unity_inventory.py --project <UNITY_PROJECT> --output <PROJECT_KNOWLEDGE_DIR>
```

Use the generated `inventory-snapshot.json` as a factual baseline.

Create `project-inventory.md` covering: Unity version, important packages,
important `Assets/` roots, C# counts grouped by major area, `.asmdef` inventory,
scenes, Editor/Test folders, Resources/StreamingAssets/Addressables indicators,
likely code roots, build/test tooling indicators. Avoid deep architecture
judgments in this file.

### 3. System index

Identify only systems that exist. Typical categories: bootstrap/initialization,
core services, scene management, player/character, input/movement,
combat/damage/ability, enemy/AI, inventory/item/quest/progression/economy,
save/load/data, UI, audio/camera/animation/VFX, pooling,
Addressables/localization, networking, analytics/ads/IAP/platform services,
editor/build/debug tools, automated tests.

For each major system, record: purpose, primary location, namespaces, important
types, entry points, config/data types, related `.asmdef`, obvious dependencies,
relevant external packages. Also include a focused key-code index — do not list
every class.

### 4. Architecture analysis

Read only enough source to establish the major architecture. Focus on
structural entry points and highly referenced abstractions.

- **Startup and lifetime** — startup entry points, initialization sequence,
  persistent/global services, scene/session lifecycle, ownership of long-lived
  objects.
- **System boundaries** — responsibilities, public entry points,
  interfaces/base classes, state ownership, runtime/data dependencies, Unity
  lifecycle usage.
- **Communication** — direct references, interfaces, events/delegates,
  event/message bus, service locator, singleton/static access, dependency
  injection, ScriptableObject event/data channels. Do not label patterns good
  or bad in `architecture-map.md`.
- **Data flow** — trace `Source Data -> Runtime Representation -> Gameplay
  Consumer` for ScriptableObjects, JSON, PlayerPrefs, local files, remote
  config, runtime state, save data, or other observed storage.
- **Modules and dependencies** — use `.asmdef` plus source evidence to map
  important dependency directions. Note circular/bidirectional relationships
  only when supported by evidence.
- **External packages** — identify architecturally significant SDK/package
  integration points and whether wrappers/adapters are used.

### 5. Technical review

Create `technical-review.md` only after the architecture map is established.
Separate **Observed risk** (directly supported by evidence), **Inferred risk**
(likely, incomplete evidence), and **Recommendation** (suggested action, not a
factual statement).

Review: high coupling, unclear ownership, global mutable state, circular
dependencies, lifecycle fragility, expensive runtime patterns when clearly
evident, duplicated infrastructure, testing gaps, build/tooling fragility,
package lock-in, obsolete/deprecated patterns relative to the project's Unity
version, reusable systems and abstractions, lessons that may generalize to
future projects. Do not apply fixes.

### 6. Completed-project candidate extraction

Only for status `completed`. Create files under `Studio/candidates/<project-name>/`
(generic layout) or `~/.claude/GameAI-Studio/candidates/<project-name>/` (Claude
Code layout):

- `architecture-candidates.md`
- `coding-candidates.md`
- `gameplay-candidates.md`
- `performance-candidates.md`
- `testing-candidates.md`
- `lessons-candidates.md`

Each candidate must include: candidate statement, source project, supporting
evidence or file references, why it may generalize, caveats/project-specific
assumptions, status `Candidate - requires human approval`. Never write to
`Studio/approved/`.

### 7. Final summary

Make `knowledge-summary.md` the primary entrypoint future agents read first. It
should let another agent quickly answer: what is this project, which Unity
version, what are the major systems, how does startup work, what are the major
communication/data patterns, where to look before changing gameplay/UI/data/
build code, what important risks or unknowns remain, and which detailed file to
read next.

### 8. Report and stop

Report a concise completion summary (see "Completion response" below) and stop.
Do not ask the user to manually start another pass.

## Model delegation

If the runtime supports model/subagent delegation, use a fast/low-cost model
for deterministic inventory and broad indexing, and a stronger reasoning model
for architecture, technical review, and Studio candidate extraction. If model
delegation is unavailable, continue with the current model.

## Refresh behavior

Use this when the project's knowledge output directory already exists —
`Projects/<project>/` (generic layout) or `<memory-dir>/gameai/` (Claude Code layout).

Goals: update stale facts without destroying useful context, avoid re-reading
the whole project when changes are localized, preserve human-reviewed notes
unless source evidence invalidates them.

Procedure:

1. Read existing `project-profile.md`, `knowledge-summary.md`, and `inventory-snapshot.json`.
2. Re-run the inventory collector.
3. Compare old and new inventory facts when available: Unity version, package set, C# counts, assemblies, major folders, scenes.
4. Identify likely change zones.
5. Re-read only affected architecture/system areas plus any entry points needed to verify downstream impact.
6. Update detailed files in place.
7. Refresh `knowledge-summary.md` last.
8. For completed projects, update Studio candidates only when newly discovered evidence changes or adds candidates.

If change detection is ambiguous, prefer correctness over optimization and
expand the scan, while keeping the Unity project read-only.

## Output requirements

Produce these project files: `project-profile.md`, `inventory-snapshot.json`,
`project-inventory.md`, `system-index.md`, `architecture-map.md`,
`technical-review.md`, `knowledge-summary.md`.

### Common labels

- **Observed** — directly verified in project files.
- **Inferred** — strongly suggested by code or structure but not fully proven.
- **Unknown** — insufficient evidence.

Use repo-relative source paths when referring to project files. Do not copy
large source excerpts.

### project-profile.md

Project name; absolute source path; project status (Completed/Developing);
detected Unity version; knowledge output path; bootstrap mode (read-only);
bootstrap/refresh timestamp; scan mode (new bootstrap or refresh).

### project-inventory.md

Unity/render-pipeline indicators; important packages; important project
folders; C# inventory summary; assembly definitions; scenes/content/tooling
indicators; tests/build/editor tooling indicators; concise inventory summary.
Keep descriptive rather than architectural.

### system-index.md

Per system: purpose, main location, important namespaces, important types,
main entry points, data/config types, related assembly, obvious dependencies,
relevant external dependency, confidence. Add a key-code index,
cross-system links, and low-confidence/unresolved areas.

### architecture-map.md

Startup/bootstrap flow; major system boundaries; dependency direction;
communication patterns; data architecture; scene/object lifecycle;
assembly/module architecture; external dependency integration; text-based
high-level architecture diagram; uncertainties. Do not mix refactor
recommendations into this file.

### technical-review.md

Organize findings by severity: High, Medium, Low, Opportunity/Reusable. Each
finding: type (Risk/Technical Debt/Reusable Pattern/Lesson), confidence
(Observed/Inferred), evidence (file/type references), impact, recommendation
if appropriate. Do not modify source.

### knowledge-summary.md

Keep concise: project at a glance; Unity version/status; major systems;
startup flow; key architecture patterns; key data/communication patterns;
important external dependencies; highest-priority technical review items;
reusable systems; important unknowns; `Read next` mapping to detailed files.
This is the first file future game-dev agents should read.

## Source-of-truth priority

During bootstrap analysis: current project files/configuration, then explicit
user-provided project facts, then existing project knowledge still supported
by source, then Studio approved knowledge for comparison only, then generic
Unity practices. Project source describes what exists; Studio knowledge
describes preferred practice — keep those concepts separate.

## Safety boundaries

Do not: edit C# source; edit `.asmdef` files; modify scenes, prefabs,
ScriptableObjects, or assets; modify `Packages/manifest.json` or lock files;
modify `ProjectSettings/`; upgrade Unity or packages; run automatic
refactors/fixes; create AI files inside the Unity repository; add files to
Git; mark Studio candidates as approved.

If a problem is discovered, document it in `technical-review.md` instead of
fixing it.

## Completion response

Return only a concise operator summary containing: project name and detected
Unity version; mode (new bootstrap or refresh); project status; output
directory; major systems identified; major architecture style/patterns; count
of high-priority review findings; whether Studio candidates were created; any
unresolved uncertainties requiring human review.
