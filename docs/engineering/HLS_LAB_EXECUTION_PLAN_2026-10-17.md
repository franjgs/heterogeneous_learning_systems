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
