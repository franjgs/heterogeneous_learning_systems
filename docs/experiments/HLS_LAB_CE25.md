# CE-25 — Descomposición de memoria, exploración y aprendizaje organizativo

**Protocolo preejecución CE25-v1.** El diseño, dominios, órdenes y horizontes de esta sección se congelan antes de generar las trayectorias. El mismo documento incorporará después los resultados y su interpretación. CE-25 es una validación elemental de mecanismos del simulador determinista, no una comparación poblacional ni una contribución sobre bandits.

## Pregunta y alcance

Se pregunta qué contraste permite distinguir conservar observaciones, explorar acciones y usar resultados para alterar elecciones posteriores. No se asumirán efectos aditivos o causalmente separables: la exploración secuencial necesita una posición/registro de acciones visitadas; el aprendizaje necesita observaciones retenidas y una regla de decisión que las consulte.

Los controles son: `FIXED`, acción inicial predeclarada por contexto; `MEMORY_ONLY`, misma regla de acción fija pero registra resultados que no consulta; `EXPLORATION_ONLY`, recorre cíclicamente un orden de acciones congelado y registra resultados, pero su calendario no depende de ellos; `LEARNED`, usa `ExploreThenGreedy` para recorrer cada acción legal una vez y, tras observar sus recompensas, elige la media empírica mayor. La memoria de `LEARNED` almacena conteo y media de éxito por contexto/acción; la de `MEMORY_ONLY` almacena los mismos datos pero no afecta la selección. Por construcción, `MEMORY_ONLY` y `FIXED` son conductualmente equivalentes. El contraste principal es `LEARNED − EXPLORATION_ONLY`, condicionado a idénticas acciones, recompensas físicas y estados de TRAIN; identifica el efecto de consultar la recompensa en la regla posterior, dado el procedimiento de exploración, no el valor universal del “aprendizaje organizativo”.

## Dominio y comparabilidad

Se usa el equipo CE-24 `((1,0),(0,1),(0,0))`, competencias reales/estimadas idénticas, producción aditiva existente, problemas A `(0.8,0)` y B `(0,0.8)` con presupuesto 1, límite individual 1, catálogo completo de 64 acciones filtrado por factibilidad (10 por contexto), recompensa física binaria de éxito, `eta=0.35` y LI apagado en el análisis principal. Existe exactamente una acción exitosa en cada contexto: IDs congelados 48 para A y 4 para B. Todas las políticas reciben las mismas instancias, requisitos, presupuesto y acciones factibles. No se redefine física ni se añade utilidad que mezcle éxito y esfuerzo.

El conjunto de órdenes de A/B se declara aquí y se aplica idéntico a todas las organizaciones de cada celda: `CANONICAL`, `REVERSE`, `BALANCED_A_FIRST_B_LAST`, `BALANCED_A_LAST_B_FIRST`, `SUCCESS_FIRST` y `SUCCESS_LAST`. Las dos órdenes balanceadas ponen los éxitos en posiciones `(1,10)` y `(10,1)`; los dos controles adicionales los sitúan en `(1,1)` y `(10,10)`. Cada orden se construye moviendo solo la acción exitosa a su rango objetivo y conservando el orden relativo de las demás. No se muestrean ni seleccionan permutaciones por resultados.

## TRAIN/EVAL y horizontes

Para A/B, TRAIN tiene diez episodios por contexto (20 en total), suficiente para visitar una vez cada brazo legal. Se alternan contextos, y ambos miembros del contraste principal recorren exactamente el mismo orden y reciben los mismos resultados. EVAL comienza con competencias reiniciadas al equipo de referencia y estado organizativo persistido/congelado. Tiene `H_eval ∈ {1,10,20}` repeticiones por contexto; `H_total` por contexto es `10+H_eval`. Se reportan por separado las fases y su suma. `EXPLORATION_ONLY` continúa su calendario sin usar recompensas; `LEARNED` explota la mejor media observada. `FIXED`/`MEMORY_ONLY` repiten la primera acción del orden.

Los órdenes cubren óptimo primero, óptimo último, orden original, inverso y posiciones balanceadas. Esta es sensibilidad estructural determinista, no aleatoriedad ni base para intervalos de confianza. Se incluye el control de resultado/coste equivalentes con dos acciones legales del experto nulo, esfuerzo 1 y producción `(0,0)`; requisitos `(0.1,0.1)` hacen que ambas fallen igual. Se incluye D `(0.95,0.95)` como contexto imposible/unobservado.

## Predicciones analíticas preregistradas

Para `K` acciones, una acción exitosa estacionaria en rango `r` (1-indexado), recompensa binaria determinista, un barrido sin repetición y aprendizaje que consulta el resultado:

- la primera observación exitosa ocurre en la decisión `r`;
- al completar TRAIN de longitud `K`, hay exactamente un éxito;
- en `H` decisiones cíclicas de EXPLORATION_ONLY posteriores, el éxito aparece `floor(H/K) + 1[r ≤ H mod K]` veces (el indicador se omite si el residuo es cero);
- LEARNED obtiene `H` éxitos de evaluación si se ha probado todo el catálogo y la acción óptima es única.

Por tanto la diferencia de éxitos en EVAL es calculable exactamente y depende de rango/horizonte. Frente a un FIXED cuyo primer brazo ya es óptimo, exploración no recupera durante TRAIN la pérdida de `K−1` éxitos: TRAIN da 1 frente a K, y EVAL empata si se compara evaluación congelada; el total permanece `K−1` por debajo. Si FIXED empieza con un brazo fallido, el benchmark es distinto y se reporta sin presentarlo como control informacionalmente equivalente.

## Complementariedad y feedback

El contexto C CE-24 `(0.8,0.8)`, presupuesto 2, tiene 37 acciones factibles y una acción de equipo exitosa ID 52. Caso `C_UNSEEN`: entrenar A/B y presentar C sin actualización; una tabla por `problem_id` carece de entrada para C y no transfiere conocimiento. Caso `C_SEEN`: entrenar las 37 acciones de C y después evaluar con `H_eval ∈ {1,37,74}`; las permutaciones ponen el éxito en rango 1, 19 o 37. Esto comprueba memorización del contexto, no aprendizaje de una regla de complementariedad.

Control de feedback desacoplado: se mantiene intacto el éxito físico y los resultados verdaderos; en una condición diagnóstica solamente se entrega `1−success` al actualizador LEARNED durante TRAIN. Si sus decisiones posteriores siguen la etiqueta invertida, se confirma dependencia de la información de recompensa. No se usa esta condición para estimar rendimiento de una política natural.

## MIS-v2 y aleatoriedad

Tras superar los contrastes congelados de LI=OFF, se ejecutan las cuatro celdas `LI×LO` en un único orden CANONICAL: operacionalmente LO=OFF corresponde a EXPLORATION_ONLY y LO=ON a LEARNED. Las acciones TRAIN son iguales para ambas. Se informa estado final de competencias; EVAL_RESET congela competencias en el estado inicial y EVAL_CARRYOVER las conserva, pero en ambos casos MIS y θ quedan congelados durante EVAL. La atribución directa de diferencias de carryover a un factor se considera mediada por exposición/decisiones.

El simulador v1 es determinista y `seed` es metadato, no entrada a un RNG. CE-25 no genera réplicas aleatorias ni intervalos estadísticos. Sus conclusiones se limitan a las secuencias finitas enumeradas.

## Métricas y artefactos

Por episodio se preservan fase, contexto, requisitos, rango/ID de acción, producción, éxito y déficit, esfuerzo/coste, competencias antes/después, θ antes/después, memoria/cursor, etiqueta vista por el aprendiz y si la acción dependió de recompensas. Por corrida se informa `H_train`, `H_eval`, `H_total`, éxitos, déficit, esfuerzo, acciones distintas, actualizaciones y costes por separado. No hay conversión arbitraria entre esfuerzo y éxito.

Runner y tests: `experiments/synthetic/hls_lab_v1/ce25.py`, `tests/test_hls_lab_v1_ce25.py`. Salidas create-only en `results/experiments/hls_lab_ce25/` (JSONL, CSV de resumen y contrastes emparejados, manifiesto SHA-256). Para reproducir sin sobrescribir, especifique una ruta vacía: `PYTHONPATH=src:. python experiments/synthetic/hls_lab_v1/ce25.py --output-dir /tmp/hls_lab_ce25_reproduction`. El ejecutor aborta si encuentra resultados previos.

## Resultados observados

Ejecución completa: **106 diseños resumidos y 4.682 decisiones registradas**. El manifiesto marca diseño determinista y semilla `20261025` como metadato no consumido. `H_train` A/B fue 20 episodios (10 por contexto); `H_eval` fue 2, 20 o 40 episodios (1, 10 o 20 por contexto). En C observado fueron 37 episodios TRAIN y 1/37/74 EVAL. Las competencias permanecieron congeladas en el análisis primario.

### Contraste emparejado A/B

En cada orden los historiales TRAIN de LEARNED y EXPLORATION_ONLY tienen exactamente los mismos contexto, acción, producción, resultado, esfuerzo y competencia antes/después. Ambos recorren las diez acciones de cada contexto y registran 2 éxitos de 20; déficit medio `0.8375`; esfuerzo total `18`. La diferencia durante TRAIN es exactamente cero. EXPLORATION_ONLY registra resultados, mantiene un cursor de calendario y no los consulta. LEARNED guarda medias empíricas por acción y sí las usa en EVAL. La evaluación congela θ y competencias.

| EVAL por contexto `H` | LEARNED éxitos / decisiones | EXPLORATION_ONLY éxitos / decisiones | Diferencia de éxitos | Déficit medio L / E | Esfuerzo L / E |
|---:|---:|---:|---:|---:|---:|
| 1 | 2/2 | 0–2 / 2, según orden compartido | 0–2 | 0 / 0–1 | 2 / 0–2 |
| 10 | 20/20 | 2/20 | +18 | 0 / 0.8375 | 20 / 18 |
| 20 | 40/40 | 4/40 | +36 | 0 / 0.8375 | 40 / 36 |

Para `H=1`, los seis pares de rangos de éxito A/B fueron: canonical `(10,5)`, invertido `(1,6)`, balanceados `(1,10)` y `(10,1)`, success-first `(1,1)`, success-last `(10,10)`. EXPLORATION_ONLY obtuvo respectivamente `0,1,1,1,2,0` éxitos, mientras LEARNED obtuvo 2 en todos. La única igualdad es el control previsto donde ambos primeros brazos son óptimos. El resultado de un paso depende del rango; para H=10 y H=20 coincide exactamente con la fórmula y no depende de cuál perfil se elija. Las permutaciones son controles estructurales fijados antes de simular, no réplicas aleatorias.

El coste de oportunidad no se convierte en utilidad: LEARNED usa dos unidades adicionales de esfuerzo durante EVAL a H=10 y cuatro a H=20, mientras logra más éxitos. El coste explícito monetario es cero. Por tanto el ensayo identifica rendimiento funcional y consumo por separado, no un óptimo neto coste-beneficio.

### Memoria, controles y recompensa

`MEMORY_ONLY` registra resultados (20 observaciones y medias/conteos en memoria), pero no consulta ese estado al elegir. Sus acciones, producciones, éxitos y déficits coinciden exactamente con `FIXED` en todas las comparaciones; esto confirma que almacenar datos no produce por sí solo cambio conductual. No es posible estimar un “efecto independiente de memoria” porque el contraste que modifica elecciones requiere consultar el contenido almacenado.

En el control de dos acciones del experto nulo, ambas consumen esfuerzo 1, producen `(0,0)` y fallan `(0.1,0.1)`. Las cuatro políticas obtuvieron cero éxitos, déficit medio 2 y esfuerzo total 4 entre TRAIN/EVAL; no aparece ventaja por elegir entre resultados idénticos. En `SUCCESS_FIRST`, FIXED logró 20/20 TRAIN y 100% en EVAL, mientras LEARNED logró 2/20 durante exploración. Frente a ese FIXED ya óptimo, la pérdida acumulada es exactamente 18 éxitos para cualquier H; ningún horizonte posterior la recupera, aunque sus rendimientos EVAL empatan. En `SUCCESS_LAST`, FIXED repite una acción fallida; la barrida descubre el éxito al rango 10 por contexto (decisiones globales 19 y 20 por alternancia A/B), registra un éxito por contexto en TRAIN y permite su reutilización posterior. La diferencia no autoriza convertir oportunidades/ esfuerzo en una magnitud escalar.

El control de feedback invertido conserva idénticas acciones y resultados físicos de TRAIN: 2/20 éxitos, mismo déficit y esfuerzo que feedback verdadero. Solo cambia la etiqueta vista por el actualizador a `1−success`. En EVAL, feedback verdadero produjo 20/20; feedback invertido 0/20 y esfuerzo 0. Esto verifica que la elección LEARNED responde causalmente a la señal almacenada; no implica que recompensas corruptas sean una política de interés científico.

### Complementariedad C y contexto nuevo

Con C observado, `K=37`, una acción conjunta exitosa (ID 52), éxito TRAIN `1/37`, déficit medio `1.385135`, esfuerzo TRAIN 63 y una actualización por episodio. Se situó ese brazo en rangos 1, 19 y 37. EVAL obtuvo:

| Rango del éxito en el orden de C | `H_eval` | LEARNED éxitos | EXPLORATION_ONLY éxitos | Déficit medio E / L |
|---:|---:|---:|---:|---:|
| 1, 19 o 37 | 1 | 1 | 1 si rango 1; 0 en otro caso | 0 o 2 / 0 |
| 1, 19 o 37 | 37 | 37 | 1 | 1.385135 / 0 |
| 1, 19 o 37 | 74 | 74 | 2 | 1.385135 / 0 |

Los conteos concuerdan con `floor(H/37)+1[r≤H mod 37]` para EXPLORATION_ONLY y H para LEARNED una vez completada la tabla. Esto es memorización tabular del ID C, no descubrimiento de una regla de complementariedad.

En `C_UNSEEN`, tras entrenar solo A/B, el estado LEARNED no contiene filas para C. Sin embargo, el orden diagnóstico colocó preejecución la acción exitosa de C en primer lugar; LEARNED eligió esa acción por defecto y acertó 10/10 episodios C, no por transferencia. EXPLORATION_ONLY acertó una vez en sus diez ciclos C. Este control demuestra por qué el resultado observable de un contexto nuevo no identifica transferencia sin inspeccionar θ y el orden. D, no factible y sin entrada entrenada, falló en todas sus presentaciones. No se afirma generalización.

### MIS-v2: interacción, no efecto directo aislado

En las cuatro celdas LI×LO, LEARNED y EXPLORATION_ONLY recorrieron las mismas acciones en TRAIN para cada orden, por lo que con un mismo LI tuvieron idénticas exposiciones y competencias finales antes de EVAL. LI=OFF produjo déficit TRAIN `0.8375`; LI=ON lo redujo a `0.708789` con la misma tasa 2/20, bajo esta secuencia exacta. Durante EVAL-CARRYOVER, EXP_ONLY (LO=OFF) tuvo déficit medio `0.565484` con LI=ON frente a `0.8375` en EVAL_RESET; las competencias se congelaron durante la evaluación. LEARNED obtuvo 20/20 tanto reset como carryover con LI ON u OFF, pues las acciones exitosas ya usan dimensiones inicialmente máximas. Son consecuencias de MIS-v2 y exposición en esta fixture, no una estimación general ni una descomposición porcentual de efectos. En evaluación reset, se restauró el equipo inicial y se reutilizó θ; durante evaluación no se actualizó θ ni MIS.

## Interpretación y decisión

**Decisión: GO, limitada a la validación elemental de los mecanismos del simulador; no es evidencia poblacional ni autoriza generalización.** La comparación central emparejó exhaustivamente exploración y recompensas TRAIN; las diferencias de EVAL siguen exactamente la consulta frente al calendario cíclico. La memoria no consultada equivale a FIXED; la señal invertida cambia las elecciones como predice el actualizador; el caso de acciones de resultado/coste idéntico no muestra ventaja; los controles óptimo-primero/último y horizontes concuerdan con la fórmula analítica. La sensibilidad de H=1 es real y está explicada por los rangos, no se oculta ni se promedia como aleatoriedad.

Este GO cierra la pregunta mecánica acotada: el laboratorio puede observar el efecto de usar recompensas pasadas dadas acciones exploratorias emparejadas. No establece una proporción separable de “memoria”, “exploración” o “aprendizaje”; estos forman una cadena causal. El evento C no observado tuvo éxito accidental sin transferencia, por lo que se excluye de toda alegación de generalización. El método tabular tampoco aprende una regla sobre complementariedad entre IDs.

Limitaciones: determinismo completo; una geometría; problemas discretos conocidos; recompensa binaria; feedback corrupto solo como control; el orden afecta short-horizon y baselines FIXED; se impuso una fase de exploración exhaustiva; coste explícito cero; MIS-v2 no calibrado. No hay intervalos ni afirmaciones poblacionales. La fase LI×LO evalúa interacción condicionada a este diseño; diferencias carryover están mediadas por exposiciones y decisiones.

**Recomendación para CE-26:** comprobar el mismo principio mecanístico dentro de la hipótesis HLS de deliberación condicional FAST/DEEP, manteniendo comparaciones emparejadas de oportunidades y coste computacional medido. CE-25 no incorpora esos operadores ni reabre CE-24.

## Verificación, incidencias y reproducción

Pruebas CE-25: `PYTHONPATH=src:. pytest -q tests/test_hls_lab_v1_ce25.py` — **11 passed**. Regresión combinada CE-23/24/25 y componentes G0/MIS relevantes: **110 passed**. Incluye igualdad paso a paso con `run_sequence`, coincidencia de acciones/resultados en TRAIN para todos los órdenes, control de feedback, fórmulas analíticas, límites de recursos, estado no transferido de C y export determinista byte-a-byte. `git diff --check` — **passed**. Los hashes del manifiesto se comprobaron contra los tres archivos de salida; los 18 contrastes A/B verifican identidad emparejada en TRAIN.

La primera invocación del runner se detuvo antes de exportar episodios por una omisión de la especificación auxiliar `EQ` (`KeyError`); se corrigió la definición de ese control y no se conservaron resultados parciales. La ejecución completa posterior es la única fuente de resultados arriba. El análisis de contrastes se añadió después con `--analyze-existing`, que verifica el hash de los datos brutos y no vuelve a simular.

Comandos reproducibles desde la raíz:

```bash
PYTHONPATH=src:. pytest -q tests/test_hls_lab_v1_ce25.py
PYTHONPATH=src:. pytest -q tests/test_hls_lab_v1.py tests/test_hls_lab_v1_ce24.py tests/test_hls_lab_v1_ce25.py tests/test_discover_v0.py tests/test_discover_develop_v2.py tests/test_campaign0_discriminative_capacity.py tests/synthetic/test_g0_a1_reference_worlds.py tests/synthetic/test_g0_architecture.py tests/synthetic/test_c1_reference_worlds.py
PYTHONPATH=src:. python experiments/synthetic/hls_lab_v1/ce25.py --output-dir /tmp/hls_lab_ce25_reproduction
```

El último comando crea los artefactos en una ruta nueva y no sobrescribe resultados. El test de integridad reproduce dos veces en directorios temporales y compara bytes y SHA-256. El manifiesto `results/experiments/hls_lab_ce25/manifest.json` registra además los hashes del protocolo/tests, el conteo `110 passed` y la comprobación de diff.

### Integridad y trazabilidad

Ejecución: 4.682 filas de episodio; resumen 106 celdas; tabla derivada `paired_contrasts.csv` contiene 29 contrastes (18 principales A/B y controles/referencias emparejadas). La etapa de contrastes se ejecutó con `--analyze-existing` y verificó primero el hash de `episodes.jsonl`; no volvió a ejecutar el simulador.

Hashes principales (SHA-256):

- `episodes.jsonl`: `17fc63337f0177f79e89720b7c606d7d751718c0b421b732c8af1b703e428bac`
- `summary.csv`: `90044a1ad6dcf5a16ab01f206ff3008c9d021df0a789bba5be919a2ffd3cf4d9`
- `paired_contrasts.csv`: `62e084cb06843e042be218c1b151e258c2c579ea3c80157ec90a338edcb8ecf3`

El manifiesto conserva el hash de la fuente ejecutada al generar las trayectorias (`ce25.py` `9d53b33415857fa371d9933a76a37b8cc79ab8e6f8c4a7b87fb5b32431f080c6`; núcleo `hls_lab_v1.py` `c8dc4cb387cc5c47eb19c9af44c40e43772aeb755b4149bf99d3eb586e11aa6f`) y separa el hash de la fase posterior de contrastes. Commit base de ejecución: `ae78cda06025e9defbaff0a3d2b3fed6d7a705ee`. Resultados pequeños; no se sobrescribió CE-23/24.
