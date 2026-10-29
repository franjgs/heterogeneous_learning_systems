# Research record

This is the evidence-oriented account of what HLS investigated and learned, not an activity log. The catalog in registry/catalog.json is the machine-readable index; this document records scope, conclusions and limitations. Historical source citations refer to feature/hls-laboratory-v1 at commit c81def3b5280b0f59d6dcbfd3e25df8805f5013c unless a different source is stated. The current branch has directly executable evidence only where an active implementation, fixture and test are identified. A documented historical summary is not equivalent to replayable raw data.

Execution status describes work performed; scientific outcome describes what the evidence supports. Closed does not mean positive, validated or universal. Unknown dates remain unknown; commit time is not substituted for experiment time. Each entry gives its stable catalog ID, question, model/scenario, evidence, conclusion, status, limits and source path. Hypotheses absent from the primary record are not reconstructed as preregistered hypotheses.

## Programme-level account

HLS has investigated finite static allocation, action-dependent competence change, assignment and continuation value, information-sensitive decisions, sequential computation, joint error dependence, transfer, contextual selection, dynamic deadline allocation and matched-marginal competence structures. Across these settings, the most defensible recurring lesson is conditional: individual competence distributions do not determine realized collective performance without the task distribution, feasible organization, policy information, dynamics and evaluation contract.

Two exact finite model families are runnable in this branch: static task allocation and two-period competence development. Their code and tests support those specific constructions. Most empirical-looking campaign numbers below are results from synthetic simulations in the historical source branch. Their reports survive as documentary summaries, while raw traces and campaign runners do not; do not call them independently reproduced in this branch.

The record includes favorable finite/synthetic contrasts and important non-results: a registered persistence interaction campaign was not executed; the initial transfer result is inconclusive; a corrected small model-selection comparison is inconclusive; the first CE-07 attempt had a nonstationary-demand protocol deviation and is excluded; and the surviving matched-marginal CE-07 result is limited to one synthetic scenario and policy. These outcomes constrain the claims; none establishes general HLS superiority.

## What can be reused

- Exact finite static and dynamic constructions can be run with the active Python package and are useful for checking derivations or creating small counterexamples.
- The normalized scenario/organization/model/evaluation distinctions and catalog validator can support a new study semantic and provenance checks.
- Historical queue, bandit, routing, learning, transfer and sequential-computation results are design precedents only in this branch: their scientific meanings and reported findings are summarized, but their old implementations and raw outputs are not reusable executables here.
- A reader may use a historical report as documentary evidence, but any claim needing raw reanalysis requires recovery from the archive or a new, separately specified study.

## Open research questions suggested by the record

1. Under what formal conditions does a compact representation of individual capabilities preserve the decision value of a richer representation across a declared class of organizational constraints?
2. Which mechanisms explain when equal marginal competence distributions but different joint structures change collective performance, beyond the single synthetic queue/P1 contrast?
3. How should experience-driven competence change, observation cost and organizational reassignment be jointly evaluated when the states and feedback are endogenous?

These are open questions, not approved priorities or claims of originality.


## Retained studies

### Competence heterogeneity in SOC alert operations: proposed testbed

- **Stable ID:** `study.soc_competence_heterogeneity_testbed`; **application scenario:** `scenario.soc_alert_operations`.
- **Proposal date:** 2026-10-27. No start or completion date; no experiment has been implemented or run.
- **Question:** how should analyst competence heterogeneity be characterized, and under what evidenced workload, organizational and resource conditions does its utilization or development affect individual and collective performance across initial triage (L1) and deeper analysis (L2)?
- **Scope:** L1 represents the supplied “escalate or not” and “report or not” decisions; L2 represents deeper investigation of alerts requiring it. The decision sequence, referral rules and outcomes are unspecified. The scenario concerns human cyberanalysts serving multiple clients, with possible new clients, technologies and threats; these are testbed scope, not facts about a verified client.
- **First research dimension:** competence heterogeneity—characterization, utilization, development, adaptation, benefits, costs and limitations. No beneficial direction is presumed. Experience is not a competence measure; learning is not assumed to improve performance.
- **Candidate mechanisms:** task allocation, learning by doing, deliberate development, knowledge transfer, specialization and adaptation. These are possible future constructs, not observed SOC procedures or validated effects.
- **Evidence and reusable context:** exact finite allocation and development results, plus synthetic queue results on mean-preserving competence profiles and joint competence structure, may inform question formation. They are not SOC evidence and do not establish real-world benefits. Relevant SOC studies describe setting-specific Tier-1 investigation variation and alert-data interpretation [@kersten2025tier1; @yang2024socalerts]. General mechanisms have prior literature [@argote2011organizational; @baccara2023task; @nembhard2015selection].
- **Status/outcome:** PROPOSED / NOT_EVALUATED.
- **Limitations and prerequisites:** no client operational facts, dataset, SOCTRA schema, individual competence observations, validated measures, workload/process rates, deadlines, outcome adjudication, cost model, or learning/transfer transition has been verified. These must be established or explicitly modeled before protocol design. No AIAI 2026 result in the accessible repository demonstrates organizational learning benefits.
- **Evidence maturity:** proposed testbed only; no empirical validation or reproducible experiment.

### Static allocation under task-dependent competence

- **Stable ID:** `study.static_allocation`; **historical aliases:** G1, G1.1, G1.2.
- **Dates:** start/close not established by the retained scientific record.
- **Question:** when can task-wise access to fixed differing competence improve attainable collective effectiveness under demand and resource constraints?
- **Model/scenario:** exact finite two-agent/two-task model. The first formulation compares a common agent across task types with independent task-wise routing. The resource extension represents outcomes as effectiveness-resource pairs and admits time-sharing by convex hull.
- **Evidence:** exact formula for crossed specialization, `ΔY(p)=min(p A1,(1-p) A2)`; symmetric case maximum 0.4 at p=.5, asymmetric control maximum .24 at p=.4. The resource-extension controls include zero gain under homogeneous and taskwise-dominance cases; a finite budget case has positive gain only for B in (.25,.65), maximum .0625 at B=.40; a separate case has geometric set expansion but zero efficient gain.
- **Conclusion:** heterogeneity alone does not entail organizational value. Demand, constraints, and feasible organization jointly determine realized value.
- **Status/outcome:** CLOSED / POSITIVE finite constructions plus null controls. This is standard assignment/frontier mathematics in HLS terminology, not a novelty claim.
- **Limitations:** two agents, two task types, constructed matrices and objectives; no learning or empirical application. Convexification assumes admissible linear time-sharing.
- **Evidence:** exact model code `src/hls/static_assignment.py`, tests, and runner `studies/static_allocation.py`. Historical derivation was in source-branch `docs/theory/HLS_G1_STATIC_EXPERIMENTAL_GROUND_TRUTH.md` and `experiments/synthetic/g1/README.md`; numerical artifact directories are not carried over. The small runner independently evaluates a retained exact control.

### Sequential deterministic allocation under finite capacity

- **Stable ID:** `study.sequential_capacity_constrained_assignment`; **project alias:** HLS-01.
- **Question:** how do a predeclared type-to-agent mapping and a greedy online rule compare with an exact offline allocation on a finite ordered task sequence when each assignment consumes one unit of fixed agent capacity?
- **Model/scenario:** a non-empty finite sequence of task-type indices, fixed deterministic effectiveness matrix `e[i,k]` in `[0,1]`, and non-negative integer initial capacities. Each task is assigned once or rejected. Effectiveness contributes directly to the objective; it is not a latent competence, service time, or observed success. No queues, deadlines, learning, cooperation, replenishment, or uncertainty are modeled.
- **Policies:** fixed mapping without reassignment; greedy online choice of the feasible agent with highest current-task effectiveness (ties by ascending agent index); exact offline enumeration with access to the complete sequence (agent indices ascending, rejection last for ties). Offline sums are compared exactly as rational values of the supplied numeric entries (for floats, their exact binary representations); displayed aggregates are floating-point summaries. The offline rule is a hindsight oracle for small instances, not an online policy.
- **Controls and results:** with non-binding capacities, the runner recovers the existing `StaticAllocationModel` values for crossed specialization and two null controls (homogeneous effectiveness and taskwise dominance); these are compatibility checks, not new discoveries. In a separate two-task constructed case, greedy obtains total effectiveness 1.0 while offline enumeration obtains 1.7; this is an exact counterexample to greedy optimality in that instance, not an estimate of typical policy performance. A fixed mapping also demonstrates policy-induced rejection while another agent still has capacity, distinct from global saturation. The mean objective divides by all tasks received, including rejected tasks.
- **Evidence status:** implementation and deterministic test/runner controls are present in `src/hls/sequential_allocation.py`, `tests/test_sequential_allocation.py`, and `studies/sequential_task_allocation.py`. The exhaustive small-instance test uses an independently written enumeration. No sampled or empirical evidence is produced.
- **Conclusion and limits:** the benchmark makes information access and finite capacity explicit and provides a reproducible comparison scaffold. It does not establish general policy rankings, a theoretical novelty claim, or an application result. Offline enumeration grows exponentially and is restricted to small instances. Task order and effectiveness are constructed inputs; future extensions involving demand, AI assistance, deadlines, or learning require separate definitions and validation. CE-04 is historical context only and is neither reproduced nor validated by this benchmark.
- **Open work:** extend only after review, with any sequential-demand assumptions, information boundaries, policy comparisons, and evaluation estimands specified separately.

### Temporal workload effects in heterogeneous task allocation

- **Stable ID:** `study.temporal_task_allocation_policy_comparison`; **project alias:** HLS-02.
- **Question:** in a finite temporal arrival stream with one recoverable server and an FCFS queue per agent, how does routing by fixed effectiveness and observable workload trade collective effectiveness against waiting and response time?
- **Model:** arrivals `(t_n,k_n)` in `[0,H)`, fixed `e[i,k]`, and positive deterministic class duration `s_k`, shared across agents. Each arrival joins one agent's FCFS queue; one task is served at a time; every task completes, including after the arrival horizon. There is no rejection, deadline, stochastic success, competence update, training, cooperation, or AI effect. Service units are synthetic and do not represent analyst time measured in SOCTRA.
- **Policies:** P0 maps each class to an agent before evaluation; P1 selects maximum `e[i,k]`, ties by ascending index; P2 selects maximum `e[i,k]/(W_i+s_k)`, where `W_i=max(0, queue_tail_i-t_n)` is current pending service work. Both dynamic policies are online and use no future arrivals. P2 is a heuristic, not an optimum.
- **Evaluation contract:** for `M` received tasks, total effectiveness is `E=Σ_n e[i_n,k_n]`; mean effectiveness is `E/M`, with all received tasks in the denominator. For each task, waiting is `start_n-t_n`, response is `completion_n-t_n`; means divide by `M`. P95 is the nearest-rank empirical quantile at rank `ceil(.95M)`. At the arrival horizon `H`, pending task count is the integer number of assigned tasks with completion time `>H`; a task completing exactly at `H` is complete. Pending work is the remaining service time at `H`: residual time of the task then in service plus full service times of queued tasks. It is measured in service-time units and may be fractional. Both are measured at `H`; simulation then drains queues so all tasks have final completion times for response and makespan. Per-agent utilization is service time overlapping `[0,H)` divided by `H`; individual effectiveness contribution is reported as per-agent sum and mean per assigned task, not as measured competence. Makespan is `max(completion_n)-min(t_n)`. Quality (effectiveness), congestion (wait/response/backlog), resource use (utilization) and elapsed span are kept separate; no scalar utility combines them.
- **Exact property:** because all tasks eventually complete, all agents are eligible and `e[i,k]` is fixed and independent of workload, P1 maximizes total effectiveness task by task: `E_P1=Σ_n max_i e[i,k_n]`. This is pointwise separability, not an empirical discovery. It does not imply best response time. It is stated and scoped in `docs/THEORY.md`.
- **Six deterministic controls:** all values below are generated by `studies/temporal_task_allocation.py`; time units, service durations and effectiveness profiles are constructed controls, not SOCTRA measurements. P0 and P1 produce identical assignments in these fixtures because each predeclared mapping was deliberately chosen to match P1's taskwise argmax (ties to agent 0); that is not a general equivalence.

| Scenario | Mean effectiveness P1→P2 | Mean response P1→P2 | P95 response P1→P2 | Pending tasks P1→P2 | Pending work (time) P1→P2 | Utilization P1→P2 by agent |
|---|---:|---:|---:|---:|---:|---|
| S1 separated arrivals | 1.000→1.000 | 1.000→1.000 | 1.000→1.000 | 0→0 | 0→0 | (0.25,0.25)→(0.25,0.25) |
| S2 balanced bursts | 1.000→1.000 | 1.500→1.500 | 2.000→2.000 | 2→2 | 2→2 | (1,1)→(1,1) |
| S3 concentrated class burst | 1.000→0.867 | 6.500→4.833 | 12→10 | 11→10 | 11→10 | (1,0)→(1,1) |
| S4 crossed specialization, block demand | 1.000→0.933 | 3.833→3.583 | 8→7 | 10→10 | 10→10 | (1,1)→(1,1) |
| S5 homogeneous effectiveness | 0.550→0.550 | 3.800→1.900 | 6.6→2.8 | 6→5 | 6→4.2 | (1,0)→(1,0.9) |
| S6 one agent dominates | 0.850→0.700 | 4.600→2.620 | 8.2→5.2 | 8→7 | 8→6.4 | (1,0)→(1,0.8) |

In S3, S4 and S6, P2 reduces mean response by 25.64%, 6.52% and 43.04% relative to P1 while reducing mean effectiveness by 13.33%, 6.67% and 17.65%. In S5 it halves mean response with no effectiveness change. In S1 and S2 it changes neither metric. These are exact outputs for six small constructed sequences, not statistical evidence, SOC performance estimates or a general ranking.
- **HLS-01 relation:** S1 recovers the crossed-specialization static allocation value under separated service; the temporal and static metrics are compatible there because no task waits. HLS-01's finite non-recovering capacity case is not a direct temporal control. Its implementation remains intact.
- **SOCTRA boundary:** existing aggregate audit supports historical alert-volume/time/project descriptions only. Alert records are not validated human work episodes; no verified service duration, staffing availability or individual competence matrix exists. The 91 handler labels and stored sample weights are not converted into people, competence or `e[i,k]`. No real dataset is integrated here.
- **Evidence/status:** model, runner and tests are locally reproducible; six deterministic controls were evaluated on 2026-10-29. Study remains active, with no confirmatory population claim. No sampling inference or uncertainty interval is applicable to these fixed fixtures.
- **Limitations/open work:** one server, unlimited queues, one duration per class shared by agents, no deadlines and no rejection. The load score's response/effectiveness trade-off depends on this formula and fixtures. SOCTRA-based arrival replay requires a defensible alert-to-human-task mapping; service/availability calibration requires operational evidence. Any such extension must keep the model assumptions and data permissions explicit.

#### Deterministic sensitivity grid

The same temporal model and unchanged P0/P1/P2 rules were evaluated on a deterministic paired grid of 96 cells: four effectiveness profiles × four arrival traces × `N∈{2,4}` × `H∈{24,48,96}`. Every cell contains 48 tasks, unit service times, and identical inputs across policies. All values are constructed controls; none are estimates from SOCTRA.

- **Effectiveness profiles:** H0 gives every agent `(0.6,0.6)`; H1 uses `(0.8,0.4)` and `(0.4,0.8)`; H2 uses `(1.0,0.2)` and `(0.2,1.0)`. For N=4, H1/H2 repeat the two rows in alternating order, leaving one agent of each profile at indices 0/1 and 2/3; this avoids making the fixed `(0,1)` roster systematically mismatch one profile group. H3 is a separate dominance control: one agent has `(0.9,0.8)` and the others `(0.4,0.2)`; at N=4 only one agent is dominant. H3 does not preserve H0–H2 marginal means (means are `(0.65,0.5)` for N=2 and `(0.525,0.35)` for N=4), so it is not a pure heterogeneity contrast. Matrix entries are deterministic objective contributions, not success probabilities or measured competencies.
- **Arrival traces:** D0 spreads task arrivals evenly and alternates classes; D1 puts balanced class arrivals into two bursts; D2 uses the same burst times but all 48 tasks are class 0; D3 spreads arrivals evenly and switches from class 0 to class 1 halfway through. All traces contain the same 48 tasks and total service demand (48 service-time units); class mix differs only where specified.
- **Offered load:** `ρ = Σ_n s[k_n] / (N H)`, total offered service work divided by nominal server-work over `[0,H)`. This gives ρ from 0.125 to 1.0; descriptive bands are low (≤0.25), intermediate (>0.25 to 0.5), and high (>0.5). A separate peak-window offered ratio is the largest work arriving in any `H/12` interval divided by `N(H/12)`. It flags temporal overload (`>1`) in 40/96 cells. These are offered-load descriptors, not realized utilization; measured utilization remains each agent's busy time over `[0,H)` divided by `H`.
- **Fixed P0 comparators:** each is frozen before evaluating a trace: (i) per-class responsibility, assigning each class to its highest-effectiveness agent (the homogeneous H0 tie uses agents 0 and 1); (ii) a fixed `(0,1)` duty roster; and (iii) one owner selected by the declared nominal class mix `(0.75,0.25)`. Identical mappings within a cell are computed once and labeled as aliases. These baselines add plausible fixed organizations to the six earlier controls; they do not use test-trace future information. The six original fixtures remain intact; their P0=P1 match was deliberately constructed and is not evidence that fixed and dynamic assignment generally coincide.

**Grid results (descriptive cell counts, not independent statistical replicates):**

| Contrast / grouping | Cells | Response faster / same / slower | Median relative response change | Effectiveness difference |
|---|---:|---:|---:|---:|
| P2−P1, all cells | 96 | 54 / 42 / 0 | −52.10% | range −0.3125 to 0 per task |
| P2−P1, H0 | 24 | 16 / 8 / 0 | −67.74% | 0 throughout |
| P2−P1, H1 | 24 | 11 / 13 / 0 | 0% | range −0.183 to 0 |
| P2−P1, H2 | 24 | 11 / 13 / 0 | 0% | range −0.267 to 0 |
| P2−P1, H3 | 24 | 16 / 8 / 0 | −59.45% | range −0.312 to 0 |
| P2−P1, D0 distributed | 24 | 4 / 20 / 0 | 0% | range −0.229 to 0 |
| P2−P1, D1 balanced bursts | 24 | 18 / 6 / 0 | −60.71% | range −0.279 to 0 |
| P2−P1, D2 class-concentrated bursts | 24 | 24 / 0 / 0 | −67.64% | range −0.312 to 0 |
| P2−P1, D3 mixture shift | 24 | 8 / 16 / 0 | 0% | range −0.267 to 0 |

Across P2−P1 cells, 25 showed faster response without an effectiveness loss; 29 were faster with lower effectiveness; 42 had no response change and none of those lost effectiveness. No cell made P2 slower than P1. That is a result of this finite parameter grid, not a guarantee about the rule. At offered-load `ρ=1` (N=2,H=24), P2 was faster in 12/16 cells; at lower global load it still often reduced response when arrivals were bursty, showing why aggregate `ρ` alone does not characterize peaks. With H=48 or 96, response differences were less frequent, consistent with greater capacity relative to the fixed 48-task trace. These are deterministic cross-scenario patterns, not statistical trends.

| Fixed baseline | P1−P0 effectiveness higher / equal | P1−P0 response range | P2−P0 response faster / same / slower | P2−P0 effectiveness lower / same / higher |
|---|---:|---:|---:|---:|
| Per-class responsibility | 0 / 96 | 0 to +11.96 | 49 / 47 / 0 | 29 / 67 / 0 |
| Fixed duty roster | 18 / 78 | 0 to +11.96 | 44 / 47 / 5 | 19 / 59 / 18 |
| Nominal-mix single owner | 36 / 60 | −11.96 to 0 | 64 / 32 / 0 | 27 / 33 / 36 |

P1's per-task argmax ensures it cannot have lower deterministic effectiveness than any fixed assignment under the same eligibility and completed-task assumptions; observed strict gains depend on matrix and mapping. Response ranges above are absolute time units (P1−P0); P2/P0 response counts are paired per cell. Relative to P0, P2 effectiveness could be lower, equal, or higher depending on the fixed comparator, because P2 is allowed to trade the P1 taskwise maximum for workload balance. P2 was slower than the fixed duty roster in 5/96 cells, a different comparison from P2−P1. No scalar score combines quality and time.

The runner reports all paired contrasts per cell, including P1−P0 and P2−P0 for each frozen P0 mapping, and P2−P1 once per cell. It also prints exact metric rows, pending task count separately from pending service-time work, utilization by agent and makespan. Reproduce the grid with `PYTHONPATH=src python studies/temporal_task_allocation.py --sensitivity`; the default command continues to run only the six original controls. No sampling inference is applied to the constructed grid. The result does not establish a general policy ranking, SOC-level service values, or an effect of AI.

### Dynamic competence-state change and future value

- **Stable ID:** `study.dynamic_competence_development`; **historical aliases:** G2, two-period control cases.
- **Dates:** source document labeled 2026-09-30 for the consolidated testbed; no separate execution date asserted.
- **Question:** does action-dependent competence change alter the efficient collective frontier, future value, and the current decision?
- **Model/scenario:** deterministic two-agent, two-task, two-period learning-by-doing construction with terminal task-dependent allocation.
- **Evidence:** the frontier-null control changes state but leaves frontier {(0.8,0.8)} and future value unchanged. In the value-reversal case, `ΔR=-.1`, `Δdev=.2p`, `ΔJ=-.1+.2p`; at p=.75, the total difference is +.05 despite the immediate disadvantage.
- **Conclusion:** state change does not imply collective capability change; capability/value changes depend on future demand and can change a choice in this constructed case.
- **Status/outcome:** CLOSED / exact finite positive and null controls.
- **Limitations:** deterministic, finite, linear transition and two periods. No forgetting, noise, saturation beyond the stated cap, cross-agent transfer, or empirical calibration. It is not a general theory of training.
- **Evidence:** exact model code `src/hls/dynamic_development.py`, tests, and runner `studies/competence_development.py`. Source derivation: source-branch `docs/theory/HLS_DYNAMIC_THEORY.md` and `docs/theory/HLS_G2_DYNAMIC_GROUND_TRUTH.md`.

### Assignment sensitivity and future opportunity

- **Stable ID:** `study.assignment_opportunity_value`; **historical aliases:** G3, G3-H.
- **Dates:** not verified.
- **Question:** when can an assignment affect the value of future competence development, and when does a local ranking reversal imply a root-level benefit?
- **Model/scenario:** finite organizational assignment and future-opportunity constructions.
- **Evidence:** the original C1 claim was falsified; the refined C2 account reduces to look-ahead/dynamic programming under its stated assumptions. A local action inversion alone does not establish a root-level value gap.
- **Conclusion:** optimal-path reachability and the full policy comparison matter; local opportunity is insufficient.
- **Status/outcome:** CLOSED / negative correction and conditional finite analysis.
- **Limitations:** no general planner, training policy, empirical validation, prevalence, or transfer across models established.
- **Evidence:** source-branch `docs/experimental_foundations/HLS_G3_ORGANIZATIONAL_VALUE_GROUND_TRUTH.md`; no active implementation retained because the historical implementation is not needed by the retained results.

### Joint versus separated operational/development decisions

- **Stable ID:** `study.joint_separated_policy_boundary`; **historical alias:** RQ0.
- **Dates:** research remains pending; no completion date.
- **Question:** can dynamic allocation and competence development improve long-term performance relative to separately managed architectures?
- **Model/scenario:** finite common-world decision processes with common state, action, reward, opportunity, resource and information semantics; a named finite redistribution family supplies constructive cases.
- **Evidence:** policy inclusion gives `Π_SEP ⊆ Π_HLS` and hence `J_SEP,max ≤ J_HLS`. In a finite attained setting, equality holds iff an HLS-optimal policy is SEP-admissible. A local Bellman opportunity identity is conditional and does not itself imply a root-level gap. A constructive family exhibits a strict region only under its named assumptions.
- **Conclusion:** strict integration is conditional; inclusion is a standard class argument. General prevalence, robustness and empirical relevance are unknown.
- **Status/outcome:** PENDING / exact conditional results; no broad empirical result.
- **Limitations:** depends on exact policy classes, common information/physics, feasibility and finite attainment. A fully coordinated separated policy can reproduce an optimum.
- **Evidence:** source-branch `docs/theory/rq0_routing_integration_boundaries.md`; historical aliases belong to this specific question, not HLS identity. Its experiment directories and raw outputs are not retained here.

### Static constrained assignment comparison

- **Stable ID:** `study.finite_assignment_comparison`; **historical alias:** S1.
- **Dates:** not verified.
- **Question:** how do taskwise assignment options compare under the finite objective and constraints?
- **Evidence:** the audit ledger reports a constructed exact value of 2.6 versus 1.8 under the stated comparison.
- **Conclusion:** the result is specific to its finite objective and feasible actions; it is not a general policy advantage.
- **Status/outcome:** CLOSED / exact finite computation; detailed source proof was not independently rechecked on this branch.
- **Limitations:** constructed model, no empirical calibration; detailed runner and result artifacts were removed.
- **Evidence:** source-branch `docs/HLS_CURRENT_STATE.md`, finite-model specification and forensic ledger.

### Shared-budget temporal optimization cases

- **Stable ID:** `study.shared_budget_temporal_optimization`; **historical aliases:** S2a, S2b, OPV.
- **Dates:** not verified.
- **Question:** how do temporal action and shared-resource constraints change finite decision value?
- **Evidence:** exact reported cases are S2a: 8 versus greedy 7.2; S2b: Bellman 1 versus myopic .9 with sufficient budget 1.9. The opportunity-value source states conditional Bellman identities/propositions for finite additive/smooth assumptions.
- **Conclusion:** these model-specific cases expose limits of myopic rules; they do not establish a general algorithmic or empirical gain.
- **Status/outcome:** CLOSED / exact finite computations, with some source propositions not independently rechecked on this branch.
- **Limitations:** distinct constructed temporal models and assumptions; no empirical calibration. Only locally reverified proofs are promoted in `THEORY.md`.
- **Evidence:** source-branch `docs/theory/minimal_hls_model.md`, `docs/theory/operational_development_opportunity_value.md`, and the forensic ledger. Detailed runner and result trees removed.

### Fixed-competence persistence interaction

- **Stable ID:** `study.persistence_interaction_boundary`; **historical aliases:** Q1/Q1-R.
- **Dates:** not verified.
- **Question:** whether architecture × demand persistence × learning interaction is present under a registered temporal estimand.
- **Evidence:** planned 960-run Q1 was NO-GO/not executed. An analytical fixed-competence, stationary, equal-marginal/full-information fixture has zero expected persistence interaction; separate finite fixture reports Θ(1)=−.003.
- **Conclusion:** the fixture does not answer or rescue the unexecuted registered Q1 study.
- **Status/outcome:** CLOSED / negative design result plus exact fixture; planned campaign not executed.
- **Limitations:** not a general null; no campaign data.
- **Evidence:** source-branch `docs/theory/HLS_Q1R_ANALYTICAL_VERIFICATION.md` and preflight record.

### Prospective information and development anticipation

- **Stable ID:** `study.prospective_adaptation`; **historical aliases:** the first and second adaptation studies.
- **Dates:** exact study dates not verified in this compact source record.
- **Question:** when do prospective information and development anticipation alter decisions and realized near-term return in the frozen finite adaptation model?
- **Model/scenario:** finite problem-history worlds, belief/capability dynamics, policy arms and counterfactual branches. The second adaptation experiment used 5,120 closed-loop runs across its frozen factorial; the sample was a Q11-reference state bank, not the whole state space.
- **Evidence:** The first adaptation experiment reported 64 counterfactual branch differences with mean ΔV −.074 (19 positive, 45 negative), limited by small seed/state coverage and action granularity. In the second adaptation experiment, The two information-sensitive prospective policies had ΔG means were .1623/.1669. Q01 realized-return estimate was .00145 with interval [−.01939,.01931]. Strict coupled-action behavior occurred in 71/15,360 eligible states (.462%).
- **Conclusion:** information/development can alter selected decisions in the frozen state population; Q01 realized-return evidence is inconclusive; local coupling prevalence is low and not a root-policy value result.
- **Status/outcome:** CLOSED / mixed, negative and inconclusive registered findings. Attempt 1 had an execution-integrity failure; attempt 2 was separately reconstructed and validated. Do not treat it as an independent replay or as train-vs-no-train full policy value.
- **Limitations:** frozen model/state population, finite worlds, conditional estimands, no broad real-world validation; internal opportunity reconstructions are not independent causal evidence.
- **Evidence:** source-branch `docs/experiments/CAMPAIGN_1_RESULTS.md`, `CAMPAIGN_2_PREREGISTRATION.md`, `CAMPAIGN_2_RESULTS.md`; raw the opportunity-landscape output was deleted as regenerable before this rebuild. Retained summary is documentary, not byte-level replay evidence.

### Sequential deliberation and computation allocation

- **Stable ID:** `study.sequential_computation_selection`; **historical aliases:** a predictor-based computation-selection rule.
- **Dates:** confirmatory report is dated 2026-10-26.
- **Question:** does prospective selection of additional computation improve performance-cost outcomes in the frozen sequential problem-belief design?
- **Model/scenario:** sequential finite problem-belief geometries and domains, FAST/DEEP computations, terminal FAST decisions; paired histories with shared physical problems and observation innovations.
- **Evidence:** The nominal 50% prospective selector compared with the nominal 50% randomized rule had mean cumulative physical reward difference +.1167 per history (95% interval [.0310,.2013]) and compute-time difference −.1924 seconds/history (95% interval [−.3539,−.0228]). Realized deep-call rates were not exactly matched (46.43% vs 49.80% equal-domain). The selector exceeded FAST by +.9535 reward but used +2.5516 s; it trailed DEEP by −.3863 reward and used −3.0126 s. No demonstrated advantage generalized to the two held-out domains.
- **Conclusion:** a joint performance-cost contrast is supported for this frozen design; it does not isolate pure efficiency at exactly equal call count or establish an original general method.
- **Status/outcome:** CLOSED / confirmatory scoped trade-off plus failed generalization boundary.
- **Limitations:** one design and compute regime, unequal realized call rates, machine-sensitive timings, no broad prior-art claim.
- **Evidence:** source-branch `docs/experiments/CAMPAIGN_3_META_VOC_CONFIRMATORY_RESULTS.md` and `docs/paper/META_VOC_SCIENTIFIC_RECORD.md`; raw artifacts are not retained in this branch. The summary is not independently replayable here.

### Dependence in collective classification

- **Stable ID:** `study.joint_error_dependence`; **historical alias:** CE-02.
- **Dates:** decision/event 2026-10-24; execution date not independently stated.
- **Question:** can the same individual error marginals yield different collective majority risk?
- **Model/scenario:** exact three-classifier synthetic joint error distributions; no model inference.
- **Evidence:** individual error probability .20 in both laws; pair covariance .06 vs .16; majority error .30 vs .20.
- **Conclusion:** yes, for those exact joint laws; dependence structure can change majority risk at fixed marginals.
- **Status/outcome:** CLOSED / exact computation, research originality NO-GO.
- **Limitations:** synthetic probability control only; no real temporal degradation evidence and no general theorem about classifier systems.
- **Evidence:** source-branch `docs/research/HLS_CE_02_AI_AGING_PREFLIGHT.md`; original exact control code and report not retained in active tree.

### Transfer and collective assignment

- **Stable ID:** `study.transfer_collective_effect`; **historical alias:** CE-03.
- **Dates:** source registry records activity 2026-10-24 through 2026-10-26.
- **Question:** whether actual transfer can improve a recipient, harm a fixed organization, and permit recovery after reorganization.
- **Model/scenario:** three synthetic binary tasks, three classifier families, twenty paired seeds; V2 compared supervised updates, aligned/permuted distillation and fixed/readapted organization.
- **Evidence:** individual task-3 aligned distillation vs supervised update +.18 pp, 95% interval [−1.06,1.42]; aligned vs permuted distillation +.59 [−.43,1.61]; collective distillation vs initial model −.34 [−1.61,.93]; validation-selected reorganization vs fixed assignment +.58 [−.74,1.89], assignment changed in 3/20 seeds. The initial iteration's apparent pattern was later invalidated as support for the transfer-harm hypothesis because task-3 labels were already in the initial pooled training data.
- **Conclusion:** H3 was not supported; no transfer advantage or collective harm was established. Preserve the V1 leakage finding.
- **Status/outcome:** CLOSED / inconclusive with a methodological invalidation in V1.
- **Limitations:** synthetic tasks, small organization and sample; the second-iteration intervals include zero; no real transfer setting.
- **Evidence:** source-branch `docs/research/HLS_CE_03_H3_CAMPAIGN_RESULTS.md` and `HLS_CE_03_H3_V2_CAMPAIGN_RESULTS.md`; raw output not carried over.

### Dynamic queue allocation under mean-preserving competence profiles

- **Stable ID:** `study.deadline_constrained_collective_allocation`; **historical alias:** CE-04.
- **Dates:** campaign date 2026-10-26.
- **Question:** how do specified competence composition, allocation policy and scale affect success correct and within deadline in one synthetic queueing world?
- **Model/scenario:** horizon 400; 12/24/48 agents; four task families; three mean-preserving profiles; Poisson arrivals, lognormal service, FCFS queues, deadline +3; no learning/cooperation; policies load-only, true competence×deadline probability, estimated competence, contextual adaptation. 1,080 confirmatory replicas, 30 paired seeds per factorial block.
- **Primary results:** the highest-vs-homogeneous profile contrast under the information-complete policy: +11.19, +11.69, +11.55 percentage points at N=12,24,48 (each 30/30 positive; nominal paired bootstrap intervals [10.89,11.50], [11.47,11.91], [11.42,11.68]). the information-complete vs load-only policy contrast in the specialized profile: +11.25, +11.65, +11.54 pp. the estimated-vs-true competence policy contrast: −6.46, −7.42, −9.90 pp. the contextual-vs-estimated competence policy contrast: +.78, +1.41, +4.19 pp. Interaction contrast: +6.14, +6.28, +6.53 pp.
- **Conclusion:** results establish those differences within the implemented synthetic model. They do not establish optimality of P1, general heterogeneity superiority, causal mediation, or real SOC performance.
- **Status/outcome:** CLOSED / confirmatory synthetic evidence.
- **Limitations:** one queue/deadline model, specified three profiles and policies; no learning/cooperation; recovery metric excluded; the information-complete rule is not a global planner. The large task-level log and original runtime are not retained in this branch, so campaign replay is unavailable here.
- **Evidence:** source-branch `docs/research/CE-04/11_CONFIRMATORY_RESULTS.md`, configuration hash `c72bdca82906daa2118b415d3ba76d1fbfac87c47a1c3ee72fea7677e4b8a1b5`.

### Calibration and load filters in estimated competence allocation

- **Stable ID:** `study.competence_information_and_load`; **historical alias:** CE-04 causal diagnostic.
- **Dates:** reported 2026-10-26.
- **Question:** how do external Bernoulli calibration and a load filter affect estimated-competence P2 in the frozen synthetic setting?
- **Evidence:** calibration contrast +5.266 pp at N=12 (95% interval [4.531,6.073]) and +8.683 pp at N=48 ([8.282,9.084]); load-only effects and calibration×load interaction were within the stated ±2 pp TOST equivalence margin at both scales.
- **Conclusion:** calibration mattered in this controlled simulation; load-filter and interaction estimates were equivalent within the chosen margin under that configuration.
- **Status/outcome:** CLOSED / confirmatory synthetic evidence.
- **Limitations:** only H2 and N=12/48, model-specific calibration and availability; cannot be generalized to other estimation or load policies.
- **Evidence:** source-branch `docs/research/CE-04/15_CAUSAL_RESULTS.md`; raw data not retained here.

### Diagnostics of the queue-allocation result

- **Stable ID:** `study.composition_selection_diagnostics`; **historical alias:** CE-06.
- **Dates:** 2026-10-26.
- **Question:** what descriptive selection/load metrics accompanied the three-profile queue contrast at N=24 under P1?
- **Evidence:** reanalysis of the same 90 queue-study replicas, not an independent replication. Success was 77.39/82.86/89.09%; selected competence .7750/.8438/.9134; wait .0106/.2746/.3100; late tasks 5.9/89.6/117.6 per replica. Gini .1969/.1227/.1235. The selection opportunity use was corrected to about 91.7% in H1 and 92.3% in H2.
- **Conclusion:** descriptive associations coexist; congestion mediation is not causally identified.
- **Status/outcome:** CLOSED / exploratory reanalysis plus a separate three-seed technical pilot; the pilot is not confirmation.
- **Evidence:** source-branch `docs/research/CE-06/01_HETEROGENEITY_DIAGNOSTICS.md`.

### Joint competence structure at fixed marginal competence

- **Stable ID:** `study.joint_competence_structure`; **historical alias:** CE-07.
- **Dates:** campaign dated 2026-10-26.
- **Question:** do two joint competence matrices with equal per-function marginals and maxima differ under fixed P1 in a stationary queueing scenario?
- **Model/scenario:** N=12, K=4; A has three universally high and nine universally low agents; B has three specialists per function; each function's mean is 27/40=.675, maximum .9. Stationary equiprobable tasks, service/deadline/queue law as described in the report; 30 paired seeds, 60 valid runs.
- **Result:** A success-on-time 65.81%, B 87.33%; paired B−A +21.52 pp, SD 1.13 pp, bootstrap 95% interval [21.12,21.92], positive in 30/30 pairs; paired t(29)=103.93, p=7.41×10⁻³⁹. TOST ±2 pp did not establish equivalence. Descriptive means: selected competence .7100 vs .8917, Gini .1999 vs .0728, mean wait .4561 vs .2657, late tasks/replica 147.93 vs 53.27.
- **Conclusion:** these two structures differed under this model despite identical per-function marginal means and maxima. The result does not prove specialization universally superior or identify whether the secondary load/selection pathways mediate the difference.
- **Status/outcome:** CLOSED / confirmatory synthetic evidence.
- **Limitations:** one N, two structures, one stationary demand law and P1; no generalization to other organizations/policies, no causal mediation. The first 60-run attempt used nonstationary family demand and was excluded; the technical pilot shared that family-phase defect. The reported valid campaign did not receive an exact full replay. Its bulky traces are not retained in this branch.
- **Evidence:** source-branch `docs/research/CE-07/04_CONFIRMATORY_RESULTS.md`; config hash `b5ab97c31e937e590ded4c99e861345c60dfd18d850edb8788c283752f6c2907`.

## Additional retained findings and explicit non-results

The following families produced scoped evidence worth retaining as a compact record, but their implementations and raw outputs are not active or replayable in this branch. Their historic names are aliases only in the catalog. Each claim is limited to the source audit’s stated scope.

### Competence-change priority statistics

- **Stable ID:** `study.competence_priority_statistic`; **historical aliases:** M0/M0.1.
- **Question/motivation:** whether failure frequency multiplied by quality gap is sufficient to prioritize competence improvement.
- **Hypothesis:** no universal sufficiency is assumed; the exact checks examine threshold behavior, null cases, and ranking reversals.
- **Evidence:** exact identities and sweeps report scoped thresholds, nulls, and rank reversals. The statistic was not validated as a universal priority rule.
- **Status/outcome:** CLOSED / exact model-specific result.
- **Limitations:** no validated selector or general priority theorem; full numeric cases are not retained here.
- **Evidence:** source-branch theory and model records listed in the audit matrix.

### Bounded reproductions of published mechanisms

- **Stable ID:** `study.published_mechanism_reproductions`; **historical aliases:** B1/B2/B12.
- **Question/motivation:** whether selected published organization and learning mechanisms can be represented and checked in bounded source-mechanism reproductions.
- **Hypothesis:** these checks establish interface/behavioral correspondence only if each source mechanism is faithfully represented; no general HLS benefit was presumed.
- **Evidence:** bounded reproductions and executable interfaces were recorded. Similar names do not establish faithful reproduction, and no end-to-end HLS result was established.
- **Status/outcome:** CLOSED / technical validation only.
- **Limitations:** no general learning/organization result; implementations are not retained.
- **Evidence:** source-branch mechanism dossier and audit matrix.

### Portfolio learning, opportunity and interference pilots

- **Stable ID:** `study.portfolio_learning_interference`; **historical aliases:** PACS B2.1–B2.4/B3–B5.
- **Question/motivation:** how learning, opportunity value, portfolio structure and interference behave in bounded pilot tasks.
- **Hypothesis:** no general direction is assumed; the studies test compatibility and bounded mechanisms.
- **Evidence:** two counterfactual bridges failed compatibility; one portfolio case was inconclusive; an interference/replay case produced bounded evidence.
- **Status/outcome:** CLOSED / negative compatibility findings and inconclusive bounded evidence.
- **Limitations:** does not validate selective training as a general policy; task/data and frozen hashes are not carried over; mechanisms are not interchangeable.
- **Evidence:** source-branch PACS protocols, audit matrix and historical reports; raw tables are not copied.

### Contextual selection under changing rewards and selective feedback

- **Stable ID:** `study.contextual_capacity_selection`; **historical aliases:** S3a/S3b and S3b-E1.
- **Question/motivation:** how nonstationary rewards, selective observations, memory and assignment affect contextual selection.
- **Evidence:** in a recovered 240-run factorial, UCB1 had lower regret in four cells and sliding-window UCB had lower global MSE. A windowed method helped only in one shared-feedback, infrequent-change cell: regret 184.88 vs 259.47, difference −74.59, interval [−89.60,−59.58]. Closed-loop intervals included zero. In a separate full-information mapping, the declared oracle was reached without showing a need for online learning.
- **Status/outcome:** CLOSED / mixed, cell-specific exploratory results.
- **Limitations:** candidate algorithms differ in more than memory; observation is endogenous; not faithful reproductions of named standard UCB procedures; estimands cannot be combined. The raw experiment tree is not retained.
- **Evidence:** source branch reports and forensic matrix; data availability is historical-source-only.

### Dynamic model selection under quality and latency constraints

- **Stable ID:** `study.dynamic_model_selection`; **historical alias:** MMLU/DCS-LA.
- **Question/motivation:** whether contextual choice across fixed language-model candidates improves a quality-latency trade-off.
- **Evidence:** after correcting an initial latency inversion and a code-hash mismatch, a 160-query held-out comparison reported DCS 46.25/139.27 ms against fixed 45.0/141.61 ms, difference +1.25 in the reported quality measure with interval [−1.25,3.75]; the same model was selected on 149/160 queries. A retrospective oracle was not deployable.
- **Status/outcome:** CLOSED / inconclusive small held-out comparison.
- **Limitations:** small evaluation, timing and provenance incidence, no deployable oracle; not evidence for real SOC operation or general contextual selection.
- **Evidence:** source-branch corrected dynamic-capacity and contextual-selection reports; raw query records not retained.

### Budgeted language-model routing

- **Stable ID:** `study.budgeted_model_routing`; **historical alias:** budgeted LLM routing.
- **Question/motivation:** whether an outcome predictor and a latency-budget optimizer improve routing over declared baselines.
- **Evidence:** Brier score .2698 vs constant .2314 for one predictor, while logistic regression scored .2174 with log loss .624; the only clear optimizer gain reported was +2.16 pp in one cell.
- **Status/outcome:** CLOSED / negative and cell-limited.
- **Limitations:** predictor and optimizer effects are separate; no general ILP superiority.
- **Evidence:** source-branch consolidated report and pilot artifacts, not retained.

### Error dependence and classifier fusion

- **Stable ID:** `study.classifier_fusion_dependence`; **historical alias:** classifier-fusion check.
- **Question/motivation:** how a joint error law and coalition choice affect ensemble accuracy.
- **Evidence:** a synthetic exact-enumeration check reported full-coalition accuracy .826 at correlation parameter 0, .700 at 1, and .7945 at .25; a separate exact three-classifier law shows majority errors .30 vs .20 at identical individual error .20.
- **Status/outcome:** CLOSED / exploratory synthetic exact calculations.
- **Limitations:** constructed dependence mixtures; consistent with known ensemble dependence effects; no novelty or real model inference.
- **Evidence:** source-branch exact validation report and CE-02 record.

### Model-specific experiment-envelope validation

- **Stable ID:** `study.model_specific_execution_contracts`; **historical alias:** ExperimentRun/HLS-PEF.
- **Question/motivation:** whether model-specific executions can expose provenance-carrying results through selected common envelopes.
- **Hypothesis:** bounded contracts may standardize serialization/evaluation without implying mathematical equivalence.
- **Evidence:** bounded tests and vertical slices passed. They did not establish a universal runner, semantic conversion, or cross-model equivalence.
- **Status/outcome:** CLOSED / technical validation.
- **Limitations:** no general cross-model adapter or universal simulator; code removed from this branch.
- **Evidence:** source-branch common-contract engineering records.

### Production, learning and teaching integration

- **Stable ID:** `study.production_learning_integration`; **historical aliases:** N×K/Nembhard.
- **Question/motivation:** whether selected production, learning, teaching and environmental components can be integrated in a bounded model.
- **Hypothesis:** no general productivity/competence equivalence is assumed.
- **Evidence:** bounded N×K routes were validated; the Nembhard productivity law is distinct from competence/MIS. A reported 1,016-run local artifact was not published; only 29 tracked records were available, so the broader result is not verifiable. A later campaign was interrupted.
- **Status/outcome:** SUSPENDED / technical validation plus unpublished evidence.
- **Limitations:** no completed independently verifiable campaign; Nembhard productivity and competence semantics differ.
- **Evidence:** source-branch current-state and mechanism records; no runner retained.

### Empirical vehicle feasibility screen

- **Stable ID:** `study.empirical_vehicle_feasibility`; **historical aliases:** office/home, Sprint0.
- **Question/motivation:** whether candidate empirical data satisfy structural and competence-measurement requirements.
- **Evidence:** feasibility screens only; no empirical outcome validation.
- **Status/outcome:** CLOSED / STOP at vehicle gate.
- **Limitations:** no real-world performance claim.
- **Evidence:** source-branch feasibility gate documents.

### State and trajectory discrimination gates

- **Stable ID:** `study.state_discrimination_gates`; **historical alias:** Campaign 0.
- **Question/motivation:** whether generated trajectories and states provide sufficient discrimination/support for later policy comparisons.
- **Evidence:** finite diagnostics documented state/action divergence and support limits; these were gates, not confirmatory policy effects.
- **Status/outcome:** CLOSED / technical diagnostic.
- **Limitations:** no confirmatory policy-value estimate.
- **Evidence:** source-branch gate report and diagnostics.

### Counterfactual-engine equivalence gate

- **Stable ID:** `study.counterfactual_engine_equivalence`; **historical alias:** Campaign 4.
- **Question/motivation:** whether counterfactual labels and engine outputs support the proposed larger comparison.
- **Evidence:** the control labels were not equivalent, so the proposed 800-run campaign received NO-GO and no scientific outcome run was conducted.
- **Status/outcome:** SUSPENDED / technical negative.
- **Limitations:** no campaign result; the gate does not estimate policy effects.
- **Evidence:** source-branch engine verification record.

### Finite service and assignment solver checks

- **Stable ID:** `study.finite_service_assignment_solver_checks`; **historical aliases:** S4/S7.
- **Dates:** not verified.
- **Question:** how do service assumptions, assignment rules and tie handling affect exact finite solver comparisons?
- **Evidence:** historical reports contain finite solver values/frontiers and tie-rule sensitivity checks.
- **Conclusion:** tie rules and service semantics affect the reported planner gap; these checks use distinct formulations and are not pooled.
- **Status/outcome:** CLOSED / bounded exact and technical checks.
- **Limitations:** detailed values and implementations are not independently retained in this branch; no general policy conclusion follows.
- **Evidence:** source-branch theory specifications and the forensic theoretical-results ledger.

## Disposition of other source families

The rebuild does not preserve every historical family as an active component. Other legacy families are represented only in the catalog’s alias map when their relation is supported; uncertain mappings are explicitly unresolved. They were not promoted to reusable components where the retained record lacked an interpretable result, lacked protocol/evidence detail, or duplicated a scoped exact result above. This does not claim that every removed line lacked scientific value; it means this branch does not retain enough verified evidence to treat it as active reproducible knowledge.

A documented course-correction decision, not an experiment, is reflected in HLS's research stance: characterize conditions and limits before proposing universal claims. SOC and LLMs remain possible applications only; no real-world validation is represented by the retained studies.

## Reproduction boundary

The exact finite models and deterministic temporal runner under `studies/` run without external datasets or large artifacts. Historical campaign summaries above preserve evidence claims and limitations, not raw reproducibility. A researcher needing their original protocols, full reports, logs, or data must consult the cited source-branch commit; their absence from this rebuilt working tree must not be described as regenerated or replayed evidence.
