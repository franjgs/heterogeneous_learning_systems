# Strategy-discrimination gate

## Frozen design and provenance

This is a pre-Campaign-2 diagnostic, **not Campaign 2**. Initial clean HEAD:
`3cf4eec` (prospective-policy freeze); source audit: `7f0df6f`. Required reading:
[policy audit](../theory/CURRENT_POLICY_FORMAL_AUDIT.md),
[policy specification](../theory/POLICY_ABLATION_SPECIFICATION.md), and Campaign 1
[range](CAMPAIGN_1_TEST_RANGE.md), [protocol](CAMPAIGN_1_PROTOCOL.md),
[results](CAMPAIGN_1_RESULTS.md). The prerequisite freeze records zero Q11
candidate-value regression error. Campaign 1 design commits are `05b86cb` and
`bcc3ad8`; historical results are `ac9d421`.

Exactly TR-PR/TR-PM/TR-G/TR-J/TR-R/TR-D/TR-HA/TR-HB × G00/G04/G05/G07 ×
Q00/Q10/Q01/Q11 × seeds 0–9 were executed: 1,280 closed loops, 320 per policy,
23,040 real decisions. Each history has six problems and three decisions per
problem. N=3, K=2, rho=.5, sigma=.10, eta=.35, hypotheses (.8,.2),(.5,.5),(.2,.8),
uniform problem-reset prior, action enumeration, quadrature and tie tolerance
1e-10 are unchanged. Performance is **mu_true**, never the noisy observation.

Q00 freezes prospective belief and capability; Q10 anticipates only belief;
Q01 only capability; Q11 both. All reuse the frozen common operator. Every
real action under every policy still receives the same Gaussian observation
physics, Bayesian update and enabled MIS-v2 development. Only prospective
evaluation differs. CRN uses `Random(seed)`, one standard-normal innovation
per real decision, aligned across all policies, configurations and scenarios.

The execution manifest was written before loops ran. It fixes all design
choices, counts, source hashes and qualitative PASS/PARTIAL/FAIL criteria;
integrity results/output hashes were appended after execution. No thresholds,
parameters or cases were tuned. Campaign 0 provenance remains: TR-PR is H2
(prior-diagnostic/not out-of-sample); TR-G/J/HA/HB reorder known content; TR-R
is structurally related to H3; TR-PM/D were pre-performance Campaign 1 scenarios.
This gate reuses an already characterized laboratory, not an out-of-sample world.

## Primary: paired-state counterfactual decisions

The pre-specified reference is **every Q11 pre-decision state**, including
terminal states: 5,760 states, of which 3,840 are nonterminal. Four read-only
evaluations per state give 23,040 decision rows; six pairwise comparisons give
34,560 rows. Immutable state/belief tuples and exact memoization do not change
the real state. The optional union-of-policy-state audit was not run, as declared
before execution; conclusions are conditional on Q11-reference state coverage.

Before execution the distance was fixed to sum_i,k |Xa[i,k]−Xb[i,k]|, alongside
exact action equality. A divergent pair is *mutually tie-equivalent* only when
each chosen action lies within the existing 1e-10 tolerance of the other
operator's maximum. Full cross-evaluation of the four selected actions is
retained. Every observed divergent pair rejects the other action on **both**
sides; none is a mutual-tie artifact. Minimum reciprocal regrets over divergent
pairs are 2.95e-5 and 2.74e-4, respectively, well above the frozen tolerance.

| Policy pair | Nonterminal differing states / 3,840 | Rate | Mean action L1 |
|---|---:|---:|---:|
| Q00/Q10 | 830 | 21.615% | .216146 |
| Q00/Q01 | 308 | 8.021% | .080990 |
| Q00/Q11 | 854 | 22.240% | .223958 |
| Q10/Q01 | 599 | 15.599% | .160677 |
| Q10/Q11 | 62 | 1.615% | .021875 |
| Q01/Q11 | 583 | 15.182% | .151823 |

Q00/Q11 differing-state counts by scenario (480 nonterminal states each):
PR 45, PM 68, G 122, J 161, R 49, D 123, HA 113, HB 173. By configuration
(960 each): G00 381, G04 114, G05 275, G07 84. Summaries additionally stratify
by within-problem decision and represented/unrepresented true problem.
Representation strata describe states; they do not isolate a mismatch effect.

All 1,920 terminal states collapse exactly. At the first/reset decision Q10
and Q11 always agree; all their 62 disagreements arise at the second decision.
Prospective-information and prospective-development restrictions therefore
do not act uniformly over the visited state range.

### Action patterns and immediate opportunity cost

| Exact pattern | Nonterminal states |
|---|---:|
| All same | 2,958 |
| Information-sensitive (Q10 differs from Q00, Q01 does not) | 553 |
| Development-sensitive (Q01 differs from Q00, Q10 does not) | 31 |
| Both single ablations change | 277 |
| Coupled-only (Q10=Q01=Q00, Q11 differs) | 21 |
| Other mixed | 0 |

These are descriptive action-equality classes, not causal decompositions.
882 states differ under at least one restriction. For Q00 versus Q11,
g(b,S,X00)−g(b,S,X11) is positive in all 854 divergent states and zero elsewhere:
overall mean .002990954, mean conditional on divergence .013448786, maximum
.057067679. This is the **immediate opportunity cost of the Q11 decision
relative to Q00**, not a cost of development or value of information.
Signed immediate differences for all six pairs are preserved; they can be
negative for pairs other than the myopic reference comparison.

## Secondary: independent closed-loop trajectories

Each policy generates its own real history, not counterfactual rewards from
the primary shared states. Means below average four configurations and ten
seeds, and sum expected production over all 18 real decisions.

| Scenario | Q00 | Q10 | Q01 | Q11 |
|---|---:|---:|---:|---:|
| TR-PR | 27.742 | 29.996 | 29.767 | 29.996 |
| TR-PM | 26.845 | 27.832 | 27.543 | 27.834 |
| TR-G | 25.746 | 26.637 | 25.861 | 26.676 |
| TR-J | 25.501 | 26.339 | 25.646 | 26.377 |
| TR-R | 27.434 | 29.274 | 29.007 | 29.264 |
| TR-D | 25.541 | 26.045 | 25.589 | 26.124 |
| TR-HA | 25.718 | 26.659 | 25.846 | 26.671 |
| TR-HB | 25.574 | 26.418 | 25.616 | 26.504 |

Q11 is not uniformly better than Q10: among the 32 scenario/configuration mean
comparisons, Q11−Q10 is positive in 16, negative in four, and within the existing
1e-10 tolerance in 12. TR-R's aggregate Q10 mean exceeds Q11's. G07 remains the
mean cumulative leader in every scenario under every policy. Neither finding
determines the gate classification. Per-problem performance, final-state and
exposure matrices, final recurrence flags, seed-paired differences and first
closed-loop action divergences are retained without winner-based selection.
Among the 1,920 closed-loop policy-pair comparisons, 1,204 differ in at least
one real action; 404 of those nonetheless select the same final action, and
41 reach exactly the same final S. Behavioral reconvergence and state
reconvergence are different observations, neither implying equal cumulative
performance.

## Mechanistic inspection: deterministic representative states

Representatives are the **first occurrence of each observed pattern** in
the original frozen factorial order, not maximum-effect or favorable-seed
searches. Indices below are zero-based (problem, within-problem decision).
Actions list the three agents' (capability-1, capability-2) efforts. Each
example has exactly the same S and b across its four evaluations; detailed
S/b and all cross-objectives are in `representative_decisions.csv`.

1. Both single ablations: TR-PR/G00/seed0, (0,0). S starts entirely at .5,
   b is uniform. Q00 chooses [(0,1),(.5,.5),(1,0)] with g=.750000;
   Q10/Q01/Q11 choose [(0,1),(0,1),(1,0)] with g=.733701. Q11's advantage
   over the Q00 action in its own objective is .090434 despite immediate
   sacrifice .016299. This changes agent 2's real exposure if executed;
   each selected action's MIS-v2 transition then feeds the next real state.
2. Null: TR-PR/G00/seed0, (1,0). Despite distinct objective values, all four
   choose [(0,1),(1,0),(1,0)] with g=1.232946 on the same developed state.
   Anticipation changes values without necessarily changing decisions.
3. Information-sensitive: TR-PR/G00/seed1, (3,0). Uniform reset belief and
   developed S produce Q00/Q01 [(0,1),(.5,.5),(1,0)] (g=1.445749), versus
   Q10/Q11 [(0,1),(0,1),(1,0)] (g=1.424672). Posterior-contingent terminal
   maximization changes the action; prospective development alone does not.
4. Coupled-only: TR-PM/G00/seed0, (2,1). b≈(.650226,.349590,.000184).
   Q00/Q10/Q01 choose [(0,1),(1,0),(1,0)] (g=1.546902); Q11 chooses
   [(.5,.5),(1,0),(1,0)] (g=1.520656). Q11's own objective improves by
   .006269. Prospective Bayes and MIS-v2 together offset .026245 of immediate
   production; neither single restriction changes the selected action here.
5. Development-sensitive: TR-G/G00/seed1, (3,1). b≈(.000013,.143210,.856777).
   Q00/Q10 choose [(0,1),(0,1),(1,0)] (g=1.696446); Q01/Q11 choose
   [(0,1),(0,1),(.5,.5)] (g=1.687503). The latter exercises agent 3's second
   capability as well as its first; anticipated F(S,X) changes the terminal
   production possibilities. Q11's own-objective advantage is .029080.

The computational attribution is to the frozen prospective terms: current
X changes observation likelihood/posterior and/or F(S,X); terminal actions
re-optimize on those simulated states. Real future closed-loop decisions also
depend on realized observations. These counterfactual state inspections do
not assert that a frozen alternative action was actually executed along Q11's
real history. Full real traces are available for every independent policy.

## Validation, nulls and limitations

Q11 exactly reproduces historical Campaign 1 FULL on all 5,760 real steps:
actions, beliefs, S and exposure match as parsed JSON; maximum numeric errors
in mu_true, observed reward and cumulative performance are all **zero**.
Across all policies the unchanged MIS-v2 transition reconstructs with zero
error; independent Bayes and production checks have maximum errors
3.50e-15 and 2.22e-16 after CSV float roundtrip. CRN innovations match exactly.
Factorial completeness, unique run/step keys, all ten seeds per cell, no missing
trajectories, prior resets, capability persistence and frozen C/N/M all pass.
Source hashes guard frozen code and historical raw Campaign 1 results.
Validation suites: 46 tests covering this gate, policy ablations, Campaign 1
closure/protocol/range; 48 further tests covering finite belief, MIS-v2,
problem geometry and the frozen Small Problem World. **94 passed**. The full
historical repository suite was not run. `git diff --check` passes; production
code, frozen policy specification and Campaign 0/1 artifacts are unchanged.

Important negative evidence: 77.03% of nonterminal states are all-same;
Q10/Q11 agree throughout TR-PR reference states; no first/reset state separates
them; information-only and coupled closed loops often perform nearly equally;
the cumulative configuration leader remains invariant. No full scenario is
all-four action-equivalent on its primary reference states. Terminal equality
is a required invariant, not evidence against discrimination.

The samples are related deterministic states under a small ten-seed diagnostic,
not independent statistical observations. No significance tests or novel
divergence cutoffs are used. A three-node quadrature, two-stage prospective
operator and fixed finite internal model limit generalization. Pattern counts
depend on Q11's reference trajectories. Closed-loop differences jointly involve
later inference, exposure and production; they are not additive causal effects.

## Classification and implications

**PASS**, applying the pre-specified qualitative criteria: nonterminal action
differences are reproducible, exceed tie tolerance, occur across all scenarios
and configurations, and include structurally distinct information-sensitive,
development-sensitive and coupled-only patterns alongside extensive nulls.
The result is not based on performance winners or a post-hoc rate threshold.

The frozen range discriminates these specific prospective restrictions. This
supports proceeding to a separately designed scientific review of Campaign 2;
it does not design or execute that campaign, select strategies, or justify
changing the world. Null states and the invariant configuration leader must
remain visible. Unsupported: pure information/development values, additive
causal contributions, strict classical dual control, Q11 optimality, universal
planning or heterogeneous-team superiority, empirical eta calibration, or
generalization outside the declared physics.

## Artifacts and reproduction

Directory: `results/diagnostics/strategy_discrimination_gate/`.

- `execution_manifest.json`: pre-execution design, source hashes, validation and CSV hashes.
- `closed_loop_runs.csv`: 1,280 run keys, cumulative/per-problem mu_true, final S/E.
- `closed_loop_trajectories.csv`: 23,040 real steps; z/C/N/M, b/S before/after,
  action, exposure/development, noise innovation, observed reward and mu_true.
- `paired_state_decisions.csv`: 23,040 read-only evaluations with selected and
  maximum objective, immediate g, exact shared S/b and cross-action objectives.
- `paired_state_comparisons.csv`: 34,560 pair rows, equality, L1, reciprocal
  regrets, tie flags and immediate differences.
- `divergence_summary.csv`, `ablation_patterns.csv`: nonterminal grouped counts.
- `performance_summary.csv`: 128 scenario/configuration/policy cells, ten seeds each.
- `closed_loop_policy_comparisons.csv`: 1,920 seed-paired closed-loop comparisons.
- `representative_decisions.csv`: 20 evaluations, first state of each pattern.
- `analysis_summary.json`: integrity checks, bounded interpretation and PASS.

Runner: `experiments/synthetic/strategy_discrimination_gate/run.py` (refuses
overwriting existing closed-loop runs). Analysis-only entry point:
`python experiments/synthetic/strategy_discrimination_gate/analyze.py`.
Focused tests: `tests/test_strategy_discrimination_gate.py`. No historical
artifact or source physics is regenerated by the analysis or these tests.
