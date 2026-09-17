# Workflow: Technical Design

## Goal

Translate a feature or engineering requirement into the smallest robust technical solution that fits the existing architecture.

## Inputs

- Product/GDD requirement or engineering problem.
- Relevant project architecture and existing implementation.
- Constraints: platform, networking, persistence, performance, deadlines.

## Steps

1. Restate the required observable behavior and non-goals.
2. Identify existing systems that own the relevant state and behavior.
3. Trace data/control flow through those systems.
4. Identify compatibility constraints: save data, replication, APIs, assets, platform behavior.
5. Propose the minimal design that reuses existing extension points.
6. Compare alternatives only when there is a material trade-off.
7. Define files/modules likely to change without inventing exact names before repository inspection.
8. Define failure modes and edge cases.
9. Define validation strategy and performance implications.
10. Record unresolved product/architecture decisions explicitly.

## Design gate

A design is ready for implementation when:

- Ownership of state and behavior is clear.
- Public interfaces and data changes are explicit.
- Backward compatibility/migration needs are addressed.
- The design can be broken into independently verifiable implementation steps.
- No critical requirement is silently assumed.

## Output

Produce:

- behavior summary
- affected systems
- proposed data/control flow
- interface/data changes
- implementation outline
- risks and alternatives
- validation plan
- unresolved decisions

Keep the document proportional to risk. A local feature may need only a short design note.
