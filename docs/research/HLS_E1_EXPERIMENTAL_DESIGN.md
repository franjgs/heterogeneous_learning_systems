# HLS-E1 — Orden temporal, arquitectura y MIS-v2

**Estado:** propuesta exploratoria mínima; ejecución en HOLD.
**Pregunta:** ¿cambiar el orden de una misma colección de problemas cambia la ventaja relativa de las arquitecturas A/B/C, y difiere ese efecto con MIS-v2 ON frente a OFF?

## 1. Alcance y relación con antecedentes

El objeto de intervención es exclusivamente el **orden temporal**: cada par usa exactamente los mismos 40 problemas, con idénticos identificadores, requisitos, pesos CES y presupuesto, pero en órdenes distintos. Se prioriza P0 con MIS ON/OFF para no mezclar el primer contraste con reglas de enseñanza o memoria P2. No se introduce ninguna política o mecanismo.

Antecedentes internos relevantes:

- **G1** estudia asignación estática y muestra que heterogeneidad no garantiza por sí sola valor; no estudia aprendizaje ni orden temporal de una colección común.
- **G2, MIS y G3/G3-H** conectan asignación/exposición con desarrollo competencial y valor futuro. G3/G3-H usan la ley cuadrática histórica; aquí se usa exclusivamente MIS-v2 exponencial, con ecuación y exposición declaradas abajo.
- **Campañas 1–2** ya estudiaron interacción contextual de enseñanza y MIS, y el valor condicional de una intervención docente. HLS-E1 excluye enseñanza y no vuelve a probar esa pregunta.
- **Q1 preflight** es el antecedente más próximo: comparó arquitecturas bajo demanda IID y Markov con marginales iguales. Encontró que, con MIS OFF, competencias fijas y P0 sin memoria, el contraste medio arquitectura×persistencia es estructuralmente nulo. El bloque MIS ON mostró trayectorias distintas, pero la comparación no mantenía una misma colección finita permutada entre órdenes.
- **RQ0-D** propone estudiar si la estructura temporal de demanda modifica fases de integración bajo demanda estacionaria/no estacionaria. Es un solapamiento conceptual importante, pero no especifica este contraste mínimo de permutación exacta ni el estimando de orden×arquitectura×MIS con P0.

Por tanto, E1 no debe presentarse como un nuevo tema amplio sobre demanda dinámica. Su diferenciación concreta es controlar la **composición realizada de problemas** fijando el multiconjunto y variando solo el orden. Se recomienda registrarlo como subestudio de Q1/RQ0-D salvo que CE/PI justifiquen una campaña independiente. La novedad externa no está establecida.

## 2. Configuraciones del colectivo

N=3, K=2, filas=agentes A0–A2, columnas=competencias S0–S1:

```text
A — especialización marcada     B — uniforme
[[.90,.10],                     [[.50,.50],
 [.50,.50],                      [.50,.50],
 [.10,.90]]                      [.50,.50]]

C — mixta
[[.70,.30],
 [.50,.50],
 [.30,.70]]
```

Las tres tienen la misma suma por fila (1), por columna (1.5) y total (3), así como mismos agentes, límites individuales, catálogo de esfuerzo y presupuesto. Esto iguala dotación competencial agregada, **no** la frontera de producción multidimensional. El máximo marginal inicial de producción en S0 o S1 es 1.5 para las tres; no se afirmará equivalencia de capacidad en problemas mixtos.

Recursos comunes: límite individual 1.0, presupuesto colectivo 3.0 por periodo, presupuesto por problema 3.0 y catálogo de esfuerzo existente `[(0,0),(0,1),(.5,.5),(1,0)]` por agente. Igual presupuesto disponible no implica igual consumo realizado.

Para evitar que una orientación o el desempate por índice determine el resultado, usar permutaciones de agentes y, cuando corresponda, espejo S0↔S1 balanceados de antemano. Aplicar exactamente la misma transformación a organización y colección en ambos órdenes y a las tres arquitecturas. No se interpretará el balance como invariancia de la política.

## 3. Intervención: dos órdenes del mismo multiconjunto

Horizonte H=40. Multiconjunto fijo, idéntico en todos los bloques emparejados:

| Problemas | Cantidad | Requisitos (S0,S1) | Pesos CES |
|---|---:|---:|---:|
| A-easy | 5 | (.70,0) | (1,0) |
| A-near | 5 | (1.45,0) | (1,0) |
| A-learnable | 5 | (1.55,0) | (1,0) |
| B-easy | 5 | (0,.70) | (0,1) |
| B-near | 5 | (0,1.45) | (0,1) |
| B-learnable | 5 | (0,1.55) | (0,1) |
| M-balanced | 10 | (.85,.85) | (.5,.5) |

Cada problema conserva un ID único; las copias de un tipo tienen los mismos requisitos, peso y presupuesto. Las variantes A/B están espejadas. 1.55 supera el máximo marginal inicial común 1.5 y puede hacerse alcanzable al desarrollar competencias mediante MIS-v2; .70 y 1.45 representan niveles bajo y próximo a esa frontera. Estos umbrales se fijan antes de ver resultados. Las tareas mixtas representan requisitos en dos dimensiones, no sinergia productiva.

Se comparan dos órdenes construidos a partir de **la misma lista concreta** en cada bloque:

1. **Agrupado A→B:** colocar los 15 problemas A en los primeros 15 espacios no-M, después los 15 B; los 10 M ocupan posiciones 4,8,…,40.
2. **Intercalado A/B:** mantener los problemas M en esas mismas diez posiciones y alternar A1,B1,…,A15,B15 en los espacios restantes.

Para cada bloque, sortear previamente el orden interno de la lista A, de la lista B y de los diez problemas M; reutilizar esas listas sin cambios en ambos órdenes. Así cada pareja tiene los mismos IDs, y solo cambia la posición temporal. La secuencia es exógena y se entrega como lista congelada al runner existente; no se necesita un generador nuevo.

Ambos órdenes tienen exactamente 15 problemas A, 15 B y 10 M y el mismo número de cada variante. Cambian la longitud y repetición de episodios de demanda A/B, no la composición ni la dificultad acumulada. Esto evita confundir orden con diferencias de frecuencias realizadas.

## 4. Políticas y mecanismos

Solo **P0**: selección productiva lexicográfica existente por éxito funcional, menor déficit normalizado, mayor margen y menor esfuerzo, con desempate por primer candidato. No maximiza CES.

MIS-v2 se evalúa OFF y ON. ON usa `eta[i,k]=0.10` en todas las celdas y la ley actual

\[
c'_{ik}=1-(1-c_{ik})(1-\eta_{ik})^{e_{ik}},
\]

donde la exposición `e` es el esfuerzo productivo asignado a esa celda. La producción y evaluación del periodo usan la competencia previa al aprendizaje; la transición modifica periodos posteriores. MIS OFF congela competencias. Enseñanza OFF en todos los brazos. Información perfecta común: la estimación disponible para P0 coincide con la competencia actual. No se incluye incertidumbre observacional como factor.

## 5. Contrastes, controles y métricas

Sea `R(a,o,m,r)` el CES bruto acumulado de arquitectura `a∈{A,B,C}`, orden `o∈{G,I}` (agrupado/intercalado), MIS `m∈{0,1}` y bloque emparejado `r`.

Contrastes primarios por bloque:

\[
\Delta_{AB}(o,m,r)=R(A,o,m,r)-R(B,o,m,r),
\]
\[
\Theta_{AB}(m,r)=\Delta_{AB}(G,m,r)-\Delta_{AB}(I,m,r),
\]
\[
\Psi_{AB}(r)=\Theta_{AB}(1,r)-\Theta_{AB}(0,r).
\]

`Theta` pregunta si el orden modifica la ventaja A frente a B; `Psi` si ese contraste difiere al habilitar MIS-v2. Repetir descriptivamente para A−C y C−B, secundarios exploratorios. También reportar cambio de orden dentro de cada arquitectura. Esta diferencia-en-diferencias es un contraste de intervenciones en el simulador, no mediación causal de las competencias.

**Control exacto:** con MIS OFF, P0, estado congelado, catálogo y colección idénticos, la decisión por problema no depende del tiempo. Para cada arquitectura, el acumulado de CES, éxitos, producción y esfuerzo debe ser idéntico entre ambos órdenes, salvo tolerancia numérica; por tanto `Theta(0)=0` exactamente. Un fallo indica divergencia de IDs/contenido, orden de catálogo, estado, trazas o implementación. Con MIS ON no se exige igualdad: el orden puede cambiar exposición y estado posterior.

**Medidas separadas:** CES acumulado y por periodo; problemas resueltos; output por competencia; esfuerzo productivo total y por agente/competencia; recursos no usados; matriz de competencias antes/después e incrementos MIS por celda; éxito por periodo y tipo de problema. Esfuerzo por problema resuelto se reporta solo si hay resoluciones. Las curvas por periodo se interpretan junto al problema presente en ese tiempo; no se comparan tiempos sin estratificar por tipo. Las métricas de agente son contabilidad descriptiva, no contribuciones causales individuales. CES bruto no es utilidad neta.

No hay enseñanza ni coste docente. Las competencias solo cambian por MIS-v2, de manera que el control MIS OFF aísla el efecto de orden con estado fijo y el contraste ON/OFF mide el efecto conjunto de permitir aprendizaje en esta configuración P0.

## 6. Tamaño y análisis exploratorio

Propuesta mínima: **10 bloques de orden emparejados**. En cada bloque se fija multiconjunto/IDs y listas internas; se generan las dos permutaciones descritas. Cada bloque se ejecuta en 3 arquitecturas × 2 órdenes × 2 estados MIS = 12 episodios. Total: **120 episodios, 40 periodos cada uno (4,800 episodios-periodo)**. Diez bloques no sustentan generalización poblacional; el alcance es la variación entre órdenes de este multiconjunto y estas reglas de aleatorización.

Analizar los diez valores pareados de `Theta_AB(0)`, `Theta_AB(1)` y `Psi_AB`, además de A−C/C−B descriptivos. Mostrar todos los valores, media, mediana, dispersión y un intervalo bootstrap 95% por bloques como resumen exploratorio; no pruebas de significación ni afirmación de descubrimiento. No tratar periodos ni las 12 ejecuciones de un bloque como réplicas independientes. Congelar IDs, generación de permutaciones, transformaciones y semillas antes de correr; mismo bloque de permutación se comparte entre los 12 brazos.

## 7. Viabilidad y preflight técnico

En N=3,K=2 hay 64 asignaciones productivas. El catálogo conjunto bruto con cero o una enseñanza sería `64×(1+3×2×2)=832`; enseñanza estará deshabilitada, por lo que P0 recorre solo acciones productivas (máximo 64 candidatas por decisión). La estimación es 120×40×64 = **307,200 evaluaciones P0** como cota simple, además de producción, MIS-v2 y serialización; el coste debería ser pequeño respecto a campañas anteriores, pero no se declara un tiempo sin medirlo.

Antes de ejecución, preflight solo funcional: una pareja de órdenes, las tres arquitecturas, MIS ON/OFF (12 episodios) y replay exacto (otros 12); validar multiconjunto por IDs, control `Theta(0)=0`, reproducibilidad, acciones factibles y trazas. Registrar tiempo/memoria sin seleccionar parámetros ni inspeccionar rankings para rediseñar el protocolo. No se ha ejecutado.

## 8. Criterio de autorización

**GO para diseño; HOLD para ejecutar** hasta que CE/PI:

1. Confirmen que el estimando de orden exacto ofrece suficiente diferenciación frente a Q1 y que E1 se integra en RQ0-D o se justifica como subestudio separado.
2. Aprueben las matrices, el multiconjunto, las dos reglas de orden y diez bloques antes de observar resultados.
3. Verifiquen manifiesto con MIS-v2, `eta=.10`, exposición, límites, presupuesto y versión exacta del simulador.
4. Confirmen el control exacto MIS OFF y el preflight de replay, sin truncamiento ni divergencia.
5. Acepten que cualquier inferencia se limita a este multiconjunto, P0, N=3,K=2, catálogo discreto y modelos actuales; P1/P2, enseñanza, información imperfecta y otras demandas quedan para estudios posteriores, no extensiones implícitas de E1.

**Conclusión:** Q1 ya estableció que el contraste promedio de arquitectura×persistencia bajo MIS OFF puede ser estructuralmente nulo; no probó la intervención exacta de reordenar una colección fija. RQ0-D cubre el tema general de demanda dinámica, pero su protocolo amplio no equivale a esta prueba de permutación. E1 puede aportar un diagnóstico mínimo y limpio de sensibilidad al orden y de su dependencia de MIS-v2; debe tratarse como subestudio de esos antecedentes, no como una campaña científicamente independiente o novedosa sin una decisión adicional.

## Referencias internas de implementación y antecedentes

- P0 y CES: `src/hls/hls_lab_nk_production.py`; catálogo y recursos: `src/hls/hls_lab_nk_geometry.py`.
- Transición MIS-v2 y ejecución secuencial: `src/hls/hls_lab_nk_learning.py`, `src/hls/hls_lab_nk_execution.py`.
- Replay de secuencia explícita y entorno exógeno: `src/hls/hls_lab_nk_environment.py`, `src/hls/hls_lab_nk_execution.py`.
- Antecedentes: `docs/theory/HLS_G1_STATIC_EXPERIMENTAL_GROUND_TRUTH.md`, `docs/theory/HLS_G2_DYNAMIC_GROUND_TRUTH.md`, `docs/experimental_foundations/HLS_G3_ORGANIZATIONAL_VALUE_GROUND_TRUTH.md`, `docs/experiments/HLS_Q1_PREFLIGHT.md`, `docs/experimental_foundations/RQ0_EXPERIMENTAL_CAMPAIGN.md` (incluido RQ0-D), `docs/experiments/HLS_CAMPAIGN1_FINDINGS.md` y `docs/experiments/HLS_CAMPAIGN2_FINDINGS.md`.
