# HLS-CE-07.5 — Resultados confirmatorios de estructura de competencias

**Fecha:** 2026-10-26
**Estado:** campaña conforme al protocolo completada; 60/60 réplicas válidas.
**Alcance:** comparación de las estructuras A y B especificadas, N=12, K=4, bajo P1 de CE-04 sin cambios. Evidencia limitada al escenario sintético descrito.

## 1. Pregunta y configuración

Se comparó si dos distribuciones conjuntas distintas de competencias, con idénticas marginales por función, producen distinto rendimiento colectivo bajo una política y condiciones operativas fijas. En A hay tres agentes con competencia 0,9 en las cuatro funciones y nueve con 0,6 en todas. En B hay doce especialistas, tres por función, con 0,9 en su función y 0,6 en las restantes. En ambas estructuras, la media de cada función es exactamente `27/40 = 0,675` y el máximo es 0,9.

Se mantuvieron horizonte 400, llegadas Poisson de tasa total 6,6, cuatro marcas de tarea equiprobables e independientes del tiempo, servicio lognormal de CE-04 (media 1,25; CV 0,30), plazo llegada+3, colas FCFS y una tarea en servicio por agente. P1 original (`q_ik × F_i`); sin aprendizaje ni cooperación. Se evaluaron semillas 30100–30129 en A y B: 30 pares, **60 réplicas confirmatorias válidas**.

Cada semilla generó una permutación reproducible de perfiles a slots con flujo `[seed, 12, 707]`, compartida por A y B. Las 30 permutaciones variaron. Se emparejaron demanda, servicio y potenciales de corrección por tarea-agente. El desempate mantuvo la prioridad por slots generada por CE-04; no se modificó P1.

Hash científico congelado: `b5ab97c31e937e590ded4c99e861345c60dfd18d850edb8788c283752f6c2907`. SHA-256 del código CE-04: `2ac84e7c1c152f03da1cf139194c83bf0add783bdd028ae4608c5eec8bf47adb` (igual al código de la base). Ejecutor y entorno quedan identificados en el manifiesto. Tiempo de la campaña válida: **42,15 s de pared; 43,47 s de CPU**. RSS máximo: **475,873,280 bytes** según `ru_maxrss` de esta plataforma.

### Incidencia de protocolo y preservación

La primera ejecución de 60 réplicas reutilizó `ce04.generate_workload`, que asigna probabilidades familiares diferentes por segmentos temporales. Esa ejecución no cumplía el requisito CE-07 de demanda familiar estacionaria y se excluyó completamente de los resultados confirmatorios. Sus artefactos se conservaron en [`attempt_01_nonstationary_ce04_demand/`](../../../results/experiments/hls_ce07_confirmatory/attempt_01_nonstationary_ce04_demand/) con estado explícito de desviación. Se corrigió únicamente el generador de marcas de tarea del ejecutor CE-07: mantuvo el flujo Poisson de llegadas de CE-04 y usó marcas iid uniformes en las cuatro familias; CE-04 y P1 no se modificaron. A continuación se ejecutaron las 60 réplicas válidas con las mismas semillas asignadas, sin selección por resultado. La validación de workload reconstruyó las 30 entradas y sus hashes emparejados.

Esta discrepancia también afecta la fidelidad de demanda del piloto CE-07.3, cuyo ejecutor reutilizó el generador de familias por fases de CE-04. Su registro histórico permanece intacto, pero no se utiliza como confirmación técnica de la demanda estacionaria. La auditoría CE-07.4 sigue describiendo correctamente los empates que están en esos registros; no valida la estacionariedad del piloto.

## 2. Validación, pruebas y análisis

Las 60 réplicas pasaron los validadores del adaptador CE-07: identidad/conservación de tareas, una asignación y resultado final por tarea admitida, capacidad/FCFS, resultados potenciales emparejados, marginales y consistencia de éxito en plazo. Las 30 parejas tuvieron idéntica demanda y potenciales, con una misma permutación por pareja. Se comprobaron 30 permutaciones únicas; la reconstrucción de los 30 workstreams coincidió con sus hashes registrados. No se detectaron fallos de validación, contaminación de réplicas ni cambios de CE-04/P1.

Pruebas focalizadas previas: `pytest -q tests/test_ce07_structure.py tests/test_ce07_pilot.py` — **9 passed**. También pasaron `py_compile` del ejecutor y `git diff --check`. Se comprobó determinismo de la generación estacionaria y se reconstruyeron las demandas por semilla (generación de entradas solamente, sin simulación adicional). No se ejecutó replay completo de las 60 simulaciones.

La unidad inferencial es la diferencia emparejada por semilla. Para `Delta = 100 × (Y_B − Y_A)` se usó IC95% percentile bootstrap por semillas, 10.000 remuestreos, prueba t pareada bilateral de media cero y TOST pareado con margen ±2 pp. No se remuestrearon tareas.

## 3. Resultado principal

| Resultado | Estimación |
|---|---:|
| Tasa media de éxito correcto y en plazo, A | 65,81% |
| Tasa media de éxito correcto y en plazo, B | 87,33% |
| Diferencia media emparejada B−A | **+21,52 pp** |
| SD entre 30 diferencias | 1,13 pp |
| Mediana de diferencias | +21,80 pp |
| IC95% bootstrap pareado | **[+21,12; +21,92] pp** |
| Contraste bilateral t pareado vs. 0 | `t(29)=103,93`; `p=7,41×10⁻³⁹` |
| TOST margen ±2 pp | `p=1,00`; equivalencia no establecida |
| Signo de diferencias | B>A en 30/30 pares |

El intervalo queda por encima de cero y del margen +2 pp. TOST no respalda equivalencia práctica dentro de ±2 pp. Este contraste estima la diferencia entre estas dos estructuras bajo la configuración especificada; no estima un efecto universal de “heterogeneidad”.

### Resultados por semilla

| Semilla | A éxito (%) | B éxito (%) | B−A (pp) | Empates A / B |
|---:|---:|---:|---:|---:|
| 30100 | 66.25 | 87.56 | +21.32 | 1154 / 825 |
| 30101 | 64.99 | 86.88 | +21.90 | 1287 / 775 |
| 30102 | 66.96 | 86.59 | +19.63 | 1236 / 817 |
| 30103 | 67.16 | 86.86 | +19.69 | 1250 / 820 |
| 30104 | 66.09 | 87.35 | +21.26 | 1259 / 918 |
| 30105 | 66.72 | 86.35 | +19.63 | 1210 / 765 |
| 30106 | 65.29 | 86.77 | +21.48 | 1285 / 796 |
| 30107 | 65.55 | 87.04 | +21.49 | 1256 / 799 |
| 30108 | 64.60 | 86.37 | +21.77 | 1266 / 813 |
| 30109 | 64.61 | 87.02 | +22.41 | 1255 / 857 |
| 30110 | 68.01 | 87.14 | +19.13 | 1309 / 821 |
| 30111 | 65.45 | 87.28 | +21.83 | 1282 / 820 |
| 30112 | 64.38 | 87.50 | +23.12 | 1244 / 850 |
| 30113 | 65.56 | 87.50 | +21.94 | 1283 / 830 |
| 30114 | 65.16 | 87.60 | +22.44 | 1229 / 814 |
| 30115 | 66.68 | 87.32 | +20.64 | 1299 / 836 |
| 30116 | 66.36 | 87.35 | +20.99 | 1280 / 865 |
| 30117 | 65.04 | 87.43 | +22.39 | 1300 / 821 |
| 30118 | 66.07 | 88.65 | +22.58 | 1205 / 837 |
| 30119 | 66.50 | 87.62 | +21.12 | 1284 / 831 |
| 30120 | 67.27 | 88.29 | +21.02 | 1301 / 857 |
| 30121 | 65.37 | 87.52 | +22.15 | 1246 / 840 |
| 30122 | 65.34 | 87.92 | +22.58 | 1218 / 826 |
| 30123 | 65.40 | 88.28 | +22.88 | 1259 / 832 |
| 30124 | 65.21 | 88.16 | +22.95 | 1199 / 824 |
| 30125 | 66.48 | 87.70 | +21.22 | 1274 / 807 |
| 30126 | 64.90 | 86.78 | +21.88 | 1292 / 801 |
| 30127 | 65.53 | 87.92 | +22.39 | 1287 / 845 |
| 30128 | 66.70 | 85.92 | +19.22 | 1199 / 814 |
| 30129 | 64.64 | 87.29 | +22.66 | 1222 / 804 |

## 4. Métricas secundarias

Media (SD entre réplicas) para cada organización; B−A es la media de diferencias emparejadas. Son descripciones, no contrastes confirmatorios adicionales.

| Métrica | A | B | B−A descriptivo |
|---|---:|---:|---:|
| Competencia media seleccionada | 0.7100 (0.0021) | 0.8917 (0.0019) | +0.1817 |
| Brecha de competencia a h=0,9 | 0.1900 (0.0021) | 0.0083 (0.0019) | -0.1817 |
| Utilización media | 0.6807 (0.0115) | 0.6809 (0.0133) | +0.0002 |
| SD de utilización entre agentes | 0.2485 (0.0087) | 0.0927 (0.0040) | -0.1558 |
| Gini de asignaciones | 0.1999 (0.0110) | 0.0728 (0.0040) | -0.1271 |
| Espera media admitidas | 0.4561 (0.0083) | 0.2657 (0.0212) | -0.1904 |
| Espera p95 admitidas | 1.6465 (0.0293) | 1.1988 (0.0559) | -0.4476 |
| Latencia media de completadas | 1.7070 (0.0128) | 1.5156 (0.0260) | -0.1915 |
| Latencia p95 de completadas | 3.0521 (0.0449) | 2.6271 (0.0681) | -0.4250 |
| Tardías por réplica | 147.93 (13.08) | 53.27 (11.35) | -94.6667 |
| Incorrectas completadas por réplica | 765.87 (27.53) | 285.50 (14.78) | -480.3667 |
| Empates exactos por réplica | 1255.67 (37.83) | 825.33 (28.41) | -430.3333 |

Hubo 0.0 rechazos en A y 1.0 en B (un rechazo en una réplica B); este evento se conserva en resultados.

### Éxito por familia y ventana temporal (descriptivo)

| Familia | A (%) | B (%) | B−A (pp) |
|---:|---:|---:|---:|
| F1 | 66.07 | 87.25 | +21.18 |
| F2 | 65.66 | 87.33 | +21.68 |
| F3 | 65.64 | 87.14 | +21.50 |
| F4 | 65.84 | 87.63 | +21.79 |

| Ventana temporal del horizonte | A (%) | B (%) | B−A (pp) |
|---|---:|---:|---:|
| t=0–150 | 66.29 | 87.34 | +21.05 |
| t=150–300 | 65.90 | 87.38 | +21.48 |
| t=300–400 | 64.98 | 87.28 | +22.31 |

La clasificación temporal es solo estratificación descriptiva; las familias se generaron con probabilidad 0,25 en todas las ventanas. Recuento regenerado de familias por ventana para los 30 workstreams validados (F1–F4): t=0–150: 7.265/7.368/7.498/7.379; t=150–300: 7.477/7.480/7.263/7.319; t=300–400: 5.006/4.881/4.926/4.985. Estas diferencias de conteo son variación muestral, no cambios de probabilidad. Los campos `phase` son etiquetas temporales y no representan regímenes de demanda distintos ni permiten inferir adaptación o recuperación ante cambios.

### Desempates

Se registraron **62.430** empates exactos: 37.670 en A y 24.760 en B. Tipos según la competencia de los candidatos para la familia actual: A tuvo 75 conjuntos todos `q=0,9` y 37.595 todos `q=0,6`; B tuvo 23.427 todos `q=0,9` y 1.333 todos `q=0,6`. No se observaron conjuntos empatados con niveles mixtos. Para los 62.430 registros, la selección coincide con el menor rango de prioridad P1. Las trazas incluyen candidatos, perfiles, competencia actual, score, probabilidad de plazo implícita, rangos y elegido. Conforme a CE-07.4, ello no identifica efectos futuros del desempate.

## 5. Relación con CE-04 y CE-06

CE-07 responde una pregunta más acotada dentro del programa general de HLS; no reemplaza ni resume la evidencia previa:

- **CE-04** estudió composiciones H0/H1/H2, políticas y escalas bajo demanda con cambios de mezcla temporal. En su configuración, H2 superó H0 bajo P1 aproximadamente 11,2–11,7 pp. Ese contraste no mantiene las mismas estructuras de competencia de CE-07 ni estima la misma magnitud. Véase [CE-04 confirmatorio](../CE-04/11_CONFIRMATORY_RESULTS.md).
- **CE-06** reutilizó las mismas 90 réplicas CE-04 a N=24 para diagnosticar selección y carga; mayor competencia seleccionada y éxito coexistieron descriptivamente con más espera y tardías, sin identificación de mediación por congestión. CE-06 no es una replicación independiente de CE-04. Véase [diagnóstico CE-06](../CE-06/01_HETEROGENEITY_DIAGNOSTICS.md).
- **CE-07** conserva exactamente las marginales y máximos y cambia la distribución conjunta: bajo P1, estructura B supera A en este escenario estacionario. Las medidas secundarias muestran más competencia seleccionada y menos concentración/espera/tardías en B. No identifican cuál de esas vías produce el efecto colectivo.

En conjunto, CE-04/06/07 muestran por qué HLS debe caracterizar estructuras, organización, demanda y restricciones sin tratar “heterogeneidad” como una propiedad absoluta. CE-04 y CE-06 informan efectos de composición/política y sus diagnósticos; CE-07 aporta el contraste más directo de dos estructuras con igual marginal bajo una política fija. Las campañas no comparten estimando ni condiciones y sus magnitudes no deben combinarse como si fueran una sola estimación.

## 6. Conclusión, alcance y limitaciones

**Conclusión respaldada:** con A/B tal como se definieron, N=12, cuatro funciones, familias iid equiprobables, servicio CE-04 y P1, B obtuvo mayor éxito correcto y en plazo que A: +21,52 pp de media emparejada, IC95% [+21,12; +21,92], positivo en 30/30 semillas. Como las marginales y máximos por función son idénticos, la diferencia observada no se debe a diferencias en esos resúmenes marginales; muestra que la estructura conjunta puede importar en esta comparación.

**No demostrado:** que B sea óptima; que la especialización en general sea superior; que el resultado se mantenga para otras escalas, estructuras, políticas, cargas, recursos, aprendizaje o cooperación; ni que la reducción de espera, carga o Gini sea el mediador causal. P1 es una política de información completa definida por la regla CE-04, no un óptimo global.

**Límites de evidencia:** escenario sintético, un N y dos estructuras; resultados potenciales simulados; no se hizo replay exacto de las 60 réplicas; el primer intento no estacionario se archiva y excluye; el piloto CE-07.3 comparte la desviación de familia por fases y no valida estacionariedad. No se detectaron otros fallos de validación o reproducibilidad en la campaña conforme.

## 7. Artefactos

Los 60 registros por réplica, métricas por familia/ventana, 30 contrastes emparejados, audit de demanda, configuración, trazas de empates y hashes están en [`results/experiments/hls_ce07_confirmatory/`](../../../results/experiments/hls_ce07_confirmatory/). Las trazas detalladas están comprimidas en `exact_tie_decisions.json.gz` (62.430 empates). El primer intento no conforme se preserva en su subdirectorio separado. El ejecutor es [`experiments/run_hls_ce07_confirmatory.py`](../../../experiments/run_hls_ce07_confirmatory.py).

**Cierre:** CE-07.5 queda ejecutada y documentada. Esta conclusión es parte del conocimiento acumulado de HLS junto a CE-04 y CE-06; no autoriza CE-08 ni experimentos adicionales.
