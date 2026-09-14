# Landscape 000 — Initial exploration

Date: 2026-09-14
Status: hypothesis formation; not a novelty audit or a solution survey.

## Candidate object of study

**HYPOTHESIS.** A heterogeneous system may have a time-varying competence
landscape (C_t), whose entries describe effective competence of agents over
task regions or domains. This is a conceptual abstraction only. It has no
defined state space, metric, dynamics, control variables, or validated
observability assumptions.

The programme separates execution allocation, learning/knowledge allocation,
and retention/competence evolution. Their interaction motivates RQ0; it does
not establish that they must be optimized jointly or that a generic joint
optimizer is useful.

## Edge/cloud and SLM/LLM collaboration

**KNOWN RESULT / broad coverage.** Cost-, latency-, and quality-aware routing
between local/small and remote/large models, plus knowledge transfer and
distillation, are established research themes.

**OPEN QUESTION.** Whether systems in this family explicitly manage a dynamic
distribution of competence across agents rather than separately routing and
retraining must be audited work by work.

## Robotics and autonomy

**KNOWN RESULT / broad coverage.** Active imitation learning, supervisory
intervention, collaborative autonomy, and continual adaptation address when to
seek help and how feedback alters a learner.

**OPEN QUESTION.** Whether these methods formulate competence allocation across
agents as an explicit controllable state, rather than a consequence of policy
learning or data acquisition, is unresolved here.

## Federated and continual learning

**KNOWN RESULT / broad coverage.** Federated, continual, lifelong, and
multi-agent learning address distributed knowledge, adaptation, consolidation,
and forgetting.

**OPEN QUESTION.** The relationship between those mechanisms and online task
allocation across heterogeneous agents requires precise comparison; shared
terminology is not evidence of equivalence.

## Cross-field audit targets

| Family | What is clearly relevant | What cannot yet be concluded |
| --- | --- | --- |
| MARL | Coordination, credit assignment, and evolving agent policies | That it solves competence-distribution control as posed here |
| Mixture-of-Experts/modular networks | Conditional computation, specialization, and routing | That transfer, retention, and competence evolution are jointly handled |
| Machine teaching/learning-to-teach | Deliberate selection of teaching signals | That task allocation and heterogeneous competence evolution are covered |
| Collaborative intelligence/co-distillation | Multiple models/agents exchange knowledge | That operational allocation and retention are jointly optimized |
| Lifelong multi-agent learning | Knowledge reuse and continual adaptation | That competence allocation is a controlled system state |
| Adaptive orchestration/LLM routing | Cost/quality/latency-aware allocation | That routing decisions control future competence distribution |

## Audit discipline

For each primary source, record conceptual coverage, methodological maturity,
whether an accepted solution exists, important limitations/open problems, and
evidence for effective improvement. The presence of ingredients in one paper
does not prove the target problem solved; conversely, no exact match does not
establish novelty.

See [the literature map](../literature/literature_map.md).
