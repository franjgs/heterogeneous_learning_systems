# HLS Campaign 2 — Teaching × MIS-v2 × Work Assignment

**Status:** bounded experiment COMPLETE; infrastructure milestone remains PARTIAL.
**Base:** `1c902f180d37a12fd9806d0db427b0adf83a0029`.
**Design registered:** 2026-10-15 20:37:57 +02:00.
**Execution:** 2026-10-15 20:38:57–20:39:04 +02:00, Europe/Madrid.
This HLS Laboratory campaign is separate from the historical Campaign 2 prospective-adaptation experiments; their sources, results and hashes were preserved.

## Question, hypotheses and predeclared design

Does the cumulative-CES interaction of one directed lesson with learning-by-doing depend on whether it changes subsequent productive opportunities? H1 predicts possible complementarity when teaching opens assignments; H2 predicts possible substitution when the taught skill already receives productive experience; H3 predicts dependence on subsequent demand. These are conditional hypotheses, not universal sign requirements.

The [registered protocol](../../results/experiments/hls_campaign2_teaching_mis_assignment/protocol.json) fixes three transparent configurations before outcome evaluation. This is a timestamped local design record, not an external preregistration. No parameter search or policy optimization was performed.

| Scenario | Initial competence matrix (agents × skills) | Demand | Configuration rationale |
| --- | --- | --- | --- |
| A: substitution candidate | `((.90,.20),(.45,.20),(.25,.80))` | Skill 0 for 24 periods | Learner E1 already outranks reserve E2 (.45>.25); teaching and MIS can develop an already exercised skill. |
| B: enabling candidate | `((.90,.20),(.20,.20),(.25,.80))` | Skill 0 for 24 periods | Learner .20 starts below reserve .25. The specified lesson can cross this ranking gap without imposing an individual eligibility gate. |
| C: demand change | Same as B | Skill 0 for periods 0–11; skill 1 for 12–23 | Identical initial state/prefix, with a predetermined exogenous change in relevance of the taught skill. |

Requirements are `(1,0)` or `(0,1)` with corresponding CES weights `(1,0)` or `(0,1)`. These are fixed external evaluation inputs. The active-skill CES measures gross production in that dimension; the demand shift changes its relevance. Resource budget is 2.0; expert effort cap is 1.0; recorded resource price is 0.2 per used effort unit, separate from CES. Existing C5 `StationaryTaskDemand`/`NonStationaryTaskDemand`, `DemandRegime`, and `generate_environment_trajectory` generate and freeze the sequence before branching. Demand is deterministic by scenario: seeds vary observation noise, not demand.

All four conditions share the full `OrganizationSnapshot`: true and estimated competence, experience/performance, grid posterior, empty efficacy memory and period 0. Initial prior means are explicitly calibrated to the numerical initial skills, variance .0025, grid 101 points. This is a controlled initial-information assumption, not a claim that real organizations know skills. There is no subsequent private-state access by the policy.

Conditions are C00 teaching OFF/MIS OFF; C10 ON/OFF; C01 OFF/ON; C11 ON/ON. Teaching is forced only at period 0: instructor E0, learner E1, skill 0, effort .25 per participant (total .5), efficacy .85, transfer rate .75. Off conditions use the corresponding P0 no-teaching production choice. Teaching conditions use the best feasible production allocation for that fixed relation under the existing functional decision score. These first actions are fixed identically within each MIS pair. Production effort displaced at the intervention is part of the teaching treatment.

Afterward, every branch uses the existing **P0ProductionOnly**, with no repeated teaching. It receives only `IntegratedDecisionView`, uses updated estimated competence, and orders actions by success, negative normalized deficit, margin and negative effort. It does not maximize CES or use experimental labels. Its observation/posterior updater is common; the known MIS switch also controls prediction of estimated skill development. Teaching generates its usual noisy formative observation. These information consequences belong to the treatment package and are not separately manipulated.

MIS eta is `((.06,.03),(.04,.08),(.02,.05))`. Transition order remains production → MIS-v2 → teaching. Direct gain is `g=.75*.25*.85*(1-c_after_MIS)`; here neither teaching participant produces at period 0, so the direct gain is identical in C10/C11. The existing runner logs it directly. Per-period MIS gains are obtained by applying the existing `advance_team` transition to the saved pre-period state/action, and checked against the real next state plus the separately logged teaching gain.

## Execution and estimand

Three zero-noise diagnostic quadruples and ten noisy quadruples per scenario were executed (seeds `2026101601`–`2026101610`, deterministic fixture seed `2026101600`). Gaussian production and formative observation SDs are .02 in noisy runs, zero in fixtures. Existing indexed innovations are common across branches; realized observations may differ with action and competence. An additional zero-efficacy B fixture gives **34 quadruples, 136 runs, 3,264 period records** (33 main quadruples plus one negative control).

Primary estimand: `I_R=(R11−R01)−(R10−R00)`, where each R is cumulative gross CES over 24 decisions. This is a paired, conditional factorial interaction under P0 continuation. It is not a globally optimal teaching value or a causal mediation decomposition. Break-even below is the first nonnegative cumulative teaching contrast after a loss that stays nonnegative through the horizon; periods are zero-based.

## Results

| Scenario | R00 | R10 | R01 | R11 | Teaching effect MIS OFF | Teaching effect MIS ON | I_R |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| A | 32.400000 | 33.316094 | 38.122766 | 37.946387 | +0.916094 | −0.176379 | **−1.092473** |
| B | 27.600000 | 28.482500 | 32.302596 | 34.747049 | +0.882500 | +2.444453 | **+1.561953** |
| C | 25.800000 | 25.752500 | 30.891515 | 31.183167 | −0.047500 | +0.291651 | **+0.339151** |

Values are noisy-seed means; the zero-noise fixtures give the same CES results. Every observed seed has the displayed interaction sign (A 10 negative; B/C each 10 positive). Across the ten seeds per scenario, SD and MCSE of I_R are zero, and empirical ranges and percentile-bootstrap mean intervals collapse to the displayed value. These degenerate intervals describe this finite seed sample only, not zero model uncertainty or a population effect. The protocol prespecified 5,000 paired-quadruple bootstrap resamples with separate seed 2026101599; no significance tests were performed.

Noise changes posterior paths (ten distinct estimate paths per condition), but leaves CES totals unchanged in this sample. A/B each retain one production-action path per condition. In C with MIS OFF there are seven distinct action paths: equally productive skill-1 assignments can change without changing CES. Thus these are actual noisy executions with outcome degeneracy, rather than additional independent deterministic replications supporting inferential precision.

Initial teaching CES loss is 1.1 in A and .9 in B/C, for either MIS setting. Stable break-even: A MIS OFF period 13, MIS ON never; B OFF period 12, ON period 10; C OFF never, ON period 10. The B/C trajectories match before the regime change. After period 12 their within-scenario teaching contrasts stop accumulating new skill-0 benefits in C. Positive I_R in C does not imply positive teaching value with MIS OFF.

Functional success is saturated for the no-teaching branches: 24/24 in all scenarios/conditions. Teaching branches succeed in 23/24 because the first teaching-period production fails the active requirement. Therefore teaching lowers aggregate binary success even where it improves cumulative CES. No new team-level functional feasibility is demonstrated.

## Mechanism measurements

| Scenario | Direct teaching gain (C10=C11) | Subsequent learner skill-0 effort, without → with teaching | Learner total skill-0 MIS gain, C01 → C11 | Subsequent assignment changes, OFF/ON |
| --- | ---: | ---: | ---: | ---: |
| A | .08765625 | 23 → 23 | .34352271 → .28154170 | 0 / 0 |
| B | .12750000 | 0 → 23 | 0 → .40951520 | 23 / 23 |
| C | .12750000 | 0 → 11 | 0 → .24328405 | 11 / 11 |

The effort columns exclude the intervention period; MIS-gain columns include the full run. A without teaching also has an initial productive exposure, so its total target experience is 24 versus 23 with teaching. Direct gains are never inferred from net competence changes. The final learner target skills, ordered C00/C10/C01/C11, are A `.450000/.537656/.793523/.819198`, B `.200000/.327500/.200000/.737015`, C `.200000/.327500/.200000/.570784`. Full final matrices, estimates, variances, experience, observations and actions are retained in the CSVs.

In B/C, teaching changes the selected productive pair from E0+E2 to E0+E1 on subsequent skill-0 tasks. E1 was always physically allowed to produce: “enabling” here means entering P0's preferred allocation after a competence-ranking change, not acquiring a modeled license or satisfying an individual participation threshold. B has 23 new target-skill opportunities; C has 11 before demand moves away. A develops an already selected participant and shows a negative interaction despite a higher final learner skill.

No-teaching runs use 48 productive effort units over 24 periods. Teaching runs use 47 productive units plus .5 teaching effort and leave .5 capacity unused. Each instructor/learner consumes .25 at the intervention; discrete allocations strand the remaining half-unit. Recorded resource costs are 9.6 versus 9.5 and are not subtracted from CES. Increments, opportunities, allocation changes and gross performance are separate measurements.

## Hypothesis assessment and causal limits

**H1: conditionally supported in B.** The forced lesson opens selected target-skill production, which yields additional MIS gains and positive I_R. Those observed links are consistent with the proposed mechanism. The total factorial interaction also incorporates displaced initial production/experience, heterogeneous eta, posterior changes and later P0 choices. Assignment changes alone do not identify a mediated effect.

**H2: conditionally supported in A.** Subsequent assignments are unchanged and teaching's marginal CES value falls when MIS is active. Saturation and lost initial production/experience coexist; the campaign does not establish that saturation alone causes substitution.

**H3: supported for this controlled B/C trajectory contrast.** Same initial state, period-0 intervention and first 12 problems; the exogenous shift reduces I_R from +1.561953 to +.339151 and turns the MIS-OFF teaching contrast negative. It does not establish the distribution of effects across other demand processes.

A direct assignment-mediated causal estimate would require an additional intervention on assignment or exposure while controlling feasible resources and information. That intervention was not performed. No percentages of effects are attributed to independent mechanisms, no general claim of synergy is made, and no attainable-capability set expansion is established.

## Controls, validation and limitations

The zero-efficacy fixture has zero direct gain while paying the teaching/production cost. It has I_R=−.075904: a null teaching gain need not imply zero total interaction because production and experience were displaced. MIS OFF yields an exactly zero MIS-gain matrix; C00 preserves every true competence; teaching directly changes only the targeted learner cell; all four branches share the same demand and initial state. Tests check independent snapshots, identical first actions by MIS pair, common P0 continuation, indexed noise, no private-state fields, resource limits, reproducibility, serialization, interaction arithmetic and saved-result integrity, including the matched B/C pre-change prefix.

Validation: **123 tests passed** (16 Campaign 2 tests plus 107 relevant historical regressions). [JUnit results](../../results/experiments/hls_campaign2_teaching_mis_assignment/test_results.xml) retain the executed test cases. The full repository suite was not rerun; its previously identified **13 historical provenance/integrity failures remain unresolved**, and HLS-LAB-V1-INTEGRATED remains **PARTIAL**.

Production remains additive, complementarity means multidimensional coverage, the action catalogue remains discrete, CES is gross and distinct from resource costs, the production score differs from CES, and values depend on P0 continuation. The initial calibrated prior, 101-point skill grid, elementary formative estimator, fixed efficacy .85, single lesson, short horizon, deterministic demand and seed-insensitive CES all constrain interpretation. Neither real-organization validation nor a population causal claim follows. Campaign 1 findings were not revised.

## Reproducibility and artifacts

The [execution manifest](../../results/experiments/hls_campaign2_teaching_mis_assignment/manifest.json) records execution times, source hashes, platform and original output hashes; the [analysis manifest](../../results/experiments/hls_campaign2_teaching_mis_assignment/analysis_manifest.json) records input/output hashes and integrity checks. Source files are [runner](../../experiments/synthetic/hls_campaign2/teaching_mis_assignment.py), [analysis](../../experiments/synthetic/hls_campaign2/analyze_teaching_mis.py), and [tests](../../tests/test_hls_campaign2_teaching_mis_assignment.py). Results are isolated under `results/experiments/hls_campaign2_teaching_mis_assignment/`: `paired_outcomes.csv`, `mechanism_traces.csv.gz`, `interaction_summary.csv`, `mechanism_summary.csv`, `assignment_contrasts.csv`, `seed_sensitivity.csv`, `negative_control_outcomes.csv`, `initial_states.json`, protocol/manifests and JUnit report.

Reproduce into a new directory (the runner refuses to overwrite a completed execution):

```bash
PYTHONPATH=src:. python -m experiments.synthetic.hls_campaign2.teaching_mis_assignment --prepare --output /path/to/new/output
PYTHONPATH=src:. python -m experiments.synthetic.hls_campaign2.teaching_mis_assignment --output /path/to/new/output
PYTHONPATH=src:. python -m experiments.synthetic.hls_campaign2.analyze_teaching_mis --output /path/to/new/output
PYTHONPATH=src:. pytest -q tests/test_hls_campaign2_teaching_mis_assignment.py
```

The analysis command reads the selected output directory and regenerates derived summaries; it does not execute organizations. Omit `--output` to analyze the published default artifacts. All intervention and continuation behavior comes from the existing integrated laboratory. No laboratory physics, estimator, policy or historical artifact was changed.

The subsequent read-only [Campaign 2 experimental sensitivity audit](HLS_EXPERIMENTAL_SENSITIVITY_AUDIT.md) explains replicate-level CES degeneracy from source dependencies, P0 score boundaries, reward/success sensitivity, and effective-path counts. It uses these published outputs without rewriting this findings record or changing its numerical results.
