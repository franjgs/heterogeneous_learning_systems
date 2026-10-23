# HLS-PEF — Performance Evaluation Framework

**Fase 1 · especificación científica y arquitectura conceptual · 2026-10-22**

## 1. Principios científicos

HLS-PEF es un catálogo de definiciones y un protocolo para evaluar organizaciones heterogéneas. No fija una utilidad universal. Una configuración de HLS declara el sistema **A**, el problema y modalidad organizativa **B**, y la arquitectura de decisión **C**; su evaluación añade siete objetos distintos: problema, mecanismos, objetivo optimizado, restricciones, resultados colectivos, diagnósticos explicativos y comparaciones entre políticas. Una métrica puede ser objetivo en un estudio y diagnóstico en otro; su definición y unidad no deben cambiar al cambiar de papel.

Para una instancia `z`, demanda `D_t`, acción factible `u_t`, resultado `Y_t` y política `π`, el objetivo declarado es `J_z(π)=E_π[Σ_t r_z(S_t,D_t,u_t,Y_t)+g_z(S_T)]`, sujeto a las restricciones declaradas. Un indicador `m_z(π)` puede evaluar la misma trayectoria sin entrar en `r_z`. La observación de una política se limita a su régimen informativo; el evaluador puede usar estado real u oráculos solamente para medir, señalándolo. Recompensa esperada, recompensa realizada, éxito funcional, déficit, competencia futura y uso de recursos son variables diferentes.

Cada métrica necesita una ficha con: unidad de análisis (petición, tarea, problema-periodo, pareja o horizonte), población/denominador, fórmula, orientación, rango condicionado, fuente, acceso permitido, agregación, incertidumbre, casos indefinidos y versión. Los objetivos, umbrales, pesos, baselines y métricas primarias se fijan antes de observar el resultado de las políticas. CES conserva su significado histórico donde fue el objetivo; HLS-PEF no recalcula retroactivamente campañas S1–S7.

Fuentes de esta fase: [marco unificado](HLS_UNIFIED_FRAMEWORK.md), [ontología](HLS_ONTOLOGY_V0_1_2026-10-23.md), [auditoría del rendimiento colectivo](HLS_COLLECTIVE_PERFORMANCE_AUDIT.md), [registro acumulativo](../engineering/HLS_LAB_EXECUTION_PLAN_2026-10-17.md), implementaciones y resultados citados en §2 y §6.

## 2. Auditoría de métricas y objetivos existentes

**Notación local.** En asignación discreta `x_{ikt}∈{0,1}`; `c_{ikt}` es la recompensa media/competencia declarada para esa arista y `r_{ikt}` su Bernoulli observado cuando procede. En producción N×K, `e_{ikt}≥0` es esfuerzo y `y_{kt}=Σ_i e_{ikt}c_{ikt}` es output. En ese módulo `f_t=1{y_{kt}≥q_{kt} para todo requisito activo}`, `d_{kt}=(q_{kt}-y_{kt})_+`, `D_t=Σ_{k:q_{kt}>0}d_{kt}/q_{kt}`, y `CES_t=(Σ_k w_{kt}y_{kt}^{ρ})^{1/ρ}` con `ρ=.5` por defecto. Los requisitos `q` no entran en CES. Una unidad de asignación S2a y un problema-periodo funcional S4 no son la misma unidad de servicio.

### 2.1 Magnitudes observadas

| Magnitud real; unidad, rango y orientación | Escenarios y papel actual | Datos y código; límite |
|---|---|---|
| **Recompensa de asignación:** `R_t=Σ_{(i,k)∈u_t} c_{ikt}`; unidades de recompensa, `[0,m_t]` si cada media está en `[0,1]` y se seleccionan `m_t` aristas; ↑. Acumulada `Σ_tR_t`. | S1, S2a, S2b: objetivo exacto; S3a: rendimiento/oráculo bajo competencias actuales; S3b: recompensa esperada evaluada. | Matriz de aristas y acciones factibles; [S1](../../experiments/run_hls_hungarian_assignment.py), [S2a](../../experiments/run_hls_s2a_static_demand.py), [S2b](../../experiments/run_hls_s2b_intertemporal_budget.py), [S3b](../../experiments/run_hls_s3b_nonstationary_unknown_assignment.py). El máximo depende de capacidad, demanda y escala de aristas. |
| **Recompensa Bernoulli realizada:** `Σ_{(i,k)∈u_t} r_{ikt}`, con `r∈{0,1}`; éxitos observados por periodo, `[0,m_t]`; ↑ como resultado, pero no sustituye a la recompensa esperada al calcular regret esperado. | S3b y controles: evaluación de políticas bajo feedback parcial. | Outcomes únicamente de aristas ejecutadas para la política; el simulador conserva potenciales comunes para comparación. [entorno S3b](../../src/hls/nonstationary_assignment.py), [runner](../../experiments/run_hls_s3b_nonstationary_unknown_assignment.py). Variabilidad de observación y de decisión no se deben confundir. |
| **Regret esperado dinámico:** `L_T=Σ_t[R_t^*(c_t)-R_t(u_t;c_t)]`; unidades de recompensa, ≥0 para oráculo sobre el mismo conjunto factible; ↓. | S3b: comparador de evaluación, no recompensa observada por la política; variantes S3a cuando se define oráculo. | Requiere medias reales y oráculo del mismo periodo/modalidad. [S3b](../../experiments/run_hls_s3b_nonstationary_unknown_assignment.py), [GLR](../../experiments/run_hls_s3b_glr_cucb.py). Regrets absolutos B1/B2 o con distinto horizonte/oráculo no son comparables. |
| **Demanda discreta atendida/no atendida:** `a_{kt}=Σ_i x_{ikt}`, `u_{kt}=d_{kt}-a_{kt}`; unidades de trabajo, `[0,d_{kt}]`; atendida ↑, pendiente ↓. | S2a/S2b: indicador funcional separado del reward lineal; S1 cuenta aristas seleccionadas. | Demanda y aristas asignadas; [S2a](../../experiments/run_hls_s2a_static_demand.py), [S2b](../../experiments/run_hls_s2b_intertemporal_budget.py). No mide calidad del trabajo ejecutado ni equivale al éxito N×K. |
| **Output productivo N×K:** `y_{kt}=Σ_i e_{ikt}c_{ikt}`; unidades de output por competencia, ≥0; ↑ solo respecto a una necesidad declarada. **CES:** fórmula indicada arriba; unidades de output compuesto, ≥0; ↑ donde es objetivo. | Referencias N×K de transferencia S4 y S7: CES inmediato/acumulado son objetivos; ejecuciones P0/P1/P2 lo registran aunque decidan con otra regla. | Competencia física, esfuerzo, pesos; [producción](../../src/hls/hls_lab_nk_production.py), [Bellman N×K S4](../../src/hls/synthetic/hls_s4_transfer_exact.py), [Bellman S7](../../src/hls/synthetic/hls_s7_uncertain_demand.py). CES no contiene umbrales ni coste monetario; pesos por defecto uniformes no expresan necesariamente prioridad. |
| **Reward S4 de asignación binaria:** `R_t=Σ_{(i,k)∈u_t}c_{ikt}` antes de MIS-v2; unidades de recompensa de arista, `[0,|u_t|]`; ↑. | S4 canónico inicial, Bellman, reactiva y BEST-MYOPIC: objetivo acumulado lineal, distinto del CES de los estudios N×K de transferencia. | Matriz de competencias y matching de una unidad; [S4 inicial](../../src/hls/synthetic/hls_s4.py). La etiqueta S4 indica dinámica endógena, no fija una función objetivo universal. |
| **Éxito funcional N×K:** `f_t=1{∀k:q_{kt}>0, y_{kt}+10^{-12}≥q_{kt}}`; 0/1 por problema-periodo; ↑. **Déficit:** `d_{kt}=(q_{kt}-y_{kt})_+`, en unidades de output; ↓. **Déficit normalizado:** `D_t=Σ_{k:q>0}d_{kt}/q_{kt}`, `[0,K_t^+]`; ↓. **Margen:** `min_{k:q>0}(y_{kt}-q_{kt})`, en output; ↑. | S4/S7: diagnósticos; P0/P1/P2: éxito, `-D_t`, margen y `-esfuerzo` forman la jerarquía inmediata. | Requisitos y outputs; [evaluador](../../src/hls/hls_lab_nk_production.py), [políticas](../../src/hls/hls_lab_nk_policies.py), [trazas S7](../../experiments/run_hls_s7_mechanistic_robustness.py). El éxito de un periodo no cuenta tareas individuales; `D_t` suma dimensiones y no es una tasa entre 0 y 1. |
| **Recursos:** producción `E_t=Σ_{ik}e_{ikt}`, enseñanza `H_t=2h_t` por lección de esfuerzo `h_t`, uso `E_t+H_t`, ociosidad `B_t-(E_t+H_t)` bajo el presupuesto aplicable; unidades de esfuerzo, `[0,B_t]`; menor coste deseable solo si el objetivo lo declara. En S2b, consumo es número de asignaciones, en `[0,B]`. | S2b: restricción intertemporal; S4/S7: restricciones individual/colectiva y diagnósticos de producción/enseñanza. Tiempo de ejecución de solver: segundos descriptivos. | [presupuesto S2b](../../experiments/run_hls_s2b_intertemporal_budget.py), [enseñanza/validación](../../src/hls/hls_lab_nk_teaching.py), [traza S4](../../src/hls/synthetic/hls_s4_transfer_exact.py). Una asignación y una unidad de esfuerzo no comparten escala; esfuerzo no es dinero. |
| **Desarrollo físico:** `Δc_{ikt}=c_{ik,t+1}-c_{ikt}`; unidades de competencia, habitualmente `[0,1-c_{ikt}]` bajo MIS-v2/enseñanza sin shocks; ↑ solo si la competencia será útil. Lecciones y momento: recuento/periodo, ≥0. | S4/S7: diagnóstico de exposición MIS-v2, transferencia y estado final; no premio terminal en Bellman actual. | Estado antes/después, esfuerzo, acción docente; [MIS-v2](../../src/hls/hls_lab_nk_learning.py), [transferencia](../../src/hls/hls_lab_nk_teaching.py), [S4 exacto](../../src/hls/synthetic/hls_s4_transfer_exact.py). Cambio total no identifica por sí solo qué transición lo produjo si ambas actúan; las trazas distinguen ambas etapas. |
| **Estimación/información:** MSE `(|I||K|)^{-1}Σ_{ik}(\hat c_{ikt}-c_{ikt})²` para el conjunto declarado; en `[0,1]` si estimaciones y competencias están en `[0,1]`; ↓. Observaciones por pareja, edad, ventana y bonus: recuentos/periodos/unidades de índice. | S3b y S4 bayesiano: diagnóstico, no recompensa colectiva. | Estimaciones de política y verdad del evaluador; [S3b-E1](../../experiments/run_hls_s3b_e1.py), [estimación S4](../../src/hls/synthetic/hls_s4_estimation_planning.py). MSE global puede mejorar sin mejorar decisiones; verdad no entra al estimador. |
| **Decisión/tiempo:** fracción de decisiones óptimas `Σ_t1{R_t(u_t)=R_t^*}/T` si se usa igualdad de valor; `[0,1]`, ↑. Algunas trazas usan identidad de acción oracular, que puede diferir bajo empates. Recuperación después de cambio: retraso definido por criterio predeclarado. Tiempo de cómputo: segundos por ejecución. | S3b-E1, GLR y S7: diagnósticos de elección/recuperación; S1/S2/S4/S7: tiempos descriptivos. | Acción, oracle, cambios reales y reloj; [S3b-E1](../../experiments/run_hls_s3b_e1.py), [S7](../../experiments/run_hls_s7_mechanistic_robustness.py). Cambios de matching no son costes de conmutación sin modelo de coste. Pequeños tiempos de instancia no prueban escalabilidad. |
| **Contrastes:** `J_B-J_A` (transferencia opcional exacta), `J_A-J_M` (planificación bajo objetivo/catálogo declarado), interacciones `(J_{11}-J_{10})-(J_{01}-J_{00})`; unidades del objetivo, signo dependiente del estimando. | S2b, S4, S7 y factoriales S3b/S4: comparación entre referencias/políticas. | Misma instancia, objetivo, información y diseño pareado; [S4 interacción](../../experiments/run_hls_s4_transfer_interaction.py), [S7](../../experiments/run_hls_s7_mechanistic_robustness.py). Una brecha frente a un miope con desempate fijo no prueba sacrificio inmediato estricto; interacción cerrada incluye cambio de acciones. |

Las cifras históricas ilustran unidades diferentes: S1 exacto `2.60` recompensa de asignación; S2a exacto acumulado `8.00` con `7.20` greedy; S2b con presupuesto `B=1`, Bellman `1.00` y miope `.90`; en S3b las recompensas esperadas y regrets se calculan frente a su propio oráculo; S7 central da CES `3.1628653621/3.1743777327` con déficit `0.04995/0.175`. No se transforman entre sí. La tasa de servicio N×K, un recuento de aristas y la recompensa Bernoulli no son la misma magnitud, aunque puedan denominarse “éxito”. **Rectificación de alcance respecto a la auditoría conceptual anterior:** el S4 canónico de asignación binaria optimiza `Σc·x`; solo las referencias S4 de producción/transferencia N×K aquí citadas optimizan CES. En la instancia S7 de caracterización, los pesos CES son unitarios sobre la competencia demandada, por lo que su discrepancia CES/servicio procede de umbrales, agregación temporal y reasignación de esfuerzo, no de sustitución simultánea entre competencias dentro del CES de cada periodo.

### 2.2 Estado de disponibilidad de datos

La existencia de una función calculadora no implica que todas las trazas la hayan guardado. S2a/S2b conservan demanda y unidades asignadas; S3b conserva reward esperado/realizado, oracle y diagnósticos de feedback según runner; S4 registra CES, éxito, déficit y recursos en las campañas indicadas; S7 mecanístico conserva expectativas exactas de CES, servicios, déficit, esfuerzo y enseñanza. Calidad externa del resultado, coste monetario, SLA humano y prioridad de tareas **no están definidos** en esos artefactos. El perfil de §7 debe distinguir `no_aplicable` (concepto fuera del problema), `no_disponible` (variable inaccesible o no identificable), `no_medido` (concepto definido pero no registrado) y `0` (valor numérico medido). La verdad del simulador puede servir al evaluador, pero nunca se hace observación de la política por utilizarla en una métrica offline.

## 3. Taxonomía flexible HLS-PEF

| Función de la métrica en un estudio | Preguntas y ejemplos | Condición de uso |
|---|---|---|
| **Rendimiento colectivo** | Efectividad/cumplimiento, calidad específica, recursos/eficiencia, rendimiento por tiempo, robustez y adaptación. | Definir unidad de demanda y resultado, horizonte, orientación y acceso a datos; eficacia y calidad no son sinónimos. |
| **Diagnóstico organizativo** | Competencia final y desarrollo MIS-v2, transferencia efectiva, especialización, uso por agente, distribución de carga, observaciones recibidas, cambios de organización y uso de recursos. | Son variables explicativas o resultados intermedios; en bucle cerrado la política altera muchas simultáneamente. Un cambio de matching no es coste salvo que se haya modelado. |
| **Contraste comparativo** | Ganancias de planificación, transferencia y cooperación, beneficio de heterogeneidad, regret, coste de información incompleta e interacción factorial. | Requiere contraste identificable: mismos estados/demanda/restricciones/objetivo o intervención explícita. Cooperación y heterogeneidad no disponen de un estimando transversal único en S1–S7. |

La etiqueta depende de la pregunta: déficit puede ser resultado primario, restricción o diagnóstico; recursos pueden ser restricción dura y también consumo medido. Evitar incluir la misma carga docente como restricción y penalización monetaria sin distinguir escasez de coste; evitar premiar competencia final y sus outputs futuros dos veces. Una comparación de mecanismos físicos bajo acciones fijas y una comparación de políticas cerradas son estimandos diferentes.

## 4. Catálogo mínimo M1–M10

**Convenciones comunes.** Una unidad de servicio `j` pertenece al tipo `k(j)` y tiene periodo `t(j)`, requisitos declarados y decisión/outcome observables por el evaluador. `\mathcal D` es el conjunto de unidades efectivamente demandadas; debe declararse si se trata de peticiones, tareas indivisibles o problema-periodo. Ninguna tasa se calcula solo sobre tareas que la política decidió atender. Sea `n_k=|{j∈\mathcal D:k(j)=k}|`. Las medias estocásticas se estiman por réplicas independientes (semillas), preservando emparejamiento; el árbol exacto informa esperanza exacta bajo el modelo, sin IC de muestreo. Una métrica definida sobre una política histórica no se convierte por ello en objetivo que esa política optimizara.

### M1. Tasa de cumplimiento funcional

- **Definición e interpretación:** `F=Σ_{j∈\mathcal D} s_j/|\mathcal D|`, `s_j∈{0,1}` según requisitos de esa unidad. Fracción de demanda satisfecha, no calidad media. En N×K actual, `j` es problema-periodo y `s_j` exige todos sus requisitos activos; en S2a puede ser unidad demandada atendida.
- **Datos; unidad/rango; sentido:** demanda completa, requisitos, outputs/atención y regla de éxito; proporción `[0,1]`, ↑. No asumir que S1/S3b Bernoulli constituye un servicio funcional sin declarar el requisito.
- **Heterogeneidad, incertidumbre y tiempo:** reportar soporte `n_k` y tasa por tipo; acumular numerador/denominador en un horizonte fijo o mostrar `F_{1:t}`. Para aleatoriedad, media/IC por réplica o esperanza exacta. No mezclar distinto valor o número de tareas sin declarar pesos.
- **Degeneraciones/límites:** si `|\mathcal D|=0`, indefinida; nunca sustituir por 0 o 1. Umbral binario oculta severidad de déficit y sobrecumplimiento. Una tarea multiagente se cuenta una vez después de agregar sus contribuciones.

### M2. Cumplimiento equilibrado por tipos

- **Definición e interpretación:** `F_{macro}=|K_+|^{-1}Σ_{k∈K_+}(Σ_{j:k(j)=k}s_j/n_k)`, `K_+={k:n_k>0}`. Da igual peso a cada tipo presente; complemento informativo de la tasa micro M1.
- **Datos; unidad/rango; sentido:** tipo, demanda y éxito por unidad; proporción `[0,1]`, ↑. Reportar también `n_k`, M1 y cada tasa por tipo.
- **Heterogeneidad, incertidumbre y tiempo:** las clases ausentes se excluyen y se señalan; si el objetivo requiere un universo fijo de tipos, el peso objetivo debe declararse externamente, sin imputar cero. Para periodos cortos, agrupar con soporte suficiente; réplicas independientes definen incertidumbre.
- **Degeneraciones/límites:** indefinida sin tipos demandados. Igualar tipos puede sobrerrepresentar clases raras; no ajusta automáticamente dificultad, criticidad o recursos. Variar los tipos presentes entre instancias cambia el estimando.

### M3. Calidad o valor medio del resultado

- **Definición e interpretación:** `Q=Σ_{j∈\mathcal D} v_j/|\mathcal D|` para una variable de calidad/valor `v_j` declarada, con tratamiento explícito de no atendidos. Puede ser exactitud, utilidad, error transformado o un valor de servicio específico; **no hay fórmula universal**. Si se informa `Q_cond=Σ_{atendidos}v_j/n_atendidos`, publicar cobertura M1: condicionar a atendidos puede premiar selección de casos fáciles.
- **Datos; unidad/rango; sentido:** outcomes o evaluación humana/automática y escala de `v`; unidades/rango de `v`, orientación según su contrato. CES y recompensa de asignación son candidatos solo donde fueron definidos como valor.
- **Heterogeneidad, incertidumbre y tiempo:** reportar calidad por tipo/dificultad y agregación predeclarada; si hay ruido, media/IC por réplica o validación de medida; media temporal usa denominador de demanda o periodo declarado.
- **Degeneraciones/límites:** sin resultado para tareas omitidas, la calidad incondicional puede ser `no_disponible`, no cero salvo que cero sea una consecuencia del problema. Comparar escalas distintas o confundir estimación del agente con calidad evaluada invalida el contraste.

### M4. Déficit funcional normalizado

- **Definición e interpretación:** por unidad con requisitos activos `A_j`, `D_j=Σ_{k∈A_j}(q_{jk}-y_{jk})_+/q_{jk}`; agregar `\bar D=Σ_jD_j/|\mathcal D|` o por tipo con regla declarada. Es la ley N×K existente; no es una fracción de servicios fallidos.
- **Datos; unidad/rango; sentido:** requisitos positivos y outputs por dimensión; `D_j∈[0,|A_j|]`, sin unidad, ↓. Déficit absoluto conserva unidades de output y debe informarse por dimensión si estas importan.
- **Heterogeneidad, incertidumbre y tiempo:** soporte, número de requisitos activos y dificultad se informan; no comparar sin cautela sumas con diferente `|A_j|`. Agregación por demanda y curvas de déficit acumulado o medio; incertidumbre por réplica o árbol exacto.
- **Degeneraciones/límites:** `q=0` se excluye; unidad sin requisito activo está fuera de `evaluate_problem_nk` actual y se marca `no_aplicable` hasta definirla. Una suma pequeña puede ocultar un fallo crítico; sobreproducción no compensa déficits positivos porque se trunca.

### M5. Coste total de recursos

- **Definición e interpretación:** vector `C=(Σ_t c_{rt})_{r∈\mathcal R}` por tipo de recurso: esfuerzo, tiempo, energía, cómputo, dinero, etc. Solo si hay precios/conversiones justificadas, escalar `C^p=Σ_{t,r}p_{rt}c_{rt}`. En N×K actual, `c_esfuerzo,t=Σ_{ik}e_{ikt}+2h_t`; en S2b es conteo de asignaciones bajo presupuesto global.
- **Datos; unidad/rango; sentido:** cargas de producción/enseñanza y límites, o recursos definidos externamente; unidades físicas por componente, ≥0 y acotadas por presupuesto si existe. Minimizar condicionado a servicio/calidad, no por sí solo.
- **Heterogeneidad, incertidumbre y tiempo:** consumo por tarea, agente y régimen, además de acumulado; demandas distintas pueden cambiar coste necesario. Informar variabilidad de consumo entre réplicas; no equiparar esfuerzo N×K, asignación S2b y segundos de CPU.
- **Degeneraciones/límites:** cero uso puede significar inactividad, no eficiencia. Un presupuesto duro y un precio de escasez son conceptos distintos; no añadir cargo al reward sin definir su unidad. Tiempo medido en instancias pequeñas es descriptivo, no evidencia de escalabilidad.

### M6. Eficiencia respecto a recursos consumidos

- **Definición e interpretación:** si `V` y coste escalar `C>0` están definidos, `η=V/C`; alternativa menos degenerada: mínimo coste sujeto a un umbral de servicio/calidad declarado o distancia a una frontera factible. Indica valor por recurso según `V`, no un valor colectivo universal.
- **Datos; unidad/rango; sentido:** el mismo resultado definido para M3/M1 y recursos comparables de M5; unidades `V/recurso`, ≥0 si ambos no negativos, ↑ bajo contrato fijo. El coste puede ser vector y entonces se necesita Pareto en vez de ratio.
- **Heterogeneidad, incertidumbre y tiempo:** comparar únicamente la misma mezcla de demanda y oportunidad de trabajo; calcular ratio de agregados o media de ratios con una elección explícita. IC por réplica para la transformación completa, no por periodos autocorrelacionados.
- **Degeneraciones/límites:** `C=0` hace el ratio indefinido; no añadir un ε arbitrario. Los ratios pueden premiar producir poco o abandonar tareas difíciles; acompañar de servicio, déficit y coste absoluto.

### M7. Rendimiento acumulado y evolución temporal

- **Definición e interpretación:** para valor instantáneo `v_t` declarado, `J_{1:t}=Σ_{s≤t}v_s` y tasa `\bar v_t=J_{1:t}/t`; puede ser CES, recompensa esperada, servicio o utilidad, pero se conserva su unidad. Una curva permite ver cuándo se gana o pierde.
- **Datos; unidad/rango; sentido:** serie temporal alineada con demanda, acciones y valor; rango acumulado derivado de la escala/horizonte, orientación de `v`. Si el objetivo incluye descuentos, declararlos y no compararlo con suma simple.
- **Heterogeneidad, incertidumbre y tiempo:** informar recompensa por régimen/tipo y horizonte; emparejar trayectorias ambientales cuando procede. Bandas estadísticas se calculan por réplica de curva, no tratando periodos como réplicas independientes; árbol exacto da esperanza temporal.
- **Degeneraciones/límites:** distintas duraciones, carga o reward por periodo impiden comparar totales absolutos; dividir por `T` no elimina diferencias de demanda/acciones. Recompensa realizada y esperada no son intercambiables.

### M8. Robustez ante perturbaciones

- **Definición e interpretación:** declarar antes el conjunto/distribución `\Omega` de perturbaciones y referencia `ω_0`. Ejemplos legítimos: peor valor `min_{ω∈\Omega}J(π;ω)` o pérdida `J(π;ω_0)-J(π;ω)` por perturbación; también probabilidad de violar un requisito. No existe un único escalar de robustez sin `\Omega`.
- **Datos; unidad/rango; sentido:** escenarios perturbados, política fijada o protocolo de reoptimización explícito, valores/servicios; unidades del `J` o probabilidad `[0,1]`, peor valor ↑ y pérdida ↓. Perturbaciones pueden ser demanda, competencia, recursos u observación, sin mezclarlas silenciosamente.
- **Heterogeneidad, incertidumbre y tiempo:** alinear tipo/intensidad de perturbación y horizonte; pares de semillas para diferencias. Si se reentrena o replanifica, medirlo como arquitectura adaptativa distinta. Reportar curvas o conjunto, no solo mínimo.
- **Degeneraciones/límites:** conjunto vacío/no declarado: `no_aplicable`; peor caso depende de la amplitud elegida; una normalización no crea comparabilidad con otra perturbación. S7 local OAT prueba una vecindad concreta, no robustez general.

### M9. Adaptabilidad tras cambios de régimen

- **Definición e interpretación:** dados cambios reales `τ_j`, un gap por periodo a referencia válida `g_t=V_t^*-V_t(π)` y criterios predeclarados `(ε,h)`, definir `G_h(t)` como la media de `g_t,…,g_{t+h-1}` o como su máximo, según se haya declarado. El retraso es `A_j=min{ℓ≥0:G_h(τ_j+ℓ)≤ε}`, restringido a ventanas completas anteriores al siguiente cambio o fin del horizonte. Complementar con regret/servicio durante los periodos posteriores.
- **Datos; unidad/rango; sentido:** tiempos y regímenes verdaderos para evaluador, acciones, valores/oráculo por régimen y horizonte; retraso en periodos, `≥0` si recupera, ↓. La política no recibe etiquetas de cambios salvo que el modelo lo permita.
- **Heterogeneidad, incertidumbre y tiempo:** normalizar solo si la duración de régimen y criterio coinciden; reportar por transición, incluidos cambios que no alteran decisión óptima. Incertidumbre por réplica y censura si no se recupera antes del siguiente cambio o final.
- **Degeneraciones/límites:** sin cambios relevantes: `no_aplicable`; sin recuperación: censurado, no cero ni lag inventado. Definir `ε` en unidades del gap y cómo tratar empates; la tasa de detección no equivale a recuperación ni a mejor rendimiento acumulado. S3b-E1 usó un criterio específico de 20 decisiones óptimas consecutivas, no uno universal.

### M10. Ganancia frente a referencia

- **Definición e interpretación:** para objetivo con orientación ↑, `G=J(π)-J(b)` y, si `J(b)≠0` y escala de razón interpretable, `G_rel=G/|J(b)|`. Para una pérdida ↓, invertir el signo de la diferencia. Regret a oráculo es un caso con referencia superior y signo orientado a pérdida.
- **Datos; unidad/rango; sentido:** valores de política y baseline bajo mismo sistema/objetivo/feasible set, diseño emparejado y referencia predeclarada; diferencia en unidades de `J`, sin rango universal, ↑. Una referencia exacta o cota requiere sus hipótesis de información y cómputo.
- **Heterogeneidad, incertidumbre y tiempo:** contrastes por semilla/instancia común e IC de diferencias pareadas; presentar por demanda/régimen y horizonte además de total. Baselines distintos por escenario cambian el estimando.
- **Degeneraciones/límites:** `J(b)=0` impide ratio; un baseline deliberadamente débil infla ganancia; un oráculo con más información sirve como cota, no como política realizable. Las brechas S7 frente a miope catálogo-primero contienen posible efecto de desempate; BEST-MYOPIC responde otra pregunta.

### 4.1 Demanda heterogénea y analogías con clasificación

M1 equivale a accuracy solo si cada unidad demandada produce exactamente una decisión con verdad binaria verificable y todos los errores tienen la misma unidad. M2 recuerda balanced accuracy cuando los tipos son clases con denominadores `n_k`; no corrige dificultad, prioridad ni ausencia de clase. Recall puede corresponder a demanda atendida sobre demanda total si “positivos” son todas las tareas que requerían servicio. Precision exige una noción de servicio ofrecido incorrectamente o falso positivo; en S2a/S4 no existe automáticamente esa matriz de confusión. F1 hereda esa necesidad y no debe calcularse por analogía nominal. Una evaluación cost-sensitive requiere costes/valores de error declarados; pesos CES no los proporcionan por sí solos.

La tasa micro responde “¿qué fracción de la demanda observada se completó?”; la macro responde “¿cómo se comportó el sistema entre los tipos presentes?”. Ambas deben mostrar soportes. Requisitos/dificultad desiguales exigen perfiles por tipo y déficit, no una conversión automática de una métrica a otra. En tareas parcialmente satisfechas, M4 y calidad gradual complementan M1. En tareas multiagente, agregar outputs/contribuciones sobre todos los participantes antes de aplicar el requisito evita contar agentes como servicios.

### 4.2 Comparabilidad en tres niveles

| Nivel | Comparación directa posible | Condiciones, normalización y prohibiciones |
|---|---|---|
| **A. Políticas en la misma instancia/objetivo** | Diferencias absolutas pareadas de `J`, servicio, déficit y recursos; regret frente al mismo oráculo; Pareto de métricas con unidades declaradas. | Igual demanda potencial, leyes, acción factible, horizonte y reglas de evaluación; declarar diferencias de información. Ratio relativo solo con denominador no nulo y escala de razón. Una política puede ser mejor en CES y peor en servicio, como S7. |
| **B. Instancias del mismo escenario** | Tasas por unidad de demanda, macro por tipo con soporte y contrastes frente a una referencia común, si unidades/objetivo/requisitos son comparables. | Declarar horizonte, mezcla de tareas, dificultad, capacidad y presupuesto. Regret normalizado por diferencia oráculo-baseline `G/(J^*-J_b)` solo si denominador positivo, ambos referencias factibles y mismos significados; puede ocultar distinta dificultad. No comparar totales brutos por defecto. |
| **C. Escenarios/aplicaciones** | Comparación de perfiles y compromisos, o síntesis bajo una escala de valor validada externamente. | CES, servicios humanos, reward Bernoulli y esfuerzo no comparten unidad. No promediar métricas normalizadas de dominios distintos sin modelo de valor y ponderación predeclarados. Una frontera Pareto exige dimensiones semánticamente equivalentes y mismas restricciones; si no, solo puede informarse cada estudio en su contexto. |

## 5. Protocolo de evaluación

1. **Problema:** fijar población de demanda, unidad de servicio, modalidad B, decisiones y resultado relevante; declarar qué hace difícil la instancia.
2. **Sistema A:** documentar competencias/estado real, requisitos y prioridades, recursos, dinámica exógena/endógena y mecanismo de observación.
3. **Objetivo y restricciones:** escribir `J`, orientación, valor terminal/descuento si existe, factibilidad y costes con unidades. Declarar qué métricas no entran en `J`.
4. **Perfil de métricas:** elegir primaria(s), secundarias y diagnósticos M1–M10 con denominadores, fuentes, unidades y casos indefinidos. Predeclarar agregaciones temporal, micro/macro y por régimen.
5. **Políticas C:** fijar comparadores competitivos, algoritmos/parámetros y resolución de empates. Auditar información visible a cada uno; oráculos usan verdad solo para evaluación.
6. **Diseño de contraste:** fijar referencias, controles, contrafactuales factibles e hipótesis. Para mecanismos físicos, distinguir acciones emparejadas de bucle cerrado.
7. **Ejecución común:** compartir trayectorias exógenas y potenciales cuando proceda; registrar acciones, outcomes, requisitos, recursos e información sin filtrar verdad a políticas.
8. **Incertidumbre:** en caso determinista/exacto, verificar contra referencia independiente y reportar valor exacto; en estocástico, usar semilla/instancia independiente como réplica, IC pareados y separar reward esperado del realizado; con aprendizaje, registrar feedback disponible y estados/estimaciones por fase.
9. **Diagnóstico:** comprobar que el mecanismo se activó, alteró decisiones y produjo el efecto colectivo medido. Desglosar por tipo, régimen y periodo antes de atribuir causas; no tratar periodos correlacionados como réplicas.
10. **Interpretación:** informar compromisos entre métricas, resultados nulos/negativos, condiciones de validez y límites. Una superioridad bajo el objetivo declarado no se llama mejora general del servicio si otro indicador funcional empeora.

**EvaluationProfile conceptual**, sin implementación en esta fase:

```text
scenario_id, application_domain, organizational_problem,
decision_objective {formula, orientation, unit, horizon},
constraints {feasible_set, budgets, service_constraints},
primary_metrics[], secondary_metrics[], diagnostic_metrics[],
comparison_baselines[] {role, information, action_set},
information_regime {policy_observations, evaluator_only_truth},
temporal_horizon {period_unit, T, regimes}, uncertainty_model,
aggregation_rules {service_unit, denominators, micro_macro, time, seeds},
normalization_rules {formula, reference, undefined_cases},
metric_availability {metric_id: no_aplicable | no_disponible | no_medido | valor}
```

Las entradas de disponibilidad pertenecen a cada artefacto, no solo al escenario. `no_aplicable`: concepto ausente del problema; `no_disponible`: no observable/identificable para el evaluador bajo los datos existentes; `no_medido`: definible pero no registrado; `valor=0`: cero observado/calculado, nunca un sustituto de los tres estados anteriores. Una métrica puede requerir datos de evaluador que la política no recibió; el perfil registra ambas visibilidades.

## 6. Perfiles mínimos por escenario S1–S7

Estos perfiles documentan disponibilidad; no reoptimizan ni reinterpretan resultados históricos.

| Configuración | Objetivo histórico y métricas disponibles | Perfil PEF mínimo y métricas útiles que faltan | Precaución de comparación |
|---|---|---|---|
| **S1** estática B2 | Maximizar suma de `C·x`; reward, asignación, factibilidad, greedy y enumeración. | Primaria M7 reward de un periodo; M10 exacto−greedy; diagnósticos aristas/capacidad. M1 funcional requiere definir unidad requerida y calidad de cumplimiento; `C·x` no equivale a éxito de servicio. | Exactitud matemática de matching, no superioridad general de arquitectura. |
| **S2a** demanda variable separable | `Σ_t C·x`, demanda/atención/no atención por tipo, rewards por periodo, enumeración global. | M1 sobre unidades demandadas es calculable; M2 por tipo con soporte; M7 reward y M10 exacto−greedy, carga de agentes. No hay calidad funcional más allá de atención. | Diferencia de rewards no equivale a más unidades atendidas; periodos sin demanda hacen tasa indefinida. |
| **S2b** presupuesto compartido | Reward total, uso/resto de `B`, demanda atendida, Bellman/miope/enumeración. | M7, M5 en unidades de ejecución, M10 ganancia de planificación, M1/M2 si demanda por unidad; curva de agotamiento. Calidad fuera de `C·x` no definida. | Valorar presupuesto como coste adicional cambiaría objetivo; caso pequeño verifica acoplamiento, no escalabilidad. |
| **S3a** cambios exógenos observables | Reward esperado/cumulativo, gap a asignación oracular en condiciones evaluadas, trazas de observación/ruido según campaña D0/D1/D2. | M7 y M10 con oracle por periodo; M8/M9 solo con perturbaciones y regla de recuperación fijadas; registrar MSE si existe estimación. Éxito funcional no está definido por reward de arista. | El caso perfectamente observable permite matching reactivo oracular; no extrapolarlo a feedback parcial. |
| **S3b-B1/B2** competencia desconocida, cambios exógenos | Reward esperado y Bernoulli realizado, regret oracular, decisiones, observaciones, MSE/índices, regímenes, retraso definido en E1/GLR, recursos según modalidad. | Primaria M7 o regret M10 con oráculo de cada modalidad; M9 con criterio explícito, M8 si perturbaciones predeclaradas; diagnósticos de feedback por pareja, incertidumbre y asignación. Calidad o servicio funcional externo: no disponible. | B1/B2 tienen espacios de acciones, reward máximo y feedback distintos; regrets absolutos no son comparables. MSE global no garantiza buenas decisiones. |
| **S4** competencia endógena y transferencia | En S4 binario inicial: reward lineal `Σc·x`, Bellman/reactiva/BEST-MYOPIC y MIS-v2. En S4 N×K de transferencia: CES, éxito/déficit, competencia pre/post MIS/docencia, esfuerzo/ociosidad y lecciones; P0/P1/P2 usan ranking funcional. | Perfil del binario: M7 reward lineal y M10 frente a BEST-MYOPIC. Perfil N×K: si se estudia output, M7 CES primaria y M1/M4/M5 diagnósticas; un objetivo de servicio nuevo requeriría declaración previa. M10 exige mismo objetivo/catálogos; desarrollo físico diagnóstico. | No combinar números del S4 binario con los del N×K como si compartieran reward. P0/P1/P2 y Bellman N×K optimizan criterios distintos; una ganancia frente a miope fijo puede depender de empates. |
| **S7** demanda Markov incierta, MIS-v2/enseñanza | CES esperado exacto; éxito, fallos, déficit, esfuerzo, docencia, cuatro valores de planificación/transferencia y sensibilidad local. | M7 CES primaria histórica; M1/M4/M5 y desarrollo por rama como diagnósticos; M8 solo para perturbaciones fijadas; M10 cuatro contrastes. Calidad externa y costes monetarios no definidos. | CES `3.162865→3.174378` coexistió con servicios `3.001→3.000` y déficit `.04995→.175`; la brecha Bellman−miope fijo incluye desempate. |

S4 y S7 ofrecen una validación negativa necesaria para PEF: dos políticas pueden ordenarse de forma opuesta según CES y servicio. El PEF deberá mostrar ambos resultados con sus unidades y definir previamente cuál responde a la pregunta organizativa. No se recalcula una campaña histórica con otro objetivo ni se etiqueta retrospectivamente una política como óptima para él.

## 7. Aplicabilidad externa (hipótesis de transferencia conceptual)

| Dominio | Demanda y resultado | Requisitos/recursos posibles | Métricas informativas y límite de traslado |
|---|---|---|---|
| **Gestión de trabajadores** | Órdenes, turnos o casos; servicio entregado, calidad verificable. | Plazo, certificación, seguridad, cobertura; horas, fatiga, formación y dinero si medidos. | M1/M2/M4 por tipo y M5/M9; competencia simulada no equivale a cualificación humana ni esfuerzo abstracto a coste salarial. |
| **Sistemas multiagente** | Misiones/subtareas; éxito conjunto, salida por componente. | Cobertura, coordinación, precedencia; energía, comunicación, tiempo. | Servicio conjunto, calidad, carga/recursos y robustez; recompensa aditiva de matching no representa automáticamente cooperación o dependencias. |
| **Sistemas de IA/agentes especializados** | Solicitudes y herramientas; respuesta verificada o utilidad de usuario. | Exactitud, seguridad, latencia; tokens, llamadas, energía o coste monetario si medidos. | M1/M3/M5/M6/M9 con evaluador válido; score interno de modelo y CES físico no son calidad de respuesta. |
| **ML y clasificación** | Ejemplos etiquetados; predicción frente a etiqueta. | Umbrales de error por clase; cómputo, datos/etiquetado, tiempo. | Accuracy, macro recall/balanced accuracy, precision/F1 cuando TP/FP/FN definidos, coste sensible con pesos externos. La asignación HLS no genera por sí sola una matriz de confusión. |
| **Híbridos rápido/profundo** | Flujo de solicitudes; respuestas de ruta rápida/profunda y escalamiento. | Calidad mínima, plazo; latencia, cómputo, energía. | Curva calidad-coste, cumplimiento por dificultad y ganancia frente a router fijo; “profundo” no presupone mayor calidad ni consumo medido en las instancias HLS actuales. |

Estas filas son posibilidades de especificación, no validaciones experimentales de HLS en esos dominios.

## 8. Riesgos metodológicos

1. Cambiar objetivo después de ver cuál política gana, o usar pesos/umbrales sin fuente organizativa.
2. Llamar “servicios completados” indistintamente a aristas, Bernoulli positivos y problemas-periodo plenamente satisfechos.
3. Informar tasas sobre trabajos atendidos en vez de demanda completa; ocultar tipos ausentes o imputarlos como cero.
4. Comparar CES, reward de matching, déficit y esfuerzo como si compartieran unidades; convertir un presupuesto duro en coste monetario sin precio.
5. Usar una razón de eficiencia con denominador cero, o un baseline demasiado débil; presentar normalización como equivalencia entre dominios.
6. Calcular IC con periodos correlacionados como réplicas, mezclar reward realizado con regret esperado, o esconder la censura de recuperación.
7. Atribuir a planificación una mejora dependiente del desempate miope; atribuir a una transición física la diferencia entre políticas cuyas acciones divergen.
8. Convertir verdad del evaluador en información de la política; valorar competencia futura dos veces cuando ya mejora reward futuro.
9. Interpretar mejora CES como mejora de servicio funcional: S7 ofrece un contraejemplo concreto dentro del modelo.

## 9. Propuesta de implementación mínima posterior

Una vez aprobadas las decisiones del §10, una implementación acotada podría añadir **solo una capa de evaluación offline**, sin alterar los solvers ni resultados S1–S7:

1. Esquema versionado de `EvaluationProfile` y estado explícito de disponibilidad; validación de unidades, denominadores y papel de cada campo.
2. Adaptadores de lectura para **dos artefactos existentes de semántica distinta**: S2a (unidades discretas y recompensa lineal) y S7 mecanístico (problema-periodo, CES, éxito, déficit y esfuerzo). Leer sin reescribir los JSON.
3. Calculadoras puras iniciales para M1, M2, M4, M5 y M10 solo cuando los datos y referencias son suficientes; M3/M6/M8/M9 permanecen declarables como no aplicables/no disponibles/no medidos hasta fijar contratos específicos.
4. Pruebas de casos degenerados: demanda vacía, tipo ausente, requisito cero, coste cero, baseline cero, oráculos distintos y estado “no medido” distinto de cero.
5. Informe compacto que muestra objetivo histórico y diagnósticos lado a lado, con procedencia y unidad. Validar que reproduce agregados almacenados; divergencias deben ser auditadas, nunca corregidas silenciosamente.

Este es un diseño para autorización posterior, no una nueva arquitectura de decisión ni una campaña experimental.

## 10. Decisiones pendientes del PI

1. **Unidad de servicio por configuración:** petición, tarea, problema-periodo y regla para trabajos parcialmente satisfechos o multiagente.
2. **Objetivos científicos prioritarios:** cuándo CES es producción que se optimiza, cuándo servicio/deficit es el objetivo, y qué garantías funcionales deben actuar como restricciones. Mantener históricos con su objetivo original.
3. **Prioridades:** si tipos/tareas tienen pesos de importancia, su fuente externa y su separación de pesos CES.
4. **Costes:** qué recursos se valoran como vector, cuáles tienen precio y qué presupuestos son solo restricciones.
5. **Comparadores:** para nuevas afirmaciones de valor de planificación S7, si se exige la envolvente BEST-MYOPIC junto al baseline de desempate fijo.
6. **Perfil mínimo aprobado:** M1/M2/M4/M5/M7/M10 según disponibilidad, y contratos específicos para calidad, eficiencia, robustez y adaptación antes de calcular M3/M6/M8/M9.

**Recomendación:** aprobar HLS-PEF como protocolo de declaración y evaluación, con un catálogo extensible de definiciones y un núcleo de campos obligatorios, sin imponer una puntuación única. La primera implementación debe limitarse a lectura offline y verificación de métricas inequívocas en artefactos existentes. El PI debe resolver primero la unidad de servicio y el papel de CES frente a cumplimiento funcional; de ello depende qué métricas serán primarias en un problema dado.

## 11. Fase 2 — implementación mínima y validación retrospectiva (2026-10-22)

Esta sección añade evidencia técnica sin cambiar las decisiones conceptuales de la fase 1. El módulo independiente [`performance_evaluation.py`](../../src/hls/performance_evaluation.py) no importa simuladores, transiciones ni políticas. `EvaluationProfile` declara escenario/configuración, objetivos por política, demanda/horizonte, restricciones, métricas, régimen informacional y unidades de recursos. `EvaluationRecord` contiene un problema-periodo observado por el evaluador y su procedencia. `EvaluationResult` conserva valor, unidad, definición versionada, agregación, estado y punteros de procedencia. `PerformanceEvaluator.register_profile`, `.evaluate`, `.import_historical`, `.unavailable` y `.compare` constituyen la API pública inicial. No hay normalización universal ni cálculo de eficiencia.

**Estados.** `VALID` exige valor finito y procedencia; `NOT_APPLICABLE` indica concepto fuera del perfil; `NOT_OBSERVABLE`, información que el evaluador no puede identificar; `NOT_RECORDED`, campo necesario ausente del artefacto; `UNDEFINED`, fórmula sin denominador válido (por ejemplo, cero periodos demandados). Ninguno se representa mediante cero ni NaN. Un cero medido es `VALID, value=0`. La disponibilidad se declara por perfil y el evaluador no rellena campos faltantes con transiciones físicas o simulaciones.

**Métricas implementadas.** La recompensa original acumulada suma `original_reward` con un identificador de definición ligado al objetivo declarado de cada política. El CES acumulado suma únicamente valores `ces` explícitamente registrados; no se identifica automáticamente con reward. El cumplimiento es `Σ success / número de problemas-periodo demandados`; el déficit funcional es `Σ_{t,k} deficit_{kt}` **absoluto**, no el déficit normalizado del catálogo M4 de fase 1; la producción acumulada es `Σ_{t,k} output_{kt}`; recursos se agregan por tipo con unidad declarada. La diferencia entre políticas resta una métrica solo si coinciden escenario, configuración, definición, unidad, horizonte, agregación y distribución de demanda. Regímenes informacionales distintos requieren autorización explícita y el resultado queda etiquetado `informationally_unequal`. Un mismo estudio puede comparar políticas que optimizan objetivos distintos mediante métricas de evaluación comunes; no compara como idénticas sus recompensas originales si sus definiciones difieren.

**Datos históricos auditados y límite de reconstrucción.** [`S4 exacto N×K`](../../results/experiments/hls_s4_transfer_exact/results.json) conserva tres periodos de A/B con reward, output vectorial, requisitos por diseño, éxito, déficit vectorial y esfuerzo productivo/docente/total: estas métricas se recalculan desde registros de periodo. [`S7 caracterización`](../../results/experiments/hls_s7_preparation_characterization/results.json) conserva los cuatro valores CES exactos, pero solo ramas ilustrativas, no todas las trayectorias de las cuatro políticas. [`S7 mecanístico`](../../results/experiments/hls_s7_mechanistic_robustness/results.json) conserva expectativas exactas agregadas de CES, servicios, déficit y recursos. El runner [`run_hls_pef_retrospective.py`](../../experiments/run_hls_pef_retrospective.py) importa esas expectativas como *agregados históricos* con puntero JSON; la tasa funcional S7 divide el número esperado de servicios por el horizonte declarado `T=4`. No recalcula el árbol desde las ramas parciales. La producción S7 `Σy` queda `NOT_RECORDED`: los diagnósticos guardan esfuerzo, que no es producción. La calidad externa, costes monetarios y servicios por tarea tampoco se infieren.

**Validación reproducible.** El runner solo lee los tres JSON anteriores y escribe un artefacto nuevo en [`hls_pef_retrospective/results.json`](../../results/experiments/hls_pef_retrospective/results.json). En S4 exacto, A y B reproducen CES `1.9175`, tasa funcional `1/3`, déficit absoluto `.5325` y producción `1.9175`, todos desde periodos conservados; esa igualdad CES/producción obedece a los pesos unitarios de *esta* demanda, no es una identidad del marco. En S7 central, el agregado importado reproduce `J_A=3.1628653621`, `J_B=3.1743777327`, `J_MA=J_MB=3.0346209871`; los contrastes son `.1282443750`, `.1397567456`, `.0115123706`, `0` y la interacción `.0115123706`. S7 A/B tienen tasa funcional `.75025/.75000` y déficit absoluto `.04995/.175` **importados o derivados aritméticamente de expectativas almacenadas**, no recalculados desde trayectorias. El contraste CES no implica mejora funcional ni elimina la sensibilidad al desempate miope.

**Extensión controlada.** Para añadir una métrica: (1) fijar unidad de servicio, definición/versionado, unidad, agregación, casos degenerados y variables requeridas; (2) declarar su papel en el perfil; (3) implementar una agregación pura sobre `EvaluationRecord` o una importación histórica inequívoca; (4) añadir pruebas de falta de datos, cero válido, unidades, procedencia y comparabilidad. Un escenario futuro debe emitir registros de evaluador suficientes sin entregar verdad privilegiada a la política; la instrumentación de evaluación permanece separada de decisiones y física. No se autoriza aquí cambiar CES ni reoptimizar S1–S7.

## 12. Fase 3 — integración operativa y piloto S7 (2026-10-22)

El contrato común se amplió de forma compatible con los registros posicionales existentes. `EvaluationRecord` representa unidad/periodo, tipo de demanda, requisitos, output, calidad opcional, éxito, déficit, reward original, CES, recursos por nombre, contexto de política/objetivo, episodio y probabilidad de rama, régimen informacional, estado de competencias, metadatos y procedencia. `field_status` distingue explícitamente campos `NOT_APPLICABLE`, `NOT_OBSERVABLE` y `NOT_RECORDED`; `None` no se convierte en cero. En el piloto, la importancia y calidad externa no existen en el problema y se etiquetan `NOT_APPLICABLE`. El evaluador valida contexto, objetivo declarado, periodos, probabilidades y compatibilidad; `evaluate_weighted_episodes` calcula expectativas exactas desde registros por rama.

El adaptador genérico respecto al evaluador, [`s7_pef_adapter.py`](../../src/hls/synthetic/s7_pef_adapter.py), transforma replay ya producido por las referencias S7. El [runner](../../experiments/run_hls_pef_s7_pilot.py) recorre las 16 ramas de demanda de la instancia central T=4, incluida cada rama con probabilidad cero, y conserva sus probabilidades. El evaluador solo agrega registros. Las cuatro soluciones siguen siendo Bellman sin transferencia (A), Bellman con transferencia opcional (B), miope sin transferencia (MA) y miope con transferencia opcional (MB). El perfil declara CES como objetivo de todas; servicio/funcionalidad y recursos son métricas separadas. El importe docente `h` se registra como esfuerzo docente y el consumo de recurso existente `2h` se registra aparte.

| Política | CES esperado | Cumplimiento esperado por periodo | Déficit raw esperado | Producción total | Esfuerzo productivo | Esfuerzo docente | Recurso docente `2h` | Recurso total | Acciones docentes esperadas |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| A Bellman, sin transferencia | 3.1628653621 | 0.750250 | 0.049950 | 3.1675720885 | 8.0 | 0 | 0 | 8.0 | 0 |
| B Bellman, transferencia opcional | 3.1743777327 | 0.750000 | 0.175000 | 3.1743777327 | 7.0 | 0.25 | 0.5 | 7.5 | 1 |
| MA miope, sin transferencia | 3.0346209871 | 0.3019375 | 0.1023575625 | 3.0346209871 | 5.20775 | 0 | 0 | 5.20775 | 0 |
| MB miope, transferencia opcional | 3.0346209871 | 0.3019375 | 0.1023575625 | 3.0346209871 | 5.20775 | 0 | 0 | 5.20775 | 0 |

Producción total, CES y recompensa original se conservan como campos distintos, aunque en algunos renglones coincidan numéricamente. Las diferencias B−A son, respectivamente, CES `+0.0115123706`, cumplimiento `−0.00025`, déficit `+0.12505`, producción `+0.0068056442`, esfuerzo productivo `−1`, esfuerzo docente `+0.25`, consumo docente `+0.5`, recurso total `−0.5` y acciones de enseñanza `+1`. La interacción `(B−A)−(MB−MA)` se calcula por métrica con sus propias unidades; se reproduce para CES `+0.0115123706`. Para funcionalidad es `−0.00025` y para déficit `+0.12505`. No se agregan en una puntuación.

La validación comparó CES del replay ponderado con el valor del solver en cada política, reprodujo los cuatro valores históricos con tolerancia `1e-10`, verificó que las probabilidades suman uno, que los recursos docentes están separados del esfuerzo productivo y que cada rama conserva sus acciones/estados. El artefacto nuevo está en [`hls_pef_s7_pilot/results.json`](../../results/experiments/hls_pef_s7_pilot/results.json); las salidas históricas no se sobrescriben. Esto es un piloto determinista de integración, no nueva evidencia estadística sobre S7. El adaptador específico de escenario y el evaluador genérico permanecen en módulos separados para facilitar adaptaciones futuras.
