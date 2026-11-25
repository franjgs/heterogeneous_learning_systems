# Validation report

`pytest -q studies/soc_triage_hls_availability_robustness/tests`: 17 passed. Coverage includes exact D1/P1/WAPS fixture comparisons, reference aggregate fixture, continuous and configurable weekly schedules, overnight Sunday/week boundary, shift-end suspension, repeated resumption, same analyst, remaining work, no out-of-calendar service, independent deadlines, uniform time scaling, hidden-label isolation and exact fast-D1/RNG parity against the frozen dispatcher across 40 seeds.

Full historical regression: 43,200 episodes and 1,681,848 task records compared; zero divergent episode or task assignments at absolute tolerance `1e-10`. The reference commit, fields and limitation of the continuous-mode exact backend are described in `BACKWARD_COMPATIBILITY_REPORT.md`.

The integrated technical pilot passed: 1,728 condition-seed episodes across eight paired seed blocks; 48 trace audit rows; 168 h admission and 240 h evaluation; zero terminal drain; every admitted deadline matured; both calendar arms retained identical demand, recommendation, need, confusion counts and L1 assignment hashes. Eight seeds are technical validation only, not inferential evidence.

Development found and corrected: one-analyst-at-a-time dispatch instead of joint dispatch; missed overnight week boundary; repeated episode lookup with quadratic work; and D1 candidate lookup scaling. A direct continuous event-loop stress comparison also found tiny completion rounding capable of changing a later tie. Exact 24x7 mode therefore delegates to the frozen backend. Non-continuous calendars use the new event loop, tested on explicit suspension/resumption fixtures.
