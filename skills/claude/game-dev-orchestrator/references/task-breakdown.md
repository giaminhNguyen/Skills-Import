# Workflow: Task Breakdown

## Goal

Turn an approved technical direction into ordered, independently verifiable engineering tasks.

## Steps

1. Identify dependency order.
2. Separate infrastructure changes from behavior changes when useful.
3. Split work by verifiable outcome, not arbitrary file count.
4. Keep each task small enough to review and test coherently.
5. Include migration, tooling, assets, tests, telemetry, and docs only when required.
6. Identify cross-discipline dependencies and blocking inputs.
7. Mark tasks that can run in parallel.
8. Define acceptance evidence for every task.

## Task template

For each task provide:

- **Outcome** — observable result.
- **Scope** — systems/files expected to change.
- **Dependencies** — preceding tasks or external inputs.
- **Validation** — test/build/profile evidence required.
- **Risk** — low/medium/high with the reason.

## Breakdown gate

The plan is ready when:

- Every task has a concrete completion condition.
- The ordering prevents dependent work from landing too early.
- Risky architecture/data changes occur before broad feature polish.
- Testing is embedded into the plan rather than left as a final vague task.
