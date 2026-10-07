# Capability geometry gate

## Frozen implementation audit

The gate calls the prototype without modifying it. In
`src/hls/discover_v0.py`, `N_AGENTS=3`, `N_CAPABILITIES=2`, and
`validate_state` requires every `s_ik` to lie in `[0,1]`. The prototype itself
does not impose a state budget; `enumerate_canonical_states` historically used
total budget three. This gate makes the stronger experimental restriction
`sum_i s_i1=sum_i s_i2=1.5` exact for every configuration.

`INDIVIDUAL_ACTIONS` contains `(0,0)`, `(0,1)`, `(.5,.5)`, and `(1,0)`;
`JOINT_ACTIONS` is their Cartesian product for three agents (64 actions).
`production_inputs` computes `Y_k=sum_i x_ik s_ik`, and `ces_reward` computes
`(sum_k theta_k Y_k^rho)^(1/rho)` with `rho=.5`. Agent identity therefore
enters through the matched pair `x_ik s_ik`, while capability identity enters
through both `k` and theta. Theta is restricted to `(.8,.2)` and `(.2,.8)`.

In `src/hls/discover_develop_v0.py`, `run_sequence` resets the unknown belief
to `.5` for every problem, selects an assignment with the existing MPC, draws
the existing Gaussian observation, applies `bayes_update`, and calls
`mis_transition`. That transition updates exactly the exercised cell as
`min(1, s_ik + 1.5 x_ik (1-s_ik)^2)`. Thus the person and capability exercised
determine who learns what. `evaluate_state` in `discover_v0.py` defines initial
`V_K` as the prior-weighted known-theta horizon-three value.

The environment interface accepts explicit sequences of the two existing
theta values. It supports persistent biased demand, a regime change,
alternation, and recurrence. Stable balanced demand is not representable
because there is no balanced theta. “Less predictable” demand is not a
separate model dimension: the policy does not learn an environmental process,
and every problem resets belief.

## Experimental design

Nine agent-permutation-unique configurations use `B=(1.5,1.5)`. Alpha is
`0`, `.25`, or `.5` where applicable. The four paths from the homogeneous
generalist point vary complementary specialization, co-location of both skills
in the same person, partial overlap, and asymmetric redundancy. These family
names are design labels only and never enter a policy.

Descriptors are computed only from `S`:

- individual breadth: count of positive capabilities per person (mean/min/max);
- collective breadth: count of capabilities with positive team coverage;
- concentration: `sum_ki (s_ik/B_k)^2`;
- within-person overlap: `sum_i min(s_i1,s_i2)`;
- redundancy: `sum_k count_i(s_ik>0)`;
- between-agent heterogeneity: mean pairwise squared Euclidean row distance;
- balance: `|B_1-B_2|`; coverage is each exact `B_k`.

All except the intentionally person-level breadth vector are invariant to agent
renaming. Capability-dual physics and control values are invariant when theta
and belief are dualized. A concrete action chosen among exact ties need not be
covariant because the frozen solver uses lexicographic tie-breaking; equivalent
capability-dual matrices are therefore not counted as independent evidence.

Five environments, three shared seeds, four problems, and three decisions per
problem give 135 main executions and 1,620 main trajectory rows. A/B/C/D
controls were run for G00, G06, G07, and G08, yielding 315 total executions.

## Result: gate positive

| Environment | Winning S geometry | Mean performance |
|---|---|---:|
| persistent theta1 | G07 partial overlap, alpha .5 | 20.325515 |
| persistent theta2 | G08 asymmetric redundancy, alpha .5 | 20.719703 |
| change 1122 | G08 asymmetric redundancy, alpha .5 | 19.144247 |
| alternating 1212 | G06 concentrated breadth, alpha .5 | 18.884617 |
| recurrent 1221 | G06 concentrated breadth, alpha .5 | 18.899276 |

The clearest matched comparison is G00 versus G06. Both have exact
`B=(1.5,1.5)`, `V_K=2.9666563146`, within-person overlap 1.5, identical
static-known performance, and identical DISCOVER-only performance. G00 puts
`(.5,.5)` in every person; G06 puts `(0,0)`, `(.5,.5)`, and `(1,1)` in three
different people. Under full DISCOVER+DEVELOP, G06 beats G00 by 0.0434 in
persistent theta1, 0.9269 in change, 1.4850 in alternation, and 0.9504 in
recurrence; G00 beats G06 by 0.6921 in persistent theta2. The ranking reversal
cannot be attributed to initial known productive capacity.

The controls locate most of this difference in development. For alternation,
G00/G06 are equal under static-known (11.866625) and DISCOVER-only (10.656180),
but differ under known-theta DEVELOP (19.752477 versus 20.490781) and full
DISCOVER+DEVELOP (17.399608 versus 18.884617). Discovery changes which cells
receive MIS development, so the remaining difference is sequential coupling,
not a new interaction score.

Complementary specialization is useful relative to homogeneous generalists in
several environments but never wins this grid. It is not monotone: alpha .25
beats alpha .5 in alternation. Generalists never win globally, yet beat
misaligned G07 and G06 under persistent theta2. Redundancy/overlap is relevant
but not separately identified because several descriptors change together;
G08 wins persistent theta2 and change, while its directionally different
counterparts do not.

## Representative causal trajectories (reference seed 20261007)

1. G07, persistent theta1: from `[(0,1),(.5,0),(1,.5)]`, the first assignment
   sends agents to capability 2, capability 1, capability 1. Belief becomes
   `.994822`; the middle agent's first capability rises `.5 -> .875`. Problem
   rewards rise from 4.766005 to 5.219893 by problem four; final middle skill is
   `.962136`.
2. G08, persistent theta2: from `[(0,1),(.75,.25),(.75,.25)]`, the same initial
   allocation drives belief to `.023160`. Subsequent assignments redirect two
   agents toward capability 2. Problem rewards rise 4.065851, 5.495731,
   5.561398, 5.596722; both initially weak second capabilities develop.
3. G08, change 1122: two theta1 problems first raise both `.75` capability-1
   cells to `.934839`. At the switch, belief becomes `.005371`; assignments
   then exercise capability 2, raising later problem reward from 4.158429 to
   5.534575.
4. G06, alternating: `[(0,0),(.5,.5),(1,1)]` first exercises the zero agent's
   second capability, which jumps `0 -> 1`, while `.5 -> .875` for the middle
   agent's first capability. Beliefs follow the environment (`.976840`, near
   zero, one, near zero), assignments switch, and problem rewards are 3.960360,
   4.796713, 5.180346, 4.947198.
5. G00, the matched alternating comparator: all start `(.5,.5)`. The first
   problem spreads development over three already-midlevel cells rather than
   creating the G06 zero-to-one jump. It follows similar belief directions but
   earns 3.596356, 4.413070, 4.671376, 4.718806, ending 1.485010 below G06.

## Representational boundary

The model does represent objectively **who actually knows what**: row identity
changes feasible production, experience, MIS development, later assignments,
and performance. It does not represent **who knows who knows what**. The
manager receives the complete `S` directly in `choose_dynamic_action`; no
expertise-location problem, TMS, communication, or decentralized knowledge is
present. This remains the principal representational deficiency exposed by the
gate.

This gate does not establish that heterogeneity generally wins, identify a
causal effect for any single descriptor, prove adaptive reframing, or generalize
beyond the two theta values, fixed MPC, fixed action set, short horizon, and
current MIS law.
