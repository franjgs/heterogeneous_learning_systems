# Claim--Evidence Ledger

This ledger constrains future wording.  Repository evidence supports only the
scope stated; later evidence may update status through an explicit revision.

| ID | Candidate claim | Status | Evidence type and repository evidence | External literature needed? | Experimental evidence needed? | Allowed wording | Forbidden wording |
|---|---|---|---|---|---|---|---|
| C01 | HLS defines true problems on `Delta^1` | DEFINITION / MODELING ASSUMPTION | `problem_geometry.py`; foundation specification | no for definition | no | “The current HLS world defines…” | “Real problems universally form…” |
| C02 | CES maps capability outputs and problem weights to production | STANDARD RESULT + PARAMETER CHOICE | `discover_v0.py`; tests | yes for contextual use | calibration if empirical | “The model uses CES…” | “HLS invented CES” |
| C03 | DISCOVER performs finite Bayesian updating | VALIDATED IMPLEMENTATION PROPERTY | finite-belief code/tests/artifacts | standard Bayes citation later | no | “DISCOVER updates a finite belief…” | “continuous inference” |
| C04 | True problems may lie outside `Z_hat` | VALIDATED IMPLEMENTATION PROPERTY | unrepresented-truth gate control | misspecified Bayes literature for interpretation | no | “Execution remains valid under finite misspecification” | “the agent detects mismatch” |
| C05 | M=2 recovers historical binary DISCOVER | VALIDATED IMPLEMENTATION PROPERTY | finite-belief summary and regression tests | no | no | “recovered within numerical tolerance” | “new inference theorem” |
| C06 | MIS-v2 is an exponential remaining-gap transition | MODELING ASSUMPTION | capability-development theory/code/tests | qualitative learning literature | calibration/validation | “HLS formulates…” | “literature establishes this exact law” |
| C07 | MIS-v2 avoids finite instant mastery | HLS DERIVED RESULT / VALIDATED PROPERTY | R1--R7 tests | no | no | scoped mathematical statement | empirical learning claim |
| C08 | `d_R` is a metric under current physics | HLS DERIVED RESULT | problem-distance derivation, grid, tests | no | no | “under rho=.5 and the declared envelope…” | general task-similarity theorem |
| C09 | `C_t`, `N_t`, and `M_t` are distinct | DEFINITION + VALIDATED CONTROLS | problem geometry and Small World artifacts | conceptual literature later | no | describe exact counterexamples | agent recognizes novelty |
| C10 | Small Problem World is frozen pre-execution | EXPERIMENTAL FIXTURE | `a315143`; artifact `team_executions=0` | no | no | “deliberately constructed fixture” | “empirical environment distribution” |
| C11 | WHO-HAS-WHAT affected prior MIS-v2 trajectories under equal totals | PREVIOUS DIAGNOSTIC RESULT | MIS-v2 capability-geometry artifacts | yes for broader interpretation | new frozen campaign | exact scoped diagnostic wording | universal causal law |
| C12 | Geometry winners depend on eta/environment in prior gate | PREVIOUS DIAGNOSTIC RESULT | `regime_map_by_eta.csv` | no for raw finding | robustness campaign later | “in the declared grid…” | universal regime map |
| C13 | Old MIS-v1 winner map was not robust | PREVIOUS DIAGNOSTIC RESULT | `mis_v1_vs_v2.csv` | no | no | “changed after replacing defective MIS-v1…” | all earlier evidence invalid |
| C14 | Heterogeneous teams adapt better | HYPOTHESIS TO TEST / UNSUPPORTED | none in frozen world | yes | yes | frame as question | assert as finding |
| C15 | A team remembers recurrent problems | UNSUPPORTED | belief resets; only `S` persists | memory literature if later modeled | new mechanism required | “state history may affect recurrence behavior” | “remembers A” |
| C16 | `d_R` predicts transfer or difficulty | UNSUPPORTED | no transfer/difficulty link | yes | yes | state as open question | metric interpretation as probability |
| C17 | Current MPC is globally optimal | UNSUPPORTED | dynamic controller is two-step MPC | no | exact-oracle comparison if claimed | “frozen receding-horizon controller” | “exact full-horizon optimum” |
| C18 | The Small Problem World fixture was frozen before team execution | VALIDATED HISTORICAL PROVENANCE | fixture artifact at `a315143` records `team_executions=0`; Campaign 0 was executed later at `bdcc8bd` | no | no | “the fixture was frozen before Campaign 0” | “the world has never been executed” |
| C19 | Null and negative results are admissible | PROTOCOL PRINCIPLE | philosophy and foundation specification | no | retain future outcomes | explicit retention policy | selective positive reporting |
| C20 | Campaign 0 demonstrated discriminative capacity in its frozen diagnostic | PREVIOUS DIAGNOSTIC RESULT | `CAMPAIGN_0_DISCRIMINATIVE_CAPACITY.md`; Campaign 0 manifest/raw artifacts | no for the scoped result | main campaign for substantive team hypothesis | “Campaign 0 passed its pre-specified diagnostic rule” | “Campaign 0 confirmed the paper hypothesis” |
| C21 | Campaign 0 had history-dependent recurrent-A rankings | PREVIOUS DIAGNOSTIC RESULT | `order_effects.csv`; `ranking_through_time.csv`; 10 frozen seeds | literature for broader interpretation | confirmatory protocol if generalized | report exact H0/H1 scope and positive/null cases | universal path-dependence claim |
| C22 | Conditional on `S_0` and cumulative exposure, MIS-v2 is exposure-order invariant | HLS DERIVED RESULT / VALIDATED IMPLEMENTATION PROPERTY | MIS-v2 algebra; post-hoc reconstruction of 480 Campaign 0 cells, max error `1.11e-16` | no for algebra; yes for empirical learning interpretation | external validation for real-team claim | “an algebraic consequence of the HLS MIS-v2 formulation” | “empirically discovered law” or “literature-established theorem” |
| C23 | Campaign 0 capability-state path dependence is policy-mediated | POST-HOC MECHANISTIC INTERPRETATION | exact exposure identity plus frozen H0/H1 trajectories | yes before broader theoretical framing | new preregistered evidence if promoted | “within the frozen model, history changes state through assignments and cumulative exposure” | preregistered hypothesis, direct explanation of performance, or general causal law |
| C24 | G07 was a universal adaptive winner | UNSUPPORTED | G07 won cumulative production only in four Campaign 0 histories | yes | broader pre-specified campaign | “G07 led cumulative production in all four Campaign 0 histories” | “G07 is universally optimal” |

No claim may be promoted by copying a number from prose.  Promotion requires
an authoritative artifact, analysis code, declared scope, and—where relevant—
external literature support.
