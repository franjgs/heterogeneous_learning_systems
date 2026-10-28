# Empirical alert-demand characterization and HLS sizing proposal

**Prepared:** 2026-10-28
**Status:** Local, aggregate-only characterization for PI review. Not cleared for external distribution.
**Branch:** `research/soc-human-ai-organization`
**Scope:** Read-only analysis of the locally supplied SOCTRA/GMV-CERT CSV snapshots. Per the PI's clarification received 2026-10-28, SOCTRA demonstrated reduced alert-triage burden. This characterization does not reproduce that result or quantify it in analyst-hours. No CSV, row, alert/project/analyst identifier, category value, or model output was copied into the repository. No simulator or experiment was run.

## 1. Source inventory and selection

The supplied path ended at `dataset_2025`, which was not a directory on the mounted volume. The seven CSV files were present one level above, under the supplied `.../data/interim/raw/` location. They are successive cumulative snapshots, not disjoint monthly partitions. Their alert-ID sets are nested in snapshot order; adding their row counts would count prior alerts repeatedly. The September snapshot and `dataset_20250919.csv` have identical file hashes and contents.

| Local snapshot label | Rows / distinct alert IDs | Timestamp coverage end | Columns |
|---|---:|---|---:|
| `dataset_2025_enero.csv` | 161,037 | 2024-12-31 | 41 |
| `dataset_2025_febrero.csv` | 170,653 | 2025-02-28 | 45 |
| `dataset_2025_marzo.csv` | 176,913 | 2025-03-31 | 45 |
| `dataset_2025_abril.csv` | 182,391 | 2025-04-30 | 45 |
| `dataset_2025_julio.csv` | 196,335 | 2025-07-14 | 45 |
| `dataset_2025_septiembre.csv` | 214,739 | 2025-09-18 | 45 |
| `dataset_20250919.csv` | 214,739 | 2025-09-18 | 45 |

The 19 September 2025 dated snapshot is selected for the aggregates below because it is the latest supplied version and contains 214,739 unique, non-missing `id_alerta` values. The reported AIAI source-pool size (170,653) matches the row count of the February snapshot, but exact lineage between that snapshot and the published paper's source pool has not been verified. The paper's filtered analytical sample (63,410) is a different population and must not be substituted for this demand characterization.

The final schema has 45 fields covering timestamp and alert identifiers; project, handler and service-mode labels; severity/closure and escalation/reporting labels; alert/use-case/source descriptors; event/assignment counters; network/URL/user-related fields; classifier outputs; and derived weights. The January schema has 41 columns and lacks four later-added fields. Several columns can contain sensitive or identifying content; none is reproduced here.

## 2. Method and quality controls

- Read the latest snapshot once, using the standard CSV comma/quote convention. Automatic dialect sniffing incorrectly flagged 27 records as having extra fields because it inferred nonstandard double-quote handling; the standard reader parsed all 214,739 records with the declared 45-column schema and no extra-field rows.
- Confirmed: every row in the selected snapshot has a distinct, non-empty alert identifier; the two September files are byte-identical; and every earlier snapshot's alert-ID set is contained in the latest snapshot.
- Timestamps are parseable but timezone-naive. Calendar summaries below use the literal timestamp dates; they are not represented as UTC or local time. Time-of-day/shift interpretations require GMV-CERT to confirm timezone and timestamp semantics.
- The data span 993 calendar dates, from 2022-12-31 through 2025-09-18. All 993 date bins contain at least one row. Edge periods are incomplete: the first and last dates, first and last ISO weeks, and December 2022/September 2025 are excluded from “complete-period” rate summaries.
- This directory is named `raw`, but the CSV includes derived/model-oriented fields and should not be treated as an unprocessed event log without a data dictionary.
- No raw values or project/category labels were printed into the report. Project and category distributions are reported only as aggregates. These aggregates still require disclosure approval before publication or transfer outside the authorized team.

## 3. Demand volume and variability

The unit counted is a row with a unique alert identifier. This is a count of alert records, not a count of analyst actions, minutes of work, or necessarily underlying security events.

| Period unit | Complete bins | Mean | Median | SD | CV | 95th percentile | 99th percentile | Maximum |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| Day, excluding two edge dates | 991 | 216.1 | 211 | 89.0 | 0.412 | 379 | 442 | 529 |
| ISO week, excluding two edge weeks | 141 | 1,504.0 | 1,514 | 352.7 | 0.235 | 2,102 | 2,439 | 2,444 |
| Month, excluding two partial edge months | 32 | 6,514.4 | 6,894.5 | 1,194.6 | 0.183 | 8,110 | 8,463 | 8,463 |

These statistics show substantial day-to-day variation and lower relative variation at coarser aggregation. They are descriptive rates for this historical portfolio and extraction, not forecasts, staffing requirements, or independent replications. The top observed daily count over all dates was 574; the complete-day maximum is lower (529). Do not use the partial-edge maximum as a typical peak.

## 4. Project and technology heterogeneity

There are 27 non-empty project labels in the latest snapshot. Project volumes are concentrated: the largest project label contributes 17.89% of rows; the top five contribute 59.23%; the top ten 82.83%; project-count Gini is 0.603. Among the 32 complete months, the number of project labels present ranges from 16 to 23, with median 21. The 27 labels describe this historical extract, not necessarily the current or target SOC portfolio. No project names or project-level counts are disclosed here.

Potential technology/use-case descriptors have high observed cardinality: 551 distinct non-empty `use_case_name` values (5,002 missing), 590 `use_case_id` values (107 missing), 30,560 `alert_name` values (107 missing), and 174 `fuente` values (1,191 missing). The top ten categories account for 25.82% of use-case-name values, 25.50% of use-case IDs, 10.85% of alert-name values, and 61.51% of source values. These fields establish descriptive diversity in the extract, but their taxonomic meaning is unverified: names may be rule/use-case labels rather than technologies, name-to-ID mapping is incomplete, and no controlled technology taxonomy is available. Therefore no technology-family composition is asserted. A technology-stratified scenario requires a reviewed mapping from GMV-CERT.

The project portfolio is uneven, and project labels alone do not establish project size, client workload, coverage hours, severity mix, or operational importance. A single mean arrival rate would erase both portfolio concentration and temporal variation.

## 5. Escalation and reporting labels

In the latest snapshot, `escalada_L2` is true for 636/214,739 records (0.296%); `reportado` is true for 44,354/214,739 (20.65%). Both fields are populated for all selected rows. These are historical process labels in this extract. They are not independently adjudicated threat ground truth, classifier performance, error rates, or measures of analyst effort. The two decisions need not be mutually exclusive. Their operational definitions, denominators, treatment of duplicates and relationship to the published AIAI target construction must be confirmed before modeling.

## 6. Alert records versus human activity

Evidence that these rows are alert-oriented: every selected row has its own unique `id_alerta`, a timestamp, alert/use-case descriptors, and categorical triage outcomes. However, `numero_eventos` and alert counters suggest that a record may summarize multiple lower-level events; their exact semantics are not documented in the supplied data dictionary (none was found with this data bundle).

The schema also contains a handler field (`tramitador`), an assignment-count field, service-mode labels and model-derived fields. These are attributes or aggregates attached to alert records; they do not make each CSV row a human work episode. The sparse `id_nuntiare` field is not a complete action log. The data do not provide validated analyst start/finish times, service durations, queue waiting, handoffs, training episodes, mentor time, or an auditable sequence of human decisions. Alert rows therefore cannot be converted into labor hours or capacity released. See the [analyst identifier, experience and workload audit](ANALYST_EXPERIENCE_AUDIT.md) for the field-level and code-level assessment.

## 7. HLS reference-scenario proposal

Use the latest snapshot as an **empirical demand trace**, subject to GMV-CERT authorization and validation. Preserve event timestamps and project grouping in a restricted local data adapter; do not place identifiers or records in Git. For privacy-safe simulation/publication, generate a synthetic or pseudonymized derivative only after data-owner review. Do not fit a stationary Poisson process merely for convenience: the empirical trace is nonstationary/variable and can support replay or calibrated resampling. Any stochastic arrival model should be compared against replay and must preserve observed temporal and project-level variation.

| Scenario quantity | Proposed reference representation | Status |
|---|---|---|
| Demand arrivals | Latest-snapshot trace: 214,739 alert records over 993 dates; project-conditioned empirical trace is preferred. | Measured in extract; timestamp meaning/timezone still needs validation. |
| Project portfolio | Parameter `K_project`; observed portfolio has 27 labels. Reference replay may use all observed labels without revealing them. | 27 measured labels in extract; target/current representativeness unverified. |
| Arrival intensity and peaks | Replay timestamps or derive rates at daily/weekly/monthly levels, with edge-period handling stated. | Derived from measured trace; not a forecast. |
| L1/L2 workforce | Separate parameters `N_L1`, `N_L2`; allow staffing and role mix to vary by scenario. | Unknown; must not infer from alert volume. |
| Shift availability | Per-role/project availability calendar, including absences and reserve capacity. | Unknown; request validated schedules and timezone. |
| Processing/service times | Distributions by task class, severity/context and role, with censoring and waiting separated. | Unknown; not inferable from alert count or prediction latency. |
| Competence | Latent or measured task-specific competence with uncertainty; distinguish experience, expertise proxies and observed outcomes. | No validated individual competence data in this extract. |
| AI/tool effect | Separate tool accuracy/operating point from operational change in alerts requiring human work, time and rework. | SOCTRA's reduced triage burden is a demonstrated project finding per PI clarification; this dataset analysis does not quantify released analyst-hours/capacity. Any numeric capacity release assigned in simulation is a separate hypothetical parameter. |
| Organization/policy | Assignment, specialization/polivalence, training, mentoring, and reallocation of available capacity. | Experimental variables; no strategy is presumed superior. |
| Costs and constraints | Analyst/mentor opportunity time, training/tool cost, SLA/deadlines, queue limits, missed-threat/false-escalation consequences and service reserve. | Values and trade-offs require operational/economic definitions. |

Suggested reference scale is thus **the observed historical demand stream and up to 27 project labels, with workforce, L1/L2 split, availability, service-time distributions and competencies left as explicit parameters**. It is not a fixed analyst headcount. For experiments, project count and mix can be parameterized around the observed portfolio, while test cases should include both portfolio-weighted and project-stratified views to avoid letting the largest clients silently define all conclusions. This is a proposal for PI review, not a frozen model or protocol.

## 8. Classification of quantities

**A. Measured:** row counts in each snapshot; unique alert IDs; timestamps as stored; project/use-case/source labels and missingness; `escalada_L2` and `reportado` values. These are measured properties of the supplied extract only.

**B. Derived:** daily, weekly and monthly volumes; period variability/peaks; project shares/concentration; category cardinalities/concentration; escalation/report proportions.

**C. Assumptions pending validation:** timezone; whether one alert row is one service task; how `numero_eventos` relates to grouped alert records; what constitutes L1/L2 start/end; current portfolio representativeness; staffing, shifts, availability, processing times, queue/SLA behavior, competence, training effects, numerical capacity-release rate for simulation and monetary costs. The existence of a SOCTRA triage-burden reduction is treated as a demonstrated project finding per PI clarification; its quantitative conversion to labor/capacity is not established by this extract.

**D. Experimental variables:** workforce size and L1/L2 allocation; project mix; scheduling and reserve; fixed/dynamic assignment and specialization; training/mentoring intensity; AI-assisted triage exposure and operating point; capacity reallocation; scenario shifts; cost weights. None has been set or tested here.

## 9. Information to request from GMV-CERT

1. Authoritative snapshot/version lineage, extraction rules, timezone, date semantics, inclusion/exclusion and whether later files overwrite labels or features in earlier snapshots.
2. Data dictionary for every field, especially alert identity, grouped-event counters, `id_nuntiare`, handler, assignment counters, severity/closure, escalation/reporting, duplicates and SLA violations.
3. Approved, de-identified project/client mapping and a stable technology/use-case taxonomy; clarify which categories can be shared and for which periods.
4. L1/L2 workflow map: decision authority, task boundaries, handoffs, escalation criteria, service windows, rework and closure criteria.
5. Historical staffing by role/project/shift, scheduled and actual availability, leave/on-call/reserve, concurrent-work limits and changes over time.
6. Event-level timestamps for arrival, assignment, acknowledgement, work start/stop, handoff and closure; distinguish human service time from elapsed wait and automated processing.
7. Outcome/label provenance and adjudication; definitions for `escalada_L2` and `reportado`; treatment of disagreement, duplicates, cancelled work and later corrections.
8. Deployment/change log for triage tools: exposure periods, alerts routed/filtered, human overrides, false-positive handling, rework and before/after workload measurements. Quantify released analyst time only if a valid measurement exists.
9. Training/mentoring records, competence assessment method, task-specific outcome linkage and access permissions, if those are intended study variables.
10. Contractual, privacy, security, employment/ethics, retention and publication constraints for aggregates, derived data, code and model outputs.

## 10. Reuse candidates for HLS core

Potential candidates, not transferred components: (i) a privacy-safe temporal/project-conditioned demand scenario, (ii) empirical demand-variation summaries, (iii) explicit separation of alert records from human work episodes, (iv) deadline/queue evaluation measures once service data exist, and (v) evidence discipline separating competence proxies, competence, classifier output and collective performance. Each requires a semantic-compatibility and disclosure review before core incorporation. No SOC-specific values or findings are generalized to HLS.

## 11. Limitations and representativeness risks

- One operational setting and historical extraction; the target population, censoring and extraction changes are incompletely specified.
- Snapshot names conceal cumulative exports; pooling them produces severe double counting. The final two files are exact duplicates.
- Schema evolved from 41 to 45 fields; derived/model fields are mixed with operational descriptors.
- Timezone is absent, so shift/hour-of-day patterns cannot yet be mapped to local operations.
- Project counts are concentrated; project labels are not a validated sampling frame, and 27 observed labels may not represent current SOC clients.
- Use-case/source labels are high-cardinality but not a verified technology taxonomy.
- Escalation/report fields are observed process labels, not independently verified quality outcomes.
- No analyst roster, service duration, queue waiting, occupancy, training, mentor, cost or validated competence measures are present in the inspected CSV schema.
- The observed time series is historical; client onboarding, threat shifts, policy changes and system changes may induce drift.
- Aggregate statistics remain sensitive business information; disclosure approval is required before pushing or publication.

## 12. Chronology

- **2026-10-28:** PI requested empirical demand characterization and HLS scenario sizing using the local SOCTRA/GMV-CERT data. The supplied terminal path lacked the final `dataset_2025` directory level; seven CSV snapshots were found in its parent `raw` directory.
- **2026-10-28:** Read-only inventory established cumulative snapshot structure, exact duplicate September exports, schema evolution, and the latest-snapshot coverage. Aggregates were calculated from the latest snapshot only; no raw data were copied. No simulator, model training, or experiment was run.
- **Pending:** GMV-CERT validation of data semantics, workload/capacity measurements, disclosure permissions and PI approval of the scenario scale and assumptions.

## 13. Reproducibility note

Analysis used Python's standard `csv`, `datetime`, `hashlib` and `statistics` modules, the standard CSV quoting convention, and the single latest snapshot. Period CV is population SD divided by mean. Quantiles use nearest-rank empirical quantiles. Project Gini is calculated over project alert counts. Missing category values are excluded from category-cardinality distributions. No input file, identifier, category value, output dataset, chart or execution artifact was written into the repository. Because the source remains local and restricted, another authorized analyst must rerun the aggregation against the same approved snapshot to independently reproduce the tables.

## Disposition at documentation closure

At 2026-10-28 20:32:49 CET (+0100), the PI explicitly authorized committing and pushing this aggregate-only report as part of the SOC study documentation. This authorization covers the report in this repository and its draft review PR; it does not authorize inclusion of source CSVs, row-level records, client/project labels or identifiers, nor establish permission for reuse in a manuscript or other distribution. Data-owner and publication permissions remain to be confirmed where applicable.
