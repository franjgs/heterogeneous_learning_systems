# Human–AI organization in SOC teams

**Status:** research preparation; no experiment or algorithm authorized by this task.\
**Branch origin:** `refactor/hls-scientific-core` at `319098d585d8a7f32cd1f8d978807366b581a21b`.\
**Tracking:** [GitHub issue #2](https://github.com/franjgs/heterogeneous_learning_systems/issues/2).\
**Editorial target:** *Electronics*, Special Issue [“Timely AI Advancements and Interdisciplinary Synergies for Intelligent Modeling”](https://www.mdpi.com/journal/electronics/special_issues/MET7IZ3S8B); official deadline found: **15 March 2027**. Targeting a venue does not imply editorial suitability or acceptance.

## Purpose

Prepare an independent application study of how heterogeneous cyberanalyst competencies are organized, used and potentially developed, with and without AI assistance. The intended long-term use is quantitative decision support for workforce organization under workload, time, resource and cost constraints. Sophistication is not presumed to improve outcomes. The study does not aim to reconstruct GMV-CERT's real organization, historical assignments or analyst careers; aggregate SOCTRA data anchor problem scale and structure only.

The first research dimension is **competence heterogeneity**: its characterization, utilization, development, adaptation, benefits, costs and limitations. Experience is not a competence measure; learning is not assumed to improve performance. Individual competence, individual attainable capability, collective attainable capability and realized collective performance remain separate quantities.

## Proposed research questions

These are initial questions for PI review, not approved hypotheses:

1. How can task-relevant analyst competence be measured without treating experience, credentials or task exposure as competence itself?
2. Under what workload, task-mix and resource conditions do fixed, specialized or dynamic assignment strategies change individual and collective outcomes?
3. What are the net effects of deliberate training after accounting for analyst time, mentor time, direct cost, displaced operational work and uncertain competence change?
4. How do client, technology or threat changes affect the value and cost of specialization, learning and adaptation?
5. When does AI assistance change analyst performance, workload, learning or allocation outcomes, and for whom?

No hypothesis, estimand, policy ranking or experiment has been frozen.

## Testbed boundary

The proposed scenario distinguishes L1 initial alert triage (whether to escalate and whether to report) from L2 deeper investigation of alerts requiring further analysis. These process labels and decisions come from the project instruction; they are not verified procedures of a particular client. The study-level rationale, empirical boundary and provisional competence-matrix hypothesis are in the [scientific synthesis](MODEL_AND_SCENARIO.md).

An aggregate-only characterization of the local alert snapshots proposes an empirical demand trace. It finds project concentration and substantial arrival variability, but does not identify staffing, service times or released analyst-hours. The PI authorized these aggregate study documents for this repository; this does not clear source data or establish permission for manuscript reuse. See [demand characterization and sizing proposal](DEMAND_CHARACTERIZATION.md).

## Relationship to HLS core

This is an application-specific research space, not a replacement for the HLS core or its four responsibilities: scenario, organization, model and performance evaluation. The starting conceptual anchor is [`scenario.soc_alert_operations`](../../registry/catalog.json) and [`study.soc_competence_heterogeneity_testbed`](../../registry/catalog.json), recorded in core commit `319098d585d8a7f32cd1f8d978807366b581a21b`.

Potentially reusable HLS components are listed in [evidence and transfer candidates](EVIDENCE.md). Every transfer to core requires a semantic-compatibility review, evidence review and PI approval. SOC findings remain application-scoped unless separately justified; no automatic promotion is intended.

## Editorial target and AIAI 2026 relationship

The Special Issue flyer welcomes expanded AIAI/EAAAI 2026 papers and specifies a minimum 50% increase for such expanded versions. The published baseline is Lázaro et al., Springer AIAI 2026 chapter, DOI [10.1007/978-3-032-30805-4_11](https://doi.org/10.1007/978-3-032-30805-4_11). The [source analysis](AIAI_2026_ANALYSIS.md) separates the published L1 classifier, LSEnsemble as a distinct classification method, SOCTRA's demonstrated reduction in triage burden, and the proposed HLS organizational study. Neither classifier is an organizational policy. The amount of analyst time/capacity released is not quantified in the reviewed sources, so a simulation's release value must remain explicitly hypothetical unless measured. The candidate HLS contribution is how available capacity is organized and invested, including training costs, displaced work, service constraints and performance trade-offs—not another classifier.

The task order received on 2026-10-27 authorizes this preparatory documentation, a tracking issue and a review PR. It does not authorize experiments, model implementation or a manuscript with results. Historical governance records do not identify a named PI; no identity is inferred here. Scientific decisions beyond this bounded preparation remain for PI review.

## Project files

- [AIAI/SOCTRA source inventory and critical analysis](AIAI_2026_ANALYSIS.md)
- [Literature, AIAI comparison and editorial requirements](LITERATURE.md)
- [Scientific synthesis: study question, evidence boundary and model hypothesis](MODEL_AND_SCENARIO.md)
- [Protocol readiness and reproducibility](PROTOCOL_AND_REPRODUCIBILITY.md)
- [Demand characterization and HLS sizing proposal](DEMAND_CHARACTERIZATION.md)
- [Analyst identifier, experience and workload audit](ANALYST_EXPERIENCE_AUDIT.md)
- [Evidence, limits and core-transfer candidates](EVIDENCE.md)
- [Decision and research chronology](HISTORY.md)
- [Future manuscript outline](MANUSCRIPT_OUTLINE.md)

Consult the HLS core [doctrine](../../docs/RESEARCH_DOCTRINE.md), [ontology](../../docs/ONTOLOGY.md), [theory](../../docs/THEORY.md), [literature](../../docs/LITERATURE.md), [research record](../../docs/RESEARCH.md), [history](../../docs/HISTORY.md), and [catalog](../../registry/catalog.json) for governing scientific meanings and evidence. This project does not copy those sources.
