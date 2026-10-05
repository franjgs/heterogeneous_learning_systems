# HLS Role Handover — Chief Engineer — REPLACE

**Baseline:** `87418dd73e4f7363a139f6f0794f55f2a48c5306`
**Branch:** `main`
**Date:** `2026-10-05`
**Status:** `PENDING_ACCEPTANCE`

## ROLE

**Outgoing Chief Engineer:** `OUTGOING`; responsible identifier is not
materialized in repository sources.
**Incoming Chief Engineer:** `PENDING`; responsible identifier is to be
registered after acceptance.

This transfer is authorized as a `REPLACE CHIEF ENGINEER` governance
operation. It does not itself alter scientific authority or make the incoming
CE agree with the outgoing CE's interpretations.

## MISSION

The incoming CE coordinates HLS's scientific architecture and the trace from
theory through experiment, evidence, and publication. It integrates scoped
expert work, enforces PI doctrine and source authority, and stops work that
violates frozen scope or documented reductions. Its first artifact is the CE
acceptance report required by the [Team Handover Protocol](../HLS_TEAM_HANDOVER_PROTOCOL.md#8-replace-chief-engineer).

## AUTHORITY / SCOPE

**May decide:** repository-grounded coordination, sequencing, source and WIP
classification, scoped expert integration, and stopping work inconsistent with
PI doctrine or established reductions.

**Must escalate:** changes to PI doctrine, major changes of scientific
direction, reopening a frozen direction, material contradictions in canonical
sources, or any decision requiring an unmaterialized chat-only authority.

**Must not decide:** override PI doctrine or canonical evidence; promote WIP,
literature, or publication drafts to canonical status; reinterpret a
falsification; or infer a new claim merely from policy-class inclusion.

## PROJECT QUESTION

HLS studies how heterogeneous, limited, and evolvable collective capabilities
should be organized and developed over time as problems and needs change
([Philosophy](../../HLS_PHILOSOPHY.md), [Current State](../../HLS_CURRENT_STATE.md)).
The sole official current research question is RQ0: whether dynamic allocation
and development can improve long-term performance relative to architectures
that manage allocation and transfer separately
([Research Questions](../../research_questions.md)).

## PI DOCTRINE

The governing methodology is **REDUCE BEFORE INVENTING. BUY BEFORE
REBUILDING. ASSEMBLE BEFORE EXTENDING**. Import established theory where it
solves a valid HLS component; map it to the ontology; extend only where a
demonstrated scientific need remains. Results, mechanisms, and experiments do
not redefine HLS ([Research Doctrine](../../../RESEARCH_DOCTRINE.md)).

The current PI decision recorded in Current State is:

> **SEARCH FOR A NOVEL BEAM-1 × BEAM-2 INTEGRATION MECHANISM: CLOSED.**

The current target is **CHARACTERIZATION / ASSEMBLY**, not a new local
integration score, certificate, equation, or dynamic theory. The incoming CE
may challenge this strategy, but must state the new evidence, assumption,
dependency, or argument that warrants reopening it.

## CANONICAL BASELINE

**HEAD / branch:** `87418dd73e4f7363a139f6f0794f55f2a48c5306` on `main`.

**Worktree:** clean (`git status --short` produced no entries at preparation).

**Relevant baseline history:** `8972c3c` closed the canonical G3-H C1/C2
audit boundary; `89d5a78` recorded the repeated Beam-1 × Beam-2 integration
dead ends; `2912ca3` consolidated the then-current documentation, diagnostics,
code, tests, and artifacts; `87418dd` added this governance infrastructure.
Read sources by authority, not commit chronology.

**Sources consulted:**

- [Repository Guide](../../REPOSITORY_GUIDE.md) — authority, provenance,
  implementation map, and documentation debt;
- [HLS Philosophy](../../HLS_PHILOSOPHY.md),
  [Research Doctrine](../../../RESEARCH_DOCTRINE.md),
  [HLS Ontology](../../hls_ontology.md), and
  [Research Questions](../../research_questions.md);
- [HLS Current State](../../HLS_CURRENT_STATE.md) and
  [Theory Registry](../../theory/README.md);
- static/dynamic theory and G1/G2 sources identified by the guide;
- [Minimal Reference Scenario](../../experimental_foundations/HLS_MINIMAL_REFERENCE_SCENARIO.md),
  [Minimal Reference Information Audit](../../experimental_foundations/HLS_MINIMAL_REFERENCE_INFORMATION_AUDIT.md),
  and [G3 Organizational-Value Ground Truth](../../experimental_foundations/HLS_G3_ORGANIZATIONAL_VALUE_GROUND_TRUTH.md);
- [RQ0 Routing Integration Boundaries](../../theory/rq0_routing_integration_boundaries.md),
  [G0](../../experiments/G0.md), relevant RQ0 protocols, and
  [History](../../HISTORY.md), especially §10.

**Excluded or classified WIP:** none in the clean worktree. The following are
tracked but are **not automatically canonical system state**: post-baseline
G3-H diagnostic code/results, the placement-value literature audit, and the
frozen `hls_foundations_v02` publication material. Use their documented
authority labels; do not promote them by directory presence.

**Known contradictions or gaps:**

- The Repository Guide's post-baseline G3-H row still says “WORKING /
  UNTRACKED,” while related diagnostics were committed in `2912ca3`; their
  non-canonical scientific status remains explicit, but their tracking/status
  wording requires future documentation reconciliation.
- The guide records further documentation debt: older Synthetic Environment
  wording, RQ0 campaign priority language, some protocol-to-artifact
  relations, absent B23 paths, and incomplete experiment-registry indexing.
- No named PI, CE, or expert identity was established in repository sources;
  governance identities remain `UNKNOWN / TO BE INITIALIZED`.

## ESTABLISHED RESULTS

The following are source-scoped evidence, not a universal HLS theory:

- **CONSOLIDATED / SCOPED:** Beam 1 T0–T3 and G1 establish the stated static
  capability, organization, and sufficiency boundaries. Beam 2 T4–T6 and G2
  provide the stated dynamic scaffold and D0/D1/D2 reference results. Read
  their linked sources in the guide for exact scope.
- **CANONICAL ESTABLISHED:** the Minimal Reference Scenario and its
  information audit establish their declared 2×2×2 scenario and information
  partition/reduction boundaries.
- **CANONICAL ESTABLISHED:** G3 gives an exact, standard
  assignment-sensitivity reduction for one-step organizational development
  value. G3-H changes only to fixed heterogeneous worker learning rates and
  supplies the audited local-versus-future ranking counterexample.
- **CANONICAL ESTABLISHED:** C1 is falsified because `max D` loses future
  reward and the joint future `R`–`D` trade-off; C2 restores explicit
  look-ahead/DP rather than an intermediate HLS mechanism.
- **CANONICAL FOR THE STATED RQ0 FORMALIZATION:** under common world and
  information, `Pi_SEP` is a restricted subset of `Pi_HLS`; finite-exact
  strictness relative to strong SEP holds iff no HLS-optimal policy is
  strong-SEP admissible. The scoped `C(alpha)` family establishes strict value
  only on `5/16 < alpha < 1/2`; SEP-Omega is the sufficient-continuation
  coordination/reducibility boundary.

## NON-CLAIMS

The repository does not establish universal superiority of HLS, heterogeneity,
specialization, adaptation, or joint management; prevalence, genericity,
robustness, or empirical realism of the synthetic integration window; a
universal dynamic HLS model; or superiority over sufficiently informed modular
control. Policy inclusion alone is not substantive HLS advantage. G3/G3-H do
not establish a novel HLS architecture, irreducibility, or an exact local
continuation representation. See Current State §§7–10 and the cited ground
truth sources.

## REDUCTIONS / FALSIFIED DIRECTIONS

- **FALSIFIED:** C1 development-only future opportunity preserves the wrong
  G3-H ranking.
- **REDUCTION TO STANDARD DYNAMICS:** C2's exact correction is
  look-ahead/DP.
- **HISTORICAL / NON-CANONICAL:** local `g,rho,m`, regime, stability,
screening, and continuation-relevance lines did not establish an exact local
certificate; C-stability is unresolved, not falsified or proved.
- **HISTORICAL REDUCTION — STOP:** matched-`Delta S` would provide cleaner
  causal identification, not a missing theoretical dependency. It was not
  executed and must not be relabelled as prior evidence.

Before reopening a Beam-1 × Beam-2 mechanism direction, apply History §10.4's
missing-dependency gate. A new proposal must identify a required dependency
that is not implied by organizational value/assignment sensitivity, `F(S,a)`,
standard continuation/DP, and the relevant policy-class restriction, and must
be falsifiably testable.

## FROZEN DECISIONS

- Do not silently redefine HLS around a current mechanism, RQ0, G0, or a
  policy comparison.
- The novel Beam-1 × Beam-2 integration-mechanism search is closed pending
  explicit PI reopening on a genuinely new basis.
- Do not relaunch the local-versus-continuation loop under labels such as
  continuation score, stability certificate, selective continuation,
  metareasoning, pruning, or organizational screening when exact validation
  reconstructs continuation/look-ahead.
- Do not create progressively narrower causal controls merely because they
  identify an already represented dependency more cleanly.
- Do not treat literature, publication drafts, protocols, directories, or
  post-baseline diagnostics as canonical without an explicit promotion.

## OPEN QUESTIONS

- **CANONICAL CURRENT:** RQ0 remains open within its declared scope; its
  structural characterization, robustness, and empirical relevance are not
  established.
- **PI DIRECTION / CURRENT HYPOTHESIS:** characterize when `R0` USE is
  sufficient, `R1` development is relevant but separable, and `R2` joint
  intertemporal management is relevant. These are directions for
  characterization, not theorem-level boundaries or an established ladder.
- **CANONICAL FOUNDATIONAL GAP:** a sufficiently complete operational
  performance and fair resource-constraint definition for the next reference
  problem remains open.
- **DOCUMENTATION GAP:** resolve only through evidence-backed maintenance the
  authority/track-status wording and other debt listed above.

## INTERFACES

| Role | Input received | Output owed | Escalation condition |
| --- | --- | --- | --- |
| PI | Doctrine, strategic decisions, authorization to reopen frozen directions | Evidence/interpretation distinction, decision-ready escalations | Direction, doctrine, or frozen-boundary change |
| Outgoing CE | Repository-grounded transition package; no authority beyond recorded sources | Transfer complete pending incoming acceptance | Any conflict between package and canonical sources |
| Expert / Beam Owner | Explicit scoped mission, canonical sources, stopping criteria | Auditable result including reductions, failures, contradictions, and WIP status | Scope or architecture expands beyond mandate |
| Handover Steward | Repository, protocol, and role register | Baseline/WIP audit; role-specific package; acceptance record | Missing/contradictory authority or chat-only decision |

## CURRENT TASK

The incoming CE's immediate authorized task is **acceptance and independent
reconstruction**, not new scientific research. It must read the sources below,
audit this package against them, and return the required acceptance report.
Stop and escalate to the PI if a required authority or canonical source is
materially ambiguous. No scientific direction is selected by this handover.

## REQUIRED READING

1. [HLS Philosophy](../../HLS_PHILOSOPHY.md)
2. [Research Doctrine](../../../RESEARCH_DOCTRINE.md)
3. [HLS Ontology](../../hls_ontology.md)
4. [Research Questions](../../research_questions.md)
5. [HLS Current State](../../HLS_CURRENT_STATE.md)
6. [Repository Guide](../../REPOSITORY_GUIDE.md), including authority map and
   documentation debt
7. [Theory Registry](../../theory/README.md), then static/dynamic theory and
   G1/G2 sources it identifies
8. [Minimal Reference Scenario](../../experimental_foundations/HLS_MINIMAL_REFERENCE_SCENARIO.md)
   and [Information Audit](../../experimental_foundations/HLS_MINIMAL_REFERENCE_INFORMATION_AUDIT.md)
9. [G3 Organizational-Value Ground Truth](../../experimental_foundations/HLS_G3_ORGANIZATIONAL_VALUE_GROUND_TRUTH.md)
10. [RQ0 Routing Integration Boundaries](../../theory/rq0_routing_integration_boundaries.md)
    and [G0](../../experiments/G0.md)
11. [History](../../HISTORY.md), especially §10 before proposing an integration
    mechanism or causal refinement
12. Relevant protocols, code, tests, result manifests, literature, and
    publication drafts only when the accepted task requires their provenance.

## OUTGOING MEMBER MATERIAL

This package is the outgoing transfer reconstructed from repository sources.
No named outgoing CE report, personal interpretation, or chat transcript was
materialized in the repository; this absence is recorded rather than filled by
inference. The outgoing position that is evidence-backed is the authority map,
Current State, and History §10. Interpretive recommendations beyond those
sources are deliberately not transferred as facts.

## INCOMING CONFIRMATION

Before acceptance, the incoming CE must submit the protocol's written
acceptance report: accepted baseline/branch; reconstructed project question;
established claims and non-claims; reductions/failures; PI direction; WIP;
contradictions/gaps; independent diagnosis; one first recommended action; and
only necessary escalations to the PI. It must state any disagreement with the
outgoing interpretation and identify the new evidence, assumption, dependency,
or argument required to reopen a closed direction.

Until that report is accepted, this handover remains `PENDING_ACCEPTANCE`, the
outgoing CE remains `OUTGOING`, and the incoming CE remains `PENDING`.
