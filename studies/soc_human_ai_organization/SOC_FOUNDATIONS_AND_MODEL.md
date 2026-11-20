# Fundamentos y modelo SOC

## 1. Pregunta científica y relación con HLS

HLS estudia la organización y el aprendizaje de entidades heterogéneas en entornos dinámicos. SOCTRA-HLS es una aplicación a equipos SOC donde el triaje asistido por IA y la organización del trabajo humano son componentes relacionados del problema editorial. La pregunta organizativa de este estudio es: **¿en qué condiciones pueden estrategias sencillas de priorización temporal, especialización y coordinación mejorar el rendimiento colectivo de un SOC respecto a D1?** Se busca identificar mecanismos, beneficios y compromisos; no se presupone que coordinación, heterogeneidad o adaptación sean beneficiosas ni se pretende demostrar superioridad universal.

El antecedente SOCTRA de clasificación de escalado/reporte y el estudio de organización son preguntas distintas. El capítulo de Lázaro et al., AIAI 2026, DOI [10.1007/978-3-032-30805-4_11](https://doi.org/10.1007/978-3-032-30805-4_11), informa resultados de clasificación, no asignación de analistas. La reducción de carga de triaje comunicada en SOCTRA no cuantifica horas humanas liberadas. La relación bibliográfica y las discrepancias de configuración/modelo que se documentaron están resumidas en la sección de AIAI/SOCTRA de [Resultados y lecciones](SOC_RESULTS_AND_LESSONS.md).

## 2. Evidencia y límites de observación

### Extracto SOCTRA

El extracto local restringido `dataset_20250919.csv` abarca **214.739 IDs únicos** entre 2022-12-31 y 2025-09-18, con timestamps sin zona horaria, etiquetas de proyecto, descriptores de alerta, marcas de cierre y etiquetas históricas como `escalada_L2`, `escalada_procedimiento`, `reportado` e incumplimiento SLA. En los análisis agregados se contaron 27 etiquetas de proyecto; las cinco de mayor volumen concentran 59,23% y las diez, 82,83%. Promedio observado del extracto: 216,3 alertas por día; p95 379; máximo diario 574; CV diario 0,414; Fano diario 37,05; autocorrelación de primer retardo 0,525; CV de interllegadas 1,604. Hubo 15.541 registros excedentes con timestamps coincidentes. Estas propiedades no son compatibles con un Poisson homogéneo simple y respaldan conservar variabilidad/ráfagas al construir demanda. No implican que el volumen de registros sea igual a carga de trabajo atendida.

No se incluyen aquí IDs, nombres de proyecto ni registros individuales. Las estadísticas son agregados del snapshot autorizado para análisis local; sus límites de zona horaria, construcción de snapshots y uso editorial siguen vigentes. La fuente SOCTRA caracteriza volumen, tiempos de registro, estructura y etiquetas de proceso; no una trayectoria de atención. El análisis publicado AIAI 2026 reporta, para una configuración de escalado estandarizada de LSE, balanced accuracy 0,8477, probabilidad de falsa alarma 0,2695 y detección 0,9649; el rendimiento varía por modelo y configuración de etiqueta. Son métricas agregadas bajo un protocolo de clasificación, no parámetros universales de la IA simulada ni predicciones OOS por alerta.

| Constructo | Estado | Qué permiten afirmar los datos |
|---|---|---|
| Timestamp y conteo de alertas registradas | OBSERVADO | Volumen y patrones temporales del extracto, sujeto a semántica/timezone sin validar. |
| Proyecto, prioridad/severidad, nivel y tipos/categorías | OBSERVADO | Composición etiquetada; una etiqueta no prueba gravedad objetiva ni esfuerzo. |
| Escalada, reporte, cierre e incumplimiento de SLA | OBSERVADO como etiquetas | Acciones/estados históricos según la codificación; no verdad objetiva, decisión contrafactual ni calidad adjudicada. |
| Tasas, concentración, interllegadas, variabilidad | DERIVADO | Estadísticas calculadas sobre el snapshot, no tasas de trabajo activo. |
| Asignación, inicio/parada, espera, duración activa, handoff, roster/turnos | NO DISPONIBLE | No se puede medir servicio o capacidad de analista. |
| Competencia individual, exactitud real, necesidad objetiva de escalar | NO DISPONIBLE | No inferir desde `tramitador`, volumen procesado, cierre o etiqueta de escalado. |
| SLA contractual y evento de cumplimiento | NO DISPONIBLE/INCOMPLETO | Hay una marca histórica, pero no definición verificable de reloj, inicio, término, pausas o censura. |

La columna `tramitador` contiene etiquetas con semántica e identidad no verificadas y recodificación histórica; no se usa para reconstruir trayectorias personales o competencia. No se requieren ni reproducen artefactos de predicción OOF: folds aleatorios no son recomendaciones temporalmente disponibles. El pipeline temporal se conserva como trabajo independiente y no bloqueante para la validación simulada.

### Referencia cualitativa GMV-CERT

La [referencia operativa GMV-CERT](GMV_CERT_OPERATIONAL_REFERENCE.md) conserva una reconstrucción preliminar atribuida por el PI a conversaciones con personal de GMV; las notas originales no están disponibles y no se reproducen citas textuales. Incluye el recuerdo de una herramienta para visualizar/seleccionar alertas (nombre desconocido), tendencias distintas entre generalistas y especialistas, selección individual, tratamiento secuencial y posibilidad de reordenarlas, relación comunicada entre experiencia y alertas procesadas, plantilla aproximada 20–30, cobertura nocturna desde Colombia y coordinación/supervisión L3 por proyecto. Los valores anotados de SLA incluyen crítica “4” (unidad desconocida), alta 6 h y media 12 h; no está confirmado qué evento cierra el reloj. La calidad incluye revisión/reapertura, no solo cierre o volumen. El PI plantea como hipótesis, aún no contrastada, que el conocimiento de competencias propias y la estimación de competencias de compañeros pueden influir en elecciones individuales; no se afirma que GMV utilice una estimación formal de pares. Nada de lo anterior constituye un procedimiento escrito verificado ni valida D1/P1/HLS-B como réplicas de la operación real.

Estos puntos son **información comunicada**, no procedimiento escrito verificado. Interpretar selección tipo pull/autonomía individual es plausible, pero no se confirmó cola única compartida, libertad total ni ausencia de coordinación. La fuente original del PI de 6-11-2026 no se encontró en el repositorio; la fecha/atribución se conserva como indicada, sin afirmar revisión del original. No convertir esos datos en parámetros cuantitativos.

## 3. Modelo y simulador implementados

### Demanda y entidades

El laboratorio genera alertas con llegada, clase/proyecto, severidad/prioridad, deadline, dificultad y necesidad simulada de escalado. Permite composición y carga configurables, llegadas de escenarios sintéticos y replay de timestamps SOCTRA. En ese simulador, necesidad real, dificultad y verdad de resolución son estados generados y ocultos a las políticas. La IA produce recomendación a partir de una referencia simulada con sensibilidad/falsos positivos parametrizados; recomendación, etiqueta histórica, decisión de ruta y referencia simulada son conceptos separados.

La operación L1/L2 utiliza servicio secuencial no preemptivo, elegibilidad y competencia fija; puede escalar a L2 de acuerdo con la regla del escenario. La exactitud/éxito de resolución se modela probabilísticamente en ciertas versiones. B4EpisodeEnv ofrece decisiones secuenciales sobre estados observables y recompensas en eventos de resultado. No hay turnos reales, L3 operativo, aprendizaje de competencias ni costes empíricamente calibrados. Las implementaciones históricas HLS-02 no son este motor.

### Parámetros: procedencia

| Clase | Ejemplos | Evidencia |
|---|---|---|
| Empíricos observados | Conteos/timestamps de registros, categorías y mezcla agregada de SOCTRA; métricas publicadas del clasificador bajo las configuraciones informadas | Útiles para caracterizar demanda/errores, no para especificar trabajo posterior. |
| Derivados | Tasas por hora/día, concentración, Fano, CV, autocorrelación | Dependen del snapshot, reglas de agrupación y timezone. |
| Hipotéticos operativos | Analistas por nivel, horas de disponibilidad, servicio, elegibilidad, competencia, escalado efectivo, deadline de resolución, calidad, coordinación/latencia | Escenarios experimentales, no mediciones GMV. |
| Hipotéticos experimentales | Horizonte, semillas, tasas, carga, duración de ráfaga, composición, costes y reglas de reward | Control del experimento; declarar en cada informe. |

El estudio paramétrico de referencia utilizó 9 alertas/h, H=24 h, drenaje D=36 h, 6 L1/3 L2 y tres estratos anónimos de cartera, 12 semillas por punto. Son parámetros asumidos: 9/h se deriva de 216/día suponiendo distribución uniforme durante 24 h, que no queda validada; el roster y el calendario también son hipotéticos. No llamar a esos escenarios “GMV representativo”.

### Métricas recomendadas para leer resultados

Métrica primaria de simulación: fracción de **todas las alertas admitidas** cuya resolución terminal cumple el deadline configurado; si la ruta escala, el término debe ser la finalización L2. Denominarlo cumplimiento de deadline hipotético hasta validar contrato/evento. Publicar por separado resultados al corte H y al cierre H+D; pendientes vencidas son fallos maduros, pendientes con deadline no maduro son censura, y los pendientes se informan explícitamente. Complementar con calidad simulada/adjudicada según corresponda, tiempos de espera y respuesta (distribuciones/percentiles), backlog/colas, utilización por analista/nivel y coste/latencia por unidad. Evitar la recompensa escalar con pesos no validados como métrica científica única.

La agregación de SLA terminal fue corregida para usar la finalización L2 cuando hubo escalado (ver código `src/hls/ia_l1_l2_simulation.py`, `_terminal_info`, y `src/hls/rq1_l1_l2.py`, `metrics`). Cifras de informes anteriores al arreglo requieren comprobar si usaron métrica madura correcta; [Resultados y lecciones](SOC_RESULTS_AND_LESSONS.md) las marca.

## 4. Estrategias SOC y distinción histórica

El repertorio vigente del estudio usa los nombres **D1 y P1–P5**. P1–P5 son etiquetas nuevas y no equivalen a P0/P1 de la antigua familia C×P.

| Política vigente | Mecanismo y regla | Información y coste | Régimen de interés y limitación |
|---|---|---|---|
| **D1** | Referencia descentralizada congelada; regla exacta abajo. | Riesgo y competencia propios, más elegibilidad general de compañeros; sin matching ni coste de coordinación. | Baseline operativo cualitativo. No está validado como procedimiento GMV. |
| **P1 — temporal** | Cada analista libre elige secuencialmente la alerta elegible con menor holgura posterior al servicio; empate por deadline, llegada e ID. | Cola pendiente, tiempo y duración propia. Sin coordinación. | Mecanismo directo para plazos ajustados; ignora la competencia salvo la restricción de elegibilidad. |
| **P2 — competencia** | Selección local por mayor competencia propia; empate por holgura posterior al servicio, deadline, llegada e ID. | Competencia y servicio propios. Sin coordinación. | Aísla adecuación analista-alerta; puede sacrificar puntualidad por mayor competencia. |
| **P3 — capacidad y especialización** | Selección local secuencial; prioriza alertas con menos analistas libres restantes elegibles, luego mayor competencia propia y menor holgura posterior al servicio. | Consulta elegibilidad de compañeros aún no asignados; no sus competencias ni duraciones. Sin coste de coordinación. | Orientado a elegibilidad solapada/escasez. El número de elegibles es un proxy simple de coste de oportunidad, no una medida empírica de especialización. |
| **P4 — matching conjunto** | Matching uno-a-uno en el despacho actual; maximiza lexicográficamente finalizaciones previstas a tiempo, número de asignaciones y prioridad de deadlines. | Usa elegibilidad, tiempos y deadlines de todos los analistas libres y alertas pendientes. Latencia y coste por aristas elegibles configurables; no mira llegadas futuras. | Puede aprovechar complementariedad simultánea; coste y beneficio dependen del estado y de parámetros hipotéticos. |
| **P5 — matching selectivo** | Ejecuta P3 por defecto. Usa el matching P4 solo si mejora estrictamente el par lexicográfico (finalizaciones previstas a tiempo, asignaciones totales), evaluado con la latencia configurada. | Compara centralmente el estado actual; si activa matching incurre en sus costes/latencia. No usa umbrales ni pesos. | Selectividad observable y determinista; el criterio no convierte coste y SLA a una utilidad neta común, por lo que no garantiza beneficio económico neto. |

Las cinco P son controles mecanísticos distintos, no afirmaciones de superioridad. P1–P3 separan prioridad temporal, competencia propia y escasez de elegibilidad; P4 coordina siempre; P5 coordina solo ante mejora prevista en su criterio declarado. P2 puede sacrificar puntualidad por competencia; P3 es una regla de capacidad basada en elegibilidad, no en una matriz global de habilidades.

Las denominaciones históricas **B0–B4**, **C0/C1/C2 × P0/P1** y **D1-L/D1-S** identifican campañas anteriores y no son aliases de P1–P5. Sus resultados se mantienen en [Resultados y lecciones](SOC_RESULTS_AND_LESSONS.md), con las condiciones originales. El código y runners históricos se conservan para trazabilidad y reproducción de esos resultados; la interfaz vigente del nuevo repertorio es `SOC_POLICY_NAMES` y el argumento `policy` de `simulate()` en `src/hls/rq1_allocation.py`.

Implementación principal: `src/hls/rq1_allocation.py` (`Alert`, `Analyst`, `AllocationSession`, `simulate`, `SOC_POLICY_NAMES` y selectores); `src/hls/rq1_l1_l2.py` (motor L1/L2); `src/hls/ia_l1_l2_simulation.py` (escenarios e IA simulada). Las pruebas específicas del repertorio están en `tests/test_soc_organization_policies.py`; las pruebas de eventos y D1 congelado continúan en `tests/test_rq1_allocation.py`. **HLS-02 S0–S4**, en `src/hls/temporal_allocation.py`, son políticas de otra línea histórica; no son estrategias SOC.

### Regla operativa de D1 y alcance de las comparaciones

En `src/hls/rq1_allocation.py`, `_dispatch_d1` procesa analistas libres secuencialmente en un orden aleatorio reproducible. Para cada analista considera alertas pendientes elegibles y ordena por riesgo temporal descendente, competencia propia descendente, menor número de compañeros libres elegibles y, finalmente, deadline, llegada e ID. El riesgo es

\[
r_{ia}(t)=\operatorname{clip}\!\left(\frac{s_{ia}-(d_a-t)}{s_{ia}},0,1\right),
\]

donde \(s_{ia}\) es la duración estimada para el analista \(i\) y alerta \(a\), y \(d_a-t\) es el tiempo restante hasta el deadline. D1 no realiza matching conjunto, no consulta las competencias ni velocidades específicas de compañeros, no planifica liberaciones futuras y no reserva alertas. El motor hace visible una cola pendiente común y el código consulta la elegibilidad de compañeros libres; estos son supuestos de la representación, no hechos confirmados sobre GMV-CERT.

En el repertorio vigente, D1-L y D1-S no son políticas candidatas. Históricamente, D1-L activaba su revisión solo si la elección D1 no podía terminar a tiempo y existía otra alerta elegible para el mismo analista que sí podía hacerlo. Escogía la alternativa viable con menor holgura posterior al servicio y desempates por competencia propia, deadline, llegada e ID. D1-S añadía un filtro: aceptaba esa alternativa solo si no reducía competencia propia ni aumentaba servicio respecto a la elección D1; no buscaba una segunda alternativa si fallaba el filtro. B0–B3 y C0P1 también pertenecen a formulaciones históricas distintas. No se equiparan sus métricas o información con las de P1–P5.

### Fundamentación, hipótesis y contribución organizativa

El problema se formula como asignación dinámica de alertas a recursos heterogéneos, con llegadas, deadlines, capacidad limitada y restricciones de elegibilidad. La priorización temporal puede favorecer el cumplimiento de plazos; la especialización puede aprovechar diferencias de competencia; la coordinación puede considerar conjuntamente las asignaciones posibles. Decisiones razonables para un analista individual no garantizan el mejor resultado colectivo, pero esa posibilidad es una motivación teórica que debe contrastarse en el modelo.

Los mecanismos pueden generar compromisos entre cumplimiento de deadline, calidad modelada, esperas, respuesta, backlog, utilización y coste/latencia de coordinación. Una asignación de mayor competencia puede tardar más; priorizar urgencia puede dejar otras alertas esperando; matching puede mejorar asignaciones sin que el beneficio bruto compense su coste. Son mecanismos posibles, no efectos universales.

Se plantean las siguientes hipótesis contrastables:

- **H1 — Priorización temporal:** una priorización temporal sencilla puede mejorar el cumplimiento de deadlines frente a D1, especialmente bajo congestión o plazos ajustados.
- **H2 — Corrección local:** una regla individual sencilla puede mejorar ciertos resultados de D1 sin coordinación global.
- **H3 — Coordinación:** la asignación conjunta puede mejorar el rendimiento colectivo cuando hay oportunidades simultáneas suficientes y heterogeneidad relevante.
- **H4 — Especialización:** incorporar competencia puede mejorar la calidad modelada, con posibles compromisos temporales y de congestión.
- **H5 — Dependencia del escenario:** las diferencias entre estrategias dependen de carga, composición de demanda, heterogeneidad, deadlines y costes de coordinación.

Estas hipótesis no son conclusiones demostradas. Los resultados previos de D1-L/D1-S, B0/B1/B2 y C2P1 conservan sus condiciones, intervalos y limitaciones en [Resultados y lecciones](SOC_RESULTS_AND_LESSONS.md); no forman una única comparación homogénea. En particular, las cifras de SLA terminal corregidas no se mezclan con resultados previos a la corrección, y la calidad RQ1 no se equipara a la calidad probabilística del entorno B4.

La contribución organizativa prevista es **un estudio comparativo y fundamentado de estrategias sencillas de organización del trabajo en un SOC con analistas heterogéneos, orientado a identificar mecanismos que mejoren el rendimiento colectivo frente a D1, las condiciones en que funcionan y sus compromisos**. La demostración cuantitativa queda pendiente de la validación experimental.

### Alcance del artículo y condiciones de validez

El artículo podrá conectar conceptualmente los resultados previos de triaje automático SOCTRA —incluidas detección y falsas alarmas en sus configuraciones publicadas— con el estudio organizativo, pero ambos permanecen como marcos experimentales independientes. No se afirma una evaluación integrada de predicciones IA con políticas organizativas. Quedan fuera de este estudio el aprendizaje de competencias humanas, RL, mecanismos adaptativos complejos y el uso experimental del triaje IA en las decisiones organizativas.

Las comparaciones organizativas del paso experimental deberán compartir trazas, equipos y parámetros; usar definiciones homogéneas de métricas, semillas emparejadas, escenarios justificados y costes explícitos; y reportar diferencias frente a D1 con incertidumbre. La métrica principal es la fracción de alertas admitidas cuya resolución terminal cumple el deadline simulado; para alertas escaladas cuenta la finalización L2. Se acompañará de alertas completadas, calidad modelada, espera y respuesta, backlog, utilización, latencia y recursos de coordinación. Se distinguirán el horizonte de admisión \(H\) y el drenaje \(D\), informando pendientes y censura. Una recompensa agregada no será prueba única de superioridad. La calidad RQ1 (competencia agregada en completaciones a tiempo) y la calidad probabilística de resolución usada en B4 son definiciones históricas distintas y no intercambiables.

Los datos de demanda observados o derivados de SOCTRA deben permanecer separados de los supuestos operativos. Competencias, tiempos de servicio, plantillas, elegibilidad y deadlines no están calibrados con mediciones operativas GMV-CERT; tampoco hay pool L3 operativo ni aprendizaje de competencias en el simulador vigente. Por ello, resultados comparativos describirán el modelo y sus condiciones, no el rendimiento real de GMV-CERT.

## 5. Reproducibilidad y fuentes técnicas

Conservar los scripts/resultados tabulares/figuras ya existentes; no versionar ni copiar datos SOCTRA restringidos. Las fuentes de implementación para revisar son los tres módulos indicados arriba, más los runners listados en [Resultados y lecciones](SOC_RESULTS_AND_LESSONS.md). Los documentos generales de HLS, teoría y gobierno de investigación mantienen su autoridad y no se duplican aquí.
