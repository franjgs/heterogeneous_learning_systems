# DISCOVER × DEVELOP-v0

**Status:** small functional prototype; not a new campaign or HLS theory.

## Reused physics

The sole added dependency is the canonical MIS diminishing learning-by-doing
transition from `src/hls/minimal_reference_scenario.py` and
`HLS_MINIMAL_REFERENCE_SCENARIO.md`: for an exercised competence,

$$s^+=\min\{1,s+q(1-s)^2\},\qquad q=1.5.$$

The prototype dimensionally applies the existing exercised effort `x[i,k]` as
`min(1, s[i,k] + x[i,k] * 1.5 * (1-s[i,k])^2)`.  Thus only exercised cells
update; `x=0` leaves a cell unchanged and the ceiling is one.  `q=1.5` is the
historical active reference value, not a new eta or plasticity parameter.

CES, Gaussian Bayes, belief-state control, and MIS are reused/purchased
components.  USE--DEVELOP was already established.  The limited new
experimental question is whether DISCOVER of which known-theta model applies
couples to DEVELOP through the same opportunities that exercise capabilities.
This remains inference within a known frame: it does not show reframing,
transfer, general heterogeneity advantage, or new HLS theory.

## Prototype contract

Each three-step problem resets the DISCOVER belief to `.5` but retains the
developed `S` into the next problem.  The controlled persistent, change, and
alternating theta sequences are shared by A DISCOVER+DEVELOP, B DISCOVER ONLY,
C DEVELOP with theta known, and D static known-theta.  The same seeded
standard-normal observation stream, resources, action set, CES and theta
values are used in all modes.

Because an exact three-step continuous-belief/continuous-S DP branches over
both 64 actions and Gaussian observations, the DEVELOP modes use standard
two-step receding-horizon Bellman look-ahead and replan each decision.  This is
documented approximation, not an HLS score. DISCOVER ONLY delegates to the
existing exact fixed-S DISCOVER-v0 DP.
