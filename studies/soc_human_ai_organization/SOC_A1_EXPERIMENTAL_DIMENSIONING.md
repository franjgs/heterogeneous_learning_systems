# A1 — Caracterización y dimensionamiento experimental

**Estado de la campaña:** calibración exploratoria completada; revisada posteriormente en la [consolidación científica](SOC_SCIENTIFIC_CONSOLIDATION.md). No es la comparación confirmatoria D1/P1.
**Revisión de código:** commit base `a0fdc87834b56884ec1200778d4fe2b7cbfd4699`; los cambios locales de esta A1 no están comprometidos.
**Ejecución:** 19 de noviembre de 2026, reloj local del entorno; sólo demanda sintética, sin leer el extracto SOCTRA.

## 1. Alcance y fuentes

Se reutilizaron `src/hls/ia_l1_l2_simulation.py` (`ScenarioConfig`, `generate_alerts`), `src/hls/rq1_l1_l2.py` (`simulate_l1_l2`, métricas terminales) y `src/hls/rq1_allocation.py` (`simulate`, `AllocationSession`, despacho D1/P1–P5). El roster paramétrico procede de `studies/soc_human_ai_organization/soc_parametric_baseline.py` (`build_roster`). La receta completa está en `config/a1_calibration.json`; el runner es `calibrate_a1_scenarios.py`.

Los únicos anclajes a SOCTRA son agregados de volumen y mezcla de proyectos registrados previamente en la documentación canónica. La conversión de 216,3 alertas/día en 9/h presupone distribuirlas uniformemente sobre 24 horas; no es una tasa horaria observada ni una calibración del trabajo humano. Las etiquetas y marcas de SOCTRA no parametrizan las decisiones de esta ejecución.

## 2. Modelo implementado y supuestos

| Componente | Implementación en A1 | Evidencia/estatus |
|---|---|---|
| Llegadas | Proceso Poisson homogéneo por tramos, con modo opcional de ráfaga/cambio. `generate_alerts` muestrea interllegadas exponenciales y clase, prioridad, dificultad y referencia de escalado. | Configurable y sintético. El volumen medio de registros SOCTRA sólo orienta una escala. No reproduce el perfil temporal SOCTRA. |
| Clases y prioridades | Tres estratos anónimos (`portfolio_top5`, `portfolio_next5`, `portfolio_tail`), proporciones 0,592/0,236/0,172; prioridades low/medium/high con proporciones 0,50/0,35/0,15 independientes de clase. | Mezcla de estratos derivada de registros; mezcla de prioridad independiente es supuesta. |
| Deadlines | Deadline absoluto = llegada + 12/4/1 h para low/medium/high, multiplicado por 2, 1, 0,5, 0,25 o 0,1 en las celdas correspondientes. | Hipotéticos; no son SLA contractuales GMV. |
| Dificultad y calidad | Dificultad Beta(2,2). Calidad esperada por tarea completada modelada como competencia × (1 − 0,35 × dificultad). | Sintética. No equivale a calidad humana observada ni a exactitud validada. |
| Escalado/IA | Necesidad latente por proyecto 0,03/0,05/0,08. Recomendación con sensibilidad 0,90 y FPR 0,01; se usa aceptación hipotética de recomendación para el escenario base. | Todos son supuestos. La etiqueta de necesidad y la recomendación se comparten entre políticas dentro de cada semilla. |
| Equipo | 6 L1 y 3 L2. L1 elegible según roster solapado medio 2,5 clases; L2 para las tres. Competencia por analista/clase y factor de velocidad fijos; factor de velocidad no depende de competencia. | Hipotético; no hay plantilla, disponibilidad ni capacidades GMV medidas. |
| Servicio | Media base L1 0,20/0,25/0,30 h y L2 0,75/0,90/1,00 h por clase; se multiplica por factor de velocidad fijo entre 0,90 y 1,10. Servicio secuencial, no preemptivo. | Hipotético; no se estimó a partir de timestamps SOCTRA. |
| Colas/eventos | Cola pendiente por pool; despacho inmediato al llegar una alerta o liberarse analista. En empate temporal se procesan llegadas, finalizaciones/liberaciones y un despacho. Escalado: L1 y, si hay recomendación aceptada, cola L2. | Código ejecutable; no representa turnos, L3, transferencias operativas completas ni conducta observada. |
| Coordinación | P4 incurre latencia por época de matching con asignaciones, no por cada analista; P5 sólo al activar matching. Recurso abstracto = coste configurado por arista elegible. | Latencia/coste son análisis de sensibilidad hipotéticos. Una unidad de coste no tiene conversión operativa. |

El horizonte de admisión fue H=24 h. El drenaje candidato fue D=24 h; se probó D=8/16/24/36 en una celda separada. Sólo se admiten llegadas con `arrival < H`; las métricas a H se capturan antes de despachar tareas pendientes en H. La métrica terminal toma la finalización L2 para alertas enrutadas a L2.

## 3. Capacidad efectiva

Se calculó capacidad fluida por nivel mediante LP: maximizar una tasa común de entradas por hora, manteniendo la mezcla de clases y la elegibilidad, con restricción para cada analista \(\sum_k \lambda_{ik}s_{ik}\leq 1\) hora ocupada/hora disponible. Es un límite de capacidad ideal, sin variabilidad de colas, deadlines, absentismo, cambios de turno ni coste de coordinación.

| Pool/condición | Capacidad calculada | Interpretación |
|---|---:|---|
| L1, roster base, mezcla observada de estratos | 28,42 entradas/h | Cuello de botella base; los seis analistas alcanzan utilización fluida 1 en la solución LP. |
| L2, mezcla de recomendaciones hipotéticas base | 3,835 entradas L2/h | Con recomendación IA base (4,855% de entradas), equivale a ~78,98 alertas entrantes/h. L2 no limita el caso base. |
| L1, elegibilidad media 1,5 | 27,66 entradas/h | La mayor restricción de elegibilidad reduce poco la capacidad agregada con esta mezcla. |
| L1, elegibilidad 1,0 (dos analistas por clase) | 17,06 entradas/h | Pérdida importante por partición de recursos/mix, aproximadamente −40% frente al roster base. |

Capacidad L1 si toda la demanda fuera una sola clase: top5 25,92/h; next5 20,10/h; tail 16,98/h. Esos límites por clase no deben confundirse con el caso de mezcla fijada. A la tasa de estrés L2 (necesidad ×4, recortada a 0,12/0,20/0,32), la recomendación resultante es 16,42%; a 0,65×capacidad L1 corresponde a unas 3,03 recomendaciones L2/h, cerca de 79% de la capacidad fluida L2. La campaña real puede cambiar este balance si cambia la tasa de escalado o el error de la IA.

La carga se expresa como \(\rho_{L1}=\lambda/C_{L1}\), complementada por horas de servicio ofrecidas por nivel, tasa recomendada a L2/capacidad L2, carga por clase y saturación por elegibilidad. Con servicio promedio entre elegibles, las tasas de 0,35/0,65/0,85/1,00/1,25 C consumen respectivamente 2,24/4,15/5,43/6,39/7,99 horas L1 por hora; demanda L2 base 0,42/0,77/1,01/1,19/1,48 horas de analista L2 por hora. El promedio no captura ráfagas, deadlines ni bloqueo de clases.

## 4. Calibración observada en el piloto

El runner ejecutó 1.704 filas de política (20 semillas para las celdas centrales; 8 para mecanismos), más 64 ejecuciones de drenaje, para 1.768 ejecuciones episodio-política en total; generó 170.263 filas de diagnóstico de despacho. El wall time total fue 216,6 s (3,61 min) en el entorno de esta ejecución; no extrapolar a otro hardware. Las tablas completas y reproducibles están en `results/soc_a1_calibration/` (directorio local, ignorado por Git): `episode_metrics.csv`, `policy_means.csv`, `paired_differences_vs_d1.csv`, `dispatch_opportunities.csv`, `drain_sensitivity.csv`, `run_config.json`, `runtime.json`. El CSV de diagnósticos ocupa ~21,1 MB; los demás artefactos son tabulares ligeros.

### 4.1 Carga y SLA terminal — D1

| \(\rho_{L1}\) | Llegadas/h | SLA a H | SLA H+D | Espera acumulada media/alerta a H+D | Utilización L1/L2 a H | Pendientes a H |
|---:|---:|---:|---:|---:|---:|---:|
| 0,35 | 9,95 | 0,987 | 0,997 | 0,002 h | 0,364 / 0,126 | 2,4 |
| 0,65 | 18,47 | 0,982 | 0,996 | 0,027 h | 0,676 / 0,219 | 6,1 |
| 0,85 | 24,16 | 0,981 | 0,996 | 0,136 h | 0,876 / 0,289 | 8,8 |
| 1,00 | 28,42 | 0,914 | 0,995 | 0,990 h | 0,972 / 0,331 | 55,8 |
| 1,25 | 35,52 | 0,615 | 0,795 | 4,058 h | 0,992 / 0,347 | 218,6 |

Las medias son exploratorias, no inferencias sobre GMV. Cerca de 0,35–0,85 C hay efecto techo de SLA terminal y poca diferenciación organizativa. En 1,0 C crecen mucho la cola y la espera aunque el drenaje recupera la mayoría de SLA. A 1,25 C el pool L1 está saturado y el drenaje de 24 h elimina el backlog, pero no recupera deadlines ya perdidos: SLA terminal 0,795. L2 permanece infrautilizado en base; sólo el estrés de escalado lo aproxima a su capacidad.

La variación de conteos generados en las 20 trazas de 24 h fue coherente con Poisson: media/desviación estándar de alertas 234,8/16,3 a 0,35 C; 673,9/26,1 a 1 C; 842,9/32,6 a 1,25 C. El CV medio de interllegadas por traza fue 1,009, 1,017 y 1,013, respectivamente. En la ráfaga controlada fue 1,112 y se conservó el volumen esperado; sus conteos por semilla variaron aleatoriamente. La mezcla agregada observada en estas réplicas se aproximó a las probabilidades configuradas, pero clase y severidad se muestrean independientemente; estas propiedades describen el generador, no SOCTRA.

El barrido de deadlines a 0,85 C dio para D1 SLA H/H+D de 0,977/0,992 con 0,5×, 0,894/0,908 con 0,25× y 0,737/0,749 con 0,1×. Al combinar 1,5 C y 0,1× (celda de límite, 8 semillas), SLA H y H+D fue 0,022; a pesar de D=24 h, el 97,8% de alertas no alcanzó el plazo. Esta es una condición de estrés construida, no un régimen observado. Por ello, la matriz recomendada separa sobrecarga y plazos estrictos y conserva una única celda combinada de límite.

### 4.2 Diferenciación de políticas: exploratoria

Con 20 semillas, a 1,25 C y deadline base, P1 alcanzó SLA H/H+D 0,743/0,989 y P4 0,751/0,994, frente a D1 0,615/0,795; a 0,85 C y plazo 0,1×, P4 dio 0,809/0,819 y P5 0,808/0,817 frente a D1 0,737/0,749. En 0,35–0,85 C y deadlines base las diferencias terminales son pequeñas por efecto techo. Los IC pareados piloto muestran, por ejemplo, en 1,25 C diferencia H+D P4−D1 = +0,1995 [0,1616; 0,2373] y P1−D1 = +0,1941 [0,1589; 0,2294]; con deadline 0,1×, P4−D1 = +0,0708 [0,0480; 0,0937]. Son estimaciones de calibración, no pruebas confirmatorias ni selección de ganadores; no se aplicó ajuste por multiplicidad.

La diferencia grande del estrés combinado (P4/P5 SLA H+D ~0,646/0,647 frente a D1 0,022; 8 semillas, diferencias pareadas P4−D1 +0,6239 [0,6100; 0,6378] y P5−D1 +0,6247 [0,6108; 0,6387]) **no es evidencia de beneficio por matching colectivo**: el diagnóstico no encontró una sola decisión con matching factible de dos o más tareas. En esos estados P4 puede alterar la selección de alerta para un analista libre al optimizar su objetivo de plazo, aunque no haya asignación conjunta. Los intervalos son descriptivos/exploratorios y no corregidos por multiplicidad. La interpretación causal correcta requiere separar orden/prioridad de matching en la campaña; A1 no atribuye esta ganancia a coordinación.

### 4.3 Drenaje y coste de coordinación

En la celda 1,25 C, plazo 0,5×, D=8 h dejó media de 20,9 alertas pendientes con D1 y 12,9 con P4; D=16 h y superiores dejaron cero pendientes en las semillas probadas. Se propone D=24 h como margen operativo para la matriz, sin afirmar suficiencia para todo sistema posible; publicar siempre backlog residual y SLA tanto a H como a H+D.

En el piloto de latencia a 0,85 C/0,5× (8 semillas), P4 tuvo SLA H 0,974 con latencia 0, frente a 0,878 con 0,05 h y 0,642 con 0,15 h; la suma de latencias por época promedió 30,4 h y 91,2 h por episodio, respectivamente. Esos valores equivalen a 3 y 9 minutos por despacho, frente a ~0,225 h de servicio L1 medio ponderado del roster. P4 incurre latencia en cada época coordinada incluso si hay un único analista libre; la caída no mide sólo la penalización de matching multianalista. P5 activó mucho menos: sumas 0,85 h y 2,10 h/episodio y SLA H 0,970/0,969. El parámetro de coste por arista en 0/1 sólo altera unidades abstractas acumuladas, no asignaciones ni SLA. El alto coste acumulado de P4 a coste=1 refleja el conteo de aristas, no una medición de recursos humanos o computacionales. La omisión previa del parámetro `coordination_edge_cost` en la envoltura L1/L2 impedía probarlo extremo a extremo; A1 lo propaga a ambos pools con valor por defecto 0 y añade una prueba específica.

## 5. Oportunidades de decisión y especialización

En 161.701 estados de despacho (L1 y L2, múltiples celdas), el máximo cardinal de matching factible fue 1 en todos: **cero oportunidades observadas de asignar simultáneamente dos o más alertas a analistas distintos**. Es un resultado de esa muestra, no prueba de imposibilidad del motor. El motor agrupa eventos con el mismo timestamp; la hipótesis de grafo estrella requiere que cada época actualice un solo lado y un solo vértice. Una llegada empatada con varias finalizaciones, varias finalizaciones simultáneas o un lote de alertas puede romper esa condición. La auditoría y sus tests están en [Rediseño del Paso 5](SOC_STEP5_REDESIGN.md).

En L1, con 0,35 C había al menos dos analistas libres en 93,1% de estados y al menos una alerta con varios analistas elegibles en 85,8%, pero varias tareas simultáneamente pendientes sólo en 1,8%. A 0,85 C los valores fueron 26,2%, 15,8% y 63,3%; a 1,25 C, 7,9%, 0,7% y 98,6%. A mayor carga, se acumula cola, pero casi todos los analistas están ocupados y las tareas pendientes tienden a depender de una única especialidad elegible. El indicador de alertas con varios elegibles no equivale a matching múltiple posible.

P3/P4 difirieron en pareja analista-alerta en 51,1% de los estados de L1 a 1,25 C, pero sólo en 0,2% de estados con dos o más analistas libres; en la mayoría de diferencias el estado tenía un único analista libre, por lo que se trata de una prioridad de alerta, no de complementariedad simultánea. En elegibilidad restringida 1,5 y 0,85 C/0,5×, 49,6% de estados tenían dos o más libres, pero sólo 6,0% tenía alguna alerta con múltiples elegibles y ningún estado ofreció matching de cardinalidad ≥2. La elección P3 señalaba una posibilidad diagnóstica de bloquear otro tipo de alerta elegible en 32,2% de estados a 0,85 C y 82,6% a 1,25 C; no es pérdida realizada ni prueba causal.

La heterogeneidad de competencia sí existe en el roster, pero tener perfiles diferentes no basta: debe haber una clase pendiente y varios analistas elegibles/disponibles al mismo tiempo para que P2/P3/P4 puedan distinguir una asignación. Con la demanda por clase y despacho inmediato de esta calibración, el solapamiento utilizable fue escaso durante congestión. Para P4/P5 esto condiciona fuertemente la interpretación; para P3 la escasez de elegibilidad y ocupación de especialistas parece más frecuente, pero el diagnóstico de bloqueo es potencial.

## 6. Matriz experimental compacta propuesta

No se recomienda el producto cartesiano. Se propone una matriz anidada de **17 celdas**, siempre con las seis políticas y trazas emparejadas por semilla. Todos los tiempos son horas; carga \(\rho\) se calcula respecto a 28,42 llegadas/h del roster/mix base.

| Grupo/celdas | Parámetros | Mecanismo/políticas relevantes | Hipótesis que permite contrastar | Riesgo de interpretación |
|---|---|---|---|---|
| Referencia de carga (5) | \(\rho=0,35;0,65;0,85;1,00;1,25\), deadline base 12/4/1 h, elegibilidad 2,5, heterogeneidad base | D1 vs P1; todas como respuesta bajo crecimiento de carga | Efecto techo bajo carga holgada y cambios cerca/por encima de capacidad | Tasas absolutas/capacidad son hipotéticas; 1,25 es estrés. |
| Presión temporal (3 adicionales) | En 0,85 C, deadline ×0,5/0,25/0,1 (×1 ya incluido en referencia) | P1/P4/P5, también D1 | Separar congestión de plazos no factibles | ×0,1 puede ser extremo; no es SLA real. |
| Competencia/velocidad (2) | En 0,85 C/×0,5: competencia homogénea; velocidad homogénea, una dimensión cada vez | P2/P3/P4/P5 | Aislar adecuación de competencia y velocidad | Competencia es proxy sintético y la calidad modelada es esperada. |
| Elegibilidad (2 adicionales) | En 0,85 C/×0,5, elegibilidad 3,0 y 1,5; referencia 2,5 | P3/P4/P5 | Solapamiento frente a escasez de especialistas | La elegibilidad 1,5 es diseño abstracto, no roster medido. |
| Cuello L2 (1) | 0,65 C/×0,5, probabilidad de necesidad ×4 (recortada a 1) | Todas; inspeccionar SLA L2 | L2 puede ser limitante aun con holgura L1 | Intensificación deliberada de hipótesis de escalado. |
| Ráfaga (1) | 0,65 C/×0,5, ventana 8–10 h a ×3, conservando número esperado total | P1/P3/P4/P5 | Transitorio de cola sin subir volumen esperado | Llegadas por tramos siguen siendo Poisson; no se afirma patrón SOCTRA. |
| Coste coordinación (2 adicionales) | En 0,85 C/×0,5: latencia 0,05 y 0,15 h; mantener caso 0 de referencia. Coste por arista 0 vs 1 en una comparación pareada separada | P4/P5 | Sensibilidad al retraso y al consumo abstracto de recursos | 1 unidad/arista no es coste operacional; cambios de latencia pueden volver irrelevante la coordinación. |
| Límite (1) | 1,5 C y deadline ×0,1 | Todas; diagnosticar pérdida del SLA y prioridad de alertas | Límite de capacidad/plazo | Estrés combinado; no usar para representar operación típica. |

Los valores son una propuesta de diseño, no ajustes confirmados ni objetivos para favorecer políticas. Mantener separados los contrastes que aíslan mecanismos y publicar resultados negativos.

## 7. Dimensionamiento estadístico y computacional

El piloto central estima diferencias emparejadas para 20 semillas; la desviación típica máxima observada entre contrastes de SLA terminal frente a D1 fue 0,081 (en 1,25 C, P4−D1). Con t pareado, una planificación aproximada da:

| Semillas emparejadas | Semiancho IC95% si SD=0,081 | MDE aproximado, 80% potencia, bilateral, sin multiplicidad |
|---:|---:|---:|
| 40 | 0,026 | 0,036 |
| 60 | 0,021 | 0,029 |
| 80 | 0,018 | 0,025 |

**Recomendación inicial: 60 semillas emparejadas por celda confirmatoria**; considerar 80 si el objetivo editorial exige precisión cercana a ±0,02 o detectar cambios de ~2,5 puntos. Los cálculos usan desviación de un piloto pequeño y no garantizan potencia bajo otras semillas/escenarios. Congelar análisis y contrastes primarios antes de la campaña. Usar diferencias pareadas e IC95%; para cinco comparaciones frente a D1 en cada familia preespecificada, controlar error familiar con Holm. Declarar análisis secundarios/exploratorios y evitar seleccionar política o escenario post hoc.

Para 17 celdas × 6 políticas × 60 semillas: 6.120 ejecuciones. El runner A1 tardó 216 s para 1.768 ejecuciones más registro diagnóstico; la parte medida dentro de episodios sumó 67 s, pero hay celdas sobrecargadas de coste mucho mayor (hasta ~1 s/episodio). Extrapolación conservadora del wall time completo: alrededor de 13 min para el mismo host, con rango de planificación 10–20 min y resultados tabulares de pocos MB. Si se guarda instrumentación de todos los estados, el volumen crece a varios cientos de miles de filas y decenas de MB. El diagnóstico de estados puede restringirse a semillas mecanísticas predefinidas, conservando métricas de episodio para las 60. Antes de la campaña, cronometrar una ejecución representativa de estrés.

## 8. Reproducibilidad, validación y limitaciones

- Semillas centrales: `261119000`–`261119019`; mecanismos: `261129000`–`261129007`. Semillas compartidas entre políticas generan iguales alertas/recomendaciones/verdades simuladas por celda. La matriz principal deberá usar semillas nuevas.
- `config/a1_calibration.json` declara parámetros, celdas, semillas y salida; `runtime.json` conserva el tiempo. CSV agregados/diagnósticos están en `results/soc_a1_calibration/`, excluidos por `.gitignore` (`/results/`). No hay IDs SOCTRA ni datos privados.
- Pruebas funcionales/regresión ejecutadas: `pytest -q tests/test_rq1_allocation.py tests/test_rq1_l1_l2.py tests/test_ia_l1_l2_simulation.py tests/test_soc_organization_policies.py tests/test_soc_parametric_baseline.py tests/test_soctra_demand_experiment.py` — **92 passed**. Se verificó además que la salida de calibración está ignorada por Git.
- Corrección instrumental de A1: `simulate_l1_l2` no reenviaba `coordination_edge_cost` a sus simulaciones L1/L2. Ahora lo valida y lo propaga; con valor por defecto 0 no cambia resultados históricos. `tests/test_rq1_l1_l2.py` verifica el paso del parámetro en ambos pools.
- No se modificaron las reglas D1/P1–P5 ni la dinámica del motor; se añadieron runner/configuración y análisis. La métrica primaria es fracción de todas las alertas admitidas completadas terminalmente dentro del deadline simulado, con denominador fijo en admitidas. Se reportan H y H+D; completadas tarde, pendientes, esperas y backlog se conservan por separado.
- El campo `modeled_sla_conditioned_quality_per_admitted` suma competencias de alertas completadas a tiempo y divide por admitidas; no es exactitud ni calidad real. La expectativa de corrección usa competencia × (1−0,35·dificultad) y también es hipotética.
- La política P5 sólo activa matching si el objetivo lexicográfico previsto (a tiempo, cardinalidad) mejora; no internaliza el coste abstracto al decidir. En el piloto la separación coste=0/1 altera recursos contabilizados, no decisiones.
- La utilización se calcula como fracción del tiempo en servicio; la latencia de despacho coordinado aparece como indisponibilidad y tiempo-persona de coordinación, pero no como servicio ocupado en el numerador de utilización.
- Sin competencias observadas, tiempos de atención/servicio, turnos, disponibilidad, SLA contractuales ni verdad adjudicada, el modelo está calibrado internamente pero no validado cuantitativamente para GMV-CERT. El Poisson sintético no preserva la sobredispersión/autocorrelación observadas históricamente.
- El gran aumento de SLA de P4 en estrés no prueba beneficio de matching: no se observó matching factible multiasignación; puede deberse a su elección temporal de alertas con un único analista libre. Debe describirse como respuesta del mecanismo completo, no atribuirse causalmente a coordinación.

## 9. Dictamen A1

Los rangos de carga y deadline producen desde efecto techo hasta saturación de L1 y fallo masivo de SLA; el drenaje H+D separa retraso de congestión terminal y la prueba adicional identifica un límite de inviabilidad. La sensibilidad muestra que el pool cuello de botella cambia si se fuerza más escalado. La heterogeneidad implementada no se traduce automáticamente en matching: la concurrencia y la elegibilidad simultánea escasean, incluso cuando hay cola.

**Preparación para campaña principal: condicional.** El dimensionamiento permite fijar una matriz reproducible de episodios sintéticos y confirmar D1 frente a políticas locales temporales/de competencia. La inferencia sobre P4/P5 como coordinación conjunta es débil en el proceso de despacho inmediato probado: no hubo matching de dos o más tareas, y algunas diferencias de P4 suceden con un solo analista libre. Esto debe quedar como limitación explícita en la campaña; no se han alterado reglas ni se ha “corregido” el modelo para crear oportunidades. La aprobación científica de la matriz y de las hipótesis sigue pendiente.
