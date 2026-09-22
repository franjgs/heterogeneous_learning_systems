# Routing transformation analysis

## OBSERVED
Controls passed: 5 seeds, 3 N, 6 pairs, 5 costs, 450 unique observations; Gamma_learn and Gamma_oper reproduce the stored values; TEST absent.
DeltaGamma classification: {'ABSORB': 424, 'AMPLIFY': 20, 'PRESERVE': 6}.
Routing changes relative to F0 occur in 420/450 observations under at least one intervention comparison.
route_interaction_count > 0 in 393/450 observations; mean DeltaGamma is -0.130865 when nonzero and -0.078605 when zero.
DeltaGamma range: -0.448450 to 0.035147.
Across all observations, mean (Gamma_learn, Gamma_oper, DeltaGamma) is c=0: (0.166432, 0.012528, -0.153904); c=0.15: (0.166432, 0.091474, -0.074958).

## SUPPORTED INTERPRETATION
The data show the sequence learning → competence changes → V(S) → operational routing → Gamma_oper: applying the same learned states to F/D alternatives changes the measured interaction as c changes. At low c, Gamma_oper is substantially below Gamma_learn on average, consistent with operational absorption by the available Deep alternative; as c rises, Gamma_oper moves closer to Gamma_learn. Routing structure is associated descriptively with DeltaGamma, with larger route_interaction_l1 corresponding to more negative mean DeltaGamma; this does not isolate a causal routing contribution.
Amplification exists in a minority of observations (20/450), and sign changes are present in the saved cases; they are reported in routing_representative_cases.csv without being treated as causal.

## NOT DEMONSTRATED
These results do not demonstrate routing causality, global HLS superiority, TEST performance, necessity of a joint architecture, development-cost effects, or any B2.2 claim.
