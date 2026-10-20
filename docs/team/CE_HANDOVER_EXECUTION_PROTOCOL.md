# HLS Chief Engineer handover — operational supplement

**Status:** Operational supplement to the canonical [HLS Team Handover Protocol](HLS_TEAM_HANDOVER_PROTOCOL.md), especially §8. It does not replace, amend, or outrank that protocol, the PI, or scientific source documents.

## 1. Purpose and boundary

This document turns the canonical **REPLACE CHIEF ENGINEER** procedure into an auditable sequence for transferring the CE role to a new person. It governs role continuity only. It does not transfer the PI's scientific authority, approve a research direction, resolve scientific contradictions, or make an incoming CE's agreement with an outgoing interpretation a condition of acceptance.

Creating or reading this protocol is **not itself authorization to replace the CE**. The PI must explicitly authorize a particular replacement. If an earlier CE handover is still pending—as recorded in [HLS_ROLE_REGISTER.md](HLS_ROLE_REGISTER.md) at the time this supplement was prepared—the PI must state whether that transfer remains active, is completed, or is superseded before a new transfer is entered. The steward must not silently substitute an incoming person or rewrite the earlier record.

## 2. Roles

- **PI:** authorizes the replacement; decides any strategic, doctrinal, or scientific issue escalated; accepts the governance transition.
- **Outgoing CE:** provides a source-grounded transfer of responsibilities, active work, artifacts, dependencies, WIP, failures, and known blockers. The outgoing CE does not determine the successor's independent diagnosis.
- **Incoming CE:** independently reconstructs the project and submits the acceptance report in §7. It inherits the CE role's authorized scope, not private interpretations or unmaterialized chat decisions.
- **Handover Steward:** checks repository baseline, links, source authority, worktree classification, completeness, and register consistency. The steward does not settle scientific questions or activate the successor.

## 3. Required phases

### Phase 0 — PI authorization

Before preparing a person-specific transfer, record the PI's authorization with:

- operation: **REPLACE CHIEF ENGINEER**;
- outgoing and incoming identifiers;
- effective baseline commit and branch;
- scope/mission and any changed interfaces;
- whether an existing pending CE transfer is continued, completed, or superseded;
- expected acceptance artifact and decision owner.

If authorization, identity, or disposition of a pending transfer is unclear, stop and ask the PI. Do not infer authorization from this protocol, a chat summary, commit authorship, or the existence of a draft handover.

### Phase 1 — Freeze and audit the baseline

The steward records, without cleaning or changing the worktree:

1. full git HEAD, branch, and short status;
2. each relevant change/artifact as committed, accepted WIP, pending decision, excluded, or abandoned, with owner and location where known;
3. the authoritative project sources consulted and their stated status;
4. contradictions, stale pointers, missing manifests, and unavailable data;
5. whether any experiment is running or any frozen artifact is under active generation.

Never classify untracked material as irrelevant merely because it is untracked. Never stage, discard, regenerate, or promote WIP as part of handover preparation. If a running experiment or an uncertain frozen artifact makes the baseline unsafe to characterize, pause the transfer and escalate.

### Phase 2 — Outgoing transfer

The outgoing CE package uses [HANDOVER_TEMPLATE.md](HANDOVER_TEMPLATE.md) and records, with repository paths and status labels:

- current CE mission, decision boundaries, and interfaces;
- work completed and work still active, including exact next step and stop condition;
- protocols, source revisions, results, data, hashes, commands, and reproducibility dependencies;
- committed work and every relevant WIP item, without treating WIP as canonical;
- negative results, failed approaches, reductions, unresolved hypotheses, and blockers;
- known documentation debt and disagreements between the CE's interpretation and repository authorities;
- recommendations, explicitly labelled as recommendations rather than facts.

The outgoing CE may describe its own reasoning, but the package must identify which statements are source-established and which are interpretation. Missing outgoing material is recorded as missing; the steward must not invent it.

### Phase 3 — Incoming reconstruction

The incoming CE reads sources according to the live authority map in [REPOSITORY_GUIDE.md](../REPOSITORY_GUIDE.md), not according to commit order or this supplement's cached path list. Minimum reconstruction order:

1. [HLS Philosophy](../HLS_PHILOSOPHY.md), [Research Doctrine](../../RESEARCH_DOCTRINE.md), [HLS Ontology](../hls_ontology.md), and [Research Questions](../research_questions.md);
2. [HLS Current State](../HLS_CURRENT_STATE.md), [Repository Guide](../REPOSITORY_GUIDE.md), [HISTORY](../HISTORY.md), and [Historical Memory and Novelty Guard](../HLS_HISTORICAL_MEMORY_AND_NOVELTY_GUARD.md);
3. theory registry and the theory/ground-truth sources relevant to the active programme;
4. protocols, manifests, code, tests, and result artifacts for active or recently closed experiments, consulting each source only for its declared scope;
5. publication/literature records when needed for provenance or claim review.

The incoming CE then checks the transfer against those sources and classifies significant statements as established result, scoped result, hypothesis, interpretation, protocol, WIP, or unresolved. The package does not compel the incoming CE to accept scientific interpretations.

### Phase 4 — Acceptance and PI disposition

The incoming CE submits the report in §4. The steward checks completeness and source references, then sends unresolved scientific/governance conflicts to the PI without reconciling them. The PI records one of:

- **ACCEPT TRANSFER:** role transition may be entered in the register;
- **ACCEPT WITH OPEN ITEMS:** only if the open items have an owner, safe boundary, and explicit escalation route;
- **RETURN FOR CLARIFICATION:** incoming/outgoing transfer is incomplete;
- **HOLD / ESCALATE:** baseline, authority, or scientific contradiction blocks safe activation.

Only after the PI's disposition and incoming acceptance are recorded may the steward update [HLS_ROLE_REGISTER.md](HLS_ROLE_REGISTER.md): outgoing CE to **REPLACED**, incoming CE to **ACTIVE**, with identifiers, baseline, and link to the accepted handover. The register is not updated on draft creation or receipt alone. Keep accepted and superseded handovers as historical records; make a new dated record for corrections rather than silently rewriting the audit trail.

## 4. Incoming CE acceptance report

The report must answer every item required by canonical Protocol §8:

- **BASELINE ACCEPTED:** full commit, branch, and worktree/WIP disposition;
- **PROJECT QUESTION:** concise reconstruction with governing source;
- **ESTABLISHED CLAIMS:** scoped claims and evidence sources;
- **NON-CLAIMS:** limits that constrain current interpretation;
- **REDUCTIONS / FAILURES:** closed, falsified, or abandoned directions;
- **CURRENT PI DIRECTION:** source and its status;
- **WIP:** accepted, pending, excluded, and unclassified items;
- **CONTRADICTIONS / GAPS:** items accepted, disputed, or escalated;
- **INDEPENDENT DIAGNOSIS:** agreement and disagreement with outgoing interpretations, with reasons and evidence;
- **FIRST RECOMMENDED ACTION:** one concrete, bounded action; and
- **ESCALATIONS TO PI:** only decisions that cannot safely be made within CE authority.

A disagreement is not itself a failure to accept the role. It must identify the evidence, assumption, dependency, theorem-level argument, or external result that motivates reopening any frozen direction. Until the PI accepts the transition, status remains **PENDING** and the outgoing CE remains **OUTGOING** or **ACTIVE** as specified by the current register/protocol.

## 5. Stop conditions

Stop the transfer and escalate to the PI when:

- explicit PI authorization or the incoming identity is absent;
- disposition of an earlier pending CE handover is unresolved;
- HEAD, branch, or material WIP cannot be reliably classified;
- a scientific decision exists only in chat or an untraceable summary;
- sources materially conflict on authority, frozen design, or result status;
- experimental processes or data integrity make the baseline uncertain;
- proposed acceptance requires silently promoting WIP, changing a result, or overriding canonical evidence.

A stop preserves current roles and register states. It is not scientific closure and does not authorize additional experiments.

## 6. Bootstrap prompt for an incoming CE

> You are the incoming HLS Chief Engineer, pending acceptance. Follow
> 'docs/team/HLS_TEAM_HANDOVER_PROTOCOL.md' §8 and
> 'docs/team/CE_HANDOVER_EXECUTION_PROTOCOL.md'. Use the linked dated
> handover, 'HLS_ROLE_REGISTER.md', its stated commit/branch, and the
> repository authority map as sources. Independently audit the baseline and
> classify WIP. Do not run experiments, alter frozen results, or assume
> authority beyond the CE role. Return the required acceptance report,
> including disagreements, contradictions, one bounded first action, and
> necessary PI escalations. Do not activate or update the role register; the
> PI disposition and steward process complete the transition.

## 7. Completion record

For each replacement, the dated handover record must include:

    PI authorization:
    Outgoing CE / incoming CE:
    Baseline commit / branch:
    Worktree and WIP classification:
    Outgoing transfer received:
    Incoming acceptance report:
    Unresolved items and escalation owner:
    PI disposition:
    Role-register update commit:
    Final status:

This supplement remains subordinate to the canonical Team Handover Protocol. If they conflict, stop and follow the canonical protocol while escalating the conflict for governance review.

