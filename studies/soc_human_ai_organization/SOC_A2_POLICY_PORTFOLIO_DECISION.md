# Paso 5, Fase A2.2 — Selección crítica del repertorio

**Estado en el momento de esta decisión:** recomendación para revisión; A2 no se cerraba y no se congelaba política. **Actualización posterior:** para A3.1 el PI aprobó provisionalmente D1/T/Q/C/M para evaluación, sin congelar el repertorio; véase [diagnóstico A3.1](SOC_A3_1_MECHANISM_FEASIBILITY.md) y [estado actual](SOC_CURRENT_STATE.md).
**Alcance:** comparar carteras conceptuales y precisar controles. No cambia código, reglas, datos ni resultados.

## 1. Motivación y evidencia de partida

Pregunta: **¿en qué condiciones distintas organizaciones de analistas heterogéneos mejoran o perjudican el rendimiento colectivo de un SOC frente a D1, y por qué?** D1 permanece congelado. La aplicación SOC es un laboratorio de mecanismos: tiempos, competencias, elegibilidad, roster y costes son en su mayoría hipótesis, no observaciones de GMV-CERT.

La A1 ejecutó 1.768 episodios-política y registró 170.263 estados. Observó cero estados con matching factible de cardinalidad ≥2; a carga 0,85, 26,2% de estados tenía al menos dos analistas libres y 15,8% una alerta elegible por varios analistas, pero ninguno permitía matching múltiple. Es un resultado de esa muestra, no una imposibilidad del motor: las pruebas estructurales muestran que llegadas y finalizaciones simultáneas pueden producir matching 2. Las diferencias favorables a P4 en estrés no identifican valor de matching: muchas se produjeron con un único analista libre, cuando P4 decide una selección individual central.

Las dos evaluaciones externas disponibles son los resúmenes del PI en [Rediseño del Paso 5](SOC_STEP5_REDESIGN.md); sus documentos originales no se localizaron. Ambos expertos consideran plausible la escasez estructural bajo despacho inmediato, recomiendan separar selección individual de matching y usar un control central secuencial comparable. Sus sugerencias de despacho diferido/reserva son opciones para examinar, no evidencia de que GMV-CERT las utilice. El análisis A2.1 coincide en no introducir batching y reserva conjuntamente ni crear oportunidades artificiales.

## 2. Repertorios A y B

### Repertorio A — Conservador

D1 + T temporal local + Q competencia local + S escasez de elegibilidad + M matching inmediato.

**Ventajas:** mecanismos explícitos, reglas cortas, baja complejidad temporal y buen control de prioridad/competencia. T y Q son controles locales interpretables. No requiere predicción futura ni cambiar el reloj de despacho.

**Limitaciones:** cuatro de cinco políticas son reglas de selección sobre el mismo despacho inmediato; por sí solas no cubren la distinción entre centralizar información y asignar conjuntamente. M mezcla ambas cosas frente a T/Q/D1. S no es reserva intertemporal: solo puntúa la escasez actual de elegibles. Así, A ofrece cobertura de criterios, pero no una taxonomía organizativa completa ni una identificación causal limpia del matching. S añade una dimensión con justificación operativa incierta y posible solapamiento con T.

### Repertorio B — Organizativo

D1 + L local mejorada + R reserva de capacidad especializada + C coordinación central secuencial + M matching conjunto.

**Ventajas:** distingue autonomía local, gestión intertemporal de capacidad, información global y matching. C frente a M puede identificar el incremento de asignación conjunta. Es taxonómicamente más cercano a “organización”.

**Limitaciones:** L combina urgencia y competencia, por lo que necesita ablaciones para identificar cuál cambia el resultado. R necesita horizonte y una estimación de demanda futura; sin ellos se convierte en S (escasez presente) o en una regla de reserva arbitraria. M necesita oportunidades simultáneas justificadas por eventos operativos; no basta con habilitar matching en código. La cartera completa es más compleja y requiere una política/estimador adicional y supuestos que hoy no están validados.

### Recomendación: cartera híbrida reducida

Recomiendo someter al PI **D1 + T + Q + C + M** como núcleo confirmatorio potencial. Es una combinación de controles A y B: conserva los controles locales separados de A y añade C, imprescindible para distinguir información/centralización de matching. No recomienda todavía R; S queda como contraste exploratorio si el PI decide mantener la pregunta de escasez actual. Esta cartera no está aprobada.

La elección de T y Q separadas es deliberada: se pierde la concisión de L, pero se evita que un resultado conjunto de urgencia+competencia sea imposible de atribuir. L podría usarse como ablación secundaria preespecificada (T+Q), no como sustituto de ambos controles. R se difiere porque su mecanismo solo es realmente intertemporal si usa una predicción de demanda incierta y contabiliza capacidad ociosa; no hay base empírica para escoger predictor, ventana o coste. C es más complejo que A, pero su valor causal compensa: sin C, una ventaja de M no puede atribuirse a matching.

## 3. Taxonomía y matriz comparativa

Las dimensiones son independientes conceptualmente; una política puede combinarlas. “Global” describe el alcance de información, no implica matching.

| Política propuesta | Información | Tiempo/deadline | Competencia/calidad | Velocidad | Escasez especialista | Horizonte | Decisión | Despacho | Coordinación/coste |
|---|---|---|---|---|---|---|---|---|---|
| **D1** | Estado de la cola, atributos propios y conteo limitado de elegibles libres | Riesgo temporal truncado; la regla exacta vigente no se modifica | Competencia propia como criterio secundario | Servicio propio estimado en factibilidad/riesgo | Conteo de pares como desempate, no reserva | Estado actual | Individual secuencial; orden aleatorio reproducible | Inmediato | Descentralizada; sin latencia/coste de coordinación |
| **T (P1)** | Cola visible y servicio propio | Menor holgura `d_a-t-s_ia` | No prioriza competencia | Sí, para calcular holgura | No | Estado actual | Individual secuencial | Inmediato | Local, coste adicional cero en modelo |
| **Q (P2)** | Cola visible y competencia/servicio propios | Deadline/holgura como desempate | Prioridad lexicográfica de competencia propia; calidad solo modelada | No la optimiza, aunque puede desempatar si se aprueba | No | Estado actual | Individual secuencial | Inmediato | Local, coste adicional cero en modelo |
| **C** | Vista global de cola, libres, elegibilidad, `s_ia` y deadlines | Objetivo temporal común con M | Excluida del objetivo primario para aislar matching | Sí, por pareja | Puede observar elegibilidad; no reserva | Estado actual | Central secuencial: decide una pareja, actualiza estado y repite sin resolver el matching completo | Inmediato | Coordinación central; latencia/recursos configurables e iguales a M para el contraste causal |
| **M** | Igual que C | Mismo objetivo/feasibilidad que C | Excluida del objetivo primario | Sí | Solo mediante aristas de elegibilidad | Snapshot actual | Matching conjunto uno-a-uno | Inmediato tras evento compuesto/simultáneo; sin espera artificial por defecto | Coordinación central; mismos costes por época que C; esfuerzo computacional adicional medido aparte si procede |
| **S (opcional)** | Elegibilidad y roster libre compartidos | Puede perjudicar urgencia si la escasez domina | No necesariamente usa competencia | No modela coste de oportunidad temporal futuro | Prioriza clase con menos otros elegibles libres | Estado actual | Regla greedy local-secuencial | Inmediato | Información compartida mínima; sin reserva real |
| **R (diferida)** | Historial observable de llegadas por clase, cola y roster | Deadline debe limitar cuánto recurso puede reservarse | Puede incluir especialización solo si definición aprobada | Servicio estimado por pareja | Reserva explícita guiada por escasez/demanda estimada | Intertemporal, probabilístico | Reserva o penalización por consumir recurso flexible | Puede dejar recurso ocioso; no exige batching por sí misma | Coste de ociosidad/espera; sin cifra empírica actual |

Dimensiones cubiertas por el núcleo: información local/global, urgencia, competencia, velocidad como factibilidad, selección individual/central secuencial/conjunta y coste coordinativo. No cubre intertemporalidad/reserva, despacho diferido ni activación selectiva neta; quedan fuera del contraste confirmatorio recomendado hasta justificar datos y costes.

## 4. Formulación propuesta del núcleo

### D1 — referencia congelada

Se utiliza exactamente la implementación actual `_dispatch_d1` en `src/hls/rq1_allocation.py`; no se modifica su orden, clave, desempates ni uso de competencia. La caracterización resumida en A2.1 no autoriza recalibrarla.

### T — prioridad temporal local

En orden de analista preespecificado y común en los controles de orden, para cada analista `i` libre elegir entre alertas `a` con elegibilidad `E_ia=1` la de menor holgura `h_ia=d_a-t-s_ia`; empate por deadline, llegada e ID. Servicio no preemptivo, alertas vencidas permanecen procesables. No usa competencias de pares ni coste de coordinación. Difiere de D1 si sus claves ordenan distinto la cola elegible. Puede ser inferior si atiende una tarea ya irrecuperable sobre otra viable (la regla actual de P1 usa holgura sin clase explícita de recuperabilidad); se reportará esa condición, no se ocultará.

### Q — competencia local

Cada analista decide individualmente y elige la alerta elegible de mayor `e_ia`; desempates por menor holgura, deadline, llegada e ID. La competencia no altera `s_ia`. Q difiere si hay alternativas elegibles con competencia propia distinta; puede sacrificar SLA, aumentar espera o reducir throughput si la regla no prioriza urgencia. La calidad es solo simulada y el supuesto `e_ia -> probabilidad de resolución` debe mantenerse explícito.

### C — coordinación central secuencial

En un snapshot de evento, el coordinador observa cola y todos los analistas libres/elegibles. Para cada pareja define holgura `h_ia=d_a-t-ell-s_ia`. Ordena parejas lexicográficamente: (1) factible antes del deadline antes que tardía; (2) entre las factibles, menor holgura (deadline más urgente); entre las tardías, menor tardanza prevista `-h_ia`; (3) IDs estables. Selecciona una sola pareja, la retira de la cola y actualiza los recursos del snapshot; repite hasta no haber pareja factible en elegibilidad. No maximiza conjuntamente el número de asignaciones a tiempo ni la cardinalidad, y no ve futuras llegadas. La regla evita preferir una tarea mucho más irrecuperable frente a otra tardía que casi puede cumplir; el desempate temporal exacto debe congelarse antes de A3.

Para aislar **información central** de matching, la versión primaria de C y M debe compartir únicamente el objetivo temporal (sin competencia). Q queda como contraste separado. La variante central que también considera competencia sería otra ablación, no C principal.

### M — matching conjunto

En el mismo snapshot y con la misma matriz de factibilidad que C, encontrar `x_ia ∈ {0,1}` que maximice lexicográficamente: (1) número de parejas previstas a tiempo; (2) número total de parejas factibles; (3) conjunto de deadlines más próximos; (4) vector estable de IDs. Restricciones: `sum_a x_ia <= 1` por analista y `sum_i x_ia <= 1` por alerta; `x_ia=0` si no hay elegibilidad. Sin competencia en objetivo primario, sin futuras llegadas y sin reserva.

La diferencia M−C solo identifica matching cuando ambas tienen mismo snapshot, parejas factibles, criterio temporal, desempates, latencia y coste de coordinación. C emite parejas secuencialmente sin optimización conjunta; M calcula el lote asignado conjuntamente. Si `nu(G)=1`, la cardinalidad de M no puede exceder una; puede aún seleccionar otra pareja que C por sus desempates/objetivo y eso sería un contraste de regla, no beneficio de matching múltiple. Para atribuir matching deben existir al menos dos parejas en una asignación conjunta factible **y** una competencia entre asignaciones (por ejemplo, una tarea/analista flexible y otra tarea con elegibilidad restringida) tal que C y M puedan producir asignaciones distintas. `nu(G)>=2` es necesario, no suficiente.

Latencia `ell` se contabiliza una vez por época de coordinación en ambas C/M; el tiempo-persona de coordinación se separa del tiempo de servicio. Coste computacional o de comunicación se registra en unidad propia; no se suma a SLA con pesos arbitrarios. Primero se compara límite diagnóstico `ell=0`, y después sensibilidad declarada; el coste cero no representa una operación medida.

## 5. Mecanismos operativos y plausibilidad

| Mecanismo | Evaluación para este estudio | Clasificación |
|---|---|---|
| Despacho inmediato | Coherente con el motor y con la descripción cualitativa de selección/atención individual; la descripción de GMV no confirma todos sus detalles. Mantener como base. | Directamente compatible; plausibilidad externa parcial. |
| Llegadas agrupadas | El motor agrupa timestamps iguales. SOCTRA contiene timestamps coincidentes, pero su causa y relación con trabajo simultáneo no están validadas. | Compatible con datos/replay; semántica operativa pendiente. |
| Coordinación central secuencial | Operativamente concebible como supervisor que asigna la siguiente alerta con vista global. GMV describe función L3 de coordinación/supervisión, sin confirmar despacho central de cada alerta. | Plausible no validado; no atribuir a GMV. |
| Matching conjunto | Concebible si llegan lotes o varios analistas se liberan simultáneamente; matching puede aprovechar el estado compuesto sin retrasar despacho. A1 no encontró estos estados en su muestra. | Mecanismo implementable, prevalencia por demostrar. |
| Revisión periódica/diferida | Puede acumular cola y crear matching, pero introduce espera. No hay evidencia disponible de ventana periódica real. | Extensión plausible, actualmente experimental. |
| Reserva de especialista | Puede conservar cobertura para clase rara, pero causa ociosidad o demora y requiere expectativa de demanda futura. No se conoce política real de reserva. | Extensión intertemporal no validada. |
| Reasignación | Puede mejorar cobertura/carga, pero requiere autoridad, estado del trabajo, coste de handoff y efectos sobre continuidad. No está caracterizada por datos actuales. | Fuera del núcleo; extensión por justificar. |
| Activación selectiva | Requiere estimar beneficio y comparar con latencia/coste en medida común. P5 no incluye coste de recursos en el disparador. | No lista para política confirmatoria. |

No se propone añadir batching para elevar `nu(G)`. Si se estudia en otra fase, deberá derivarse de evidencia sobre cadencia operativa y medir explícitamente espera de alertas y recursos, con controles de despacho inmediato. No se atribuye a GMV-CERT cola única, centralización, reserva ni procedimiento concreto no confirmado por [su referencia cualitativa](GMV_CERT_OPERATIONAL_REFERENCE.md).

## 6. Condiciones experimentales y estimación de oportunidades

Para cada estado pre-despacho y por pool, registrar:

- analistas libres, alertas pendientes, grado de cada vértice y `nu(G)`;
- número de matchings máximos y si existe conflicto entre ellos (no solo cardinalidad);
- decisión de T/Q/C/M y si cambia la primera pareja o el lote completo;
- diferencias de holgura, competencia y servicio entre las soluciones factibles;
- activación, latencia, coste, tiempo-persona, espera inducida y asignaciones;
- resultado de SLA terminal, calidad modelada, espera, backlog y utilización, distinguiendo estado diagnóstico de métrica de episodio.

Separar cuatro niveles: **oportunidad teórica** (alternativas factibles), **oportunidad de mecanismo** (criterio/parejas permitirían distinta asignación), **decisión diferente observada** y **beneficio de resultado medido**. No inferir el último de los anteriores.

Requisitos A3 sin fijar matriz: (i) cargas relativas a capacidad efectiva L1/L2 y por clase; (ii) presión deadline medida respecto a `s_ia` y proporción prevista alcanzable, no deadline nominal solo; (iii) heterogeneidad de `e` y `s` variada independientemente; (iv) elegibilidad solapada y escasa; (v) trazas con llegadas/finalizaciones naturalmente simultáneas y reporte de su frecuencia; (vi) estrés con cola persistente y condición de cuello L2; (vii) sensibilidad separada de latencia y coste; (viii) controles de carga homogénea/heterogénea y selección central; (ix) semillas emparejadas, resultados H/H+D y estratos por oportunidad real. A1 da punto de partida sintético; no es calibración GMV. A3 deberá comprobar primero si C/M pueden diferenciarse en condiciones justificadas antes de estimar campaña.

Escenarios deberán clasificarse como representativos plausibles (solo respecto a demanda agregada sustentada), contraste causal (variación aislada), estrés o sensibilidad. No se declara todavía ninguna celda ni nivel final.

## 7. Hipótesis independientes

- **H1 — prioridad:** T cambia la selección respecto a D1 donde las holguras discrepan y puede mejorar SLA terminal en carga/plazos conflictivos, con posibles cambios de espera y calidad.
- **H2 — adecuación:** Q aumenta calidad modelada cuando una misma persona tiene alternativas con `e` distinto; el beneficio no valida competencia humana y puede perjudicar SLA.
- **H3 — información central:** C difiere de T/D1 al usar estado global y puede alterar asignación/cobertura aun cuando `nu(G)=1`; medirlo por separado del matching.
- **H4 — matching incremental:** M mejora respecto a C solo en snapshots con conflicto de asignación conjunta factible; frecuencia y beneficio dependen de simultaneidad, elegibilidad, servicio y deadlines. Latencia/coste puede revertir mejora bruta.
- **H5 — reserva:** una política R con demanda futura incierta podría conservar cobertura especializada, pero requiere estimación histórica y coste de ociosidad; queda pendiente y no se presume favorable.
- **H6 — régimen:** efectos varían con carga efectiva por pool/clase, presión temporal, heterogeneidad, elegibilidad y eventos simultáneos.

## 8. Controles y ablaciones

1. D1 vs T y D1 vs Q con mismo roster, llegadas, servicios y elegibilidad. Mantener D1 exactamente como está; registrar su orden aleatorio original. Si se controla el efecto del orden de analistas, hacerlo mediante una ablación diagnóstica separada que aplique el mismo orden por época a las reglas comparadas, sin sustituir el resultado del baseline D1.
2. **T+Q (L)** como ablación factorial solo si se preespecifica: reglas T y Q por separado permiten atribuir efectos principales e interacción.
3. C vs selector local con objetivo temporal idéntico: estima el cambio por centralización/información.
4. M vs C bajo igualdad de snapshot, objetivo, factibilidad, desempates, latencia y coste: estima incremento de asignación conjunta.
5. Estratos `nu(G)=0/1/>=2`, y para `nu>=2` separar estados con conflicto real de asignaciones y estados donde C y M producen lo mismo.
6. Latencia cero como límite mecánico vs rangos explícitos hipotéticos; coste de recursos y latencia por separado.
7. S opcional frente a T; R no se incluirá sin especificar estimador de llegadas, horizonte de reserva, incertidumbre, coste y control sin reserva.

Contrastes primarios y multiplicidad deben preespecificarse en A4. SLA terminal por admitidas, calidad simulada, tardías/pendientes, tiempos, backlog y costes no se colapsan en una recompensa ponderada como única evidencia.

## 9. Alternativas descartadas o diferidas

- **A completo sin C:** no permite separar el efecto de información central del matching; M queda causalmente confundida frente a reglas locales.
- **B completo con R en el núcleo actual:** reserva intertemporal es científicamente interesante, pero no existe predictor/demanda por clase validado ni coste de ociosidad; una regla inventada sería difícil de justificar y ampliar el alcance.
- **L como única regla local:** combina urgencia y competencia y oculta qué mecanismo cambia resultados. Mantener T/Q como controles principales y L como ablación de interacción si se aprueba.
- **P3/S como “reserva”:** es una prioridad por elegibilidad disponible ahora, no una protección de capacidad para demanda futura.
- **P4/M frente solo a D1:** mezcla criterio temporal, visión global y matching; no identifica el mecanismo conjunto.
- **P5 selectiva actual:** activa por un proxy lexicográfico, no por beneficio neto; coste de recursos no gobierna la elección.
- **Despacho diferido/batching por conveniencia estadística:** no introducir para crear más matching sin evidencia y coste de espera.
- **Reasignación/anticipación perfecta/RL:** exceden la pregunta acotada y requieren información/decisiones no validadas.

## 10. Riesgos y decisiones pendientes

Riesgos: baja frecuencia de estados con oportunidad M; costos/latencias hipotéticos; servicio y competencia sintéticos; regla de C no corresponde a proceso GMV confirmado; calidad modelada no es exactitud real; la esperanza de frecuencia de empates depende de generador y event semantics; múltiples contrastes y selección post hoc; las métricas de A1/otros motores no son intercambiables.

Se solicita al PI decidir antes de A3:

1. Si adopta como núcleo provisional D1/T/Q/C/M, con S opcional y R fuera de campaña confirmatoria.
2. Regla de precedencia C/M: recomendación aquí es objetivo temporal común, dejando competencia en Q para evitar mezcla.
3. Si la centralización informativa C es un mecanismo de interés sustantivo o control causal necesario para M; se recomienda incluirla por ambas razones.
4. Si se permite selección de orden reproducible común como control analítico, preservando D1 original como referencia no modificada.
5. Si latencia/coste solo se tratarán como sensibilidades hipotéticas, al no existir escala operacional validada.
6. Qué frecuencia de oportunidades y qué diferencia C–M justificarían pasar a campaña principal; no fijar umbral tras ver resultados.

**Recomendación:** cartera híbrida D1 + T + Q + C + M; S como opcional exploratorio; diferir R, despacho diferido y coordinación selectiva. Es una recomendación razonada, no aprobación de A2, prueba de superioridad ni afirmación sobre procedimientos reales de GMV-CERT.
