# Workflow: Code Review and Refactoring

## Goal

Detect correctness, integration, maintainability, performance, compatibility, and test risks in a change without replacing local conventions with personal preference.

## Review order

1. Correctness against requirement and invariants.
2. Data/state ownership and lifecycle.
3. API, serialization, save, networking, and platform compatibility.
4. Error paths and edge cases.
5. Performance/resource risks when relevant.
6. Tests and observability.
7. Maintainability and duplication.
8. Style only when it affects project standards or clarity.

## Finding severity

- **Blocker** — data loss, crash, security/cheat exposure, release failure, invalid architecture boundary, deterministic severe regression.
- **High** — likely gameplay/system defect, compatibility break, major performance regression, missing critical validation.
- **Medium** — maintainability or edge-case issue likely to create future defects.
- **Low** — localized clarity or cleanup that does not block the change.

## Review rules

- Cite concrete code paths/evidence for every substantive finding.
- Avoid speculative findings that cannot explain a plausible failure.
- Do not demand refactoring unrelated to the change.
- Distinguish required fixes from optional improvements.
- If no significant issue is found, say so and identify remaining test gaps rather than inventing findings.

## Refactoring gate

Refactor when it reduces current complexity, duplication, or defect risk and can be validated without changing intended behavior. Do not refactor merely to apply a preferred pattern.
