# Scenario, model boundary and organization candidates

## Provenance classes

| Class | Current content | Status |
|---|---|---|
| Scenario specification received 2026-10-27 | Multi-client SOC context; heterogeneous human cyberanalysts; L1 initial triage with escalate/report decisions; L2 deeper analysis; possible new clients, technologies and threats. | Stated scope for a proposed testbed, not independently verified operational facts. |
| Historical HLS evidence | Synthetic finite allocation, competence-development, deadline-queue and matched-competence-structure results. | Scoped to their own models; not calibrated SOC evidence. |
| External empirical context | Other studies report analyst/process variation and SOC alert-data characteristics. | Setting-specific prior work; not a substitute for data from the intended client. |
| Future modeling assumptions | Arrival laws, label quality, severity, service times, competence measures, deadlines, costs, AI effect and learning transitions. | Unspecified; must be sourced, elicited or declared before a model is frozen. |

No real client, SOC procedure, analyst profile, service rate, SLA, competence distribution or outcome label is asserted here.

## Process representation

### L1 — initial alert triage

Represent two decisions associated with an alert: **escalate or not** and **report or not**. Whether these choices are ordered, conditional, simultaneous or made by the same role is unknown. The testbed must not assume a real escalation path from the labels alone.

### L2 — deep alert analysis

Represent deeper investigation for alerts requiring it. Entry criteria, investigative actions, evidence available, stopping rules, reporting outputs, handoff and responsibility boundaries remain unspecified.

L1 and L2 may be separate task classes or stages in a workflow. That modeling choice must follow validated process evidence; the two representations are not interchangeable by default.

## Candidate model shell (not selected or implemented)

For a future model, let (i\in\mathcal A) index analysts; (x\in\mathcal X) alert/work item; (k\in\mathcal K) task class; (c\in\mathcal C) client context; (v\in\mathcal V) technology/threat context; and (t) time. A candidate competence quantity could be

\[
q_i(x\mid s_t,c,v)=P(\text{declared correct outcome}\mid i,x,s_t,c,v),
\]

only if the outcome, population, information and calibration support a probabilistic interpretation. This is not a core SOC parameter and no values are available. A capability is instead the outcomes attainable under an organization, policy, information, resources and constraints; neither is identical to observed task success.

A future organization (o) would specify staffing, roles, access, capacity, shift/availability and coordination constraints. A policy \(\pi\) would map information actually available at decision time to assignments, escalation/report choices, training choices, or use of AI assistance. Organization and policy must remain distinct.

Possible state coordinates include workload, work-in-progress, observed outcomes, competence beliefs and context. A learning transition from experience/training to competence is unknown and must be estimated or represented as explicit scenario assumptions. Changes to assignment rules are adaptation; they do not by themselves demonstrate competence learning.

## Organization and policy candidates

These are comparison families to consider after the baseline workflow is validated, not approved algorithms:

- observed/current-practice baseline, if it can be documented;
- fixed assignment or specialization;
- dynamic assignment using permissible competence and workload information;
- training-aware assignment accounting for trainee and mentor opportunity cost;
- human–AI assistance with an explicit human role, AI output, reliance/override and accountability contract.

Each candidate requires competitive baselines. An oracle with true future competence, labels or outcomes must be reported only as an unattainable reference, never as an implementable policy.

## Constraints and objective dimensions

Potential constraints include analyst availability, simultaneous work, queue/work-in-progress limits, time-to-triage, investigation deadlines, contractual SLA, escalation authority, client-specific access, tool availability, privacy/security controls, and operational reserve capacity. Their actual presence and values are unknown.

Do not collapse these outcomes without an explicit value model:

- individual investigation quality and decision accuracy;
- collective correct resolution, missed threats, false escalation/reporting, and time-to-action;
- latency, backlog, SLA attainment and resilience after context shifts;
- analyst and mentor time, training spend, displaced service, AI/tool cost;
- workload distribution and analyst well-being, if measured validly.

Cost of opportunity must account for analyst/mentor time removed from operational capacity; it is not zero merely because payroll is fixed. Monetary conversion and competing objectives require PI-approved assumptions or a multi-objective evaluation.

## Model contract still required

Before protocol freeze, specify the system boundary; alert/task taxonomy; client/context population; evidence and ground truth; competence operationalization; arrival and service process; queue/shift/handoff rules; deadlines and loss consequences; training/experience transitions; mentor capacity; AI assistance and failure modes; available information; resource units; policies and baselines; estimands; and privacy, ethics and data-access constraints. No parameters are chosen in this document.
