# Revisión científica del diseño de políticas SOC

**Propósito:** auditar D1/P1–P5 y delimitar un conjunto evaluable; no implementar ni elegir una política ganadora.
**Base:** código local de research/soc-human-ai-organization en a0fdc87834b56884ec1200778d4fe2b7cbfd4699, más cambios A1 no comprometidos.
**Estado:** revisión conceptual; la selección requiere decisión del PI.

## 1. Resumen de la auditoría

El motor ejecuta un despacho inmediato por época de evento. D1 y P1–P3 eligen alertas mediante reglas locales secuenciales; P4 resuelve el estado actual mediante matching global y P5 decide entre P3 y P4 con un criterio previsto de SLA/cardinalidad. Las políticas no son un factorial limpio: cambian a la vez orden de analistas, prioridad de alertas, información compartida, asignación conjunta y coste.

La ausencia de matching factible de cardinalidad ≥2 en los 170.263 estados de A1 es un resultado observado para esa muestra. No es por sí sola una demostración de imposibilidad del motor. Una propiedad de grafo estrella sí se demuestra bajo supuestos adicionales (despacho exhaustivo y actualización de un solo lado del grafo entre épocas). El motor agrupa eventos simultáneos, por lo que puede incorporar varios alertas, varios analistas liberados o ambos a la vez. Una prueba nueva reproduce un estado de matching 2 bajo llegadas y finalizaciones simultáneas.

La atribución de los grandes beneficios de P4 bajo estrés a “coordinación” no está identificada: cuando solo hay un analista libre, el matching se reduce a escoger una alerta, y P4 usa una prioridad temporal distinta de P1/D1. P5 tampoco es una decisión neta de coste: sus costes no entran en la regla que activa coordinación.

## 2. Reglas efectivamente implementadas

Las reglas están en src/hls/rq1_allocation.py: simulate, AllocationSession.dispatch, _dispatch_d1, _dispatch_soc_policy, _dispatch_local_priority, _dispatch_local_competence, _dispatch_local_capacity y _dispatch_coordinated. El servicio por analista/clase se consulta mediante service_time/_service_time; elegibilidad es task_class in analyst.eligible_classes.

| Política | Regla exacta y observación | Mecanismo que sí implementa | Límite interpretativo |
|---|---|---|---|
| **D1** | Baraja reproduciblemente analistas libres en cada época. En ese orden, cada uno elige entre alertas pendientes elegibles minimizando la clave (-riesgo, -competencia propia, elegibles de pares, deadline, llegada, ID), con rᵢₐ(t)=clip((sᵢₐ−(dₐ−t))/sᵢₐ,0,1). Elige y retira inmediatamente una alerta antes del siguiente analista. | Referencia descentralizada secuencial dentro de la abstracción del motor. | El riesgo se satura en 1 para todo trabajo inviable; la competencia y disponibilidad de pares son conocidas por el simulador. No está validado como procedimiento GMV. Mantener congelada. |
| **P1** | Analistas libres ordenados por ID. Cada uno elige alerta elegible con menor holgura post-servicio dₐ−t−sᵢₐ; desempate por deadline, llegada e ID. | Priorización local de holgura temporal continua. | El orden por ID puede afectar decisiones concurrentes; no usa competencia en el orden. Es distinto de D1, cuya urgencia es riesgo truncado y desempata con competencia. |
| **P2** | Mismo procesamiento secuencial por ID. El analista selecciona primero su competencia propia más alta; luego holgura, deadline, llegada e ID. | Preferencia local de adecuación analista-alerta. | No hace matching entre competencias de varios analistas. Competencia prioritaria puede sacrificar plazo. No cambia el tiempo de servicio. |
| **P3** | Analistas libres ordenados por ID. Para cada candidato cuenta cuántos pares aún no procesados son elegibles para su clase; minimiza ese número, luego maximiza competencia propia, y después minimiza holgura/deadline/llegada/ID. | Regla local-secuencial que intenta preservar alternativas de elegibilidad restantes. | No reserva explícitamente a un especialista, no compara sus competencias/velocidades con las de pares y no anticipa llegadas futuras. Sí requiere conocer estado/eligibilidad de compañeros, así que no es conocimiento estrictamente privado del analista. La cuenta es proxy de escasez, no coste de oportunidad validado. |
| **P4** | Matching uno-a-uno en el estado de despacho con coste lexicográfico: máximo número previsto a tiempo; luego máxima cardinalidad; después prioridad de deadline más próxima y desempate determinista por grafo. Usa duración individual y latencia en factibilidad. | Matching global de alertas pendientes con analistas libres en la época actual. | Si cardinalidad máxima es 1, solo escoge una alerta/pareja; entonces no prueba el valor del matching múltiple. Su prioridad difiere de P1 y D1. No planifica liberaciones ni llegadas futuras. |
| **P5** | Calcula P3 local y P4 global. Compara únicamente el par (número previsto a tiempo, número de asignaciones); usa P4 solo si mejora lexicográficamente, incorporando latencia al pronóstico. | Selectividad según mejora prevista de plazo/cardinalidad frente a P3. | No incorpora coste de recursos ni una utilidad neta; no activa por calidad/competencia si no mejora ese par. No es una regla de beneficio neto de coordinación. Combina diferencias de regla P3/P4. |

### Costes y horizonte

- P1–P3 no incorporan coste ni latencia de coordinación. D1 tampoco.
- P4 incurre latencia si el matching devuelve asignaciones, también cuando hay un solo analista libre. La latencia se aplica una vez por época; los analistas seleccionados quedan despachando/indisponibles hasta entonces. El consumo abstracto de recursos se calcula como coste por arista elegible.
- P5 solo paga latencia/coste si decide usar P4. Sin embargo, la decisión de activación ignora el coste por arista. En A1, cambiar el coste abstracto 0→1 solo cambió el contador, no las asignaciones.
- Todas las políticas usan únicamente el estado actual (cola, analistas libres, elegibilidad, competencia/tiempos disponibles según regla). Ninguna mira llegadas futuras. simulate_l1_l2 usa la misma política en ambos pools; deriva llegadas L2 de finalizaciones L1 y mide SLA terminal en L2 para alertas escaladas.

## 3. Auditoría estructural del evento y matching

### Ciclo de simulate

1. Se agrupan alertas admitidas por timestamp exacto (arrivals_by_time).
2. El siguiente evento es el mínimo entre llegada, finalización en servicio, inicio tras latencia, corte H y fin H+D.
3. En el instante, el motor incorpora todas las llegadas de ese timestamp, libera todos los servicios que finalizan y comienza todos los despachos cuya latencia terminó.
4. Captura métricas H antes de un despacho nuevo en H.
5. Construye una sola lista de analistas disponibles y, si hay cola, invoca una vez la política. Las reglas locales recorren analistas secuencialmente; P4/P5 calculan sus parejas en conjunto.
6. Retira cada alerta elegida de la cola inmediatamente y la pone en servicio o en estado de despacho con latencia. Comprueba duplicados/staleness antes de asignar.

AllocationSession.advance_to agrupa igualmente las llegadas y finalizaciones, y además aplica cambios de roster en el límite temporal. advance_to no despacha por sí sola; el caller decide cuándo llamar dispatch. El runner A1 registra estado después de advance_to(event) y antes de dispatch("D1"); las vistas P3/P4 se calculan sobre copias/lecturas del estado y no se asignan en la sesión.

### Alcance exacto del argumento de la estrella

Defínase G=(F,Q,E), con analistas libres F, tareas pendientes Q y arista elegible (i,a)∈E si el analista puede procesar la clase de la alerta.

- Para los selectores locales actuales, al terminar la pasada de todos los analistas libres no queda una pareja libre-alerta elegible: si un analista encontró alerta elegible, asignó una; si no encontró, las asignaciones posteriores solo retiran alertas y no pueden crear una arista nueva para él. La prueba también observa que P4 maximiza cardinalidad tras su prioridad primaria y P5 usa una de las dos reglas. La propiedad se refiere al grafo residual del estado inmediato; no dice que la asignación seleccionada sea óptima globalmente.
- Si entre épocas se actualiza solo un lado con exactamente un vértice nuevo (una llegada o un analista que se libera), y no hay cambios concurrentes del otro lado, el grafo previo al próximo despacho es una estrella o subgrafo de estrella, por lo que ν(G)≤1. Esta es una conclusión matemática condicional.
- El motor no impone esos supuestos. Agrupa todas las llegadas con timestamp igual y todas las finalizaciones simultáneas; también puede procesar ambos conjuntos en una misma época. Un lote de dos alertas más dos analistas liberados puede producir ν(G)=2. Los cambios de roster en AllocationSession pueden añadir varios analistas al pool a la vez. El replay de timestamps puede tener timestamps repetidos. Por tanto, no se demuestra imposibilidad estructural absoluta.
- Con llegadas Poisson continuas independientes, empates exactos de llegada son probabilidad cero en el modelo ideal. Las finalizaciones pueden empatar por servicios deterministas, asignaciones simultáneas o tiempos iguales; el replay conserva timestamps agrupados. La muestra A1 no observó matching de cardinalidad ≥2 en 170.263 estados, pero esa frecuencia es condicional al generador, roster, clases, H/D y políticas de despacho usadas.

### Verificación añadida

tests/test_soc_organization_policies.py incorpora dos pruebas de frontera: (i) una nueva alerta con varios analistas libres seguida de despacho inmediato deja cero aristas residuales; (ii) dos llegadas coincidentes con dos finalizaciones coincidentes producen dos analistas libres, dos alertas pendientes y P4 asigna dos tareas. No se cambió el motor ni la regla de ninguna política.

## 4. Mecanismos organizativos: alcance y cómo identificarlos

| Mecanismo | Justificación/condición | Información necesaria | Beneficio posible y perjuicio | Complejidad y evaluación |
|---|---|---|---|---|
| **A. Prioridad temporal** | Ordenar cola para reducir tardanzas cuando hay conflicto por capacidad. | Deadline, hora actual y servicio propio estimado. | Puede aumentar SLA a costa de dejar otras tareas en cola; efecto pequeño con holgura/efecto techo. | Baja. P1 permite contraste, aunque la regla debe distinguir menor holgura post-servicio de EDF por deadline bruto. Medir SLA terminal, retraso y espera. |
| **B. Asignación según competencia** | Adecuar analista y tipo cuando competencia difiere en una clase elegible. | Competencia analista-clase; validación de que el proxy predice calidad. | Puede mejorar calidad modelada; puede posponer tareas urgentes o asignar más lentamente si las velocidades difieren. | Baja-media. P2 usa solo competencia propia y no decide el matching analista-alerta. Calidad actual hipotética. Reportar SLA/calidad por separado. |
| **C. Preservación de especialistas** | Evitar consumir al único analista elegible para una clase mientras otro analista puede tratar una tarea compartida. Aplicable si hay elegibilidad solapada y cola concurrente por varias clases. | Elegibilidad y libres actuales; no hace falta conocer competencia exacta. | Puede aumentar cobertura de cola; también puede dejar recursos ociosos, posponer urgencias o no ayudar si no llega trabajo futuro de la especialidad. | Media. P3 es proxy greedy; cuantificar casos de bloqueo potencial y resultados de episodio; no declarar beneficio futuro que el horizonte no observa. |
| **D. Información global** | Una vista común de libres/cola puede reducir decisiones inconsistentes incluso al emitir una sola asignación. | Cola, disponibilidad, elegibilidad y posiblemente skills/services. | Puede elegir mejor una única pareja; centralización introduce latencia/coste informacional. | Media-alta. Separar política informada de decisión conjunta, con misma función objetivo y un analista libre como control. |
| **E. Matching conjunto** | Resolver asignación uno-a-uno cuando existen ≥2 analistas y ≥2 tareas elegibles simultáneamente y complementariedad. | Grafo completo elegible, servicio/deadline de cada pareja, skills si objetivo las incluye. | Puede preservar completamientos alcanzables o calidad; puede retrasar tareas por latencia y no tiene valor si el estado solo permite una asignación. | Alta. Medir frecuencia de estados con ν(G)≥2 y efecto de asignación/episodio. Contrastar contra control central secuencial con la misma prioridad, además de D1. |
| **F. Coordinación selectiva** | Pagar coordinación solo si el beneficio previsto supera coste/latencia y coste de oportunidad. | Resultado previsto bajo alternativa local y coordinada; conversión de costes a unidades con significado. | Evita coordinación infructuosa; pronóstico equivocado o costes incompletos pueden activar mal. | Alta. P5 actual no lo realiza: ignora recurso/coste monetario y la regla es lexicográfica SLA/cardinalidad. Sin coste defendible, solo cabe ablación, no “net benefit”. |

Fundamento conceptual empleado: teoría de colas/capacidad, elegibilidad como grafo bipartito, matching máximo con pesos lexicográficos y reglas secuenciales tipo lista. No se añadieron citas bibliográficas. Si el artículo atribuye afirmaciones a literatura sobre despacho por lotes, matching online o reserva, las referencias deben verificarse bibliográficamente antes de incluirse.

## 5. Recomendación de repertorio para aprobación

### Núcleo reducido recomendado

1. **D1 — congelada:** baseline principal. No renombrar ni ajustar.
2. **P1 — local temporal:** conservar como control de prioridad. Su prioridad es holgura post-servicio, no EDF bruto.
3. **P2 — local por competencia:** conservar solo si la calidad modelada es una métrica científica explícita y se identifica como hipotética. Sirve para aislar “preferir competencia propia”, no para probar matching por competencias.
4. **P4 — matching del estado actual:** conservar como candidato condicional, no presentarlo como estrategia principal de coordinación hasta medir estados con ν(G)≥2 y controlar el cambio de prioridad individual.

**P3** queda como módulo/contraste secundario si el PI mantiene la hipótesis independiente de preservar especialistas. No debe confundirse con coordinación conjunta: es una regla greedy basada en elegibilidad de pares y competencia propia, y mezcla dos mecanismos.

### Control necesario para interpretar P4

Comparar P4 con un control de **selección central secuencial** que use la misma información, plazo previsto y desempates que P4, pero emita una pareja por vez sin optimizar la asignación completa. Evaluar además P4 en estados con un analista libre (ablation de asignación individual) y en estados con ν(G)≥2. Así se pueden separar: efecto de cambiar la prioridad de alerta, efecto de conocer el estado global y efecto incremental del matching. La definición concreta y el coste de esta referencia requieren aprobación antes de implementarla.

### P5 y alternativas descartadas

- **No recomendar P5 como política confirmatoria actual.** Es una envoltura de P3/P4 con criterio de activación estrecho (on-time y cardinalidad), no una optimización del beneficio neto. Sus resultados no aíslan la ventaja de coordinación ni incorporan coste de recurso a su elección.
- **No retirar P4 del repositorio en esta fase.** Sus pruebas muestran que puede resolver matching múltiple en un estado factible, y el motor no impide por construcción tales estados; la evidencia A1 sí limita su frecuencia en las trazas probadas.
- **No afirmar que P3 preserva capacidad futura de forma óptima.** Su mirada es solo al conjunto actualmente libre y pendiente; no reserva recurso, no espera y no anticipa llegadas.
- **No usar el resultado de alta mejora P4/P5 en 1,5 C × deadline 0,1 como evidencia causal de coordinación.** A1 observó cero estados de matching múltiple; la diferencia puede surgir de la regla de prioridad al quedar un solo analista libre.

## 6. Hipótesis contrastables y controles

- **H1, temporal:** P1 mejora SLA terminal frente a D1 cuando existe conflicto entre alertas elegibles; no debería diferenciarse en holgura alta.
- **H2, competencia propia:** P2 puede mejorar la medida de calidad modelada donde difiere competencia entre opciones del mismo analista; el efecto no valida una relación competencia-calidad real.
- **H3, escasez de elegibilidad:** P3 puede reducir bloqueos de cobertura cuando una clase tiene un único analista disponible; puede empeorar tardanza si elige una tarea menos urgente.
- **H4, matching:** P4 solo puede mostrar ventaja incremental de asignación conjunta en estados con ν(G)≥2; más concurrencia por sí sola no basta sin alternativas complementarias.
- **H5, coste:** latencia puede borrar un beneficio bruto; el coste de recursos no puede interpretarse hasta dotarlo de unidades/medición.

Controles metodológicos propuestos: mismas alertas, verdad simulada, equipo y servicios para todos; métricas terminales comunes H/H+D; análisis de estados emparejados; ablation de un analista libre frente a ν(G)≥2; latencia 0 como límite superior diagnóstico y valores no nulos declarados como hipótesis; separar coste de recursos de latencia. No ejecutar hasta aprobar el protocolo de Fase A.

## 7. Riesgos e incógnitas

- La demanda sintética Poisson produce interllegadas de CV≈1; los agregados SOCTRA documentados indican CV>1 y timestamps repetidos. Reutilizar esos agregados o trazas anonimizadas puede cambiar concurrencia y ráfagas, sin revelar trabajo real ni SLA.
- Roster, competencia, servicio, elegibilidad y deadline son supuestos. No hay calibración humana/operativa GMV. La plausibilidad del mecanismo no es validación externa.
- A1 reporta estados diagnosticados y resultados agregados; no se preservó en Git el CSV local de 21 MB. La receta y semillas sí están en config/a1_calibration.json, pero los resultados locales no están disponibles para un checkout limpio.
- P1/P2/P3 usan IDs ordenados; D1 usa orden aleatorio reproducible. Esto hace que diferencias puedan incluir orden de servicio, y el orden ID no está motivado por organización operativa.
- La definición de calidad usa competencias sintéticas, no adjudicación de incidentes. SLA es deadline terminal hipotético.
- Coordinación instantánea/coste por arista carece de escala empírica; la latencia de P4 se carga incluso con una decisión individual.

**Decisión pendiente del PI:** aprobar núcleo (D1/P1/P2/P4 y estatus de P3), control secuencial emparejado para P4, si se permite aprovechar lotes simultáneos que ya existan en timestamps o introducir un intervalo de despacho con justificación organizativa, y qué datos de operación pueden sustentar costes/latencias. No se debe alterar el motor antes de esa decisión.
