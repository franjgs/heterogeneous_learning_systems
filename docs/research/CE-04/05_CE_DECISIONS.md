# CE-04 — Chief Engineer Decisions

**Decision record date:** 2026-10-26
**Status:** decisions recorded; five implementation specifications remain
open; protocol not frozen.

The following decisions are adopted by the CE as stated in the instruction
received on 2026-10-26. They are distinct from the expert reports, whose
original texts remain pending incorporation; they do not imply that the
technical design is complete.

1. **First dimension:** capability heterogeneity and its interaction with
   organization.
2. **Cooperation:** explicit cooperation is disabled; each task is executed
   by one agent.
3. **Learning:** individual learning and competence transfer are disabled;
   competence is constant.
4. **Organization sizes:** N = 12, 24 and 48 agents.
5. **Task types:** four task families.
6. **Composition conditions:** H0 homogeneous, H1 moderate heterogeneity,
   H2 high heterogeneity. Mean competence by task type is identical across
   the three; heterogeneity changes dispersion and specialization. Exact
   generation equations and parameter values remain open.
7. **Policies:** P0 minimizes expected load; P1 uses true competence, expected
   service time and deadline; P2 uses the same decision function as P1 with
   estimated competence; P3 is an adaptive contextual policy using an
   established method. P1 is a full-information reference, not a global
   optimum. The common objective and P3 method/configuration remain open.
8. **Scaling:** resources and demand scale proportionally with N; nominal
   relative load is held constant. The exact resource scaling rule remains
   open.
9. **Design:** scenarios are paired; random seeds are independent and
   comparisons are paired.
10. **Algorithms:** no new algorithm will be developed without express CE
    authorization.
11. **Execution:** no pilot before protocol freeze; the full campaign requires
    later CE authorization.

The separate initial-dimension proposal in
[`HLS_INITIAL_DIMENSION_EXPERIMENT_PROPOSAL.md`](../HLS_INITIAL_DIMENSION_EXPERIMENT_PROPOSAL.md)
is not silently substituted for CE-04 and is not incorporated as its protocol.
