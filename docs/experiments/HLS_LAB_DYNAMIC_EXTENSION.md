# HLS Laboratory v1: dynamic scenario extension

This additive extension reuses `ProblemSpec`, the frozen 64-action catalogue,
`production_inputs`, functional evaluation, v1 episode/run records, and the
MIS-v2 exponential capability-gap law. It does not replace CE-23/24/25, G0,
DISCOVER, or MIS-v2, and it does not claim multi-step DISCOVER/G0 integration.

`DemandRegime` defines a fixed distribution over requirement vectors;
`generate_problems` uses a local seeded pseudo-random stream to materialize a
single exogenous sequence from a declared schedule. Policies compared by
`compare_organizations` receive the same initial team and exact same sequence.
Each run then develops its own capabilities and organization state, so later
experiences and trajectories may differ endogenously.

`LearningProfile` specifies one existing MIS-v2 `eta` per expert and
capability. The implementation converts each eta with the existing
`eta_to_lambda` and applies `capability_after_exposure`; the transition law is
unchanged. LI can be disabled independently. Organizational updates are
performed only when requested and supported by the organization interface.
As in Laboratory v1, estimated competence is set equal to real competence;
this extension does not add inference, partial observability, or a learned
coordination mechanism.

Run the focused and CE-23 acceptance tests from the repository root:

```bash
PYTHONPATH=src:. pytest -q tests/test_hls_lab_dynamic.py tests/test_hls_lab_v1.py
```

The dynamic tests include a bounded paired comparison of state-responsive
`GreedyAdaptive` and tabular `ExploreThenGreedy` on a pre-generated sequence
whose demand distribution changes. This is an implementation check only, not
a scientific campaign or evidence that either organization is generally
superior. The source ZIP's `__pycache__` files are intentionally not installed.
