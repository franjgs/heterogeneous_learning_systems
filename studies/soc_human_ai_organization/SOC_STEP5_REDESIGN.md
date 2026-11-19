# Rediseño del Paso 5 — SOCTRA-HLS

**Estado de este rediseño:** A1 y A3.1 documentadas; A3.2 (prototipo C y piloto D1/T/Q/C) ejecutada exploratoriamente. A0 y la campaña D1/P1–P5 se revisaron después; véase la [consolidación científica](SOC_SCIENTIFIC_CONSOLIDATION.md). Las posteriores [validación D1/P1](SOC_CONFIRMATORY_RESULTS.md) y [validación HLS-B](SOC_HLSB_VALIDATION_RESULTS.md) están completadas, sin cerrar A3.3/A4 ni congelar el repertorio D1/T/Q/C/M.
**Base del código:** a0fdc87834b56884ec1200778d4fe2b7cbfd4699 más cambios locales A1 no comprometidos.
**Alcance de este documento:** auditoría del mecanismo operativo y reformulación A/B/C; actualizado tras A3.2. D1/P1/P2 permanecen sin cambios. A3.2 añadió un prototipo C y una comparación piloto, no una campaña confirmatoria.

## 1. Motivación y resultado que se revisa

La pregunta se mantiene: **¿en qué condiciones diferentes políticas de organización de analistas heterogéneos mejoran el rendimiento colectivo de un SOC frente a D1?** D1 está congelada. P1–P5 siguen siendo candidatas; la finalidad es identificar cuándo ayudan, perjudican y por qué, sin presuponer una ventaja de coordinación.

La A1 anterior ejecutó 1.768 episodios-policy y registró 170.263 estados diagnósticos en trazas sintéticas. Estimó una capacidad fluida L1 de 28,42 entradas/h para el roster/mix hipotéticos y capacidad L2 equivalente a 78,98 entradas/h bajo enrutamiento IA supuesto. Observó efecto techo de SLA hasta aproximadamente 0,85× L1, congestión alrededor de 1× y degradación a 1,25×; los deadlines ajustados degradaron SLA incluso sin saturación de capacidad. La latencia supuesta tuvo un efecto grande, especialmente para P4. Los valores, supuestos y ficheros locales están descritos en [A1: dimensionamiento experimental](SOC_A1_EXPERIMENTAL_DIMENSIONING.md).

El hallazgo de oportunidades requiere matiz: en esa muestra no hubo estados con matching factible de cardinalidad ≥2; a 0,85×, 26,2% de estados tenía dos o más analistas libres, 15,8% tenía al menos una alerta con varios elegibles y ningún estado tuvo matching múltiple. Es evidencia observada del piloto, no un teorema general ni una propiedad demostrada de toda la operación SOC.

## 2. Auditoría estructural del motor

En src/hls/rq1_allocation.py, simulate() avanza hasta el siguiente evento entre llegada, finalización, inicio posterior a latencia, H y H+D. En el mismo timestamp incorpora todas las llegadas agrupadas, libera todas las finalizaciones, procesa los inicios coordinados y forma el conjunto libre. Si existe trabajo elegible, llama una vez al dispatcher. Los selectores locales recorren los analistas libres secuencialmente; P4/P5 calculan su propuesta conjunta. Las alertas elegidas se retiran inmediatamente de la cola, no se duplican y pasan a servicio o al estado de despacho con latencia. No hay intervalo de espera configurable ni lote creado por el motor entre eventos.

AllocationSession.advance_to() procesa llegadas y finalizaciones coincidentes juntas y puede aplicar un cambio de roster en el mismo límite. advance_to no despacha automáticamente: el caller invoca dispatch(). El runner calibrate_a1_scenarios.py registra estado después de advance_to(event) y antes de dispatch("D1"); las vistas P3/P4 son diagnósticas y no se asignan en la sesión.

### Alcance exacto del argumento de la estrella

Sea G=(F,Q,E), con analistas libres F, tareas pendientes Q y arista elegible (i,a)∈E si el analista puede procesar la clase de la alerta.

1. Tras el despacho secuencial de los selectores locales no queda una pareja libre-alerta elegible: un analista que ve alerta elegible asigna una; las asignaciones posteriores solo retiran alertas. P4 maximiza cardinalidad después de su prioridad primaria. P5 usa una de estas dos reglas. Esto describe el estado residual inmediato; no demuestra optimalidad global.
2. Si entre épocas se actualiza solo un lado con exactamente un vértice nuevo (una llegada, o un analista liberado), sin eventos concurrentes del otro lado, el siguiente grafo es una estrella o subgrafo y su matching máximo cumple ν(G)≤1. Es una conclusión matemática condicional.
3. El motor no impone la condición 2. Agrupa todas las llegadas con timestamp igual y todas las finalizaciones simultáneas; también procesa llegadas y finalizaciones en una misma época. Un lote de dos alertas y dos analistas liberados puede producir ν(G)=2. Los cambios de roster de AllocationSession pueden activar varios recursos a la vez. Por tanto, no se demuestra imposibilidad estructural absoluta.
4. En Poisson continuo independiente, empates exactos de llegada tienen probabilidad cero en el modelo ideal. Las finalizaciones pueden empatar por servicios deterministas, asignaciones simultáneas o duraciones iguales; un replay puede agrupar timestamps repetidos. La muestra A1 no observó matching ≥2 en 170.263 estados, pero esa frecuencia es condicional al generador, roster, clases, H/D y reglas probadas.

El runner A1 toma los diagnósticos después de advance_to(event) y antes del despacho D1. Los previews P3/P4 inspeccionan el estado; no asignan tareas. Se añadieron dos pruebas de frontera: despacho inmediato de una nueva alerta con varios analistas libres deja cero aristas residuales; dos llegadas coincidentes con dos finalizaciones coincidentes crean un estado con matching 2. No se cambió el motor ni las políticas.

## 3. Evaluaciones externas y valoración propia

Los documentos originales de las dos evaluaciones no se encontraron en el repositorio ni entre los ficheros locales identificables en el ámbito revisado. Este análisis usa únicamente el resumen proporcionado por el PI; no presenta citas textuales ni atribuye bibliografía.

- **Experto 1:** explicó el grafo estrella bajo despacho inmediato exhaustivo y eventos individuales; advirtió que lotes, simultaneidad, el estado previo/posterior y los recursos L1/L2 condicionan el resultado. Sugirió micro-batching, llegadas agrupadas, reserva, reasignación, controles de selección individual y ablaciones de latencia/información.
- **Experto 2:** coincidió en que el matching múltiple puede escasear; pidió inspeccionar trazas, probar despacho diferido, separar prioridad individual de matching y usar una referencia central fuerte con criterio comparable. También recomendó analizar reserva y desagregar métricas por clase/tipo de analista.
- **Coincidencia:** la escasez de matching es plausible con el despacho inmediato, y diferencias de P4 no prueban por sí mismas valor de matching.
- **Límite:** el motor permite matching múltiple bajo eventos simultáneos; las pruebas no estiman su frecuencia operativa. Las revisiones externas son resúmenes recibidos, no evidencia operacional ni fuentes bibliográficas verificadas.

### Análisis crítico

- **Demostrado por inspección:** el motor despacha inmediatamente tras un evento y no deja una ventana configurable para acumular cola. Agrupa eventos con igual tiempo. A1 registra estado antes de despachar.
- **Observado:** cero matching factible de cardinalidad ≥2 en los 170.263 estados A1. En alta carga las diferencias P3/P4 ocurrieron mayormente con un analista libre. La latencia P4 también se aplicó a esos despachos individuales.
- **Hipótesis plausible:** la llegada/evento individual y la ausencia de cola con varios elegibles explican parte de la escasez. El generador, equipo y mezcla elegidos también condicionan la frecuencia.
- **No identificado:** la mejora SLA de P4/P5 en estrés no prueba mejora por matching. Con un analista libre P4 se reduce a elección central de alerta y utiliza un objetivo distinto de P1/D1.
- Una organización puede mejorar una decisión individual informándose del estado colectivo sin matching múltiple.
- No se acepta introducir simultáneamente batching y reserva. El primero cambia el tiempo de decisión; la segunda cambia el uso de capacidad ante trabajo futuro desconocido. Requieren justificaciones y costes separados.

## 4. Qué reutilizar de A1 y qué revisar

### Reutilizable como evidencia condicional

- Capacidad fluida por nivel calculada por LP para roster, mezcla, servicio y elegibilidad hipotéticos; no es capacidad medida GMV.
- Curvas piloto de carga y presión temporal, métricas H/H+D, pendientes y drenaje. Se observaron efecto techo, transición y saturación dentro del modelo A1.
- Sensibilidad a latencia/coste supuestos y diagnóstico de oportunidades; no atribuir a matching los efectos de P4/P5.
- Parámetros, semillas y runner: config/a1_calibration.json y calibrate_a1_scenarios.py. Los resultados CSV permanecen locales e ignorados por Git; no están disponibles en un checkout limpio.
- Regresión previa A1: 92 tests relevantes. En esta revisión se añadieron tests estructurales. El coste por arista se propaga en la envoltura L1/L2 con valor por defecto cero; latencia y coste siguen siendo hipótesis.

### Debe recalibrarse o explicitarse antes de Fase B

- Oportunidades por fuente: llegadas, liberaciones, empate llegada-finalización, cardinalidad de lote, aristas elegibles y ν(G), por separado para L1 y L2.
- Proporción de decisiones P4 con cero, uno o ≥2 analistas libres; resultados con ν(G)=1 frente a ganancia incremental cuando ν(G)≥2.
- Carga por clase, elegibilidad, competencia, velocidad y composición del roster; determinan complementariedad y cuello de botella, pero no están medidos para GMV.
- Latencia/coste, cola y definición H/H+D. Coste por arista es una unidad abstracta; P5 no lo considera al activar matching. La utilización reportada mide servicio y no cuenta espera de coordinación como servicio ocupado.
- Poisson sintético no reproduce la sobredispersión/interllegadas SOCTRA. El replay puede conservar timestamps empatados, pero SOCTRA no observa servicio, competencia, turnos ni SLA terminal.
- Esta formulación histórica proponía SLA terminal simulado por alerta admitida como métrica primaria, con H y H+D y L2 como término final cuando hubo escalado. La campaña D1/P1–P5 posterior fijó R/N esperado por admitida como métrica primaria exploratoria e informó SLA y calidad por separado. Ambas definiciones se conservan con su procedencia; no son intercambiables.

## 5. Diseño de políticas: propuesta A2 para revisión

La taxonomía, reglas y controles están en [A2: taxonomía y diseño](SOC_A2_POLICY_TAXONOMY_AND_DESIGN.md); la comparación entre carteras A/B y recomendación híbrida está en [A2.2: decisión de cartera](SOC_A2_POLICY_PORTFOLIO_DECISION.md). El PI aprobó provisionalmente D1/T/Q/C/M para evaluación; no se congelan las políticas ni se cierra A2.

La comparación A2.2 recomendó **D1 congelada + T, Q, C (coordinación central secuencial) y M (matching conjunto)**. El PI aprobó esta cartera provisionalmente para evaluación, no como congelación definitiva. S queda como posible contraste secundario; R/reserva intertemporal queda diferida. P5 no se recomienda en su forma actual como política confirmatoria: su activación no optimiza beneficio neto y mezcla P3/P4. En A3.2 C se implementó como greedy secuencial, sin lote; M sigue fuera del piloto.

Para identificar matching, M/P4 requiere un control de selección central secuencial que use la misma información, factibilidad, urgencia y desempates, pero emita una pareja por vez sin optimizar la asignación completa. Estratificar además estados con un analista libre y con ν(G)≥2. Esta definición está pendiente, no implementada.

P3 debe describirse como regla greedy de escasez de elegibilidad con prioridad secundaria de competencia propia, no como reserva de especialistas: no espera ni protege recursos ante llegadas futuras. Una política de reserva futura sería un mecanismo diferente que requeriría medir coste de ociosidad.

## 6. Nueva hoja de ruta del Paso 5

### Fase A — Fundamentación y diseño

| Etapa | Actividad y dependencia | Entregable | Criterio de cierre |
|---|---|---|---|
| **A1. Auditoría del mecanismo** | Revisar eventos, reglas y evidencia existente. Dimensionamiento exploratorio previo; revisión estructural en curso. | Este documento, revisión de políticas y tests estructurales. | Condiciones del resultado estrella y discrepancias documentadas. |
| **A2. Taxonomía y selección del repertorio** | Comparar cartera conservadora y organizativa; PI decide cartera y reglas. | [Propuesta A2](SOC_A2_POLICY_TAXONOMY_AND_DESIGN.md), [decisión A2.2](SOC_A2_POLICY_PORTFOLIO_DECISION.md) y repertorio aprobado. | Controles separan decisión local, información central y matching; D1 sigue congelada. |
| **A3.1. Viabilidad de mecanismos** | Verificar diferenciación lógica y oportunidades M bajo A1; definir estados de contraste. | [Diagnóstico A3.1](SOC_A3_1_MECHANISM_FEASIBILITY.md). | Distinguir oportunidad, desacuerdo, objetivo previsto y resultado; A1 no mostró matching múltiple. |
| **A3.2. Prototipo C y piloto** | Hacer comparable la selección central secuencial con D1/T/Q y medir mecanismos en un piloto pequeño. | [Piloto A3.2](SOC_A3_2_PILOT_COMPARISON.md), código y configuración reproducibles. | C diferenciada y probada; resultados pareados y límites reportados; piloto explícitamente exploratorio. |
| **A3.3. Revisión de estimandos y cartera** | Revisar los resultados A3.2; decidir papel de C y M, métricas primarias y costes/latencias que pueden justificarse. | Decisiones PI registradas y protocolo/matriz propuestos. | Evitar atribuir a matching resultados de selección central; fijar comparaciones y reglas antes de B. |
| **A4. Protocolo** | Preespecificar semillas, contrastes primarios, IC/multiplicidad, métricas terminales y coste. | Protocolo reproducible congelado. | Comparación pareada homogénea y costes con unidades interpretables o sensibilidad declarada. |

**Dependencias:** aprobación provisional A2 precede al piloto; A3.1 informa A3.2; revisión A3.3 precede al cierre de cartera, estimandos y matriz; A4 y tamaño muestral preceden a B.

### Fase B — Validación experimental

1. Verificar controles de mecanismo con estados conocidos, conservación, elegibilidad, no duplicación, causalidad y simultaneidad.
2. Comparar D1 y políticas aprobadas con trazas, recursos y métricas homogéneas y semillas emparejadas.
3. Aislar prioridad individual, información global, matching y costes mediante controles/ablaciones aprobados.
4. Reportar SLA terminal H/H+D, calidad modelada, espera/respuesta, backlog, utilización por pool/clase/tipo, latencia y coste.

**Cierre:** resultados reproducibles responden a contrastes predefinidos, muestran pendientes/censura y compromisos y no atribuyen mejora a un mecanismo no aislado. No declarar superioridad universal.

### Fase C — Robustez y realismo operativo

1. Sensibilidad a patrones temporales, lotes, composición, elegibilidad/servicio/competencia, escalado, horizonte/drenaje y costes.
2. Contrastar con agregados/replay SOCTRA autorizado, sin confundir registro de alerta con tiempo de trabajo ni etiqueta con verdad.
3. Incorporar evidencia GMV adicional solo con autorización y definiciones verificables.
4. Identificar conclusiones invariantes, dependientes del modelo y no validadas externamente.

**Cierre:** documentar límites de generalización. Fase C no convierte hipótesis en hechos por ajuste.

## 7. Criterios de avance y decisiones del PI

- Avanzar a B requiere aprobación del repertorio y del control de matching, además de aceptar que la simulación describe mecanismos y no la operación GMV.
- No alterar el motor antes de decidir si los empates/lotes existentes son suficientes para estudiar matching; cualquier intervalo deliberado requiere evidencia sobre una operación real, coste y duración.
- Si se introduce reserva, especificar horizonte de decisión, coste de capacidad ociosa y control sin reserva; no asumir que reservar es beneficioso.
- Mantener explícito que A1 obtuvo frecuencia cero en la muestra, no imposibilidad; la prueba unitaria de matching 2 demuestra capacidad funcional en un caso construido, no frecuencia operativa.
- No se añadió bibliografía. Revisiones externas disponibles solo en el resumen del PI.

**A2.2 decisión PI:** D1/T/Q/C/M aprobado provisionalmente para evaluación, no congelado. **A3.2 resolvió parcialmente:** C tiene ahora un prototipo definido y probado como selección central greedy, y Q se reutiliza sin alterar P2. El piloto encontró cero matching ≥2 en 66.140 snapshots D1 y la latencia hipotética de C perjudicó prestaciones; el control sin coste/latencia es sólo un límite diagnóstico. **Pendiente en A3.3/A4:** decidir si C se mantiene como contraste central; el papel de M ante oportunidades naturales escasas; si la unidad de coste por arista y la latencia de 0,05 h tienen interpretación defendible; congelar métricas, estimandos, matriz y precisión estadística. Los resultados A3.2 son exploratorios y no sustituyen la campaña B.

**A3.1 (registro histórico de esa fase):** la instrumentación A1 reutilizada arrojó cero estados `nu(G)>=2` en 170.263 filas y cero llegadas simultáneas exactas en la comprobación acotada de 42.293 trazas sintéticas regeneradas. El motor admite matching múltiple, pero M careció de oportunidad bajo A1. C todavía no existía como política en A3.1; los ejemplos controlados eran diagnósticos, no evaluación de episodio. Véase [A3.1](SOC_A3_1_MECHANISM_FEASIBILITY.md). A3.1 no aprueba ni elimina M.
