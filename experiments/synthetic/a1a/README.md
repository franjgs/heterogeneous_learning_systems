# A1a exact reference solver

This directory verifies the frozen A1a `T=2` primitive specification and
reference worlds A--F in
[HLS Synthetic Environment](../../../docs/experimental_foundations/HLS_SYNTHETIC_ENVIRONMENT.md#20-a1a-frozen-primitive-specification-and-analytical-reference-worlds).

A--F are exact solver acceptance tests, not experimental evidence for RQ0.
Their parameters are frozen and this verifier performs no sampling, fitting,
parameter sweep, or result-file generation.

Strong SEP retains every immediate-reward-maximizing action. If those actions
have different total values, its result is the interval `J_SEP_min` to
`J_SEP_max`, without label-based tie breaking. A future conservative claim of
`HLS > SEP` must compare against `J_SEP_max` when that interval is non-degenerate.

In A1a, HLS and SEP-Omega solve the same exact `argmax_a [r(a)+G(a)]` objective
when SEP-Omega receives sufficient continuation-value information. Their
equality is a reducibility consistency test, not evidence from an independent
algorithmic comparison.

From the repository root:

```text
python -m pytest -q tests/test_a1a_exact_solver.py
python experiments/synthetic/a1a/run_reference_worlds.py
```
