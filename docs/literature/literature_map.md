# Literature map

Status: initial map, 2026-09-14. No bibliographic claim below should be read as
a completeness claim or as evidence that the programme has a scientific gap.

## Review protocol

For every important source, distinguish:

1. **Conceptual precedent:** does it formulate the same problem, or only share
   ingredients?
2. **Methodological maturity:** what is optimized or approximated; what state,
   information, assumptions, and control variables are required?
3. **Accepted-solution status:** does the field treat the problem as solved, or
   are limitations/open problems documented?
4. **Scientific value of a possible extension:** could a new formulation or
   method improve an important outcome under fair evidence standards?

Status labels: **identified**, **primary source obtained**, **preliminarily
reviewed**, **critically reviewed**. No work has yet been critically reviewed
for this programme.

## Family map

| Family | Initial relevance | Current status | TODO for critical audit |
| --- | --- | --- | --- |
| Multi-agent learning / MARL | Heterogeneous policies, coordination, adaptation | identified | Determine whether competence distribution is explicit, controllable, and empirically useful. |
| Mixture-of-Experts / modular networks | Specialization and conditional task allocation | identified | Separate routing/conditional computation from knowledge-transfer and retention control. |
| Learning-to-teach / machine teaching | Selection of teaching signals and learners | identified | Determine whether multiple heterogeneous learners and future execution allocation enter the objective. |
| Collaborative intelligence / co-distillation | Knowledge exchange across agents/models | identified | Audit what transfers, who decides, and whether competence allocation is controlled. |
| Lifelong / continual multi-agent learning | Retention, consolidation, forgetting, knowledge reuse | identified | Audit links to online execution allocation. |
| Adaptive orchestration / LLM routing | Cost, latency, competence, and deployment constraints | identified | Determine whether routing changes future model competence through transfer. |
| Edge/cloud collaborative intelligence | Heterogeneous local/remote computation and collaboration | identified | Distinguish architecture and periodic retraining from deliberate competence-distribution evolution. |
| Federated / continual learning | Distributed training, personalization, retention | identified | Determine whether task assignment and competence evolution are coupled. |
| Data / knowledge valuation | Value of examples, labels, or knowledge transfer | identified | Determine whether value is assigned to changing the system-wide competence landscape. |

## Bibliography policy

`references.bib` contains only entries whose metadata have been verified from
reliable source material available to the programme. It is intentionally empty
at setup. Candidate works and missing metadata belong in this file as TODOs,
not in the BibTeX database.

## Immediate TODOs

- Obtain and critically map a small set of primary sources from each family.
- Identify whether any work explicitly represents competence distribution as a
  controllable state rather than an incidental outcome.
- Do not infer novelty from an absent exact phrase, a narrow benchmark, or an
  incomplete search.
- Do not design an algorithm or experiment until this map supports a concrete,
  falsifiable problem statement.
