# HLS External Mechanism Contract — v0.1 (design only)

**Date:** 2026-10-17
**Decision status:** PROPOSED / DESIGN REVIEW — **NOT IMPLEMENTED; NO EXPERIMENT AUTHORIZED**
**Evidence:** reviewed on 2026-10-17 against the original local Nembhard–Bentefouet PDF (SHA-256 recorded in the mathematical extraction), the source-code paths listed in `HLS_NEMBHARD_FIDELITY_AND_CONTRACT_REVIEW_2026-10-17.md`, the earlier code-reuse audit at commit `57f4ebfe7c51e7762a6a1d0a2cef3e18011b5501`, and `docs/hls_ontology.md`. **Revision record:** this v0.1 design specification has been reviewed in place; its version and design-only status are unchanged. Corrections below document verified source/HLS distinctions; unresolved source ambiguities remain open. No mechanism or experiment is authorized.

## 1. Purpose and boundary

**Implementation status addendum (2026-10-17):** the design-only status above
records the decision at the time v0.1 was drafted. A subsequent CE
authorization approved a narrowly scoped HLS N×K adaptation of the direct
curve only. It is implemented and documented in
[`HLS_EXTERNAL_MECHANISM_INTEGRATION_01.md`](../../engineering/HLS_EXTERNAL_MECHANISM_INTEGRATION_01.md).
That authorization does not change v0.1's source-fidelity limits: the
adaptation's effort-to-exposure and beginning-of-period output conventions
are HLS decisions, not a full source-model reproduction. Indirect transfer,
grouping and source production timing remain excluded or unresolved.

Define the **smallest reversible seam** for independently testing an external *experience-to-productivity* law while preserving the existing N×K MIS-v2 path and its semantics. The first candidate is Nembhard & Bentefouet's **direct-experience curve only**. Do not implement peer transfer, workforce selection, grouping, serial production, a universal plugin framework, or a cross-paper comparison under this contract.

The contract must support three independent claims, never conflated: (A) source equation correctly evaluated; (B) source experiments reproduced; (C) an explicitly adapted HLS comparison performed. v0.1 aims only to specify (A) and the prerequisites for (C), not to assert (B).

## 2. Existing seams — preserve, do not generalize prematurely

| Existing component | Audited contract | v0.1 treatment |
|---|---|---|
| `src/hls/hls_lab_nk_geometry.py` | `OrganizationConfigNK`, `OrganizationStateNK`, `ProblemSpecNK`, `validate_productive_allocation_nk`, discrete N×K action catalogue | **Reuse only** identifiers, fixed exogenous tasks and feasible effort when semantics align. Existing state and normalized competence stay unchanged. |
| `src/hls/hls_lab_nk_production.py` | `productive_outputs_nk(C,e) = Σ_i e_ik C_ik`; `evaluate_problem_nk`; `ces_reward_nk`; `p0_rank_nk` | **Do not override.** Nembhard's productivity rate is not `C`; its source output is not CES. Any shared outcome bridge is separate and gated. |
| `src/hls/hls_lab_nk_learning.py` + `discover_develop_v2.py` | `mis_v2_transition_nk`; `c' = 1-(1-c)(1-eta)^e` | **Frozen comparator.** Never insert Nembhard state into `C`, or change MIS-v2. |
| `src/hls/hls_lab_nk_teaching.py` | Directed teacher/learner/skill action and resource charge | **Not Nembhard transfer.** Excluded from v0.1. |
| `src/hls/hls_lab_nk_policies.py` | `NKCoordinationPolicy.choose(view,memory,parameters)`, P0/P1/P2 | **Not assumed compatible** with Nembhard outcomes; P0's lexicographic ranking is not a source-policy reproduction. Fixed exogenous action traces preferred for law tests. |
| `src/hls/hls_lab_nk_environment.py` + `hls_lab_nk_execution.py` | Frozen demand, policy-specific trajectories, trace/serialization | **Reuse as test infrastructure** only if action timing, units and source law are preserved; no modification to legacy runner in v0.1. |

**Architectural rule:** first design a standalone, pure reference evaluator and a thin **proposed** bridge to the N×K harness. Do not introduce a generic `Mechanism` superclass before a second genuinely different external law demonstrates a stable common contract. The minimum interface is a *documented callable protocol*, not necessarily a new base class.

## 3. Formal source model and scoped simplification

Nembhard direct learning, printed Eq. (1):

\[
P_{ij}(D)=k_{ij}\frac{D+p_{ij}}{D+p_{ij}+r_{ij}},\qquad D\ge0.
\]

Here `P` is a **productivity/performance measure** (called a rate in Appendix A), `D` is cumulative direct work in the source's time/trial units, `k` is the asymptotic performance level, `p` prior experience and `r` the learning-scale parameter. All terms added in the ratio must share an exposure unit; the paper does not give a physical unit beyond time/trials for work. Source Eq. (3) uses `Σ x` for direct exposure while Appendix (A-4) uses `Σ L x`; **the convention is unresolved**. The scoped reference evaluator must take **direct exposure in explicitly declared units** and must not silently choose `L=1` as an interpretation of the whole source model.

Source admissibility printed near Eq. (1) is `y,k,p,x ≥ 0`, `p+r>0`; it does **not** separately state `r>0` there. In the simulated parameterization, `r` is generated by exponentiating a normal draw for `log r`, hence is positive. For a simple monotone saturating test family require **additional adapter-domain assumptions** `k≥0, p≥0, r>0, D≥0` (narrower than the equation's printed domain); record this narrowing rather than claiming it is the full source domain. Under these assumptions, `dP/dD = kr/(D+p+r)^2 ≥0`, `d²P/dD² = -2kr/(D+p+r)^3 ≤0`, and `lim_{D→∞}P=k`; strict inequalities require `k>0`. Solving `P=k/2` gives `D+p=r`, so the future exposure at half-asymptotic performance is `D=r-p` when nonnegative. Thus the prose description of `r` as the production needed to reach `k/2` is literally true for `p=0`, but with prior experience `p>0`, `r` is the **total effective exposure threshold** `D+p`, not generally the additional production required from the current state. This distinction must be retained in tests and interpretation.

**Explicit exclusions:** indirect experience `θT`, team-type transfer, worker selection/grouping, parallel/serial objective, empirical 45/9/3 workforce and original solver. A direct-curve implementation is a **source-equation implementation**, not reproduction of Nembhard (2015).

## 4. Proposed minimal data and evaluation contract

The following names are **design notation**, not existing code or mandated signatures:

| Object / operation | Inputs | Outputs | Invariants |
|---|---|---|---|
| `DirectExperienceState` | ordered `(worker_id, task_type_id)` keys; `D_ij ≥ 0` with exposure unit | immutable cumulative exposure snapshot | Task-specific; no cross-worker transfer; no negative exposure; stable identifier order. |
| `NembhardDirectParameters` | per-pair `k_ij, p_ij, r_ij` with declared units and domain | immutable parameter set | `k` rate; `p,r,D` same exposure units; no implicit normalization to `[0,1]`. |
| `direct_productivity(params,state)` | `(k,p,r,D)` for each eligible pair | `P_ij` with explicit rate unit | Pure and deterministic; no state mutation, no CES. |
| `advance_direct_experience(state,assignment,duration)` | old `D`, **source-compatible binary** `x_ijt`, `L` with time unit | new `D`, per-pair increment | `D' = D + Lx` **only for the Appendix-A-4 convention**; update order documented. No update to HLS `C`. |
| `reference_output(productivity,assignment,duration)` | productivity, assignment, duration | output with declared units | **Not yet fixed**: original Appendix A-2 uses cumulative `Σ_{k≤t}x_ijk P_ijk` rather than an obvious period `LxP`; source timing/output interpretation requires fidelity resolution before implementation. |
| `HLSComparisonBridge` (future) | frozen common task/action trajectory, native MIS state and separate direct-experience state, calibration record | paired **separate** native outputs and optionally justified common observables | No implicit equation `P=C`, no forced CES; equal resource meaning and baseline observables must be demonstrated first. |

**Critical timing gate:** distinguish productivity evaluated at `D_t` (pre-exposure) versus `D_{t+1}` (includes current assignment). Source Eq. (3)/(A-4) sums through `t`, while HLS MIS-v2 produces current output from pre-learning competence. This is a real semantic mismatch. Record both as source/adapter conventions; **do not choose one silently or present either as equivalent**. Native fidelity tests must resolve the paper's evaluation ordering or report the ambiguity and STOP the reproduction claim.

**Additional source-consistency gates confirmed from Appendix A:** equation (A-3) includes the current period in its sum and weights assignments by `P_pqk`, while (A-4) defines `P_ijt` using `T_ijt`. Under a literal simultaneous-period reading, current-period productivities can therefore depend on one another through same-type peers. The paper does not specify a causal within-period update order, a simultaneous fixed-point solution, or conditions establishing existence/uniqueness of such a solution. This is an **unresolved implicit-dependence ambiguity**, not evidence that the authors intended a particular sequential or lagged rule. In addition, Appendix A-2 defines `O_ijt` as a cumulative sum through `t` of `x_ijk P_ijk`, while prose calls it output at time `t`, A-1 calls `S_jt` period output, and A-4 explicitly includes duration `L` in exposure but A-2 does not. Read literally, summing those cumulative `S_jt` in the objective may count prior output repeatedly; the source does not reconcile this with a period-flow interpretation. Nor does it state how the dimensions of productivity rate, assignment indicator, period duration, output, and the transfer factor `θ` align. Do not repair these equations by inserting `L`, differencing cumulative output, lagging `T`, or solving an implicit system without clearly labelling that as a new HLS modeling decision.

## 5. Semantic map (ontology categories)

| Source | HLS object | Class | Condition / prohibition |
|---|---|---|---|
| Worker `i`, task class `j` | agent / task type | `RELATED` | HLS K-skill index is not automatically source machine type; define a task-class map. |
| Binary `x_ijt` | organization/use `a_t` | `RELATED` | Source worker exclusivity and exactly-one-per-task differ from fractional N×K effort. |
| Cumulative direct work `D_ij` | direct experience `E_dir` | `RELATED` | Equivalence only after unit, exposure and timing contract. |
| `P_ij` productivity rate | expected operational performance `Qbar` | `RELATED` | Do not identify with competence `S`, observed quality `Q`, operational value `Y` or CES. |
| `k,p,r` | mechanism parameters / prior experience | `RELATED` | `k` is asymptote of productivity, not normalized competence. |
| `θT` | indirect experience `E_ind` | `UNRESOLVED` in v0.1 | Out of scope; not HLS directed teaching. |
| Duration `L` | elapsed time / exposure | `UNRESOLVED` | Source main text and Appendix differ; no implicit effort-to-time conversion. |

No new ontological primitive is necessary for v0.1; the proposed state is a model-specific instantiation of the ontology's existing experience object.

## 6. Independence and non-regression requirements

1. No changes to existing `OrganizationStateNK` meaning, N×K competence bounds, MIS-v2 transition, teaching semantics, P0/P1/P2 decisions, action catalogue ordering or legacy 3×2 reference behavior.
2. Direct-experience state and source parameters live in a separate namespace; Nembhard productivity is not stored in HLS competence fields.
3. Source evaluator is deterministic, pure and independently testable without the HLS runner.
4. No transfer, teaching or policy-memory updates occur when testing the direct law.
5. Record exposure unit, rate unit, period length, update ordering, parameter-domain restrictions and all conversions in traces/fixtures.
6. Keep frozen problem paths and initial conditions equal across any *adapted* comparisons, but acknowledge action-dependent learning/observations diverge across policies.
7. Compare physical outputs only if the source-to-HLS output bridge is justified. Otherwise report each model's observables separately; never treat gross CES as throughput or net welfare.
8. No new historical result, originality or superiority claim follows from passing unit tests.

## 7. Proposed acceptance tests — specification, not execution

**A. Native direct-curve fidelity (necessary first):**

- A1: hand-calculated cases at `D=0`, `D=p`, large `D`, and nonzero `p`; check `P(0)=kp/(p+r)` for `r>0`.
- A2: monotonicity and diminishing increments for `k>0,r>0`, convergence toward `k`, and `0≤P<k` for finite nonnegative `D,p` with `r>0`.
- A3: `k=0`, `p=0`, `D=0`, invalid `p+r≤0`, negative exposure and unit mismatch; fail closed under explicitly declared adapter domain.
- A4: independent `i,j` state keys; changing exposure for `(i,j)` cannot affect `(i',j')` with no transfer.
- A5: distinguish unit-duration and general-`L` exposure fixtures; do not assert source Eq. (3) and Appendix (A-4) numerically coincide without a stated normalization.
- A6: explicitly record whether current-period exposure contributes to current-period productivity; source-consistent timing fixture must precede any paper reproduction claim.

**B. Bridge tests (only after contract approval):**

- B1: fixed action/exposure trace replay, identical exogenous tasks and recorded duration, deterministic separate model trajectories.
- B2: independently verified calibration of **initial observable productivity**, not equality of raw state/parameter vectors; check units and outputs.
- B3: no-learning and zero-exposure controls; transfer/teaching disabled; verify unchanged source and HLS baselines.
- B4: source worker exclusivity is checked if using source assignment; otherwise explicitly label HLS fractional effort an **adaptation**.
- B5: existing 3×2 decision/catalogue/hash regressions and focused N×K tests remain unchanged; do not edit expected artifacts to pass.
- B6: reject comparisons that scalarize rate, CES, monetary cost, latency and effort without an explicit justified transformation.

**C. Future extension gates (not part of v0.1):**

- C1: indirect transfer reproduces Appendix (A-3) including task-type indicator, exclusion of focal worker and productivity weighting; check circular/current-period dependencies.
- C2: selection/grouping/assignment implements source feasibility and tie rules, plus serial/parallel evaluation and original reference statistics.
- C3: any second external mechanism must demonstrate that a shared interface preserves its own state and output semantics; otherwise keep model-specific adapters.

## 8. Open questions and explicit STOP criteria

| Issue | Evidence / consequence | Required disposition |
|---|---|---|
| Eq. (3) vs (A-4) direct experience `L` | Source extraction documents mismatch | Pin explicit unit convention for native equation test; if paper reproduction needs unavailable `L`, label **not reproducible**. |
| Meaning of `r` with prior experience `p` | Eq. (1) gives `P=k/2` at total effective exposure `D+p=r` | Correct the interpretation: incremental exposure to half is `r-p` when nonnegative; never call `r` the remaining exposure for arbitrary `p`. |
| A-3/A-4 same-period transfer | A-3 includes `k=t` and productivity terms; A-4 depends on `T_ijt` | No causal order or implicit-system solution is supplied. Keep peer-transfer implementation out of scope pending source/PI decision. |
| Eq. (A-2) output and period timing | Source extraction reports cumulative `Σ xP` | Resolve output-vs-rate and evaluation order from original PDF; do not infer `output=L×P` as source fact. |
| Dimensional consistency of Appendix output/transfer | A-4 adds `Lx` and `θT`; A-3 defines `T` from `xP`; A-2 has `xP` without `L` | Units of `θ`, period output and cumulative objective are not fully reconciled. Explicitly report units/normalizations in any adapter; no silent conversion. |
| Source `θ` normal draws / truncation | Not specified in source extraction | Out of scope for direct-only v0.1; required for full source simulation. |
| Source feasible actions vs HLS effort catalogue | Binary worker/task vs discrete fractional N×K effort | Preserve separate domains or explicitly label adaptation; STOP any claimed faithful source policy reproduction using HLS catalogue unchanged. |
| Parameter fitting/calibration | Published fitted-worker raw tuples unavailable | No empirical-calibration or full numeric reproduction claim. |
| Cost/benefit of abstraction | Only one external direct curve presently approved for design | STOP generic plugin framework if it adds dependencies without a second demonstrated use case. |
| Historical novelty | G2/MIS/G3 already establish learning/opportunity/assignment phenomena | STOP scientific novelty claims based solely on a different curve or renewed present/future tradeoff. |

**Hard STOP:** any required bridge silently changes the meaning of competence, productivity, exposure, duration, task type, feasibility or output; any regression of frozen HLS behavior; any unsupported claim of original-paper reproduction; or any experiment without a controlled common observable and resource basis.

## 9. Decision and bounded next action

**Decision: GO for design review only; HOLD on implementation.** The direct-curve reference evaluator is the smallest independently verifiable candidate. Before authorizing code, Codex/PI must resolve (or explicitly scope out) the source timing/output ambiguities and approve the proposed state/unit contract. The first possible implementation authorization would cover only pure source-law evaluation, exposure bookkeeping and its unit tests **outside** the existing runner; no peer transfer, grouping, router, simulator integration or experimental campaign.

**Review checklist:** (i) ontology mapping accepted; (ii) original equation and units checked against PDF; (iii) time/output ambiguity disposition recorded; (iv) no new generic abstraction justified prematurely; (v) regression and STOP gates accepted; (vi) PI explicitly authorizes any subsequent code.
