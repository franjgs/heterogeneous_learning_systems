# Retrospective B2.1–B2.2 portfolio bridge

Status: **HALTED — COUNTERFACTUAL INCOMPATIBILITY**.

This is a retrospective bridge audit, not part of the preregistered B2.2 protocol. It used only stored VALIDATION results and did not train models or access TEST.

## Compatibility gate

The candidate universe contains 90 learned `seed × N × pair` states and 1800 possible `seed × N × pair × c × B` valuations. None is admissible for the requested bridge:

- B2.1 and B2.2 `S(F0)` agree in 0/5 seeds; maximum component differences range from 0.021582 to 0.124772.
- B2.1 and B2.2 `S(D)` agree in 0/5 seeds; maximum component differences range from 0.013191 to 0.048583.
- Singleton vectors agree in 0/60 interventions at tolerance `1e-12`; their maximum component differences range from 0.009324 to 0.348962.
- Therefore compatible factorial states: 0/90; compatible analytical observations: 0/1800.

Both runners nominally use the same manifest, split routine, selection seed formula, architectures, optimizer parameters, three epochs, and VALIDATION evaluation. B2.2 stores its selected IDs; B2.1 did not store selected IDs, pseudo-labels, model fingerprints, checkpoints, manifest hash, or implementation hash, so equality of its realized inputs cannot be demonstrated from the artifacts.

The concrete training-path difference is that B2.2 calls `seed_everything(training_seed)` before every singleton update, while B2.1 only seeds the DataLoader shuffle generator. Random crop/flip state in B2.1 therefore depends on the preceding execution order. The independently retrained B2.1 and B2.2 base states also differ, and B2.1 lacks the provenance needed to attribute that base divergence further. Because D differs, equality of realized pseudo-labels is not established.

## Scientific stop

Per the declared compatibility rule, `rho_i`, `rho_j`, `DeltaV_i`, `DeltaV_j`, `DeltaV_ij`, `Gamma_oper`, `H_i`, `H_j`, and `H_ij` were not combined across B2.1 and B2.2. `portfolio_bridge_raw.csv`, reproducibility, and representative cases therefore contain zero eligible rows.

This does **not** mean that zero portfolio rescues exist. It means the existing runs cannot identify whether `H_i<0`, `H_j<0`, and `H_ij>0` hold for matched counterfactual states. No claim about accumulated-opportunity portfolio value or RQ0 follows from this retrospective bridge.

## What is observed

- The stored result vectors are numerically incompatible at the base and singleton levels.
- Nominal grids, domain definitions, selection rule, CPU device, VALIDATION evaluation, and TEST closure agree.
- No eligible state remains after the counterfactual compatibility gate.

## Supported interpretation

The B2.1 factorial interaction and B2.2 absolute opportunity values belong to separately trained realizations. Combining their states as though they shared F0, D, pseudo-labels, and singleton updates would create an invalid counterfactual.

## Not demonstrated

- existence or absence of portfolio rescue;
- reproducibility of rescue across seeds;
- sequential accumulation value;
- an ex-ante opportunity-accumulation policy;
- a stronger RQ0 mechanism, TEST generalization, HLS superiority, or novelty.
