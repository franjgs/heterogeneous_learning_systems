# Placement-value literature audit: Beam 1–Beam 2

**Status:** SUPPORTING literature audit, not a canonical theory source  
**Question:** whether the collective value of the same competence increment can
depend on the worker who receives it:

$$
\Delta V_{ik}=V(S+\delta e_{ik};P,B,\Pi)-V(S).
$$

**Method:** adversarial reduction audit.  The question is mapped to each
source's stated objects before drawing any HLS conclusion.  It neither asserts
novelty nor changes T0--T6, G1, or the HLS ontology.

## Executive verdict

**Classification: C — partial reduction.**  Existing workforce-flexibility,
assignment, training, and dynamic-matching models establish most of the
ingredients separately, and some directly optimize worker--skill development
choices.  In particular, Sayın--Karabatı and De Bruecker et al. reduce
domain-specific versions of the placement question to established optimization;
Nembhard--Bentefouet and Baccara--Lee--Yariv establish assignment--learning
couplings under their respective learning structures.

They do **not**, on the evidence reviewed here, establish a general
worker-indexed result for the displayed \(\Delta V_{ik}\) across arbitrary
collective-capability criteria, common future conditions, constraints, and
policy classes.  That absence is not evidence of novelty.  It is a boundary:
any HLS use of the expression should be an explicit adaptation or a
model-scoped measurement, and should first attempt reduction to the relevant
assignment/training model.

**Recommendation: REFORMULATE.**  Do not pursue the placement question as an
unqualified HLS novelty claim.  State it, if needed, as a comparative-value
interface between a fixed-competence allocation model and an imported dynamic
training/assignment model, with the source-specific assumptions made explicit.

## Adversarial comparison

| Source | Competence / skills | Organizational decision | Skill location and differential placement value | Development and worker dependence | Explicit link from placement to who develops? | Reduction result |
| --- | --- | --- | --- | --- | --- | --- |
| Campbell (1999) | Worker--department capability parameters in \([0,1]\); fractional values mean less than fully qualified. | Allocate cross-trained workers to departments at a shift's start. | **Yes** for current capability: it is indexed by worker and department.  It values a worker's current placement, not an increment to that worker's future competence. | No acquisition or training state. | No. | Static Beam-1 reduction only. |
| Jordan--Graves (1995) | Plant--product production flexibility, not worker competence. | Configure product--plant flexibility/capacity links under demand uncertainty. | **Yes** for capability location at plants, but only as an aggregate network analogue. | No development. | No. | Imports a capacity/flexibility geometry analogue, not the worker-placement question. |
| Sayın--Karabatı (2007) | Cross-trained workers' department-specific skills; improvement follows a hyperbolic learning curve. | First maximize departmental utility; then maximize total skill improvement while retaining the first-stage utility level. | **Yes**: assignment and skill improvement are worker--department indexed.  A different recipient can yield a different modeled improvement. | Development is endogenous to assignment and current skill; the reported formulation is not an explicit discounted continuation-value model or training-cost model. | **Partly**: it explicitly chooses assignments with skill improvement, but its sequential objective is not \(V(S+\delta e_{ik};P,B,\Pi)-V(S)\). | Specific workforce-assignment reduction; not a general proof about collective future value. |
| Nembhard--Bentefouet (2015) | Worker productivity incorporates individual learning-by-doing and knowledge transfer parameters. | Select workers, group them, and assign groups to tasks to improve system throughput. | **Yes**: worker-specific learning/transfer characteristics make organization and future productivity recipient-sensitive. | Yes; own experience and transfer are modeled with individual characteristics.  The paper compares policies/heuristics and a nonlinear-programming upper bound. | **Partly**: it connects assignment to learning and throughput, but does not state the common-future-conditions marginal collective-value operator above. | Strong imported dynamic-assignment comparator; partial reduction. |
| De Bruecker et al. (2018) | Worker licenses/skills and a desired workforce skill mix. | Jointly choose skill mix, workforce schedule, and a feasible worker--skill training schedule for aircraft maintenance. | **Yes**: skills are located in workers; the model chooses who is trained for which skill and evaluates consequences for feasible schedules. | Yes; explicit training costs and temporary worker unavailability.  It is training, not learning-by-doing. | **Yes, domain-specifically**: recipient and skill are decision variables because they affect future scheduling cost/feasibility. | Specific domain reduction of a worker--skill development choice. |
| Baccara--Lee--Yariv (2023) | Providers are junior or senior; expertise evolves endogenously through on-the-job training. | Dynamic allocation of arriving clients/tasks, comparing centralized protocols with discretionary selection. | Location is at provider type/mass rather than an arbitrary named worker--skill matrix; within-type recipients are symmetric. | Yes; service opportunities train juniors and alter future expertise; waiting/service-quality trade-offs matter. | **Yes** for junior-versus-senior task allocation, but not for an arbitrary worker-indexed skill increment. | Strong dynamic allocation--training reduction with a coarser state than \(e_{ik}\). |

### What the closest models already explain

1. **Current collective capability is location-sensitive.**  Campbell's
worker--department matrix and Jordan--Graves' plant--product network both show
that the same aggregate amount of capability need not have the same operating
value when it resides at different admissible locations.  The second is only an
analogy until a worker--plant mapping is specified.
2. **Placement can be development-sensitive.**  Sayın--Karabatı makes skill
improvement part of assignment; Nembhard--Bentefouet uses worker-specific
learning and transfer; De Bruecker et al. choose recipients of training; and
Baccara--Lee--Yariv makes task allocation determine endogenous expertise.
3. **The present/future trade-off is established methodology.**  Baccara--Lee--
Yariv directly studies it dynamically.  De Bruecker et al. trade training cost
and availability against later schedule cost; Sayın--Karabatı protects an
immediate utility level before maximizing improvement.  None licenses a claim
that the T6 decomposition or the HLS Relevance Cascade is new mathematics.

## Beam mapping and import boundary

### What Beam 1 may import directly

- From Campbell: worker--task capability matrices and assignment constraints
  as an established static representation of heterogeneous cross-utilization.
- From Jordan--Graves: the structural lesson that constrained capability links
  and their topology affect collective operating value under demand variation.
  This is a **RELATED**, not equivalent, mapping: plants/products are not
  workers/competences.
- From Sayın--Karabatı: a lexicographic or constrained comparison between
  present departmental utility and modeled worker--department skill
  improvement, when that exact decision semantics is adopted.

### Beam 1–Beam 2 interface already covered

The interface "present allocation \(\rightarrow\) worker-indexed competence
state \(\rightarrow\) later performance" is already covered in scoped forms:

- learning-by-doing and transfer in Nembhard--Bentefouet;
- explicit training recipient/schedule and future roster feasibility in De
  Bruecker et al.;
- task allocation and endogenous provider expertise in Baccara--Lee--Yariv;
- immediate utility plus skill improvement in Sayın--Karabatı.

The remaining work is semantic and model-specific: define the state, future
conditions \((P,B,\Pi)\), learning/training law, capacity constraints, and
criterion before asking whether a named placement increment differs.  It does
not follow from the sources that every competence increment is
recipient-dependent, nor that any such difference changes an optimal present
choice.

### Residual HLS question, if one remains

Under a specified multi-skill, worker-indexed dynamic workforce model, can an
imported solver/evaluator establish whether two equal physical increments
\(\delta e_{ik}\) and \(\delta e_{jk}\) have different collective continuation
values under **common** \((P,B,\Pi)\)?  This is a well-posed adaptation and
measurement question.  It is not currently a demonstrated non-reducible or
novel HLS result.

## Retention and provenance audit

Metadata were checked against the linked publisher or author/repository record
on 2026-10-01.  A local PDF is retained only where the repository already has
an accessible source whose title/authors match the cited work.  "Not retained"
means that this audit did not identify a legal, source-verifiable full text;
it does not imply that no lawful access route exists for a licensed reader.

| Reference | Bibliography action | PDF / provenance action |
| --- | --- | --- |
| Campbell (1999) | Added `campbell1999crossutilization`, verified against the INFORMS record and DOI. | Not retained: publisher record exposes a PDF-download route but this audit did not establish open access. |
| Jordan--Graves (1995) | Added `jordangraves1995flexibility`, verified against the INFORMS record and DOI. | Not retained: MIT hosts a legal **1991 working paper** (`SWP-3296-91`), but it is not represented as the cited 1995 journal version; retaining it under the cited filename would violate the local version convention. |
| Sayın--Karabatı (2007) | Added `sayinkarabati2007crosstrained`, verified against the publisher DOI and bibliographic records. | Not retained: the accessible author-index page requests full text rather than providing it. |
| Nembhard--Bentefouet (2015) | Corrected the existing entry with DOI and canonical DOI URL. | Already retained at `competence_evolution/Nembhard_Bentefouet_2015_Selection_Grouping_Assignment.pdf`; SHA-256 `30129963aa6b69197140552b9431480b7b976d5c3d521eabbe3ec63478402e81`. |
| De Bruecker et al. (2018) | Added `debrueckeretal2018skillmix`, verified against DOI/publisher and bibliographic records. | Not retained: the publisher record indicated purchase/institutional access, and no author/repository full text with clear provenance was found. |
| Baccara--Lee--Yariv (2023) | Existing `baccaraleeyariv2023` was already metadata-complete. | Already retained at `cross_cutting/Baccara_et_al_2023_Task_Allocation_OnTheJob_Training.pdf`; author-hosted version, 44 pages, SHA-256 `230af14ae06a4896a3f8091668d201b39bcf8a0da12fb83a40bef339a19a22ad`. |

No additional references were retained: these six cover the required static
location, cross-training/assignment, learning-by-doing/transfer, explicit
training, and dynamic-task-allocation comparators.  Adding thematic surveys or
adjacent models would not change the reduction classification.

## Claim discipline

- This audit supports **import / adaptation**, not a new theorem or an HLS
  exclusivity claim.
- The HLS Relevance Cascade remains a structural screen.  These sources may
  instantiate parts of it; they do not turn it into a new DP result.
- A future model may find \(\Delta V_{ik}=\Delta V_{jk}\), a nonzero
  difference, or a difference with no decision consequence.  Each outcome is
  model-scoped and must be evaluated under common future conditions.
