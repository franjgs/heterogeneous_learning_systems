# Configuration × Environment × Organization × Learning v0.1

## Scope and status

This is a deterministic, finite-grid factorial evaluation of the CE-02
extension to the v0/v0.1 laboratory. It evaluates the existing three
configurations, 125 declared environments, three organization classes, and
learning ON/OFF. It is not a stochastic campaign and the grid frequencies are
not estimates of population prevalence. No physics, MIS transition, reward,
environment sequence, or pre-existing policy was changed.

Reproduce from the repository root with:

```sh
python experiments/synthetic/prototype_v01/run_fixed_organization_factorial.py
```

The runner refuses to overwrite its output directory. Results and hashes are
under `results/experiments/configuration_environment_factorial_v01_fixed/`.
The historical two-policy v0.1 results remain in
`results/foundations/configuration_environment_performance_v01/` and were
used only for the pre-run regression check.

## Validation before execution

The v0 and v0.1 suites passed (25 tests). Re-evaluation of the historical
375 configuration–environment rows reproduced every stored `GREEDY_USE` and
`JOINT_DP` value exactly, for both learning conditions. Thus all 750
policy/condition comparisons matched the old ledger with zero mismatches.
Historical artifacts were not rewritten.

`FIXED_BEST` is the retrospective maximum of the three constant-agent
assignments for a given configuration, known sequence, and learning setting.
It is an oracle within the fixed class, not an online policy and not an
information-matched baseline against `GREEDY_USE`. In six of the 750 cells its
stored floating-point value exceeds `JOINT_DP` by roundoff only; the largest
difference is `1.7763568394002505e-15`, below the laboratory's frozen
`EXACT_TOL = 7.105427357601002e-15`. No dominance violation exceeds that
existing tolerance.

All three evaluators receive the same initial configuration, generated
16-task sequence, MIS transition, horizon, and reward definition. Learning
OFF uses the same transition with scale zero. These are deterministic known-
sequence evaluations; no inferential confidence intervals are applicable.

## Observed finite-grid results

The complete 2,250-row policy ledger is `policy_ledger.csv`. Values below are
equal-weight means over the 125 grid points for each configuration and
condition; they summarize this declared grid only.

| Configuration | Learning | FIXED_BEST | GREEDY_USE | JOINT_DP |
|---|---:|---:|---:|---:|
| GENERALIST | ON | 11.701586 | 11.701586 | 11.701586 |
| GENERALIST | OFF | 8.000000 | 8.000000 | 8.000000 |
| SPECIALIST | ON | 13.454534 | 16.000000 | 16.000000 |
| SPECIALIST | OFF | 10.400000 | 16.000000 | 16.000000 |
| DIVERSE | ON | 12.257178 | 13.658162 | 13.658162 |
| DIVERSE | OFF | 9.440000 | 12.800000 | 12.800000 |

Observed organizational differences, using the frozen numerical tolerance:

- For GENERALIST, `GREEDY_USE` equals `FIXED_BEST` throughout the grid in
  both learning conditions.
- For SPECIALIST and DIVERSE, `GREEDY_USE` strictly exceeds `FIXED_BEST` in
  all 125 environments for each learning condition. The grid-mean gains are
  respectively 2.545466 and 1.400983 with learning ON, and 5.600000 and
  3.360000 with learning OFF.
- `JOINT_DP - GREEDY_USE` is zero in every cell (up to floating-point
  tolerance). The finite-horizon intertemporal optimizer therefore adds no
  measured value over the fair greedy policy class in this particular
  laboratory/grid.
- Configuration rankings under `GREEDY_USE` and `JOINT_DP` are identical:
  SPECIALIST is the unique best configuration in all 125 environments both
  ON and OFF. Under `FIXED_BEST`, SPECIALIST is uniquely best in all ON
  environments; in OFF, all three tie in 25 environments and SPECIALIST is
  uniquely best in the other 100.
- Comparing complete configuration rankings across organization classes,
  `FIXED_BEST` and `GREEDY_USE` differ in 25/125 OFF environments and 0/125
  ON environments. `GREEDY_USE` and `JOINT_DP` rankings never differ.
- Comparing learning ON versus OFF, the identity of the top configuration
  changes for `FIXED_BEST` in 25/125 environments (OFF all-tie becomes ON
  SPECIALIST); it changes in 0/125 environments for either adaptive policy.

Grid-mean learning values (`ON − OFF`) are:

| Configuration | FIXED_BEST | GREEDY_USE | JOINT_DP |
|---|---:|---:|---:|
| GENERALIST | 3.701586 | 3.701586 | 3.701586 |
| SPECIALIST | 3.054534 | 0.000000 | 0.000000 |
| DIVERSE | 2.817178 | 0.858162 | 0.858162 |

These are arithmetic consequences of the implemented reward and MIS update
over the fixed sequence grid, not population-level causal estimates.

## Organizational regimes and interactions

`organizational_regimes.csv` gives cell-level gains and exact-tolerance
classifications. Within each learning condition (375 configuration–environment
cells):

- Fixed assignment is sufficient relative to `GREEDY_USE` for all 125
  GENERALIST cells, and for none of the SPECIALIST or DIVERSE cells.
- Adaptive assignment contributes a strict gain for all 250 SPECIALIST and
  DIVERSE cells; no cell has a positive `JOINT_DP − GREEDY_USE` gain beyond
  tolerance. Across both learning conditions those counts double.
- Thus this finite design contains no environment region where intertemporal
  planning adds value beyond GREEDY_USE. There are broad regions where
  adaptive assignment adds value for SPECIALIST and DIVERSE, but the finite
  grid is not a frequency sample of environments.

The mean change in the adaptive-over-fixed advantage from OFF to ON is
approximately zero for GENERALIST, −3.054534 for SPECIALIST, and −1.959017
for DIVERSE. This describes how development narrows the fixed-versus-adaptive
gap in these configurations; it does not establish a general law. The
machine-readable `organization_learning_interactions.csv` contains cellwise
learning effects and the paired differences-in-differences.

## Nulls, counterexamples, and interpretation

The principal null is that `JOINT_DP` never exceeds `GREEDY_USE` on the
specified factorial. This is a real negative result for the claim that
intertemporal assignment adds value in this model/grid. A second null is that
organization does not change performance for GENERALIST. Conversely,
SPECIALIST and DIVERSE provide consistent finite-grid examples where
state/task-adaptive assignment outperforms even the retrospective fixed-class
oracle. This does not make the fixed comparator information-equivalent; the
comparison is descriptive of policy classes and values under the same
deterministic sequence.

The model uses two task types, three agents, a 16-task known sequence, a
specific competence reward, and the canonical MIS learning increment. The
environment axes are discrete design coordinates with feasibility clipping
and deterministic sequence ordering. Therefore the results do not establish
general properties of heterogeneous teams, realistic environmental change,
learned organizational policies, or prevalence of any regime. `GREEDY_USE`
reacts to the current task and competence state; it does not learn an
organization policy. `JOINT_DP` has full sequence knowledge by construction.

## Machine-readable artifacts

- `policy_ledger.csv`: all 2,250 evaluations, including the three fixed-agent
  candidate values and selected fixed-agent ties.
- `configuration_summary.csv`: finite-grid means/minima/maxima by
  configuration, policy, and learning condition.
- `organizational_regimes.csv`: cell-level policy values, gains, and
  exact-tolerance regime flags.
- `organization_learning_interactions.csv`: cellwise learning value and
  learning-by-organization advantage contrasts.
- `summary.json`, `manifest.json`: design counts, parameters, source and
  historical-reference hashes, and output hashes.

The manifest records the code revision and working-tree status at execution.
The pre-existing historical result directory was only read, and its content
hashes are recorded for traceability.
