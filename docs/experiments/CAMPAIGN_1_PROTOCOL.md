# Campaign 1 — frozen execution protocol

## Provenance boundary and purpose

This document freezes Campaign 1 before results. The test range is imported unchanged from commit `05b86cb`; no history is duplicated or redesigned. Everything through this protocol commit is pre-results design. Campaign 1 asks whether the frozen HLS laboratory supplies a small, diverse, interpretable range of adaptive situations suitable for later strategy discrimination. It is not a configuration competition, parameter sweep, exhaustive regime map, novelty search, or test that C/N/M predict performance.

No team is executed by this protocol gate. Team executions, performance artifacts, and trajectory artifacts are all zero.

## Frozen run matrix

- Scenarios: exactly TR-PR, TR-PM, TR-G, TR-J, TR-R, TR-D, TR-HA, TR-HB, loaded from `campaign1_test_range.py`.
- Probe configurations: exactly G00, G04, G05, G07, resolved from the existing canonical geometry fixture. They are probes rather than competitors.
- Seeds: exactly `0,...,9`.
- Conditions: exactly FULL, NO-DEVELOP, KNOWN-Z.

Each condition contains `8 scenarios x 4 configurations x 10 seeds = 320` runs. The frozen total is `3 x 320 = 960`. KNOWN-Z+NO-DEVELOP is excluded.

## Frozen model and temporal semantics

The model retains N=3, K=2, rho=.5, sigma=.10, eta=.35, within-problem horizon three, current CES, finite Bayesian DISCOVER, MPC, MIS-v2, belief reset between problems, and persistent capability state between problems. No mechanism or parameter is varied.

Common random numbers use the same seed for every matched scenario/configuration/condition run. This shares the Gaussian standard-normal draw stream; true means and resulting observations may differ. Observations remain irrelevant to KNOWN-Z decisions.

## Conditions and implementation mapping

### FULL

Finite Bayesian DISCOVER and MIS-v2 development are active. Action selection is the existing `finite_choose_dynamic_action_v2(..., develop=True)` path represented by `DISCOVER_DEVELOP`.

### NO-DEVELOP

Finite Bayesian DISCOVER remains active, capability development is disabled, and S stays at its initial value across problems. To isolate development while preserving the current dynamic MPC, execution must use the existing `finite_choose_dynamic_action_v2(..., develop=False)` primitive.

The historical `DISCOVER_ONLY` sequence mode must **not** be silently substituted: it invokes the fixed-state finite-horizon DP rather than the same dynamic-MPC primitive. This is an execution-adapter requirement, not new physics or a new controller. If it cannot be honored, execution must stop before producing results.

### KNOWN-Z

The true problem enters the existing known oracle directly, inference uncertainty is absent, and MIS-v2 remains active. This maps to the existing `DEVELOP_KNOWN` control and `_known_dynamic_action_v2(..., develop=True)`.

FULL−NO-DEVELOP is a diagnostic comparison associated with capability development. FULL−KNOWN-Z is associated with imperfect problem knowledge/DISCOVER. Neither is assumed to be an additive causal decomposition.

## Performance and retained trajectories

Performance is the existing true expected/latent production `mu_true`. Observed noisy reward drives Bayesian inference where applicable and is retained, but it is never silently substituted for performance.

Every future run must retain true z and C/N/M; belief before/after where applicable; action X; cumulative continuous exposure E; S before/after; `mu_true`; and observed noisy reward. Primary interpretation follows:

```text
z -> belief/decision -> X -> E -> S -> later decisions -> performance.
```

Supported outputs are trajectories and cumulative performance, assignment/exposure/capability trajectories, response to recurrence or familiar return, configuration sensitivity/insensitivity, and the two diagnostic control comparisons. No ad-hoc scalar inventory is frozen.

## Controlled contrasts

The four test-range contrasts remain questions, not predictions:

1. TR-PR/TR-PM: represented versus mismatched persistence.
2. TR-G/TR-J: identical problem content and transition-distance multiset, different order.
3. TR-R/TR-D: recurrence versus continued displacement; not matched total change.
4. TR-HA/TR-HB: identical content/transitions and A endpoints, different intervening history.

## Empirically unknown before execution

Unknown are: the best configuration; ranking changes; whether adaptation is valuable or weak in any scenario; whether prior development helps or becomes a liability; configuration sensitivity or insensitivity; whether TR-G is harder than TR-J; whether TR-R is harder than TR-D; whether TR-HA or TR-HB is preferable; whether any history produces path dependence; and whether any scenario discriminates later strategies. Analysis code must not encode answers.

## Frozen assessment

**PASS:** the predefined range produces multiple qualitatively different and interpretable adaptive demands plausibly useful for later strategy discrimination, without collapsing to a scalar ordering such as “more change = harder.” Coverage is assessed across the range. A universal cumulative leader does not imply FAIL; multiple winners do not imply PASS.

**PARTIAL:** meaningful interpretable variation exists, but important predefined scenario classes collapse onto essentially the same adaptive challenge. Preserve the result and identify what appears missing before Campaign 2; add no rescue physics.

**FAIL:** the proposed scenarios generate essentially the same adaptive problem, or differences are dominated by artifacts of the frozen implementation rather than problem/environment structure. Preserve the negative result; do not rescue it by changing the model.

## Campaign 0 provenance

The test-range contamination labels remain unchanged: TR-PR is identical to Campaign 0 H2; TR-G/TR-J/TR-HA/TR-HB use known H0/H1 content in new orders; TR-R is structurally related to H3; TR-PM and TR-D are pre-performance Campaign 1 scenarios. Campaign 0 outcomes do not alter this protocol.

## Machine-readable authority

`results/foundations/campaign1_protocol/pre_experiment_protocol.json` records exact sequences, resolved configuration states, conditions, seeds, parameters, CRN policy, run counts, retained variables, contrasts, assessment rules, unknown claims, and provenance. It contains no Campaign 1 result.
