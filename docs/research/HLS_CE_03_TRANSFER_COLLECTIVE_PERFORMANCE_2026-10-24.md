# HLS-CE-03 — Transfer and Collective Performance

**Status:** ACTIVE — exploratory framing and reuse assessment only. No experiment, campaign, or new algorithm is authorized by this document.
**Strategic decision date:** 24 October 2026.
**Branch:** `feature/hls-laboratory-v1`.

## 1. PI resolution and scope

This mission records the strategic resolution communicated by the PI on
2026-10-24. It does not amend the HLS philosophy or research doctrine.

- **PI-01:** LLM-assisted bibliographic audits are not, by themselves,
  exclusionary filters. Their claims must be checked against sources and
  scientific judgment; this does not waive prior-art analysis.
- **PI-02:** prioritize research on competence transfer and collective
  performance.
- **PI-03:** authorize a six-week exploratory phase, with an initial review
  after two weeks. This is staged exploration, not permission to run a
  campaign under this task.
- **PI-04:** do not develop a new algorithm yet.
- **PI-06:** HLS-CE-01 and HLS-CE-02 remain closed.
- **PI-07:** decide continuation from evidence.

Only the decision identifiers supplied in the PI resolution are recorded;
no PI-05 decision is inferred. This is a scoped research priority within HLS,
not a new definition of the programme.

## 2. Problem-first question and hypothesis

The problem is organizational: **can a transfer that improves the receiving
agent's capability reduce collective performance by changing the distribution
of complementary capabilities or the organization's specialization?**

**HLS-H3 (hypothesis, not established):** A transfer that improves the
recipient's individual performance may harm collective performance by
changing complementarity or specialization.

“Individual improvement” and “collective harm” must be defined as separate
measured outcomes for a specified task mix, resource regime, horizon, and
organization. A competence increment is not itself proof of improved
individual task performance; aggregate competence is not a substitute for
collective performance.

The initial comparison is **fixed organization**, **readapted organization**,
and an **optimal reference**. To separate transfer from reorganization, the
eventual design should include matched transfer-available and transfer-off
conditions for the organizational alternatives, holding the physical instance,
action feasibility, resources, horizon, and evaluation fixed. Exact operational
definitions, information available to readaptation, and the privilege level of
the optimal reference remain to be frozen before any execution. The optimum
must be labelled as an oracle/reference if it uses full state or future
information unavailable to operational policies.

## 3. Existing HLS components to reuse

The following are existing candidate components, not evidence that the
proposed comparison has already been implemented:

| Need | Existing component and boundary |
|---|---|
| Joint productive/teaching actions, shared effort limits, transitions and per-period traces | [`src/hls/hls_lab_v1_integrated.py`](../../src/hls/hls_lab_v1_integrated.py): `run_integrated_sequence`, `IntegratedAction`, P0/P1/P2 and `IntegratedEpisodeRecord`. P0 is production-only; P1 fixes a teaching relation; P2 is a heuristic adaptive teaching policy. These names do not by themselves implement the fixed/readapted/optimal comparison. |
| N×K teaching action, directed efficacy, transfer transition and joint resource validation | [`src/hls/hls_lab_nk_teaching.py`](../../src/hls/hls_lab_nk_teaching.py): `TeachingActionNK`, `TeachingEfficacyNK`, `teaching_transition_nk`, and `validate_joint_action_resources_nk`. Preserve its declared transition semantics. |
| Exact finite-horizon reference with transfer on/off | [`src/hls/synthetic/hls_s4_transfer_exact.py`](../../src/hls/synthetic/hls_s4_transfer_exact.py): `ExactTransferCase`, `solve_bellman`, and independent exhaustive replay. It is a deterministic, full-state finite-instance reference, not a general planner or a ready-made model of every proposed organizational restriction. |
| Existing transfer × MIS contrasts and mechanism traces | [HLS Campaign 2 report](../experiments/HLS_CAMPAIGN2_FINDINGS.md), runner [`experiments/synthetic/hls_campaign2/teaching_mis_assignment.py`](../../experiments/synthetic/hls_campaign2/teaching_mis_assignment.py), and [`tests/test_hls_campaign2_teaching_mis_assignment.py`](../../tests/test_hls_campaign2_teaching_mis_assignment.py). This is bounded, forced-single-lesson evidence with P0 continuation; it does not establish H3 or the fixed/readapted/optimal comparison. |
| Common execution records and independent performance evaluation | [`ExperimentRun` v1](../../src/hls/experiment_contract.py) and [HLS-PEF](../architecture/HLS_PERFORMANCE_EVALUATION_FRAMEWORK.md) have been reused in other validated scenario integrations. Existing adapters are route-specific; compatibility of `IntegratedRunResult` with the chosen adapter must be checked before relying on it. |

Related bounded evidence is summarized in [HLS Current State](../HLS_CURRENT_STATE.md), particularly its S4 and S7 entries. The audited S4 `T=3, x,y,y` integration did not select teaching; it is not a positive transfer result. Campaign 2 found context-dependent transfer/MIS interactions but did not identify their causal mediation. These findings motivate the question and constrain claims; they do not prove H3.

## 4. Dependencies and cost drivers

Before an executable protocol can be frozen, CE-03 must specify or verify:

1. The exact existing scenario/configuration and its provenance; do not invent
   a new scenario or tune it to produce a negative collective outcome.
2. The receiver-level performance outcome and collective outcome, with units,
   aggregation, and the task mix under which complementarity is defined.
3. Whether teaching consumes the same resources as production, the transfer
   opportunity/efficacy assumptions, and the applicable existing transition.
4. The fixed organization, readaptation rule/information boundary, and the
   optimal reference's information and action set.
5. Matched transfer-off controls and a decomposition that distinguishes direct
   skill change, changed assignment, displaced production, and resource cost.
6. Horizon, uncertainty, seeds if stochastic, and an analysis unit that avoids
   treating repeated periods from one run as independent samples.

**Engineering reuse cost:** likely bounded if the existing integrated N×K
runner and exact solver cover the selected instance. No universal runner or
new framework is indicated. A small adapter/result serializer may be required;
first verify whether current records can be mapped to `ExperimentRun` without
losing transfer, assignment, and resource semantics.

**Scientific and computational cost:** no defensible run count or wall-clock
estimate exists until the scenario, action set, horizon, and uncertainty are
fixed. Exact Bellman/enumeration cost can grow with the number of reachable
competence states and feasible joint actions; continuous-valued states may
prevent state reuse. Simulation cost depends on paired conditions × instances
× seeds × periods. Effort/resource units in the model are not compute cost.
The six-week exploration is moderate-compute by PI direction, but this note
does not allocate a numeric compute budget.

## 5. Gates and responsibilities

- **Initial review after two weeks:** confirm a problem-grounded, falsifiable
  H3 contrast; evidence and prior-work map; matched controls; feasible reuse;
  and whether the reference is exact and appropriately privileged. If these
  are unresolved, revise or stop before execution.
- **At six weeks:** continue only if evidence supports a discriminating,
  reproducible study and CE-03 can distinguish recipient benefit from
  collective effect without changing historical physics or using an unfair
  comparator. PI-07 makes evidence the continuation basis.
- CE directs scientific framing and interpretation; Codex documents and
  verifies repository components and any later authorized implementation.
  This activation does not authorize an experimental campaign, code changes
  to scientific mechanisms, or a new algorithm.

## 6. Source map

- [HLS scientific philosophy](../HLS_PHILOSOPHY.md) and
  [research doctrine](../../RESEARCH_DOCTRINE.md): governing problem-first
  orientation and evidence principles.
- [HLS Current State](../HLS_CURRENT_STATE.md): canonical current status and
  bounded S4/S7 evidence.
- [HLS Campaign 2 findings](../experiments/HLS_CAMPAIGN2_FINDINGS.md): prior
  transfer/MIS evidence and limitations.
- [HLS Laboratory v1](../experiments/HLS_LAB_V1.md): integrated runner
  contracts and boundaries.
- [HLS S4 transfer audit and exact artifacts](../engineering/HLS_S4_SEMANTIC_INTEGRATION_AUDIT.md)
  and [`results/experiments/hls_s4_transfer_exact/`](../../results/experiments/hls_s4_transfer_exact/):
  finite-instance evidence; not a general result.
