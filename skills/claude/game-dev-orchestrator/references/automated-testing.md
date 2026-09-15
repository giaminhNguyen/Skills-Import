# Workflow: Automated Testing

## Goal

Add the cheapest reliable automated evidence that protects the behavior or invariant affected by the change.

## Test selection

Prefer, in order, the lowest layer that can prove the behavior:

1. Pure/unit test for deterministic logic.
2. Module/system integration test for component interaction.
3. Engine/play-mode/world test for lifecycle, physics, animation, rendering-adjacent, or scene behavior.
4. End-to-end/smoke test for build/platform/user-flow validation.

Do not use a slower layer when a cheaper deterministic layer proves the same invariant.

## Steps

1. Identify the failure/behavior contract.
2. Select test layer and fixtures consistent with the repository.
3. Include at least one positive path and the highest-risk boundary condition.
4. For bug fixes, make the regression test fail on the old behavior when practical.
5. Keep tests deterministic; control time, randomness, network, and asynchronous completion when possible.
6. Run targeted tests, then the relevant suite.
7. Report skipped/unavailable tests explicitly.

## Testing rules

- Do not assert implementation details when user-visible/system behavior can be asserted.
- Do not solve flaky tests with arbitrary sleeps.
- Do not disable failing tests to make validation pass.
- Keep performance benchmarks separate from ordinary correctness assertions unless the project already combines them.

## Completion gate

Testing is complete when the changed behavior and its most important regression risk have executable evidence, or when the environment limitation preventing execution is explicitly documented.
