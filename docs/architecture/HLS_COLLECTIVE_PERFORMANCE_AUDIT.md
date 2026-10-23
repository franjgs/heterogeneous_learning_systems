# Auditoría conceptual del rendimiento colectivo en HLS

**Fecha:** 2026-10-22  
**Alcance:** análisis documental del modelo y las implementaciones existentes. No modifica leyes, objetivos ejecutables, resultados ni escenarios.

Fuentes inspeccionadas: [marco unificado](HLS_UNIFIED_FRAMEWORK.md), [ontología](HLS_ONTOLOGY_V0_1_2026-10-23.md), registro acumulativo, [`hls_lab_nk_production.py`](../../src/hls/hls_lab_nk_production.py), [`discover_v0.py`](../../src/hls/discover_v0.py), [`hls_lab_nk_geometry.py`](../../src/hls/hls_lab_nk_geometry.py), [`hls_lab_nk_learning.py`](../../src/hls/hls_lab_nk_learning.py), [`discover_develop_v2.py`](../../src/hls/discover_develop_v2.py), [`hls_lab_nk_teaching.py`](../../src/hls/hls_lab_nk_teaching.py), [`hls_lab_nk_policies.py`](../../src/hls/hls_lab_nk_policies.py), [`hls_s4_transfer_exact.py`](../../src/hls/synthetic/hls_s4_transfer_exact.py) y [`hls_s7_uncertain_demand.py`](../../src/hls/synthetic/hls_s7_uncertain_demand.py).

## 1. Resumen ejecutivo

HLS no optimiza hoy una única noción general de rendimiento colectivo. Cada experimento declara una recompensa o criterio concreto: por ejemplo, suma de recompensas esperadas en matching, regret frente a un oráculo, CES acumulado en las referencias exactas S4/S7, o una regla lexicográfica funcional en P0/P1/P2. La ontología ya advierte correctamente que CES, producción, éxito funcional, déficit y esfuerzo son magnitudes distintas.

La implementación productiva N×K separa producción determinista, recompensa CES, éxito funcional y déficit. El solver de S7 y las referencias intertemporales S4 optimizan la suma de CES actual, antes de las transiciones MIS-v2 y enseñanza. Las transiciones afectan el estado futuro, no la recompensa corriente. Los recursos productivos y docentes limitan las acciones factibles; salvo que un objetivo de escenario lo especifique, no se restan de la recompensa como coste monetario.

Esto explica matemáticamente el resultado central S7: Bellman con transferencia puede aumentar CES acumulado esperado de `3.1628653621` a `3.1743777327`, mientras los servicios funcionales esperados bajan de `3.001` a `3.000` y el déficit absoluto aumenta de `.04995` a `.175`. CES premia output agregado según pesos y curvatura; no impone los requisitos ni penaliza déficits. La trayectoria con transferencia redistribuye producción desde x hacia una preparación que favorece y futuro, pero deja mayor déficit funcional en x. No hay contradicción de implementación: son objetivos y diagnósticos diferentes.

Recomendación del CE: conservar CES como objetivo válido de **esas referencias** y como métrica comparable histórica, no como sinónimo ni objetivo universal de servicio. HLS debe declarar por configuración el objetivo primario, sus restricciones operativas, costes explícitos y métricas diagnósticas. Antes de nuevas afirmaciones de “mejora colectiva” en S4/S7, el PI debe decidir si la prioridad del problema es output CES, cumplimiento de servicios, déficit/prioridad, o un objetivo lexicográfico/constrained que los ordene explícitamente. No se recomienda insertar pesos de utilidad sin fundamento externo.

## 2. Definiciones actuales verificadas

### 2.1 Magnitudes físicas y de servicio

En la implementación N×K, sean `c[i,k]∈[0,1]` la competencia física, `e[i,k]≥0` el esfuerzo productivo y `k` una competencia/tipo de tarea. El output agregado por dimensión es

\[
y_k=\sum_i e_{ik}c_{ik}.
\]

Es una ecuación aditiva determinista. No representa por sí sola una asignación indivisible ni el éxito del servicio.

Para requisitos `r_k≥0`, la métrica funcional activa las dimensiones con `r_k>0`:

\[
\text{success}=\mathbf{1}\{y_k\ge r_k\;\forall k:r_k>0\},
\quad d_k=(r_k-y_k)_+,
\quad D_{norm}=\sum_{k:r_k>0}\frac{d_k}{r_k},
\quad m=\min_{k:r_k>0}(y_k-r_k).
\]

La comparación de éxito usa una tolerancia numérica `1e-12`. El déficit es truncado en cero si hay sobreproducción; `D_norm` es una suma, no un promedio. `success`, `deficits`, `normalized_deficit` y `margin` son observadores calculados por `evaluate_problem_nk`; no forman automáticamente parte del reward.

En N×K, la CES es

\[
R_{CES}(y;w,\rho)=\left(\sum_k w_k y_k^\rho\right)^{1/\rho},
\qquad w_k\ge0,\;\sum_k w_k=1,
\]

con `ρ=0.5` por defecto, heredado de DISCOVER-v0. Los pesos viven en `ProblemSpecNK`; si se omiten, el código usa pesos uniformes por dimensión. La fórmula recibe outputs y pesos, **no** requisitos. Por ello no garantiza `y_k≥r_k`, no aplica un coste por déficit y no aplica un coste de esfuerzo. Puede haber output CES positivo aunque el servicio falle; sobreproducción de una dimensión puede compensar parcialmente poca producción en otra según pesos y `ρ`. La CES no debe confundirse con capacidad productiva ni con utilidad neta.

### 2.2 Estado, desarrollo y recursos

| Concepto | Representación actual | No debe inferirse |
|---|---|---|
| **A. Competencia disponible** | Matriz física `c[i,k]`, en `[0,1]`. S4/S7 exactos la incluyen en el estado del oráculo. | No es una recompensa, un output, un éxito de servicio ni una medida de experiencia acumulada. |
| **B. Capacidad productiva** | Relación entre competencia y esfuerzo permitido por límites individuales, presupuesto colectivo y presupuesto del problema. | No es el output ya realizado ni significa que la capacidad esté disponible sin consumir recursos. |
| **C. Producción efectiva** | `y_k=Σ_i e_ik c_ik`, calculado antes de las transiciones. | No implica que se haya cumplido cada requisito. |
| **D. Servicio funcionalmente satisfactorio** | Indicador de que todos los requisitos activos se alcanzan; déficit y margen asociados. | No es el reward CES, ni está ponderado por importancia salvo que el escenario lo defina. |
| **E. Desarrollo futuro** | MIS-v2 y, si está disponible, transición docente actualizan competencias tras producción/reward. El nuevo estado cambia outputs futuros. | No recibe recompensa directa ni valor terminal en las referencias S4/S7 actuales. |
| **F. Coste de recursos** | Restricciones de factibilidad. Enseñar carga `e` al docente y `e` al aprendiz: `2e` de esfuerzo colectivo, además de cargas individuales. Se registran uso y ociosidad. | No es coste monetario ni se resta automáticamente de CES. El coste de oportunidad aparece indirectamente al reducir esfuerzo productivo factible. |

La ley MIS-v2 actualiza cada celda independientemente:
`c' = 1-(1-c) exp(-λ(η[i,k])e[i,k])`, `λ(η)=-log(1-η)`; solo el esfuerzo ejecutado en esa celda genera esa exposición. La enseñanza se aplica después de MIS-v2 al aprendiz indicado:
`c' = min(1, c + transfer_rate·e·T[teacher,learner,k]·(1-c))`. La competencia del docente no aparece directamente en esa eficacia. Estas transiciones cambian el estado futuro, pero no la producción ni el reward que ya se registraron en el periodo actual.

### 2.3 Qué optimizan las implementaciones

- **S1/S2a/S2b:** las referencias exactas maximizan la suma de recompensas de asignación declaradas, normalmente `Σ C[i,k]x[i,k,t]`; S2b añade presupuesto global. No son CES N×K.
- **S3b:** las políticas de asignación estiman recompensas de parejas; la evaluación utiliza recompensa esperada/regret frente al oráculo definido por modalidad. El regret no es una función objetivo que conozca la política.
- **Referencias exactas S4/S7:** `_step` calcula CES a partir del output pre-transición y Bellman maximiza la suma esperada/acumulada de ese CES. El reward no resta esfuerzo ni déficit, y no agrega un valor terminal de competencias.
- **Referencia miope S7:** en cada estado escoge una acción con máximo CES inmediato y luego propaga MIS-v2/enseñanza de esa acción para evaluar la trayectoria. No maximiza el desarrollo futuro al elegir.
- **P0/P1/P2 N×K:** no maximizan CES ni Bellman. Ordenan acciones lexicográficamente por `(success, -normalized_deficit, margin, -productive_effort)`. P1/P2 añaden su regla de relación docente, memoria de eficacia/umbral y acciones factibles; no valoran el efecto de enseñanza sobre asignaciones futuras mediante una función de valor de horizonte. La memoria de P2 no es un optimizador intertemporal.

Así, “HLS optimiza X” no tiene una respuesta única sin nombrar escenario, referencia/política y objetivo.

## 3. Diagnóstico de S4 y S7

### 3.1 Por qué S7 mejora CES y empeora indicadores funcionales

El caso central usa el mismo estado inicial, proceso C5, catálogo físico y leyes de transición. Bellman sin transferencia vale `3.1628653621`; con transferencia opcional, `3.1743777327`. El cambio de política inicial divide producción de x entre agentes y enseña y de A a B; el CES inmediato cae de `.35` a `.175`, se gastan `.5` recursos docentes y la competencia B/y aumenta `.08` tras MIS-v2. En ramas futuras y, ese estado puede producir más output y superar el umbral y `.95` antes.

Los agregados exactos sobre el árbol de demanda indican, en orden **Bellman sin → con transferencia**:

| Medida | Sin transferencia | Con transferencia |
|---|---:|---:|
| CES acumulado esperado (objetivo) | 3.1628653621 | 3.1743777327 |
| Servicios completados esperados | 3.001 | 3.000 |
| Incumplimientos esperados | .999 | 1.000 |
| Déficit absoluto total esperado | .04995 | .175 |
| Déficit normalizado acumulado | .0525789474 | .5 |
| Esfuerzo productivo acumulado | 8 | 7 |
| Recursos de enseñanza | 0 | .5 |
| Recursos totales utilizados | 8 | 7.5 |

La combinación de factores es verificable:

1. **Definición de CES:** usa outputs agregados con pesos/curvatura; no usa `r_k` ni el indicador de éxito. Por tanto, maximizarla no es maximizar servicios completados ni minimizar déficit.
2. **Agregación temporal:** Bellman suma CES de periodos. Un aumento pequeño de output en varios periodos futuros puede compensar una pérdida corriente, sin requerir que cada periodo cumpla el servicio.
3. **Umbral funcional:** el éxito es discontinuo y exige satisfacer todas las dimensiones activas. Una política puede superar el umbral de y más a menudo, pero fallar x por la inversión presente; el conteo esperado no pondera severidad del déficit.
4. **Enseñanza y recursos:** el evento consume esfuerzo de ambos participantes y desplaza producción actual. Ese coste no se resta dos veces: restringe factibilidad, pero no es un término negativo CES.
5. **Contabilidad de producción:** no se encontró un desacuerdo de implementación. Output, reward, competencias post-MIS y post-enseñanza se registran en orden separado; éxito/déficit se calculan sobre el output pre-transición. Las pruebas y el replay de S7 verificaron coincidencia entre reward replay y valor Bellman.

En S4 de bucle cerrado también se registró que CES y éxitos pueden ordenar las políticas de modo distinto; por ejemplo, en la evaluación de oportunidades de transferencia P2 obtuvo menos CES que P0 con el mismo número medio de éxitos, y en el factorial previo P2 no superó P0 en CES pese a logros funcionales similares. Esto no invalida CES: limita la interpretación de CES como “servicio” y exige decir qué resultado colectivo se pretende maximizar.

### 3.2 Hechos frente a interpretación

**Hecho matemático:** las ecuaciones implementadas permiten el ordenamiento divergente porque CES y los indicadores funcionales son funciones distintas de `y`; los requisitos no entran en CES. **Hecho experimental:** en la instancia S7 anterior se dio el cambio cuantitativo de la tabla. **Interpretación:** la inversión de esfuerzo hacia y prepara capacidad futura pero ocasiona déficit x presente; llamarlo una mejora global de servicio sería injustificado. Ninguno de estos hechos demuestra que CES sea una mala métrica en todo contexto.

## 4. Comparación de objetivos alternativos

Sea `s_t∈{0,1}` el éxito funcional, `d_{kt}` el déficit y `q_{kt}` importancia declarada. Estas son familias posibles para un problema concreto; ninguna se adopta automáticamente como nueva ley HLS.

| Objetivo | Definición posible | Interpretación y requisitos | Ventajas y riesgos |
|---|---|---|---|
| **O1. CES acumulado** | `max E Σ_t R_CES(y_t;w_t,ρ)` | Rendimiento agregado/sustitutivo según pesos y curvatura. Necesita outputs, pesos y horizonte. | Continuo y ya implementado/verificado. No garantiza umbrales, no resta recursos, puede compensar output de unas dimensiones con otras. Adecuado si la pregunta científica trata sobre ese índice, no como sinónimo de servicio. |
| **O2. Servicios completados** | `max E Σ_t s_t` | Cada periodo/tarea satisfecha cuenta como unidad. Necesita una definición estable de unidad de servicio y requisitos. | Directo para throughput funcional; ignora magnitud de fallos, prioridades y cuánto supera el umbral. Puede privilegiar muchos servicios sencillos sobre pocos críticos. |
| **O3. Déficit funcional** | `min E Σ_t Σ_{k:r>0} d_{kt}/r_{kt}` (o déficit absoluto declarado) | Penaliza insuficiencia relativa o absoluta. Necesita requisitos y unidades comparables. | Sensible a magnitud y severidad del incumplimiento. La versión normalizada suma ratios y puede contar varias dimensiones por servicio; la absoluta mezcla escalas. Sin recompensa por excedente, puede dejar de producir una vez cubiertos requisitos. |
| **O4. Servicio ponderado por importancia** | `max E Σ_t q_t s_t` o una función declarada de servicio/deficit ponderado por dimensión | Prioriza clientes/tareas/skills con peso exógeno justificable. Requiere fuente organizativa para `q`. | Puede expresar criticidad y SLA. Sin prioridades legitimadas, los pesos son arbitrarios; puede sacrificar servicio de baja prioridad deliberadamente. No debe confundirse importancia de tarea con peso CES por dimensión. |
| **O5. Multicriterio** | Vector `(servicio, CES/output, -déficit, -recursos, desarrollo futuro)` o una formulación constrained/pareto | Mantiene explícitos resultados que representan valores distintos. Requiere orden, presupuesto o preferencia institucional. | Evita ocultar tradeoffs dentro de un único escalar y permite fronteras Pareto. Riesgos: incomparable sin regla de elección, escalas incompatibles y doble conteo. Sumar competencias futuras a CES futuro puede contar dos veces el desarrollo, pues ya eleva producción futura. |
| **O6. Lexicográfico** | Primero maximizar servicio (o alcanzar metas), entre óptimos maximizar CES; luego minimizar recursos/desempatar | Expresa prioridades no compensatorias. Requiere orden institucional explícito y definir qué sucede si metas son inviables. | Evita que una ganancia pequeña de CES compre un fallo crítico. Puede imponer costes muy altos por una mejora marginal de servicio y producir saltos/discontinuidades; el orden es normativo, no deducible del código. |

O2/O3 pueden ser reward o, preferiblemente en ciertos dominios, restricciones operativas: por ejemplo, exigir un nivel mínimo de éxito y maximizar CES dentro de ese conjunto factible. Eso sigue requiriendo declarar si la meta es por periodo, por clase de tarea o en expectativa; no es una “corrección neutral”. O4 y O6 también requieren decisiones de política/operación fuera del simulador.

## 5. Propuesta de arquitectura de objetivos

Recomiendo una **familia explícita de contratos de rendimiento por configuración**, no una función universal para S1–S7 ni una suma ponderada común.

Cada escenario/pregunta debe declarar antes de comparar políticas:

1. **Objetivo primario** `J`: por ejemplo, recompensa de asignación, CES, servicios ponderados, o déficit. Es lo que optimizan las referencias del experimento.
2. **Restricciones operativas** `g_j(trajectory)≤b_j`: recursos, capacidad y, si el problema lo exige, mínimos de nivel de servicio. No convertir automáticamente todo indicador en restricción.
3. **Costes de decisión** incluidos en `J` solo si existe interpretación y escala explícitas; no confundir el consumo de un presupuesto duro con coste monetario.
4. **Diagnósticos independientes:** CES/output, éxito, déficit por tipo, margen, esfuerzo, enseñanza, recursos ociosos y estado final de competencias, según la pregunta. Se informan aunque no sean optimizados.
5. **Efectos futuros:** competencias son estado de transición; su valor aparece mediante futuras recompensas/restricciones. No añadir recompensa por “competencia desarrollada” salvo que el problema estudie explícitamente ese valor terminal.

Un modelo general puede mantener `J_θ=E[Σ_t r_θ(S_t,D_t,u_t,Y_t) + g_θ(S_T)]` sujeto a acciones factibles y restricciones operativas declaradas. El índice `θ` es parte del modelo del problema y debe tener semántica; no es un parámetro libre para favorecer una arquitectura. Se deben presentar de forma separada optimalidad matemática bajo `J_θ` y desempeño en cada diagnóstico de servicio/recurso.

Así CES puede seguir siendo objetivo principal en los estudios que preguntan por producción agregada con sustitución, una métrica secundaria en estudios de servicio cuya utilidad principal es otra, o un criterio interno dentro de una especificación multicriterio respaldada por el contexto. Cambiarlo por sí solo no resolvería los empates ni los problemas de atribución.

## 6. Auditoría de políticas miopes

### 6.1 Desempate ejecutado

En `solve_reactive_greedy` de S7, las acciones se recorren en orden del catálogo y `best_action` se reemplaza solo si el CES supera el mejor por más de `TOL=1e-12`. Por tanto, diferencias de hasta esa tolerancia se tratan como empate y gana la primera acción enumerada. El catálogo de S7 se genera desde los vectores de esfuerzo y, al permitir enseñanza, añade acciones con lección en orden declarado. No usa el futuro para desempatar; calcula el estado sucesor pero lo ignora al elegir el máximo inmediato. La política sí conoce el estado de competencia exacto en esa referencia y la demanda actual, igual que el Bellman-oráculo; no es una política de competencia oculta.

Bellman elige con retorno inmediato más continuación estocástica conocida. También usa mejora `> best + TOL` y conserva el primer óptimo dentro de tolerancia. La poda exacta de dominancia declara conservar el primer orden para acciones equivalentes. Así que la diferencia puede contener tanto anticipación real como la resolución de empates que la reacción deja a un orden técnico.

Esto es distinto de P0/P1/P2: `_production_rank` ordena primero éxito, después menor déficit normalizado, mayor margen y menor esfuerzo; `_best` conserva el primer candidato si la tupla empata. P1/P2 combinan ese ranking con selección docente fija/adaptativa; no son comparadores inmediatos de CES ni referencias intertemporales equivalentes a S7.

### 6.2 Familia mínima de referencias para atribución

Sin implementarlas en esta auditoría, una comparación futura de planificación debería distinguir:

1. **Miope catálogo-primero existente:** referencia ejecutable y reproducible, con el orden del catálogo congelado.
2. **Envolvente BEST-MYOPIC / tie-set:** en cada estado, permitir exclusivamente acciones dentro de la tolerancia del máximo inmediato y calcular mediante DP restringida la mejor continuación entre ellas. Es una cota diagnóstica deliberadamente fuerte, no una política reactiva desplegable porque usa continuación/demanda futura para desempatar.
3. **Control de aprendizaje congelado o transición MIS desactivada:** conserva acciones y reward corriente, pero bloquea desarrollo; permite probar si la brecha requiere aprendizaje endógeno. Para identificar aprendizaje productivo “gratis” entre empates, informar además qué maximizadores inmediatos producen qué estado MIS, no solo un desempate elegido a posteriori.

La comparación Bellman vs BEST-MYOPIC identifica si hace falta alguna acción estrictamente subóptima inmediata. La brecha catálogo-primero vs BEST-MYOPIC cuantifica sensibilidad al empate. La comparación con MIS congelado prueba dependencia de transición, pero ninguna diferencia aislada debe llamarse causal si también cambian factibilidad o consumo; esos elementos deben mantenerse. Un desempate uniforme aleatorio puede complementar, pero no sustituye las cotas de mejor/peor empate.

## 7. Riesgos metodológicos

- Llamar “rendimiento colectivo” a CES sin declarar CES como objetivo, o llamar “servicio” a output/competencia.
- Comparar Bellman y reacción con estados/recursos o catálogos distintos; o atribuir a foresight un gap enteramente producido por un empate de la reacción.
- Usar pesos CES como si fueran prioridades funcionales: son pesos de dimensión en una función de producción, no necesariamente pesos de servicio/tarea.
- Reportar solo éxitos: oculta severidad de déficit; reportar solo déficit: oculta prioridades, umbrales y output excedente.
- Tratar recurso duro como penalización de reward además de restringir factibilidad, lo que doble-cuenta el coste sin justificación.
- Sumar el desarrollo de competencias como beneficio explícito a la producción futura que ya depende de esas competencias.
- Seleccionar objetivo, umbral, pesos o criterios de éxito después de ver qué política gana.
- Extrapolar las referencias exactas con competencia/demanda conocidas a políticas realistas con estado parcialmente observado.

## 8. Decisiones pendientes del PI

1. ¿Qué significa “servicio completado” en una unidad de evaluación: un periodo, una tarea, un cliente o todos los requisitos activos? En el código actual es el problema/período completo; no representa una cardinalidad de tareas individuales.
2. ¿El CES de S4/S7 representa el objetivo organizativo primario o una función de producción de referencia que debe acompañarse de una restricción/meta funcional?
3. ¿Son las dimensiones/k requisitos sustitutos con los pesos CES existentes, o hay tareas críticas/no sustituibles? Si hay prioridad, ¿de qué fuente provienen los pesos/umbrales?
4. ¿Qué recursos son meras capacidades duras y cuáles tienen coste de oportunidad o monetario que deba entrar al objetivo? Actualmente la enseñanza comparte esfuerzo y no hay precio monetario.
5. Para estudios de planificación, ¿debe la referencia central ser Bellman vs BEST-MYOPIC y reportarse aparte el baseline catálogo-primero?
6. ¿Qué diagnóstico de servicio debe ser restricción, objetivo secundario lexicográfico o solo indicador para cada pregunta S4/S7?

## 9. Recomendación final del CE

No cambiar CES ni el código a partir de esta auditoría. Mantener CES como reward reproducible de las referencias S4/S7 y reportar en paralelo éxito, déficit por dimensión y recursos. No describir un aumento de CES como mejor servicio salvo que el criterio de servicio se incluya en la definición del problema y el resultado lo respalde.

Para el marco general, adoptar como principio documental una familia de objetivos declarados por escenario con separación entre objetivo, restricciones, costes y diagnósticos. Antes de una nueva inferencia sobre el valor de Bellman, resolver el comparador tie-aware: publicar el resultado existente de catálogo-primero como referencia histórica y distinguirlo de la envolvente BEST-MYOPIC. La decisión conceptual prioritaria para el PI es especificar si S7 estudia maximización de producción CES bajo recursos o cumplimiento de servicios bajo demanda incierta, y cómo se ordenan esos dos fines. La auditoría no elige por el PI ni recomienda ponderaciones ad hoc.
