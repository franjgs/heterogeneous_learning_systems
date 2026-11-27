# Estado científico actual de SOCTRA-HLS

> **OLD MODEL / MODELO VIEJO:** this document records the historical L1-first organizational model and its evidence. Its results remain valid only for that model and do not validate the NEW MODEL. See [MODEL_GENERATIONS.md](../soc_triage_hls_availability_robustness/MODEL_GENERATIONS.md). The current LaTeX manuscript belongs entirely to the OLD MODEL; NEW MODEL transfer is deferred.

## Resumen

SOCTRA-HLS es una aplicación del programa general HLS al triaje asistido por IA y la organización del trabajo humano en un SOC. El artículo para *Electronics* relacionará conceptualmente los resultados previos de triaje automático de SOCTRA con el estudio de organización de analistas, pero ambos se mantienen como marcos experimentales independientes: no se afirma que las predicciones SOCTRA se hayan integrado experimentalmente en las decisiones organizativas. D1 es la referencia descentralizada del estudio organizativo. Existe un simulador funcional, pero sus parámetros operativos son mayoritariamente hipotéticos y no lo convierten en una reproducción cuantitativamente validada de GMV-CERT.

No se ha seleccionado todavía una política organizativa definitiva ni se ha demostrado una mejora de D1 dentro del proceso integrado con triaje IA. Las mejoras observadas en simulación son condicionales a escenarios concretos y deben leerse junto con sus efectos sobre calidad, tiempos, backlog y coste.

## Hoja de ruta científica

### Paso 1 — Consolidación documental: completado

La documentación de la aplicación SOC se consolidó en seis archivos canónicos: [AGENTS.md](AGENTS.md), [README.md](README.md), [SOC_FOUNDATIONS_AND_MODEL.md](SOC_FOUNDATIONS_AND_MODEL.md), [SOC_RESULTS_AND_LESSONS.md](SOC_RESULTS_AND_LESSONS.md), este documento y [GMV_CERT_OPERATIONAL_REFERENCE.md](GMV_CERT_OPERATIONAL_REFERENCE.md). Se eliminaron documentos redundantes después de preservar sus fundamentos, resultados, limitaciones y referencias operativas. La documentación general de HLS mantiene su autoridad y no forma parte de esta consolidación.

### Paso 2 — Verificación científica: completado

La revisión documental y de código confirmó que existe un simulador SOC funcional con gestión de alertas y colas, pools L1/L2, competencias heterogéneas, restricciones temporales, triaje IA simulado y políticas de asignación. Los detalles del modelo y sus fuentes están en [Fundamentos y modelo](SOC_FOUNDATIONS_AND_MODEL.md).

Las competencias, tiempos de servicio, disponibilidad y costes de coordinación son mayoritariamente parámetros sintéticos. SOCTRA permite caracterizar alertas y estudiar modelos de triaje, pero no valida por sí solo la organización operativa ni la capacidad del SOC. D1 permanece congelado como referencia descentralizada inspirada en la descripción cualitativa de GMV-CERT; no se ha demostrado que reproduzca sus procedimientos reales.

Las campañas existentes muestran mejoras y deterioros condicionados por escenario; no existe una estrategia organizativa universalmente superior demostrada. D1-L y D1-S están implementadas y han mejorado el SLA terminal frente a D1 en ciertas condiciones, con posibles efectos adversos en otras métricas y escenarios. No se ha demostrado que ninguna mejore a D1 en el sistema integrado con triaje IA.

La métrica corregida de SLA terminal cuenta la finalización de L2 para alertas escaladas. Los resultados anteriores a esa corrección son históricos y no deben mezclarse con métricas terminales corregidas. Parte de los resultados conserva resúmenes numéricos, pero no todos los artefactos tabulares originales; véase [Resultados y lecciones](SOC_RESULTS_AND_LESSONS.md). Los dos experimentos PPO no demostraron superioridad general frente a controles competitivos; esto limita las formulaciones ensayadas, no permite concluir que RL sea inadecuado en general.

La auditoría de este paso consistió en lectura e inspección de documentación, código y artefactos existentes. No incluyó una nueva ejecución de tests, simulaciones ni experimentos. La evidencia y sus condiciones se resumen en [Resultados y lecciones](SOC_RESULTS_AND_LESSONS.md).

### Paso 3 — Selección del problema científico: completado

El artículo de *Electronics* relacionará el trabajo previo de clasificación automática de SOCTRA —incluidas detección y falsas alarmas bajo las configuraciones publicadas— con la investigación de organización de analistas. La evaluación organizativa y el triaje SOCTRA son marcos experimentales independientes; esta línea no afirma una integración experimental de predicciones IA en las decisiones de asignación.

**Pregunta seleccionada:** ¿En qué condiciones pueden estrategias sencillas de priorización temporal, especialización y coordinación mejorar el rendimiento colectivo de un SOC respecto a D1?

El propósito es identificar mecanismos organizativos, cuantificar beneficios y compromisos, y establecer bajo qué condiciones operativas funcionan. La prioridad es justificar una mejora concreta, sencilla y reproducible respecto a D1; no se exige superioridad universal. Las posibles mejoras en métricas relevantes deberán acompañarse de la cuantificación de deterioros en otras métricas. Esta es una decisión científica, no un resultado ya obtenido.

Decisiones vigentes:

- D1 permanece congelado como baseline principal.
- La cartera provisional para evaluación es D1/T/Q/C/M. T y Q reutilizan las reglas implementadas P1 y P2; C cuenta ahora con un prototipo greedy central secuencial; M sigue fuera del piloto A3.2 y no está implementada como miembro de esta cartera. D1-L/D1-S y B0–B4/C0–C2×P0/P1 son formulaciones históricas, no aliases de T/Q/C/M.
- La cartera sigue provisional: el piloto no demuestra una mejora general ni selecciona una estrategia definitiva.
- D1-S y C0P1 pueden aparecer como referencias históricas complementarias solo si la comparabilidad con la evaluación vigente se establece explícitamente.
- La coordinación global o selectiva podrá estudiarse si resulta útil, pero no es requisito del artículo.
- No se requiere desarrollar un nuevo agente de aprendizaje por refuerzo para el alcance inmediato.
- El aprendizaje y la evolución de competencias humanas quedan fuera del alcance inmediato.
- HLS general sigue siendo un programa de investigación más amplio; el artículo se limita a la aplicación SOCTRA-HLS.
- El simulador no se presentará como reproducción cuantitativamente validada de GMV-CERT.

### Paso 4 — Fundamentación teórica y definición de la contribución: completado documental y conceptualmente

Se formuló el problema como asignación dinámica de alertas a recursos heterogéneos con elegibilidad, deadlines y capacidad limitada. Se documentaron los mecanismos de priorización temporal, competencia, capacidad/especialización y matching selectivo/conjunto; las hipótesis contrastables H1–H5; la contribución prevista; la métrica primaria y sus complementarias; y las condiciones para comparar resultados. El repertorio implementado D1/P1–P5 está definido en [Fundamentos y modelo](SOC_FOUNDATIONS_AND_MODEL.md) y comparte el motor de eventos y métricas. La validación funcional específica y de regresión ejecutó 143 tests; no fue una campaña de rendimiento. Esto cierra la fundamentación e implementación del repertorio, pero no selecciona una política ganadora ni demuestra sus efectos.

### Paso 5 — Validación experimental y artículo: en curso

#### Fase A0 — Caracterización de congestión de D1: ejecutada y revisada científicamente como exploratoria

La caracterización D1-only está en [A0: congestión del baseline](SOC_A0_BASELINE_CONGESTION.md). Se ejecutaron 420 episodios sintéticos (14 configuraciones, 30 semillas) variando carga, número de L1 y combinación de demanda alta con disponibilidad reducida. El motor no tiene límites de cola, descartes ni expiración automática; alertas vencidas permanecen en cola y las pendientes al corte se distinguen de los incumplimientos terminales. Con capacidad fluida L1 de referencia 28,42/h, la cola/espera creció desde \(\rho\approx0,85\), se hizo marcada alrededor de 1,0 y se volvió severa por encima de 1,1–1,25. L2 permaneció por debajo de 0,38 de utilización media con el enrutamiento IA hipotético base. No se compararon políticas y no se atribuyeron pérdidas a una ineficiencia de D1.

El [diagnóstico cuantitativo de debilidades D1](SOC_A0_D1_ORGANIZATIONAL_WEAKNESSES.md) añade 18 episodios acotados: pérdidas positivas de orden local sólo en la carga 1,25, sin intercambios simultáneos ni ociosidad factible observados. Son oportunidades locales, no mejoras terminales demostradas.

#### Fase A1 — Caracterización, dimensionamiento y auditoría estructural: ejecutada; decisiones pendientes del PI

La calibración exploratoria sintética está documentada en [Dimensionamiento experimental A1](SOC_A1_EXPERIMENTAL_DIMENSIONING.md), y la auditoría del modelo/políticas y el rediseño del Paso 5 en [Rediseño del Paso 5](SOC_STEP5_REDESIGN.md) y [Revisión de diseño de políticas](SOC_POLICY_DESIGN_REVIEW.md). La capacidad fluida L1 estimada es 28,42 alertas/h para el roster/mix hipotéticos; la elegibilidad estricta puede reducirla y el estrés de escalado desplaza el cuello hacia L2. Son resultados del simulador, no mediciones GMV.

En la muestra A1 no apareció matching factible de dos o más tareas. La inspección muestra que es un efecto condicionado por el despacho inmediato y los eventos, no una imposibilidad absoluta: el motor agrupa eventos simultáneos y una prueba demuestra un estado factible de cardinalidad 2. La diferencia de P4 con un solo analista libre no identifica beneficio de matching. Se ejecutaron 92 tests en A1 y 62 tests de motor/políticas tras añadir los casos estructurales; no se inició la campaña principal.

#### Fase A2 — Taxonomía y selección del repertorio: aprobado provisionalmente para evaluación; no congelado

La taxonomía inicial T/Q/S/M está en [A2: taxonomía y diseño](SOC_A2_POLICY_TAXONOMY_AND_DESIGN.md); la comparación de carteras está en [A2.2: decisión de cartera](SOC_A2_POLICY_PORTFOLIO_DECISION.md). El PI aprobó provisionalmente D1/T/Q/C/M para evaluación, sin congelar el repertorio. S queda como posible contraste secundario y R/reserva intertemporal diferida. C separa información central de matching; T/Q mantienen urgencia y competencia como contrastes distintos. A3.2 implementó un prototipo piloto de C; no es un matching conjunto ni convierte el repertorio en definitivo.

#### Fase A3.1 — Viabilidad de mecanismos: diagnóstico ejecutado

La auditoría y los estados de contraste están en [A3.1: viabilidad de mecanismos](SOC_A3_1_MECHANISM_FEASIBILITY.md). El artefacto A1 registra `nu(G)>=2` en 0/170.263 estados (L1 0/162.517; L2 0/7.746), pese a concurrencia y cola. En un subconjunto regenerado de cuatro niveles con 20 semillas por nivel hubo 0 timestamps duplicados en 42.293 llegadas: el generador Poisson continuo por tramos no produce lotes. El motor sí admite matching múltiple ante eventos simultáneos, según la prueba existente; la frecuencia cero es de A1, no imposibilidad del motor.

Los contrastes controlados muestran reglas capaces de divergir, incluidos casos donde T perjudica tardanza, Q cambia SLA/calidad modelada, selección central puede elegir un analista más rápido y M puede superar una elección greedy en un snapshot conflictivo. Son ejemplos mecánicos, no beneficios de episodio. En ese momento C aún no estaba implementada; A3.2 incorporó después un prototipo secuencial. M no tuvo oportunidad de matching múltiple en A1 y quedó como contraste condicionado/secundario potencial.

#### Fase A3.2 — Implementación de C y piloto D1/T/Q/C: ejecutados; pendiente revisión científica

El prototipo C usa criterio lexicográfico (cumplimiento previsto, holgura/tardanza, competencia, servicio y desempate estable), selecciona parejas una por una y aplica una latencia hipotética de 0,05 h por época. No optimiza un lote ni altera D1/P1/P2. T/Q son alias operativos de P1/P2. El piloto sintético tuvo siete escenarios, 20 semillas emparejadas, H=24 h, D=24 h y 700 ejecuciones episodio-política, además de 140 diagnósticos sobre trayectorias D1. No encontró matching factible ≥2 en 66.140 estados diagnósticos.

Los resultados se documentan en [A3.2](SOC_A3_2_PILOT_COMPARISON.md). T mejora SLA en H cerca de capacidad, pero no SLA terminal y reduce calidad modelada; Q mejora calidad y aciertos simulados bajo elegibilidad restringida sin mejora clara de SLA; C con latencia deteriora SLA/espera, especialmente con deadlines ajustados. El control C de coste/latencia cero obtiene mejoras terminales pequeñas en ciertas celdas, con pérdida de calidad en near capacity. Todo depende de parámetros sintéticos y los IC son exploratorios, sin corrección por multiplicidad.


#### Comparación exploratoria D1/P1–P5: ejecutada y revisada científicamente como exploratoria

La [campaña emparejada](SOC_POLICY_COMPARISON_RESULTS.md) utilizó cuatro cargas A0 y sensibilidad a plantilla, 20 semillas por celda, con y sin latencia/coste hipotéticos. A ρ=1,25 P1/P4/P5 elevaron R/N frente a D1 bajo coste cero; con latencia P4/P5 conservaron mejoras menores. P1/P4 empeoraron R/N en cargas inferiores por menor calidad modelada, y P2/P3 fueron prácticamente equivalentes. No hubo asignaciones múltiples simultáneas P4/P5 en las trazas principales, por lo que no se atribuye ganancia al matching conjunto. Resultados exploratorios sintéticos sin corrección por multiplicidad.

La [consolidación científica](SOC_SCIENTIFIC_CONSOLIDATION.md) contrasta código, configuraciones y CSV de A0, A3.2 y la campaña D1/P1–P5. Mantiene separadas sus semillas, políticas y métricas: en la campaña actual R/N es calidad **esperada** y puntualidad terminal por admitida; A3.2 también informó corrección realizada mediante Bernoulli común. La mejora bajo ρ=1,25 no valida una organización real GMV ni un efecto incremental de matching.

#### Validación confirmatoria D1 frente a P1: ejecutada

El [protocolo prefijado](SOC_CONFIRMATORY_PROTOCOL.md) fijó 100 semillas independientes de campañas previas, ρ=1,25, H=D=24 h y R/N terminal como variable primaria. El [informe de resultados](SOC_CONFIRMATORY_RESULTS.md) registra D1 0,5180 y P1 0,6162: diferencia pareada +0,0982 [IC95 % bilateral 0,0891; 0,1073], t unilateral con 99 grados de libertad, p=2,57×10⁻³⁹; P1 ganó 98/100 episodios. En cuatro cargas secundarias, P1 perdió R/N en ρ=0,85/1,00/1,10 y ganó modestamente en 1,15; los ocho contrastes secundarios se evaluaron con Holm. P1 perdió calidad esperada entre completadas bajo sobrecarga (0,6749→0,6378), aunque elevó el SLA terminal (0,7556→0,9663). Son resultados del simulador con parámetros humanos hipotéticos, no mediciones operativas de GMV-CERT ni evidencia de superioridad universal.

#### HLS-B: desarrollo y validación independiente ejecutados

El [desarrollo HLS-B](SOC_HLSB_DEVELOPMENT_RESULTS.md) seleccionó una ventana de llegadas observadas de 4 h e histéresis 1,05/1,20 sobre seis semillas de desarrollo. El [protocolo de validación](SOC_HLSB_VALIDATION_PROTOCOL.md) fijó después 100 semillas nuevas y cuatro escenarios sintéticos, con D1, P1 y HLS-A como referencias. El [resultado independiente](SOC_HLSB_VALIDATION_RESULTS.md) encontró HLS-B−D1 = **+0,02820** en R/N terminal, IC95 % bilateral [0,02526; 0,03115], p unilateral 4,62×10⁻³⁵, para la media de cuatro escenarios equiponderados dentro de cada semilla. La ganancia procede principalmente de la sobrecarga estacionaria ρ=1,25 (+0,1106); en ρ=1,00 perdió 0,0013 y en los dos escenarios variables la diferencia frente a D1 fue incierta. El estimando representa esa distribución artificial de escenarios, no un SOC real. No se ajustó HLS-B con las semillas de validación ni se demostró una ventaja en transiciones individuales.

#### A3.3/A4 y fases B/C — Pendientes

A3.3 debe revisar el papel de C/M y aprobar la interpretación de latencia, el conjunto de estimandos y la matriz antes de congelar A4. No iniciar campaña principal hasta resolver esas decisiones; A3 no está completa.

## Qué sigue siendo desconocido

**Supervisor HLS-A (desarrollo):** [definición, pruebas y piloto](SOC_HLS_ADAPTIVE_SUPERVISOR.md). Se integró una selección D1/P1 por presión local normalizada con histéresis, sin alterar sus reglas. Se ensayaron tres umbrales sobre seis semillas nuevas y cinco escenarios; se propuso 2/3 por el compromiso de R/N medio y conmutaciones. El piloto no demostró ventaja sobre D1 en episodios variables. El [diagnóstico directo](SOC_HLS_ADAPTIVE_DIAGNOSTIC.md) confirmó equivalencia de trayectorias con/sin instrumentación y mostró que muchos desacuerdos D1/P1 no tienen ganancia local identificable; sustituye la reconstrucción anterior no equivalente. HLS-A sirvió además como referencia en la validación independiente de HLS-B, sin constituir una validación propia preespecificada.

1. Definición operativa de llegada y zona horaria por fuente/cliente, y relación entre filas SOCTRA y trabajo efectivamente atendido.
2. Inicio, parada, espera, pausa, reasignación, handoff, cierre terminal y retrabajo por alerta.
3. SLA contractuales por prioridad/cliente: reloj, evento final, pausas, horario, prioridad cambiante y tratamiento de pendientes o reaperturas.
4. Roster L1/L2/L3 por turno, ausencias, disponibilidad, carga paralela, reglas de transferencia y elegibilidad efectiva.
5. Medidas válidas de competencia por tarea, calidad adjudicada y dificultad; `tramitador` o número de cierres no las proporcionan.
6. Si las restantes políticas T/Q/C/M (o el repertorio final) mejoran frente a D1 y bajo qué condiciones. Para P1 existe ya contraste confirmatorio limitado a ρ=1,25 y análisis secundarios; A3.2 sigue siendo piloto exploratorio y M aún no se ha implementado ni comparado en esa cartera.
7. Relación entre recomendación IA, exposición, decisión humana efectiva y tiempo/capacidad liberada; las evaluaciones organizativas no integran experimentalmente las predicciones SOCTRA.
8. Costes reales de coordinación y servicio, además de la viabilidad operativa de latencia, matching o información compartida.
9. Disponibilidad y autorización de publicación del informe original del PI de 6-11-2026 y de estadísticas de la fuente. La referencia cualitativa disponible advierte que el informe original no se encontró en el repositorio.

## Clasificación de conclusiones

| Clase | Afirmación actual |
|---|---|
| Hecho documentado | El extracto SOCTRA contiene volumen, timestamps, categorías y marcas de proceso; no hay registros de trabajo humano suficientes para reconstruir servicios. La descripción de GMV-CERT disponible es cualitativa y su fuente primaria no está en el repositorio. |
| Resultado experimental | En escenarios y semillas publicados, algunas estrategias cambian SLA, calidad modelada, cola o recompensa según carga, competencias y costes. Son resultados de simulación bajo las configuraciones descritas en [Resultados y lecciones](SOC_RESULTS_AND_LESSONS.md). |
| Decisión de investigación | El artículo relacionará conceptualmente el triaje SOCTRA previo y el estudio organizativo; sus evaluaciones se mantienen independientes. D1 queda congelado como referencia y no se exige superioridad universal. |
| Hipótesis | Roster, competencia, servicio, deadlines terminales, disponibilidad, escalado, IA simulada y costes representan configuraciones plausibles. |
| Desconocido | Si esas configuraciones describen GMV-CERT; si D1-L o D1-S mejoran el proceso integrado; y qué modificación ofrece una contribución defendible. |
| Obsoleto o condicionado | Las métricas de SLA de informes previos que computaron finalización L1 para casos escalados no equivalen a SLA terminal. Se conservan como resultados históricos y no se mezclan con la métrica corregida. |

## Estado hacia *Electronics*

La contribución organizativa aún no está demostrada mediante una mejora robusta frente a D1 y controles competitivos dentro del proceso integrado. Existe una pregunta científica delimitada, un simulador y resultados condicionales que informan la selección del problema, pero no evidencia de mejora operativa real ni validación cuantitativa del modelo para GMV-CERT. La evaluación futura deberá presentar resultados positivos y negativos con métricas terminales coherentes y supuestos explícitos.

**Estado actual:** pasos 1–4 completados; en Paso 5, A0 y D1/P1–P5 son exploratorios, D1/P1 cuenta con confirmación en sobrecarga sintética y HLS-B cuenta con validación independiente limitada a una distribución sintética equiponderada. A1/A3.1 diagnosticaron la escasez de matching y A3.2 evaluó C como prototipo distinto de P4. La cartera D1/T/Q/C/M permanece provisional. Ningún contraste representa por sí mismo GMV-CERT ni demuestra una mejora operativa allí.
