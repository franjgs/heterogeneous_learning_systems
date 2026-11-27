# Validación confirmatoria del perfil D — NEW MODEL / MODELO NUEVO

> Este informe se refiere exclusivamente al **NEW MODEL / MODELO NUEVO**. El OLD MODEL / MODELO VIEJO y el manuscrito LaTeX actual corresponden a otra generación organizativa; sus cifras no se combinan con las de este estudio.

## Registro, procedencia y ejecución

El análisis exploratorio previo seleccionó el perfil D y motivó la hipótesis. Antes de generar las semillas confirmatorias se congelaron el protocolo y una copia idéntica de la configuración D en el commit `47c1c1c810f404b552f77140aed1c33743f475fc`. El commit de partida era `1eade759c6fb8f46275a797d627f76d9a3a1acfd`, rama `research/soctra-hls-new-model`.

- Protocolo: [SOC_NEW_MODEL_PROFILE_D_CONFIRMATORY_PROTOCOL.md](SOC_NEW_MODEL_PROFILE_D_CONFIRMATORY_PROTOCOL.md).
- Configuración congelada: [SOC_NEW_MODEL_PROFILE_D_CONFIRMATORY.json](config/SOC_NEW_MODEL_PROFILE_D_CONFIRMATORY.json), SHA-256 `10733bf5f5a890e312163f96028b4bdc3b1cf36da3e278f6411a7c29b8535efc`, igual byte a byte al perfil D exploratorio.
- Organización: SHA-256 `9c055bf7341e36d71788cd7cc9b8d6a7220ddd1889d7972cf11f38a0175fbc9b`.
- Semillas fijadas: `2026112901–2026112960`; 60 episodios emparejados por política, **180 ejecuciones confirmatorias**. El piloto exploratorio no entra en los contrastes. Como verificación técnica fuera de la muestra se ejecutaron además tres lotes de replay de las tres políticas sobre la primera semilla prefijada (`2026112901`): **9 ejecuciones técnicas**, no incluidas en n ni en pruebas.
- Resultados íntegros por ejecución y hashes: [SOC_NEW_MODEL_PROFILE_D_CONFIRMATORY_RESULTS.json](SOC_NEW_MODEL_PROFILE_D_CONFIRMATORY_RESULTS.json).
- Resumen estadístico reproducible: [SOC_NEW_MODEL_PROFILE_D_CONFIRMATORY_ANALYSIS.json](SOC_NEW_MODEL_PROFILE_D_CONFIRMATORY_ANALYSIS.json), generado por [analyze_confirmatory_profile_d.py](analyze_confirmatory_profile_d.py).

Para reproducir las 180 ejecuciones confirmatorias desde el repositorio, el API usado fue `run_policy_pilot.run_pilot(config, range(2026112901, 2026112961))`, con la configuración congelada enlazada arriba; el JSON de resultados conserva el mismo bloque de semillas, hashes y registros. El postproceso se reproduce con `python studies/soc_triage_hls_availability_robustness/analyze_confirmatory_profile_d.py studies/soc_triage_hls_availability_robustness/SOC_NEW_MODEL_PROFILE_D_CONFIRMATORY_RESULTS.json --output studies/soc_triage_hls_availability_robustness/SOC_NEW_MODEL_PROFILE_D_CONFIRMATORY_ANALYSIS.json`.

Se usó el runner existente `run_policy_pilot.py` y la misma configuración D: triaje automático e investigación única, disponibilidad individual 24x7, demanda ordinaria 96 h (ρL1=0.85), pulso 48 h (ρL1=1.25), recuperación 48 h (ρL1=0.65), admisión 192 h y corte 360 h. Se conservaron plantilla, perfiles, mezcla, clases, deadlines, clasificador, tasas y reglas de las políticas. `alpha=0.50`, `beta=0`, `gamma=1`. Las semillas exploratorias `2026112801–2026112812` se usaron únicamente para dimensionar el estudio.

## Dimensionamiento y contraste

La planificación precedió a la ejecución. En las 12 diferencias exploratorias de perfil D, la media (DE muestral) fue 0.008552 (0.005657) para HLS-B−D1 y 0.005200 (0.002104) para HLS-B−P1. Se tomó la mayor DE observada como base conservadora. Con prueba t no central unilateral, α=0.05, potencia marginal objetivo 95% y efecto de planificación anclado al menor efecto exploratorio (0.00520), el tamaño aproximado es 15, 31 o 53 semillas con 1×, 1.5× o 2× la DE máxima (0.005657), respectivamente. Se eligieron **60 episodios**. Para 2× variabilidad, la cota de unión implica potencia conjunta de al menos 90% si cada contraste alcanza 95%; la mitad del menor efecto exploratorio requeriría aproximadamente 207 episodios con esa variabilidad. La mitad es una sensibilidad, no un umbral de relevancia. No se fijó un umbral práctico o económico.

La hipótesis primaria conjunta exige que la media por episodio de HLS-B−D1 **y** HLS-B−P1 sea positiva. Se aplicaron dos pruebas t pareadas unilaterales, cada una con α=0.05; se declara superioridad conjunta solo si ambas se rechazan (intersección-unión). Se muestran IC t bilaterales del 95%. La unidad estadística es la semilla/episodio, no cada alerta.

## Resultado primario

Medias entre los 60 episodios. R/N es la suma de competencia modelada de alertas finalizadas dentro del SLA y del corte, dividida por todas las alertas admitidas. Las tardías y pendientes aportan cero al numerador. No hubo pendientes al corte.

| Política | R/N medio (DE) | SLA dentro del plazo | Calidad modelada entre completadas | Espera hasta servicio (h) |
|---|---:|---:|---:|---:|
| D1 | 0.63200 (0.03000) | 78.05% | 0.81004 | 2.766 |
| P1 | 0.63583 (0.03165) | 81.68% | 0.77640 | 2.733 |
| HLS-B / WAPS | 0.64049 (0.03194) | 81.49% | 0.78762 | 2.742 |

| Contraste primario | Δ R/N media | DE pareada | IC95% bilateral | t (59 gl) | p unilateral | Semillas Δ>0 | Δ relativa al control |
|---|---:|---:|---:|---:|---:|---:|---:|
| HLS-B − D1 | +0.008483 | 0.006608 | [+0.006775, +0.010190] | 9.943 | 1.59×10⁻¹⁴ | 55/60 | +1.342% |
| HLS-B − P1 | +0.004656 | 0.001622 | [+0.004237, +0.005075] | 22.237 | 1.14×10⁻³⁰ | 60/60 | +0.732% |

**Conclusión primaria:** ambos contrastes rechazan sus nulos direccionales con α=0.05 y ambos IC95% quedan por encima de cero. La hipótesis de superioridad conjunta de HLS-B frente a D1 y P1 queda respaldada para este perfil sintético y esta implementación. Es validación independiente por semillas en el perfil D congelado; no valida universalmente la ventaja adaptativa ni otros perfiles.

El SLA de HLS-B fue 3.44 puntos porcentuales mayor que D1 y 0.19 pp menor que P1. Su calidad media modelada entre completadas fue menor que D1 (−0.02243) y mayor que P1 (+0.01122). Así, HLS-B−D1 combina mayor puntualidad con menor calidad media; HLS-B−P1 combina mayor calidad modelada con puntualidad ligeramente inferior. R/N integra ambos componentes. Son descripciones contables, no mediación causal.

## Resultados secundarios por cohorte de llegada

La cohorte depende del instante de llegada y las alertas se siguen hasta el corte de 360 h aunque terminen después de cambiar el régimen. Valores son medias entre semillas.

| Cohorte | Alertas medias | Política | R/N | SLA | Calidad entre completadas | Espera (h) |
|---|---:|---|---:|---:|---:|---:|
| Ordinaria | 1,585.12 | D1 | 0.79717 | 99.991% | 0.79725 | 0.113 |
|  |  | P1 | 0.77545 | 99.999% | 0.77546 | 0.114 |
|  |  | HLS-B | 0.77984 | 99.999% | 0.77984 | 0.114 |
| Sobrecarga | 1,171.12 | D1 | 0.44644 | 53.18% | 0.82697 | 5.756 |
|  |  | P1 | 0.49356 | 62.99% | 0.77772 | 5.595 |
|  |  | HLS-B | 0.49415 | 63.00% | 0.78600 | 5.626 |
| Recuperación | 613.70 | D1 | 0.56037 | 68.97% | 0.81067 | 3.890 |
|  |  | P1 | 0.54771 | 70.18% | 0.77629 | 4.015 |
|  |  | HLS-B | 0.56087 | 69.14% | 0.81076 | 4.004 |

| Cohorte | Contraste | Δ R/N (IC95% t) | Δ SLA, pp (IC95% t) |
|---|---|---:|---:|
| Ordinaria | HLS-B−D1 | −0.01733 [−0.01823, −0.01643] | +0.008 [−0.002, +0.019] |
|  | HLS-B−P1 | +0.00439 [+0.00388, +0.00489] | 0.000 [0.000, 0.000] |
| Sobrecarga | HLS-B−D1 | +0.04772 [+0.04291, +0.05252] | +9.816 [+9.160, +10.473] |
|  | HLS-B−P1 | +0.00059 [+0.00013, +0.00106] | +0.007 [−0.017, +0.031] |
| Recuperación | HLS-B−D1 | +0.00050 [−0.00096, +0.00196] | +0.167 [−0.003, +0.338] |
|  | HLS-B−P1 | +0.01316 [+0.01147, +0.01485] | −1.044 [−1.253, −0.835] |

Los contrastes de cohorte son secundarios, correlacionados dentro de semilla y sin ajuste confirmatorio por multiplicidad. Descriptivamente, D1 domina R/N en el tramo ordinario; en el pulso HLS-B y P1 casi empatan R/N y SLA, y ambos muestran mayor puntualidad que D1; durante recuperación HLS-B supera a P1 en R/N pero queda prácticamente igual que D1. No aparece una ventaja localizada de HLS-B frente a ambas políticas fijas en recuperación.

## Congestión y comportamiento de HLS-B

La presión se concentra en L1: utilización media por servicio en ordinario/pulso/recuperación fue 0.846/0.999/0.914; en L2 fue 0.157/0.233/0.126. En la trayectoria horaria media de L1, la cola creció desde aproximadamente 1.6 alertas al inicio del pulso hasta 211.4 al final (hora 144), y descendió a 73.4 en hora 168, 14.3 en hora 180 y 0.6 al fin de admisión (hora 192). La cola media horaria de L2 no superó 0.1; su máximo medio por episodio fue cerca de una alerta. Es una evolución observada con llegadas y asignaciones conjuntas; no identifica causalmente un mecanismo de HLS-B.

HLS-B registró 1,806 cambios de modo en 60 episodios: 1,018 en L1 y 788 en L2 (media 30.1 por episodio). Integrando el último modo hasta el corte de 360 h, permaneció en P1 durante 38.3% del tiempo L1 y 6.95% del tiempo L2. Son contadores y ocupación de estado; no demuestran que conmutar causara la diferencia.

En promedio hubo 3,369.93 alertas por episodio: TP=286.18, FP=134.27, TN=2,895.18 y FN=54.30. Los hashes de traza y ambiente, conteos, confusiones y rutas fueron idénticos entre políticas por semilla. Cada alerta recibió una investigación, las rutas respetaron TP/FP→L2 y TN/FN→L1, y no hubo pendientes al corte en ninguna ejecución.

## Interpretación, OLD MODEL y límites

El patrón cualitativo coincide con el OLD MODEL en que la carga elevada hace visible un compromiso entre puntualidad y calidad modelada, y puede cambiar la ordenación relativa. Sin embargo, las rutas directas por recomendación, investigación única, plantilla, servicio, demanda y estimando son distintos. No se comparan magnitudes absolutas ni se infiere continuidad causal. Los resultados confirmatorios históricos del OLD MODEL no validan este flujo.

La ventaja primaria aparece en el promedio del perfil D, no en todos sus regímenes: en ordinario HLS-B pierde R/N frente a D1; en recuperación no muestra diferencia clara frente a D1 y sí supera a P1. La agregación depende del volumen de cada cohorte y sus resultados terminales.

Limitaciones: D fue escogido tras una campaña exploratoria; las semillas nuevas son independientes, pero la selección del perfil no lo es. La inferencia es condicional al perfil sintético. La prueba t se basa en 60 diferencias de episodio y presupone una distribución de medias razonable. Competencia es calidad esperada modelada, no corrección empírica validada. Los análisis por cohorte y mecanismos son descriptivos. En esta configuración `beta=0` y `gamma=1` son neutros; `alpha=0.50` sí reduce el servicio FP en L2. No se ejecutaron contrafactuales para atribuir ganancias a transiciones adaptativas.

**Recomendación:** conservar el resultado como validación confirmatoria acotada de la hipótesis conjunta en perfil D. No hace falta repetir este contraste ni ajustar HLS-B. Afirmaciones para otras cargas, mezclas o parámetros requieren evidencia con estimandos que cubran esas condiciones; no se recomienda automáticamente otra campaña.

## Validaciones técnicas

El runner verificó por semilla hashes idénticos de traza exógena y `EnvironmentRealization`, alertas, confusión y rutas. El postproceso revalidó 60 semillas × 3 políticas, una investigación por alerta, rutas, estados y cero pendientes. El replay de la semilla `2026112901` coincidió en todos los registros bajo comparación JSON canónica; la primera comparación directa solo detectó la conversión normal de claves de `investigation_counts` entre enteros Python y cadenas JSON. Se verificaron los hashes de configuración y organización indicados. Pruebas focalizadas `test_policy_pilot.py`, `test_scenario_loader.py` y `test_triage_execution.py`: **37 pasaron**. No se ejecutaron campañas OLD MODEL ni regresiones masivas. Los informes, JSON por ejecución y análisis reproducible no cambian motores, políticas, configuraciones históricas ni manuscritos LaTeX.
