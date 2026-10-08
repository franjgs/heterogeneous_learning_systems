# Campaign 3 horizon-pilot protocol

## Status and purpose

This is the frozen **pre-execution** protocol for a development-only temporal
diagnostic. No pilot history, agent trajectory, reward, counterfactual outcome,
Gate 1 analysis, Gate 2 analysis, or selector is produced by this freeze.

The sole question is how many future **problems** must be included when
assessing the consequence of changing one current decision. It is not horizon
optimization, policy ranking, strategy comparison, continuation-sensitivity
inference, state-coverage analysis, or selector development.

## Temporal estimands

Let `j(t)` be the one-indexed problem containing decision `t`, and let `e(j)`
be its final decision. For `j(t)+ell <= J`, the performance accumulation is

```text
G_t(ell) = sum_(tau=t)^(e(j(t)+ell)) mu_tau^true.
```

Thus `ell=0` includes the current decision through the end of the current
problem. It is not the Campaign 2 two-real-reward endpoint. Missing future
rewards are never imputed as zero.

For initial mode `m` and continuation `c`,

```text
Y_m^c(h_t,ell)
  = E[G_t(ell) | do(m_t=m), pi_(t+1:)=Q^c, h_t].
```

Later branches are CRN-paired stochastic realizations, not exact conditional
expectations. With `Q00` as the initial-mode reference:

```text
Delta_m^c(h_t,ell) = G_m^c(h_t,ell) - G_00^c(h_t,ell),
delta_m^c(h_t,ell) = Delta_m^c(h_t,ell) - Delta_m^c(h_t,ell-1).
```

The modes `m` remain separate (`Q10`, `Q01`, `Q11`), as do the continuation
probes `c in {Q00,Q11}`.

## Frozen development design

The diagnostic range is `J_pilot=12`. The factual state-source policy is Q11,
so future factual states have the conditional interpretation
`h_t ~ d_Q11^pilot`. Q11 is not an oracle, exact optimum, upper bound, or
preferred policy, and this reference distribution establishes no state-space
coverage claim.

The team set is the frozen size-eight prefix of `S_dev`:

```text
S_pilot = G00 G04 G05 G07 F01 F02 F03 F04.
```

Exact canonical matrices are loaded from `campaign3_team_split/team_split.csv`.
No held-out team is executable in the pilot.

The generator set is all 21 frozen development regimes:

```text
Phi_pilot =
K01 K02 K03 K05 K06 K07 K10 K11 K13 K15 K16
K17 K20 K21 K23 K25 K26 K27 K31 K32 K33.
```

Exact parameters are loaded from `campaign3_generator_split/kernel_split.csv`.
No held-out kernel is executable in the pilot. The cross-product contains 168
team-by-kernel cells. Five fresh histories per cell are initially allocated,
giving 840 base histories. Complete base histories—not their decisions—are the
independent replication units.

All temporally eligible factual decision states are intervention states. The
current decision is cloned under `Q00/Q10/Q01/Q11`; after it, each branch uses
either Q00 or Q11. These eight combinations are not permanent strategies.

## Seed allocation and CRN semantics

Protocol identifier `campaign3_horizon_pilot_v1` namespaces every seed. For
each `(team ID, kernel ID, replicate index)`, canonical compact JSON is hashed
with SHA-256 and its first 32 big-endian bits define the simulator seed. Python
`hash()` is never used. Replicates `0..4` are initial; `5..9` are reserved for
a possible global 5-to-10 escalation. The complete 1,680-row allocation is
frozen before execution, is collision-checked, and excludes the recorded PGCG
and team-geometry seeds.

Each base seed deterministically produces named physical-problem,
observation-noise, and other-exogenous substream seeds. At a future factual
state, the runner must clone the complete pre-action simulator and RNG states,
then restore the same future exogenous stream state for every initial-mode and
continuation branch. Future physical problems and standard-normal observation
innovations are shared; realized observations need not be equal when branch
means differ. Differences in actions, beliefs, capabilities, and later policy
decisions remain endogenous and are preserved.

## Nested support and secondary analysis

The primary characterization reports exactly three nested common-support
windows:

| Window | Eligible problem indices at J=12 | Role |
|---:|---|---|
| `L=2` | 1–10 | short |
| `L=5` | 1–7 | intermediate |
| `L=11` | 1 only | long-range early-state |

Within each population, all `ell=0..L` are evaluated. The `L=11` population
necessarily contains only first-problem states. For every window, later reports
must give problem indices, histories, factual states, and paired contrast
observations. Each factual state contributes six contrast pairs: three
non-reference initial modes under each of two continuations.

The **SECONDARY AVAILABLE-STATE ANALYSIS** uses all states satisfying
`j(t)+ell<=J` separately for each `ell`. Its support changes with `ell`, so it
cannot replace the nested common-support analysis.

## Uncertainty

Uncertainty uses a nonparametric clustered bootstrap over complete base
histories. Every resampled history contributes all of its eligible states.
The freeze sets `B=2000`, bootstrap seed `20261013`, and two-sided 95%
percentile descriptive intervals. Required summaries are mean `Delta` with its
bootstrap interval, mean `delta` with its bootstrap interval, median `Delta`,
descriptive distribution quantiles, and contributing history/state counts.
Decisions are never treated as independent replicates.

## Decision procedure

**INSUFFICIENT TEMPORAL PRECISION** means boundary-region `Delta/delta`
uncertainty leaves both stabilization and persistent boundary evolution
plausible. It does not mean nonsignificance, an inconvenient result, or noise
in an isolated cell. Only this classification permits a global replication
increase from five to ten histories in every one of the 168 cells. A
timestamped or content-addressed decision artifact with evidence and hashes
must exist before replicates `5..9` are generated. Selective replication and
replication above ten are prohibited.

**STABILIZATION** means the predefined windows show no coherent continuing
accumulation near their assessed boundary, while the final marginal sequence
is dominated by small or nonsystematic fluctuations under history-level
uncertainty and both continuation probes. It requires neither zero `Delta` nor
identical continuations and uses no fixed effect-size epsilon or single-test
rule.

**PERSISTENT BOUNDARY EVOLUTION** requires multiple consecutive boundary
contributions coherently continuing the evolution of `Delta`, credibly under
history-level uncertainty, the predefined windows, and both continuations. An
isolated terminal contribution or continuation difference is insufficient.

At `J=12`, stabilization closes the pilot with an adequate temporal assessment
range. Insufficient precision may authorize only the global 5-to-10 step.
Persistent boundary evolution may authorize `J=18`; more replication is not a
substitute for range. Any extension requires a pre-extension artifact and
fresh independent histories—never appended inspected histories. That artifact
must freeze outcome-independent short, intermediate, and full-range early-state
windows before execution. The same rule permits at most `J=24`. If range is
still limiting there, the terminal result is **HORIZON UNRESOLVED**; `J>24` is
prohibited. A later pragmatic engineering range must not be described as a
scientifically identified saturation horizon.

## Firewalls and immutable mechanisms

- **Gate 1:** the two continuations diagnose temporal range only. No
  continuation superiority, invariance, cross-continuation regret, or robust
  mode ranking is inferred.
- **Gate 2:** Q11 supplies only the reference-state distribution. No hybrid
  state source, coverage claim, action coverage, outcome coverage, or selector
  coverage is introduced.
- **Held-out:** held-out IDs are read solely to verify disjointness. Held-out
  teams, kernels, histories, outcomes, debugging evidence, stopping evidence,
  and performance information are prohibited.

The pilot may inform only the later temporal assessment range. It cannot alter
physics, CES, observation noise, `Z_hat`, Bayes, MIS-v2, eta/lambda, the four
policies, either frozen split, either structural space, generator parameters,
exclusions, selector features, or selector architecture.

Machine-readable authority resides in
`results/foundations/campaign3_horizon_pilot/`. Those artifacts allocate seeds
and freeze the design; they contain no generated history or scientific result.
