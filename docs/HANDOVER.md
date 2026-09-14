# Heterogeneous Learning Systems — Handover

Last updated: 2026-09-14
Repository state: broad landscape phase provisionally consolidated; see
`research_program_checkpoint_002.md` and `landscape/landscape_001_consolidated.md`.

## Purpose

This is a research-landscape and hypothesis-formation repository. It is not a
continuation, rename, or copy of `adaptive_routing`; it contains no algorithm,
experiment, theorem, or paper claim.

## Evidence discipline

When continuing the programme, distinguish:

- **KNOWN RESULT:** established in a verified primary source or accepted
  framework;
- **EMPIRICAL EVIDENCE:** an observed result tied to a stated protocol;
- **COMMUNITY OPEN PROBLEM:** an externally documented unresolved question;
- **OUR INFERENCE:** a cautious conclusion drawn from reviewed evidence;
- **HYPOTHESIS:** an unverified programme proposition.

Existing work that shares components does not alone establish either that this
programme is novel or that the relevant problem has an accepted solution.

## Current framing

Heterogeneous systems can comprise agents/models that differ in competence,
computational cost, latency, plasticity/adaptability, specialization, and
memory or retention capability. A provisional decomposition is:

1. **Execution allocation:** which agent/model solves the current task?
2. **Learning/knowledge allocation:** which agents learn from the interaction?
3. **Retention/competence evolution:** what should persist, be consolidated,
   updated, or forgotten?

**HYPOTHESIS.** The distribution of effective competence across agents and task
regions may itself be a controllable dynamic system property. A conceptual
competence landscape (C_t) denotes this distribution; it is not yet a
validated mathematical model.

```text
competence distribution
    -> task allocation
    -> operational interactions
    -> selective knowledge transfer
    -> competence distribution'
    -> future task allocation
```

## Current falsifiable question

See [research_questions.md](research_questions.md). The sole promoted question
is RQ0: whether deliberate evolution of competence allocation improves
long-term performance relative to independently optimizing task allocation and
knowledge transfer.

## Literature state

**KNOWN RESULT / landscape observation.** Relevant bodies of work include
multi-agent learning/MARL, mixture-of-experts and modular networks,
learning-to-teach/machine teaching, collaborative intelligence and
co-distillation, lifelong/continual multi-agent learning, adaptive
orchestration and LLM routing, edge/cloud collaboration, federated/continual
learning, and data/knowledge valuation.

**HYPOTHESIS.** Individual ingredients are well studied. Whether their joint
control as a competence-distribution problem is sufficiently distinct,
methodologically immature, and practically consequential remains unknown.
No novelty claim follows from the absence of an exact wording match.

Read [landscape/landscape_000.md](landscape/landscape_000.md) and
[literature/literature_map.md](literature/literature_map.md) before proposing
theory, a method, an application, or an experiment.

## Independent prior project

`adaptive_routing` investigated a narrower two-agent execution/learning
coupling problem. It remains independent and unmodified at
<https://github.com/franjgs/adaptive_routing>. Its conclusions are not
conclusions of this programme. It may later be cited only when scientifically
relevant and with its own evidence status preserved.

## Next action

The broad horizontal audit is provisionally closed, not complete. Before
starting a minimal model, read checkpoint 002 and the consolidated landscape.
The next phase must expose assumptions and falsification criteria before an
algorithm or experiment is designed.

## New-session protocol

1. Read this file completely.
2. Read `research_questions.md`, `landscape/landscape_000.md`, and the current
   literature map.
3. Report the reconstructed evidence state before proposing work.
4. Explicitly flag any conflict between a summary and a primary source.
5. Do not convert hypotheses into novelty claims.
