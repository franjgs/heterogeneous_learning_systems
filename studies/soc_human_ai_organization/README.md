# Human–AI organization in SOC teams

**Status:** research preparation; no experiment or algorithm authorized by this task.\
**Branch origin:** `refactor/hls-scientific-core` at `319098d585d8a7f32cd1f8d978807366b581a21b`.\
**Tracking:** [GitHub issue #2](https://github.com/franjgs/heterogeneous_learning_systems/issues/2).\
**Editorial target:** *Electronics*, Special Issue [“Timely AI Advancements and Interdisciplinary Synergies for Intelligent Modeling”](https://www.mdpi.com/journal/electronics/special_issues/MET7IZ3S8B); official deadline found: **15 March 2027**. Targeting a venue does not imply editorial suitability or acceptance.

## Purpose

Prepare an independent application study of how heterogeneous cyberanalyst competencies are organized, used and potentially developed, with and without AI assistance. The intended long-term use is quantitative decision support for workforce organization under workload, time, resource and cost constraints. Sophistication is not presumed to improve outcomes.

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

The proposed scenario distinguishes L1 initial alert triage (whether to escalate and whether to report) from L2 deeper investigation of alerts requiring further analysis. These process labels and decisions come from the project instruction; they are not verified procedures of a particular client. See [scenario and model boundary](MODEL_AND_SCENARIO.md).

## Relationship to HLS core

This is an application-specific research space, not a replacement for the HLS core or its four responsibilities: scenario, organization, model and performance evaluation. The starting conceptual anchor is [`scenario.soc_alert_operations`](../../registry/catalog.json) and [`study.soc_competence_heterogeneity_testbed`](../../registry/catalog.json), recorded in core commit `319098d585d8a7f32cd1f8d978807366b581a21b`.

Potentially reusable HLS components are listed in [evidence and transfer candidates](EVIDENCE.md). Every transfer to core requires a semantic-compatibility review, evidence review and PI approval. SOC findings remain application-scoped unless separately justified; no automatic promotion is intended.

## Editorial target and AIAI 2026 relationship

The Special Issue flyer welcomes expanded AIAI/EAAAI 2026 papers and specifies a minimum 50% increase for such expanded versions. The project instruction intends to extend an AIAI 2026 article, but **the specific article (title, author list, DOI/version and full text) was not identifiable in the accessible HLS core or historical archive**. Therefore eligibility, overlap and contribution differences are unresolved. The proposed extension dimensions—workforce organization, task assignment, competence development and training opportunity costs, changing clients/threats, and human–AI assistance—are intended comparison axes, not established novelty claims. See [literature and publication fit](LITERATURE.md) and the [manuscript outline](MANUSCRIPT_OUTLINE.md).

The task order received on 2026-10-27 authorizes this preparatory documentation, a tracking issue and a review PR. It does not authorize experiments, model implementation or a manuscript with results. Historical governance records do not identify a named PI; no identity is inferred here. Scientific decisions beyond this bounded preparation remain for PI review.

## Project files

- [Literature, AIAI comparison and editorial requirements](LITERATURE.md)
- [Scenario, model constructs and organization candidates](MODEL_AND_SCENARIO.md)
- [Protocol readiness and reproducibility](PROTOCOL_AND_REPRODUCIBILITY.md)
- [Evidence, limits and core-transfer candidates](EVIDENCE.md)
- [Decision and research chronology](HISTORY.md)
- [Future manuscript outline](MANUSCRIPT_OUTLINE.md)

Consult the HLS core [doctrine](../../docs/RESEARCH_DOCTRINE.md), [ontology](../../docs/ONTOLOGY.md), [theory](../../docs/THEORY.md), [literature](../../docs/LITERATURE.md), [research record](../../docs/RESEARCH.md), [history](../../docs/HISTORY.md), and [catalog](../../registry/catalog.json) for governing scientific meanings and evidence. This project does not copy those sources.
