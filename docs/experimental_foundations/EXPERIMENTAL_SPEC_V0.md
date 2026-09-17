# HLS Experimental Foundation — Frozen Specification v0

Status: FROZEN BASELINE
Purpose: reproduce selected results from current primary references for Beam 1 and Beam 2, and verify a minimal executable interface before any HLS-specific extension. This frozen specification predates the canonical ontology; its `x_t` identifies normalized real work with learning exposure as a declared special case, not a general equivalence.

## Beam 1 — Garicano reproduction block

| ID | Target | Conditions | Reproduction criterion |
|---|---|---|---|
| B1.1 | Autarky | Problem distribution F, density f, knowledge interval [0, Za], marginal acquisition cost c | Numerical optimum agrees with f(Za)=c within solver tolerance. |
| B1.2 | Specialization | Production and helping roles allowed | Optimal organization has one producing class; remaining classes specialize in problem solving/help. |
| B1.2b | Non-overlapping knowledge | Base Garicano assumptions | Optimal knowledge intervals assigned to different classes do not overlap. Secondary check. |
| B1.3 | Organization by frequency | Distributed knowledge + helping cost h | Production workers cover the most frequent problems; successive problem solvers cover increasingly exceptional problems. |
| B1.4 | Pyramidal organization | Multiple layers | Layer sizes satisfy b_(i+1) < b_i. |

## Beam 2 — Gutjahr reproduction block

Core dynamics:

z_it = z_i1 - beta_i (t-1) + eta_i sum_(s<t) x_is
gamma_it = phi(z_it)

| ID | Target | Conditions | Reproduction criterion |
|---|---|---|---|
| B2.1 | Competence dynamics | Fixed x, eta, beta, phi | Simulated z_it and gamma_it agree with the analytical equations within numerical tolerance. |
| B2.2 | Extremal policy under convex learning | Assumptions of Gutjahr Theorem 2 | Recover an optimal policy assigning all capacity in each period to one class. |
| B2.3 | Mixed portfolio | Non-convex regime / Gutjahr counterexample | Recover a case in which a mixed/interior allocation strictly improves on the relevant extremal alternatives. |
| B2.4 | Persistence without forgetting | beta_i=0, eta_i>0, w_i>0, phi strictly increasing; extremal decisions | Recover an optimum (e_i*,...,e_i*) as in Theorem 3. |
| B2.5 | Audit switching with forgetting | Published parameters and equations from Gutjahr Example 3 | Preserve `FAILED_SOURCE_REPRODUCTION`: literal evaluation gives objectives 2.0, 1.5, 0.5, 1.5 and does not recover the paper's claimed switching optimum. |

## Beam 1 + Beam 2 — Integration tests

Historical executable interface used by B12:

(F_t,S_t) --R--> a_t --X--> x_t --L--> S_(t+1)

Current general documentation instead requires `a_t --W--> w_t --E--> e_t --L--> C_(t+1)` with explicit mappings. The B12 implementation is the special case in which assigned normalized work supplies the exposure variable.

| ID | Target | Conditions | Reproduction criterion |
|---|---|---|---|
| B12.1 | Closed feedback | Beam 1 produces a_t; execution produces x_t; Beam 2 updates S_(t+1) | Every transition is explicit, dimensionally/semantically consistent, and numerically executable. |
| B12.2 | Recover Beam 1 | eta=0 / no competence evolution | Combined implementation agrees with Beam 1 baseline. |
| B12.3 | Recover Beam 2 | Remove/fix routing and provide x_t directly | Competence trajectory agrees with Beam 2 baseline. |
| B12.4 | Effective coupling | eta>0 and allocation depends on competence | Exhibit a non-degenerate parameter region where changing a_t changes x_t, hence S_(t+1), and this changes a_(t+1). |

## Rules

1. No Large Language Models or real Machine Learning models yet.
2. No new mechanism is introduced merely to make B12.4 work.
3. Beam-specific notation keeps the semantics of the source model.
4. Common notation is introduced only at the interface.
5. Each experiment must have: source result, assumptions, parameters, expected result, numerical tolerance, and pass/fail outcome.
6. A failed reproduction is investigated before extending the model.
7. B12.4 must be tested over a parameter region, not demonstrated by one hand-picked point only.
8. No claim of HLS superiority follows from passing these tests.
