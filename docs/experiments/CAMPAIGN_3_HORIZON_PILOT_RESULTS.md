# Campaign 3 initial horizon-pilot result

## Scope and provenance

This report closes only the initial frozen `J=12`, five-histories-per-cell
horizon pilot preregistered at commit `a984893`. It is a development-only
temporal diagnostic, not a strategy comparison, policy ranking, state-coverage
study, Gate 1 analysis, Gate 2 analysis, or selector study.

Execution used exactly eight development teams, all 21 `Phi_dev` regimes, and
replicates `0..4`: 168 cells and 840 factual Q11 histories. It generated no
held-out execution and no reserved replicate `5..9` or extended history.

## Integrity

The persisted data contain:

```text
840 factual histories
30,240 factual decision states
241,920 conceptual initial-mode x continuation branch starts
181,440 conceptual mode-vs-Q00 pair starts
1,572,480 problem-indexed branch-return rows
1,179,360 problem-indexed paired-return rows
```

All histories contain 12 problems and three decisions per problem. Validation
found zero factual accumulation error, zero innovation mismatch, zero paired
return reconstruction error, and maximum observation construction error
`2.22e-16`. `mu_true`, not noisy observation, is accumulated; observation
noise remains active in Bayesian updates.

## Primary nested common-support windows

All windows retain all 840 histories. Counts below are per curve—that is, per
mode, continuation, and `ell`.

| Window | Problem indices | Factual states | Label |
|---:|---|---:|---|
| 2 | 1–10 | 25,200 | short |
| 5 | 1–7 | 17,640 | intermediate |
| 11 | 1 | 2,520 | **EARLY-STATE DIAGNOSTIC** |

The table reports each predefined window boundary. Full `ell=0..L`
trajectories, medians, and quantiles are retained in
`common_support_summary.csv`.

| L | Continuation | Mode | ell | mean Delta [95% history-bootstrap interval] | mean delta [95% interval] |
|---:|---|---|---:|---|---|
| 2 | Q00 | Q10 | 2 | .020247 [.017031,.023574] | .002500 [.001910,.003142] |
| 2 | Q00 | Q01 | 2 | .005690 [.004223,.007270] | .002465 [.001838,.003167] |
| 2 | Q00 | Q11 | 2 | .019958 [.016694,.023288] | .002639 [.002061,.003278] |
| 2 | Q11 | Q10 | 2 | .013967 [.011604,.016546] | .000918 [.000348,.001464] |
| 2 | Q11 | Q01 | 2 | .001887 [.000747,.003072] | .000668 [.000129,.001239] |
| 2 | Q11 | Q11 | 2 | .013760 [.011379,.016400] | .001127 [.000530,.001719] |
| 5 | Q00 | Q10 | 5 | .028690 [.024181,.033523] | .002814 [.002023,.003623] |
| 5 | Q00 | Q01 | 5 | .017304 [.012896,.022125] | .003107 [.002226,.004030] |
| 5 | Q00 | Q11 | 5 | .028882 [.024289,.033762] | .002819 [.002021,.003665] |
| 5 | Q11 | Q10 | 5 | .013615 [.009893,.017529] | .000721 [.000070,.001356] |
| 5 | Q11 | Q01 | 5 | .003933 [.001126,.006742] | .000518 [−.000073,.001132] |
| 5 | Q11 | Q11 | 5 | .014025 [.010228,.018001] | .000875 [.000191,.001534] |
| 11 | Q00 | Q10 | 11 | .192561 [.142685,.245621] | .015399 [.010880,.020207] |
| 11 | Q00 | Q01 | 11 | .250665 [.193967,.313137] | .021725 [.016633,.027087] |
| 11 | Q00 | Q11 | 11 | .198265 [.147409,.251540] | .016001 [.011422,.020798] |
| 11 | Q11 | Q10 | 11 | −.003904 [−.023644,.015320] | −.001686 [−.003769,.000381] |
| 11 | Q11 | Q01 | 11 | .044209 [.013410,.077474] | .003511 [.000196,.006838] |
| 11 | Q11 | Q11 | 11 | .002152 [−.017346,.021901] | −.001826 [−.003881,.000221] |

The bootstrap resampled complete histories, used `B=2000`, seed `20261013`,
and two-sided percentile intervals. Decisions were not treated as independent.
Median `Delta` is zero throughout these aggregate curves because most initial
mode choices exactly match Q00; this retained null structure is not replaced
by conditioning on action divergence.

## DEVELOPMENT temporal result

For Q01, the long early-state curve continues to evolve through `ell=11` under
both continuation probes. Under Q00 continuation its final three marginal
means are `.022902`, `.021349`, and `.021725`. Under Q11 continuation they are
`.002341`, `.003015`, and `.003511`; the first two intervals overlap zero and
the last does not. Thus development anticipation is not temporally stabilized
at the assessed boundary. The magnitude differs sharply between continuation
probes. This is a temporal statement only and does not establish mode or
continuation superiority.

## Secondary available-state analysis

This changing-population analysis is explicitly secondary.

| ell | Problem indices | Histories | Factual states per curve |
|---:|---|---:|---:|
| 0 | 1–12 | 840 | 30,240 |
| 1 | 1–11 | 840 | 27,720 |
| 2 | 1–10 | 840 | 25,200 |
| 3 | 1–9 | 840 | 22,680 |
| 4 | 1–8 | 840 | 20,160 |
| 5 | 1–7 | 840 | 17,640 |
| 6 | 1–6 | 840 | 15,120 |
| 7 | 1–5 | 840 | 12,600 |
| 8 | 1–4 | 840 | 10,080 |
| 9 | 1–3 | 840 | 7,560 |
| 10 | 1–2 | 840 | 5,040 |
| 11 | 1 | 840 | 2,520 |

Its full six curves and intervals are retained in
`available_state_summary.csv`. Their changing support prevents using them as a
substitute for the nested common-support results.

## Frozen-rule classification

**PERSISTENT BOUNDARY EVOLUTION.** At the `L=11` boundary, multiple consecutive
marginal contributions coherently continue the evolution of `Delta`. Under Q00
continuation all three contrasts continue positive accumulation. Under Q11
continuation Q01 continues positive accumulation, while Q10 and Q11 show
coherent late-range decreases. History-level uncertainty is sufficiently
informative to distinguish this pattern from insufficient temporal precision.

The frozen pilot rule initially authorized **J=18**, not replication `5→10`.
That preregistered classification and authorization remain preserved in their
original artifacts. The subsequent CE decision closes the pragmatic pilot at
`J=12` without exercising the extension. Campaign 3 development therefore
uses `ell=11` as its operational temporal assessment range. This is explicitly
an engineering/development choice under a persistent-boundary result, not an
identified optimal, true, stabilizing, or saturation horizon. No `J=18` or
`J=24` history was generated.

This classification does not infer a best mode, best continuation, Q11
superiority, continuation robustness, or state coverage. Gate 1 and Gate 2
remain unstarted.
