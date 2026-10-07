# Campaign 2 theoretical/mechanistic freeze — C2.0

## 1. Purpose and status

C2.0 specifies executable quantities for studying state/world → internal
opportunity landscape → decision → realized counterfactual consequence. It is
**pre-experiment theory/software validation, not Campaign 2 execution or its
statistical preregistration**. Initial clean HEAD: `5c3fca6`. Prerequisites:
`3cf4eec` (policy ablations) and `5c3fca6` (Strategy-Discrimination Gate).
Authoritative sources: [CURRENT audit](CURRENT_POLICY_FORMAL_AUDIT.md),
[policy specification](POLICY_ABLATION_SPECIFICATION.md),
[Gate report](../experiments/STRATEGY_DISCRIMINATION_GATE.md), Campaign 1
[range](../experiments/CAMPAIGN_1_TEST_RANGE.md) and
[protocol](../experiments/CAMPAIGN_1_PROTOCOL.md), plus their frozen manifests.
Historical gate observations remain development evidence; they are not new
confirmatory results or rewritten as predictions.

## 2. Epistemological layers

| Layer | Quantities | Permitted role |
|---|---|---|
| STRUCTURAL DESCRIPTOR | H(b), D_I, D_I_norm, D_I_loss, H_S, true z and existing C/N/M | Characterize pre-decision world/state/information structure; ask when landscapes arise |
| INTERNAL PLANNER QUANTITY | g, V0, C(X), V_D/V_I/V_ID, A_D/A_I/A_ID, Gamma, Q values | Algebraically describe how the frozen planner ranks actions |
| REALIZED COUNTERFACTUAL OUTCOME | G_(t,2), Delta G_(t,2)^(ab\|00) | Evaluate two real production consequences of a forced first-action contrast |

Structural information descriptors depend on the agent's model; they are not
necessarily external to representation I. Unlike A quantities, they are not
defined as differences between prospective operator values. No layer is an
independent empirical cause merely by being measured. M (physics), I (inference)
and pi (policy) remain distinct; no new pi, M or I is introduced by C2.0.

## 3. Frozen laboratory and notation

N=3, K=2, rho=.5, sigma=.10, eta=.35, three real decisions per problem, existing
64 actions and their Cartesian order; three-node Gauss–Hermite integration
per positive-mass hypothesis; tie tolerance 1e-10 and first tolerance-optimal
selection. Q00/Q10/Q01/Q11 remain restrictions of the same frozen operator.
Effective prospective horizons are 2,2,1. Uniform beliefs reset between problems;
S persists. Real Bayes and MIS-v2 apply under **every** policy.

World z=(p,1−p) need not be in internal Z_hat=((.8,.2),(.5,.5),(.2,.8)). The
eight scenarios are TR-PR, TR-PM, TR-G, TR-J, TR-R, TR-D, TR-HA, TR-HB; probe
configurations remain G00/G04/G05/G07. No definitions or historical artifacts
change. Performance is mu_true=R_z(S,X), not observed noisy reward.

Let g(b,S,X)=sum_m b_m R_z_hat_m(S,X), V0(b,S)=max_U g(b,S,U), and X00* be the
first action within the frozen tolerance of max_X g. F is the unchanged MIS-v2
transition: F(S,X)[i,k]=1−(1−S[i,k]) exp(−lambda X[i,k]), lambda=−log(1−eta).
Exposure is actual fractional effort X[i,k], not an exercised-cell count.
B_num is the existing numerically stable Gaussian Bayes operator, including
its equal-predicted-mean tolerance shortcut and zero-prior behavior.

## 4. Information structure

All entropy logs are natural: H(b)=−sum_(m:b_m>0) b_m log b_m (nats,
unnormalized). In particular deterministic belief has entropy zero.

For every hypothesis define X_m*(S) using the frozen action enumeration and
tie rule applied to R_z_hat_m(S,X). Then

```text
D_I(b,S) = sum_(m<n) b_m b_n 1[X_m* != X_n*]
D_I_norm = D_I / sum_(m<n) b_m b_n, if denominator > 0
           None, otherwise (undefined comparison, not silently zero/NaN)
D_I_loss(b,S) = sum_m b_m [R_z_hat_m(S,X_m*) − R_z_hat_m(S,X00*)].
```

D_I is discrete hypothesis-action disagreement, not information value.
D_I_loss is **Hypothesis-Conditioned Myopic Regret**: model-weighted production
loss from belief-myopic commitment versus hypothesis-specific optimization.
It is not regret against true z, realized regret, an empirical causal effect,
or value of information. Deterministic belief and a shared optimum on every
positive-mass hypothesis give zero regret (subject to the frozen numerical
tie convention). Relabeling hypotheses with aligned weights does not change
these descriptors; canonical ordering is inherited from the model.

## 5. Development headroom

H_S(S)=sum_i,k (1−s_ik) is global capability headroom, a STRUCTURAL DESCRIPTOR.
It measures physical room for development only. High headroom does **not**
imply that development changes decisions or has high productive consequence.
No new heterogeneity/adaptability scalar is introduced.

## 6. Internal opportunity landscape

For each of the 64 current candidates X, define

```text
C(X)    = g(b,S,X00*) − g(b,S,X)
V_D(X)  = max_U g(b,F(S,X),U)
V_I(X)  = sum_m b_m sum_j omega_j max_U g(B_num(b,S,X,r_mj),S,U)
V_ID(X) = sum_m b_m sum_j omega_j max_U g(B_num(b,S,X,r_mj),F(S,X),U)
A_D(X)  = V_D(X) − V0
A_I(X)  = V_I(X) − V0
A_ID(X) = V_ID(X) − V0
Gamma(X)= A_ID(X) − A_I(X) − A_D(X).
```

A_D is **Action-Conditioned Development Opportunity**; A_I is
**Action-Conditioned Information Opportunity**; Gamma is **Prospective Coupling
Residual**. All are INTERNAL PLANNER QUANTITIES, not empirical causal effects.
Gamma measures non-separability of the numerical continuation landscape; its
sign is not assumed or clamped. It is not physical/team synergy, a causal
interaction or dual-control value.

The observation construction is exactly frozen Q10/Q11: r_mj=mu_m(S,X)+
sqrt(2) sigma xi_j, omega_j=w_j/sqrt(pi). Both likelihood and current
production use **pre-development S**. Only continuation production may see
F(S,X). Positive-mass hypotheses and all three Gaussian nodes are handled by
the authoritative operator, not a new approximation.

## 7. Exact operator identities and implementation

```text
Q00(X) = g(X) + V0
Q10(X) = g(X) + V0 + A_I(X)
Q01(X) = g(X) + V0 + A_D(X)
Q11(X) = g(X) + V0 + A_ID(X)
A_ID(X)= A_I(X) + A_D(X) + Gamma(X).
```

These are two-stage identities. At the terminal real decision all four
operators instead equal g; do not attach these two-stage continuations to Q_1.
`hls.campaign2_theory.opportunity_landscape` calls the frozen
`prospective_action_values` for all modes, extracting V=Q−g. This avoids
duplicate quadrature, likelihood or production implementations; extraction
and reconstruction incur ordinary floating-point cancellation/rounding only.
Independent unit checks also compute continuation maxima/integrals using the
existing helpers, over every action of three fixed synthetic states.

C and D_I_loss are nonnegative in exact argmax mathematics; the implemented
first-within-1e-10 selection may be slightly suboptimal. Their raw values are
retained with the inherited tolerance qualification, not clamped to zero.
V0 is always the numerical **maximum**, not the selected action's possibly
tolerance-suboptimal value. The existing Q00-versus-one-stage equivalence
caveat remains: constant addition can change tolerance membership at a
floating-point boundary. No new tie rule or action threshold is introduced.

## 8. Prominent tautology boundary

“A_I changes Q10's ranking” and “A_D changes Q01's ranking” are algebraic
consequences of definitions, **not empirical discoveries**. For example,
Q11(X)−Q11(U)=g(X)−g(U)+A_ID(X)−A_ID(U). This ranking identity neither validates
the internal model in the true world nor guarantees realized gains.
Future empirical questions concern which structural states produce relevant
landscapes, their frequencies, and agreement/disagreement with realized
counterfactual consequences. Gamma(X11)>C(X11) is not required by C2.0 and
is not asserted as necessary for X11 differing from X10 and X01.

## 9. One-decision intervention, two-decision outcome

For ab in {10,01,11}, at a supplied real pre-decision state compute the frozen
pi_ab and pi_00 actions. Branch A forces Xab once; branch B forces X00 once.
**Both then replan with the same pi_ab** on their own updated S and b:

```text
G_(t,2)(X;pi_ab,epsilon) = mu_true(t) + mu_true(t+1)
Delta G_(t,2)^(ab|00) = G_(t,2)(Xab;pi_ab,epsilon)
                       − G_(t,2)(X00;pi_ab,epsilon).
```

This is one initial-action intervention, not a global policy contrast. Exactly
two real rewards are counted, never “through t+2.” Only remaining=2 or 3 is
accepted. True z is fixed in both branches and at both steps; there is no
problem loop/reset, boundary crossing or terminal primary counterfactual.
Each reward is computed before that step's development, followed by real Bayes
and real enabled MIS-v2. Both steps' observations, posteriors and developed S
are retained in immutable records even though the second update has no reward
after it in this endpoint. Original caller inputs are deep-copied to tuples.

`two_decision_counterfactual` uses the actual frozen Q00 operator for its
baseline first action; the landscape's X00* uses immediate-only frozen tie
selection. They coincide in regression fixtures and are mathematically
policy-equivalent. The inherited floating-point tolerance-boundary caveat is
explicit, not repaired by overriding either frozen selection rule.

**Endpoint qualification:** with remaining=3, the second real decision replans
with remaining=2 and can anticipate the third decision. The third production
is NOT included in G_(t,2). This preserves pi_ab as required; replacing it by
the planner's myopic terminal leaf would be a different continuation policy.
Thus the realized endpoint is not an unbiased numerical estimator of Q_2:
it also uses true z, actual observations and receding-horizon replanning.

## 10. CRN and invariants

The primitive accepts exactly two finite standard-normal **innovations**
(epsilon_0,epsilon_1), never seeds or supplied observations. Corresponding
branch positions use the same innovation:

```text
r_A = mu_A + .10 epsilon_j
r_B = mu_B + .10 epsilon_j.
```

The observations need not agree when the true means differ. Branch-specific
posteriors/capabilities are induced consequences, not contamination. Branch
evaluation order cannot change immutable results. Equal first actions and CRN
produce identical branches and exactly zero Delta G. Q10/Q01/Q11 continuation
identity is tested explicitly; no branch falls through to Q11 by default.
No normalization by empirical outcome variance or newly chosen divergence
epsilon is allowed. Exact discrete action identity and existing tie diagnostics
remain the action-discrimination standard.

## 11. Mismatch and world descriptors

Keep existing C_t, N_t and M_t=min_z_hat d_R(z_true_t,z_hat). These are
experimenter descriptors and are **not inputs to the unknown planner**. M_t
is a non-directional future moderator of internal-opportunity/realized-return
agreement, not a theorem that greater mismatch lowers return. No new distance,
novelty detector, model-repair mechanism or normalization is introduced.

## 12. Conceptual hypotheses frozen; not tested here

- **H1 — Information structure:** Hypothesis-Conditioned Myopic Regret and
  belief/action disagreement will help characterize structural states in which
  information landscapes become decisionally relevant. No iff statement.
- **H2 — Development structure:** global headroom alone is insufficient to
  characterize development relevance. Study capability/problem/history states
  associated with differential A_D landscapes and Q01/Q00 divergence; the
  algebraic relation itself is not a finding.
- **H3 — Prospective coupling:** test whether new confirmatory states include
  X11 not in {X10,X01}; characterize with Gamma and complete landscapes.
  No Gamma positivity or Gamma>C requirement.
- **H4 — Internal versus realized consequence:** internal prospective preference
  does not mathematically guarantee positive Delta G_(t,2). Quantify positive,
  zero and negative returns and structural moderators; M is non-directional.

## 13. Confirmatory/exploratory boundary

Seeds 0–9 are already-observed development/gate data. **Seeds 10–49 are reserved
confirmatory Campaign 2 data and are not executed here.** Potential confirmatory
quantities: exact action divergence, immediate opportunity cost, structural
descriptors, full opportunity landscapes, the three Delta G_(t,2) endpoints,
return signs and structural-descriptor/return relationships.

Statistical models, state-sampling/weighting rules, multiplicity, sign reporting
near floating-point zero, replication protocol and primary comparisons are
**not finalized**; they belong to the subsequent preregistration. End-of-problem
and end-of-history returns, team-specific narratives, post-hoc feature
construction and additional geometry descriptors remain exploratory/secondary
unless explicitly preregistered later. They are not implemented now.

## 14. Validation scope and scientific limits

Implementation: new pure module `src/hls/campaign2_theory.py`; focused synthetic
tests `tests/test_campaign2_theory.py`; freeze manifest
`results/foundations/campaign2_theory/pre_experiment_campaign2_theory.json`.
No campaign runner, analysis pipeline, research CSV, figure or scientific result
is created. No seed parameter/RNG exists in the new primitive. Unit fixtures
have fixed states and innovations, not scenario/configuration/seed runs.

Maximum all-action algebraic/independent-continuation discrepancy over the three
synthetic fixtures is 4.440892098500626e-16. This is mathematical/software
validation, not a Campaign 2 result. Existing exact Q11 regression and historical
gate artifact hashes are independently checked. Frozen physics, inference,
policies, scenarios, teams and historical Campaign 0/1/Gate results are untouched.

Validation record: **114 tests passed** (44 new C2.0 checks and 70 existing
regression/provenance/geometry/Bayes/MIS checks). The main selected suite has
110 cases; four additional direct Bayes/validation/MIS unit tests are run
separately. Q11's existing six-case, all-candidate CURRENT regression remains
exact with zero discrepancy. Counterfactual null, branch-order, no-mutation,
shared-innovation, real-transition, same-continuation and horizon tests pass.
JSON/source hashes and frozen gate CSV hashes validate; git whitespace checks
pass. No full repository suite is run: historical sequence tests using seeds
10–49 are deliberately excluded to respect the reservation. No historical
test is weakened. These are validation results, not empirical hypothesis tests.

No empirical frequency, scenario effect, return distribution, new-seed behavior
or scientific superiority is established. Prohibited interpretations: pure
information/development value, additive causal decomposition, Gamma as physical
synergy/causal interaction/dual-control value, global policy value from this
initial intervention, universal planning/heterogeneity superiority, calibrated
eta, or generalization outside frozen CES/Bayes/MPC/MIS-v2. C2.0 is downstream
of already-observed gates; it is pre-confirmatory, not independent of all
previous theory development. **Experimental scientific results in this task:
NONE.** Stop at this freeze; do not proceed automatically to preregistration.
