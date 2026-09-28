# A1c pre-registered competence-geometry sweep

A1c executes the protocol frozen in
[HLS Synthetic Environment](../../../docs/experimental_foundations/HLS_SYNTHETIC_ENVIRONMENT.md#22-a1c-competence-geometry-phase-sweep).
It evaluates exactly 458 deterministic competence geometries through the
unchanged A1a solver. It does not tune parameters, use seeds, implement A1d, or
provide empirical validation of RQ0.

From the repository root:

```text
python -m pytest -q tests/test_a1a_exact_solver.py tests/test_a1b_phase_sweep.py tests/test_a1c_competence_sweep.py
python experiments/synthetic/a1c/run_sweep.py
```

The run writes machine-readable rows, a summary, a provenance manifest, and
only the two pre-registered figures to
`results/foundations/a1c_competence_geometry/`.
