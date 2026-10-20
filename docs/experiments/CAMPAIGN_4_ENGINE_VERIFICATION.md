# Campaign 4 counterfactual engine — engineering verification

**Status: PREPARATION ONLY. No Campaign 4 sample selection, N=800 evaluation,
or scientific counterfactual experiment was run.** This report verifies the
installed counterfactual engine against frozen Campaign 3 records and records
an important horizon mismatch. It does not authorize Campaign 4 execution.

Audit base repository HEAD: `cec804b00482c5a121bae5434893bc069208484c`.

## Source audit and provenance

Inspected the following implementations and records:

| Source | SHA-256 |
|---|---|
| `experiments/synthetic/campaign3_meta_voc/run.py` | `190344d023d084b028a77c33589bd32897ed4511dccf7fdd9d304cb9cbd93f1f` |
| `experiments/synthetic/campaign3_meta_voc/confirmatory.py` | `4293c15d52e7e839f872c58fe7f76d7f6b2b04943498f28ff408740df4ac5218` |
| `experiments/synthetic/campaign3_fast_deep_meta/run.py` | `aa4c4428ec3b24b523d3169ec11bbbb72cfa3927a0850e51f1bb6df81d69a876` |
| `experiments/synthetic/campaign3_c33/c33.py` | `9f5079d15a0ad4ea356f94ef3d280040a0d96b4abcbda7467f0f6c00e8aee0e1` |
| `experiments/synthetic/campaign3_c32_data/targets.py` | `ebccceb2de3795a51f8224dc402667b09067d8f82e196d3999ee81bad3e8211d` |
| `src/hls/campaign2_theory.py` | `37638c609f31cc6dd5777def3210857990443d26b507f54273a7a2bdec4eb0ff` |
| `src/hls/finite_problem_belief.py` | `6625f1f1c6b8172aea8545074741364298637bd37909bd12113cac00a9e03e99` |
| `src/hls/campaign3_problem_generator.py` | `4bfc16c1f57df71fc097f2876d1f1074cae024f1308e2d0130ddd07a534eb797` |
| `experiments/synthetic/campaign4_counterfactual_deliberation/engine.py` | `3a249df7f96b4913e6eeabd94691662aacea8825d9515c54f72cae3c808c1f10` |
| `experiments/synthetic/campaign4_counterfactual_deliberation/preflight.py` | `df0a2980caa349001a1c2a4d59463fa4bab200d995f524e921f897745ba42efe` |
| `experiments/synthetic/campaign4_counterfactual_deliberation/sampling.py` | `189b68634f5dd85401613e168e18518f4f0a06314b6f4fddbe1c4438291a5286` |

The frozen data hashes were independently recomputed and match the supplied
values: `runs.csv.gz` `3c2d7310a510deed03264b9a6df30ffc09a0af5915cc76dba233d29eadfd9e28`,
`trajectories.csv.gz` `b4022b7a76c2aece607138d6d740ae854517fa171e889d09c557350c8da2e498`,
Ridge model `1874b1f06a7122361677f5bb617132bd2eff3976fd1aa890d7152436fb59ba1d`,
and META-VOC calibration
`bf329147e4e62a98bbfc9ae48c75cbe1066c1ff73b87c6fce6b63cf4f796e94a`.
The preflight also verified 868 histories, 6,944 policy trajectories,
249,984 decision records, 36 records per trajectory, and unique
`(history_id, policy, clock)` keys.

## Verified invariants

The three implemented evaluation horizons use inclusive global decision
clocks:

- H0 ends at `start_clock + 1`: exactly two real decisions.
- H1 ends at the final decision of the current physical problem.
- H2 ends at global clock 36.

The engine uses a forced initial FAST or DEEP action and subsequently calls
the same supplied continuation rule in both branches. It receives one common
latent problem sequence and one clock-indexed innovation mapping; it calls the
real `_real_decision` separately with each branch's own state, action and
belief. Consequently observations are recomputed from branch-specific
`mu_true`, capability transitions are branch-specific, and Bayes updates are
branch-specific. The belief resets at physical problem boundaries; capability
state is not reset. Subsequent terminal decisions route to FAST without a
META-VOC selector or DEEP call. Identical first actions with identical
innovations produce identical physical trajectories in the bounded invariant
test (route bookkeeping differs only in the explicitly recorded initial
`invoked_deep` flag).

FAST delegates to the frozen immediate-action implementation. On the sampled
frozen states, its action exactly matched the original C2 `Q00` operator
(`ProspectivePolicyMode.NONE`), including a symmetric tied-optimum fixture.
FAST and DEEP also selected the same action at `remaining=1`. No Campaign 3
source was changed.

The frozen selector uses the existing `c33.feature_vector` and
`voc.ex_ante_score`/`threshold_route`: six row-major capability entries, three
belief masses, `tau/36`; frozen model normalization, intercept and Ridge
coefficients; predicted-benefit clipping at zero; cost strata 2/3; score
threshold plus SHA-256 feature tie cutoff; and terminal FAST handling. No
fitting, calibration or threshold changes occurred.

The only Campaign 4 engine code change in this audit was a pure
`horizon_end(start_clock, remaining, horizon)` helper used by `rollout` and
`evaluate_pair`. It centralizes the specified H0/H1/H2 inclusive end-clock
calculation for direct testing; it does not change the horizons or transition
logic.

## Frozen-record reconstruction regression

The regression test is deliberately restricted to the two explicitly fixed
histories:

- `campaign3_meta_voc_confirmatory_v1:G1:F01:K01:0`
- `campaign3_meta_voc_confirmatory_v1:G4:F24:K30:0`

Using their recorded seeds and frozen kernels, it reconstructed all twelve
physical problems and all 36 standard-normal observation innovations with the
unchanged Campaign 3 `make_exogenous` implementation. The reconstructed JSON
stream hashes matched each frozen run record. It then replayed every recorded
action under each of the eight policies, resetting beliefs at all problem
boundaries and carrying capability forward.

| Replay check | Result |
|---|---:|
| Transitions replayed | 576 |
| Belief-reset boundaries checked | 176 |
| `state_before`, `belief_before`, `state_after`, `belief_after` discrepancies | 0 |
| Maximum absolute capability/belief discrepancy | 0.0 |
| Maximum absolute `mu_true` discrepancy | `2.220446049250313e-16` |
| Comparison tolerance | `atol=rtol=1e-12` |

The recorded META-VOC-50 decisions were separately checked on these histories:
48 nonterminal rows reproduced the stored prediction, extra-cost estimate,
score and DEEP/FAST route within `1e-12`; 24 terminal rows were recorded as
`FAST_TERMINAL`.

## FAILED equivalence claim: H0 versus the C3.2 training labels

The initial C4 protocol called H0 “target-fidelity” and described it as
matching the original supervised counterfactual target. Inspection of the
actual label generator, `experiments/synthetic/campaign3_c32_data/targets.py`,
shows this equivalence claim is **FAILED**. C3.2 sets `ELL=11` and sums the
current problem remainder plus eleven subsequent complete problems; it does
not sum two real decisions. C3.2 also draws a fresh conditional future
generator continuation and its own paired noise stream. C4 H0 is two real
decisions and H2 is planned to replay the recorded physical stream with
separately keyed innovations.

The C4 protocol was corrected to preserve H0's specified two-decision
estimand, while removing the false training-target equivalence. No C3.2 label,
Campaign 3 result, or H0 horizon was changed. H0 can remain a distinct short
diagnostic, but it cannot serve as same-horizon fidelity validation of the
Ridge target.

## Test suite and commands

Tests are split by purpose:

```sh
pytest -q tests/test_campaign4_counterfactual_unit.py
pytest -q tests/test_campaign4_frozen_regression.py
pytest -q tests/test_campaign4_counterfactual_invariance.py
pytest -q tests/test_campaign4_counterfactual_unit.py tests/test_campaign4_frozen_regression.py tests/test_campaign4_counterfactual_invariance.py
```

The frozen-artifact test calls only the read-only preflight and deterministic
reconstruction/replay on the two listed histories. The invariance suite uses
synthetic fixed problem/innovation sequences and mocked action selection; it
does not launch a sampled campaign or Monte Carlo estimate. No N=800
counterfactual evaluation, target generation, selector training, or new
scientific outcome analysis was performed.

Executed combined command:
`pytest -q -s tests/test_campaign4_counterfactual_unit.py tests/test_campaign4_counterfactual_invariance.py tests/test_campaign4_frozen_regression.py tests/test_campaign3_problem_generator.py` — **22 passed** (12 C4 tests, 10 frozen problem-generator tests).

## Remaining risks and recommendation

| Item | Status | Note |
|---|---|---|
| Frozen C3 source/result hashes | **VERIFIED** | All supplied hashes match. |
| Recorded-stream reconstruction and real-decision replay | **VERIFIED** | Two histories, all eight policies, 576 transitions. |
| Frozen selector reproduction | **VERIFIED** | Selected recorded META-VOC-50 rows only; no fitting. |
| H0 is the C3.2 label horizon | **FAILED** | C3.2 uses `ell=11`, not two real decisions. |
| N=800 selection or execution | **NOT VERIFIED / NOT RUN** | Explicitly outside this task. |
| Scientific adequacy of sampled-state estimands | **NOT VERIFIED** | Engineering replay does not validate the protocol's scientific sufficiency. |

**Recommendation: NO-GO for N=800 execution at this stage.** Before any
execution, the CE/PI should accept H0 as a distinct two-decision diagnostic
rather than a training-target fidelity check, or separately authorize a
scientifically specified same-horizon diagnostic. The latter would be a
design decision, not an engineering repair. H1/H2 mechanics are only
unit-/bounded-tested here; this report makes no claim of Campaign 4 scientific
validity or outcome evidence.
