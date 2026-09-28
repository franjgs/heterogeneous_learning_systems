# A1b pre-registered phase-boundary sweep

A1b executes the protocol frozen in
[HLS Synthetic Environment](../../../docs/experimental_foundations/HLS_SYNTHETIC_ENVIRONMENT.md#21-a1b-predefined-primitive-parameter-phase-boundary-sweep).
It evaluates exactly 1,020 deterministic A1a primitive configurations and
tests analytical phase-boundary agreement. It does not tune parameters, use
seeds, implement A1c, or provide empirical validation of RQ0.

From the repository root:

```text
python -m pytest -q tests/test_a1a_exact_solver.py tests/test_a1b_phase_sweep.py
python experiments/synthetic/a1b/run_sweep.py
```

The run writes machine-readable rows, summary, provenance manifest, and only
the three pre-registered figures to `results/foundations/a1b_phase_boundary/`.
