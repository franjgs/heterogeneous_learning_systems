# SOC expert input delta

This note records qualitative guidance from a professional with SOC experience. It is not an operational measurement, is not necessarily representative of GMV-CERT, and must not be attributed as a GMV-CERT schedule, SLA, service time, procedure, policy, or assignment mechanism. SOCTRA empirical classifier results remain a separate evidence stream; the guidance informs only plausible configurable synthetic scenarios.

## A. Capabilities already present

The previous simulator already had L1→L2 routing, independent L1 and shared L2 queues, severity/task classes, arrival-relative deadlines, heterogeneous analyst eligibility/competence/service, D1/P1/WAPS dispatch, an alpha control for FP service, hidden need in the environment, and paired synthetic SOCTRA recommendation traces. Escalation in the integrated evidence engine was modeled as a fixed routing decision; return to L1 was not modeled.

## B. Capabilities added in this branch

The isolated availability engine now accepts weekly per-analyst calendars, configurable weekdays, overnight intervals, and uniform temporal scaling. Assigned work keeps its analyst and remaining service across duty closures; it resumes before any fresh queue dispatch. Effective service segments and completed work are returned separately from elapsed calendar time. A helper allows explicit deadlines independent of severity while retaining severity→deadline maps when desired.

## C. Conceptual clarifications

- Rapid and delayed escalation are possible scenario distinctions; L1 service can instead represent aggregate pre-escalation analysis. This phase does not implement a speed-based escalation rule.
- L1 and L2 can have different effective work requirements. Unnecessary escalations may plausibly require less work; alpha remains a synthetic sensitivity parameter, not measured effort.
- Analyst availability may differ by level and person. Calendars encode that availability without geographic assumptions.
- An investigation may pause at unavailability and resume with retained work. The current explicit assumption is same-analyst ownership across suspension.
- Service objectives may be expressed over hours or days. Deadline is conceptually independent from technical severity, though a configurable mapping is supported.
- L2 specialists share a queue in the abstracted model. Different task-selection rules are plausible, but this work retains D1/P1/WAPS unchanged.
- Escalation and client reporting are separate decisions; reporting is outside the present flow.

## D. Deliberate exclusions

No rapid/late escalation logic, client reporting, reassignment, voluntary interruption, external-information wait, new priority policy, or SOCTRA decision change is introduced. No CVSS calculation or new alert feature is introduced. No claim of reproducing a real SOC is made.

## E. Open uncertainties

Actual duty rosters, holiday coverage, handoff practice, service distributions, deadline targets, escalation timing, false-alarm verification effort, priority rules, and reporting procedures are unknown. Calendars omit holidays, leave, and absences. Therefore results are conditional synthetic scenario analyses, not estimates of a named SOC's operations.
