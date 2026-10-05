# HLS Team Handover Protocol

**Status:** CANONICAL governance procedure for role transfer and continuity.

## 1. Purpose and governing principle

This protocol governs **ADD EXPERT**, **REPLACE EXPERT**, **FREEZE / REMOVE
EXPERT**, and **REPLACE CHIEF ENGINEER** operations. It does not establish a
scientific claim, change scientific authority, or replace the repository's
scientific sources.

> Repository sources carry project knowledge; handovers transfer
> role-specific responsibility; chats are not authoritative project state.

Every operation uses a compact, source-referenced handover under
[`handovers/`](handovers/), based on
[`HANDOVER_TEMPLATE.md`](HANDOVER_TEMPLATE.md), and updates the operational
[`HLS_ROLE_REGISTER.md`](HLS_ROLE_REGISTER.md). Do not duplicate complete
scientific documents in a handover.

## 2. Roles and authority

| Role | Authority and responsibility | May not do |
| --- | --- | --- |
| **PI** | Owns scientific doctrine and ultimate strategic authority; authorizes major direction changes and may reopen frozen directions. | Be silently overridden by another role. |
| **Chief Engineer (CE)** | Coordinates scientific architecture and theory → experiment → evidence → paper traceability; integrates specialist work; enforces PI doctrine and repository authority; may stop work that violates reductions or scope. | Silently override PI doctrine or established evidence. |
| **Expert / Beam Owner** | Investigates an explicitly scoped problem; reports reductions, failures, and contradictions as well as positive results; escalates scope changes. | Own global doctrine or unrelated architecture. |
| **Handover Steward** | Retrieves and checks repository sources; prepares handovers; checks Git baseline and WIP; identifies contradictions or missing information; records transfer and acceptance. Normally an operational tooling role such as Codex. | Decide claims, resolve scientific contradictions, alter PI doctrine, promote WIP, reinterpret falsifications, or reopen frozen decisions. |

## 3. Source authority and status discipline

Handovers reconstruct the project from repository sources, never from chat
summaries alone. Apply the authority relationships in
[`../REPOSITORY_GUIDE.md`](../REPOSITORY_GUIDE.md), and distinguish the
following labels in the handover:

- **CANONICAL ESTABLISHED**
- **CONSOLIDATED / SCOPED**
- **VERIFIED BUT NON-CANONICAL**
- **PROTOCOL / SUPPORTING**
- **HISTORICAL**
- **HYPOTHESIS / INTERPRETATION**
- **FALSIFIED / ABANDONED**
- **WIP**

Literature records and publication drafts are not automatically authoritative
for system state. Chat content becomes authoritative only when its decision is
materialized in a repository source with the appropriate authority.

## 4. Universal handover baseline

Every handover must record:

1. exact Git `HEAD` commit and branch;
2. `git status --short` and a classification of all relevant WIP;
3. canonical sources consulted;
4. known contradictions or documentation gaps;
5. outgoing responsibility state, where applicable; and
6. incoming acceptance state.

If a mission, authority, baseline, WIP classification, frozen decision, or
canonical interpretation is materially missing or contradictory, **STOP AND
ESCALATE**. The steward must not infer a scientific decision merely to finish
a handover.

## 5. ADD EXPERT

### Preconditions

The PI or CE authorizes the role, mission, scope, interfaces, expected
artifact, and stopping/escalation conditions.

### Preparation and package

The steward identifies the Git baseline, classifies WIP, retrieves global
doctrine and current state, and selects the role-specific canonical sources.
The package states mission, authority, established results, non-claims,
reductions/falsifications, frozen decisions, open questions, interfaces,
current task, and required reading.

### Incoming confirmation and activation

The incoming member confirms that it has read the sources; understands its
mission, authority, non-claims, and frozen decisions; accepts the baseline and
WIP classification; and reports ambiguities. Only then does the role become
**ACTIVE** in the role register.

## 6. REPLACE EXPERT

Use the ADD EXPERT procedure plus an outgoing transfer containing work
performed, task state, decisions, artifacts, unresolved questions,
dependencies, failed approaches, unvalidated hypotheses, and blockers. The
steward compares that report with repository sources and reports divergence;
it must not reconcile divergence silently. The incoming expert inherits the
role's scope, not the outgoing expert's personal interpretation.

## 7. FREEZE / REMOVE EXPERT

The CE first confirms whether scientific work remains dependent on the role.
Record the final baseline, unfinished tasks, reproduction/data/artifact
dependencies, and unresolved questions. Identify a successor or mark the role
**VACANT** or **FROZEN**. A role's disappearance never constitutes scientific
closure.

## 8. REPLACE CHIEF ENGINEER

This is the strongest handover and requires PI authorization.

### Preconditions

- Validate the explicit baseline commit and branch.
- Classify the working tree as accepted/committed, pending decision, excluded,
  or abandoned.
- Confirm the outgoing CE's responsibility state and the incoming CE's
  pending status in the role register.

### Outgoing CE package

Using the template, provide the project question; PI doctrine; authority and
source map; established claims and non-claims; falsified/abandoned directions;
frozen decisions; active hypotheses; current direction; active roles and
interfaces; experimental/programmatic and relevant publication state;
documentary debt; contradictions; immediate task; and recommendations clearly
labelled as recommendations.

The required reconstruction reading order is: programme philosophy; doctrine;
ontology; research questions; current state; repository guide; theory registry
and Beam 1 / Beam 2 sources; ground truths; MIS and information audits;
integration/RQ0 material; history; relevant current experiments/protocols;
then literature or publication drafts only as needed. Follow current links in
the guide rather than hard-coding obsolete paths.

### Incoming CE independence and acceptance

The incoming CE may independently challenge interpretations, priorities,
architectural choices, recommendations, and hypotheses. It may not silently
ignore canonical evidence, falsified results, PI doctrine, explicit PI
decisions, or documented reductions. Reopening a frozen direction requires a
stated new evidence, assumption, dependency, theorem-level argument, or
external result.

Before acceptance, the incoming CE returns a written report containing:

- **BASELINE ACCEPTED:** commit and branch;
- **PROJECT QUESTION:** its concise reconstruction;
- **ESTABLISHED CLAIMS** and **NON-CLAIMS**;
- **REDUCTIONS / FAILURES** not to rediscover silently;
- **CURRENT PI DIRECTION**;
- **WIP** classification;
- **CONTRADICTIONS / GAPS**;
- **INDEPENDENT DIAGNOSIS:** agreements and disagreements with outgoing
  interpretation;
- **FIRST RECOMMENDED ACTION:** one concrete action; and
- **ESCALATIONS TO PI:** only genuinely necessary decisions.

Until that report is accepted according to this protocol, the outgoing CE is
**ACTIVE** or **OUTGOING** and the incoming CE is **PENDING**. After
acceptance, update them to **REPLACED** and **ACTIVE**, respectively.

## 9. Handover-steward stop conditions

The steward stops and escalates to the CE or PI when applicable if:

- mission or authority is missing or ambiguous;
- Git baseline is unknown;
- WIP cannot be classified;
- canonical sources conflict materially;
- frozen decisions are unclear;
- an incoming member challenges canonical evidence without identifying a new
  basis;
- an outgoing interpretation is being promoted to fact; or
- a required decision exists only in chat and was not materialized.

For a CE replacement, unresolved scientific or governance authority issues go
to the PI.

## 10. Bootstrap prompt principle

The initiating prompt for a new member must be short. It specifies the role,
handover path, baseline, required reconstruction, independence requirement,
and first acceptance report. It must not duplicate the project: the repository
and handover are the sources of truth.

## 11. Completion and maintenance

The steward records the final handover status and updates the role register
only after the required confirmation. Keep old accepted handovers as a
historical transfer record. Update this protocol only for governance changes;
scientific status belongs in the established scientific sources.
