# B2.1 PACS factorial analysis

Controls passed: 5 seeds, 3 N, 6 pairs, 5 costs; 90 factorial rows; Gamma values recomputed from stored values; no TEST values detected. Zero tolerance: 1e-12.

Gamma_learn mean range: 0.003803 to 0.429410 across N/pairs.
N=25: positive pair means 6/6; negative 0/6.
N=50: positive pair means 6/6; negative 0/6.
N=100: positive pair means 6/6; negative 0/6.

Consistent Gamma_learn complementarity (5/5 positive): N=25 art_painting-sketch, N=25 photo-cartoon, N=25 photo-sketch, N=50 art_painting-cartoon, N=50 art_painting-sketch, N=50 cartoon-sketch, N=50 photo-art_painting, N=50 photo-cartoon, N=50 photo-sketch, N=100 art_painting-cartoon, N=100 art_painting-sketch, N=100 cartoon-sketch, N=100 photo-art_painting, N=100 photo-cartoon, N=100 photo-sketch.
Consistent Gamma_learn substitution (5/5 negative): none.
Consistent Gamma_oper complementarity: N=25 art_painting-sketch c=0.10, N=25 art_painting-sketch c=0.15, N=25 cartoon-sketch c=0.02, N=25 cartoon-sketch c=0.05, N=25 cartoon-sketch c=0.10, N=25 cartoon-sketch c=0.15, N=25 photo-cartoon c=0.02, N=25 photo-cartoon c=0.05, N=25 photo-cartoon c=0.10, N=25 photo-cartoon c=0.15, N=25 photo-sketch c=0.10, N=25 photo-sketch c=0.15, N=50 art_painting-cartoon c=0.02, N=50 art_painting-cartoon c=0.05, N=50 art_painting-cartoon c=0.10, N=50 art_painting-cartoon c=0.15, N=50 art_painting-sketch c=0.02, N=50 art_painting-sketch c=0.05, N=50 art_painting-sketch c=0.10, N=50 art_painting-sketch c=0.15, N=50 cartoon-sketch c=0.02, N=50 cartoon-sketch c=0.05, N=50 cartoon-sketch c=0.10, N=50 cartoon-sketch c=0.15, N=50 photo-art_painting c=0.02, N=50 photo-art_painting c=0.05, N=50 photo-art_painting c=0.10, N=50 photo-art_painting c=0.15, N=50 photo-cartoon c=0.00, N=50 photo-cartoon c=0.02, N=50 photo-cartoon c=0.05, N=50 photo-cartoon c=0.10, N=50 photo-cartoon c=0.15, N=50 photo-sketch c=0.05, N=50 photo-sketch c=0.10, N=50 photo-sketch c=0.15, N=100 art_painting-cartoon c=0.02, N=100 art_painting-cartoon c=0.05, N=100 art_painting-cartoon c=0.10, N=100 art_painting-cartoon c=0.15, N=100 art_painting-sketch c=0.02, N=100 art_painting-sketch c=0.05, N=100 art_painting-sketch c=0.10, N=100 art_painting-sketch c=0.15, N=100 cartoon-sketch c=0.02, N=100 cartoon-sketch c=0.05, N=100 cartoon-sketch c=0.10, N=100 cartoon-sketch c=0.15, N=100 photo-art_painting c=0.05, N=100 photo-art_painting c=0.10, N=100 photo-art_painting c=0.15, N=100 photo-cartoon c=0.02, N=100 photo-cartoon c=0.05, N=100 photo-cartoon c=0.10, N=100 photo-cartoon c=0.15, N=100 photo-sketch c=0.05, N=100 photo-sketch c=0.10, N=100 photo-sketch c=0.15.
Consistent Gamma_oper substitution: none.
Mean-sign changes between Gamma_learn and Gamma_oper: 0 of 90 N/pair/c cells.
Routing-change observations: {False: {'count': 30, 'mean': 0.009607458733449769, 'std': 0.01563850368738258, 'median': 0.0, 'min': -0.0038854746125094, 'max': 0.0544602218118391}, True: {'count': 420, 'mean': 0.04451380343956536, 'std': 0.041488345462050394, 'median': 0.0300734682486975, 'min': -0.0168276787629967, 'max': 0.1800395656853511}}.
Magnitud |Gamma_learn| por par y N:
art_painting-cartoon: |Gamma_learn| crece (0.057, 0.097, 0.138).
art_painting-sketch: |Gamma_learn| crece (0.062, 0.235, 0.391).
cartoon-sketch: |Gamma_learn| crece (0.062, 0.201, 0.366).
photo-art_painting: |Gamma_learn| crece (0.004, 0.076, 0.098).
photo-cartoon: |Gamma_learn| crece (0.072, 0.149, 0.192).
photo-sketch: |Gamma_learn| crece (0.092, 0.272, 0.429).
Routing-change comparisons are descriptive; they do not identify a causal routing effect. See routing_vs_gamma.csv and delta_gamma.csv.

B2.1 supports descriptive evidence about pairwise validation interactions and their dependence on N and the fixed operational cost grid. It does not establish inferential significance, global HLS superiority, development costs, TEST performance, or B2.2 claims.
