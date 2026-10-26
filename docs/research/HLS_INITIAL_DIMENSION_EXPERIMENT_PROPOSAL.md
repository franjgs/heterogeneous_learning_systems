# Proposed first incremental HLS experiment

**Status:** proposal for PI decision; not approved for implementation or
execution. **Prepared:** 26 October 2026.

## Dimension and question

Study one dimension: **how individual competencies are paired across workers**
(their cross-skill dependence), while holding each skill's marginal
distribution exactly fixed. This isolates capability distribution before
studying its interaction with learning, information, changing demand, or
adaptive organization.

**Question:** When a collective must allocate workers to distinct tasks under
a one-worker/one-task constraint, does the association between workers'
competencies change attainable collective output even if the skill-by-skill
marginals and total competence are identical?

This is a focused test of whether aggregate competence summaries suffice for
collective allocation. The linear synthetic production assumption below is
explicit; it is not asserted as a universal physical law or a novel result.

## Scenario and organization

- **Organization:** 12 workers, two task types X and Y, and one simultaneous
  request for each task. Both requests must be assigned to distinct workers.
  Each worker can take at most one task; the collective resource budget is
  two assignments. Twelve candidates create a nontrivial collective matching
  choice; three-worker cases remain appropriate for code or mathematical
  checks, not for this collective-performance claim.
- **Capabilities:** each worker `i` has two fixed values `c[i,X], c[i,Y]` in
  `[0,1]`. If assigned to task `k`, realized output is `c[i,k]` output units.
  Collective output is the sum over the two assigned jobs. There is no
  learning, transfer, uncertainty at decision time, or time evolution.
- **Paired competence profiles:** for each of 50 proposed independent seeds,
  draw two 12-value vectors from a predeclared uniform distribution on
  `[0,1]`. Keep those exact vectors in all conditions. Pair the Y values to
  the X values in three ways: same sorted rank (positive/assortative), an
  independent random permutation, and reverse sorted rank
  (negative/complementary). Apply one shared random permutation of worker IDs
  to all three profiles. Every condition therefore has exactly the same
  empirical marginal for X and Y, and the same aggregate skill totals; only
  the within-worker pairing differs.

The scenario is simple, scales directly in worker count and task count, and
represents a standard HLS problem: allocate a heterogeneous capability pool
when workers cannot serve every task simultaneously. The chosen size is a
pragmatic initial scale, not a universal threshold or a scale-generalization
claim.

For profile pairing `π`, the feasible collective optimum is
`V(π) = max_{i != j} [x_i + y_{π(j)}]`: worker `i` serves X and a different
worker `j` serves Y. The competence-blind expected output under a uniform
feasible assignment is exactly `(sum_i x_i + sum_i y_i)/12`, identical across
the three pairings. That equality is a useful implementation check.

## Baselines and measures

Evaluate the same competence matrix and feasible set with:

1. **Information-blind feasible reference:** expected output under a uniformly
   random one-to-one assignment, computed exactly over all feasible pairs.
2. **Greedy feasible matching:** deterministic descending-edge selection,
   with a predeclared stable tie rule.
3. **Exact feasible matching:** the existing N×K Hungarian assignment
   optimizer; this is the optimum for the declared additive objective and
   constraints, not an oracle with extra information.

Report individual assigned output, output by task, collective total output,
whether both task slots are served, assignment regret relative to exact,
resource use, and decision runtime. Keep competence, realized output, and
collective performance distinct. All policies use the same complete
competence matrix; no information advantage is introduced.

## Isolation and analysis

Within each seed, the three capability profiles have identical per-skill
values, task requests, capacities, feasible actions, objective, and baselines.
The only changed variable is how the two skill values are paired across
workers. The primary estimand is the paired difference in exact feasible
collective output between the three association conditions. Greedy and
information-blind results are secondary comparisons of how each strategy
uses the same structure.

Use 50 paired population seeds as a proposed initial sample; this is a
moderate-compute starting point, not a power guarantee. Treat the seed as the
independent unit; do not count workers, assignments, or the three conditions
as independent observations. Report per-seed contrasts, means, dispersion,
and paired 95% bootstrap confidence intervals over seed-level contrasts.
Before execution, CE/E3 should freeze a precision target; it must not be
revised in response to observed test results. No condition or seed will be
selected based on its result.

The skill-value distribution, pairing definitions, seeds, task counts, and
tie rules must be frozen before execution. A negative, null, or opposite
direction result is retained. If preliminary mathematical analysis shows
that the exact effect is fully determined by a standard rearrangement or
assignment result and yields no useful HLS-level characterization, treat the
experiment as a bounded calibration/control and do not expand it into a
publication campaign.

## Reuse, limits, and decision requested

The exact assignment formulation can reuse
[`HungarianAssignmentOptimizerNK`](../../src/hls/hls_lab_nk_assignment.py),
already checked against enumeration in the [S1 reference](../HLS_CURRENT_STATE.md).
The greedy comparator has a corresponding bounded N×K implementation in
[`run_hls_hungarian_assignment.py`](../../experiments/run_hls_hungarian_assignment.py).
ExperimentRun/HLS-PEF are optional for a later implementation; this proposal
does not require changing either contract or creating new infrastructure.

The experiment isolates static capability dependence under additive output.
It does not establish results for nonlinear production, unequal task demand,
resources beyond the one-to-one assignment constraint, learning, or larger
scale. The main scientific risk is that the result reduces directly to known
assignment/complementarity theory and contributes only a useful HLS control.

This static study does not test RQ0, competence development, or HLS-H3. The PI
must decide whether it should precede or sit alongside the active CE-03 work;
this proposal does not change that priority.

**PI decision requested:** approve this as a bounded first study, request a
reframing, or decline it. No code, experiment, campaign, or new algorithm is
authorized by this proposal.
