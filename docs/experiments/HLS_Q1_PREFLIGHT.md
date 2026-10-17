# HLS Q1 campaign preflight

**Registration timestamp:** 2026-10-16 10:33 +02:00 (Europe/Madrid)
**Status:** preregistered preflight; the 960-run main campaign remains on HOLD.
**Design authority:** [HLS first scientific campaign design](HLS_FIRST_SCIENTIFIC_CAMPAIGN_DESIGN.md).

This is an instrument/design preflight, not a test of scientific superiority.
No scenario, threshold, seed, estimand, or acceptance rule below may be changed
after diagnostic outputs are inspected. The main campaign is not authorized by
this registration.

## 1. Registered contrasts and invariants

The primary simulation contrast is the difference between the matched
heterogeneity-tilted minus homogeneous architecture effect under persistent
Markov demand and the same architecture effect under IID demand, at the
frontier-defined near-boundary stratum, with MIS-v2 OFF and the existing P0
policy. Primary outcome is cumulative **gross CES**. The secondary MIS-v2 ON
block uses the same policy and demand trajectories. The architecture × demand
estimand is conditional on the fixed action catalogue, resource budget,
full-information initial estimates, P0 ranking rule, and the additive
production model; it is not an external-organizations estimand.

Architecture invariants are fixed at:

| Arm | Initial competence matrix (agents × skills) | Skill totals | Agent totals |
| --- | --- | --- | --- |
| Homogeneous | `((.5,.5),(.5,.5),(.5,.5))` | `(1.5,1.5)` | `(1,1,1)` |
| Tilted | `((.6,.4),(.4,.6),(.5,.5))` | `(1.5,1.5)` | `(1,1,1)` |

Both use three agents, the same `eta=.10` for every agent/skill, budgets
`B=2` and per-agent cap `1`, the same 64-action DISCOVER catalogue, public
problem requirements, initial estimates equal to each declared roster, zero
production-observation noise, no teaching, and the same P0 implementation.
Only the distribution of the fixed aggregate skill endowment differs.

Demand task labels are skill-0, skill-1, and joint with `pi=(.4,.4,.2)`.
IID draws use `StationaryTaskDemand(pi)`. Persistent demand uses initial
distribution `pi` and `P(i,j)=.8·1[i=j]+.2·pi[j]`. Since
`πP=.8π+.2π=π`, both have the same theoretical stationary marginals. Their
theoretical lag-one probability of retaining the same task is `.36` for IID
(`Σπᵢ²`) and `.872` for Markov (`.8+.2Σπᵢ²`). Demand is generated and frozen
before organization runs; task paths, not diagnostic noise seeds, are the
independent replication units.

The three competence-frontier strata retain the registered design values:
easy requirements `(.5,0)`, `(0,.5)`, `(.25,.25)`; near-boundary
`(1.05,0)`, `(0,1.05)`, `(.55,.55)`; and initially infeasible but
MIS-witness-reachable `(1.3348,0)`, `(0,1.3348)`, `(.6924,.6924)`. The
separate equivalence control is skill-0-only demand with `B=3`, cap `1`, all
three agents productively exposed, and matched `eta=.10`.

## 2. Preregistered diagnostic samples and analysis

1. **Architecture and exact frontier:** enumerate all frozen actions for both
   architectures and all three orientations; no sampling. Check frontier,
   successful-action count, feasibility distance, and resource-use range.
   Reproduce the 24-period feasible exposure witness and calculate its
   post-MIS frontiers using the existing MIS-v2 transition.
2. **Demand process:** generate 200 independent paths of length 24 per process,
   with fixed disjoint seed ranges `2026101600–2026101799` (IID) and
   `2026101800–2026101999` (Markov). Report empirical task frequencies,
   lag-one same-task rate, run-length distribution by type, distinct paths,
   and exact repeat-seed checks. Do not require finite-sample marginal counts
   to match between IID and Markov.
3. **Outcome/instrument sensitivity:** use 12 predeclared independent paths
   per process, task-path seeds `2026102100–2026102111` (IID) and
   `2026102200–2026102211` (Markov), each length 24. Run both architectures,
   all three registered difficulty strata, and MIS OFF/ON on each frozen path
   (288 trajectories; 6,912 problem decisions). No observation-noise replicate
   is counted as an independent scenario. Include the deterministic
   equivalence control under MIS OFF/ON.
4. **Uncertainty:** report paired architecture differences by path. For the
   primary preflight contrast, report mean, seed-cluster bootstrap 95%
   percentile interval (10,000 resamples, fixed analysis seed `20261016`),
   median, and all paired values. Resample whole demand paths within each
   process, then subtract Markov and IID architecture-effect means. These
   small preflight intervals describe diagnostic uncertainty only; they do
   not constitute a power calculation or permit scenario selection.

All task paths and architecture arms within a path remain paired. No period
rows are treated as independent. A zero estimated architecture effect is
permitted and is not by itself a failure. The experiment is structurally
insensitive only if exact action/frontier analysis and outcome instrumentation
show that the declared architecture and demand interventions cannot alter any
measured outcome under the registered strata.

## 3. Acceptance criteria and failure conditions

| Requirement | PASS criterion | Failure/stop condition |
| --- | --- | --- |
| Architecture match | Exact equality of agent count, skill totals, per-agent totals, learning parameters, budgets, action catalogue and information mode; only cell redistribution differs. | Any unmatched factor other than the declared competence redistribution. |
| Stationary marginal | Algebraic `πP=π`; empirical frequencies reported with trajectory-level uncertainty, with no demand for sample equality. | Matrix/initial distribution differs from registered process. |
| Persistence | Markov theoretical same-task probability `.872` versus IID `.36`; repeatable empirical sample shows higher Markov lag-one persistence and longer runs. | Markov process does not produce greater persistence or is not reproducible. |
| Feasibility | Exact initial frontiers reproduce skill-0 `(1.0,1.1)`, skill-1 `(1.0,1.1)`, and joint `(.5,.6)` for homogeneous/tilted arms; easy both feasible; boundary lies between frontiers; learnable requirements exceed both initial frontiers and lie below both MIS-witness frontiers; infeasible controls have zero successful actions. | Any required class cannot be expressed or computed under the existing catalogue/physics. Preserve unexpected values; do not retune. |
| Outcome instrumentation | Same frozen task sequence reaches both architectures and MIS conditions; action, CES, success and resource traces are reproducible and correctly measured. | Trace mismatch, latent-state leakage, or inconsistent accounting. |
| Diagnostic sensitivity | At least two distinct paths per process; all output counts and changes are reported. Exact frontiers establish potential architecture sensitivity. A realized zero effect remains valid. | NO-GO only if structural checks prove the contrast incapable of affecting any registered outcome; otherwise a small-sample null is INCONCLUSIVE. |
| MIS control | OFF produces no competence change; ON changes only via productive MIS-v2 exposure; learning rates match; no teaching; demand generation is independent of learning/observation streams. | Any undeclared competence transition, teaching, or shared/random-stream dependence. |
| Statistical registration | Estimand and gross-CES primary outcome above; independent demand paths are clusters; seed-cluster 95% intervals and separate resource reporting. No arbitrary minimum effect. | Any post-outcome change to estimand, sample definition, or primary outcome. |

The fixed MIS exposure witness is period `t`: one full skill-0 unit to
expert `t mod 3` and one full skill-1 unit to expert `(t+1) mod 3`, for 24
periods. At `eta=.10`, expected post-witness frontiers are approximately
`(1.5695,1.5695,.7848)` for homogeneous and `(1.6126,1.6126,.8278)` for
tilted, ordered skill-0, skill-1, joint. The registered learnable thresholds
are `(1.3348,0)`, `(0,1.3348)`, and `(.6924,.6924)` respectively.

Status vocabulary: **PASS** means the declared instrument check held;
**FAIL** means observed behavior contradicts its registered invariant;
**INCONCLUSIVE** means the diagnostic sample cannot determine the property;
**BLOCKED** means existing interfaces cannot express the required comparison.
Main-campaign GO requires architecture matching, demand validity, feasibility,
valid outcomes/resources, independent demand realizations and identifiable
estimand to pass. A null treatment estimate is not a failure. Any structural
insensitivity, confounding beyond the stated conditional estimand, or
unreproducible stream is NO-GO pending CE review.

## 4. Registered exclusions and confounding

No teaching, new policy, action catalogue, simulator physics, external noise,
scenario, or architecture may be added. Do not substitute a threshold if the
frontier check fails. Do not use the preflight to select only favorable
seeds. Report equal budgets separately from realized effort and unused
capacity. Gross CES is not net welfare; P0 ranks success, deficit, margin,
then effort, rather than maximizing CES. The architecture effect is therefore
conditional on P0 and may include its assignment response to the public
competence estimates. Full-information initialization is shared but limits
claims about partial-information organizations. The tilted roster changes
who is more competent in a skill by design; individual identity may interact
with deterministic tie-breaking and must be reported as part of the specified
architecture treatment.

## 5. Executed preflight results — 16 October 2026

Protocol was fixed before diagnostic generation. Registered document
SHA-256: `7fcfb9a900e522356531d02ef1fa65bc619643e798c3373a7031b39bdc4572ce`;
machine-readable preregistration SHA-256:
`45cbdd4254ea6353d6ef3dc1a66b8f9c5b900b1ff2fc4a602b7fe00db81e804f`.
The result manifest preserves both digests and source/output hashes.

### Exact checks

Architecture matching **PASS**. Both arms have three agents, skill totals
`(1.5,1.5)`, row totals `(1,1,1)`, identical `eta=.10`, `B=2`, cap `1`,
P0, action catalogue, initial information contract and noise settings. The
only intended change is the cellwise redistribution. One residual limitation
is that the particular tilt is tied to fixed expert IDs; it estimates this
declared roster contrast, not an average over relabelings or all heterogeneous
architectures.

Demand process **PASS**. Algebraically `πP=π` exactly. In 200 paths/process ×
24 periods, empirical frequencies were IID `(skill0 .4027, skill1 .3967,
joint .2006)` and Markov `(.3388,.4531,.2081)`. There were 200 distinct IID
paths and 190 distinct Markov paths (the remaining seeded draws duplicated a
realized categorical path); the registered criterion was at least 190, not
finite-sample equality of marginals. Empirical lag-one same-task rates were
`.3537` IID and `.8748` Markov, against theoretical `.36` and `.872`. Mean
observed completed/censored run lengths were IID `1.23–1.61` and Markov
`5.23–6.93` by task; theoretical geometric means are IID `(1.67,1.67,1.25)`
and Markov `(8.33,8.33,6.25)`. Horizon censoring explains shorter empirical
Markov runs. Seed replay reproduced every checked path.

Productive feasibility **PASS**. The exact 37-action feasible catalogue
reproduced initial frontiers: homogeneous `(1.0,1.0,.5)`, tilted
`(1.1,1.1,.6)` for skill-0, skill-1, joint. For each orientation, easy
requirements were feasible in both; near-boundary requirements had zero
successful actions for homogeneous and one for tilted; initially learnable
requirements had zero successful actions in both. The 24-period MIS witness
produced frontiers homogeneous `(1.56953,1.56953,.78477)` and tilted
`(1.61258,1.61258,.82781)`, strictly above the registered learnable levels.
Across every feasibility case, feasible action effort ranged `0–2`; the
manifested JSON records the effort count distribution and successful-action
IDs rather than hiding action granularity.

The demand/outcome diagnostics used 12 independent paths per process and ran
both architectures × three strata × MIS OFF/ON on each frozen path: 288
organization trajectories (6,912 decisions), plus four equivalence-control
trajectories. All conditions received identical requirements, budgets and
task labels within a path. No teaching or observation noise was active.
Resource accounting passed: each near-boundary trajectory consumed `48` of
`48` available units over 24 periods, with zero residual capacity. MIS OFF
preserved real competence; MIS ON changed it according to the existing
MIS-v2 transition and recorded productive exposure. The all-skill-0
equivalence control passed with both MIS settings (outputs, CES, success,
resource and aggregate skill-0 competence equal within `1e-12`).

### Outcome sensitivity and the registered estimand

The instrument is outcome-sensitive: for near-boundary/MIS-OFF, cumulative
CES was IID `22.25` homogeneous and `24.65` tilted; Markov `22.00` and
`24.40`. Functional success was `0/288` versus `288/288` within each demand
family. These are conditional pilot observations, not population estimates.
Finite realized task frequencies differ between the two diagnostic families,
so the raw family means must not be read as a temporal-demand causal effect.

The registered architecture effect (tilted minus homogeneous) was
`+2.400000` for every one of the 12 IID and 12 Markov paired paths. The
primary moderation estimate was `Theta = −1.33×10⁻¹⁵` CES, with seed-cluster
bootstrap 95% percentile interval `[−4.00×10⁻¹⁵, 4.44×10⁻¹⁶]`. Direct
one-period checks found architecture CES differences of `+.10` for skill-0,
skill-1 and joint tasks; P0's selected actions were stable by task type in the
diagnostic paths. MIS-OFF competencies were fixed and the full-information
estimates moved by at most `1.01×10⁻¹³` (the zero-noise posterior corrected a
tiny grid-prior mean discrepancy, below the registered `1e-12` tolerance).
Thus this primary block has no material state
pathway through which task ordering can change its expected architecture
contrast: with a stationary common marginal, the expected sum of the
task-specific architecture contrasts is the same under IID and Markov
demand. Persistence changes realized composition/variance, not the registered
mean interaction. This is a structural null for the primary estimand, not
merely a small observed effect.

MIS-ON is secondary and does show intertemporal outcome variation (for
example, near-boundary successes were IID `269/288` vs `288/288`, Markov
`268/288` vs `288/288`; learnable successes `185/288` vs `206/288`, Markov
`197/288` vs `218/288`). These data do not promote MIS-ON to primary after
inspection, nor isolate a general architecture effect from the particular
P0/learning interaction. No hypothesis or estimand was changed.

### Acceptance matrix and decision

| Requirement | Status | Result |
| --- | --- | --- |
| Architecture matching | **PASS** | Aggregate, per-agent, learning, budget and information controls matched. |
| Demand process | **PASS** | Same theoretical stationary marginals; reproducible Markov persistence substantially higher. |
| Feasibility controls | **PASS** | Easy, boundary, initially infeasible/witness-reachable and aggregate-equivalence controls behaved as registered. |
| Outcome sensitivity | **PASS** | Architecture changes CES and success; multiple exogenous paths produce varied outcome traces. |
| Primary Q1 mean-interaction identifiability | **FAIL — structurally null** | With MIS OFF, frozen state and common stationary marginals make the registered mean moderation zero; task deltas were all +.10. |
| MIS-v2 control | **PASS** | OFF freezes; ON follows productive MIS-v2 exposure; teaching disabled. |
| Resource accounting | **PASS** | Gross CES, actual use and residual reported separately; no cost coefficient added. |
| Statistical registration | **PASS** | Paths are clusters; paired arms retained; no effect threshold or period-level pseudoreplication. |

**Decision: NO-GO for the 960-run campaign as registered.** The laboratory
can represent architecture and persistence, but the registered primary
estimand cannot answer the intended interaction in its MIS-OFF block. The
observed zero is backed by the frozen-state/common-marginal structure and
task-level response check; it is not a failure of the demand generator or
outcome instrument. A CE-approved redesign/re-registration would be required
before any main campaign. MIS-ON was explicitly secondary and must not be
silently substituted. No main campaign was run.

Residual scope: comparison is conditional on P0, additive production, the
discrete 37-action feasible set, full-information initialization, zero
observation noise, and the fixed expert-ID tilt. Demand types are stationary
with persistence, not exogenous regime shifts. Resource budget equality does
not imply equal realized use generally, although this sample used all
resources. No external calibration or real-organization inference is made.

### Reproducibility and artifacts

Runner: `experiments/synthetic/hls_lab_v1/q1_preflight.py`. Reproduce with:

```sh
PYTHONPATH=src python experiments/synthetic/hls_lab_v1/q1_preflight.py
```

Focused tests: `PYTHONPATH=src:. pytest -q tests/test_hls_q1_preflight.py tests/test_hls_lab_v1_environment.py tests/test_hls_lab_v1_integrated.py` — **24 passed**. Two fresh output-directory executions were byte-identical (`diff -r` clean). Artifacts are isolated under `results/diagnostics/hls_q1_preflight/`: preregistration, demand paths, trajectory CSV, exact action feasibility, equivalence control, summary and manifest. The full repository suite was not rerun; its 13 previously documented provenance/integrity failures remain unresolved and are not hidden. HLS Laboratory remains **PARTIAL**.
