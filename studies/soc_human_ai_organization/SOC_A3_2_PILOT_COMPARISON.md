# A3.2 — Implementación de C y comparación piloto D1/T/Q/C

**Estado:** prototipo de C y piloto exploratorio ejecutados; pendiente de revisión científica del PI. No es campaña confirmatoria ni cierra A3.
**Fuentes:** demanda sintética con receta derivada de A1; sin datos SOCTRA individuales ni predicciones reales.
**Reproducibilidad:** `run_a3_2_pilot.py` + `config/a3_2_pilot.json`; salidas agregadas/raw locales e ignoradas por Git en `results/soc_a3_2_pilot/`.

## 1. Objetivo y antecedentes

Se implementa **C, coordinación central secuencial**, para compararla con D1, T y Q. T y Q llaman exactamente a las reglas ya implementadas P1 y P2, respectivamente; P1/P2 no se modificaron. D1 tampoco se modificó. M queda fuera: C no calcula un matching óptimo ni espera a acumular trabajo.

A1 estimó capacidad L1 de 28,42 alertas/h para roster y mezcla hipotéticos; registró cero matchings de cardinalidad ≥2 en 170.263 estados. A3.1 confirmó que el motor puede representar cardinalidad 2 en un estado construido, aunque no apareció en esas trazas. Las dos evaluaciones externas resumidas por el PI atribuyeron plausiblemente la escasez natural al despacho inmediato y recomendaron separar selección central de matching; sus documentos originales no estaban disponibles y no se les atribuyen citas. Este piloto conserva el despacho inmediato, como corresponde al modelo actual.

## 2. Definición de C

Para la época (t), sea (F_t) el conjunto de analistas disponibles y (A_t) las alertas pendientes. Sólo se consideran parejas elegibles (E_t=\{(i,a): k_a\in K_i\}\). El servicio estimado (s_{ia}), competencia (e_{ia}), deadline (d_a) y latencia de despacho (\ell_C) son los parámetros conocidos del modelo. Se calcula holgura postservicio:

\[
\sigma_{ia}=d_a-t-\ell_C-s_{ia},\qquad
o_{ia}=\mathbb{1}[\sigma_{ia}\ge 0],\qquad
q_{ia}=\begin{cases}\sigma_{ia},&o_{ia}=1\\-\sigma_{ia},&o_{ia}=0.\end{cases}
\]

C escoge la pareja factible que minimiza lexicográficamente
\[
(-o_{ia},\ q_{ia},\ -e_{ia},\ s_{ia},\ d_a,\ arrival_a,\ id_a,\ id_i).
\]
Así prioriza: (1) poder terminar a tiempo; (2) menor holgura entre las viables o menor tardanza entre las inviables; (3) mayor competencia; (4) menor servicio; y luego claves estables. No hay suma de magnitudes incompatibles ni pesos ajustables.

Tras elegir una pareja se retiran esa alerta y ese analista del conjunto de candidatos y se vuelve a escoger hasta que no queden parejas. Es un greedy secuencial con desempate determinista, **no** una optimización global de lote; el orden de selección puede perder cardinalidad máxima en grafos generales. No conoce llegadas futuras ni reserva especialistas.

La latencia se aplica una vez por época no vacía; las tareas seleccionadas comienzan en (t+\ell_C). La contabilidad de recurso es `coordination_edge_cost × número de aristas elegibles en el estado inicial de la época`. Es un proxy explícito del alcance de información consultada, no un conteo de todas las evaluaciones internas del greedy ni una medición de cómputo. En la configuración principal se usó (\ell_C=0,05) h (3 minutos) y 1 unidad abstracta por arista inicial elegible. Esos valores no son mediciones GMV. El coste en unidades no modifica las decisiones ni se convierte en penalización de recompensa; el tiempo sí retrasa el servicio. La prueba adicional `C_zero_latency` fija latencia y coste a cero como límite diagnóstico, no como política operativa.

La regla ya es distinta de T y Q en estados pequeños alcanzables: C puede elegir la alerta viable cuando T seleccionaría una ya irrecuperable; puede preferir la alerta más urgente antes que la de mayor competencia que escogería Q; y, cuando dos analistas estiman velocidades distintas, C puede escoger centralmente el analista más rápido. También hay estados simétricos donde C=T=Q. Estas pruebas muestran diferenciación lógica, no superioridad de episodio.

## 3. Configuración y metodología

Se reutilizó A1: tres clases anónimas con mezcla base 0,592/0,236/0,172, severidades y deadlines sintéticos, roster paramétrico de seis L1 y tres L2, elegibilidad solapada, servicios y competencias heterogéneos, recomendación IA sintética con aceptación hipotética fija para encaminar L2. Cada alerta y recomendación simulada se generó una sola vez por escenario/semilla y se reutilizó para todas las políticas. El SLA se evalúa terminalmente en L2 si la ruta simulada indica escalado.

| Escenario | \(\rho_{L1}\) | Capacidad fluida roster/mix (alertas/h) | Llegadas/h | Deadline × | Elegibilidad media | Variación aislada |
|---|---:|---:|---:|---:|---:|---|
| Holgado | 0,35 | 28,42 | 9,95 | 1 | 2,5 | Referencia heterogénea |
| Intermedio | 0,65 | 28,42 | 18,47 | 1 | 2,5 | Referencia heterogénea |
| Próximo a capacidad | 1,00 | 28,42 | 28,42 | 1 | 2,5 | Referencia heterogénea |
| Especialización restringida | 0,65 | 27,66 | 17,98 | 1 | 1,5 | Menos clases elegibles; misma mezcla base |
| Control homogéneo | 0,65 | 26,20 | 17,03 | 1 | 2,5 | Competencia 0,8 homogénea y servicio homogéneo |
| Mezcla balanceada | 0,65 | 26,01 | 16,91 | 1 | 2,5 | Tercios por clase, sensibilidad hipotética |
| Deadlines ajustados | 0,65 | 28,42 | 18,47 | 0,25 | 2,5 | Referencia heterogénea |

Las capacidades son límites fluidos LP de L1 para su roster, elegibilidad y mezcla particulares; no incluyen variabilidad de cola, SLA o coste. Las celdas de control homogéneo y mezcla balanceada son contrastes sintéticos, no afirmaciones sobre GMV. El plazo base es el de A1 (low/medium/high: 12/4/1 h) y todos estos valores siguen siendo hipotéticos.

Se ejecutaron 20 semillas emparejadas (`261132000`–`261132019`) en cada una de siete configuraciones, con cinco corridas por traza: D1, T, Q, C con latencia/coste y C de coste cero. Total: **700 episodios-política**, más **140 trayectorias diagnósticas D1**. H=24 h y D=24 h. El proceso tardó 9,034 s en el host de esta ejecución. Cada episodio admite alertas en `[0,H)`; a H se toma el corte y las completadas durante D se distinguen de las pendientes en H y H+D.

Para la calidad se reporta (a) calidad esperada entre completadas, (p_{ia}=e_{ia}(1-0,35\,difficulty_a)), y (b) una resolución Bernoulli contrafactual con un mismo uniforme determinista por alerta/semilla para todas las políticas; la proporción correcta y a tiempo usa como denominador todas las admitidas. Ambas son calidad simulada, no exactitud humana observada. Utilización por pool se calcula sobre H con las asignaciones de cada nivel. IC95% de diferencias: t pareada, 19 grados de libertad, exploratoria, sin ajuste por multiplicidad; no inferencia confirmatoria.

## 4. Prestaciones medias observadas

Cada celda de SLA indica **H / H+D**. La calidad esperada es la probabilidad modelada media entre las alertas finalmente completadas; `correcta+a tiempo` es la realización común aleatoria por alerta, sobre admitidas. `Espera` es la espera total L1+L2 media por alerta hasta el corte terminal. Todas las métricas son sintéticas.

| Escenario | Política | SLA H / H+D | Calidad esperada | Correcta y a tiempo / admitidas | Espera (h) |
|---|---|---:|---:|---:|---:|
| Holgado | D1 | .9854 / .9958 | .6383 | .6260 | .0016 |
|  | T | .9856 / .9953 | .6412 | .6314 | .0018 |
|  | Q | .9856 / .9953 | .6415 | .6316 | .0018 |
|  | C | .9830 / .9954 | .6396 | .6343 | .0586 |
| Intermedio | D1 | .9839 / .9954 | .6441 | .6440 | .0250 |
|  | T | .9835 / .9951 | .6409 | .6394 | .0264 |
|  | Q | .9833 / .9952 | .6452 | .6447 | .0259 |
|  | C | .9775 / .9944 | .6386 | .6405 | .1477 |
| Próximo a capacidad | D1 | .9052 / .9944 | .6744 | .6767 | 1.0253 |
|  | T | .9141 / .9945 | .6384 | .6404 | .9160 |
|  | Q | .9064 / .9949 | .6743 | .6778 | 1.0174 |
|  | C | .7526 / .9912 | .6388 | .6404 | 3.5653 |
| Especialización restringida | D1 | .9832 / .9953 | .6624 | .6613 | .0508 |
|  | T | .9833 / .9954 | .6650 | .6663 | .0472 |
|  | Q | .9831 / .9952 | .6661 | .6671 | .0475 |
|  | C | .9742 / .9940 | .6615 | .6600 | .2567 |
| Control homogéneo | D1 | .9835 / .9953 | .6606 | .6601 | .0196 |
|  | T | .9838 / .9954 | .6606 | .6603 | .0203 |
|  | Q | .9838 / .9954 | .6606 | .6603 | .0203 |
|  | C | .9761 / .9925 | .6606 | .6581 | .1150 |
| Mezcla balanceada | D1 | .9792 / .9922 | .6435 | .6408 | .0266 |
|  | T | .9800 / .9924 | .6384 | .6343 | .0277 |
|  | Q | .9795 / .9923 | .6447 | .6422 | .0266 |
|  | C | .9735 / .9918 | .6380 | .6380 | .1457 |
| Deadlines ajustados | D1 | .9240 / .9344 | .6435 | .6054 | .0255 |
|  | T | .9227 / .9332 | .6409 | .5994 | .0264 |
|  | Q | .9209 / .9318 | .6452 | .6029 | .0259 |
|  | C | .8641 / .8777 | .6394 | .5671 | .1470 |

`C_zero_latency` da SLA H/H+D de .9851/.9958, .9836/.9953, .9142/.9952, .9830/.9956, .9838/.9954, .9793/.9923 y .9311/.9421 en ese orden de escenarios. Su calidad esperada correspondiente es .6391, .6380, .6374, .6619, .6606, .6380 y .6387. Es un control ideal de latencia y coste cero.

En el corte H el escenario próximo a capacidad revela demoras que el drenaje de 24 h oculta en SLA terminal: D1 termina con .905 SLA en H pero .994 tras drenaje. El escenario de deadlines ajustados evita ese efecto techo (.934 terminal D1). En todas las celdas el backlog final se drenó a cero; esto no significa ausencia de congestión: en H el promedio pendiente fue 61,6 alertas para D1 y 164,7 para C en saturación. Las medias completas de backlog, respuestas, utilizaciones, L1/L2, completadas durante el drenaje y resultados por clase están en los CSV locales del piloto.

## 5. Diferencias pareadas y mecanismos

Las diferencias están calculadas por semilla contra D1 con trazas comunes. A continuación se muestran contrastes informativos; el archivo `paired_differences.csv` contiene el resto de las celdas y métricas.

| Contraste | Δ SLA terminal (IC95%) | Δ calidad esperada completadas (IC95%) | Δ correcta+a tiempo/admitidas (IC95%) | Mejora / empeora episodios |
|---|---:|---:|---:|---:|
| T−D1, near capacity | +.0001 [−.0006,.0007] | −.0360 [−.0378,−.0342] | −.0363 [−.0419,−.0307] | SLA 6/5; calidad 0/20 |
| Q−D1, especialización restringida | +.0001 [−.0003,.0006] | +.0037 [.0030,.0044] | +.0058 [.0018,.0099] | calidad 19/1; acierto-tiempo 14/3 |
| C−D1, near capacity | −.0032 [−.0061,−.0002] | −.0356 [−.0377,−.0334] | −.0363 [−.0423,−.0303] | SLA 0/14; calidad 0/20 |
| C−D1, tight deadlines | −.0567 [−.0624,−.0510] | −.0041 [−.0059,−.0023] | −.0384 [−.0456,−.0311] | 0/20 en las tres |
| C sin coste/latencia−D1, tight deadlines | +.0077 [.0042,.0112] | −.0048 [−.0071,−.0024] | +.0006 [−.0045,.0058] | SLA 14/2 |
| C sin coste/latencia−D1, near capacity | +.0008 [.0002,.0014] | −.0370 [−.0386,−.0355] | −.0370 [−.0420,−.0319] | SLA 11/2; calidad 0/20 |

**T:** cerca de capacidad mejora SLA en H +.0089 [.0065,.0112], pero no el SLA terminal; simultáneamente disminuyen la calidad esperada y los aciertos a tiempo. Esto es un compromiso de la regla temporal dentro del modelo, no una mejora neta general.

**Q:** suele conservar SLA; en elegibilidad restringida aumenta calidad esperada +.0037 y correcta+a tiempo +.0058, con intervalos exploratorios por encima de cero. Bajo deadlines ajustados la mejora no se observa claramente. El mecanismo sólo puede actuar donde hay diferencias de competencia entre analistas elegibles.

**C:** la latencia de 3 minutos por época perjudica de manera consistente la puntualidad durante H y el tiempo de espera. En cada escenario C−D1 tiene SLA H menor; en saturación cae .153 (IC [−.157,−.148]) y en deadlines ajustados .060 (IC [−.066,−.054]). El efecto terminal es pequeño bajo plazos holgados por el drenaje, y grande con deadlines ajustados. `C−C_zero_latency` en SLA terminal es −.0644 [−.0700,−.0587] con deadlines ajustados y −.0040 [−.0071,−.0009] cerca de capacidad. El coste abstracto por arista no altera resultados; por ello no se puede hablar de coste neto monetizado.

Al quitar la latencia, C mejora modestamente el SLA terminal con deadlines ajustados (+.0077) y cerca de capacidad (+.0008), pero reduce la calidad esperada en near capacity aproximadamente .037. Es un límite ideal, no evidencia de que coordinación sea beneficiosa con coste operacional. En las restantes celdas de SLA holgado hay efecto techo y no se observan mejoras terminales grandes.

### Oportunidades y diferencias de decisión

Se generaron 140 trazas D1 diagnósticas (una por escenario/semilla) y se compararon D1/T/Q/C sobre el mismo estado justo antes del despacho D1. Hubo **66.140 estados** de despacho en total; el máximo matching factible fue ≥2 en **0 estados**. Esto es frecuencia observada en este piloto, no imposibilidad matemática ni estimación para GMV. La fracción con al menos dos analistas libres varió del 13,7% en near capacity al 94,2% en carga baja; la cola y la escasez de elegibilidad condicionan la coexistencia.

La frecuencia de desacuerdo C–T fue 0% en el control homogéneo y aproximadamente 25,6% en el escenario intermedio heterogéneo, 28,8% cerca de capacidad y 32,3% con deadlines ajustados. C y T/Q coincidieron en el control homogéneo; ahí las diferencias D1–T/Q/C proceden principalmente del orden aleatorio de D1 frente al orden estable de las reglas deterministas. En el resto, los desacuerdos muestran decisiones posibles, no mejoras. En la trayectoria D1, el desacuerdo D1–C fue 29–36% según configuración; el porcentaje no representa decisiones tomadas por C en su propia trayectoria ni efectos causales de episodio.

No se observó ninguna oportunidad de asignar dos o más alertas simultáneamente en las trazas. Por tanto el resultado de C en este piloto es de **asignación central individual con información de pareja**, no de matching colectivo. C/M no es una comparación válida aquí: M fue excluida y C no la reemplaza.

## 6. Coste, métricas por clase/pool y limitaciones

| Régimen | Épocas de despacho C L1+L2 por episodio, aprox. | Latencia acumulada C (h/episodio) | Unidades abstractas de recurso C/episodio | Espera C−D1 |
|---|---:|---:|---:|---:|
| Holgado | 247 | 12,34 | 653 | +.057 h |
| Intermedio | 457 | 22,84 | 1.255 | +.123 h |
| Near capacity | 712 | 35,59 | 44.275 | +2,54 h |
| Elegibilidad restringida | 456 | 22,22 | 1.440 | +.206 h |
| Homogéneo | 421 | 21,08 | 995 | +.095 h |
| Mezcla balanceada | 422 | 21,10 | 1.100 | +.119 h |
| Deadlines ajustados | 457 | 22,84 | 1.260 | +.122 h |

Los valores son promedios sintéticos. El `resource_units` cuenta aristas elegibles existentes al inicio de cada época, con unidad de escala arbitraria; es un proxy de consulta global y no representa el número real de operaciones, personal, CPU, dinero ni coste de coordinación medido. La latencia se registra por época; cuando se asigna un analista, su disponibilidad se retrasa. En este generador suele haber un trabajo por despacho, de modo que la suma por episodio se aproxima a 0,05 h por despacho. Near capacity muestra por qué el modelo de coste debe validarse antes de interpretar C.

`class_metrics.csv` registra por proyecto anonimizado la población admitida, completadas, SLA terminal y calidad esperada; `pool_class_metrics.csv` registra entradas, completadas, esperas y cumplimiento de etapa para L1/L2 por clase. Son métricas simuladas. La métrica de etapa L1 no se debe confundir con SLA terminal cuando la alerta escala. Se incluyen utilizaciones de cada pool sobre H en `episode_metrics.csv`.

Limitaciones principales:

- Competencias, servicio, roster, deadlines, escalado, error IA y latencia son hipotéticos. La mezcla de clases base sólo reutiliza los estratos agregados documentados en A1; el control balanceado es sintético.
- D=24 h resuelve el backlog final en estas semillas, pero la cifra terminal no representa el corte operacional H; se publican ambos.
- Las diferencias se estiman con 20 semillas y múltiples escenarios/métricas; IC t exploratorios sin corrección por multiplicidad.
- La calidad probabilística depende de una función sintética; la aleatoriedad común reduce ruido comparativo, pero no convierte la salida en verdad humana.
- C es un prototipo greedy, no óptimo. La regla de urgencia lexicográfica produce compromisos; la latencia de 0,05 h puede dominar su efecto de asignación.
- El coste de recursos no se valora en recompensa ni tiene unidades empíricas.
- Se reutilizó el mismo modelo de enrutamiento hipotético por recomendación IA aceptada para todas las políticas; no se integraron predicciones SOCTRA.
- Los diagnósticos son snapshots sobre la trayectoria D1, no sobre una trayectoria común contrafactual ni evidencia causal por sí solos.

## 7. Archivos reproducibles y alcance

- Código: `src/hls/rq1_allocation.py` (`_dispatch_central_sequential`, soporte T/Q/C en `simulate` y `AllocationSession`). D1 y P1/P2 no se reescribieron.
- Pruebas: `tests/test_soc_organization_policies.py` y tests RQ1 existentes.
- Runner: `run_a3_2_pilot.py`.
- Configuración/semillas: `config/a3_2_pilot.json`.
- Artefactos locales excluidos de Git: `results/soc_a3_2_pilot/episode_metrics.csv`, `scenario_policy_summary.csv`, `paired_differences.csv`, `class_metrics.csv`, `pool_class_metrics.csv`, `d1_trajectory_decision_diagnostics.csv`, `run_metadata.json`.

## 8. Recomendación para A3.3

1. Mantener D1/T/Q/C como repertorio piloto reducido, sujeto a revisión del PI. Q ofrece la señal más clara de mejora de calidad bajo elegibilidad restringida; T cambia el SLA durante H cerca de capacidad con un coste modelado de calidad.
2. No presentar C como prueba de matching ni como mejora neta: la versión con 0,05 h perjudica; el caso sin coste sólo es un control límite. Antes de una comparación principal, el PI debe aprobar la interpretación y escala operativa de latencia/coste, y decidir si C es contraste secundario o principal.
3. Mantener M fuera del piloto. A1 y estas trazas no ofrecen matching múltiple natural. Si permanece en la tesis/artículo, deberá tratarse como contraste limitado y no atribuirle los resultados de C.
4. En A3.3 cerrar los estimandos/métricas primarias (H y terminal), la cota de latencia y el rol de la celda near-capacity, donde terminal H+D tiene efecto techo; no cambiar reglas a partir de estos resultados exploratorios.

El piloto confirma que D1/T/Q/C pueden generar decisiones distintas y que existe un contraste empírico medible, pero **no demuestra una mejora general del rendimiento colectivo**. La parte experimental del artículo aún requiere decisión del PI sobre C y preespecificación de A3.3/A4 antes de una campaña principal.
