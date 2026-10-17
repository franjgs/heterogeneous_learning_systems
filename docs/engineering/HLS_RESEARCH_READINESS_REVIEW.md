# HLS Laboratory — Phase 5 research-readiness review

**Recorded:** 2026-10-16 20:22 +02:00 (Europe/Madrid).
**Validated base:** `8804daf6303a5db134098ea87ac5c8ff2469a3b8`.
**Scope:** integrated validation, metrics/configuration audit, reproducibility,
bounded scalability, and readiness. No campaign, model, or frozen result was
changed.

## Executive decision

**Recommendation: CONDITIONALLY READY for a bounded, pre-registered study
inside the tested N×K model, after that study archives its complete inputs and
trajectory. Not ready for broad claims of organizational realism, scalability,
or scientific superiority.** Integrated tests and legacy regressions support
internal consistency, not empirical adequacy. HLS Laboratory remains
**PARTIAL** pending PI review. The final suite has five known provenance/
integrity failures, none new to this intervention.

The main operational gap is that N×K result serialization is deterministic
but does not itself store a complete experiment manifest: initial organization,
environment configuration/seed, policy parameters, mechanism settings,
information seed, and software revision must be archived by the caller.

## 1. Architecture map

| Stage | Implementation | Evidence and boundary |
|---|---|---|
| Organization | `OrganizationConfigNK` / `OrganizationStateNK`: ordered IDs, actual/estimated N×K competence, per-agent effort limits, shared budget. | **VALIDATED** at 1×1, 2×2, 3×2, 4×3. No general network/topology object. |
| Environment | `ExogenousEnvironmentConfigNK`, `DemandRegimeNK`, `EnvironmentTrajectoryNK`; existing C5 IID/stationary, time-indexed nonstationary and first-order Markov processes. | **VALIDATED** for state transitions, replay, K-dimensional emission, legacy 3×2 equivalence and policy independence. One problem per period. |
| Decision | P0/P1/P2 adapters, shared decision view, feasible joint actions and P2 efficacy memory. | **VALIDATED** against historical 3×2 behavior/rules. N=1 supports P0 only; P1/P2 require a distinct-agent teaching relation. These are three specific policies, not a broad policy family. |
| Production/evaluation | Additive `y[k]=Σᵢ e[i,k]c_actual[i,k]`; functional success/deficit/margin and gross CES. | **VALIDATED** against hand calculations, constraints and 3×2 outcomes. CES excludes resource costs. |
| Learning and teaching | N×K MIS-v2 adapter; one directed lesson at most with `N×N×K` efficacy and the legacy two-participant charge. | **VALIDATED** for transitions, timing, resource accounting and 3×2 regression. No alternative learning model or simultaneous lessons. |
| Observation/estimation | Perfect reference or existing bounded posterior, production/formative observations and efficacy memory. | **VALIDATED** for N×K shapes, replay and legacy equivalence. Decision views exclude actual competence in imperfect mode, private efficacy and latent regimes. |
| Trace/replay | Immutable records, deterministic JSON serializers; environment trajectory returned separately from execution. | **PARTIALLY VALIDATED**: exact repeated and fresh-process serialization verified; full inputs/software metadata are not embedded. |

“Implemented” means code exists; “validated” means specific tests and/or
independent arithmetic checks support the behavior. Neither implies real-world
calibration.

## 2. Integrated validation and invariants

Added `tests/test_hls_research_readiness.py`. For each required geometry it
generates one three-period Markov trajectory with a deterministic regime
transition and runs all valid combinations of P0/P1/P2, MIS ON/OFF, teaching
ON/OFF, and perfect/imperfect information. For 1×1 only P0 is valid; P1/P2
are not constructed because no directed relation exists. Candidate enumeration
is guarded at 10,000 and never truncated.

The tests independently recompute additive production, weighted CES using
`RHO`, functional success, total/per-agent resource feasibility, unused
capacity, the MIS-v2 equation and directed teaching increments. They also
check perfect estimates follow actual transitions and imperfect estimates
remain bounded. Result: **4 parametrized geometry tests passed**. The wider
focused HLS/Phase 1–4 regression command passed **172 tests**.

Supported invariants:

* Actual competence, not estimates, determines realized production; bounds
  and production → MIS-v2 → teaching ordering hold.
* Individual/shared resource limits hold and effort reconciles to the effective
  budget, with unused capacity separate.
* Policies receive only authorized decision information.
* C5 demand is frozen before policy execution; actions cannot alter future
  demand.
* Production, success, CES, competence and resource traces agree with
  independent per-period checks.
* Repeated runs serialize identically. Two fresh Python processes produced
  identical information-run SHA-256:
  `0a5710ce5f7b40e58b2760d53f2f916c544098c1e28d13870634c405eac90985`.

## 3. Experimental configuration and comparability

Configuration is compositional through existing APIs, not a single run
configuration file. Researchers pass dataclasses and runner arguments; no
scientific source edit is required.

| Factor | Accepted representation and range | Dependency or limitation |
|---|---|---|
| N, K, identifiers | Ordered unique non-empty agent/skill IDs, N,K≥1. | No arbitrary dimension cap; exhaustive catalogs are bounded by `max_candidates`. |
| Competence | Actual and optional estimated rectangular N×K matrices in [0,1]. | Omitted estimates initialize to actual; imperfect mode can start with a distinct estimate. |
| Effort/resources | Finite nonnegative per-agent limits and shared/problem budgets. | Effective budget is their minimum; discrete actions can strand capacity. |
| Productive actions | Ordered per-agent vectors in [0,1]. | K=2 uses legacy catalog by default; other K require explicit catalogs. Full Cartesian enumeration. |
| MIS-v2 | N×K eta profile, historical admissible interval; toggle `individual_learning`. | Eta=0 is invalid; use MIS OFF control. |
| Teaching | N×N×K efficacy in [0,1], zero diagonal; historical transfer/effort parameters. | One directed event, teacher≠learner, requires N≥2. |
| Policies | P0, configured P1 relation, configured ordered P2 relation set and historical parameters. | P1/P2 relation and teaching availability constraints apply. P0 never teaches. |
| Information | `perfect`/`imperfect`, observation SDs, prior variance [0,.25], grid points≥3. | Existing bounded posterior only; zero noise is not necessarily perfect knowledge. |
| Demand | Explicit sequence or C5 process + finite task emissions, horizon, seed. | One problem per period; problem catalog size independent of K. |
| Seeds | Separate environment and indexed information seeds. | Result serializer does not persist them or all other inputs. |

Fair comparisons must hold fixed initial actual/estimated states, ordered IDs,
effort catalogs/limits, shared budget, environment and frozen trajectory,
learning/teaching parameters, information mode, observation parameters,
horizon, non-treatment policy parameters and software revision. Common indexed
random innovations couple corresponding coordinates, but equal seeds do not
guarantee equal realized observations when actions/exposure differ. Demand
trajectories—not observation-noise seeds—should normally define independent
replication units. Equal budgets are not equal consumption.

The environment/emission and observation streams are separated; trajectory
generation is completed before a policy runs. Stable sorted-key JSON is
provided for execution results. However, environment metadata is separate,
and result records omit complete run configuration, seeds, and software
revision. Archive a machine-readable input manifest, trajectory, trace,
source commit, and runtime versions for every campaign. Cross-platform
bit-identical floating-point behavior is not promised.

## 4. Scientific metrics inventory

| Metric | Availability | Interpretation |
|---|---|---|
| Productive effort by agent | **DIRECTLY RECORDED** | `individual_effort_used`. |
| Productive contribution by agent × competence | **DIRECTLY RECORDED** | `individual_outputs` (effort × actual competence); not a causal marginal effect on collective success. |
| Productive output by competence | **DIRECTLY RECORDED** | `outputs`. |
| Teaching relation/action and formative observation | **DIRECTLY RECORDED** | `action.teaching`, `teaching_observation`, efficacy memory. Latent efficacy is configuration, not observation. |
| Teaching effort by participant | **EXACTLY DERIVABLE** | Each of the two participants is charged lesson effort; their sum is teaching resource use. Not external labor time. |
| Actual competence, MIS gain, teaching gain | **DIRECTLY RECORDED** | Before/after matrices and separate increments. |
| Estimate, posterior variance, estimation error | **DIRECTLY RECORDED** | Information trace; perfect mode has no posterior variance. |
| Success rate / successes | **EXACTLY DERIVABLE** | Count per-period functional successes; every period is attempted, with no queue/deadline semantics. |
| Gross CES | **DIRECTLY RECORDED** | Per-period gross functional reward; not net utility, welfare or profit. |
| Productive/teaching/total use and unused capacity | **DIRECTLY RECORDED** | Period trace; individual combined loads are derivable. |
| Performance, competence, resources, actions over time | **DIRECTLY RECORDED / EXACTLY DERIVABLE** | Period records aligned by index with separate environment regime labels. |
| Causal individual contribution to collective success | **NOT CURRENTLY AVAILABLE** | Requires counterfactual intervention; do not infer from `individual_outputs`. |
| Monetary cost/net economic utility | **NOT CURRENTLY AVAILABLE** | No cost conversion or CES subtraction is defined. |
| Concurrent throughput, backlog, deadlines | **NOT CURRENTLY AVAILABLE** | No task queue or concurrent problem model. |

No new metrics or scalar objective were added.

## 5. Historical 3×2 equivalence

Regression coverage retains the ordered 64-production and 508-integrated
catalogs, P0/P1/P2 decisions and serialized traces; production/CES, MIS-v2,
teaching, noisy observation, estimation/posterior, efficacy memory and
historical IID/Markov/nonstationary behavior. Phase 4 also compares emitted
legacy/N×K problem IDs, requirements, CES weights, budgets and latent task
states. These establish implementation compatibility under matched conditions,
not external validation. This phase changed no historical code, fixtures,
campaign outputs, manifests or expected hashes.

## 6. Scalability measurements

Python 3.11.9, macOS 27.0.1 arm64. Three-period stationary one-type demand;
P2/MIS ON/teaching available/imperfect information for N≥2 (1×1 uses P0,
no teaching). Eta=.15, efficacy=.6 off-diagonal, budget=2, lesson effort=.25,
observation SD=.02. K=2 used the historical catalog; K=1/3 used zero plus
one 0.5 single-skill vector per agent. Environment, enumeration and direct
mechanism times are local means of five calls; policy selection is a mean of
10 calls; complete episodes are a mean of three runs; peak memory is one
`tracemalloc` run. Candidate counts are feasible under this configuration;
these are not portable performance guarantees.

| N×K | Feasible production / joint candidates | Environment generation ms | Joint enumeration ms | P0 / P1 / P2 selection ms | Production+evaluation ms | MIS / teaching transition ms | Observation / posterior ms | 3-period episode ms | Peak traced bytes | Trace bytes |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1×1 | 2 / 2 | .041 | .015 | .015 / n/a / n/a | .004 | .005 / n/a | .009 / .020 | .532 | 33,512 | 8,956 |
| 2×2 | 16 / 20 | .047 | .226 | .099 / .008 / .105 | .005 | .004 / .0001 | .031 / .069 | 2.142 | 63,652 | 18,569 |
| 3×2 | 37 / 85 | .045 | 1.419 | .247 / .032 / .252 | .005 | .006 / .0001 | .045 / .114 | 6.873 | 101,172 | 25,563 |
| 4×3 | 256 / 6,556 | .039 | 36.034 | 2.129 / 2.230 / 2.181 | .007 | .010 / .0001 | .097 / .195 | 119.578 | 1,659,352 | 50,860 |

Exhaustive joint-action enumeration is the main measured bottleneck; at 4×3,
6,556 feasible candidates took about 36 ms per decision and a three-period
episode about 120 ms. The explicit guard remains necessary. Larger catalogs
and horizons require a preflight; no pruning or approximation is authorized.

## 7. Research scope and readiness risks

Within the declared model, controlled studies can compare competence
distributions under fixed dimensions/action catalogs; the specified P0/P1/P2
packages under common conditions; MIS, teaching, and information toggles;
response to known exogenous IID/nonstationary/Markov demand; and separate
performance, success, resource and competence trajectories.

The laboratory does not currently support concurrent tasks, backlog/deadlines,
latent-demand inference, stochastic production, arbitrary coordination or
learning families, calibrated costs, or broad network organization. Demand
requirements are public; production is additive and action choice discrete.
The largest measured geometry is 4×3, where enumeration already dominates.

| Class | Finding |
|---|---|
| **BLOCKER for affected provenance claims** | Five tests still fail: foundation inventory is 12 vs frozen 11; Campaign 2 closure digest mismatch; Campaign 2 theory source digest mismatch; Campaign 3 frozen `finite_problem_belief.py` digest mismatch; strategy-discrimination frozen source digest mismatch. Claims relying on affected artifacts require provenance resolution. No evidence was modified. |
| **IMPORTANT LIMITATION** | There is no first-class versioned run manifest. A campaign harness must archive all inputs, seeds, frozen demand, policy memory/settings, source revision and runtime. |
| **IMPORTANT LIMITATION** | Exhaustive action enumeration is combinatorial; campaign size must be preflighted with its exact catalog. |
| **IMPORTANT LIMITATION** | Internal mechanism validation is not empirical calibration; gross CES is not net welfare and individual outputs are not causal individual effects. |
| **FUTURE EXTENSION** | Queues, alternative policies/mechanisms, latent-demand learning, stochastic production, broad networks and scalable action generation require a specific question and separate authorization. |

## 8. Final validation and decision

Final command: `PYTHONPATH=src:. python -m pytest -q` — **1,396 passed,
5 failed in 503.84 s**. Failures:

1. `tests/foundations/test_result_manifests.py::test_every_foundation_result_has_consistent_manifest`
2. `tests/test_campaign2_state_coverage_audit.py::test_frozen_inputs_and_completed_artifacts`
3. `tests/test_campaign2_theory.py::test_preexperiment_manifest_and_contamination_boundary`
4. `tests/test_campaign3_meta_voc_confirmatory.py::test_pre_execution_manifest_and_raw_integrity_when_present`
5. `tests/test_strategy_discrimination_gate.py::test_source_hashes_and_raw_output_hashes`

These are the same five baseline failures. Their observed causes are,
respectively, the extra current foundation result directory; Campaign 2
closure digest mismatches for `docs/experiments/CAMPAIGN_2_RESULTS.md` and
three paper traceability documents; and a source digest mismatch for
`src/hls/finite_problem_belief.py` in the Campaign 2, Campaign 3 and strategy
gate freezes. For that source, the stored digest is
`4ea7e964bf0e700f98fea700a9541c1ef374ce713338dd1eb78bc5fac8a3b097`, while
the current file digest is
`992a8eedb6bb77af7a9c1286ca6c63d1ff3805341421d5674c64a5e406f1b2fd`. No new
functional regression appeared. `git diff --check` passed.

**Decision: CONDITIONALLY READY** for a modest pre-registered study inside the
validated scope, provided its harness archives a complete manifest, freezes
common demand and preflights exact candidate counts. Resolve the five
provenance failures before claims relying on affected historical evidence.
No campaign is authorized by this review. HLS Laboratory remains **PARTIAL**
pending PI review.
