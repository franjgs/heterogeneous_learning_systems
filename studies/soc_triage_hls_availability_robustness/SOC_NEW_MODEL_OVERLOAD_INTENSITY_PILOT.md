# Experimento de intensidad y duración de sobrecarga — NEW MODEL / MODELO NUEVO

> Experimento exploratorio del **NEW MODEL / MODELO NUEVO**. El manuscrito LaTeX y los resultados confirmatorios del repositorio pertenecen exclusivamente al **OLD MODEL / MODELO VIEJO**. No se mezclan ni comparan aquí magnitudes absolutas de ambos modelos.

## Diseño y reproducibilidad

Partida: rama `research/soctra-hls-new-model`, commit `5026e303c51e6dd4523d5aad90b276309385ea2b`. Se ejecutaron 144 episodios (12 semillas × cuatro escenarios × tres políticas), con el runner [`run_overload_intensity_pilot.py`](run_overload_intensity_pilot.py), el adaptador [`run_policy_pilot.py`](run_policy_pilot.py) y el generador/motores existentes. Las semillas fijadas antes de ejecutar fueron `2026112801–2026112812`. La búsqueda de declaraciones de semillas y campañas del repositorio confirmó que este bloque no se solapa con el piloto previo (`2026112701–2026112710`), `998001`, los bloques documentados `910000/920000/930000` ni la campaña histórica `711000000–711000399`.

La configuración organizativa, roster, calendario continuo individual 24x7, elegibilidad, competencias, eficiencias, servicios, deadlines, clasificador, mezcla, `alpha=0.50`, `beta=0`, `gamma=1`, parámetros y reglas D1/P1/WAPS se mantuvieron idénticos. SHA-256 de organización en los cuatro JSON: `9c055bf7341e36d71788cd7cc9b8d6a7220ddd1889d7972cf11f38a0175fbc9b`. Las trazas exógenas y el ambiente se verificaron iguales entre las tres políticas dentro de cada escenario-semilla; entre escenarios las trazas cambian con el perfil de tasas.

Las cuatro hipótesis prefijadas fueron A: ρL1=1.10 durante 24 h; B: 1.25 durante 8 h; C: 1.25 durante 24 h; D: 1.25 durante 48 h. Todas preceden y siguen con 96 h ordinarias (ρL1=0.85) y 48 h de recuperación (ρL1=0.65). C reproduce el **perfil** del piloto previo, no sus realizaciones ni semillas. El drenaje fue fijo en 168 h desde el fin de admisión: cortes A/C=336 h, B=320 h y D=360 h; así madura el deadline máximo de 12 h y el horizonte relativo de evaluación es común.

## Capacidad LP y tasas de llegada

Se reutilizó `scenario_diagnostics.assess_capacity` con elegibilidad, servicios heterogéneos, mezcla de clase y probabilidades de ruta del triaje. La capacidad asignable es μL1=17.034626 alertas destinadas a L1/h y μL2=13.045624 alertas destinadas a L2/h. La probabilidad configurada de ruta L1 es 0.87529 y L2 0.12471. Cada tasa total se deriva como λtotal=ρL1·μL1/0.87529 y luego se reparte con mezcla fija Top5/Next5/Tail=0.50/0.30/0.20. Los valores son hipótesis sintéticas; no tasas SOC medidas.

| Régimen | ρL1 objetivo | λ total esperada | λ a L1 | λ a L2 | Trabajo L1 esperado (h-persona/h) | Trabajo L2 esperado (h-persona/h) | ρL2 LP |
|---|---:|---:|---:|---:|---:|---:|---:|
| A: ordinary | 0.85 | 16.542439 | 14.479432 | 2.063008 | 4.271 | 0.476 | 0.158 |
| A: overload_pulse | 1.10 | 21.407863 | 18.738088 | 2.669775 | 5.528 | 0.616 | 0.205 |
| A: recovery | 0.65 | 12.650101 | 11.072507 | 1.577594 | 3.266 | 0.364 | 0.121 |
| B: ordinary | 0.85 | 16.542439 | 14.479432 | 2.063008 | 4.271 | 0.476 | 0.158 |
| B: overload_pulse | 1.25 | 24.327117 | 21.293282 | 3.033835 | 6.282 | 0.700 | 0.233 |
| B: recovery | 0.65 | 12.650101 | 11.072507 | 1.577594 | 3.266 | 0.364 | 0.121 |
| C: ordinary | 0.85 | 16.542439 | 14.479432 | 2.063008 | 4.271 | 0.476 | 0.158 |
| C: overload_pulse | 1.25 | 24.327117 | 21.293282 | 3.033835 | 6.282 | 0.700 | 0.233 |
| C: recovery | 0.65 | 12.650101 | 11.072507 | 1.577594 | 3.266 | 0.364 | 0.121 |
| D: ordinary | 0.85 | 16.542439 | 14.479432 | 2.063008 | 4.271 | 0.476 | 0.158 |
| D: overload_pulse | 1.25 | 24.327117 | 21.293282 | 3.033835 | 6.282 | 0.700 | 0.233 |
| D: recovery | 0.65 | 12.650101 | 11.072507 | 1.577594 | 3.266 | 0.364 | 0.121 |

L2 queda lejos de su capacidad media en los cuatro perfiles (ρL2≈0.12–0.23); la presión principal prevista es L1. El LP no representa colas ni sincronía intrahoraria. Tasas realizadas de Poisson difieren de sus expectativas:

| Perfil | Régimen | λ esperada alertas/h | n medio observado | tasa observada alertas/h |
|---|---|---:|---:|---:|
| Todos | ordinary | 16.542 | 1,569.2 | 16.346 |
| A | overload_pulse | 21.408 | 527.2 | 21.967 |
| B | overload_pulse | 24.327 | 190.7 | 23.838 |
| C | overload_pulse | 24.327 | 595.8 | 24.825 |
| D | overload_pulse | 24.327 | 1,170.0 | 24.375 |
| A | recovery | 12.650 | 600.2 | 12.504 |
| B | recovery | 12.650 | 622.8 | 12.975 |
| C | recovery | 12.650 | 596.0 | 12.417 |
| D | recovery | 12.650 | 609.8 | 12.704 |

No se seleccionaron semillas por sus tasas realizadas.

## Resultados globales

Medias de 12 episodios por política; R/N conserva la definición vigente. “Mayor media” es solo una ordenación descriptiva, no una selección inferencial. Todas las ejecuciones finalizaron antes del corte: pendiente=0%.

| Perfil | Pulso (ρL1, h) | n medio | D1 R/N; SLA | P1 R/N; SLA | HLS-B R/N; SLA | Mayor media R/N |
|---|---:|---:|---:|---:|---:|---|
| A | 1.10, 24 | 2696.7 | 0.7997; 99.80% | 0.7756; 100.00% | 0.7820; 100.00% | D1 (0.7997) |
| B | 1.25, 8 | 2382.7 | 0.7969; 100.00% | 0.7752; 100.00% | 0.7810; 100.00% | D1 (0.7969) |
| C | 1.25, 24 | 2761.1 | 0.7873; 97.77% | 0.7758; 100.00% | 0.7826; 99.70% | D1 (0.7873) |
| D | 1.25, 48 | 3349.0 | 0.6433; 79.44% | 0.6466; 83.06% | 0.6518; 82.89% | WAPS (0.6518) |

### Contrastes emparejados globales

Cada diferencia se calcula dentro de la misma semilla y escenario. Formato: media (DE), IC95% t descriptivo con 11 g.l.; semillas favorables a la política izquierda / derecha / empate. Para SLA, unidades en puntos porcentuales (pp).

| Perfil | Diferencia | Δ R/N | Δ SLA (pp) |
|---|---|---|---|
| A | P1 - D1 | -0.02407 (0.00366), [-0.02640, -0.02175]; 0/12/0 | +0.202 (0.317), [+0.001, +0.404]; 5/0/7 |
| A | WAPS - D1 | -0.01762 (0.00248), [-0.01920, -0.01605]; 0/12/0 | +0.202 (0.317), [+0.001, +0.404]; 5/0/7 |
| A | WAPS - P1 | +0.00645 (0.00190), [+0.00524, +0.00765]; 12/0/0 | +0.000 (0.000), [+0.000, +0.000]; 0/0/12 |
| B | P1 - D1 | -0.02176 (0.00368), [-0.02410, -0.01942]; 0/12/0 | +0.004 (0.012), [-0.004, +0.012]; 1/0/11 |
| B | WAPS - D1 | -0.01598 (0.00400), [-0.01852, -0.01344]; 0/12/0 | +0.004 (0.012), [-0.004, +0.012]; 1/0/11 |
| B | WAPS - P1 | +0.00578 (0.00185), [+0.00461, +0.00696]; 12/0/0 | +0.000 (0.000), [+0.000, +0.000]; 0/0/12 |
| C | P1 - D1 | -0.01150 (0.01145), [-0.01878, -0.00422]; 3/9/0 | +2.227 (1.395), [+1.340, +3.113]; 12/0/0 |
| C | WAPS - D1 | -0.00469 (0.00788), [-0.00970, +0.00031]; 4/8/0 | +1.928 (1.074), [+1.245, +2.611]; 12/0/0 |
| C | WAPS - P1 | +0.00681 (0.00393), [+0.00431, +0.00931]; 12/0/0 | -0.299 (0.330), [-0.508, -0.089]; 0/8/4 |
| D | P1 - D1 | +0.00335 (0.00549), [-0.00013, +0.00684]; 10/2/0 | +3.626 (0.848), [+3.087, +4.165]; 12/0/0 |
| D | WAPS - D1 | +0.00855 (0.00566), [+0.00496, +0.01215]; 12/0/0 | +3.449 (0.850), [+2.909, +3.990]; 12/0/0 |
| D | WAPS - P1 | +0.00520 (0.00210), [+0.00386, +0.00654]; 12/0/0 | -0.177 (0.118), [-0.252, -0.102]; 1/11/0 |

## Cohortes de llegada

Las cohortes siguen el régimen de admisión, no el régimen de finalización; todas se evalúan hasta el corte terminal correspondiente. Calidad es competencia media modelada entre completadas puntuales o tardías. Espera se mide desde llegada a primer servicio (h naturales).

| Perfil | Cohorte | n medio | Política | R/N | SLA | Calidad completadas | Espera h |
|---|---|---:|---|---:|---:|---:|---:|
| A | ordinary | 1569.2 | D1 | 0.7970 | 100.00% | 0.7970 | 0.116 |
| A | ordinary | 1569.2 | P1 | 0.7750 | 100.00% | 0.7750 | 0.117 |
| A | ordinary | 1569.2 | WAPS | 0.7802 | 100.00% | 0.7802 | 0.116 |
| A | overload_pulse | 527.2 | D1 | 0.8200 | 99.05% | 0.8273 | 1.581 |
| A | overload_pulse | 527.2 | P1 | 0.7769 | 100.00% | 0.7769 | 1.486 |
| A | overload_pulse | 527.2 | WAPS | 0.7804 | 100.00% | 0.7804 | 1.493 |
| A | recovery | 600.2 | D1 | 0.7887 | 99.93% | 0.7892 | 0.210 |
| A | recovery | 600.2 | P1 | 0.7759 | 100.00% | 0.7759 | 0.265 |
| A | recovery | 600.2 | WAPS | 0.7883 | 100.00% | 0.7883 | 0.261 |
| B | ordinary | 1569.2 | D1 | 0.7970 | 100.00% | 0.7970 | 0.116 |
| B | ordinary | 1569.2 | P1 | 0.7750 | 100.00% | 0.7750 | 0.117 |
| B | ordinary | 1569.2 | WAPS | 0.7802 | 100.00% | 0.7802 | 0.116 |
| B | overload_pulse | 190.7 | D1 | 0.8275 | 100.00% | 0.8275 | 0.992 |
| B | overload_pulse | 190.7 | P1 | 0.7782 | 100.00% | 0.7782 | 0.912 |
| B | overload_pulse | 190.7 | WAPS | 0.7773 | 100.00% | 0.7773 | 0.912 |
| B | recovery | 622.8 | D1 | 0.7874 | 99.99% | 0.7874 | 0.120 |
| B | recovery | 622.8 | P1 | 0.7746 | 100.00% | 0.7746 | 0.140 |
| B | recovery | 622.8 | WAPS | 0.7840 | 100.00% | 0.7840 | 0.140 |
| C | ordinary | 1569.2 | D1 | 0.7970 | 100.00% | 0.7970 | 0.116 |
| C | ordinary | 1569.2 | P1 | 0.7750 | 100.00% | 0.7750 | 0.117 |
| C | ordinary | 1569.2 | WAPS | 0.7802 | 100.00% | 0.7802 | 0.116 |
| C | overload_pulse | 595.8 | D1 | 0.7602 | 91.00% | 0.8289 | 3.223 |
| C | overload_pulse | 595.8 | P1 | 0.7771 | 100.00% | 0.7771 | 3.078 |
| C | overload_pulse | 595.8 | WAPS | 0.7786 | 99.15% | 0.7850 | 3.101 |
| C | recovery | 596.0 | D1 | 0.7894 | 98.77% | 0.7988 | 0.938 |
| C | recovery | 596.0 | P1 | 0.7765 | 100.00% | 0.7765 | 0.929 |
| C | recovery | 596.0 | WAPS | 0.7931 | 99.48% | 0.7971 | 0.933 |
| D | ordinary | 1569.2 | D1 | 0.7970 | 100.00% | 0.7970 | 0.116 |
| D | ordinary | 1569.2 | P1 | 0.7750 | 100.00% | 0.7750 | 0.117 |
| D | ordinary | 1569.2 | WAPS | 0.7802 | 100.00% | 0.7802 | 0.116 |
| D | overload_pulse | 1170.0 | D1 | 0.4571 | 54.45% | 0.8269 | 5.756 |
| D | overload_pulse | 1170.0 | P1 | 0.5030 | 64.10% | 0.7788 | 5.596 |
| D | overload_pulse | 1170.0 | WAPS | 0.5036 | 64.09% | 0.7870 | 5.624 |
| D | recovery | 609.8 | D1 | 0.6071 | 74.74% | 0.8109 | 3.453 |
| D | recovery | 609.8 | P1 | 0.5944 | 76.21% | 0.7765 | 3.581 |
| D | recovery | 609.8 | WAPS | 0.6087 | 75.26% | 0.8089 | 3.567 |

### Diferencias emparejadas en las cohortes de sobrecarga y recuperación

Formato por métrica: media (DE), IC95%; +/−/= semillas. Δ SLA en pp con tres decimales. Las cohortes de una misma semilla están correlacionadas; no se combinan como réplicas independientes.

| Perfil | Cohorte | Diferencia | Δ R/N | Δ SLA (pp) |
|---|---|---|---|---|
| A | overload_pulse | P1 - D1 | -0.04318 (0.01145), [-0.05046, -0.03591]; 0/12/0 | +0.947 (1.549), [-0.037, +1.932]; 5/0/7 |
| A | overload_pulse | WAPS - D1 | -0.03967 (0.01245), [-0.04758, -0.03176]; 0/12/0 | +0.947 (1.549), [-0.037, +1.932]; 5/0/7 |
| A | overload_pulse | WAPS - P1 | +0.00351 (0.00229), [+0.00206, +0.00497]; 11/1/0 | +0.000 (0.000), [+0.000, +0.000]; 0/0/12 |
| A | recovery | P1 - D1 | -0.01288 (0.00548), [-0.01637, -0.00940]; 0/12/0 | +0.066 (0.157), [-0.034, +0.166]; 2/0/10 |
| A | recovery | WAPS - D1 | -0.00049 (0.00464), [-0.00344, +0.00246]; 6/6/0 | +0.066 (0.157), [-0.034, +0.166]; 2/0/10 |
| A | recovery | WAPS - P1 | +0.01240 (0.00378), [+0.01000, +0.01480]; 12/0/0 | +0.000 (0.000), [+0.000, +0.000]; 0/0/12 |
| B | overload_pulse | P1 - D1 | -0.04937 (0.00585), [-0.05309, -0.04566]; 0/12/0 | +0.000 (0.000), [+0.000, +0.000]; 0/0/12 |
| B | overload_pulse | WAPS - D1 | -0.05029 (0.00456), [-0.05318, -0.04739]; 0/12/0 | +0.000 (0.000), [+0.000, +0.000]; 0/0/12 |
| B | overload_pulse | WAPS - P1 | -0.00091 (0.00397), [-0.00343, +0.00161]; 4/7/1 | +0.000 (0.000), [+0.000, +0.000]; 0/0/12 |
| B | recovery | P1 - D1 | -0.01275 (0.00430), [-0.01548, -0.01002]; 0/12/0 | +0.013 (0.045), [-0.015, +0.041]; 1/0/11 |
| B | recovery | WAPS - D1 | -0.00337 (0.00512), [-0.00662, -0.00012]; 4/8/0 | +0.013 (0.045), [-0.015, +0.041]; 1/0/11 |
| B | recovery | WAPS - P1 | +0.00938 (0.00292), [+0.00752, +0.01123]; 12/0/0 | +0.000 (0.000), [+0.000, +0.000]; 0/0/12 |
| C | overload_pulse | P1 - D1 | +0.01692 (0.04162), [-0.00953, +0.04336]; 6/6/0 | +9.005 (5.233), [+5.680, +12.329]; 12/0/0 |
| C | overload_pulse | WAPS - D1 | +0.01836 (0.03437), [-0.00347, +0.04020]; 7/5/0 | +8.153 (4.223), [+5.470, +10.836]; 12/0/0 |
| C | overload_pulse | WAPS - P1 | +0.00145 (0.00768), [-0.00343, +0.00633]; 9/3/0 | -0.852 (1.066), [-1.529, -0.174]; 0/7/5 |
| C | recovery | P1 - D1 | -0.01287 (0.01047), [-0.01952, -0.00622]; 2/10/0 | +1.231 (1.169), [+0.488, +1.974]; 11/0/1 |
| C | recovery | WAPS - D1 | +0.00368 (0.00741), [-0.00102, +0.00839]; 8/4/0 | +0.709 (0.787), [+0.209, +1.209]; 10/0/2 |
| C | recovery | WAPS - P1 | +0.01655 (0.00471), [+0.01356, +0.01954]; 12/0/0 | -0.522 (0.515), [-0.849, -0.194]; 0/8/4 |
| D | overload_pulse | P1 - D1 | +0.04594 (0.01658), [+0.03541, +0.05648]; 12/0/0 | +9.652 (2.650), [+7.969, +11.336]; 12/0/0 |
| D | overload_pulse | WAPS - D1 | +0.04651 (0.01704), [+0.03569, +0.05734]; 12/0/0 | +9.644 (2.589), [+7.999, +11.289]; 12/0/0 |
| D | overload_pulse | WAPS - P1 | +0.00057 (0.00128), [-0.00025, +0.00139]; 8/4/0 | -0.008 (0.115), [-0.081, +0.065]; 1/2/9 |
| D | recovery | P1 - D1 | -0.01272 (0.00796), [-0.01777, -0.00766]; 1/11/0 | +1.469 (1.025), [+0.818, +2.121]; 11/0/1 |
| D | recovery | WAPS - D1 | +0.00155 (0.00712), [-0.00297, +0.00607]; 6/6/0 | +0.518 (0.795), [+0.012, +1.023]; 9/2/1 |
| D | recovery | WAPS - P1 | +0.01427 (0.00590), [+0.01053, +0.01802]; 12/0/0 | -0.952 (0.630), [-1.352, -0.551]; 1/11/0 |

## Congestión, recuperación y modos de HLS-B

Las colas son recuentos de alertas aún no iniciadas en snapshots horarios; el máximo es la media entre semillas del máximo por episodio durante el pulso. El trabajo residual registrado cubre solo alertas ya iniciadas/asignadas; no se imputa servicio futuro a tareas en cola. Utilización es la fracción de horas-persona disponibles ocupada en cada cohorte.

| Perfil | Política | Cola L1 en t=96 | Máximo L1 en pulso | Cola L1 fin pulso | Cola L1 fin recuperación | h hasta volver a cola ≤ t=96 | Util L1 pulso/recup | Util L2 pulso/recup |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| A | D1 | 1.4 | 59.8 | 56.5 | 0.2 | 9.8 (12/12) | 0.989/0.713 | 0.216/0.121 |
| A | P1 | 1.4 | 57.9 | 54.7 | 0.2 | 9.8 (12/12) | 0.989/0.710 | 0.215/0.120 |
| A | WAPS | 1.5 | 57.8 | 54.8 | 0.1 | 9.8 (12/12) | 0.989/0.714 | 0.216/0.121 |
| B | D1 | 1.4 | 32.7 | 32.1 | 0.7 | 6.7 (12/12) | 0.994/0.703 | 0.228/0.129 |
| B | P1 | 1.4 | 32.2 | 31.7 | 0.5 | 6.7 (12/12) | 0.994/0.699 | 0.227/0.128 |
| B | WAPS | 1.5 | 32.3 | 31.8 | 0.5 | 6.8 (12/12) | 0.995/0.703 | 0.227/0.129 |
| C | D1 | 1.4 | 116.6 | 116.3 | 0.0 | 18.6 (12/12) | 0.998/0.777 | 0.243/0.122 |
| C | P1 | 1.4 | 112.0 | 111.5 | 0.0 | 18.5 (12/12) | 0.998/0.774 | 0.241/0.122 |
| C | WAPS | 1.5 | 112.2 | 111.6 | 0.0 | 18.5 (12/12) | 0.998/0.776 | 0.242/0.122 |
| D | D1 | 1.4 | 207.1 | 207.0 | 0.3 | 35.2 (12/12) | 0.999/0.902 | 0.237/0.129 |
| D | P1 | 1.4 | 206.6 | 206.2 | 0.2 | 35.2 (12/12) | 0.999/0.901 | 0.236/0.128 |
| D | WAPS | 1.5 | 206.8 | 206.4 | 0.2 | 35.2 (12/12) | 0.999/0.902 | 0.236/0.129 |

En los cuatro perfiles y para las tres políticas, la cola L1 al final de recuperación descendió por debajo o igualó su valor de inicio de pulso en 12/12 semillas; según snapshots horarios, el retorno tomó en promedio 6.7 h (B), 9.8 h (A), 18.5 h (C) y 35.3 h (D). Esto documenta reducción de la cola, no una garantía de estabilidad futura ni una recuperación de cada métrica/alerta. El número pendiente en el corte de evaluación fue cero. Las tasas L1 realizadas durante el pulso saturan utilización (~0.989–0.999); L2 se mantiene más baja (~0.215–0.243), coherente con cuello de botella de L1 en estos perfiles.

El motor conserva únicamente los cambios de estado HLS-B y contadores de épocas de despacho. Se añadieron al registro post-simulación los contadores exactos de despacho ya producidos por el motor, sin cambiar sus decisiones. La fracción de decisiones P1 es `P1 dispatch epochs / all dispatch epochs`; el tiempo de estado integra los cambios registrados, con D1 inicial, sobre el horizonte completo de evaluación (incluido drenaje). No equivale al tiempo de trabajo ni al porcentaje de alertas asignadas en cada modo.

| Perfil | Nivel | Decisiones P1 (%) | Estado P1-tiempo (%) | Cambios de modo medios |
|---|---|---:|---:|---:|
| A | L1 | 59.8 | 27.4 | 17.7 |
| A | L2 | 10.2 | 4.1 | 7.3 |
| B | L1 | 55.7 | 24.2 | 17.7 |
| B | L2 | 7.7 | 3.1 | 5.3 |
| C | L1 | 58.2 | 27.2 | 17.2 |
| C | L2 | 14.4 | 5.2 | 8.0 |
| D | L1 | 63.0 | 32.5 | 18.3 |
| D | L2 | 19.4 | 7.8 | 13.2 |

La mayor duración del pulso D aumenta descriptivamente la proporción de decisiones P1 de WAPS (L1: 62.96%, frente a 58.18% en C; L2: 19.38%, frente a 14.41%). El estado temporal P1 también aumenta, aunque mucho menos. No se interpreta el número de cambios como bueno/malo ni como prueba causal de ventaja adaptativa.

## Interpretación científica

- **Intensidad:** al mantener el pulso de 24 h y elevar ρL1 de 1.10 (A) a 1.25 (C), el R/N global de D1 desciende de 0.7997 a 0.7873, mientras P1 y WAPS quedan aproximadamente estables (0.7756→0.7758 y 0.7820→0.7826). En la cohorte de sobrecarga, D1 pierde puntualidad y R/N; la cola L1 pico sube de ~60 a ~117. Señal descriptiva de dependencia por intensidad, sin contraste inferencial entre escenarios.
- **Duración a ρL1=1.25:** B (8 h) apenas altera SLA y deja pico de cola ~33; C (24 h) da pico ~116; D (48 h) da ~207 y lleva SLA global a 79–83%. Los R/N globales caen de 0.7970/0.7752/0.7810 en B a 0.6433/0.6466/0.6518 en D para D1/P1/WAPS. La recuperación reduce la cola, pero empieza con deuda mayor; en D utiliza L1 ~90% mientras se drena. Este cambio incluye también un mayor peso de alertas admitidas bajo pulso en el promedio global; no es un efecto puro de duración sobre una traza fija.
- **Ventaja adaptativa:** A–C no muestran una victoria global de WAPS frente a D1; D1 tiene la mayor media de R/N en A–C. En C, WAPS−D1 es −0.00469 [−0.00970, +0.00031]. En D WAPS tiene la mayor media global y supera descriptivamente a D1 (+0.00855 [0.00496, 0.01215]) y P1 (+0.00520 [0.00386, 0.00654]), ambos contrastes positivos en 12/12 semillas. Sin embargo, durante la cohorte de sobrecarga WAPS y P1 prácticamente empatan en R/N (+0.00057 [−0.00025, +0.00139]); la ventaja global no equivale a que WAPS supere a las dos políticas en esa cohorte. En recuperación WAPS supera a P1 en R/N (+0.01427 [0.01053, 0.01802]), pero no claramente a D1 (+0.00155 [−0.00297, 0.00607]).
- **Descomposición de R/N:** episodio a episodio, `R/N = fracción SLA × competencia media de las alertas puntuales`. La descomposición simétrica de los productos atribuye descriptivamente parte de ΔR/N al cambio de puntualidad y parte al cambio de competencia media puntual:

| Perfil/cohorte | Contraste | Δ R/N | Contribución puntualidad | Contribución competencia puntual |
|---|---|---:|---:|---:|
| C / sobrecarga | WAPS−D1 | +0.01836 | +0.06610 | −0.04774 |
| C / sobrecarga | WAPS−P1 | +0.00145 | −0.00665 | +0.00810 |
| D / global | WAPS−D1 | +0.00855 | +0.02754 | −0.01898 |
| D / global | WAPS−P1 | +0.00520 | −0.00138 | +0.00658 |
| D / sobrecarga | WAPS−D1 | +0.04651 | +0.07837 | −0.03185 |
| D / sobrecarga | WAPS−P1 | +0.00057 | −0.00006 | +0.00063 |
| D / recuperación | WAPS−D1 | +0.00155 | +0.00421 | −0.00266 |
| D / recuperación | WAPS−P1 | +0.01427 | −0.00757 | +0.02184 |

En el perfil D, la ventaja global WAPS−D1 coexiste con una competencia media puntual inferior; la contribución de SLA la compensa parcialmente. Frente a P1, la ganancia R/N se asocia principalmente a mayor competencia puntual, pese a una pequeña pérdida de puntualidad. En la sobrecarga D, WAPS y P1 son prácticamente iguales tanto en R/N como en puntualidad. Esta identidad contable no aísla mediación causal ni identifica qué asignaciones individuales explican la diferencia.

## Relación cualitativa con OLD MODEL / MODELO VIEJO

Los mapas y estudios del OLD MODEL documentan ventaja de D1 en bastantes condiciones de menor presión, ventaja de P1 en sobrecarga más severa/prolongada por protección de deadlines y ganancias de HLS-B dependientes del punto de carga, duración y ponderación de escenarios; la adaptación no gana en todas las transiciones. El NEW MODEL reproduce cualitativamente: D1 retiene R/N con carga moderada, P1 eleva puntualidad bajo congestión prolongada, y la ventaja de HLS-B depende del régimen. La señal global positiva de HLS-B en D es compatible con la complementariedad, pero no demuestra un mecanismo ni traslada la validación OLD. El OLD MODEL requiere L1 inicial y posible segunda etapa L2; NEW MODEL enruta tras triaje a una investigación única. También difieren roster, servicios, deadlines, mezcla, horizontes y definición experimental. No se comparan cifras absolutas. Referencias: [`SOC_HLS_FINAL_OPERATING_MAP.md`](../soc_human_ai_organization/SOC_HLS_FINAL_OPERATING_MAP.md) y [`SOC_HLSB_VALIDATION_RESULTS.md`](../soc_human_ai_organization/SOC_HLSB_VALIDATION_RESULTS.md). El manuscrito LaTeX vigente sigue siendo OLD MODEL.

## Validaciones y límites

- El runner verifica en cada episodio hashes de traza y ambiente compartidos por política; igualdad de alertas/rutas/matriz TP-FP-TN-FN; investigación única; ruta de acuerdo con recomendación; elegibilidad; deadlines originales; y suma de estados SLA igual a admitidas. Se regeneraron dos veces las trazas y realizaciones ambientales de una semilla en cada perfil: los objetos y hashes coinciden con los registros. El evaluador de HLS-B usa llegadas observadas hasta el instante de despacho; las pruebas focalizadas de aislamiento de información permanecen aplicables.
- Se confirmó igualdad estructural de roster, políticas, generación, deadlines, flujo, costes y parámetros entre los cuatro perfiles; solo cambian tasas/ventanas/horizontes/metadatos del experimento. Los cuatro JSON conservan el mismo SHA de organización. Los cortes dejan 168 h de drenaje; ninguna ejecución dejó pendientes.
- Se realizaron 144 episodios, sin campañas OLD MODEL ni nuevas campañas adicionales. Pruebas focalizadas ejecutadas: `test_policy_pilot.py` y `test_scenario_integration.py` (4 pasaron). `git diff --check`, parseo de los cuatro JSON y comprobación de enlaces Markdown locales pasan.
- Los contadores de épocas por modo suman el total de despachos; las duraciones integradas de D1/P1 suman exactamente cada horizonte de evaluación en los 48 episodios WAPS/HLS-B.
- El análisis usa 12 semillas; intervalos t descriptivos no son contrastes confirmatorios, y se presentan múltiples cohortes/contrastes sin ajuste. Los perfiles entre sí cambian el volumen y ponderación de las cohortes; el mismo número de semilla no hace idénticas sus realizaciones de pulso. Las conclusiones solo describen estos escenarios sintéticos y este endpoint de competencia modelada.
- Cola y trabajo residual ejecutado son observables distintos. No se estimó servicio futuro de alertas todavía en cola ni se reconstruyó un backlog total en horas. El estado temporal de modo HLS-B se obtiene integrando transiciones registradas a lo largo del horizonte; las decisiones por modo sí usan el contador exacto de épocas del motor.

## Recomendación

El piloto cumple su propósito exploratorio: muestra gradiente de congestión con duración y una posible ventaja global de WAPS solo en el pulso más largo, además de compensaciones por cohorte. No se necesita otra corrida ahora para responder estas preguntas descriptivas. Si se pretende afirmar superioridad adaptativa en NEW MODEL, se requerirá un protocolo confirmatorio con hipótesis primaria y escenario/cohorte preespecificados, más semillas emparejadas independientes y control explícito de multiplicidad; no se recomienda ampliar una cuadrícula extensa ni ajustar HLS-B con este piloto.

## Artefactos de reproducción

- [Perfiles JSON A–D](config/SOC_NEW_MODEL_OVERLOAD_PROFILE_A.json), [`B`](config/SOC_NEW_MODEL_OVERLOAD_PROFILE_B.json), [`C`](config/SOC_NEW_MODEL_OVERLOAD_PROFILE_C.json), [`D`](config/SOC_NEW_MODEL_OVERLOAD_PROFILE_D.json).
- [Runner reproducible](run_overload_intensity_pilot.py); ejecuta el adaptador existente y guarda la salida JSON completa.
- [Resultados, 144 ejecuciones, hashes, métricas, trazas horarias, decisiones de modo y diferencias](SOC_NEW_MODEL_OVERLOAD_INTENSITY_RESULTS.json).
- Configuración organizativa base: [`SOC_REFERENCE_V2_24X7_LOAD_REGIMES.json`](config/SOC_REFERENCE_V2_24X7_LOAD_REGIMES.json).
