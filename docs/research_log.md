# Research log

## Decision 001 — Creation of the umbrella research programme

Date: 2026-09-14.

### Decision

Create **Heterogeneous Learning Systems** as an umbrella research programme.
The purpose is to investigate whether competence allocation across heterogeneous
agents can be deliberately evolved through operation and knowledge transfer.

`adaptive_routing` was judged too narrow to serve as the main programme axis:
it addresses a particular two-agent execution/learning coupling. It remains a
valid, independent subproject. It is neither abandoned, rewritten, moved, nor
treated as historical data belonging to this repository.

### Initial scientific status

**HYPOTHESIS.** Competence distribution may be a controllable dynamic property
of a heterogeneous learning system. This is not a model, theorem, algorithm,
or novelty claim.

**KNOWN RESULT / landscape observation.** MARL, mixture-of-experts, machine
teaching, collaborative intelligence/co-distillation, lifelong multi-agent
learning, orchestration/routing, edge/cloud collaboration, federated/continual
learning, and knowledge valuation each cover relevant ingredients.

**OPEN QUESTION.** Whether their interaction has an accepted formulation or
solution for deliberate competence-distribution evolution is unknown.

### Methodological rule

Prior work combining some or even most ingredients does not by itself settle
the direction. Each candidate literature family must be evaluated for
conceptual precedent, methodological maturity, accepted-solution status,
limitations/open problems, and potential for meaningful improvement. Novelty is
not ``being the first paper to mention an idea.''

### Next action

Create and maintain a literature map before promoting additional research
questions, methods, experiments, or formal models.

## Decision 002 — Provisional consolidation of the landscape phase

Date: 2026-09-14.

### Decision

Close the broad horizontal landscape phase provisionally and record its
technical synthesis in `landscape/landscape_001_consolidated.md` and research
checkpoint 002. This is a documentation decision, not a conclusion that the
literature is complete or that the programme has a scientific gap.

### Consolidated position

The audit covered routing/RouteNLP, Machine Teaching and curriculum, Active
Learning/Value of Information, bandits/resource allocation, capacity
expansion/optimal control, continual/lifelong learning, and decision-focused
optimization. The principal correction is that Machine Teaching must not be
caricatured as fixed-single-target teaching: the audited literature includes
iterative, learner-state-dependent, partially observed, and selective teaching
mechanisms.

H1 survives as a better-specified working hypothesis: the relevant comparison
is whether an intervention should be valued by expected future portfolio
operation rather than solely observed routing failure frequency and quality
gap. No novelty claim follows. RQ0 remains the only official research question.

### Next action

Develop a minimal model and a synthetic falsification experiment only after
documenting their assumptions. Neither is started by this decision.

## Decision 003 — Formalization of M0

Date: 2026-09-14.

### Decision

Formalize `models/model_M0.md` as a deliberately minimal working model for H1.
M0 distinguishes observed failure severity, learnability, and downstream
operational value without claiming to be the final HLS model.

### Result

M0 values an intervention as:

```text
V_z = -K_z + A_H p_z ell_z [g_z - m_z]_+.
```

It supplies a rank-reversal construction in which a frequency-gap baseline
selects a different region from downstream operational value, and a
perfect-gap-closure special case in which the quality gap cancels from the
conditional downstream value. These results support mathematical coherence of
H1, but are not by themselves considered a sufficient research contribution.

### Limitations and next action

M0 excludes cross-competence effects, forgetting, transfer, and realistic
routing uncertainty. The next planned critical analysis is M1: vector-valued
competence changes and interference. M1 is not formulated or started here.

## Decision 004 — M0 implementation and canonical regime verification

Date: 2026-09-14.

### Decision

Create the minimal computational laboratory for M0: pure model functions,
unit tests, a reproduction of the documented rank-reversal example, and a
reproducible equal-parameter regime sweep.

### Result

The formulas are numerically verified and the documented rank reversal is
reproduced. The canonical sweep is restricted to `m_z > 0` (`delta_z > c`) so
that it does not mix regions where the cheap model already routes. Within the
strict switchable band `c < delta_z < c + g`, it confirms the opposite
monotonicity of frequency-gap score and M0 intervention value when the other
region-level parameters are equal. This is an M0 structural observation caused
by its fixed gain and deterministic switching threshold, not a general result.

### Limitations and next action

Ties and non-switchable regions are recorded separately rather than being
labelled as rank reversals. The next scientific decision is analysis of M0
results before any M1 work; M1 is not implemented or started here.

## Decision 005 — Analytical M0.1 gap-dependent learning response

Date: 2026-09-14.

### Decision

Interpret the M0 computational result critically: its 75.953% strict
rank-reversal fraction is grid geometry under a selected parameter range, not
an empirical prevalence estimate. The fixed conditional gain is an important
structural assumption of that result. Document `models/model_M0_1_gap_dependent_learning.md`
as an analytical extension of M0, not as M1 or a new complete model.

### Result

M0.1 permits gain, learnability, and training cost to depend on the observed
quality gap. Within a strictly switchable interval, its central derivative is:

```text
V'(delta) = -K'(delta) + A_H p [ell'(delta) h(delta) + ell(delta)(g'(delta)-1)].
```

The theoretical objective is therefore reframed from showing that a
frequency-gap score can fail to characterising the assumptions under which it
is, or is not, a useful proxy for downstream intervention value. No novelty or
empirical claim follows.

### Next action

Perform a narrow computational verification of the analytical response
families, beginning with linear gain `g(delta)=a+b delta` and its boundary at
`b=1`. M1 remains deferred; do not restart broad horizontal literature search.
