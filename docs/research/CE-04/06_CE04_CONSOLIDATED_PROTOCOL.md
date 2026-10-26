# CE-04 — Consolidated Protocol (Pre-freeze)

**Status: NOT FROZEN.** This document consolidates only values and decisions
provided by the CE on 2026-10-26. It does not reconstruct E1/E2/E3 reports.
The five open specifications in §7 and unresolved operational semantics in
§8 prohibit implementation or execution until the CE closes them.

## 1. Scientific scope and conditions

- **Question:** how capability heterogeneity, organization and organization
  scale affect collective performance.
- **First dimension:** capability heterogeneity and its interaction with
  organization.
- **Organization size:** N ∈ {12, 24, 48} agents.
- **Tasks:** four task families.
- **Competence composition:** H0 homogeneous, H1 moderate heterogeneity, H2
  high heterogeneity. Mean competence for each task family must match across
  H0/H1/H2; dispersion and specialization differ. The generator and exact
  profiles are not yet defined.
- **Policies:** P0, least expected load; P1, true competence + expected service
  time + deadline; P2, the same decision function as P1 with estimated
  competence; P3, an established adaptive contextual method. P1 is a
  full-information reference, not a global optimum.
- **No explicit cooperation, individual learning or transfer.** Competencies
  remain constant; each task is served by one agent.

## 2. Workload and resources

- **Horizon:** 400 time units.
- **Arrivals:** Poisson, stated intensity 0.55 arrivals per agent per time
  unit.
- **Demand mix:**

  | Stated phase | Task-family mix |
  |---|---|
  | t = 0–150 | 40/20/20/20% |
  | t = 150–300 | 10/40/40/10% |
  | t = 300–400 | 25/25/25/25% |

- **Deadline:** arrival time + 3 time units.
- **Capacity:** at most one simultaneous task per agent.
- **Scaling:** both resources and demand are proportional to N; nominal
  relative load is constant. The exact resource budget/function is pending.

## 3. Factorial design and planned sizes

The stated factorial is 3 composition conditions × 4 policies × 3 scales = 36
conditions.

| Stage | Replicate seeds | Planned simulations |
|---|---:|---:|
| Pilot | 0–2 (3 seeds) | 108 |
| Full campaign | 1000–1029 (30 seeds) | 1,080 |

These are planned counts only. The pilot is not authorized until protocol
freeze. The campaign requires a subsequent CE authorization.

## 4. Outcomes and analysis specified by CE

- **Primary:** percentage of all received tasks completed correctly within
  deadline.
- **Secondary:** latency, utilization, rejections, errors, deadline
  violations, operating cost, decision cost, outcomes by task family and
  demand phase, and recovery after demand changes.
- Paired contrasts; bootstrap over independent replications; 95% confidence
  intervals; Holm adjustment; TOST with equivalence margin ±2 percentage
  points.

The bootstrap resampling hierarchy and test family/contrast family are not
specified in this record and must be explicit before analysis. No TOST or
statistical conclusion has been executed.

## 5. Policy information boundaries

- P1 can access true competence as a benchmark, plus expected service time
  and deadline information as defined by the eventual decision rule.
- P2 must use the same decision function, replacing true competence with an
  estimate based only on outcomes actually observed by that policy.
- P3 must not access future outcomes or counterfactual potential outcomes.
- P0–P3 are CE-04 labels; existing N×K P0/P1/P2 names refer to different
  production/teaching policies and are not reused as CE-04 implementations.

The exact observable information sets, update times and action constraints
remain to be frozen.

## 6. Randomization and pairing

Scenarios are to be paired, seeds independent, and contrasts paired. The
current laboratory can record named seeds and freeze finite demand trajectories
but does not yet provide CE-04's event-level Poisson arrival and service
streams. Seed-to-stream mapping, pairing unit, and streams for arrivals, task
types, service outcomes and any policy randomization require explicit
implementation-level specification before freeze.

## 7. Five unclosed scientific/technical specifications

1. **H0/H1/H2 generator:** exact construction preserving each task's mean
   while changing dispersion/specialization.
2. **Heterogeneity profiles:** exact profiles and parameter values for H0,
   H1 and H2.
3. **Shared estimator for P2/P3:** estimator, observation target and
   update-only-from-observed-results rule.
4. **P3:** established method, contextual features, parameters, information
   set and update/decision cadence.
5. **Common P1/P2 decision function:** units and rule combining competence,
   expected service time, workload and deadline.

## 8. Operational details still needing explicit freeze

These do not authorize Codex to select defaults: the interpretation of
0.55 arrivals per agent as total rate 0.55N; phase boundary convention at
t=150 and t=300; continuous/discrete time and service-duration semantics;
queue discipline and deadline completion boundary; exact resource scaling;
cost accounting; decision tie-breaking; and the resampling unit/contrast
family for paired bootstrap, Holm and TOST. The CE should resolve these while
incorporating the expert originals and closing the five specifications.

## 9. Freeze gate

Do not implement or run the pilot until all expert originals and addendum are
incorporated, §§7–8 are resolved, policy information/actions/objectives are
consistent, and the CE records a dated protocol-freeze decision. The full
campaign remains separately gated by CE authorization.
