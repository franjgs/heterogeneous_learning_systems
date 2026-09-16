# Integrated competence-investment model for HLS

Date: 2026-09-15
Status: integration-theory working model. This document introduces one candidate competence-investment decision model for the HLS programme. It does not change RQ0, establish novelty, establish P4, or establish a general HLS result.

## 1. Scope and epistemic status

The model treats competence investment as a portfolio-level decision inside the A1--A5 architecture. It does not replace the programme-level model or the earlier CR0--CR4 laboratory. R1--R3 below are three resolutions of **one** competence-investment decision:

```text
R1: WHETHER to invest
R2: WHERE to place a competence-changing intervention
R3: WHAT organization to construct through competing transformations.
```

The labels used here are:

- **DERIVED-IN-MODEL:** follows from the explicit CIV definition and the stated specialization.
- **CANDIDATE / NOT ESTABLISHED:** requires a physical transition model, empirical validation, or a stronger comparison class.

## 2. General competence-investment value

Let `C_t` be a provisional competence portfolio, `E_t` the environment, and `a` a competence-changing action selected at time `t`. Let `C_\tau^a` denote the counterfactual portfolio trajectory after action `a`, and `C_\tau^0` the trajectory under the no-investment counterfactual. Let `U^*(C,E)` be the best operational utility attainable from portfolio `C` in environment `E` under the feasible operational allocation for that state. The competence investment value is

```text
CIV_t(a)
  = -K_t(a)
    + E[ sum_{tau=t+1}^H gamma^(tau-t)
         (U*(C_tau^a,E_tau) - U*(C_tau^0,E_tau)) ].
```

Here `K_t(a)` includes the immediate resource, service, data, teacher, or training opportunity costs assigned to the intervention. The expectation is conditional on the information available at time `t` and covers environment, learning, and transition uncertainty. The no-investment action `0` has `K_t(0)=0` and `C_\tau^0` by definition, so `CIV_t(0)=0`.

This definition preserves the HLS axis: competence has value only through future feasible operation. It does not assume that competence is directly observed, that `C_t` is sufficient, or that a central controller can compute CIV exactly.

## 3. A1--A5 interpretation

| Architecture element | Role in the CIV model |
| --- | --- |
| **A1 Distributed heterogeneous competence** | `C_t` records a provisional distribution of effective competence, cost, latency, availability, and learning response. |
| **A2 Collaborative division of labour** | `U^*(C,E)` is induced by feasible allocation among functional student/learner and teacher roles. Roles are not rigid types. |
| **A3 Selective learning and knowledge allocation** | `a` specifies a knowledge-selection and recipient/competence transformation, distinct from the current work allocation. |
| **A4 Portfolio evolution** | `C_\tau^a-C_\tau^0` is the future portfolio difference created by the intervention. |
| **A5 System-level orchestration** | selects a current work allocation and, conceptually, compares competence investments using CIV. No specific algorithm is imposed. |

The two coupled flows are therefore retained: operational allocation determines current utility and potentially formative experience; knowledge allocation selects whether and where that experience changes the future portfolio.

## 4. R1 -- WHETHER: invest or do nothing

Let `A_I` be the available investment actions. Under the CIV comparison, the action-level decision rule is:

```text
choose a in A_I only if CIV_t(a) > 0.
```

At portfolio level, invest rather than do nothing iff:

```text
max_{a in A_I} CIV_t(a) > 0.
```

The boundary between investment and do-nothing is:

```text
max_{a in A_I} CIV_t(a) = 0.
```

**Status: DERIVED-IN-MODEL.** This is a decision identity relative to the explicit no-investment counterfactual, not an optimality result for real HLS. Its use requires that costs, counterfactual operational value, and relevant uncertainty be modelled well enough for the comparison.

## 5. Minimal specialization for analysing CIV

Consider two students `S_1,S_2`, one teacher `T`, and two task regions `z in {1,2}`. The teacher and students have finite environment-dependent operational capacities `b_i(E)`. For a portfolio `C` and environment `E`, let `R(C,E)` be the feasible set of task allocations satisfying those capacities and any stated availability or service constraints. Define:

```text
U*(C,E) = max_{r in R(C,E)} U(C,E,r).
```

The environment is a Markov process with persistence parameter `rho`. One explicit representation is:

```text
P_rho(E_(t+1)=e' | E_t=e) = rho I[e'=e] + (1-rho) Q(e'|e),
```

where `Q` specifies the non-persistence transition component. Thus `rho` changes future exposure through the distribution of `E_tau`; it does not itself prescribe a preferred competence organization.

Each available action `a` has learning cost `K_a`, success probability `eta_a in [0,1]`, and delay `delta_a >= 1`. Conditional on success, it produces a specified portfolio transformation `T_a`; conditional on failure it leaves the comparison portfolio unchanged. Assume, for this specialization only, that success is independent of the environment path conditional on information at `t`, and that the transformation is available from `t+delta_a` onward. Define its conditional marginal operational value by:

```text
m_a(E,C) = U*(T_a(C),E) - U*(C,E).
```

Under these assumptions,

```text
CIV_t(a)
  = -K_a
    + eta_a E[ sum_{tau=t+delta_a}^H
        gamma^(tau-t) m_a(E_tau,C_tau^0) ].
```

The factorization by `eta_a` is not general: it relies on the stated binary-success and conditional-independence specialization. The quantity `m_a` can incorporate future demand, portfolio exposure, capacity and availability scarcity, teacher substitution cost, and the operational consequences of the action.

For compactness, define the discounted exposure value:

```text
L_t(a) = E[ sum_{tau=t+delta_a}^H gamma^(tau-t) m_a(E_tau,C_tau^0) ].
```

Then `CIV_t(a)=-K_a+eta_a L_t(a)`.

## 6. R2 -- WHERE: local gain need not determine CIV

Let `g_a` be an action's local recipient competence gain under a chosen local measure. The model does not assume that `g_a` determines `L_t(a)`. In particular, a gain can be locally large but operationally redundant because another member has sufficient capacity and availability; a smaller gain can relieve a scarce task region or substitute expensive teacher service.

For two actions `a,b`, a local/system ranking reversal occurs whenever:

```text
g_a > g_b
and
CIV_t(a) < CIV_t(b),
```

equivalently, under the specialization,

```text
g_a > g_b
and
eta_a L_t(a) - eta_b L_t(b) < K_a-K_b.
```

**Proposition (local-gain/system-value reversal).** If local gain is not constrained to be order-equivalent to discounted exposure value, there exist admissible action pairs with `g_a>g_b` and `CIV_t(a)<CIV_t(b)`.

**Derivation.** Let `a` add a larger competence increment in a region already covered by an available specialist with slack capacity, so `L_t(a)=0`; let `b` add a smaller increment that relieves a positive-cost teacher allocation or a binding capacity constraint, so `L_t(b)>0`. With equal positive success probabilities and equal costs, `CIV_t(b)>CIV_t(a)` while the local gain ordering is reversed. Unequal costs, success probabilities, and delays produce the displayed more general inequality.

**Status: DERIVED-IN-MODEL.** The proposition establishes existence under the model's allowed portfolio and capacity conditions. It does not show how often reversals occur, how `g_a`, `eta_a`, or `m_a` should be estimated, or that a practical HLS policy can identify them.

## 7. R3 -- ORGANIZATION: competing portfolio transformations

Let the candidate action set be:

```text
A = {SPECIALIZE, REPLICATE, REBALANCE, DO-NOTHING}.
```

These are competing transformations of the same competence portfolio, not separate models or independent pillars. `SPECIALIZE` concentrates a competence; `REPLICATE` creates another holder of a competence; `REBALANCE` changes who holds competence across the portfolio; and `DO-NOTHING` retains the counterfactual portfolio.

For any two investment actions `a,b`, the regime boundary is the pairwise CIV equality:

```text
CIV_t(a) = CIV_t(b)
iff
eta_a L_t(a) - eta_b L_t(b) = K_a-K_b.
```

Thus the requested boundaries are:

```text
CIV(SPECIALIZE) = CIV(REPLICATE)
iff eta_S L_S - eta_R L_R = K_S-K_R,

CIV(REPLICATE) = CIV(REBALANCE)
iff eta_R L_R - eta_B L_B = K_R-K_B,

CIV(SPECIALIZE) = CIV(REBALANCE)
iff eta_S L_S - eta_B L_B = K_S-K_B.
```

The invest/do-nothing boundary is `max_{a in {S,R,B}} CIV_t(a)=0`. The preferred organization is the action with the largest CIV only within this candidate action set and only relative to the stated baseline.

**Status: DERIVED-IN-MODEL.** These are pairwise indifference identities. They are not empirical regime maps, claims that the action set is complete, or an optimality proof for specialization, replication, or rebalancing.

## 8. Null result: volatility alone does not imply replication

Suppose environment volatility is high (for example, `rho` is low), but each existing specialist remains available and has enough capacity to serve every relevant regime. If replication changes no feasible allocation and no optimal operational utility, then:

```text
m_REPLICATE(E,C) = 0 for every reachable E.
```

Consequently `L_t(REPLICATE)=0` and:

```text
CIV_t(REPLICATE) = -K_REPLICATE <= 0.
```

**Status: DERIVED-IN-MODEL.** Environmental volatility by itself therefore does not imply replication. Its potential value depends on the interaction among future demand, portfolio exposure, capacity or availability scarcity, teacher cost, learning cost and speed, adaptation delay, and environment persistence.

## 9. Teacher buffering as conditional behaviour

Teacher buffering is not an axiom of the model. It can emerge conditionally when an environment change raises teacher load because the current portfolio mismatches demand; teacher service generates usable knowledge or formative experience; a feasible intervention has positive CIV; and the successful transformation later makes lower-cost student allocation feasible. The candidate sequence is:

```text
environment change
    -> teacher load rises
    -> teacher-generated knowledge / experience
    -> positive-CIV investment
    -> competence reorganization
    -> teacher load falls
    -> new division of labour.
```

Any link can fail: knowledge may not transfer, learning may be too slow or costly, capacity may not bind, or a frozen portfolio may already cover the changed environment. Broad practical relevance of buffering is therefore **CANDIDATE / NOT ESTABLISHED**.

## 10. Relation to prior work and programme boundaries

The model imports dynamic-investment and human-capital language only as apparatus. Borgonjon and Maenhout provide a serious structural precedent for staffing, learning-by-doing, forgetting, training, shadow training, and future efficiency; their workforce staffing objective does not automatically determine the HLS comparison. Machine Teaching provides learner-aware sequential intervention toward specified targets. Transactive memory systems motivate who-knows-what, complementarity, coordination, and reconfiguration without supplying this normative HLS decision. Comparative advantage, portfolio, and control traditions motivate exposure, scarcity, substitution, persistence, and opportunity-cost terms.

The model does not re-demonstrate these precedents or CR0--CR4. It provides a common candidate value language in which their mechanisms can later be structurally reduced, imported, or falsified.

## 11. What is and is not established

**DERIVED-IN-MODEL:** the invest/do-nothing threshold; existence of a local-gain/system-value ranking reversal; pairwise CIV regime boundaries; and the volatility-alone null result, all under the stated CIV specialization.

**CANDIDATE / NOT ESTABLISHED:** broad practical relevance of these regimes; general benefit of teacher buffering; superiority over strong modular control; novelty; a general RQ0 or P4 result; a final observable competence state; and a practical method for estimating CIV.

The next theoretical task is not to elaborate a second model by default. It is to test whether the assumptions that make CIV decision-relevant survive structural reductions to the strongest prior models and to physically meaningful HLS transitions.

## 12. Adversarial stress-test outcome

The [adversarial CIV stress test](theory_civ_adversarial_stress_test.md) retains CIV as the candidate common framework. It retains REPLICATE when an additional holder relieves a real capacity/cost exposure and REBALANCE when a persistent operational mismatch can be relieved. It parks SPECIALIZE as a fundamental regime: it remains possible vocabulary, but the current specialization gives it no independent system value once existing capacity already suffices.

The nominal SPECIALIZE/REPLICATE/REBALANCE taxonomy is therefore no longer the organizing theory. Within this model, feasible transformations are valued in relation to discounted future portfolio exposure. That concept is retained as model-scoped vocabulary, not as the current programme priority. Persistence does not select a transformation by name, and teacher buffering remains conditional behaviour rather than an axiom. See the [research doctrine](../RESEARCH_DOCTRINE.md) and [cross-domain foundations map](theoretical_foundations_cross_domain.md) for the active programme direction.
