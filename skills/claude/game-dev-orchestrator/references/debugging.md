# Workflow: Debugging

## Goal

Move from symptom to reproducible cause, implement the narrowest correct fix, and protect against regression.

## Steps

1. Capture the symptom precisely: expected, actual, environment, frequency, logs, call stack, player state.
2. Reproduce with the smallest reliable scenario.
3. Determine the first point where actual behavior diverges from expected behavior.
4. Form one or more falsifiable hypotheses.
5. Gather evidence using logs, assertions, debugger, state inspection, captures, or minimal instrumentation.
6. Identify root cause rather than the final visible failure when possible.
7. Design the smallest fix that restores the intended invariant.
8. Add a regression test or reproducible validation case.
9. Remove temporary instrumentation unless it is useful permanent diagnostics.
10. Run targeted and neighboring regression checks.

## Debugging rules

- Do not patch a null/invalid state blindly if the real bug is incorrect lifecycle or ownership.
- Do not swallow exceptions or disable assertions to make a symptom disappear.
- Distinguish deterministic bugs from race/timing/resource-budget issues.
- For non-reproducible live issues, improve evidence collection before speculative rewrites.

## Root-cause gate

A fix is credible when the proposed cause explains the observed evidence and changing the causal condition changes the outcome.

## Output

Report:

- reproduction
- root cause
- fix
- regression protection
- residual risk
