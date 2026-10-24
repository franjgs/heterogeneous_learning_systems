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

### 2026-10-21 — S3b: diagnóstico de detectabilidad GLR

**Motivación.** La evaluación GLR-CUCB anterior ejecutó las 30 semillas de
S3b-0, las 30 de S3b-1 y las 120 oportunidades de cambio de S3b-2 sin alarmas.
Esta entrada separa error de implementación, falta de evidencia por pareja,
umbral respecto al horizonte y relevancia para el matching. No se modificaron
GLR-CUCB, sus parámetros, las políticas ni los escenarios.

#### Verificación matemática y de información

La inspección de [`glr_cucb.py`](../../src/hls/glr_cucb.py) confirma que el
detector calcula para cada brazo observado

`max_{1<=s<n} {s KL_Bern(p_1:s || p_1:n) + (n-s) KL_Bern(p_(s+1):n || p_1:n)}`,

incluyendo todos los puntos de corte y las convenciones Bernoulli de frontera.
Coincide con la ecuación (1) y la Definición 2.6 de Zhou et al. El umbral es
`beta(n,delta)=2 Q(log(3 n^(3/2)/delta)/2)+6 log(1+log n)`: se aplica el límite
superior publicado de `Q` para argumentos `x>=5`; cuando `x<5`, el código lo
eleva a 5, una extensión conservadora porque `Q` es creciente. El detector se
evalúa al recibir feedback de un brazo, usa `n` observaciones de ese brazo (no
tiempo global) y reinicia globalmente todos los historiales ante cualquier
alarma. La exploración forzada cicla por los nueve brazos con periodo global
relativo a `tau`; en cada periodo sólo se actualizan las aristas seleccionadas.
No se identificó un error matemático de GLR, KL, umbral, reloj ni reinicio.

La única adaptación protocolaria ya declarada permanece: las tres
observaciones comunes por pareja de los nueve periodos de calibración se pasan
como prehistoria y el reloj arranca al terminar la calibración. Esto difiere
de la inicialización cero de Algorithm 2; por tanto, no se transfieren aquí sus
garantías de regret. Las competencias/recompensas reales y cambios conocidos
sólo se usan en la evaluación posterior, nunca por el detector ni por las
decisiones.

#### Reproducción pasiva y trazas

Se instrumentó el evaluador para calcular las trazas antes de `update`, sin
escribir en el estado de política ni consumir aleatoriedad. Los 90 episodios
de los tres comparadores reprodujeron sus asignaciones y rewards esperados
archivados exactamente (diferencia máxima `0.0`). GLR-CUCB reprodujo sus
rewards esperados por semilla y conteos de alarmas (`0.0` de diferencia y cero
alarmas); el JSON GLR anterior no guarda IDs de asignación por episodio, por lo
que su reproducción exacta de la secuencia de asignaciones no se puede
verificar retrospectivamente. En los 90 episodios, las ejecuciones trazadas y
no trazadas del mismo evaluador conservaron exactamente las secuencias de
asignación de las cuatro políticas y sus rewards (diferencia máxima `0.0`);
para GLR, reward y alarmas también coinciden con el archivo previo. No se
sobrescribió ningún resultado S3b anterior.

En todos los escenarios hubo cero alarmas. Los máximos observados de
`GLR/umbral` fueron `0.2554` en S3b-0, `0.8543` en S3b-1 y `0.8691` en S3b-2;
ningún par alcanzó 1. Los máximos más próximos fueron, respectivamente,
`9.298/36.414` con `n=26`, `34.936/40.895` con `n=168` y `33.310/38.326` con
`n=78`. El umbral en los tamaños de muestra relevantes queda aproximadamente
entre 35 y 41 unidades GLR: alto frente a la evidencia empírica alcanzada en
este horizonte, aunque no es un defecto del umbral publicado.

| Escenario/cambio | Observaciones posteriores por pareja relevante | Resultado de detectabilidad |
|---|---:|---|
| S3b-0, sin cambio | 246 por pareja del matching estacionario (media); 22–29 en varias no asignadas | Sin alarma, como comportamiento esperado bajo estacionariedad |
| S3b-1, `t=150`, `0.2↔0.8` | 29.17 de media en aristas del matching anterior; 108.93 en aristas del nuevo (rango observado hasta 131); aristas sin cambio de media: 11.90 | El matching óptimo cambió en las 30 semillas; las aristas nuevas recibieron feedback, pero el máximo GLR siguió bajo umbral |
| S3b-2, cambios cada 60 periodos | En aristas cuyo valor cambió: 26.22 post-cambio de media; 13.74 en aristas del matching previo y 38.69 en aristas del nuevo (máximo 53) | Los cuatro cambios alteraron el matching óptimo; segmentos cortos y evidencia por pareja insuficiente para cruzar el umbral |

En cada breakpoint, 6 de las 9 medias de pareja cambiaron en `0.6`; tres
permanecieron iguales. En `t=150` (y `t=60,240` en la transición 0→1), cambian
`(0,0),(1,1),(2,2),(0,1),(1,2),(2,0)`; permanecen iguales
`(0,2),(1,0),(2,1)`. En `t=120` (1→2) cambian
`(0,1),(1,2),(2,0),(0,2),(1,0),(2,1)` y permanecen iguales las diagonales.
En `t=180` (2→0) cambian `(0,2),(1,0),(2,1),(0,0),(1,1),(2,2)` y quedan
iguales `(0,1),(1,2),(2,0)`. El matching óptimo cambió en cada breakpoint y las seis
aristas que cambiaron pertenecían al matching antiguo o al nuevo. Por ello,
**E no explica la ausencia de detecciones**: los cambios fueron relevantes
para la solución combinatoria. Sí explica por qué no todos los pares debían
señalar alarma: tres pares por régimen no cambiaron de media.

Las cuentas por pareja son feedback efectivo, no periodos globales. En S3b-1
las aristas que dejaron el matching pierden exposición tras el cambio; las que
entraron reciben más, pero sus muestras pre-cambio eran cortas. En S3b-2 la
ventana de cada régimen fue de sólo 60 periodos; el máximo post-cambio por
pareja fue 53 y la mayoría recibió bastante menos. No se ejecutó reinicio,
así que las observaciones de regímenes anteriores siguieron mezcladas en el
GLR. Esto es evidencia de **D** combinada con poca longitud de segmento.

#### Control aislado del detector

Se ejecutaron secuencias Bernoulli predefinidas con 100 semillas (`41000–41099`),
`delta=20/300`, umbral original, 60 observaciones pre-cambio y presupuestos de
10, 25, 50 o 100 observaciones post-cambio. El control estacionario tuvo 0/100
falsas alarmas. Tasas de detección acumulada:

| Medias antes→después | 10 obs. | 25 obs. | 50 obs. | 100 obs. |
|---|---:|---:|---:|---:|
| `0.45→0.55` (pequeño) | 0% | 0% | 0% | 0% |
| `0.30→0.70` (moderado) | 0% | 0% | 0% | 0% |
| `0.20→0.80` (amplitud S3b) | 0% | 0% | 2% | 7% |
| `0.10→0.90` (grande) | 0% | 5% | 60% | 100% |

Para el salto `0.20→0.80`, 15 observaciones pre-cambio (subcaso que aproxima
mejor la exposición de aristas nuevas de S3b-1) produjeron 0/100 detecciones
hasta 100 muestras post-cambio; el máximo `GLR/umbral` fue `0.647`. Con 60
observaciones previas, sólo 7/100 detectaron antes de 100 muestras post, con
retraso medio condicionado a detección de `69.57`. Es prueba de potencia
empírica bajo estas semillas y esta parametrización, no una cota probabilística
ni demostración de imposibilidad. Confirma **B+C**: para el salto de S3b, el
umbral conservador exige más evidencia de la que típicamente ofrecen los
segmentos/exposiciones disponibles. En S3b-1 también opera **D** para aristas
que dejan de ser elegidas; S3b-2 añade que se cambia de régimen antes de que
muchas parejas acumulen muestras suficientes.

#### Diagnóstico y decisión

- **A — error de implementación:** no observado en GLR Bernoulli, segmentación,
  umbral publicado/conservador, relojes, reinicio o feedback parcial.
- **B — evidencia insuficiente:** respaldada por los cocientes GLR/umbral y el
  control aislado; incluso el salto exacto S3b detectó raramente dentro de 100
  observaciones por pareja.
- **C — umbral conservador para `T=300`:** cierto en sentido operativo (ningún
  cociente llegó a uno y umbrales cercanos a 35–41), no como error ni motivo
  para cambiar `delta`.
- **D — observación desigual/insuficiente:** respaldada, especialmente para
  aristas que dejan de ser elegidas y para segmentos recurrentes de 60 rondas;
  no es la única causa porque algunas aristas nuevas acumularon >100 feedbacks.
- **E — cambios irrelevantes para matching:** descartada como explicación
  general; cada cambio sí alteró el matching óptimo, aunque tres aristas no
  cambiaron su media en cada régimen.

**Conclusión:** la ausencia de alarmas es coherente con una implementación
GLR matemáticamente alineada, un umbral deliberadamente conservador y pocas
observaciones post-cambio por pareja dentro del horizonte. El detector sí
funciona con evidencia fuerte: en el control `0.10→0.90`, detectó en 100/100
semillas antes de 100 observaciones y sin falsas alarmas en el control
estacionario. Para HLS esto implica que “cambió la solución óptima” no basta:
una política combinatoria debe observar repetidamente las parejas diagnósticas,
y el horizonte/segmento debe permitir acumular señal antes del siguiente
cambio. Es una conclusión limitada al protocolo sintético S3b, no una
recomendación de cambiar el algoritmo o sus parámetros. No se abre otro
escenario ni campaña; S3b permanece como línea científica abierta conforme a
la consolidación del 21/10.

Artefactos nuevos: [diagnóstico reproducible](../../experiments/diagnose_hls_s3b_glr_detectability.py),
[pruebas de no interferencia](../../tests/test_hls_s3b_glr_detectability.py) y
[trazas compactas por semilla/pareja](../../results/experiments/hls_s3b_glr_detectability/results.json).
Reproducción:

```bash
PYTHONPATH=.:src pytest -q tests/test_hls_s3b_glr_cucb.py \
  tests/test_hls_s3b_glr_detectability.py \
  tests/test_hls_s3b_nonstationary_assignment.py \
  tests/test_hls_lab_nk_assignment.py
PYTHONPATH=.:src python experiments/diagnose_hls_s3b_glr_detectability.py
```

### 2026-10-21 — S3b-L: evaluación organizativa a horizonte extendido

**Protocolo bloqueado antes de la evaluación.** Para determinar si el
resultado GLR de 300 periodos era una limitación temporal, se preparó una
comparación emparejada de 2400 ciclos operativos abstractos (duración física
no inferida), 3 agentes × 3 tareas, 30 semillas originales `9300–9329`, con
los mismos nueve periodos iniciales de calibración, matching exacto y feedback
Bernoulli sólo en aristas ejecutadas. Los tres métodos son UCB1+matching,
SW-UCB+matching y GLR-CUCB+matching. Las medias y rotaciones siguen el diseño
original (`0.2/0.8`, con una permutación cíclica por régimen); L0 es estacionario,
L1 cambia una vez en `t=1200`, y L2 en `t={600,1200,1800}`. Las competencias
reales, los breakpoints y los uniformes potenciales se reservan al entorno y
evaluación. Se conservan el generador, el orden de aristas y la semilla XOR del
experimento original, extendiendo el flujo a 2400 periodos.

La longitud SW-UCB se fijó por la regla ya usada en S3b,
`W=round(2 sqrt(T log(T)/M))`, con rango de recompensa `B=1` y `M` igual al
número de cambios de la condición predefinida: L0 `W=2400`, L1 `W=273`, L2
`W=158`. No se usan instantes de cambio. Para GLR-CUCB se detectó que la
parametrización del runner histórico (`epsilon=0.5 sqrt((9−1)log(T)/T)`,
`delta=20/T`) no corresponde literalmente a una receta que el artículo
establezca como universal; no se altera el algoritmo. Appendix C.2 reporta
para el experimento sintético del artículo `p=0.05 sqrt((Nseg−1)log(T)/T)`
con `Nseg=5` y `delta=20/T`; `Nseg` significa número de segmentos y `K` en las
ecuaciones es el número de brazos base, no agentes ni tipos de tarea. Para
evitar filtrar el número de cambios y seguir una regla teórica reproducible, se fijó para los
tres regímenes el corolario del artículo para número de segmentos desconocido:
`p=sqrt(K log(T)/T)`, `delta=1/T`, usando `K=9` brazos base agente-tarea,
`T=2400` (`p≈0.1709`, `delta≈0.0004167`). Es una parametrización theorem-guided,
no una reproducción exacta de los experimentos sintéticos del artículo. La
composición de GLR-CUCB con matching bipartito sigue siendo la adaptación HLS;
no se reclaman garantías teóricas trasladadas. La inicialización común de
nueve periodos también difiere de la inicialización en cero del pseudocódigo
publicado.

Pruebas focalizadas de configuración, matrices/regímenes, historial de
calibración sin fuga de información, restricciones de matching y componentes
previos: `34 passed`; `py_compile` y `git diff --check` pasan. Como smoke test
operativo previo a la campaña se evaluó una vez la semilla `9300`/L1, que
pertenece al conjunto luego fijado de evaluación; no se utilizó para ajustar
ningún parámetro ni se cambió el protocolo, pero se registra como una
limitación menor de separación estricta entre preflight y evaluación. La
re-ejecución determinista de tres episodios (uno por condición) coincidió
exactamente con sus asignaciones y recompensas guardadas. Los hashes de los
tres resultados históricos S3b se comprobaron antes y después; no se han
sobrescrito.

**Resultados (30 semillas emparejadas por condición; reward esperado medio
acumulado, IC 95% entre semillas).** El oráculo esperado es `5738.40` en las
tres condiciones (`2391×2.4`). El regret es oráculo menos reward esperado.

| Condición | Política | Reward esperado [IC95%] | Regret esperado | Reward Bernoulli realizado medio | Matching óptimo |
|---|---|---:|---:|---:|---:|
| L0 estacionario | UCB1 | 5628.56 [5625.42, 5631.70] | 109.84 | 5630.43 | 96.59% |
| L0 | SW-UCB | 5628.56 [5625.42, 5631.70] | 109.84 | 5630.43 | 96.59% |
| L0 | GLR-CUCB | 5232.34 [5229.09, 5235.59] | 506.06 | 5231.23 | 85.30% |
| L1 abrupto | UCB1 | 5580.10 [5570.95, 5589.25] | 158.30 | 5575.17 | 95.43% |
| L1 | SW-UCB | 5168.42 [5160.63, 5176.21] | 569.98 | 5163.37 | 82.94% |
| L1 | GLR-CUCB | 5112.66 [5104.27, 5121.05] | 625.74 | 5111.10 | 82.33% |
| L2 recurrente | UCB1 | 5434.34 [5422.51, 5446.17] | 304.06 | 5444.13 | 90.82% |
| L2 | SW-UCB | 4966.62 [4958.12, 4975.12] | 771.78 | 4978.73 | 77.01% |
| L2 | GLR-CUCB | 4871.24 [4859.35, 4883.13] | 867.16 | 4880.43 | 76.46% |

Las diferencias pareadas de reward esperado acumulado (media e IC95%) fueron:

| Condición | Contraste | Diferencia [IC95%] |
|---|---|---:|
| L0 | GLR − UCB1 = GLR − SW-UCB | −396.22 [−399.73, −392.71] |
| L1 | GLR − UCB1 | −467.44 [−479.20, −455.68] |
| L1 | GLR − SW-UCB | −55.76 [−67.94, −43.58] |
| L1 | SW-UCB − UCB1 | −411.68 [−422.59, −400.77] |
| L2 | GLR − UCB1 | −563.10 [−579.70, −546.50] |
| L2 | GLR − SW-UCB | −95.38 [−111.00, −79.76] |
| L2 | SW-UCB − UCB1 | −467.72 [−481.54, −453.90] |

Todas las diferencias GLR frente a los comparadores en L1/L2 excluyen cero
en estos IC pareados. UCB1 y SW-UCB coincidieron exactamente en reward y
asignaciones en L0. En los regímenes de L1, reward esperado medio por ciclo
(antes→después del cambio) fue UCB1 `2.324→2.343`, SW-UCB `2.162→2.161` y GLR
`2.184→2.093`. En L2, UCB1 obtuvo `2.277, 2.313, 2.298, 2.204`; SW-UCB
`2.089, 2.067, 2.075, 2.078`; GLR `2.169, 1.996, 1.995, 1.991`. El archivo
de resultados contiene además la serie temporal agregada del regret y las
trazas por semilla para los 2391 ciclos evaluados.

**Actividad de detección y organización.** GLR produjo `0/30` alarmas en L0,
`30/30` en L1 y `90/90` alarmas correspondientes a sus tres cambios en L2;
no hubo alarmas estacionarias ni alarmas extra en L1/L2. Retraso medio
condicional: `68.47` ciclos para el cambio de L1 y `65.60`, `64.87`, `66.37`
para los tres cambios de L2 (respectivamente; cada cambio se detectó en las
30 semillas). Son retrasos del 5.7% de un régimen L1 y ~11% de uno L2. Tras
la alarma, la siguiente asignación cambió respecto a la anterior en `60.0%`
de episodios L1 y `87.8%` de eventos L2. Evaluando sólo a posteriori contra el
matching verdadero: ninguna primera decisión post-alarma fue óptima en L1,
pero `96.7%` alcanzó una asignación óptima en algún momento dentro de los diez
ciclos siguientes (`83.3%` exactamente al retardo 10); en L2 `21.1%` fue
óptima inmediatamente y `88.9%` alcanzó una óptima dentro de diez ciclos
(`75.6%` exactamente al retardo 10). Este análisis confirma
reorganización posterior a la detección, no que el reinicio sea la causa de
la recompensa obtenida.

GLR forzó exploración en media `414.0/2391` periodos L0 (`17.3%`), `421.37`
L1 (`17.6%`) y `429.17` L2 (`17.9%`). El regret esperado que coincidió con
periodos forzados fue `499.70`, `506.40`, `511.56`, respectivamente. Son
regrets observados durante esos periodos, no estimaciones contrafactuales del
coste causal. En L0, el regret total GLR fue `506.06`, por lo que casi todo
coincidió con la exploración forzada; el hecho de no haber falsas alarmas no
elimina ese coste. Todas las políticas usaron tres unidades de recurso por
ciclo evaluado, sin diferencia de capacidad.

**Interpretación y decisión.** La ampliación temporal resolvió el fallo de
activación: el detector detectó de forma reproducible las transiciones de
este diseño, y la demora fue menor que la duración de cada régimen. No
resolvió la cuestión organizativa a favor de GLR-CUCB: su reward esperado fue
menor que UCB1 y SW-UCB en las dos condiciones cambiantes y menor que UCB1 en
estacionario; además, la política de ventana rindió también por debajo de
UCB1 en L1/L2 con esta ventana preespecificada. La detección sí precedió a
reasignaciones y a recuperación parcial, pero la tasa de forced exploration,
los reinicios globales y su interacción con índices/matching coinciden con
regret alto. Sin ablación contrafactual en este protocolo, no se separa
causalmente el coste de explorar del coste del reinicio. **Recomendación:**
GLR-CUCB deja de ser la arquitectura candidata principal para este S3b; UCB1
+ matching queda como referencia/candidato empírico principal en las
condiciones aquí evaluadas, no como ganador general ni con garantía heredada.
GLR-CUCB se conserva como comparador con detección activa. Se cierra esta
evaluación larga, no la línea S3b: no se abre otra campaña de ajuste.

La compatibilidad sigue siendo la de un semi-bandit aditivo con nueve brazos
Bernoulli y feedback de aristas seleccionadas, pero la aplicación de GLR-CUCB
al matching es una adaptación, con prehistoria común distinta del Algorithm 2.
No se transfieren las garantías publicadas. La hipótesis de ciclos abstractos
no corresponde a una duración empírica; sólo cambia el horizonte matemático.

Reproducción: `PYTHONPATH=.:src python experiments/run_hls_s3b_long_horizon.py`.
Resultados compactos por escenario/semilla, series de regret, alarmas y
decisiones: `../../results/experiments/hls_s3b_long_horizon/results.json`.
Runner y pruebas: `../../experiments/run_hls_s3b_long_horizon.py` y
`../../tests/test_hls_s3b_long_horizon.py`. Referencia metodológica: Zhou et
al., *A Near-Optimal Change-Detection Based Algorithm for Piecewise-Stationary
Combinatorial Semi-Bandits*, AAAI 2020,
https://arxiv.org/abs/1908.10402.

## 2026-10-21 — D-UCB: reproducción de cambios abruptos y adaptación S3b

**Motivación y fuente primaria.** Se leyó el artículo completo de Garivier y
Moulines, *On Upper-Confidence Bound Policies for Non-Stationary Bandit
Problems* (https://arxiv.org/abs/0805.3415), incluidas las secciones de
definición, análisis y simulaciones. La reproducción objetivo es el primer
ejemplo de la sección 5, no el ejemplo de evolución periódica. El artículo fija
K=3, T=10.000, recompensas Bernoulli independientes y medias
`(0.5, 0.3, p3(t))`, con `p3=0.4` para `t<3000` o `t>=5000` y `p3=0.9` para
`3000<=t<5000`. El óptimo instantáneo es el brazo 1 antes y después del
intervalo, y el brazo 3 durante este. La sección 5 no declara semillas ni
número de réplicas Monte Carlo.

**Formulaciones y parámetros verificados.** Para D-UCB se implementaron
`S_t(gamma,i)=sum_{s<=t} gamma^(t-s) X_s(i) 1{I_s=i}`,
`N_t(gamma,i)=sum gamma^(t-s) 1{I_s=i}`, media `S/N`,
`n_t(gamma)=sum_i N_t(gamma,i)` e índice
`S/N + 2B sqrt(xi log(n_t(gamma))/N_t(gamma,i))`. Cada periodo descuenta
también los brazos no seleccionados; el brazo no observado recibe índice
optimista infinito hasta su inicialización. La inicialización reproduce el
artículo: una selección forzada de cada brazo durante las primeras K rondas.
UCB-1 y SW-UCB usan las expresiones publicadas, respectivamente
`media + B sqrt(xi log(t)/N)` y
`media_tau + B sqrt(xi log(min(t,tau))/N_tau)`.

Los parámetros de la simulación del artículo son `xi=1/2`,
`gamma=1-1/(4 sqrt(T))` (0.9975 en T=10.000) y
`tau=4 sqrt(T log(T))` (1214, redondeado). Se conservaron literalmente para
esta reproducción. Es distinto de las elecciones derivadas en las notas
teóricas al conocer el número de cambios. Además, los teoremas del artículo
requieren `xi>1/2`; por tanto, el valor `xi=1/2` es el ajuste empírico de su
sección 5, no una instancia cubierta literalmente por esas cotas. Se comparó
el trío UCB-1/D-UCB/SW-UCB con 50 semillas propias emparejadas. EXP3.S también
aparece en la figura original, pero no existe implementación EXP3.S en el
laboratorio y no se añadió otro algoritmo: esta es una reproducción del
subconjunto UCB, no una reproducción de todas las curvas de la figura.

**Resultado de la reproducción (media de reward esperado acumulado; regret
dinámico esperado entre paréntesis, IC95% pareado entre semillas).** El oráculo
instantáneo acumula 5800:

| Política | Reward esperado [IC95%] | Regret esperado | Coincidencia con brazo óptimo |
|---|---:|---:|---:|
| UCB-1 | 5130.854 [5098.321, 5163.387] | 669.146 | 48.81% |
| D-UCB | 5199.280 [5193.572, 5204.988] | 600.720 | 60.92% |
| SW-UCB | 5511.908 [5492.069, 5531.747] | 288.092 | 79.61% |

D-UCB ganó a UCB-1 por `+68.426` reward esperado (IC95% pareado
`[35.750, 101.102]`); SW-UCB ganó a D-UCB por `+312.628`
(`[292.060, 333.196]`). La selección del brazo óptimo fue, antes/durante/después
del episodio temporal: UCB-1 `0.906/0.248/0.132`, D-UCB
`0.551/0.062/0.529` y SW-UCB `0.828/0.070/0.726`. El regret por esos tres
regímenes fue, respectivamente, UCB-1 `35.0/199.8/434.4`, D-UCB
`185.8/99.0/315.9` y SW-UCB `66.2/63.3/158.6`. Esto apoya la ventaja de
olvidar parcialmente frente al UCB estacionario y el coste de la memoria
descontada frente a la ventana en esta reproducción. D-UCB no igualó
cuantitativamente a SW-UCB, aunque conservó el orden cualitativo de ambos
métodos no estacionarios por delante de UCB-1 en regret total. Como el artículo
no aporta semillas ni tamaño de muestra, la discrepancia respecto a la frase
“casi tan bien” no puede convertirse en una comparación numérica directa; la
brecha observada queda registrada, no ajustada.

Con un criterio más estricto de recuperación —20 elecciones óptimas
consecutivas antes del siguiente cambio— D-UCB lo alcanzó en 50/50 semillas
tras la mejora (retraso medio 7.9) y 49/50 tras la reversión (518.3); SW-UCB,
50/50 y 48/50 (125.8 y 602.2); UCB-1, 42/50 y 5/50 (266.3 y 0.0 entre las
cinco que ya estaban óptimas al inicio de la fase). Esto distingue detectar o
visitar pronto el brazo correcto de sostener la política correcta.

**Adaptación HLS 3×3 inspirada en el artículo.** Se mantuvieron T=10.000 y los
cambios `t=3000,5000`. La matriz base fue
`((.8,.05,.05),(.05,.8,.05),(.4,.05,.1))`; en el intervalo central únicamente
`c[2,0]` cambia de `.4` a `.9`. La enumeración exhaustiva de las seis
asignaciones perfectas, independiente del solver SciPy, verificó óptimos
únicos: base `((0,0),(1,1),(2,2))`, valor 1.70; intervalo
`((0,2),(1,1),(2,0))`, valor 1.75; después vuelve el óptimo base. Por tanto,
la competencia localizada cambia efectivamente la organización óptima y luego
revierte. Se usaron 30 semillas emparejadas, recompensas Bernoulli potenciales
comunes por periodo/arista, nueve periodos de calibración común que cubren cada
pareja tres veces y matching exacto en todas las políticas. UCB-1, D-UCB y
SW-UCB usaron `xi=.5`; D-UCB usó `gamma=.9975` y SW-UCB `tau=1214`. Las
políticas solo recibieron feedback de las aristas ejecutadas.

| Política + matching | Reward esperado [IC95%] | Regret esperado | Reward realizado medio | Matching óptimo |
|---|---:|---:|---:|---:|
| UCB-1 | 16860.297 [16848.849, 16871.744] | 224.403 | 16860.333 | 91.98% |
| D-UCB | 14999.198 [14988.182, 15010.214] | 2085.502 | 15005.867 | 65.70% |
| SW-UCB | 16691.137 [16683.114, 16699.159] | 393.563 | 16689.500 | 88.68% |

El óptimo esperado del horizonte de evaluación (9991 periodos, sin contabilizar
la calibración común) es 17084.7. En contrastes pareados de regret, D-UCB
acumuló `1861.098` más que UCB-1 (IC95% `[1848.731,1873.465]`) y `1691.938`
más que SW-UCB (`[1681.114,1702.763]`). D-UCB sí eligió por primera vez el
matching óptimo más pronto tras los cambios (promedio `3.6` y `1.3` ciclos,
frente a UCB-1 `252.9` y `210.6`, SW-UCB `66.2` y `17.5`), pero su tasa de
matching óptimo permaneció mucho menor en los tres regímenes: aproximadamente
`69.4%/49.8%/69.8%`, frente a UCB-1 `97.6%/80.3%/93.3%`. La rapidez de la
primera decisión correcta no equivale a recuperación sostenida ni a mayor
reward. El resultado es compatible con un coste persistente de índices
optimistas por arista dentro de una asignación múltiple; no identifica
causalmente exploración como explicación única.

Con el mismo criterio de 20 asignaciones óptimas consecutivas antes del
siguiente cambio, D-UCB solo logró recuperarse en 3/30 y 2/30 semillas
(retrasos medios condicionales 382.7 y 528.5); UCB-1 en 28/30 y 30/30
(306.6 y 226.6); SW-UCB en 30/30 en ambos cambios (134.3 y 72.2). La
desventaja de D-UCB en el escenario combinatorio no se explica por tardar en
producir una primera coincidencia: en esta instancia se asocia con no sostener
el matching correcto.

**Traslado a los S3b históricos.** Se añadió D-UCB, sin cambiar matrices,
horizonte, recompensas o semillas de L0/L1/L2 (H=2400, 30 semillas). Se usó
`gamma=1-1/(4 sqrt(2400))=0.994896`, `xi=.5`; se mantuvo el discounting por
periodo global y feedback solo de matching. En la semilla 9300 se reejecutaron
UCB-1, SW-UCB y GLR-CUCB y el reward esperado acumulado reprodujo exactamente
los artefactos existentes; estos conservan sus series históricas y no se
sobrescribieron. Los comparadores publicados de ese S3b ya usaban `xi=2`, así
que la comparación retrospectiva con D-UCB (`xi=.5`) es descriptiva y no una
comparación de hiperparámetros igualados.

| Condición | D-UCB reward esperado [IC95%] | UCB-1 previo | SW-UCB previo | GLR-CUCB previo |
|---|---:|---:|---:|---:|
| L0 estacionario | 4974.140 [4967.120, 4981.160] | 5628.560 | 5628.560 | 5232.340 |
| L1 abrupto | 4950.940 [4943.238, 4958.642] | 5580.100 | 5168.420 | 5112.660 |
| L2 recurrente | 4935.760 [4929.268, 4942.252] | 5434.340 | 4966.620 | 4871.240 |

Las diferencias pareadas de D-UCB frente a UCB-1 fueron `-654.42` en L0,
`-629.16` en L1 y `-498.58` en L2; frente a SW-UCB fueron `-654.42`, `-217.48`
y `-30.86`; frente a GLR-CUCB fueron `-258.20`, `-161.72` y `+64.52`. En los
escenarios históricos, por tanto, D-UCB quedó por debajo de UCB-1 y SW-UCB en
las tres condiciones y solo superó a GLR-CUCB en L2. Esto no se puede
atribuir exclusivamente a la dinámica del índice por la diferencia de `xi`
indicada.

**Lectura A/B/C y conclusión.** A — sistema: competencias heterogéneas
desconocidas, recompensas Bernoulli y cambios exógenos; en la réplica original
hay una mejora temporal y reversión. B — problema: bandit de una elección en
la reproducción y semi-bandit combinatorio en HLS, con feedback parcial. C —
arquitectura: estimador UCB por brazo/arista más selección individual o
matching bipartito exacto. En el bandit original, D-UCB mejoró a UCB-1 y quedó
por debajo de SW-UCB. Al introducir matching, D-UCB fue más rápido en la
primera reorganización, pero perdió en reward acumulado y porcentaje de
matching óptimo; no se trasladó la ventaja organizativa. La reversión importa
porque exige olvidar el episodio temporal, pero también deja un tramo largo
estacionario donde el descuento mantiene incertidumbre y exploración. La
composición multiple-play no hereda las garantías single-play del artículo.
No se concluye generalidad más allá de estas matrices, semillas, parámetros y
horizontes.

**Estado y trazabilidad.** Evaluación ejecutada y documentada; no se abren más
campañas en esta tarea. Reproducción y resultados: ejecutar
`PYTHONPATH=.:src python experiments/run_hls_s3b_discounted_ucb.py`; artefacto
independiente `../../results/experiments/hls_s3b_discounted_ucb/results.json`.
Implementación del estimador: `../../src/hls/nonstationary_assignment.py`;
runner: `../../experiments/run_hls_s3b_discounted_ucb.py`; pruebas focalizadas:
`../../tests/test_hls_s3b_discounted_ucb.py`. La formulación del entorno se
mantiene dentro de S3b de `../../docs/architecture/HLS_UNIFIED_FRAMEWORK.md`.

## 2026-10-21 — Formalización de modalidades organizativas y separación A/B/C

**Tipo/estado:** aclaración del marco científico; documentación. No es una
decisión de algoritmo, rediseño de software ni reinterpretación de resultados
anteriores. Se apoya en el marco unificado, la ontología v0.1 y los contratos
implementados para selección individual, asignación combinatoria y planificación.

**Decisión conceptual.** La formulación de HLS distingue:

- **A — Modelo del sistema:** agentes `I`, tareas `K`, competencias reales
  `C_t`, entorno `Z_t`, demanda `D_t`, recursos, dinámica de capacidades,
  recompensa y observación. Cada instancia declara qué es conocido, latente,
  estático/dinámico, exógeno/endógeno y completo/parcialmente observable.
- **B — Problema y modalidad organizativa:** decisión que debe tomarse,
  participantes elegibles, cobertura, conjunto factible y dependencias entre
  decisiones. B1 selecciona un agente `a_t∈I_t` para una tarea; B2 elige una
  asignación conjunta `X_t∈𝒳(S_t,D_t)`; B3 elige acciones por periodo con
  consecuencias optimizadas sobre un horizonte. B1–B3 no son exhaustivas.
- **C — Arquitectura de decisión:** política o composición concreta que
  estima información, optimiza acciones factibles y/o planifica. Estas
  funciones son opcionales según el problema. El aprendizaje de estimaciones
  (EXP3/LinUCB/UCB/D-UCB) no es aprendizaje de competencias (MIS-v2); matching
  es un solver para una estructura bipartita concreta, no sinónimo de
  organización.

La notación general es `u_t∈𝒰(S_t,D_t)`, con
`S_{t+1}=F(S_t,D_t,u_t,ξ_{t+1})` y
`max_{π∈Π} E_π[Σ_{t=0}^{T−1}R(S_t,u_t,D_t)+R_T^{term}]` (el término terminal
se omite si no existe). En B1, `u_t=a_t`; en B2, `u_t=X_t`; en B3 la política
sigue decidiendo por periodo, pero valora la continuación. La notación
histórica `X_t`/`x[i,k,t]` para asignación se conserva en sus escenarios.

**Relación con S1–S4.** Estos identificadores describen regímenes del sistema
y acoplamiento temporal, no fijan una modalidad universal: S1/S2a usan B2
por periodo; S2b añade B3 por presupuesto compartido; S3a evalúa B2 reactivo
con competencia observable; S4 combina acciones B2 y planificación B3 por
competencia endógena. S3b admite como configuraciones descriptivas distintas
la elección individual B1 y la asignación combinatoria B2. `S3b-B1` y
`S3b-B2` son etiquetas explicativas nuevas; no cambian nombres de artefactos.

**Evidencia S3b y límites.** En la reproducción bandit inspirada en
Garivier–Moulines, regret dinámico esperado: UCB1 `669.146`, D-UCB `600.720`,
SW-UCB `288.092`. En la instancia HLS 3×3 con matching: UCB1+matching
`224.403`, D-UCB+matching `2085.502`, SW-UCB+matching `393.563`. Son instancias
distintas y sus regrets no son comparables directamente. No se ha demostrado
que matching por sí solo cause el cambio de ranking, ni se ha identificado
una arquitectura universalmente óptima para S3b; la línea científica S3b
permanece abierta.

**Trazabilidad documental.** La formulación matemática, las modalidades y el
mapa de escenarios se desarrollan en
[`HLS_UNIFIED_FRAMEWORK.md`](../architecture/HLS_UNIFIED_FRAMEWORK.md); la
ontología añade esta aclaración sin sustituir sus definiciones N×K en
[`HLS_ONTOLOGY_V0_1_2026-10-23.md`](../architecture/HLS_ONTOLOGY_V0_1_2026-10-23.md).
Los artefactos y cifras previas permanecen intactos. El marco general no
prescribe modalidad ni algoritmo; cada solución se estudia y valida para
una configuración concreta.

## 2026-10-21 — Decisión PI y diseño revisado de HLS-S3b-E1

**Estado:** GO para especificación; E1 especificado, aún no implementado ni
ejecutado. Entrada cronológica nueva. Se conservan íntegramente las decisiones,
resultados y límites históricos anteriores.

**Título aprobado:** “Interacción entre aprendizaje, información y
organización”.

### Estado anterior y consolidación conceptual

Antes de esta decisión, HLS ya tenía escenarios de referencia S1–S4 y una
formulación A/B/C que separaba sistema, modalidad organizativa y arquitectura.
El marco común usa estado real `S_t`, demanda `D_t`, decisión `u_t`, conjunto
factible `𝒰(S_t,D_t)`, observación `Y_t^{obs}∼O(·|S_t,u_t)` y dinámica
`S_{t+1}=F(S_t,D_t,u_t,ξ_{t+1})`. La política solo utiliza observaciones,
historia y conocimiento/modelo declarados; no recibe el estado real ni
diagnósticos del evaluador.

Se conserva la distinción entre modalidad B1 (elección individual de una
pareja agente-tarea), B2 (asignación conjunta) y B3 (decisiones por periodo
optimizadas considerando consecuencias intertemporales). Pueden incorporarse
otras modalidades si se justifican. Matching sigue siendo un optimizador
para ciertos problemas bipartitos B2, no una propiedad definitoria de HLS.
S1–S4 son regímenes de referencia, no una jerarquía rígida; propiedades de
varios pueden coexistir en una configuración sin acuñar automáticamente un
nuevo escenario. Aprender estimaciones en S3b no equivale a desarrollar
competencias en S4.

### RESULTADOS OBSERVADOS

La observación que motiva E1 es:

| Modalidad previa | Horizonte | UCB1 regret | SW-UCB regret |
|---|---:|---:|---:|
| B1, selección individual | 10,000 | 669.146 | 288.092 |
| B2, matching 3×3 | 10,000 | 224.403 | 393.563 |

Estos regrets proceden de instancias distintas. No demuestran que matching
favorezca intrínsecamente UCB1 o perjudique SW-UCB. Los posibles efectos de
restricciones, número/distribución de observaciones, exposición por agente y
pareja, dinámica/magnitud de cambio, márgenes de decisión y parámetros de
memoria/exploración son explicaciones por comprobar, no resultados. Las
campañas anteriores de D-UCB y GLR-CUCB se conservan como antecedentes, pero
no entran en el conjunto inicial de E1.

### DECISIONES DEL PI

El PI decide **GO** y establece prioridades: (1) S3b, aprendizaje, adaptación
y organización; (2) S4, desarrollo endógeno; (3) S2b, planificación con
recursos intertemporales. S1, S2a y S3a permanecen como referencias. No se
autoriza desarrollar nuevas políticas HLS, ampliar escenarios sin necesidad,
repetir campañas S4 sobre ventajas ya demostradas ni refactorizar el
laboratorio de forma general. La consolidación del laboratorio será
incremental durante la investigación de S3b.

**Preguntas de decisión registradas para resolución del PI** (el repositorio
no conserva un intercambio separado con su formulación literal): (i) ¿se
prioriza S3b aunque los regrets absolutos de B1 y B2 no sean comparables? Sí:
UCB1–SW-UCB se contrastan dentro de cada modalidad y se incluyen controles
específicos. (ii) ¿se conserva S4 como prioridad o se repiten sus
demostraciones constructivas? Se conserva como segunda línea, sin repetir
ventajas ya demostradas. (iii) ¿se añaden inmediatamente nuevas políticas o
escenarios? No; se reutiliza el laboratorio y la consolidación es incremental.

### Consulta externa y aportaciones adoptadas

El CE recibió una evaluación externa del diseño de S3b-E1. Su artefacto o
referencia independiente no se encuentra en el repositorio; se registra como
insumo recibido, no como literatura verificada. Se retienen tres advertencias
metodológicas: B2-Full (bandit sobre matchings completos) cambiaría también
los estimadores y no es un control de la modalidad bajo UCB1/SW-UCB; escalar
la ventana como `W/M` no está justificado por el número total de feedbacks
por periodo, pues éstos no se distribuyen uniformemente entre parejas; y
correlaciones entre métricas no demuestran causalidad.

### HIPÓTESIS (no confirmadas)

- **H1:** cantidad/distribución del feedback explica parte del cambio de
  ranking UCB1–SW-UCB.
- **H2:** SW-UCB descarta observaciones aún útiles durante regímenes
  estacionarios.
- **H3:** fluctuaciones de índices inducen cambios de matching que generan
  regret.
- **H4:** ventana y exploración explican una parte principal de las diferencias.
- **H5:** los márgenes entre matchings cambian la pérdida colectiva causada
  por errores de estimación similares.

Ninguna hipótesis se considerará confirmada por una correlación aislada o por
una comparación agregada entre instancias.

### DECISIONES DE DISEÑO DEL CE — especificación E1.1

**Pregunta y alcance.** “¿Por qué cambia el rendimiento relativo de UCB1 y
SW-UCB entre selección individual y asignación combinatoria?” E1 estudia
aprendizaje de recompensas desconocidas bajo cambios exógenos; no desarrolla
competencias por experiencia, transferencia, enseñanza ni planificación.

**Sistema común predeclarado.** Tres agentes, tres tareas, demanda de una
unidad de cada tarea por periodo, recompensas Bernoulli independientes
condicionadas a medias `C[i,k,t]`. Se reutiliza la matriz de la adaptación
HLS 3×3 anterior:

```text
C_base      = ((0.80, 0.05, 0.05),
               (0.05, 0.80, 0.05),
               (0.40, 0.05, 0.10))
C_transient = C_base con C[2,0] = 0.90
```

Los índices de agente/tarea de esta matriz son base cero.

Horizonte `T=10,000`: base para `t<3,000`; transitoria para
`3,000≤t<5,000`; después vuelve a base. La enumeración bipartita previa
verificó matching óptimo único: base `((0,0),(1,1),(2,2))`, valor `1.70`;
transitorio `((0,2),(1,1),(2,0))`, valor `1.75`; luego se revierte. El
oráculo B1 elige la pareja de mayor media: valor `0.80` en base y `0.90` en
la fase transitoria. Es una construcción sintética y no representa una
duración industrial observada.

Se usarán 30 semillas emparejadas `8200,…,8229`, reutilizando los
identificadores de la adaptación HLS previa. Para cada semilla, generar una
matriz de uniformes potenciales con el stream `random.Random(seed XOR
0xD0C0A7)`, en orden `(periodo, agente, tarea)`, la misma semilla XOR y orden
de generación usados por esa adaptación HLS, y convertirla a Bernoulli con
la media real de esa pareja y periodo. Así las políticas comparten el mismo
resultado potencial para cada arista, aunque solo reciben el feedback
permitido. Los medios verdaderos, cambios futuros, outcomes no seleccionados
y oráculos quedan en el evaluador.

**Inicialización común de 9 periodos.** `t=0,…,8` son calibración forzada,
sin decisiones de política, pero sus recompensas y regrets se incluyen en el
total y también se reportan separadamente del tramo `t≥9`.

- B1 selecciona cada una de las nueve parejas una vez, en orden
  lexicográfico `(agente,tarea)`, y observa su recompensa.
- B2 repite tres veces el ciclo de matchings por permutaciones
  `((0,1,2),(1,2,0),(2,0,1))`. B2-Semi observa las tres recompensas de cada
  matching: 27 observaciones iniciales, tres por pareja.
- En B2-Partial se ejecutan exactamente los mismos matchings, pero se revela
  solo una pareja ejecutada. En la repetición `r∈{0,1,2}` del ciclo se
  selecciona la arista lexicográficamente ordenada de rango `r`; cada pareja
  se observa una vez en los nueve periodos.

Por tanto B1 y B2-Partial inician con una observación por pareja; B2-Semi
inicia con tres. La diferencia de información de B2-Semi es intencional y se
medirá, no se presentará como igualdad de feedback.

**Modalidades y control de información.** B1 E1 elige una pareja de las nueve
por periodo; no aplica matching. El resultado B1 que motiva E1 procede de la
reproducción de un bandit de tres brazos; la configuración E1 B1 tiene nueve
parejas candidato y no es un replay exacto de ese benchmark. B2 ejecuta
siempre un matching completo de
tres agentes y tres tareas. En B2-Semi el estimador recibe los tres
resultados individuales. En B2-Partial recibe una sola recompensa individual
después de ejecutar el matching completo; la arista se elige mediante un
índice uniforme pre-generado `q(seed,t)∈{0,1,2}` sobre las tres aristas
ejecutadas ordenadas lexicográficamente; generar rangos con
`random.Random(seed XOR 0xB2F33D)` en orden temporal, separado del stream de
recompensas y compartido entre políticas UCB1/SW-UCB. El score colectivo de
B2 siempre incluye las tres
tareas; **no** se entrega recompensa agregada al learner. El control modifica
solo feedback observable, no el conjunto factible, trabajo ejecutado ni
evaluación de rendimiento.

**Políticas reutilizadas.** Usar `PairwiseBanditEstimator` de
`src/hls/nonstationary_assignment.py`; no cambiar ecuaciones ni matching.
UCB1: `index=μ_all+sqrt(2 log(max(2,t+1))/n_all)`. SW-UCB:
`index=μ_W+sqrt(ξ log(max(2,min(t+1,W))/n_W))`, `ξ=2`, que iguala la escala
de confianza implementada por UCB1. SW conserva periodos globales y usa
observaciones `s` con `max(0,t−W)≤s<t`; una pareja sin observaciones válidas
recibe el sentinel optimista existente. Cada actualización usa únicamente
parejas seleccionadas y feedback entregado. B1 maximiza índice de pareja y
resuelve empates por menor par lexicográfico. B2 maximiza la matriz de
índices mediante el solver bipartito existente; si hay score total empatado
en tolerancia absoluta `1e-12`, se elige el matching lexicográficamente
menor entre los óptimos (enumerar las seis permutaciones 3×3 solo para
resolver empates y comprobar que el solver alcanza el mismo valor). Este
desempate determinista debe tener prueba focalizada; no cambia el índice ni
la función objetivo.

Para `T=10,000`, la ventana de referencia de la simulación bibliográfica es
`W_ref=round(4 sqrt(T log T))=1,214`. Se añade solo una ventana más larga,
`W_long=min(T,2W_ref)=2,428`, como sensibilidad predeclarada; no se ajusta
con semillas de evaluación. No se usa `W/M`: múltiples observaciones por
periodo no equivalen a esa cantidad para cada pareja.

Para separar adaptación inmediata de rendimiento de régimen, reportar los
regímenes completos `[0,3000)`, `[3000,5000)` y `[5000,10000)`, más ventanas
post-cambio predefinidas `[3000,3200)` y `[5000,5200)`. Las ventanas de 200
ciclos son diagnósticos descriptivos comunes a políticas, no costes ni un
parámetro de decisión.

**Comparaciones.** (i) UCB1 vs SW-UCB dentro de B1; (ii) UCB1 vs SW-UCB
dentro de B2-Semi y B2-Partial; (iii) B2-Semi vs B2-Partial para cada
estimador; (iv) SW-UCB con `W_ref` vs `W_long` en B2-Semi. No incluir D-UCB,
GLR-CUCB ni bandit sobre matchings completos en la primera E1.

El contraste B2-Semi vs B2-Partial es una intervención de protocolo de
información con acción factible y reward colectivo B2 constantes; su
estimando es la diferencia cerrada de política/feedback. Tras el inicio,
decisiones e historiales divergen, por lo que no separa un efecto informativo
de cada periodo del efecto mediado por asignaciones y exposición posteriores.
El contraste de ventanas cambia memoria dentro de SW-UCB, pero no identifica
por sí solo el efecto de cada término de exploración. Por ello H4 solo puede
evaluarse parcialmente en E1; variar coeficientes requeriría una decisión
posterior y no forma parte del diseño aprobado. B1-vs-B2 tampoco identifica
causalmente un efecto puro de matching, pues cambian acción y número de
trabajos/rewards por periodo.

**Oráculos y métricas.** Regret B1 por periodo es
`max_{i,k}C[i,k,t]−C[i*,k*,t]`; regret B2 es el valor de matching óptimo
con medias reales menos valor esperado de las aristas asignadas. No comparar
regrets absolutos entre modalidades. Reportar recompensa esperada y
Bernoulli realizada, regret acumulado y por régimen/transición, diferencias
pareadas UCB1–SW-UCB y B2-Semi–Partial con IC 95% pareado Student-t sobre
30 semillas, asignaciones/agentes/parejas por periodo, conteos/antigüedad
de observaciones por pareja, conteos dentro de ventana, error cuadrático de
estimación (solo diagnóstico del evaluador), índices UCB, tasa de matching
óptimo, frecuencia de cambios, margen real entre mejor y segundo matching,
retraso desde cada breakpoint hasta el primer bloque de 20 decisiones
consecutivas óptimas (en B1, cualquier pareja empatada en media máxima; si
no aparece antes del siguiente cambio/final, se registra como censurado),
restricciones activas y coste computacional descriptivo. No existe coste de
conmutación en este modelo; cambios de matching no se etiquetan como tal.

### TRABAJO PENDIENTE Y PRÓXIMOS PASOS AUTORIZADOS

- **E1.1 Especificación:** registrada en esta entrada.
- **E1.2 Adaptaciones mínimas:** pendientes; solo runner/adaptador de
  selección B1 y feedback parcial si las interfaces existentes no bastan.
- **E1.3 Pruebas de consistencia/reproducibilidad:** pendientes; validar
  información visible, calibración, common random numbers, update solo de
  feedback recibido, matching y cálculo de oráculos/métricas.
- **E1.4 Comparaciones principales:** pendientes.
- **E1.5 Controles de feedback y memoria:** pendientes.
- **E1.6 Análisis de H1–H5:** pendiente y sujeto a límites de identificación.
- **E1.7 Recomendación de siguiente experimento:** pendiente hasta analizar
  E1.

El siguiente trabajo autorizado se limita a la implementación mínima de
E1.2 y las verificaciones previas, bajo una instrucción posterior. E1 no se ha
ejecutado y esta entrada no autoriza su inicio.

## 2026-10-21 — HLS-S3b-E1 ejecutado: aprendizaje, información y organización

**Estado:** E1 ejecutado y analizado en las configuraciones predeclaradas.
Esta entrada actualiza el estado de trabajo, no reemplaza la especificación
E1.1 ni reinterpreta los experimentos históricos.

### Implementación y protocolo efectivo

Se creó `experiments/run_hls_s3b_e1.py` y la prueba focalizada
`tests/test_hls_s3b_e1.py`. Se reutilizaron
`PairwiseBanditEstimator` y `HungarianAssignmentOptimizerNK` (SciPy/Jonker–Volgenant).
Para evitar escanear todo el historial en cada decisión se añadieron sumas
prefijas por pareja en `src/hls/nonstationary_assignment.py`; la ventana,
medias, índices y feedback siguen siendo exactamente los definidos por E1.1.
Las pruebas comparan los resultados de esta optimización computacional con
un escaneo directo del historial.

Se ejecutaron `N=K=3`, `T=10,000`, 30 semillas emparejadas `8200–8229`, con 9
periodos de calibración incluidos en totales y 9,991 decisiones de evaluación.
Se conservaron matrices, cambios en `t=3000,5000`, recompensas Bernoulli
potenciales comunes, demanda, restricciones, stream de selección de feedback
parcial y ventanas `W_ref=1214`, `W_long=2428` de E1.1. UCB1 usó el índice
predeclarado `mean + sqrt(2 log(max(2,t+1))/n)`; SW-UCB usó `xi=2` y los
periodos globales de su ventana. B2 ejecutó matching completo en Semi y
Partial; Partial evaluó siempre las tres recompensas pero solo reveló una
observación individual al estimador. Las políticas no recibieron competencias,
medias verdaderas, cambios futuros ni resultados contrafactuales.

Las siete configuraciones fueron B1/UCB1, B1/SW-UCB-Wref;
B2-Semi/UCB1, SW-UCB-Wref y SW-UCB-Wlong; B2-Partial/UCB1 y SW-UCB-Wref.
Para cada seed se guardaron las series por periodo de reward esperado y
realizado, regret, acción, máscara de observaciones y éxitos, además de
muestras diagnósticas de medias, índices, bonus, conteos y antigüedad. Los
oráculos se verificaron contra enumeración de los seis matchings. Los márgenes
exactos mejor–segundo matching son `0.45` en la matriz base y `0.05` durante
el régimen transitorio.

### Resultados agregados

La tabla muestra media entre semillas e IC 95% Student-t del valor medio.
El regret se calcula respecto al oráculo de la modalidad correspondiente;
los regrets B1 y B2 no son comparables entre sí.

| Configuración | Reward esperado acumulado (IC 95%) | Regret esperado acumulado (IC 95%) | Decisión óptima | Cambios de acción |
|---|---:|---:|---:|---:|
| B1 / UCB1 | 7,827.977 [7,819.699; 7,836.255] | 372.023 [363.745; 380.301] | 0.539 | 961 |
| B1 / SW-UCB Wref | 7,328.523 [7,321.866; 7,335.181] | 871.477 [864.819; 878.134] | 0.466 | 2,185 |
| B2-Semi / UCB1 | 16,686.640 [16,673.613; 16,699.667] | 413.360 [400.333; 426.387] | 0.918 | 745 |
| B2-Semi / SW-UCB Wref | 16,052.560 [16,043.492; 16,061.628] | 1,047.440 [1,038.372; 1,056.508] | 0.791 | 1,809 |
| B2-Semi / SW-UCB Wlong | 16,377.040 [16,368.985; 16,385.095] | 722.960 [714.905; 731.015] | 0.835 | 1,229 |
| B2-Partial / UCB1 | 16,351.408 [16,334.540; 16,368.276] | 748.592 [731.724; 765.460] | 0.853 | 1,024 |
| B2-Partial / SW-UCB Wref | 14,986.465 [14,965.711; 15,007.219] | 2,113.535 [2,092.781; 2,134.289] | 0.653 | 2,336 |

Las diferencias pareadas de regret (primera configuración menos segunda)
fueron: SW-UCB menos UCB1 `+499.453` en B1, IC `[489.227,509.680]`;
`+634.080` en B2-Semi, IC `[621.808,646.352]`; y `+1,364.943` en
B2-Partial, IC `[1,338.838,1,391.048]`. El efecto de Wlong frente a Wref
en B2-Semi fue `−324.480` de regret, IC `[-333.826,-315.134]`.
B2-Semi frente a B2-Partial redujo regret en `335.232` para UCB1
(IC `[-349.492,-320.972]`, contraste Semi−Partial) y en `1,066.095`
para SW-UCB (IC `[-1,089.358,-1,042.832]`). Estas son diferencias de
protocolos cerrados; después de la intervención cambian las asignaciones,
exposiciones e historiales, así que no identifican un efecto informativo
instantáneo separado de sus mediadores.

En los tres tramos, SW-UCB Wref acumuló más regret que UCB1. Diferencia
SW−UCB por tramos (IC 95% pareado):

| Modalidad | Base previa | Transitorio | Base posterior |
|---|---:|---:|---:|
| B1 | +144.47 [141.45;147.48] | +145.63 [134.07;157.18] | +209.36 [197.14;221.57] |
| B2-Semi | +175.78 [171.36;180.21] | +123.28 [120.02;126.55] | +335.01 [323.06;346.97] |
| B2-Partial | +304.73 [295.60;313.86] | +220.25 [213.34;227.15] | +839.97 [818.64;861.30] |

Sin embargo, en las ventanas post-cambio predefinidas, SW-UCB tuvo menor
regret que UCB1 en B1: `10.58` frente a `16.75` en `[3000,3200)` y `29.84`
frente a `80.17` en `[5000,5200)`. En B2-Semi las cifras fueron `10.12`
frente a `8.76` y `36.81` frente a `63.52`. Recuperación media a 20 decisiones
óptimas consecutivas en B2-Semi: SW-UCB `63.5` y `121.8` periodos tras los
dos cambios, frente a UCB1 `125.3` y `169.8`. Es adaptación local más rápida,
no mayor rendimiento acumulado.

El total de feedback fue 10,000 observaciones por trayectoria en B1 y
B2-Partial, y 30,000 en B2-Semi. En B2-Semi, por ejemplo, UCB1 concentró
feedback en las aristas de los matchings dominantes (promedios por seed:
`(0,0)=7441`, `(1,1)=9854`, `(2,2)=7388`; las aristas cambiantes `(0,2)` y
`(2,0)` recibieron aproximadamente 2,485 y 2,540). El flujo completo por
pareja y periodo se conserva en las trazas. El diagnóstico de bonus mide la
frecuencia muestreada en que el matching/pareja elegida por índices difiere
de la elección por medias actuales: 0.240 para B2-Semi UCB1, 0.264 para
SW-UCB Wref y 0.294 para Wlong. Esta discrepancia mide influencia del bonus,
no exploración óptima ni regret causal. SW-UCB también mostró menor MSE de
estimación en las muestras diagnósticas que UCB1, pese a su peor reward; por
tanto, exactitud de estimación y calidad de decisión no son equivalentes.

El tiempo medio de cálculo por seed fue aproximadamente `0.21–0.25 s` en B1
y `0.68–0.76 s` en B2 en este equipo; dato descriptivo, no evidencia de
escalabilidad. La campaña tardó `141.3 s` en total.

### Evaluación de H1–H5

- **H1, cantidad/distribución de feedback — apoyada como efecto del protocolo,
  no como mecanismo causal aislado.** Semi superó a Partial para ambos
  estimadores, con diferencias pareadas estrechas; Semi entrega tres veces
  más observaciones globales. La selección de aristas y los historiales
  posteriores divergen, por lo que no se atribuye toda la diferencia a una
  sola observación adicional por periodo.
- **H2, descarte de observaciones útiles — parcialmente apoyada.** En las
  fases base SW-UCB Wref rindió peor que el historial completo; Wlong redujo
  regret frente a Wref en los tres regímenes B2-Semi (diferencias de regret
  long−ref: `−95.29`, `−55.68`, `−173.51`; IC pareados excluyen cero).
  Pero ventana y término temporal de confianza cambian conjuntamente, y la
  MSE de SW fue menor; no se identifica un efecto puro de memoria.
- **H3, oscilaciones de índices y cambios subóptimos — compatible, no
  demostrado causalmente.** SW-UCB hizo muchos más cambios de acción y tuvo
  peor rendimiento acumulado; los cambios no tienen coste explícito en el
  reward. Tras los breakpoints, SW recuperó antes en varias comparaciones.
  La actividad de cambio explica descriptivamente volatilidad, no demuestra
  que cada cambio cause regret.
- **H4, sensibilidad a memoria/exploración — apoyada parcialmente para
  memoria.** La ventana larga mejora claramente frente a Wref, pero sigue
  por debajo de UCB1 en reward total. La influencia observada del bonus
  permite diagnosticar decisiones alteradas; no se variaron coeficientes,
  así que el papel cuantitativo de la exploración sigue sin identificar.
- **H5, márgenes entre matchings — no resuelta.** El margen cambia de `0.45`
  a `0.05`, pero solo hay dos matrices enlazadas por el mismo cambio de una
  arista. No se manipuló el margen manteniendo constantes los demás factores.
  El regret depende también de qué matching subóptimo se elige, no solo del
  gap al segundo mejor.

### Interpretación, límites y decisión siguiente

En el sistema común E1, UCB1 superó a SW-UCB en las tres modalidades; la
ventana larga mejoró SW-UCB, pero no cambió el ganador. Por tanto, la ventaja
SW-UCB del antecedente B1 de tres brazos no se reproduce en B1-E1, que tiene
nueve parejas candidatas. E1 no reproduce aquel bandit: cambian brazos,
instancia, calibración y protocolo. Tampoco identifica por qué surgió la
clasificación histórica. La ventaja acumulada de UCB1 en E1 no demuestra
superioridad general; el SW-UCB más corto mostró recuperación local más
rápida tras varios cambios. Los regrets absolutos B1/B2 no se comparan.

La especificación E1.1 se respetó. La elección de `PairwiseBanditEstimator`
implica la escala UCB1/SW-UCB predeclarada `xi=2`; es una composición HLS de
índices por pareja con matching y no hereda automáticamente garantías
single-play publicadas. El B1 de nueve parejas tampoco es reproducción exacta
del antecedente B1 de tres brazos. No hubo fuga de medias reales ni feedback
contrafactual. La evidencia es sintética y específica de estas matrices,
semillas, horizonte y reglas de calibración. Los intervalos cuantifican
variación entre 30 semillas, no incertidumbre sobre el modelo ni validez
externa.

**Recomendación concreta:** no ampliar la campaña ni ajustar ventanas ahora.
Antes de otra evaluación, decidir si se necesita una reconciliación acotada
del antecedente B1 de tres brazos con el B1-E1 de nueve parejas, verificando
sus diferencias exactas de brazos, inicialización y coeficientes. Hasta esa
decisión, la causa del cambio de ranking entre estudios queda **no resuelta**.

### Artefactos y verificaciones

- `experiments/run_hls_s3b_e1.py` — runner reproducible.
- `src/hls/nonstationary_assignment.py` — aceleración exacta por sumas
  prefijas, sin cambio de las ecuaciones del estimador.
- `tests/test_hls_s3b_e1.py` — oráculos, calibración, ecuaciones, información,
  consistencia reward/regret y reproducibilidad.
- Resultados compactos: `results/experiments/hls_s3b_e1/results.json` y
  `results/experiments/hls_s3b_e1/period_traces.jsonl.gz` (30 semillas ×
  10,000 periodos × 7 configuraciones).
- Pruebas focalizadas: `PYTHONPATH=src:. pytest -q tests/test_hls_s3b_e1.py
  tests/test_hls_s3b_nonstationary_assignment.py
  tests/test_hls_s3b_discounted_ucb.py` — **18 passed**. La campaña completa
  finalizó para las 30 semillas. La reproducción determinista se comprobó
  repitiendo una semilla en prueba; los streams de potenciales y de selección
  parcial son independientes y emparejados como especifica E1.1.
- Hitos E1.2–E1.6: completados para el alcance anterior. E1.7: la causa
  histórica sigue pendiente; no se autorizan otras campañas por esta entrada.

## Reconciliación S3b: B1 histórico de tres brazos frente a B1-E1 — 21/10/2026

**Objetivo.** Contrastar los artefactos existentes del antecedente de selección
individual y de B1-E1, sin ejecutar experimentos ni alterar algoritmos o
resultados. Fuentes inspeccionadas: `experiments/run_hls_s3b_discounted_ucb.py`,
`experiments/run_hls_s3b_e1.py`,
`src/hls/nonstationary_assignment.py`,
`results/experiments/hls_s3b_discounted_ucb/results.json` y
`results/experiments/hls_s3b_e1/results.json`.

### Hechos comprobados

| Dimensión | B1 histórico (reproducción de tres brazos) | B1-E1 (selección de una pareja) |
|---|---|---|
| Espacio de acciones | 3 brazos abstractos; se elige exactamente uno. No son parejas de un sistema 3×3. | 9 parejas agente–tarea de una matriz 3×3; se elige exactamente una. Sigue siendo selección individual, no matching. |
| Medias Bernoulli | `(0.5, 0.3, 0.4)` antes y después, salvo el brazo 3 que sube a `0.9` durante `[3000,5000)`. | Matriz base `((.8,.05,.05),(.05,.8,.05),(.4,.05,.1))`; durante `[3000,5000)`, `(2,0)` cambia de `.4` a `.9`. |
| Cambio y relevancia | Un brazo pasa de estar `.1` por debajo del mejor estable (`.5`) a ser el mejor (`.9`), y luego revierte. | La mejor pareja pasa de `(0,0)` con `.8` a `(2,0)` con `.9`, y revierte. El espacio de selección y los gaps entre alternativas son diferentes. |
| Horizonte y semillas | 10 000 periodos; 50 semillas `8100–8149`. | 10 000 periodos; 30 semillas `8200–8229`. |
| Inicialización | Primeros 3 periodos fuerzan una observación por brazo; esos periodos cuentan en reward y regret. Después hay una observación por periodo. | Primeros 9 periodos fuerzan una observación por cada pareja; cuentan en reward y regret. Después hay una observación por periodo en B1. |
| Índice UCB | `media + B·sqrt(xi·log(t)/n)`, con `B=1`, `xi=.5` (equivale a bonus `sqrt(.5 log(t)/n)`, salvo el suelo numérico `t≥2`). | `media + sqrt(2·log(max(2,t+1))/n)` mediante `PairwiseBanditEstimator`; el bonus es dos veces el histórico para el mismo `t,n`. |
| Índice SW-UCB | Misma escala histórica `xi=.5`; usa observaciones dentro de ventana temporal global y término `log(max(2,min(t,W)))`. | `PairwiseBanditEstimator`, ventana en periodos globales, `xi=2`; mismo ancho de ventana de referencia, `W=1214`, pero término de confianza de mayor amplitud. |
| Oráculo y regret | Oráculo dinámico elige el brazo con mayor media en cada periodo; pseudo-regret suma `max_i μ_i(t) − μ_{seleccionado}(t)`. | Oráculo B1 elige la pareja de mayor media en cada periodo; pseudo-regret usa la misma forma, pero sobre otro conjunto y otras medias. |
| Feedback y aleatoriedad | Feedback Bernoulli solo del brazo elegido. Potenciales comunes entre políticas por semilla, generados con `random.Random(seed)` en orden periodo–brazo. | Feedback Bernoulli solo de la pareja elegida. Potenciales comunes entre configuraciones por semilla, con `random.Random(seed XOR 0xD0C0A7)` en orden periodo–agente–tarea. Semillas y streams no coinciden con el antecedente. |
| Resultado relevante | UCB1 regret `669.146`; SW-UCB regret `288.092`; SW supera a UCB1 en esta instancia. | UCB1 reward `7827.977`, regret `372.023`; SW-UCB-Wref reward `7328.523`, regret `871.477`; UCB1 supera a SW en B1-E1. |

Ambos artefactos usan recompensas Bernoulli y pseudo-regret esperado respecto
al oráculo de su propio problema. El antecedente empleó `xi=.5` para UCB1 y
SW-UCB. B1-E1 predeclaró `xi=2` para ambos índices de confianza; no fue una
modificación posterior a observar resultados. El ancho de ventana de
referencia coincide (`1214`), pero no coincide la confianza que acompaña a la
ventana. B1-E1 además comparó una ventana larga (`2428`), sin equivalente en
el B1 histórico. Los flujos comunes emparejan políticas dentro de cada
estudio, pero no emparejan episodios entre estudios.

### Qué permiten concluir los artefactos

- **Hecho observado:** en el protocolo histórico de tres brazos SW-UCB tuvo
  menos pseudo-regret que UCB1; en el nuevo protocolo de selección individual
  de nueve parejas ocurrió la clasificación inversa. B1-E1 no es reproducción
  del B1 histórico.
- **Hecho observado:** la inversión ya aparece al comparar dos experimentos
  que son ambos selección individual. Por tanto, no puede atribuirse a un
  contraste B1 frente a B2/matching basándose en estos dos resultados.
- **Interpretación compatible, no causalmente aislada:** el número y
  distribución de candidatos, las medias/gaps, el número de rondas de
  inicialización y, especialmente, el doble de amplitud del bonus en E1
  pueden cambiar la trayectoria de selección y el ranking de UCB1/SW-UCB.
  Que `W=1214` coincida no elimina la diferencia en el índice SW.
- **No concluible:** los artefactos no identifican cuál diferencia produjo
  la inversión, ni permiten afirmar que la modalidad organizativa cause el
  cambio. Tampoco permiten comparar directamente los regrets absolutos,
  pues los oráculos, medias y escalas de oportunidad son propios de cada
  instancia. La comparación UCB1–SW dentro de cada artefacto sí corresponde
  a sus respectivas semillas y protocolo, pero no es un contraste pareado
  entre estudios.

### Una comparación puente propuesta (no ejecutada)

Si el PI considera necesario identificar una causa concreta, la comparación
mínima recomendada es un **cruce de escala de confianza en el B1 histórico de
tres brazos**: conservar exactamente sus medias, cambios, horizonte,
inicialización de tres pulls, potenciales Bernoulli y semillas; evaluar UCB1
y SW-UCB con la escala histórica `xi=.5` y con la escala E1 `xi=2`, usando
los mismos flujos potenciales en las cuatro celdas. Esto aísla si el cambio de
escala, por sí solo, puede cambiar la clasificación en el benchmark histórico.
No resolvería por sí solo los efectos del conjunto de nueve parejas ni
explicaría toda la diferencia entre instancias; si el ranking no cambia,
esas diferencias estructurales y de calibración seguirían abiertas. No se
autoriza ni ejecuta esta comparación en esta entrada.

**Estado:** reconciliación documental completada; causa de la inversión
histórica **no identificada**. No se modificaron algoritmos, resultados ni
protocolos, y no se ejecutaron nuevas campañas.

## S3b — Control factorial del coeficiente de exploración en B1 — 21/10/2026

**Autorización:** GO para el control focalizado de `xi`. **Pregunta:** ¿cambiar
`xi` de `0.5` a `2` cambia la clasificación UCB1/SW-UCB dentro de la instancia
histórica de tres brazos? La reconciliación previa documentó que B1-E1 tiene
nueve parejas y otros parámetros; aquí se mantuvo exclusivamente el B1
histórico.

### Diseño y verificaciones

- Instancia: medias Bernoulli `(0.5,0.3,0.4)`; brazo 3 cambia a `0.9` en
  periodos `[3000,5000)` y vuelve a `0.4`; horizonte 10 000; `W=1214`.
- Cuatro celdas: UCB1 y SW-UCB, cada uno con `xi∈{0.5,2}`. El peso de
  recompensa es `B=1`. En cada semilla, las cuatro celdas usan exactamente
  los mismos potenciales Bernoulli, generados con `random.Random(seed)` en
  orden periodo–brazo; se conservaron las 50 semillas históricas `8100–8149`.
- Inicialización intacta: periodos 0, 1 y 2 fuerzan un pull de los brazos
  0, 1 y 2 respectivamente; esos periodos cuentan en reward y regret. No
  hubo ajuste de ventana, cambio de recompensas ni modificación de la regla
  de actualización.
- Índices con tiempo global `t` y observaciones `n`: UCB1 usa
  `mean+B·sqrt(xi·log(max(2,t+1))/n)`; SW-UCB sustituye la media por la media
  de las observaciones en la ventana global y usa
  `B·sqrt(xi·log(max(2,min(t+1,W)))/n)`. La amplitud del bonus escala como
  `sqrt(xi)`: cambiar `xi=.5` por `xi=2` duplica el bonus para iguales `t,n`.
  Se comprobó numéricamente esa razón `2.0`.
- La celda `xi=.5` reprodujo **por semilla** las recompensas y regrets
  esperados UCB1 y SW-UCB del artefacto histórico. Es una comprobación de
  consistencia del runner y de las realizaciones, no una nueva validación de
  las garantías teóricas publicadas. La parametrización `xi=.5` se conserva
  como la de la simulación del artículo; la prueba `xi=2` es un control de
  sensibilidad y no se presenta como reproducción publicada.
- Comando reproducible: `PYTHONPATH=src:. python
  experiments/run_hls_s3b_b1_xi_control.py`. Verificación focalizada:
  `PYTHONPATH=src:. pytest -q tests/test_hls_s3b_discounted_ucb.py` — **5
  passed**. Salida independiente:
  `results/experiments/hls_s3b_b1_xi_control/results.json`.

### Resultados

Reward esperado y pseudo-regret son complementarios: el oráculo acumula
`5800` de reward esperado en esta instancia. Los IC son t-intervalos pareados
entre semillas para las diferencias y 95% CI entre semillas para las celdas.

| Configuración | Reward esperado | Reward Bernoulli realizado | Pseudo-regret esperado | Fracción de decisiones óptimas |
|---|---:|---:|---:|---:|
| UCB1, `xi=.5` | 5130.854 | 5141.14 | 669.146 | 0.4881 |
| SW-UCB, `xi=.5` | 5511.908 | 5507.48 | 288.092 | 0.7961 |
| UCB1, `xi=2` | 5204.776 | 5214.02 | 595.224 | 0.4464 |
| SW-UCB, `xi=2` | 5369.266 | 5367.16 | 430.734 | 0.6938 |

Contrastes pareados positivos de reward (`SW − UCB`) equivalen a contrastes
negativos de regret:

| Contraste | Diferencia en reward esperado (IC 95%) | Diferencia en regret (IC 95%) |
|---|---:|---:|
| SW-UCB − UCB1, `xi=.5` | `+381.054` (`[342.807,419.301]`) | `−381.054` (`[−419.301,−342.807]`) |
| SW-UCB − UCB1, `xi=2` | `+164.490` (`[153.016,175.964]`) | `−164.490` (`[−175.964,−153.016]`) |
| UCB1, `xi=2 − .5` | `+73.922` (`[45.042,102.802]`) | `−73.922` (`[−102.802,−45.042]`) |
| SW-UCB, `xi=2 − .5` | `−142.642` (`[−161.615,−123.669]`) | `+142.642` (`[123.669,161.615]`) |

La atenuación de la ventaja SW-UCB al subir `xi` fue `216.564` puntos de
reward (`IC 95% [181.427,251.701]`; equivalente a +216.564 regret relativo).
En fase pre-cambio, regrets medios fueron UCB/SW `34.994/66.172` con `xi=.5`
y `90.018/137.094` con `xi=2`. En el régimen transitorio fueron
`199.760/63.332` y `24.860/49.060`, respectivamente; tras la reversión,
`434.392/158.588` y `480.346/244.580`. Los resultados por régimen son
descriptivos de estas políticas adaptativas y no equivalen a efectos
causales aislados por periodo.

Como recuperación se definieron 20 decisiones óptimas consecutivas, buscando
hasta 1000 periodos posteriores a cada breakpoint. Los lags medios para esa
recuperación tras el primer breakpoint, UCB/SW, fueron `383.88/125.80`
(`xi=.5`) y `61.68/23.86` (`xi=2`).
Tras la reversión fueron `900.90/618.14` con `xi=.5`, y `>1000` en las 50
semillas para UCB1 frente a `465.94` para SW-UCB con `xi=2`; `>1000` está
censurado por el límite de búsqueda, no es un lag exacto.

### Interpretación y límites

- **Resultado:** SW-UCB mantuvo menor regret que UCB1 con ambos coeficientes;
  la clasificación no se invirtió en el B1 histórico. Por tanto, `xi` no
  explica la inversión como un cambio de ganador dentro de esta instancia.
- **Sensibilidad demostrada aquí:** al pasar a `xi=2`, el regret de UCB1
  bajó en `73.922`, mientras que el de SW-UCB subió en `142.642`; la ventaja
  de SW sobre UCB se redujo, pero siguió siendo positiva. El coeficiente
  explica una parte cuantificable de la diferencia de magnitud entre las dos
  configuraciones de `xi`, no la inversión de clasificación.
- **No concluible:** esto no determina por qué B1-E1 (`xi=2`) favoreció a
  UCB1. Persisten diferencias de número y distribución de brazos/parejas,
  medias y gaps, calentamiento de 9 frente a 3 periodos, semillas y streams.
  Tampoco puede atribuirse a matching: ambos B1 son selección individual.
- La recompensa Bernoulli realizada es estocástica; el regret reportado se
  calcula con medias verdaderas conocidas solo al evaluador. Los intervalos
  miden variación entre estas 50 semillas, no incertidumbre del modelo ni
  generalización a otros cambios.

**Siguiente paso único recomendado, no autorizado ni ejecutado:** si se
requiere explicar qué queda del cambio de ranking más allá de `xi`, hacer un
puente B1 armonizado entre el benchmark histórico de 3 brazos y las 9 parejas
de E1, con una implementación de estimador, `xi`, horizonte, reglas de
inicialización por candidato y protocolo de semillas/potenciales comunes
predeclarados. La comparación debe limitarse a UCB1 frente a SW-UCB dentro de
cada conjunto de acciones; no comparar regrets absolutos entre los dos
oráculos. Este puente aún agruparía diferencias inherentes de medias y tamaño
del conjunto y no justificaría por sí solo una atribución universal a la
modalidad.

## S3b — Factorial mínimo de cambios de competencias × oportunidades de observación — 21/10/2026

**Decisión del PI:** GO. **Prioridad:** ejecución experimental. Esta entrada
registra la reformulación aprobada de S3b: estudiar cuándo es útil conservar
historial frente a descontarlo, mediante el ciclo organización → observaciones
→ estimación → organización. A diferencia de S4, las asignaciones no alteran
las competencias reales; solo condicionan qué feedback puede llegar a la
política.

### Diseño ejecutado y alcance

Se reutilizaron las matrices y componentes de S3b-E1. Se eligió B2-Semi como
modalidad común: matching completo 3×3, una asignación por agente/tarea y tres
recompensas individuales ejecutadas que contribuyen al reward colectivo. Las
condiciones de feedback no cambian las asignaciones factibles, la demanda, el
reward ni el oráculo.

| Factor | Nivel 1 | Nivel 2 |
|---|---|---|
| Frecuencia A | Infrecuente: permanencia `τc=2500`; 3 transiciones en 10 000 periodos | Frecuente: `τc=500`; 19 transiciones |
| Oportunidad B | Alta: cada pareja-periodo tiene máscara exógena disponible con probabilidad `p=.75` | Baja: `p=.25` |

Las matrices alternan determinísticamente entre la matriz base de E1 y la
transitoria: solo `(2,0)` cambia de `.4` a `.9` y vuelve, con amplitud constante
`.5`. Se conserva la matriz inicial; los mismos dos estados cambian el
matching óptimo: base `((0,0),(1,1),(2,2))`, valor `1.70`, margen al segundo
matching `.45`; transitorio `((0,2),(1,1),(2,0))`, valor `1.75`, margen `.05`.
El horizonte, las capacidades, el reward Bernoulli y las seis asignaciones
factibles son iguales en todas las celdas. Se usaron 30 semillas emparejadas
`8200–8229`, calibración común E1 de nueve periodos y el mismo solver/oráculo
exacto para las dos políticas.

Las oportunidades son máscaras Bernoulli exógenas por pareja-periodo,
precalculadas con un stream independiente del reward y compartidas entre
políticas y niveles (umbrales anidados `.25/.75`). La política no ve máscaras
antes de asignar. La recompensa de cada pareja ejecutada cuenta aunque su
feedback no esté disponible; el estimador solo recibe feedback de parejas
ejecutadas cuya máscara lo permite. UCB1 y SW-UCB usan la formulación de
`PairwiseBanditEstimator`, coeficiente efectivo común `xi=2`, ventana global
fija `W=1214` para SW-UCB y el matching exacto. No se cambió ninguna ecuación.

**Descriptor de información:** `p·τc` es el número esperado de oportunidades
de sensor por pareja durante una estabilidad (alta/baja: `1875/625` con
`τc=2500`; `375/125` con `τc=500`). No es `rho_ik` observado ni predictor de
reward. La tasa efectiva depende además de si la política ejecuta la pareja.
Se registraron por pareja oportunidades, ejecuciones, feedback obtenido,
tasas, edad, errores de estimación, observaciones por régimen y cuántas
observaciones vigentes, compatibles de regímenes anteriores o incompatibles
permanecen en la memoria. La competencia real solo se usa en reward, oráculo y
diagnósticos posteriores; no se expone a los estimadores.

**Estatus de hipótesis:** los cuatro niveles y parámetros se fijaron antes de
la campaña, pero no se congeló por escrito un criterio direccional de
rechazo antes de ejecutarla. En consecuencia, los contrastes se reportan con
IC pareados y el análisis direccional se trata como exploratorio, no como una
prueba confirmatoria prerregistrada. La hipótesis operacional examinada fue
que, con feedback alto, los cambios frecuentes podrían mejorar SW-UCB
relativamente a UCB1 más que con feedback bajo; su criterio era la
diferencia-en-diferencias de `regret(SW)−regret(UCB)`.

### Resultados de rendimiento

El oráculo esperado es `17 250` en las cuatro celdas: cada frecuencia dedica
5 000 periodos a cada matriz. La tabla presenta reward esperado y regret
esperado medios por semilla; entre corchetes, IC 95% de cada media. `Δopt`
es la fracción de decisiones que coincide exactamente con el matching
óptimo; cambios es el promedio de cambios de matching entre periodos. Reward
Bernoulli realizado también se conserva en el JSON.

| Cambios / oportunidad | Política | Reward esperado [IC95] | Regret [IC95] | `Δopt` | Cambios de matching |
|---|---|---:|---:|---:|---:|
| Infrecuente / alta | UCB1 | 16 822.00 [16 811.97, 16 832.04] | 428.00 [417.96, 438.03] | .863 | 812 |
| Infrecuente / alta | SW-UCB | 16 088.18 [16 078.57, 16 097.80] | 1 161.82 [1 152.20, 1 171.43] | .669 | 1 828 |
| Infrecuente / baja | UCB1 | 16 432.12 [16 412.52, 16 451.71] | 817.88 [798.29, 837.48] | .729 | 824 |
| Infrecuente / baja | SW-UCB | 15 065.04 [15 038.47, 15 091.62] | 2 184.96 [2 158.38, 2 211.53] | .559 | 1 800 |
| Frecuente / alta | UCB1 | 16 722.90 [16 714.30, 16 731.51] | 527.10 [518.49, 535.70] | .756 | 1 042 |
| Frecuente / alta | SW-UCB | 15 967.20 [15 956.69, 15 977.70] | 1 282.80 [1 272.30, 1 293.31] | .657 | 2 322 |
| Frecuente / baja | UCB1 | 16 326.30 [16 307.81, 16 344.80] | 923.70 [905.20, 942.19] | .653 | 955 |
| Frecuente / baja | SW-UCB | 14 964.38 [14 939.13, 14 989.64] | 2 285.62 [2 260.36, 2 310.87] | .542 | 2 048 |

Diferencias pareadas de regret `SW-UCB − UCB1` (positivo desfavorece SW-UCB):

| Celda | Diferencia de regret (IC 95%) |
|---|---:|
| Infrecuente / alta | `+733.82` `[+720.79,+746.85]` |
| Infrecuente / baja | `+1 367.07` `[+1 336.82,+1 397.32]` |
| Frecuente / alta | `+755.71` `[+744.75,+766.66]` |
| Frecuente / baja | `+1 361.92` `[+1 333.93,+1 389.91]` |

Al bajar oportunidades de altas a bajas, el regret aumentó para ambas
políticas: UCB1 `+389.89` (IC `[369.54,410.24]`) y SW-UCB `+1 023.14`
(`[993.55,1 052.73]`) en cambios infrecuentes; UCB1 `+396.60`
(`[377.24,415.96]`) y SW-UCB `+1 002.81` (`[980.44,1 025.19]`) en cambios
frecuentes. Al aumentar la frecuencia, el regret UCB1 subió `99.10`
(`[88.83,109.37]`) con oportunidades altas y `105.81` (`[85.33,126.29]`)
con bajas; el regret SW-UCB subió `120.99` (`[107.62,134.36]`) y `100.66`
(`[65.64,135.68]`), respectivamente.

Contrastes factoriales sobre el diferencial de regret SW-UCB menos UCB1:

- Efecto de frecuencia con oportunidades altas: `+21.89` (IC95
  `[+5.04,+38.74]`), desfavorable relativamente a SW-UCB.
- Efecto de frecuencia con oportunidades bajas: `−5.15` (IC95
  `[−45.47,+35.16]`), no concluyente.
- Diferencia-en-diferencias frecuencia × disponibilidad: `+27.04` (IC95
  `[−17.58,+71.66]`), compatible con cero para regret; no se identifica una
  interacción de rendimiento acumulado. En tasa de matching óptimo el
  contraste fue `+.0351` (IC95 `[.0190,.0512]`), señal descriptiva distinta
  que no se tradujo en una interacción concluyente de regret.

### Información, estimación y organización

- En el par alterado y decisivo `(2,0)`, el número esperado de oportunidades
  por intervalo estable era `1875/625` con cambios infrecuentes y `375/125`
  con frecuentes (alta/baja). Pero el número medio efectivo de observaciones
  por episodio del estado base/transitorio (UCB1/SW-UCB) fue, respectivamente:
  `190/253` y `1608/1081`; `90/134` y `421/332`; `47/72` y `250/227`; `22/33`
  y `69/68`. La diferencia entre oportunidades y observaciones muestra el
  papel de la asignación: `(2,0)` apenas se ejecuta en base, pero es parte del
  matching óptimo transitorio. Los agregados completos de las nueve parejas
  están en el artefacto.
- La reducción de oportunidades disminuyó observaciones de las parejas
  críticas y empeoró el reward de ambas políticas; el deterioro medio fue
  mayor para SW-UCB. La frecuencia por sí sola también elevó regret en ambas.
  Estas son comparaciones del efecto total del tratamiento sobre la política
  cerrada; cantidad de feedback, estimaciones y decisiones median ese efecto y
  no son causas aisladas.
- Error cuadrático medio temporal de la media estimada en `(2,0)` fue menor
  para SW-UCB en las cuatro celdas (infrecuente alta `.0181` frente a UCB
  `.0554`; infrecuente baja `.0217` frente a `.0550`; frecuente alta `.0666`
  frente a `.0793`; frecuente baja `.0606` frente a `.0714`). El MSE promedio
  sobre nueve pares también fue menor para SW en cada celda. Sin embargo,
  SW-UCB tuvo menor tasa de matching óptimo, más cambios de matching y mayor
  regret. Por tanto, MSE agregado no basta para explicar calidad de decisión;
  son posibles errores concentrados en alternativas críticas, interacción con
  los índices de confianza y la selección combinatoria. Esta causa no queda
  aislada por el factorial.
- La recurrencia hace que observaciones antiguas de `(2,0)` vuelvan a ser
  compatibles cuando retorna el estado que las generó. Al final del horizonte
  el régimen vuelve a ser transitorio: con cambios infrecuentes/oportunidades
  altas UCB1 conserva en promedio `3216` observaciones compatibles y `380`
  incompatibles, mientras SW-UCB conserva `537` compatibles y ninguna
  incompatible; con cambios frecuentes/alta, UCB1 conserva `2505/473` y
  SW-UCB `331/72`. UCB1 guarda más evidencia útil recurrente, pero también
  más evidencia obsoleta. SW-UCB filtra más datos incompatibles, aunque con
  `W=1214` puede descartar observaciones compatibles de retornos anteriores.
  No se puede llamar inútil a todo el historial ni atribuirle por sí solo la
  clasificación.
- En esta campaña SW-UCB no recuperó más rápido que UCB1 con la métrica de 20
  matchings óptimos consecutivos: lags medios observados tras el primer cambio
  fueron UCB/SW `98/152`, `98/161`, `67/121` y `82/131` para las celdas en el
  orden de la tabla. En el régimen frecuente hubo eventos sin 20 aciertos
  consecutivos antes del siguiente cambio o del límite de búsqueda; están
  contabilizados como no recuperación, no como lags exactos.
- El número de cambios de matching no implica un coste de conmutación: tal
  coste no forma parte de reward. Es una medida de estabilidad organizativa.

### Hechos, hipótesis y límites

**Hechos observados:** UCB1 tuvo menor regret que SW-UCB en las cuatro celdas,
con IC pareados que excluyen cero. Más oportunidades mejoraron ambas políticas;
menos frecuencia de cambios también redujo regret. La interacción entre
frecuencia y disponibilidad para regret no quedó identificada. El oráculo
esperado permaneció idéntico entre niveles de disponibilidad para cada
trayectoria.

**Hipótesis debilitada/no resuelta:** no se observó la predicción direccional
exploratoria de que los cambios frecuentes con alto feedback mejorarían SW-UCB
relativamente más; el efecto puntual fue contrario y la diferencia-en-
diferencias incluyó cero. Los datos sí muestran que disponibilidad baja
perjudica especialmente a SW-UCB en este sistema, pero no distinguen por sí
solos estimación, exploración, selección de parejas y matching.

**Limitaciones/protocolo:** diseño sintético con dos matrices y dos niveles;
solo una pareja cambia y el margen entre matchings es diferente por régimen.
La disponibilidad aleatoria se aplica uniformemente a parejas, no manipula
directamente una cuota fija de observaciones. La feedback efectiva depende de
la organización. `rho=p·τc` solo describe oportunidades esperadas, mientras
que `rho` efectiva es dependiente de política. Además, aunque los niveles se
fijaron antes de correr, faltó dejar congelado antes de la campaña un criterio
direccional de contraste; inferencias direccionales son exploratorias. Los IC
miden variación de semillas, no incertidumbre del modelo ni validez externa.

Artefactos y validación focalizada:
`experiments/run_hls_s3b_change_observation_factorial.py`,
`tests/test_hls_s3b_change_observation_factorial.py`,
`results/experiments/hls_s3b_change_observation_factorial/results.json` y
`period_traces.jsonl.gz`. Ejecución: `PYTHONPATH=src:. python
experiments/run_hls_s3b_change_observation_factorial.py` (8 celdas, 30 semillas,
tiempo observado ~124 s). Pruebas: `PYTHONPATH=src:. pytest -q
tests/test_hls_s3b_change_observation_factorial.py tests/test_hls_s3b_e1.py
tests/test_hls_s3b_discounted_ucb.py` — **12 passed**. `git diff --check`
pasó.

**Siguiente paso condicionado, no ejecutado:** queda una ambigüedad concreta:
SW-UCB tiene menor MSE medio, pero peores decisiones y regret. Si el PI desea
aislar memoria/índice de la generación endógena de feedback, se propone una
reproducción diagnóstica offline que congele para ambos estimadores la misma
secuencia fechada de observaciones por pareja (por ejemplo, la secuencia
observada de una trayectoria B2-Semi de referencia), y compare medias/índices,
matching inducido, matching óptimo y regret sobre las mismas competencias.
Las actualizaciones incluirían solo el replay común; las decisiones no
determinarían nuevas observaciones. Ese control diagnosticaría el efecto de
los estimadores condicionados a igual información, pero no sería una política
operativa ni estimaría el efecto cerrado de organización → feedback. Requiere
autorización explícita antes de ejecutarse. No se propone otra campaña.

## 2026-10-21 — S3b: replay diagnóstico offline con historial común

**Autorización del PI:** GO con condición de parada. Se implementó el control
offline para separar estimación, índices y matching; no es una evaluación
operativa en bucle cerrado.

**Fuente y validez.** El trace del factorial cambios × oportunidades guarda
asignaciones, máscara de feedback y recompensas por periodo agregadas, pero no
los outcomes Bernoulli individuales por pareja. No se reconstruyeron rewards
no registrados. Como alternativa, fijada antes de analizar los resultados,
se usó el trace B2-Semi/UCB1 de S3b-E1 (`results/experiments/hls_s3b_e1/period_traces.jsonl.gz`):
30 semillas `8200–8229`, 3×3, horizonte 10.000, matrices base/transitoria,
cambios en 3.000 y 5.000, full feedback, `W=1214`, `xi=2`. Esta trayectoria
de origen UCB1 no es una celda del factorial recurrente; toda conclusión es
condicional a dicho historial. Cada periodo entrega a ambos estimadores las
mismas tres observaciones fechadas. Las decisiones replay no afectan eventos
posteriores. Competencias reales se usan solo para evaluación posterior.

Se compararon cuatro reglas diagnósticas: matching por medias e índices de
UCB1 y SW-UCB, siempre con el mismo solver. Fórmulas y reglas de inicialización
son las del estimador existente; en SW-UCB la ventana global es `[t−1214,t)`.
La matriz real determina el óptimo esperado y el regret diagnóstico en cada
periodo.

**Resultados observados: media de 30 semillas; intervalos de regret acumulado
al 95%; contrastes pareados por semilla.**

| Regla | Recompensa esperada [IC95] | Regret esperado [IC95] | Matching óptimo [IC95] |
|---|---:|---:|---:|
| UCB1 por medias | 16.992,927 [16.988,664; 16.997,190] | 107,073 [102,810; 111,336] | 82,32% [81,31; 83,34] |
| UCB1 por índices | 16.689,682 [16.676,637; 16.702,726] | 410,318 [397,274; 423,363] | 91,79% [91,36; 92,23] |
| SW-UCB por medias | 16.990,225 [16.968,353; 17.012,097] | 109,775 [87,903; 131,647] | 88,17% [87,47; 88,86] |
| SW-UCB por índices | 4.007,577 [3.929,858; 4.085,295] | 13.092,423 [13.014,705; 13.170,142] | 10,37% [10,29; 10,44] |

El MSE global fue `0,010394` para UCB1 y `0,027782` para SW-UCB; diferencia
pareada SW−UCB `+0,017388`, IC95 `[+0,016528;+0,018248]`. Así, la ventaja de
MSE global vista en el factorial no persiste en este historial común. En las
tres parejas del matching verdadero, la diferencia fue `+0,000186`, IC95
`[-0,000050;+0,000421]` (no concluyente). La señal depende de pareja y tiempo:
en el régimen transitorio SW-UCB tuvo menor MSE en las parejas del matching
óptimo (`0,00561` vs `0,01104`) y en `(2,0)` durante el horizonte (`0,02263`
vs `0,08685`); tras el retorno al régimen base la ventana retuvo evidencia
transitoria y el MSE de SW-UCB empeoró.

La MSE global de SW-UCB está dominada en parte por parejas poco informadas
que no pertenecían al matching óptimo: para `(1,0)` fue `0,12886` frente a
`0,00339` de UCB1. Esa pareja estuvo fuera de la ventana SW en `61,9%` de
periodos y fue incorporada al matching por índices en promedio `8.139`
periodos por semilla. Así, el promedio global puede ocultar simultáneamente
una mejor estimación temporal de una pareja decisiva y errores grandes en
parejas raras que el índice puede elevar a la asignación.

Por medias, el diferencial acumulado de regret SW−UCB fue `+2,702`, IC95
`[-20,971;+26,374]`; no hay diferencia global distinguible. SW-UCB por medias
mejoró en el régimen transitorio en `33,208` (IC95 `[-38,48;-27,93]`) y
empeoró tras volver al régimen base en `35,910` (IC95 `[+9,83;+61,99]`). El
matching por índices difirió del matching por medias en `22,98%` de periodos
UCB1 y `88,48%` SW-UCB. En el mismo historial congelado, índices menos medias
añadió regret diagnóstico de `303,245` para UCB1 (IC95 `[292,859;313,631]`)
y `12.982,648` para SW-UCB (IC95 `[12.903,031;13.062,362]`). SW-UCB-index
menos UCB1-index fue `12.682,105` (IC95 `[12.600,829;12.763,381]`). Esta es
una diferencia inmediata del criterio de matching, sin consecuencias de
feedback futuro.

**Mecanismo local identificado.** En `PairwiseBanditEstimator.score_matrix`,
una pareja sin observaciones dentro de la ventana SW recibe el índice
optimista finito `2 + sqrt(2 log(max(2,t+1)))`. En el replay, las parejas
`(1,0)` y `(2,1)` no tuvieron observaciones en la ventana durante `61,9%` y
`29,1%` de periodos, respectivamente; `(0,1)`, durante `3,0%`. El índice
SW-UCB añadió `(1,0)` al matching respecto a medias en promedio 8.139
periodos/semilla y `(2,1)` en 5.415. El margen óptimo–segundo matching era
`0,45` en base y `0,05` en el transitorio. Esto demuestra el efecto local de
la ventana vacía/bonus sobre decisiones y regret condicionado a la historia.
No demuestra que explique causalmente el resultado cerrado del factorial:
la observación fijada fue generada por UCB1 y no se adapta a decisiones replay.

**Verificaciones y artefactos.** Se validó que las máscaras coinciden con las
tres parejas ejecutadas y que los outcomes observados suman la recompensa
realizada registrada. Las trazas por periodo están en
`results/experiments/hls_s3b_offline_replay/period_traces.jsonl.gz`; resumen,
regímenes, contrastes e información por semilla en
`results/experiments/hls_s3b_offline_replay/results.json`. Código:
`experiments/run_hls_s3b_offline_replay.py`; pruebas focalizadas:
`tests/test_hls_s3b_offline_replay.py` (**3 passed**). Ejecución reproducible:
`PYTHONPATH=src:. python experiments/run_hls_s3b_offline_replay.py`. No se
modificaron algoritmos ni resultados previos.

**Decisión bajo el criterio del PI:** el replay identifica un mecanismo local
reproducible —parejas sin datos en ventana reciben un índice optimista y
pueden desplazar asignaciones de mayor recompensa—, pero no reproduce la
ventaja global de MSE del factorial ni explica su interacción cerrada entre
organización y feedback. Se registra el mecanismo con ese límite y se devuelve
al PI. No se amplía la investigación ni se cierra S3b como línea general.

## HLS-S3b — Síntesis científica y consolidación del ciclo experimental (21/10/2026)

**Decisión del PI:** CONSOLIDAR RESULTADOS. **Estado:** el ciclo experimental
comparativo UCB1/SW-UCB queda **APARCADO**; S3b permanece **ABIERTA** como línea
general. Esta síntesis integra las entradas anteriores sin tratarlas como un
diseño único ni modificar sus resultados o interpretaciones fechadas.

### Alcance y trazabilidad de la evidencia

La secuencia consolidada es: (i) S3b inicial, 3×3 y 300 periodos, competencias
Bernoulli exógenas con feedback parcial; (ii) evaluación no estacionaria y
revisión metodológica; (iii) reproducción B1 de Garivier–Moulines y traslado
de índices a B2 matching; (iv) E1, que comparó B1 selección de una entre nueve
parejas, B2-Semi y B2-Partial; (v) control factorial de `xi` en el B1 histórico
de tres brazos; (vi) factorial de frecuencia × oportunidades de observación;
y (vii) replay offline sobre una trayectoria congelada. Sus objetivos,
entornos, horizontes, streams aleatorios y modalidades difieren. Por tanto,
las comparaciones entre entradas son síntesis de evidencia, no contrastes
armonizados ni estimaciones causales conjuntas.

Referencias de código, resultados y decisiones que sustentan esta síntesis:

- S3b original y revisión: `experiments/run_hls_s3b_nonstationary_unknown_assignment.py`,
  `src/hls/nonstationary_assignment.py`,
  `results/experiments/hls_s3b_nonstationary_unknown_assignment/results.json`;
  entradas del 20/10/2026 en este registro.
- Reproducción B1 y adaptación a matching B2: `experiments/run_hls_s3b_discounted_ucb.py`,
  `results/experiments/hls_s3b_discounted_ucb/results.json`; entrada del
  21/10/2026 «D-UCB: reproducción de cambios abruptos y adaptación S3b».
- E1: `experiments/run_hls_s3b_e1.py`, `tests/test_hls_s3b_e1.py`,
  `results/experiments/hls_s3b_e1/results.json` y `period_traces.jsonl.gz`;
  entrada «HLS-S3b-E1 ejecutado».
- Sensibilidad a `xi`: `experiments/run_hls_s3b_b1_xi_control.py`,
  `results/experiments/hls_s3b_b1_xi_control/results.json` y su entrada
  cronológica.
- Factorial cambios × oportunidades: `experiments/run_hls_s3b_change_observation_factorial.py`,
  `tests/test_hls_s3b_change_observation_factorial.py`,
  `results/experiments/hls_s3b_change_observation_factorial/results.json` y
  `period_traces.jsonl.gz`.
- Replay: `experiments/run_hls_s3b_offline_replay.py`,
  `tests/test_hls_s3b_offline_replay.py` y los dos artefactos bajo
  `results/experiments/hls_s3b_offline_replay/`.

### C1 — Utilidad de la información histórica

**Hechos observados.** El resultado cambia con escenario, memoria y exploración.
En el S3b inicial de 300 periodos, UCB1 y SW-UCB empataron en S3b-0 (regret
54,16); UCB1 superó a SW-UCB en S3b-1 (75,10 frente a 123,24) y S3b-2
(107,30 frente a 174,16). En otra instancia, la reproducción B1 de tres
brazos obtuvo regret 669,146 para UCB1 y 288,092 para SW-UCB. El cambio de
`xi=.5` a `xi=2` en ese B1 mantuvo a SW-UCB por delante, pero redujo la ventaja:
el diferencial de regret SW−UCB pasó de −381,054 a −164,490. En E1, una ventana
más larga mejoró SW-UCB B2-Semi (regret 722,960 con `W=2428`, frente a
1.047,440 con `W=1214`), sin superar UCB1 (413,360). Estos son resultados de
instancias y protocolos distintos.

La evaluación E1 registró además regret UCB1/SW-UCB de 372,023/871,477 en B1
(nueve parejas), 413,360/1.047,440 en B2-Semi y 748,592/2.113,535 en
B2-Partial; no es una reproducción del B1 histórico. En la reproducción
publicada de D-UCB, los regrets B1 fueron UCB1 669,146, D-UCB 600,720 y
SW-UCB 288,092; en la adaptación B2 con matching fueron 224,403, 2.085,502 y
393,563, respectivamente. B1 y B2 son instancias diferentes: estos valores no
permiten atribuir al matching, por sí solo, la inversión de clasificación ni
comparar regrets absolutos entre modalidades.

En el factorial recurrente, UCB1 obtuvo menor regret en las cuatro celdas.
Reducir oportunidades de feedback perjudicó a ambas políticas, con deterioro
mayor para SW-UCB: +1.023,14 frente a +389,89 en cambios infrecuentes, y
+1.002,81 frente a +396,60 en cambios frecuentes. La diferencia-en-diferencias
frecuencia × disponibilidad fue +27,04, IC95 [−17,58;+71,66], compatible con
cero. La estimación redondeada pedida por el PI (+27, IC95 [−18;+72]) es
coherente con la cifra registrada.

La recurrencia también mostró que observaciones antiguas pueden volver a ser
compatibles al regresar el mismo régimen; SW-UCB, a su vez, puede descartar
observaciones compatibles de ciclos previos. La antigüedad por sí sola no
clasifica una observación como útil o inútil.

**Conclusión respaldada y límite.** La utilidad del historial depende de la
dinámica de competencias, las oportunidades y la secuencia de observaciones
efectivamente obtenidas. La sensibilidad a `xi`, `W` y feedback está
demostrada para estas instancias. No hay base para una regla general de
selección de ventana o memoria óptima; las comparaciones históricas no aíslan
una causa única.

### C2 — Estimación, incertidumbre y organización

**Hechos observados.** En el factorial, SW-UCB tuvo menor MSE diagnóstica
promedio que UCB1 en las cuatro condiciones, pero mayor regret y menor
coincidencia de matching óptimo. En el replay, ambas estimaciones recibieron
idénticas observaciones fechadas de una trayectoria B2-Semi/UCB1 de E1. El
MSE global de SW-UCB fue mayor (0,027782 frente a 0,010394), así que la ventaja
global de MSE del factorial no se reprodujo. Sin embargo, la MSE de la pareja
`(2,0)` fue menor para SW-UCB (0,02263 frente a 0,08685), en particular en el
régimen transitorio. El origen de datos importa: el replay utilizó E1 porque
las trazas factoriales no guardaron outcomes Bernoulli individuales por
pareja; no se reconstruyeron recompensas ausentes.

El regret acumulado diagnóstico en ese replay fue:

| Regla | Regret |
|---|---:|
| UCB1 por medias | 107,073 |
| SW-UCB por medias | 109,775 |
| UCB1 por índices | 410,318 |
| SW-UCB por índices | 13.092,423 |

En el historial congelado, índices frente a medias añadieron 303,245 de
regret diagnóstico en UCB1 y 12.982,648 en SW-UCB. El índice SW-UCB favoreció
parejas sin observaciones recientes; `(1,0)` y `(2,1)` carecieron de datos en
ventana el 61,9% y 29,1% de periodos, respectivamente. El código asigna un
índice optimista finito a una ventana vacía. La comparación medias/índices
identifica directamente el efecto inmediato del criterio de decisión sobre
ese historial fijo.

**Distinciones interpretativas.** Deben mantenerse separados: (a) estimación
de competencias/recompensas —medias y MSE—; (b) representación de incertidumbre
—conteos, antigüedad y ventana—; (c) conversión a índices; (d) optimización
organizativa por matching; y (e) recompensa/regret resultante. MSE y matching
óptimo valoran aspectos diferentes; una media precisa no determina por sí
sola el efecto de un bonus ni el matching elegido. El regret offline no es el
rendimiento de una política desplegada: las decisiones diagnósticas no
modificaron las observaciones futuras y no midieron sus consecuencias de
feedback.

**Límite causal.** El factorial compara políticas cerradas que generan
historiales distintos. El replay controla el historial, pero usa uno originado
por UCB1 y elimina el bucle organización→feedback. Por ello el efecto local
de índices sobre matching/regret sí queda medido; no se cuantifica cuánto de
la diferencia cerrada del factorial se debe causalmente al índice, a la
historia o a su interacción.

### C3 — Retroalimentación entre organización e información

En S3b, la selección determina qué parejas agente–tarea se ejecutan; junto
con la disponibilidad exógena, determina qué recompensas se observan. El
feedback modifica medias, conteos y evidencia conservada; esas cantidades
alimentan índices y siguientes asignaciones. El ciclo documentado es:

```text
Organización → Observaciones → Estimación e incertidumbre
             → Índices de decisión → Organización
```

Esto es distinto de S4: allí las asignaciones pueden modificar competencias
reales futuras mediante MIS-v2; en S3b las competencias reales cambian
exógenamente y la organización modifica qué llega a conocerse, no las
competencias. Ambas dinámicas pueden coexistir en modelos futuros, pero los
resultados aquí no las confunden ni las estudian simultáneamente.

**Implicación para HLS.** La información disponible es parcialmente
consecuencia de la organización. Por tanto, precisión de estimación,
incertidumbre, regla de índice y optimización organizativa deben evaluarse en
conjunto, sin usar la precisión aislada como sustituto de rendimiento
colectivo. Esto es una pauta metodológica sustentada por las comparaciones
descritas, no una teoría general demostrada ni una propuesta de algoritmo
integrado.

### Decisión de continuidad y límites generales

**ESTADO:** ciclo experimental UCB1/SW-UCB de S3b **APARCADO**. **Motivo:** el
replay identificó un mecanismo local verificable —el índice de ventana vacía
puede elevar parejas poco observadas y cambiar el matching en una secuencia
congelada—, pero no reprodujo la ventaja global de MSE del factorial ni
explica causalmente la diferencia en bucle cerrado. La evidencia no justifica
encadenar más controles sobre estas dos políticas. **Alcance:** se aparca esta
secuencia experimental, no S3b como línea científica; S3b permanece **ABIERTA**.
No se inicia automáticamente S4 ni S2b. La siguiente prioridad experimental
queda pendiente de decisión del PI.

En conjunto, no se identifica una regla universal para preferir UCB1 o
SW-UCB. Los resultados son sintéticos, específicos de matrices, cambios,
feedback, inicializaciones, coeficientes y ventanas evaluadas. La composición
de estimadores por pareja con matching no hereda automáticamente garantías
single-play. Las interpretaciones causales quedan limitadas por historiales
endógenos y por el replay condicionado a una trayectoria de origen UCB1.

## 2026-10-21 — S3b: información efectiva y relevancia organizativa

**Autorización del PI:** GO, un análisis acotado. **Pregunta:** si la
distribución de feedback entre parejas organizativamente relevantes aporta
información descriptiva del rendimiento que no recogen el volumen total ni
el MSE global.
No se repitió el factorial, no se ejecutaron simulaciones y no se alteraron
políticas. Se reutilizaron los traces B2-Semi de E1 para UCB1, SW-UCB `W=1214`
y SW-UCB `W=2428`: 30 semillas emparejadas (`8200–8229`), matriz base y
transitoria conocidas por el evaluador, cambios en `t=3000,5000`, horizonte
10.000.

**Definición de relevancia (diagnóstico, no observable por las políticas).**
Para cada periodo, se enumeraron las seis asignaciones completas factibles y
se obtuvo `V*`, el valor del matching de recompensa esperada máxima. La
relevancia actual de una pareja es su pertenencia al matching óptimo. La
sensibilidad se cuantificó sin umbral: para una pareja óptima, pérdida por
exclusión `V* − max_{M: pareja ∉ M} R(M)`; para otra pareja, brecha de entrada
`V* − max_{M: pareja ∈ M} R(M)`. Como resumen de competidores se usó el
matching segundo en valor, no un corte arbitrario de brecha. En el régimen
base, el matching óptimo es la diagonal y aventaja al segundo por `0,45`; en
el transitorio, el óptimo es `((2,0),(1,1),(0,2))`, la diagonal pasa a ser
segunda y la diferencia es solo `0,05`. Así quedan separadas relevancia para
la solución actual y sensibilidad a una alternativa cercana.

**Oportunidad y observación.** En B2-Semi se ejecutan tres parejas completas
y se registra feedback Bernoulli de cada una: hay exactamente 30.000
observaciones efectivas por semilla y política. En esta configuración,
oportunidad de feedback para una pareja ejecutada = observación efectiva; no
hay un canal de observabilidad exógeno independiente de la asignación. La
distribución entre las nueve parejas sí depende de la organización. Una
observación “relevante” se contabiliza como feedback de una pareja del
matching óptimo vigente; la sensibilidad de competidores se informa aparte.
Esto no equivale a medir ganancia de información ni a afirmar que cada
outcome reduzca incertidumbre útil.

**Resultados descriptivos.** La fracción de los tres feedbacks por periodo
que corresponde a aristas del matching óptimo vigente fue:

| Régimen | UCB1 | SW-UCB W=1214 | SW-UCB W=2428 | Δ UCB1 − SW ref. (IC95 pareado) |
|---|---:|---:|---:|---:|
| Base previo, `t=9–2999` | 94,1% [93,9;94,3] | 88,3% [88,0;88,6] | 91,4% [91,2;91,6] | +5,77 pp [5,58;5,96] |
| Transitorio, `t=3000–4999` | 96,1% [94,9;97,4] | 72,2% [71,5;73,0] | 75,6% [74,6;76,7] | +23,87 pp [22,44;25,30] |
| Base posterior, `t=5000–9999` | 94,0% [93,6;94,3] | 88,7% [88,5;88,9] | 92,0% [91,8;92,2] | +5,26 pp [4,92;5,59] |

IC95 de proporciones y diferencias calculados entre semillas, unidad de
replicación `n=30` (t de Student); periodos dentro de una semilla no se tratan
como réplicas independientes. Durante el transitorio las nuevas aristas
óptimas `(0,2),(1,1),(2,0)` recibieron en promedio `1.883, 1.969, 1.914`
observaciones por UCB1 frente a `1.201, 1.867, 1.265` por SW-UCB W=1214.
SW-UCB siguió observando más las aristas del régimen anterior, en particular
`(0,0)` y `(2,2)` (719 y 681 observaciones frente a 86 y 86 de UCB1). La
ventana larga quedó entre ambos. En el régimen base posterior las aristas
diagonales vuelven a ser óptimas; observaciones de ciclos anteriores pueden
volver a ser compatibles, lo que impide llamar “inútil” a toda observación
antigua.

El patrón coincide descriptivamente con el regret por régimen de E1:
UCB1/SW-UCB W=1214/W=2428 obtuvieron `166,43/342,22/246,93` en base previo,
`27,76/151,04/95,35` en el transitorio y `210,92/545,93/372,42` en base
posterior. En total fueron `413,36/1.047,44/722,96`; la diferencia pareada de
regret SW ref. menos UCB1 fue `634,08`, IC95 `[621,81;646,35]` (resultado E1,
no una nueva evaluación). El total de feedback y las restricciones fueron
iguales.

La concentración global de observaciones (HHI sobre nueve parejas) fue
`0,2442/0,2350/0,2472` para esas tres organizaciones, frente a `1/9` bajo
reparto uniforme. SW ref. distribuyó algo menos concentradamente el mismo
volumen, pero tuvo menos feedback sobre aristas óptimas durante el cambio. El
MSE global de los snapshots diagnósticos fue `0,010483` [0,010228;0,010738]
para UCB1, `0,003745` [0,003650;0,003841] para SW ref. y `0,004992`
[0,004843;0,005140] para SW largo: menor MSE global no implicó menor regret.
En el transitorio, MSE diagnóstico restringido a las aristas óptimas fue
`0,01367` para UCB1 y `0,00771` para SW ref., aunque sus regrets medios fueron
`27,76` y `151,04`. Estos MSE son resúmenes de snapshots espaciados por 100
periodos, no mediciones continuas ni pruebas causales.

**Interpretación de H1.** El análisis muestra que la asignación del feedback
entre aristas óptimas aporta una dimensión descriptiva que no muestran el
volumen total (constante aquí) ni el MSE global. La asociación con el
comportamiento organizativo es especialmente visible durante el cambio:
SW-UCB sigue ejecutando con más frecuencia el matching anterior, por lo que
obtiene más feedback de esas aristas, tarda más en cambiar asignaciones y
recoge menos feedback de la nueva solución. Es evidencia descriptiva
compatible con H1,
no una estimación causal de cuánto “explica” la relevancia por encima de la
política. La fracción de observaciones sobre aristas óptimas es endógena y
mecánicamente ligada a las asignaciones y al regret; además, las matrices
reales usadas para puntuar relevancia solo las conoce el evaluador. No se
aislaron la secuencia de observaciones, los índices y la organización.

**USE / KNOW / DEVELOP.** USE: en este S3b la organización aprovecha
competencias exógenas desconocidas al asignar tareas. KNOW: las decisiones
determinan qué feedback llega y, por tanto, qué se puede estimar; precisión,
recencia y relevancia organizativa son dimensiones distintas. DEVELOP: valor
futuro de cambiar competencias reales mediante experiencia; no se estudia en
este ciclo y corresponde al fenómeno endógeno S4. Esta separación es un marco
interpretativo, no un módulo ni una conclusión universal.

**Validación, límites y decisión.** Se reutilizaron traces existentes; se
comprobó que contienen 30 semillas únicas, que cada periodo B2-Semi registra
feedback de las tres parejas ejecutadas, y que el regret recalculado de las
series coincide con los agregados E1 (UCB1 `413,36`, SW ref. `1.047,44`, SW
largo `722,96`). No hubo cambio de código, pruebas nuevas ni simulaciones;
por ello `git diff --check` es la única comprobación de cambio solicitada.
La asociación está limitada a una instancia 3×3, un cambio transitorio y
trazas generadas por cada política; las aristas óptimas y los outcomes son
estocásticos/temporales dentro de trayectorias, no réplicas independientes.
La parte atribuible de forma independiente a “información organizativamente
útil” frente a selección de una asignación ya buena no queda identificada.

**Conclusión:** H1 recibe apoyo exploratorio descriptivo en esta instancia:
con igual volumen, el feedback de las aristas óptimas vigentes fue menor para
SW-UCB —sobre todo durante el cambio— y coincidió con mayor regret. No queda
demostrado que esa distribución añada poder explicativo independiente del
comportamiento de asignación ni que el patrón generalice. **Estado de esta
investigación acotada:** análisis concluido con esta limitación; no se inicia
otra campaña. La prioridad S3b general permanece abierta y cualquier paso
posterior queda sujeto a decisión del PI.

## S3b — Intervención informativa en bucle cerrado (21/10/2026)

**Decisión del PI:** GO, una intervención controlada. **Objetivo:** estimar el
efecto de distribuir una observación adicional por periodo sobre el regret
organizativo de SW-UCB, con el ciclo de decisiones y feedback endógeno activo.
Esta ejecución no reabre la comparación UCB1/SW-UCB ni agrega una modalidad.

### Configuración A/B/C y tratamientos

- **A — Sistema:** S3b-E1 3×3, competencias reales Bernoulli conocidas solo por
  el simulador, matriz base/transitoria y cambios exógenos en `t=3000,5000`,
  10.000 periodos, semillas `8200–8229`. Solo se intervino el mecanismo de
  observación; competencias, demanda/capacidad y outcomes potenciales de las
  tareas se mantuvieron comunes entre brazos emparejados.
- **B — Modalidad:** B2, matching completo 3×3 con las mismas restricciones y
  solver existente.
- **C — Arquitectura:** SW-UCB existente, `xi=2`, `W=1214`, misma calibración
  común de nueve periodos, mismo índice y matching. No se creó política nueva.

En ambos tratamientos cada periodo produjo las tres observaciones semi-bandit
normales más exactamente una observación subsidiada. En **U (uniforme)**, la
pareja adicional se muestreó uniformemente entre las nueve; en **R (dirigido)**,
uniformemente entre las tres parejas del matching óptimo verdadero del periodo.
R es una intervención oracular no implementable sin conocer competencias. La
política recibió solo identidad de pareja, outcome Bernoulli y tiempo; no
recibió etiqueta, competencias ni matching óptimo. La observación adicional
no aportó recompensa ni capacidad a la asignación.

La asignación se decidió antes de ambos updates. Cada brazo usó flujos
separados para outcomes de tarea, selección subsidiada y outcomes subsidiados;
los potenciales de tarea y las semillas se emparejaron. Si la pareja subsidiada
coincidió con una ejecutada, se generó un segundo Bernoulli independiente con
la misma competencia real. Ambos samples se guardaron con el timestamp global
del periodo: incrementan `n` de SW-UCB, pero no adelantan el reloj ni la
expiración de ventana.

### Resultado experimental

Métrica primaria: `L = Σ_t (R(a*_t,t) − R(a_t,t))`, regret esperado, no reward
Bernoulli realizado. IC95 t pareado por semilla (`n=30`):

| Tratamiento | Regret acumulado medio [IC95] | Reward esperado [IC95] | Matching óptimo [IC95] |
|---|---:|---:|---:|
| U — uniforme | 119,675 [111,499;127,851] | 16.980,325 [16.972,149;16.988,501] | 91,856% [91,544;92,168] |
| R — dirigido | 1.145,285 [1.134,128;1.156,442] | 15.954,715 [15.943,558;15.965,872] | 76,062% [75,652;76,472] |

Estimando emparejado `Δ=E[L_U−L_R]`: `−1.025,610`, IC95
`[−1.036,650;−1.014,570]`. Equivalentemente, `L_R−L_U=+1.025,610`,
IC95 `[+1.014,570;+1.036,650]`: el subsidio uniforme obtuvo menor regret.
La diferencia emparejada en tasa de matching óptimo (R−U) fue `−15,794`
puntos porcentuales, IC95 `[−16,218;−15,370]`. Reward realizado medio:
U `16.975,700` [16.945,047;17.006,353], R `15.959,533`
[15.931,529;15.987,538]. La tabla de regret por régimen (U/R) fue:

| Régimen | Regret U [IC95] | Regret R [IC95] | Matching óptimo U [IC95] | Matching óptimo R [IC95] |
|---|---:|---:|---:|---:|
| Base previo | 32,622 [28,981;36,262] | 371,970 [365,758;378,182] | 97,82% [97,57;98,08] | 82,09% [81,73;82,44] |
| Transitorio | 31,958 [30,635;33,282] | 170,417 [167,590;173,243] | 68,04% [66,72;69,37] | 51,48% [49,62;53,35] |
| Base posterior | 46,845 [40,094;53,596] | 594,648 [586,755;602,541] | 97,92% [97,62;98,22] | 82,37% [82,04;82,70] |

La desventaja de R no quedó restringida al cambio.

### Información y diagnóstico

El presupuesto de observación fue idéntico: 30.000 feedbacks endógenos y
10.000 subsidiados por réplica y brazo, 40.000 en total. U distribuyó el
subsidio casi uniformemente: entre `1.105` y `1.119` por pareja de media. R
lo concentró exclusivamente en parejas óptimas verdaderas: aproximadamente
`2.672` en `(0,0)`, `3.326` en `(1,1)`, `2.663` en `(2,2)`, `673` en `(0,2)` y
`665` en `(2,0)`; las otras cuatro recibieron cero subsidios. Las asignaciones
continuaron generando feedback endógeno, que se registra separadamente.

MSE medio por periodo, calculado en cada decisión y agregado dentro de cada
semilla, global y restringido a parejas del matching óptimo vigente: U
`0,003022` [0,002918;0,003126] y
`0,001668` [0,001450;0,001886]; R `0,003196` [0,003105;0,003287] y
`0,001025` [0,000948;0,001102]. Así, R tuvo menor MSE en parejas óptimas y,
sin embargo, peor rendimiento colectivo. El feedback global de U redujo
además la inanición de alternativas: el subsidio uniforme midió todas las
parejas, mientras el dirigido nunca subsidiaba las cuatro no óptimas en estos
regímenes. Esto es compatible con que el bonus UCB mantenga atractivo explorar
alternativas poco observadas, pero el experimento no identifica ese mediador
por separado.

No hubo parejas sin observaciones en ventana en ninguno de los dos brazos;
“ventana vacía” no explica aquí el efecto. Las trazas contienen reward/regret,
asignación, máscara de feedback endógeno, pareja y outcome subsidiados, MSE
global/óptimo y conteo de ventanas vacías por periodo. Se registran conteos
recientes y por fuente en los resúmenes por pareja y régimen.

### Validación del laboratorio, interpretación y límites

**Resultado experimental:** en esta configuración, uniformar el subsidio
causó menor regret que dirigirlo al matching óptimo, bajo el estimando
emparejado y los flujos compartidos descritos. No se demuestra que la
información uniforme sea generalmente mejor; el tratamiento R solo informa
pares actualmente óptimos y puede dejar insuficientemente observadas
alternativas competitivas. La identidad de las observaciones subsidiadas está
relacionada mecánicamente con el estado real por definición del tratamiento.
El efecto estimado es el efecto total de la intervención oracular en bucle
cerrado, incluidos los cambios posteriores de asignación y feedback endógeno;
no descompone mediadores ni explica por completo resultados previos UCB1/SW-UCB.

**Resultado del laboratorio:** quedó soportada una intervención local de
observabilidad que mantiene fijos B y C, da a cada outcome adicional la misma
marca temporal, distingue feedback endógeno/subsidiado y deja trazas
reproducibles por periodo. `PairwiseBanditEstimator.update_additional_observation`
añade un único sample al periodo actual sin avanzar tiempo. El control sin
subsidio reprodujo acciones y outcomes esperados SW-UCB B2-Semi de E1 para la
semilla 8200 dentro del redondeo registrado; las dos ejecuciones con semillas
fijas reprodujeron los agregados primarios.

Pruebas focalizadas: `tests/test_hls_s3b_observation_subsidy.py`,
`tests/test_hls_s3b_e1.py` y `tests/test_hls_s3b_nonstationary_assignment.py`;
**17 passed**. Artefactos nuevos, separados de resultados previos:
`experiments/run_hls_s3b_observation_subsidy.py`,
`results/experiments/hls_s3b_observation_subsidy/results.json` y
`period_traces.jsonl.gz`. Ejecución: `PYTHONPATH=src:. python
experiments/run_hls_s3b_observation_subsidy.py`.

Limitaciones: una instancia 3×3, una política, una matriz transitoria, 30
semillas; R usa información privilegiada y es intervención diagnóstica, no
arquitectura operativa. La conclusión concierne al contraste de estos dos
subsidios, no a la adquisición óptima general. **Estado:** experimento acotado
cerrado; no se inicia otra campaña. S3b permanece abierta y el siguiente paso
corresponde al PI.

## 2026-10-22 — S4: interacción MIS-v2 × enseñanza/transferencia (diseño previo)

**Autorización del PI:** GO acotado. Esta entrada fija el diseño antes de evaluar resultados; las cifras y conclusiones se añadirán después, sin alterar campañas previas.

**Pregunta e hipótesis.** En el sistema N×K existente, ¿cómo interactúan la exposición productiva MIS-v2 y la enseñanza dirigida cuando comparten esfuerzo y la demanda cambia? La identidad de transición sobre una misma celda predice una interacción de competencia no positiva por saturación del hueco restante; **no** predice el signo de la interacción de producción o éxito. Se evaluará si el efecto colectivo depende de la demanda y de las acciones elegidas. P2 no tiene superioridad presupuesta frente a una relación fija seleccionada en entrenamiento.

**Instancia fijada antes de resultados.** Dos agentes `A,B`, dos competencias `x,y`; competencia inicial `((.85,.15),(.20,.20))`, estimación inicial igual a la real y observación perfecta para aislar las transiciones. Parámetros existentes del caso de referencia: `eta=((.20,.15),(.12,.18))`; eficacia `A→B=(.75,.80)`, `B→A=(.70,.65)` en `x,y`, diagonal nula; tasa de transferencia `.4`; enseñanza de esfuerzo `.25`; parámetros P1/P2 `(prior=.5, threshold=.35, target=.95)`. Límites individuales `1`, presupuesto colectivo `2`; catálogo productivo de seis vectores por agente del caso de referencia. Demanda C5 Markov con estados `x,y`, distribución inicial `.5/.5`, permanencia `.9` y cambio `.1`, horizonte `24`. Requisitos `x=(.35,0)`, `y=(0,.40)`, pesos CES respectivos `(1,0)` y `(0,1)`: el umbral deja el problema `x` alcanzable inicialmente con media unidad de `A/x`, mientras que `y` supera el máximo productivo inicial `.15+.20=.35` y abre margen para aprendizaje o enseñanza. La elección se fija por este análisis de capacidad inicial, no por resultados de políticas. Semillas de entrenamiento `42000–42019`, evaluación emparejada `43000–43029`, sin reajuste. Solo varía la trayectoria exógena de demanda entre semillas; las transiciones y la observación son deterministas.

**Factorial:** `J00` sin transición, `J10` solo MIS-v2, `J01` solo transferencia, `J11` ambas; `I_J=J11-J10-J01+J00`. En todas las celdas siguen disponibles los mismos catálogos de acciones de cada política. MIS-v2 se desactiva con `individual_learning=False`; transferencia se desactiva con tensor de eficacia cero, conservando lecciones y cargos de `2u` al colectivo y `u` a docente/aprendiz. Producción precede a MIS-v2 y a enseñanza. La recompensa del periodo usa competencia previa a ambas transiciones.

**Dos estimandos distintos.** (1) Transición controlada: repetir en las cuatro celdas una misma acción factible definida por demanda: ante `x`, `A/x=.5, B/y=.5`; ante `y`, `A/y=.5, B/y=.5`; siempre `A→B/y` con `u=.25`. Esto prueba efectos físicos condicionados a una ruta de acciones común, no calidad de una política. (2) Bucle cerrado: ejecutar P0 sin enseñanza, P1 de relación fija y P2 adaptativa con las cuatro relaciones dirigidas posibles, manteniendo código y parámetros. P1 se elige entre esas cuatro relaciones por mayor CES medio acumulado en las 20 trayectorias **de entrenamiento bajo `J11`**, con desempate por orden declarado; la misma relación se congela en las cuatro condiciones y en las 30 semillas independientes de evaluación. P0 es referencia productiva separada. La selección entrenada hace fuerte al comparador fijo para CES en la condición principal, pero le concede información previa adicional; una diferencia P2–P1 no identifica aisladamente el valor causal de adaptar la relación.

**Medidas y lectura.** Principal: CES acumulado y su interacción factorial, calculada por semilla; diferencias/IC95 pareados sobre semillas. Secundarias: éxito funcional, déficit normalizado, competencias por celda, esfuerzo productivo/de enseñanza/total, número de lecciones y relación seleccionada, trayectoria por periodo. Se mostrarán interacciones de transición controlada y de política por separado. El signo de `I_CES` en bucle cerrado incluye respuesta de acciones; no se atribuirá a la identidad mecánica de MIS-v2 y transferencia. Una interacción nula/negativa se conservará como resultado. No se cambiarán instancias ni parámetros tras ver resultados.

### Ejecución y resultados del diseño fijado

**Validación previa.** Las transiciones usan las implementaciones existentes `mis_v2_transition_nk` y `teaching_transition_nk`; no se modificaron sus ecuaciones ni P0/P1/P2. El catálogo conjunto con eficacia real y con eficacia cero es idéntico; la ruta de acciones controladas pertenece a ambos y mantiene un cargo de enseñanza `2u=.5` por periodo en las cuatro celdas. El primer CES coincide entre celdas porque producción antecede al desarrollo. La prueba de una celda confirma `I_c=-(M(c,x)-c)·(.4·.25·T)`. La demanda generada por semilla es común a condiciones y políticas; 29/30 semillas de evaluación tuvieron al menos un cambio (`2.1` cambios medios; 352 periodos `x`, 368 `y`). La observación de competencia es perfecta en todo el protocolo; P2 solo actualiza memoria de eficacia después de una lección. Pruebas focalizadas antes de ejecutar: **46 passed**.

**Factorial de transiciones, acciones emparejadas:** CES acumulado medio [IC95] entre 30 semillas independientes; el éxito es número de periodos funcionales sobre 24. Cada celda utiliza exactamente `24` unidades productivas y `12` de enseñanza, `36` en total por réplica.

| Celda | CES acumulado [IC95] | Éxitos medios | Déficit normalizado acumulado medio | Competencia final media `B/y` |
|---|---:|---:|---:|---:|
| `J00` ninguna transición | 7.133 [6.530, 7.736] | 11.73 | 6.900 | .200 |
| `J10` MIS-v2 | 12.648 [12.189, 13.108] | 21.80 | .620 | .926 |
| `J01` transferencia | 9.915 [9.690, 10.140] | 19.47 | 1.200 | .892 |
| `J11` ambas | 13.411 [12.811, 14.011] | 22.50 | .458 | .990 |

Para CES, el efecto marginal de transferencia fue `+2.782` sin MIS-v2 y `+.763` con MIS-v2; **interacción factorial pareada `I_CES=−2.019`, IC95 `[−2.440,−1.598]`**. La interacción de éxitos fue `−7.03` periodos, IC95 `[−8.69,−5.37]`. La interacción final de competencia `B/y` fue `−.628` (misma exposición y lección en todas las semillas), coherente con saturación del hueco de competencia. La mejora absoluta de `J11` frente a `J10` existe en esta ruta, aunque es menor que el efecto de transferir sin MIS-v2. La demanda afecta CES y éxito, mientras la exposición controlada de `B/y` permanece constante.

**Bucle cerrado.** P1 se eligió entre las cuatro relaciones factibles usando solo 20 semillas de entrenamiento `J11`; CES medio de entrenamiento: `A→B/x=16.254`, `A→B/y=15.621`, `B→A/x=14.741`, `B→A/y=15.666`. Se congeló `A→B/x` en todas las celdas de evaluación. No se entrenó con ninguna semilla `43000–43029`.

| Política | `J00` CES | `J10` CES | `J01` CES | `J11` CES [IC95] | `J11` éxitos /24 | `J11` esfuerzo prod. + enseñanza | `J11` lecciones |
|---|---:|---:|---:|---:|---:|---:|---:|
| P0 productiva | 16.613 | 34.762 | 16.613 | 34.762 [34.007, 35.517] | 23.03 | 48.000 + 0 | 0 |
| P1 relación fija entrenada | 8.307 | 14.531 | 10.712 | 15.976 [15.368, 16.584] | 20.37 | 24.000 + 12.000 | 24 |
| P2 adaptativa | 16.281 | 33.999 | 17.167 | 34.249 [33.448, 35.050] | 23.03 | 47.033 + .483 | .97 |

En `J11`, diferencia pareada P2−P0 de CES `−.513`, IC95 `[−.570,−.456]`; P2−P1 `+18.273`, IC95 `[17.835,18.711]`. P1 es la mejor **relación fija de su clase** en entrenamiento, no un óptimo de todos los calendarios de enseñanza. La regla P1 enseña en los 24 periodos y utiliza `36/48` unidades disponibles; P2 enseña aproximadamente una vez, y P0 no enseña. Los costes y trayectorias de acciones difieren; por ello las brechas entre políticas no pueden atribuirse solo a una transición. P0 es además una referencia fuerte sin enseñanza en esta instancia; P2 no la supera en `J11` para el CES principal, aunque ambas alcanzan `23.03` éxitos medios.

Interacción `I_CES` dentro de cada política: P0 `0` (nunca enseña); P1 `−.960`, IC95 `[−1.293,−.627]`; P2 `−.637`, IC95 `[−.768,−.507]`. Para P2, el efecto marginal de transferencia sobre CES fue `+.887` sin MIS y `+.249` con MIS. Este contraste de bucle cerrado incluye las decisiones y el feedback de eficacia, no identifica el efecto mecánico aislado. El resultado negativo de interacción no significa transferencia nociva: con acciones controladas y en P2, la transferencia elevó CES respecto a la misma condición MIS.

**Interpretación y límites.** El experimento comprueba una interacción física subaditiva en competencia bajo exposición y enseñanza sobre la misma celda y una interacción negativa de CES en la ruta controlada. En el bucle cerrado de esta configuración, P2 recupera casi todo el rendimiento de P0 con un pequeño coste de enseñanza, pero no aporta una mejora colectiva en `J11`; la P1 entrenada queda limitada por su regla fija de enseñanza, pese a haber seleccionado la mejor relación disponible en su clase. El protocolo usa una instancia sintética 2×2, 24 periodos, parámetros del caso de referencia y demanda C5; no estima prevalencia ni validez externa. La observación perfecta y la señal de eficacia sin ruido simplifican la información de P2. CES es rendimiento bruto; el esfuerzo se informa por separado. Los IC95 usan semillas como réplicas y son descriptivos para este diseño, sin corrección por multiplicidad. La capacidad validada del laboratorio es la conmutación controlada de dos transiciones sobre el mismo estado con acciones/cargos fijos, y su evaluación separada bajo políticas existentes en bucle cerrado.

Artefactos: `experiments/run_hls_s4_transfer_interaction.py`, `tests/test_hls_s4_transfer_interaction.py` y `results/experiments/hls_s4_transfer_interaction/results.json` (un JSON compacto con valores por semilla, resúmenes, contrastes y una traza ejemplar). **Estado:** estudio acotado ejecutado y cerrado; cualquier ampliación requiere decisión posterior del PI.

## 2026-10-22 — S4: estimación bayesiana × planificación

**Autorización y pregunta.** GO acotado del PI para evaluar si actualizar las estimaciones de competencias aumenta el valor colectivo de planificar mediante Bellman frente a una decisión reactiva exacta. La configuración es A: sistema S4 pequeño, competencias reales ocultas, observación productiva ruidosa, demanda conocida y transición MIS-v2; B: planificación intertemporal sobre asignaciones factibles B2; C: estimador bayesiano existente y planificador S4 existente.

**Diseño fijado.** Factorial 2×2: reactiva/Bellman × estimación congelada/actualizada. Se reutilizan el caso `A_no_future_return` y la familia S4 ya registrada de horizontes 1–4. Cada celda tiene dos agentes y dos tareas; la familia de inversión demanda solo la tarea `x`. Se usan 30 semillas emparejadas (`81000–81029`), ruido normal de observación `σ=.02`, prior uniforme discreto de 101 puntos en `[0,1]` (media `.5`) para todas las competencias y condiciones, y los parámetros MIS-v2 de los casos originales. El prior inicial común no usa competencias verdaderas. Las observaciones se producen para las parejas ejecutadas y se generan con innovaciones indexadas por semilla, periodo y pareja.

“Congelada” significa que no se incorpora la verosimilitud de observaciones; el estimador sí se propaga por la transición MIS-v2 conocida tras la acción ejecutada. “Actualizada” asimila las observaciones ejecutadas y luego propaga por MIS-v2. Ambas políticas reciben el mismo tipo de observación y la misma información de demanda. En cada periodo, la política reactiva maximiza exactamente la recompensa inmediata sobre la media posterior; Bellman resuelve el sufijo conocido desde esa misma media y ejecuta la primera asignación. Es planificación de certeza equivalente: no resuelve el POMDP ni es planificación bayesiana óptima. La transición física emplea `mis_v2_transition_nk`; la predicción del posterior emplea `predict_mis_v2_nk`. La ley MIS-v2 es afín en cada competencia, por lo que propagar la media coincide con la media de las competencias propagadas bajo esa ley.

**Corrección de inicialización detectada en verificación.** Una ejecución preliminar de comprobación con el prior momento-equivalente por defecto mostró masa prácticamente nula fuera de `{0, .5, 1}`; no permitía actualizar de manera informativa competencias reales intermedias como `.525`. Esa ejecución no se usa como resultado. Antes de la campaña registrada se sustituyó únicamente el prior por una cuadrícula uniforme declarada; se conservaron el soporte acotado, la verosimilitud/update bayesiano y la transición existentes. Esta decisión y el resultado negativo preliminar quedan visibles para trazabilidad.

**Resultados.** La métrica es recompensa colectiva acumulada calculada con competencias reales pretransición; la unidad de replicación son las semillas. IC95 de medias y contrastes se calcularon como aproximación normal pareada (`1.96×SE`).

| Caso | R-F | R-A | B-F | B-A | Interacción `I=(B-A−R-A)−(B-F−R-F)` [IC95] |
|---|---:|---:|---:|---:|---:|
| Sin retorno futuro, `T=1` | .7000 | .7000 | .7000 | .7000 | .0000 [.0000, .0000] |
| Familia inversión, `T=1` | .5250 | .5250 | .5250 | .5250 | .0000 [.0000, .0000] |
| Familia inversión, `T=2` | 1.1213 | 1.1213 | 1.1250 | 1.1250 | .0000 [.0000, .0000] |
| Familia inversión, `T=3` | 1.7781 | 1.7781 | 1.8438 | 1.8438 | .0000 [.0000, .0000] |
| Familia inversión, `T=4` | 2.4864 | 2.4864 | 2.6328 | 2.6328 | .0000 [.0000, .0000] |

No cambió ninguna trayectoria de decisiones entre estimación congelada y actualizada para una política y caso dados; por tanto, el contraste de interacción es exactamente cero en las 30 réplicas de cada caso. Bellman superó a la decisión reactiva en los horizontes 2–4 de la familia, pero en la misma magnitud con estimación congelada y actualizada: la ganancia de planificación ya observada en S4 no aumentó al incorporar las observaciones. El MSE previo medio disminuyó ligeramente con actualización en la trayectoria reactiva para `T=2–4` (aprox. `.052947→.052938`, `.052929→.052905`, `.052915→.052886`); en Bellman aumentó ligeramente (`.052969→.052998`, `.052969→.052996`, `.052969→.052992`). Por tanto, aquí la mejora pequeña de ajuste global no alteró la asignación ni la recompensa.

El tiempo medio medido por decisión fue inferior a `.2 ms` en estas instancias; el coste no es una evidencia de escalabilidad. Las medias de recompensa y de interacción fueron idénticas entre semillas, así que los IC de recompensa/interacción son degenerados; el ruido de observación modificó estimaciones, pero no decisiones en este protocolo.

**Interpretación y límites.** La hipótesis de que actualizar estimaciones aumentaría el valor de Bellman no recibe apoyo en las instancias evaluadas; el contraste factorial la debilita para este conjunto, pero no demuestra equivalencia general. La experiencia informativa fue escasa y las decisiones no cruzaron ningún umbral de asignación. El control sin retorno confirma interacción nula cuando no hay continuación. El resultado muestra que integrar dos componentes ejecutables no basta para obtener complementariedad de rendimiento. El estimador conserva sus ecuaciones, pero usa un prior uniforme especificado para competencias ocultas intermedias; Bellman sigue siendo una referencia exacta solo para su modelo de certeza equivalente, no para el problema parcialmente observable. La familia S4 es pequeña y previamente construida para estudiar valor de planificación; no se estima prevalencia ni generalización.

**Validación y artefactos.** Se verificaron la igualdad de la primera decisión ante cambios exclusivos de competencia oculta, actualización solo de parejas ejecutadas, propagación de la media mediante MIS-v2, coincidencia de la transición real con `mis_v2_transition_nk`, factibilidad por catálogo S4, y reproducibilidad por semilla. Resultados: `results/experiments/hls_s4_estimation_planning/results.json`; implementación adaptadora: `src/hls/synthetic/hls_s4_estimation_planning.py`; runner y pruebas focalizadas: `experiments/run_hls_s4_estimation_planning.py`, `tests/synthetic/test_hls_s4_estimation_planning.py`. **Estado:** experimento acotado ejecutado y registrado; no se inicia otro experimento.

## 2026-10-22 — S4: repetición con actualización informativa

**Objetivo.** GO del PI para repetir el factorial de estimación × planificación en un régimen donde las observaciones puedan mover el posterior y las decisiones. Se conservaron A/B/C y la política de certeza equivalente de la entrada anterior. La regla de actualización bayesiana, transición MIS-v2 y optimizadores no cambiaron.

**Calibración predeclarada.** Se examinaron candidatos en orden, con semillas `80000–80009`, y se seleccionó el primero que cumplía todos estos criterios, sin consultar recompensa ni interacción factorial: (i) desplazamiento medio de la media posterior de al menos `.025` tras la primera observación; (ii) decisiones reactivas posteriores distintas entre estimación congelada/actualizada en al menos la mitad de réplicas; (iii) trayectorias Bellman/reactiva distintas en al menos la mitad. El candidato 1 cumplió: competencias iniciales reales `((.55,.175),(.45,.175))`, `η=((.15,.15),(.05,.25))`, demanda `x` en cuatro periodos; prior gaussiano discretizado en 101 puntos, medias `((.52,.50),(.55,.50))`, desviación `.12`; ruido productivo `σ=.02`. El desplazamiento posterior medio en parejas observadas fue `.05667`; la fracción de semillas con cambio reactivo posterior fue `1.0`; la fracción con trayectorias Bellman/reactiva distintas bajo F fue `1.0`. No se evaluaron candidatos posteriores.

La evaluación usó semillas independientes `82000–82029`. Incluyó el control sin retorno futuro `A_no_future_return` y la familia fijada de horizontes `T=1,2,3,4` con el candidato calibrado. Se ejecutaron R-F, R-A, B-F y B-A sobre las mismas instancias. Las competencias reales se usaron para producción, transición y métricas; las políticas recibieron solo prior, demanda y outcomes observados. Semillas indexaron ruido por periodo y pareja, sin forzar que las políticas observaran las mismas parejas.

**Resultados.** Métrica principal: recompensa colectiva acumulada sobre competencias reales. IC95 pareados usan réplicas como unidades y aproximación normal `1.96×SE`.

| Caso | R-F | R-A | B-F | B-A | `I=(B-A−R-A)−(B-F−R-F)` [IC95%] |
|---|---:|---:|---:|---:|---:|
| Sin retorno, control | .7000 | .7000 | .7000 | .7000 | .0000 [.0000, .0000] |
| Familia, `T=1` | .4500 | .4500 | .4500 | .4500 | .0000 [.0000, .0000] |
| Familia, `T=2` | .9275 | 1.0000 | .9275 | 1.0000 | .0000 [.0000, .0000] |
| Familia, `T=3` | 1.4311 | 1.6175 | 1.8424 | 1.8424 | −.1864 [−.1864, −.1864] |
| Familia, `T=4` | 1.9596 | 2.2924 | 2.5660 | 2.5660 | −.3328 [−.3328, −.3328] |

Los contrastes tienen IC degenerados porque las trayectorias de asignación fueron invariantes entre las 30 semillas dentro de cada condición; la variación del ruido no cruzó los umbrales de acción en este diseño. La fracción de periodos con asignación distinta entre A y F fue, para reactiva, `.50/.667/.75` en `T=2/3/4`; para Bellman, `.50/0/0`. En T=3 y T=4, actualizar el posterior elevó la recompensa reactiva en `.1864` y `.3328`, respectivamente, mientras Bellman no cambió su trayectoria ni recompensa. Por ello la ventaja Bellman−reactiva se redujo exactamente en esas cantidades: la interacción fue negativa. En T=2, la actualización benefició por igual a ambas reglas y la interacción fue cero.

La magnitud media `L1` de actualización posterior por periodo en condiciones A fue para reactiva `.01580/.01118/.00867` y para Bellman `.01580/.00344/.00274` en `T=2/3/4`; el control de un periodo fue `.08516` en el caso canónico y `.02427` en el miembro `T=1`. El MSE medio previo a decisión en `T=4` cambió de `.055194` a `.053628` para reactiva y de `.055458` a `.055404` para Bellman. Se observó así A (cambio de estimación), B (cambios de decisiones, especialmente reactiva), C (mejora de recompensa reactiva en T≥2) y D: no hubo valor adicional de planificar al actualizar; en T≥3, la actualización redujo la ventaja relativa de Bellman.

Coste descriptivo por periodo en `T=4`: R-F `.0930 ms`, R-A `.0898 ms`, B-F `.1566 ms`, B-A `.1549 ms` por decisión. No implica una conclusión de escalabilidad. La propagación posterior de su media coincide con MIS-v2 por la afinidad de la transición en competencia; Bellman sigue siendo exacto solo para el problema determinista de certeza equivalente, no para el estado de creencia completo.

**Conclusión y límites.** La calibración verificó un régimen operativo: observaciones informativas, cambios de decisiones y diferencia entre planificación y reacción. La hipótesis de complementariedad positiva queda **debilitada en esta instancia**: la actualización ayudó a la política reactiva y no cambió Bellman, produciendo interacción negativa a horizontes 3 y 4. Esto es compatible con sustitución entre información y planificación en esta configuración, no demuestra una regla general. El control sin retorno confirma que las observaciones no alteran la recompensa ya ejecutada. La evaluación es una familia pequeña heredada, una matriz de competencias y demanda determinista; los intervalos degenerados reflejan políticas estables bajo los outcomes evaluados y no garantizan ausencia de incertidumbre en otras instancias.

**Artefactos y validación.** Calibración: `experiments/calibrate_hls_s4_estimation_planning.py` y `results/experiments/hls_s4_estimation_planning_informative/calibration.json`. Ejecución: `experiments/run_hls_s4_estimation_planning_informative.py`, con trazas y resúmenes en `results/experiments/hls_s4_estimation_planning_informative/results.json`. Adaptador S4 y pruebas: `src/hls/synthetic/hls_s4_estimation_planning.py`, `tests/synthetic/test_hls_s4_estimation_planning.py`. Pruebas focalizadas, incluido estimador y MIS-v2: **42 passed**; `git diff --check` sin errores. **Estado:** repetición acotada completada; no se inicia otra campaña.

## 2026-10-22 — S4: repetición con oportunidades de transferencia

**Autorización y objetivo.** GO del PI para evaluar MIS-v2 y transferencia en
bucle cerrado en un régimen donde enseñar tenga una oportunidad organizativa
plausible. Se reutilizaron las transiciones N×K, los costes, el generador C5 y
P0/P1/P2; no se modificaron sus reglas de decisión ni las ecuaciones físicas.
La evaluación se limita a la configuración congelada que sigue.

**Calibración ex ante, independiente de P0/P1/P2.** Se conservaron las
competencias iniciales `((.85,.15),(.20,.20))`, C5 Markov (`x/y=.5/.5`,
permanencia `.9`), horizonte `T=24`, presupuesto colectivo `2` y límites
individuales `1`. Se aumentó el requisito de y de `.40` a `.70`: el output y
máximo inicial sin lección es `.35`, y una lección A→B/y con eficacia `.8`,
tasa `.4` y esfuerzo `.25` aporta `.064` a B/y; aun sin contar producción,
la suma inicial de competencia y tras esa transferencia es `.414 < .70`. La
transición conserva su ley original; se calibró su parámetro MIS-v2 `eta[B,y]`
en el orden predeclarado `.18, .10, .05`, dejando el resto de `eta` y la
eficacia/tasa/esfuerzo de transferencia sin cambios.

El criterio no consultó políticas ni recompensas de P2: trayectoria física
fija con la demanda C5, un primer y en que se compara no enseñar (producción
1.5) con enseñar (producción 1.0 + coste docente `.5`), y después acciones
productivas iguales; exigir déficit inicial, transición de enseñanza positiva,
al menos ocho periodos y-demandados de media y CES acumulado neto positivo en
al menos 8/10 trayectorias de calibración (`44000–44009`). Los candidatos
`eta[B,y]=.18/.10/.05` dieron diferencias CES medias `−.1251/+ .0049/+.1458`
y signos positivos en `0/5/8` de 10 trayectorias, respectivamente. Se congeló
`.05`, el primero que cumplió el criterio. La pérdida CES inmediata media al
enseñar en el primer y fue `.075`; la ganancia posterior bajo esa ruta fija
compensó esa oportunidad de producción. Esto demuestra potencial físico para
esa ruta, no que P2 vaya a seleccionarla ni que supere a P0.

**Evaluación fijada.** P1 se seleccionó entre las cuatro relaciones usando
20 semillas de entrenamiento (`44100–44119`) y luego se congeló; la mejor fue
A→B/x (CES medio de entrenamiento `15.839`, frente a `15.772` para A→B/y,
`14.327` para B→A/x y `15.210` para B→A/y). P0, P1 y P2 se ejecutaron sobre
las mismas 30 trayectorias C5 de evaluación (`44200–44229`), independientes
de calibración y entrenamiento, con la misma información perfecta del estudio
S4 previo. La unidad de réplica es la semilla. Los intervalos de diferencias
son pareados; las medias tienen IC95% t de Student.

| Política | CES acumulado [IC95%] | P2−comparador CES [IC95%] | Éxitos /24 | Déficit normalizado | Lecciones | Esfuerzo productivo + docente; ocioso |
|---|---:|---:|---:|---:|---:|---:|
| P0 productiva | `32.421 [31.235,33.606]` | — | `21.10` | `.807` | `0` | `48.00 + 0; 0` |
| P1 relación fija entrenada (A→B/x) | `15.399 [14.460,16.339]` | `+16.231 [15.739,16.722]` | `13.97` | `4.480` | `24` | `24.00 + 12.00; 12.00` |
| P2 adaptativa | `31.630 [30.421,32.840]` | `−.791 [−.840,−.741]` vs P0 | `21.10` | `1.892` | `2.90` | `45.10 + 1.45; 1.45` |

La otra diferencia pareada fue P1−P0 CES `−17.021`, IC95%
`[−17.474,−16.569]`. En evaluación había **24/24 periodos por semilla** con
alguna acción docente factible y con al menos una acción sobre la competencia
requerida en ese periodo (18 acciones conjuntas factibles sobre la tarea
actual, con el catálogo y los recursos configurados). Por tanto, las 2.9
lecciones medias de P2 no se explican por ausencia de acciones factibles.
P2 enseñó 2 o 3 veces en cada semilla (57 lecciones A→B/y y 30 B→A/y); primera
lección en promedio en `t=4.70`, última en `t=8.37`. P1, por su regla fija,
enseñó A→B/x en los 24 periodos, incluidos periodos cuya demanda era y.

**Competencias y lectura de A/B/C.** P2 produjo transferencia positiva: las
ganancias transferidas medias fueron `A/y=.047`, `B/y=.111` por réplica; sus
ganancias MIS-v2 en y fueron `.503` y `.226`. P0, sin transferencia, obtuvo
ganancias MIS-v2 en y de `.594` y `.298`. Las ganancias agregadas en y son
parecidas (`.887` P2, contando transferencia, frente a `.892` P0), lo que es
compatible con que la transferencia sustituyera parte del aprendizaje por
producción en esta ruta; no identifica por sí solo mediación causal.
La competencia inicial fue `((.85,.15),(.20,.20))`. Medias finales por
agente/competencia fueron P0 `((.979,.744),(.801,.498))`, P1
`((.957,.576),(.944,.375))` y P2 `((.979,.700),(.801,.537))`. La evaluación
tuvo en promedio `10.13` periodos con demanda y por réplica.

- **A — Sistema:** las necesidades de y exceden el output inicial, existe una
  relación docente con eficacia positiva y C5 ofrece tiempo futuro; la
  calibración física muestra un beneficio potencial neto bajo una ruta fija.
- **B — Modalidad:** esfuerzo productivo y una lección compiten por el mismo
  presupuesto de recursos; las acciones docentes son factibles durante todos
  los periodos y su coste está contabilizado.
- **C — Arquitectura:** P2 selecciona lecciones adaptativamente y las activa,
  pero no convirtió esa activación en mejora de CES ni de éxitos frente a P0.
  P2 tuvo los mismos éxitos que P0 y CES `.791` menor; P1 fue aún peor y su
  coste fijo implicó 12 recursos ociosos por réplica.

**Conclusión y límites.** Se verifican A (transferencia físicamente positiva
bajo la ruta de calibración), B (P2 selecciona oportunidades docentes) y C
(en este bucle cerrado, enseñar no mejora el resultado colectivo frente a
P0). La enseñanza seleccionada es compatible con un coste de oportunidad
observable: P2 usó `1.45` recursos docentes y produjo `2.90` unidades menos
de esfuerzo productivo que P0, con idéntico número medio de éxitos pero más
déficit y menor CES. Así, el potencial mecánico del desarrollo no basta para
garantizar beneficio de la política. La comparación con P1 es frente a la
mejor relación fija dentro de esa clase en entrenamiento independiente; su
regla enseña siempre y no equivale a un calendario fijo optimizado.

El cribado fue deliberadamente físico y estrecho; la calibración escogió un
régimen donde una ruta de transferencia puede pagar su coste, no una victoria
de P2. Solo se evaluó una configuración, con observación perfecta, C5 de dos
estados y parámetros sintéticos; no se infiere superioridad general ni se
separan causalmente los mediadores del bucle cerrado. El resultado negativo
P2−P0 se conserva como tal.

Artefactos: runner `experiments/run_hls_s4_transfer_opportunities.py`, pruebas
`tests/test_hls_s4_transfer_opportunities.py` y resultado reproducible con
semillas, calibración, agregados, diferencias pareadas y trazas por periodo en
`results/experiments/hls_s4_transfer_opportunities/results.json`. Pruebas
focalizadas: `PYTHONPATH=src:. pytest -q
tests/test_hls_s4_transfer_opportunities.py
tests/test_hls_s4_transfer_interaction.py` — **9 passed**. `git diff --check`
se ejecutó tras documentar. **Estado:** esta repetición queda registrada y
cerrada; no se inicia otra campaña.

## 2026-10-22 — S4: referencia intertemporal exacta de transferencia

**Objetivo y modelo.** Se implementó una referencia exacta para medir el valor
organizativo de permitir transferencia, manteniendo las leyes físicas
existentes. El estado es la matriz real de competencias `C_t`; las acciones
son asignaciones productivas del catálogo declarado y, en la condición B,
opcionalmente una lección dirigida factible. El reward por periodo es el CES
colectivo vigente calculado sobre la producción **antes** de las transiciones;
el déficit funcional se registra, pero no es una penalización adicional del
objetivo. El estado siguiente aplica primero MIS-v2,
`c' = 1-(1-c)exp(-lambda(eta)e)`, y luego, si hay lección,
`c'' = min(1,c' + r e T[i,j,k](1-c'))`. La enseñanza consume los mismos
recursos y límites individuales según el validador existente. La demanda y
las competencias son deterministas; la referencia exacta conoce la secuencia
completa y el estado real. No representa una política desplegable.

**Instancia fijada y espacio de acciones.** Dos agentes (`A,B`), dos
competencias (`x,y`), `C_0=((.85,.15),(.20,.20))`, parámetros MIS-v2
`eta=((.20,.15),(.12,.05))`, secuencia de demanda `x,y,y`, requisitos
`(.35,0)` y `(0,.70)`, pesos CES unitarios sobre la tarea activa, presupuesto
colectivo `2`, límites individuales `1`, esfuerzo docente `.25`, tasa de
transferencia `.4` y tensor de eficacia del experimento S4 previo sin cambios
(incluida `T[A,B,y]=.80`). Se reutilizaron íntegramente los seis vectores de
esfuerzo declarados por agente; no se redujo el catálogo. La enumeración
existente produce 36 acciones productivas factibles por periodo en A y 72
acciones factibles en B, que incluyen todas las acciones de A sin enseñanza.
La reconstrucción independiente desde los vectores de esfuerzo y relaciones
docentes encontró exactamente los mismos catálogos.

**Métodos y verificaciones.** Bellman memoizado optimiza por estado y periodo
en las dos condiciones. Una enumeración independiente recorre secuencias
factibles completas (46.656 en A y 373.248 en B); no usa la recurrencia ni el
constructor de acciones de Bellman. Bellman y enumeración coinciden en ambas
condiciones. También se verificó `J_B* >= J_A*`, la inclusión de acciones A en
B, la factibilidad de recursos en las trayectorias y que el óptimo de B con
eficacia física fijada a cero coincide con A.

**Resultado exacto.** `J_A*=1.9175000000000004` y
`J_B*=1.9175000000000004`; valor organizativo de disponibilidad de
transferencia en esta instancia: `0`. Ambas referencias eligen las mismas
acciones: en `t=0` asignan esfuerzo `1` a x para cada agente (reward `1.05`);
en `t=1,2` asignan esfuerzo `1` a y para cada agente (rewards `.35` y
`.5175`). No enseñan. El output y permanece bajo el requisito `.70` en ambos
periodos (`.35` y `.5175`), pero maximizar el CES vigente no aplica una
bonificación adicional por cruzar ese umbral. La competencia evoluciona por
MIS-v2 de `((.85,.15),(.20,.20))` a `((.88,.15),(.296,.20))` tras x; luego
`y` lleva los valores a `((.88,.2775),(.296,.24))` y
`((.88,.385875),(.296,.278))`.

Como diagnóstico adicional dentro de la misma enumeración, el mejor plan que
contiene al menos una lección obtiene `1.7239746573521653`, es decir,
`0.19352534264783516` menos que el óptimo. Enseña A→B/y en `t=1`: la
competencia de B/y sube por MIS-v2 de `.20` a `.220256` y por transferencia a
`.282636` (incremento transferido `.062379`). La producción y del periodo
baja a `.175`; en el último periodo el output y es `.498975`, todavía inferior
al plan sin enseñanza (`.5175`). En esa acción quedan `.5` recursos colectivos
sin usar por la granularidad del catálogo y los límites individuales. Así,
el desarrollo físico ocurre, pero no compensa la producción sacrificada en
este horizonte.

**Interpretación y límites.** La igualdad no indica que la transferencia sea
inútil en general: en esta instancia corta, la demanda de la competencia
objetivo coincide con el periodo en que habría que pagar el coste; MIS-v2
desarrolla ambas competencias de y mediante producción y genera retorno
productivo inmediato, mientras la lección solo cambia el estado futuro. El
resultado también depende de la recompensa CES que no premia directamente
alcanzar el requisito funcional, de los recursos y del catálogo discreto
declarado. No se atribuye la igualdad a P2: las dos cifras son óptimos
intertemporales con modelo conocido. El valor de P2 requeriría una comparación
separada contra estas cotas y no se evaluó aquí.

**Artefactos y estado.** Implementación acotada: `src/hls/synthetic/hls_s4_transfer_exact.py`;
runner y resultado: `experiments/run_hls_s4_transfer_exact.py` y
`results/experiments/hls_s4_transfer_exact/results.json`; pruebas:
`tests/synthetic/test_hls_s4_transfer_exact.py`. Pruebas focalizadas:
**4 passed**. Bellman para ambas condiciones tardó descriptivamente `1.29 s`
y enumeración independiente `13.03 s` en esta ejecución; no se infiere
escalabilidad de esos tiempos. Se reutilizaron MIS-v2, transferencia, reward,
catálogo y validación de recursos; P0/P1/P2 y las leyes físicas no se
modificaron. **Conclusión:** referencia exacta viable para esta instancia;
valor de transferencia nulo con `T=3`, `x,y,y`. No se ajustaron parámetros
tras el resultado. Como modificación motivada —no ejecutada— se propone una
instancia determinista `x,x,y,y`: dos periodos de preparación productiva antes
de dos demandas consecutivas de y. Esto representa explícitamente un plazo
para desarrollar capacidad antes de un cuello de botella sostenido; permite
al MIS-v2 desarrollar y mediante esfuerzo productivo en periodos x (sin
recompensa CES inmediata por y) y a la transferencia prepararla antes de su
demanda. La comparación exacta seguiría usando el mismo catálogo y recursos
en A/B. No se presupone que el nuevo perfil dé ventaja a B; requiere
autorización aparte.

## 2026-10-22 — S4: frontera preparación × demanda futura para transferencia

**Objetivo y configuración.** Por autorización del PI, se amplió el uso de la
referencia Bellman exacta para comparar el óptimo A (producción + MIS-v2) con
el óptimo B (las mismas acciones más transferencia opcional). Se conservaron
sin cambios dos agentes, las competencias iniciales `((.85,.15),(.20,.20))`,
parámetros MIS-v2 `((.20,.15),(.12,.05))`, los límites individuales y el
presupuesto colectivo existentes, el esfuerzo/coste y tasa de enseñanza, el
tensor de eficacia, el catálogo completo de esfuerzo, la transición física y
el CES. Solo cambió la secuencia de demanda: `x^p y^q`. Se evaluaron los tres
puntos T=4 predeclarados (`p,q` = `(2,2)`, `(1,3)`, `(3,1)`) y una ampliación
secuencial acotada a T=5 (`(2,3)`) tras comprobar el coste del primer nivel.
No se alteraron parámetros físicos ni se escogieron instancias por reward.

**Método y verificaciones.** Bellman memoizado enumeró en cada periodo el
catálogo completo de acciones factibles del laboratorio: 36 acciones en A y
72 en B, incluyendo todas las acciones de A en B; no se restringió el espacio
de decisiones. En todas las instancias se comprobó `J_B* >= J_A*` y que B con
eficacia física de transferencia igual a cero coincide con A. La verificación
independiente por enumeración completa de secuencias para el caso previamente
registrado `x,y,y` volvió a coincidir con Bellman: 46.656 secuencias A y
373.248 B. Este control independiente valida las leyes/catálogos y la
recurrencia en una instancia pequeña; la enumeración exhaustiva no se extendió
a T=4/5 por el tamaño del producto de acciones (26.873.856 secuencias B ya en
T=4 y 1.934.917.632 en el punto T=5). La expansión se mantuvo exacta, sin
discretización ni aproximación.

**Resultados.** Las recompensas son CES acumuladas; éxito funcional y déficit
se registran aparte y no son términos adicionales del objetivo.

| Preparación `p` | Demanda futura `q` | `J_A*` | `J_B*` | `Δ` | Lecciones óptimas B |
|---:|---:|---:|---:|---:|---:|
| 2 | 2 | 3.093500 | 3.093500 | 0 | 0 |
| 1 | 3 | 2.581375 | 2.581375 | 0 | 0 |
| 3 | 1 | 3.860480 | 3.860480 | 0 | 0 |
| 2 | 3 | 3.757375 | 3.757375 | 0 | 0 |

En `x,x,y,y`, ambas referencias eligen producción completa en x en los dos
primeros periodos (rewards `1.050000`, `1.176000`) y en y en los dos últimos
(`.350000`, `.517500`). MIS-v2 desarrolla y durante su ejecución; las dos
salidas y siguen por debajo del umbral funcional `.70`, aunque el CES las
recompensa como `.35` y `.5175`. En `x,y,y`, el único periodo x no proporciona
tiempo adicional de preparación y las salidas y son `.35`, `.5175`, `.663875`.
Con tres periodos x y uno y, el óptimo acumula `.35` en el único periodo y:
una lección no tiene retorno productivo suficiente dentro del horizonte. En
`x,x,y,y,y`, la trayectoria óptima coincide con `x,x,y,y` hasta el segundo y,
y produce `.663875` en el último; competencias y déficits quedan registrados
por periodo en el artefacto de resultados. En ninguno de los cuatro óptimos B
enseña: el aumento de horizonte/demanda probado no crea una región de valor
positivo para transferir bajo estos parámetros.

**Coste computacional y frontera observada.** En esta máquina, Bellman B
visitó 120.085 estados y tardó descriptivamente 12.60–12.74 s para cada
instancia T=4. Para el único punto T=5 visitó 654.665 estados y tardó 93.50 s;
el producto bruto de acciones crece mucho más rápido que el número de estados
memoizados. Son mediciones de esta ejecución, no una afirmación de escalabilidad.
El crecimiento observado define el límite práctico de esta evaluación: no se
amplió a T=6 ni se hizo búsqueda adicional. T=5 permaneció resoluble de forma
exacta, pero ya con un coste sustancial.

**Interpretación organizativa.** No se identificaron, dentro de la frontera
temporal explorada y con las leyes físicas, CES, recursos y competencias
existentes, condiciones donde la transferencia mejore el óptimo colectivo
frente a MIS-v2. En los perfiles con preparación, la producción x permite
mejorar x vía MIS-v2, pero el y futuro se desarrolla mediante MIS-v2 al
asignar y; la lección consume recursos productivos y su incremento transferido
no recupera ese coste antes del final del horizonte. Alargar la demanda y
permite más actualizaciones MIS-v2 por experiencia, no evidencia un cambio
de régimen a favor de enseñar en T=5. Esto es una conclusión exacta para las
instancias evaluadas, no una prueba de que la transferencia carezca de valor
en otros parámetros o perfiles de demanda. La frontera `Δ>0` no quedó
identificada.

**Artefactos, pruebas y estado.** Runner: `experiments/run_hls_s4_transfer_frontier.py`;
resultados compactos con trazas óptimas por periodo:
`results/experiments/hls_s4_transfer_frontier/results.json`; pruebas:
`tests/synthetic/test_hls_s4_transfer_frontier.py`, junto con las pruebas de
la referencia exacta `tests/synthetic/test_hls_s4_transfer_exact.py`.
Ejecución focalizada: **6 passed**. `git diff --check` se ejecutó tras esta
entrada. La referencia exacta verifica `J_B* >= J_A*`, igualdad al desactivar
físicamente transferencia, y coincidencia Bellman/enumeración independiente
en el caso pequeño. **Conclusión:** no se demuestra una condición positiva de
transferencia en la familia temporal acotada; el estudio solicitado queda
documentado y cerrado en su alcance, sin modificar P0/P1/P2 ni iniciar otra
campaña.

## 2026-10-22 — S4 y literatura de workforce learning; candidatos S5–S7

**Alcance y verificación bibliográfica.** Revisión documental/científica; no
se ejecutaron simulaciones ni se modificaron leyes o políticas. Se detecta una
corrección de autoría: el trabajo de 2015 cuyo título se proporcionó,
“Selection, grouping, and assignment policies with learning-by-doing and
knowledge transfer”, es de David A. Nembhard y Frank Bentefouet, no de Jin et
al. La página editorial confirma *Computers & Industrial Engineering* 79,
175–187 (2015), DOI [10.1016/j.cie.2014.11.006](https://doi.org/10.1016/j.cie.2014.11.006).
Para este trabajo se consultaron metadatos, highlights y abstract del editor,
no el texto completo; no se atribuyen detalles cuantitativos no visibles allí.

Para Jin, Hewitt y Thomas (2018), *International Journal of Production
Research* 56(14), 4968–4982, DOI
[10.1080/00207543.2018.1424366](https://doi.org/10.1080/00207543.2018.1424366),
se consultó el artículo completo en la copia de autor alojada en
[ResearchGate](https://www.researchgate.net/publication/322638546_Workforce_grouping_and_assignment_with_learning-by-doing_and_knowledge_transfer),
contrastando título y DOI de publicación. Para Su, Zhong y Zhang (2025),
*International Journal of Production Economics* 286, artículo 109642, DOI
[10.1016/j.ijpe.2025.109642](https://doi.org/10.1016/j.ijpe.2025.109642),
se consultó la página editorial y su abstract, no el texto completo. Por ello
se pueden comparar su problema, formulación y método tal como los declara el
abstract, pero no verificar ecuaciones completas, parámetros, resultados
numéricos ni tratamiento de incertidumbre.

**Comparación técnica con S4.**

| Dimensión | HLS-S4 actual | Nembhard–Bentefouet (2015) | Jin–Hewitt–Thomas (2018) | Su–Zhong–Zhang (2025) |
|---|---|---|---|---|
| Competencia/productividad | Matriz `c[i,k]∈[0,1]`; producción aditiva por esfuerzo y competencia. | Productividad por trabajador/tarea con características individuales de aprendizaje y transferencia; detalle de ecuación no confirmado en el abstract consultado. | Curva hiperbólica de productividad con `K`, `r`, experiencia previa `p`; experiencia acumulada directa e indirecta. | Trabajadores multi-skilled y estructura jerárquica de skill-mix; reglas exactas de competencia no verificables desde el abstract. |
| Aprender y transferir/formar | MIS-v2 exponencial, por celda y esfuerzo ejecutado; transferencia dirigida modifica solo al aprendiz según eficacia fija `T[docente,aprendiz,k]`. | Integra learning-by-doing y learning-by-transfer al modelo de productividad; la organización agrupa trabajadores para transferir. | Compañeros co-localizados transfieren mediante experiencia indirecta, ponderada por `θ` del receptor; no es una lección discreta con coste separado. | Planificación explícita de cursos; certificación/habilitación precede a tareas, con cursos y scheduling integrados. |
| Organización y horizonte | Acciones por periodo; producción/enseñanza compiten por recursos; demanda C5 o secuencias conocidas; referencia exacta solo para instancias pequeñas. | Selección de trabajadores, agrupación y asignación a trabajos; heurísticas por etapa; se examinan sistemas paralelos y seriales. | Grupos de trabajadores a grupos de trabajos en sistema paralelo y horizonte finito; demuestra que bajo sus hipótesis existe óptimo especializado sin cambios de grupo/job durante el horizonte; MINLP reformulado como MIP exacto. | Modelo entero que integra calendario de cursos y schedules de empleados, con precedencia curso-tarea, capacidad de cursos y otras restricciones; CGBH basado en column generation/matheuristic. |
| Objetivo/evidencia | CES colectivo; éxito funcional/deficits se reportan aparte. T4/T5 exactos dieron `Δ transferencia=0` en la familia `x^p y^q`; factorial físico S4 e interacción de políticas aportan evidencia distinta. | Throughput; abstract informa comparación con baseline y cota no lineal, y que selección de trabajadores tendió a afectar más que agrupación/asignación; sin cifras verificadas del texto completo. | Throughput acumulado; en 100 instancias 9 trabajadores/9 trabajos el beneficio medio de derivar el plan reconociendo transferencia fue 5.8%; reformulación exacta superó la mejor heurística por gap medio 10.59%. No modela forgetting; no demuestra demanda aleatoria. | Beneficio neto (ingresos de servicio y términos de formación/coste declarados); 18 conjuntos de instancias sintéticas de home services y análisis de escenarios/sensibilidad. No se verifican valores numéricos ni hipótesis de demanda futura incierta. |

La cercanía de S4 a esta literatura es sustantiva: comparte decisiones de
asignación/desarrollo, competencia heterogénea y horizonte, por lo que “usar
aprendizaje y transferencia en workforce assignment” no sería por sí sola una
novedad de HLS. Las diferencias verificables son las leyes físicas y la
modalidad: MIS-v2 de HLS depende de exposición productiva continua y satura
exponencialmente; Jin et al. usan una curva hiperbólica con acumulación de
experiencia indirecta por convivencia en grupos; Su et al. planifican cursos y
precedencias, no la transición MIS-v2 aquí implementada. En el artículo 2018
la solución especializada fija se demuestra para sus hipótesis de aprendizaje
monótono y sistema paralelo; no es una ley universal para demanda que cambia,
costes de enseñar o reward CES de HLS.

**Revisión de las leyes físicas S4.** `mis_v2_transition_nk` aplica
`c'=1-(1-c)exp(-λ(η[i,k])e[i,k])`; es determinista, acotada, específica de
agente-skill, sin forgetting ni transferencia cruzada. El output de producción
es `Σ_i e[i,k]c[i,k]`. La ley docente aplica al aprendiz
`min(1,c + r e T[i,j,k](1-c))`; la competencia actual del docente no aparece
en la ecuación. Su capacidad queda resumida por la eficacia dirigida fija `T`,
que por tanto representa una hipótesis fuerte: un docente puede tener
efectividad constante sin que su propio dominio actual module la ganancia. La
enseñanza carga `e` a docente y aprendiz (`2e` recursos colectivos), por lo
que el coste de oportunidad productivo sí existe, pero no hay un coste
monetario adicional.

El reward CES se calcula sobre output antes de las transiciones. El éxito
funcional se calcula con requisitos y umbrales en paralelo, no como premio o
penalización CES. Los resultados de transferencia S4 muestran que esto importa:
puede crecer CES aunque siga habiendo déficit, y alcanzar/mejorar el estado de
una skill no equivale automáticamente a elevar el objetivo colectivo. Esto no
es un error de implementación, sino una elección de modelado que limita qué
afirmaciones sobre cumplimiento de servicio permite hacer. Ninguna ley se
modifica en esta revisión.

**Evaluación de candidatos (no son escenarios implementados).**

| Candidato | Problema, A/B/C y mecanismos | Qué existe / qué falta y comparaciones | Aportación posible / riesgo de duplicación |
|---|---|---|---|
| **S5 — especialización, cuello de botella y cross-training** | A: competencias heterogéneas con una skill crítica y demanda desbalanceada/variable. B: asignación B2 con competencia multi-skill y recursos de preparación. C: MIS-v2, transferencia/P2 y optimización reactiva. Problema real: resiliencia ante ausencia o pico de demanda de una skill especialista. | Existe N×K, tareas/demanda, CES, enseñanza dirigida, MIS-v2 y P0/P1/P2; falta que la eficacia docente dependa de competencia actual, y no hay disponibilidad/ausencia/turnos explícitos. Comparar no cross-training/MIS, transferencia fija y P2, con P0 y referencia exacta pequeña. | Puede estudiar cómo competencia basal y margen de capacidad determinan si se debe especializar o cruzar-formar. Riesgo alto: muy próximo a grouping/assignment con LBD y knowledge transfer de 2015/2018 y al training-scheduling de 2025; requeriría delimitar qué decisión dinámica distinta se aporta. |
| **S6 — aprendizaje por experiencia vs transferencia** | A: mismo sistema con capacidad de aprendizaje endógeno; B: acción productiva más enseñanza; C: MIS-v2, transferencia y referencias intertemporales. Pregunta: cuándo una vía de desarrollo sustituye o complementa a la otra. | Ya hay factorial de transiciones bajo acciones emparejadas, comparaciones de P0/P1/P2, referencia exacta MIS-v2 frente a transferencia opcional y frontera temporal T=3–5. Falta una región positiva de valor exacto en la configuración canónica, pero no justifica por sí sola repetir. | La interacción física es potencialmente interesante; riesgo muy alto de repetir los artículos 2015/2018 y experimentos S4 ya cerrados. **No GO** mientras no haya una dimensión de sistema nueva y justificada; no reabrir solo para hallar `Δ>0`. |
| **S7 — desarrollo ante demanda futura incierta** | A: competencias endógenas y demanda futura estocástica, con distribución o proceso de demanda explícito. B: decisión B3 sobre asignación/enseñanza entre periodos. C: políticas existentes P0/P1/P2 frente a una referencia estocástica exacta pequeña; P2 no conoce el futuro. | C5 Markov y P0/P1/P2 ya operan en simulación; existe Bellman determinista de horizonte conocido. Falta que la referencia intertemporal integre probabilidades de demanda como parte del estado/transición, además de tests que separen adaptación al estado actual de preparación anticipada. Comparar reacción a demanda actual, política adaptativa de enseñanza y valor de información/predicción mediante control exacto-oracular acotado. | Puede aportar evidencia sobre valor de preparar capacidades bajo incertidumbre, distinto de los resultados actuales con secuencia conocida. Riesgo medio-alto de solapamiento con ITCESP (2025); el abstract disponible no permite determinar si su demanda es estocástica, por lo que la novedad no se puede afirmar antes de consultar texto completo. |

**Recomendación.** **GO condicionado para especificar S7; NO-GO para comenzar
implementación o simulación todavía.** Es la pregunta más diferenciada de las
fronteras S4 ya ejecutadas: mantiene MIS-v2/transferencia y recursos, pero
introduce incertidumbre genuina sobre qué competencias se necesitarán y mide
si anticipar bajo una distribución conocida añade valor frente a reaccionar.
Su viabilidad es razonable en el 2×2 ya usado con C5, aunque requeriría una
extensión acotada del Bellman determinista a una transición probabilística de
demanda y estado. Antes de afirmar una brecha científica hay que leer el texto
completo de Su et al. (2025) y fijar qué incertidumbre del problema no cubre.
La métrica debería conservar CES como objetivo y reportar éxito/déficit aparte;
las comparaciones deben separar política ejecutable de referencia que conoce
la ley de demanda. La evidencia publicable dependería de un efecto reproducible
de anticipación en una familia delimitada, no de comparar únicamente P2 con un
baseline débil. Si la lectura completa revela que el artículo ya resuelve la
misma cuestión bajo hipótesis equivalentes, revisar prioridad antes de autorizar
trabajo.

**Estado.** S5–S7 son candidatos analizados, no nuevos escenarios ni campañas.
No se implementó nada, no se ejecutaron simulaciones y no se modificaron leyes,
políticas, ontología ni resultados. La prioridad propuesta se remite al PI para
decisión.

## 2026-10-22 — S7: primera referencia exacta con demanda Markov incierta

**Autorización y alcance.** A petición del PI se avanzó desde la especificación
existente de S7, sin rehacer su definición conceptual. Se leyó íntegramente el
PDF de 19 páginas `~/Downloads/1-s2.0-S0925527325001276-main.pdf`: Su, Zhong y
Zhang (2025), “Integrated training course planning and hierarchical multi-skilled
employee scheduling in the workforce skill transformation context”,
*International Journal of Production Economics* 286, 109642,
DOI 10.1016/j.ijpe.2025.109642. El artículo presenta el ITCESP como una
optimización integrada de calendario de cursos y asignación/scheduling de
servicios; las tareas, sus tiempos y requisitos se declaran conocidos de
antemano, el modelo básico es de una etapa y la demanda estocástica aparece en
las conclusiones como extensión futura (pp. 4–5, 17 del artículo). Su modelo
usa cursos y habilitación jerárquica, no las leyes continuas MIS-v2/transferencia
de HLS. Por ello sirve para delimitar el antecedente, no como validación ni
implementación del modelo HLS.

**Estado anterior y diferencia abordada.** El registro ya describía S7 como
competencias endógenas y demanda futura estocástica (A), decisión intertemporal
B3, y comparación de P0/P1/P2 con una referencia estocástica exacta pequeña
(C). El laboratorio ya tenía C5 Markov, las transiciones N×K de MIS-v2 y
transferencia, catálogos exhaustivos de acciones factibles, CES y Bellman exacto
para secuencias de demanda conocidas. Faltaba incorporar la transición
probabilística de demanda al estado del Bellman y validarla sin revelar la
demanda futura a la decisión actual. Esta entrada registra el primer incremento
funcional; no cambia la ontología ni cierra S7.

**Implementación.** Se añadió `src/hls/synthetic/hls_s7_uncertain_demand.py`,
una referencia finita y específica de escenario. Para competencia real `C` y
estado Markov observado `q`, usa

`V_t(C,q) = max_a { R(C,a,q) + Σ_q' P(q'|q) V_(t+1)(F(C,a),q') }`,

con condición terminal cero. `F` compone sin cambios MIS-v2 y, si está
permitida, la transición de enseñanza existente; `R` es el CES existente. La
acción solo condiciona en el estado de demanda actual. Se añadió también un
comparador reactivo que maximiza recompensa inmediata y una enumeración
independiente del árbol contingente para horizontes mínimos. La referencia
exacta conoce el estado físico y la ley de transición: es un oráculo de
validación, no una política ejecutable bajo competencia oculta o distribución
desconocida.

Runner: `experiments/run_hls_s7_uncertain_demand.py`. Resultado separado, sin
alterar resultados anteriores:
`results/experiments/hls_s7_uncertain_demand/results.json`.
Pruebas focalizadas: `tests/synthetic/test_hls_s7_uncertain_demand.py`.

**Diseño de primera validación.** Se reutilizó la instancia física S4 2 agentes
× 2 competencias, su demanda C5 Markov x/y (probabilidades iniciales 0.5/0.5;
permanencia 0.9 y cambio 0.1), las competencias iniciales, parámetros MIS-v2,
recursos, catálogo de producción/enseñanza y CES existentes. Horizonte T=3,
igual al caso exacto S4 existente. Se evaluaron Bellman y regla reactiva, con el
espacio de acciones de MIS-v2 solo y con transferencia opcional. No se
reparametrizó la física ni se seleccionó la instancia según una ventaja de
rendimiento. Se contrastó T=2 mediante árbol exhaustivo independiente y se
reprodujeron las políticas exactas en 1.000 trayectorias C5 con semillas
73000–73999.

**Resultados observados.** En T=2, el valor esperado Bellman y el árbol
independiente coincidieron exactamente: `1.532075` tanto sin transferencia
como con transferencia opcional (diferencia numérica 0). En T=3, los cuatro
valores fueron `J=2.468833775`: Bellman/reactivo y transferencia desactivada/
opcional coincidieron. En la trayectoria ilustrativa y–y–x, ambas decisiones
produjeron CES por periodo `0.3500, 0.5175, 1.0500`; no hubo enseñanza. La
simulación de 1.000 trayectorias dio media `2.44167`, DE `0.90036`, EE `0.02847`
para cada referencia, compatible con el valor esperado exacto (diferencia
`−0.02716`, menor que un EE). Las pruebas nuevas pasaron (`7 passed`); la
enumeración confirma Bellman en ambas disponibilidades de transferencia.

**Interpretación y límites.** El resultado nulo es válido para esta instancia y
horizonte: acredita que la política contingente, el valor esperado Markov, la
transición física y la enumeración independiente están conectados
coherentemente; no demuestra valor de planificación ni de transferencia bajo
demanda incierta. Con T=3, la reacción óptima coincide con el plan óptimo, y el
espacio opcional de enseñanza no se utiliza. El chequeo Monte Carlo valida la
media, no añade evidencia independiente sobre eficacia organizativa. No se han
ejecutado P0/P1/P2, no se estudió demanda futura desconocida para el decisor, ni
se generaliza a otras matrices, horizontes o procesos. El artículo 2025 tampoco
resuelve esta misma extensión estocástica en el modelo aquí estudiado; la
distinción es que su propia formulación asume órdenes conocidos y deja demanda
estocástica como trabajo futuro.

**Estado y siguiente requisito técnico.** S7 tiene ahora una referencia exacta
estocástica verificable en una instancia mínima, pero continúa abierto. Para
estudiar un efecto organizativo no nulo sin calibración retrospectiva, falta
fijar ex ante una instancia/horizonte con oportunidades suficientes de
preparación y una métrica de ejecución de P0/P1/P2 bajo información disponible,
con el oráculo exacto como referencia separada. Esta tarea no amplió la campaña
ni inició esa comparación.

## 2026-10-22 — S7: caracterización de oportunidades organizativas

**Pregunta y alcance.** Se examinó por qué la referencia inicial `T=3`
igualaba Bellman y reacción (`J=2.468833775`, con o sin transferencia) y si,
bajo las leyes físicas ya existentes, había condiciones concretas en las que
la anticipación de demanda incierta justificaba preparar una competencia. Se
mantuvieron intactas las leyes de CES, MIS-v2, transferencia, recursos y
factibilidad; no se modificaron S1–S6 ni los resultados previos.

**Análisis de la instancia inicial.** El régimen x/y con permanencia `0.9`, el
horizonte de tres periodos y las competencias originales no hacían rentable
una acción docente anticipada. La transferencia cobra `e` a docente y aprendiz
(coste colectivo `2e`), mientras MIS-v2 desarrolla una competencia solo al
ejecutar producción en ella. En esta instancia el horizonte corto y las
alternativas de producción/MIS-v2 bastaban para que la acción miope coincidiera
con Bellman; la opción de transferencia no se usó. Esto es un resultado nulo de
esa configuración, no evidencia de que preparar nunca aporte valor.

**Diseño de caracterización.** Tras el resultado nulo inicial se hizo un
cribado determinista pequeño y mecanístico de condiciones, no una búsqueda
extensa ni una maximización de la diferencia Bellman–miope. La instancia
principal se debe leer como una caracterización exploratoria: sus valores
sirven para demostrar una posibilidad estructural en el modelo, no como una
confirmación preregistrada ni como una estimación de frecuencia del fenómeno.
La justificación física del candidato final es que el docente es poco
productivo en la demanda x actual, el aprendiz aporta a x pero carece de y, y
la transición incierta favorece un régimen y persistente. El incremento inicial
de B/y (`.08`) multiplicado por el número esperado de periodos y restantes
(`.90 + .955 + .94775 = 2.80275`, pues la cadena permite regresar a x y volver
a y) da una cota mecanística de capacidad futura (`.22422`) del mismo orden
que el coste CES presente observado (`.175`);
no es una predicción exacta de `J_B−J_A` porque omite aprendizaje posterior,
alternativas de acción y ramas x.

Se reutilizó el sistema exacto S4 de dos agentes
(`A`, `B`) y dos competencias (`x`, `y`), la demanda C5 Markov, la recompensa
CES, los parámetros MIS-v2 y la transferencia existentes (`rate=0.4`,
`e=0.25`, eficacia `A→B/y=0.8`). El catálogo completo de esfuerzos declarado
por S4 produjo 36 acciones factibles sin transferencia y 72 con transferencia
opcional; no se truncaron acciones. Se definió una instancia mecanística
pequeña: competencias iniciales `A=(.05,.90)`, `B=(.30,0)`, demanda inicial x,
`P(y|x)=.90`, `P(y|y)=.95`, y requisito funcional de y `.95`. El requisito solo
hace observable el cuello de botella en éxito funcional; la función objetivo
sigue siendo el CES inalterado. La preparación en t=0 no conoce el siguiente
estado: Bellman solo observa la demanda actual y usa las probabilidades C5.

Se fijaron además dos controles: (i) mismos parámetros y proceso incierto,
pero `T=3`, para examinar oportunidad física con menos tiempo de recuperación;
(ii) `T=4` con x absorbente, para comprobar un régimen donde la competencia y
no la demanda futura de y es irrelevante. No se hizo un barrido extenso de
parámetros; los controles se fijaron para aislar horizonte y necesidad futura.
En la instancia corta y en el control x absorbente hay acciones docentes
físicamente factibles; por tanto, sus valores nulos no se explican por haber
eliminado la opción de enseñar.

**Resultados exactos (CES acumulado esperado).**

| Configuración | `J_A`: Bellman sin transferencia | `J_B`: Bellman, transferencia opcional | `J_M`: reactiva (sin / con transferencia) | `J_A−J_M` | `J_B−J_A` |
|---|---:|---:|---:|---:|---:|
| Oportunidad, `T=4`, C5 incierta | 3.1628653621 | 3.1743777327 | 3.0346209871 / 3.0346209871 | 0.1282443750 | 0.0115123706 |
| Control corto, `T=3`, C5 incierta | 2.1650542000 | 2.1650542000 | 2.1223042000 / 2.1223042000 | 0.0427500000 | 0 |
| Control sin demanda futura y | 2.8604896000 | 2.8604896000 | 2.8604896000 / 2.8604896000 | 0 | 0 |

En el caso principal, Bellman con transferencia vale `0.1397567456` sobre la
política reactiva (`J_B−J_M`). Para la reacción, ofrecer transferencia
opcional no altera el valor: maximiza recompensa inmediata y no elige enseñar.
`J_A−J_M` mide el valor de planificación sin transferencia; `J_B−J_A` mide el
valor incremental de hacerla disponible bajo planificación. Son estimandos
distintos.

**Decisión y transición explicativas.** En el estado inicial x, la política
miope y Bellman sin transferencia ejecutan esfuerzo productivo `1.0` en x
para ambos agentes: CES inmediato `0.35`. Bellman con transferencia produce
`0.5` en x para cada agente y enseña y de A a B con esfuerzo `.25`; el CES
inmediato baja a `0.175` (sacrificio `0.175`) y el recurso contabilizado es
`1.5` (producción `1.0` más enseñanza `0.5`). MIS-v2 se aplica primero; la ley
de transferencia vigente eleva después `B/y` de `0` a `.08` (`.4×.25×.8`). La
acción se elige usando la probabilidad de transición a y, no con conocimiento
de que y ocurrirá.

En la rama futura `x→y`, la asignación productiva a y obtiene CES `.98` y éxito
funcional con preparación, frente a CES `.90` y fallo funcional sin ella
(`y` requiere `.95`). En periodos y posteriores, MIS-v2 sigue desarrollando
ambos agentes y la brecha inicial persiste parcialmente. La trayectoria miope
en la rama `x→y→y→y` logra CES `.90, .915, .92775` y no alcanza el requisito
funcional en esos tres periodos: al no invertir, deja de desarrollar B/y. Esto
contrasta con Bellman sin transferencia, que puede usar aprendizaje MIS-v2
después de observar y, y con Bellman con transferencia, que adelanta parte de
esa capacidad. El valor esperado incremental neto de transferencia es
positivo pero pequeño (`.0115123706`), porque debe recuperar el coste presente
bajo todas las ramas de demanda. En el control `T=3`, la transferencia no se
selecciona y `J_B=J_A`; en x absorbente no se prepara y Bellman, reacción y ambos
espacios de acción coinciden.

**Verificación.** Para una truncación `T=2` de la instancia principal, Bellman
con y sin transferencia coincidió exactamente (`1.2224`) con (a) Bellman sin
poda de dominancia y (b) enumeración independiente del árbol contingente.
Las pruebas focalizadas verifican también el estado inicial y su transición,
coste inmediato, éxito/fallo en la rama y controles de horizonte/demanda. La
implementación usa poda exacta de acciones dominadas por recompensa inmediata
y estado de competencias componente a componente; la equivalencia con el
solver sin poda se comprobó en la validación mínima. Las pruebas
`tests/synthetic/test_hls_s7_uncertain_demand.py` pasaron (`11 passed`).

Artefactos nuevos:
`experiments/run_hls_s7_preparation_characterization.py` y
`results/experiments/hls_s7_preparation_characterization/results.json`.
El resultado previo `results/experiments/hls_s7_uncertain_demand/results.json`
se conservó sin sobrescribir.

**Conclusión A/B/C/D.** (A) Sí: existe una oportunidad física, con coste
presente y mejora de capacidad futura. (B) Sí: en la instancia principal la
planificación estocástica modifica la acción inicial y selecciona la
preparación; en los controles no lo hace. (C) Sí: el valor esperado CES mejora
frente a la política miope en la configuración con retorno temporal. (D) Sí,
con alcance limitado: disponer de transferencia aporta un incremento exacto de
`0.0115123706` sobre el óptimo MIS-v2-only en la instancia `T=4`; no aporta
valor en los controles. La primera validación `T=3` sigue siendo un resultado
nulo válido.

**Límites y estado.** Es una caracterización exacta de tres configuraciones
pequeñas, con competencias reales y matriz C5 conocidas por el oráculo; no
evalúa una política P0/P1/P2 con información realista ni establece robustez,
superioridad general de Bellman o una frontera completa de preparación. El
requisito funcional y las competencias iniciales definen una instancia
focalizada, no datos empíricos. S7 permanece abierto; no se inicia otra campaña
sin decisión del PI.

## 2026-10-22 — S7: protocolo de validación mecanística y robustez local

**Objetivo.** Antes de ejecutar la sensibilidad local se fijaron cuatro
referencias sobre la misma instancia y distribución: `J_A` Bellman sin
transferencia, `J_B` Bellman con transferencia opcional, `J_MA` reacción sin
transferencia y `J_MB` reacción con transferencia opcional. Las cuatro usan el
mismo estado observado, competencias reales del oráculo, demanda actual,
transiciones físicas, restricciones y CES. El Bellman usa la matriz C5 en la
continuación; la regla reactiva conoce el mismo caso pero, por definición,
maximiza solo el CES inmediato. Las políticas con transferencia tienen el
mismo catálogo opcional de enseñanza entre sí; ídem las dos sin transferencia.
Estas referencias son informacionalmente comparables como contraste de
planificación exacta, no son políticas ejecutables con competencias ocultas.

Se calcularán las identidades
`planificación sin transf.=J_A−J_MA`,
`planificación con transf.=J_B−J_MB`,
`transferencia con plan.=J_B−J_A`,
`transferencia sin plan.=J_MB−J_MA`, e interacción
`I=(J_B−J_A)−(J_MB−J_MA)`. La igualdad algebraica de la interacción con la
diferencia entre valores de planificación se comprobará automáticamente.

**Sensibilidad fijada antes de la evaluación.** Se conservará el horizonte
`T=4`, las competencias iniciales, el requisito y los recursos del caso
constructivo. Se ejecutará el centro y ocho perturbaciones locales
simétricas, una dimensión cada vez: `P(y|x)=.90±.05` (`.85,.95`),
`P(y|y)=.95±.025` (`.925,.975`), `eta(B,y)=.05±.01` (`.04,.06`) y eficacia
`A→B/y=.80±.10` (`.70,.90`). Los cambios permanecen en los dominios físicos
admisibles; solo se perturba la celda de MIS-v2 correspondiente al cuello de
botella y la relación docente usada. No se ampliará el intervalo ni se
seleccionarán parámetros según las diferencias resultantes. Se repetirán como
controles negativos los casos ya definidos `T=3` con transición incierta y
`T=4` con demanda x absorbente.

**Métricas funcionales predefinidas.** Se contabilizará como servicio
completado cada periodo que satisface todos los requisitos activos según
`evaluate_problem_nk`; incumplimiento será su complemento por periodo. Se
sumarán el déficit normalizado ya definido por esa función, déficits absolutos
por competencia, esfuerzo productivo y cargos docentes (`2e` por lección), así
como número de acciones de enseñanza. Son diagnósticos de trayectoria y no
modifican el objetivo CES. Cada esperanza se evaluará exactamente sobre el
árbol C5, no mediante muestreo de periodos.

### Resultados y lectura mecanística

El runner `experiments/run_hls_s7_mechanistic_robustness.py` resolvió las
cuatro políticas exactamente en el centro, ocho perturbaciones locales y dos
controles. El artefacto íntegro, con contrastes, métricas por política y ramas
de demanda `x→y→y→y`, `x→x→y→y` y `x→x→x→x`, está en
`results/experiments/hls_s7_mechanistic_robustness/results.json`.

| Configuración | `J_A` | `J_B` | `J_MA` | `J_MB` | Planificación sin transf. `J_A−J_MA` | Planificación con transf. `J_B−J_MB` | Transf. con planificación `J_B−J_A` | Transf. miope `J_MB−J_MA` | `I` |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| Centro | 3.1628653621 | 3.1743777327 | 3.0346209871 | 3.0346209871 | 0.1282443750 | 0.1397567456 | 0.0115123706 | 0 | 0.0115123706 |
| `P(y\|x)=.85` | 3.1432132587 | 3.1432132587 | 3.0201810712 | 3.0201810712 | 0.1230321875 | 0.1230321875 | 0 | 0 | 0 |
| `P(y\|x)=.95` | 3.1822044600 | 3.2051619587 | 3.0489728975 | 3.0489728975 | 0.1332315625 | 0.1561890612 | 0.0229574987 | 0 | 0.0229574987 |
| `P(y\|y)=.925` | 3.1454197677 | 3.1475605205 | 3.0215136740 | 3.0215136740 | 0.1239060938 | 0.1260468465 | 0.0021407528 | 0 | 0.0021407528 |
| `P(y\|y)=.975` | 3.1807623627 | 3.2018742357 | 3.0480700190 | 3.0480700190 | 0.1326923438 | 0.1538042167 | 0.0211118730 | 0 | 0.0211118730 |
| `eta(B,y)=.04` | 3.1375413871 | 3.1510796757 | 3.0346209871 | 3.0346209871 | 0.1029204000 | 0.1164586886 | 0.0135382886 | 0 | 0.0135382886 |
| `eta(B,y)=.06` | 3.1880268871 | 3.1975263357 | 3.0346209871 | 3.0346209871 | 0.1534059000 | 0.1629053486 | 0.0094994486 | 0 | 0.0094994486 |
| Eficacia `.70` | 3.1628653621 | 3.1628653621 | 3.0346209871 | 3.0346209871 | 0.1282443750 | 0.1282443750 | 0 | 0 | 0 |
| Eficacia `.90` | 3.1628653621 | 3.2010177890 | 3.0346209871 | 3.0346209871 | 0.1282443750 | 0.1663968019 | 0.0381524269 | 0 | 0.0381524269 |

`I` satisface en cada caso la identidad entre diferencias de planificación.
En el centro, la reacción con transferencia opcional no enseña: ambas
reacciones valen `3.0346209871`. Así, el efecto incremental de transferencia
sin planificación es cero; el efecto de transferencia con Bellman y la
interacción son ambos `0.0115123706`. No es una ley general de
complementariedad: en este diseño, la transferencia solo es utilizada por la
política que valora consecuencias futuras.

**Mecanismo observado.** En el centro, bajo demanda inicial x, `J_A` y la
reacción asignan esfuerzo productivo 1 a x por agente (CES inmediato `.35`).
`J_B` divide ese esfuerzo a `.5` por agente y enseña y de A a B con esfuerzo
`.25`; CES inmediato baja a `.175` (coste `.175`). MIS-v2 actualiza las
competencias x por el trabajo productivo; después, la transferencia eleva
B/y de `0` a `.08`, dejando el estado en
`(.150294,.90),(.343342,.08)`. En la rama predefinida `x→y→y→y`, la primera tarea y obtiene
CES `.98` y cumple el requisito y `.95`; `J_A` obtiene `.90` y no lo cumple
en ese primer periodo y. La transferencia añade `.08` a B/y; luego MIS-v2
continúa bajo el trabajo efectivamente realizado. La decisión inicial se
toma con la distribución C5, no con conocimiento de qué rama ocurrirá.

El valor `J_A−J_MA` tiene una explicación más delicada: cuando llega y, Bellman
asigna esfuerzo también a B aunque su producción inmediata no aumente CES;
esa acción produce experiencia MIS-v2 y eleva B/y para periodos siguientes.
La reacción existente no lo hace por su desempate fijo entre acciones con
igual CES inmediato. Por tanto, los contrafactuales confirman que la
trayectoria de trabajo genera aprendizaje útil, pero el valor numérico frente
a esta reacción incluye la resolución de empates y no demuestra ventaja
estricta frente a toda política miope que escogiese favorablemente entre
acciones inmediatamente óptimas. En el centro, la ganancia de Bellman sin
transferencia no requiere elegir una acción de menor CES inmediato; con
transferencia sí hay un sacrificio inicial estricto.

**CES y servicio no son equivalentes.** En el centro, `J_B` aumenta CES en
`.0115123706` respecto a `J_A`, pero los diagnósticos exactos dan servicios
completados esperados `3.000` frente a `3.001`, fallos `1.000` frente a
`.999`, déficit raw total `.175` frente a `.04995` y déficit normalizado
`.5` frente a `.05258`. Bellman con transferencia hace una acción docente,
consume `.5` de recurso docente y reduce el esfuerzo productivo acumulado de
8 a 7; el total utilizado es 7.5. La mejora CES, pues, no mejora el
cumplimiento funcional agregado: cambia dónde se incurre en déficit, del
cuello de botella futuro y al servicio inicial x. Esto impide describir el
resultado como mejora inequívoca del servicio.

**Robustez local y controles.** La ventaja de planificación sin transferencia
permanece positiva en las ocho perturbaciones (`.1029204` a `.1534059`). El
incremento de transferencia permanece positivo en seis de ocho; se anula en
`P(y|x)=.85` y eficacia `.70`, donde Bellman no enseña. En el control `T=3`,
con opción física de enseñar, transferencia aporta cero; en el control con x
absorbente, las cuatro políticas coinciden (`2.8604896`). El efecto de
transferencia es por tanto sensible al retorno y eficacia, mientras que la
ventaja observada de planificación frente al desempate miope se mantiene en
esta vecindad. Son soluciones exactas de una familia pequeña, no réplicas
estadísticas ni robustez global.

**Conclusiones obligatorias.** (A) El valor de planificación se explica por
anticipar el régimen y por producir experiencia MIS-v2 en B/y cuando esa
experiencia tendrá utilidad; el valor medido también depende del desempate de
la reacción. (B) El valor de transferencia surge de desarrollar antes B/y,
pagando producción presente y recursos docentes, para elevar CES futuro en
ramas y. (C) Hay interacción positiva en el centro y en seis perturbaciones,
pero vale cero en dos; no se generaliza como complementariedad universal.
(D) La planificación exacta conserva valor CES en la vecindad analizada;
el valor adicional de transferencia depende de suficiente probabilidad de
demanda y eficacia docente. (E) No: la ganancia CES central no se traduce en
ganancia de cumplimiento funcional agregado y el déficit diagnóstico
aumenta. (F) Limitan la generalización el estado real conocido por estos
oráculos, una sola instancia base y vecindad OAT, `T=4`, la matriz C5 y las
leyes físicas particulares; además, el comparador miope usa un desempate
fijo.

**Clasificación:** fenómeno condicionado a un régimen, no robusto de forma
general. La planificación exacta conserva valor CES en la vecindad analizada;
el valor adicional de transferencia depende de suficiente probabilidad de
demanda y eficacia docente, y puede entrar en conflicto con el éxito
funcional. No se afirma novedad científica.

La validación focalizada pasó: `PYTHONPATH=src:. pytest -q
tests/synthetic/test_hls_s7_uncertain_demand.py
tests/synthetic/test_hls_s7_mechanistic_robustness.py` (`14 passed`). También
pasó `git diff --check`. El runner guarda cuatro valores, descomposiciones,
ramas y métricas funcionales/recursos; las pruebas verifican la identidad de
contrastes, el registro de las ramas, la consistencia CES-métricas y que no
haya enseñanza en configuraciones sin transferencia. No se modificaron leyes
físicas ni resultados históricos.

## 2026-10-22 — Auditoría conceptual del rendimiento colectivo

Se añadió [`HLS_COLLECTIVE_PERFORMANCE_AUDIT.md`](../architecture/HLS_COLLECTIVE_PERFORMANCE_AUDIT.md), una revisión documental de la definición de rendimiento colectivo en HLS. No se modificaron código, objetivos implementados ni artefactos históricos, y no se ejecutaron campañas.

**Hechos verificados.** En N×K, `productive_outputs_nk` calcula `y_k=Σ_i e_ik c_ik`; CES es `(Σ_k w_k y_k^ρ)^(1/ρ)` (`ρ=.5` por defecto) y no usa los requisitos funcionales. `evaluate_problem_nk` calcula por separado éxito, déficit truncado, déficit normalizado sumado y margen. Recursos y esfuerzo restringen factibilidad, pero no se restan de CES. MIS-v2/enseñanza modifican el estado después de registrar producción y reward. Bellman S4/S7 optimiza CES; P0/P1/P2 utilizan la jerarquía lexicográfica éxito, déficit normalizado, margen y esfuerzo, más sus reglas docentes. S7 miope maximiza CES inmediato y resuelve empates por primer candidato con tolerancia `1e-12`.

**Diagnóstico.** En S7 central, Bellman con transferencia aumenta CES `3.1628653621→3.1743777327`, mientras servicios esperados cambian `3.001→3.000` y déficit absoluto `.04995→.175`. Es coherente con objetivos diferentes: el coste docente desplaza producción presente y la mejora productiva futura afecta CES, pero CES no impone requisitos. La auditoría también identifica que el valor de planificación medido frente al miope puede depender del desempate entre acciones de igual CES inmediato; para atribuir valor estricto de foresight se debe distinguir del comparador BEST-MYOPIC/tie-set. Los resultados S4/S7 no justifican una noción universal de rendimiento basada exclusivamente en CES.

**Recomendación y decisión pendiente.** Mantener CES como objetivo válido en las referencias donde fue declarado y reportar funcionalidad/déficit/recursos separadamente. Para el marco HLS, declarar por configuración objetivo primario, restricciones, costes explícitos y diagnósticos, sin pesos arbitrarios ni doble conteo. Antes de cambiar código o ampliar S7, el PI debe decidir si el problema prioriza output CES, cumplimiento funcional o una jerarquía/constrained formulation, y confirmar el comparador reactivo tie-aware requerido. No se implementó ni probó ninguna alternativa.

## 2026-10-22 — HLS-PEF, fase 1: especificación científica y arquitectura conceptual

Se creó [`HLS_PERFORMANCE_EVALUATION_FRAMEWORK.md`](../architecture/HLS_PERFORMANCE_EVALUATION_FRAMEWORK.md) como catálogo extensible y protocolo de evaluación, sin definir una puntuación ni un objetivo universal. Se preservan los niveles A (sistema), B (modalidad organizativa) y C (arquitectura de decisión), y se declaran por separado problema, objetivo, restricciones, métricas colectivas, diagnósticos y contrastes entre políticas. Esta fase fue exclusivamente documental: no se cambiaron código, funciones objetivo ni resultados S1–S7, y no se ejecutaron experimentos.

**Auditoría y rectificación de alcance.** Se contrastaron las definiciones con las implementaciones de asignación S1–S3, producción N×K, MIS-v2, transferencia, S4 y S7. Recompensa de matching, reward Bernoulli, output, CES, éxito funcional, déficit, esfuerzo y competencia futura tienen unidades y semánticas diferentes. En particular, el S4 canónico inicial de asignación binaria optimiza `Σ c_ik x_ik`; las referencias posteriores S4 de producción/transferencia N×K optimizan CES. La auditoría conceptual precedente había usado «S4» demasiado ampliamente al hablar de CES; se conserva su entrada histórica y se precisa aquí el alcance, sin alterar sus resultados. En S7, la mejora central CES `3.1628653621→3.1743777327` coexistió con servicios esperados `3.001→3.000` y déficit absoluto `.04995→.175`: no es una mejora inequívoca del servicio. Como los pesos CES de esa instancia recaen en la competencia demandada, la divergencia procede de umbrales, agregación temporal y esfuerzo reasignado, no de sustitución simultánea entre competencias dentro del CES de un periodo.

**Especificación HLS-PEF.** El núcleo propuesto incluye cumplimiento funcional (micro y equilibrado por tipo), calidad específica, déficit, coste y eficiencia de recursos, evolución temporal, robustez, adaptación y ganancia frente a referencias, con contrato de unidad, denominador, orientación, información requerida, agregación, incertidumbre y casos indefinidos. Calidad, robustez y adaptación necesitan contratos de aplicación o perturbación; no reciben una fórmula universal. El `EvaluationProfile` conceptual distingue `no_aplicable`, `no_disponible`, `no_medido` y cero medido, y registra separadamente información de política y verdad accesible solo al evaluador. Se proponen perfiles mínimos S1–S7 y tres niveles de comparabilidad: políticas en una misma instancia, instancias de un escenario y aplicaciones distintas. La analogía con accuracy/balanced accuracy/precision/recall/F1 solo se usa cuando están definidos sus denominadores y errores; no se trasladan nombres mecánicamente.

**Decisiones pendientes del PI.** Fijar la unidad de servicio y el tratamiento de tareas parciales/multiagente; decidir por problema si CES, cumplimiento o déficit será objetivo y qué requisitos serán restricciones; definir de dónde proceden prioridades y precios de recursos; acordar comparadores sensibles a empates para nuevas afirmaciones de planificación; y aprobar el perfil mínimo antes de implementar. La opción técnica posterior, aún no autorizada, es una capa de evaluación offline y de solo lectura sobre artefactos existentes, con pruebas de casos degenerados y sin reescribir campañas históricas.

## 2026-10-22 — HLS-PEF, fase 2: implementación mínima y validación retrospectiva

Se implementó [`performance_evaluation.py`](../../src/hls/performance_evaluation.py) como capa de evaluación independiente de física y políticas, con `EvaluationProfile`, `EvaluationRecord`, `EvaluationResult`, estados explícitos de disponibilidad y una API de registro, agregación, importación histórica y comparación compatible. La especificación técnica y los límites figuran en la [sección 11 de HLS-PEF](../architecture/HLS_PERFORMANCE_EVALUATION_FRAMEWORK.md#11-fase-2--implementación-mínima-y-validación-retrospectiva-2026-10-22). No se cambiaron objetivos, leyes, políticas ni resultados anteriores.

**Auditoría previa.** El [S4 exacto N×K](../../results/experiments/hls_s4_transfer_exact/results.json) guarda tres periodos completos de A/B; se pueden recalcular CES, éxito, déficit absoluto, output y recursos. La [caracterización S7](../../results/experiments/hls_s7_preparation_characterization/results.json) solo guarda algunas ramas ilustrativas además de sus valores exactos; la [validación mecanística S7](../../results/experiments/hls_s7_mechanistic_robustness/results.json) conserva expectativas funcionales y de recursos agregadas. No es posible reconstruir desde esas ramas el árbol completo ni `Σoutput` S7; esa métrica se marca `NOT_RECORDED`. Las expectativas S7 se importan con punteros de procedencia, sin presentarlas como cálculos desde periodos inexistentes.

**Resultados retrospectivos.** El [runner de solo lectura](../../experiments/run_hls_pef_retrospective.py) generó un [resultado separado](../../results/experiments/hls_pef_retrospective/results.json). Desde periodos S4 se obtuvieron para A/B CES `1.9175`, cumplimiento `1/3`, déficit absoluto `.5325` y producción `1.9175`. Desde agregados históricos S7 central se verificaron `J_A=3.1628653621`, `J_B=3.1743777327`, `J_MA=J_MB=3.0346209871`; planificación sin/con transferencia `.1282443750/.1397567456`, transferencia con/sin planificación `.0115123706/0`, interacción `.0115123706`. La tasa funcional esperada A/B es `.75025/.75000` y el déficit absoluto `.04995/.175`; no se infiere mejor servicio de la ganancia CES. La igualdad S4 entre CES y suma de outputs es específica de sus pesos por periodo.

**Validación y límites.** Las [pruebas PEF](../../tests/test_hls_performance_evaluation.py) cubren agregación, unidades, denominador nulo, cinco estados, cero medido, comparaciones incompatibles, regímenes informacionales desiguales, procedencia y regresión histórica; `6 passed`. Las pruebas focalizadas existentes S4/S7 pasaron (`28 passed`), sin reejecutar campañas. El módulo no calcula calidad externa, eficiencia, robustez ni adaptación sin contratos/datos adicionales. Antes de integrarlo en nuevos escenarios el PI debe fijar la unidad de servicio, los perfiles primarios y los registros mínimos de evaluador; no se amplió la implementación ni se hizo commit/push.

## 2026-10-22 — HLS-PEF, fase 3: integración operativa y piloto S7

Se amplió el contrato `EvaluationRecord` para incluir ID de unidad, tipo de tarea, importancia, calidad opcional, episodio/rama y probabilidad, régimen informacional, objetivo de decisión, competencias y estados por campo, conservando compatibilidad con sus campos posicionales originales. El adaptador [`s7_pef_adapter.py`](../../src/hls/synthetic/s7_pef_adapter.py) convierte replays ya calculados; el [runner de piloto](../../experiments/run_hls_pef_s7_pilot.py) obtiene los cuatro resultados S7 centrales y evalúa las 16 ramas T=4 con sus probabilidades exactas. `evaluate_weighted_episodes` agrega los registros sin afectar la selección de acciones.

**Perfil y resultados.** Se declaró unidad de servicio tarea-periodo; CES acumulado como objetivo de las cuatro referencias; cumplimiento y déficit como principales; producción, esfuerzo productivo/docente, consumo docente `2h`, recurso total y acciones docentes como secundarias; competencias y decisiones como campos diagnósticos. El output del piloto nuevo reproduce A/B/MA/MB: CES `3.1628653621/3.1743777327/3.0346209871/3.0346209871`; cumplimiento por periodo `.750250/.750000/.3019375/.3019375`; déficit absoluto `.049950/.175000/.10235756/.10235756`. Esfuerzo productivo `8/7/5.20775/5.20775`, esfuerzo docente `0/.25/0/0`, consumo docente `0/.5/0/0`, recurso total `8/7.5/5.20775/5.20775`, y acciones docentes `0/1/0/0`. Diferencias e interacciones se guardan por métrica y unidad; no hay escalar agregado. El resultado está en [`hls_pef_s7_pilot/results.json`](../../results/experiments/hls_pef_s7_pilot/results.json), separado de los artefactos históricos.

**Integridad y límites.** Las ramas suman probabilidad `1.0`; el CES ponderado reproduce el valor exacto de cada solucionador a `1e-10`. La prueba confirma repetibilidad, identidad de objetivos, contabilidad `total = producción + recurso docente` y retención de decisiones/estados en trazas. Calidad externa e importancia no están definidas por S7 y se marcan `NOT_APPLICABLE`; no se inventan. La caracterización es exacta para la instancia central, no una campaña ni validación estadística nueva. Pasaron las pruebas PEF (`8 passed`) y las pruebas focalizadas existentes S4/S7 en conjunto (`36 passed`). `git diff --check` pasó. No se modificaron las políticas ni leyes físicas, ni se sobrescribieron resultados anteriores.

## 2026-10-23 — S7: auditoría BEST-MYOPIC de desempates

**Pregunta y diseño.** Se comprobó si la ventaja CES de Bellman sobre el miope histórico persistía frente a un comparador reactivo que maximiza el mismo CES inmediato y desempata favoreciendo el incremento positivo inmediato de competencias bajo MIS-v2/transferencia. Se utilizó exclusivamente la instancia central S7 C5, `T=4`, con enumeración exacta de las 16 trayectorias de demanda. BEST-MYOPIC no consulta demanda futura ni valores Bellman; en el régimen exacto existente recibe el estado de competencia actual y demanda usados por las referencias S7. Si persiste empate secundario, selecciona por clave canónica independiente del orden del catálogo.

**Auditoría de implementación.** El miope original recorre el catálogo y cambia la acción vigente solo cuando `reward > best_reward + 1e-12`; por tanto, el primer candidato resuelve empates de CES dentro de esa tolerancia. CES se obtiene mediante la transición `_step`; MIS-v2 y la transferencia actualizan competencias después de la decisión y las acciones empatadas también pueden diferir en output y recursos. La auditoría compara los estados alcanzados por MA/BMA y MB/BMB. En cada variante examinó 32 estados: 16 tenían varias acciones empatadas y en los 16 la acción elegida difería. En los 16 estados empatados hubo sucesores de competencia distintos y diferencias de output o recursos (clases B y C no excluyentes); ninguno tuvo consecuencias físicas equivalentes (clase A).

**Resultados exactos HLS-PEF.** Se reprodujeron los valores históricos: CES A=`3.1628653621`, B=`3.1743777327`, MA=`3.0346209871`, MB=`3.0346209871`. BEST-MYOPIC obtuvo BMA=BMB=`3.0444737839`. Cumplimiento esperado A/B/MA/MB/BMA/BMB: `.750250/.750000/.3019375/.3019375/.3019375/.3019375`; déficit absoluto: `.049950/.175000/.10235756/.10235756/.10235756/.10235756`. Esfuerzo productivo: `8/7/5.20775/5.20775/8/8`; esfuerzo docente: `0/.25/0/0/0/0`; recurso docente: `0/.5/0/0/0/0`; acciones docentes: `0/1/0/0/0/0`. Producción acumulada: `3.16757209/3.17437773/3.03462099/3.03462099/4.31819114/4.31819114`. Se mantienen métricas y unidades separadas; mayor producción no se interpreta automáticamente como mayor CES ni servicio.

La brecha histórica sin transferencia `D0=A−MA=.1282443750` se descompone contablemente en `D1=A−BMA=.1183915782` más `T0=BMA−MA=.0098527968`. Con transferencia, `D0T=B−MB=.1397567456`, `D1T=B−BMB=.1299039488` y `TT=BMB−MB=.0098527968`. Ambos residuos son cero. El desempate explica alrededor del 7.7% de la brecha histórica en esta instancia, pero la ventaja de Bellman frente a BEST-MYOPIC persiste. No se interpreta `T0/TT` como efecto causal independiente de las trayectorias inducidas. La interacción planificación×transferencia respecto a BEST-MYOPIC es `.0115123706` en CES: B−BMB menos A−BMA.

**Mecanismo intertemporal.** Sin transferencia Bellman no escogió acciones estrictamente inferiores al máximo inmediato en los estados de su trayectoria óptima. Con transferencia lo hizo en un estado de probabilidad de ocupación uno: `t=0`, `task-x`, competencia `[[.05,.9],[.3,0]]`. Eligió producir `.5` por agente y enseñar A→B/y con esfuerzo `.25`: CES inmediato `.175` frente a `.35`, sacrificio `.175`; la competencia B/y posterior aumenta `.08`. Bajo continuación Bellman, el valor Q de esa acción es `3.1743777327`, frente a `3.1628653621` al sustituirla por la acción BEST-MYOPIC inmediata; ventaja Q local `.0115123706`. Es una sustitución de una etapa bajo continuación Bellman, no una descomposición aditiva completa del efecto de política.

**Interpretación y límites.** El desempate fijo explica una fracción pequeña pero verificable de la brecha; no la elimina. Bellman conserva ventaja CES contra BEST-MYOPIC en esta instancia. La acción que enseña muestra anticipación intertemporal estricta en la variante con transferencia. BEST-MYOPIC mantiene el cumplimiento y déficit del miope original; tampoco se infiere que la ventaja CES de Bellman sea mejora de servicio, ya que B presenta mayor déficit que A. La evidencia es exacta para una sola instancia, sin incertidumbre estadística ni generalización. El criterio secundario es un comparador diagnóstico, no una política universal recomendada.

**Artefactos y validación.** El [informe de auditoría](../experiments/HLS_S7_MYOPIC_TIEBREAK_AUDIT.md) documenta definición, seis políticas, decisiones empatadas, descomposiciones y límites. El [runner](../../experiments/run_hls_s7_myopic_tiebreak_audit.py) guarda en una ruta nueva el árbol ponderado, métricas HLS-PEF con procedencia y decisiones por estado: [`results.json`](../../results/experiments/hls_s7_myopic_tiebreak_audit/results.json). La extensión de `hls_s7_uncertain_demand.py` conserva la selección histórica y añade BEST-MYOPIC, auditoría y valores Bellman por estado para el contrafactual Q; no cambia leyes físicas ni resultados antiguos. Pasaron las pruebas S7/PEF focalizadas (`25 passed`), incluida reproducción de cuatro valores, acción inmediata óptima, independencia del orden del catálogo para desempates secundarios distintos, árbol/procedencia, identidades contables y sacrificio inmediato. `git diff --check` se ejecutó tras documentar. No se inició otra campaña ni se hizo commit/push.

## 2026-10-23 — S7: selección anticipativa frente a BEST-MYOPIC

Se mantuvo el caso central `T=4` sin transferencia y se añadió el control reactivo **CURRENT-DEMAND-MYOPIC (CDM)**: maximiza CES inmediato y desempata maximizando incrementos MIS-v2 en las competencias con requisito positivo en la demanda corriente; no recibe la ley futura C5. Se compararon Bellman (A), miope histórico (MA), BEST-MYOPIC (BMA) y CDM mediante enumeración exacta y HLS-PEF. De las 16 secuencias combinatorias, 8 tienen probabilidad positiva desde el estado inicial; solo esas forman el árbol de soporte de esta entrada.

**Resultados.** CES A/MA/BMA/CDM=`3.1628653621/3.0346209871/3.0444737839/3.1628653621`; cumplimiento=`.750250/.3019375/.3019375/.750250`; déficit absoluto=`.049950/.1023575625/.1023575625/.049950`. Por tanto A−BMA=`.1183915782`, A−CDM=`0`, BMA−CDM=`−.1183915782`. La ventaja de Bellman sobre BMA se reproduce, pero CDM alcanza el mismo CES, cumplimiento y déficit esperados que Bellman en este caso.

**Mecanismo.** La primera divergencia A/BMA con masa positiva ocurre en `t=1`, demanda y=.9 de probabilidad, después de una acción común en t=0/x. Con competencia `[[.24,.90],[.384,0]]`, ambos asignan esfuerzo total 2 y logran CES inmediato `.90`. Bellman actualiza `ΔC=[[0,.015],[0,.05]]`, total `.065` concentrado en y; BMA actualiza `[[0,.015],[.07392,0]]`, total `.08892` dirigido a B/x. La demanda y permanece y con probabilidad `.95`. Q bajo continuación Bellman favorece la acción de Bellman en `.085086302` en t=1 y `.04424752` en t=2, con rewards inmediatos iguales. Así, el mecanismo observado es la distribución organizativamente útil del aprendizaje; más incremento total no implica mayor continuación. CDM coincide con Bellman antes de la última decisión y elimina la brecha agregada; en t=3 difieren en un empate sin continuación, lo que muestra que aquí la ventaja A/BMA no demuestra una necesidad exclusiva de usar previsiones futuras.

**Descomposición y verificación.** Se comprobó la identidad finita `J_A−J_π = E_π[Σ_t(V_A(s_t,d_t)−Q_A(s_t,d_t,a_t))]` con valores Bellman sin poda usados solo como tabla contrafactual. Para BMA, ambos lados son `.1183915782`, residuo `4.2×10⁻¹⁶`; contribuciones ponderadas por ocupación: t1 `.0765776718`, t2 `.0418139064`, t0/t3 cero. Para MA la suma es `.1282443750` (residuo `8.3×10⁻¹⁷`); para CDM es cero. El JSON registra estados y ocupaciones por política, acciones, CES, matrices de incrementos y Q; las ocupaciones suman uno en cada periodo. No hubo sacrificio estricto de CES inmediato por Bellman sin transferencia.

**Límites y artefactos.** La evidencia es exacta para una única instancia C5 y horizonte corto; no incluye incertidumbre estadística ni generaliza a otras dinámicas. CDM es un control mecanístico, no una nueva política general. El [informe](../experiments/HLS_S7_ANTICIPATORY_SELECTION_AUDIT.md), [runner](../../experiments/run_hls_s7_anticipatory_selection_audit.py), [resultado](../../results/experiments/hls_s7_anticipatory_selection_audit/results.json) y [pruebas](../../tests/synthetic/test_hls_s7_anticipatory_selection.py) se añadieron en rutas nuevas. La matriz de incrementos, valores Q, reproducción histórica, probabilidades, PEF y lema de diferencia de rendimiento se verifican automáticamente. Las pruebas focalizadas S7/PEF pasaron (`28 passed`); queda ejecutar `git diff --check` final. No se alteraron artefactos históricos ni se inició otra campaña.

## 2026-10-23 — Revisión integral del plan y consolidación del laboratorio HLS

**Objetivo y alcance.** Por indicación del PI, se recuperó el plan original,
se reconstruyó su evolución hasta esta fecha y se contrastó la capacidad
documentada con código, pruebas y artefactos. La prioridad actual es construir
el laboratorio HLS como flujo reutilizable; no se busca demostrar todavía la
superioridad general de una organización o mecanismo. Esta revisión es
documental: no cambia código, escenarios, políticas ni resultados, y no
ejecuta pruebas ni campañas.

### Plan original y trazabilidad de cambios

La línea base operativa del 17/10 conservaba un calendario de 19–30/10:
auditoría de memoria; selección de literatura; prioridades; análisis
matemático; ontología; reutilización; reproducibilidad/comparabilidad;
memorando de novedad; diseño preliminar; y cierre GO/REFRAME/STOP. El plan
original no fijaba umbrales cuantitativos de aceptación, presupuesto de
campaña ni dependencias detalladas; su calendario no autorizaba ejecutar
experimentos. La integración Nembhard Direct/router se adelantó y acotó por
decisiones documentadas del 17/10; la reproducción integral e indirecta quedó
aplazada. El hito original de novedad fue retirado del calendario operativo
por instrucción expresa del PI. El documento histórico y la reconstrucción
de ese plan se mantienen sin reescritura: [línea base y registro](HLS_LAB_EXECUTION_PLAN_2026-10-17.md),
[reconstrucción original](../project/HLS_ORIGINAL_WORK_PLAN_TO_2026-10-30.md).

Las fechas siguientes son fechas de registro disponibles, no timestamps
independientes de ejecución. Las entradas del 20–23/10 no documentan horas de
inicio/fin. La cronología, rectificaciones incluidas, está consolidada en
[HLS_LAB_ROADMAP_CURRENT.md](HLS_LAB_ROADMAP_CURRENT.md): el 20/10 se
establecieron referencias finitas S1–S4 y resultados de S3a/S3b; entre
20–21/10 se revisaron protocolos y líneas S3b, preservando resultados
negativos y la distinción entre campaña completada y línea científica abierta;
entre 20–22/10 se expandió S4 desde MIS-v2 a transferencia y planificación,
incluida la corrección del comparador miope sensible a empates; el 22/10 se
desarrolló S7 con demanda Markov, preparación y robustez local, y se auditó
el significado de CES y servicio; HLS-PEF pasó de especificación conceptual a
módulo independiente, validación retrospectiva y un piloto integrado S7; el
23/10 se realizaron las auditorías BEST-MYOPIC y CURRENT-DEMAND-MYOPIC. La
secuencia y los artefactos por hito permanecen en las entradas anteriores y
no se reordenan aquí.

### Estado auditado por componentes

**A — Escenarios/sistemas.** S1 y S2a tienen instancias deterministas de
referencia y verificación solver/enumeración; S2b añade un presupuesto
intertemporal exacto; S3a cubre cambios exógenos observables y ruido; S3b
cubre recompensas desconocidas y feedback selectivo con varias políticas y
diagnósticos; S4 incluye el sistema N×K de MIS-v2/enseñanza/transferencia y
referencias exactas pequeñas; S7 añade demanda incierta Markov al sistema
endógeno. S5/S6 permanecen como candidatos documentales, no escenarios
implementados. La validación y limitaciones son locales a cada instancia; no
se infiere validez externa o una interfaz universal por la existencia de
simuladores separados.

**B — Organizaciones/problemas.** Hay instancias ejecutables de selección
individual B1, asignación B2 (matching bipartito y otras acciones N×K) y
planificación B3 (presupuesto compartido o transiciones endógenas). Los
contratos de acción y restricciones difieren entre rutas; binary matching,
unidades repetidas, esfuerzo divisible y enseñanza no son un único problema
intercambiable. No hay una API organizativa general que permita configurar
cualquier conjunto factible y seleccionar automáticamente un optimizador.

**C — Modelos/mecanismos.** Están implementados y probados, dentro de ámbitos
declarados, reglas reactivas, asignación exacta, Bellman finito, estimadores
bandit/contextuales, MIS-v2, transferencia, estimación N×K y referencias
Nembhard. BEST-MYOPIC y CURRENT-DEMAND-MYOPIC son controles diagnósticos S7,
no una política universal. Parte de los mecanismos son reutilizables como
funciones o componentes; las composiciones, estados, objetivos y vistas
informacionales siguen ligadas a escenarios concretos. Estimación de una
competencia desconocida y cambio de competencia real por experiencia son
procesos distintos.

**D — HLS-PEF.** La capa métrica tiene perfiles, registros y resultados
tipados, unidades, procedencia, estados explícitos de disponibilidad,
agregación exacta ponderada por probabilidad, importación de métricas
históricas y controles de comparabilidad. La validación retrospectiva no
reconstruye trayectorias ausentes. El piloto nuevo conecta S7 con PEF sin
participar en decisiones. Además, `experiment_contract.py` define un sobre
versionado y adaptadores no destructivos para resultados N×K seleccionados,
Nembhard y ruta contextual; explícitamente no es un ejecutor ni normaliza
magnitudes para hacerlas comparables. No todos los runners S1–S7 producen
todavía ese sobre o registros PEF. Por tanto, existe una integración de
referencia en S7 y piezas de contrato comunes, pero no un pipeline general
escenario→organización→mecanismos→ejecución→PEF.

### Madurez, decisión de consolidación y próximos hitos

La matriz de madurez del roadmap usa los estados **CONCEPTUAL, ESPECIFICADO,
IMPLEMENTADO, PROBADO, INTEGRADO y VALIDADO** con evidencia y alcance por
componente; no traduce código existente en integración general. Se adopta
como prioridad inmediata el **Hito 1: consolidar el contrato experimental
común**, partiendo de `ExperimentRun`, adaptadores y perfiles PEF existentes,
sin reescribirlos. Después: Hito 2, conectar una configuración A/B/C y un
perfil PEF mediante una ruta fina; Hito 3, validar reutilización en rutas ya
existentes distintas de S7; Hito 4, uniformar procedencia, reproducibilidad,
comparabilidad y validación de artefactos; Hito 5, preparar diseños
científicos de problemas organizativos relevantes. Cada hito tiene
dependencias y criterios verificables en
[el roadmap vigente](HLS_LAB_ROADMAP_CURRENT.md). Un diseño posterior no
autoriza una campaña sin decisión separada.

**Decisiones no asumidas.** Queda para el PI decidir el primer piloto de
reutilización fuera de S7 si S2a no conserva procedencia suficiente; el
formato/manifest común de los artefactos; los campos de revisión, semillas e
información obligatorios para runners heredados; y cuándo reanudar una línea
científica abierta como S3b. La presente revisión no cierra S3b ni reabre S4,
S7 u otras campañas. No se alteran objetivos científicos ya registrados.

**Resultado de esta revisión:** se recuperó la línea base y se hizo explícita
la brecha entre componentes funcionales probados por separado y el flujo
general todavía no integrado. El siguiente incremento recomendado es un
mapa de compatibilidad/contrato sobre las rutas actuales y un adaptador
mínimo solo donde el mapa demuestre una carencia, seguido de un vertical
slice de evaluación no-S7. Este documento y
[HLS_LAB_ROADMAP_CURRENT.md](HLS_LAB_ROADMAP_CURRENT.md) son los únicos
documentos modificados en esta actualización.

## 2026-10-23 — Hito 1, Incremento 1: auditoría y contrato experimental común

**Fecha del trabajo y del registro:** 23 de octubre de 2026; no se conservó
hora exacta. **Tipo:** auditoría y especificación documental. No se modificó
código ni se ejecutaron simulaciones.

### Trabajo y hallazgos verificados

Se inspeccionaron `src/hls/experiment_contract.py`,
`src/hls/performance_evaluation.py`, el adaptador y piloto PEF de S7, los
runners representativos S2a/S3b/S4/S7, y pruebas/resultados disponibles. El
contrato `ExperimentRun` versionado ya contiene identidad de mecanismo,
configuración, condiciones iniciales, semillas, régimen de información,
unidades, eventos, métricas, procedencia y resultado fuente; adaptadores
explícitos cubren solo algunas estructuras N×K, Nembhard y contextual. No es
un ejecutor ni todos los runners lo producen. PEF ya ofrece perfiles,
registros, resultados, estados de disponibilidad, agregación ponderada y
comparación semántica básica; no alinea semillas ni calcula intervalos
pareados. La única ruta nueva completa runner→adaptador→PEF verificada es
S7.

El contraste de rutas mostró semánticas que deben permanecer distintas:
S2a es determinista y separable, S3b tiene feedback selectivo y varios
protocolos, S4 mezcla dinámicas/objetivos N×K y exactos, y S7 usa ramas
Markov exactas ponderadas. El contrato común debe describir esas diferencias,
no homogeneizarlas. En particular, ausencia/no observabilidad no equivale a
cero, y recompensa original no equivale automáticamente a CES ni a servicio
funcional.

### Propuesta y decisión técnica

Se recomienda reutilizar `ExperimentRun` como sobre de réplica y
`EvaluationProfile` como configuración de evaluación, usando inicialmente
campos/mapas existentes para IDs canónicos de escenario, configuración,
problema organizativo y perfil. No se justifica todavía cambiar el schema ni
crear una segunda arquitectura experimental. Los vínculos entre perfil y run,
ID único de réplica y régimen informacional deben quedar explícitos en el
adaptador. `PerformanceEvaluator.compare` no sustituye el emparejamiento
estadístico.

S2a se recomienda como primer vertical slice no-S7: su regresión conocida
(exacto 8.0, greedy 7.2, enumeración global 8.0 y 84,388 secuencias) permite
validar el flujo sin nueva estocasticidad. El alcance PEF debe limitarse a la
recompensa de asignación; conteos de unidades/capacidad se conservan como
diagnósticos porque el catálogo PEF actual no contiene una métrica genérica
de cobertura por tipo. S2a no conserva
requisitos funcionales, producción física, CES ni déficit funcional; no se
deben inventar esas métricas. Si el PI exige cumplimiento funcional en el
primer slice, deberá elegir una ruta con requisitos registrados antes de
autorizar implementación.

### Estado, límites y siguiente paso

Se creó la especificación
[`HLS_EXPERIMENT_CONTRACT_INTEGRATION.md`](HLS_EXPERIMENT_CONTRACT_INTEGRATION.md),
con inventario, comparación de flujos, contrato mínimo, evaluación de
`ExperimentRun`/`EvaluationProfile`, recomendación S2a, límites y pruebas de
aceptación del Incremento 2. El roadmap vigente incorpora el estado de esta
auditoría y su decisión pendiente.

**Estado de Hito 1:** Incremento 1 (auditoría/especificación) documentado;
Incremento 2 (implementación del primer adaptador/vertical slice) no iniciado
y requiere autorización del PI. No se alteraron runners, políticas,
escenarios, métricas ni resultados históricos. No se ejecutaron pruebas porque
el cambio es exclusivamente documental; `git diff --check` es la validación
solicitada.

## 2026-10-23 — Hito 1, Incremento 2: integración vertical S2a con HLS-PEF

**Fecha del trabajo:** 23 de octubre de 2026; no se conserva hora exacta.
**Autorización:** GO del PI. **Objetivo:** ejecutar el S2a existente,
representar sus dos políticas con el contrato común y evaluar los registros
mediante HLS-PEF sin cambiar la asignación.

### Implementación

Se añadió `src/hls/synthetic/s2a_pef_adapter.py`, que valida la salida en
memoria de `run_s2a()` y crea un `ExperimentRun`/registros PEF por política.
La configuración conserva matriz, demanda, capacidad, horizonte, objetivo,
problema organizativo, información disponible, unidades y procedencia. Los
eventos por periodo retienen asignaciones, demanda, conteos satisfechos/no
servidos, capacidad y recompensa. El perfil PEF calcula recompensa original
y conteo de asignaciones; el desglose por tipo queda como diagnóstico. CES,
éxito funcional, déficit funcional y producción física se declaran
`NOT_APPLICABLE`, sin fabricar ceros.

Se añadió `ExperimentRun.from_dict()`/`from_json()` estricto para validar el
round-trip solicitado. No cambió el schema v1. El adaptador usa IDs distintos
para exacto y greedy, declara sin azar (`random_seeds=()`), y deja revisión de
software desconocida. La enumeración global continúa etiquetada como
referencia de optimalidad y no como política.

La auditoría encontró que el piloto S7 original guardó perfiles/resultados y
registros PEF, pero no emitió `ExperimentRun`. Se añadió a
`s7_pef_adapter.py` un conversor downstream del artefacto S7 existente al
sobre común. Este conversor no reejecuta S7 ni altera sus resultados. Las
pruebas rehidratan perfiles/registros archivados y vuelven a evaluarlos con
HLS-PEF, además de verificar el sobre común; queda explícito que la conversión
es posterior al runner S7, no una emisión nativa suya.

El runner integrado nuevo es
`experiments/run_hls_s2a_pef_integration.py`. Llama una vez a la función
existente `run_s2a()` sin invocar su bloque CLI de escritura del resultado
histórico; filtra timings descriptivos y genera únicamente
`results/experiments/hls_s2a_pef_integration/results.json`.

### Resultados y aceptación

La ejecución fresca reprodujo desde el runner fuente:

| Método | Recompensa acumulada | Rol en el análisis |
|---|---:|---|
| Asignación exacta | 8.0 | Política ejecutable |
| Greedy | 7.2 | Política ejecutable |
| Enumeración global | 8.0 | Referencia exhaustiva, no política |

La referencia examinó 84,388 secuencias. HLS-PEF reprodujo 8.0 y 7.2 con
unidad `declared_reward`; exacto−greedy es 0.8 para esta instancia. No se
interpreta como resultado general de algoritmo. El uso de capacidad se
representa como conteo de asignaciones; la distribución por tipo es
diagnóstica, no una métrica nueva del catálogo.

**Pruebas:** la suite conjunta focalizada ejecutó 63 pruebas y todas pasaron
(adaptador S2a, contrato común, PEF, asignación S1/S2a y pruebas sintéticas
S7). Incluye configuración/salida del runner, reconciliación de reward con
asignaciones, rechazo de datos incompletos, disponibilidad PEF, comparación
incompatible, pureza del evaluador, round-trip JSON, reejecución determinista
y compatibilidad estructural del artefacto S7. También se ejecutó el runner
integrado y se inspeccionó el artefacto nuevo. `git diff --check` se ejecutó
como verificación final.

### Conclusión, límites y decisión posterior

Incremento 2 queda **completado** para la ruta determinista S2a: el resultado
fuente permanece en su ubicación, no se alteraron políticas ni instancia y
PEF evalúa registros adaptados. El resultado histórico S7 tampoco se
sobrescribió. C9 se cumple estructuralmente con alcance limitado: S7 obtiene
`ExperimentRun` desde su artefacto guardado; el runner S7 original aún no
emite ese sobre. La prueba no cubre aprendizaje, feedback parcial,
reproducibilidad estadística ni una métrica PEF de cobertura por tipo.

Se recomienda como siguiente incremento técnico un adaptador a una ejecución
S4 N×K ya existente, para verificar traducción de producción, requisitos,
recursos y MIS-v2/enseñanza a perfiles PEF sin alterar políticas. Es solo una
recomendación; no se inició y requiere alcance/autorización posterior del PI.

## 2026-10-23 — Hito 2.1: auditoría semántica ejecutable de S4 N×K

**Fecha del trabajo:** 23 de octubre de 2026; no se conserva hora exacta.
**Autorización:** GO del PI. **Objetivo:** determinar si `ExperimentRun` v1 y
HLS-PEF preservan la semántica de una ejecución S4 con producción,
requisitos funcionales y recursos, antes de autorizar su integración.

### Instancia y evidencia examinadas

Se tomó la referencia determinista existente S4 exacta, dos agentes × dos
competencias, `T=3`, demanda conocida `x,y,y`, con Bellman sin transferencia
(A) y transferencia opcional (B). Se inspeccionaron `make_case`, el solver
exacto, leyes N×K de producción/MIS-v2/transferencia, resultados históricos,
el recálculo retrospectivo HLS-PEF, el contrato común y los perfiles. La
auditoría detallada y su matriz semántica están en
[`HLS_S4_SEMANTIC_INTEGRATION_AUDIT.md`](HLS_S4_SEMANTIC_INTEGRATION_AUDIT.md).

Las pruebas recalcularon A/B sin invocar el escritor del runner: ambos valores
son `1.9175000000000004`, coinciden con enumeración independiente y la
transferencia de eficacia cero reproduce A. Las decisiones y estados de
competencia por periodo coinciden con el artefacto histórico. No se modificó
ni sobrescribió ese artefacto.

### Hallazgos semánticos

Producción es `y_k=Σ_i e_ik c_ik`; no equivale en general a esfuerzo,
competencia, recompensa ni cumplimiento. El éxito exige alcanzar todos los
requisitos activos con la tolerancia física existente; el déficit es
`(q_k-y_k)_+`. En la trayectoria se observa un periodo con producción x
positiva y cumplimiento, y dos periodos con producción y positiva pero
servicio funcional fallido. CES/recompensa suma `1.9175`; aquí coincide
numéricamente con producción por los pesos de la instancia, pero no incluye
requisitos ni coste de recursos. El esfuerzo productivo total es `6`, el
recurso docente `0` y el total `6`, frente a capacidad efectiva `2` por
periodo. La unidad `effort` es abstracta del modelo.

El recálculo HLS-PEF desde el artefacto da por política: reward/CES `1.9175`,
tasa funcional `1/3`, déficit absoluto acumulado `0.5325`, producción
acumulada `1.9175`, esfuerzo productivo `6`, recurso docente `0` y recurso
total `6`; estados y unidades se verifican en las pruebas. Producción por
agente se deriva exactamente de acción y competencia previa, pero no es una
métrica de calidad individual. No se añadió una métrica ni un campo al
contrato.

### Pruebas, límites y decisión

Se añadió una prueba focalizada de caracterización que cubre regresión,
producción, separación output/éxito/reward, recursos, recálculo PEF y
round-trip estructural `ExperimentRun` v1. El caso exacto ve competencias
reales y conoce la secuencia completa; no representa las políticas S4 N×K
parcialmente observadas. Esta comprobación prueba compatibilidad semántica
colectiva de una referencia, no integración permanente ni validez para todas
las rutas S4. No se encontró insuficiencia del contrato o del catálogo PEF:
la brecha restante es un adaptador que una configuración/requisitos por
periodo con eventos y registros ya representables.

**Decisión recomendada al PI:** GO acotado para Hito 2.2 sobre esta ruta
determinista, sujeto a preservar explícitamente su régimen de información y
sin presentarla como ejecución de política parcialmente observada. Hito 2.2
no se inició en este trabajo; requiere autorización independiente. No se
modificaron runner, políticas, transición física, objetivo, `ExperimentRun`,
HLS-PEF ni resultados históricos. Se ejecutaron pruebas focalizadas y
`git diff --check`.

## 2026-10-23 — Hito 2.2: integración operativa S4 N×K con ExperimentRun y HLS-PEF

**Fecha del trabajo:** 23 de octubre de 2026; no se conserva hora exacta.
**Autorización:** GO del PI. **Objetivo:** ejecutar la referencia exacta S4
auditada y demostrar que el contrato común y HLS-PEF preservan sus magnitudes
colectivas, sin crear otra arquitectura experimental.

### Implementación

Se añadió [`s4_pef_adapter.py`](../../src/hls/synthetic/s4_pef_adapter.py),
que consume `ExactResult` del solver existente y produce un `ExperimentRun`
v1 más `EvaluationRecord` por periodo. Registra decisión, transición
MIS-v2/transferencia y ejecución como eventos separados; mapea output,
requisito, éxito, déficit, CES/reward, competencias, incrementos, esfuerzo
productivo, esfuerzo docente `h`, recurso docente `2h`, total y ociosidad.
No decide, reproduce física ni modifica el solver. La información completa
(competencias reales y secuencia determinista de demanda conocida) y la
procedencia están declaradas.

El runner
[`run_hls_s4_pef_integration.py`](../../experiments/run_hls_s4_pef_integration.py)
ejecuta A y B con `make_case()` y `solve_bellman()` originales, serializa los
sobres v1 y aplica dos perfiles al mismo conjunto de registros. El perfil
básico incluye recompensa original/CES, producción, cumplimiento y déficit;
el ampliado añade los recursos separados y acciones docentes. No se cambió
`ExperimentRun` ni el catálogo PEF.

### Resultados y regresión

El nuevo artefacto se guardó en
[`results/experiments/hls_s4_pef_integration/results.json`](../../results/experiments/hls_s4_pef_integration/results.json).
Para A y B reproduce reward `1.9175000000000004`, producción `1.9175`,
cumplimiento `1/3`, déficit acumulado `.5325`, esfuerzo productivo `6`,
esfuerzo docente `0`, recurso docente `0`, total `6` y cero acciones docentes.
La diferencia PEF A−B en reward es `0` dentro de `1e-12`. Los identificadores
y unidades de reward (`declared_reward`) y producción (`output`) se conservan
distintos pese a la coincidencia numérica local. La selección de perfil se
verificó como evaluación de solo lectura sobre un mismo run/traza.

### Reutilización, validación y alcance

La comprobación transversal reusa `ExperimentRun`, `EvaluationProfile`,
`EvaluationRecord` y `PerformanceEvaluator` para S2a/S4/S7, conservando sus
perfiles y semánticas diferentes. S2a usa su runner determinista en memoria
para generar records completos; S7 se reevalúa desde las 16 ramas ya
guardadas. Los artefactos históricos S2a/S7 y el resultado fuente S4 no se
sobrescribieron. El artefacto nuevo registra hash del solver antes/después y
la revisión base Git, el estado dirty/clean y hashes de solver, adaptador y
runner; cuando el árbol está modificado, `software_revision` se deja nulo en
vez de atribuir el resultado al commit base. Su salida es determinista.

Se ejecutaron **69 pruebas** de integración S4, caracterización S4, solver
exacto S4, demanda S7, PEF, contrato común e integración S2a; todas pasaron.
También se ejecutaron el runner integrado y `git diff --check`. La integración
valida una tercera familia semántica, no una ejecución parcialmente observada
P0/P1/P2 ni el efecto de una transferencia utilizada: B ofrece enseñar, pero
la solución óptima no enseña. S2a, S4 y S7 comparten estructuras, no una
interpretación forzada de sus métricas.

**Cierre:** C1–C10 del Hito 2.2 se consideran cumplidos en el alcance de esta
referencia exacta. Hito 2.2 queda completado como integración acotada; quedan
fuera P0/P1/P2, transferencia efectiva y un ejecutor universal. No se inició
campaña científica ni otra ruta S4.

## 2026-10-23 — S3b: recuperación y reproducción instrumentada de memoria × dinámica × observabilidad

**Fecha del trabajo:** 23 de octubre de 2026; no se conserva hora exacta.
**Autorización:** GO del PI. **Alcance:** una reproducción factorial acotada,
sin modificar otras campañas ni escenarios.

### Estado S3b recuperado

El modelo representa competencias Bernoulli desconocidas que cambian
exógenamente en un sistema de 3 agentes × 3 tareas. El problema organizativo
es B2, matching completo uno a uno con los mismos seis matchings factibles.
El feedback es semi-bandit selectivo: solo se aprende de una pareja ejecutada
si su oportunidad exógena está disponible. No hay demanda funcional, coste
independiente de recursos ni métrica de servicio en esta instancia.

El runner compara UCB1 y SW-UCB con PairwiseBanditEstimator y matching exacto.
UCB1 usa media por pareja más sqrt(2 log(max(2,t+1))/n). SW-UCB usa una
ventana temporal global W=1214 y bonus sqrt(xi log(max(2,min(t+1,W)))/n),
xi=2. Es una adaptación por pareja a matching combinatorio; no se atribuyen
a la composición garantías del bandit de selección individual.

Los antecedentes incluyen B1/E1, B2-Semi, factorial cambios × observabilidad,
replay offline e intervención de subsidio. Son diseños distintos. El factorial
anterior favoreció UCB1 en sus cuatro celdas y no encontró interacción
concluyente frecuencia × disponibilidad en regret (+27.04; IC95%
[-17.58,71.66]). Sus trazas no guardaban outcomes Bernoulli individuales ni
estimaciones/índices temporales. La secuencia UCB1/SW-UCB había quedado
aparcada; esta ejecución registra la prioridad GO actual del PI y no reescribe
esa decisión histórica.

### Diseño ejecutado

Se conservaron los cuatro niveles ya especificados: cambios infrecuentes cada
2500 periodos o frecuentes cada 500; oportunidad de feedback por pareja-periodo
alta p=.75 o baja p=.25. En ambas matrices solo cambia la competencia (2,0),
que alterna .4 ↔ .9; los demás valores se mantienen. La alternancia recurrente
cambia el matching óptimo. Horizonte 10000, calibración de nueve periodos,
xi=2, W=1214, recompensa Bernoulli y oráculo exacto de reward esperado
permanecieron fijos.

Se ejecutaron 30 semillas emparejadas nuevas (9000–9029), independientes de
las históricas 8200–8229. Los flujos pre-generados de outcomes y máscaras de
oportunidad son independientes entre sí y comunes por semilla a ambas políticas
y a los niveles factoriales; los umbrales .25/.75 son anidados. Un outcome
ejecutado cuenta para reward aunque no haya feedback; solo las parejas
ejecutadas y observadas actualizan el estimador. La política no ve competencias
reales, máscara previa ni demanda futura. El oráculo solo se usa en evaluación.

La separación del flujo se mantuvo verificable: A (escenario) contiene
competencias, transiciones exógenas, outcomes y mecanismo de observación; B
(problema organizativo) mantiene el matching completo y sus seis acciones;
C (mecanismo) intercambia UCB1/SW-UCB sobre la misma ruta de ejecución; D
(HLS-PEF) evalúa reward esperado desde registros adaptados, sin seleccionar
acciones ni actualizar estados. La observabilidad es una propiedad de A
intervenida exógenamente, mientras que las observaciones efectivas dependen
también de las asignaciones.

La instrumentación opcional registra por periodo decisiones, outcomes,
feedback, medias, conteos, bonus, índices, régimen y rewards/regret. Una prueba
de episodio corto confirmó que activar el registro no cambia el resumen de la
ejecución. El régimen real aparece únicamente como diagnóstico retrospectivo.

### Resultados observados

Se completaron 240 réplicas: 4 celdas × 2 políticas × 30 semillas. La tabla
muestra medias; el contraste SW-UCB menos UCB1 es pareado por semilla. IC95%
t sobre las 30 semillas.

| Cambios / oportunidades | Reward UCB1 | Reward SW-UCB | Regret UCB1 | Regret SW-UCB | Δ regret SW−UCB1 (IC95%) |
|---|---:|---:|---:|---:|---:|
| Infrecuentes / altas | 16812.5 | 16089.9 | 437.5 | 1160.1 | 722.60 [712.38,732.81] |
| Infrecuentes / bajas | 16418.8 | 15035.6 | 831.2 | 2214.4 | 1383.25 [1355.75,1410.75] |
| Frecuentes / altas | 16720.8 | 15959.6 | 529.2 | 1290.4 | 761.26 [750.00,772.52] |
| Frecuentes / bajas | 16348.0 | 14955.3 | 902.0 | 2294.7 | 1392.75 [1361.17,1424.32] |

La tasa de matching óptimo UCB1/SW-UCB fue 86.1/66.7%, 73.2/55.2%,
74.9/65.8% y 67.0/54.3%, en el orden de la tabla. El MSE medio, no ponderado
entre las nueve parejas y comparado por semilla, fue menor para SW-UCB en
cada celda: Δ MSE SW−UCB1 = -0.00385 (IC95% [-0.00402,-0.00369]),
-0.00304 ([-0.00333,-0.00276]), -0.00112 ([-0.00126,-0.00099]) y -0.00074
([-0.00102,-0.00045]). Es una discrepancia estimación/decisión observada,
no identifica por sí sola un mediador causal.

Reducir p de .75 a .25 elevó el regret: +393.73 (IC95% [372.51,414.94]) y
+1054.38 ([1025.22,1083.54]) con cambios infrecuentes para UCB1 y SW-UCB;
+372.82 ([353.01,392.63]) y +1004.30 ([971.55,1037.06]) con cambios
frecuentes. El contraste de interacción frecuencia × disponibilidad sobre el
gap de regret fue +29.17, IC95% [-3.92,62.25], no concluyente. La diferencia
de frecuencia en ese gap fue +38.66 [24.72,52.60] con oportunidades altas
y +9.49 [-25.07,44.06] con oportunidades bajas.

El volumen observado por réplica fue aproximadamente 22500 con p=.75 y 7500
con p=.25 para ambas políticas. Su distribución entre parejas dependió de las
asignaciones. La cantidad nominal por pareja y estabilidad es p×tau:
1875/625 en cambios infrecuentes y 375/125 en frecuentes (oportunidad
alta/baja); no equivale a observaciones efectivas. La pareja cambiante (2,0)
y las parejas de matchings alternativos reciben cantidades distintas; por
ejemplo, (0,1), fuera de ambos matchings óptimos, recibió alrededor de 60–77
observaciones con UCB1 y 199–325 con SW-UCB según celda. Estas tasas son
endógenas a las asignaciones.

La recuperación se definió como 20 selecciones consecutivas del matching
óptimo, buscando hasta 1000 periodos tras cada cambio. La latencia media
descriptiva por semilla UCB1/SW-UCB fue 106.5/162.8, 93.1/171.3,
66.7/115.8 y 76.0/121.6 periodos; se registraron cambios frecuentes sin
recuperación dentro del límite. Las fronteras dentro de una semilla no se
trataron como réplicas independientes para los intervalos.

### Contrato común, interpretación y límites

El runner nuevo crea 240 ExperimentRun v1 compactos y aplica
EvaluationProfile/PerformanceEvaluator al reward esperado por periodo. El
reward PEF reconcilia con la salida del simulador en cada ejecución. La traza
comprimida guarda 2.4 millones de filas de diagnóstico por periodo. Regret,
índices, estimaciones, observaciones y estabilidad siguen como diagnósticos
del experimento, no como nuevas métricas genéricas PEF. Producción, servicio,
déficit y recursos son no aplicables: el modelo no los define. El regret usa
reward esperado frente al oráculo dinámico, no reward Bernoulli realizado.
El árbol de trabajo ya estaba modificado por otras integraciones autorizadas;
por ello ExperimentRun deja software_revision nulo y conserva revisión Git
base y hashes SHA-256 de las fuentes usadas. Tras la campaña se recalcularon
solo los resúmenes de latencia desde los eventos guardados, agregando primero
por semilla para no tratar fronteras de cambio como réplicas; la simulación
original y sus trazas no se alteraron.

En las condiciones probadas, UCB1 con historial completo obtuvo menor regret;
SW-UCB obtuvo menor MSE. La baja disponibilidad perjudicó a ambos,
especialmente a SW-UCB. No se detectó una interacción factorial concluyente.
La ventana fija W=1214 es menor que tau=2500 y mayor que tau=500; en el
régimen recurrente UCB1 conserva también observaciones antiguas que pueden
volver a ser compatibles al regresar el estado base. Esto es compatible con
los resultados, pero UCB1/SW-UCB difieren también en bonus de confianza y sus
asignaciones generan historiales endógenos: no se aísla el efecto causal puro
de conservar memoria. rho=p×tau es solo un descriptor de oportunidades para
esta instancia, no una ley predictiva. No se modela coste de recursos.

**Conclusión:** en esta configuración concreta, el feedback y el mecanismo
completo de estimación/índices se relacionan con reward y regret colectivos;
la comparación no justifica una regla general de selección de memoria ni una
preferencia universal entre algoritmos. S3b permanece abierta y queda a
decisión del PI el siguiente paso.

**Validación:** 48 pruebas focalizadas de S3b, contrato y PEF pasaron. Se
completó la ejecución de 240 réplicas, la reconciliación PEF y el round-trip
ExperimentRun; git diff --check se ejecutó al cierre. Los resultados
históricos se conservaron.
+
## 2026-10-23 — S3b-E1: diagnóstico final de memoria y feedback organizativo

**Fecha del trabajo:** 23 de octubre de 2026; no se conserva hora exacta.
**Decisión del PI:** GO, cierre de S3b-E1. **Estado tras esta entrada:**
S3b-E1 cerrado; no se inicia otra campaña.

### Pregunta y controles

El factorial anterior de UCB1/SW-UCB dejó una diferencia de regret junto a
menor MSE global de SW-UCB, pero no separó memoria de bonus ni del feedback
endógeno. Este diagnóstico no vuelve a ejecutar UCB1/SW-UCB ni los llama así:
usa dos variantes locales de media empírica para aislar el filtrado temporal.

FULL promedia todo feedback recibido antes de decidir. WINDOW usa el mismo
promedio sobre observaciones con timestamp en [t−W,t), W=1214. Ambas usan
media neutral .5 si no hay observación utilizable; no tienen bonus de
exploración, prior adicional ni aleatoriedad de decisión. En las seis
asignaciones B2 factibles eligen el matching que maximiza la suma de medias;
los empates se resuelven por clave lexicográfica canónica. En los primeros
nueve periodos se conserva el ciclo de calibración existente. Así, la única
diferencia del estimador es qué observaciones históricas retiene.

Se usaron tres condiciones seleccionadas antes de esta campaña por su relación
con W y la tasa de oportunidad: infrecuente/alta (tau=2500,p=.75), frecuente/
alta (tau=500,p=.75) y frecuente/baja (tau=500,p=.25). El contraste primero
varía tau a p alta; el segundo varía p a tau corta. Es un diseño L de tres
celdas y no estima la interacción factorial. Se reutilizó el sistema 3×3,
matrices recurrentes base/transitoria, horizonte 10000, matching y máscara
exógena; se reutilizaron las 30 semillas 9000–9029 para acoplar outcomes y
máscaras entre controles. Total: 3 condiciones × 2 controles × 2 estimadores
× 30 semillas = 360 ejecuciones.

**Control A, observaciones compartidas:** tras el ciclo común de calibración,
un calendario externo recorre cíclicamente los seis matchings, balanceando la
exposición de parejas; la máscara Bernoulli del escenario decide cuáles
outcomes se observan. Ambos estimadores reciben exactamente las mismas
parejas, rewards y timestamps. Sus decisiones posteriores son contrafactuales
y no alteran ese calendario.

**Control B, bucle cerrado:** tras la misma calibración, cada matching elegido
determina qué parejas se ejecutan y pueden producir feedback. Outcomes
potenciales y máscaras siguen acoplados por semilla, aunque las parejas
observadas puedan divergir. No se añadió exploración: la regla greedy y los
empates permanecen comunes. Esta decisión deja lock-in por falta de
observaciones como posible limitación diagnóstica.

Se evaluó reward esperado y regret frente al mejor matching de media real
entre las mismas seis acciones factibles (oráculo solo evaluativo); la suma
del oráculo es 17250 en todas las condiciones. Se registraron matching óptimo,
errores globales y por arista, observaciones/máscaras por pareja, edad,
conteos usados, transiciones, latencia de recuperación y tiempo. HLS-PEF
evaluó únicamente reward esperado; no se añadieron métricas a su catálogo.

### Resultados observados

Las medias son por réplica; Δ regret es WINDOW−FULL pareado por semilla,
IC t del 95%. El MSE es el promedio temporal y no ponderado de las nueve
parejas. La tasa óptima es porcentaje de periodos.

| Condición | Control | Regret FULL | Regret WINDOW | Δ regret (IC95%) | MSE FULL / WINDOW | Matching óptimo FULL / WINDOW |
|---|---|---:|---:|---:|---:|---:|
| Infrecuente/alta | A, compartido | 259.47 | 184.88 | -74.59 [-89.60,-59.58] | .00731 / .00390 | 49.91% / 75.33% |
| Frecuente/alta | A, compartido | 259.47 | 259.47 | 0.00 [0,0] | .00728 / .00630 | 49.91% / 49.91% |
| Frecuente/baja | A, compartido | 269.55 | 268.97 | -.58 [-1.63,.46] | .00800 / .00743 | 49.74% / 49.96% |
| Infrecuente/alta | B, bucle cerrado | 641.46 | 361.15 | -280.31 [-842.61,281.98] | .03710 / .06981 | 48.27% / 57.42% |
| Frecuente/alta | B, bucle cerrado | 641.46 | 373.67 | -267.80 [-811.09,275.50] | .03711 / .06933 | 48.27% / 53.31% |
| Frecuente/baja | B, bucle cerrado | 662.91 | 415.70 | -247.21 [-727.96,233.53] | .06706 / .08001 | 48.21% / 53.40% |

En A, la igualdad de historiales se comprobó con hashes de las secuencias de
feedback por réplica. Con observaciones comunes, WINDOW redujo regret en
74.59 unidades con cambios infrecuentes y disponibilidad alta. A cambios
rápidos, el regret fue idéntico con disponibilidad alta; con disponibilidad
baja la diferencia fue pequeña e incluyó cero. El filtrado temporal sí bajó
el MSE global en las tres condiciones. Por tanto, una mejora de estimación
no garantiza una mejora de decisión ni de reward.

En B, los intervalos de regret WINDOW−FULL incluyen cero en las tres celdas.
WINDOW seleccionó el matching óptimo con más frecuencia: diferencias pareadas
de +9.15, +5.04 y +5.18 puntos porcentuales, con IC95% [4.82,13.47],
[1.95,8.13] y [1.59,8.78]. El MSE global, en cambio, fue menor para FULL;
WINDOW−FULL fue +.03270 [.02264,.04277], +.03222 [.02208,.04236] y
+.01295 [.00102,.02487]. Este patrón muestra que MSE global y acierto
organizativo pueden ordenar los métodos de forma distinta; el efecto en
regret acumulado no queda establecido con precisión en este control.

La discrepancia se concentra en la relevancia de las parejas. En frecuente/
baja y bucle cerrado, el MSE de FULL/WINDOW sobre aristas del matching óptimo
fue .08910/.04582, aunque el MSE global favorece a FULL (.06706 frente a
.08001). Para la pareja (0,1), que no pertenece a ninguno de los dos
matchings óptimos, el MSE fue .0586/.1536 y se obtuvieron en promedio 1/3
observaciones. En cambio, (2,0), cuya competencia cambia y entra en el
óptimo transitorio, tuvo MSE .2586/.1590. El total de feedback fue similar
(aprox. 7496/7492 observaciones por ejecución), pero su distribución cambió.
La media global da el mismo peso a esas parejas y no representa su impacto
desigual en el matching.

En A no se observó un periodo con menor MSE global y mayor regret de WINDOW
frente a FULL. En B, FULL tuvo simultáneamente menor MSE global y mayor regret
en la muestra en varios periodos de trayectorias emparejadas; la frecuencia
fue baja, aproximadamente 2.2%, 35.0% y 34.1% en las tres condiciones.
Esta comparación es descriptiva porque los historiales ya divergen.

### Interpretación, validación y límites

A identifica un efecto inmediato del filtrado temporal sobre un historial
común: en la condición infrecuente/alta, retirar muestras antiguas mejoró
estimación de aristas cambiantes y decisiones; en las otras condiciones el
cambio de MSE no produjo una mejora de regret clara. B incorpora la
retroalimentación de las acciones: FULL y WINDOW recibieron volúmenes totales
parecidos, pero asignaron observaciones de modo distinto. Por ejemplo, en
frecuente/baja FULL/WINDOW observaron (2,0) 165/247 veces y (1,1)
2409/2476; parejas poco relevantes podían quedar casi sin observaciones.
Esto es compatible con un mecanismo de relevancia selectiva, pero el contraste
A/B no identifica un mediador causal puro: cambia el calendario de adquisición
y la trayectoria organizativa.

Una mejor MSE global puede coexistir con más decisiones subóptimas porque el
MSE no pondera por margen ni por efecto de cada arista sobre matchings
candidatos. En frecuente/baja el margen real entre matching óptimo y segundo
mejor es .05 en el régimen transitorio y .45 en el base; los errores
concentrados en aristas críticas pueden importar más que los errores sobre
aristas no competitivas. No se generaliza esta relación fuera de estas
matrices y políticas diagnósticas. Las variantes no son UCB1/SW-UCB, no usan
bonus ni exploración, y la política greedy puede quedar bloqueada tras una
calibración con feedback perdido. El diseño de tres celdas no estima una
interacción A×B. El resultado no cuantifica qué fracción de la brecha previa
UCB1/SW-UCB se debía a memoria.

Se generaron 360 ExperimentRun v1 y perfiles HLS-PEF; el reward PEF
reconcilia por ejecución con el simulador. Las curvas por periodo se agregaron
sobre semillas y no se guardó una traza cruda extensa. El artefacto resume
decisiones, errores, observaciones, hashes de control común y ejemplos
decisivos. La corrida ocurrió con árbol de trabajo modificado: la revisión
base Git está registrada, pero el hash exacto de fuente en el instante de
ejecución no quedó guardado; el código se modificó después solo para añadir
resúmenes de régimen/recuperación y más validaciones, sin alterar trayectorias.

**Cierre:** el control de observaciones comunes identifica una ventaja local
de la ventana en cambios infrecuentes con feedback alto; el control cerrado
muestra una separación reproducible entre MSE global y acierto del matching,
pero regret acumulado queda incierto. S3b-E1 se cierra con estas limitaciones.
No se inicia otra campaña; cualquier prioridad posterior queda a decisión
del PI.

**Validación:** 53 pruebas focalizadas de memoria, S3b, contrato y PEF pasaron;
360 ejecuciones completadas; hashes del control A coincidentes; registros
ExperimentRun serializables; recompensa PEF reconciliada; git diff --check pasó. El resultado está en
[results.json](../../results/experiments/hls_s3b_memory_replay_diagnostic/results.json);
la integración usa el runner
[run_hls_s3b_memory_replay_diagnostic.py](../../experiments/run_hls_s3b_memory_replay_diagnostic.py).

## 2026-10-23 — Piloto de asignación adaptativa de consultas bajo presupuesto

**Objetivo y diseño.** Se ejecutó el primer piloto de asignación de consultas de modelos heterogéneos con presupuesto compartido por lote. xRouteBench `llmrouter_generic` no ofrecía una licencia que pudiéramos establecer con claridad; conforme a la instrucción se usó MMLU (MIT), con pesos Apache-2.0. Se fijaron 200 consultas oficiales `auxiliary_train` (160 ajuste, 40 calibración), 160 consultas `test` balanceadas entre cuatro materias, tres modelos abiertos locales, lotes de 10, 20 semillas de empaquetado emparejadas, lotes homogéneos/heterogéneos y presupuestos de 0,35/0,70 entre extremos de coste predicho. La respuesta se puntuó por coincidencia exacta de letra, sin umbrales de calidad.

**Mecanismos.** Todas las políticas compartieron una adaptación MIRT de IRT-Router y una matriz de costes de latencia predicha mediante regresión afín ajustada solo en train. Se compararon routing independiente con reparación, greedy factible, ILP aditivo conjunto, modelos fijos económico y de mayor calidad de entrenamiento, y una cota retrospectiva de test. El ILP es una adaptación determinista de la formulación de asignación por lotes; no implementa robustez ante incertidumbre ni capacidad/concurrencia del artículo publicado. No es una reproducción completa de IRT-Router: se usó hashing de texto en lugar de BERT.

**Resultados aceptados.** Se produjeron 480 `ExperimentRun` v1, 76.800 asignaciones y 1.080 outcomes de consultas-modelo. En presupuesto 0,35, ILP logró exactitud macro 0,3250/0,3244 en lotes homogéneos/heterogéneos, frente a 0,3278/0,3247 del greedy y 0,2991/0,2953 del routing independiente reparado. La diferencia emparejada ILP−greedy fue −0,28 pp (IC95% bootstrap estratificado por consulta [−1,00; +0,44]) en homogéneos y −0,03 pp (IC [−0,78; +0,75]) en heterogéneos. ILP−independiente fue +2,59 pp (IC [ +0,41; +4,91]) y +2,91 pp (IC [+0,91; +4,97]), respectivamente. Con presupuesto 0,70, greedy e independiente quedaron aproximadamente empatados con ILP (diferencias menores de 0,2 pp; IC por consulta incluyen cero). Los IC por empaquetado y consulta, y las tablas por política/tarea, se preservan en el informe y `results.json`.

La MIRT convergió en 773 iteraciones; su Brier test fue 0,26983 frente a 0,23139 para un baseline constante por modelo ajustado con prevalencias de entrenamiento. El RMSE de latencia test fue 0,414 s por consulta-modelo. Aunque ILP/greedy/reparación respetaron en 100% de los lotes el presupuesto de coste predicho, solo 74–85% de sus lotes heterogéneos cumplieron también el umbral usando latencia observada en las celdas principales (aprox. 64–85% considerando ambas composiciones y presupuestos). La latencia es tiempo de inferencia local serial, no coste monetario ni medida de servicio concurrente.

**Interpretación y límites.** En esta muestra el optimizador ILP no aportó mejora medible frente a greedy; sí superó el router independiente reparado bajo presupuesto más restrictivo, diferencia que se reduce al relajar el presupuesto. Es evidencia local sobre estos datos, modelos y coste imperfectamente predicho, no una superioridad general ni una atribución pura a optimización exacta. El predictor de calidad está peor que el baseline de prevalencia y la predicción de costes no asegura el límite de latencia observada; estas limitaciones restringen especialmente cualquier conclusión sobre despliegue. El estudio no basta por sí solo para sostener novedad publicable: la literatura ya contiene routing IRT y routing conjunto por lotes.

Durante la ejecución se detectó que el ajuste inicial alcanzó el límite de iteraciones; ese resultado no se aceptó. Se amplió el máximo de iteraciones, se exigió convergencia explícita y se volvió a calcular el mismo diseño usando los outcomes ya generados, sin cambiar semillas, datos, políticas ni parámetros experimentales. El artefacto final registra convergencia.

**Artefactos y validación.** Implementación en `src/hls/llm_routing_pilot.py`, runner `experiments/run_hls_budgeted_llm_routing_pilot.py`, pruebas `tests/test_hls_llm_routing_pilot.py`, resultados reproducibles en `results/experiments/hls_budgeted_llm_routing_pilot/` e informe `docs/experiments/HLS_BUDGETED_LLM_ROUTING_PILOT.md`. Pasaron 24 pruebas focalizadas de piloto, contrato y PEF; compilación Python y `git diff --check`. No se modificaron algoritmos históricos ni se hizo commit/push.

## 2026-10-23 — Revisión correctiva del predictor en routing presupuestado

**Objetivo.** Determinar si el Brier deficiente de MIRT adaptado en el piloto LLM condicionó las decisiones organizativas. Se mantuvieron consultas test, modelos, outcomes generados, costes, lotes homogéneos/heterogéneos, presupuestos y semillas originales; los resultados se escribieron en un directorio separado y no se sustituyeron los del piloto inicial.

**Método.** Se añadió regresión logística L2 con texto de pregunta/opciones, identidad de modelo, tipo de tarea e interacción modelo×tarea. `C` se seleccionó entre 0,01/0,1/1/10 por Brier en cinco pliegues agrupados por consulta, exclusivamente dentro de los 160 ejemplos de entrenamiento; resultó C=1. Se comparó contra MIRT adaptado y prevalencia train por modelo. El precio del router independiente se calibró en el mismo subconjunto de 40 consultas auxiliares. La matriz de costes test se reutilizó desde el artefacto original y se verificó frente a su recálculo con tolerancia 1e−12. Se generaron 720 ExperimentRun con HLS-PEF y 115.200 decisiones para los tres predictores por ILP/greedy/router reparado.

**Resultado predictivo.** Brier MIRT/prevalencia/logística: 0,26983/0,23139/0,21744; log-loss: 0,80482/0,65336/0,62402; ECE diez bins: 0,18985/0,08542/0,04305. La diferencia logística−prevalencia fue −0,01395 en Brier (IC95% consulta [−0,02615; −0,00184]) y −0,02934 en log-loss ([−0,05479; −0,00405]). La exactitud top-model fue 0,36875/0,45/0,45; el orden por pares informativos fue 0,52174/0,69022/0,69022. Las diferencias por materia y calibración completa están en `results.json`.

**Resultado organizativo.** A presupuesto 0,35, prevalencia train obtuvo exactitud ILP/greedy/router 0,4359/0,4356/0,4359 en lotes homogéneos y 0,4309/0,4213/0,4219 en heterogéneos. Logística obtuvo 0,4094/0,3878/0,3872 y 0,4247/0,4194/0,4194. A presupuesto 0,70, prevalencia y logística convergieron en 0,45 en las tres políticas y ambas asignaron todas las consultas al modelo de mayor exactitud de entrenamiento. La exactitud logística fue superior a MIRT en todas las condiciones; sin embargo, el predictor contextual de menor Brier no superó al predictor constante en rendimiento organizativo a presupuesto bajo.

ILP−greedy con predictor contextual y lote homogéneo a 0,35 fue +2,16 pp (IC95% por packing [+1,63; +2,72], bootstrap consulta [+0,72; +3,78]); en heterogéneo fue +0,53 pp (IC consulta [−1,34; +2,56]). En el resto de celdas la ventaja conjunta no fue consistente y a presupuesto 0,70 las políticas coincidieron.

**Límite de cobertura.** `auxiliary_train` solo proporcionó el tipo `mmlu_auxiliary_mixed`; las cuatro categorías del test no estaban presentes al entrenar el efecto de tarea. La logística codifica ese atributo, pero no puede aprender coeficientes específicos para esos sujetos no vistos. Coste sigue siendo latencia local estimada, no precio monetario ni serving concurrente. Las consultas test son una sola muestra de cuatro materias y se probaron muchos contrastes exploratorios sin corrección de multiplicidad. La evidencia no establece superioridad general del ILP ni una contribución publicable autónoma.

**Artefactos y verificación.** Predictor en `src/hls/llm_routing_pilot.py`; runner en `experiments/run_hls_budgeted_llm_routing_predictor_recheck.py`; resultados nuevos en `results/experiments/hls_budgeted_llm_routing_predictor_recheck/`; informe `docs/experiments/HLS_BUDGETED_LLM_ROUTING_PREDICTOR_RECHECK.md`. Los resultados originales permanecen en `hls_budgeted_llm_routing_pilot/`. Pasaron pruebas focalizadas de predictor, contrato y PEF; serialización de ExperimentRun, comprobación exacta de costes y `git diff --check`. No se ejecutó inferencia adicional ni se abrió otra línea.

## 2026-10-23 — Consolidación y cierre de routing presupuestado

**Decisión y alcance.** Por decisión del CE se cerró la campaña sin nuevas ejecuciones. Se consolidaron el piloto inicial y la corrección del predictor en [el informe científico unificado](../experiments/HLS_BUDGETED_LLM_ROUTING_CONSOLIDATED_REPORT.md), manteniendo los informes, resultados y hashes de cada iteración como fuentes históricas separadas.

**Síntesis verificable.** El piloto inicial, con MIRT adaptado, no encontró ventaja del ILP frente al greedy en ninguna celda; sí observó que ILP y greedy superaban al router independiente reparado en el presupuesto 0,35. En la corrección, logística contextual obtuvo Brier 0,21744 frente a 0,23139 de prevalencia y 0,26983 de MIRT, pero no mejoró uniformemente el resultado organizativo: con presupuesto 0,35 la prevalencia superó a logística, y con 0,70 ambas dieron la misma asignación. ILP superó a greedy en +2,16 pp solo para predictor contextual, lote homogéneo y presupuesto 0,35 (IC95% bootstrap por packing [+1,63; +2,72] y por consulta [+0,72; +3,78]); los demás contrastes no acreditan una ventaja general. El resultado de coste se refiere a latencia local predicha: el cumplimiento del presupuesto estimado no garantizó cumplimiento con la latencia observada.

**Conclusión y límites.** La campaña demuestra en esta muestra que calidad predictiva y utilidad organizativa no son equivalentes, y que la ventaja ILP–greedy depende de predictor, composición y presupuesto. El único contraste favorable al ILP es local y exploratorio, entre varios contrastes sin corrección por multiplicidad. El benchmark cubre 160 consultas de cuatro materias y tres modelos pequeños; las categorías test no estaban representadas como tipos de tarea en el entrenamiento correctivo. Los costes no son precios ni latencia de servicio concurrente; los métodos publicados se adaptaron, no se reprodujeron íntegramente. No queda establecida superioridad general ni novedad publicable autónoma. HLS puede reutilizar la separación predictor/asignador/evaluador como ejemplo de evaluación organizativa bajo presupuesto.

**Trazabilidad y estado.** Se conservaron íntegros `results/experiments/hls_budgeted_llm_routing_pilot/` y `results/experiments/hls_budgeted_llm_routing_predictor_recheck/`, incluidos sus `artifact_hashes.json`. No se modificaron algoritmos, contratos ni artefactos experimentales; no se inició otra campaña. Informe de origen: `docs/experiments/HLS_BUDGETED_LLM_ROUTING_PILOT.md` e iteración correctiva: `docs/experiments/HLS_BUDGETED_LLM_ROUTING_PREDICTOR_RECHECK.md`. La consolidación es documental y deja la campaña cerrada.

## 2026-10-23 — Organización dinámica de capacidades heterogéneas

**Objetivo y particiones.** Se ejecutó un piloto de selección estática, routing por consulta, escalado FAST→DEEP y combinación sobre MMLU. Se reutilizó el mismo subconjunto test oficial de 160 preguntas del routing presupuestado. Para separar ajuste/decisión se usó `all/dev` (5 preguntas por cada uno de cuatro tipos, selección estática), `all/validation` (muestra fija de 22 por tipo para umbrales y precio del IRT-Router) y `test` (40 por tipo). El predictor IRT usó exclusivamente los 160 ejemplos auxiliares de ajuste del piloto anterior. Se generaron 804 respuestas/scores nuevos para las particiones por modelo; las 480 letras regeneradas en test coincidieron al 100% con las archivadas.

**Mecanismos y señales.** Se reutilizó el predictor IRT multidimensional adaptado de IRT-Router; la selección coste-calidad `argmax(q_hat − λ c_hat)` y la elección de λ por niveles de coste son adaptaciones experimentales. La cascada aplicó umbral selectivo a la masa softmax normalizada de la letra emitida por FAST en logits del primer token, y escaló a DEEP cuando el score quedaba bajo el umbral. Es una adaptación de clasificación selectiva con rechazo, no la implementación de sus garantías de riesgo. Los umbrales se eligieron en validación por tasa objetivo de activación, sin etiquetas de corrección. Se añadió pluralidad de las tres letras como comparador, con DEEP para desempates. FAST/DEEP se fijaron antes del test a partir de coste y calidad train: SmolLM2-360M y SmolLM2-1.7B, respectivamente.

**Resultados.** En test FAST logró exactitud 0,2313 (IC95% estratificado [0,1688; 0,3000]) y DEEP 0,4500 [0,3813; 0,5250]; la diferencia DEEP−FAST fue +21,88 pp [ +11,88; +31,88]. Los outcomes fueron complementarios: 22 preguntas solo correctas por FAST, 57 solo por DEEP, 15 por ambos y 66 por ninguno. Por materia, FAST superó a DEEP en matemáticas (0,225 frente a 0,150), mientras DEEP fue mejor en las otras tres. La selección fija por tarea, entrenada con cinco ejemplos por tipo, obtuvo 0,4688 [0,4000; 0,5438], pero su diferencia emparejada frente a DEEP fue +1,88 pp [−2,50; +6,25], no concluyente.

La cascada alcanzó 0,3813 con 46,25% de activación DEEP y 0,6847 s/consulta; a 93,75% de activación igualó a DEEP en exactitud (0,45) pero costó 0,9031 s/consulta frente a 0,4056. Ningún punto de cascada superó a DEEP siempre en exactitud; todos añadieron la llamada FAST. La pluralidad de los tres modelos obtuvo 0,4188 y 1,4835 s/consulta, sin superar a DEEP. El oráculo retrospectivo alcanzó 0,6625 y no es desplegable.

**Interpretación y límites.** Hay diversidad de errores, pero la pluralidad no la convierte en mejora; la confianza FAST tuvo AUC de ranking de error 0,444 en validación y 0,521 en test. Además, la latencia se invirtió: FAST costó 0,5191 s/consulta test y DEEP 0,4056, aunque FAST era más rápido en ajuste. La salida breve del modelo grande y el hardware local afectan el orden de latencia. Dentro de este test no se encontró condición favorable al escalado por confianza; la especialización de FAST en matemáticas es una señal por confirmar, no una regla general.

**Validación y artefactos.** Se generaron 27 `ExperimentRun` con 4.320 eventos y evaluación HLS-PEF; cada cascada suma la latencia medida de FAST y las llamadas DEEP activadas. Los IC95% son bootstrap emparejado por pregunta, estratificado por materia, y se condicionan a la muestra, modelos y hardware. Pasaron 21 pruebas focalizadas de políticas, routing previo y HLS-PEF; se verificó round-trip de los 27 ExperimentRun y los seis hashes del piloto original. Runner, resultados y curvas están en `experiments/run_hls_dynamic_capacity_organization.py` y `results/experiments/hls_dynamic_capacity_organization/`; mecanismo y pruebas en `src/hls/dynamic_capacity_organization.py` y `tests/test_hls_dynamic_capacity_organization.py`. El informe detallado es [HLS_DYNAMIC_CAPACITY_ORGANIZATION.md](../experiments/HLS_DYNAMIC_CAPACITY_ORGANIZATION.md). No se modificaron resultados históricos ni contratos.

## 2026-10-23 — Organización dinámica de capacidades: corrección experimental

**Objetivo y diagnóstico.** Se corrigió la inversión de latencia del primer piloto sin demoras artificiales ni cambios de objetivo. El piloto anterior midió generación autoregresiva de hasta ocho tokens, una sola vez por consulta y con orden fijo; en su test previo el 360M generó 6,775 tokens de media y tardó 0,5191 s, frente a 2,844 tokens y 0,4056 s para el 1.7B. Esto explica plausiblemente la inversión por longitud de generación, pero el diseño previo no permite aislar el efecto de tokens del orden/backend. Se conservaron los artefactos del piloto anterior.

**Diseño ejecutado.** Se usaron los tres modelos y revisiones fijadas del piloto, FP16, Transformers eager sobre MPS, Apple M2 Max/64 GB, PyTorch 2.4.1 y Transformers 4.45.0. El protocolo nuevo puntúa opciones A–D con una pasada de logits por pregunta y tres repeticiones temporales por consulta/modelo. Entrenamiento: 200 ejemplos auxiliares para MIRT; selector estático con cinco ejemplos `dev` por materia; 88 ejemplos de validación para precio/umbrales. La pareja 360M→1.7B y todos los parámetros se congelaron con train/validación. Test final: seed 20261025, 40 preguntas por cada una de cuatro materias de la partición oficial, excluyendo por hash de pregunta/opciones las 160 preguntas ya evaluadas en el piloto anterior. No se usaron etiquetas test para seleccionar capacidades o políticas.

**Resultados.** En el test nuevo, 360M obtuvo 24,38% (0,0962 s/consulta), 1.7B 45,00% (0,1416 s), y Qwen-0.5B 46,25% (0,0889 s). El contraste emparejado 1.7B−360M fue +20,63 pp (IC95% [11,25; 30,00]) con +45,4 ms de coste. El selector fijo por materia obtuvo 51,25% (IC95% [43,75; 58,75]) en 0,1242 s; su diferencia frente a B fue +6,25 pp (IC95% [0; 12,5]), no concluyente. El router MIRT llegó a 41,88%/0,1065 s en su nivel intermedio; la cascada a 34,38%/0,1523 s con 40,6% de activaciones; pluralidad logró 45,63%/0,3267 s. Qwen fijo dominó en la muestra todos los puntos IRT y cascada. La señal de confianza de A tuvo AUC de error 0,508 en test; el predictor MIRT tuvo Brier 0,2828 frente a 0,2326 de la referencia constante train. Resultados por materia, intervalos, diagnósticos y curvas quedan en [el informe corregido](../experiments/HLS_DYNAMIC_CAPACITY_ORGANIZATION_CORRECTED.md).

**Interpretación y límites.** El protocolo corregido sí revela perfiles calidad-latencia físicos, pero la pareja seleccionada con train/validación no dominó: Qwen fue algo más preciso y bastante más rápido en el test nuevo, mientras la selección estática por materia tuvo la mayor exactitud puntual. El orden Qwen/1.7B no generalizó desde validación y la mejora puntual del selector fijo sobre B no es concluyente. La cascada por confianza no aporta una frontera no dominada; 24 de 65 activaciones en el punto de tasa objetivo 0,3 corrigieron A, 8 empeoraron una respuesta correcta de A, 10 encontraron ambas ya correctas y 23 dejaron ambas incorrectas. No se demuestra valor general de organización dinámica. La muestra sigue siendo 160 preguntas, cuatro materias y un hardware; la latencia es replay local, sin energía ni serving concurrente.

**Capacidad e integridad.** El runner corregido reutiliza las políticas existentes, `ExperimentRun` y HLS-PEF, sin alterar contratos ni el experimento anterior. Se registraron 28 ejecuciones, 4.480 eventos, tres tiempos por consulta/modelo, outputs deterministas, curva PNG/CSV, métricas de señales y hashes. Se verificó la separación por contenido de particiones, round-trip de los 28 `ExperimentRun`, hashes del nuevo artefacto, 25 pruebas focalizadas y `git diff --check`. Runner: `experiments/run_hls_dynamic_capacity_corrected.py`; resumen: `experiments/summarize_hls_dynamic_capacity_corrected.py`; resultados: `results/experiments/hls_dynamic_capacity_organization_corrected/`. Sin commit ni push.

## 2026-10-23 — Selección contextual de capacidades mediante DCS-LA

**Objetivo y método.** Por autorización del CE se evaluó si las características observables de consulta permiten mejorar sobre una selección estática. Se implementó una adaptación de DCS-LA de Woods, Kegelmeyer y Bowyer (1997): exactitud local por modelo en los `k` vecinos de entrenamiento, con similitud coseno sobre TF-IDF. El vocabulario se ajustó solo con entrenamiento; materia fue una característica categórica candidata, observable, nunca inferida de la etiqueta. El grid de 70 configuraciones se eligió con validación. La configuración seleccionada fue `k=21`, unigramas, peso de materia 0; por tanto el resultado final usa texto y no aporta evidencia de utilidad incremental de materia. No se usaron etiquetas test para selección ni se hicieron inferencias nuevas.

**Datos y comparadores.** Se reutilizaron outcomes y latencias del piloto corregido: 200 ejemplos `auxiliary_train` (sin materia registrada), 20 `dev` con materia (5 por tipo), 88 de validación y las mismas 160 consultas test nuevas, disjuntas por contenido. El fijo global se eligió por validación (SmolLM2-1.7B); la política fija por materia conservó el mapeo ajustado en `dev`; el cuarto comparador fue oráculo retrospectivo no operable. Se generaron cuatro `ExperimentRun` v1 con 640 eventos HLS-PEF.

**Resultados.** DCS-LA obtuvo exactitud 46,25% (IC95% [38,75; 53,75]) y latencia total media 139,27 ms/consulta (IC95% [135,77; 142,77]); selección online: media 0,456 ms, con búsqueda de vecinos alrededor de 0,290 ms. Frente al mejor fijo global (45,00%), diferencia +1,25 pp (IC95% [−1,25; +3,75]), no concluyente; ahorró 2,34 ms de latencia total (IC95% de DCS−fijo [−4,30; −0,75] ms), porque seleccionó modelos más baratos en 11/160 casos. Frente al selector por materia (51,25%, 124,20 ms), DCS fue −5 pp (IC95% [−11,25; +1,25]) y +15,07 ms más lento (IC95% [+12,87; +16,94]). Coincidió con la decisión por materia en 76 consultas, difirió en 84; en estas diferencias corrigió 9 errores y perdió 17 aciertos de la selección por materia. Eligió el 1.7B en 149/160, Qwen en 7 y 360M en 4. El oráculo retrospectivo dio 68,75%, 22,5 pp sobre DCS, sin coste decisional operable.

**Interpretación y límites.** La adaptación local no demuestra una mejora de exactitud sobre el mejor fijo global y queda dominada por el punto estimado de selección por materia en calidad/latencia. La pequeña reducción de latencia frente al fijo global es real en esta muestra, pero no acredita superioridad contextual de calidad. Solo 20 ejemplos de entrenamiento tienen materia anotada y la configuración final descarta el peso de materia; se cubren cuatro materias, 160 consultas y tres modelos. Informe, adaptación, resultados, curva, hashes y pruebas: [HLS_CONTEXTUAL_CAPACITY_SELECTION.md](../experiments/HLS_CONTEXTUAL_CAPACITY_SELECTION.md), `src/hls/contextual_capacity_selection.py`, `experiments/run_hls_contextual_capacity_selection.py`, `results/experiments/hls_contextual_capacity_selection/` y `tests/test_hls_contextual_capacity_selection.py`. Pasaron 30 pruebas focalizadas/regresión y `git diff --check`; se verificó round-trip de los cuatro ExperimentRun. Los resultados históricos permanecen intactos; no se hizo commit ni push.

## 2026-10-23 — Consolidación científica y trazabilidad publicable

**Objetivo y alcance.** Se reconstruyó el estado científico desde los
documentos, implementaciones y artefactos existentes para ofrecer al PI un
punto de entrada único en GitHub. No se ejecutaron simulaciones, campañas ni
inferencias, y no se modificaron resultados históricos.

**Documentación consolidada.** Se añadió el snapshot científico y el índice
de evidencias en [`docs/HLS_CURRENT_STATE.md`](../HLS_CURRENT_STATE.md). Se
distinguieron los problemas S1–S7 de las secuencias temporales `TR-*`, se
registró que no existe un escenario canónico S8 y se conservaron por separado
los resultados positivos, nulos y negativos de S3b-E1, combinación exacta,
routing presupuestado, MMLU inicial/corregido y DCS-LA. La página diferencia
estado definido/implementado/ejecutado/evaluado/validado y limita cada
conclusión a su evidencia. El roadmap recibió una nota de estado que cierra la
discrepancia temporal sobre Hito 2.2/S3b-E1 y apunta al snapshot; sus entradas
anteriores no se reescribieron.

**Diagnóstico de publicación.** En la fecha de revisión, `feature/hls-laboratory-v1`
estaba en `f945836b07a263401bf03f5a9b035835dc53ff8d`, `origin/main` en
`931c560aae5424a29844f8a998518460db9db973`, y la rama de trabajo estaba 88
commits por delante y cero por detrás. `origin/main` era antecesora directa;
los documentos de laboratorio listados en el snapshot existían localmente y
en la rama de trabajo, pero no en `origin/main`. La falta de acceso se debía a
que aún no estaban integrados en `main`, no a permisos. `README.md` ya enlazaba
el snapshot canónico y no requirió cambio.

**Integridad y publicación.** No se reejecutaron artefactos. Los manifiestos
de hash verificaron los 15 archivos declarados del piloto MMLU corregido, los
8 del DCS-LA y los 6/4 archivos de datos declarados en los dos pilotos de
routing. El manifiesto del piloto MMLU inicial verificó 8 de 9 entradas: los
ocho artefactos de salida coinciden y la entrada del código fuente difiere
del archivo de fuente actual, que evolucionó después; no se alteró ni se
reescribió el manifiesto histórico. Se excluyen los trazados crudos ignorados
por política del repositorio (incluido el trazado comprimido S3b de 318 MB);
se conservan resultados estructurados y procedencia. Pasaron 92 pruebas
focalizadas de S2a/S3b/S4/PEF/complementariedad/routing/MMLU/DCS-LA y
`git diff --check`; enlaces relativos del snapshot y roadmap comprobados.
La situación de integración y publicación debe verificarse contra el remoto
después del commit, no inferirse de esta entrada documental.

## 2026-10-24 — PI strategic proposal and HLS-CE-01 feasibility mission

**Event date:** 2026-10-24, the date of the PI's strategic proposal. **CE interpretation:** 2026-10-24, feasibility planning only. **Document record date:** 2026-10-24. The Git commit date is the record-publication date and must not be used to infer when the scientific proposal or interpretation occurred.

The PI proposed three priorities, in order: (1) dynamic organization of fast and deliberative capabilities, (2) selective cooperation among heterogeneous capabilities, and (3) organizational learning and emergent specialization. The proposed objective is to assess a first publishable contribution within twelve months, with moderate compute and concrete problem focus. The priorities are pending ratification and do not define HLS.

### HLS-CE-01 — planning/feasibility proposal

This is a scoped addition to the existing plan, not a new general plan or replacement calendar. The CE considers a feasibility assessment appropriate. The working question is: **When does activating additional deliberative capability add value compared with accepting a fast decision?** Initial hypothesis: incremental deliberation value may differ substantially from what confidence, estimated difficulty, or individual capability performance predicts. It remains untested and no originality is claimed.

The assessment is to compare prior work on routing, cascades, value of computation, metareasoning, adaptive computation, decision-focused learning, and budgeted allocation. It should reuse, without reopening, bounded HLS evidence from META-VOC/Campaign 3, budgeted routing, MMLU, DCS-LA, and work on information and collective decisions. A design-only minimum experiment concept should compare fast and deliberative capabilities on common problems, measuring initial/final quality, realized incremental benefit, complete cost/latency, predictive signal value, and collective performance at matched budgets. It must include strong static/adaptive comparators and distinguish non-deployable oracles from policies using operational information. No execution is authorized.

| Target date | Proposed activity | Status boundary |
|---|---|---|
| 26 Oct | Delimit problem, falsifiable hypothesis, and reusable HLS evidence. | Proposed planning target. |
| 27 Oct | Compare prior work on routing, cascades, metareasoning, and adaptive deliberation. | Documentary comparison only. |
| 28 Oct | Analyze incremental deliberation benefit, predictive signals, uncertainty, and costs. | No experiment. |
| 29 Oct | Design the minimum decisive experiment, comparators, controls, metrics, data, and stopping criteria. | Design only; no execution. |
| 30 Oct | Interim feasibility report and GO / REVISE / NO-GO recommendation. | No automatic campaign authorization. |
| 2–6 Nov | Resolve specific remaining uncertainties and prepare the final report. | **Proposed dates; not ratified.** |
| 9–13 Nov | Optional extension only for a specific justified pending check. | **Proposed dates; not ratified.** |

Deliverable: a concise feasibility report with the question, hypothesis, evidence map, prior-art comparison, minimal design, comparators, metrics, stopping criteria, risks, and recommendation. The CE leads/integrates the scientific assessment; Codex provides technical and documentary support under CE instructions; strategic ratification remains with the PI. No personal task assignment or role acceptance for E1/E2/E3 is implied.

**Current status:** planning/feasibility only. No new campaign, algorithm, or manuscript is authorized. No code, scenarios, mechanisms, or historical results were modified. See [`HLS_CE_01_DYNAMIC_DELIBERATION_2026-10-24.md`](../research/HLS_CE_01_DYNAMIC_DELIBERATION_2026-10-24.md).
