# Evidence ledger and HLS transfer candidates

## Project evidence state

This HLS application project has **no experiments, data collection, organizational outcomes or validated results of its own**. It now records (i) the public AIAI 2026 classifier results, (ii) separate internal SOCTRA LSE experiments and operational descriptions, and (iii) HLS hypotheses. These categories are not interchangeable. The testbed is proposed, not validated.

The historical archive audit at `feature/hls-laboratory-v1`, commit `c81def3b5280b0f59d6dcbfd3e25df8805f5013c`, reports that SOCTRA's schema was not verified for analyst-level competence, alert routes, analyst service times or training history. The same audit warns that mapping HLS agents/tasks/capabilities to analysts/alerts is an inference, not validation. Per PI clarification, SOCTRA demonstrated reduced operational triage burden from AI-assisted triage; this is distinct from a measured quantity of analyst time/capacity released. The reviewed sources do not quantify before/after analyst minutes, queue burden, staffing requirement or released capacity. A classifier metric or reduced false-alarm rate is not by itself a labor-time estimate. The public AIAI chapter contains classifier evaluation, not organizational-learning evidence. Internal SOCTRA artifacts include additional LSE classifier results and workflow context; their exact table-producing configuration and permission for release/reuse are unresolved. Any numerical capacity-release value used in a future simulation is hypothetical unless independently measured and documented.

## HLS components that may inform this application

All items below are **candidates for reuse**, not already imported project components. Reuse requires a study-specific semantic, unit, information, evidence and compatibility review; transfer into the HLS core also requires PI approval.

| Candidate | Core source | Possible relevance | Transfer limit |
|---|---|---|---|
| Static assignment model and crossed-specialization exact result | [`src/hls/static_assignment.py`](../../src/hls/static_assignment.py); `model.static_allocation`; `theoretical_result.crossed_specialization_gain` | Formalize fixed competence allocation and conditions for taskwise value. | Two agents/tasks and scalar effectiveness; not SOC queue, incident severity or human workforce evidence. |
| Dynamic competence-development construction | [`src/hls/dynamic_development.py`](../../src/hls/dynamic_development.py); `model.two_period_competence_development`; `study.dynamic_competence_development` | Distinguish state change, competence/frontier change and future value. | Deterministic finite two-period model; no empirical training law, mentor or economic opportunity cost. |
| Deadline-constrained allocation and mean-preserving composition result | Core catalog `model.dynamic_deadline_allocation`, `result.mean_preserving_composition_effect`; historical source `docs/research/CE-04/11_CONFIRMATORY_RESULTS.md` in archive commit above | Candidate vocabulary for queue, deadline, performance and mean-preserving heterogeneity comparisons. | Synthetic model, fixed competence/no learning/cooperation; campaign runners/raw traces are not reproducible on this branch. |
| Matched-marginal structure comparison | Core catalog `study.joint_competence_structure`, `result.joint_structure_effect`; historical source `docs/research/CE-07/04_CONFIRMATORY_RESULTS.md` | A narrowly scoped precedent that joint competence structure can matter under one synthetic organization/policy. | Only two structures, one synthetic queue and fixed P1; no general specialization claim or identified mediator. |
| Competence transfer and learning negative/inconclusive evidence | Core catalog `result.transfer_effect_inconclusive`; historical source `docs/research/HLS_CE_03_H3_V2_CAMPAIGN_RESULTS.md` | Warns against assuming transfer improves an individual or collective outcome. | Synthetic transfer procedure; inconclusive results are not evidence that SOC training/transfer has no effect. |
| Evaluation and ontology | [`docs/ONTOLOGY.md`](../../docs/ONTOLOGY.md), `evaluation.paired_seed_bootstrap`, `evaluation.on_time_collective_success` | Reuse distinctions among competence/capability, policy/organization, estimand/metric and independent replication unit. | Measures and causal design must be rebuilt for human analysts, SOC outcomes and clustered/longitudinal observations. |

No core organizational policy, AI mechanism, training estimator or SOC implementation is declared directly reusable. The current active core contains no SOC execution code.

## Evidence status labels for future entries

When results arise, classify each as literature context, hypothesis, formal result, exact computation, simulation, exploratory/confirmatory empirical observation, technical validation, negative, null, ambiguous or inconclusive. Keep execution status separate from scientific outcome. Link all claims to protocol/configuration/data/code and retain adverse findings. Do not count historical CE-06 reanalysis as independent replication of CE-04.


## AIAI/SOCTRA evidence boundary

See [AIAI_2026_ANALYSIS.md](AIAI_2026_ANALYSIS.md) for the published article results, internal LSE results, operational source inventory, version differences and restrictions. Keep three levels separate: (1) classification methods and predictive performance; (2) the SOCTRA-demonstrated reduction in triage burden, distinct from a quantitative analyst-time/capacity estimate, which is unavailable in the reviewed sources; and (3) organizational policies for using capacity released in practice or assumed in simulation. The third level is the proposed HLS contribution; costs, service constraints and performance trade-offs must be explicit.
