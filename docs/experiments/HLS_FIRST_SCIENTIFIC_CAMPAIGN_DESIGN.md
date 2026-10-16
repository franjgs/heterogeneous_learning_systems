# HLS First Scientific Campaign — Design Proposal

**Recorded:** 2026-10-16 10:29 +02:00 (Europe/Madrid)

**Status:** design only; no campaign execution authorized or performed.

**Laboratory:** HLS Laboratory v1, status PARTIAL.

## 1. Decision and candidate questions

| Candidate | Relevance and theoretical basis | Testability now | Main confounds / novelty risk | Assessment |
| --- | --- | --- | --- | --- |
| **Q1. When does a heterogeneous competence distribution outperform a more homogeneous one?** | Central to HLS's “who does what?” question. G1 treats static competence/configuration; G2 and the minimal model connect changing opportunities to evolving competence. | High for a restricted three-agent/two-skill comparison: competence matrices, P0, C5 IID/Markov demand, shared budgets, MIS-v2 ON/OFF and full traces already exist. | High novelty risk: specialization, workforce composition and assignment have extensive prior treatment, and broad versions overlap G1/G2. A distinct contribution is not established. Skill distribution must be matched on aggregate capacity and learning rates. | **Recommend**, narrowly: test the architecture × demand-temporal-structure interaction at matched aggregate competence, conditional on P0 and the existing additive production kernel. |
| **Q2. When does assigning work to develop future competencies improve performance versus greedy assignment?** | Strong theoretical grounding in dynamic allocation and learning-by-doing; G2/G3-H and HLS's conditional Bellman analysis already address intertemporal assignment. | Partial. Current P0 is myopic functional ranking; no existing pair isolates a learning-oriented assignment rule under the same information and objective. | Requires a new policy/control or a constrained exact benchmark. High risk of repeating G3-H/RQ0 or conflating policy quality with the objective mismatch; P0 does not maximize CES. | Defer. It is scientifically important, but not cleanly testable as a new claim with current policies. |
| **Q3. When does directed teaching add value beyond learning-by-doing?** | Relevant to training/knowledge-transfer literature and HLS's “who learns from whom?” question. | Mechanism is controllable; Campaigns 1–2 already compare teaching × MIS-v2 with matched demand and P0 continuation. | Very high novelty and duplication risk; teaching policy packages, resource displacement and mediation remain hard to isolate. It is also only one HLS mechanism. | Do not select as the first campaign. Existing evidence makes another broad teaching factorial a poor first use of the laboratory. |

**Primary question:** Under what temporal demand structures does redistributing the same aggregate two-skill competence across a fixed three-agent team change cumulative collective performance, and does that architecture contrast change when the same MIS-v2 learning-by-doing mechanism is enabled?

This is a focused Q1, not a claim that HLS has established novelty. The second clause is a prespecified mechanism block: MIS is switched ON/OFF identically for both architectures, not treated as an architecture change.

## 2. Factor separation and hypotheses

| Dimension | Primary design setting |
| --- | --- |
| **Architecture treatment** | Homogeneous versus heterogeneity-tilted initial competence matrices below; same three agents, two skills and total capacity. |
| **Policy** | Existing `P0ProductionOnly` in every arm. No new policy and no teaching. Exact same code/ranking rule. |
| **Mechanism** | MIS-v2 disabled in the primary contrast; repeated matched block with MIS-v2 enabled and identical per-cell learning rate. Teaching and organizational teaching-memory updates are absent. |
| **Scenario** | Same task types and marginal task frequencies; IID stationary versus persistent Markov demand; three frontier-defined difficulty strata. Horizon and budgets fixed. |
| **Information** | Common full-information initialization: organizational estimates are set to the declared initial roster in both architectures. This is an explicit control, not a realistic information claim. Production-observation noise is zero in the main design; demand is the stochastic stream. |

Use competence matrices (agents × skills):

\[
S_G=((.5,.5),(.5,.5),(.5,.5)),\qquad
S_H=((.6,.4),(.4,.6),(.5,.5)).
\]

Both have per-skill totals `(1.5, 1.5)`, total competence 3.0, and per-agent row total 1.0. The heterogeneous arm is a moderate tilt, not a fully specialized team. All agents receive the same MIS-v2 rate for each skill (proposed `eta=0.10` everywhere); bounds, resource caps and policy are identical. Thus aggregate competence and aggregate initial learning headroom match. Any change in the *distribution* of productive exposure under P0 is part of the architecture's total effect, not a baseline imbalance.

Hypotheses (directional only where stated):

- **H1 (primary):** the paired architecture effect on cumulative gross CES differs between IID and persistent demand, even though both processes have the same task marginals. Statistical null `H0: Theta = 0`; two-sided alternative `H1: Theta != 0`.
- **H2 (secondary):** enabling MIS-v2 changes the architecture effect by changing the distribution of experience and competence over time. No sign is prespecified; the interaction may be zero or negative.
- **Equivalence negative control:** for a single-skill workload using all three agents each period, equal aggregate skill totals and equal MIS-v2 rates imply equal aggregate production paths across the two architectures. A difference indicates a failure of matching, action symmetry, or implementation assumptions.
- **Feasibility prediction:** an initially infeasible requirement may become feasible under MIS-v2 only if it lies below an explicitly enumerated reachable frontier. If the preflight finds no such common requirement for both architectures, do not improvise a replacement after outcomes; report that stratum blocked and seek CE review.

## 3. Scenario construction

Use the existing three problem orientations, emitted with identical orientation-specific reward weights in every arm:

- skill 0: requirements `r=(lambda,0)`, CES weights `(1,0)`;
- skill 1: `r=(0,lambda)`, weights `(0,1)`;
- joint: `r=(lambda,lambda)`, weights `(.5,.5)`.

The task-type marginal distribution is `pi=(.4,.4,.2)` for skill 0, skill 1, and joint tasks. Compare:

1. **IID stationary:** existing `StationaryTaskDemand(pi)`.
2. **Persistent/recurrent:** existing `MarkovTaskDemand`, initialized at `pi`, with transition `P(i,j)=.8*1[i=j]+.2*pi[j]`. This has stationary marginal `pi`, but positive temporal persistence. It is not described as an abrupt regime shift.

For each orientation `w`, enumerate the feasible production actions under common budget `B=2` and per-expert cap `1`. Define the realized capability frontier

\[
F_{A,w}=\max_{a\in\mathcal A(B)}\min_{k:w_k>0}\frac{Y_k(S_A,a)}{w_k},
\]

where `w` is `(1,0)`, `(0,1)`, or `(1,1)`. Requirements are `r=lambda*w`. Calculate and publish `F` separately for each architecture before generating campaign outcomes. Use three prespecified strata:

Direct enumeration of the frozen action catalogue gives the following **design calculations** (the preflight must independently reproduce them):

| Orientation `w` | `F_G,w` | `F_H,w` | Reason |
| --- | ---: | ---: | --- |
| `(1,0)` | 1.00 | 1.10 | Budget permits one full skill-0 unit for each of two experts; take the two largest skill-0 competencies. |
| `(0,1)` | 1.00 | 1.10 | Symmetric calculation for skill 1. |
| `(1,1)` | 0.50 | 0.60 | The best balanced allocation assigns one full unit to each dimension; homogeneous agents yield `.5/.5`, tilted agents can yield `.6/.6`. |

These imply easy levels `.50` for single-skill tasks and `.25` for joint tasks; common near-boundary levels `1.05` and `.55`, respectively. They are derived from both arms' frontiers, not selected from policy outcomes.

- **Easy:** `lambda_easy = 0.5 * min(F_G,w,F_H,w)`, feasible for both with a substantial frontier margin.
- **Near-boundary:** `lambda_boundary = (F_G,w + F_H,w)/2` when the frontiers differ. This common threshold is symmetric in the two arms; report its ratio to each frontier. If frontiers are equal for an orientation, use the adjacent attainable output levels immediately below/above that common frontier as a sensitivity pair, not an architecture contrast selected from results.
- **Initially infeasible but learnable:** use a fixed feasible reachability witness: at period `t`, allocate one full effort unit to skill 0 for expert `t mod 3`, and one to skill 1 for expert `(t+1) mod 3`. Over 24 periods this rotates exposure evenly, respects the existing action catalogue and budget, and gives each expert eight exposures per skill. Under MIS-v2 with `eta=.10`, each cell becomes `c'=1-(1-c)(.9)^8` after its eight full-effort exposures. The resulting witness frontiers are approximately `W_G=(1.5695,1.5695,.7848)` and `W_H=(1.6126,1.6126,.8278)` for skill 0, skill 1, and joint orientations. Thus the common learnable levels are `1.3348` for single-skill tasks and `.6924` for joint tasks: each lies above both initial frontiers and below both witness frontiers. The preflight must reproduce these values using the actual MIS-v2 function. This proves physical reachability under one declared feasible schedule; it does not predict that P0 will choose that schedule.

The requirement vector and task/reward mapping are identical for both architectures within a matched task. “Difficulty” is the measured requirement-to-frontier ratio, never an arbitrary label. The easy and boundary conditions do not require learning to create initial feasibility; the learnable stratum tests whether development can expand realized feasibility. No-heterogeneity-advantage is a separate structural negative control: repeated skill-0 demand, `B=3`, cap 1, no teaching, equal skill-0 sum, same eta. P0 should allocate all three experts to skill 0; with LI off aggregate output is the common sum 1.5, and with LI on aggregate MIS gain remains equal because `sum_i(1-c_i)` is matched and all receive equal exposure.

Do not choose or omit task orientations based on policy outcomes. If frontier conditions differ from the expected direction, preserve and report the computed values; revise only before campaign registration, with CE approval.

## 4. Matched contrasts and estimands

Every comparison uses the same frozen exogenous task-type sequence, requirements, initial state for its architecture arm, budgets, effort caps, reward weights, policy, learning rates, and indexed innovations. Architecture arms differ only in the competence distribution shown above. MIS ON/OFF arms differ only in the existing LI toggle. No teaching, teacher efficacy, or organizational teaching-memory mechanism is present.

For trajectory seed `s`, difficulty `d`, demand process `q`, and MIS setting `m`, primary matched architecture contrast:

\[
\Delta_{s,d,q,m}=R_{H,s,d,q,m}-R_{G,s,d,q,m},
\]

where `R` is cumulative **gross CES** over 24 decisions. Primary estimand is the difference in paired architecture effects between persistent and IID demand, at the near-boundary stratum and MIS OFF:

\[
\Theta=E_s[\Delta_{s,near,persistent,OFF}]-E_s[\Delta_{s,near,IID,OFF}].
\]

This identifies a controlled architecture × temporal-demand contrast **within this simulator**, conditional on P0, the specified matched skill totals and full-information start. It does not identify a real-organization effect. Secondary contrasts are architecture effects by difficulty and demand under MIS ON; the change in architecture effect from MIS OFF to ON; and the architecture × demand × MIS interaction. These do not receive primary-claim status.

Interpretation rule: a 95% interval excluding zero supports a nonzero architecture-by-demand moderation in this simulation; an interval wholly within a CE-approved equivalence margin supports practical equivalence; any interval satisfying neither condition is inconclusive. Until CE supplies that margin, report the interval without an equivalence claim. The equivalence control fails if matched aggregate competence produces different cumulative output/competence paths under its stated full-participation assumptions.

## 5. Outcomes and resource accounting

Primary outcome: cumulative gross CES per fixed-horizon trajectory. Report separately, with no composite utility:

- functional successes and success rate; “problems completed” means one successful problem decision in this one-problem-per-period model;
- cumulative resource used, residual/unused capacity, and resource cost field (not subtracted from CES);
- CES per resource used as a secondary descriptive ratio only, with denominator and zero-use handling declared;
- initial/final competence by agent and skill, competence increments, and per-agent/per-skill productive effort and MIS learning increments;
- task-type-specific CES/success and performance before/after demand runs of the other type;
- feasible-action frontier and distance to it for every task orientation.

Every arm gets the same budget (main block B=2, cap=1) and action catalogue. Actual use can differ; the difference is reported, not “corrected” by an arbitrary resource price. CES weights are fixed by task type and identical across architecture arms. Resource price is set to zero for the primary gross-CES analysis unless a future application supplies a defensible calibration; physical use remains reported.

## 6. Sampling and statistical analysis

Use **40 independent exogenous trajectory seeds per demand process** as an initial estimation design, with distinct predeclared seed namespaces for IID and Markov. For a seed, freeze one 24-period task-type sequence; reuse it across both architectures, all three difficulty mappings and MIS ON/OFF. This creates 80 independent exogenous trajectories, not 40×the number of policy/architecture arms. Observation noise is zero and is not counted as replication. Demand streams, estimator noise (if later activated), and any physical innovations must be distinct indexed streams.

Main runs: `2 demand processes × 40 trajectories × 3 difficulty strata × 2 architectures × 2 MIS settings = 960` trajectories, or 23,040 period decisions. Add the deterministic equivalence control (4 trajectories × 24 decisions) and its frontier calculations. This is compact relative to a broad factorial, but **not asserted to have a known power**: no prior variance estimate exists for this architecture contrast. Before registration, CE must state the smallest scientifically meaningful CES difference or confirm an estimation-only objective. If a precision/power calculation using an independently justified variance cannot support 40 seeds, revise sample size before seeing outcomes.

For each architecture contrast, report paired mean and median, paired SD, absolute CES difference, difference normalized by the homogeneous arm's mean only when that mean is nonzero, and 95% confidence intervals. Bootstrap at the exogenous-seed cluster: resample whole seeds and retain all paired architecture/MIS/difficulty outcomes within each seed. For `Theta`, resample seed clusters within each demand process independently, then subtract the resampled means. Report the empirical distribution and plots of paired effects; do not treat episode rows as independent observations.

One primary test/interval: `Theta` at near-boundary, MIS OFF. Family-wise Holm correction applies to the prespecified secondary architecture × demand contrasts for easy/learnable strata and MIS ON. The equivalence control uses a numerical tolerance test, not a population test. All remaining outcome decompositions are descriptive. No confidence interval is calculated from repeated observation-noise draws as if they were independent demand samples.

## 7. Preflight and acceptance criteria

Before registering or running the campaign, a small preflight must pass without outcome-driven tuning:

1. Verify the two architecture matrices have identical skill totals, total competence, per-agent row totals, parameter values, and initial information regime.
2. Enumerate feasible actions and save all `F_A,w`, near-boundary ratios, and post-witness `W_A,w(24)` values. Confirm each learnable interval is nonempty for the selected task type; otherwise stop and report blocked.
3. Confirm the equivalence-control action uses all agents and gives exactly equal initial output and equal aggregate MIS transition under both matrices (within `1e-12`).
4. Generate all demand sequences before policy evaluation; assert every paired arm receives identical task IDs, requirements, CES weights and resource limits. Verify at least 30 unique paths within each 40-seed demand family and report task frequencies and lag-one persistence.
5. Confirm frontier-based scenarios include easy success in both architectures, a genuinely near-boundary common requirement, and initially infeasible but witness-reachable demand. Do not substitute a threshold if the check fails.
6. Confirm trajectories are not outcome-saturated at every primary task type, that both success and failure occur in the designed boundary set across the two architectures, and that the easy/control negative cases remain equivalent as predicted.
7. Verify policy inputs contain estimates/public problems only; actual skills, architecture arm labels and latent demand states do not leak through the decision view. The architectural roster is public only via the specified competence estimates.
8. Run the same frozen input twice and require identical trace hashes; confirm the environment trajectory hash is identical across matched arms.
9. Record code, config, seed, trajectory, and output hashes. Keep outputs in a new campaign-specific directory, never Campaign 1/2.

These checks validate design and instrumentation, not scientific conclusions. No code extension is currently required for the proposed three-agent/two-skill study. If any acceptance criterion is impossible with existing interfaces, stop before campaign execution and ask CE to approve the smallest fix.

## 8. Candidate comparison and novelty boundary

Q1 is the only candidate recommended for the first campaign because it can hold policy, demand marginals, total competence, learning-rate rule, resources, horizon and information contract fixed using current code. Its theoretical framing is supported by G1's static configuration questions, G2's dynamic configuration/development cases, the existing MIS-v2 transition, and the model's allocation-versus-continuation propositions. This is not a new theoretical result by itself.

Novelty risk remains **high**. Prior work and internal G1/G2/G3-H already address workforce heterogeneity, allocation and learning. The exact proposed niche is narrower: matched aggregate competence distributions under equal task marginals but different temporal autocorrelation, with identical greedy P0 and a controlled MIS block. A literature review must determine whether this is substantively distinct, not merely a reparameterization. Campaign 1/2 already address directed teaching and its interaction with MIS; Q3 should not be repackaged as a novelty claim. Q2 overlaps the theoretical and historical intertemporal assignment work and would need a separate policy-identification contract.

## 9. Implementation requirements and decision

The existing three-agent/two-skill laboratory is sufficient for this question. Reuse `TeamState`/`make_team` with explicit matched matrices, `ProblemSpec` and the frozen `JOINT_ACTIONS` frontier, `P0ProductionOnly`, `LearningProfile`/MIS-v2, `ExogenousEnvironmentConfig` with C5 stationary/Markov processes, and `compare_integrated_policies` or the current runner on pre-generated trajectories. No new policy, architecture class, simulator physics, teaching mechanism, or generator is warranted. A small runner/config/result schema may be needed only after campaign authorization; it is not implemented here.

**Recommendation: GO for the preflight and campaign registration, but HOLD campaign execution** until (a) the preflight passes, (b) CE defines the minimum scientifically meaningful CES effect or approves estimation-only reporting, and (c) novelty review confirms the narrow Q1 is not already functionally covered by G1/G2 or prior workforce-allocation literature. If any fails, **NO-GO** for this campaign as currently specified; do not tune scenarios or policies to rescue it.

This design estimates effects inside the current deterministic-production, additive, discrete-action model. It does not establish external validity, social synergy, policy optimality, generalization beyond the two skills/three experts, or a net welfare ranking. The 13 previously documented repository integrity/provenance failures were not rerun; the laboratory remains **PARTIAL**.
