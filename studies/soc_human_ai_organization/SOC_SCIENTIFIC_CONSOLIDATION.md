# Consolidación científica del estudio organizativo SOC

**Estado:** punto de retorno científico **anterior a HLS-A/HLS-B**. A0 y comparación D1/P1–P5 fueron revisadas contra código, configuraciones y CSV locales. Este documento conserva su evidencia exploratoria sin recalcularla ni reemplazarla. La validación posterior de [D1 frente a P1](SOC_CONFIRMATORY_RESULTS.md) confirma una mejora condicionada bajo sobrecarga sintética, separada de esta muestra. Los supervisores posteriores se documentan en [HLS-A](SOC_HLS_ADAPTIVE_SUPERVISOR.md) y [HLS-B](SOC_HLSB_VALIDATION_RESULTS.md); sus resultados no alteran este estado previo.

## 1. Pregunta científica y alcance

¿En qué condiciones una organización distinta de D1 aumenta el rendimiento esperado de un equipo SOC heterogéneo sin ampliar su plantilla? El estudio organizativo constituye aproximadamente el 45 % del artículo HLS previsto. SOCTRA informa el contexto de triaje y demanda, pero la campaña aquí revisada usa alertas sintéticas y no prueba la integración experimental de predicciones históricas SOCTRA.

## 2. Modelo y políticas efectivas

El motor de `src/hls/rq1_allocation.py::simulate` admite alertas con clase, llegada y deadline, servicio secuencial no preventivo, analistas con elegibilidad y competencia, despacho tras cada evento y colas pendientes ilimitadas. `src/hls/rq1_l1_l2.py::simulate_l1_l2` hace entrar en L2 las alertas escaladas al terminar L1; `metrics` utiliza la finalización L2 para su resultado terminal. La ruta de escalado de esta campaña procede de una recomendación IA sintética aceptada según una regla fija. No se pierde una alerta por vencer.

`_dispatch_d1` elige secuencialmente en orden de analistas aleatorio reproducible según riesgo de deadline, competencia propia y elegibilidad de compañeros. `_dispatch_local_priority` (P1) minimiza holgura posterior al servicio; `_dispatch_local_competence` (P2) prioriza competencia propia; `_dispatch_local_capacity` (P3) prioriza menor número de otros libres elegibles, luego competencia. `_dispatch_soc_policy` llama en P4 al matching de `_dispatch_coordinated` y en P5 lo compara con P3: P5 activa P4 sólo cuando mejora lexicográficamente (finalizaciones previstas a tiempo, número de asignaciones), considerando la latencia. La C central secuencial de A3.2 usa otro selector y no es P4. Véase [Fundamentos y modelo](SOC_FOUNDATIONS_AND_MODEL.md) para las reglas y límites.

## 3. Diseño experimental y estimando

| Campaña | Diseño y semillas | Propósito | Métrica principal publicada |
|---|---|---|---|
| [A0 congestión](SOC_A0_BASELINE_CONGESTION.md) | D1; 14 configuraciones × 30 semillas `261140000–261140029`; H=24 h, D=24 h | Respuesta a carga y plantilla | SLA, colas, espera, pendientes; calidad esperada por completadas |
| [A0 debilidades](SOC_A0_D1_ORGANIZATIONAL_WEAKNESSES.md) | D1; tres cargas × seis semillas `261140000–261140005`; H/D idénticos | Contrastes de orden y bloqueo | Pérdida local potencial y R/N diagnóstico |
| [D1/P1–P5](SOC_POLICY_COMPARISON_RESULTS.md) | Cuatro cargas principales y tres plantillas × 20 semillas `261140000–261140019`; seis políticas; coste cero y coste supuesto; H/D idénticos | Comparación pareada exploratoria | R/N en H y H+D |
| [A3.2](SOC_A3_2_PILOT_COMPARISON.md) | Siete configuraciones × 20 semillas `261132000–261132019`; D1/T/Q/C/C ideal | Piloto de centralización secuencial | SLA, calidad esperada y correcta a tiempo realizada con Bernoulli común |

En la campaña principal, \(R(c)/N=N^{-1}\sum_a e_{i(a),k(a)}(1-0,35\,difficulty_a)\,\mathbf 1\{completion_a\leq d_a,\ completion_a\leq c\}\), con \(c=H\) o \(H+D\); para escaladas, \(i(a)\) y `completion` corresponden a L2. **N siempre es el número admitido**, y una pendiente aporta cero en ese corte. La calidad entre completadas tiene otro denominador. La dificultad y competencia son sintéticas; R/N es una esperanza modelada, no exactitud humana observada. A3.2 también informa una realización Bernoulli: no es la misma métrica que R/N de esta campaña.

El CSV `results/soc_policy_comparison/episodes.csv` tiene 3.360 filas de corte: 7 escenarios × 20 semillas × 2 condiciones de coste × 6 políticas × 2 cortes, correspondientes a 1.680 ejecuciones política–episodio. `summary.csv` contiene media, desviación, diferencia pareada, IC95 % t con 19 grados de libertad y frecuencia de mejora. Los SHA-256 de trazas, admitidas y semillas coinciden dentro de cada escenario; el D1 de las 20 semillas comunes coincide exactamente con el CSV A0 en admitidas y SLA terminal. Los IC son exploratorios, sin corrección por multiplicidad.

## 4. Caracterización de D1 (A0)

La capacidad fluida L1 calculada para roster, mezcla y servicios hipotéticos fue 28,42 alertas/h. En la serie de 30 semillas, la utilización media L1 subió de 0,888 en \(\rho=0,85\) a 0,980 en 1,00 y 0,995 en 1,25; la cola L1 máxima media en H creció de 16,0 a 56,5 y 214,6. El P95 de espera L1 creció de 0,753 a 4,999 y 11,912 h. El SLA en H/terminal pasó de 0,976/0,994 a 0,918/0,994 y 0,602/0,777. Con el escalado base L2 permaneció por debajo de 0,38 de utilización media. No hubo descartes ni censura tras D=24 h en estas corridas. Las pendientes en H sí fueron relevantes.

El SLA terminal cercano al techo en \(\rho=1\) coexiste con una cola grande porque se detienen las llegadas en H y continúa el servicio durante D. Por ello se mantienen separados ambos cortes. La cola media de A0 se integra en H, mientras la tabla secundaria de la campaña comparativa la integra en H+D; esas cifras no deben cotejarse como si fueran la misma medida.

## 5. Debilidades organizativas observadas

En seis semillas por carga, las inversiones de holgura fueron 562/3.459, 1.096/4.021 y 1.619/5.045 decisiones L1 para \(\rho=0,85/1,00/1,25\). El contraste de dos servicios consecutivos halló ganancia local esperada positiva en 0, 0 y 1.484 decisiones, respectivamente: 29,4 % de las decisiones en 1,25, con media de 0,6219 entre casos positivos. Esa proporción **no** es mejora recuperable del episodio: las alternativas se solapan y pueden modificar otras tareas y L2. El contraste usa un proxy de calidad del evaluador, incluida dificultad simulada, que D1 no observa.

El tiempo medio de reloj en H con una alerta high pendiente y todos sus L1 elegibles ocupados fue 3,193/5,241/12,996 h. No se observó tiempo ocioso con trabajo elegible después del despacho ni intercambio simultáneo factible en esas 18 trayectorias. El bloqueo señala falta momentánea de capacidad elegible; A0 no establece qué parte podría evitar otra organización.

## 6. Resultados comparativos D1/P1–P5

Medias de R/N terminal **sin latencia ni coste**, con las mismas 20 semillas por carga. Entre corchetes: IC95 % de la diferencia pareada respecto a D1. La selección de la mayor media por escenario es descriptiva, no un contraste confirmatorio.

| Carga \(\rho\) | D1 | P1 | P2 | P3 | P4 | P5 |
|---:|---:|---:|---:|---:|---:|---:|
| 0,65 | 0,6394 | 0,6364 | 0,6416 | 0,6416 | 0,6370 | 0,6418 |
| 0,85 | 0,6550 | 0,6344 | 0,6555 | 0,6555 | 0,6347 | 0,6559 |
| 1,00 | 0,6699 | 0,6343 | 0,6698 | 0,6698 | 0,6342 | 0,6701 |
| 1,25 | 0,5280 | 0,6278 | 0,4859 | 0,4859 | 0,6336 | 0,6167 |

En 1,25: P1−D1 = **+0,0998 [0,0825; 0,1172]**, P4 ideal−D1 = **+0,1056 [0,0844; 0,1268]** y P5 ideal−D1 = **+0,0887 [0,0724; 0,1050]**. P2/P3−D1 = **−0,0421 [−0,0539; −0,0302]**. En 0,85 y 1,00, P1 y P4 redujeron R/N respecto a D1; P2/P3 fueron idénticas **por episodio** en esta matriz, aunque sus reglas difieren en el código. Las diferencias pequeñas de P5 a menor carga no prueban una mejora general, especialmente tras escoger la mayor media entre políticas.

## 7. Efecto del régimen de carga

La ventaja de P1/P4 aparece aquí cuando el sistema ya está sobrecargado y el SLA deja de estar cerca del techo. En \(\rho=1,00\), P1 y P4 ideal reducen algo espera y cola en H, pero el SLA terminal cambia menos de 0,001 y la calidad modelada cae; R/N disminuye aproximadamente 0,036. Esto muestra que una mejora temporal parcial no basta para mejorar el objetivo conjunto en todo régimen. No se extrapola un umbral operativo GMV a partir de cuatro tasas sintéticas.

## 8. Compromiso entre calidad y puntualidad

En \(\rho=1,25\), el SLA terminal D1/P1/P4 ideal fue 0,7689/0,9849/0,9929 y la calidad esperada entre completadas 0,6762/0,6376/0,6383. La ganancia de puntualidad compensó esa pérdida de calidad en R/N. P2/P3 elevaron levemente la calidad entre completadas a 0,6791, pero el SLA cayó a 0,7068 y R/N a 0,4859. Para prioridad high, el SLA terminal D1/P1/P4 ideal fue 0,7710/0,9620/0,9640. Estas son consecuencias del modelo y sus deadlines, no medidas de analistas reales.

## 9. Interpretación de P4 y P5

El diagnóstico `results/soc_policy_comparison/matching_diagnostics.csv` registra **0 épocas con ≥2 asignaciones simultáneas** en 80 trazas principales P4 y 80 P5 (L1 y L2). A1 y A3.2 también observaron cero matching factible de cardinalidad ≥2 en sus muestras, aunque el motor admite eventos simultáneos que sí lo permitirían. Así, la ventaja P4 en 1,25 no identifica valor incremental del matching conjunto: en estas trazas su regla realiza selección central de una pareja a la vez, con objetivo temporal diferente al de D1/P1. La explicación por mejor prioridad temporal es **compatible** con el SLA y el diagnóstico A0, pero falta una ablación causal que separe criterio, información global y selección de analista. P5 tampoco mostró matching múltiple; su comparación frente a P3 sólo identifica la activación de su criterio conjunto local al estado.

## 10. Sensibilidad a costes y plantilla

Con latencia hipotética de 0,05 h por época coordinada y coste de 1 unidad abstracta por arista elegible, en 1,25 P4 bajó de R/N 0,6336 a **0,5538**: diferencia frente a D1 **+0,0258 [0,0091; 0,0424]**. P5 bajó de 0,6167 a **0,6003**, diferencia **+0,0723 [0,0571; 0,0876]**. El recurso abstracto no se monetiza ni se resta de R/N. La evaluación de matching que hace P5 aun cuando retorna a P3 carece de coste contabilizado; sus resultados con coste pueden ser optimistas. P4 paga incluso al asignar una sola alerta, como define esta implementación, aunque tal operación no se ha validado operativamente.

Con demanda fija de 18,472/h, la plantilla de seis/cinco/cuatro L1 produjo D1 R/N 0,6394/0,6520/0,6865; P1 0,6364/0,6410/0,6531 y P4 ideal 0,6370/0,6412/0,6548. El aumento de R/N D1 al reducir personal **no** significa mejora de capacidad: cambian los perfiles activos, el reparto y la calidad entre completadas; aumentan congestión y esperas (véase A0). El efecto de políticas sobre R/N no es monótono en esta serie. `staff_6` repite la misma configuración y semillas que `rho_065`; no constituye evidencia independiente.

## 11. Contribuciones científicas respaldadas

**Q1.** En el simulador, sí existe una región examinada donde otra regla aumenta R/N sin contratar analistas: 1,25 para P1/P4/P5. Es una comparación de episodios pareados, no una validación de eficacia en GMV.

**Q2.** La ventaja depende del régimen: P1/P4 pierden R/N con SLA terminal cercano al techo, mientras ganan en la sobrecarga estudiada. La dependencia se observa en las celdas probadas; el punto de transición exacto no está estimado.

**Q3.** Hay valor observado de priorización temporal bajo sobrecarga y un compromiso cuantificado con calidad. P2/P3 no aportan mejora conjunta en esa celda; P3 no se diferencia empíricamente de P2 en esta matriz. El valor incremental de matching no se identifica porque no se activó la asignación múltiple. Tampoco se ha aislado un beneficio causal de información global frente a prioridad individual.

## 12. Limitaciones y amenazas a la validez

Plantilla, elegibilidad, competencias estáticas, velocidad, servicio, deadlines, escalado, IA y coste de coordinación son supuestos sintéticos; no hay calibración operativa GMV-CERT ni registros SOCTRA en esta campaña. Las llegadas son Poisson homogéneas y el modelo carece de preempción, colas finitas, descartes, turnos, cambios de competencia y calidad humana observada. R/N usa corrección esperada, no resoluciones adjudicadas. El drenaje mejora algunas métricas terminales después de detener la demanda. La selección descriptiva del mejor resultado entre varias políticas y escenarios aumenta el riesgo de sobreinterpretar IC exploratorios sin ajuste por multiplicidad. Las semillas de A0 y comparación se solapan deliberadamente; A3.2 usa semillas y configuraciones distintas. `results/` está excluido de Git: un checkout limpio contiene la [tabla agregada versionada](evidence/soc_policy_comparison_rn_terminal.csv) y los scripts/configuraciones, pero no los CSV por episodio necesarios para recalcular directamente los IC sin regenerar la campaña.

## 13. Afirmaciones defendibles para el artículo

El modelo permite estudiar cómo una regla temporal y una selección central actual modifican puntualidad y calidad cuando crece la carga. En la sobrecarga sintética 1,25, P1/P4/P5 elevan R/N respecto al D1 definido, con costes y compensaciones explicitados. Con carga inferior, P1/P4 pueden reducir R/N. La frase sobre P4 debe referirse a **selección central según su objetivo implementado**, no a una ganancia demostrada de matching. La contribución defendible hoy es una comparación condicionada y reproducible de mecanismos de organización; no una afirmación universal ni una mejora medida del SOC de GMV.

## 14. Cuestiones pendientes de confirmación

Una afirmación confirmatoria requeriría preespecificar contraste principal y tratamiento de multiplicidad, evaluarlo con semillas independientes de las usadas aquí, confirmar robustez ante parámetros operativos plausibles y aclarar con evidencia externa deadlines, carga de trabajo real, tiempos de servicio, competencias y coste de coordinación. También se necesita identificar causalmente qué parte de P4 corresponde a su criterio temporal o información central; estas campañas no activaron matching múltiple. Son límites de la evidencia disponible, no tareas iniciadas por esta consolidación.

**Procedencia verificable:** código `src/hls/rq1_allocation.py`, `src/hls/rq1_l1_l2.py`; configuración `config/a0_baseline_congestion.json`, `config/soc_policy_comparison.json`, `config/a3_2_pilot.json`; scripts `run_a0_baseline_congestion.py`, `analyze_a0_weaknesses.py`, `run_soc_policy_comparison.py`, `diagnose_soc_matching.py`, `run_a3_2_pilot.py`; CSV y `run_metadata.json` en los directorios locales `results/soc_a0_baseline_congestion/`, `results/soc_a0_weaknesses/`, `results/soc_policy_comparison/` y `results/soc_a3_2_pilot/`.
