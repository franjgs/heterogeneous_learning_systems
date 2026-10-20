# HLS Laboratory — Plan operativo y registro de decisiones (17–30 octubre 2026)

**Estado:** plan de trabajo vigente e incorporado al repositorio en la revisión documental del 17-10-2026. **Rama:** `feature/hls-laboratory-v1`. **Autoridad:** planificación operativa; no sustituye `docs/HLS_CURRENT_STATE.md`, `docs/HISTORY.md`, la ontología ni los protocolos congelados.

## 1. Reglas de gestión

- Construir y validar componentes HLS; no exigir reproducción íntegra de artículos para reutilizar mecanismos delimitados.
- No evaluar novedad o publicabilidad en esta fase, por decisión del PI.
- Mantener separados competencia, productividad, exposición, esfuerzo, output, presupuesto y observaciones; declarar adaptaciones.
- No modificar resultados históricos ni artefactos congelados. PDF científicos solo locales.
- Distinguir tests focalizados de suite completa y experimentos científicos.
- **Todo cambio de fechas, prioridades, alcance o criterios se registra en este documento en el mismo commit que lo oficializa**, sin borrar el plan anterior.
- Las campañas experimentales requieren autorización específica; el calendario no la concede.
- **Regla permanente de publicación:** “Toda modificación relevante del alcance, arquitectura, prioridades, calendario o decisiones científicas deberá registrarse en el repositorio antes de continuar con el siguiente trabajo. Cada entrega deberá incluir la documentación correspondiente, validación, commit y push. Los cambios no publicados no se considerarán incorporados al estado oficial del proyecto. No se crearán fases o subfases adicionales salvo necesidad técnica expresamente justificada.”

## 2. Calendario original (línea base, no borrar)

| Fecha | Trabajo previsto inicialmente |
|---|---|
| 19 oct. | Auditoría de la memoria científica HLS |
| 20 oct. | Selección inicial de 6–10 artículos |
| 21 oct. | Priorización de 3–4 investigaciones |
| 22 oct. | Análisis matemático de los modelos |
| 23 oct. | Ontología HLS v0.1 y revisión semanal |
| 26 oct. | Matriz de reutilización del laboratorio |
| 27 oct. | Reproducibilidad y comparabilidad |
| 28 oct. | Memoria de novedad científica |
| 29 oct. | Diseño experimental preliminar |
| 30 oct. | Informe final y decisión GO / REFRAME / STOP |

## 3. Hoja de ruta de mecanismos — estado comunicado por Codex el 17 oct.

| Prioridad | Actividad | Estado | Evidencia y límite |
|---|---|---|---|
| 1 | Evaluador independiente Nembhard Direct | COMPLETADO | Commits `2e65926`, `f345535` |
| 2 | Tests matemáticos y regresión | COMPLETADO (focalizados) | 24 tests del mecanismo + 184 regresiones N×K comunicados |
| 3 | Adaptador experimental Nembhard–HLS | COMPLETADO (acotado) | Commits `be4d1a0`, `f73e688`; 222 tests focalizados; sin campañas |
| 4 | Transferencia indirecta Nembhard | APLAZADO | Fuera de integración actual |
| 5 | Reproducción completa del artículo | APLAZADO / FUERA DE ALCANCE | No necesaria para adaptación acotada |
| 6 | Router ORACLE Nembhard Direct, como baseline intermedio | COMPLETADO | `router_id="nembhard_oracle"`; información perfecta de experiencia/productividad, ranking funcional P0 actual, tests N×K; no es un router aprendido ni reproducción de MixLLM |
| 7 | Router Nembhard basado en estimaciones | COMPLETADO (entrega integrada única; 2026-10-17) | `nembhard_adaptive`; observación individual configurable, estimador online, epsilon-greedy reproducible y runner N×K; 48 tests Nembhard y 180 tests N×K focalizados; suite 1,458 passed / 5 fallos históricos conocidos |
| 8 | Ejecutor y análisis del protocolo Nembhard revisado | IMPLEMENTADO; validación focalizada; campaña NO EJECUTADA | `src/hls/nembhard_campaign.py`; 1.016 configuraciones únicas, FIXED explícito y reutilización ORACLE/ADAPTIVE; métricas y contrastes del protocolo. Ejecución pendiente de autorización PI/CE. |

**Estado del laboratorio: PARTIAL.** La integración Nembhard usa `mechanism_id="nembhard_direct"`, experiencia `D[N,K]` y parámetros `k,p,r` separados de competencia; productividad al inicio del periodo, output `Σ_i e[i,k]P[i,k](D)Δt`, después incremento de experiencia `eΔt`. Contrato explícito de unidades. Presupuestos limitan intensidad `e` por periodo. Soporta asignaciones explícitas factibles y demanda del entorno. Desde el 17-10-2026 dispone de `nembhard_oracle`, que enumera acciones factibles y aplica el ranking funcional P0 con información perfecta, y `nembhard_adaptive`, que observa output individual, mantiene estimaciones online y selecciona usando esos valores con exploración epsilon-greedy opcional. Ambos usan la producción Nembhard verdadera y el catálogo compartido; el primero conoce perfil/experiencia verdaderos, mientras el segundo no accede al perfil/productividad verdaderos en su vista de decisión. Ninguno valora aprendizaje futuro. Nembhard sigue sin admitir P0/P1/P2 históricos, MIS-v2, enseñanza, transferencia o estimación de competencias. MIS-v2 permanece predeterminado. Router adaptativo: 48 tests Nembhard y 180 tests N×K focalizados; suite completa 1,458 passed/5 fallos de integridad conocidos; no hubo campaña científica. Se conservaron cambios locales ajenos.

## 4. Calendario reajustado (objetivos, no resultados)

| Fecha | Trabajo principal | Entregable o criterio de cierre | Estado |
|---|---|---|---|
| 17 oct. | Integración Nembhard–HLS y formalización del plan | Adaptador y pruebas; registro de decisiones | Integración COMPLETADA (222 tests focalizados); plan incorporado en esta revisión documental |
| 17 oct. | Router Nembhard ORACLE intermedio | Selección determinista de asignaciones con productividad verdadera; tests N×K | COMPLETADO (166 tests focalizados combinados); no estima ni aprende |
| 19 oct. | Revisión de integración y contrato de comparación | Nota de observables comunes, límites de comparación y tests | PREVISTO |
| 20 oct. | Modelo de información para decisión | Definir estado conocido/estimado, productividad, costes y política base | PREVISTO; además, HLS-P1 y su ablación causal se completaron el 20 oct. (§5, cierre P1) |
| 21 oct. | Análisis de componentes MixLLM | Mapa de predicción, routing, feedback y límites de reutilización | PREVISTO |
| 22 oct. | Diseño del router Nembhard basado en estimaciones | Se conserva como antecedente del calendario; consolidado en entrega única del 17 oct. | ABSORBIDO; no es hito independiente |
| 23 oct. | Implementación inicial del router basado en estimaciones, si está preparado; revisión semanal | Se conserva como antecedente del calendario; consolidado en entrega única del 17 oct. | ABSORBIDO; no es hito independiente |
| 26 oct. | Identificar un problema práctico relevante y soportado por literatura | Especificar su descomposición A/B/C, soporte HLS existente, brechas, comparadores y una hipótesis falsable | PROGRAMADO; pendiente. Usar P1 como evidencia de evaluación finita exacta, baseline fijo optimizado, comparaciones reactiva/anticipatoria, ablación de desarrollo, métricas funcionales y análisis Bellman; P1 no es validación práctica |
| 27 oct. | Definir reproducibilidad y comparación justa para el problema seleccionado | Condiciones iniciales, trayectorias exógenas, información, recursos, aleatoriedad, métricas y evidencia requerida | PROGRAMADO; pendiente. Los artefactos P1 son material de evaluación, no cierre del hito |
| 28 oct. | Consolidación ontológica y arquitectónica | Referencia conceptual: `docs/architecture/HLS_ONTOLOGY_V0_1_2026-10-23.md`; contrastar con el problema de 26 oct. solo donde sea necesario | ENLACE DOCUMENTAL; no se declara integración o validación experimental |
| 29 oct. | Preparar un protocolo experimental acotado para el problema seleccionado | Escenario, comparadores, hipótesis, métricas, controles y criterios de parada; pedir autorización antes de ejecutar | PENDIENTE; diseño solamente |
| 30 oct. | Cierre y decisión de la ventana de trabajo | Evaluar evidencia disponible y decidir GO / REFRAME / STOP; conservar el límite de cierre del plan | PENDIENTE |

El objetivo inicialmente previsto para el 19–20 oct. (adaptador Nembhard) se adelantó al 17 oct. La etapa de router ORACLE se completó como baseline intermedio. La decisión registrada el 17 oct. consolida estimación y routing basado en observaciones en una única entrega implementable, sin diseño/implementación como subfases; queda completada en el alcance acotado descrito abajo. El protocolo Nembhard y su revisión ya se tradujeron a un ejecutor y análisis deterministas; su preparación no autoriza la campaña.

**Interpretación operativa aprobada el 19-10-2026:** las actividades de 26, 27, 29 y 30 se interpretan según la decisión de marco científico añadida al registro acumulativo (§5 y §6). Esto actualiza la ejecución restante, no la línea base original de §2. La literatura se usará para identificar problemas y condiciones operativas relevantes, no para imponer la reproducción de un algoritmo por defecto. El cierre del 30 de octubre se conserva.

## 5. Registro de decisiones (acumulativo)

| Fecha | Cambio respecto del plan previo | Motivo | Consecuencia |
|---|---|---|---|
| 17-10-2026 | Pasar de calendario secuencial de lectura a construcción y validación incremental | Auditoría, extracción e infraestructura avanzaron antes de las fechas previstas | Mantener línea base; adelantar integraciones |
| 17-10-2026 | No exigir réplica completa de Nembhard | Se prioriza reutilizar mecanismos acotados con convenciones explícitas | Curva directa y adaptador; transferencia y réplica completa aplazadas |
| 17-10-2026 | Retirar evaluación de novedad/publicabilidad del calendario operativo | Instrucción expresa del PI | Sustituir hito del 28 oct. por consolidación de arquitectura y ontología |
| 17-10-2026 | Dar por terminada la integración Nembhard acotada según informe Codex | Commits `be4d1a0`, `f73e688` y 222 tests focalizados | Priorizar contrato de comparación y router; no confundir integración con política automática |
| 17-10-2026 | Revisar el calendario y publicar este plan con su registro acumulativo de decisiones | Hacer explícitos los cambios de calendario y conservar la línea base sin sustituirla | El registro y las tablas se mantienen versionados; el router adaptativo permanece como siguiente objetivo y las campañas siguen requiriendo autorización específica |
| 17-10-2026 | Cambiar el hito inmediato previamente denominado «router adaptativo inspirado en MixLLM» por un baseline Nembhard ORACLE; conservar como objetivo posterior el router basado en estimaciones | Validar selección, catálogo y ranking con estado verdadero de productividad antes de añadir inferencia, sin presentar el ORACLE como aprendido ni como reproducción de MixLLM | `nembhard_oracle` queda disponible como baseline determinista de decisión actual; el siguiente diseño debe estimar productividad desde observaciones, sin equipararla a competencia HLS |
| 17-10-2026 | Consolidar el objetivo previamente pendiente de estimación y routing en una sola entrega integrada, en vez de diseño e implementación como hitos separados | La ruta completa Observe → Estimate → Decide → Produce → Learn puede especificarse y validarse en el componente Nembhard existente; dividirla añadiría hitos sin necesidad técnica | `nembhard_adaptive` implementado con observación individual, estimación online, exploración epsilon-greedy opcional y trazas. La evidencia/limitaciones se registran en `engineering/HLS_NEMBHARD_ADAPTIVE_ROUTER.md`; no se crean subfases ni se autorizan campañas. HLS permanece PARTIAL |
| 17-10-2026 | No autorizar campañas por el mero hecho de estar en el calendario | Aún no hay protocolo aprobado para nueva campaña | 29 oct. queda en diseño; ejecución requiere permiso |
| 17-10-2026 | Registrar toda modificación del plan en archivo versionado | Evitar pérdida de decisiones entre chats y agentes | Actualizar tablas y registro, hacer commit y push identificables |
| 17-10-2026 | Seleccionar como máximo un siguiente mecanismo de entre MixLLM, System-1.x y Baccara, sin alterar el calendario vigente | Tras completarse `nembhard_adaptive`, la comparación conjunta favorece una extensión contextual del routing, cuyo seam de decisión y trazabilidad ya existe; las otras opciones requieren estados centrales ausentes | Se recomienda un predictor contextual de calidad/coste por candidato actualizado con feedback del candidato seleccionado, inspirado en componentes de MixLLM y condicionado a un contrato de datos/unidades. System-1.x se difiere por falta de planes/subobjetivos verificables; Baccara por falta de llegadas, colas y capacidad de servicio. No es implementación, no añade fechas ni autoriza campañas; evidencia en `engineering/HLS_NEXT_MECHANISMS_SELECTION_2026-10-17.md` |
| 17-10-2026 | Fijar el contrato técnico de la adaptación MixLLM-inspired seleccionada, sin alterar el calendario | La selección necesitaba determinar unidades, predicción contextual, feedback parcial, objetivo y fallback antes de cualquier implementación; HLS no debe confundir calidad/coste con CES, competencia o esfuerzo | Contrato v0.1 documentado en `engineering/HLS_MIXLLM_ROUTER_CONTRACT.md`: calidad [0,1], coste monetario por consulta en una moneda/versionado, regresión ridge contextual separada para calidad/coste, actualización solo con outcomes observados y selector de coste mínimo sujeto a objetivo de calidad con fallback explícito. Supuestos: contexto/candidatos exógenos, evaluator/ledger versionados y priors declarados. Pendiente por instancia: dataset/schema, moneda/medición, priors y si el presupuesto debe ser hard; especificación, no implementación. No se cambian fechas ni se autoriza campaña. |
| 17-10-2026 | Implementar el contrato contextual MixLLM-inspired como capacidad sintética independiente, sin alterar el calendario | Validar de extremo a extremo predicción contextual, selección, ejecución seleccionada y actualización desde feedback observado en un entorno determinista controlable | Implementados `src/hls/contextual_router.py` y `contextual_router_synthetic.py`, con 17 tests focalizados, incluyendo el ejemplo manual del contrato y replay en procesos nuevos. La instancia declara calidad en [0,1] y coste monetario simulado por consulta; priors, transformaciones, evaluator y ledger reales siguen requiriendo decisión por dominio. Regresiones N×K: 162 pasaron; suite completa: 1,476 pasaron y 5 fallos históricos de procedencia/integridad. No es reproducción de MixLLM, no integra agentes N×K, no ejecuta campaña y no altera rutas MIS-v2/Nembhard/P0/P1/P2. Detalle: `engineering/HLS_MIXLLM_ROUTER_IMPLEMENTATION.md`; HLS permanece PARTIAL. |
| 17-10-2026 | Consolidar la arquitectura documental a partir de las capacidades implementadas, sin cambiar calendario ni mecanismos | La incorporación del router contextual creó una ruta ejecutable independiente; el mapa debe distinguirla de N×K y Nembhard para impedir equivalencias o integraciones implícitas | `engineering/HLS_LAB_ARCHITECTURE_2026-10-17.md` registra contratos verificados, límites ontológicos y comparaciones defendibles. No crea mecanismos, fases ni campañas; HLS permanece PARTIAL. |
| 17-10-2026 | Añadir un contrato común de ejecución/trazas como adaptador no destructivo, sin unificar simuladores ni métricas | Tres rutas ya devuelven resultados y serializadores distintos; se necesita una forma versionada de archivar e inspeccionar ejecuciones sin cambiar sus ecuaciones, interfaces nativas o unidades | `src/hls/experiment_contract.py` adapta resultados MIS-v2/N×K, Nembhard y routing contextual a `hls-experiment-run/1.0`, con eventos, unidades, métricas separadas, procedencia explícita y JSON estable. 11 tests nuevos y 184 tests focalizados combinados pasaron; serializadores nativos permanecen intactos. No crea un runner común ni comparabilidad científica; HLS permanece PARTIAL. Especificación en `engineering/HLS_COMMON_EXPERIMENT_CONTRACT.md`. |
| 17-10-2026 | Detener temporalmente la incorporación de mecanismos e infraestructura y priorizar el diseño de un protocolo Nembhard sobre asignación adaptativa | Las rutas actuales ya permiten definir una comparación controlada entre asignación fija, `nembhard_oracle` y `nembhard_adaptive`; antes de ampliar el laboratorio se requiere concretar la pregunta, controles y resultados observables | Siguiente objetivo autorizado: diseñar el protocolo para estudiar cuándo una política de asignación adaptativa supera a una asignación fija con capacidades complementarias y productividad dependiente de experiencia. Mantener constantes y registrar condiciones iniciales, demandas, recursos, horizonte, información, observación y aleatoriedad; considerar producción/éxito, esfuerzo, productividad, experiencia y rendimiento acumulado, incluyendo información perfecta/imperfecta. No se afirma superioridad: ORACLE solo rankea el resultado inmediato. Solo diseño autorizado; no ejecutar campaña, no comparar rutas distintas, no adoptar mecanismos System-1.x/Baccara. Se conservan las fechas del calendario como estaban; HLS permanece PARTIAL. |
| 17-10-2026 | Completar la redacción documental del primer protocolo exploratorio Nembhard, conforme a la prioridad vigente y sin modificar fechas | Hacer implementable la comparación fija/ORACLE/ADAPTIVE con perfiles, demandas emparejadas, presupuesto, semillas, información, métricas y límites declarados | El borrador inicial en `docs/experiments/HLS_NEMBHARD_ADAPTIVE_ALLOCATION_PROTOCOL.md` definió 3×2 perfiles/productividad, dos escalas de experiencia, dos ordenamientos de idéntica colección de problemas, dos niveles de ruido ADAPTIVE, 20 bloques exploratorios y controles acotados; propuso 1,018 ejecuciones contando diagnósticos. Entrega documental, no registro confirmatorio congelado ni autorización de campaña. La revisión metodológica siguiente reduce las ejecuciones únicas a 1,016. No se cambió calendario ni estado de capacidad; System-1.x/Baccara siguen diferidos y HLS permanece PARTIAL. |
| 17-10-2026 | Revisión metodológica crítica del protocolo Nembhard publicado en `62a08df` | Reconstruir carga de ejecución, validar comparaciones frente al código y comprobar que H1–H4 tienen estimandos operativos | Decisión **ADJUST** en `experiments/HLS_NEMBHARD_PROTOCOL_REVIEW.md`: reutilizar dos casos identidad duplicados para reducir 1,018 ejecuciones propuestas a 1,016; corregir la descripción verificable de los flujos gaussianos; predefinir diferencias-en-diferencias H1–H3; especificar serialización canónica del hash de demanda. Estas correcciones documentales se incorporan en el mismo commit de revisión; el protocolo es técnicamente viable sin cambios científicos, pero requiere revisión PI/CE y autorización PI/CE separada antes de ejecutar. No se modifica el calendario ni HLS PARTIAL. |
| 17-10-2026 | Implementar el ejecutor y análisis del protocolo Nembhard revisado, sin ejecutar la campaña | Convertir el protocolo revisado en configuraciones deterministas, secuencias explícitas, rutas de política existentes, resultados versionados y contrastes predeclarados | `src/hls/nembhard_campaign.py` genera y valida 1.016 configuraciones únicas (960 factoriales, 40 epsilon-cero y 16 diagnósticos únicos), adapta resultados al contrato común y calcula métricas/contrastes incluyendo H1–H3. FIXED reutiliza la tabla estática protocolizada; ORACLE/ADAPTIVE son las rutas existentes. Los tests usan secuencias sintéticas de hasta 3 periodos; la campaña NO se ejecutó. Validación focalizada: 65 tests combinados; suite completa: 1.503 pasaron y los mismos 5 fallos históricos de inventario/procedencia. `run --all` sin token de confirmación se verificó como rechazado sin ejecución. Ejecución científica requiere autorización PI/CE. No cambia el calendario; HLS permanece PARTIAL. |
| 17-10-2026 | Corregir la interrupción de HLS-E1 y permitir reanudación segura sin alterar el diseño | El estimador podía producir un M2 diminuto negativo en la primera observación al tratar un prior con count=0 mediante la fórmula aritmética de Welford; los resultados parciales deben poder auditarse y continuarse sin sobrescritura | La primera observación ahora establece exactamente media observada/count=1/M2=0; actualizaciones posteriores toleran solo negativos dentro de un límite de ocho ULPs y rechazan no finitos/negativos materiales. Añadidos `status` y `resume` explícito: exige resultados previos válidos, comprueba los tres JSON, demanda y trazas, y ejecuta solo IDs ausentes; `run --all` no cambia. Auditoría local: 29 completos válidos, 0 incompletos/corruptos, 987 pendientes; ejecución iniciada e interrumpida, campaña NO COMPLETADA ni interpretada. Validación focalizada: 74; suite completa: 1.512 aprobados y los mismos cinco fallos históricos de inventario/proveniencia. No se altera el calendario ni HLS PARTIAL. |
| 17-10-2026 (trabajo previsto para la sesión del 18-10-2026) | Dar por completada, dentro de su alcance documentado, la validación integrada de capacidades adaptativas existentes y priorizar la preparación de una reproducción controlada de literatura | La validación S0–S4 ya publicada demuestra ejecución reproducible de mecanismos existentes; no hace falta desarrollar nuevas capacidades adaptativas antes del trabajo de reproducción | El 18 oct. se revisarán fuentes primarias y experimentos reproducibles, se compararán candidatos con HLS, se seleccionará uno, se preparará una matriz de correspondencia y un protocolo acotado, y se solicitará autorización antes de ejecutar. No seleccionar Nembhard por defecto, no repetir auditorías ya completadas, no reconstruir mecanismos existentes ni ejecutar campañas. La validación no implica superioridad de políticas ni reproducción completa de artículos. HLS permanece PARTIAL. Evidencia: `docs/experiments/HLS_LAB_ADAPTIVE_CAPABILITY_VALIDATION.md`, `results/analysis/hls_lab_validation/integrated_validation_results.json` y `results/analysis/hls_lab_validation/capability_registry.json`; 135 tests focalizados pasaron y la suite completa no se ejecutó en esa validación. |
| 19-10-2026 (reanudación del trabajo previsto para el 18-10-2026) | Revisar fuentes primarias, seleccionar un experimento y preparar un protocolo acotado, sin ejecutar | Se consultaron los artículos originales registrados y se contrastaron contra las rutas implementadas y su evidencia validada. El ajuste conceptual no equivale a fidelidad matemática/experimental | Informe `docs/experiments/HLS_LITERATURE_REPRODUCTION_SELECTION_2026-10-19.md`. MixLLM §4.3/Table 1 queda como el candidato más próximo por interfaz, pero el router HLS usa otro predictor, objetivo, datos y feedback; faltan artefactos primarios críticos. Decisión **STOP**: no hay candidato autorizado/preparado para reproducción exacta o defendiblemente aproximada con las capacidades e insumos actuales. No se ejecutó experimento ni se implementó nada. La decisión no cancela la prioridad de reproducibilidad: antes de GO se deben resolver las dependencias o elegir otro experimento con correspondencia suficiente. HLS permanece PARTIAL. |
| 19-10-2026 | Aprobar el marco científico/conceptual de tres niveles: problemas, mecanismos y organizaciones | Explicitar qué se estudia, qué dinámicas operan y cómo se coordinan, sin convertir la ontología en una arquitectura de software ni exigir superioridad universal de HLS | Se registra la pregunta central sobre organizar, desarrollar y coordinar capacidades heterogéneas bajo demanda cambiante y recursos limitados; orientar 26–30 oct. a un problema práctico, comparabilidad y protocolo acotado. Es dirección conceptual aprobada, no capacidad implementada/validada ni autorización de campaña. Detalle y trazabilidad en §6. |

## 6. Procedimiento obligatorio para cambios futuros

### Prioridad de sesión registrada el 17 de octubre — domingo 18 de octubre de 2026

**Estado actualizado el 19-10-2026:** el trabajo se reanudó el lunes 19; véase
“Registro de reanudación y resultado” más abajo. La prioridad original y el
calendario de la sección 2 se conservan como registro histórico.

La validación integrada de capacidades adaptativas existentes se considera
completada en el alcance de la evidencia publicada. La siguiente sesión se
dedicará a seleccionar y diseñar una reproducción controlada de un único
experimento de literatura: revisar artículos originales disponibles,
identificar protocolos cuantitativos reproducibles, comparar su ajuste a
componentes HLS existentes, elegir un candidato con justificación, preparar
una matriz modelo–escenario–políticas–implementación–métricas y redactar un
protocolo acotado para revisión PI/CE. La ejecución requiere autorización
posterior explícita. No se selecciona Nembhard de antemano ni se repiten las
auditorías ya publicadas. Se conserva el calendario original de la sección 2;
esta es una prioridad de sesión registrada, no una reescritura del calendario.

1. Identificar fecha/objetivo anterior, nuevo objetivo, razón y dependencias afectadas.
2. Modificar tablas de estado y calendario **sin borrar la línea base**, y añadir entrada fechada al registro.
3. Vincular documentación, tests y commits; distinguir evidencia verificada de informe de un agente.
4. Publicar la modificación en `feature/hls-laboratory-v1`, preservando cambios locales ajenos.
5. Comunicar SHA, estado de push y asuntos pendientes. No declarar una actividad completada sin evidencia.

Esta regla se aplica a cada entrega: registrar antes de continuar, documentar y validar, y publicar mediante commit y push. Un cambio sin publicar no forma parte del estado oficial. No se añadirán fases/subfases salvo necesidad técnica justificada y registrada.

### Registro de reanudación y resultado — lunes 19 de octubre de 2026

El trabajo documental previsto para el domingo 18 se reanudó el lunes 19,
conservando la prioridad y el calendario original. Se revisaron las fuentes
primarias disponibles de Nembhard–Bentefouet, Borgonjon–Maenhout,
Baccara–Lee–Yariv, MixLLM, System-1.x y Liu et al., y se confrontaron sus
experimentos con el código y las pruebas HLS. La selección no produjo un
protocolo ejecutable fiel: MixLLM Table 1 es el candidato más cercano en el
nivel abstracto de routing, pero faltan datos/modelos/runtime de origen y sus
componentes no corresponden al router contextual HLS. Por ello se registra
**STOP antes de ejecución** en el informe de selección. Esto no es un rechazo
de futuras reproducciones ni autorización para construir sustitutos; el
siguiente paso deberá resolver dependencias primarias o seleccionar otra
fuente y pedir autorización PI antes de cualquier ejecución. Véase
[`HLS_LITERATURE_REPRODUCTION_SELECTION_2026-10-19.md`](../experiments/HLS_LITERATURE_REPRODUCTION_SELECTION_2026-10-19.md).

### Decisión científica y conceptual aprobada por PI — 19 de octubre de 2026

**Fecha:** 2026-10-19. **Autoridad:** PI. **Estado:** APROBADA.
**Tipo:** marco científico y conceptual. Esta entrada se añade después de las
decisiones y resultados anteriores; no altera retroactivamente la línea base
del 17 de octubre ni reescribe los informes históricos.

#### Marco de tres niveles

La investigación HLS distinguirá tres niveles conceptuales. No constituyen
una arquitectura de software ni mandatan una refactorización del simulador.

**Nivel A — Problemas.** Define el problema práctico y el entorno: tareas y
demanda, capacidades requeridas, dinámica ambiental, recursos y restricciones,
costes y objetivos, información disponible y oportunidades de aprendizaje y
cooperación. Las definiciones pueden originarse en modelos matemáticos,
escenarios prácticos publicados, datos reales o benchmarks. La literatura
debe ayudar a identificar problemas y condiciones operativas realistas, no
servir únicamente como catálogo de algoritmos que reproducir.

**Nivel B — Mecanismos.** Define capacidades de agentes y su evolución:
aprendizaje individual, transferencia de conocimiento, especialización,
productividad dependiente de experiencia, desarrollo de competencia,
estimación y actualización de creencias, exploración y cooperación, y
activación de capacidades dependiente de recursos. Un mecanismo puede ser
conocido individualmente; su interacción, integración y consecuencias siguen
siendo objetos de investigación.

**Nivel C — Organizaciones.** Define cómo se toman decisiones y cómo se
coordinan capacidades y recursos: organizaciones fijas optimizadas,
estrategias reactivas o modulares, organizaciones adaptativas, optimización
conjunta y estrategias con información o anticipación diferentes.

#### Motivación y principios experimentales

Pregunta central aprobada:

> ¿Cómo deben los sistemas de aprendizaje heterogéneos organizar, desarrollar
> y coordinar sus capacidades para maximizar el rendimiento ante demandas
> cambiantes y recursos limitados?

El laboratorio debe permitir estudiar dónde ayuda la adaptación organizativa,
bajo qué condiciones, por cuánto, mediante qué mecanismos y a qué coste
computacional, informativo, de coordinación y de recursos. También debe
identificar condiciones en que organizaciones más simples son suficientes o
preferibles. HLS no se define como una arquitectura que deba superar siempre
a sus alternativas.

Las comparaciones deberán distinguir: (A) ventaja práctica frente a
organizaciones fijas optimizadas; (B) ventaja de integración frente a
estrategias modulares fuertes; (C) interacción de aprendizaje, transferencia,
estimación y otros mecanismos; y (D) rendimiento frente a complejidad,
información, coordinación y recursos. Los baselines no se debilitarán
artificialmente y se preservarán resultados positivos, negativos y nulos.
Estos principios no anticipan el ganador ni autorizan experimentos.

#### Trazabilidad con evidencia y decisiones previas

- **ESTABLECIDO (alcances distintos):** G1 conserva referencias estáticas;
  G2 trata valor dinámico del desarrollo; G3/G3-H analizan valor
  organizativo, sensibilidad y oportunidades futuras bajo sus supuestos;
  RQ0 formaliza clases de decisión conjunta/separada y sus comparaciones.
  MIS-v2 implementa la transición de competencia por exposición en N×K; la
  ejecución N×K registra demanda, producción, recursos y, en rutas
  pertinentes, enseñanza/estimación. Nembhard Direct implementa su estado de
  experiencia-productividad propio, sin equivalencia con MIS-v2. El router
  contextual calidad-coste es independiente. E2.0/E2.1 establecen resultados
  solo para sus modelos reducidos; HLS-G0-C6 conserva valores exactos y
  evidencia exploratoria para instancias declaradas. Su decisión STOP cierra
  esa línea de investigación, no invalida ni generaliza sus resultados. La
  ontología v0.1 consolida distinciones semánticas sin unificar rutas. Véanse
  los informes enlazados abajo.
- **NUEVA DECISIÓN:** organizar la formulación científica y la trazabilidad
  de estudios mediante el encadenamiento conceptual A (problema), B
  (mecanismos) y C (organización), y analizar sus interacciones sin exigir
  que cada estudio incluya los tres niveles o que un componente sea novedoso
  por separado.
- **NO IMPLEMENTADO POR ESTA DECISIÓN:** arquitectura universal A/B/C,
  composición ejecutable común de todas las rutas, soporte de cualquier
  interacción entre transferencia, aprendizaje, información y recursos, o
  comparación general entre todas las organizaciones listadas. La cobertura
  debe comprobarse por el código de cada mecanismo y sus tests; el marco no
  eleva documentación a capacidad validada.

Referencias de trazabilidad: [síntesis matemática del 22 oct.](../research/HLS_MATHEMATICAL_ANALYSIS_2026-10-22.md),
[ontología v0.1](../architecture/HLS_ONTOLOGY_V0_1_2026-10-23.md),
[cierre de G0-C6](../experiments/HLS_G0_C6_CLOSURE_2026-10-19.md),
[validación integrada del laboratorio](../experiments/HLS_LAB_ADAPTIVE_CAPABILITY_VALIDATION.md),
[G1](../theory/HLS_G1_STATIC_EXPERIMENTAL_GROUND_TRUTH.md),
[G2](../theory/HLS_G2_DYNAMIC_GROUND_TRUTH.md),
[G3](../experimental_foundations/HLS_G3_ORGANIZATIONAL_VALUE_GROUND_TRUTH.md),
[MIS-v2](../theory/HLS_CAPABILITY_DEVELOPMENT.md), y la documentación de
[Nembhard Direct](HLS_NEMBHARD_DIRECT_EXPERIENCE_MECHANISM.md) y del
[router contextual](HLS_MIXLLM_ROUTER_IMPLEMENTATION.md). Las referencias
permiten verificar alcances particulares; no implican una integración
ejecutable entre ellos.

#### Consecuencia para el trabajo restante hasta el 30 de octubre

La interpretación operativa aprobada es:

- **26 oct.:** identificar una familia de problemas prácticamente relevante
  y apoyada por literatura; especificar A/B/C, soporte del laboratorio,
  funcionalidad faltante, comparadores y una hipótesis falsable.
- **27 oct.:** definir los requisitos de reproducibilidad y comparación justa.
- **29 oct.:** preparar un protocolo acotado para el problema seleccionado;
  solicitar autorización antes de ejecutar.
- **30 oct.:** evaluar evidencia disponible y decidir **GO / REFRAME / STOP**.

El calendario original de §2 se conserva íntegro. Estas metas actualizan la
interpretación operativa de los hitos restantes, no reconstruyen el plan
original ni crean fases o subfases. El hito de cierre del 30 de octubre
permanece vigente.

**Estado:** marco conceptual aprobado; no implementado como arquitectura, no
validado como mecanismo y no ejecutado como campaña. **Preguntas abiertas:**
qué problema práctico ofrece un test informativo de las interacciones; qué
partes A/B/C soporta de hecho cada ruta; qué comparadores fuertes comparten
información y restricciones; y qué costes además del rendimiento deben
medirse.

### RETROSPECTIVE MANAGEMENT AUDIT — CLOSED — 19 de octubre de 2026

**Tipo:** auditoría retrospectiva única del patrón de solicitudes CE. No es
una evaluación nueva del laboratorio, una búsqueda bibliográfica ni una
propuesta experimental. **Cobertura:** instrucciones CE/PI visibles en el
historial de esta conversación, documentos de decisión/actividad y productos
de trabajo presentes en el repositorio. Se contrastó la existencia y alcance
de los principales informes; no se volvió a verificar sus análisis
científicos. Dos archivos de sesión Codex locales accesibles corresponden a
handover de 19-10, no constituyen un archivo completo de todas las solicitudes
CE. Por tanto, el recuento es exacto para las 16 solicitudes identificables
en el historial de instrucciones disponible, pero no pretende ser un censo
de sesiones externas o no retenidas.

#### Cuantificación

Se contaron solicitudes distintas, no menciones repetidas de un informe en
otros documentos. Una solicitud puede producir información incremental y a
la vez repetir sustancialmente un objetivo. Con ese criterio:

- **Solicitudes identificables con objetivos A–D:** 16.
- **Solicitudes sustancialmente repetitivas:** 7.
- **Solicitudes que añadieron evidencia incremental de fuente primaria,
  código, prueba, resultado o análisis verificable:** 13 (#1–8 y #12–16).
- **Solicitudes cuyo resultado principal repitió hallazgos previos sin cerrar
  la decisión operativa pendiente:** 5 (#5, #8, #9, #11 y #13).

Estas categorías no son una partición exhaustiva. “Nueva evidencia” incluye
evidencia incremental de alcance acotado; no significa que la solicitud
completa fuese nueva ni que el resultado validase científicamente una
política. Los productos #9–11 sí contienen síntesis/diseños útiles, pero no
añadieron evidencia independiente suficiente para contarlos en la cifra
estricta anterior.

| # | Fecha / referencia de solicitud | Objetivo identificable y resultado documentado | Equivalente ya disponible / decisión posterior | Clasificación |
|---:|---|---|---|---|
| 1 | 17-10; [auditoría diferencial](../engineering/HLS_LAB_DIFFERENTIAL_CAPABILITY_AUDIT.md) | Revisar capacidades dinámicas, aprendizaje, políticas, escenarios y requisitos originales; concluyó que existían mecanismos y que E1/E2 no los invalidaban. | No había aún una síntesis diferencial en ese alcance. Resultado: GO a validación acotada. | Nueva evidencia; referencia inicial. |
| 2 | 17-10; [validación integrada](../experiments/HLS_LAB_ADAPTIVE_CAPABILITY_VALIDATION.md) | Ejecutó S0–S4 mediante componentes existentes, con 135 tests focalizados reportados; acotó qué estaba validado. | Fue seguimiento legítimo al GO #1, produjo trazas/resultados; no equivalía a otra auditoría ni probó superioridad. | Nueva evidencia; follow-up legítimo. |
| 3 | 19-10; [selección de reproducción literaria](../experiments/HLS_LITERATURE_REPRODUCTION_SELECTION_2026-10-19.md) | Revisó fuentes y correspondencia HLS para elegir un experimento reproducible; STOP antes de ejecutar por falta de fidelidad/insumos. | No había una selección y protocolo comparativo con esa decisión. | Nueva evidencia; no repetición. |
| 4 | 19-10; [búsqueda dirigida de ventaja adaptativa](../experiments/HLS_TARGETED_ADAPTIVE_ADVANTAGE_LITERATURE_SEARCH_2026-10-19.md) | Buscó precedentes publicados positivos frente a alternativas fijas fuertes; no halló un precedente directo suficientemente cercano. | Pregunta más estrecha que #3 y nueva cobertura de candidatos; no seleccionó un escenario HLS. | Nueva evidencia; follow-up legítimo. |
| 5 | 19-10; [auditoría de novedad y prior art](../research/HLS_SCIENTIFIC_NOVELTY_AUDIT_2026-10-19.md) | Amplió la búsqueda a solapamiento matemático y amenazas de prior art. | Revisitó el propósito de búsqueda/adjudicación ya cubierto por #3–4 y auditorías previas; añadió referencias y clasificación de claims, pero no fijó decisión operativa de experimento. | **Repetitiva**, con evidencia incremental. |
| 6 | 19-10; [comparación formal Baccara–Chen–RQ0](../research/HLS_BACCARA_CHEN_FORMAL_COMPARISON_2026-10-19.md) | Pidió mapeo matemático específico de dos modelos a RQ0/strong-SEP. | Pregunta técnica delimitada que no estaba resuelta por una matriz de literatura; se pidió después análisis full-text de Chen cuando apareció la fuente completa. | Nueva evidencia; follow-up legítimo. |
| 7 | 19-10; [compatibilidad del simulador con Chen](../experiments/HLS_CHEN_SIMULATOR_COMPATIBILITY_AUDIT_2026-10-19.md) | Contrastó requisitos del artículo con interfaces/código, algoritmos y coste de reproducción. | No era idéntico al mapeo matemático #6: añadió factibilidad técnica verificable. | Nueva evidencia; no repetición. |
| 8 | 19-10; [inversión de benchmark](../research/HLS_BENCHMARK_INVESTMENT_ASSESSMENT_2026-10-19.md) | Volvió a decidir si Chen u otra referencia justificaba implementación, con adopción/código y costes. | El valor/factibilidad de Chen ya eran objeto de #6–7; la búsqueda de adopción añadió elementos, pero la decisión de selección quedó reabierta en vez de fijarse. | **Repetitiva**, con evidencia incremental. |
| 9 | 19-10; [extensibilidad arquitectónica](../architecture/HLS_LABORATORY_EXTENSIBILITY_AUDIT_2026-10-19.md) | Volvió a inventariar entorno, estado, decisiones, capacidades, políticas, trazas y límites para extensibilidad. | Superpone en gran medida el inventario de #1 y la matriz de #7–8; incorporó opciones de arquitectura y diseño mínimo, pero ninguna implementación fue autorizada. | **Repetitiva**, con nueva síntesis de ingeniería. |
| 10 | 19-10; [diseño de validación E1](../experiments/HLS_E1_VALIDATION_DESIGN_2026-10-19.md) | Volvió a examinar ambientes/políticas y propuso comparadores, instancia G0/RQ0 y criterios; decisión REVISE por colisión de identificador/definiciones. | Especificó una pregunta de diseño más concreta; no debe confundirse con ejecutar E1 Nembhard ni con prueba de capacidad general. | **Repetitiva en A/C/D**, con nuevo diseño delimitado. |
| 11 | 19-10; [capacidad y selección de métodos publicados](../research/HLS_LABORATORY_CAPABILITY_ASSESSMENT_2026-10-19.md) | Reexaminó capacidades, escenarios, comparadores e hipótesis para seleccionar dos mecanismos. | Abarca nuevamente A–D tras #1, #2 y #9. Aportó candidatos/compatibilidad contextual, pero no produjo pareja fiel y aprobada. | **Repetitiva**, con información incremental. |
| 12 | 19-10; [preflight MixLLM/System-1.x](../experiments/HLS_PUBLISHED_METHODS_REPRODUCTION_PREFLIGHT_2026-10-19.md) | Verificó requisitos de repositorio, datos, modelos, runtime, hardware y smoke test. | Follow-up legítimo que concreta los bloqueos de los métodos considerados en #11; no fue una campaña ni una auditoría genérica nueva. | Nueva evidencia; follow-up legítimo. |
| 13 | 19-10; [selección de métodos ejecutables](../experiments/HLS_EXECUTABLE_PUBLISHED_METHOD_SELECTION_2026-10-19.md) | Volvió a seleccionar métodos/pair tras los bloqueos y fijó criterio de factibilidad acotada; REVISE, sin pareja compuesta seleccionada. | Repite materialmente selección de escenario/método de #3, #11 y decisión posterior a #12; cambió restricciones de ejecutabilidad y descartó composición forzada. | **Repetitiva**, con criterio nuevo. |
| 14 | 20–21-10, según el documento; [síntesis de evidencia](../research/HLS_SCIENTIFIC_EVIDENCE_SYNTHESIS_2026-10-20.md) y [priorización](../research/HLS_PRIORITIZED_INVESTIGATIONS_2026-10-21.md) | Consolidó G1–C6, separó preguntas e hipótesis y priorizó tres investigaciones. | Parte sustancial de la evidencia y la pregunta “qué sigue” ya figuraba en #1–13; C6 y la priorización por interacciones actualizaron el material. | **Repetitiva en objetivo de síntesis/priorización**, con evidencia nueva de C6 y decisión provisional. |
| 15 | 22-10, según el documento; [análisis matemático](../research/HLS_MATHEMATICAL_ANALYSIS_2026-10-22.md) | Formalizó las tres investigaciones ya priorizadas, entre ellas transferencia × MIS-v2 × demanda cambiante; demostró identidad mecánica subaditiva para actualización de una misma celda y distinguió interacción organizativa. | Follow-up matemático legítimo a #14; produjo una pregunta delimitada, no selección/ejecución de campaña. | Nueva evidencia analítica; follow-up legítimo. |
| 16 | 23-10, según el documento; [ontología v0.1](../architecture/HLS_ONTOLOGY_V0_1_2026-10-23.md) | Consolidó términos, transiciones, trazabilidad y observabilidad de la investigación priorizada. | Desarrollo conceptual específico posterior a #15; no es otra búsqueda de escenario ni una capacidad implementada. | Nueva consolidación; no repetición. |

#### Repeticiones, conclusiones y fallo de gestión

Las conclusiones que reaparecieron con distintos nombres fueron:

1. **Ya hay mecanismos adaptativos y demanda dinámica en varias rutas;**
   dinámica ambiental, decisión sensible al estado, estimación, aprendizaje
   de política y evolución de capacidad son fenómenos distintos. La validación
   S0–S4 de #2 y el código/test mapping de #1 ya fijaban este límite.
2. **E1/E2 no son pruebas generales contra la adaptabilidad.** E1 tenía una
   referencia fija alineada con perfiles; E2.1 era separable y BEST-STATIC
   estaba optimizada. Esta limitación ya estaba en #1 antes de volver a
   plantear pruebas de capacidades en #9–11.
3. **No se puede llamar reproducción a una analogía de interfaz.** La ruta
   contextual HLS no es MixLLM; el resultado STOP de #3 se reabrió como
   selección de pareja en #11–13 sin que aparecieran los artefactos necesarios
   ni una pareja fiel ejecutable.
4. **Chen es un entorno distinto y costoso**, no una extensión por simple
   configuración del N×K actual; #6–8 volvió a evaluar compatibilidad y valor
   de inversión en solicitudes consecutivas.
5. **Una ventaja adaptativa no es requisito ni conclusión.** Los comparadores
   deben ser fuertes, la hipótesis falsable y los null/negativos informativos;
   este principio se reiteró entre #10–15.

**Fallo de gestión identificado:** no se mantuvo una puerta operativa de
“conclusión ya establecida → decisión que habilita → pregunta residual”. El
CE volvió a solicitar inventarios de capacidad, búsquedas de escenarios,
selección de comparadores y formulación de hipótesis con terminología nueva
(reproducción, referencia positiva, novedad, benchmark, métodos ejecutables,
priorización), sin exigir primero el delta de información frente a los
informes previos. En varios casos, la respuesta produjo otra matriz o una
decisión STOP/REVISE, pero no se congeló qué decisión práctica quedaba
resuelta; entonces el problema reapareció bajo otra formulación.

La repetición no significa que todas las solicitudes fueran inútiles: #2,
#6–7, #12 y #15 son follow-ups justificables porque aportaron validación,
formalización o factibilidad concreta. La auditoría necesaria consistía en
verificar el nuevo delta, no en volver a abrir el inventario completo.

#### Decisiones pendientes al cierre de esta retrospectiva

No queda pendiente decidir si el laboratorio posee capacidades adaptativas
básicas: la evidencia existente lo establece dentro de rutas y alcances
concretos. Sigue pendiente escoger una familia de problema que permita
formular una comparación científicamente útil, verificar su correspondencia
A/B/C y fijar comparadores/estimandos comunes. El plan asigna esa identificación
al **26 oct.**, reproducibilidad y comparación justa al **27 oct.**, protocolo
acotado al **29 oct.** y decisión **GO / REFRAME / STOP** al **30 oct.**. No
hay autorización aquí para implementación, experimento o campaña.

#### Regla PI para evitar recurrencia

Antes de pedir una nueva evaluación del laboratorio, búsqueda de escenarios,
comparación de baselines o formulación de hipótesis, el CE consultará las
conclusiones existentes e identificará la pregunta concreta aún sin respuesta.
La nueva solicitud deberá declarar expresamente:

1. qué ya se sabe;
2. qué información genuinamente nueva se necesita;
3. por qué la evidencia existente es insuficiente; y
4. qué decisión concreta permitirá tomar el resultado.

No se repetirán evaluaciones completadas únicamente porque la decisión
experimental siga siendo difícil. Esta entrada cierra una sola auditoría
retrospectiva y no autoriza otra.

<a id="p1-initial-reframe"></a>
### 2026-10-19 — HLS-P1: piloto práctico acotado (resultado REFRAME)

**Título aprobado:** *Anticipatory Capability Development in Dynamic
Technical Operations*. La pregunta aprobada es bajo qué persistencia de cambios
de demanda la anticipación mejora frente a FIXED-OPT y REACTIVE, usando MIS-v2,
controles estacionario/sin desarrollo y una instancia pequeña. La autorización
permitía ejecutar solamente comparaciones que las interfaces existentes
representaran fielmente.

**Comprobación de clases antes de ejecutar.** En la ruta N×K/MIS-v2,
`P0ProductionOnlyPolicyNK` es una regla de producción reactiva de solo
producción; `P1FixedTeachingNK` fija la relación de enseñanza, pero no la
organización productiva; `P2AdaptiveTeachingNK` usa la heurística existente de
memoria de eficacia, sin planificación anticipatoria. No existe en esta ruta
una política FIXED-OPT optimizada globalmente ni un decisor anticipatorio MIS-v2.
El solver exacto G0/RQ0 utiliza la dinámica A1, distinta de MIS-v2, por lo que no
se lo etiqueta como HLS-ANTICIPATORY. En consecuencia, la comparación completa
aprobada no es ejecutable sin cambiar o mezclar modelos científicos; no se hizo
esa sustitución.

En la subejecución, las tres políticas recibieron la vista imperfecta con
competencias estimadas y el conjunto de acciones factibles del periodo; P2
además mantuvo su memoria de eficacia. Ninguna recibió demanda futura. P0,
P1 y P2 no consumieron aleatoriedad propia; el generador de entorno congeló
caminos por separado y la observación usó la semilla indexada común. Las
restricciones físicas y contabilidad de recursos fueron comunes, pero P0 tiene
catálogo solo productivo, mientras que P1/P2 pueden escoger acciones de
enseñanza: las clases de acción no son idénticas.

**Ejecución válida disponible.** Se ejecutó el subestudio descriptivo de P0,
P1 y P2 sobre la configuración S4 ya existente (2 agentes, 2 competencias,
horizonte 4, presupuesto colectivo 2 y límites individuales 1), en tres
condiciones: (i) demanda IID estacionaria 50/50 con MIS-v2 y enseñanza; (ii)
alternancia Markov determinista x,y,x,y con MIS-v2 y enseñanza; (iii) la misma
alternancia con aprendizaje individual y enseñanza deshabilitados. Para cada
condición se congeló la trayectoria antes de pasarla a las tres políticas; se
usaron semillas de entorno 24016 e información 24017. El control estacionario
realizado fue x,x,x,y. Cada una de las nueve ejecuciones fue un episodio
determinista de cuatro periodos, no una campaña ni una muestra para inferencia.

| Condición | P0 reactiva CES acumulada | P1 relación fija CES | P2 relación adaptativa CES |
|---|---:|---:|---:|
| Estacionaria, MIS-v2 + enseñanza | 1.8782079257190412 | 1.1925133796059215 | 1.1695029972464253 |
| Alternancia, MIS-v2 + enseñanza | 1.8550497116681317 | 1.1925133796059215 | 1.1695029972464253 |
| Alternancia, sin desarrollo | 1.5250905584278822 | 1.5250905584278822 | 1.5250905584278822 |

En las seis ejecuciones con desarrollo habilitado hubo cuatro periodos con
incremento MIS-v2. P1 y P2 enseñaron los cuatro periodos, con cargo total de
recursos 2.0 y esfuerzo productivo total 4.0; P0 no enseñó y usó esfuerzo
productivo total 8.0. En el control sin desarrollo no hubo incrementos MIS ni
enseñanza; los tres resultados y trazados de producción coincidieron. No hubo
periodos con éxito funcional en estas configuraciones; se conservaron también
déficit funcional y trazas por periodo en el artefacto. Los resultados describen
este S4 y estas políticas, no una comparación de organizaciones estáticas u
anticipatorias. Las reglas P1/P2 eligieron enseñanza en cada periodo de esta
instancia y redujeron el esfuerzo productivo disponible; no se infiere de ello
que la enseñanza sea generalmente perjudicial.

**Reproducibilidad y validación.** El ejecutor es
[`experiments/hls_p1_supported_comparison.py`](../../experiments/hls_p1_supported_comparison.py)
y rehúsa sobrescribir resultados. El artefacto completo, incluidos parámetros,
semillas, trayectorias y decisiones, está en
[`results/experiments/hls_p1_supported_comparison/results.json`](../../results/experiments/hls_p1_supported_comparison/results.json).
Reproducción: `PYTHONPATH=src python experiments/hls_p1_supported_comparison.py`
(requiere retirar o elegir explícitamente otro destino si el artefacto ya
existe; el ejecutor nunca lo reemplaza). Validación ejecutada:
`pytest -q tests/test_hls_lab_nk_environment.py tests/test_hls_lab_nk_execution.py tests/test_hls_lab_nk_policies.py tests/test_hls_lab_nk_learning_transition.py tests/test_hls_lab_nk_teaching.py` — **90 passed**.
JSON válido mediante `python -m json.tool ...` y sin campos no finitos. No se
ejecutó una campaña; el episodio inicial S4 también se conservó separadamente
en `results/diagnostics/hls_p1_supported_comparison/initial_s4_run.json`.

**Decisión: REFRAME para la pregunta HLS-P1 completa.** El subestudio verifica
la ejecución emparejada de las tres políticas MIS-v2 disponibles y el control
nulo, pero no varía persistencia, no optimiza FIXED-OPT y no incluye
HLS-ANTICIPATORY. Por tanto no responde la pregunta científica aprobada ni
autoriza una conclusión sobre anticipación. La comparación solicitada requeriría
una política FIXED-OPT compatible y un decisor anticipatorio MIS-v2; ambas
dependencias quedan explícitas, sin inventar ni implementar sustitutos en esta
entrega. Se preservan tanto el resultado nulo como la limitación de alcance.

#### Diagnóstico técnico HLS-P1 — 2026-10-19 (decisión C: REFRAME)

Esta revisión es de la ejecución ya guardada; no cambia código ni artefactos.
Evidencia primaria: [`ejecutor`](../../experiments/hls_p1_supported_comparison.py),
[`resultados y trazas`](../../results/experiments/hls_p1_supported_comparison/results.json),
reglas de [`política`](../../src/hls/hls_lab_nk_policies.py),
[`producción y recompensas`](../../src/hls/hls_lab_nk_production.py),
[`transiciones MIS-v2 y ejecución`](../../src/hls/hls_lab_nk_execution.py),
[`transferencia y recursos`](../../src/hls/hls_lab_nk_teaching.py) y
[`S4 de referencia`](../../experiments/synthetic/hls_lab_v1/scientific_model_reference.py).

**Éxito funcional cero — esperado e inevitable en el espacio discreto
configurado, no error del medidor.** `evaluate_problem_nk` declara éxito solo
si, para toda competencia con requisito positivo, producción `output + 1e-12`
alcanza el requisito. Se usaron `task-x=(1.10, 0.10)` y `task-y=(0.10, 1.20)`;
competencia inicial verdadera `((0.85,0.15),(0.20,0.20))`. Para determinar si
era solo una limitación de P0/P1/P2, se enumeraron de forma exhaustiva las 72
acciones conjuntas factibles del catálogo declarado (incluyendo producción y
todas las opciones factibles de enseñanza) sobre cada estado alcanzable en las
dos trayectorias congeladas, aplicando las transiciones MIS-v2 y enseñanza
existentes. No hubo ningún par estado-acción exitoso en ninguno de los cuatro
periodos ni en ninguna trayectoria. Estados alcanzables al inicio de cada
periodo: 1, 72, 1.071 y 8.265; acciones factibles: 72 por periodo. Máximos por
competencia, maximizados separadamente sobre esos pares estado-acción:

| Periodo | Tarea alternante | Máximo x | Máximo y | Requisito de la tarea |
|---:|---|---:|---:|---|
| 0 | x | 1.050000 | 0.350000 | (1.10, 0.10) |
| 1 | y | 1.176000 | 0.621500 | (0.10, 1.20) |
| 2 | x | 1.284480 | 0.847955 | (1.10, 0.10) |
| 3 | y | 1.378022 | 1.036899 | (0.10, 1.20) |

En los periodos de tarea-y ni siquiera el máximo alcanzable de y llega a 1.20.
En periodo 0 el máximo x queda por debajo de 1.10; en periodo 2 la enumeración
de pares completos confirma que ningún mismo estado-acción satisface a la vez
ambos requisitos, pese a que los máximos marginales separados superen sus
umbrales. La misma secuencia de problemas alternantes aparece en el control sin
desarrollo. Para la realización estacionaria x,x,x,y, la enumeración también
encontró cero éxitos; en periodos 0–2 la demanda x requiere ambas competencias,
y en el periodo 3 el máximo y alcanzable vuelve a ser 1.036899 frente a 1.20.
Esto establece imposibilidad solo dentro del catálogo discreto, parámetros,
transiciones y horizonte del piloto; no afirma imposibilidad bajo acciones
continuas, otro horizonte o una distribución distinta.

**Por qué P1/P2 enseñan.** La enseñanza no es obligatoria en el ejecutor:
acciones sin enseñanza están en el catálogo. Pero P1 restringe su comparación a
acciones con su relación A→B/y y escoge la de mayor ranking de producción; solo
vuelve a `_best` sin enseñanza si no existe una acción factible de esa relación.
No compara ese ranking contra la mejor acción sin enseñanza ni descuenta el
valor futuro. La relación es factible los cuatro periodos, por lo que enseña
siempre. P2 es opcional: si la mejor acción productiva ya da éxito, no enseña;
si no, elige primero una relación elegible aún no observada; después prioriza
la mayor eficacia media de memoria y solo abandona la enseñanza si no hay
relación por encima del umbral. No calcula continuación ni anticipa demanda.
Como nunca hay éxito, ambas reglas entran en su rama de enseñanza; ambas
relaciones siguen elegibles bajo el umbral de competencia 0.95 y las señales
registradas superan el umbral de eficacia 0.35.

P1 usa A→B/y en los cuatro periodos. P2 usa A→B/y, B→A/x, A→B/y, A→B/y; por
tanto las decisiones conjuntas sí difieren en el periodo 1, aunque la matriz de
esfuerzo productivo es idéntica. El primer cambio de P2 es explorar la relación
no observada, no una respuesta a la demanda ni una elección anticipatoria. Con
`r=0.4`, esfuerzo de enseñanza `e=0.25` y eficacias respectivas 0.80 y 0.70,
la ganancia de competencia sigue `r e T (1-c)` tras MIS-v2: en ese periodo P1
añade 0.0482816 a B/y; P2 añade 0.0084 a A/x. El posterior menor B/y reduce la
producción de P2 en los periodos 2–3. P2 queda 0.023010382359496262 CES por
debajo de P1 en ambas condiciones; no se debe a que sus acciones fueran
idénticas, sino a explorar un vínculo de menor retorno en esta realización.

**Coste de oportunidad observado.** En cada periodo P0 asigna esfuerzo
productivo total 2.0, sin enseñanza. P1/P2 asignan producción total 1.0 más
cargo de enseñanza `2e=0.5`, totalizando 1.5 de un presupuesto 2.0; cada
participante paga `e=0.25` de su límite individual. Así, frente a la acción P0,
las acciones P1/P2 desplazan una unidad de esfuerzo productivo por periodo y
dejan 0.5 de presupuesto colectivo sin usar. No hay una penalización monetaria
de enseñanza sustraída de CES: CES agrega solo las salidas de producción. La
enseñanza tiene coste de recurso y afecta indirectamente producción factible;
recompensa, éxito y déficit se registran por separado. No atribuir toda la
diferencia P0–P1/P2 causalmente a una sola unidad de esfuerzo: también difieren
las trayectorias de competencia causadas por MIS y transferencia.

**Demanda y recompensa.** Los caminos reproducidos fueron `x,x,x,y` (IID
50/50, semilla 24016) y `x,y,x,y` (Markov alternante determinista, misma
semilla). La demanda llega a las políticas como `requirements` de la vista y
entra en `_production_rank` mediante éxito, déficit normalizado y margen;
en esta instancia la acción productiva elegida por P1/P2 no cambia al cambiar
la tarea. Ambas siguen la misma secuencia de matrices productivas y de
competencias en los dos escenarios; P2 conserva también la misma secuencia de
relaciones docentes. El resultado CES por periodo depende de las salidas y de
los pesos (0.5,0.5), no del requisito ni del estado de demanda. Por ello las
recompensas acumuladas P1=1.1925133796059215 y P2=1.1695029972464253 son
idénticas entre caminos. No es una fuga de demanda: los déficits sí reflejan
los requisitos y cambian. Por ejemplo P1: déficits acumulados 2.5961439874980625
(x,x,x,y) y 2.850737580832767 (x,y,x,y); P2: 2.6090854641981576 y
2.8636790575328623 respectivamente. P0 sí cambia su decisión productiva con
la tarea y su CES acumulado cambia de 1.8782079257190412 a 1.8550497116681317.

La recompensa CES implementada es
`(Σ_k w_k output_k^ρ)^(1/ρ)`, `ρ=0.5`; éxito funcional no es sumando de CES,
aunque forme parte de la clasificación lexicográfica que guía el ranking de
políticas. En el control sin desarrollo, MIS está deshabilitado y no ocurren
acciones de enseñanza; P1/P2 caen en la mejor acción productiva y coinciden
exactamente con P0: CES 1.5250905584278822, esfuerzo productivo 8.0, cargo de
enseñanza 0 y competencia final igual a la inicial. Es un control nulo
internamente consistente. Las tres políticas comparten semillas/ruta congelada
por condición y semilla de observación indexada; no consumen azar propio.

**Clasificación.** No se detecta defecto en medición de éxito, transición,
recompensa, cargos de recursos ni emparejamiento. Enseñanza frecuente en P1 es
limitación de diseño de la política; exploración de P2 es comportamiento
codificado y no anticipación; sensibilidad de la acción a requisitos existe,
pero no cambia el argmax de P1/P2 en este escenario. El control compara
correctamente el mecanismo deshabilitado con los mismos presupuestos y
demanda. La comparación P0/P1/P2 es ejecutable y trazable dentro de su alcance,
pero no aísla el beneficio de enseñar bajo acción-equivalencia: P0 no admite
enseñanza y P1/P2 sí. No se observa una comparación de horizonte ni de
persistencia; solo una realización estacionaria y una alternancia fijada.

**Decisión final para la pregunta HLS-P1: REFRAME.** La subejecución es
internamente interpretable y sus resultados son consistentes con el código,
pero no responde a FIXED-OPT frente a REACTIVE frente a HLS-ANTICIPATORY. Las
dos clases ausentes siguen siendo la limitación decisiva ya registrada; P1/P2
no deben renombrarse como sustitutos. No se prescribe aquí una corrección de
parámetros ni se inicia otro experimento.

<a id="p1-validated-comparison"></a>
### 2026-10-19 — HLS-P1: implementación dirigida y comparación exacta

**Relación con el registro previo.** El subestudio HLS-P1 soportado de arriba
permanece **CLOSED / REFRAME**, con sus resultados intactos. Esta es una
implementación/ejecución nueva, guardada en una ruta distinta, para las tres
clases organizativas aprobadas; no reinterpreta P0/P1/P2 como tales clases.

**Modelo implementado.** Se añadió un módulo autónomo acotado que reutiliza la
transición MIS-v2 existente `mis_v2_transition_nk` y la producción aditiva
`productive_outputs_nk`; no cambia el ejecutor N×K ni sus mecanismos. Hay dos
agentes A/B, competencias x/y, competencia inicial `((.85,.15),(.20,.20))`,
parámetros MIS-v2 `eta=((.15,.15),(.25,.25))`, horizonte 4, límite individual
1 y presupuesto colectivo 2. Cada agente elige de
`(0,0),(.5,0),(0,.5),(1,0),(0,1),(.5,.5)`; se obtienen 36 asignaciones
conjuntas factibles, compartidas por las tres políticas. Requisitos:
`x=(.65,.12)`, `y=(.12,.65)`, pesos funcionales iguales. MIS-v2 actualiza la
competencia después de producir, por la exposición de esfuerzo correspondiente.
No hay acción de desarrollo independiente en MIS-v2 ni coste monetario de
desarrollo: el esfuerzo es simultáneamente recurso limitado y exposición de
aprendizaje. El objetivo no vuelve a restar ese esfuerzo; así se evita
contabilizarlo dos veces.

La recompensa primaria por periodo es
`F_t = 0.5*min(output_x/requirement_x,1) + 0.5*min(output_y/requirement_y,1)`.
La tarea completa obtiene exactamente 1; satisfacción parcial obtiene el
promedio ponderado de fracciones satisfechas, truncadas por competencia. Éxito
binario se informa aparte, no añade un bono que duplique el valor de completar.
CES queda fuera de la medida primaria. El consumo de recursos restringe las
acciones; esfuerzo/exposición MIS se registra como inversión y no se sustrae
otra vez de `F_t`.

**Organizaciones.** `FIXED-OPT` enumera y optimiza los 1.296 mapas estacionarios
posibles `task → allocation` sobre la distribución de demanda completa y el
horizonte; el mapa se mantiene fijo durante el episodio. `REACTIVE` elige la
asignación que maximiza `F_t` con demanda y competencia actuales, sin valorar
continuación. `HLS-ANTICIPATORY` resuelve por DP exacta la esperanza de
recompensa futura, con transición MIS-v2 y ley de demanda conocida; no observa
ninguna realización futura. Las tres reciben la misma demanda actual y
competencia verdadera actual, tienen el mismo catálogo y presupuestos. El
conocimiento de la ley exógena se declara común; solo FIXED-OPT la usa para
optimizar previamente su mapa y HLS para su continuación. No hay ruido de
observación ni aleatoriedad de política. El comparador FIXED-OPT estacionario
óptimo dentro de su clase no es llamado óptimo global.

**Puertas previas y verificación.** La prueba
[`tests/synthetic/test_hls_p1.py`](../../tests/synthetic/test_hls_p1.py)
comprueba: éxito alcanzable en ambas tareas bajo una secuencia factible;
catálogo y restricciones comunes; exhaustividad del óptimo fijo contra
enumeración independiente; acción miope de REACTIVE; continuación exacta de
HLS y su decisión de invertir exposición MIS-v2 en B/y en un empate inmediato;
coste de oportunidad medible con igual recurso y menor recompensa actual;
recompensa dependiente de requisitos; emparejamiento de cada trayectoria para
las tres políticas; y ausencia de argumento de trayectoria futura en las
interfaces de decisión. Ejecución:
`PYTHONPATH=src pytest -q tests/synthetic/test_hls_p1.py tests/test_hls_lab_nk_learning_transition.py`
— **17 passed**. Se verificó además JSON válido y `git diff --check` limpio.

Una trayectoria factible de éxito para y empieza con tres periodos de
`A=(0,1), B=(0,1)` y termina con `A=(.5,.5), B=(0,1)`; las salidas y fueron
`.35, .6775, .935875, .901496875`, con éxito en el cuarto periodo y x=.425.
Para x, `A=(1,0), B=(0,1)` obtiene de inmediato salidas `(.85,.20)` y éxito.
El éxito, por tanto, es alcanzable pero no trivial bajo demanda y decisiones
distintas.

**Ejecución acotada.** El ejecutor
[`experiments/run_hls_p1_validated.py`](../../experiments/run_hls_p1_validated.py)
enumeró exactamente las 16 trayectorias de cuatro tareas para cada proceso
(32 trayectorias; 96 episodios emparejados entre tres políticas), ponderadas
por su probabilidad; no usó Monte Carlo. Demanda estacionaria IID:
`P(x)=P(y)=.5` cada periodo. Demanda cambiante: `(0.8,0.2)` en periodos 0–1 y
`(0.2,0.8)` en periodos 2–3. El resultado completo, todas las trazas y
metadatos están en
[`results/experiments/hls_p1_validated/results.json`](../../results/experiments/hls_p1_validated/results.json).
El ejecutor rehúsa sobrescribirlo. Comando de reproducción a una ruta nueva:
`PYTHONPATH=src python experiments/run_hls_p1_validated.py --output
results/experiments/hls_p1_validated/reproduction.json`.

| Proceso | FIXED-OPT: rendimiento / éxito | REACTIVE: rendimiento / éxito | HLS-ANTICIPATORY: rendimiento / éxito |
|---|---:|---:|---:|
| Estacionario | 3.792436415493279 / 0.71875 | 3.7786324612647912 / 0.671875 | 3.792436415493279 / 0.71875 |
| Cambiante | 3.9065590572481566 / 0.772 | 3.871122075016697 / 0.7144 | 3.9065590572481566 / 0.772 |

Rendimiento es suma esperada de `F_t`; éxito es fracción esperada de periodos
completados. Diferencia HLS–FIXED-OPT: cero en ambas condiciones. Diferencia
HLS–REACTIVE: `+0.0138045542284878` estacionaria y `+0.0354369822314594`
cambiante. Los mapas fijos ganadores fueron iguales: para x,
`A=(1,0),B=(0,1)`; para y, `A=(.5,.5),B=(0,1)`. La inversión esperada en
exposición/recurso fue FIXED-OPT 8.0 y HLS 7.375 (estacionaria) / 7.48
(cambiante); REACTIVE 7.1875 / 7.336. En el empate de rendimiento funcional
de tarea x, HLS escoge una exposición B/y mayor que REACTIVE y obtiene más
competencia futura; el mapa fijo ya incluye esa asignación para x y empata el
resultado. Esto demuestra valor frente a la regla miope en estas instancias,
pero no frente al baseline fijo fuerte.

**Interpretación y límite.** La comparación y la implementación satisfacen las
clases declaradas para MIS-v2; el piloto no demuestra superioridad universal ni
una ventaja anticipatoria frente a FIXED-OPT en estos dos procesos. El resultado
positivo frente a REACTIVE y nulo frente a FIXED-OPT se limita a los parámetros,
horizonte y dos leyes de demanda indicados. Se conserva el alcance acotado; no
se amplió a una campaña. HLS-P1 pasa a estado **EXECUTED — BOUNDED EXACT
COMPARISON**, mientras la conclusión científica es **REFRAME** respecto de la
pregunta de ventaja sobre ambas baselines: no se observó tal ventaja sobre el
fijo optimizado.

<a id="p1-bellman-regret"></a>
### 2026-10-19 — HLS-P1: condición matemática para una ventaja adaptativa estricta

**Alcance.** Análisis exacto del modelo ya validado en
[`src/hls/synthetic/hls_p1.py`](../../src/hls/synthetic/hls_p1.py) y de
[`results/experiments/hls_p1_validated/results.json`](../../results/experiments/hls_p1_validated/results.json).
No se añadieron modelos, parámetros ni experimentos. El análisis Bellman y de
empates se limita a las dos instancias finitas ya guardadas.

#### Modelo y clases de política

El estado de decisión es `s_t=(t,w_t,C_t)`, con periodo `t`, tarea observada
`w_t∈{x,y}` y matriz de competencias verdaderas `C_t∈[0,1]^{2×2}`. El catálogo
común `𝒰` contiene 36 asignaciones conjuntas factibles: esfuerzo individual
máximo 1 y presupuesto colectivo 2. La recompensa `r(s,a)` es el cumplimiento
funcional ponderado y truncado definido en la entrada anterior de HLS-P1. La
transición es `C_{t+1}=M(C_t,a_t)` mediante MIS-v2 después de producir; no hay
acción independiente de desarrollo ni coste monetario de desarrollo. La tarea
siguiente sigue la ley exógena `p_{t+1}(w'|t)`, independiente de la política.
Las políticas observan `t,w_t,C_t` y conocen la ley, pero no realizaciones
futuras de demanda.

`V_T=0`,
`Q_t(w,C,a)=r((t,w,C),a)+Σ_{w'}p_{t+1}(w'|t)V_{t+1}(w',M(C,a))`,
`V_t(w,C)=max_{a∈𝒰}Q_t(w,C,a)`; en el último periodo la continuación vale 0.
El valor inicial promedia `V_0(w,C_0)` según `p_0(w)`.

- `F`: mapas deterministas `f:{x,y}→A`, optimizados sobre la distribución
  completa y horizonte, constantes durante el episodio; dependen solo de la
  tarea, no de periodo ni competencia.
- `R`: regla miope que elige un maximizer de la recompensa inmediata
  `argmax_{a∈𝒰} r((t,w,C),a)`; el código desempata por primer índice del catálogo.
- `A`: políticas factibles no anticipativas que pueden depender de
  `(t,w_t,C_t)` y optimizar valor acumulado con la ley conocida; el DP
  implementado resuelve el representante óptimo de Bellman y no ve demanda
  futura realizada.

Se tiene `F⊆A` y `R⊆A` (donde `A` es la clase adaptativa y `𝒰` el catálogo
factible). En general `F` y `R` no están anidadas: un mapa fijo
puede no ser miope-óptimo en algún estado y una regla reactiva puede cambiar
la acción para una misma tarea cuando cambia la competencia. Hay intersección
si el mapa fijo también maximiza recompensa inmediata en todos los estados
donde se usa. Estas inclusiones no implican igualdad de valor.

#### Suficiencia fija y condición necesaria-y-suficiente del gap

Sea `d_t^π(s)` la distribución de ocupación bajo la política `π` y sea el
arrepentimiento de Bellman `δ_t(s,a)=V_t(s)−Q_t(s,a)≥0`. Para cualquier política
factible no anticipativa, la ecuación de Bellman y la transición implican por
telescopado la identidad exacta:

`V_A−J(π)=E_π[Σ_{t=0}^{T−1}δ_t(s_t,a_t)]`.

La identidad también vale promediando sobre la distribución inicial. Los
empates en Q tienen `δ=0`; una diferencia de acciones no basta para inferir
pérdida. Tampoco cuentan estados no alcanzados bajo la política evaluada.

Un mapa fijo `f` alcanza `V_A` si y solo si
`f(w)∈argmax_{a∈𝒰} Q_t(w,C,a)` para todo estado con `d_t^f(t,w,C)>0`. Por tanto,
para la clase finita `F`:

`V_A>V_F  ⇔  ∀f∈F: E_f[Σ_t δ_t(s_t,f(w_t))]>0`.

Es decir, cada mapa fijo debe incurrir en arrepentimiento Bellman estrictamente
positivo en al menos una decisión alcanzable con probabilidad positiva bajo
ese mismo mapa. Si un mapa tiene arrepentimiento cero en todo su soporte de
ocupación, `V_F=V_A`. Esta es una condición necesaria y suficiente que respeta
que los mapas inducen soportes diferentes.

Condición suficiente más simple, pero más fuerte: existen dos estados de
probabilidad positiva bajo todo mapa, con la misma tarea y conjuntos de
acciones Bellman-óptimas disjuntos (maximizadores estrictos). Como `f(w)` no
puede cambiar entre esos estados, cada mapa pierde estrictamente en alguno y
el gap es positivo. No es necesaria: puede haber gap aunque no exista ese par.

**Prueba.** Por Bellman, `δ` es no negativo y la diferencia entre valor óptimo
y retorno realizado telescopa a la suma de `δ`. Una suma no negativa tiene
esperanza cero exactamente cuando cada término es cero casi seguramente en
los estados ocupados. Esto prueba la equivalencia para cada `f`. Como `F` es
finita, `V_F=max_f J(f)`; luego `V_A>V_F` si y solo si ningún `f` tiene retorno
`V_A`, equivalente a que todos tengan arrepentimiento esperado positivo.

#### Aplicación al P1 validado

En ambos escenarios el mapa optimizador almacenado es `(22,34)`: para `x`,
`A=(1,0), B=(0,1)`; para `y`, `A=(.5,.5), B=(0,1)`. Una evaluación del
soporte alcanzable y las continuaciones Bellman en las mismas instancias
encontró 22 estados ocupados por el mapa en cada escenario. Su acción tuvo
arrepentimiento Bellman máximo `0.0` en esos estados (comparación numérica con
tolerancia `10⁻¹²`). Así, el mapa FIXED-OPT es Bellman-óptimo en todo su soporte
de ocupación, lo que explica su igualdad de valor inicial con HLS.

La enumeración de los 1.296 mapas encontró un único maximizador dentro de
`10⁻¹²` en cada escenario: `(22,34)`. No se detectó mapa alternativo empatado
a esa tolerancia. Es unicidad numérica en estas instancias, no un teorema
general ni una afirmación de igualdad matemática exacta más allá de la
precisión de coma flotante.

HLS elige acciones distintas en estados tardíos: en las trazas cambia `22→20`
para `x` en periodos 2 y 3, y `34→10` para `y` en periodo 3. Las recompensas
inmediatas respectivas siguen siendo `1.0`; las alternativas son empates de
valor Bellman en esos estados. Para cada una de las 16 secuencias de demanda,
el retorno acumulado de HLS y FIXED-OPT coincide en el resultado guardado.
Hay adaptación de acción, pero no conflicto con consecuencia positiva de
valor. MIS-v2 sí evoluciona la competencia, pero en el soporte alcanzado no
crea un estado en que el mapa fijo deba cambiar su regla para preservar el
óptimo. El mismo resultado se mantiene bajo demanda estacionaria IID
`(0.5,0.5)` y bajo la distribución cambiante `(0.8,0.2)` en periodos 0–1 y
`(0.2,0.8)` en 2–3.

#### Relación con resultados previos y límite estructural

El resultado concreta para P1, sin generalizar, la relación entre desarrollo
y oportunidades futuras tratada en
[G2](../theory/HLS_G2_DYNAMIC_GROUND_TRUTH.md) y
[G3/G3-H](../experimental_foundations/HLS_G3_ORGANIZATIONAL_VALUE_GROUND_TRUTH.md):
el valor de desarrollar depende de decisiones de asignación posteriores y la
continuación conjunta lo representa. La identidad de arrepentimiento es una
caracterización de control finito aplicada a P1, no una tesis de superioridad
universal. El mecanismo de desarrollo anticipatorio seguido de routing flexible
ya aparece en el análisis acotado de
[HLS-G0-C6](../experiments/HLS_G0_C6_EXACT_MECHANISM_ANALYSIS_2026-10-19.md);
P1 no lo reinterpreta retroactivamente. La contribución de este análisis es
identificar suficiencia Bellman del mapa fijo en estas instancias.

La condición estructural mínima para que haya gap no es simplemente que la
competencia cambie ni que HLS elija otra acción: debe haber arrepentimiento
Bellman positivo en soporte alcanzable para todo mapa fijo. Un candidato es
que la misma tarea requiera acciones óptimas incompatibles en estados de
competencia alcanzables; otro, que cambien con el tiempo los costes de
oportunidad de desarrollar. Son posibilidades, no propiedades halladas ni
escenarios propuestos aquí.

**Implicación falsable para una evaluación futura autorizada:** si existe un
mapa fijo cuyas acciones tienen arrepentimiento Bellman cero en todos sus
estados ocupados, su retorno esperado debe igualar al óptimo adaptativo, aun
si otras acciones óptimas difieren por estado. Un gap positivo bajo esa
condición apuntaría a una inconsistencia de cómputo, información, transición
o contabilidad.

**Estado epistemológico.** **Establecido para estas instancias:** igualdad
HLS/FIXED-OPT, único mapa maximizador dentro de la tolerancia declarada y
arrepentimiento cero del fijo en los estados ocupados inspeccionados.
**Probado:** identidad de arrepentimiento y condición necesaria-y-suficiente
del gap para el MDP finito y las clases definidas. **No establecido:** que el
P1 sea el único régimen de suficiencia fija, que adaptación sea innecesaria
en general bajo MIS-v2, ni que todo conflicto local produzca ventaja estricta.
No se seleccionan escenarios ni se autoriza trabajo experimental.

<a id="p1-six-configurations"></a>
### 2026-10-19 — HLS-P1: adaptación organizativa inducida por el estado de competencia

**Decisión:** GO para el estudio teórico y computacional exacto acotado de esta
entrada. No implica campaña adicional, nuevo mecanismo ni afirmación de
novedad publicable.

**Diseño de verificación.** Se reutilizaron `P1Scenario`, el catálogo y las
funciones de producción/transición de
[`src/hls/synthetic/hls_p1.py`](../../src/hls/synthetic/hls_p1.py), los
optimizadores exactos existentes y las dos leyes de demanda ya validadas. Se
examinaron seis configuraciones explícitas: (i) P1 estacionario original; (ii)
P1 con demanda cambiante; (iii) solo para demanda estacionaria, igualación de
la competencia inicial entre agentes por habilidad, preservando cada media
del equipo; (iv) intercambio de las filas de competencia inicial, sin cambiar
los `eta` ligados a los agentes; (v) `eta=.15` en todas las celdas; y (vi)
`eta=.25` en todas las celdas. En todos los casos se conservaron requisitos,
pesos, catálogo de acciones, presupuestos, horizonte y políticas. La tabla
resume evaluación determinista exacta de todas las trayectorias posibles y
enumeración de los 1.296 mapas fijos. Las dos últimas columnas indican si se
encontraron inversiones estrictas de preferencia inmediata y Bellman,
respectivamente, entre pares de acciones factibles para la misma tarea y
periodo, en estados de competencia visitados por FIXED-OPT/HLS.

| Configuración | Mapa `f*` | `V_A` | `V_F` | `V_A−V_F` | `∀f: E_f[Σδ]>0` | Reversión inmediata / Bellman |
|---|---|---:|---:|---:|---|---|
| P1 original, estacionaria | `(22,34)` | 3.7924364154932793 | 3.7924364154932793 | 0 | No; `f*` tiene arrepentimiento 0 | Sí / Sí |
| P1 original, cambiante | `(22,34)` | 3.906559057248156 | 3.906559057248156 | 0 | No; `f*` tiene arrepentimiento 0 | Sí / Sí |
| Competencia inicial igualada por habilidad, estacionaria | `(22,34)` | 3.723545666944881 | 3.6990500567473568 | **0.024495610197524442** | Sí, los 1.296 mapas | Sí / Sí |
| Filas iniciales de especialistas intercambiadas, estacionaria | `(27,29)` | 3.7264245787167187 | 3.7264245787167187 | 0 | No; `f*` tiene arrepentimiento 0 | Sí / Sí |
| `eta=.15` uniforme, estacionaria | `(22,34)` | 3.7093996618372875 | 3.7093996618372875 | 0 | No; `f*` tiene arrepentimiento 0 | Sí / Sí |
| `eta=.25` uniforme, estacionaria | `(22,34)` | 3.797007539113772 | 3.797007539113772 | 0 | No; `f*` tiene arrepentimiento 0 | Sí / Sí |

Las competencias iniciales de la tercera fila son `((.525,.175),(.525,.175))`;
se preservan las medias por habilidad de P1 original `((.85,.15),(.20,.20))`.
Los parámetros de aprendizaje permanecen heterogéneos por agente:
`eta=((.15,.15),(.25,.25))`. “Igualada” describe solo la competencia inicial,
no todo el agente. No se probó `eta=0`: MIS-v2 requiere `0<eta<1` y esta
comparación mantiene activa la transición canónica.

#### Mecanismo MIS-v2 y condición restringida

Para cada celda agente-habilidad, la transición implementada es
`c'_{ik}=1−(1−c_{ik})exp(−lambda(eta_{ik}) e_{ik})`, con
`lambda(eta)=−ln(1−eta)` y exposición productiva `e_{ik}≥0`. Al componer
periodos con el mismo `eta_{ik}`:

`c_{ik,t}=1−(1−c_{ik,0})exp(−lambda(eta_{ik}) E_{ik,t})`,
`E_{ik,t}=Σ_{u<t}e_{ik,u}`.

Así, para un mismo tiempo, la historia de las asignaciones cambia el vector de
exposiciones acumuladas y, con ello, las competencias; la tasa y la brecha
restante `(1−c)` controlan cuánto responde cada celda. La transición es
monótona y saturante, pero no garantiza que dos agentes mantengan su ranking
ni que una preferencia entre asignaciones conserve su signo. La acción consume
el mismo presupuesto que limita la producción; no hay coste separado que se
reste de la recompensa. El coste de oportunidad aparece en la producción
funcional sacrificada y en el valor de continuación, ambos contabilizados en
`Q`.

Para una tarea `w` y acciones factibles `a,b`, la diferencia inmediata real es

`D^r_w(C;a,b)=Σ_k q_k [min(Σ_i c_{ik}a_{ik}/d_{wk},1) − min(Σ_i c_{ik}b_{ik}/d_{wk},1)]`,

donde `q_k` son los pesos funcionales y `d_{wk}` los requisitos existentes.
La preferencia inmediata se invierte entre dos estados alcanzables `C,C'` si
`D^r_w(C;a,b)D^r_w(C';a,b)<0`. La diferencia Bellman es

`D^Q_{t,w}(C;a,b)=D^r_w(C;a,b)+Σ_{w'}p_{t+1}(w'|t)[V_{t+1}(w',M(C,a))−V_{t+1}(w',M(C,b))]`.

Su signo incluye el rendimiento actual, la evolución MIS-v2 de cada acción,
la demanda futura y las restricciones/opciones de uso del recurso a través de
`V`. A diferencia de `D^r`, `D^Q` puede invertirse por continuación aun cuando
la diferencia inmediata no lo haga. Las expresiones son caracterizaciones
exactas para este modelo; no implican que la transición por sí sola cause un
gap.

**Proposición restringida (suficiente).** En este MDP finito, si para cada
mapa fijo task-conditioned `f` existe un estado `(t,w,C)` con probabilidad
positiva bajo la ocupación inducida por ese mismo `f` en el que
`f(w)∉argmax_{a∈𝒰}Q_t(w,C,a)`, entonces `V_A>V_F`. En particular, una forma
verificable suficiente es que MIS-v2 genere estados alcanzables para una misma
tarea con conjuntos de maximizadores Bellman incompatibles y que estos estados
sean inevitables con probabilidad positiva bajo todo mapa fijo. La prueba es
la identidad de arrepentimiento Bellman establecida en la entrada anterior:
cada mapa tiene al menos una pérdida estricta con masa positiva, y la clase
de mapas es finita. No se afirma que una reversión sea necesaria en todos los
modelos: tiempo/demanda también pueden causar incompatibilidad. La condición
es suficiente, no necesaria; la condición necesaria-y-suficiente general ya
registrada sigue siendo la de arrepentimiento positivo para cada mapa.

#### Reversión exacta y caso con gap

En el caso de competencia inicial igualada, bajo FIXED-OPT (mapa `(22,34)`),
los dos prefijos `xx` y `yx` tienen probabilidad positiva y llevan a estados
diferentes con tarea actual `x` en el mismo periodo `t=1`:

| Prefijo / competencia actual `C=(A_x,A_y;B_x,B_y)` | Acción 3: `B→x` (`r`,`Q`) | Acción 12: `A→.5y` (`r`,`Q`) |
|---|---:|---:|
| `xx`: `(.59625,.175;.525,.38125)` | `.403846`, `2.315221` | `.364583`, `2.294531` |
| `yx`: `(.562072,.239388;.525,.38125)` | `.403846`, `2.333794` | `.498724`, `2.445796` |

En el mismo periodo y para la misma tarea, tanto la comparación inmediata
como la Bellman cambian de signo: primero se prefiere la acción 3, después la
12. Los estados son realmente alcanzables bajo el mismo mapa fijo tras
distintas demandas previas; la diferencia de competencias viene de la
exposición MIS-v2 inducida por las asignaciones precedentes. Es evidencia
exacta de reversión, no solo de que el controlador elige acciones distintas.

En el caso con gap, el mapa fijo óptimo sigue siendo `(22,34)`. HLS usa acción
23 en los estados `x` indicados; esta reasignación tiene el mismo uso total de
recurso que acción 22 (`2` unidades), pero distribuye la unidad del agente B
entre x/y (`(.5,.5)`) en lugar de dedicarla toda a y. En cada estado, la
contribución ponderada de arrepentimiento del mapa fijo se obtiene como masa
de ocupación por `Q(23)−Q(22)`:

| `t`, tarea | `C=(A_x,A_y;B_x,B_y)` | Masa | `r(22)→r(23)` | `Q(22)→Q(23)` | Contribución esperada |
|---|---|---:|---:|---:|---:|
| 1, x | `(.59625,.175;.525,.38125)` | .25 | `.958654→1` | `2.948438→2.962172` | `.003433585` |
| 1, x | `(.562072,.239388;.525,.38125)` | .25 | `.932363→1` | `2.932363→2.974554` | `.010547817` |
| 2, x | `(.627761,.239388;.525,.535938)` | .25 | `.982893→1` | `1.982893→2` | `.004276751` |
| 2, x | `(.59625,.29875;.525,.535938)` | .125 | `.958654→1` | `1.958654→2` | `.005168269` |
| 3, x | `(.627761,.353479;.525,.651953)` | .0625 | `.982893→1` | `.982893→1` | `.001069188` |
| **Total** |  |  |  |  | **`.024495610`** |

En el primer estado `t=1`, acción 22 tiene continuación mayor (`1.989784`
frente a `1.962172`), pero la ganancia inmediata de 23 la compensa y deja
`Q(23)>Q(22)`. En los estados siguientes, la recompensa inmediata de 23 es
mayor y la continuación es igual o insuficiente para revertirlo. Por tanto,
este gap particular no requiere sacrificar recompensa inmediata para invertir
en desarrollo futuro: es flexibilidad de routing dependiente de la competencia
actual, con MIS-v2 como causa de la evolución de estado. La tabla identifica
exactamente los estados alcanzados por el mapa ganador que generan su
arrepentimiento; el gap global implica que los otros 1.295 mapas también
quedan estrictamente por debajo de `V_A`, pues ninguno puede superar `V_F`.

En las otras cinco configuraciones también se observó al menos una inversión
inmediata y una de Bellman en los estados inspeccionados, pero no hubo gap.
Esto es un contraejemplo finito a “reversión implica ventaja estricta”:
reversión es evidencia de preferencias dependientes del estado, no prueba de
que todos los mapas fijos deban sufrir arrepentimiento esperado. En particular,
P1 original tiene numerosas inversiones entre acciones disponibles y aun así
su mapa ganador es Bellman-suficiente; cambiar la tasa uniformemente a `.15`
o `.25` tampoco rompió esa suficiencia en esta prueba acotada.

#### Interpretación y estado de la investigación

**Establecido en el alcance exacto:** (1) MIS-v2 puede producir una inversión
inmediata y de continuación entre asignaciones para la misma tarea/periodo al
cambiar las competencias alcanzables; (2) esa propiedad no es suficiente para
un gap; y (3) la igualación inicial por habilidad, preservando medias del
equipo y manteniendo aprendizaje MIS-v2 heterogéneo, produce en la instancia
estacionaria un gap exacto `0.024495610197524442` sobre los 1.296 mapas fijos.
Los estados de arrepentimiento del mejor mapa suman ese gap. El resultado no
depende de demanda no estacionaria.

**Relación con G2/G3-H/C6.** No se reclama un nuevo teorema general ni una
ventaja universal. G2/G3-H ya caracterizan valor de desarrollo condicionado a
asignaciones futuras; C6 ya documenta desarrollo anticipatorio más routing
flexible en otra dinámica. La adición concreta es un control exacto dentro del
P1 validado que relaciona una perturbación de heterogeneidad inicial con
reversiones MIS-v2 y suficiencia/insuficiencia del mapa task-conditioned. A
diferencia de C6, aquí la ventaja observada procede del rendimiento funcional
actual en estados de competencia modificados por experiencia, no de una acción
de desarrollo separada ni de un coste explícito de invertir. Esto es una
caracterización local y reproducible, no evidencia de prevalencia.

**Límite y falsabilidad.** No se aisló causalmente la competencia de todo
efecto temporal mediante un control sin aprendizaje: `eta=0` no pertenece al
dominio MIS-v2 de este wrapper y no se introdujo una transición alternativa.
La pareja de reversión se compara a igual tiempo; el gap se verifica sobre
todos los caminos finitos y mapas fijos. Una predicción refutable para este
modelo es que, si el análisis de una configuración identifica una reversión
pero además encuentra un mapa cuyos actos son Bellman-óptimos en todo su
soporte de ocupación, entonces no puede haber gap positivo en esa
configuración. Esta predicción se confirma en los cinco controles nulos. No
se amplía el conjunto de parámetros ni se abre una nueva campaña.

<a id="p1-reactive-decomposition"></a>
### 2026-10-19 — HLS-P1: descomposición exacta frente a REACTIVE

**Alcance.** Se evaluó exactamente una configuración ya autorizada y positiva;
no se añadieron escenarios ni se modificaron políticas, modelos o resultados
guardados. Se enumeraron las 16 trayectorias de demanda IID estacionaria para
el horizonte de cuatro periodos y se reutilizaron el catálogo factible y los
solvers existentes de [`hls_p1.py`](../../src/hls/synthetic/hls_p1.py). La
comparación conserva el estado inicial `((0.525, 0.175), (0.525, 0.175))`, las
tasas MIS-v2 `((0.15, 0.15), (0.25, 0.25))` y el mapa FIXED-OPT ya optimizado
exhaustivamente entre 1.296 mapas.

**Verificación de REACTIVE.** `solve_reactive` elige, en cada periodo, la
acción del catálogo de 36 acciones que maximiza `task_performance` para la
demanda y competencia actuales. Ignora el índice temporal, no evalúa la
transición MIS-v2 ni recompensas futuras. Por tanto es reactiva a la
competencia verdadera observable, pero no anticipatoria. Comparte con HLS el
estado presente, las acciones factibles, restricciones, recompensa y
realizaciones exógenas; HLS, además, valora la continuación según la
distribución futura conocida. Ninguna política observa demandas futuras ya
realizadas. No se cambió la definición de REACTIVE.

**Valores esperados exactos.** La tabla usa la misma recompensa funcional
acumulada y el mismo soporte exógeno. El éxito es la fracción esperada de
periodos con cumplimiento funcional completo. El recurso es el consumo
esperado de esfuerzo, también registrado como exposición de desarrollo MIS-v2;
no se descuenta otra vez como coste monetario.

| Política | Valor acumulado | Tasa de éxito | Recurso/exposición esperado |
|---|---:|---:|---:|
| FIXED-OPT | 3.6990500567473568 | 0.359375 | 8.0 |
| REACTIVE | 3.698638746537539 | 0.5 | 7.6875 |
| HLS-ANTICIPATORY | 3.723545666944881 | 0.5625 | 7.71875 |

`V_R - V_F = -0.0004113102098175503`; `V_A - V_R =
0.024906920407341993`; `V_A - V_F = 0.024495610197524442`. Por tanto, en
esta configuración REACTIVE **no mejora** FIXED-OPT (opción C de la
clasificación solicitada), mientras que HLS-ANTICIPATORY supera a ambos.
La mayor tasa de éxito de REACTIVE no contradice su menor recompensa primaria:
el objetivo suma cumplimiento ponderado y truncado, no solo el indicador
binario de éxito.

**Divergencias exactas y descomposición Bellman.** Se comparó la acción de
REACTIVE con la acción HLS en cada estado alcanzado bajo REACTIVE, evaluando
ambas con la función de continuación óptima de HLS. Las masas son
probabilidades de ocupación de esos estados. La contribución ponderada es
`masa × (Δ recompensa inmediata + Δ continuación)`.

| Periodo | Demanda | Competencia actual | Acción R → HLS | Δ inmediata | Δ continuación | Masa | Contribución esperada |
|---:|---|---|---|---:|---:|---:|---:|
| 0 | y | `((.525,.175),(.525,.175))` | 29 `((0,1),(.5,.5))` → 34 `((.5,.5),(0,1))` | 0 | +0.04089378393922516 | 0.5 | +0.02044689196961258 |
| 1 | y | `((.525,.29875),(.5886379332023917,.2855290418778381))` | 29 → 34 | −0.005084983893139161 | +0.017816924567133352 | 0.25 | +0.0031829851684985477 |
| 2 | x | `((.6568125,.175),(.5886379332023917,.4641467814083786))` | 20 `((1,0),(0,.5))` → 22 `((1,0),(0,1))` | 0 | +0.010216346153846145 | 0.125 | +0.0012770432692307682 |

Las acciones distintas suman 14 ocurrencias de trayectoria, agregadas aquí
en tres pares estado-acción. No hubo divergencias explicadas solo por un
empate del valor total de Bellman. En los periodos 0 y 2 la recompensa
inmediata empata y HLS resuelve el empate a favor de mayor continuación; en
el periodo 1 sacrifica aproximadamente `0.005085` de recompensa presente,
pero obtiene aproximadamente `0.017817` más de continuación. La suma exacta
por ocupación es `−0.0012712459732847903` de recompensa inmediata más
`+0.026178166380626686` de continuación, total `+0.024906920407341895`, que
coincide con `V_A−V_R` salvo redondeo de coma flotante.

Esta es una identidad de telescopaje de ventajas de Bellman bajo la ocupación
de REACTIVE; no es una atribución causal que trate decisiones y estados
futuros como independientes. La parte inmediata no puede ser una ventaja
positiva de HLS respecto a la política que maximiza recompensa actual; el
saldo positivo procede del valor de continuación, incluida la anticipación
de la evolución MIS-v2. El resultado separa así la mera respuesta a la
competencia presente —insuficiente aquí— del uso de valor futuro. No
establece un mecanismo nuevo ni una superioridad general: es evidencia exacta
para una instancia finita, coherente con los análisis previos de anticipación
y valor de desarrollo de G2/G3-H y con la suficiencia dependiente del caso
documentada en HLS-P1.

**Estado.** Comparación exacta completada; no se propone otro experimento.
Se preservan los resultados originales de HLS-P1. La evidencia y el alcance
se añaden al registro acumulativo, sin alterar la campaña ni sus artefactos.

### 2026-10-19 — HLS-P1: Evidence of Anticipatory Organizational Advantage

**Hito científico completado; alcance acotado.** Esta síntesis enlaza, sin
sustituirlas, las entradas anteriores sobre el REFRAME del P1 soportado, la
comparación exacta validada, la condición de arrepentimiento Bellman, el
estudio estructural de seis configuraciones y la descomposición
FIXED-OPT/REACTIVE/HLS. Se preservan las conclusiones y artefactos de cada una.

**Trazabilidad:** [REFRAME inicial](#p1-initial-reframe), [comparación P1
validada](#p1-validated-comparison), [condición de arrepentimiento
Bellman](#p1-bellman-regret), [estudio de seis configuraciones](#p1-six-configurations)
y [descomposición REACTIVE](#p1-reactive-decomposition). Relaciones previas:
[G2](../theory/HLS_G2_DYNAMIC_GROUND_TRUTH.md),
[G3](../experimental_foundations/HLS_G3_ORGANIZATIONAL_VALUE_GROUND_TRUTH.md)
y [C6](../experiments/HLS_G0_C6_CLOSURE_2026-10-19.md); G3-H está recogido y
referenciado en las entradas de arrepentimiento y adaptación organizativa.

**Configuración positiva.** Competencia inicial
`((0.525, 0.175), (0.525, 0.175))`; tasas MIS-v2
`((0.15, 0.15), (0.25, 0.25))`; demanda IID estacionaria; horizonte 4. La
recompensa primaria es rendimiento funcional acumulado; tasa de éxito y
consumo de recurso se informan separadamente.

| Organización | Recompensa | Éxito | Uso de recursos |
|---|---:|---:|---:|
| FIXED-OPT | 3.6990500567473568 | 0.359375 | 8.0 |
| REACTIVE | 3.698638746537539 | 0.5 | 7.6875 |
| HLS-ANTICIPATORY | 3.723545666944881 | 0.5625 | 7.71875 |

Brechas exactas: `HLS − FIXED-OPT = 0.024495610197524442`;
`HLS − REACTIVE = 0.024906920407341993`; `REACTIVE − FIXED-OPT =
−0.0004113102098175503`. La comparación frente a FIXED-OPT conserva la
enumeración exhaustiva de los 1.296 mapas task-conditioned. En la
descomposición Bellman bajo la ocupación de REACTIVE, la contribución
inmediata es `−0.0012712459732847903`, la contribución de continuación es
`+0.026178166380626686` y el total `+0.024906920407341896`; las últimas
cifras pueden diferir por redondeo de coma flotante.

**Interpretación y límites.** (A) En la configuración inicial del piloto
validado, el resultado era `HLS-ANTICIPATORY = FIXED-OPT > REACTIVE`. (B) El
cambio controlado de estructura de competencia inicial documentado aquí
produce `HLS-ANTICIPATORY > FIXED-OPT > REACTIVE`. (C) El gap estricto frente
a FIXED-OPT se verifica respecto de toda la clase fija declarada, no de una
asignación arbitraria. (D) Frente a REACTIVE, la ventaja neta se explica por
valor futuro; hay decisiones que empatan en recompensa inmediata y favorecen
la continuación, y otra que sacrifica recompensa inmediata a cambio de mayor
continuación. (E) MIS-v2 ofrece un mecanismo plausible al hacer que las
decisiones afecten competencias futuras, pero la necesidad causal de esa
evolución para el gap de esta instancia no ha sido aislada experimentalmente.
(F) Es evidencia exacta de un problema sintético pequeño y finito: no prueba
superioridad general, escalabilidad práctica ni novedad publicable. (G) Tasa
de éxito y rendimiento acumulado parcial son objetivos distintos y pueden
ordenar las organizaciones de modo diferente: aquí REACTIVE tiene más éxito
que FIXED-OPT, pero recompensa primaria ligeramente menor.

El resultado se interpreta junto con G2/G3/G3-H y C6, ya referenciados en las
entradas analíticas anteriores: es una caracterización adicional dentro de
P1, no una afirmación de que el principio anticipatorio sea un mecanismo
nuevo. Tampoco modifica retroactivamente el REFRAME del piloto original; la
distinción reside en la instancia y el baseline fijo fuerte evaluados.

#### Estado operativo del trabajo

**COMPLETADO en el alcance P1:** formulación exacta validada; tres
organizaciones comparables; optimización de la clase fija y condición/análisis
de suficiencia mediante arrepentimiento Bellman; seis configuraciones
controladas; identificación de una configuración con gap adaptativo estricto;
y descomposición exacta REACTIVE frente a HLS. Las referencias y límites de
cada resultado permanecen en sus entradas precedentes.

**Estado histórico al redactar esta entrada:** la ablación MIS-v2 era una
comprobación propuesta, aún no ejecutada. Se completó el 20-10-2026 y se
registra por separado en el [cierre HLS-P1](#hls-p1-cierre-exacto-del-estudio-finito).

**PENDIENTE:** generalización estructural más allá de estas configuraciones;
robustez más allá de la instancia finita; validación en un problema práctico;
evaluación de complejidad/escalabilidad; y valoración de novedad frente a la
literatura. La ablación propuesta tampoco resuelve por sí sola estos puntos.

**Relación con la línea base 17–30 de octubre.** Este trabajo P1 se registra
como avance efectivamente realizado junto a las actividades planificadas; no
reemplaza el calendario original de §2 ni cambia retroactivamente sus fechas.
Los hitos operativos del 26, 27, 29 y 30 de octubre siguen pendientes según
§4: P1 añade evidencia metodológica sobre comparadores, emparejamiento y
anticipación, pero no identifica por sí mismo el problema práctico del 26,
no cierra los requisitos de reproducibilidad del 27, no constituye el
protocolo preliminar del 29 ni anticipa la decisión de cierre del 30.

### 2026-10-20 — HLS-P1: ablación causal exacta de MIS-v2

**Intervención y fidelidad.** Se reutilizó la configuración positiva
estacionaria (`C₀=((0.525,0.175),(0.525,0.175))`, perfil nominal
`eta=((0.15,0.15),(0.25,0.25))`, demanda IID, horizonte 4) y se deshabilitó
la transición de aprendizaje. La interfaz MIS-v2 canónica exige
`0 < eta < 1`; por ello `eta=0` literal no es un perfil válido. La ablación
se representó mediante su control oficial `mis_v2_transition_nk(...,
enabled=False)`, que deja cada competencia exactamente invariante y es
matemáticamente equivalente a tasa efectiva cero. Se conservó el perfil eta
nominal en la configuración y se añadió `learning_enabled` al wrapper local
P1, con valor por defecto `True`, para hacer explícito y reproducible el
control sin alterar la semántica previa.

Se mantuvieron sin cambios competencia inicial, demandas/probabilidades,
requisitos, horizonte, recompensa, catálogo de 36 acciones y presupuestos.
Las 16 trayectorias se enumeraron exhaustivamente. FIXED-OPT se volvió a
optimizar entre sus 1.296 mapas; HLS-ANTICIPATORY resolvió de nuevo la DP, y
REACTIVE se reevaluó bajo la transición invariante.

| Política | Valor esperado | Tasa de éxito | Recurso esperado |
|---|---:|---:|---:|
| FIXED-OPT | 3.211538461538461 | 0.0 | 8.0 |
| REACTIVE | 3.211538461538461 | 0.0 | 8.0 |
| HLS-ANTICIPATORY | 3.211538461538461 | 0.0 | 8.0 |

Por tanto, `V_A−V_F=0` y `V_A−V_R=0`. Frente al caso con aprendizaje
habilitado, los valores de FIXED-OPT, REACTIVE y HLS cambian respectivamente
en `−0.487511595208896`, `−0.4871002849990784` y `−0.5120072054064204`.
Los gaps habilitados eran `V_A−V_F=0.024495610197524442` y
`V_A−V_R=0.024906920407341993`; ambos desaparecen en la ablación.

**Explicación de la igualdad y éxito funcional.** Con competencia congelada,
la continuación no depende de la acción. En cada tarea, los tres métodos
seleccionan el mismo primer maximizador según el desempate determinista por
índice del catálogo: para x, acción 22 `((1,0),(0,1))`; para y, acción 29
`((0,1),(0.5,0.5))`. Hay maximizadores inmediatos empatados (x: 22, 27, 35;
y: 29, 34), pero FIXED-OPT, REACTIVE y HLS eligen el mismo representante.
No queda una diferencia de valor causada por anticipación, aprendizaje,
información distinta sobre demanda o acciones implementadas distintas. La
ley de demanda futura tampoco cambia la elección: sin transición de estado,
el valor restante es aditivo y no depende de la acción actual.

La evaluación de las 36 acciones factibles para cada tarea encontró cero
acciones que satisfagan conjuntamente todos los requisitos funcionales bajo
`C₀` congelada. Para y, además, la producción máxima posible en la
competencia y es `0.35`, inferior al requisito `0.65`. Así, la tasa de éxito
cero no se debe a un fallo de medición, sino a la imposibilidad de éxito en
esta ablación concreta con el catálogo discreto y el estado inicial fijo; la
recompensa de satisfacción parcial sigue siendo positiva.

**Interpretación causal y límites.** Para esta instancia finita, la
intervención controlada elimina la ventaja de HLS tanto frente al óptimo fijo
como frente a REACTIVE, mientras que con MIS-v2 activa existía un gap
positivo. Esto respalda que la evolución de competencia es necesaria para
el gap observado **en esta configuración y estas clases de política**; no
demuestra que MIS-v2 sea necesaria en general ni separa todos los canales
mediadores de su efecto. El resultado tampoco prueba prevalencia, ventaja
práctica ni novedad. El éxito binario permanece distinto de la recompensa
acumulada parcial.

**Validación.** Se agregó una regresión que comprueba la transición identidad,
el catálogo y conteo fijo conservados, las 16 trayectorias, los valores,
recursos, éxitos y competencias invariantes. Comando focalizado:
`PYTHONPATH=src pytest -q tests/synthetic/test_hls_p1.py tests/test_hls_lab_nk_learning_transition.py`
— **18 passed**. No se ejecutó campaña ni se sobrescribieron los resultados
anteriores; el análisis se limita a esta ablación exacta.

<a id="hls-p1-cierre-exacto-del-estudio-finito"></a>
### 2026-10-20 — HLS-P1: cierre exacto del estudio finito

**Estado: CLOSED — EXACT FINITE EXPERIMENTAL STUDY COMPLETED.** Este cierre
administrativo-científico es posterior y distinto del **REFRAME** inicial del
piloto soportado y del REFRAME de la pregunta que aquella comparación no podía
resolver. Esas decisiones históricas se preservan: el piloto original no se
reinterpreta; el estudio P1 ampliado y su control causal quedan cerrados en
el alcance exacto que efectivamente evaluaron. Trazabilidad: [REFRAME
inicial](#p1-initial-reframe), [comparación exacta validada](#p1-validated-comparison),
[condición de arrepentimiento Bellman](#p1-bellman-regret), [estudio de seis
configuraciones](#p1-six-configurations) y [descomposición frente a
REACTIVE](#p1-reactive-decomposition).

#### Hallazgos establecidos

1. En la instancia original validada, `HLS-ANTICIPATORY = FIXED-OPT >
   REACTIVE` (sección de implementación dirigida; resultado serializado en
   [`results/experiments/hls_p1_validated/results.json`](../../results/experiments/hls_p1_validated/results.json)).
2. Bajo la variación controlada de competencia inicial, con MIS-v2 activa,
   `HLS-ANTICIPATORY > FIXED-OPT > REACTIVE`:
   `V_A=3.723545666944881`, `V_F=3.6990500567473568` y
   `V_R=3.698638746537539`. El valor fijo se optimizó exhaustivamente sobre
   los 1.296 mapas task-conditioned; el gap frente a FIXED-OPT es
   `0.024495610197524442`.
3. La descomposición exacta de HLS frente a REACTIVE es contribución inmediata
   `−0.0012712459732847903` más contribución de continuación
   `+0.026178166380626686`; la suma es `+0.024906920407341895` (la cifra
   reportada como gap de valores es `+0.024906920407341993`; la diferencia de
   las últimas cifras es redondeo de coma flotante).
4. En la ablación sin aprendizaje, `V_A=V_F=V_R=3.211538461538461`, con tasa
   de éxito funcional cero para las tres políticas. La transición se desactivó
   por el mecanismo ya existente `enabled=False`, no con un literal inválido
   `eta=0`: el contrato MIS-v2 define eta estrictamente dentro de `(0,1)`.
5. En esta instancia, deshabilitar la evolución endógena elimina el gap
   anticipatorio observado. Esto apoya su dependencia causal **local a esta
   configuración y estas clases de política**, no una necesidad universal de
   MIS-v2.
6. La caracterización de arrepentimiento Bellman de la entrada “condición
   matemática para una ventaja adaptativa estricta” establece suficiencia y
   gap dentro de la formulación finita: un mapa fijo que elige acciones
   Bellman-óptimas en todo su soporte de ocupación alcanza el valor óptimo; el
   gap estricto exige arrepentimiento esperado positivo para cada mapa fijo
   admisible. No es un teorema fuera de esa formulación.

#### Conclusión científica y límites

> “In a finite heterogeneous learning system, competence evolution can make
> anticipatory organization strictly preferable to both optimized fixed
> organization and reactive allocation. In the studied instance, the
> advantage arises from future-value considerations and disappears when
> competence evolution is disabled.”

La evidencia corresponde a una instancia sintética pequeña y horizonte
finito; es exacta pero específica a las configuraciones estudiadas. No
establece un teorema de superioridad general, escalabilidad práctica ni
novedad publicable. En el control sin aprendizaje no hubo éxitos funcionales.
Tampoco implica que MIS-v2 sea universalmente necesaria para obtener una
ventaja anticipatoria. La recompensa acumulada parcial y la tasa de éxito
son métricas distintas y pueden ordenar las organizaciones de modo diferente.

#### Integración A/B/C

- **A — Problema:** agentes heterogéneos, tareas múltiples, recursos
  limitados, competencias cambiantes y demanda incierta se representaron en
  un problema sintético controlado. No es una aplicación práctica validada.
- **B — Mecanismos:** se utilizó desarrollo de competencia por experiencia
  MIS-v2. La ablación muestra el papel de la evolución de competencia en el
  gap de esta instancia. No se añade ni se afirma otro mecanismo.
- **C — Organizaciones:** se compararon mapas fijos task-conditioned
  optimizados, asignación reactiva miope y optimización anticipatoria exacta.
  La flexibilidad organizativa por sí sola no garantiza mejor rendimiento:
  en la instancia original FIXED-OPT empató con HLS y REACTIVE quedó por
  debajo; el gap aparece solo bajo la variación controlada documentada.

#### Evidencia, trazabilidad y plan vigente

Implementación y contrato local: [`src/hls/synthetic/hls_p1.py`](../../src/hls/synthetic/hls_p1.py);
regresiones: [`tests/synthetic/test_hls_p1.py`](../../tests/synthetic/test_hls_p1.py)
y `tests/test_hls_lab_nk_learning_transition.py` (**18 passed** en la
ejecución focalizada registrada el 20-10-2026). El resultado original tiene
el JSON enlazado arriba. La variación controlada y su descomposición están
registradas en las entradas de P1 de este plan; la ablación exacta está
respaldada por la regresión y los valores registrados aquí. No se creó ni se
sobrescribió un artefacto JSON adicional.

La trazabilidad teórica previa se conserva en [G2](../theory/HLS_G2_DYNAMIC_GROUND_TRUTH.md),
[G3](../experimental_foundations/HLS_G3_ORGANIZATIONAL_VALUE_GROUND_TRUTH.md),
la implementación G3-H en [`g3_h_organizational_value.py`](../../src/hls/g3_h_organizational_value.py)
y su análisis en las entradas analíticas precedentes, y el cierre de
[G0-C6](../experiments/HLS_G0_C6_CLOSURE_2026-10-19.md). Se enlaza esta
relación para contextualizar, no para reabrir dichas investigaciones.

El estudio P1 y su ablación quedan **COMPLETADOS el 20-10-2026**. Esto añade
evidencia, pero no sustituye la línea base 17–30 de octubre: el hito del 26
(matriz de reutilización) y el del 27 (reproducibilidad/comparabilidad) siguen
**PROGRAMADOS**, con los artefactos P1 como evidencia que deberá evaluarse;
no se marcan como completados. Los hitos del 29 y 30 permanecen **PENDIENTES**
según §4.

### 2026-10-20 — HLS-RQ1: selección razonada de escenario (decisión inicial)

**Pregunta:** “Under what conditions does joint coordination of learning and
task allocation improve collective performance compared with decoupled
approaches?” Esta decisión usa el marco A/B/C ya aprobado y los análisis
existentes; no reabre auditorías, no selecciona algoritmos y no autoriza
implementación ni experimentación.

#### Evaluación comparativa de escenarios

| Candidato | A — Problema y capacidades | B — Aprendizaje que cambia capacidades y vínculo con asignación | Evaluación reproducible y comparadores desacoplados fuertes | Riesgo científico principal |
|---|---|---|---|---|
| **Equipos de agentes de IA especializados** | Resolver flujos secuenciales de tareas heterogéneas (p. ej., planificación/razonamiento o tareas de software) con modelos/agentes de pericia desigual. La competencia sería calidad por agente y tipo de tarea, pero la calidad contextual de un modelo no equivale automáticamente a la competencia N×K de un agente. | MixLLM aprende/actualiza la selección y predicción del router a partir del feedback seleccionado; System-1.x aprende un controlador de descomposición fast/slow en entrenamiento. En los mecanismos revisados no se actualiza durante la operación la capacidad intrínseca de cada experto ni se transfiere habilidad entre agentes. La asignación cambia qué experto atiende la consulta, no necesariamente lo que ese experto puede hacer después. Para RQ1 sería necesario un mecanismo verificable de aprendizaje o transferencia a nivel del experto, que no está cubierto por estos métodos. | Tareas/datos: los artefactos específicos de MixLLM no estaban resueltos en el preflight; System-1.x dispone de datos/código de Maze, aunque checkpoints y camino de cómputo siguen siendo barreras. Métricas naturales: validez/calidad, coste y latencia por separado. Comparadores: mejor experto fijo por clase/contexto, router fijo entrenado en split separado y selección contextual con feedback; para estudiar aprendizaje de capacidad, comparar aprendizaje aislado frente a transferencia con igual presupuesto y datos. | Confundir aprendizaje del selector con desarrollo de capacidades de los expertos; leakage de resultados entre entrenamiento/prueba; drift o variabilidad de modelos externos. Alto riesgo de que un resultado sobre routing no responda RQ1. |
| **Producción o mantenimiento** | Asignar trabajo secuencial (incidentes, órdenes de mantenimiento o tareas de producción) a una plantilla heterogénea, con habilidades, productividad y recursos limitados, bajo cambios de mezcla y volumen de demanda. | MIS-v2 cambia competencia real por exposición productiva; la ruta N×K también contiene transferencia/enseñanza dirigida con consumo de recursos. La asignación determina qué trabajador practica qué habilidad y qué capacidad queda disponible para demanda posterior; la transferencia puede competir con producción por el mismo presupuesto. Son mecanismos existentes, aunque su combinación aún no tiene validación discriminante. Nembhard Direct es una alternativa de productividad por experiencia separada y no debe confundirse con MIS-v2. | Base reproducible adecuada: trayectorias abiertas de órdenes/incidentes con tipo, requisitos de habilidad, llegadas, duración/coste y, si se estudia transferencia, historial de formación; o simulador de workforce calibrado con parámetros/estadísticas publicados y seeds. Los informes de Chen (2018), Annear et al. (2023) y Borgonjon–Maenhout (2024) aportan modelos/problemas relacionados, pero los análisis existentes no verificaron un paquete completo de datos/código/instancias reutilizable para reproducción exacta. Comparadores: mejor mapa fijo optimizado en su clase; asignación reactiva a demanda/competencia actual; y estrategia modular que optimice formación/transferencia y asignación por separado bajo idénticos recursos, información y horizonte. P0/P1/P2 son componentes comparativos disponibles, pero P1 no es un FIXED-OPT y P2 no es un planificador exacto; Strong-SEP de RQ0 no se traslada sin demostrar equivalencia del modelo. | La validez externa depende de conseguir datos o parámetros calibrables y de representar turnos, duración, simultaneidad, costes y restricciones reales. El N×K actual usa esfuerzo divisible y una tarea por periodo, no un scheduler de órdenes de trabajo; resultados sintéticos solos no validan una planta real. |
| **Equipos de robots heterogéneos** | Coordinar robots con perfiles de movilidad, sensores o manipulación distintos para tareas cambiantes en un entorno físico compartido. La publicación Emam et al. (2020), ya analizada, es antecedente cercano de asignación adaptativa con capacidades desconocidas/evolutivas. | En el modelo revisado, la asignación/control se ajusta usando progreso observado y un estado de especialización/suitability que se actualiza con discrepancias entre progreso esperado y observado. Esto modifica el estado informativo de idoneidad; no debe presentarse sin más como mejora física de competencia por práctica. La asignación afecta a observaciones/progreso futuro y por ello a la especialización estimada; una transición real de destreza requeriría especificación independiente. | Evaluación defendible: escenario fuente de simulación/Robotarium con dinámica, tareas, progreso y parámetros congelados; el análisis previo no verificó implementación oficial lista para ejecutar y exige instanciar la dinámica/control. Comparadores: asignación fija optimizada bajo el mapa de tareas; reasignación reactiva a estado/progreso actual; y módulos de asignación y actualización de especialización optimizados por separado con el mismo controlador, seguridad e información. Las políticas deben respetar las restricciones de control del paper. | Cambiar la semántica continua de control, progreso, seguridad y estado de especialización por asignaciones N×K produciría una adaptación, no reproducción. También se corre el riesgo de llamar “aprendizaje de capacidad” a estimación de idoneidad sin evidencia de cambio de habilidad real. |

#### Decisión recomendada

**Escenario recomendado para preparar HLS-RQ1: producción o mantenimiento,
de forma condicional.** Es el candidato con mejor correspondencia entre los
tres niveles: el problema práctico requiere asignar trabajo a capacidades
heterogéneas bajo demanda y recursos; MIS-v2 y la transferencia N×K modifican
la competencia efectiva; y se puede contrastar organización conjunta con
referencias fijas, reactivas y modulares sin confundir el nivel de decisión.
Es, además, el que más directamente reutiliza el código y las validaciones
existentes (`hls_lab_nk_learning.py`, `hls_lab_nk_teaching.py`, `hls_lab_nk_environment.py`,
`hls_lab_nk_execution.py`, generadores C5 y trazas P1). P1 ya demuestra
evaluación exacta de asignación anticipatoria bajo MIS-v2 en un problema
pequeño, pero no equivale a validación industrial.

La valoración de plazo inferior a un año es **plausible pero no asegurada**:
depende de identificar un conjunto de datos abierto y documentado o de un
simulador calibrable, y de representar sus unidades/restricciones sin
distorsionar MIS-v2 o enseñanza. La opción de un modelo sintético basado en
parámetros publicados podría dar reproducibilidad causal, pero por sí sola
solo sustenta una afirmación sobre el modelo, no una validación práctica.

**Incertidumbres que quedan abiertas:** (1) no se ha verificado aquí un
dataset abierto de órdenes y habilidades con historial de aprendizaje; (2)
los modelos publicados considerados no proporcionan, según los registros
existentes, un paquete completo de instancias y código que permita réplica
exacta; (3) falta determinar si el caso elegido cabe en N×K esfuerzo-divisible
o requiere un entorno aislado de scheduling; (4) no está demostrado que la
formación/transferencia disponible tenga eficacia identificable en los datos
del dominio; (5) no se ha validado todavía un baseline modular comparable en
la ruta N×K. La ausencia de resolución de cualquiera de estas cuestiones
puede cambiar la viabilidad temporal o el tipo de afirmación científica.

#### Trazabilidad de la decisión

La conclusión se apoya en la [síntesis de evidencia](../research/HLS_SCIENTIFIC_EVIDENCE_SYNTHESIS_2026-10-20.md), la
[priorización RQ1](../research/HLS_PRIORITIZED_INVESTIGATIONS_2026-10-21.md), el
[análisis matemático de transferencia × MIS-v2 × demanda](../research/HLS_MATHEMATICAL_ANALYSIS_2026-10-22.md),
la [ontología A/B/C](../architecture/HLS_ONTOLOGY_V0_1_2026-10-23.md), la
[evaluación de capacidades y métodos](../research/HLS_LABORATORY_CAPABILITY_ASSESSMENT_2026-10-19.md),
la [selección de métodos ejecutables](../experiments/HLS_EXECUTABLE_PUBLISHED_METHOD_SELECTION_2026-10-19.md),
la [auditoría de reutilización de aprendizaje/transferencia](../experiments/HLS_ADAPTIVE_TRAINING_REUSE_AUDIT.md),
el [cierre de P1](#hls-p1-cierre-exacto-del-estudio-finito) y las decisiones
anteriores del registro. No se inicia revisión bibliográfica nueva, no se
define protocolo ni algoritmo y no se ejecuta experimento. La recomendación
es una selección de escenario para guiar la siguiente decisión PI/CE, no una
autorización de implementación.

### 2026-10-20 — HLS-RQ1: evidencia externa para producción/mantenimiento

**Estado: REFRAME — escenario prometedor; base integrada empírica todavía insuficiente.**
Esta búsqueda acotada responde a la incertidumbre señalada en la decisión
provisional de escenario: si hay evidencia y recursos reproducibles para
estudiar conjuntamente asignación de trabajo y evolución de capacidades. No
repite la selección de escenarios ni autoriza código, adaptación de modelos o
experimentos. Se separan los datos observados, los modelos científicos y los
supuestos de benchmarks sintéticos.

#### A — Escenario: datos y benchmarks de asignación

| Recurso | Qué contiene y qué falta | Reproducibilidad y relación con HLS |
|---|---|---|
| [MSLIB, biblioteca de problemas multi-skill](https://github.com/MarioVanhoucke/MSLIB-Multi-Skilled-Resource-Constrained-Project-Library) y [registro del grupo OR&S](https://www.projectmanagement.ugent.be/research/data) | Datos de proyectos, precedencias, recursos y matrices de habilidades; la versión publicada enumera 32.480 instancias en MSLIB1–4 y best-known solutions. Son instancias benchmark generadas, no observaciones longitudinales de trabajadores. La biblioteca marca MSLIB5 como empírica, pero la información revisada no permite afirmar que contenga resultados repetidos por trabajador×tarea, transiciones de competencia o tratamientos de transferencia. | Descarga, formato y soluciones de referencia disponibles; buena base para contrastar scheduling multi-skill y heterogeneidad inicial. No aporta aprendizaje por experiencia ni demanda observada a lo largo del tiempo; usarla con MIS-v2 exigiría declarar esa transición como modelo añadido, no como dato del benchmark. |
| [DWSRP-TW-SC, dataset público de workforce dinámico](https://data.mendeley.com/datasets/dbsf73xpg5/1), DOI `10.17632/dbsf73xpg5.1` | Instancias de una jornada de 540 minutos; tareas con llegada, ventanas, duración, prioridad, localización y habilidades requeridas; equipos con capacidades; algunas tareas requieren sincronizar varios equipos. La variación de “dynamism” es parte de las instancias. No registra personas reales, pericia cambiante, exposición de aprendizaje, feedback de desempeño ni transferencia. | Descarga identificable y escenarios reproducibles; útil para medir asignación bajo arribos dinámicos, ventanas y viajes. Es un benchmark de modelo, no una muestra empírica ni un benchmark de desarrollo de competencia. La unidad “team” y la logística espacial tampoco coinciden directamente con el agente-esfuerzo N×K. |
| [MPSPLib/estudio de mantenimiento pesado SNCF](https://doi.org/10.1007/s10479-023-05784-7) | El artículo modela mantenimiento de material rodante: actividades con precedencias, múltiples proyectos simultáneos, equipos multi-skill, capacidades por habilidad/periodo, instalaciones y objetivos de tardanza/duración ponderadas. Informa 10 instancias pequeñas industriales y 27 grandes instancias reales; contrasta MILP, reglas y metaheurísticas. No modela evolución de habilidades por asignación ni publica en la página consultada una descarga de las instancias SNCF. El propio artículo indica que no existía un benchmark público que reuniera proyectos múltiples y multi-skill; su prueba benchmark complementaria usa MPSPLib, construida combinando RCPSP. | Evidencia fuerte de que el problema A es industrialmente concreto y de que hay formulación/heurísticas y métricas defendibles. El artículo es reproducible como formulación y comparación metodológica en lo que respecta a sus datos publicados, pero no se verificó réplica exacta de las instancias confidenciales. Para MIS-v2 habría que agregar una dinámica que el artículo no contiene; no atribuirla a SNCF. |
| [DSLIB: proyectos reales con scheduling, riesgo y control](https://www.projectmanagement.ugent.be/research/data) | Más de 180 proyectos empresariales descargables, pero los campos descritos son red de proyecto, recursos de programación, riesgo y control; no trabajadores individualizados, habilidades, asignaciones de personas ni curvas de aprendizaje. | Datos empíricos para incertidumbre/control de proyectos, no para evolución de competencias ni workforce allocation. No es intercambiable con MSLIB/DWSRP. |

El artículo SNCF tiene especial pertinencia práctica, pero su estado de datos
no debe confundirse con disponibilidad abierta del caso industrial. MSLIB y
DWSRP dan comparabilidad computacional y escenarios repetibles, pero sus
competencias son atributos de entrada y no estados que evolucionen por
asignación. Por tanto, los recursos de asignación disponibles cubren A mejor
que la interacción A×B.

#### B — Evidencia de experiencia, productividad y transferencia

1. **Datos empíricos de trabajadores.** Nembhard, *The Effects of Task
   Complexity and Experience on Learning and Forgetting: A Field Study*
   ([Human Factors, 42(2), 272–286, DOI `10.1518/001872000779656516`](https://doi.org/10.1518/001872000779656516)) informa 2.853 episodios individuales de aprendizaje/olvido en una planta textil y encuentra efectos significativos de experiencia y complejidad (método, máquina, material) sobre las tasas estimadas. Es evidencia directa de que exposición, tarea y aprendizaje/olvido guardan relación; el artículo no es un dataset público de scheduling y el texto completo requiere acceso. No ofrece demanda, recursos, asignación contrafactual ni matriz de transferencia.
2. **Datos industriales longitudinales y curva por trabajador-tarea.** Tai et al., *Determining worker training time for precast component production in construction* ([JCEM 147(1), DOI `10.1061/(ASCE)CO.1943-7862.0001964`](https://doi.org/10.1061/%28ASCE%29CO.1943-7862.0001964); [manuscrito aceptado en PolyU](https://ira.lib.polyu.edu.hk/handle/10397/103155)), reportan cinco años de registros, 317.832 registros/datasets, 14 actividades, 4.352 participaciones de trabajadores y 492 tiempos de terminación; estiman curvas y umbrales de formación, con pendiente de curva −0,75 según el resumen institucional. El manuscrito es accesible, pero no se verificó que los microdatos sean descargables. Es evidencia empírica cuantitativa de aprendizaje de producción, no historial de asignaciones común con MSLIB ni estimación de MIS-v2.
3. **Operación de montaje instrumentada.** San-Juan, Merino-Gómez y Santos, *About human and learning factors impacting manual picking on assembly lines* ([DOI `10.1007/s00170-025-16856-2`](https://doi.org/10.1007/s00170-025-16856-2)), describen tiempos de picking/ensamblaje y volumen acumulado desagregados por trabajador y familia de producto, modos de asistencia e interrupciones. Reportan, como ejemplo para W1968 tras 48 unidades en dos turnos, `Y=108.73 X^-0.156` (learning rate 89,75 %). El artículo también advierte variabilidad por complejidad, ergonomía y fatiga. Es evidencia/medición de un prototipo de workstation, no evidencia de evaluación de políticas organizacionales ni, en las fuentes revisadas, un dataset crudo público.
4. **Transferencia organizacional.** Macher y Mowery, *“Managing” Learning by Doing: An Empirical Study in Semiconductor Manufacturing* ([DOI `10.1111/1540-5885.00036`](https://doi.org/10.1111/1540-5885.00036)), estiman mejoras de yield y cycle time tras introducir procesos y relacionan prácticas de resolución de problemas en equipo, transferencia intrafirma, IT y programación con resultados fabriles. Su nivel de análisis es de planta/organización y el resumen no identifica una transición individual trabajador×habilidad ni un coeficiente de transferencia aplicable a MIS-v2. Apoya la relevancia de transferencia como práctica organizacional, no una ley causal individual de transferencia calibrada.
5. **Mantenimiento.** El informe técnico de 1970 *Maintenance Technicians Performance Curves* (DTIC `AD0875295`, [ficha y resumen](https://dtic.minsky.ai/index/AD0875295)) describe medidas de tiempo y precisión en tareas de mantenimiento electrónico de la USAF, seleccionadas según experiencia en el sistema y ajustadas como curvas. La ficha prueba antecedente empírico directo, pero no bastó para verificar descarga íntegra de datos ni parámetros reproducibles actuales. El artículo SNCF aporta scheduling real, mientras esta ficha aporta desempeño relacionado con experiencia; no hay vínculo individual de datos entre ambos.

**Compatibilidad conceptual con MIS-v2.** La literatura ofrece evidencia de que
el tiempo/calidad de una persona en tareas repetidas cambia con la exposición,
y en varios casos se observan saturación potencial, diferencias individuales,
dependencia del tipo de tarea y olvido. Esto es compatible en sentido
cualitativo con una competencia latente por agente×skill que evoluciona con
exposición. No demuestra equivalencia paramétrica con MIS-v2: los estudios
ajustan tiempos, precisión o curvas de salida, mientras MIS-v2 actualiza una
variable de competencia normalizada mediante su ley saturante. Harían falta
una transformación de resultado a competencia, exposición comparable y
datos de seguimiento; olvido, fatiga, calidad y efectos de equipo no están
automáticamente representados por la transición actual. Ninguna fuente
revisada identifica una matriz de transferencia de habilidades a partir de
acciones de enseñanza y resultados individuales. La eficacia de transferencia
continúa siendo un supuesto/modelo experimental, no un parámetro empírico
establecido para este dominio.

#### C — Simulación disponible y límite de validez

- [Simulatte](https://simulatte.dev/) es un framework de eventos discretos
  sobre SimPy para jobs, estaciones, release/dispatching, WIP, intralogística,
  trazas y ejecuciones multi-seed; tiene versión y registro de software
  citable. Es un punto de partida para flujo fabril y demanda/colas, pero la
  documentación consultada no acredita transición MIS-v2 ni aprendizaje por
  trabajador-skill. Es una infraestructura reutilizable, no evidencia empírica
  ni un simulador ya calibrado para RQ1.
- [Manufacturing Simulator (Small)](https://github.com/SHAFNehal/manufacturing_sim_s)
  expone Workers, Machines, skills requeridas, variabilidad y KPIs de
  utilización, throughput, WIP y lead time. Su README lo caracteriza como
  software educativo no validado industrialmente; no se verificó aprendizaje
  de trabajadores por experiencia. Puede servir como prototipo de flujo, no
  como benchmark científico validado.
- [WorkforceSim](https://pypi.org/project/workforcesim/) genera perfiles y
  comportamiento de plantilla, rendimiento diario, interacciones, errores y
  registros potencialmente incompletos; sus propios datos generados son
  sintéticos y sus capacidades derivan de atributos aleatorizados. No se
  verificó un modelo de asignación a una demanda de tareas multi-skill ni una
  transición aprendida calibrada con trabajadores reales. No tratar sus
  CSV sintéticos como evidencia de learning-by-doing industrial.

Así, sí existen simuladores aprovechables para el esqueleto de producción y
flujo, pero ninguno de los revisados integra de forma ya validada la combinación
de órdenes dinámicas, competencia por trabajador×tarea, aprendizaje MIS-v2,
transferencia y costes de recursos. Usarlos requeriría definir explícitamente
qué es evidencia del simulador fuente y qué es una capa de mecanismo añadida.

#### Balance A/B/C y decisión

- **A — Escenario:** los benchmarks públicos ofrecen precedencias, habilidades,
  capacidad y/o llegadas dinámicas; el caso SNCF demuestra relevancia de
  mantenimiento multi-skill con restricciones industriales. Faltan en los
  datasets citados trayectorias abiertas que conecten órdenes, asignaciones y
  desempeño aprendido de cada trabajador.
- **B — Mecanismos:** hay evidencia empírica de learning curves a niveles
  individuales, tarea/trabajador y organizacional; la evidencia reporta también
  forgetting, fatiga y complejidad. Los parámetros de esas fuentes no son
  directamente eta MIS-v2. La transferencia tiene indicios empíricos a nivel
  organizacional, pero no una ley de transferencia por par de habilidades
  compatible y calibrada con la evidencia consultada.
- **C — Organización:** las publicaciones proporcionan modelos explícitos de
  asignación/scheduling y comparadores como reglas, MILP y metaheurísticas;
  estas comparaciones son de scheduling, no de aprendizaje conjunto. No debe
  inferirse de ellas que ya se validó una organización HLS o la ventaja de
  combinar asignación y desarrollo.

**Recomendación: REFRAME, no NO-GO.** Mantener producción/mantenimiento como
escenario práctico candidato, pero reformular el nivel de evidencia permitido:
los recursos públicos sostienen una evaluación reproducible *basada en
modelos* de asignación multi-skill y una calibración/contraste parcial de
curvas de experiencia; actualmente no sostienen una validación empírica
integrada de la coordinación conjunta MIS-v2 + asignación + transferencia.
La afirmación de que la instancia representa datos reales solo sería válida
para los campos realmente observados; combinar MSLIB/DWSRP con ecuaciones
MIS-v2 constituye un escenario híbrido/sintético. El caso SNCF no debe
etiquetarse como reproducción exacta sin acceso confirmado a sus instancias.

Antes de que el escenario pueda respaldar una afirmación empírica conjunta,
quedan por resolver: acceso público o autorizado a paneles trabajador×tarea
con exposición y resultados; correspondencia entre tiempos/calidad y estado
de competencia; tratamiento de cambios de método/equipo, fatiga y forgetting;
identificación de transferencia y sus costes; y compatibilidad de esas
unidades con el paso temporal y recursos del entorno elegido. En ausencia de
esos datos, un resultado puede ser científicamente útil como análisis de
mecanismo bajo supuestos publicados/sintéticos, pero no probar eficacia
industrial ni calibración de MIS-v2.

Esta decisión amplía, no sustituye, la recomendación condicional previa de
producción/mantenimiento. Preserva la distinción entre datos empíricos,
modelos publicados y supuestos sintéticos, y no autoriza selección final de
benchmark, protocolo, implementación o ejecución.

### 2026-10-20 — HLS-RQ1: estrategia experimental mínima propuesta

**Estado: REFRAME — GO condicionado para una prueba de mecanismo basada en
modelos; no GO todavía para una afirmación empírica industrial.** Esta entrada
responde cómo probar la coordinación conjunta con el menor cambio científico
y de software. Usa la evaluación de fuentes de la entrada inmediatamente
anterior y los contratos ya establecidos en la [priorización](../research/HLS_PRIORITIZED_INVESTIGATIONS_2026-10-21.md), el
[análisis matemático](../research/HLS_MATHEMATICAL_ANALYSIS_2026-10-22.md) y la
[ontología A/B/C](../architecture/HLS_ONTOLOGY_V0_1_2026-10-23.md). No
selecciona algoritmos, no implementa y no autoriza ejecutar.

#### Comparación de plataformas para el primer estudio

| Alternativa | Validez y reproducibilidad | Complejidad/esfuerzo | Decisión para RQ1 inicial |
|---|---|---|---|
| **Reutilizar el N×K/C5 existente** | Alta validez interna para estudiar asignación de esfuerzo, demanda exógena, competencias N×K, MIS-v2, transferencia y restricciones compartidas. Trazas y trayectorias de demanda son reproducibles. La validez externa industrial es limitada: una tarea/problema por periodo, esfuerzo divisible, sin precedencias, viaje ni turnos de scheduler. | **Bajo–medio** para diseño de instancia/control; **medio** para comparadores fuertes que aún faltan. No hay coste de portar un caso de scheduling completo. | **Recomendado.** Nombrar el dominio como problema abstracto inspirado en producción/mantenimiento; no decir que reproduce MSLIB, DWSRP o SNCF. No requiere nuevo simulador ni refactor. |
| **Extender MSLIB** | Fuerte reproducibilidad y comparabilidad en programación multi-skill; precedencias y recursos de proyecto. Es esencialmente estático y las competencias de benchmark son atributos iniciales. Insertar aprendizaje continuo y transferencia cambiaría la semántica de la instancia y no constituiría reproducción del benchmark original. | **Alto**: convertir actividades, capacidades categóricas/jerárquicas, duración y precedencias a unidades de exposición, estado y acciones dinámicas; validar que la conversión preserve el problema. | **Posponer.** Útil después como prueba de sensibilidad estructural/benchmark externo, no como primera prueba causal. |
| **Extender DWSRP-TW-SC** | Tiene arribos dinámicos, skills, tiempos, localización, ventanas y sincronización; buen ajuste a demanda online. El dataset es benchmark, no historial empírico de trabajadores; los equipos y rutas no son directamente agentes N×K con competencia continua. | **Alto–muy alto**: viajes, ventanas, servicio multi-equipo, asignación temporal y cambio de unidad/acción antes de introducir aprendizaje. | **Posponer.** Más realismo logístico no compensa el riesgo de confundir aprendizaje con conversión del problema. |
| **Construir simulador industrial nuevo** | Permitiría controlar todos los mecanismos, pero sin calibración externa sus trayectorias serían supuestos sintéticos y una nueva fuente de validez incierta. | **Muy alto**, con esfuerzo adicional de verificación, validación y mantenimiento. | **Descartar ahora.** No es necesario para probar primero la interacción de mecanismos ya implementados. |

Los benchmarks externos siguen siendo valiosos como referencias de A y como
futuras pruebas de transportabilidad. No se recomienda conectarlos aún al
runner: ninguno contiene el estado/transición que requiere B, y forzar una
traducción ahora añadiría supuestos antes de saber qué propiedad científica
se pretende preservar.

#### B — mecanismo elegido y frontera de incertidumbre

**MIS-v2 se recomienda como mecanismo primario del primer test, no como
modelo empíricamente verdadero.** Su ley `c' = 1-(1-c)exp(-lambda*x)` da un
estado de competencia acotado por agente×skill, cambio endógeno al esfuerzo
productivo, saturación y composición limpia de exposiciones. Eso permite
atribuir el aprendizaje a decisiones de asignación sin crear una variable de
experiencia adicional. Sus límites conocidos se mantienen visibles: no hay
olvido, transferencia entre agentes ni spillover entre skills dentro de
MIS-v2.

**Alternativas publicadas:** las curvas de Nembhard/Uzumeri y la evidencia
de Tai et al. o de montaje por trabajador×producto respaldan cambios de
tiempos/productividad con experiencia; las formas y unidades observadas no
son la transición MIS-v2 ni proveen todos los parámetros y trayectorias de
asignación necesarios. Nembhard Direct del repositorio es un mecanismo de
productividad por stock de experiencia `D`, separado de competencia MIS-v2.
Se recomienda conservarlo como modelo alternativo para una futura prueba de
robustez si se puede fijar una transformación/unidad válida. No combinar dos
leyes de aprendizaje en el primer estimando.

La **transferencia dirigida existente** sí es pertinente para el alcance
amplio de RQ1: actualiza una celda de competencia distinta mediante eficacia
`T` y esfuerzo docente, compite por presupuesto con producción y se aplica
después de MIS-v2. Pero no hay ley empírica abierta que calibre la matriz
`T[i,j,k]`. En el primer factorial debe tratarse como mecanismo explícito
de modelo con eficacia declarada, no como efecto industrial observado. El
contraste mínimo del aprendizaje individual puede ejecutarse sin transferencia;
para conservar la prioridad transferencia×MIS-v2, añadir el factor de
transferencia con `T` fijo y predeclarado dentro de cada réplica, incluyendo
su control cero. No estimar `T` a posteriori de los resultados.

**Dinámica verdadera y conocimiento del organizador son capas separadas.**
El mundo conserva competencia verdadera `C`, eficacia verdadera `T` y la ley
de transición elegida. La vista del organizador puede contener competencia
verdadera o una estimación `Ĉ`; nunca se debe sustituir la dinámica del mundo
por la creencia del agente. Para identificar primero el valor de coordinar
asignación y desarrollo, la comparación primaria dará a las organizaciones
el mismo estado actual y conocimiento correcto de la ley y de la distribución
de demanda, pero nunca el futuro realizado. Esto es una referencia de
información común, no un supuesto de despliegue realista. Una segunda
condición, solo después de identificar la señal, variaría error de estimación
de `C`, incertidumbre de `T` o misspecification de `lambda` **por separado**.
Combinar desde el inicio aprendizaje de capacidad, estimación imperfecta y
error de modelo impediría atribuir un gap a coordinación.

#### C — familias de organizaciones necesarias (sin definir algoritmos)

1. **FIXED-OPT:** mejor mapa task-conditioned estacionario en una clase
   declarada antes de evaluar; optimizado sobre entrenamiento/expectativa,
   no un mapa arbitrario. MIS-v2 sigue evolucionando como consecuencia de las
   asignaciones. Si hay transferencia, su regla también debe quedar dentro de
   la clase fija declarada y su inversión cuenta contra el mismo presupuesto.
2. **REACTIVE:** política que puede responder a la demanda y estado actuales
   y maximiza criterio corriente, sin valorar continuación de competencias.
   Mide adaptación al estado, no aprendizaje online de parámetros.
3. **DECOUPLED fuerte:** decisiones de asignación y de desarrollo/transferencia
   se optimizan por separado, pero con los mismos recursos, información,
   horizonte y función objetivo; la definición exacta de la separación debe
   fijarse antes de comparar. No basta con usar P1 como sustituto: su relación
   docente configurada no es un óptimo de clase. P2 es heurística adaptativa
   de selección de relación y tampoco es un planificador de horizonte.
4. **JOINT anticipatoria:** una referencia que elige asignación y acciones de
   desarrollo/transferencia valorando su efecto conjunto en desempeño futuro.
   Para una instancia diminuta puede ser exacta con horizonte finito y
   catálogo discreto; no puede acceder a demandas futuras realizadas. Si no
   existe un solver integrado MIS-v2 para esta clase, su construcción y
   validación son dependencia previa, no una capacidad ya disponible.

P0/P1/P2 actuales son útiles como controles de mecanismos y ejecución, pero
no cubren por sí solos FIXED-OPT, DECOUPLED fuerte y JOINT anticipatoria bajo
una clase común de acciones. El comparador sustantivo es `JOINT` frente al
mejor `DECOUPLED`; FIXED-OPT y REACTIVE caracterizan extremos más simples.

#### Primer experimento propuesto

**Pregunta operacional:** con demanda C5 emparejada y restricciones idénticas,
¿el acoplamiento de la decisión productiva con el desarrollo de competencias
produce más rendimiento acumulado que el mejor enfoque modular, y cómo
depende ese contraste de aprendizaje presente y de cambio en la mezcla de
tareas?

- **A — instancia:** reutilizar N×K, inicialmente 2 agentes × 2 skills,
  catálogo discreto de acciones ya existente y horizonte finito pequeño que
  mantenga headroom de aprendizaje/recompensa y permita evaluación exhaustiva
  o enumeración exacta de trayectorias. Dos controles de demanda: stationary
  y una mezcla cambiante/Markov C5. Predeclarar una estructura heterogénea
  interpretable; no calibrarla ni seleccionarla por quién gana. Este es un
  escenario de mecanismo con inspiración industrial, no una línea real.
- **B — factores:** MIS-v2 deshabilitado/activo con el mecanismo existente
  `enabled=False` para el control (no `eta=0`); transferencia ausente/eficacia
  cero versus transferencia con tensor `T` fijo y predeclarado; misma acción
  y contabilidad factible en todos los brazos. La interacción aprendizaje ×
  transferencia se informa aparte de las comparaciones de organización. Si
  conservar el catálogo común exige que las acciones docentes de control
  sigan consumiendo esfuerzo sin ganancia, registrar ese coste; no cambiarlo
  silenciosamente entre brazos.
- **C — factores:** comparar FIXED-OPT, REACTIVE, DECOUPLED fuerte y JOINT
  anticipatoria sobre los mismos escenarios y clases físicas de acción. La
  sensibilidad primaria es stationary vs. cambio de tarea; no hacer búsqueda
  de parámetros favorable.
- **Controles:** mismos `C_0`, perfiles MIS-v2, presupuesto global/individual,
  catálogo, objetivos, orden producción→MIS-v2→transferencia y realizaciones
  exógenas pareadas; streams de política separados; misma información presente
  y mismos parámetros conocidos entre políticas; sin filtrar estados futuros.
  Semillas se congelan antes de comparar. Una corrida independiente de una
  política no puede consumir aleatoriedad que cambie la demanda de otra.
- **Métricas primarias:** rendimiento funcional acumulado/deficit o producción
  útil, seleccionado de acuerdo con el reward ya especificado en N×K; éxito
  binario se reporta por separado. **Costes y diagnósticos:** esfuerzo
  productivo, esfuerzo docente, utilización de recursos, trayectoria de cada
  competencia, desempeño por tipo de tarea, gap frente a referencia exacta
  cuando disponible y coste computacional de decisión. No restar “coste de
  esfuerzo” del reward si no existe una utilidad común autorizada; reportarlo
  como eje de trade-off. Usar diferencias pareadas y sus intervalos; una
  prueba pequeña exploratoria no da base para significación confirmatoria.
- **Contraste causal/mecanicista:** reportar por separado `JOINT−DECOUPLED`
  con MIS-v2 activo y apagado; su diferencia de diferencias cuantifica cuánto
  cambia la brecha organizativa al habilitar aprendizaje en estas instancias.
  Repetir el contraste con transferencia inactiva/activa para estimar
  interacción, sin afirmar causalidad general fuera de las intervenciones
  definidas.
- **Refutación o resultado nulo informativo:** (i) JOINT no supera al
  DECOUPLED fuerte en los regímenes preregistrados pese a que el preflight
  confirma oportunidades de desarrollo y no saturación; (ii) una aparente
  ganancia persiste idéntica con mecanismos deshabilitados, sugiriendo que la
  causa es flexibilidad de routing u otra diferencia; (iii) la ganancia se
  explica por más información, recursos o acciones, en cuyo caso la comparación
  es inválida; o (iv) el beneficio de rendimiento no compensa una diferencia
  material en coste/computación bajo el criterio declarado. Ningún resultado
  refuta universalmente la utilidad de HLS.

**Amenazas principales:** elección de escalas y recompensa sintéticas;
proyección de output a “competencia”; ausencia de forgetting/fatiga;
parámetros de transferencia no calibrados; resultados saturados o task mix
no decisivo; DECOUPLED insuficientemente optimizado; clases de información o
recursos no equivalentes; explosión de estados en el solver. El primer
preflight debe verificar oportunidades de desarrollo y diferencias
decision-relevantes antes de una comparación; si no las hay, no ejecutar una
campaña mayor.

#### Esfuerzo y decisión

**Esfuerzo orientativo, no compromiso:** bajo para configurar un control
N×K/C5 y trazas; medio para optimizar FIXED-OPT y construir comparadores
REACTIVE/DECOUPLED coherentes; medio-alto para un solver JOINT exacto de MIS-v2
con transferencia. Para mantener exactitud, habría que acotar horizonte y
catálogo, y medir la explosión de estados en preflight. Orden de magnitud
preliminar: **1–2 semanas de ingeniería focalizada** para un prototipo
pequeño, pruebas de contrato y salida reproducible; no incluye validación
con datos de empresa, integración MSLIB/DWSRP ni estudio confirmatorio. Es una
estimación incierta hasta fijar catálogo y tamaño de estado.

**Decisión: REFRAME.** Proceder conceptualmente con una prueba de mecanismo
model-based reutilizando N×K, MIS-v2 y enseñanza existentes; no presentar el
resultado inicial como validación empírica de producción/mantenimiento ni como
reproducción MSLIB/DWSRP. El experimento solo puede ponerse en marcha tras
autorizar los comparadores que faltan y superar el preflight de clases,
información, recursos y headroom. Esta formulación mantiene abiertos los
resultados positivos, negativos y condicionados y no presupone superioridad
de JOINT.

### 2026-10-20 — HLS-RQ1: formalización del contraste JOINT vs DECOUPLED

**Estado: análisis conceptual completado; implementación y experimentos no
autorizados.** Esta entrada concreta RQ1 sin reabrir la auditoría del
laboratorio ni repetir HLS-P1. Se apoya en las clases y límites ya
formalizados en [el análisis matemático del 22-10](../research/HLS_MATHEMATICAL_ANALYSIS_2026-10-22.md),
[los límites de enrutamiento RQ0](../theory/rq0_routing_integration_boundaries.md)
y la definición de transferencia × MIS-v2 × demanda en
[investigaciones priorizadas](../research/HLS_PRIORITIZED_INVESTIGATIONS_2026-10-21.md).

#### Modelo común que debe fijarse antes de cualquier comparación

Para el candidato N×K, el estado verdadero previo a la decisión es
`S_t=(C_t,W_t,B_t,t)`: competencias `C_t`, estado/demanda actual `W_t`,
recursos restantes `B_t` y periodo. La información política común `I_t`
contiene exactamente las observaciones autorizadas del estado e historia; no
incluye realizaciones futuras. Para aislar el valor de coordinación, el
contraste de referencia debe dar a ambas organizaciones el mismo `I_t`,
conocimiento de la ley de transición y de la distribución de demanda, y la
misma información de oportunidades. Incertidumbre de competencia, eficacia o
modelo es otro factor, no una diferencia encubierta entre comparadores.

En cada periodo se eligen esfuerzo/asignación productiva `X_t` y acción de
enseñanza/transferencia `τ_t` dentro del mismo catálogo y presupuesto conjunto.
La transición debe ser la existente, no una ecuación nueva:
`C_t^M = M_MIS-v2(C_t,X_t; λ)` y
`C_{t+1}=H_teaching(C_t^M,τ_t;T)`, con los costes y orden temporal definidos
por N×K. La demanda evoluciona exógenamente según `W_{t+1}~P_W(.|W_t)` y no
depende de qué política haya consumido más números aleatorios. La acción
conjunta es factible solo si satisface simultáneamente los límites de
producción, enseñanza y recursos globales/individuales. El rendimiento es el
objetivo colectivo acumulado ya declarado para el mundo; costes separados se
informan como tales salvo que la especificación científica autorice
expresamente una utilidad neta. No se debe contar dos veces el consumo de
recursos.

La organización JOINT resuelve, desde el mismo estado e información,
`V_t^J(s)=max_{(x,τ)∈A(s)} E[r_t(s,x,τ)+V_{t+1}(F(s,x,τ,W'))]`, con condición
terminal común. Si el mecanismo conserva orden interno u observación de
oportunidades entre producción y enseñanza, esta expresión se expande en la
recursión por etapas correspondiente: no se permite anticipar una oportunidad
antes de observarla. Ningún decisor ve el futuro realizado.

#### Qué puede significar un DECOUPLED fuerte

**Hecho conceptual importante:** “optimizar asignación y aprendizaje por
separado” no identifica por sí solo una clase matemática. Si dos módulos
reciben la historia común completa, pueden elegir respectivamente `X_t` y
`τ_t` en cada estado, usan el mismo objetivo de horizonte completo y pueden
coordinar libremente sus reglas, la pareja de funciones
`(π_X(I_t),π_τ(I_t))` puede representar cualquier regla de acción conjunta.
Renombrar dos salidas como dos optimizadores no crea una restricción; en ese
caso las clases y sus valores coinciden por construcción.

Para hacer falsable el contraste se requiere declarar una frontera
organizativa real. Una opción defendible —**propuesta, no decisión de modelo
aprobada**— es un DECOUPLED de compromiso modular:

1. Un planificador de desarrollo elige exactamente una política/plan de
   enseñanza `δ` sobre el horizonte, maximizando el mismo rendimiento
   colectivo esperado, pero condicionado a un plan operativo de referencia
   `α₀` declarado antes de optimizar (por ejemplo, una política operacional
   de clase fija optimizada, si esa es la organización que se pretende
   modelar).
2. El plan queda comprometido para el episodio: el módulo operacional puede
   reoptimizar `X` de forma dinámica y exacta, con el mismo horizonte,
   demanda, competencias observadas, transición MIS-v2/enseñanza, objetivo y
   recursos, pero condicionado a `δ`; no puede devolver al módulo de
   desarrollo una nueva asignación para reoptimizar conjuntamente el plan.
3. Ambos módulos conocen el mismo modelo y estado observable; el límite es la
   dependencia/retroalimentación acción-condicionada y el compromiso entre
   módulos, no una desventaja de horizonte, datos, presupuesto, catálogo o
   esfuerzo computacional impuesto solo al DECOUPLED.

Formalmente, primero `δ*∈argmax_{δ∈Π_D}J(α₀,δ)` y después
`α*(δ*)∈argmax_{α∈Π_X}J(α,δ*)`; se informa el protocolo de desempate y se
congela `α₀`. Cada subproblema puede resolverse exactamente en su clase. La
brecha mide el coste de esa frontera/compromiso, no una propiedad universal
de toda separación. Para considerarlo comparador científicamente fuerte, la
elección de `α₀`, el alcance de contingencias permitidas en `δ` y la
interpretación organizativa del compromiso deben justificarse antes de ver
resultados. Si no hay justificación operacional para esa frontera, no debe
presentarse como baseline natural.

El **Strong-SEP canónico de RQ0** es un comparador adicional ya definido,
pero no es sinónimo de este DECOUPLED: restringe el enrutamiento al conjunto
de maximizadores de recompensa inmediata `G(s)` y optimiza el desarrollo
después de la ruta/oportunidad observada. Su gap frente a JOINT ya tiene
criterio exacto y casos RQ0; volver a ejecutar solo ese contraste no aportaría
por sí mismo una nueva prueba de RQ1. SEP-Ω marca precisamente la frontera en
la que el módulo de ruta recibe información exacta suficiente de continuación
y puede recuperar la decisión conjunta.

#### Inclusión, igualdad y condición de diferencia

Con un compromiso DECOUPLED fijo y una clase de acciones factibles común,
JOINT puede imitar la secuencia modular, por lo que
`Π_D⊆Π_J` y `J_D≤J_J`. En un problema finito con máximos alcanzados, hay
igualdad si y solo si existe una política óptima JOINT que respeta el
compromiso DECOUPLED; hay gap estricto solo si toda política JOINT óptima
requiere, en algún historial alcanzable de probabilidad positiva, cambiar el
plan de desarrollo en función de la asignación/continuación que la frontera
modular bloquea (o recíprocamente). Esta es una condición de soporte y
regret, no basta con observar acciones distintas ni trayectorias de
competencia diferentes. Se conservan todos los empates del DECOUPLED y se
compara contra su mejor valor admisible.

Las clases pueden coincidir en valor cuando no hay aprendizaje con valor
futuro; cuando el desarrollo es nulo, irrelevante para las tareas alcanzables
o independiente de `X`; cuando las asignaciones óptimas no cambian a través
de los estados alcanzables; cuando el plan comprometido ya es compatible con
una política JOINT óptima; o cuando la frontera se amplía con una señal
acción-condicionada de continuación suficiente (caso SEP-Ω). Si se permite
retroalimentación completa y reoptimización conjunta a ambos módulos, las
clases pueden ser idénticas y el contraste deja de estar definido. Los
recursos compartidos y la dependencia MIS-v2 `C_{t+1}` de `X_t` son fuentes
posibles de acoplamiento, no garantía de un gap: debe demostrarse que inducen
regret esperado positivo en estados alcanzables.

#### Qué sería nuevo respecto a HLS-P1 y recomendación

HLS-P1 ya comparó FIXED-OPT, REACTIVE y ANTICIPATORY, mostró un gap exacto en
una instancia finita y mediante ablación encontró que allí desaparece al
desactivar la evolución de competencia. Eso no estima el valor de una
frontera modular con el mismo plan de desarrollo, horizonte, información,
recursos y demanda. El resultado nuevo requeriría comparar JOINT con el
DECOUPLED de compromiso anterior, informar su gap y coste, y demostrar por
trazas/regret que la diferencia proviene de dependencia acción-condicionada
entre asignación y desarrollo. En el control de aprendizaje apagado, el
contraste JOINT–DECOUPLED debería colapsar si esa es la explicación; no se
presupone este resultado. RQ0/Strong-SEP, G2/G3-H y C6 siguen como evidencia
previa sobre anticipación y clases restringidas, no se reabren aquí.

**Decisión: REFRAME antes de implementación.** La pregunta amplia “joint
frente a decoupled” no es todavía un estimando único. Existe una distinción
matemática defendible solo al especificar una frontera organizativa concreta
(compromiso, información de continuación o ausencia de realimentación entre
módulos). Se recomienda reformular RQ1 como: **“¿Cuál es el valor y el coste
de permitir retroalimentación acción-condicionada entre el plan de
desarrollo/transferencia y la asignación operacional, frente a una
organización modular que compromete su plan bajo el mismo modelo y recursos?”**
Antes de experimentar, debe aprobarse y justificarse el contrato DECOUPLED
—en especial `α₀` y el compromiso—; si no representa una organización
plausible, se abandona ese contraste y no se etiqueta un baseline debilitado
como “DECOUPLED fuerte”. No se implementó ni ejecutó nada en esta decisión.

### 2026-10-20 — HLS-RQ1: piloto ejecutado de aprendizaje MIS-v2 y organización

**Estado: PILOTO ACOTADO EJECUTADO; resultado nulo entre organizaciones.**
Se implementó un runner específico, reutilizando C5, geometría/restricciones
N×K, producción y MIS-v2. No se modificaron los mecanismos centrales ni se
ejecutó una campaña amplia. Artefactos completos: [resultados reproducibles
JSON](../../results/experiments/hls_rq1_learning_organization/results.json)
y [visualización comparativa](../../results/experiments/hls_rq1_learning_organization/comparison.png).
El código ejecutable está en [run_hls_rq1_learning_organization.py](../../experiments/run_hls_rq1_learning_organization.py)
y las pruebas específicas en [test_hls_rq1_learning_organization.py](../../tests/synthetic/test_hls_rq1_learning_organization.py).
El solver P1 anterior no se reutilizó directamente porque su escenario está
restringido a dos tareas; sí se reutilizaron las transiciones y contratos N×K/C5.

#### Configuración y políticas realmente ejecutadas

- **Escenario:** cinco agentes (`A`–`E`), tres tareas/habilidades
  (`diagnostics`, `repair`, `inspection`), una tarea por periodo y 100
  periodos. Demanda C5 `NonStationaryTaskDemand`: probabilidades
  `(0.70,0.20,0.10)` en periodos 0–29, `(0.20,0.60,0.20)` en 30–59 y
  `(0.15,0.20,0.65)` en 60–99. La trayectoria se genera antes de ejecutar
  políticas y se comparte por semilla.
- **Heterogeneidad inicial** (filas agentes, columnas tareas):
  `((0.78,0.31,0.27),(0.29,0.76,0.34),(0.32,0.37,0.79),
  (0.60,0.57,0.41),(0.40,0.59,0.62))`.
- **MIS-v2:** `eta=((0.09,0.10,0.08),(0.08,0.09,0.10),
  (0.10,0.08,0.09),(0.13,0.12,0.11),(0.12,0.10,0.14))`; la exposición
  productiva actualiza la celda agente-habilidad asignada mediante la
  transición existente. Transferencia desactivada.
- **Acciones y recursos comunes:** 10 acciones por tarea (uno de cinco
  agentes, esfuerzo 0.5 o 1.0); presupuesto colectivo y límite individual
  por periodo 1.0, presupuesto de la tarea 1.0. La recompensa es
  cumplimiento fraccional truncado del requisito activo `0.88`; éxito se
  registra aparte y el esfuerzo se reporta, no se resta dos veces.
- **FIXED-OPT (train-optimum):** enumeración exhaustiva de los 1.000 mapas
  tarea→(agente, esfuerzo), optimizando reward medio sobre 10 semillas de
  calibración (`1–10`) y evaluando en semillas disjuntas (`101–120`). Por
  rigor, es el óptimo empírico de esa muestra/clase, no el óptimo esperado
  poblacional. Mapa seleccionado: diagnostics→A/1.0, repair→B/1.0,
  inspection→C/1.0.
- **REACTIVE:** en cada periodo elige la acción de mayor recompensa actual
  usando la competencia verdadera observable; desempata por menor esfuerzo y
  luego orden de agente. No valora continuación.
- **ANTICIPATORY:** programación dinámica exacta receding-horizon de dos
  periodos (actual y siguiente), usando la distribución futura declarada,
  la competencia actual y la transición MIS-v2. No observa demandas futuras
  realizadas. Su horizonte es limitado y no es el óptimo de 100 periodos.
- Información presente, recursos, acción factible, demanda C5 y oportunidad
  determinista de aprendizaje fueron iguales. Las políticas no tienen
  aleatoriedad interna; las semillas de demanda se emparejaron.

#### Resultados de evaluación

20 semillas × 100 periodos (2.000 decisiones por organización):

| Organización | Reward acumulado medio (SD entre semillas) | Tasa de éxito por tarea | Esfuerzo medio total | Diferencias de acción vs. las otras |
|---|---:|---:|---:|---:|
| FIXED-OPT (train-optimum) | 98.77020926533908 (0.0) | 0.79 | 100.0 | 0 |
| REACTIVE | 98.77020926533908 (0.0) | 0.79 | 100.0 | 0 |
| ANTICIPATORY (horizonte 2) | 98.77020926533908 (0.0) | 0.79 | 100.0 | 0 |

Las tres diferencias pareadas medias son exactamente `0.0`. Las 20
trayectorias de demanda sí son distintas. La competencia final media fue
`A=(0.989110,0.310000,0.270000)`,
`B=(0.290000,0.987731,0.340000)`,
`C=(0.320000,0.370000,0.991151)`, mientras D y E conservaron las celdas no
expuestas. La tasa de éxito temporal varía durante los cambios de mezcla y
alcanza 1 en el tramo final; el panel de la figura muestra también la
evolución de reward, competencia media y recursos. Las trazas completas por
semilla conservan tareas, asignación, esfuerzo, éxito, reward y matrices de
competencia pre/post.

**Interpretación limitada:** en esta configuración, el mapa fijo escogió un
especialista distinto para cada habilidad; REACTIVE y ANTICIPATORY
coincidieron con él en todas las decisiones evaluadas. Por tanto, el runner
compara correctamente las tres reglas y muestra aprendizaje dependiente de
asignaciones, pero este resultado no demuestra ventaja organizativa ni
discrimina el valor de anticipar. La recompensa se acerca al techo y las
competencias de los tres especialistas se aproximan a uno; la dimensión
entrenada favorece el ajuste del mapa fijo. No se alteró el escenario para
forzar una victoria adaptativa. Es un piloto sintético no calibrado con datos
industriales; tampoco es inferencia confirmatoria (20 semillas). La
restricción de una tarea por periodo y esfuerzo por agente no representa
planificación simultánea de órdenes ni costes monetarios.

#### Reproducibilidad y validación

Comando de ejecución utilizado: `PYTHONPATH=src python
experiments/run_hls_rq1_learning_organization.py`. El runner no sobrescribe
resultados; para repetirlo hay que indicar rutas de salida nuevas mediante
`--output` y `--plot`. Pruebas focalizadas: 70 pasaron, incluidas tres pruebas
del piloto sobre replay C5, actualización MIS-v2, reproducción determinista,
éxito y conservación de recursos, más pruebas existentes de ambiente,
aprendizaje y demanda C5. `git diff --check` pasó. No se generaron archivos
JSON por episodio: todas las semillas y trazas están en un único JSON.

**Cierre de este objetivo inmediato:** las tres organizaciones se ejecutaron
de principio a fin bajo escenarios emparejados y con trazabilidad suficiente.
El resultado es nulo y específico a la configuración. No prueba que las
políticas sean equivalentes en general ni que un horizonte mayor no importe;
no se autoriza inferirlo de este piloto.

### 2026-10-20 — Integración y validación acotada de EXP3

**Estado: IMPLEMENTACIÓN Y EVALUACIÓN PILOTO COMPLETADAS.** El piloto
HLS-RQ1 5×3×100 permanece cerrado; no se cambiaron sus políticas ni sus
artefactos. Se integró una implementación aislada de EXP3 en
[`src/hls/exp3.py`](../../src/hls/exp3.py), con runner
[`run_hls_exp3_validation.py`](../../experiments/run_hls_exp3_validation.py),
pruebas focalizadas en [`test_exp3.py`](../../tests/test_exp3.py) y un único
artefacto agregado de resultados en
[`results.json`](../../results/experiments/hls_exp3_validation/results.json).
La formulación seguida es Auer, Cesa-Bianchi, Freund y Schapire (2002),
Figura 1, p. 53, Teorema 3.1 y Corolario 3.2, DOI
[10.1137/S0097539701398375](https://doi.org/10.1137/S0097539701398375).

#### Implementación y verificación del algoritmo

La política mantiene pesos positivos; calcula
`p_i=(1−γ)w_i/Σ_j w_j + γ/K`; selecciona estocásticamente un brazo; recibe
únicamente su recompensa escalar observada `x∈[0,1]`; calcula
`x̂_i=x/p_i` para el brazo elegido y cero para los demás; y aplica
`w_i←w_i exp(γ x̂_i/K)`. El reescalado común de pesos evita crecimiento
numérico y no cambia la distribución. La API impone una selección seguida de
una única observación, sin aceptar el vector contrafactual de recompensas.
Para el piloto se utilizó la regla del Corolario 3.2 con `g=T`:
`γ=min(1,sqrt(K ln(K)/((e−1)T)))`.

Las **11 pruebas EXP3 pasaron**. Cubren normalización y masa mínima de
exploración, fórmula de actualización, repetibilidad con semilla, dominio y
acotación de recompensas, rechazo de vectores no observados y orden de
selección/feedback. Como comprobación separada de implementación, en el
bandit determinista de 3 brazos con recompensas `(1,0,0)`, horizonte 300 y
40 semillas, EXP3 obtuvo media `246.95/300`, frente a `99.725/300` de la
referencia uniforme y regret débil medio `53.05` frente a `200.275` de la
uniforme. Esta comprobación verifica comportamiento en un caso conocido; no
es evidencia de desempeño general ni un resultado de HLS.

#### Evaluación HLS compatible

Se evaluó la abstracción mínima “un trabajo unitario repetido; elegir un
agente heterogéneo”: tres agentes con probabilidades de éxito constantes
`(0.80, 0.55, 0.35)`, recompensa Bernoulli acotada `[0,1]`, horizonte 300,
20 trayectorias y `γ=0.07996041282317397`. Las capacidades no evolucionan;
no se usaron MIS-v2, transferencia ni asignación N×K. Para cada semilla, el
entorno generó de antemano los resultados potenciales por agente y periodo;
EXP3 y UNIFORM recibieron los mismos resultados exógenos, pero sus flujos de
aleatoriedad de política fueron independientes. EXP3 observó solamente la
recompensa del agente seleccionado.

| Comparación | Recompensa acumulada media (SD entre 20 trayectorias) | Regret medio frente al mejor agente fijo retrospectivo | Selecciones medias (agente 0, 1, 2) |
|---|---:|---:|---:|
| EXP3 | `204.9 (9.4863)` | `37.7` | `(184.45, 68.50, 47.05)` |
| UNIFORM | `170.7 (6.1138)` | `71.9` | `(99.10, 100.60, 100.30)` |
| BEST_FIXED_RETROSPECTIVE | `242.6 (7.7351)` | — | — |

La diferencia pareada EXP3−UNIFORM fue media `+34.2`, SD `11.423` por
trayectoria. BEST_FIXED_RETROSPECTIVE elige, después de observar toda la
trayectoria, el brazo constante con mayor suma; por tanto, es un comparador
diagnóstico/oráculo retrospectivo, no una política desplegable. Se guardaron
en el JSON agregado las semillas, recompensa por política, regret, selección
por agente, probabilidades antes/después de cada elección y decisiones por
periodo. El tiempo medido dentro del bucle fue, en promedio, aproximadamente
`0.000393 s` por ejecución completa de 300 pasos de EXP3 y `0.000061 s` para
UNIFORM en esta máquina; es una medición indicativa dependiente del entorno,
no una comparación de presupuestos computacionales igualados.

#### Interpretación y límites

La implementación respeta el feedback parcial y la actualización EXP3; el
caso determinista muestra la respuesta esperada a un brazo claramente mejor.
En el pequeño caso HLS, EXP3 superó a UNIFORM en recompensa media y redujo el
regret observado frente al mejor brazo retrospectivo, pero quedó por debajo
de esa referencia. Esto es una comparación piloto reproducible, no una
afirmación de significancia ni una validación de ventaja en problemas HLS
generales. El modelo representa una sola clase de tarea repetida y
capacidades constantes; no prueba demandas multi-tarea, aprendizaje de
competencia, no estacionariedad, selección contextual ni interacción con
políticas organizativas. La interfaz P0/P1/P2 y la interfaz N×K existentes
devuelven acciones de producción/desarrollo, no una selección escalar de
brazo; por eso EXP3 vive como módulo específico bajo `src/hls` y no se
modificaron esos mecanismos ni se introdujo una arquitectura general.

**Reproducción:**
`PYTHONPATH=src pytest -q tests/test_exp3.py`
`PYTHONPATH=src python experiments/run_hls_exp3_validation.py`
El segundo comando genera un único JSON con las 20 trayectorias. No se
ejecutó una campaña extensa, no se generaron archivos por episodio y no se
modificó ni reabrió el piloto HLS-RQ1 5×3×100.

### 2026-10-20 — Segunda integración externa: LinUCB contextual

**Estado: IMPLEMENTACIÓN Y VALIDACIÓN PILOTO COMPLETADAS.** EXP3 conserva su
estado de integración cerrada: no se modificó su módulo, prueba, runner ni
artefacto original. EXP3 solo se ejecutó como comparador en el nuevo replay
contextual exigido para LinUCB. Código nuevo: [`src/hls/linucb.py`](../../src/hls/linucb.py),
runner [`run_hls_linucb_validation.py`](../../experiments/run_hls_linucb_validation.py),
pruebas [`test_linucb.py`](../../tests/test_linucb.py) y resultados agregados
[`results.json`](../../results/experiments/hls_linucb_validation/results.json).

La variante es **LinUCB con modelos lineales disjuntos**, Li et al. (2010),
§3.1, Ecs. (2)–(5), Algoritmo 1 ([arXiv](https://arxiv.org/abs/1003.0146),
[WWW 2010 DOI 10.1145/1772690.1772758](https://doi.org/10.1145/1772690.1772758)).
Por agente/brazo `a`, el estado de la política es `A_a=I` y `b_a=0`; calcula
`θ̂_a=A_a⁻¹b_a` y
`UCB_a=x_{t,a}ᵀθ̂_a+α√(x_{t,a}ᵀA_a⁻¹x_{t,a})`, elige el máximo (empates:
menor índice), y actualiza únicamente el brazo elegido:
`A_a←A_a+x xᵀ`, `b_a←b_a+r x`. Se usó el coeficiente de la Ec. (4) con
`δ=0.05`, es decir `α=1+√(ln(2/δ)/2)≈2.358`. Esto es una implementación del
algoritmo publicado en un entorno pequeño, no reproducción del experimento
Yahoo! ni del resultado publicado de 12.5%.

#### Correspondencia con la ontología HLS A/B/C

La correspondencia se contrasta con
[`HLS_ONTOLOGY_V0_1_2026-10-23.md`](../../docs/architecture/HLS_ONTOLOGY_V0_1_2026-10-23.md).
En ambos algoritmos “aprendizaje” significa **actualización de la política
de selección**, no aprendizaje de las competencias físicas de los agentes.
Las competencias son probabilidades de éxito fijas por agente y tarea y no
cambian durante estas ejecuciones.

| Nivel | EXP3 ya integrado | LinUCB en esta integración |
|---|---|---|
| **A — Escenario** | Un trabajo unitario repetido y agentes como brazos; recompensa escalar acotada. | Tres tipos observables de tarea, tres agentes y demanda C5 no estacionaria; contexto one-hot de la tarea. Recompensa Bernoulli determinada por la competencia fija agente-tarea. |
| **B — Mecanismos** | Estado interno `w_i`; observación solo de la recompensa del agente elegido; estimador `r/p_i` y actualización exponencial. No actualiza competencia, experiencia ni transferencia. | Estado interno por agente `A_a,b_a,θ̂_a`; observa características de todos los brazos y solo la recompensa del elegido; actualiza regresión ridge/UCB. No actualiza competencia, MIS-v2, experiencia ni transferencia. |
| **C — Organización** | Selector estocástico no contextual sobre brazos/agentes, con mezcla uniforme `γ`. | Selector contextual determinista UCB: el agente se elige usando tarea actual, modelo estimado e incertidumbre. |

**Contratos observados y límite de integración:** los dos selectores reciben
un contexto/semilla de azar mediante contratos experimentales simples
`select`/`observe_reward`. EXP3 conserva su módulo original. LinUCB usa
`select(contextos_por_agente)`/`observe_reward(recompensa)`. En cambio, el
contrato N×K real `NKCoordinationPolicy.choose(view, memory, parameters)`
devuelve una acción conjunta de producción/enseñanza `JointActionNK`, no un
índice de agente; ninguno de estos selectores se presenta como adaptador de
ese contrato. La evaluación reutiliza `NonStationaryTaskDemand` de C5,
`WorldState`, replay exógeno y el formato de trazas, sin modificar N×K ni
crear una arquitectura común nueva.

| Algoritmo | Estado/observación y acción | Supuestos y restricciones | Métricas/comparadores | Componentes HLS que no implementa |
|---|---|---|---|---|
| EXP3 | Pesos positivos; contexto ignorado; feedback escalar del agente elegido; selecciona un agente. | Recompensa `[0,1]`; actualización adversarial no contextual; todos los brazos disponibles. | Reward, weak regret frente al mejor brazo constante retrospectivo, probabilidades y decisiones; uniforme y referencias fijas. | No modela task features, competencia, MIS-v2, enseñanza, capacidad conjunta ni restricciones de esfuerzo. |
| LinUCB-disjoint | `A_a,b_a`; características de cada agente bajo la tarea actual; feedback escalar solo del elegido; selecciona `argmax UCB`. | Esperanza de recompensa lineal en características; parámetros independientes por agente; una tarea/decisión por periodo y reward `[0,1]`. Cotas estadísticas requieren los supuestos del artículo. | Reward, pseudo-regret frente al oráculo contextual de media conocida, regret frente a mapas fijos retrospectivos, UCB, coeficientes, decisiones y tiempo; EXP3 y uniforme. | No actualiza las capacidades físicas; no enseña ni transfiere; no asigna tareas concurrentes, no modela esfuerzo/coste ni ejecuta la política N×K. |

#### Validación del algoritmo publicado

Las **12 pruebas LinUCB pasaron**. Verifican la estimación ridge, el término
de confianza y la actualización `A,b` con valores calculados a mano, que solo
cambia el modelo del brazo seleccionado, rechazo de feedback vectorial/no
observado y recompensas no acotadas, repetibilidad, desempate determinista,
dimensiones válidas y replay C5 reproducible. En una prueba contextual
determinista con tres contextos one-hot y un agente óptimo distinto por
contexto, el algoritmo aprendió las tres preferencias tras entrenamiento
repetido. Esto valida el mecanismo de selección, no competencias ni
superioridad general.

#### Evaluación HLS contextual emparejada

Se ejecutaron 20 semillas × 300 periodos. Competencias fijas
`C[agente,tarea]`:
`((.85,.20,.20),(.20,.85,.20),(.20,.20,.85))`; tres fases de demanda C5 con
distribuciones `(0.70,0.20,0.10)`, `(0.10,0.20,0.70)` y `(0.20,0.70,0.10)`.
Las características eran el vector one-hot de tarea, compartido por los
agentes candidatos. Los resultados potenciales Bernoulli por agente y
periodo se generaron antes de ejecutar políticas y se compartieron entre
ellas. LinUCB observa el contexto actual y la recompensa de su agente elegido;
EXP3 y uniforme no reciben el contexto (EXP3 se mantuvo en su definición
context-free). El oráculo conoce las medias verdaderas y selecciona el agente
de mayor recompensa esperada para cada tarea, pero no mira el resultado
Bernoulli realizado. Las semillas de política son independientes de las del
entorno.

| Método/referencia | Reward acumulado medio (SD, 20 trayectorias) | Pseudo-regret medio vs. oráculo contextual | Diferencia realizada: mejor mapa retrospectivo menos método | Diferencia realizada: mejor agente constante menos método | Tiempo selector medio por ejecución de 300 pasos |
|---|---:|---:|---:|---:|---:|
| LinUCB-disjoint | `229.55 (6.386)` | `25.0575` | `23.50` | `-95.15` | `0.00938 s` |
| EXP3 | `125.85 (8.368)` | `130.3900` | `127.20` | `8.55` | `0.000527 s` |
| Uniforme | `125.15 (7.095)` | `129.3500` | `127.90` | `9.25` | `0.000095 s` |
| Oráculo contextual (referencia) | `253.05 (5.698)` | `0` | `0` | `-118.65` | no aplica |
| Mejor mapa fijo tarea→agente (retrospectivo) | `253.05 (5.698)` | — | `0` | `-118.65` | no aplica |
| Mejor agente constante (retrospectivo) | `134.40 (5.491)` | — | `118.65` | `0` | no aplica |

La exactitud de elección LinUCB frente al agente de mayor media en el
contexto fue `0.8715`. El mapa fijo retrospectivo fue `(agent_0, agent_1,
agent_2)` para estas competencias, y coincide en reward con el oráculo porque
la mejor elección por contexto es una asignación estacionaria task→agent en
este modelo. Es una referencia de clase calculada con resultados potenciales
de evaluación, no una política desplegable. EXP3 se mantiene como comparador
context-free; su resultado en esta tabla pertenece al nuevo replay emparejado,
no modifica ni amplía la campaña EXP3 archivada.

**Interpretación y límites:** en este caso sintético, con competencias
especializadas, LinUCB aprovecha el contexto y supera en reward a EXP3 y a
uniforme; aún no alcanza la referencia contextual fija/oráculo. El resultado
no estima una ventaja en escenarios generales ni reproduce el dataset ni la
evaluación Yahoo! del artículo. La comparación da a LinUCB información
contextual explícita y mantiene EXP3 context-free según su algoritmo; este
contraste mide también el valor de usar contexto. Los tiempos son de esta
ejecución local y no están igualados por presupuesto computacional. No se
evalúan capacidades que cambian, MIS-v2, transferencia, aprendizaje de
competencias, restricciones de recursos ni asignaciones N×K simultáneas.

**Reproducción:**
`PYTHONPATH=src pytest -q tests/test_linucb.py`
`PYTHONPATH=src python experiments/run_hls_linucb_validation.py`
Se conserva un único JSON agregado con semillas, contextos, potenciales
evaluator-only, score UCB, estados de la política, decisiones, recompensas,
regrets y tiempos. No se modificó el resultado EXP3 previo ni se generaron
archivos por episodio.

### 2026-10-20 — Interacción LinUCB × MIS-v2 (primer piloto acotado)

**Estado:** ejecutado; evidencia exploratoria emparejada, sin nueva campaña.
Se reutilizaron LinUCB-disjoint, MIS-v2, C5 y el ranking productivo P0
existentes. No se modificaron sus ecuaciones ni los resultados anteriores de
EXP3, LinUCB o del piloto HLS-RQ1.

#### Correspondencia A/B/C y contratos observados

La correspondencia sigue
[`HLS_ONTOLOGY_V0_1_2026-10-23.md`](../../docs/architecture/HLS_ONTOLOGY_V0_1_2026-10-23.md)
y se comprobó contra las interfaces ejecutadas:

| Nivel | Instanciación en este piloto |
|---|---|
| **A — Escenario** | Tres agentes, tres tipos de tarea, 300 periodos, demanda C5 no estacionaria en tres fases, una asignación unitaria por periodo y presupuesto colectivo/individual de una unidad. Los parámetros C5 son `(0.70,0.20,0.10)`, `(0.10,0.20,0.70)` y `(0.20,0.70,0.10)`, repetidos durante 100 periodos por fase. |
| **B — Mecanismos** | En la condición constante se usa el mismo estado inicial sin transición. En la condición evolutiva se aplica después de cada tarea la transición MIS-v2 existente, con `eta=0.15` para cada celda agente-tarea y `enabled=True`; solo recibe exposición la celda asignada. La transferencia está desactivada/no modelada. |
| **C — Organizaciones** | `LINUCB`: LinUCB-disjoint aprende parámetros de selección por agente con feedback de la recompensa elegida. `FIXED_SPECIALIZED`: mapa predeclarado tarea_i→agente_i. `REACTIVE_P0`: P0 selecciona la acción de producción de valor inmediato máximo según las competencias actuales, sin continuación ni actualización de política. |

Se conservaron separados los dos aprendizajes: LinUCB actualiza `A_a`, `b_a`
y `theta_hat_a`; MIS-v2 modifica la competencia física `C[i,k]`. No hay
estimación oculta de competencia en este piloto: el estado actual de
competencia es perfectamente observable y común a las tres organizaciones.
Cada brazo LinUCB recibe un contexto de seis características: identidad de
tarea one-hot más las tres competencias actuales para esa tarea. P0 usa ese
mismo estado observable en su ranking inmediato; la organización fija dispone
de la información, pero ignora el estado al decidir. LinUCB no recibe demanda
futura, outcomes no seleccionados ni continuación MIS-v2. Tras elegir, solo se
le entrega su recompensa escalar. Las recompensas potenciales se muestrean
mediante shocks uniformes pre-generados por semilla-periodo-agente y solo se
revela el resultado del agente elegido.

**Límite de integración:** la llamada real es
`LinUCBDisjoint.select(contexts)` / `observe_reward(reward)`. P0 se reutiliza
mediante `P0ProductionOnlyNK.choose(feasible_actions, competence, problem)`;
el catálogo del piloto restringe esa llamada existente a las tres acciones
de un agente por tarea. MIS-v2 se llama mediante
`mis_v2_transition_nk(..., enabled=...)`. El contrato de coordinación N×K
`NKCoordinationPolicy.choose(...) -> JointActionNK` no es el contrato de
LinUCB ni de este selector escalar; no se añadió un adaptador general ni se
afirma que el piloto sea ejecución del runner N×K integrado.

#### Diseño, replay y evidencia

Se cruzaron competencia constante/evolutiva con las tres organizaciones:
`2 condiciones × 3 políticas × 20 semillas × 300 periodos` (36.000 decisiones
evaluadas). Para cada semilla se generaron una única vez la secuencia de
demanda C5 y los shocks de recompensa; ambas condiciones y las tres políticas
reutilizan los mismos datos exógenos. El catálogo factible y el recurso usado
son idénticos: una unidad en cada periodo, 300 por ejecución. El reward es
éxito Bernoulli en `[0,1]`, con probabilidad igual a la competencia actual
del agente en la tarea. Cada asignación genera una unidad de exposición MIS-v2
en la condición evolutiva; no existe un coste de desarrollo separado del
recurso de producción. La matriz inicial fue
`((.85,.20,.20),(.20,.85,.20),(.20,.20,.85))`; `eta=.15` en todas las nueve
celdas. La esperanza de reward es lineal en el contexto porque cada brazo
puede seleccionar la característica de competencia correspondiente; el
resultado no equivale a dar a LinUCB el feedback de los brazos no elegidos.

| Competencia | Organización | Reward acumulado medio (SD) | Tasa de éxito media | Competencia final media, diagonal/especialidad |
|---|---|---:|---:|---|
| Constante | LINUCB | 225.70 (5.877) | 0.7523 | sin cambios: diagonal 0.85 |
| Constante | FIXED_SPECIALIZED | 253.05 (5.698) | 0.8435 | sin cambios: diagonal 0.85 |
| Constante | REACTIVE_P0 | 253.05 (5.698) | 0.8435 | sin cambios: diagonal 0.85 |
| MIS-v2 | LINUCB | 265.95 (3.379) | 0.8865 | diagonal ≈0.9999; fuera de diagonal ≈0.91–0.95 |
| MIS-v2 | FIXED_SPECIALIZED | 296.60 (2.137) | 0.9887 | diagonal ≈1; fuera de diagonal 0.20 |
| MIS-v2 | REACTIVE_P0 | 296.60 (2.137) | 0.9887 | diagonal ≈1; fuera de diagonal 0.20 |

Las diferencias emparejadas medias de reward (SD entre diferencias por
semilla) fueron:

| Contraste | Competencia constante | MIS-v2 evolutivo |
|---|---:|---:|
| LinUCB − fijo especializado | −27.35 (2.796) | −30.65 (2.852) |
| LinUCB − P0 reactivo | −27.35 (2.796) | −30.65 (2.852) |
| P0 reactivo − fijo especializado | 0 (0) | 0 (0) |

MIS-v2 aumentó el reward medio respecto al control constante en `40.25`
puntos para LinUCB y `43.55` para cada uno de los otros dos métodos. La
diferencia-en-diferencias `(LinUCB−fijo)_MIS − (LinUCB−fijo)_constante` fue
`−3.30` puntos (descriptiva; no identifica un efecto mediado). Las decisiones
de LinUCB difirieron entre sus ejecuciones emparejadas con y sin MIS-v2 en un
promedio del `44.18%` de los periodos. El mapa fijo y P0 eligieron exactamente
lo mismo en las 20 semillas y ambas condiciones: el agente especialista siguió
siendo el de mayor competencia para cada tarea, pues no hay transferencia
entre tareas. Así, la demanda cambiante no hizo cambiar la asignación óptima
condicionada por tarea en esta instancia.

#### Interpretación científica

**Hecho observado:** MIS-v2 cambia el estado, el feedback esperado y muchas
decisiones de LinUCB; su reward aumenta sustancialmente frente a su propio
control de competencia constante. **Pero** el selector contextual no obtiene
una ventaja organizacional sobre la asignación fija especializada ni sobre
P0. En este diseño, la exploración de LinUCB expone competencias fuera de la
diagonal, mientras que la organización fija concentra toda exposición en la
competencia especialista requerida. La respuesta miope P0 coincide con el
mapa fijo porque el especialista inicial ya es el máximo por tarea y el
aprendizaje es local por tarea. El resultado muestra interacción entre
aprendizaje de política y desarrollo de competencias, no sinergia ni
superioridad de LinUCB; la política puede actualizarse y cambiar decisiones
sin mejorar frente a un baseline fuerte.

Este piloto no separa causalmente mediación de feedback y de estado: al
activar MIS cambia tanto la probabilidad de reward como el contexto futuro
observado por LinUCB. Es un contraste factorial emparejado y descriptivo. El
estado perfectamente observable, la competencia inicial fuertemente
especializada, la regla de reward Bernoulli, la ausencia de coste separado de
desarrollo y la demanda C5 sintética limitan validez externa. Los 20 pares no
constituyen confirmación general ni permiten inferir ventajas fuera de esta
configuración. Se preservan las diferencias cero/negativas como resultado.

#### Trazabilidad y reproducción

Correspondencia ontológica, configuración, semillas, secuencias por política,
competencias periodo a periodo, contexto, decisión, reward observado, scores
UCB, coeficientes estimados, recurso y resúmenes están en un único artefacto:
[`results.json`](../../results/experiments/hls_linucb_mis_v2_interaction/results.json).
La ejecución reproducible es:

```bash
PYTHONPATH=src pytest -q tests/synthetic/test_hls_linucb_mis_v2_interaction.py tests/test_linucb.py
PYTHONPATH=src python experiments/run_hls_linucb_mis_v2_interaction.py
```

Las pruebas focalizadas pasaron (`17 passed`). Los resultados deterministas se
reconstruyen a partir del runner y las semillas guardadas; los tiempos locales
de selección son diagnósticos y varían entre ejecuciones. No se modificaron
EXP3, LinUCB, MIS-v2, C5 ni la ontología, y no se alteraron los artefactos
históricos.

### 2026-10-20 — Integración comparativa de MIS-v2 y Nembhard Direct

**Estado:** piloto pequeño ejecutado y registrado; no es una campaña extensa ni
una reproducción integral del artículo de Nembhard y Bentefouet. Se reutilizó
la curva directa existente y no se modificaron MIS-v2, LinUCB, EXP3, C5 ni la
ontología.

#### Correspondencia A/B/C

- **A — Escenario:** 3 agentes heterogéneos × 3 tareas, demanda no estacionaria
  del generador C5, horizonte de 90 periodos y 10 trayectorias emparejadas
  (semillas 0–9). Cada periodo presenta una tarea; las tres fases de demanda
  duran 30 periodos y usan probabilidades `(0.70,0.20,0.10)`,
  `(0.10,0.20,0.70)` y `(0.20,0.70,0.10)`. La matriz inicial de productividad/
  competencia es `((.85,.20,.20),(.20,.85,.20),(.20,.20,.85))`.
- **B — Mecanismos:** MIS-v2 actualiza la competencia acotada mediante la
  transición ya implementada, con `eta=.15` en las nueve celdas y exposición
  en la celda asignada. Nembhard Direct usa la ecuación publicada (1),
  `P(D)=k(D+p)/(D+p+r)`, y acumula exposición por asignación. Para igualar
  exactamente la productividad inicial, el piloto fija `k=1`, `r=1` y
  `p=C0/(1-C0)` por celda (diagonal `5.6666667`, fuera de diagonal `.25`);
  es una calibración de prior-exposure sintética, no una estimación empírica
  publicada. Productividad y reward se evalúan antes de actualizar exposición
  al final del periodo. La transferencia entre tareas no se integró.
- **C — Organizaciones:** las mismas tres organizaciones se ejecutaron con
  ambos mecanismos: LinUCB-disjoint contextual, mapa fijo especializado
  `task_i → agent_i` y selección reactiva de producción actual P0. LinUCB
  aprende parámetros de selección; MIS-v2 o Nembhard modifica el estado físico
  de los agentes. Son estados distintos, registrados por separado. Todos
  observan la tarea y la productividad/competencia actual; no reciben demanda
  futura ni rewards de agentes no seleccionados. Recursos y catálogo son
  idénticos: una unidad de esfuerzo, un agente por periodo, presupuesto
  compartido e individual igual a 1.

#### Fidelidad y alcance de Nembhard

La función existente [Nembhard Direct](../../src/hls/mechanisms/nembhard_direct.py)
y su adaptador N×K en [hls_lab_nk_nembhard.py](../../src/hls/hls_lab_nk_nembhard.py)
implementan la curva escalar de la ecuación (1) y la contabilidad acumulativa
de exposición. Las pruebas existentes comprueban valores manuales, umbral de
media asíntota, monotonía, concavidad, asíntota, validación de parámetros y
actualización de exposición; las pruebas del adaptador verifican el cálculo
N×K. Esto valida la ecuación directa bajo la convención operativa declarada
(productividad pre-periodo y `D += esfuerzo × duración` post-periodo), pero no
la temporización ambigua del artículo ni el modelo completo.

Nembhard y Bentefouet (2015), ecuación (1), p. 176; ecuaciones (2)–(3),
pp. 176–177; apéndices A-3/A-4, p. 185. La revisión de la fuente primaria
([auditoría de fidelidad](../../docs/literature/audits/HLS_NEMBHARD_FIDELITY_AND_CONTRACT_REVIEW_2026-10-17.md),
[extracción matemática](../../docs/literature/audits/Nembhard_Bentefouet_2015_Mathematical_Extraction.md),
[PDF local](../../docs/literature/competence_evolution/Nembhard_Bentefouet_2015_Selection_Grouping_Assignment.pdf))
deja sin resolver dependencias contemporáneas, unidades y temporización de la
transferencia indirecta. Por tanto, ésta no se implementó ni se atribuye al
piloto. Su estado es **no aplicable al contraste de curva directa**, no una
transferencia validada. El piloto no reproduce las políticas de selección,
agrupamiento y asignación del artículo.

#### Resultados del piloto

Reward: suma de salida efectiva normalizada por periodo; en MIS-v2 es `C[i,k]`
y en Nembhard Direct `P[i,k](D)`. Éxito funcional secundario: salida `≥.90`.
No hay coste de desarrollo separado: la unidad de asignación es a la vez
recurso operativo y exposición al aprendizaje. Las trayectorias de tareas son
idénticas entre políticas dentro de cada semilla; las recompensas son
deterministas condicionadas al estado y a la asignación. Se muestran media y
desviación estándar entre las 10 trayectorias:

| Mecanismo | Organización | Reward acumulado medio (SD) | Éxito funcional medio | Recurso medio | Estado final medio |
|---|---|---:|---:|---:|---|
| MIS-v2 | LinUCB | 67.3708 (0.0903) | 0.5000 | 90 | competencia: diagonal ≈0.99; fuera de diagonal ≈0.67–0.73 |
| MIS-v2 | Fijo especializado | 87.0281 (0.0044) | 0.9000 | 90 | competencia diagonal ≈0.998–0.999; resto 0.20 |
| MIS-v2 | Reactivo P0 | 87.0281 (0.0044) | 0.9000 | 90 | igual al fijo en estas trayectorias |
| Nembhard Direct | LinUCB | 71.9117 (0.0530) | 0.3144 | 90 | experiencia media por celda: `[[12.6,9.4,8.4],[8.7,13.7,8.1],[8.2,9.0,11.9]]` |
| Nembhard Direct | Fijo especializado | 84.7151 (0.0147) | 0.8667 | 90 | exposición diagonal `29.5,32.1,28.4`; resto 0 |
| Nembhard Direct | Reactivo P0 | 84.7151 (0.0147) | 0.8667 | 90 | igual al fijo en estas trayectorias |

El LinUCB menos fijo especializado fue `−19.6573` (SD de diferencias emparejadas
`0.0863`) bajo MIS-v2 y `−12.8034` (SD `0.0445`) bajo Nembhard Direct. P0 y el
mapa fijo coincidieron en las 10 semillas en ambos mecanismos. Entre mecanismos,
Nembhard Direct dio a LinUCB `+4.5409` (SD `0.0765`) de reward acumulado medio
frente a MIS-v2, pero dio al mapa fijo/P0 `−2.3130` (SD `0.0104`). El ranking
depende de la organización y de la métrica: Nembhard Direct no es universalmente
mejor; la tasa de éxito de LinUCB fue además menor que bajo MIS-v2. La política
fija concentra exposición en especialistas, mientras que LinUCB explora y
actualiza su selección; la evolución de competencias y la actualización de la
política quedan diferenciadas en los trazados.

**Interpretación:** el piloto confirma que dos mecanismos B distintos pueden
ejecutarse con las mismas organizaciones, demandas emparejadas, catálogo y
presupuesto en un entorno N×K acotado. También demuestra que el mecanismo de
selección no debe confundirse con aprendizaje de competencias. No demuestra
ventaja de LinUCB, transferencia, superioridad general de un mecanismo,
validez industrial ni reproducción completa de Nembhard. La demanda, reward,
prior-exposure y umbral son sintéticos; la observación de productividad es
perfecta y no hay datos industriales.

#### Evidencia y reproducción

Código del piloto: [runner](../../experiments/run_hls_learning_mechanism_comparison.py)
y [pruebas específicas](../../tests/synthetic/test_hls_learning_mechanism_comparison.py).
Resultados, parámetros, 10 semillas, 60 episodios, secuencias emparejadas,
decisiones, trazas por periodo, estados antes/después, matrices/coefs de LinUCB
y diferencias emparejadas: [artefacto agregado](../../results/experiments/hls_learning_mechanism_comparison/results.json).
Las pruebas específicas, junto con las pruebas existentes de la ecuación
Nembhard, adaptador, MIS-v2, LinUCB y políticas N×K, pasaron: `140 passed`.

```bash
PYTHONPATH=src pytest -q \
  tests/synthetic/test_hls_learning_mechanism_comparison.py \
  tests/synthetic/test_hls_linucb_mis_v2_interaction.py \
  tests/test_linucb.py tests/test_nembhard_direct.py \
  tests/test_hls_lab_nk_nembhard.py \
  tests/test_hls_lab_nk_nembhard_oracle.py \
  tests/test_hls_lab_nk_nembhard_adaptive.py \
  tests/test_hls_lab_nk_learning.py \
  tests/test_hls_lab_nk_learning_transition.py \
  tests/test_hls_lab_nk_policies.py \
  tests/test_hls_lab_v1_nk_geometry.py
PYTHONPATH=src python experiments/run_hls_learning_mechanism_comparison.py
```

La ontología existente [v0.1](../architecture/HLS_ONTOLOGY_V0_1_2026-10-23.md)
se conserva: A describe la demanda/recursos, B distingue las dos transiciones,
y C enumera organizaciones reutilizables. No se cambió el documento ontológico
ni se extendió esta evidencia a capacidades que sólo existan en G0/RQ0.

### 2026-10-20 — Integración acotada de asignación bipartita conjunta

**Estado:** implementada, comparada y verificada para el subproblema de
asignación discreta uno-a-uno. Esta integración no reemplaza ni restringe el
contrato general de esfuerzo N×K, que admite asignaciones fraccionarias.

#### Correspondencia A/B/C y contrato

- **A — Escenario:** un lote por periodo contiene 3 agentes y 3 tareas
  simultáneas; cada pareja agente-tarea tiene recompensa escalar explícita.
  Cada pareja seleccionada consume una unidad; cada agente y cada tarea pueden
  aparecer como máximo una vez. Los límites individual, colectivo y del
  problema se validan contra `OrganizationResourcesNK`/`ProblemSpecNK` y la
  matriz de salida satisface `ProductiveAllocationNK`.
- **B — Mecanismos:** competencias permanecen constantes (`.5` como estado
  inerte); no se ejecuta MIS-v2, Nembhard Direct, transferencia ni otra
  transición. Las recompensas de este control son exógenas y aditivas, no una
  inferencia de aprendizaje o productividad.
- **C — Organización:** el solver de asignación lineal conjunta se compara con
  greedy por aristas de recompensa actual y con el mejor mapa fijo uno-a-uno
  optimizado para el episodio completo. La optimización fija ve todas las
  matrices del episodio, por lo que constituye un comparador estático fuerte
  con información offline; greedy y el solver conjunto sólo necesitan la
  matriz del periodo actual.

La integración está en
[hls_lab_nk_assignment.py](../../src/hls/hls_lab_nk_assignment.py). Resuelve
recompensa máxima opcional sobre todas las cardinalidades factibles, o coste
mínimo cubriendo el lado menor en el modo clásico; la construcción con nodos
dummy representa no-asignaciones y cardinalidad, y descarta aristas prohibidas.
Unidades asignadas y recursos respetan los límites N×K. El algoritmo bipartito
no representa esfuerzo divisible, parejas que requieren varios agentes,
complementariedad CES, costes de activación dependientes del estado ni
restricciones temporales más allá de la matriz actual.

**Fidelidad de referencia:** Kuhn (1955), “The Hungarian Method for the
Assignment Problem”, proporciona la referencia histórica para el problema de
asignación. Se reutiliza `scipy.optimize.linear_sum_assignment` (SciPy
1.13.1), solver científico mantenido para el mismo objetivo de asignación
lineal; su implementación documentada usa una variante Jonker–Volgenant. Por
tanto, se integra y valida el **problema/solución óptima de asignación**, no se
afirma reproducir paso a paso la implementación original del método húngaro.
La dependencia directa `scipy>=1.9` se declara en `pyproject.toml`.

#### Verificación y comparación reproducible

Las pruebas comparan el solver contra enumeración exhaustiva de todos los
emparejamientos en varias matrices pequeñas, incluidas matrices rectangulares,
presupuesto fraccionario, límite individual restrictivo, recompensas
negativas y coste mínimo de cobertura completa. Un caso de 3×3 también verifica
que la solución conjunta obtiene 26 frente a 18 de greedy global por aristas.
La batería específica pasó: `9 passed`; al añadir las regresiones de geometría
y políticas N×K, el total fue `46 passed`.

El piloto usa 10 semillas (`20261020`–`20261029`), 12 matrices 3×3 por semilla
(120 matrices en total), recompensas discretas `U{1,…,100}/100` y presupuesto
3. La asignación fija escoge, por enumeración de las seis permutaciones, el
mapa que maximiza la recompensa sumada sobre las 12 matrices de cada episodio.
Todas las políticas reciben exactamente las mismas matrices y consumen 36
unidades por episodio. Resultados por episodio, emparejamientos, recompensas,
uso por agente/tarea, tiempos y comparaciones están en el
[resultado agregado](../../results/experiments/hls_hungarian_assignment/results.json):

| Organización | Recompensa acumulada media (SD), 12 periodos | Recursos medios | Tiempo medio de decisión/ajuste por episodio |
|---|---:|---:|---:|
| Asignación conjunta SciPy | 24.6280 (0.9095) | 36 | 0.000235 s |
| Greedy | 23.5850 (1.2677) | 36 | 0.000043 s |
| Mejor mapa fijo offline | 20.0760 (0.9858) | 36 | 0.000015 s para seleccionar el mapa |

La diferencia emparejada conjunta−greedy fue `1.0430` (SD entre semillas
`0.7108`); conjunta−fijo `4.5520` (SD `0.7256`). En cada una de las 120
matrices, la recompensa del solver coincidió con el máximo por enumeración de
las seis permutaciones completas 3×3. Los tiempos son diagnósticos locales,
no una afirmación de escalabilidad. El resultado ilustra ventajas posibles
frente a greedy y fijo en matrices sintéticas variables; no demuestra una
ventaja general en HLS ni en datos operativos.

#### Reproducción y límites

```bash
PYTHONPATH=src pytest -q tests/test_hls_lab_nk_assignment.py
PYTHONPATH=src python experiments/run_hls_hungarian_assignment.py
```

Runner: [run_hls_hungarian_assignment.py](../../experiments/run_hls_hungarian_assignment.py);
pruebas: [test_hls_lab_nk_assignment.py](../../tests/test_hls_lab_nk_assignment.py).
La correspondencia ontológica mantiene A como escenario, B como mecanismos
inertes en esta validación y C como organización conjunta, compatible con la
[ontología v0.1](../architecture/HLS_ONTOLOGY_V0_1_2026-10-23.md). No se
modificaron MIS-v2, Nembhard Direct, LinUCB, EXP3 ni la semántica del catálogo
general de acciones. No se ejecutó una campaña extensa ni se hizo commit o
push.

### 2026-10-20 — Composición LinUCB disjoint × asignación bipartita

**Estado:** piloto híbrido implementado y ejecutado en modo acotado. Se
reutilizaron `LinUCBDisjoint` y `HungarianAssignmentOptimizerNK`; las
formulaciones fuente no se modificaron.

#### Correspondencia ontológica A/B/C

- **A — Escenario:** tres agentes heterogéneos, tres tareas presentes
  simultáneamente y un contexto operativo de tres modos que varía por una
  trayectoria reproducible. Cada pareja agente-tarea tiene reward contextual
  en `[0,1]`; cada periodo exige un matching uno-a-uno, con límites individual,
  colectivo y del problema de una unidad por asignación. Las competencias son
  constantes.
- **B — Mecanismo:** LinUCB aprende la recompensa de selección contextual por
  pareja. La matriz de competencia fija afecta la recompensa latente, pero no
  cambia; no se ejecuta aprendizaje de competencias ni transferencia.
- **C — Organización:** la organización principal calcula una matriz de
  puntuaciones UCB por pareja y la entrega al optimizador conjunto. También se
  evalúan greedy con idéntica matriz de puntuaciones, LinUCB+greedy en una rama
  online independiente, un oráculo y un mapa fijo entrenado.

El adaptador mínimo
[`PairwiseLinUCBAdapterNK`](../../src/hls/hls_lab_nk_linucb_assignment.py)
mantiene un modelo disjoint existente por cada pareja, convierte sus scores en
matriz N×K y envía feedback sólo a parejas seleccionadas. El wrapper llama la
actualización existente de LinUCB una vez por recompensa observada. Como hay
asignaciones simultáneas, se actualizan varios pares al final del periodo: es
una composición **multiple-play / feedback por lotes** del update single-play
de Li et al., no el protocolo de una acción por ronda del artículo ni una
transferencia automática de sus garantías. La selección de parejas, sus
puntuaciones, coeficientes y contadores de observación quedan registrados por
periodo.

#### Diseño, información y comparadores

Se usaron 8 semillas de entrenamiento (`7100`–`7107`), 36 periodos cada una,
para seleccionar por enumeración de las `3!` permutaciones el mejor mapa fijo.
Ese mapa recibe las matrices completas de reward del conjunto de entrenamiento;
el simulador genera esas etiquetas para el ajuste offline. El mapa se evalúa
sólo en 10 semillas distintas (`8200`–`8209`), también de 36 periodos,
emparejadas entre políticas. LinUCB comienza sin observaciones y sólo se
actualiza con feedback de parejas seleccionadas durante cada trayectoria de
evaluación.

El vector contextual es `[1, mode_0, mode_1, mode_2]`. Los rewards simulados
son lineales y deterministas dado el contexto, con coeficientes por pareja
derivados de competencias heterogéneas constantes, y permanecen en `[0,1]`.
Los coeficientes verdaderos y matrices completas se guardan como datos del
evaluador para reproducibilidad; no se suministran a la política híbrida. El
oráculo asigna con recompensas verdaderas actuales y está identificado como
referencia no desplegable.

**GREEDY_SAME_LINUCB_SCORES** es una ablación contrafactual: usa en cada periodo
exactamente la matriz UCB de la organización híbrida, pero sus acciones no
alimentan el modelo LinUCB principal. Se incluye además
**LINUCB_GREEDY_ONLINE**, una organización online independiente que actualiza
sus propios modelos sólo con las parejas que greedy selecciona. Así el
baseline contrafactual no se presenta como un segundo proceso de aprendizaje.

#### Resultados de evaluación

Reward acumulado medio y desviación estándar entre diez trayectorias de 36
periodos; regret acumulado es la diferencia respecto al oráculo de reward
verdadero en cada periodo. Todas las organizaciones consumieron 108 unidades
por trayectoria y mantuvieron matching uno-a-uno.

| Organización | Reward medio (SD) | Regret medio vs. oráculo (SD) | Recursos medios | Tiempo medio por trayectoria |
|---|---:|---:|---:|---:|
| LinUCB + matching conjunto | 64.1086 (2.2238) | 15.2382 (1.4998) | 108 | 0.004816 s |
| Greedy sobre las mismas puntuaciones UCB (contrafactual) | 63.9215 (2.1436) | 15.4253 (1.6195) | 108 | 0.000117 s |
| LinUCB + greedy online independiente | 63.6367 (2.1126) | 15.7101 (1.7955) | 108 | 0.003854 s |
| Oráculo: matching de rewards verdaderos | 79.3468 (3.5262) | 0 | 108 | 0.000837 s |
| Mejor mapa fijo ajustado en entrenamiento | 77.2020 (4.6921) | 2.1448 (1.3341) | 108 | 0.000020 s de lookup |

El mapa fijo seleccionado fue `task_0→agent_0`, `task_1→agent_1`,
`task_2→agent_2`; su reward en entrenamiento fue `610.128`. En este piloto,
el matching conjunto sobre UCB superó ligeramente al greedy score-matched y
al greedy online en reward verdadero, pero quedó por debajo del mapa fijo
entrenado y del oráculo. No se interpreta como superioridad general: reward,
contexto, competencias y horizonte son sintéticos, y el resultado no se
generaliza fuera de estas semillas.

#### Verificación y reproducción

Las pruebas comprueban scores iniciales de confianza, update matricial de
LinUCB en el par seleccionado, ausencia de updates para pares no seleccionados,
rechazo de feedback adicional, replay por semilla, asignación óptima sobre la
matriz UCB, greedy sobre esa misma matriz, matching y recursos, regret no
negativo frente al oráculo y separación de semillas train/evaluation. La
batería focalizada pasó: `27 passed`.

```bash
PYTHONPATH=src pytest -q \
  tests/test_hls_lab_nk_linucb_assignment.py \
  tests/test_hls_lab_nk_assignment.py tests/test_linucb.py
PYTHONPATH=src python experiments/run_hls_linucb_bipartite_hybrid.py
```

Código: [runner](../../experiments/run_hls_linucb_bipartite_hybrid.py),
[adaptador](../../src/hls/hls_lab_nk_linucb_assignment.py) y
[pruebas](../../tests/test_hls_lab_nk_linucb_assignment.py). Configuración,
datos de entrenamiento/evaluación, 360 trazas, rewards por pareja,
asignaciones, coeficientes, counts, regret y tiempos están en el
[resultado agregado](../../results/experiments/hls_linucb_bipartite_hybrid/results.json).
Los tiempos son diagnósticos locales. No se inició aprendizaje de
competencias, no se cambiaron los algoritmos fuente y no se alteraron el piloto
LinUCB×MIS-v2 ni la integración bipartita previa.

### 2026-10-20 — Sensibilidad al dinamismo exógeno de competencias

**Estado: campaña acotada D0/D1/D2 ejecutada y registrada.** Se compararon
LinUCB disjoint + matching bipartito, LinUCB disjoint + greedy online, un mapa
fijo optimizado sólo en entrenamiento y un oráculo dinámico evaluador. No se
introdujeron algoritmos ni se modificaron las implementaciones de LinUCB,
asignación bipartita, N×K o C5.

#### Inspección y definición del dinamismo

La inspección previa confirmó que `StationaryTaskDemand`,
`NonStationaryTaskDemand`, `MarkovTaskDemand` y
`generate_environment_trajectory_nk` generan demanda/escenarios exógenos, no
trayectorias exógenas de competencia. La transición MIS-v2 existente es
dependiente del esfuerzo/acción, por lo que no se usó para este estudio. Se
reutilizaron la geometría y restricciones N×K, el emisor C5 de demanda
estacionaria y el runner/adapter LinUCB×bipartito ya validados. La única
parametrización nueva está aislada en el runner experimental: un proceso
exógeno de dos regímenes que no consulta acciones ni resultados de políticas.

La configuración, fijada antes de medir políticas, fue:

\[
C^0=\begin{bmatrix}.70&.50&.35\\.35&.70&.50\\.50&.35&.70\end{bmatrix},\quad
S=\begin{bmatrix}-1&1&0\\0&-1&1\\1&0&-1\end{bmatrix},\quad
C_t=C^0+a_D z_tS,
\]

donde `z_0=0` y en cada periodo posterior el régimen alterna con probabilidad
`p_D`, independientemente de acciones. D0 usa `a=0,p=0`; D1 usa amplitud
`a=.15` y `p=.01` (duración media geométrica de 100 periodos); D2 usa
`a=.30` y `p=.04` (duración media de 25 periodos). Así, las tres condiciones
comparten exactamente el estado inicial; todas las celdas permanecen en
`[.20,.80]`. El cambio de la diagonal especializada al ciclo adelantado
invierte la asignación óptima según la matriz de reward esperado: en régimen
estable, diagonal `2.10` frente a ciclo `1.50`; en régimen cambiado, D1 ciclo
`1.95` frente a diagonal `1.65`, y D2 ciclo `2.40` frente a diagonal `1.20`.
Es una comprobación estructural de la configuración, no una selección basada
en qué política gana.

#### Protocolo, información y ontología A/B/C

- **A — Escenario:** 3 agentes × 3 tareas unitarias simultáneas, 300 periodos,
  matching uno-a-uno y presupuesto común de 3 asignaciones por periodo. Se
  reutilizó `StationaryTaskDemand`/`generate_environment_trajectory_nk`; las
  tres tareas están presentes en todos los periodos. No varía la demanda de
  tareas: D1/D2 varían exclusivamente competencias exógenas. Por condición se
  ajustó el mapa fijo con 20 trayectorias de entrenamiento de 300 periodos y
  se evaluó en 20 semillas distintas (`8200`–`8219`), compartidas entre D0,
  D1 y D2; las semillas de entrenamiento (`6100`–`6119`) son disjuntas.
- **B — Mecanismo:** `MIS-v2` y Nembhard están desactivados. El reward esperado
  es `mu[i,k,t]=C[i,k,t]`; el outcome observado es Bernoulli(`mu`). Se entrega
  como contexto actual observable `x=C[i,k,t]` a LinUCB, con parámetro
  verdadero `theta=1` por pareja. LinUCB conserva sus ecuaciones y
  `alpha_from_delta(0.05)`. Esto es aprendizaje de la política de selección,
  no aprendizaje de las competencias.
- **C — Organización:** (1) puntuaciones pairwise LinUCB seguidas por el
  optimizador conjunto existente; (2) una instancia independiente del mismo
  LinUCB seguida de greedy online; (3) mejor mapa fijo entre las 3! opciones,
  optimizado sobre reward esperado de entrenamiento; (4) oráculo por periodo
  que maximiza la matriz verdadera de reward esperado, sólo como referencia.
  Las políticas online conocen competencia actual pero no futuro; actualizan
  sólo las recompensas de parejas asignadas. El evaluador pre-genera outcomes
  potenciales por pareja/periodo con un flujo de semilla separado y común a
  políticas y condiciones. Cada método consume 900 unidades por ejecución.

Los datos son sintéticos; el proceso Markov de competencia es una
parametrización del experimento, no un generador existente ni un modelo
empírico de aprendizaje. La amplitud y frecuencia aumentan conjuntamente, por
lo que el diseño no identifica sus efectos por separado. El mapa fijo recibe
información completa de reward esperado en entrenamiento, pero no accede a
evaluación; por tanto es un baseline offline fuerte, aunque su presupuesto de
información de entrenamiento no es idéntico al feedback seleccionado de
LinUCB. El oráculo conoce el reward esperado actual sólo para puntuar regret;
no ve outcomes Bernoulli futuros ni se ofrece como política desplegable.

#### Evidencia de dinamismo y resultados

Cada número es media de 20 ejecuciones de 300 periodos; entre paréntesis está
la desviación estándar del reward acumulado. El regret es *pseudo-regret*
contra el matching de reward esperado actual, evitando que el ruido Bernoulli
produzca regret negativo. `Δ vs fijo` es la diferencia pareada de reward
realizado frente al mapa fijo entrenado; entre corchetes se informa su
intervalo t descriptivo del 95% (no se interpreta como confirmación de una
hipótesis general).

| Condición | Organización | Reward acumulado (SD) | Pseudo-regret vs oráculo | Δ vs fijo (IC t 95%) |
|---|---|---:|---:|---:|
| D0 | LinUCB + matching | 611.950 (16.797) | 22.955 | −22.200 [−25.273, −19.127] |
| D0 | LinUCB + greedy online | 599.000 (21.191) | 36.565 | −35.150 [−40.277, −30.023] |
| D0 | FIXED-OPT entrenamiento | 634.150 (14.299) | 0 | 0 |
| D0 | Oráculo dinámico | 634.150 (14.299) | 0 | 0 |
| D1 | LinUCB + matching | 604.250 (20.616) | 12.410 | +22.350 [+9.709, +34.991] |
| D1 | LinUCB + greedy online | 595.450 (22.751) | 18.678 | +13.550 [−0.672, +27.772] |
| D1 | FIXED-OPT entrenamiento | 581.900 (40.186) | 36.780 | 0 |
| D1 | Oráculo dinámico | 614.450 (21.252) | 0 | +32.550 [+21.155, +43.945] |
| D2 | LinUCB + matching | 676.800 (18.048) | 2.717 | +92.250 [+78.266, +106.234] |
| D2 | LinUCB + greedy online | 674.350 (19.115) | 5.125 | +89.800 [+76.293, +103.307] |
| D2 | FIXED-OPT entrenamiento | 584.550 (41.163) | 91.320 | 0 |
| D2 | Oráculo dinámico | 679.150 (17.825) | 0 | +94.600 [+80.235, +108.965] |

La media de cambios de competencia y de cambios de asignación óptima fue
respectivamente D0 `0/0`, D1 `2.90/2.90` y D2 `11.90/11.90` por trayectoria;
el 95% de las rutas D1 y el 100% de las D2 tuvo al menos un cambio de óptimo.
La variación Frobenius acumulada de la matriz de reward esperado fue `0`,
`1.066` y `8.745`. La pérdida del mejor mapa fijo retrospectivo frente al
oráculo dinámico fue `0`, `31.695` y `81.690` unidades esperadas, indicando
que las oportunidades de reasignación potencial aumentan en estas
configuraciones.

En D0, donde el óptimo no cambia, FIXED-OPT coincide con el oráculo y supera a
ambos LinUCB: hay coste observable de aprender/explorar cuando no existe
oportunidad de adaptación. En D1, matching-LinUCB reduce el pseudo-regret de
`36.780` (fijo) a `12.410` y su diferencia pareada con el fijo es positiva en
esta muestra; LinUCB-greedy también reduce regret, pero su intervalo pareado
incluye cero. En D2, matching y greedy siguen el óptimo en el `98.5%` y `97.0%`
de los periodos, con pseudo-regret `2.717` y `5.125`, frente a `91.320` del
mapa fijo. El reward esperado por régimen confirma el límite: en D1 el fijo
alcanza `2.10` por periodo estable, pero `1.65` en régimen cambiado; en D2
el mapa fijo entrenado en el ciclo obtiene `1.50` estable y `2.40` cambiado,
frente a `2.10` y `2.40` del oráculo. Por tanto un mapa fijo sigue siendo
competitivo cuando el entorno permanece en su régimen de entrenamiento.

El reward esperado agrupado por periodos de régimen (pooling sobre todos los
episodios; `—` significa que el régimen no aparece) fue:

| Condición | Política | Estable | Cambiado |
|---|---|---:|---:|
| D0 | LinUCB + matching | 2.024 | — |
| D0 | LinUCB + greedy online | 1.978 | — |
| D0 | FIXED-OPT entrenamiento | 2.100 | — |
| D0 | Oráculo dinámico | 2.100 | — |
| D1 | LinUCB + matching | 2.045 | 1.928 |
| D1 | LinUCB + greedy online | 2.017 | 1.918 |
| D1 | FIXED-OPT entrenamiento | 2.100 | 1.650 |
| D1 | Oráculo dinámico | 2.100 | 1.950 |
| D2 | LinUCB + matching | 2.082 | 2.400 |
| D2 | LinUCB + greedy online | 2.066 | 2.400 |
| D2 | FIXED-OPT entrenamiento | 1.500 | 2.400 |
| D2 | Oráculo dinámico | 2.100 | 2.400 |

El pseudo-regret medio por ventana post-cambio (hasta 10 periodos, truncada
ante el cambio siguiente) fue D1: matching `0.021`, greedy `0.114`, fijo
`1.645`; D2: matching `0`, greedy `0.016`, fijo `2.251`. Los LinUCB
coincidieron con el matching oracular en todos los eventos dentro de esa
ventana; esto no es una estimación causal del coste de cómputo ni demuestra
adaptación bajo competencia oculta: la competencia actual se entrega como
contexto. Para el mapa fijo, una coincidencia tras un cambio puede deberse a
que el régimen volvió al estado al que el mapa se ajusta, no a adaptación.

El reward bruto D2 es mayor en parte porque el régimen cambiado tiene un nivel
de reward alcanzable más alto; por ello no debe leerse como efecto puro de la
frecuencia de cambio. Regret y brecha retrospectiva separan mejor oportunidad
de reasignación de nivel de reward. Además, D1 y D2 cambian a la vez amplitud y
frecuencia; no permiten atribuir el efecto a una de ellas por separado. Los
resultados muestran que el dinamismo genera oportunidades cuando cambia la
asignación óptima y que LinUCB puede aprovecharlas bajo observabilidad perfecta
del estado; no son evidencia sobre error de estimación de competencias,
aprendizaje endógeno, datos industriales ni superioridad general.

#### Artefactos, pruebas y reproducción

El artefacto compacto conserva configuración, semillas, resúmenes por régimen,
series medias temporales, outcomes/decisiones por semilla codificados,
diagnósticos post-cambio y tiempos. La ruta de asignación almacena un dígito
`0–5` por periodo según la lista de permutaciones en la configuración; la ruta
de reward realizado almacena un dígito `0–3`. La imagen compara reward
acumulado medio a lo largo de los 300 periodos.

Pruebas focalizadas: `32 passed` (runner nuevo y regresión de LinUCB,
adaptador y asignación). `git diff --check` pasa. No se ejecutó la suite
completa.

```bash
PYTHONPATH=src pytest -q tests/test_hls_dynamicity_sensitivity.py \
  tests/test_hls_lab_nk_linucb_assignment.py \
  tests/test_hls_lab_nk_assignment.py tests/test_linucb.py
PYTHONPATH=src python experiments/run_hls_dynamicity_sensitivity.py
```

Código: [runner](../../experiments/run_hls_dynamicity_sensitivity.py) y
[pruebas](../../tests/test_hls_dynamicity_sensitivity.py). Evidencia compacta:
[resultados agregados](../../results/experiments/hls_dynamicity_sensitivity/results.json)
y [gráfico temporal](../../results/experiments/hls_dynamicity_sensitivity/dynamicity_sensitivity.png).
Las conclusiones son específicas al generador sintético, 3×3, horizonte 300 y
20 semillas; no se modificaron campañas previas ni los algoritmos existentes.

### 2026-10-20 — Ablación informacional D0/D1/D2

**Estado: campaña acotada ejecutada; evidencia exploratoria.** Se conservó sin
cambios el escenario de [sensibilidad D0/D1/D2](../../experiments/run_hls_dynamicity_sensitivity.py),
incluidas las 20 semillas de evaluación (`8200`–`8219`), 300 periodos, demanda,
trayectorias exógenas de competencias, ruido potencial de outcomes, presupuestos
y restricciones. Se añadieron P0 reactivo y LinUCB+matching sin competencias en
el contexto. El JSON histórico de sensibilidad no se sobrescribió.

#### Información y organizaciones realmente evaluadas

- **Observable:** tarea (las tres están presentes siempre), matriz actual de
  competencias y geometría pública. LinUCB con contexto completo recibe el
  rasgo escalar original `x=C[i,k,t]`; la variante ablacionada recibe identidad
  de tarea one-hot, sin competencia ni etiqueta de régimen. Cada LinUCB recibe
  feedback únicamente de las parejas ejecutadas.
- **P0 REACTIVO + MATCHING:** reutiliza `P0ProductionOnlyNK` y su ranking
  productivo canónico sobre las seis asignaciones perfectas factibles. Recibe
  sólo competencia observable y requisitos públicos unitarios; no recibe la
  matriz evaluadora, outcomes contrafactuales, régimen futuro ni matching
  oracular. Como la salida aditiva pública es `C[i,k]` y todas las competencias
  son inferiores al requisito uno, el ranking P0 maximiza la suma de
  competencias asignadas. Esto coincide con el matching de reward esperado;
  se verificó en preflight. P0 es reactivo y no actualiza parámetros.
- **Privilegiado/evaluador únicamente:** matriz de medias verdadera para
  pseudo-regret, matching óptimo y sus chequeos. No se entrega a políticas.
  Demandas, competencias y outcomes potenciales se pre-generan en flujos
  comunes e independientes de las decisiones.
- **Organizaciones:** FIXED-OPT entrenado, LinUCB+matching con contexto
  completo, LinUCB+matching sin competencia, LinUCB+greedy con contexto
  completo, P0+matching y oráculo dinámico evaluador. Cada una ejecuta tres
  asignaciones por periodo (900 unidades por réplica). FIXED-OPT mantiene el
  protocolo original: se ajusta por condición usando las 20 trayectorias de
  entrenamiento y sus medias esperadas conocidas, sin acceso a las semillas de
  evaluación; por tanto no tiene el mismo canal de feedback que los selectores
  online, una limitación de comparabilidad que se conserva explícitamente.

#### Resultados

Media del reward acumulado realizado en 20 semillas (desviación estándar);
regret es pseudo-regret de medias esperadas frente al matching oracular
actual; coincidencia es la fracción de periodos con esa asignación; recursos
son unidades agregadas por réplica.

| Condición | Organización | Reward (SD) | Pseudo-regret | Coincidencia óptima | Recursos |
|---|---|---:|---:|---:|---:|
| D0 | FIXED-OPT entrenamiento | 634.150 (14.299) | 0.000 | 1.000 | 900 |
| D0 | LinUCB + matching, contexto completo | 611.950 (16.797) | 22.955 | 0.870 | 900 |
| D0 | LinUCB + matching, sin competencia | 587.100 (18.410) | 46.885 | 0.738 | 900 |
| D0 | LinUCB + greedy, contexto completo | 599.000 (21.191) | 36.565 | 0.784 | 900 |
| D0 | P0 reactivo + matching | 634.150 (14.299) | 0.000 | 1.000 | 900 |
| D0 | Oráculo dinámico (sólo evaluación) | 634.150 (14.299) | 0.000 | 1.000 | 900 |
| D1 | FIXED-OPT entrenamiento | 581.900 (40.186) | 36.780 | 0.591 | 900 |
| D1 | LinUCB + matching, contexto completo | 604.250 (20.616) | 12.410 | 0.921 | 900 |
| D1 | LinUCB + matching, sin competencia | 562.400 (25.386) | 56.092 | 0.594 | 900 |
| D1 | LinUCB + greedy, contexto completo | 595.450 (22.751) | 18.677 | 0.877 | 900 |
| D1 | P0 reactivo + matching | 614.450 (21.252) | 0.000 | 1.000 | 900 |
| D1 | Oráculo dinámico (sólo evaluación) | 614.450 (21.252) | 0.000 | 1.000 | 900 |
| D2 | FIXED-OPT entrenamiento | 584.550 (41.163) | 91.320 | 0.493 | 900 |
| D2 | LinUCB + matching, contexto completo | 676.800 (18.048) | 2.717 | 0.985 | 900 |
| D2 | LinUCB + matching, sin competencia | 605.400 (21.466) | 74.517 | 0.648 | 900 |
| D2 | LinUCB + greedy, contexto completo | 674.350 (19.115) | 5.125 | 0.970 | 900 |
| D2 | P0 reactivo + matching | 679.150 (17.825) | 0.000 | 1.000 | 900 |
| D2 | Oráculo dinámico (sólo evaluación) | 679.150 (17.825) | 0.000 | 1.000 | 900 |

Diferencias pareadas de reward acumulado (misma seed):

| Contraste | D0 | D1 | D2 |
|---|---:|---:|---:|
| P0 − FIXED-OPT | 0.000 | +32.550 | +94.600 |
| LinUCB completo − FIXED-OPT | −22.200 | +22.350 | +92.250 |
| P0 − LinUCB completo | +22.200 | +10.200 | +2.350 |
| LinUCB completo − LinUCB sin competencia | +24.850 | +41.850 | +71.400 |

IC t descriptivos del 95% para **P0 − LinUCB completo**: D0 `[19.127,
25.273]`, D1 `[7.329, 13.071]`, D2 `[0.837, 3.863]`. Para **LinUCB completo
− sin competencia**: D0 `[20.221, 29.479]`, D1 `[34.775, 48.925]`, D2
`[65.599, 77.201]`. Son resúmenes exploratorios de 20 pares, no pruebas
confirmatorias.

En D1 hubo una media de 2.9 cambios de régimen/asignación óptima por trayectoria;
en D2, 11.9; en D0, cero. P0 cambió asignación en el 100% de los cambios de
régimen y coincidió con la asignación óptima justo después del cambio en el
100% de eventos D1/D2. LinUCB+matching completo cambió en 94.8% de eventos D1 y
97.9% D2; LinUCB sin competencias, en 36.2% y 30.7%. Reward esperado medio por
periodo de P0: D1 estable `2.100`, cambiado `1.950`; D2 estable `2.100`,
cambiado `2.400`.

El reward esperado por periodo en ventanas de hasta 10 periodos antes/después
de un cambio (truncadas en el cambio vecino y horizonte) fue:

| Condición | Organización | Antes | Después |
|---|---|---:|---:|
| D1 | FIXED-OPT | 1.9184 | 1.8284 |
| D1 | LinUCB matching, completo | 1.9827 | 2.0074 |
| D1 | LinUCB matching, sin competencia | 1.8476 | 1.7768 |
| D1 | LinUCB greedy, completo | 1.9542 | 1.9974 |
| D1 | P0 reactivo / oráculo evaluador | 2.0395 | 2.0095 |
| D2 | FIXED-OPT | 1.9245 | 1.9765 |
| D2 | LinUCB matching, completo | 2.2321 | 2.2588 |
| D2 | LinUCB matching, sin competencia | 1.9580 | 1.8241 |
| D2 | LinUCB greedy, completo | 2.2243 | 2.2572 |
| D2 | P0 reactivo / oráculo evaluador | 2.2415 | 2.2588 |

En D0 no hubo cambios y estas métricas son no aplicables. Las ventanas
pre/post son promedios descriptivos de eventos, no estimaciones causales; su
duración real se conserva por evento en el artefacto.

#### Interpretación, límites y decisión

1. **La información observable y reorganización bastan aquí:** P0 alcanza el
   valor y las asignaciones del oráculo en D0/D1/D2; frente a FIXED-OPT gana
   `32.550` en D1 y `94.600` en D2, y empata en D0. En el escenario especificado,
   la ventaja dinámica no requiere aprendizaje estadístico de selección.
2. **No se observa valor adicional de LinUCB frente a P0.** LinUCB con
   matching/contexto completo queda por debajo de P0 en las tres condiciones.
   El feedback y la exploración no mejoran una regla reactiva que ya conoce
   correctamente `E[R]=C`.
3. **La competencia observable sí mejora LinUCB:** al retirarla del contexto,
   LinUCB pierde en promedio `24.850`, `41.850` y `71.400` unidades D0/D1/D2
   respecto a su variante completa. Este contraste estima el valor de la
   información de competencia para ese selector; no aísla aprendizaje de
   estado ni constituye una comparación entre algoritmos idénticos en todo
   salvo el aprendizaje.
4. El resultado previo “LinUCB supera FIXED-OPT” en D1/D2 no prueba que el
   aprendizaje LinUCB cause la mejora: P0, sin actualizar parámetros, iguala
   al oráculo y supera LinUCB. P0-vs-LinUCB cambia la regla de decisión; el
   contraste LinUCB completo-vs-ablacionado cambia la información contextual.
5. La explicación depende de `E[R_ikt]=C_ikt` conocido públicamente,
   observación perfecta de competencia y matching uno-a-uno completo. No evalúa
   incertidumbre de estado, error de modelo, demanda de tareas variable,
   MIS-v2, transferencia ni aprendizaje endógeno. D1/D2 cambian conjuntamente
   amplitud y persistencia. Los intervalos son descriptivos.

**Conclusión:** en D0/D1/D2, el beneficio frente al mapa fijo queda explicado
por competencias actuales observables más reorganización. La ablación muestra
que esa información mejora LinUCB; no muestra beneficio adicional de su
aprendizaje estadístico frente a P0. No se extrapola a entornos inciertos ni a
competencias que evolucionan por las acciones.

Ontología: **A**, escenario sintético D0/D1/D2 congelado; **B**, outcomes
Bernoulli y competencias exógenas, con aprendizaje de parámetros sólo en
LinUCB (sin aprendizaje de competencias); **C**, comparadores FIXED-OPT,
LinUCB+matching/greedy, P0 reactivo y oráculo evaluador.

Reproducción focalizada:

```bash
PYTHONPATH=src pytest -q tests/test_hls_dynamicity_information_ablation.py \
  tests/test_hls_dynamicity_sensitivity.py \
  tests/test_hls_lab_nk_linucb_assignment.py \
  tests/test_hls_lab_nk_assignment.py tests/test_linucb.py
PYTHONPATH=src python experiments/run_hls_dynamicity_information_ablation.py
```

Código y evidencia: [runner](../../experiments/run_hls_dynamicity_information_ablation.py),
[pruebas](../../tests/test_hls_dynamicity_information_ablation.py) y
[resultados compactos por seed y condición](../../results/experiments/hls_dynamicity_information_ablation/results.json).
Se superaron 38 pruebas focalizadas; no se ejecutó la suite completa. El runner,
JSON y políticas de D0/D1/D2 originales, LinUCB y optimizador bipartito no se
modificaron.

### 2026-10-20 — Competencias observadas con incertidumbre en D0/D1/D2

**Estado: campaña exploratoria acotada ejecutada.** Se reutilizó exactamente
la generación D0/D1/D2 del [runner base](../../experiments/run_hls_dynamicity_sensitivity.py)
y las organizaciones del estudio de [ablación informacional](../../experiments/run_hls_dynamicity_information_ablation.py).
Se añadieron niveles de ruido de observación `sigma={0, 0.10, 0.20}`; no se
alteraron trayectorias reales, LinUCB, el matching bipartito ni sus ecuaciones.

#### Definición y límites de información

- **Estado real:** `C_true[i,k,t]` sigue las trayectorias exógenas D0/D1/D2
  congeladas y genera outcomes Bernoulli con media `C_true`. El ruido de
  reward usa el flujo previo `seed XOR 0xA11CE`.
- **Observación disponible:** `C_obs=clip(C_true + sigma*Z, 0, 1)`, con
  `Z~N(0,1)`. Para cada seed se genera una sola matriz estandarizada Z con
  flujo separado (`seed XOR 0x0B5E7A`); la misma Z se escala para σ=0/.10/.20,
  se comparte entre D0/D1/D2 y la reciben P0 y LinUCB. El evaluador genera los
  mismos outcomes potenciales por pareja/periodo para las cuatro
  organizaciones.
- **Políticas ejecutables:** FIXED-OPT se entrena sólo con las 20 seeds de
  entrenamiento y medias de reward conocidas en entrenamiento; no ve
  evaluación. P0 recibe C_obs y requisitos públicos; LinUCB recibe C_obs y
  actualiza exclusivamente con rewards de aristas seleccionadas. Ninguna
  recibe C_true, shocks futuros ni el matching del oráculo. El oráculo usa
  C_true sólo para evaluación, regret y coincidencia óptima.
- Se conserva el contrato del matching existente: asignación uno-a-uno con
  presupuesto máximo 3 (no obligación de cubrir las tres tareas). Para mantener
  igualdad de acciones factibles, P0 evalúa las 34 asignaciones permitidas de
  cardinalidad 0–3. A σ=0, todas las políticas producen 900 asignaciones por
  réplica y la salida replica el estudio previo; con ruido, un empate en cero
  puede dejar una arista sin asignar. Se registra consumo efectivo.

#### Resultados

Cada celda usa 20 seeds emparejadas y 300 periodos. Reward es media acumulada
realizada (SD); regret es pseudo-regret medio respecto al óptimo que conoce la
competencia real; `opt.` es fracción de periodos que coincide con la asignación
óptima. `F`, `P`, `L` y `O` denotan FIXED-OPT, P0 reactivo, LinUCB+matching y
oráculo evaluador, respectivamente.

| Dinamismo | σ | F reward (SD) | P reward (SD) | L reward (SD) | O reward (SD) |
|---|---:|---:|---:|---:|---:|
| D0 | 0.00 | 634.150 (14.299) | 634.150 (14.299) | 611.950 (16.797) | 634.150 (14.299) |
| D0 | 0.10 | 634.150 (14.299) | 631.500 (13.721) | 584.000 (14.275) | 634.150 (14.299) |
| D0 | 0.20 | 634.150 (14.299) | 595.650 (9.184) | 567.050 (12.605) | 634.150 (14.299) |
| D1 | 0.00 | 581.900 (40.186) | 614.450 (21.252) | 604.250 (20.616) | 614.450 (21.252) |
| D1 | 0.10 | 581.900 (40.186) | 608.750 (23.526) | 581.050 (18.237) | 614.450 (21.252) |
| D1 | 0.20 | 581.900 (40.186) | 573.900 (19.606) | 558.800 (16.767) | 614.450 (21.252) |
| D2 | 0.00 | 584.550 (41.163) | 679.150 (17.825) | 676.800 (18.048) | 679.150 (17.825) |
| D2 | 0.10 | 584.550 (41.163) | 677.500 (18.069) | 660.450 (24.167) | 679.150 (17.825) |
| D2 | 0.20 | 584.550 (41.163) | 652.050 (21.150) | 634.900 (24.927) | 679.150 (17.825) |

| D | σ | F regret / opt. | P regret / opt. | L regret / opt. | O regret / opt. |
|---|---:|---:|---:|---:|---:|
| D0 | 0.00 | 0.000 / 1.000 | 0.000 / 1.000 | 22.955 / .870 | 0.000 / 1.000 |
| D0 | 0.10 | 0.000 / 1.000 | 2.770 / .984 | 52.425 / .697 | 0.000 / 1.000 |
| D0 | 0.20 | 0.000 / 1.000 | 41.225 / .760 | 69.732 / .604 | 0.000 / 1.000 |
| D1 | 0.00 | 36.780 / .591 | 0.000 / 1.000 | 12.410 / .921 | 0.000 / 1.000 |
| D1 | 0.10 | 36.780 / .591 | 7.185 / .934 | 38.260 / .743 | 0.000 / 1.000 |
| D1 | 0.20 | 36.780 / .591 | 44.960 / .672 | 62.127 / .583 | 0.000 / 1.000 |
| D2 | 0.00 | 91.320 / .493 | 0.000 / 1.000 | 2.717 / .985 | 0.000 / 1.000 |
| D2 | 0.10 | 91.320 / .493 | 1.420 / .992 | 20.920 / .891 | 0.000 / 1.000 |
| D2 | 0.20 | 91.320 / .493 | 28.603 / .848 | 48.445 / .759 | 0.000 / 1.000 |

El uso de recursos fue 900 unidades en todas las condiciones σ=0 y para
FIXED-OPT/oráculo en todas las celdas. En σ=.20, el promedio de P0/L fue
D0 `899.95/899.95`, D1 `899.85/899.90` y D2 `900/900`; el resto fue 900. La
RMSE observacional media fue σ=.10: D0 `0.1004`, D1 `0.1004`, D2 `0.1000`;
σ=.20: D0 `0.1935`, D1 `0.1942`, D2 `0.1912`.
Fracción recortada a los límites en σ=.20: D0 `.0420`, D1 `.0380`, D2 `.0581`.

Diferencia pareada `P0 − LinUCB` en reward acumulado (IC t descriptivo 95%):

| Condición | σ=.00 | σ=.10 | σ=.20 |
|---|---:|---:|---:|
| D0 | +22.200 `[19.127,25.273]` | +47.500 `[43.675,51.325]` | +28.600 `[24.427,32.773]` |
| D1 | +10.200 `[7.329,13.071]` | +27.700 `[21.722,33.678]` | +15.100 `[10.694,19.506]` |
| D2 | +2.350 `[0.837,3.863]` | +17.050 `[12.446,21.654]` | +17.150 `[13.399,20.901]` |

Cambio de reward medio frente a σ=0 (P0 / LinUCB): D0, σ=.10 `−2.650/−27.950`
y σ=.20 `−38.500/−44.900`; D1 `−5.700/−23.200` y `−40.550/−45.450`; D2
`−1.650/−16.350` y `−27.100/−41.900`. D1 con σ=.10 deja P0 sobre FIXED-OPT
(`+26.850`) pero LinUCB ligeramente debajo (`−0.850`); con σ=.20 ambas
organizaciones quedan debajo del fijo (`−8.000` y `−23.100`). En D2 σ=.20
ambas siguen sobre el fijo (`+67.500` y `+50.350`).

#### Interpretación y conclusión

- **σ=0 reproducido exactamente:** un chequeo automatizado comparó por seed
  las rutas de asignación y los rewards realizados con el artefacto anterior en
  D0/D1/D2; las tres validaciones pasaron. También coinciden los resúmenes
  precedentes.
- **P0 supera a LinUCB en las nueve celdas.** En cada condición la diferencia
  pareada favorece P0; los intervalos descriptivos anteriores no incluyen
  cero. El aprendizaje contextual no aporta ventaja frente a la organización
  reactiva en este entorno, ni con observación perfecta ni con ruido moderado o
  elevado.
- **La incertidumbre reduce la adaptación de ambos métodos**, sobre todo a
  σ=.20. LinUCB pierde más que P0 frente a σ=0 en todas las combinaciones. P0
  mantiene ventaja sobre FIXED-OPT en D1 σ=.10 y ambas σ de D2, pero deja de
  hacerlo en D1 σ=.20; D0 sigue teniendo un fijo óptimo.
- **Interacción descriptiva D×σ:** D2 retiene más de la ventaja del dinamismo
  bajo σ=.20 porque la amplitud de la matriz cambiante es mayor; D1 pierde la
  ventaja reactiva frente al fijo con incertidumbre elevada. No puede
  atribuirse esto sólo a frecuencia: D1/D2 difieren simultáneamente en amplitud
  y persistencia. D0 demuestra que la incertidumbre también perjudica aunque
  no haya cambios de régimen.
- LinUCB ve contexto ruidoso mientras su feedback tiene media dependiente de
  competencia verdadera. Por tanto hay error en covariables (y clipping), no
  sólo “menos información”; las ecuaciones originales de LinUCB no corrigen
  errores de medición. El mecanismo puede degradarse por esa especificación.
- Las conclusiones son para rewards sintéticos con `E[R]=C_true` conocido,
  observación gaussiana/clipped y 20 seeds exploratorias. No demuestran
  superioridad general, calibración bajo otras distribuciones de error ni
  aprendizaje de competencias.

**Conclusión:** no hay evidencia de ventaja adicional de aprendizaje
contextual sobre P0 cuando ambos reciben las mismas competencias observadas.
Con incertidumbre, el selector P0 fue más robusto en estas condiciones; a
σ=.20 el dinamismo D2 aún permite superar el fijo, mientras D1 no. Esto
caracteriza el sistema sintético usado, no un resultado general.

Ontología: **A**, las trayectorias/demanda D0/D1/D2 permanecen congeladas y se
añade sólo un canal observacional; **B**, rewards usan `C_true`, policies ven
`C_obs`, y sólo LinUCB aprende parámetros (no evolucionan competencias);
**C**, FIXED-OPT, P0 reactivo con matching, LinUCB+matching y oráculo
evaluador.

Reproducción focalizada:

```bash
PYTHONPATH=src pytest -q tests/test_hls_dynamicity_observation_uncertainty.py \
  tests/test_hls_dynamicity_information_ablation.py \
  tests/test_hls_dynamicity_sensitivity.py \
  tests/test_hls_lab_nk_linucb_assignment.py \
  tests/test_hls_lab_nk_assignment.py tests/test_linucb.py
PYTHONPATH=src python experiments/run_hls_dynamicity_observation_uncertainty.py
```

Código y evidencia: [runner](../../experiments/run_hls_dynamicity_observation_uncertainty.py),
[pruebas](../../tests/test_hls_dynamicity_observation_uncertainty.py) y
[resultados/configuración compactos](../../results/experiments/hls_dynamicity_observation_uncertainty/results.json).
σ=0 valida contra los resultados anteriores; las matrices reales y ruido son
reproducibles desde los seeds y las trayectorias se guardan codificadas. Se
ejecutaron 43 pruebas focalizadas; la suite completa no se ejecutó. No se
modificaron experimentos anteriores ni algoritmos existentes.

### 2026-10-20 — Consolidación experimental y plan científico S1–S4

**Estado: cierre documental de la evidencia enumerada; sin nuevos experimentos.**
Esta entrada indexa resultados existentes y actualiza su interpretación
operativa; no sustituye las entradas históricas. Se conserva la ontología
A/B/C de [HLS Ontology v0.1](../architecture/HLS_ONTOLOGY_V0_1_2026-10-23.md):
escenario, mecanismos y organizaciones. Los seis documentos de referencia
indicados para esta tarea existen. El [original work plan](../project/HLS_ORIGINAL_WORK_PLAN_TO_2026-10-30.md)
permanece como línea base histórica; no se modifica retrospectivamente.

#### 1. Cierre e índice de bloques experimentales

**CERRADO** significa que el estudio queda concluido en su alcance declarado,
no que pruebe validez universal. Los informes y artefactos enlazados conservan
configuraciones, trazas y comandos; esta tabla evita reproducirlos íntegramente.

| Bloque / estado | A — escenario | B — mecanismo | C — comparadores | Resultado y límite sustentado | Evidencia |
|---|---|---|---|---|---|
| G1, G2, G3/G3-H y RQ0 — **CERRADOS** | Mundos sintéticos exactos distintos, con heterogeneidad, tareas y recursos definidos por cada modelo. | G1 sin aprendizaje; G2 aprendizaje por asignación; G3/G3-H desarrollo/MIS bajo supuestos propios. | Óptimos, asignaciones y clases joint/separated de cada formulación. | G1: heterogeneidad no basta. G2/G3: el valor del desarrollo depende de la sensibilidad de asignación y oportunidades futuras. RQ0: inclusión de políticas y gap sólo bajo condiciones finitas; no superioridad universal. No combinar resultados de modelos distintos. | [Síntesis](../research/HLS_SCIENTIFIC_EVIDENCE_SYNTHESIS_2026-10-20.md), [análisis matemático](../research/HLS_MATHEMATICAL_ANALYSIS_2026-10-22.md), [G1](../theory/HLS_G1_STATIC_EXPERIMENTAL_GROUND_TRUTH.md), [G2](../theory/HLS_G2_DYNAMIC_GROUND_TRUTH.md), [G3/G3-H](../experimental_foundations/HLS_G3_ORGANIZATIONAL_VALUE_GROUND_TRUTH.md), [RQ0](../theory/rq0_routing_integration_boundaries.md). |
| N×K/C5 y HLS-RQ1 5×3×100 — **CERRADO** | Cinco agentes, tres tareas, horizonte 100 y demanda C5 emparejada. | MIS-v2; transferencia desactivada. | FIXED-OPT empírico de entrenamiento, REACTIVE y ANTICIPATORY a dos periodos. | Las tres políticas coincidieron en `98.77020926533908` en la evaluación reportada. Nulo específico a este escenario; no implica equivalencia general. | [Runner](../../experiments/run_hls_rq1_learning_organization.py), [tests](../../tests/synthetic/test_hls_rq1_learning_organization.py), [JSON](../../results/experiments/hls_rq1_learning_organization/results.json). |
| HLS-P1 anticipación — **CERRADO** | G0/RQ0 sintético; dos agentes/tareas, horizonte 4; seis configuraciones controladas. | MIS-v2 y una ablación `enabled=False`. | FIXED-OPT exhaustivo (1.296 mapas), REACTIVE, HLS-ANTICIPATORY exacto. | Hubo ventaja adaptativa pequeña en **una de seis configuraciones** (`V_A=3.723545666944881`, `V_F=3.6990500567473568`, `V_R=3.698638746537539`); en la ablación de esa configuración el gap desapareció. No hay generalización demostrada. Se conserva el REFRAME inicial, distinto del cierre. | [Cierre P1](#hls-p1-cierre-exacto-del-estudio-finito), [código](../../src/hls/synthetic/hls_p1.py), [tests](../../tests/synthetic/test_hls_p1.py), [resultado inicial](../../results/experiments/hls_p1_validated/results.json). |
| EXP3 — **CERRADO** | Bandit sintético de tres agentes/brazos, recompensa Bernoulli acotada; capacidad fija. | EXP3 publicado, feedback sólo del brazo elegido. | EXP3, uniforme y mejor brazo fijo retrospectivo. | La comprobación matemática/tests del algoritmo queda separada de su piloto sintético HLS. No reproduce el estudio ni acredita eficacia general o en N×K contextual. | [Módulo](../../src/hls/exp3.py), [tests](../../tests/test_exp3.py), [runner](../../experiments/run_hls_exp3_validation.py), [JSON](../../results/experiments/hls_exp3_validation/results.json). |
| LinUCB disjoint — **CERRADO** | Selección contextual de un agente para tarea observable, una decisión por periodo y feedback parcial. | Aprende parámetros de selección, no competencias. | LinUCB, EXP3 context-free, uniforme, referencias retrospectivas y oráculo evaluador. | Algoritmo publicado de selección contextual; el benchmark original es recomendación contextual con feedback parcial, no un benchmark experimental HLS. La integración no reproduce Yahoo! ni sus resultados publicados. | [Módulo](../../src/hls/linucb.py), [tests](../../tests/test_linucb.py), [runner](../../experiments/run_hls_linucb_validation.py), [JSON](../../results/experiments/hls_linucb_validation/results.json). |
| Asignación bipartita SciPy — **CERRADO** | Lotes sintéticos 3×3, asignación uno-a-uno y recompensas explícitas. | Competencia inerte; no aprendizaje. | SciPy `linear_sum_assignment`, greedy y fijo offline. | Se validó el óptimo de asignación frente a enumeración en instancias pequeñas. SciPy usa Jonker–Volgenant; no se afirma implementación paso a paso del método húngaro de Kuhn. No reemplaza el contrato divisible N×K. | [Módulo](../../src/hls/hls_lab_nk_assignment.py), [tests](../../tests/test_hls_lab_nk_assignment.py), [runner](../../experiments/run_hls_hungarian_assignment.py), [JSON](../../results/experiments/hls_hungarian_assignment/results.json). |
| LinUCB × MIS-v2 — **CERRADO** | C5 sintético, tres agentes/tareas, 300 periodos, semillas emparejadas. | LinUCB aprende selección; MIS-v2 modifica capacidades; mecanismos distintos. | LinUCB, fijo especializado, P0; capacidad constante frente a evolución. | MIS-v2 modificó el sistema, pero LinUCB no superó a fijo/P0 en el piloto. No evaluó transferencia ni establece superioridad de un mecanismo. | [Runner](../../experiments/run_hls_linucb_mis_v2_interaction.py), [tests](../../tests/synthetic/test_hls_linucb_mis_v2_interaction.py), [JSON](../../results/experiments/hls_linucb_mis_v2_interaction/results.json). |
| MIS-v2 vs Nembhard Direct — **CERRADO** | C5 3×3 sintético, 90 periodos, diez trayectorias emparejadas. | MIS-v2 competencia vs curva de experiencia/productividad Nembhard Direct. Transferencia no evaluada. | LinUCB, mapa especializado fijo y P0 bajo ambos mecanismos. | El ranking depende de organización y métrica. Se adaptó Nembhard Direct; no se reprodujo el artículo completo ni se validó su formulación de transferencia. | [Mecanismo](../../src/hls/mechanisms/nembhard_direct.py), [runner](../../experiments/run_hls_learning_mechanism_comparison.py), [tests](../../tests/synthetic/test_hls_learning_mechanism_comparison.py), [JSON](../../results/experiments/hls_learning_mechanism_comparison/results.json). |
| LinUCB + matching — **CERRADO** | Asignación concurrente agente-tarea 3×3. | LinUCB disjoint puntúa pares y actualiza sólo por outcomes observados; matching compone puntuaciones. | Matching conjunto, greedy con igual matriz, fijo entrenado y oráculo evaluador. | Es una adaptación multiple-play de ingeniería. Las garantías de LinUCB original no se heredan automáticamente al protocolo de acción conjunta/feedback parcial. | [Adapter](../../src/hls/hls_lab_nk_linucb_assignment.py), [runner](../../experiments/run_hls_linucb_bipartite_hybrid.py), [tests](../../tests/test_hls_lab_nk_linucb_assignment.py), [JSON](../../results/experiments/hls_linucb_bipartite_hybrid/results.json). |
| D0/D1/D2 — **CERRADO** | Competencias exógenas constantes, moderadamente cambiantes o más dinámicas; 3×3, 300 periodos, 20 semillas. | Sin MIS-v2/Nembhard; competencias no dependen de la organización. | LinUCB+matching, LinUCB+greedy, fijo entrenado y oráculo dinámico evaluador. | Reward acumulado: matching `611.950/604.250/676.800`; fijo `634.150/581.900/584.550`; oráculo `634.150/614.450/679.150`. En estas condiciones D1/D2 hicieron más valiosa la reorganización; no atribuir la ventaja automáticamente al aprendizaje. | [Runner](../../experiments/run_hls_dynamicity_sensitivity.py), [tests](../../tests/test_hls_dynamicity_sensitivity.py), [JSON](../../results/experiments/hls_dynamicity_sensitivity/results.json). |
| Ablación informacional — **CERRADO** | El mismo D0/D1/D2; reward esperado público `E[R(i,k,t)]=c(i,k,t)`. | P0 no aprende parámetros; LinUCB sí aprende política desde rewards seleccionados. | P0+matching, LinUCB con/sin competencia contextual, greedy, fijo y oráculo. | P0 igualó al oráculo con competencias observables: `634.150/614.450/679.150`. En este mundo el matching reactivo resuelve directamente el óptimo por periodo; no hay beneficio adicional probado de LinUCB. | [Runner](../../experiments/run_hls_dynamicity_information_ablation.py), [tests](../../tests/test_hls_dynamicity_information_ablation.py), [JSON](../../results/experiments/hls_dynamicity_information_ablation/results.json). |
| D0/D1/D2 × incertidumbre — **CERRADO** | Mismas trayectorias reales; `C_obs=clip(C_true+ε,0,1)`, σ `0/.10/.20`; 20 semillas × 300 periodos/celda. | Reward usa estado real; observación ruidosa común a P0/LinUCB; sólo LinUCB aprende parámetros. | Fijo, P0, LinUCB+matching y oráculo con verdad sólo evaluador. | P0 superó LinUCB en las nueve celdas; el ruido redujo el desempeño dinámico con efecto dependiente de D. σ=0 reproduce la ablación previa. Es conclusión del reward/ruido sintético especificado, no de otros modelos. | [Runner](../../experiments/run_hls_dynamicity_observation_uncertainty.py), [tests](../../tests/test_hls_dynamicity_observation_uncertainty.py), [JSON](../../results/experiments/hls_dynamicity_observation_uncertainty/results.json). |

#### 2. Hallazgo fechado 20/10/2026 — reorganización frente a aprendizaje

**“Separación experimental entre reorganización adaptativa y aprendizaje
contextual”.** En los escenarios sintéticos D0/D1/D2 estudiados, reorganizar
con información actualizada pudo aportar ventajas frente a FIXED-OPT sin
aprendizaje contextual. Con observación perfecta, P0 igualó al oráculo porque
la media por pareja era competencia observable (`E[R]=c`). En las nueve
condiciones con ruido, P0 superó a LinUCB. Así, el beneficio de la adaptación
organizativa no debe confundirse con el del aprendizaje de selección. Este
hallazgo se limita a escenarios sintéticos, recompensa conocida, matching
uno-a-uno, clipping gaussiano y las muestras exploratorias declaradas; no es
una afirmación universal ni evidencia con datos reales.

#### 3. Plan de investigación por escenarios A/B/C

Estados: **IMPLEMENTADO** = código disponible; **VALIDADO** = contrato probado
dentro del alcance; **EVALUADO** = comparación ejecutada; **PENDIENTE** = falta
evidencia o componente. Estos estados no son equivalentes.

| Escenario | Supuestos / referencias metodológicas apropiadas | HLS disponible y estado | Pendiente, comparadores y pregunta concreta | Prioridad |
|---|---|---|---|---|
| **S1 — Estático estricto** | Competencias, demanda, restricciones y óptimo estables. Matching exacto; LP/MIP si las restricciones exceden la asignación bipartita; greedy como comparador. | SciPy assignment **IMPLEMENTADO, VALIDADO, EVALUADO** contra enumeración. | No repetir validación. Evaluar coste/escalabilidad sólo ante un aumento justificado de tamaño o nueva restricción. | Mantenimiento; sin campaña ahora. |
| **S2 — Estacionario con demanda variable** | Competencias/ley estacionarias. S2a decisiones independientes y recursos renovados: optimización exacta repetida por periodo. S2b acoplamiento temporal real: DP/MDP, MPC u optimización estocástica. | C5, demanda secuencial y matching disponibles; secuencias evaluadas en las instancias existentes. | Aplicar métodos temporales sólo si hay inventario, presupuesto persistente, setup, cola u otra dependencia que conecte periodos. Pregunta: ¿el óptimo instantáneo deja de ser suficiente? Igualar información/costes. | Condicional a formalizar acoplamiento. |
| **S3 — Dinámico exógeno** | Estado cambia independientemente de asignaciones. S3a observable y recompensa conocida: P0/optimización reactiva. S3b parcial o recompensa desconocida: Sliding-Window UCB, Discounted UCB, Rexp3 o detección de cambios; Garivier–Moulines (2011) y Besbes–Gur–Zeevi (2014) son candidatos metodológicos, no óptimos universales. | D0/D1/D2, matching, P0/LinUCB y ruido observacional **IMPLEMENTADOS, VALIDADOS, EVALUADOS** en el caso archivado. | No repetir ni extender D0/D1/D2 por rutina. Falta evaluar un problema donde recompensa/estado no sean directamente conocidos; separar valor de información, reorganización y estimación. Comparadores informacionalmente iguales. | Segunda prioridad, sólo con pregunta S3b y método justificado. |
| **S4 — Dinámico endógeno** | Exposición/acciones cambian capacidades futuras. MIS-v2 y Nembhard Direct son mecanismos diferentes. DP/MDP como referencia finita de modelo conocido; MPC/RL sólo si lo requieren horizonte o desconocimiento. | MIS-v2, transición de enseñanza, Nembhard Direct y trazado **IMPLEMENTADOS/VALIDADOS** en contrato; P1 y comparaciones de mecanismos **EVALUADOS** en alcances acotados. | Transferencia Nembhard no validada. Falta medir interacción MIS-v2×enseñanza con catálogo, costes, información y reward comunes; comprobar si P0/P1/P2 son comparadores compatibles según reglas reales. | **Primera prioridad científica** por centralidad HLS y brecha concreta; primero diseñar protocolo, sin ejecutar. |

#### 4. Principios para la investigación siguiente

1. Seleccionar métodos desde dinámica, información, objetivo y restricciones
   del problema, no desde el nombre o disponibilidad del algoritmo.
2. Preferir formulaciones publicadas verificables y protocolos reproducibles;
   distinguir implementación fiel independiente de reproducción de resultados.
3. Analizar si un contraste puede distinguir estimandos antes de implementar.
4. Reportar por separado corrección matemática, eficacia experimental y
   generalización.
5. Separar cambios del escenario, información, aprendizaje de política,
   evolución de competencias y organización.
6. No ajustar escenarios por el resultado; conservar hallazgos nulos/negativos.
7. No reabrir estudios cerrados sin una pregunta nueva y explícita.
8. Igualar información, recursos, oportunidades y aleatoriedad; identificar
   oráculos como referencias evaluativas, no políticas desplegables.
9. Diferenciar evidencia sintética de validación con datos reales.
10. Un algoritmo fuera de las hipótesis del problema no es “mejor” por defecto.

#### 5. Siguiente actividad priorizada — diseño, no ejecución

Preparar un único protocolo acotado **S4: interacción MIS-v2 × enseñanza bajo
demanda cambiante**, sin implementar ni ejecutar. Esta prioridad sigue la
pregunta HLS de cómo aprendizaje y transferencia interactúan bajo restricciones:
los mecanismos y recursos N×K existen, pero la evidencia de ejecución no
establece todavía el signo del efecto colectivo de combinarlos. El análisis
matemático ya distingue la interacción mecánica en una transición compartida
de la interacción organizativa cuando una política responde al estado; ambas
deben tener estimandos separados.

El diseño deberá conservar catálogo factible y cargos de recursos al apagar
una transición, fijar observabilidad y emparejar estados/demanda/semillas;
comparar primero acciones idénticas (efecto mecánico) y sólo después, si está
justificado, respuestas de P0/P1/P2 verificadas por regla. Separar output,
éxito, competencia, esfuerzo productivo y esfuerzo de enseñanza. Evidencia
mínima de cierre del diseño: tabla de controles/estimandos, controles nulos,
pruebas de factibilidad y criterios de parada. Dependencias: [priorización
21/10](../research/HLS_PRIORITIZED_INVESTIGATIONS_2026-10-21.md), [análisis
22/10](../research/HLS_MATHEMATICAL_ANALYSIS_2026-10-22.md) y [ontología
v0.1](../architecture/HLS_ONTOLOGY_V0_1_2026-10-23.md). **Estado: propuesta
de diseño pendiente; no implementada ni ejecutada.** Toda ejecución requiere
autorización específica; no cambia retrospectivamente el calendario ni
decisiones anteriores.

### 2026-10-20 — S1: referencia fundamental de asignación estática

**Estado: CERRADO — caso canónico determinista establecido.** Se reutilizan
[`HungarianAssignmentOptimizerNK`](../../src/hls/hls_lab_nk_assignment.py),
[`greedy_assignment`](../../experiments/run_hls_hungarian_assignment.py) y
la enumeración independiente ya alojada en
[`test_hls_lab_nk_assignment.py`](../../tests/test_hls_lab_nk_assignment.py).
No se creó otro solver, generador ni documento. S1 queda limitado a asignación
bipartita lineal estática; no incluye incertidumbre, aprendizaje, cooperación,
transferencia, enseñanza ni restricciones temporales.

#### Definición y correspondencia A/B/C

Para agentes `i∈{0,…,N−1}` y tareas `k∈{0,…,K−1}`, `C[i,k]` es recompensa
esperada conocida y constante. Se maximiza
`Σ_i Σ_k C[i,k] x[i,k]`, sujeto a `Σ_k x[i,k]≤1`,
`Σ_i x[i,k]≤1`, `x[i,k]∈{0,1}` y al presupuesto unitario común (hasta
`min(N,K)` parejas). No asignar queda permitido; las competencias y los demás
parámetros no evolucionan y no hay transición de ambiente.

- **A — Escenario:** `N=K=3`, matriz constante y presupuesto 3.
- **B — Mecanismos:** inertes; no se actualizan competencias y no se ejecuta
  MIS-v2, Nembhard, LinUCB, EXP3, enseñanza ni transferencia.
- **C — Organizaciones:** optimizador exacto bipartito existente; greedy
  determinista existente; enumeración exhaustiva como verificación
  independiente, no como política competidora.

#### Instancia canónica y resultado

```text
             t0    t1    t2
       a0   1.00  0.90  0.00
       a1   0.90  0.00  0.00
       a2   0.00  0.80  0.80
```

La matriz representa especializaciones distintas y dos conflictos locales
por los valores altos de `a0–t0`/`a1–t0` y `a0–t1`/`a2–t1`. Su máximo global
es único.

| Método | Asignación (agente, tarea) | Reward total | Gap respecto al óptimo |
|---|---|---:|---:|
| Solver exacto existente | `(a0,t1), (a1,t0), (a2,t2)` | `2.60` | `0.00` |
| Enumeración exhaustiva | `(a0,t1), (a1,t0), (a2,t2)` | `2.60` | `0.00` |
| Greedy por aristas descendentes | `(a0,t0), (a2,t1), (a1,t2)` | `1.80` | `0.80` |

Greedy acepta primero `(a0,t0)=1.00`, bloqueando la reasignación global; el
último emparejamiento `(a1,t2)` tiene recompensa cero y procede de la regla
greedy ya existente de completar hasta el cardinal permitido. El óptimo
asigna tres parejas positivas. Todas las asignaciones respetan unicidad de
agente/tarea y presupuesto 3. El solver y la enumeración coinciden, la
enumeración encuentra una sola solución de valor `2.60`, y la repetición del
solver produce la misma asignación y reward.

Tiempos de una ejecución local de esta instancia (sólo descriptivos, no
benchmarks): solver SciPy aproximadamente `0.000071 s`, greedy
`0.000010 s`, enumeración de `3!` permutaciones `0.000005 s`. La resolución
exacta reutiliza `scipy.optimize.linear_sum_assignment`, cuyo backend SciPy
es Jonker–Volgenant; no se afirma reimplementar el algoritmo histórico de
Kuhn.

#### Validación y reproducción

Se añadió un único test de regresión canónico que comprueba óptimo único,
igualdad solver–enumeración, resultado greedy, factibilidad y repetibilidad.
Comando focalizado:

```bash
PYTHONPATH=src pytest -q tests/test_hls_lab_nk_assignment.py
```

Resultado: **10 passed** (incluye los nueve tests previos del módulo y el caso
S1 añadido). No se ejecutó la batería general ni una campaña.

**Interpretación científica:** bajo las hipótesis S1, el solver exacto
existente entrega el óptimo del problema bipartito lineal. El caso demuestra
que la optimización global puede superar la decisión greedy local en esta
matriz; no es una contribución algorítmica nueva ni demuestra superioridad
general de HLS. Este cierre verifica el caso de referencia, no escalabilidad
ni otros modelos de restricciones.

### 2026-10-20 — S2a: demanda variable sin acoplamiento temporal

**Estado: CERRADO — referencia determinista reproducible.** S2a cambia S1
únicamente al permitir que el vector de demanda varíe por periodo. Las
competencias y la recompensa esperada son conocidas y constantes; se renuevan
los recursos en cada periodo; no hay coste de cambio, cola, presupuesto
intertemporal, aprendizaje, transferencia ni restricción temporal. La demanda
actual se observa antes de decidir; no se observa el futuro porque no es
necesario para este problema separable.

#### Formulación y representación de demanda

Para periodo `t`, la demanda `d[k,t]` es un número entero de unidades de
trabajo. Cada unidad se expande como una columna/tarea individual que conserva
el tipo `k`; la matriz de recompensa de esa unidad copia `C[:,k]`. La
asignación binaria `x[i,j,t]` sobre unidades expandidas permite varias
asignaciones del mismo tipo a agentes distintos y respeta una unidad por
agente y por unidad de trabajo, con capacidad compartida 3 por periodo. Por
tipo, la suma asignada no puede exceder `d[k,t]`. Se documenta la función
objetivo equivalente `Σ_t Σ_i Σ_k C[i,k] x[i,k,t]` en la formulación agregada
por tipo.

Esta representación sí es compatible con el optimizador existente si cada
unidad demandada se presenta como una columna con identificador único. No se
modificó el solver. El contrato `ProblemSpecNK` exige dimensión de tarea no
vacía; por eso, en el periodo sin demanda se registra directamente el único
conjunto factible, la asignación vacía con reward y uso de recursos cero. Es
un caso trivial explícito, no un cambio del modelo ni una aproximación.

#### Correspondencia A/B/C e instancia

- **A — Escenario:** tres agentes y tres tipos, `C=((1,.9,0),(.9,0,0),(0,.8,.8))`,
  capacidad máxima tres unidades por periodo. Secuencia determinista de
  demandas `(1,1,1)`, `(2,0,1)`, `(3,1,0)`, `(0,0,0)`.
- **B — Mecanismos:** inertes; `C` se conserva sin cambios durante los cuatro
  periodos. No se ejecutan MIS-v2, Nembhard, LinUCB, EXP3 ni transferencia.
- **C — Organizaciones:** solver bipartito existente por periodo; greedy
  existente por periodo; enumeración independiente de todas las asignaciones
  factibles de cada periodo y de todas las secuencias factibles del horizonte.

La secuencia contiene una unidad de cada tipo, dos unidades de `t0` en un
periodo, cuatro unidades demandadas con capacidad total tres, un cambio de
combinación y un periodo sin trabajo. En el periodo de demanda excedente se
atienden dos de las tres unidades `t0` y la unidad `t1`; queda una unidad `t0`
sin atender por capacidad, no por falta de oferta de trabajo.

#### Resultados por periodo

| t | Demanda `(t0,t1,t2)` | Solver exacto | Reward | Greedy | Reward | No atendido exacto `(t0,t1,t2)` |
|---:|---|---|---:|---|---:|---|
| 0 | `(1,1,1)` | `(a0,t1),(a1,t0),(a2,t2)` | `2.60` | `(a0,t0),(a2,t1),(a1,t2)` | `1.80` | `(0,0,0)` |
| 1 | `(2,0,1)` | `(a0,t0),(a1,t0),(a2,t2)` | `2.70` | igual al exacto | `2.70` | `(0,0,0)` |
| 2 | `(3,1,0)` | `(a0,t0),(a1,t0),(a2,t1)` | `2.70` | igual al exacto | `2.70` | `(1,0,0)` |
| 3 | `(0,0,0)` | `∅` | `0.00` | `∅` | `0.00` | `(0,0,0)` |

| Horizonte | Reward total | Uso total de recursos | Diferencia frente al global enumerado |
|---|---:|---:|---:|
| Solver exacto por periodo | `8.00` | `9` | `0.00` |
| Greedy por periodo | `7.20` | `9` | `−0.80` |
| Óptimo global por enumeración exhaustiva | `8.00` | `9` | `0.00` |

La enumeración independiente evaluó **84.388 secuencias factibles** (producto
de los conjuntos de acciones factibles por periodo). El valor exacto por
periodo coincidió con su máximo global. Greedy no excedió al óptimo en ningún
periodo ni en el horizonte. La repetición determinista reprodujo demandas,
asignaciones, recompensas, capacidad y conteos de unidades; el test excluye
los tiempos de pared, que necesariamente varían.

Los tiempos de una ejecución local fueron aproximadamente `0.000149 s` para
el solver exacto acumulado, `0.000023 s` para greedy y `0.0274 s` para la
enumeración global de secuencias. Son cifras descriptivas de esta instancia y
máquina; no sustentan conclusiones de escalabilidad.

#### Propiedad, validación y límites

La igualdad matemática `max_{x_0,…,x_{T−1}} Σ_t R_t(x_t) = Σ_t max_{x_t}
R_t(x_t)` se sigue de que el conjunto factible del horizonte es el producto
cartesiano de los conjuntos factibles por periodo y la recompensa es aditiva.
El experimento **verifica que esta implementación respeta esa separabilidad**;
no presenta la identidad como descubrimiento científico. La demanda variable
no exige por sí misma aprendizaje ni planificación temporal bajo estas
hipótesis.

Se añadió el runner acotado
[`run_hls_s2a_static_demand.py`](../../experiments/run_hls_s2a_static_demand.py),
el artefacto agregado
[`results.json`](../../results/experiments/hls_s2a_static_demand/results.json)
y pruebas del caso canónico en
[`test_hls_lab_nk_assignment.py`](../../tests/test_hls_lab_nk_assignment.py).
Comandos de reproducción:

```bash
PYTHONPATH=src pytest -q tests/test_hls_lab_nk_assignment.py
PYTHONPATH=src python experiments/run_hls_s2a_static_demand.py
```

Resultado focalizado: **11 passed**. `git diff --check` pasó. La conclusión
queda restringida a competencia/recompensa conocida, unidades idénticas por
tipo, recursos renovables y ausencia de costes, colas, aprendizaje, cambios
de estado o cualquier acoplamiento entre periodos. No se extiende a S2b ni a
los escenarios S3/S4. **S2a: CERRADO.**

### 2026-10-20 — S2b: asignación con presupuesto intertemporal compartido

**Estado: CERRADO — propiedad de acoplamiento verificada en una instancia
finita exacta.** S2b parte de la matriz constante de S1/S2a y mantiene demanda
determinista, conocida por ambas estrategias. La única diferencia estructural
es un presupuesto global `B` no renovable: cada asignación consume una unidad,
con `Σ_t Σ_i Σ_k x[i,k,t] ≤ B`. Se mantienen una unidad por agente y periodo,
un agente por unidad demandada, ausencia de aprendizaje/enseñanza/transferencia,
y ausencia de cualquier otro coste o restricción temporal.

#### Métodos y correspondencia A/B/C

- **A — Escenario:** `N=3`, `K=3`, dos periodos, matriz
  `C=((1,.9,0),(.9,0,0),(0,.8,.8))`, demanda fija
  `d_0=(0,1,0)` y `d_1=(1,0,0)`. La secuencia completa es pública a las dos
  estrategias. El método miope sólo consulta la demanda del periodo corriente.
- **B — Mecanismos:** competencias y recompensas deterministas constantes; no
  hay aprendizaje, transferencia ni incertidumbre.
- **C — Organizaciones:** **MYOPIC** usa el solver bipartito exacto por periodo
  y limita su recurso del periodo a `min(B_restante, capacidad_periodal)`;
  resuelve así el máximo reward inmediato factible, no una asignación greedy.
  **BELLMAN** resuelve el estado `(t,b)` con acciones enumeradas factibles,
  transición `(t,b)→(t+1,b−m)` y terminal `V(T,b)=0`. **ENUMERACIÓN GLOBAL**
  examina independientemente todas las secuencias de asignaciones factibles
  bajo B; no llama a la recursión Bellman.

La recurrencia implementada es
`V(t,b)=max_{a: m(a)≤b}{R_t(a)+V(t+1,b−m(a))}`. El solver existente admite
este límite cardinal al recibir como presupuesto del `ProblemSpecNK` el
presupuesto restante (acotado por la capacidad periodal); no se modificó el
solver. La enumeración independiente reutiliza la generación de emparejamientos
por unidades de S2a y forma el producto cartesiano de acciones periodales,
filtrando secuencias que exceden B.

#### Casos y resultados

Se conservaron la misma C y demanda; sólo cambia B entre los casos de
verificación:

| Caso | B | MYOPIC: asignaciones por periodo; reward | BELLMAN: asignaciones por periodo; reward | Enumeración global | Gap Bellman−miope |
|---|---:|---|---|---:|---:|
| A — presupuesto suficiente | `3` | `t0: (a0,t1), .90`; `t1: (a0,t0), 1.00`; total `1.90` | Igual; total `1.90` | `1.90` (16 secuencias factibles de 16) | `0.00` |
| B — presupuesto vinculante | `1` | `t0: (a0,t1), .90`; `t1: ∅, 0`; total `.90` | `t0: ∅, 0`; `t1: (a0,t0), 1.00`; total `1.00` | `1.00` (7 secuencias factibles de 16) | `+.10` |
| Control B=0 | `0` | `t0: ∅`; `t1: ∅`; total `0` | Igual; total `0` | `0` (1 secuencia factible de 16) | `0` |

En el caso A ambos consumen 2 de las 3 unidades y queda una unidad de
presupuesto. En B, MYOPIC consume la única unidad en el reward inmediato `.90`
y queda sin recursos para el reward futuro `1.00`; BELLMAN reserva esa unidad.
En B=0 ninguna estrategia asigna y el presupuesto queda en cero. En todos los
casos el consumo acumulado no excede B, cada agente trabaja como máximo una
vez por periodo, las asignaciones no exceden demanda y las competencias no
cambian.

#### Verificación e interpretación científica

En los dos periodos de cada caso, el valor MYOPIC coincide con el máximo
obtenido al enumerar las acciones del periodo condicionadas al presupuesto
restante; por tanto el gap no se debe a una heurística débil de asignación.
Bellman coincide exactamente con la enumeración global en A (`1.90`), B
(`1.00`) y B=0 (`0`), y nunca queda por debajo de MYOPIC. La reconstrucción
registra asignaciones, recompensa y presupuesto antes/después de cada periodo.
La repetición produce resultados deterministas.

La causa de la no separabilidad es únicamente la restricción
`Σ_t m_t≤B`: las decisiones periodales compiten por el mismo recurso. Para
esta información completa y horizonte finito, Bellman proporciona el óptimo
global tratable. El ejemplo muestra una condición en la que maximizar cada
periodo por separado pierde valor; no establece que Bellman siempre supere
estrictamente a MYOPIC, una ventaja general de HLS ni una contribución
algorítmica nueva.

Artefactos: [runner S2b](../../experiments/run_hls_s2b_intertemporal_budget.py),
[tests](../../tests/test_hls_s2b_intertemporal_budget.py) y [resultados
agregados](../../results/experiments/hls_s2b_intertemporal_budget/results.json).
Reproducción focalizada:

```bash
PYTHONPATH=src pytest -q tests/test_hls_s2b_intertemporal_budget.py \
  tests/test_hls_lab_nk_assignment.py
PYTHONPATH=src python experiments/run_hls_s2b_intertemporal_budget.py
```

Resultado: **15 passed** en las pruebas focalizadas y regresión del solver de
asignación. `git diff --check` pasó. No se ejecutó campaña ni se modificaron
S1/S2a. **S2b: CERRADO.**

### 2026-10-20 — S3b: competencias desconocidas y no estacionarias

**Estado: CERRADO — comparación sintética reproducible ejecutada.** Se
implementó la estimación de recompensas por pareja agente–tarea y se evaluó su
composición con el matching bipartito existente. El entorno genera
competencias exógenas conocidas sólo por el evaluador; las políticas no reciben
competencias reales, matrices de medias, recompensas contrafactuales ni cambios
futuros. No hay aprendizaje de competencias, transferencia, enseñanza ni
planificación intertemporal.

#### Modelo A/B/C y protocolos

- **A — Escenario:** `N=K=3`, una unidad disponible de cada tarea por periodo,
  capacidad máxima de una tarea por agente y una por tipo, `T=300`. La matriz
  de medias cambia en bloques deterministas, independientemente de las
  asignaciones:
  `c[i,k,t]=0.8` si `k=(i+s_t) mod 3`, y `0.2` en otro caso. Por tanto, todas
  las recompensas potenciales son Bernoulli con media en `[0,1]`, y cada bloque
  tiene una asignación óptima única con recompensa esperada `2.4` por periodo.
  `S3b-0` usa `s_t=0` todo el horizonte; `S3b-1` cambia de `s=0` a `s=1` en
  `t=150`; `S3b-2` usa bloques de 60 periodos con
  `s=(0,1,2,0,1)` y cambios en `t=(60,120,180,240)`. Los índices de asignación
  óptimos son respectivamente `57`; `57→39`; y `57→39→30→57→39`, que
  corresponden a las permutaciones diagonales y dos ciclos desplazados. Así,
  los cambios de matriz sí cambian la asignación óptima. La amplitud `0.6` es
  constante entre condiciones; sólo cambia la frecuencia/número de cambios.
- **B — Mecanismos:** competencia/recompensa esperada exógena; resultado
  observado `r[i,k,t]=1{u[i,k,t]<c[i,k,t]}`. Para cada semilla se generaron de
  antemano números uniformes por periodo y pareja, compartidos entre políticas
  y escenarios. Este acoplamiento sólo lo usa el evaluador: cada política
  recibe resultados Bernoulli únicamente de las parejas seleccionadas.
- **C — Organizaciones:** `UCB1_MATCHING` asigna a cada pareja la media de todo
  su historial más `sqrt(2 log(t+1)/n[i,k])`; `SW_UCB_MATCHING` usa observaciones
  en los últimos `W` periodos globales y el índice
  `media_W + sqrt(2 log(min(t+1,W))/n_W)`; `RECENT_MEAN_MATCHING` usa la misma
  ventana sin bonus explícito de exploración (si una ventana no contiene observaciones,
  usa el prior neutral `0.5`); `FIXED_LEARNED` selecciona una única
  permutación maximizando las medias del periodo inicial común y después no se
  actualiza; `DYNAMIC_ORACLE` conoce `c_t` y sirve sólo de referencia. Los tres
  índices de pareja se convierten en matrices de puntuación y se pasan al
  solver bipartito exacto existente; no se sustituye matching por elecciones
  greedy independientes. Si una pareja UCB no tiene observaciones en su
  historia/ventana, recibe un sentinel finito que domina cualquier puntuación
  observada finita; en la media reciente se aplica el prior indicado.

Cada trayectoria reserva los primeros **9 periodos** a una calibración común
forzada de tres matchings cíclicos: cada una de las nueve parejas obtiene tres
observaciones y todos reciben exactamente la misma información inicial. El
mapa fijo se estima sólo con estos datos y queda congelado. Los resultados
comparativos se calculan en los **291 periodos restantes**. Se evaluaron 30
semillas (`9300–9329`) emparejadas en las tres condiciones. La calibración se
registra separada y no se incluye en los retornos/regrets comparativos. No hubo
semillas separadas para ajustar `W`: se usó la recomendación teórica que
depende del número de breakpoints conocido por el diseño, no de sus instantes
futuros. Con `T=300`, cota de recompensa `B=1`, `W=round(2 sqrt(T log(T)/Υ_T))`
da `W=83` para un cambio y `W=41` para cuatro; en estacionario se fijó `W=T=300`
para desactivar el olvido y hacer coincidir el índice SW con UCB1. Se usó
`ξ=2` (`ξ>1/2` en el análisis SW-UCB), igualando la escala del bonus a UCB1.

**Fuentes metodológicas primarias:** Auer, Cesa-Bianchi y Fischer, “Finite-time
Analysis of the Multiarmed Bandit Problem”, *Machine Learning* 47 (2002),
235–256, [DOI 10.1023/A:1013689704352](https://doi.org/10.1023/A:1013689704352),
Fig. 1 y Teorema 1, pp. 237–238 (UCB1 para brazos con recompensas en `[0,1]`).
Garivier y Moulines, “On Upper-Confidence Bound Policies for Non-Stationary
Bandit Problems”, arXiv:0805.3415, Sec. 1.2/Algoritmo 3, pp. 3–4, y Sec. 3,
Teorema 7, ec. (7), y Observación 9, pp. 9–10; versión de congreso publicada
como “On Upper-Confidence Bound Policies for Switching Bandit Problems”, ALT
2011, LNCS 6925, 174–188, [DOI 10.1007/978-3-642-24412-4_16](https://doi.org/10.1007/978-3-642-24412-4_16).
La fórmula de ventana publicada presupone un bandit de una jugada por ronda y
el artículo condiciona su recomendación de `W` al horizonte y una cota de
breakpoints. Aplicar índices por pareja y resolver simultáneamente un matching
es una **adaptación HLS multiple-play/combinatorial**: las garantías de regret
de los papers no se trasladan automáticamente a esta composición.

#### Resultados

Retorno y regret son esperados, calculados por el evaluador como
`Σ c[i,k,t]` de las asignaciones ejecutadas y diferencia respecto al matching
óptimo de medias en cada periodo. Se informan también recompensas Bernoulli
realizadas. La desviación y el IC 95% t se calculan entre semillas; las
diferencias pareadas usan las mismas semillas. El oráculo suma `698.4` en los
291 periodos de evaluación en cada condición.

| Condición (`W`) | Política | Reward esperado medio ± SD | Regret esperado medio ± SD | Coincidencia óptima | Reward Bernoulli realizado medio |
|---|---|---:|---:|---:|---:|
| S3b-0 (`300`) | UCB1 + matching | 644.24 ± 5.82 | 54.16 ± 5.82 | 0.863 | 644.07 |
|  | SW-UCB + matching | 644.24 ± 5.82 | 54.16 ± 5.82 | 0.863 | 644.07 |
|  | Media reciente + matching | 690.56 ± 42.49 | 7.84 ± 42.49 | 0.966 | 689.33 |
|  | Fijo aprendido | 679.00 ± 75.40 | 19.40 ± 75.40 | 0.933 | 677.47 |
|  | Oráculo dinámico | 698.40 ± 0.00 | 0.00 ± 0.00 | 1.000 | 697.20 |
| S3b-1 (`83`) | UCB1 + matching | 623.30 ± 8.20 | 75.10 ± 8.20 | 0.820 | 620.33 |
|  | SW-UCB + matching | 575.16 ± 7.68 | 123.24 ± 7.68 | 0.699 | 571.57 |
|  | Media reciente + matching | 577.75 ± 57.09 | 120.65 ± 57.09 | 0.691 | 575.57 |
|  | Fijo aprendido | 421.00 ± 29.37 | 277.40 ± 29.37 | 0.452 | 419.07 |
|  | Oráculo dinámico | 698.40 ± 0.00 | 0.00 ± 0.00 | 1.000 | 695.30 |
| S3b-2 (`41`) | UCB1 + matching | 591.10 ± 10.26 | 107.30 ± 10.26 | 0.732 | 590.30 |
|  | SW-UCB + matching | 524.24 ± 8.51 | 174.16 ± 8.51 | 0.582 | 524.50 |
|  | Media reciente + matching | 477.82 ± 48.24 | 220.58 ± 48.24 | 0.449 | 478.20 |
|  | Fijo aprendido | 369.40 ± 23.09 | 329.00 ± 23.09 | 0.356 | 367.80 |
|  | Oráculo dinámico | 698.40 ± 0.00 | 0.00 ± 0.00 | 1.000 | 697.50 |

Los IC 95% de reward esperado fueron: en S3b-0 UCB1/SW `[642.07,646.41]`,
media reciente `[674.69,706.43]`, fijo `[650.85,707.15]`; en S3b-1 UCB1
`[620.24,626.36]`, SW `[572.29,578.03]`, reciente `[556.44,599.07]`, fijo
`[410.03,431.97]`; en S3b-2 UCB1 `[587.27,594.93]`, SW `[521.06,527.42]`,
reciente `[459.81,495.83]`, fijo `[360.78,378.02]`. Para S3b-0, las bandas de
regret de media reciente `[-8.03,23.71]` y fijo `[-8.75,47.55]` incluyen cero;
no se interpreta su diferencia observada con el oráculo como una separación
estadística confirmada. El regret verdadero por semilla y política no puede
ser negativo; esos límites inferiores negativos reflejan incertidumbre de la
media, no regret negativo observado.

Diferencias **pareadas** de reward esperado (primera menos segunda; IC 95%):
UCB1−SW fue `0.00 [0.00,0.00]` en S3b-0, `+48.14 [45.36,50.92]` en S3b-1 y
`+66.86 [63.54,70.18]` en S3b-2. UCB1−media reciente fue `−46.32
[-62.55,-30.09]`, `+45.55 [25.29,65.80]` y `+113.28 [94.75,131.81]`,
respectivamente. Esto muestra un resultado condicionado: la media reciente fue
mejor en estacionario, mientras que el índice acumulativo UCB1 fue mejor en
estos dos escenarios de cambio; **SW-UCB no superó a UCB1** pese al olvido.
El tiempo medio hasta volver a elegir exactamente el matching óptimo después
del cambio fue, en S3b-1, 6.13 periodos UCB1 y 3.87 SW (media reciente 45.71
entre 28/30 episodios; dos quedaron censurados). En S3b-2 fue 4.64 UCB1, 4.91
SW y 22.69 media reciente entre 98/120 cambios; hubo 22 episodios censurados.
Que el fijo coincida con el óptimo durante un régimen que vuelve a una
permutación previa no cuenta como adaptación.

El uso de recursos fue 873 asignaciones de máximo 873 en UCB1, SW y oráculo
para cada condición; la media reciente usó 863.30 en S3b-0, 834.47 en S3b-1 y
800.50 en S3b-2; el fijo, 863.30. Los métodos pueden dejar capacidad sin usar
cuando el matching de puntuaciones observadas tiene recompensa estimada cero.
Los resultados por régimen y periodo, IDs de asignación por semilla, conteos
finales de observaciones por pareja, tasas de divergencia índice-vs-media,
regret pareado y recuperación están en el JSON compacto. La divergencia
índice-vs-media es sólo un indicador operacional de decisiones inducidas por
el bonus, no una descomposición causal del valor de exploración.

#### Validación, interpretación y límites

Se validó que sólo se actualizan parejas seleccionadas; las recompensas deben
estar en `[0,1]`; SW descarta observaciones que salen de la ventana de **periodo
global** y prioriza parejas sin muestra válida; UCB1 conserva el historial;
el matching respeta unicidad de agentes/tareas; los tres escenarios alteran la
permutación óptima como se especificó; el oráculo maximiza la recompensa
esperada por periodo; las semillas reproducen decisiones y resultados, y el
regret esperado evaluado no es negativo (tolerancia numérica `1e-12`). En
estacionario, con `W=T`, ambos índices producen exactamente la misma política.

El hallazgo es negativo respecto a una expectativa simplista de que olvidar
mejora necesariamente la adaptación: con estos perfiles cíclicos, feedback
Bernoulli y matching multi-play, el olvido/bonus SW rindió por debajo de UCB1
en ambos escenarios cambiantes. El SW recuperó antes después del cambio único,
pero pagó una pérdida previa atribuible a su ventana más corta; con cuatro
cambios su recuperación media fue similar a UCB1 y su reward menor. La media
reciente fue competitiva en estacionario y más lenta/inestable en cambio
recurrente. No son conclusiones universales: perfiles sintéticos, tres agentes
y tareas, horizonte 300, 30 semillas y una única amplitud/familia de cambios.
Las condiciones conocen la cota/número de cambios para elegir `W`, pero las
políticas no conocen sus tiempos ni matrices. Los intervalos son exploratorios
y no corrigen comparaciones múltiples.

**Estado A/B/C:** A está implementado como entorno reproducible sintético; B
contiene recompensas Bernoulli de medias exógenas y no aprendizaje de
competencia; C contiene cuatro políticas realizables informacionalmente
limitadas y un oráculo evaluador. **S3b: CERRADO** para la comparación descrita;
no se extiende el resultado fuera de este protocolo.

Artefactos: [estimadores](../../src/hls/nonstationary_assignment.py),
[runner](../../experiments/run_hls_s3b_nonstationary_unknown_assignment.py),
[tests](../../tests/test_hls_s3b_nonstationary_assignment.py) y [resultados
por semilla](../../results/experiments/hls_s3b_nonstationary_unknown_assignment/results.json).
Reproducción:

```bash
PYTHONPATH=.:src pytest -q tests/test_hls_s3b_nonstationary_assignment.py \
  tests/test_hls_lab_nk_assignment.py
PYTHONPATH=.:src python experiments/run_hls_s3b_nonstationary_unknown_assignment.py
```

No se alteraron los registros de S1, S2a, S2b ni D0/D1/D2; no se inició S4.

### 2026-10-20 — S4: dinámica endógena por aprendizaje de competencias

**Estado: CERRADO — referencia exacta determinista de alcance acotado.** Se
reutilizó la transición MIS-v2 existente sin modificarla: para cada agente y
tarea, después de registrar la recompensa,
`c' = 1 - (1-c) exp(-lambda(eta[i,k]) * x[i,k])`, con
`lambda(eta)=-ln(1-eta)`. La acción ejecutada induce exposición `x[i,k]∈{0,1}`;
la celda sólo cambia si esa pareja ejecutó la tarea. Este MIS-v2 no mantiene
una variable de experiencia adicional: la matriz de competencia es estado
Markov suficiente para su transición. La exposición acumulada se conserva en
las trazas como diagnóstico, no se usa para alterar la ley. `eta` sigue
estrictamente en `(0,1)`. La transición no incorpora enseñanza, transferencia
ni efectos entre celdas.

**Modelo A/B/C.** A: dos agentes, dos tareas, demanda determinista y conocida;
cada agente ejecuta como máximo una unidad por periodo y cada tarea disponible
se asigna como máximo a un agente. No hay presupuesto entre periodos ni otra
restricción de recursos. B: competencia evoluciona sólo por el MIS-v2 aplicado
al trabajo ejecutado; no hay incertidumbre ni coste separado de desarrollo.
C: `REACTIVE_EXACT` maximiza la recompensa inmediata con el solver
`HungarianAssignmentOptimizerNK` existente y su desempate estable; `BELLMAN_EXACT`
optimiza la suma finita usando la misma información observable, demanda
determinista, acción factible y transición; `EXHAUSTIVE_OPTIMUM` enumera
independientemente secuencias factibles. La recompensa por periodo es
`R_t=Σ_(i,k) c[i,k,t] x[i,k,t]`, evaluada antes de la transición. Por tanto,
el esfuerzo productivo es la exposición de aprendizaje y no se vuelve a
restar como coste.

Las dos instancias usan parámetros previamente registrados en HLS:
`C(0)=((0.525,0.175),(0.525,0.175))` y
`eta=((0.15,0.15),(0.25,0.25))`. Caso A (“sin retorno futuro”): un periodo,
demanda simultánea de ambas tareas. Caso B: cuatro periodos, demanda
`ambas, tarea 0, tarea 0, tarea 0`. Sólo cambian horizonte y secuencia de
demanda; no se buscaron parámetros. No hay aleatoriedad. El espacio de acciones
de cada periodo contiene todos los matchings parciales factibles; para B,
enumeración exhaustiva examina `7×3×3×3=189` secuencias.

| Caso | REACTIVE exacta | Bellman exacta | Enumeración independiente | Diferencia Bellman−reactiva |
|---|---:|---:|---:|---:|
| A | 0.700000000000 | 0.700000000000 | 0.700000000000 | 0 |
| B | 2.661353125000 | 2.876171875000 | 2.876171875000 | +0.214818750000 |

En B, el solver reactivo elige en el primer periodo `(agente 0,tarea 0)` y
`(agente 1,tarea 1)`, recompensa `0.700000`. Bellman elige
`(agente 0,tarea 1)` y `(agente 1,tarea 0)`, también `0.700000`. La competencia
de agente 1 en tarea 0 pasa de `0.525` a `0.64375`; después, al ejecutarla en
los tres periodos restantes, sus recompensas son `0.64375`, `0.7328125` y
`0.799609375`. La ruta reactiva conserva esa tarea en agente 0 y obtiene
`0.59625`, `0.6568125` y `0.708290625`. Las competencias no asignadas
permanecen constantes. La diferencia acumulada surge íntegramente después del
primer periodo.

**Interpretación y límite crítico.** Bellman coincide exactamente con la
enumeración, y no queda por debajo de la política reactiva evaluada. Sin
embargo, en el único caso B el primer cambio de asignación es entre dos
maximizadores de recompensa inmediata: la evidencia no muestra que Bellman
sacrifique recompensa presente frente al conjunto de acciones inmediatas
óptimas. Sí existe una acción factible de inversión estricta: ejecutar sólo
`(agente 1,tarea 0)` en el primer periodo da `0.525` en vez de `0.700`, eleva
esa competencia a `0.64375` y la hace útil para la demanda futura. Pero Bellman
no necesita escogerla frente a su alternativa empatada para obtener la ruta
reportada. La mejora depende del desempate estable del solver usado por la
política reactiva; una regla reactiva distinta que escogiera el otro empate
podría igualar el valor. En
consecuencia, el caso B verifica valor de continuación bajo el comparador
reactivo implementado, pero no establece una ventaja estricta frente a toda
política miope ni una inversión de recompensa inmediata. En A, la igualdad es
la esperable porque no hay periodo posterior que valore el aprendizaje.

La programación es determinista y exacta en estas instancias. Las pruebas
focalizadas comprobaron la actualización sólo de celdas ejecutadas, optimalidad
inmediata de REACTIVE, factibilidad uno-a-uno, reproducción exacta,
Bellman=enumeración y los resultados A/B: `PYTHONPATH=src pytest -q
tests/synthetic/test_hls_s4.py tests/test_hls_lab_nk_learning_transition.py`
— **13 passed**. Ejecución y resultados compactos:
[`runner`](../../experiments/run_hls_s4.py),
[`implementación exacta`](../../src/hls/synthetic/hls_s4.py),
[`tests`](../../tests/synthetic/test_hls_s4.py) y
[`resultados`](../../results/experiments/hls_s4/results.json). Reproducción:

```bash
PYTHONPATH=src pytest -q tests/synthetic/test_hls_s4.py \
  tests/test_hls_lab_nk_learning_transition.py
PYTHONPATH=src python experiments/run_hls_s4.py
```

S4 queda **CERRADO** para estos dos controles finitos. El mecanismo MIS-v2
introduce dependencia temporal porque las asignaciones determinan competencias
futuras, a diferencia del presupuesto compartido S2b; no implica que Bellman
supere siempre a REACTIVE. No se establecen realismo empírico, ventaja general,
escalabilidad ni superioridad de una arquitectura HLS. La diferencia de B debe
interpretarse específicamente como selección anticipatoria entre empates
inmediatos bajo el desempate de referencia.

### 2026-10-20 — S4: contraste con BEST-MYOPIC y validación de inversión

**Motivación.** La entrada S4 anterior comparaba Bellman con un único
desempate inmediato. Esta revisión conserva sus resultados y añade la referencia
deliberadamente más fuerte `BEST-MYOPIC`: en todo estado selecciona sólo una
acción de `A_miope(s,t)=argmax_a R(s,a)`, pero resuelve entre esos empates con
DP y conocimiento de demanda y MIS-v2. Se usó tolerancia absoluta
`1e-12`. La DP restringida se verificó también enumerando independientemente
secuencias completas y descartando las que contienen una acción no maximizadora
inmediata.

**MIS-v2: propiedad relevante.** Para una celda `(i,k)` con exposición binaria
`x`, la implementación original es
`c' = 1-(1-c)exp(-lambda(eta[i,k])x)`. Como
`lambda=-ln(1-eta)`, para una unidad ejecutada `c'=c+eta(1-c)`; sin ejecución,
`c'=c`. Tras `n` exposiciones a esa celda,
`c_n=1-(1-c_0)(1-eta)^n`. La evolución es monótona, con incrementos
decrecientes y límite 1; las celdas agente×tarea evolucionan independientemente.
La demanda no cambia directamente la competencia: determina qué celdas pueden
recibir exposición. En este MIS-v2 la competencia actual es el estado Markov
suficiente; exposición acumulada se registra, pero no es estado adicional.
La asignación acopla las celdas por las restricciones bipartitas.

**Condición suficiente, restringida.** Considérese una sola tarea demandada en
cada periodo, dos agentes y horizonte `T`. Si sus competencias iniciales son
`a>b`, la tasa del agente A es `eta_A`, la del B es mayor (`eta_B>eta_A`), y la
demanda se mantiene, todo BEST-MYOPIC debe asignar A cada periodo: cuando A es
asignado aumenta su competencia y B permanece en `b`, por lo que A sigue siendo
el maximizador inmediato único. Una política factible que asigna B en cada
periodo obtiene la secuencia `b_j=1-(1-b)(1-eta_B)^j`; BEST-MYOPIC obtiene
`a_j=1-(1-a)(1-eta_A)^j`, para `j=0,…,T-1`. Por tanto, la condición verificable
`Σ_j b_j > Σ_j a_j` es suficiente para que Bellman supere estrictamente a
BEST-MYOPIC. Si además `b+eta_B(1-b)>a`, B ya supera a A tras su primera
exposición, haciendo explícita la reversión de competencia y permitiendo que la
continuación use después al maximizador inmediato B. No es una condición
necesaria general: con varias tareas la factibilidad matching acopla celdas y
requiere evaluar el estado completo.

**Caso B anterior reevaluado.** Con los parámetros originales, la ruta fija de
REACTIVE vale `2.661353125`; el DP restringido a acciones inmediatamente
óptimas da `BEST-MYOPIC=2.876171875`, igual a Bellman y a la enumeración global.
En el primer periodo hay dos matchings maximizadores (`0.700000`): el solver
fijo elige A/tarea 0 + B/tarea 1, mientras que BEST-MYOPIC puede elegir
A/tarea 1 + B/tarea 0 y desarrollar la celda que sirve a la demanda futura.
Bellman no usa ninguna acción estrictamente subóptima en la ruta óptima
(`(2,1,1,1)` maximizadores inmediatos por periodo; cero periodos
estrictamente subóptimos). La diferencia previa de `0.21481875` frente al
desempate fijo desaparece frente a BEST-MYOPIC. Así se confirma que el primer
resultado era sensible al desempate, no evidencia de inversión estricta.

**Familia constructiva controlada.** Para probar inversión estricta sin
ampliar parámetros, se mantuvo `eta_A=0.15`, `eta_B=0.25` (tasas ya usadas),
`a=0.525` (valor inicial ya usado), tarea 0 repetida, y se cambió sólo
`b=0.500` para representar un agente inicialmente algo menos competente.
La tarea 1 queda sin demanda. Horizontes `T=1,2,3,4` forman la familia; no hubo
búsqueda masiva. En cada horizonte el agente A es el maximizador inmediato
único para BEST-MYOPIC, por lo que `BEST-MYOPIC=REACTIVE`. Para `T≥2`, la
exposición del agente B invierte el orden: después de una asignación,
`b_1=0.625>a=0.525`. La suma geométrica satisface la condición suficiente:

| Horizonte T | Reactiva / BEST-MYOPIC | Bellman / enumeración global | Bellman−BEST-MYOPIC |
|---:|---:|---:|---:|
| 1 | 0.525000000 | 0.525000000 | 0 |
| 2 | 1.121250000 | 1.125000000 | +0.003750000 |
| 3 | 1.778062500 | 1.843750000 | +0.065687500 |
| 4 | 2.486353125 | 2.632812500 | +0.146459375 |

En `T=4`, Bellman asigna B/tarea 0 desde el primer periodo. La recompensa
inmediata cae de `0.525` a `0.500` (pérdida `0.025`); las recompensas
posteriores son `0.625`, `0.71875` y `0.7890625`, frente a `0.59625`,
`0.6568125` y `0.708290625` de A. La ganancia posterior acumulada es
`0.171459375`, que compensa la pérdida inicial y deja `+0.146459375`. La
competencia de B evoluciona `.500 → .625 → .71875 → .7890625 → .841796875`;
la de A evoluciona `.525 → .59625 → .6568125 → .708290625 → .75204703125` en
la ruta BEST-MYOPIC.

**Control contrafactual congelado.** En `T=4`, con las mismas competencias
iniciales, demanda y acciones factibles, se aplicó MIS-v2 por la interfaz
canónica `enabled=False` (no se usó `eta=0`, que no pertenece al dominio de
MIS-v2). Los cuatro valores —reactiva, BEST-MYOPIC, Bellman y enumeración— son
`2.100000000`; todos los periodos asignan A a tarea 0. Por tanto, en esta
instancia la ventaja estricta depende de la evolución endógena, no de una
diferencia de información, demanda ni recompensa.

**Verificación y nivel de evidencia.** Global Bellman coincide con enumeración
independiente; BEST-MYOPIC coincide con la enumeración restringida; en cada
caso `Bellman ≥ BEST-MYOPIC ≥ REACTIVE`. Se probaron los empates del caso B
anterior, acción subóptima, reversión MIS-v2, control congelado, factibilidad y
determinismo: **17 tests focalizados pasaron**. El resultado alcanza el **nivel
3 en una familia estrecha controlada por horizonte**: identifica un régimen
`T≥2` para el perfil especificado, no una frecuencia o robustez general. La
familia es una prueba constructiva diseñada a partir de la condición analítica;
no estima prevalencia ni generaliza a otros perfiles/demandas. El antiguo caso
B y su JSON se preservan.

Implementación y reproducción: [solver S4](../../src/hls/synthetic/hls_s4.py),
[runner de validación](../../experiments/run_hls_s4_validation.py),
[tests](../../tests/synthetic/test_hls_s4.py) y
[resultados de validación](../../results/experiments/hls_s4_validation/results.json).

```bash
PYTHONPATH=src pytest -q tests/synthetic/test_hls_s4.py \
  tests/test_hls_lab_nk_learning_transition.py
PYTHONPATH=src python experiments/run_hls_s4_validation.py
```

**Conclusión revisada.** MIS-v2 sí permite una ventaja genuina de planificación
del aprendizaje: la familia de un solo tipo de tarea da
`Bellman > BEST-MYOPIC`, con decisión estrictamente subóptima en recompensa
inmediata y ablation que elimina el gap. El caso anterior de dos tareas no
proporcionaba esa evidencia: su ventaja sólo era frente a un desempate fijo.
S4 alcanza el criterio de existencia y un régimen controlado acotado, pero no
demuestra superioridad general, validez empírica externa ni escalabilidad. No
se inició S3b ni otra línea experimental.

### 2026-10-20 — Revisión científica y metodológica de S3b

**Decisión principal: B — IMPLEMENTACIÓN CORRECTA, EVALUACIÓN INSUFICIENTE
PARA ATRIBUCIÓN CAUSAL Y VALIDACIÓN DE MÉTODO COMBINATORIO.** Esta revisión
inspeccionó el estimador, runner, pruebas y JSON ya existentes; no ejecutó una
nueva campaña ni cambió algoritmos, parámetros o resultados.

#### Problema e información

En S3b hay tres agentes y tres tareas disponibles simultáneamente en cada uno
de 300 periodos. La recompensa esperada de la pareja `(i,k)` es la competencia
exógena `c[i,k,t]∈{0.2,0.8}` y la recompensa observada es Bernoulli con esa
media. La matriz cambia de forma piecewise-constant, independientemente de las
decisiones; la demanda no cambia. El evaluador conoce las matrices y puede
calcular el matching óptimo por periodo, pero las políticas no reciben las
competencias reales, las recompensas contrafactuales, el momento de los cambios
ni las matrices futuras. Tras cada matching sólo se incorporan al estimador
las recompensas de las parejas seleccionadas: es feedback semi-bandit. Cada
acción factible es un matching uno-a-uno y la recompensa es aditiva. Se
observan tres de nueve parejas por periodo; el solver bipartito optimiza
exactamente la suma de puntuaciones que recibe, no la suma de recompensas
verdaderas.

Las cuatro operaciones científicamente distintas son: estimar medias por
pareja; asignar optimismo/exploración a las estimaciones; olvidar o retener
historial; resolver la restricción de matching. El matching exacto resuelve el
subproblema combinatorio dado un score, pero por sí mismo no estima, explora ni
detecta cambios.

#### Correspondencia de los métodos y hallazgos técnicos

- **UCB1 por pareja:** implementa `media_histórica + sqrt(2 log(t+1)/n)` y usa
  un índice optimista finito para parejas no observadas. La forma del índice
  corresponde al UCB1 de recompensas en `[0,1]`; tres observaciones iniciales
  por pareja proceden de la calibración común de 9 periodos, no de la
  inicialización original de un solo brazo por ronda.
- **SW-UCB por pareja:** conserva las observaciones en los últimos `W` periodos
  globales y usa `media_W + sqrt(xi log(min(t+1,W))/n_W)` con `xi=2`. El paper
  de Garivier–Moulines da el término `B sqrt(xi log(t∧tau)/N)` y requiere
  `xi≥1/2` para el análisis; con `B=1`, la fórmula implementada y la constante
  cumplen esa especificación. Una pareja sin muestra vigente recibe el índice
  optimista sentinela. No se encontró un error de fórmula en esta
  implementación. La definición de periodo global resulta adecuada para
  cambios del entorno ocurridos aunque una pareja no se haya seleccionado.
- **Media reciente:** usa media empírica sin bonus y la misma ventana que
  SW-UCB; una ventana vacía recibe prior `0.5`. Es un comparador de explotación,
  no un algoritmo de exploración publicado. Si el score de una pareja es cero,
  el matching puede dejar capacidad sin asignar porque las restricciones son
  `≤`; esto explica parte de su menor uso de recursos y debe mantenerse visible
  al interpretar resultados.
- **Matching conjunto:** `HungarianAssignmentOptimizerNK` recibe la matriz de
  índices/medias. Es una optimización global exacta de scores aditivos con
  restricciones uno-a-uno. Los empates son deterministas por el solver. La
  combinación índice-por-arista + matching es la adaptación HLS combinatoria;
  UCB1 y SW-UCB publicados analizan una sola jugada por ronda. No se heredan
  automáticamente sus garantías de regret al seleccionar varias aristas
  simultáneas.

**Clasificación.** No se identificó **ERROR DE IMPLEMENTACIÓN** en las
fórmulas declaradas, feedback seleccionado, caducidad por ventana, acoplamiento
de recompensas, ni factibilidad del matching. Es una **DECISIÓN DE DISEÑO
DISCUTIBLE** fijar `W` usando el número de cambios conocido por la condición:
no es acceso de la política a los tiempos ni valores futuros, y coincide con
la condición de sintonización considerada en la fuente, pero concede
información del número de breakpoints que un usuario real quizá no tendría.
La diferencia entre matching de índices y un algoritmo combinatorio con
análisis propio es una **LIMITACIÓN DEL MÉTODO/ADAPTACIÓN**, no un bug. La
exploración por UCB y la posible inestabilidad/olvido de SW son **COMPORTAMIENTO
ESPERABLE** de estas reglas, no evidencia de que una regla sea universalmente
mejor.

La calibración usa los mismos nueve matchings cíclicos, tres observaciones por
pareja y las mismas recompensas potenciales emparejadas para todas las
políticas; `W` no se ajustó con las semillas de evaluación. Se verifica que
ninguna política ejecutable recibe competencias reales o recompensas no
seleccionadas. El oráculo es sólo evaluador. Los retornos/regrets del JSON son
esperados a partir de `c`, distintos de los retornos Bernoulli realizados.
Estas condiciones hacen válida la comparación dentro del protocolo sintético.

#### Qué permiten decir las trazas existentes

En estacionario `W=300`; durante el horizonte no expira ninguna observación y,
con `xi=2`, SW-UCB y UCB1 producen decisiones idénticas: ambos obtienen
`644.24`, regret esperado `54.16` y coincidencia óptima `0.863`. Media reciente
también conserva todo el historial en esta condición, pero quita el bonus:
obtiene `690.56`, regret `7.84` y coincidencia `0.966`. UCB1/SW divergen de la
asignación derivada de medias puras en `13.7%` de periodos; media reciente, por
definición, no diverge. Esto es compatible con un coste de exploración
innecesaria cuando el entorno es estacionario y la calibración ya es
informativa, pero no constituye por sí solo una atribución causal: las
políticas también generan historiales de feedback distintos tras separarse.

En el cambio abrupto, UCB1 obtiene `623.30` frente a `575.16` de SW-UCB; en el
cambio recurrente, `591.10` frente a `524.24`. Diferencias pareadas UCB1−SW:
`+48.14 [45.36,50.92]` y `+66.86 [63.54,70.18]` (IC 95% t entre 30 semillas).
UCB1 supera a SW en cada segmento registrado, incluso antes del primer cambio
del caso abrupto (`301.46` frente a `282.46` de reward esperado en el segmento
0). SW, sin embargo, recupera antes tras el cambio abrupto (3.87 frente a 6.13
periodos), mientras que en el recurrente sus medias de recuperación son
similares (4.91 frente a 4.64). Sus frecuencias de cambio de matching son
mayores: 124.43 frente a 79.67 en abrupto y 147.80 frente a 106.63 en
recurrente. Por tanto, los datos no respaldan que UCB1 gane simplemente por
“adaptarse más deprisa”; sí muestran el intercambio entre olvidar datos
antiguos/recuperarse y el coste de estimaciones locales más volátiles o menos
precisas bajo feedback escaso.

La media reciente supera a UCB1 en estacionario (`+46.32`, IC pareado para
UCB1−media `[-62.55,-30.09]`) y queda por debajo en cambio abrupto y recurrente
(`−45.55` y `−113.28` para UCB1−media). Esto es compatible con que la ausencia
de bonus evite exploración costosa cuando no hay cambios, pero que la
explotación con ventana tarde en corregir una asignación tras cambios: en
abrupto recupera en promedio 45.71 periodos (28/30 episodios; dos censurados),
y en recurrente 22.69 (98/120 cambios observables; 22 censurados). La
interpretación no es una descomposición causal.

Las tasas registradas de `index_vs_mean_assignment_divergence` —13.7%, 53.9%
y 62.7% para UCB1; 13.7%, 37.9% y 51.2% para SW— son un proxy de decisiones
alteradas por los bonuses, no una medida causal de “asignaciones exploratorias”.
En el JSON hay IDs de asignación y conteos de observaciones finales por pareja,
pero no hay series temporales de índices, `n_W`, medias por pareja, ni etiquetas
de exploración. El promedio de observaciones finales por pareja es 100 para
UCB1/SW en cada condición (tres por pareja en calibración y 873 elecciones
posteriores repartidas entre nueve aristas); los mínimos/máximos agregados
entre semilla y pareja son 11–272 en estacionario, 11–272/29–145 en abrupto
(UCB1/SW), y 57–133/69–122 en recurrente. En media reciente son 99/96/92 de
media, con mínimos–máximos 3–294, 3–289 y 6–223. Los conteos acumulados no
indican cuántas observaciones siguen vigentes dentro de la ventana; no se puede
medir persistencia local o redundancia exploratoria exactamente.

La fuente de SW-UCB recomienda `tau` dependiente de horizonte y número de
breakpoints; el protocolo usa `W=83` para un cambio y `W=41` para cuatro,
frente a segmentos de 150 y 60 periodos respectivamente. Esa escala es
compatible con las duraciones, pero no determina por sí sola la adecuación:
con sólo tres aristas observadas por ronda, el soporte local por pareja depende
de las asignaciones que produce el matching. En S3b-0 no hay cambio de la
solución óptima; S3b-1 cambia una vez de `57` a `39`; S3b-2 cambia cuatro veces
(`57→39→30→57→39`). La separación de medias es grande: una permutación
completa óptima da `2.4`, y cualquier permutación completa no óptima da como
máximo `1.2`; las asignaciones parciales también son factibles y, por ejemplo,
dos aristas correctas dan `1.6`. El problema ofrece señal de asignación clara;
el problema es el aprendizaje y seguimiento bajo observación parcial, no una
ambigüedad del oráculo.

**Qué no queda identificado.** Los resultados muestran el rendimiento relativo
de tres reglas completas en esta familia; no permiten atribuir el gap entre
UCB1 y SW únicamente a exploración o a olvido. En ese contraste cambian a la
vez el historial y la confianza, y la conducta de cada política modifica qué
feedback obtiene después. Tampoco se puede cuantificar cuánto del resultado
proviene del solver de matching porque no hay ablación con una política de
combinación distinta. La comparación pareada controla los shocks potenciales,
pero no elimina esas diferencias endógenas de historia. Los 30 seeds y los IC
son evidencia exploratoria de este protocolo; no cubren familias de matrices,
amplitudes o tasas de cambio, y no hay corrección por comparaciones múltiples.

#### Adecuación metodológica y decisión

Para el problema de S3b se requiere un algoritmo que trate explícitamente
conjuntos factibles combinatorios, feedback semi-bandit por arista, recompensa
aditiva y medias no estacionarias. El adaptador actual sí respeta las
restricciones y es un comparador experimental interpretable, pero no es una
reproducción teórica completa de UCB1/SW-UCB para asignación combinatoria. Una
referencia más alineada para cambios piecewise-constant es **GLR-CUCB** de
Zhou et al. (AAAI 2020): combina un oráculo combinatorio CUCB con detección GLR
de cambios, bajo feedback combinatorial semi-bandit; los autores presentan
cotas de regret para ese problema. El caso HLS tiene recompensa aditiva
Bernoulli y un oráculo matching exacto, por lo que la correspondencia es
plausible, sujeta a revisar al integrar las hipótesis y definición exactas del
paper. No se recomienda implementar ahora ni asumir que hereda sus cotas sin
esa comprobación. También existe la formulación no estacionaria combinatorial
semi-bandit de Chen et al. (UAI 2021), que incluye caso lineal con oráculo
exacto y una variante sin conocer de antemano el número de cambios; es otra
referencia posible, no un resultado del S3b actual.

**Experimento mínimo que justificaría avanzar (propuesto, no ejecutado).**
En las mismas trayectorias, semillas, calibración y oráculo de S3b, completar
la ablación 2×2 que falta: (historial global o ventana) × (sin bonus o con
bonus). Ya existen global+bonus (UCB1), ventana+bonus (SW-UCB) y ventana sin
bonus (media reciente); falta global sin bonus (media histórica greedy).
Añadir, como comparador del problema y no como sustituto retrospectivo de los
resultados existentes, una implementación fiel de GLR-CUCB si se cumplen sus
hipótesis. Registrar por periodo las nueve medias/índices, `n`/`n_W`, aristas
observadas, matching elegido, regret esperado y detecciones/reset. Usar
calibración común y un conjunto de semillas de evaluación fijado antes de
medir; informar contrasts pareados y separar la selección de parámetros de la
evaluación. Esta prueba respondería al punto no identificado (retención,
exploración y detección) y ofrecería una referencia diseñada para combinatorial
semi-bandits; no es una petición para iniciar trabajo en esta revisión.

**Referencias metodológicas:** Auer, Cesa-Bianchi y Fischer (2002), “Finite-time
Analysis of the Multiarmed Bandit Problem”, *Machine Learning* 47, 235–256,
[DOI 10.1023/A:1013689704352](https://doi.org/10.1023/A:1013689704352);
Garivier y Moulines (2011), “On Upper-Confidence Bound Policies for Switching
Bandit Problems”, ALT 2011, 174–188, [DOI
10.1007/978-3-642-24412-4_16](https://doi.org/10.1007/978-3-642-24412-4_16);
Zhou et al. (2020), “A Near-Optimal Change-Detection Based Algorithm for
Piecewise-Stationary Combinatorial Semi-Bandits”, AAAI 2020,
[arXiv:1908.10402](https://arxiv.org/abs/1908.10402); Chen et al. (2021),
“Combinatorial Semi-Bandit in the Non-Stationary Environment”, UAI 2021,
[arXiv:2002.03580](https://arxiv.org/abs/2002.03580).

Artefactos inspeccionados: [estimadores](../../src/hls/nonstationary_assignment.py),
[runner](../../experiments/run_hls_s3b_nonstationary_unknown_assignment.py),
[pruebas](../../tests/test_hls_s3b_nonstationary_assignment.py) y
[resultados](../../results/experiments/hls_s3b_nonstationary_unknown_assignment/results.json).
La implementación original y sus resultados quedan intactos; la extensión
propuesta no se ha ejecutado.

### 2026-10-20 — S3b: ablación factorial historial × exploración

**Estado: CERRADA — ablación 2×2 ejecutada sobre el protocolo original.** Se
añadió únicamente `GLOBAL_MEAN_MATCHING`: media empírica de todo el historial,
sin bonus y con feedback sólo de parejas seleccionadas. Las otras celdas son
UCB1 (historial completo + bonus), media reciente (ventana + sin bonus) y
SW-UCB (ventana + bonus). Las cuatro entregan sus puntuaciones al mismo solver
bipartito. Se conservaron las 9 rondas de calibración, 291 rondas evaluadas,
30 semillas `9300–9329`, trayectorias, recompensas Bernoulli potenciales,
ventanas `300/83/41`, matrices, demanda y restricciones. El JSON de S3b
original no se sobrescribió.

#### Reproducción y resultados

La calibración coincide exactamente. UCB1, SW-UCB y media reciente reproducen
sus secuencias de asignación y recompensa esperada para los 90 pares
condición-semilla: diferencia máxima de reward `0.0` y secuencias idénticas.
La tabla muestra medias de reward esperado acumulado; entre paréntesis figura
IC 95% t no pareado entre semillas. Los contrastes factoriales siguientes sí
son pareados por semilla.

| Escenario | Historial completo, sin bonus (GF) | Historial completo, bonus (GU/UCB1) | Ventana, sin bonus (WF/reciente) | Ventana, bonus (WU/SW-UCB) |
|---|---:|---:|---:|---:|
| S3b-0 estacionario (`W=300`) | 690.56 (674.69–706.43) | 644.24 (642.07–646.41) | 690.56 (674.69–706.43) | 644.24 (642.07–646.41) |
| S3b-1 abrupto (`W=83`) | 424.26 (414.46–434.06) | 623.30 (620.24–626.36) | 577.75 (556.44–599.07) | 575.16 (572.29–578.03) |
| S3b-2 recurrente (`W=41`) | 375.02 (365.24–384.80) | 591.10 (587.27–594.93) | 477.82 (459.81–495.83) | 524.24 (521.06–527.42) |

Los regret esperados acumulados medios —respecto al oráculo dinámico— son,
respectivamente por celda GF/GU/WF/WU: S3b-0 `7.84/54.16/7.84/54.16`; S3b-1
`274.14/75.10/120.65/123.24`; S3b-2 `323.38/107.30/220.58/174.16`. Los IC 95%
por política, recompensa realizada Bernoulli, recursos, tasa de matching óptimo,
frecuencias de asignación y resultados por semilla están en el JSON específico.

Contrastes pareados (`media [IC 95%]`, unidades de recompensa acumulada):

| Contraste | S3b-0 | S3b-1 | S3b-2 |
|---|---:|---:|---:|
| Bonus, historial completo `GU−GF` | −46.32 [−62.55, −30.09] | +199.04 [+188.55, +209.53] | +216.08 [+206.62, +225.54] |
| Bonus, ventana `WU−WF` | −46.32 [−62.55, −30.09] | −2.59 [−23.58, +18.39] | +46.42 [+28.20, +64.64] |
| Ventana sin bonus `WF−GF` | 0.00 [0.00, 0.00] | +153.49 [+131.53, +175.45] | +102.80 [+81.76, +123.84] |
| Ventana con bonus `WU−GU` | 0.00 [0.00, 0.00] | −48.14 [−50.92, −45.36] | −66.86 [−70.18, −63.54] |
| Interacción factorial `(WU−WF)−(GU−GF)` | 0.00 [0.00, 0.00] | −201.63 [−224.22, −179.05] | −169.66 [−190.58, −148.74] |

#### Diagnóstico

**Observación.** En estacionario `W=300` no expira observaciones durante la
evaluación; media global y reciente son la misma regla y producen secuencias
idénticas. También UCB1 y SW-UCB coinciden. El contraste aislado del bonus es
−46.32: aquí el bonus modifica asignaciones en 13.72% de periodos y coincide
con menor reward. En los dos escenarios cambiantes, mantener historial completo
sin bonus es la peor celda (424.26 y 375.02); usar ventana sin bonus aumenta el
reward en 153.49 y 102.80. Bajo historial completo, el bonus añade 199.04 y
216.08; bajo ventana añade −2.59 (IC incluye cero) y +46.42. La interacción
factorial es negativa en ambos escenarios dinámicos.

**Interpretación compatible, no efecto causal puro.** La ventana ayuda a la
media codiciosa cuando recompensas antiguas quedan obsoletas. El bonus ayuda
mucho al estimador global, que de otro modo persiste en la asignación inicial;
con ventana, su valor depende del patrón de cambios: no mejora el retorno
abrupto y sí el recurrente. La interacción negativa muestra que no se deben
sumar separadamente “beneficio de ventana” y “beneficio de exploración”. Cada
política genera sus propios feedbacks y la acción determina qué datos verá
después.

La influencia operacional del bonus se midió como la proporción de periodos
en que matching sobre índices difiere de matching sobre las medias del mismo
estado estimador. Fue UCB1 `13.7%, 53.9%, 62.7%` y SW-UCB `13.7%, 37.9%, 51.2%`
en S3b-0/1/2; media global y reciente dan `0%` por definición. Es una medida de
influencia del bonus, no etiqueta de exploración óptima ni regret causal. La
ventana de diagnóstico registra por régimen y pareja `n`, media, bonus, índice,
edad, muestra vigente/descartada y frecuencia seleccionada; alrededor de cada
cambio registra las mismas cantidades entre −5 y +10 periodos. Las medias
recientes seleccionaron menos de 3 tareas por periodo en promedio en algunas
condiciones (recursos: `863.30`, `834.47`, `800.50` frente a `873` en UCB1/SW),
porque el modelo permite dejar asignaciones sin cubrir cuando el score
estimado es cero; se conserva esta regla del conjunto factible.

Después del cambio abrupto, regret medio en los cinco periodos previos y los
cinco posteriores fue: UCB1 `0.152→1.340`, SW-UCB `0.288→1.120`, reciente/global
`0.027→1.807`. SW tuvo menor regret inmediato que UCB1 en esa ventana, coherente
con su recuperación más rápida tras ese único cambio (`3.87` frente a `6.13`
periodos hasta matching óptimo), pero no compensó su menor reward agregado.
En cambios recurrentes la recuperación media fue `4.64` UCB1 y `4.91` SW; no
hay ventaja de recuperación consistente para SW. Media global puede reaparecer
rápidamente cuando vuelve un régimen antiguo, pero suele quedar bloqueada en
los otros regímenes. La condición estacionaria no contiene cambios, por lo
que no tiene métrica de recuperación.

#### Conclusión y decisión S3b

La ablación explica operacionalmente dos patrones: sin cambios, el bonus
observado es costoso en esta instancia tras calibración; con cambios, ignorar
la historia antigua da una mejora sustancial para el estimador sin bonus, y el
bonus aporta valor adicional en ciertas combinaciones, sobre todo UCB global en
estos entornos. También confirma que UCB1 supera a SW-UCB en retorno total en
S3b-1/2 pese a que SW puede recuperar antes en el evento abrupto. **No demuestra
por qué**: el contraste no fija el historial de feedback, y no separa de forma
causal exploración, olvido y matching. Los IC pareados son exploratorios entre
30 semillas; no corrigen comparaciones múltiples ni generalizan a otras
familias de cambio.

No se detectó defecto de implementación/protocolo. La limitación que persiste
es metodológica: las garantías single-play de UCB1/SW-UCB no se transfieren
automáticamente a la composición multi-play con matching. Se mantiene como
referencia futura, no implementada, un método diseñado para combinatorial
semi-bandits piecewise-stationary como GLR-CUCB; resolvería la falta de un
comparador publicado con detector de cambios y oráculo combinatorio, sujeto a
verificar exactamente sus hipótesis. No se abre esa campaña en esta entrada.

**Validación:** se verificaron para todas las 90 ejecuciones las tres
secuencias existentes contra el JSON original, además de calibración, semillas,
restricciones, actualización sólo de parejas ejecutadas y contrastes pareados.
Las pruebas focalizadas dieron **20 passed**; `git diff --check` pasó.

Artefactos nuevos: [runner factorial](../../experiments/run_hls_s3b_factorial_ablation.py),
[resultado factorial compacto](../../results/experiments/hls_s3b_factorial_ablation/results.json).
Estimador extendido: [nonstationary_assignment.py](../../src/hls/nonstationary_assignment.py).
Pruebas focalizadas: [test_hls_s3b_nonstationary_assignment.py](../../tests/test_hls_s3b_nonstationary_assignment.py).
Reproducción:

```bash
PYTHONPATH=.:src pytest -q tests/test_hls_s3b_nonstationary_assignment.py \
  tests/test_hls_lab_nk_assignment.py
PYTHONPATH=.:src python experiments/run_hls_s3b_factorial_ablation.py
```

### 2026-10-20 — S3b: evaluación final GLR-CUCB

**Estado: CERRADA — resultado B (método ejecutable, sin ventaja clara y
generalizable en las condiciones evaluadas).** Esta es la última evaluación
experimental de S3b; no se abre otra arquitectura ni campaña.

#### Referencia, formulación y compatibilidad

Se consultó el texto completo de Zhou et al., *A Near-Optimal Change-Detection
Based Algorithm for Piecewise-Stationary Combinatorial Semi-Bandits*, AAAI 2020,
[arXiv:1908.10402v4](https://arxiv.org/abs/1908.10402). GLR-CUCB combina índices
CUCB con un detector GLR por brazo base. Para la secuencia de feedback binario
de un brazo, el estadístico es

`max_{1<=s<n} [s kl(mean_1:s || mean_1:n) + (n-s) kl(mean_(s+1):n || mean_1:n)]`,

con KL Bernoulli y el umbral `beta(n,delta) = 2 Q(log(3 n^(3/2)/delta)/2) +
6 log(1+log n)`. Se usa el límite superior publicado
`Q(x) <= x + 4 log(1+x+sqrt(2x))` para `x >= 5`, extendido conservadoramente
para argumentos menores mediante monotonicidad. Los índices post-reinicio son
`mean_i + sqrt(3 log(t-tau)/(2 z_i))`. La exploración uniforme programa brazos
base en ciclos de longitud `floor(L/epsilon)`; si el brazo indicado se fuerza,
se elige aleatoriamente un superbrazo factible que lo contenga. Si cualquier
detector alarma, el algoritmo original hace reinicio **global** de todos los
contadores y fija `tau` al periodo actual. Los parámetros siguen la receta
del experimento sintético del artículo: `delta=20/T=0.0666667` y
`epsilon=0.5 sqrt((L-1) log(T)/T)=0.195001`, con `L=9` brazos base y `T=300`.
La publicación describe feedback semi-bandit de cada brazo incluido en la
acción, distribuciones acotadas en `[0,1]`, cambios piecewise-i.i.d., reward
monótono y Lipschitz y un oráculo combinatorio alpha-aproximado.

S3b es compatible con esa estructura: los nueve pares agente-tarea son brazos
base; la acción de cada periodo es un matching; se observan las recompensas
Bernoulli únicamente de sus aristas; el reward esperado es la suma de medias.
Es monótono y `sqrt(3)`-Lipschitz sobre matchings de cardinalidad hasta tres.
El optimizador bipartito resuelve exactamente la maximización aditiva, por lo
que el oráculo tiene `alpha=1`. Las trayectorias de medias son deterministas y
piecewise constantes, exógenas a la política; las recompensas potenciales
Bernoulli son independientes por par-periodo y se comparten para evaluación
pareada. Así, no se encontró incompatibilidad fundamental.

Adaptaciones declaradas: la política parte de las nueve rondas de calibración
comunes (tres observaciones por arista), llevadas como historial inicial del
estimador, y pone el reloj de GLR en el final de esa calibración; en una
exploración forzada se sortea uniformemente entre los matchings perfectos que
contienen la arista programada. Esto conserva el feedback permitido y las
restricciones de matching, pero no es la inicialización desde contadores cero
del pseudocódigo ni prueba que se transfieran sus garantías de regret. Además,
los segmentos de 60 periodos de S3b-2 no satisfacen las condiciones de duración
de segmento usadas en la cota teórica. El umbral emplea el límite superior de
`Q`, no inversión numérica de dicha función; es conservador y queda como
adaptación de implementación explícita.

#### Validación y resultados emparejados

La comparación reutilizó sin cambios S3b-0/1/2, calibración de 9 periodos,
291 periodos evaluados, semillas `9300–9329`, matrices, demanda, restricciones
y recompensas potenciales comunes. UCB1, SW-UCB y media reciente reprodujeron
las 90 ejecuciones originales: las secuencias de asignación fueron idénticas
y la diferencia máxima de reward esperado fue `0.0`. Pruebas focalizadas:
**27 passed** (GLR, estimadores S3b y solver de matching). `git diff --check`
pasó.

Reward esperado acumulado medio (IC 95% entre semillas); regret esperado medio
respecto al matching oracular por periodo:

| Escenario | UCB1 | SW-UCB | Media reciente | GLR-CUCB |
|---|---:|---:|---:|---:|
| S3b-0 estacionario | 644.24 (642.07–646.41); regret 54.16 | 644.24 (642.07–646.41); 54.16 | 690.56 (674.69–706.43); 7.84 | 617.66 (615.96–619.36); 80.74 |
| S3b-1 abrupto | 623.30 (620.24–626.36); 75.10 | 575.16 (572.29–578.03); 123.24 | 577.75 (556.44–599.07); 120.65 | 583.44 (576.33–590.55); 114.96 |
| S3b-2 recurrente | 591.10 (587.27–594.93); 107.30 | 524.24 (521.06–527.42); 174.16 | 477.82 (459.81–495.83); 220.58 | 524.92 (516.50–533.34); 173.48 |

Diferencia pareada de reward esperado GLR-CUCB menos comparador, media [IC
95%]: S3b-0: frente a UCB1 `−26.58 [−29.33,−23.83]`, SW-UCB igual, media reciente
`−72.90 [−88.62,−57.18]`; S3b-1: frente a UCB1 `−39.86 [−45.98,−33.74]`,
SW-UCB `+8.28 [+1.21,+15.35]`, media reciente `+5.69 [−15.15,+26.52]`; S3b-2:
frente a UCB1 `−66.18 [−74.71,−57.65]`, SW-UCB `+0.68 [−7.98,+9.34]`, media
reciente `+47.10 [+25.42,+68.78]`. Los intervalos son t pareados descriptivos
con 30 semillas, no una confirmación corregida por multiplicidad.

GLR forzó en promedio `63.0` de los 291 periodos evaluados (aprox. 22%); el
regret esperado acumulado en los periodos forzados fue en promedio `75.74`,
`75.44` y `74.54`, respectivamente. No hubo falsas alarmas: tampoco hubo
alarmas observadas en las 30 ejecuciones estacionarias, las 30 abruptas ni las
120 oportunidades de cambio recurrente. El retraso de detección quedó
censurado por el horizonte para todos los cambios. La recuperación, definida
como primer matching óptimo tras el cambio, sí ocurrió en todos los episodios:
media `7.37` periodos en S3b-1 y, en S3b-2, `3.77, 26.43, 12.80, 4.90` para
los cambios en `60,120,180,240`. No se atribuye esa recuperación al detector:
se produjo sin alarmas y puede depender de UCB y la exploración forzada. En el
cambio abrupto, SW-UCB recuperó en `3.87` periodos y UCB1 en `6.13`; recuperación
temprana no implica detección GLR.

#### Interpretación y cierre

GLR-CUCB no supera convincentemente a las referencias como conjunto. Pierde con
claridad en el estacionario y frente a UCB1 en ambos casos cambiantes. En el
abrupto logra una ventaja pareada modesta frente a SW-UCB (`+8.28`, IC que no
incluye cero), pero no frente a UCB1; en recurrente es indistinguible de SW-UCB,
aunque supera la media reciente. Como no se activó ningún detector, esa ventaja
puntual no puede atribuirse a GLR; podría proceder del patrón de exploración y
de las asignaciones inducidas por índices. La detección ausente no sustenta
ventaja por cambio-detección. El coste de exploración y los reinicios no producen una
mejora clara a `T=300`; el protocolo tiene poca información por arista para
detectar cambios recurrentes y la inicialización común difiere del algoritmo
desde cero. Son observaciones de este protocolo sintético, no refutación
general de GLR-CUCB ni validación de sus garantías en la adaptación HLS.

**Conclusión B.** GLR-CUCB fue implementado, probado y ejecutado con matching
exacto y feedback parcial, pero no ofrece una ventaja clara y explicable frente
a las políticas existentes en S3b. Se cierra la evaluación prevista; no se
ajustaron parámetros tras observar resultados ni se propone otra campaña.
El resultado no convierte S3b en benchmark publicado ni valida universalmente
la arquitectura combinatoria.

Artefactos: [implementación GLR-CUCB](../../src/hls/glr_cucb.py), [runner de la
evaluación final](../../experiments/run_hls_s3b_glr_cucb.py), [pruebas
focalizadas](../../tests/test_hls_s3b_glr_cucb.py) y [resultados separados y
compactos](../../results/experiments/hls_s3b_glr_cucb/results.json). Se
conservan intactos los JSON previos de S3b y la ablación factorial.
Reproducción:

```bash
PYTHONPATH=.:src pytest -q tests/test_hls_s3b_glr_cucb.py \
  tests/test_hls_s3b_nonstationary_assignment.py tests/test_hls_lab_nk_assignment.py
PYTHONPATH=.:src python experiments/run_hls_s3b_glr_cucb.py
```

### 2026-10-21 — Consolidación científica S1–S4 y formulación común

**Tipo:** síntesis científica y actualización de estado; no se ejecutaron
experimentos, no se modificaron código ni resultados. Se preservan todas las
entradas anteriores. La formulación técnica común está en
[`HLS_UNIFIED_FRAMEWORK.md`](../architecture/HLS_UNIFIED_FRAMEWORK.md); la
integración semántica se añadió a la
[ontología v0.1](../architecture/HLS_ONTOLOGY_V0_1_2026-10-23.md).

#### 1. Evidencia auditada y alcance de cada escenario

| Escenario | Evidencia comprobada en artefactos | Conclusión actualmente respaldada | Límite / cuestión abierta |
|---|---|---|---|
| **S1 — estático** | Matriz 3×3; solver de asignación SciPy, greedy y enumeración/test independiente. Exacto = enumeración `2.60`; greedy `1.80`. | El solver optimiza la asignación bipartita lineal bajo las restricciones declaradas; la decisión global supera al greedy en esta matriz. | Una matriz no demuestra escalabilidad ni ventaja de una arquitectura HLS. El backend de SciPy es Jonker–Volgenant, no una implementación del procedimiento histórico de Kuhn. |
| **S2a — demanda variable separable** | Demanda `(1,1,1),(2,0,1),(3,1,0),(0,0,0)` sobre la matriz S1; reward exacto por periodo `2.60,2.70,2.70,0`, total `8.00`; greedy `7.20`; enumeración global independiente `8.00` sobre 84,388 secuencias. | Con recompensas conocidas, competencias constantes, recursos renovables y conjuntos factibles independientes, el óptimo por periodo es óptimo del horizonte: `max Σ R_t = Σ max R_t`. | Identidad matemática por separabilidad, no hallazgo de que demanda variable requiera planificación. No cubre colas, presupuesto persistente o cambios de estado. |
| **S2b — presupuesto intertemporal** | Mismo `C` y demanda, presupuesto global no renovable. `B=3`: miope = Bellman = enumeración `1.90`; `B=1`: miope `.90`, Bellman = enumeración `1.00`; `B=0`: todos `0`. | El recurso común acopla periodos; existe una instancia donde el óptimo inmediato consume el recurso antes de una oportunidad posterior. Bellman coincide con enumeración. | Ejemplo constructivo finito; planificación no gana estrictamente con todo presupuesto/demanda. No es una contribución algorítmica nueva. |
| **S3a — competencia exógena observable** | D0/D1/D2, 3×3, 300 periodos, 20 semillas emparejadas; outcomes potenciales Bernoulli. Después se hizo ablación informacional y ruido observacional. Con `E[R]=C` conocida, P0+matching coincide con oráculo en D0/D1/D2: `634.150/614.450/679.150`; LinUCB completo: `611.950/604.250/676.800`; fijo entrenado: `634.150/581.900/584.550`. En las nueve celdas D0/D1/D2 × `σ=0,.10,.20`, P0 superó a LinUCB. | En ese mapeo, observabilidad correcta más reorganización reactiva explica la ventaja sobre fijo; no se observa valor adicional del aprendizaje de parámetros LinUCB frente a P0. | Dinamismo, amplitud y persistencia no siempre se aíslan entre sí. P0/oráculo coinciden porque la media de reward es la competencia observable, no porque P0 conozca reward oculto. Resultado sintético de 20 semillas, no generalizable a otro modelo de observación/reward. |
| **S3b — recompensa desconocida, cambio exógeno, feedback parcial** | Recompensas Bernoulli de media `.2/.8`, 3 agentes × 3 tareas, 300 periodos (9 calibración común + 291 evaluación), 30 semillas. Comparaciones UCB1, SW-UCB, media reciente/fija/oráculo; ablación factorial añade media global; iteración GLR-CUCB con tests y comparación emparejada. | El rendimiento depende conjuntamente del historial, bonus, cambios y matching. La ablación identifica contrastes entre políticas completas y una interacción historia×bonus; GLR-CUCB no produjo detecciones en las ejecuciones evaluadas y no dio ventaja general clara. | **La iteración de evaluación está completada; la línea científica S3b sigue ABIERTA.** La interacción factorial no identifica efectos causales puros porque cada política genera su feedback; la adaptación multiple-play no hereda automáticamente garantías single-play. Se desconoce generalización a otras dinámicas y si existe una comparación combinatoria con garantías aplicables. |
| **S4 — aprendizaje endógeno MIS-v2** | MIS-v2 determinista por celda; 2 agentes/2 tareas en caso inicial. Bellman inicial `2.876171875` frente al reactive de desempate fijo `2.661353125`; la revisión tie-aware obtiene BEST-MYOPIC = Bellman = enumeración `2.876171875`, invalidando ese gap como inversión estricta. Luego se verificó una familia de un agente/tarea activa, horizonte 1–4: gaps Bellman−BEST-MYOPIC `0,.00375,.0656875,.146459375`; en `T=4`, sacrificio inmediato `.025`, ganancia posterior `.171459375`, gap `.146459375`. El control con transición deshabilitada vale `2.10` para las cuatro referencias. | En esa familia acotada existe valor estrictamente anticipatorio del aprendizaje: Bellman elige una acción de reward inmediato estrictamente menor y supera a todas las políticas que sólo eligen maximizadores inmediatos. La recursión y el óptimo miope restringido se verificaron por enumeración independiente. | No estima prevalencia, robustez, validez externa o escalabilidad. La condición analítica es suficiente y restringida, no una caracterización general de sistemas multi-tarea. La ablation apoya causalidad sólo para la instancia declarada; no implica necesidad universal de MIS-v2. |

Las configuraciones, ecuaciones, hipótesis de información, parámetros, rutas y
limitaciones detalladas siguen en las entradas fechadas de S1–S4 y en sus JSON;
esta tabla no sustituye ni reescribe dichos registros. Referencias directas:
[solver bipartito](../../src/hls/hls_lab_nk_assignment.py), [S2a](../../experiments/run_hls_s2a_static_demand.py),
[S2b](../../experiments/run_hls_s2b_intertemporal_budget.py), [S3a base](../../experiments/run_hls_dynamicity_sensitivity.py),
[S3a información](../../experiments/run_hls_dynamicity_information_ablation.py),
[S3a observación ruidosa](../../experiments/run_hls_dynamicity_observation_uncertainty.py),
[S3b estimadores](../../src/hls/nonstationary_assignment.py), [S3b detector](../../src/hls/glr_cucb.py),
[S4 solver](../../src/hls/synthetic/hls_s4.py). La matriz completa de runners,
tests y resultados está en el documento de formulación unificada.

#### 2. Trazabilidad temporal y rectificaciones

La fecha disponible para las entradas de escenario S1, S2a, S2b, S3a, S3b y
S4 es **2026-10-20**. Las marcas horarias intradía no constan; por tanto, la
secuencia que sigue es la secuencia documental de decisiones y revisiones, no
una reconstrucción de horas no registradas.

1. **S3a y sus extensiones informacionales** — Las entradas D0/D1/D2,
   ablación P0/contexto y ruido observacional registran primero el contraste
   entre dinamismo exógeno observable, estimación LinUCB y mapa fijo. La
   interpretación inicial de que LinUCB dinámico superaba el mapa fijo se
   acotó cuando P0, sin actualizar parámetros, igualó al oráculo en el caso
   conocido `E[R]=C`. Resultado actual: la reorganización con información
   correcta explica esa ventaja en el protocolo; la incertidumbre añadida
   reduce resultados, con efecto dependiente de D y σ.
2. **S1 → S2a → S2b** — Se estableció primero asignación lineal estática;
   luego se permitió demanda variable sin acoplamiento y se verificó
   separabilidad; finalmente se introdujo sólo el presupuesto global, que sí
   permite competencia entre periodos. La igualdad S2a es una identidad; el
   gap S2b es una observación exacta en una instancia, no una ley estricta
   general.
3. **S3b — comparación base → revisión metodológica → factorial → GLR-CUCB**
   — La primera campaña describió UCB1, SW-UCB y media reciente. La revisión
   separó estimación, bonus, retención de historia y matching; la ablación
   2×2 encontró que el efecto del bonus depende del historial y que cada regla
   produce sus propias observaciones. La iteración GLR-CUCB implementó y
   evaluó una referencia combinatoria, pero no registró alarmas en ninguna
   ejecución; la recuperación tras cambios no se atribuye al detector. Estado
   correcto: aquella evaluación está terminada, no la investigación S3b.
4. **S4 — comparación inicial → revisión tie-aware → régimen estricto** — La
   diferencia inicial de `0.21481875` contra un único desempate reactivo se
   revisó usando BEST-MYOPIC, que optimiza sobre todos los empates inmediatos;
   el gap desapareció en el caso 2×2. Después se formuló y verificó una
   condición suficiente restringida y una familia por horizonte con acción
   inicial estrictamente subóptima, más control `enabled=False`. Conclusión
   vigente: existencia en esa familia pequeña, no ventaja general. Ambas
   lecturas previas quedan preservadas porque explican la corrección.

Las fechas exactas de estas etapas son la fecha común del registro
2026-10-20; no hay evidencia suficiente para ordenar con más precisión los
experimentos de ese día salvo por la sucesión explícita de revisiones indicada
en el propio documento. La ontología consultada está titulada/fechada
2026-10-23, aunque esta síntesis ocurre el 2026-10-21. Se conserva esa
procedencia; no es posible establecer con los artefactos disponibles si se
trata de fecha prospectiva o error de metadatos.

#### 3. Qué significa un marco unificado

La formulación matemática común y las seis especializaciones están en
[`HLS_UNIFIED_FRAMEWORK.md`](../architecture/HLS_UNIFIED_FRAMEWORK.md). La
conclusión de arquitectura científica es que HLS es, con el respaldo actual,
**una representación común de problemas heterogéneos y una familia
parametrizada para comparar organizaciones según estructura, información y
mecanismos**. También ofrece una metodología de selección/diagnóstico
condicional: matching para asignación lineal factible; solución por periodo
cuando hay separabilidad; DP como referencia en acoplamientos temporales
tratables; respuesta reactiva ante estado observado y conocido; estimación y
adaptación bajo feedback parcial; planificación cuando las acciones modifican
competencias futuras.

No está respaldada la afirmación de que HLS sea una arquitectura única ni una
teoría general validada. Los problemas de matching, MDP/POMDP, bandits y
asignación adaptativa ya tienen sus propios marcos; HLS no los reemplaza ni
reclama originalidad sobre ellos. Posible contribución propia, aún por
establecer: una metodología reproducible que conecte estructura del escenario,
dinámica real de capacidad, información, restricciones y organización, y
cuantifique interacción, beneficios y costes con comparadores justos. La
evidencia actual establece casos y contraejemplos acotados, no esa contribución
general.

#### 4. Estado científico y prioridades de trabajo

**Completado:** seis escenarios matemáticamente articulados; referencias
exactas de matching y de enumeración para S1/S2a/S2b/S4 en tamaños pequeños;
evidencia S3a con competencia observable y ruido de observación; campañas
S3b base, factorial y GLR-CUCB preservadas; revisión S4 de empates y
verificación de una familia de ventaja estricta. Implementación, prueba,
ejecución y validación científica permanecen como estados distintos: por
ejemplo, la integración matching+estimadores S3b está ejecutable y probada,
pero sus garantías combinatorias no están demostradas.

**Interpretaciones descartadas o limitadas:** demanda variable sin
acoplamiento no requiere planificación; no toda restricción intertemporal
produce gap; reorganización observable no es evidencia de aprendizaje del
selector; el primer gap S4 no vencía una referencia miope tie-aware; ninguna
alarma GLR observada permite atribuir recuperación al detector.

**Prioridades de conocimiento (sin calendarizar ni autorizar campañas):**

1. **Consolidación del marco HLS:** mantener definiciones, información,
   recursos, objetivos y niveles A/B/C trazables; declarar explícitamente qué
   es extensión respecto a los seis escenarios.
2. **S3b — línea abierta:** cualquier decisión posterior debe resolver una
   pregunta identificable sobre feedback semi-bandit, matching, exploración,
   historia o cambio-detección; los resultados GLR negativos forman parte de
   la evidencia y no justifican por sí solos otra arquitectura.
3. **Generalización S4:** distinguir existencia matemática ya verificada de
   robustez/prevalencia; no extrapolar fuera del perfil MIS-v2 y familia
   estrecha comprobados.
4. **Escalabilidad:** exact assignment, DP y enumeración sólo se han
   establecido en instancias pequeñas; coste computacional a escala permanece
   sin caracterizar.
5. **Validez de escenarios:** todos los casos S1–S4 aquí consolidados son
   sintéticos; la relación con un dominio práctico, sus datos y parámetros
   empíricos no está validada por estas ejecuciones.

Estas son dependencias y preguntas de investigación, no un calendario ni
protocolo experimental. **No se programa una campaña nueva en esta
consolidación.** Cualquier futura implementación o medición requiere una
decisión científica separada que especifique qué evidencia falta y por qué
los artefactos existentes no la aportan.

#### 5. Trazabilidad documental

La formulación común está en
[`HLS_UNIFIED_FRAMEWORK.md`](../architecture/HLS_UNIFIED_FRAMEWORK.md), que
incluye definiciones de estado real, observación, estimación, recompensas,
dinámicas y reducciones S1–S4. La ontología conserva sus conceptos y ecuaciones
N×K/MIS-v2 y añade una nota de conexión; no se iguala el esfuerzo divisible
N×K con el matching binario de escenarios canónicos. Los documentos fuente,
pruebas y JSON se identifican en el §6 del marco unificado. No se alteraron los
resultados ni el código de ningún escenario.
