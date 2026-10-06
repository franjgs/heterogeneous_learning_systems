# Configuration × Environment → Performance v0.1

**Status:** Technical protocol and reproducible diagnostic. It is a
characterization/assembly instrument, not a new HLS mechanism, theorem, or
claim of configuration superiority.

**Implementation:** `src/hls/configuration_environment_policy_v01.py`
**Runner:** `experiments/synthetic/prototype_v01/run_configuration_environment_sweep.py`
**Outputs:** `results/foundations/configuration_environment_performance_v01/`

## Scope

This diagnostic reuses Prototype v0 exactly: three agents, two capabilities,
the fixed GENERALIST/SPECIALIST/DIVERSE initial configurations, equal total and
per-capability competence budgets, immediate reward equal to the assigned
capability, and canonical MIS learning-by-doing. Environments are fully known;
there is no LATENT state, uncertainty, DISCOVER operation, transfer, new
learning law, local score, or policy invention.

`GREEDY_USE` is the strong fair current-reward policy class already implemented
in v0. `JOINT_DP` is the exact finite-horizon oracle. Both use the same state,
sequence, transition, and resources.

## Known environment grid

Every environment has 16 one-task opportunities, divided into two portions of
eight. A task is `A` or `B`. The grid is the Cartesian product
`nu, chi, rho ∈ {0,.25,.5,.75,1}`.

- `nu` is the normalized A-composition coordinate. It maps to 2--6 A tasks
  per portion before temporal change: `.0` is B-skewed, `.5` balanced, and
  `1` A-skewed. The retained 25--75% range keeps nonzero temporal changes
  feasible without adding a third task or new demand physics.
- `chi` is the requested magnitude of a compositional shift from the first to
  the second portion. It moves 0--4 A tasks while preserving aggregate task
  composition. At the finite-composition boundary, the requested shift is
  clipped to the largest feasible integer shift and the effective shift is
  recorded in every output; it is never silently rounded.
- `rho` is temporal persistence/clustering. Holding each portion's task count
  fixed, it selects a deterministic ordering from least to most adjacent-task
  persistence. It cannot alter aggregate composition or the inter-portion
  shift.

The test suite verifies the clean interior semantics: at `chi=0`, `nu` changes
aggregate composition without an inter-portion change; at `nu=.5`, `chi`
changes only the inter-portion allocation while preserving aggregate counts;
and `rho` preserves both counts while weakly increasing adjacent persistence.
Boundary clipping is a finite binary-sequence feasibility condition, not a new
physical parameter.

## Recorded quantities

For configuration `C` and environment `E`, development-enabled values carry
`+`; the exact no-development ablation carries `0`:

```text
P(C,E) = V_DP+(C,E)
M(C,E) = V_DP+(C,E) - V_GREEDY+(C,E)
L(C,E) = V_DP+(C,E) - V_DP0(C,E)

I(C1,C2,E) = [P+(C1,E)-P+(C2,E)] - [P0(C1,E)-P0(C2,E)]
```

`points.csv` contains the complete ledger. `interactions.csv` contains `I`.
`regime_maps.csv` records all DP-maximizing configurations and full rankings
for ON/OFF development, preserving exact ties. `management_maps.csv` records
`M`, `M0`, and `L` by point. These are descriptive outputs, not prevalence
estimates or causal claims beyond the declared world.

## Reduction rule

If development leaves configuration rankings and regime boundaries unchanged,
report that negative result. Do not alter physics, add uncertainty, change
baselines, introduce a score, or add an HLS mechanism to manufacture an
effect.
