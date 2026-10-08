# Equation Traceability

This is the source map for a future LaTeX mathematical section, not manuscript
prose.  No unverified citation is introduced here.

## E1. Aggregate capability output

```text
Y_k(S,X)=sum_i x_ik s_ik.
```

- Symbols: `s_ik` latent capability; `x_ik` allocated effort; `Y_k` aggregate
  output in capability dimension `k`.
- Status: HLS operational definition.
- Implementation: `src/hls/discover_v0.py::production_inputs`.
- Validation: DISCOVER and capability-geometry tests.
- Assumptions: `N=3`, `K=2`, declared action set for current prototype.

## E2. CES production

```text
R_z(S,X)=(sum_k z_k Y_k(S,X)^rho)^(1/rho), rho=.5.
```

- Status: standard/purchased CES family; HLS parameter/domain choice.
- Literature: requires verified CES source before manuscript drafting.
- Implementation: `discover_v0.py::ces_reward`.
- Validation: `test_discover_v0.py`, finite-belief and distance gates.
- Assumptions: nonnegative outputs, normalized nonnegative two-vector `z`.

## E3. Gaussian finite Bayesian update

```text
mu_m=R_z_hat_m(S,X)
L_m(r)=Normal(r;mu_m,sigma^2)
b'_m=b_m L_m(r)/sum_j b_j L_j(r), sigma=.10.
```

- Status: standard Bayes/likelihood machinery; HLS finite repertoire and sigma
  are modeling choices.
- Implementation: `finite_problem_belief.py::finite_bayes_update` using stable
  shifted log weights.
- Validation: M=1/2/3, normalization, represented/unrepresented truth, and
  permutation tests.
- Assumptions: finite `Z_hat`; Gaussian homoskedastic observation.

## E4. Belief-weighted expected production

```text
g(S,X,b)=sum_m b_m R_z_hat_m(S,X).
```

- Status: standard expectation under the finite agent model.
- Implementation: `finite_problem_belief.py::expected_reward`.
- Validation: manual-mixture and binary-regression tests.
- Assumptions: valid finite probability vector aligned with `Z_hat`.

## E5. MIS-v2 capability transition

```text
s+=1-(1-s)exp(-lambda x), lambda>0
eta=1-exp(-lambda)
s+=s+eta(1-s) for x=1.
```

- Status: HLS modeling formulation motivated qualitatively by learning through
  experience; not a literature-prescribed state equation.
- Implementation: `discover_develop_v2.py::capability_after_exposure` and
  `mis_v2_transition`.
- Validation: R1--R7 tests and MIS-v2 sensitivity gate.
- Assumptions: common rate, fixed ceiling one, no forgetting/transfer,
  homogeneous composable exposure.

## E6. Production-surface problem distance

```text
d_R(p,q)=(1/3) sup_{Y1,Y2>=0,Y1+Y2<=3}|R_p(Y)-R_q(Y)|.
```

- Status: HLS modeling choice using standard sup-norm mathematics.
- Implementation: closed form in `problem_geometry.py::production_distance`;
  independent original-definition validator in
  `numerical_production_supremum`.
- Validation: Problem Distance Gate grid and metric tests.
- Assumptions: neutral envelope, current two-output production physics.

## E7. Closed form of problem distance

```text
d_R(p,q)=|p-q|[1+|p+q-1|].
```

- Status: HLS derived result for `rho=.5`; not a novel general theorem.
- Implementation: `problem_geometry.py::production_distance`.
- Validation: 196-pair independent triangular-lattice check, maximum error
  `3.33e-16`, plus endpoint and metric controls.
- Assumptions: E2 with `rho=.5` and E6 envelope/normalization.

## E8. Environmental change

```text
C_t=d_R(z_t,z_(t-1)), t>1; C_1=None.
```

- Status: HLS experimental descriptor.
- Implementation: `problem_geometry.py::change_magnitudes`.
- Validation: recurrence and Small World controls.
- Interpretation: movement from the immediately preceding true problem.

## E9. Historical novelty

```text
N_t=min_(j<t)d_R(z_t,z_j), t>1; N_1=None.
```

- Status: HLS experimental descriptor, not an agent detector.
- Implementation: `problem_geometry.py::historical_novelties`.
- Validation: exact recurrence, represented-novel, and Small World controls.

## E10. Representational mismatch

```text
M_t=min_(z_hat in Z_hat)d_R(z_t,z_hat).
```

- Status: HLS experimental descriptor, not recognized misspecification.
- Implementation: `problem_geometry.py::representational_mismatches`.
- Validation: represented/unrepresented and recurrence controls.
- Assumptions: nonempty finite `Z_hat`.

## Campaign 1 use of E8--E10

Campaign 1 retained `C_t`, `N_t`, and `M_t` as pre-specified structural
descriptors of its eight frozen histories. It did **not** fit, test, or derive
an equation claiming that any one descriptor predicts performance, difficulty,
or strategy value. The Campaign 1 PASS classification rests on the diversity
of retained adaptive trajectories and controls, not on validation of E8--E10
as explanatory metrics.

## E11. MIS-v2 cumulative-exposure identity

```text
E_ik(t)=sum_(tau<t) X_tau[i,k]
s_ik(t)=1-(1-s_ik(0))exp(-lambda E_ik(t))
       =1-(1-s_ik(0))(1-eta)^(E_ik(t)).
```

- Symbols: `X_tau[i,k]` is the continuous exposure allocated by the executed
  action (including `.5`, not merely a binary count); `E_ik` is cumulative
  cell exposure.
- Status: HLS derived result from the MIS-v2 composition assumption and
  exponential remaining-gap formulation; not an empirical discovery or a
  literature-derived theorem.
- Implementation: `discover_develop_v2.py::capability_after_exposure` and
  `mis_v2_transition`.
- Validation: post-Campaign-0 mechanistic reconstruction of 80 H0/H1 pre-A
  states (480 cells), maximum absolute discrepancy
  `1.1102230246251565e-16`.
- Assumptions: fixed `lambda`, no forgetting/transfer, separable cell updates,
  and the same initial `S_0`.
- Consequence: for fixed `S_0` and `E`, capability state is invariant to the
  order of exposures. This does not imply equal policy or performance unless
  subsequent beliefs, assignments, problems, and production consequences also
  coincide.

## E12. Frozen prospective operators

```text
Q00(X)=g(b,S,X)+V0(b,S)
Q10(X)=g(b,S,X)+V0(b,S)+A_I(b,S;X)
Q01(X)=g(b,S,X)+V0(b,S)+A_D(b,S;X)
Q11(X)=g(b,S,X)+V0(b,S)+A_ID(b,S;X).
```

- Status: HLS policy definitions and algebraic decompositions, not empirical
  causes or measured values of information/development.
- Implementation: `finite_problem_belief.py::prospective_action_values` and
  `campaign2_theory.py`; formal source in `POLICY_ABLATION_SPECIFICATION.md` and
  `CAMPAIGN_2_THEORETICAL_SPECIFICATION.md`.
- Validation: all 983,040 candidate-action rows reconstructed the frozen
  operators with maximum absolute error `2.22e-16`; Q11/current regressions
  remained unchanged.
- Assumptions: frozen 64-action space, two-stage lookahead where continuation
  exists, three-node Gauss--Hermite integration, and inherited tie tolerance.
- Boundary: statements that an opportunity term changes an operator ranking
  are tautological consequences of these definitions, not Campaign 2 findings.

## E13. Prospective coupling residual

```text
Gamma(b,S;X)=A_ID(b,S;X)-A_I(b,S;X)-A_D(b,S;X).
```

- Status: HLS internal planner quantity / algebraic residual.
- Implementation: `campaign2_theory.py::opportunity_landscape`.
- Validation: identity covered for all candidates in the retained Campaign 2
  opportunity landscapes.
- Interpretation: non-separability of prospective continuation evaluation.
  It is not physical synergy, team synergy, or a causal interaction.
- Campaign 2 use: D_coupled occurred in 71/15,360 Q11-reference states. This is
  an empirical prevalence result about selected actions, not a new equation.

## E14. Internal prospective advantage

```text
DeltaQ_ab=Q_ab(b,S,X_ab)-Q_ab(b,S,X_00), ab in {10,01,11}.
```

- Status: HLS internal planner quantity; nonnegative up to frozen selection
  tolerance by construction.
- Implementation: Campaign 2 policy evaluation and opportunity-landscape code.
- Validation: selected values and all candidate rankings were independently
  reconstructed from retained data.
- Boundary: `DeltaQ_ab>0` does not imply positive realized consequence. Campaign
  2 observed negative DeltaG in 25.43%, 54.01%, and 25.47% of divergent Q10,
  Q01, and Q11 states respectively.

## E15. Two-reward realized counterfactual consequence

```text
DeltaG_(t,2)^(ab|00)
 = [mu_true(t)+mu_true(t+1)]_(force X_ab, then pi_ab)
 - [mu_true(t)+mu_true(t+1)]_(force X_00, then pi_ab).
```

- Status: HLS realized counterfactual outcome and Campaign 2 primary consequence
  definition; not the global value of a policy.
- Implementation: `campaign2_theory.py::two_decision_counterfactual`; Campaign
  2 runner records both real branches.
- Validation: 46,080 pairs, exactly two within-problem rewards, branch-specific
  Bayes/MIS-v2, shared normal innovations, zero branch/return reconstruction
  error, and 38,846 equal-action controls exactly zero.
- Assumptions: same continuation policy `pi_ab` in both branches, true frozen
  problem, real dynamics, and no crossing of the problem boundary.
- Evidence boundary: Campaign 2 estimates condition on exact policy divergence
  and on the 15,360 nonterminal states generated by Q11 trajectories in the
  frozen test range. They do not estimate unconditional or universal policy
  value.
