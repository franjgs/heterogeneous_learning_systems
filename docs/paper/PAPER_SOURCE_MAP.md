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
| Experimental design | `SMALL_PROBLEM_WORLD_GATE.md`; future preregistration | `small_problem_world.py`; future runner | frozen world artifacts | world/repertoire/descriptors fixed | G00--G08 protocol pending |
| Results | capability-geometry docs only as prior diagnostic provenance | historical gate runners | MIS-v1/v2 result tables | scoped previous diagnostic findings | frozen-world results do not exist |
| Discussion | foundation specification; future results | none | future analysis | limitations and absent mechanisms | conclusions before campaign/review |
| Limitations | foundation specification; gate documents | source validators/controllers | gate controls | present model boundary | external validity assessment pending |
| Conclusions | none yet | none | none | no substantive experimental conclusion | entirely pending |
| Reproducibility | foundation specification; repository guide | tests and gate runners | foundation manifest and gate artifacts | current foundation traceability | future run/protocol identifiers pending |

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

`a315143` is the source foundation HEAD, not the future protocol commit.

## Paper readiness

| Component | Status |
|---|---|
| Model specification | READY FOR FOUNDATION REVIEW |
| Mathematical derivations | READY FOR FOUNDATION REVIEW |
| Problem-world specification | READY; NO TEAM EXECUTION |
| Scientific-status ledger | READY FOR FOUNDATION REVIEW |
| Literature review | PENDING |
| Experimental hypotheses | PENDING |
| Experimental protocol | PENDING |
| Main campaign | PENDING |
| Statistical analysis | PENDING |
| Figures/tables | PENDING |
| Discussion | PENDING |
| LaTeX manuscript | PENDING |
