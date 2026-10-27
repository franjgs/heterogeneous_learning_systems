# Protocol readiness and reproducibility

## Current status

Protocol development has **not** begun beyond this preparation checklist. No simulator, algorithm, training method, data collection, model inference, pilot or experiment is implemented or executed. No confirmatory hypothesis or estimand is frozen.

## Decisions needed before a protocol can be frozen

1. Identify the target SOC setting and obtain permission to describe/model it; distinguish real workflow facts from scenario assumptions.
2. Define L1/L2 task instances, decision order, labels, escalation/report consequences, ground truth and adjudication.
3. Decide the population and unit of analysis: analysts, alerts, incidents, client-periods or another defensible unit; account for repeated observations and clustering.
4. Operationalize competence with validated measures or outcome-linked estimates; track experience separately. Specify uncertainty, label noise and calibration.
5. Specify workload, service time, availability, shifts, queues, deadlines/SLA, capacity, interruptions, handoffs and resource units.
6. Define training intervention, mentor involvement, time/cash cost, displaced work, expected persistence, transfer and a suitable no-training or alternative-training comparator.
7. Define AI assistance: system/version, information access, recommendations, human authority, reliance/override, failure modes, exposure and cost.
8. Separate fixed organization, assignment policy, training and AI effects before testing interactions; choose strong current-practice and literature-based comparators.
9. Define individual and collective estimands, costs, uncertainty analysis, practical thresholds, stopping rules and sensitivity analyses before confirmatory test data are inspected.
10. Resolve privacy, cybersecurity, contractual, employment, ethics-review, data-protection, retention and publication permissions.

## Candidate staged evaluation (not an approved experimental protocol)

If the PI later approves scientific execution, a defensible sequence could first characterize task/competence distributions and operational constraints; then test assignment under matched workload without training/AI changes; then evaluate a training intervention with opportunity cost; and only after isolated effects are understood test interactions with AI assistance or context shifts. This ordering is a methodological suggestion, not an authorized campaign or a frozen design. Real data, simulation, replay or controlled human study must be selected based on evidence and feasibility.

Potential baselines include documented current practice, a strong fixed assignment rule, a dynamic rule under the same information constraints, and simple non-AI/AI-assisted alternatives. An oracle using future truth or latent competence is an unattainable upper reference, not an implementable policy. No baseline is selected here.

## Reproducibility and evidence records

For every future study version, retain (or securely reference under approved access control):

- immutable protocol/version and decision date;
- source commit, dirty-tree status, software/dependency and model versions;
- configuration, seeds/random-stream policy and execution command;
- data provenance, license/consent/contract, inclusion and exclusion rules, de-identification process, data hash and access location;
- task/label/competence definitions, outcome adjudication and missing-data handling;
- all baseline/control settings, human and AI procedures, costs and units;
- outputs at the independent unit, analysis code, statistical procedures, uncertainty and deviations;
- manifest linking question → model → scenario → organization/policy → evaluation → experiment → result → conclusion.

Do not commit SOC alerts, customer identifiers, secrets, personal data, proprietary analyst profiles or restricted model prompts. Store only an approved public derivative or a non-sensitive manifest when raw evidence cannot be released. Report data restrictions honestly; a hash is a provenance check, not a substitute for access to evidence.

For an eventual *Electronics* submission, prepare a Data Availability Statement even if data are restricted or no new data were generated. State what can be shared, where, under what license/access procedure, and what cannot be shared with the legal/privacy reason. Provide code and full method details proportionate to replication. Report all prespecified controls and negative/null findings; do not tune confirmatory choices on test outcomes.

## Freeze and authorization boundary

No experiment proceeds until the PI reviews and explicitly approves a complete protocol and the applicable ethics/data permissions are confirmed. This project-start task authorizes organization and documentation only.
