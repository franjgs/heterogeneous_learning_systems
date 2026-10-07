# Capability geometry gate under MIS-v2

## Design and artifacts

This is the exact MIS-v2 replication of the historical MIS-v1 gate. The only
physics intervention is replacing the clipped transition with
`1-(1-s)exp(-lambda x)`. The nine configurations, five environments, three
seeds, `B=(1.5,1.5)`, actions, CES, theta, Bayes, MPC, horizons, descriptors,
and A/B/C/D controls are unchanged. The preregistered eta grid is
`.05,.10,.20,.35,.50,.70,.90`; it was fixed before outcome computation.

The artifact schemas are:

- `eta_grid.csv`: eta, lambda, qualitative sensitivity band, and one-exposure
  updates from four initial capability levels;
- `configurations.csv`, `environments.csv`, `geometry_descriptors.csv`: exact
  replicated design tables;
- `runs.csv`: eta, configuration, environment, mode, seed, performance
  summaries, initial `V_K`, and final `S`;
- `trajectories.csv`: every belief, assignment, exercised cell, MIS-v2
  increment, state transition, and reward;
- `matched_pairs.csv`: continuous `Delta V_K`, descriptor distances, and
  environment-specific performance differences for every eta;
- `regime_map_by_eta.csv`: complete rankings and winners by eta/environment;
- `representative_cases.csv`: reference-seed winner and G00/G06 summaries;
- `mis_v1_vs_v2.csv`: historical and revised winner comparison;
- `interior_geometry_check.csv`: rankings restricted to `0<s_ik<1`;
- `manifest.json`: frozen design, counts, and provenance.

There are 945 main DISCOVER+DEVELOP executions (7 eta x 9 configurations x 5
environments x 3 seeds), and 2,205 run rows after A/B/C/D controls. The 26,460
trajectory rows retain every step. No-development controls are exactly
eta-invariant and were computed once then identically labeled for each eta.

## Raw regime map

| eta | persistent theta1 | persistent theta2 | change 1122 | alternating 1212 | recurrent 1221 |
|---:|---|---|---|---|---|
| .05 | G07 | G05 | G05 | G07 | G07 |
| .10 | G07 | G05 | G07 | G07 | G07 |
| .20 | G07 | G05 | G07 | G07 | G07 |
| .35 | G07 | G05 | G06 | G06 | G06 |
| .50 | G07 | G00 | G06 | G06 | G06 |
| .70 | G03 | G02 | G03 | G06 | G06 |
| .90 | G03 | G04 | G04 | G04 | G04 |

WHO HAS WHAT matters at every eta, and every eta has environment-dependent
crossovers. Exact winner identity is rate-sensitive. The appropriate
classification is **ROBUST POSITIVE** for the existence of identity effects
and crossovers, with a parameter-conditional detailed regime map.

## Strong matched comparison

G00 `[(.5,.5),(.5,.5),(.5,.5)]` and G06
`[(0,0),(.5,.5),(1,1)]` have identical `B_k`, `V_K=2.9666563146`, static-known
performance, and DISCOVER-only performance. Their full alternating difference
`performance(G06)-performance(G00)` is +1.2181, +1.8519, +2.0538, +1.8938,
+1.6346, +.5898, and -.5292 as eta rises through the grid. Thus G06 retains an
adaptive advantage for eta `.05-.70`, but loses it at `.90`. Under persistent
theta2, G00 weakly dominates or ties G06 throughout.

The difference is adaptive. In alternating demand, the static and DISCOVER-only
controls are identical. Known-theta DEVELOP favors G06 through eta `.50`; at
eta `.70`, known-theta DEVELOP favors G00 while full DISCOVER+DEVELOP still
favors G06, identifying a discovery-development coupling effect. At eta `.90`,
both comparisons favor G00.

## MIS-v1 comparison and zero-cell diagnosis

Historical winners were G07 (persistent theta1), G08 (persistent theta2 and
change), and G06 (alternating and recurrent). Under MIS-v2:

- G07 persistent-theta1 survives through eta `.50`;
- G06 alternating/recurrent survives only for eta `.35-.70`;
- G08 never wins and is the clearest result lost after removing instant mastery;
- at eta `.90`, all winners are interior G03/G04 configurations.

For one standard exposure, a zero cell becomes exactly eta (within numerical
representation), not mastery: `.05,.10,.20,.35,.50,.70,.90` across the grid.
An initial `.1` becomes `.1+.9 eta`, `.5` becomes `.5+.5 eta`, and `.9` becomes
`.9+.1 eta`. Gains diminish with prior capability and no main-grid exposure
clips. Configurations containing zeros still win at several slow/intermediate
rates because their assignments and complementary existing capabilities can be
useful—not because zero jumps to one. Their dominance disappears at eta `.90`.

## Interior diagnostic

G00--G04 all satisfy `0<s_ik<1` with entries between `.25` and `.75` except the
homogeneous `.5` point. Restricting the rankings to these matrices still gives
different winners by environment for every eta. Examples include G03 versus
G01 at eta `.05-.20`, G03 versus G00 at `.35`, four different winners at `.50`,
and G03 versus G04 at `.90`. Geometry-environment crossovers therefore do not
require boundary entries.

## Representative causal attribution

At eta `.35` in alternation, G06 and G00 already diverge at the first
assignment. G06 exercises the zero agent's second capability and changes it
`0 -> .35`, while its middle first capability changes `.5 -> .675`. G00 spreads
the same opportunity over three `.5` cells, each exercised unit changing by
`.175`. Both first beliefs become `.976840`, but the resulting states differ;
subsequent assignments and rewards diverge. G06 problem rewards are 3.410426,
4.921252, 4.587340, 5.479599 versus G00's 3.134294, 3.992487, 4.619261,
4.758776.

At eta `.05`, G07 wins alternation without fast zero-cell acquisition. Its
exercised `.5` cell gains only `.025` initially and reaches `.729820` after the
four problems. At the same rate, G05 wins persistent theta2 by repeatedly
developing the middle second capability `.5 -> .729820`.

At eta `.90`, interior G04 wins alternation. Its first split assignment uses
fractional exposure on two agents; `.625` rises by `.256415`, not to mastery.
Later assignments exploit the resulting state, producing problem rewards
4.122856, 4.877397, 5.692848, and 5.117287.

## Scientific interpretation

MIS-v1's exact winner map was not robust, and G08 appears to have benefited
materially from its low-cell transition pathology. The stronger structural
finding survives: with equal capability totals and sometimes identical initial
productive value, interpersonal placement changes experience, development,
reassignment, and performance. This supports capability geometry x problem
dynamics within the current synthetic physics. It does not calibrate eta,
establish universal superiority of heterogeneity, prove adaptive reframing, or
generalize beyond the fixed CES/Bayes/MPC/theta/action system.
