# Paso 5, Fase A2 — Taxonomía y diseño de políticas

**Estado histórico:** propuesta inicial T/Q/S/M para revisión; A2.2 comparó carteras y recomendó T/Q/C/M. Posteriormente el PI aprobó D1/T/Q/C/M de forma provisional para evaluación, no congelada. C aún no estaba implementada en A3.1; se incorporó como prototipo secuencial en [A3.2](SOC_A3_2_PILOT_COMPARISON.md). Véase el [estado actual](SOC_CURRENT_STATE.md).
**Alcance:** formular mecanismos organizativos distinguibles para comparar con D1. No modifica políticas, motor ni resultados.
**Trazabilidad:** complementa [Rediseño del Paso 5](SOC_STEP5_REDESIGN.md), [Revisión previa de políticas](SOC_POLICY_DESIGN_REVIEW.md) y [dimensionamiento A1](SOC_A1_EXPERIMENTAL_DIMENSIONING.md). Las evaluaciones de expertos externos se conocen únicamente mediante el resumen del PI recogido en el primero de esos documentos; sus originales no se localizaron.

La recomendación inicial de T/Q/S/M de este documento se conserva como antecedente. La revisión posterior [A2.2: selección crítica de cartera](SOC_A2_POLICY_PORTFOLIO_DECISION.md) añade coordinación central secuencial C como control necesario para separar información global de matching, y difiere reserva intertemporal R.

## 1. Pregunta y alcance

Pregunta: **¿en qué condiciones diferentes políticas de organización de analistas heterogéneos mejoran o perjudican el rendimiento colectivo de un SOC frente a D1, y mediante qué mecanismo?** No se presupone una ventaja de coordinación. D1 permanece congelado. La aplicación SOC es una abstracción experimental y no una reproducción cuantitativamente validada de GMV-CERT.

La decisión se formula sobre el estado observable en un instante `t`: alertas pendientes `Q_t`, analistas libres `F_t`, elegibilidad `E_ia`, deadlines `d_a`, tiempos estimados `s_ia` y competencias modeladas `e_ia`. La elegibilidad determina factibilidad; competencia y duración son parámetros hipotéticos y no deben presentarse como medidas humanas observadas. Ninguna regla propuesta observa futuras llegadas ni resultados realizados.

## 2. Taxonomía de decisiones

Las dimensiones siguientes son ortogonales en la formulación, aunque las políticas concretas combinen varias:

| Dimensión | Alternativas | Pregunta que permite estudiar |
|---|---|---|
| Información | Solo estado propio/local; estado compartido; vista global de colas, roster y matriz de elegibilidad/servicio | ¿El cambio procede de información adicional? |
| Criterio de prioridad | Deadline bruto; holgura tras servicio; calidad/competencia; escasez de elegibilidad | ¿Qué resultado se favorece al elegir una tarea? |
| Unidad de decisión | Elección individual secuencial; selección central secuencial; asignación conjunta | ¿Hay valor incremental del matching frente a decidir una pareja cada vez? |
| Horizonte | Estado actual; reserva o decisión intertemporal | ¿Se usa solo trabajo presente o se sacrifica capacidad ahora por trabajo futuro? |
| Temporización | Despacho inmediato; espera deliberada/micro-lote | ¿Se compra una oportunidad potencial mediante demora? |
| Activación | Coordinación permanente; coordinación selectiva | ¿El beneficio previsto supera latencia y consumo de recursos? |
| Recursos | Elegibilidad fija; conservación/reserva de especialista; reasignación | ¿Se protege capacidad escasa o se redistribuye trabajo? |
| Costes | Latencia, tiempo-persona, coste computacional/recursos, espera inducida | ¿Qué operación se está midiendo y con qué unidad? |

El núcleo de la pregunta requiere separar prioridad temporal, adecuación de competencia y asignación conjunta/global. La preservación de especialistas es pertinente si existe elegibilidad solapada y escasez por clase. Reserva futura y despacho diferido son extensiones intertemporales distintas, con coste de espera; no forman parte del núcleo sin justificación operativa. No se afirma que esta taxonomía sea universalmente exhaustiva.

## 3. Auditoría de D1 y P1–P5

Las funciones correspondientes están en `src/hls/rq1_allocation.py`: `_dispatch_d1`, `_dispatch_soc_policy`, `_dispatch_local_priority`, `_dispatch_local_competence`, `_dispatch_local_capacity` y `_dispatch_coordinated`. La simulación activa decisiones con información del estado actual y no consulta futuras llegadas.

| Regla actual | Qué hace y qué información usa | Valor y limitación conceptual | Recomendación A2 |
|---|---|---|---|
| **D1** | Orden reproducible aleatorio de analistas libres; selección local secuencial. Prioriza riesgo temporal truncado `r_ia(t) = clip((s_ia - (d_a - t))/s_ia, 0, 1)`, luego competencia propia, número de pares libres elegibles y desempates por deadline/llegada/ID. | Referencia descentralizada simplificada; usa datos de estado del simulador y conteo de pares, pero no matching, competencias/velocidades específicas de compañeros, reserva ni planificación futura. No está validada como procedimiento real GMV. | Congelar sin cambios y usar como referencia primaria. |
| **P1** | Analistas por ID; cada uno elige alerta elegible de menor holgura post-servicio `h_ia = d_a - t - s_ia`, con desempates deterministas. | Control temporal local. No es EDF por deadline bruto: incorpora duración propia. El orden ID puede afectar asignaciones concurrentes. | Conservar como contraste temporal; etiquetar por holgura, no por EDF estricto. |
| **P2** | Analistas por ID; maximiza competencia propia `e_ia` y después usa holgura/deadline/llegada/ID. | Aísla preferencia local por adecuación, pero la competencia solo representa calidad si se valida el mapeo; puede sacrificar SLA. No optimiza matching de competencias. | Conservar como contraste local de competencia, con SLA y calidad separadas. |
| **P3** | Selección secuencial local; minimiza el número de otros analistas libres aún elegibles para la clase; después maximiza competencia propia y aplica desempates temporales. | Proxy de escasez basado en elegibilidad; no es reserva intertemporal ni compara adecuación/velocidad exacta de compañeros. Requiere información de roster común. Puede preservar flexibilidad o consumir innecesariamente un recurso generalista. | Reformular para A3 solo si el PI aprueba la hipótesis de coste de oportunidad; mantener su resultado actual como histórico, no llamarlo reserva. |
| **P4** | Matching uno-a-uno en el conjunto actual; lexicográficamente maximiza finalizaciones previstas a tiempo, luego cardinalidad, y usa prioridad de deadline/desempate determinista. Factibilidad incorpora duración individual y latencia. | Es asignación central global; solo es matching múltiple cuando la cardinalidad factible alcanza ≥2. Con un analista libre cambia la selección individual, no el matching. Coste/latencia actual hipotético. | Conservar como candidato de matching, pero añadir control central secuencial comparable; informar estratos por cardinalidad factible. |
| **P5** | Calcula P3 y P4; activa P4 si mejora estrictamente el par lexicográfico (número previsto a tiempo, número de asignaciones), incluyendo latencia prevista. | Selectiva respecto a ese proxy, no respecto a beneficio neto: ignora coste de recursos en la activación y no pondera calidad. Hereda mezcla de mecanismos P3/P4. | Descartar como contraste confirmatorio en su forma actual. El concepto selectivo queda pendiente de utilidad/coste defendibles. |

P1–P3 usan orden determinista por ID, mientras D1 usa orden aleatorio reproducible. Es una diferencia de procedimiento que puede afectar decisiones; los futuros controles deben emparejar o aislar orden cuando se atribuya causalidad. Las políticas históricas B0–B4, C0–C2×P0/P1 y D1-L/D1-S no son alias de P1–P5; sus resultados se preservan en [Resultados y lecciones](SOC_RESULTS_AND_LESSONS.md), pero no integran automáticamente la comparación A2/A3.

## 4. Repertorio candidato para revisión

Se recomienda someter a aprobación **D1 más cuatro contrastes**, no declararlos definitivos:

### T — Priorización temporal local (candidata basada en P1)

- **Regla:** para cada analista libre, en orden fijado por protocolo, elegir alerta elegible que minimiza holgura `h_ia = d_a - t - s_ia`; desempate por deadline, llegada e ID. No descartar tareas vencidas; se procesan cuando no haya alternativa mejor según la regla.
- **Información/recursos:** estado local del analista, cola visible, su duración por alerta y deadline; no cambia equipo ni elegibilidad.
- **Objetivo/coste:** reducir incumplimientos evitables mediante holgura, sin latencia coordinativa adicional. No combina magnitudes.
- **Hipótesis:** puede cambiar SLA terminal cuando hay competencia por capacidad y distintas holguras; efecto pequeño con holgura general o si la regla D1 ya ordena igual.
- **Diferencia:** temporal explícita frente al riesgo truncado y desempate de D1; sigue siendo individual.

### Q — Adecuación local por competencia (candidata basada en P2)

- **Regla:** cada analista libre elige la alerta elegible de máximo `e_ia`; desempata por mayor holgura `h_ia`, luego deadline/llegada/ID. La competencia es prioritaria para aislar el mecanismo; la posible pérdida temporal se reporta por separado. Esta prioridad lexicográfica debe congelarse antes de A3.
- **Información/recursos:** competencia propia modelada, servicio propio estimado, deadline y cola; sin competencia de pares ni matching.
- **Objetivo/coste:** aumentar adecuación/calidad modelada. La competencia no modifica `s_ia`; no hay coste de coordinación.
- **Hipótesis:** la calidad modelada aumenta solo si existen alternativas elegibles con distinta competencia; puede aumentar tardanzas o espera.
- **Diferencia:** prioridad individual por competencia, no asignación global. La interpretación depende de que `e_ia` guarde relación explícita con el outcome sintético, no con calidad real GMV.

### S — Preservación de elegibilidad/especialistas (reformulación que debe aprobarse)

- **Regla provisional:** selección local secuencial. Para una pareja factible `(i,a)`, definir `n_k,-i(t)` como el número de analistas `j` libres, distintos de `i`, elegibles para clase `k`, donde `k` es la clase de la alerta. Primero minimizar `n_k,-i(t)` (atender clases con menos alternativas libres); entre empates aplicar prioridad temporal T y desempates estables. No retener a un analista ni esperar llegadas.
- **Información/recursos:** elegibilidad de colegas libres y cola actual; no requiere competencia exacta de pares ni futuro. Cambia únicamente la asignación presente.
- **Objetivo/coste:** preservar opciones de cobertura en el estado actual; sin coste de coordinación modelado. El tiempo de oportunidad por ocupar a un generalista es consecuencia que se mide, no una unidad añadida al score.
- **Hipótesis:** puede reducir bloqueo por clase si coexisten tareas de varias clases y elegibilidad solapada; puede empeorar holgura de alertas urgentes o no ayudar si la clase preservada no recibe demanda.
- **Diferencia:** prioriza escasez de elegibilidad, no competencia ni cardinalidad de matching. No es reserva futura. El criterio exacto y si merece ser política principal requieren aprobación, pues la P3 actual combina escasez y competencia.

### M — Matching temporal del estado actual (candidata basada en P4)

- **Regla:** en cada época formar grafo bipartito `G_t=(F_t,Q_t,E_t)`, con arista `(i,a)` cuando `i` es elegible para `a`. Buscar matching binario `x_ia` que maximice lexicográficamente: (1) número de tareas previstas a tiempo; (2) cardinalidad total; (3) deadlines más próximos; (4) orden estable por IDs. Factibilidad de plazo para cada pareja: `t + latencia + s_ia <= d_a`. Restricciones: cada analista y alerta aparece como máximo una vez; solo estado actual; no anticipación.
- **Información/recursos:** cola, roster libre, elegibilidad y tiempos de cada pareja. La competencia no entra en M, para no confundir matching con calidad.
- **Objetivo/coste:** aprovechar complementariedad concurrente para SLA y asignaciones factibles. Latencia `ell` y coste de recursos se aplican una vez por época de coordinación, con unidades declaradas; sin evidencia, usar latencia cero solo como límite diagnóstico y sensibilidad, no como operación real.
- **Sin oportunidad:** si el matching máximo es 1, M es una selección central de una pareja; si coincide el control secuencial central, no hay efecto atribuible a matching. Si solo existe una pareja factible, M coincide necesariamente en asignación.
- **Hipótesis:** beneficio incremental de matching solo puede atribuirse en estados donde haya varias asignaciones factibles y complementariedad, especialmente cuando el matching máximo `nu(G_t) >= 2`; más concurrencia no garantiza beneficio terminal.
- **Diferencia:** resuelve conjuntamente el snapshot, frente a selección individual/central secuencial. Control central emparejado obligatorio para identificar este mecanismo.

**Selectiva:** no se propone aún una quinta política principal. La coordinación selectiva necesitaría comparar valor previsto y coste en una unidad común: por ejemplo, una utilidad terminal preespecificada con componentes y pesos científicamente defendibles. P5 no lo hace. Hasta que el PI apruebe estimando y conversión de costes, selección selectiva debe evaluarse como ablación/control exploratorio, no como algoritmo confirmado.

### Complementariedad

| Contraste | Mecanismo aislado | Qué se mantiene comparable | Control necesario |
|---|---|---|---|
| T vs D1 | Prioridad de holgura temporal | Elegibilidad, servicio, recursos, traza | Emparejar orden de analistas/desempatar o registrar efecto del orden. |
| Q vs T/D1 | Competencia propia local | Mismo estado y tiempo de servicio; competencia no altera duración | Reportar SLA y calidad por separado; control competencia homogénea. |
| S vs T | Escasez de elegibilidad | Mismo roster y cola | Ablación homogénea/solapada/restringida; contar bloqueos potenciales, no inferir demanda futura. |
| M vs control central secuencial | Matching conjunto incremental | Mismo criterio temporal, grafo, información, desempate y coste por decisión | Estratificar por `nu(G)`, n.º libres y asignaciones; control de una tarea/una opción. |
| M coste 0 vs coste >0 | Coste temporal/recursos | Misma asignación/traza antes de contabilizar coste | Separar latencia de recursos; coste nulo es límite ideal, no conclusión operativa. |

Las estrategias son mecanismos alternativos para atribución primaria; combinaciones T+Q o T+S pueden ser análisis factoriales posteriores, pero no deben llamarse mecanismos independientes ni agregarse sin una pregunta y regla preespecificadas.

## 5. Hipótesis contrastables

- **H-T:** la prioridad de holgura cambia decisiones y puede elevar cumplimiento terminal cuando hay conflicto y deadlines diferenciados; no necesariamente mejora calidad.
- **H-Q:** priorizar competencia propia eleva la calidad modelada cuando la matriz de competencias difiere entre alternativas; puede reducir SLA/velocidad efectiva del sistema.
- **H-S:** la prioridad por escasez de elegibilidad reduce bloqueos de clases bajo cola multicategoría y roster solapado; su efecto depende de composición y puede desplazar urgencias.
- **H-M:** matching mejora el resultado sobre una selección central secuencial equivalente solo si `nu(G_t) >= 2` y las alternativas tienen consecuencias diferentes; coste/latencia puede revertir beneficio bruto.
- **H-regímenes:** el signo y tamaño de los efectos varían con carga efectiva por pool/clase, deadline relativo al servicio, elegibilidad y frecuencia de estados de oportunidad.

Son hipótesis del simulador. Competencia→calidad, deadlines como SLA terminal y latencias/costes no están validados operativamente para GMV.

## 6. Controles causales y medidas

Para cada época registrar snapshot anterior al despacho: `F_t,Q_t,E_ia,s_ia,e_ia,d_a-t`, propuestas por política y pareja ejecutada. Registrar `nu(G_t)`, cardinalidad máxima, número de asignaciones, si la primera acción difiere, si la diferencia afecta un segundo emparejamiento, y latencia/coste aplicados. Las medidas de oportunidad son diagnósticas: no equivalen a mejora.

Controles mínimos propuestos:

1. **Selección individual:** política local vs selector central secuencial de una pareja, con la misma clave y datos; identifica ganancia por información/prioridad sin matching.
2. **Matching:** control central secuencial anterior vs M, solo estados emparejados y estratificados por `nu(G_t)=1` o `nu(G_t)>=2`; atribuir incremento a matching solo en el estrato con alternativas conjuntas.
3. **Competencia:** Q vs regla temporal bajo matriz heterogénea y control de matriz homogénea; mantener `s_ia` constante al variar `e_ia`.
4. **Preservación:** S vs T, desglosar clases y elegibilidad; no denominar beneficio “futuro” sin trabajo futuro observado por la política.
5. **Costes/espera:** ablar latencia y consumo separadamente. Despacho diferido es un mecanismo distinto: requiere parámetro de ventana y justificar operación; no se añade por defecto.

Métricas de mecanismo: oportunidad/activación/diferencia efectiva, matching factible y ejecutado, especialistas libres/ocupados por clase, espera creada, latencia y coste. Métricas de episodio: SLA terminal con denominador fijo de admitidas, desglosado por clase/pool; completadas, tardías y pendientes; calidad modelada completada; espera/respuesta, backlog/utilización por pool; coste y latencia. No usar recompensa escalar como única prueba. Mantener H frente a H+D y término L2 para SLA de alertas escaladas.

## 7. Escenarios que A3 debe dimensionar, sin fijar aún la matriz

Los niveles se definirán por carga ofrecida respecto a capacidad **efectiva por clase y pool**, no solo alertas/h:

| Familia | Propósito | Diseño necesario | Clasificación inicial |
|---|---|---|---|
| Operativamente representativos | Cubrir rangos compatibles con agregados de demanda y descripción GMV disponible | Conservar trazas SOCTRA autorizadas o patrones derivados; roster/servicio solo si hay evidencia | Plausibilidad empírica parcial; operación no calibrada. |
| Contraste causal | Cambiar una dimensión a la vez | Homogéneo/heterogéneo `e` con `s` fijo; homogéneo/heterogéneo `s` con `e` fijo; elegibilidad solapada/restringida; misma traza | Hipotético mecanístico, no frecuencia GMV. |
| Estrés | Explorar saturación L1/L2 y deadlines inviables | Subir carga relativa o escalado, y deadlines relativos al servicio, identificando límites | Extremo sintético. |
| Sensibilidad | Probar costos, latencia, agrupación y drenaje | Barridos univariados alrededor del escenario base; costes con unidades separadas | Parámetros no validados, reportar rango. |

La A1 sigue siendo útil para capacidad fluida del roster sintético, efecto techo/transición/saturación, H/H+D y sensibilidad a latencia. Debe recalcularse o desagregarse para el repertorio aprobado: frecuencia `nu(G_t)`, matching por pool, carga por clase, oportunidades del control de selección central, competencia y velocidad separadas, especialistas preservados y efectos de coincidencias. A1 no representa una medición de capacidad GMV y los resultados CSV de estados permanecen locales/no están en un checkout limpio.

No hay evidencia para introducir batching deliberado, reserva intertemporal ni costes reales. La prueba de matching simultáneo es una prueba funcional, no justificación de prevalencia operativa. Las llegadas simultáneas deben proceder del generador/replay especificado, no fabricarse para inflar oportunidades.

## 8. Marcos teóricos y bibliografía

Marcos pertinentes para fundamentación (descripción conceptual, no afirmaciones de optimalidad):

- **Colas multicategoría/servidores heterogéneos y skill-based routing:** elegibilidad, carga por clase, pools y asignación de tareas a recursos compatibles (T, Q, S, M).
- **Scheduling con deadlines:** holgura, tardanza, factibilidad prevista y compromisos temporales (T y objetivo primario de M).
- **Matching bipartito/dynamic o online matching:** complementariedad de decisiones uno-a-uno sobre un snapshot y efecto de oportunidades simultáneas (M). No implica optimalidad de horizonte ni de cola dinámica.
- **Reserva/capacidad escasa:** coste de oportunidad de consumir recursos flexibles frente a mantener cobertura (S); una reserva verdadera requiere modelar horizonte, llegada futura/predicción y coste de ociosidad.
- **Control estocástico/MDP:** solo relevante si se formula decisión intertemporal o política adaptativa; fuera del repertorio confirmatorio propuesto.
- **Decisión descentralizada vs coordinación:** permite definir asimetría de información y coste de compartir/centralizar; debe distinguirse centralización de matching.

No se añade bibliografía ni se atribuyen teoremas. Las referencias específicas y sus hipótesis deberán verificarse bibliográficamente antes de incorporarse al artículo. Los resúmenes de expertos no son referencias científicas.

## 9. Decisiones pendientes del PI y criterio A2

1. Aprobar/rechazar el núcleo candidato T, Q, S, M; en particular si S representa una pregunta científica prioritaria o queda como sensibilidad.
2. Aprobar la selección de competencia “primaria” de Q o exigir regla temporal secundaria común.
3. Definir el control central secuencial y coste equivalente necesarios para identificar el incremento de matching M.
4. Aclarar si los costes de coordinación se evaluarán solo como sensibilidad hipotética o si hay unidades externas defendibles.
5. Decidir si el artículo mantiene fuera del alcance despacho diferido y reserva futura (recomendación actual: sí, salvo evidencia operativa).

A2 podrá cerrarse cuando el repertorio, estimandos, controles y definiciones se congelen; A3 podrá entonces dimensionar escenarios y potencia estadística. Esta propuesta no aprueba políticas ni inicia Fase B.
