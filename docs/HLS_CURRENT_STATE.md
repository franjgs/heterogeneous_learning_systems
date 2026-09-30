# HLS Current State

This is the single canonical summary of the programme's present scientific
state. Frozen protocols, detailed derivations, executable code, and result
artifacts remain authoritative for their own scope; this file does not replace
them.

## 1. Current scientific question

RQ0 is the sole promoted research question:

> Can the dynamic allocation and development of competences in a heterogeneous
> learning system improve long-term system performance compared with
> architectures that manage task allocation and knowledge transfer separately?

RQ0 remains open. At programme level, it asks when the interaction between the
organization/use of current competences and the development/evolution of future
competences has system-level value, and when the two can instead be managed
separately or through sufficient coordination.

The current exact and synthetic work studies a narrower routing/development
instantiation of this question. Within that formalization, the objective is to
determine when joint routing/development has strict value over a scientifically
strong separated architecture, and when separation or sufficient coordination
reproduces the joint value.

## 2. What is established

### Programme and policy classes

- HLS is a collective of heterogeneous, limited, and evolvable competences;
  the common semantic contract is in [the ontology](hls_ontology.md).
- Under common world physics and information, strong SEP is a restricted
  policy class of HLS policies. Therefore
  `Pi_SEP ⊆ Pi_HLS` and `J_SEP,max <= J_HLS`.
- In the finite exact setting, strict value relative to strong SEP occurs iff
  no HLS-optimal policy is strong-SEP-admissible on its positive-probability
  support. A local non-greedy Bellman action alone is insufficient.
- The local identity `Q(b)-Q(g) = -DeltaR + DeltaP D*` is exact under its
  stated one-step factorization, but is not a global integration criterion.

The formal source is [RQ0 routing integration boundaries](theory/rq0_routing_integration_boundaries.md).

### Synthetic framework

- G0 is implemented and passed its architecture and A1 compatibility gates.
- A1 is closed/pass: A1a exact worlds, A1b 1,020 preregistered boundary
  configurations, and A1c 458 competence-geometry configurations.
- C1--C5 are implemented and passed their reference gates on the common,
  policy-neutral G0 framework. C6--C8 are not implemented.
- The synthetic framework is an instrument for testing mechanisms and
  boundaries; it is not itself evidence that HLS wins.

The current framework contract is in [G0](experiments/G0.md); the exact A1
reference specification and compatibility record remain in the frozen
[synthetic environment record](experimental_foundations/HLS_SYNTHETIC_ENVIRONMENT.md).

### Exact and synthetic RQ0 results

- A1 World E and C1 R5 are constructive, exact existence cases relative to
  strong SEP. They do not establish prevalence or superiority over SEP-Omega.
- The original eta=.5 diagnostic found physically reachable local routing
  inversions that were off every HLS-optimal root continuation. Constrained
  reachability and demand-persistence audits therefore established a local
  mechanism without a global root-value result in that family.
- The frozen routing-to-opportunity lambda family was SEP-reducible at all 21
  points. Persistence strengthened local incentives in its tested worlds but
  did not remove the observed global barrier.
- The frozen zero-sum competence redistribution family
  `C(alpha)=((4/5,4/5-alpha/5),(3/5,3/5+alpha/5))` gives the exact
  model-scoped result

  ```text
  Phi(alpha) = 0                         for 0 <= alpha <= 5/16
               3 alpha/10 - 3/32         for 5/16 < alpha < 1/2
               0                         for 1/2 <= alpha <= 1.
  ```

  Thus it establishes existence of strict integration relative to strong SEP
  on the open interval `5/16 < alpha < 1/2`.
- `alpha=5/16` is a Bellman inversion boundary. `alpha=1/2` is a
  greedy-admissibility boundary: the required action enters the SEP greedy
  set. These are properties of this family, not universal boundaries.
- SEP-Omega equals HLS in the audited A1, A1b, A1c, lambda, and geometry
  families within the declared tolerance. This is a coordination/reducibility
  boundary, not an independent algorithmic benchmark.

## 3. What is not established

The repository does not establish prevalence, genericity, robustness, or
empirical-realism of the synthetic integration window. It does not establish
that complementarity, specialization, persistence, or stronger coupling is
sufficient for integration. It does not establish intrinsic superiority over
every sufficiently coordinated modular architecture, and it does not transfer
the C(alpha) interval to all G0+C1--C5 worlds or to real systems.

The PACS and Office-Home records are scoped vehicle and mechanism evidence,
with negative/inconclusive outcomes where stated; they are not general RQ0
validation.

## 4. Current structural understanding

Within the current finite exact routing/development formalization, the analysis
distinguishes three levels:

1. physical/local non-separability: a state admits a Bellman-optimal
   non-greedy action;
2. on-policy non-separability: an HLS-optimal policy uses such an action on
   its own positive-probability support;
3. irreducible integration relative to strong SEP: every HLS-optimal policy
   does so.

Only the third level implies `J_HLS > J_SEP,max` in the finite exact setting.

SEP-Omega demonstrates that the positive result is about the strong-SEP
contract, especially its routing objective and continuation information, not
about centralization versus modular software as such.

These distinctions characterize the current formal treatment of RQ0. They are
not definitions of HLS itself and need not constitute the appropriate
formalism for other HLS organization/development mechanisms.

## 5. Open questions in the current structural analysis

The following are open questions of the current routing/development
formalization, not an exhaustive statement of the open scientific questions of
HLS:

- Which physical transition, opportunity, and support-tree properties make
  `Pi_H^*(S0) ∩ Pi_SEP` empty or non-empty?
- When do parametrized families contain one, several, or no open regions of
  irreducible integration?
- Which conclusions survive beyond the frozen synthetic mechanisms without
  adding realism merely for its own sake?

No new experiment is implied by this summary.

## 6. Current research position

The programme is in theoretical consolidation after the exact synthetic
existence result. RQ0 is `OPEN`; existence under the exact model and
strong-SEP contract is `YES`, while structural characterization,
robustness/prevalence, and empirical relevance remain unresolved. C6--C8 are
outside the implemented framework.

The current routing/development formalization is therefore one active route
for investigating RQ0, not a restriction of the broader HLS programme to that
formalism.

## 7. Evidence pointers

- Question: [research_questions.md](research_questions.md)
- Method: [RESEARCH_DOCTRINE.md](../RESEARCH_DOCTRINE.md)
- Semantics: [hls_ontology.md](hls_ontology.md)
- Formal theory: [rq0_routing_integration_boundaries.md](theory/rq0_routing_integration_boundaries.md)
- Synthetic contract: [G0.md](experiments/G0.md)
- A1/C1--C5 gates: [HLS_SYNTHETIC_ENVIRONMENT.md](experimental_foundations/HLS_SYNTHETIC_ENVIRONMENT.md)
- Campaign chronology: [RQ0_EXPERIMENTAL_CAMPAIGN.md](experimental_foundations/RQ0_EXPERIMENTAL_CAMPAIGN.md)
- Geometry protocol/outcome: [RQ0_GEOMETRY_REDISTRIBUTION_PROTOCOL.md](experimental_foundations/RQ0_GEOMETRY_REDISTRIBUTION_PROTOCOL.md)
- Coupling protocol/outcome: [RQ0_ROUTING_OPPORTUNITY_COUPLING_PROTOCOL.md](experimental_foundations/RQ0_ROUTING_OPPORTUNITY_COUPLING_PROTOCOL.md)
- Executable synthetic gates: [experiments/synthetic](../experiments/synthetic/)