# HLS reuse audit for adaptive teaching preparation

**Scope:** repository/source audit for documentary preparation. No frozen implementation was changed, and no experiment was run. This is not authorization to extend the simulator.

## Repository position

The auditable scientific status is recorded in `docs/HLS_CURRENT_STATE.md`, `docs/HLS_HISTORICAL_MEMORY_AND_NOVELTY_GUARD.md`, `HISTORY.md`, and the canonical ground-truth / protocol documents listed below. The historical record establishes organization, assignment, competence geometry, individual development, planning, and demand dynamics. It does not establish unknown relation-specific teaching efficacy.

| Component | Executable source / record | Reuse classification | What it supports | Boundary for the proposed question |
|---|---|---|---|---|
| Production and collective reward | `src/hls/discover_v0.py`: `production_inputs`, `ces_reward`, frozen `JOINT_ACTIONS` | **Reuse directly as a production component**, after checking budget compatibility | Three experts, two capability dimensions, additive output inputs, CES reward and existing action set | `ces_reward` is not a functional requirements score; current action is productive allocation only, not teaching |
| Individual learning | `src/hls/discover_develop_v2.py`: `capability_after_exposure`, `mis_v2_transition`; `docs/theory/MIS_GROUND_TRUTH.md` | **Reuse directly without modification** when the same effort/exposure semantics apply | Frozen experience-conditioned individual competence development | Does not model teaching or a relation-specific training effect |
| One-step functional organization | `src/hls/hls_lab_v1.py`: `ProblemSpec`, `TeamState`, `DecisionView`, `OrganizationState`, `FixedRouting`, `GreedyAdaptive`, `ExploreThenGreedy`, `run_sequence` | **Adapt as an interface/reference layer** | Feasibility, organization protocol, functional observer, persistent organization state | `ProblemSpec` requires horizon 1; `Organization.choose` returns a productive `JointAction`; no joint work/training action |
| Dynamic demand and partial information | `src/hls/hls_lab_dynamic.py`: `DemandRegime`, `LearningProfile`, `run_dynamic_sequence`, `run_belief_sequence`, competence estimator functions | **Adapt/reuse selectively** | Dynamic task contexts, independent real/estimated capabilities, indexed observation noise, MIS-v2 development, environment beliefs | Does not store or infer teaching efficacy; cannot currently allocate instructor time |
| Bayesian environmental planning | `src/hls/finite_problem_belief.py`: belief update, `choose_prospective_action`, `run_finite_problem_sequence` | **Reuse methodological patterns only** | Belief updates over problem hypotheses and finite-horizon action evaluation | Its posterior is about environmental hypotheses, not skill efficacy; its action and transition model cannot stand in for teaching |
| Demand generators | `src/hls/synthetic/c5.py`: `StationaryTaskDemand`, `NonStationaryTaskDemand`, `MarkovTaskDemand`; RQ0-D in `docs/experimental_foundations/RQ0_EXPERIMENTAL_CAMPAIGN.md` | **Reuse directly where semantics match** | Stationary, scheduled/nonstationary, and Markov demand variation | RQ0-D already makes demand dynamics an existing research axis; demand change alone is not the candidate extension |
| Exact/approximate optimization | `src/hls/synthetic/exact.py`, G0/C1 evaluators and tests; `docs/experimental_foundations/RQ0_EXPERIMENTAL_CAMPAIGN.md` | **Reuse only after mapping the action/state contract** | Exact small-world optimization and controlled organization comparisons exist in other synthetic contracts | No evidence yet that a solver accepts a coupled action containing production, teaching, efficacy beliefs, and shared time budget |
| Competence uncertainty | `src/hls/hls_lab_dynamic.py`: `SkillPosterior`, `initialize_competence_estimator`, `update_skill_posterior`, `predict_skill_posterior_after_mis` | **Do not reuse as relation efficacy estimator without a new observation model** | Bounded competence posterior updated from individual production observation, predicted through public MIS-v2 parameters | Identifiability and likelihood are for individual skill under effort, not instructor→learner transfer efficacy |
| Frozen historical ground truths | `docs/theory/HLS_G1_STATIC_EXPERIMENTAL_GROUND_TRUTH.md`; `docs/theory/HLS_G2_DYNAMIC_GROUND_TRUTH.md`; `docs/theory/HLS_CAPABILITY_DEVELOPMENT.md` (MIS-v2); `docs/experimental_foundations/HLS_G3_ORGANIZATIONAL_VALUE_GROUND_TRUTH.md`; RQ0 protocol above | **Reuse as constraints/comparators, not rewrite** | G1 static organization; G2/MIS present-use versus future individual development; G3-H heterogeneous learning rates/assignment continuation; RQ0 policy classes and demand dynamics | These results are not evidence that teaching works, nor that teaching efficacy is unknown and learned online |
| Existing experiment infrastructure | `experiments/synthetic/hls_lab_dynamic/characterize_laboratory.py`, `stress_pilot.py`, `smoke.py`; corresponding docs under `docs/experiments/` | **Reuse runner patterns, not old result claims** | Paired seeds, manifests/hashes, trace export, bounded pilots | Prior characterization documents confounding in organizational learning; pilots do not include teaching action or relation-efficacy targets |

## Historical results relevant to avoid repetition

- **G1:** static organization, demand, and resource interactions; no competence learning.
- **G2 and MIS:** individual learning-by-doing can make present production sacrifice worthwhile for future capability; their canonical target is not social teaching.
- **G3-H:** heterogeneous learning rates and assignment continuation are already part of the historical development story.
- **RQ0 / RQ0-D:** policy-class integration and temporal demand patterns (stationary, regime change, Markov persistence) are already explicit. A new study cannot present demand uncertainty or prospective allocation by itself as a new contribution.
- **Dynamic laboratory characterization and stress pilot:** the dynamic runner already pairs demand/noise and represents ORACLE/PARTIAL competence information. Its organizational `ExploreThenGreedy` contrast bundled exploration, stored experience, and reward-conditioned updates; the report explicitly warns that it is not a clean isolated learning effect. Functional success saturation was reduced in a bounded stress pilot but not eliminated generally.

Sources of these boundaries: `docs/HLS_HISTORICAL_MEMORY_AND_NOVELTY_GUARD.md`, `docs/theory/HLS_G2_DYNAMIC_GROUND_TRUTH.md`, `docs/theory/HLS_CAPABILITY_DEVELOPMENT.md`, `docs/experimental_foundations/HLS_G3_ORGANIZATIONAL_VALUE_GROUND_TRUTH.md`, `docs/experimental_foundations/RQ0_EXPERIMENTAL_CAMPAIGN.md`, `docs/experiments/HLS_DYNAMIC_LAB_CHARACTERIZATION.md`, and `docs/experiments/HLS_DYNAMIC_STRESS_PILOT.md`.

## What is and is not needed now

**Reuse now in scientific preparation:** the production function/action catalogue, MIS-v2 as the individual-learning arm, team/functional evaluation contracts, the dynamic demand generator, partial-information separation, paired noise/seed and artifact-manifest patterns, and the historical ground truths as frozen constraints.

**Requires approved adaptation before any implementation:** a training action with explicit time/compatibility constraints; a relation-specific latent efficacy state; an observation likelihood that can distinguish efficacy from baseline learner ability and individual learning-by-doing; competence transition semantics for instruction; and a planner that gives fixed-estimate and updated-estimate arms equivalent optimization/compute.

**Not needed for the first question:** META-VOC, Campaign 4, a general simulator rewrite, extra coordination architectures, or a broad parameter sweep. None resolves the teaching-action/identifiability gap.

## Audit conclusion

There is a substantial reusable base, but not a ready-to-run teaching experiment. The candidate should remain **HOLD / REDESIGN before implementation** until (1) prior-art full texts and a targeted search of adaptive mentoring/training assignment are completed, (2) a common production/resource accounting is approved, and (3) a teaching outcome model is specified and shown identifiable. This is a scientific contract gap, not a reason to modify frozen HLS components now.
