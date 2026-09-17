# Workflow: Performance Optimization

## Goal

Improve a measured performance problem without changing intended behavior or moving cost into an unmeasured subsystem.

## Steps

1. Define the metric, target hardware/platform, scenario, and acceptance threshold.
2. Reproduce consistently and record a baseline.
3. Determine the dominant bottleneck category: CPU, GPU, memory/GC, IO/loading, network, shader/content, synchronization, or build configuration.
4. Use profiler/capture evidence to identify the dominant hot path/resource.
5. Form a specific optimization hypothesis.
6. Make one coherent change or a small controlled set of related changes.
7. Re-run the same scenario and compare against baseline.
8. Check visual/gameplay correctness and secondary metrics.
9. Retain a benchmark, budget check, or reproducible scenario when practical.

## Rules

- Measure before optimizing.
- Optimize the dominant cost, not the easiest code to change.
- Report absolute values and context when available, not only percentages.
- Watch for work shifted from CPU to GPU, runtime to load time, memory to IO, client to server, or one platform to another.
- Do not reduce quality silently. Treat quality/budget trade-offs as product/technical decisions.

## Completion gate

An optimization is complete when before/after evidence shows the target metric improved sufficiently, correctness is preserved, and major secondary regressions were checked.
