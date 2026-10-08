# Post-Campaign-2 state-coverage audit

## Scope and decision

**Decision: INSUFFICIENT COVERAGE for using the Q11 bank as the sole source of
C3-development states.** Future development should draw retained/generated
states from **all four frozen policies Q00/Q10/Q01/Q11**. This audit does not
justify or design a new exploration policy or metacontroller.

This is a post-Campaign-2 diagnostic based exclusively on the 92,160 real steps
already retained in commit `dabf6babf3d7d99105e3faad785313b0c3d641c3` and
scientifically closed in `41d918da3d13ea6380064c76166d7248b00935ac`. It runs
no environment transition, draws no random number, changes no action, and does
not reopen H1--H4. The question is representational coverage for future
development, not another Campaign 2 finding.

Only the 61,440 nonterminal pre-decision states are relevant because all four
prospective modes collapse at the terminal decision. There are 15,360 retained
states per policy. Frozen diagnostic functions compute H(b), D_I, D_I_loss,
and H_S on those states. The policy's executed action is retained; Q11 is
evaluated side-effect-free on each non-Q11 state only to identify action-
disagreement subsets. No subsequent outcome is evaluated.

## Operational diagnostic fixed before inspection

Coverage uses the primitive state, not a fitted embedding:

```text
x=(b_1,b_2,b_3,s_11,s_12,s_21,s_22,s_31,s_32).
```

All nine coordinates already lie in [0,1] and receive equal weight. Within
each exact scenario × configuration × problem-position × decision-position
stratum, distance is normalized RMS over these coordinates. For every target,
Q11 observations with the same seed are excluded. The Q11 self-spacing radius
of a stratum is the maximum nearest-Q11 distance obtained when each Q11 seed is
itself left out.

A target is operationally covered when its nearest eligible Q11 state is no
farther than that stratum's Q11 self-spacing radius. The pre-fixed conservative
binary rule calls Q11-only development sufficient only if every non-Q11 target
is covered. This is a transparent non-extrapolation diagnostic, **not** a
confirmatory threshold or a claim about the true state-space distribution.
Coordinate-wise Q11 envelopes are reported separately and do not determine the
classification. Derived variables are compared marginally but not double-
counted in the distance.

## Overall coverage

The Q11-only criterion misses **6,506/46,080 (14.12%)** non-Q11 states.

| Visited-state policy | States | Spacing coverage | Coordinate-envelope coverage | Uncovered | Nearest RMS median | Nearest RMS 95th percentile |
|---|---:|---:|---:|---:|---:|---:|
| Q00 | 15,360 | 70.07% | 68.50% | 4,598 | .00748 | .16791 |
| Q10 | 15,360 | 99.77% | 94.65% | 35 | .00009 | .03969 |
| Q01 | 15,360 | 87.81% | 84.66% | 1,873 | .00033 | .14668 |
| Q11 self baseline | 15,360 | 100.00% by construction | 94.67% | 0 | .00008 | .03939 |

Thus Q10 visits almost the same support as Q11, but Q00 and Q01 do not. This
conclusion is not based on a mean difference alone: it combines nearest-support,
coordinate-envelope, marginal-distribution, structural-stratum, and action-
disagreement diagnostics.

## Marginal distributions

All policies have exactly the same scenario, configuration, problem/decision
position, represented/unrepresented composition, and C/N/M distributions by
the frozen factorial. Differences arise in endogenous b and S and their derived
descriptors.

The largest normalized Wasserstein-1 differences from Q11 were:

| Policy | Variable | normalized W1 | KS | Mean difference from Q11 |
|---|---|---:|---:|---:|
| Q00 | D_I | .2356 | .3490 | +.0785 |
| Q00 | H(b) | .2009 | .2846 | +.2207 |
| Q00 | b_1 | .1179 | .1600 | −.0510 |
| Q00 | b_3 | .1007 | .2225 | +.0417 |
| Q01 | D_I | .0903 | .1208 | +.0301 |
| Q01 | H(b) | .0891 | .1186 | +.0978 |
| Q01 | b_1 | .0473 | .0557 | −.0146 |
| Q01 | b_3 | .0429 | .0824 | +.0093 |
| Q10 | largest difference, s_32 | .0019 | .0061 | −.0019 |

The complete table includes all b/S cells, H, D_I, normalized disagreement,
D_I_loss, H_S, C/N/M and p. These are descriptive distances, not tests or new
Campaign 2 hypotheses.

## Where Q11 coverage fails

Coverage depends strongly on configuration and time.

- Q00 coverage is 43.46% for G00 and 52.01% for G05, versus 93.23% for G04
  and 91.56% for G07. G00/G05 account for 4,014 of Q00's 4,598 uncovered states.
- Q01 coverage is 83.93% for G00 and 83.46% for G05, versus 93.33% for G04
  and 90.49% for G07.
- At the second within-problem decision, Q00 coverage falls to 49.51% and Q01
  to 77.38%, compared with 90.63% and 98.23% at the first decision. Q10 remains
  above 99.7% at both positions.
- Late history is least covered: at problem index 5, Q00 coverage is 55.04%
  and Q01 coverage 69.22%. The largest scenario gaps occur for TR-HB/TR-J:
  Q00 coverage is 65.36%/65.99%; Q01 is 72.86%/75.52%.

At the exact 40-seed stratum level, Q00 has **100/384 strata with zero
coverage** and Q01 has **8/384**; Q10 has none and its minimum stratum coverage
is 87.5%. Q01's zero-coverage strata concentrate in later second decisions for
G00/G05 in TR-G, TR-HA, and TR-HB. Q00 zero-coverage strata are also concentrated
in G00/G05 and later decisions. `support_rows.csv.gz` retains exact rows and
`stratified_support.csv` provides the requested one-dimensional strata.

## Action-disagreement regions

Coverage failure is especially relevant where the policy owning the visited
state and Q11 choose different actions on that same state:

| Policy owning state | Action-different states | Q11 spacing coverage | Uncovered | Coverage when actions equal |
|---|---:|---:|---:|---:|
| Q00 | 8,873 (57.77%) | 49.68% | 4,465 | 97.95% |
| Q10 | 150 (.98%) | 98.67% | 2 | 99.78% |
| Q01 | 3,654 (23.79%) | 56.27% | 1,598 | 97.65% |

For Q00 and Q01, almost all support failures occur in precisely the regions
where their action differs from Q11: 4,465/4,598 and 1,598/1,873 respectively.
This is the central reason Q11 alone is inadequate for developing a selector:
its weakest empirical support coincides with states where policy choice is most
consequential as a classification problem. This is a coverage statement, not a
claim about which action or policy performs better.

## Recommendation before C3

Use a development state bank formed from the **union of states visited by all
four frozen policies**, with policy/source identity and the existing structural
strata retained for auditing. Do not rely on Q11 alone. The current evidence
does not require inventing a new exploration policy: the already retained four-
policy trajectories directly supply the missing Q00/Q01 regions. Any sampling,
weighting, train/test partition, selector objective, or exploration design must
be specified separately before C3 and is not chosen here.

## Limitations

- Coverage is empirical and diagnostic, not proof over all reachable states.
- The audit is limited to 40 seeds, eight frozen histories, four capability
  configurations, the current action space, and frozen HLS physics.
- Q11 is the reference distribution and its maximum leave-one-seed-out spacing
  defines the operational radius; another preregistered geometry could differ.
- Equal-weight raw b/S coordinates preserve agent/capability identity. The
  audit does not assert that this is a universal behavioral metric.
- Coordinate boxes ignore dependence and nearest-neighbour distance is subject
  to finite-sample sparsity; reporting both exposes rather than removes this.
- The action-disagreement diagnostic evaluates frozen policies on retained
  states but does not simulate consequences or reopen Campaign 2 H1--H4.
- No metacontroller, C3 protocol, new policy, or new experiment is created.

## Artifacts and provenance

Machine-readable artifacts are under
`results/diagnostics/campaign2_state_coverage_audit/`. The manifest binds the
unchanged Campaign 2 trajectory/reference hashes, fixed method, counts and
persisted files. The audit summary records the binary decision and recommendation.
Campaign 2 results, closure, preregistration, I/O incident, and failure evidence
remain unchanged.
