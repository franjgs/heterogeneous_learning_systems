# HLS Campaign 1 — Consolidated Findings

**Scope:** documentation synthesis of the published Campaign 1 pilot, mechanism diagnostics, counterfactual teaching-value analysis, and behavioral-plausibility validation. No experiments were run for this synthesis. Linked machine-readable artifacts are the numerical source of truth.

## Evidence and traceability

| Evidence | Source | Results / provenance |
| --- | --- | --- |
| Pilot | [`run.py`](../../experiments/synthetic/hls_campaign1/run.py), [`protocol.json`](../../results/experiments/hls_campaign1_pilot/protocol.json) | [Manifest and outputs](../../results/experiments/hls_campaign1_pilot/manifest.json); source base `a179041a1617e250e3fe83065db7dbc8402b0d62`; integration commit [`f4694c9`](https://github.com/franjgs/heterogeneous_learning_systems/commit/f4694c9). |
| Mechanism diagnostics | [`analyze_mechanisms.py`](../../experiments/synthetic/hls_campaign1/analyze_mechanisms.py) | [Analysis manifest and CSVs](../../results/diagnostics/hls_campaign1_mechanism_diagnostics/analysis_manifest.json); commit [`f27ffba`](https://github.com/franjgs/heterogeneous_learning_systems/commit/f27ffba); frozen pilot analysis plus 876 targeted deterministic replays for omitted direct teaching-gain fields. |
| Counterfactual teaching value | [`counterfactual_teaching.py`](../../experiments/synthetic/hls_campaign1/counterfactual_teaching.py) | [Manifest and CSVs](../../results/diagnostics/hls_campaign1_counterfactual_teaching_value/manifest.json); commit [`1f34079`](https://github.com/franjgs/heterogeneous_learning_systems/commit/1f34079); 32 prespecified states, 64 paired interventions. |
| Behavioral plausibility | [`behavioral_plausibility.py`](../../experiments/synthetic/hls_lab_v1/behavioral_plausibility.py), [`tests`](../../tests/test_hls_behavioral_plausibility.py) | [Manifest and CSVs](../../results/diagnostics/hls_behavioral_plausibility/manifest.json); commit [`fd67de6`](https://github.com/franjgs/heterogeneous_learning_systems/commit/fd67de6); deterministic fixtures, seed 2501. |

The pilot factorial had 16 demand × initial-deficit × teaching-efficacy × horizon configurations, MIS-v2 ON/OFF, four policy conditions, ten paired seeds per configuration, 1,280 policy runs and 20,480 episode records. Horizons were 8/24, resource budget 2.0. Policies: P0 production-only, P1 fixed teaching, P2 adaptive teaching, and scheduled teaching without feedback. Pairing used common seeds and exogenous conditions. The published manifests contain SHA-256 digests for source/input/output artifacts; reported output hashes were checked against them during consolidation. Source hashes identify code at execution time, not necessarily the current worktree. Three invalid pilot attempts (latent-label exposure, private-truth prior, budget/action-granularity failure) remain excluded and separately recorded.

## A. Pilot

| Policy contrast vs P0 | Mean paired ΔCES | SD across pairs | Positive / negative / tie | Paired Δ success rate |
| --- | ---: | ---: | ---: | ---: |
| P1 fixed teaching | −2.370 | 1.525 | 0 / 320 / 0 | −0.533 |
| P2 adaptive teaching | −0.184 | 0.223 | 37 / 241 / 42 | +0.010 |
| P2 scheduled, no feedback | −0.821 | 0.960 | 20 / 258 / 42 | −0.091 |

P0 exceeded P1 CES in 320/320 pairs. P0 exceeded P2 in 241, P2 exceeded P0 in 37, and 42 tied. Thus aggregate P2 CES was slightly lower while its aggregate functional-success difference was slightly positive: the measures are not interchangeable. In the predeclared high-deficit/high-efficacy/long-horizon/MIS-OFF cell, P2 exceeded P0 under stationary demand (ΔCES +0.313, SD 0.194; Δsuccess +0.483, SD 0.074) and changing demand (+0.380, SD 0.107; +0.537, SD 0.105), each n=10. The advantage was absent in this cell with MIS ON. P2 taught in 623/5,120 episodes (no teaching in 4,497); P1 taught 5,120 times and scheduled no-feedback 1,679 times.

These are descriptive summaries, not population estimates. Ten seeds per cell do not justify broad inferential claims. The choice score prioritizes functional success, deficit, margin, and effort—not CES. Resource costs are recorded separately. P2 versus scheduled control is not an information-only contrast because teaching exposure and state trajectories differ.

## B. Mechanism diagnostics

For P2−P0, MIS ON mean ΔCES was −0.241 (between-pair SD 0.181, n=160 configuration-seed pairs); MIS OFF was −0.126 (SD 0.246, n=160). The descriptive difference-in-differences ON−OFF was −0.115 (SD 0.196; 28 positive, 112 negative, 20 ties). This is an interaction of the MIS toggle with the policy package in this simulator/design, not an estimate of mechanism shares or a population causal effect.

Across P2/P0 trajectories, 278/320 runs incurred a negative cumulative CES difference after teaching. Thirty-nine later crossed back to nonnegative; 239 never crossed. Final counts: P2 ahead 37, behind 241, tied 42; all 42 tied runs had no P2 teaching. In high-deficit/high-efficacy/long-horizon/MIS-OFF, all 20 trajectories crossed and ended ahead (mean break-even period 17.3 stationary, 8.2 changing demand). With MIS ON, only 4/20 crossed after a teaching-associated negative path and 3/20 ended ahead. A single crossing is not robust amortization.

Each lesson used 0.5 participant-effort; relative to matched P0, it displaced 1.0 productive effort and left 0.5 budget unused because productive actions are discrete. Counts were P1 5,120, P2 623, scheduled control 1,679. The pilot CSV omitted direct teaching gain; 876 deterministic targeted replay blocks recovered 7,422 event gains and matched frozen actions, CES, resources and real-competence traces. Mean direct gain per event: P1 high/low efficacy 0.0352/0.0103; P2 MIS-OFF 0.1031/0.0131 and MIS-ON 0.1014/0.0128. These condition on each policy's selected events and state path; they are not intrinsic efficacy comparisons. Net skill change with LI ON can combine MIS and teaching.

## C. Counterfactual teaching value

Selection used all long-horizon pilot cells: demand stationary/changing × deficit low/high × efficacy 0.10/0.85 × MIS ON/OFF × period 2/16, first seed `2026101511`: 32 states, not outcome-selected. Relations `(2,1,1)` and `(0,1,0)` yielded 64 paired branches. At the first action, no-teach used P0's observable production-only action; teach used the best feasible production allocation for that specified relation under the same functional score. Both branches then used the same P2 continuation rule, independently evolving observations and states, over a frozen exogenous suffix with indexed common innovations.

The estimand is conditional remaining-horizon cumulative CES(teach−no-teach), not globally optimal teaching value. Immediate difference averaged −0.142 (SD 0.103); final ΔV_H −0.074 (SD 0.181; range −0.370 to +0.565), 19 positive/45 negative. Early (22 decisions remaining): +0.033 (SD 0.186; 19 positive/13 negative). Late (8 remaining): −0.181 (SD 0.093; all 32 negative). Early MIS-OFF mean +0.055 (11/16 positive), MIS-ON +0.011 (8/16); late MIS-OFF −0.115 and MIS-ON −0.247 (each all 16 negative).

P2 chose no teaching in 22/32 states and `(0,1,0)` in 10/32. Relative only to tested candidates: 17 correct no-teach choices, 5 missed positive candidate opportunities, 4 selected positive teaching cases, 6 selected harmful cases. These are not oracle regret. Value includes immediate allocation, direct skill change, later observation/MIS exposure and subsequent P2 choices. It depends on continuation policy; one seed per stratum provides no population uncertainty estimate.

## D. Behavioral plausibility

Tests and deterministic scenarios verify implementation behavior, not real-world validity.

| Check | Result | Status / boundary |
| --- | --- | --- |
| Production P1–P5 | Additive output `Y_k=Σ_i x_ik s_ik`; relevant skill helps; specialists can fit dominant requirements; multidimensional requirements can need collective coverage; infeasible tasks may fail; adding resources weakly expands best feasible output. | **VERIFIED** for this function/catalogue. Complementarity is coverage, not superadditivity. |
| MIS-v2 L1–L5 | Relevant experience updates corresponding skill; no unrelated transfer; bounds/saturation hold; `enabled=False` gives no MIS gain. | **VERIFIED** under MIS-v2. Eta=0 is unsupported; OFF flag is the zero-learning control. |
| Teaching T1–T7 | Targeting and relation-specific efficacy work; zero efficacy gives zero direct gain; gain is monotone in efficacy at fixed state; bounds/saturation and resource charge hold; direct teaching and MIS can be separately tested. | **VERIFIED**. Net period change can combine transitions. |
| Environment E1–E6 | Specialized/complementary requirement vectors, recurrence, novelty as unseen requirement structure, regime-dependent demand and policy-independent trajectories are tested. | **VERIFIED** for generator contract, not empirical demand realism. |
| S1 adequate | H=24, forced intervention ΔCES_H −0.4002; P2 independently declined to teach. | **CONDITIONAL** fixture. |
| S2 persistent deficit, effective early teaching | H=24, MIS OFF; immediate −0.9000, ΔCES_H +0.8825; break-even period 12. | **CONDITIONAL** positive fixture. |
| S3 short horizon | H=8; ΔCES_H −0.3575. | **CONDITIONAL**. |
| S4 weak efficacy | Efficacy 0.10, H=24; ΔCES_H −0.9000, direct gain 0.0150. | **CONDITIONAL**. |
| S5 MIS ON | H=24; ΔCES_H +2.4445; break-even period 10. | **CONDITIONAL**; no universal interaction claim. |
| S6 demand regime change | H=24; ΔCES_H −0.0475 versus S2 +0.8825. | **CONDITIONAL** fixture. |

Behavioral plausibility shows coherent responses to controlled model changes; it is not empirical validation against real teams or organizations.

## Critical model limitations

1. **Additive production:** multidimensional complementarity is requirement coverage, not superadditivity or organizational synergy.
2. **Discrete action catalogue:** budget 2.0, teaching 0.5 leaves 1.5, but at most 1.0 is productively assigned; 0.5 is stranded and 1.0 production effort is displaced versus no teaching. This is catalogue granularity, not a general resource law.
3. **Gross CES:** CES is gross functional reward. Resource use is separate; no net economic utility is defined.
4. **Different choice objective:** production decisions use functional success/deficit/margin/effort ordering, not direct CES maximization.
5. **MIS/teaching interaction:** neither universal substitution nor universal complementarity is established.
6. **Counterfactual continuation:** teaching value is conditional on the specified continuation rule.
7. **External validity:** plausibility checks are not empirical validation.
8. **Suite status:** the full repository suite retains 13 previously identified historical provenance/integrity failures. HLS Laboratory v1 remains **PARTIAL**; the behavioral-validation run did not rerun the full suite.

## Verified observation and open hypothesis

**VERIFIED:** teaching can incur immediate production loss and yield delayed cumulative benefit under some prespecified model conditions. Observed value varies with competence state, efficacy, remaining horizon, demand, individual learning, resource constraints, and later assignments. The design has not independently identified each factor's contribution.

**HYPOTHESIS — unverified:** “The interaction between directed teaching and learning-by-doing depends on whether teaching changes the learner's future productive opportunities.” Possible pathway: teaching → competence development → access to new productive assignments → experience-based learning → further development. Alternative: substitution if both develop the same skills without opening productive opportunities. Existing results do not distinguish these generally.

## Next scientific experiment (proposed, not executed)

Use a controlled 2×2 intervention: teaching ON/OFF × MIS-v2 learning-by-doing ON/OFF. Match initial states and exogenous demand; specify one common continuation policy and report its role separately from the intervention. Record direct teaching gains, subsequent MIS gains, productive-assignment changes, cumulative CES and resources separately. Keep CES gross and costs separate. Do not add policies, neural predictors or RL. This direction was not executed in this documentation intervention.

## Reproduction

Original commands (not rerun for this synthesis):

```bash
PYTHONPATH=src:. python -m experiments.synthetic.hls_campaign1.run
PYTHONPATH=.:src python experiments/synthetic/hls_campaign1/analyze_mechanisms.py
PYTHONPATH=src:. python -m experiments.synthetic.hls_campaign1.counterfactual_teaching
python experiments/synthetic/hls_lab_v1/behavioral_plausibility.py
```

Behavioral validation recorded 54 focused integrated/environment/CE-23–25 tests and 56 DISCOVER-v0, MIS-v2, dynamic-lab, and Campaign 1 regressions passing. Full-suite status remains the documented 13 provenance/integrity failures.
