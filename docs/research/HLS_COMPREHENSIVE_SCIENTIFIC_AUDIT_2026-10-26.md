# HLS — auditoría científica integral para publicación

**Fecha:** 26 de octubre de 2026
**Alcance:** reconstrucción de evidencia HLS desde las primeras investigaciones hasta los registros disponibles en esta fecha.
**Naturaleza:** auditoría documental y de artefactos, de solo lectura. No se ejecutaron campañas ni se modificaron código o resultados.

## 1. Evaluación ejecutiva

### Dictamen: **YES, CONDITIONALLY — existe una contribución coherente, pero falta validación específica**

HLS puede sustentar un artículo serio sobre el valor organizacional de desarrollar capacidades. No puede sostener, con la evidencia actual, una conclusión empírica general sobre cómo escoger, a quién, qué y cuándo entrenar. La evidencia más fuerte está en modelos exactos pequeños y en contrafactuales condicionados, no en un estudio confirmatorio que compare políticas de entrenamiento con recursos, producción, aprendizaje natural y demanda futura medidos bajo un mismo diseño.

La proposición mejor sustentada es más estrecha y más interesante que “el déficit individual no basta”: **el valor del desarrollo depende de cómo una mejora marginal cambia el valor futuro de la organización; el rendimiento inmediato perdido y la evolución que ocurriría sin intervención deben entrar en la comparación.** G2, G3/G3-H, RQ0 y C6 establecen este mecanismo en familias exactas diferentes. Campaign 2 aporta evidencia computacional finita de que anticipar desarrollo puede tener retorno realizado positivo en promedio en estados divergentes, pero que la preferencia prospectiva no garantiza ese retorno y que el anticipo basado solo en desarrollo tiene resultado medio no distinguible de cero. Es evidencia relevante, aunque condicional a un conjunto de estados y un modelo sintético.

Lo que falta es precisamente el puente que haría de ello un artículo de “entrenamiento selectivo”: comparar intervenciones explícitas contra un contrafactual sin entrenamiento que mantenga el aprendizaje por producción; cobrar el tiempo/capacidad que la formación retira de la producción; incluir evaluación organizacional alineada con el objetivo; y mostrar bajo qué estructura de demanda, complementariedad y horizonte una política de formación vence baselines competitivos. El laboratorio N×K implementa varios de estos componentes, pero la integración no equivale a validación científica de su interacción.

**Recomendación final:** **2. Reformular el artículo alrededor de un hallazgo más fuerte.** Título propuesto: **“The Organizational Value of Capability Development: Assignment Sensitivity, Opportunity Costs, and Endogenous Learning”**. El artículo puede presentar una síntesis teórica con resultados exactos de HLS ya demostrados y Campaign 2 como evidencia computacional acotada, con una validación factorial pequeña y específicamente diseñada aún necesaria antes de sostener una recomendación de entrenamiento selectivo. No presentaría hoy la versión propuesta como una guía validada de SOC ni afirmaría superioridad general de una política.

### Convenciones de evidencia

- **FACT:** derivación, ejecución o resultado verificable en documentos y artefactos primarios.
- **INFERENCE:** interpretación que conecta resultados o propone su relevancia fuera de su modelo.
- **PROPOSAL:** trabajo futuro recomendado; no es un resultado HLS.

Los números se reproducen aquí solo cuando se encuentran en informes/artifactos de ejecuciones identificadas. Un STOP describe la decisión sobre una pregunta o línea concreta, no borra por sí solo el resultado que motivó la decisión.

## 2. Qué ha establecido HLS

Los hallazgos siguientes son los más pertinentes para la candidatura. No son intercambiables: G0/A1, MIS-v2, la productividad Nembhard y la eficacia de transferencia tienen estados y leyes distintos.

### 2.1 La heterogeneidad no crea valor organizacional por sí sola

**Pregunta.** ¿Cuándo organizar capacidades existentes mejora producción colectiva?

**Mecanismo y evidencia. FACT.** G1 compara organizaciones sobre matrices conocidas de competencia, demanda y restricciones, sin aprendizaje. Las referencias exactas muestran casos nulos bajo homogeneidad o dominancia y casos de ganancia con especialización cruzada; el valor depende de que la demanda y las restricciones permitan usar las capacidades diferenciadas. El resultado es una frontera/contraste estático finito, no una ley universal. Experimentos posteriores en SOC sintético refuerzan la dependencia contextual: con CE-04 P1 y N=24, success-on-time registrado para H0/H1/H2 fue 77.39/82.86/89.09%, al tiempo que espera media y tareas tardías admitidas también aumentaron con heterogeneidad; esos diagnósticos no identifican mediación. CE-07 comparó dos estructuras particulares bajo P1, demanda estacionaria equiprobable y N=12: B−A fue +21.52 pp (IC pareado bootstrap 95% [+21.12,+21.92], 30 pares). Son diferencias específicas de esas matrices y reglas.

**Límites y relevancia.** Asignación y distribución de capacidades pueden afectar calidad, puntualidad y congestión; no se ha probado que especialización, diversidad o redundancia sean siempre preferibles. Estos resultados motivan SOC y justifican medir costos operativos junto a acierto, pero no validan entrenamiento. H0/H1/H2 de CE-04/06/07 representan composiciones de competencia prefijadas y reglas de asignación, no analistas reales ni formación.

**Fuentes:** [G1 ground truth](../theory/HLS_G1_STATIC_EXPERIMENTAL_GROUND_TRUTH.md), [síntesis científica 2026-10-20](HLS_SCIENTIFIC_EVIDENCE_SYNTHESIS_2026-10-20.md), [CE-04 resultados](CE-04/11_CONFIRMATORY_RESULTS.md), [CE-06 diagnósticos](CE-06/01_HETEROGENEITY_DIAGNOSTICS.md), [CE-07 resultados](CE-07/04_CONFIRMATORY_RESULTS.md).

### 2.2 El aprendizaje por hacer puede cambiar la asignación futura, pero no siempre cambia su valor

**Pregunta.** ¿Puede la experiencia inducida por asignación justificar un sacrificio inmediato o invertir la decisión productiva óptima?

**Mecanismo. FACT.** G2 formaliza competencias que evolucionan por acción y una decisión terminal dependiente del estado aprendido. En instancias exactas 2×2×2 periodos, controles D0/D1 muestran respectivamente ausencia de desarrollo si no hay aprendizaje y cambio de estado sin cambio de la frontera colectiva eficiente; el caso D2 demuestra existencia de valor futuro y reversión de asignación. La distinción central es entre “la competencia cambió” y “la organización obtuvo valor de ese cambio”. G3 y G3-H desarrollan el mismo punto para tres trabajadores, dos habilidades, asignaciones factibles y aprendizaje saturante: la contribución marginal del aprendizaje se evalúa contra la sensibilidad/gap de la asignación futura. G3-H ofrece un contraejemplo exacto a una decisión basada en ranking local inmediato; incluir continuación puede cambiar la elección.

**Límites y relevancia.** Estos son resultados analíticos/exactos de modelos pequeños, no estimaciones poblacionales. La ecuación MIS cuadrática histórica no es MIS-v2: una parte de la literatura HLS utiliza leyes distintas. La conclusión transferible es estructural: el déficit marginal individual no determina por sí solo el valor de mejorar una capacidad. No se ha probado una regla empírica que seleccione al analista a formar.

**Fuentes:** [G2 ground truth](../theory/HLS_G2_DYNAMIC_GROUND_TRUTH.md), [G3/G3-H organizational value](../experimental_foundations/HLS_G3_ORGANIZATIONAL_VALUE_GROUND_TRUTH.md), [teoría de desarrollo de capacidades](../theory/HLS_CAPABILITY_DEVELOPMENT.md), [análisis matemático HLS 2026-10-22](HLS_MATHEMATICAL_ANALYSIS_2026-10-22.md).

### 2.3 El valor del desarrollo puede expresarse mediante sensibilidad de asignación; los atajos basados en valores locales fallan

**Pregunta.** ¿Qué hace organizacionalmente valiosa una mejora de competencia?

**Mecanismo y evidencia. FACT.** En G3, dado el mapa de asignación posterior, el cambio de valor se reduce exactamente a los incrementos de aprendizaje multiplicados por sensibilidades/gaps de asignación, bajo sus supuestos. Esto proporciona un cálculo de valor organizacional condicionado al mapa y al régimen estudiados, no una medida universal de “capacidad valiosa”. El análisis RQ0 prueba inclusión de clases: con la misma física, información, factibilidad y recompensa, `Pi_SEP ⊆ Pi_HLS`, así que `J_SEP,max ≤ J_HLS`; igualdad ocurre si existe una política HLS óptima que satisface la restricción strong-SEP. El trabajo exhibe familias reducibles y una familia exacta `C(alpha)` con región de separación estricta. También muestra que una inversión local de Bellman no basta para probar una brecha en valor desde el estado raíz: puede estar fuera del soporte de toda política HLS óptima.

**Límites y relevancia.** Inclusión de clases y resultados para `C(alpha)` son matemáticas conocidas/estándar una vez fijadas las clases; el interés HLS reside en condiciones y testigos específicos, no en atribuir originalidad al principio de optimización conjunta. Aún falta una caracterización corta en parámetros primitivos que cubra oportunidad, recursos, demanda futura y alcanzabilidad. Esto desaconseja reducir formación selectiva a una sola medida local de déficit o frecuencia de error.

**Fuentes:** [G3/H ground truth](../experimental_foundations/HLS_G3_ORGANIZATIONAL_VALUE_GROUND_TRUTH.md), [RQ0 routing boundaries](../theory/rq0_routing_integration_boundaries.md), [especificación teórica mínima](../theory/HLS_MINIMAL_THEORETICAL_MODEL.md), [análisis matemático, secciones 3–4](HLS_MATHEMATICAL_ANALYSIS_2026-10-22.md).

### 2.4 La interacción entre aprendizaje natural y transferencia es subaditiva a nivel de estado; el efecto organizacional no se deduce de esa identidad

**Pregunta.** ¿Se suman de forma independiente la práctica productiva y la formación/transferencia?

**Mecanismo y evidencia. FACT.** MIS-v2 y transferencia dirigida actúan secuencialmente sobre competencias acotadas. Si ambas elevan la misma celda, la segunda opera sobre el menor gap restante; la suma de cambios aislados excede la actualización conjunta bajo las ecuaciones especificadas. La identidad es exacta. El informe matemático 2026-10-22 deriva esta superposición y verifica que el catálogo de acciones N×K permite distinguir una ablación de transición de una comparación de políticas cerradas, manteniendo cargos de recursos constantes.

**Límites y relevancia.** La subaditividad del cambio de una celda no fija el signo de la interacción en recompensa, calidad, cumplimiento o valor colectivo: la organización puede reasignar trabajo, y la mejora puede alterar cuello de botella o especialización. El N×K implementa oportunidad, producción, desarrollo, observación y recursos, pero la validación integrada S4 fue una verificación de trayectoria/contrato y no un test discriminante de beneficio por transferencia. Es una pieza útil para el modelo propuesto; no es evidencia confirmatoria de eficacia de entrenamiento.

**Fuentes:** [análisis matemático, sección 4](HLS_MATHEMATICAL_ANALYSIS_2026-10-22.md), [modelo dinámico HLS](../theory/HLS_DYNAMIC_THEORY.md), [capacidad de desarrollo N×K](../../src/hls/hls_lab_nk_learning.py), [reuse audit](../experiments/HLS_ADAPTIVE_TRAINING_REUSE_AUDIT.md).

### 2.5 La anticipación de desarrollo tiene valor realizado condicional; preferencia prospectiva no garantiza beneficio

**Pregunta.** ¿Cuándo cambia una política informada por demanda/desarrollo la decisión y qué ocurre tras esa divergencia?

**Mecanismo y evidencia. FACT.** Campaign 2 (prerregistrada, 5,120 corridas reconstruidas y validadas, 40 semillas por política) examinó políticas Q00/Q10/Q01/Q11 bajo escenarios, probes y contrafactuales pareados, con MIS-v2 y demanda bajo creencias. Q10 divergió de Q00 en 3,004 de 15,360 estados elegibles; el retorno medio de dos recompensas `DeltaG` fue .1623 (IC 95% [.1476,.1771]). Q11 divergió en 3,058; promedio .1669 [.1530,.1803]. Para ambos, alrededor de 74.5% de decisiones divergentes retornaron positivo; una cuarta parte fue negativa. Q01 (anticipación de desarrollo sin información adicional) divergió en 1,172 estados; `DeltaG` promedio .00145 (IC [−.01939,.01931]) y 45.99% positivos. La ventaja interna prospectiva `DeltaQ>0` no implicó `DeltaG>0`. La prevalencia de acoplamiento estricto fue 71/15,360 (0.462%): señal de estructura no separable rara en la población de referencia, no de sinergia física.

**Límites y relevancia.** Es la evidencia HLS más informativa de preferencia prospectiva frente a consecuencia realizada, pero su unidad inferencial son estados Q11 generados por el mismo diseño finito y ocho historias. Cada contraste cambia la decisión en el estado de referencia y compara dos recompensas siguientes, no el valor global de políticas completas, ni el efecto de introducir formación frente a quitarla: todas las ramas conservan desarrollo real. Los análisis son condicionales, no un estimador de retorno de vida laboral. H4 no demuestra que formación explícita sea útil ni que Q10 supere Q11.

**Fuentes:** [Campaign 2 report](../experiments/CAMPAIGN_2_RESULTS.md), artefactos confirmatorios en [`results/campaign2_prospective_adaptation/attempt_02`](../../results/campaigns/campaign2_prospective_adaptation/attempt_02), [preregistro](../experiments/CAMPAIGN_2_PREREGISTRATION.md).

### 2.6 Un valor exacto positivo de desarrollo anticipatorio sobrevive al STOP de C6, pero no es resultado de entrenamiento realista

**Pregunta.** ¿Puede routing sacrificar recompensa inmediata para crear una oportunidad de desarrollar y obtener valor posterior?

**Mecanismo y evidencia. FACT.** C6 construyó una instancia exacta de dos agentes, dos tareas y cuatro periodos; primero routing, luego oportunidad y luego desarrollo A1 `c' = c + eta(1-c)`. Con `eta=.75`, el valor exacto HLS−BEST_STATIC fue .159375 con demanda estacionaria y .12456 con demanda cambiante; a `eta=0` y `.1` la brecha fue cero. El análisis deriva el desvío inicial: pérdida inmediata .2 y continuación ganada .275/.320, por lo que `−.2 + .275=.075` o `−.2 + .320=.120` según demanda. La brecha también aparece en régimen estacionario; no se atribuye a no estacionariedad. El resultado cuantitativo persiste como evidencia exacta del mecanismo de G2/G3/RQ0.

**Límites.** Oportunidad es determinista condicional a la ruta (0/1), costo en objetivo es cero, hay una sola capacidad desarrollable, y HLS conoce la ley y resuelve exactamente. BEST_STATIC restringe rutas pero aún optimiza desarrollo. La física A1 no es MIS-v2 ni capacitación SOC. El STOP es correcto para ampliar C6 como línea de novedad; no invalida los valores.

**Fuentes:** [análisis exacto C6](../experiments/HLS_G0_C6_EXACT_MECHANISM_ANALYSIS_2026-10-19.md), [cierre](../experiments/HLS_G0_C6_CLOSURE_2026-10-19.md), [`exploratory_results.json`](../../results/experiments/hls_g0_c6/exploratory_results.json).

### 2.7 HLS mostró que el ajuste de política y la geometría importan, y que varios resultados de adaptación son nulos o dependientes del comparador

**Pregunta.** ¿Basta cambiar demanda, información o permitir adaptación para crear valor?

**FACT.** G1 ofrece nulos y ventanas positivas; en E2.1, 33 casos con dos habilidades independientes no tuvieron brecha entre Bellman dinámico y el mapa estacionario globalmente optimizado. Las primeras celdas RQ0/A/B fueron reducibles; la posterior `C(alpha)` sí da un intervalo exacto estricto. Campaign 1 encontró diversidad de trayectorias y sensibilidad a orden/configuración, pero G07 fue líder de media en las ocho historias y `FULL−NO-DEVELOP` fue positivo en todas las medias de configuración×escenario; no se encontró liability de desarrollo. Campaign 2 tampoco estableció que Q11 supere Q10. En S7, un tie-breaker myopic alternativo redujo la brecha Bellman; CURRENT-DEMAND-MYOPIC coincidió con Bellman en CES en la instancia central, y CES podía subir mientras empeoraban servicios y déficit. Son advertencias sustantivas sobre baseline, objetivo y desempate.

**Relevancia.** El hallazgo no es “la adaptación no vale”, sino que dependencia de habilidades, costos, horizonte, información, objetivo y baseline definen qué efecto se puede identificar. Cualquier artículo de entrenamiento debe controlar estas dimensiones y reportar calidad, oportunidad, recursos, espera y trabajo tardío por separado.

**Fuentes:** [Campaign 1](../experiments/CAMPAIGN_1_RESULTS.md), [Campaign 2](../experiments/CAMPAIGN_2_RESULTS.md), [S7 y evidencia actual](../HLS_CURRENT_STATE.md), [E2.1 protocol](../experiments/HLS_E2_1_PROTOCOL.md).

## 3. Qué no ha establecido HLS

1. **No existe aún una función de valor de entrenamiento validada.** La aproximación de G3 sirve dentro de sus supuestos; no es un predictor validado para seleccionar intervención en datos nuevos.
2. **No se aisló de forma confirmatoria explícita formación vs práctica natural.** En Campaign 2 todas las ramas conservan la ley de desarrollo; en Campaign 1 el control sin desarrollo es una referencia de trayectoria, no un diseño causal de inversión en una política realista. El runner N×K contiene cargos y transiciones, pero no una campaña válida que aísle su interacción.
3. **Costo de oportunidad no está completo en una sola unidad organizacional.** C6 tiene costo de objetivo nulo; N×K maneja esfuerzo/recurso por acción; CE-04 mide colas, latencia, admisión y puntualidad. No existe una calibración común de horas de formación, productividad dejada de atender, costo presupuestario y daño por demora.
4. **Futuro de demanda y práctica observada son parciales.** Hay historias sintéticas estacionarias, programadas y Markovianas, y planificación exacta en mundos pequeños; no hay modelo inferido de llegadas SOC que conecte carga, categoría y exposición de analista a incidentes.
5. **No está resuelta la distinción entre competencia verdadera y estimada en decisiones de formación.** El N×K separa competencia y estimación, pero no hay evaluación confirmatoria de una regla selectiva bajo error de estimación, feedback que depende de asignación y cambio de política.
6. **No existe validación empírica SOC.** El repositorio no acredita registros de analistas SOC con etiquetas de competencia, asignaciones, duraciones, carga, entrenamiento y outcomes enlazados. CE-04/06/07 son simulaciones sintéticas genéricas, no datos SOC.
7. **No hay una afirmación general sobre el especialista más débil o más fuerte.** HLS proporciona casos donde la mejora de una celda/capacidad con alto impacto de asignación puede valer más que el mayor déficit local, pero no hay caracterización universal que recomiende entrenar siempre al experto más competente o nunca al menos competente.
8. **No se ha mostrado superioridad general de planners, políticas adaptativas o algoritmos.** USE/DEVELOP y strong-SEP se reducen bajo condiciones de información/coordination a clases conocidas; muchos análisis son demostraciones de reducibilidad o testigos exactos. No atribuir novedad algorítmica al nombre HLS.
9. **Transferencia y cooperación no equivalen a formación eficaz.** El módulo de enseñanza valida ejecución, orden y recursos; eficacia verdadera y estimada, concentración de exposiciones, congestión y valor colectivo requieren experimentos distintos.

### Negativos y cierres: significado preciso

- **H1/M0/CIV:** no justifican que frecuencia de fallo × gap de calidad sea una estadística suficiente ni una regla universal de inversión. Conservan valores de diagnóstico, umbrales y casos nulos; no rescatan la hipótesis inicial.
- **PACS B2.1–B2.2:** el puente contrafactual falló compatibilidad; B2.3 quedó inconcluso bajo su criterio; B2.4 sí deja evidencia acotada de interferencia/replay. No usar PACS como validación de desarrollo selectivo. La fundación B1/B2/B12 estableció mecanismos reproducidos en los alcances declarados, no una prueba HLS end-to-end.
- **G0/A1/C1–C6:** gates de exactitud y microgeometría identifican casos reducibles y testigos. C6 STOP significa que la estructura ya está explicada por A1 anticipatorio + routing flexible y no merece expansión propia; significa conservarlo como testigo cuantitativo.
- **RQ0:** demostración de que la coordinación estricta puede no aportar en unas clases y sí en una familia constructiva. No demuestra frecuencia típica de brechas ni necesidad universal de política conjunta.
- **Campaign 3 META-VOC:** contraste confirmatorio de desempeño/costo favorable en promedio igualado por dominio (+.1167 `mu_true`, IC [.0310,.2013]; −.1924 s, IC [−.3539,−.0228]) pero el punto primario se seleccionó tras ver desarrollo, presupuesto real de llamadas no quedó exactamente igualado y los dominios de equipos held-out G3/G4 no tuvieron ventaja significativa de producción. No informa sobre capacitación humana; sirve como advertencia que un predictor prometedor debe probarse en geometrías nuevas.
- **Nembhard E1:** el protocolo/revisión encontró la asignación FIXED alineada con los perfiles y casi igual al ORACLE en casos mixtos/especialistas; ADAPTIVE quedó peor bajo aquel diseño. La campaña no se completó como prueba válida de ventaja y hay discrepancia entre artefactos parciales y registro de interrupción. No convertirlo en resultado confirmatorio, ni confundir experiencia-productividad (`D,k,p,r`) con competencia MIS-v2 (`c,eta`).
- **CE-04/06/07:** aportan evidencia ejecutada sobre colas, deadline, asignación P1 y heterogeneidad en escenarios específicos. El efecto confirmatorio CE-04 de H2−H0 y P1−P0, P2−P1 negativo y P3 dependiente de escala son efectos del mundo congelado; la calibración P2 elevó success-on-time 5.27 pp (IC [4.53,6.07]) con N=12 y 8.68 pp ([8.28,9.08]) con N=48 en ese escenario. CE-06 y CE-07 amplían caracterización de composición y organización; ninguno estudia desarrollo/entrenamiento. Un primer intento de CE-07 con demanda CE-04 no estacionaria fue inválido para la pregunta; fue excluido y corregido. CE-04/07 no identifican que la congestión medie el efecto. Estos resultados son valiosos contexto SOC, no evidencia sustituta.
- **CE-03/H3 transferencia colectiva (V1/V2):** V2 no apoyó estadísticamente H3; C2−C1 y C2−C3 de precisión individual y C2−C0 en equipo tuvieron intervalos incluyendo cero. Retener como nulo acotado. V1 se conserva, no se agrega como réplica independiente de V2.
- **CE-01/02, Baccara–Lee–Yariv, Chen–Hewitt–Thomas, Nembhard:** análisis matemáticos/literarios sirven para delimitar estructuras conocidas, equivalencias y portabilidad; no deben reaparecer como reivindicación original. El STOP de AI-aging o USE/DEVELOP es una decisión de publicación actual, no inexistencia del fenómeno.

## 4. Evaluación del artículo propuesto

### Contribución central defendible

**FACT + INFERENCE:** HLS soporta una síntesis y demostración de mecanismo: la elección de formación es un problema dinámico de organización porque la mejora transforma el conjunto de asignaciones futuras; el valor neto incluye producción perdida por retirar al experto, recursos de formación y aprendizaje natural contrafactual. El ranking de brechas personales o eficacia técnica de curso no es suficiente en general. La frase “no es suficiente” está probada como posibilidad en exactos y compatible con Campaign 2; no es aún una regla cuantitativa validada sobre poblaciones reales.

### Desarrollo matemático que falta para un artículo concluyente

Formalizar un estado mínimo `s_t=(C_t, Ĉ_t, Q_t, W_t, B_t, H_t)` con competencia verdadera y creencia, demanda futura, asignaciones/carga, presupuesto/tiempo formativo y horizonte. Comparar acción `a_t` que incluye asignación/entrenamiento factible, valor productivo inmediato `r`, transición de aprendizaje natural `F^0`, transición inducida por formación `F^T`, y costos de formación y atraso separados. La decisión correcta debe ser un contrafactual incremental del tipo:

\[
\text{NV}_{ikm}(s_t)=\mathbb E[J\mid \text{entrenar }(i,k),m]-\mathbb E[J\mid \text{no entrenar, misma política/base}],
\]

con la misma realización/demanda exógena y costos completos. El teorema/fundamento de G3 puede ser un caso reducido cuando el cambio de asignación futura es conocido; Campaign 2 informa cómo distinguir valor interno de retorno observado. No se necesita re-demostrar DP estándar. La contribución potencial sería una condición o descomposición original para el valor marginal neto de una intervención bajo aprendizaje endógeno, información parcial y demanda futura; aún no está en el repositorio.

### Evidencia HLS apta para el manuscrito, con rol explícito

- **Núcleo teórico:** G2, G3/G3-H y matemáticas RQ0/C(alpha), limitadas a sus instancias/proposiciones; explicar qué se deriva y qué es importado de Bellman/asignación.
- **Ilustración mecanística exacta:** C6, identificada como testigo de routing anticipatorio y A1; incluir solo si la sencillez ayuda al mecanismo y declarar costo nulo/oportunidad degenerada.
- **Evidencia computacional condicional:** Campaign 2 H4 y H2/H3, presentados como análisis de estados de referencia, con retornos positivos para Q10/Q11 y nulo para Q01; no como prueba de políticas globales.
- **Negativos/baselines:** G2 D0/D1, E2.1 separable, RQ0 reducible, Campaign 2 Q01 y nulls, Campaign 1 near-null/order and no-development-liability. Estos límites hacen al argumento más preciso.
- **Contexto de aplicación:** CE-04/06/07 para mostrar que calidad, deadlines, workload y composición pueden producir trade-offs; no adjudicarles efectos de entrenamiento.

### Excluir del núcleo

MMLU/MixLLM contextual routing, resultados de CAC/fusión de clasificadores, MMLU dynamic capacity, CE-01 deliberación, CE-02 AI-aging y la totalidad de actividades de laboratorio que solo verifican ejecución. Son líneas no pertinentes o analogías demasiado lejanas. No incluir varias campañas solo para demostrar volumen.

### Literatura y objeciones previsibles

La literatura más próxima incluye aprendizaje por hacer en organizaciones (Nembhard y sucesores), asignación/organización de expertise y aprendizaje de equipos (incl. Chen–Hewitt–Thomas en su modelo), teoría de matching/asignación, control óptimo/DP, entrenamiento como inversión en capital humano y planificación de fuerza laboral bajo colas/demandas. Baccara–Lee–Yariv y los textos ya auditados deben tratarse según su mecanismo formal, no citarse como novedad de HLS. Revisión bibliográfica final actualizada y búsqueda de SOC workforce/skill-based routing son necesarias antes de envío; este informe no afirma exhaustividad bibliográfica externa.

Objeciones probables: (i) el resultado teórico es una reexpresión de DP estándar o valor marginal de asignación; (ii) demasiados mundos incompatibles; (iii) parámetros de desarrollo y demanda no empíricos; (iv) costo de entrenamiento omitido o medido en unidades incompatibles; (v) policy comparison confounded with information, tie-breaking o exploration; (vi) Campaign 2 condiciona a estados Q11 y mide dos pasos; (vii) ausencia de comparación con déficit, eficacia de curso, carga simple y planificador; (viii) el SOC aparece como motivación sin datos. La formulación sugerida y una única validación focal deben responder a estas objeciones.

## 5. Aplicabilidad a centros SOC

### Qué puede transferirse legítimamente

**INFERENCE.** Agentes → analistas; tareas → alertas/categorías de incidente; capacidades → competencia por categoría; demanda → llegadas por tipo y severidad; routing/asignación → selección del analista; esfuerzo/recursos → capacidad laboral; reward → calidad de investigación, resolución y cumplimiento oportuno. G1 y CE-04 demuestran que asignación y deadlines pueden afectar resultados en simulación; G2/G3 formalizan cómo práctica y desarrollo alteran capacidad; Campaign 2 aporta el problema de decisión con incertidumbre y continuación. Esos son mapeos semánticos razonables, no evidencia de validez en SOC.

### Qué falta modelar o calibrar

- Llegadas puntuales, severidad, SLA/deadline heterogéneo, prioridad, dependencia temporal e incidentes que continúan o escalan.
- Competencia observable/proxy vs latente por técnica/categoría, novatos y expertos, calidad de etiqueta y cambios en herramientas/amenazas.
- Tiempos de servicio, calidad y re-trabajo dependientes de analista, categoría, severidad y carga; asignaciones simultáneas, turnos, ausencias, interrupciones y handoffs.
- Capacitación: duración, instructor, interrupción de servicio, costo monetario, efectividad por alumno/habilidad, persistencia, transferencia entre categorías y práctica natural.
- Congestión: colas y trabajos en curso, preempción, rechazo/escalamiento, dependencia entre incidentes, costo por demora y reserva mínima por especialidad.
- Objetivos no colapsados: resolución correcta, tiempo hasta contención, severidad ponderada, falsos positivos, errores de escalamiento, carga y bienestar. “Sin aumentar recursos” requiere recurso fijo explícito; no implica costo de oportunidad cero.

No hay evidencia verificada de que SOCTRA contenga competencias individuales, rutas de alertas, tiempo de servicio por analista ni historial de entrenamiento. No atribuirle esas columnas sin auditoría de esquema y linaje.

### Mínimo escenario creíble antes de afirmar utilidad SOC

**PROPOSAL.** No construir hoy un nuevo simulador SOC. El primer mínimo es un replay/counterfactual sobre registros reales o una instancia de servicio validada por expertos: incidentes con tiempos, severidad, skills requeridas, analista asignado, outcome y recurso usado; entrenamiento se puede mantener como intervención modelada inicialmente con rangos explícitos, no como eficacia observada. Comparar asignación actual o mejor regla fija, especialización/capacidad máxima, déficit local, y un planificador de valor marginal de formación; mantener demanda, capacidad laboral y semillas/eventos pareados. Luego mostrar sensitivity envelopes para efectividad/costo de entrenamiento y futuro de demanda. Sin datos enlazados de entrenamiento, se puede reclamar únicamente **análisis de escenarios calibrados**, nunca eficacia causal de entrenamiento real en SOC.

## 6. Camino mínimo a envío

### Esencial

1. **Elegir un solo marco dinámico.** No mezclar A1, MIS-v2, Nembhard y enseñanza dirigida como si fueran parámetros del mismo proceso. Para el artículo, seleccionar MIS-v2/N×K si la tesis es producción + práctica + entrenamiento con recursos, y presentar G0/A1 solo como microfundamento ilustrativo.
2. **Definir estimando neto y recursos.** En cada estado pareado, comparar entrenar contra no entrenar bajo la misma asignación base, demanda y aprendizaje natural; contabilizar output perdido, tiempo/cupo, gasto de formación, transferencia y valor terminal por separado.
3. **Diseñar una validación única y focal.** Un factorial pequeño preespecificado sobre (a) sensibilidad de asignación/complementariedad, (b) costo de oportunidad, (c) aprendizaje natural y (d) demanda futura. Incluir al menos un baseline de déficit local y uno de eficacia×demanda; política óptima exacta solo en subinstancia finita. Usar seeds pareadas, held-out escenarios, tamaño basado en precisión y métricas de producción/servicio/costo. No reusar Q11-reference como muestra independiente.
4. **Fijar un estimando primario, plan de intervalos y auditoría de recursos antes de correr.** Separar mecanismo de transición (ablación con iguales cargos) de comparación de políticas cerradas; evitar confundir entrenamiento con información, optimización o exposición.
5. **Establecer originalidad con literatura y derivación.** La novedad debe ser una condición/descomposición nueva o evidencia causal sobre una interacción no establecida; DP estándar y la mera suma de tres factores no alcanzan.
6. **Si se conserva SOC como caso central**, obtener un conjunto mínimo de datos/descripciones operativas que calibre tipos de incidente, demanda, deadline, skills, tiempos y disponibilidad; si no, presentarlo como motivación y abstenerse de reclamos externos.

### Deseable

- Validación en segundo conjunto de equipos/escenarios, análisis de incertidumbre de competencia y cambio de mix de incidentes.
- Análisis económico de productividad perdida en entrenamiento y costos por demora, con rangos si no hay estimaciones puntuales.
- Reproducción limpia de una publicación específica solo si sus interfaces y parámetros están completos; no como requisito ceremonial.

### Innecesario

- Otra campaña amplia que vuelva a demostrar que rutas o composición afectan score.
- Reabrir C6, CE-01, CE-02 o resultados cerrados sin hipótesis nueva e identificable.
- Un “benchmark universal HLS”, una nueva arquitectura de laboratorio o integrar todas las ramas bajo un scalar común.
- Un simulador SOC nuevo antes de verificar disponibilidad y calidad de datos reales.
- Alegar novelty porque una etiqueta combinada no se encontró literalmente en un artículo.

## 7. Recomendación final

**Elegir opción 2: reformular alrededor de un hallazgo más fuerte.**

El título de trabajo recomendado es **“The Organizational Value of Capability Development: Assignment Sensitivity, Opportunity Costs, and Endogenous Learning.”** La afirmación central defendible hoy es que el valor de una capacidad no se obtiene del déficit individual aislado: depende de la sensibilidad del valor de asignación y de las oportunidades futuras, mientras que una intervención debe descontar producción/capacidad sacrificada y aprendizaje natural. G2/G3 proveen estructura exacta; RQ0 delimita cuándo flexibilidad conjunta puede o no mejorar valor; C6 conserva un testigo transparente; Campaign 2 muestra que preferencia prospectiva y consecuencia realizada divergen y que el valor anticipatorio depende de la información y del estado.

La evidencia no basta aún para presentar un algoritmo de selección de entrenamiento como superior ni para recomendar cómo debe operar un SOC. La publicación es viable si se reduce el claim a mecanismo/condición y se completa una sola validación enfocada en la interacción neta de práctica, entrenamiento y costo de oportunidad. Si no se realiza esa validación, el trabajo tendría que ser explícitamente un artículo teórico/computacional de resultados finitos, con alcance igualmente acotado, y deberá aportar una derivación original identificable más allá de la aplicación de programación dinámica estándar.

### Referencias primarias internas clave

La trazabilidad detallada está en las citas inline; las referencias esenciales para la lectura son [HLS history](../HISTORY.md), [current state](../HLS_CURRENT_STATE.md), [HLS minimal theoretical model](../theory/HLS_MINIMAL_THEORETICAL_MODEL.md), [RQ0 boundaries](../theory/rq0_routing_integration_boundaries.md), [G1](../theory/HLS_G1_STATIC_EXPERIMENTAL_GROUND_TRUTH.md), [G2](../theory/HLS_G2_DYNAMIC_GROUND_TRUTH.md), [G3/G3-H](../experimental_foundations/HLS_G3_ORGANIZATIONAL_VALUE_GROUND_TRUTH.md), [Campaign 1](../experiments/CAMPAIGN_1_RESULTS.md), [Campaign 2](../experiments/CAMPAIGN_2_RESULTS.md), [Campaign 3 META-VOC](../experiments/CAMPAIGN_3_META_VOC_CONFIRMATORY_RESULTS.md), [exact C6 analysis](../experiments/HLS_G0_C6_EXACT_MECHANISM_ANALYSIS_2026-10-19.md), [mathematical analysis](HLS_MATHEMATICAL_ANALYSIS_2026-10-22.md), [CE-04](CE-04/11_CONFIRMATORY_RESULTS.md), [CE-06](CE-06/01_HETEROGENEITY_DIAGNOSTICS.md), [CE-07](CE-07/04_CONFIRMATORY_RESULTS.md), and raw machine-readable results under `results/` linked in their reports.
