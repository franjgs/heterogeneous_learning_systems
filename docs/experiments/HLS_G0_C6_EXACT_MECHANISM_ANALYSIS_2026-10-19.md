# HLS-G0-C6 — Exact Mechanism Analysis

**Date:** 19 October 2026  
**Scope:** exact analysis of the existing two-agent, two-task, four-period
model and the archived campaign; no new simulation or Monte Carlo run.  
**Evidence:** [campaign report](HLS_G0_C6_EXPLORATORY_REPORT_2026-10-19.md),
[trajectory results](../../results/experiments/hls_g0_c6/exploratory_results.json),
[runner](../../experiments/run_hls_g0_c6.py),
[model builder](../../src/hls/synthetic/e1_minimum.py), and
[exact solver](../../src/hls/synthetic/exact.py).

## A. Model and policies

State is competence matrix `C` plus remaining one-unit development budget
`b`; time is `t`. A task `q_t` is observed, then one agent `a_t` is routed.
Reward is `r(C,q,a)=C[a,q]`. The routed agent determines an A1 opportunity:
`p(O=1|a=M1)=0`, `p(O=1|a=M2)=1`, independent of task. Only after observing
`O` does the policy select development. Development can improve task 1 for
either learner by `c' = c + eta(1-c)`, consumes the whole budget, and has zero
objective cost. Demand is exogenous: stationary probabilities are `(0.5,
0.5)`; changing probabilities are `(0.8,0.2)` for periods 0–1 and
`(0.2,0.8)` for periods 2–3. A terminal task-1 reward equal to the best
agent's task-1 competence is added after period 3.

The policies compared are the executable exact HLS controller, which jointly
selects routing and post-opportunity development; and BEST_STATIC, which
globally optimizes a stationary task-to-agent map over the demand law, then
optimizes development continuation conditional on that map. At `eta=.75`
its map is `task 1→M2, task 2→M1`. BEST_STATIC is strong in the static-routing
class, but is not a fixed development policy. MYOPIC and STRONG_SEP do not
provide the comparison requested here; at the initial states their immediate
greedy route is M1 and they never develop in these cells.

The information sequence is unchanged: **route → opportunity observation →
development**. Policies know the transition and demand law, but not future
realized tasks. All values below are exact policy/Dynamic Programming values
from the existing solver or exact enumeration of its induced finite Markov
chain. No future task realization is supplied to the policy.

## B. Reachable states and decisions (`eta=.75`)

Write `C0=((.8,.8),(.6,.6))`, `CH=((.95,.8),(.6,.6))` for the HLS-trained
state, and `CB=((.8,.8),(.9,.6))` for the state after BEST_STATIC develops
M2 on task 1. `U` denotes `C0,b=1`; `B` denotes `CB,b=0`.

| Policy | Period | Reachable pre-decision competence/budget states and probabilities |
|---|---:|---|
| HLS | 0 | `U`: 1 |
| HLS | 1–3 | `CH,b=0`: 1 |
| BEST_STATIC, stationary | 0 | `U`: 1 |
| BEST_STATIC, stationary | 1 | `U`: .5; `B`: .5 |
| BEST_STATIC, stationary | 2 | `U`: .25; `B`: .75 |
| BEST_STATIC, stationary | 3 | `U`: .125; `B`: .875 |
| BEST_STATIC, changing | 0 | `U`: 1 |
| BEST_STATIC, changing | 1 | `U`: .2; `B`: .8 |
| BEST_STATIC, changing | 2 | `U`: .04; `B`: .96 |
| BEST_STATIC, changing | 3 | `U`: .032; `B`: .968 |

At each listed pre-decision state, pair these masses with the period's demand
distribution: stationary `(q1,q2)=(.5,.5)` throughout; changing `(.8,.2)` in
periods 0–1 and `(.2,.8)` in periods 2–3. Those products enumerate the
state-demand support. Opportunities are deterministic conditional on route,
so there are no additional stochastic state branches. The two policies share
state-demand support only in period 0; after that their competence/resource
states are disjoint. Thus later decision comparisons are each on their own
on-policy support, not comparisons at a shared state.

For completeness, the following are the Bellman values at every positive-
probability period-1-to-3 state-demand pair. Each entry is `continuation / V`,
where continuation is the exact expected value after current reward and `V`
is the exact value of the selected action from that state. They are all
reachable as specified in the support table. For HLS state `CH`, selected
route is M1 for both tasks (immediate rewards `.95/.8`), opportunity is 0 and
development is null. For BEST_STATIC state `B`, route is M2/M1 (rewards
`.9/.8`); task-1 opportunity is 1 but budget is exhausted, and development
is null. For BEST_STATIC state `U`, route is M2/M1 (rewards `.6/.8`); task-1
opportunity is 1 and it develops M2 in periods 1–2, M1 in period 3; task 2
has no opportunity and null development.

| Reachable policy/state | Demand | t | q1 continuation / V | q2 continuation / V |
|---|---|---:|---:|---:|
| HLS / CH | stationary | 1 | 2.700 / 3.650 | 2.700 / 3.500 |
| HLS / CH | stationary | 2 | 1.825 / 2.775 | 1.825 / 2.625 |
| HLS / CH | stationary | 3 | .950 / 1.900 | .950 / 1.750 |
| HLS / CH | changing | 1 | 2.610 / 3.560 | 2.610 / 3.410 |
| HLS / CH | changing | 2 | 1.780 / 2.730 | 1.780 / 2.580 |
| HLS / CH | changing | 3 | .950 / 1.900 | .950 / 1.750 |
| BEST_STATIC / B | stationary | 1 | 2.600 / 3.500 | 2.600 / 3.400 |
| BEST_STATIC / B | stationary | 2 | 1.750 / 2.650 | 1.750 / 2.550 |
| BEST_STATIC / B | stationary | 3 | .900 / 1.800 | .900 / 1.700 |
| BEST_STATIC / B | changing | 1 | 2.540 / 3.440 | 2.540 / 3.340 |
| BEST_STATIC / B | changing | 2 | 1.720 / 2.620 | 1.720 / 2.520 |
| BEST_STATIC / B | changing | 3 | .900 / 1.800 | .900 / 1.700 |
| BEST_STATIC / U | stationary | 1 | 2.600 / 3.200 | 2.3625 / 3.1625 |
| BEST_STATIC / U | stationary | 2 | 1.750 / 2.350 | 1.575 / 2.375 |
| BEST_STATIC / U | stationary | 3 | .950 / 1.550 | .800 / 1.600 |
| BEST_STATIC / U | changing | 1 | 2.540 / 3.140 | 2.376 / 3.176 |
| BEST_STATIC / U | changing | 2 | 1.720 / 2.320 | 1.590 / 2.390 |
| BEST_STATIC / U | changing | 3 | .950 / 1.550 | .800 / 1.600 |

The first routing divergence is period 0, task 2, which has probability .5
(stationary) or .2 (changing). Both policies have `U`. HLS routes M2; its
immediate reward is .6, opportunity probability 1, then it develops M1/task
1. BEST_STATIC routes M1; immediate reward .8, opportunity probability 0,
and development is necessarily null. HLS therefore sacrifices .2 immediate
reward in this state.

At the other initial demand, task 1, both route M2 (reward .6, opportunity
probability 1), but their development decisions already differ: HLS develops
M1/task 1, BEST_STATIC develops M2/task 1. The opportunity is observed before
these actions. This difference is important: the gap is not attributable to
routing changes alone.

After its period-0 development HLS reaches `CH,b=0` and routes M1 for both
tasks: reward .95 for task 1 and .8 for task 2; the opportunity probability
is 0 and development is null. This reverses its period-0 route from M2 to M1.
BEST_STATIC remains at its task map. If it has developed, its state is `B`:
it routes M2 on task 1 for .9 and M1 on task 2 for .8. If it has not yet seen
task 1, it remains at `U,b=1`; it routes M2 on task 1 (reward .6, opportunity
1) and M1 on task 2 (reward .8, opportunity 0). With remaining budget it
develops M2 on an opportunity before the final period; if the first
opportunity arrives in period 3, it develops M1 because only terminal reward
remains. It otherwise chooses null development. These are the complete
on-policy state/action patterns for the two supports above.

## C. Bellman choice at the first divergence

At `U`, period 0, observed task 2, the HLS continuation values for the two
candidate routes are:

| Demand law | Route | Immediate reward | `P(opportunity)` | Development after observation | HLS Bellman action value |
|---|---|---:|---:|---|---:|
| Stationary | M1 | .8 | 0 | null | 4.100 |
| Stationary | M2 | .6 | 1 | develop M1/task 1 | **4.175** |
| Changing | M1 | .8 | 0 | null | 4.010 |
| Changing | M2 | .6 | 1 | develop M1/task 1 | **4.130** |

The stationary `M2` route has conditional continuation value 3.575 after
current reward; the `M1` route has 3.300. Under changing demand those
continuations are 3.530 and 3.210. Thus the opportunity raises continuation by
.275 / .320, exceeding the .2 current reward sacrifice. In the exact local
identity, `Q(M2)-Q(M1) = -.2 + (W1-W0)`, yielding +.075 stationary and +.120
changing. BEST_STATIC's actual task-2 action is M1; its conditional total
value from this initial state/task is 3.98125 stationary and 3.94720
changing. HLS's task-2 value is 4.175 / 4.130.

For initial task 1, routing is M2 under both policies, but HLS develops M1
whereas BEST_STATIC develops M2. The respective conditional policy values
are 4.175 versus 4.050 (stationary) and 4.130 versus 4.020 (changing).

This is the canonical routing–opportunity calculation already recorded in
[RQ0 routing boundaries](../theory/rq0_routing_integration_boundaries.md),
Section 5: an immediate loss is traded for action-conditioned continuation
value. Here its assumptions hold: route affects the immediate competence
reward and opportunity probability; conditional on the opportunity and
development action, the transition is otherwise route-independent; demand
evolves independently of routing.

## D. Exact expected-value decomposition

The exact identity is
`J = expected operational rewards − expected development objective cost +
expected terminal reward`.

| Demand | Policy | Period 0 op | Period 1 op | Period 2 op | Period 3 op | Op total | Dev cost | Terminal | Total |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|
| Stationary | HLS | .60000 | .87500 | .87500 | .87500 | 3.22500 | 0 | .95000 | 4.17500 |
| Stationary | BEST_STATIC | .70000 | .77500 | .81250 | .83125 | 3.11875 | 0 | .896875 | 4.015625 |
| Changing | HLS | .60000 | .92000 | .83000 | .83000 | 3.18000 | 0 | .95000 | 4.13000 |
| Changing | BEST_STATIC | .64000 | .83200 | .81760 | .81808 | 3.10768 | 0 | .89776 | 4.00544 |
| Difference, stationary | HLS − BEST_STATIC | −.10000 | +.10000 | +.06250 | +.04375 | **+.10625** | 0 | **+.053125** | **+.159375** |
| Difference, changing | HLS − BEST_STATIC | −.04000 | +.08800 | +.01240 | +.01192 | **+.07232** | 0 | **+.05224** | **+.12456** |

There is no objective development-cost difference because its configured
coefficient is zero. This does **not** mean resource use is identical: HLS
uses its unit at period 0 to develop M1 in every path. BEST_STATIC's exact
development-action probability by period is `.5,.25,.125,.0625` under
stationary demand and `.8,.16,.008,.0064` under changing demand. It develops
M2 before the final period, M1 if its first opportunity is in the final
period, and otherwise does not develop. HLS's development probability is 1
at period 0 and 0 thereafter. These resource differences are not charged to
the objective in this configuration.

The decomposition is an exact accounting identity, not a unique causal
allocation of the gap to independent “routing” and “development effects.”
Those decisions interact through opportunity and subsequent state. The
conditional initial-demand decomposition is also exact:

| Demand | Initial task | Probability | HLS − BEST_STATIC conditional value |
|---|---|---:|---:|
| Stationary | task 1 | .5 | .12500 |
| Stationary | task 2 | .5 | .19375 |
| Changing | task 1 | .8 | .11000 |
| Changing | task 2 | .2 | .18280 |

Weighting gives `.5(.125)+.5(.19375)=.159375` and
`.8(.110)+.2(.1828)=.12456`.

## E. Mechanism, counterfactual, and feasible witness

**Exact mechanism:** (1) both policies use M2 on task 1 initially, but HLS
uses the resulting opportunity to develop M1 while the fixed-map optimizer
develops M2; (2) on task 2, HLS additionally routes to M2, sacrificing .2 to
obtain an opportunity, while the fixed map assigns task 2 to M1 and receives
none; (3) HLS's M1/task-1 competence becomes .95, after which it routes M1 on
both tasks; (4) BEST_STATIC's task-1 route remains M2, whose trained
competence is .9. Thus development changes the capability state and HLS
exploits it with state-dependent routing. Immediate reward is lower in the
first task-2 divergence, not its cause; later operational reward and terminal
reward more than offset that loss.

A positive-probability witness is task sequence `(2,1,1,1)`. Its probability
is `1/16` under stationary demand and `.0064` under changing demand. HLS gets
period rewards `.6,.95,.95,.95`, develops M1 after period 0, and terminal
reward `.95`, total **4.40**. BEST_STATIC gets `.8,.6,.9,.9`, develops M2
after the first task-1 opportunity, and terminal `.9`, total **4.10**. This is
an illustrative path, not the expected-value decomposition.

The decomposition shows HLS's operational advantage emerges after the first
period: stationary period differences are `−.10,+.10,+.0625,+.04375`; changing
period differences are `−.04,+.088,+.0124,+.01192`. The terminal contribution
is also positive. There is no separate switching cost. Organizational
flexibility is therefore a mediator for exploiting the different developed
competence, while opportunity access and development-recipient choice create
the state difference. The fixed baseline's development optimizer is itself
anticipatory within the fixed routing map; it is not an intentionally weak
“do nothing” comparator.

## F. Learning intensity and demand

At `eta=0` and `.1`, exact values are 4.0 for all four policies in both
demand regimes. On every positive-probability state reached from the initial
conditions, HLS and BEST_STATIC route M1 for both tasks and choose null
development. The static map is `(task1→M1, task2→M1)`. There are no
value-equivalent routing differences in these reachable states: the
decisions coincide. The opportunity-making M2 route on task 2 is rejected
because its continuation gain is too small. At initial task 2 the exact HLS
forced-route values are:

| `eta` | Demand | Q(M1; immediate .8, no opportunity) | Q(M2; immediate .6, opportunity; HLS continuation) |
|---:|---|---:|---:|
| 0 | stationary | 4.000 | 3.800 |
| 0.1 | stationary | 4.000 | 3.850 |
| 0 | changing | 4.000 | 3.800 |
| 0.1 | changing | 4.000 | 3.844 |

At `.1`, the opportunity-conditioned continuation advantage is only .050
stationary / .044 changing, below the .2 immediate loss. At `.75` it is
.275 / .320, above that loss. These three levels do not identify or justify a
critical learning threshold. If M2 is forced at task 2, HLS develops M1 at
`eta=.1`; at `eta=0` its post-opportunity choice is null. In either case the
route remains rejected by the Bellman optimizer.

The same structural sequence explains both high-intensity demand cases.
Changing demand alters the probability weights and expected continuation,
but the gap is positive under stationary demand as well (and is smaller in
the changing configuration). HLS routes M1 after development in both demand
regimes; it does not switch because the task distribution changes. This
design therefore cannot establish that nonstationarity causes or amplifies
the gap.

## G. Relation to established HLS results

- **G1:** establishes static organization/demand interactions and useful
  nulls, without capability evolution. C6 adds a dynamic state but does not
  create a new static organization principle.
- **G2:** already constructs a present-sacrifice/future-development tradeoff
  and decision reversal in a two-agent/two-task finite model. C6 adds a
  four-period horizon, stochastic task law and route-conditioned opportunity,
  but instantiates the same broad present-versus-future mechanism.
- **MIS:** C6 does not use the MIS learning-by-doing competence transition.
  It uses an explicit A1 development action after an opportunity is observed.
  No claim about MIS-v2 is supported.
- **G3/G3-H:** characterize development value through assignment sensitivity
  and show why future development opportunities can affect earlier choices.
  C6 is a quantitative instance of opportunity value; its update law and
  environment are not identical to G3-H's heterogeneous-rate MIS law.
- **RQ0:** its policy-class inclusion and strict-gap criterion concern
  strong SEP specifically. BEST_STATIC is also a restricted policy class
  embedded in HLS, so the observed strict gap is an instance of optimizing
  beyond the fixed-map restriction, not a new inclusion theorem. The exact
  local condition `−ΔR + Δp·D* > 0` predicts C6's high-eta route to M2:
  `−.2+.275=.075` stationary and `−.2+.320=.120` changing. C6 supplies a
  stochastic-demand numerical realization, not a new general result.
- **Campaign 2:** studies a different teaching/MIS-v2 and information
  structure. It reports positive conditional prospective returns for some
  restrictions, but Q11 superiority over Q10 was not established. It does
  not isolate this fixed-routing versus opportunity-gated A1 mechanism.

The four earlier policies' equality at lower eta is a useful negative
control. The high-eta strict gap is a useful quantitative characterization
of the already stated RQ0/G2/G3-H mechanism, but no new structural boundary
has been established. The current comparisons also use an exact model-known
controller, not a learned or partial-information adaptive policy.

## H. Proposition status

**No new proposition is proposed.** The verified statement for these
instances is the exact finite calculation and local inequality above. The
local opportunity-value condition is already present in the RQ0 routing
analysis; extending it to a new theorem would require a distinct unresolved
claim, not just restating that inequality for these parameter values.

## I. Limitations

- Opportunity probabilities are degenerate (0/1); no stochastic opportunity
  uncertainty is tested.
- Only one competence matrix, one development budget, one target skill and
  horizon 4 are analyzed. The demand-change factor is not causally isolated.
- Development objective cost is zero; consumed budget is physical resource,
  not a monetary penalty.
- BEST_STATIC constrains routing only; its development action is optimized
  over the horizon. The gap is not against an entirely frozen organization.
- Exact HLS has model knowledge and the demand distribution, though not
  future realized demand. There is no estimator or exploration.
- C6 uses A1 explicit capability development, not the MIS transition.
- No general parameter condition, prevalence result, empirical relevance, or
  external-literature reproduction follows.

## J. Recommendation

**STOP — as a new C6 research line or novelty claim.**

The gap is precisely generated by action-conditioned access to development,
anticipatory choice of which agent to develop, and subsequent state-dependent
routing. At the first task-2 divergence, the continuation value of the
opportunity exceeds the immediate loss; on task 1, the policies already
disagree about whom to develop despite identical routing. The resulting
operational and terminal advantages are exactly decomposed above. This is a
clear quantitative illustration of the established present/future and
RQ0 routing–opportunity mechanisms, not a distinct structural discovery.

The C6 evidence can remain a useful regression/reference case. The analysis
does not justify further work merely to seek a larger HLS win. A future
question would need a genuinely unresolved target beyond the known
opportunity-value condition; none is established by this instance. No new
experiment was run. No code, model, results artifact, or canonical scientific
claim was modified.
