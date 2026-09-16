# Adversarial stress test of the integrated CIV model

Date: 2026-09-15
Status: technical research record. This audit tests the internal implications of the candidate competence-investment value (CIV) specialization. It does not change RQ0, establish novelty, establish P4, or establish a general HLS result.

## 1. Purpose, scope, and branch statuses

The integrated CIV model was subjected to an adversarial stress test so that a convenient naming scheme for portfolio transformations would not become an unsupported theory. The record preserves all branches examined, including null cases and formulations that should no longer organize the active theory.

The statuses used below are:

- **ACTIVE:** retained as part of the current theory direction, within its stated scope.
- **PARKED:** plausible but not currently justified strongly enough to organize the theory. Parked does not mean false.
- **REJECTED:** a formulation that should not guide the active research direction.
- **NULL-RESULT:** a model-scoped condition in which a proposed mechanism has no value.
- **DERIVED-IN-MODEL:** follows under the explicit specialization.
- **CANDIDATE / NOT ESTABLISHED:** an interpretation or generalization requiring further theory or evidence.

This document supplements, rather than overwrites, the historical vocabulary in [general_research_model.md](general_research_model.md), the CIV scaffold in [theory_integrated_competence_investment_model.md](theory_integrated_competence_investment_model.md), and the earlier minimal laboratory.

**Post-audit programme status.** The statuses below preserve the outcome of this CIV stress test. “Portfolio exposure” remains useful vocabulary within this specialization, but it is not a current programme-level research priority; the active programme priority is cross-domain theoretical and experimental foundations. See [RESEARCH_DOCTRINE.md](../RESEARCH_DOCTRINE.md) and [theoretical_foundations_cross_domain.md](theoretical_foundations_cross_domain.md).

## 2. Starting specialization

Condition on currently observing the first state of a symmetric two-state Markov environment. Let the persistence probability be `rho`, let

```text
lambda = 2 rho - 1,
```

and let `n = H-t`. Then

```text
P(E_(t+k)=E_1 | E_t=E_1) = (1 + lambda^k)/2
P(E_(t+k)=E_2 | E_t=E_1) = (1 - lambda^k)/2.
```

For an action `a`, let its persistent post-success marginal operational values be `m_a^1` and `m_a^2` in the two regimes. Define

```text
bar(m)_a   = (m_a^1 + m_a^2)/2
Delta(m)_a = (m_a^1 - m_a^2)/2.
```

With learning cost `K_a`, success probability `eta_a`, learning delay `delta_a`, and discount factor `gamma`, the specialized CIV is

```text
CIV_a(rho)
  = -K_a
    + eta_a [bar(m)_a G_a + Delta(m)_a Q_a(rho)],
```

where

```text
G_a = sum_(k=delta_a)^n gamma^k
    = gamma^(delta_a) [1-gamma^(n-delta_a+1)] / (1-gamma),  for gamma != 1,

Q_a(rho) = sum_(k=delta_a)^n [gamma(2rho-1)]^k.
```

For `gamma=1`, `G_a=n-delta_a+1` when `n >= delta_a`; if `n < delta_a`, both sums are empty and the future-benefit term is zero. The decomposition follows by substituting the two-state transition probabilities into the discounted expected marginal value:

```text
L_a = bar(m)_a G_a + Delta(m)_a Q_a(rho).
```

Within this specialization, `bar(m)_a G_a` is the discounted cross-regime portfolio value, whereas `Delta(m)_a Q_a(rho)` is the discounted value aligned with the currently observed regime and weighted by persistence. This is an interpretation of the specialization, not a theorem about general HLS environments.

## 3. Results that survive the stress test

### 3.1 Persistence values alignment, not a named strategy

**Status: ACTIVE; DERIVED-IN-MODEL.** For `rho >= 1/2`, `lambda >= 0` and `Q_a(rho)` is non-decreasing in `rho`. More precisely, away from degenerate endpoints,

```text
d Q_a / d rho
  = 2 sum_(k=delta_a)^n k gamma^k lambda^(k-1) >= 0.
```

Consequently, holding the other action parameters fixed,

```text
sign(d CIV_a / d rho) = sign(Delta(m)_a)
```

whenever the derivative is strictly informative. Thus persistence increases the value of a transformation whose marginal benefit is more concentrated in the currently observed regime (`Delta(m)_a>0`), reduces it when the benefit is concentrated in the alternative regime (`Delta(m)_a<0`), and does not affect CIV through this term when `Delta(m)_a=0`.

The derivative can be zero at a boundary (for example, `lambda=0` with all terms of degree greater than one), so “increasing” here should not be read as universally strict. The active result is:

> Environmental persistence changes the value of a competence transformation according to how its operational benefit is aligned with the current regime.

The simplified formulations “more environmental persistence implies SPECIALIZE” and “more environmental volatility implies REPLICATE” are **REJECTED** as organizing claims.

### 3.2 Dominance can remove a transformation entirely

**Status: ACTIVE; DERIVED-IN-MODEL.** Consider two persistent actions `a,b` against the same baseline. Suppose their marginal values are non-negative in every regime and, pointwise,

```text
m_a^1 <= m_b^1,   m_a^2 <= m_b^2,
K_a >= K_b,       eta_a <= eta_b,       delta_a >= delta_b.
```

Also require the binary-success, conditional-independence specialization; a transformation that succeeds must remain available over the same future state path, and the marginal values must be comparable against that baseline. Then the original discounted expectation, rather than only its `G/Q` representation, gives `L_a <= L_b`: action `b` has at least as much non-negative marginal value in each state and begins no later. Hence `eta_a L_a <= eta_b L_b` and

```text
CIV_a <= CIV_b.
```

The inequality is strict when at least one comparison is strict in a way that affects a non-zero discounted term. This is deliberately not a dominance theorem for signed effects, state-dependent success, interacting actions, or different baseline trajectories.

The consequence is important: CIV does not force the existence of SPECIALIZE, REPLICATE, and REBALANCE regions. A feasible transformation can be dominated and disappear from an action map.

### 3.3 REPLICATE survives under capacity exposure

**Status: ACTIVE; DERIVED-IN-MODEL in the stated capacity subcase.** Replication is not valuable merely because redundancy sounds desirable. If learner `S_1` already covers all relevant demand in region 1,

```text
b_1 >= max_e d_1(E_e),
```

and an additional holder has no other operational effect, then

```text
m_R^1 = m_R^2 = 0,
CIV_R = -K_R < 0  for K_R > 0.
```

This is a **NULL-RESULT**: replication without operational exposure is not a reason to invest.

In contrast, suppose in regime `E_1` demand exceeds existing cheap capacity and the teacher serves the excess. If a replication action gives `S_2` competence for region 1, with `c_T>c_2`, then a capacity-and-cost subcase has

```text
m_R^1
  = (c_T-c_2) min{b_2, [d_1(E_1)-b_1]_+},
```

with the analogous expression for `E_2`. This is positive whenever the teacher is substituting for a strictly positive capacity shortfall that the additional learner can serve. Since CIV is continuous in these finite-horizon parameters, a strict inequality

```text
CIV_R > max{0, CIV_B, ...}
```

at one admissible parameter point persists on an open neighbourhood. No equality-tuned example is required. The active interpretation is that an additional competence holder can matter by relieving a real portfolio exposure: capacity scarcity and costly teacher substitution are the mechanisms modelled here. Availability, robustness, latency, and failure tolerance are possible extensions, not mechanisms added by this stress test.

### 3.4 REBALANCE survives under persistent operational mismatch

**Status: ACTIVE; DERIVED-IN-MODEL subject to the crossing conditions.** After a change, a rebalancing transformation can have

```text
m_B^1 > 0,   m_B^2 < 0,
```

so that improving allocation for the currently relevant regime trades off against alternative-regime adequacy. Its value is

```text
CIV_B(rho)
  = -K_B + eta_B [bar(m)_B G_B + Delta(m)_B Q_B(rho)].
```

For example, on an interval in `[1/2,1]` where `Delta(m)_B>0`, the expression is non-decreasing in `rho`. If it is continuous and its endpoint values straddle zero, then a threshold `rho_B*` exists (and is unique under strict monotonicity) such that

```text
rho < rho_B*  -> DO-NOTHING / no rebalancing
rho > rho_B*  -> REBALANCE.
```

The threshold is conditional, not universal. If no endpoint crossing occurs, if the relevant alignment has the other sign, or if the environment is parameterized differently, this ordering need not arise.

There is also a **NULL-RESULT**. If environmental change creates no operational competence mismatch that the transformation can relieve,

```text
m_B^1 = m_B^2 = 0,
CIV_B = -K_B.
```

Environmental change alone therefore does not justify rebalancing.

### 3.5 Learning delay and horizon

**Status: ACTIVE; DERIVED-IN-MODEL for the basic non-negative case.** If `m_a^1 >= 0` and `m_a^2 >= 0`, increasing `delta_a` removes or discounts non-negative future-benefit terms, so CIV cannot increase. Slow competence acquisition can therefore make continued teacher use preferable to investment.

If an action has signed effects across regimes, such as `m_a^1>0` and `m_a^2<0`, delay can interact with state exposure in a more complex, potentially non-monotone way. This branch is **PARKED**: it is potentially interesting but lateral to the active direction.

**Status: ACTIVE; DERIVED-IN-MODEL.** If the horizon ends before learning becomes available (`n<delta_a`), CIV equals `-K_a`. Positive investment requires enough remaining time to amortize acquisition. For `|lambda|<1`, the state-memory component decays term-by-term because `lambda^k -> 0`. Under an undiscounted or sufficiently long effective horizon, cross-regime value can accumulate relative to this decaying alignment term. With a fixed `gamma<1`, early alignment terms remain discounted but non-zero, so this is not a universal asymptotic dominance statement.

## 4. Branch intentionally left out of the active core

### SPECIALIZE as a fundamental regime

**Status: PARKED.** SPECIALIZE is not rejected as a possible competence transformation. Indeed, there can be open parameter sets in which `CIV_S > max{CIV_R,CIV_B,0}`. It is not mathematically degenerate.

Its present scientific weakness is that, in the minimal capacity specialization, further increasing competence of a learner already able to serve a region can leave `U^*(C,E)` unchanged. In that case

```text
m_S^1 = m_S^2 = 0,
CIV_S = -K_S.
```

Giving specialization distinctive value would require a justified competence-to-performance relation under which further competence changes operational utility. Such a relation may be realistic for machine learning, but it must not be introduced merely to rescue a preferred label. Moreover, “improve the learner already good at `z`” can collapse into ordinary individual model improvement rather than a distinct organization-level transformation.

SPECIALIZE therefore remains in the programme vocabulary and retains its links to comparative advantage, learning-by-doing, and Gutjahr-style competence development. It is **ACTIVE but secondary** as vocabulary, while SPECIALIZE as a fundamental CIV regime is **PARKED** until an externally justified HLS mechanism gives it an independent system-level role.

## 5. Teacher buffering

**Status: CANDIDATE / NOT ESTABLISHED.** Teacher buffering is neither an axiom nor a fundamental strategy. It can emerge conditionally:

```text
environment changes
    -> current portfolio has operational exposure
    -> teacher absorbs expensive or scarce work
    -> teacher-generated knowledge or experience becomes usable
    -> some transformation has positive CIV
    -> competence portfolio changes
    -> future teacher dependence falls.
```

The same teacher load can occur without competence investment when `max_a CIV_a <= 0`. This teacher-buffering-without-investment regime prevents the inference that every teacher intervention should produce training.

## 6. Current organizing principle

**Status: model-scoped organizing concept; CANDIDATE / NOT ESTABLISHED outside the specialization.** The relevant object in this stress test is not a fixed taxonomy of SPECIALIZE / REPLICATE / REBALANCE strategies. It is the value of feasible transformations of the competence portfolio.

> Competence evolution is valuable when a feasible competence transformation removes enough discounted future portfolio exposure to amortize its competence-acquisition cost.

Here “portfolio exposure” is a working organizing quantity, not yet a closed general definition. The active structural questions are:

1. **Portfolio exposure:** what future demand cannot be served efficiently by `C_t`?
2. **Transformation value:** what exposure is removed by `T_a(C_t)`?
3. **Environment persistence:** how long is that exposure likely to remain relevant?
4. **Learnability and delay:** can the transformation be achieved reliably and early enough?
5. **Investment cost:** do the future savings amortize the transformation?

This focus replaces the premature effort to build a nominal SPECIALIZE/REPLICATE/REBALANCE map. Rejecting that map as the current organizing framework does not mean that any particular transformation can never be optimal.

## 7. Research-branch register

| Branch / result | Status | Reason | Revisit when |
| --- | --- | --- | --- |
| CIV common framework | **ACTIVE** | One counterfactual value language for competence investments. | Transition and value assumptions can be structurally reduced to strong prior models. |
| R1 WHETHER threshold | **ACTIVE; DERIVED-IN-MODEL** | Direct comparison with the no-investment counterfactual. | A practical observable or estimator of CIV is specified. |
| R2 WHERE local/system reversal | **ACTIVE; DERIVED-IN-MODEL** | Capacity and teacher-substitution exposure can reverse local-gain ordering. | A physical HLS transition makes the comparison measurable. |
| Portfolio-transformation comparison | **ACTIVE; DERIVED-IN-MODEL** | Pairwise CIV identities compare feasible actions without requiring labels. | Candidate action sets or interactions become explicit. |
| REPLICATE under capacity exposure | **ACTIVE; DERIVED-IN-MODEL** | Additional competence can relieve capacity shortfall and costly teacher service. | Other exposure mechanisms are justified, not assumed. |
| REBALANCE under persistent mismatch | **ACTIVE; DERIVED-IN-MODEL** | A mismatch can produce a conditional persistence threshold. | A realistic mismatch/transition model is defined. |
| Teacher buffering as emergent behaviour | **CANDIDATE / NOT ESTABLISHED** | Requires a real coupling from operation to usable knowledge and learning. | Such a coupling and fair alternatives are modelled. |
| SPECIALIZE as fundamental regime | **PARKED** | Current specialization gives no independent system value once existing capacity suffices. | A justified competence--performance mechanism gives it a distinct portfolio role. |
| SPECIALIZE as possible transformation vocabulary | **ACTIVE but secondary** | It remains a possible trajectory, not the active analytic core. | Its system-level mechanism is externally motivated. |
| “Volatility implies replication” | **REJECTED** | Volatility alone can leave replication marginal value at zero. | Never as a standalone claim; analyze exposure instead. |
| “Persistence implies specialization” | **REJECTED** | Persistence values current-regime alignment, not an action name. | Never as a standalone claim; analyze `Delta(m)`. |
| Replication without operational exposure | **NULL-RESULT; DERIVED-IN-MODEL** | Sufficient existing capacity gives `m_R=0`. | A distinct, stated source of operational value exists. |
| Rebalancing without mismatch | **NULL-RESULT; DERIVED-IN-MODEL** | Environmental change that changes no operational value gives `m_B=0`. | A transformation relieves a stated mismatch. |
| Non-monotone delay effects | **PARKED** | Signed regime effects can make delay behavior complex but are lateral now. | The active exposure model requires signed effects. |
| Fundamental S/R/B regime map | **REJECTED AS CURRENT ORGANIZING FRAMEWORK** | Labels neither force distinct regions nor capture dominance/null cases. | Only as a descriptive output of a later justified action space. |
| Portfolio exposure as organizing quantity | **PARKED AS PROGRAMME PRIORITY; retained model-scoped vocabulary** | It connects demand, feasible operation, transformation, persistence, delay, and cost within CIV. | Cross-domain foundation work identifies a system-level need for a general definition. |

## 8. What this audit does not establish

The stress test does not establish a general competence state, a practical CIV policy, realistic learning dynamics, the prevalence of any branch, novelty, superiority to a strong modular controller, P4, or RQ0. It does not convert REPLICATE or REBALANCE into universally valuable strategies. Its contribution to the programme is disciplinary: it retains only model-scoped implications that survive adversarial comparison and records why other formulations are active, parked, null, or rejected.
