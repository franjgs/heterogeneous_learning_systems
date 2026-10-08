# Future Paper Source Map

This is a traceability map, not a manuscript draft.  The consolidated model
authority is `docs/theory/HLS_FOUNDATION_SPECIFICATION.md`; executable code and
machine-readable artifacts remain authoritative for equations and numerical
claims.

| Provisional section | Authoritative documents | Executable sources | Validated artifacts | Currently supportable | Deferred / unsupported |
|---|---|---|---|---|---|
| Introduction / research question | `HLS_PHILOSOPHY.md`; foundation specification | none | none | conditional study of capability geometry x problem dynamics | impact, prevalence, superiority |
| Related work | `docs/literature/README.md`; `references.bib`; `LITERATURE_NEEDS.md` | none | retained source inventory | only already audited scoped antecedents | synthesis pending targeted review |
| Model | foundation specification; `HLS_CAPABILITY_DEVELOPMENT.md` | `discover_v0.py`; `discover_develop_v2.py`; `finite_problem_belief.py` | finite-belief and MIS-v2 controls | exact current state/action/transition model | empirical realism/calibration |
| Problem space and geometry | `PROBLEM_DISTANCE_GATE.md`; foundation specification | `problem_geometry.py` | problem-distance grid and summary | `Z=Delta^1`, metric and closed form under fixed physics | empirical task-distance validity |
| Agent representation and DISCOVER | `FINITE_PROBLEM_BELIEF_GATE.md` | `finite_problem_belief.py`; historical `discover_v0.py` | finite-belief summary/trajectories | finite beliefs, world/model separation, M=2 recovery | novelty recognition, continuous inference |
| Capability development | `HLS_CAPABILITY_DEVELOPMENT.md` | `discover_develop_v2.py` | MIS-v2 gate artifacts | declared exponential gap transition and properties | calibrated learning law |
| Experimental design | `SMALL_PROBLEM_WORLD_GATE.md`; Campaign 0/1 documents; `POLICY_ABLATION_SPECIFICATION.md`; `CAMPAIGN_2_THEORETICAL_SPECIFICATION.md`; `CAMPAIGN_2_PREREGISTRATION.md` | frozen world and Campaign 0–2 runners | frozen world/test-range/protocol/theory manifests | Campaign 2's prospective-policy comparison was preregistered before seeds 10–49 | no Campaign 3 design or broader strategy family |
| Results | Campaign 0/1 results; `CAMPAIGN_2_RESULTS.md`; `CAMPAIGN_2_IO_INCIDENT.md` | Campaign 0–2 runners, validators, and analyses | Campaign 2 raw/reference/counterfactual tables, bootstrap outputs, provenance, and retained failure record | Campaign 2 H1/H2/H3 support; robust positive conditional Q10/Q11 benefit; Q01 null; negative returns and secondary G07 replication | no Q11-over-Q10 superiority, universal team/policy ranking, or general causal value claim |
| Discussion | foundation specification; Campaign 1/2 results and ledgers | none | validated campaign artifacts | bounded interpretation of prospective anticipation, null Q01 utility, and state/reference limitations | external validity and literature synthesis pending |
| Limitations | foundation specification; gate documents | source validators/controllers | gate controls | present model boundary | external validity assessment pending |
| Conclusions | `CAMPAIGN_2_RESULTS.md`; claim ledger | none | Campaign 2 confirmatory outputs | “prospective anticipation can have realized adaptive value, but internal preference does not guarantee realized benefit” within frozen scope | manuscript-level/general conclusion pending literature review |
| Reproducibility | foundation specification; campaign protocols/results | tests, validators, analysis, provenance tools | foundation plus Campaign 0–2 manifests, hashes, raw and derived outputs | traceability through Campaign 2, including the retained I/O incident | manuscript version and any future-campaign provenance pending |

## Machine-readable publication workflow

Every future campaign must follow:

```text
executable experiment
-> immutable/raw machine-readable artifacts
-> versioned analysis
-> generated table/figure plus source data
-> LaTeX manuscript.
```

No table may depend exclusively on manually transcribed values.  No figure
should exist only as an opaque image when its underlying data can reasonably be
preserved. Negative and null outcomes remain in the analysis provenance.

## Intended provenance chain

```text
foundation/model commit
-> experimental-protocol commit
-> experiment commit + run identifier
-> raw artifacts
-> analysis code
-> generated table/figure
-> manuscript version.
```

`a315143` is the Small Problem World fixture commit, `20106d3` is the
consolidated pre-experiment foundation, and `bdcc8bd` executed the diagnostic
Campaign 0. Campaign 1’s frozen test range and protocol are `05b86cb` and
`bcc3ad8`; its test-range-characterisation result commit is `ac9d421`.
Campaign 2 theory, preregistration, execution/results, and scientific closure
are `c7071769`, `9cfb6891`, `dabf6bab`, and the closure commit containing this
map, respectively. The failed first execution and its `validation_failure.json`
remain part of the provenance chain rather than being overwritten.

## Paper readiness

| Component | Status |
|---|---|
| Model specification | READY FOR FOUNDATION REVIEW |
| Mathematical derivations | READY FOR FOUNDATION REVIEW |
| Problem-world specification | READY; DIAGNOSTIC CAMPAIGN 0 EXECUTED |
| Scientific-status ledger | READY FOR FOUNDATION REVIEW |
| Literature review | PENDING |
| Campaign 0 diagnostic | COMPLETE; NOT MAIN EVIDENCE |
| Campaign 1 test-range characterisation | COMPLETE; NOT A STRATEGY COMPARISON |
| Campaign 2 hypotheses | COMPLETE; H1–H4 CLOSED WITH BOUNDED STATUS |
| Campaign 2 protocol | COMPLETE; PREREGISTERED |
| Prospective-policy comparison | COMPLETE; CONDITIONAL ON Q11 REFERENCE STATES |
| Statistical analysis | COMPLETE FOR CAMPAIGN 2 |
| Figures/tables | CAMPAIGN 2 MACHINE-REGENERABLE OUTPUTS READY |
| Discussion | PENDING |
| LaTeX manuscript | PENDING |
