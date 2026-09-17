# Workflow: Feature Implementation

## Goal

Implement requested behavior with the smallest coherent change that matches the project's architecture and conventions.

## Steps

1. Confirm the observable acceptance criteria from the request/spec.
2. Inspect analogous code and extension points.
3. Determine whether technical design or task breakdown is required by routing rules.
4. Implement the behavior in the owning system; avoid duplicated state or parallel frameworks.
5. Handle boundary conditions explicitly: lifecycle, disabled/dead states, initialization, reset, scene/world transitions, latency, persistence as relevant.
6. Add or update tests at the cheapest reliable layer.
7. Run targeted validation first, then broader validation proportional to impact.
8. Review the diff for accidental scope expansion, duplicated logic, dead code, and unnecessary abstraction.
9. Route to code review and automated testing when changes are substantive.

## Implementation rules

- Prefer existing interfaces and patterns.
- Do not add a general-purpose abstraction for a single speculative future need.
- Keep authoritative state ownership unambiguous.
- Preserve serialization and network compatibility unless migration is deliberate.
- Keep editor/debug tooling separate from runtime code when the project does so.
- Do not change unrelated formatting or files.

## Completion gate

The feature is ready when:

- Acceptance criteria are demonstrably met.
- Edge cases relevant to the system are handled.
- Tests or validation evidence exist.
- No known regression is introduced.
- Any migration/config/content dependency is documented.
