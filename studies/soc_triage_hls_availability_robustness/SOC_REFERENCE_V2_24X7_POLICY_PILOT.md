# Piloto exploratorio de D1, P1 y HLS-B — V2_24X7

**Tipo:** comparación piloto, exploratoria y emparejada; no análisis confirmatorio.  
**Commit de configuración:** `6ab0934aaf5b9f821b55ca002e05e68e00a68334`.  
**Configuración:** [`SOC_REFERENCE_V2_24X7_LOAD_REGIMES.json`](config/SOC_REFERENCE_V2_24X7_LOAD_REGIMES.json).  
**Resultados y metadatos por ejecución:** [`SOC_REFERENCE_V2_24X7_POLICY_PILOT_RESULTS.json`](SOC_REFERENCE_V2_24X7_POLICY_PILOT_RESULTS.json).

## Diseño y reproducción

Se ejecutaron las diez semillas fijadas antes de analizar resultados: `2026112701`–`2026112710`. No se solapan con el bloque de la campaña histórica documentada (`711000000`–`711000399), ni con las semillas piloto/configuraciones previas documentadas (`998001`, bases `910000`, `920000`, `930000`). Se ejecutaron **30 episodios**: 10 semillas × D1/P1/WAPS. Cada semilla produce la misma traza de alertas, recomendaciones y entorno para las tres políticas; solo puede cambiar la asignación.

La organización es exactamente la de V2_24X7 con perfil ordinario/pulso/recuperación: roster, disponibilidad individual 24x7, elegibilidad, competencias, eficiencia, servicios, clases, severidades, dificultad, clasificador, prevalencia, alpha=0.50, beta=0, gamma=1, deadlines, horizontes y régimen de llegadas permanecen fijos. No se modificaron algoritmos, motores, parámetros adaptativos ni la configuración JSON. La huella SHA-256 de la configuración es `37549c5191cce46fd02aae8f683996af7aa4451dce38a8b3db1b6221dfad316f` y la del bloque de organización (recursos y calendarios) es `9c055bf7341e36d71788cd7cc9b8d6a7220ddd1889d7972cf11f38a0175fbc9b`.

```sh
python studies/soc_triage_hls_availability_robustness/run_policy_pilot.py \
  --config studies/soc_triage_hls_availability_robustness/config/SOC_REFERENCE_V2_24X7_LOAD_REGIMES.json \
  --output studies/soc_triage_hls_availability_robustness/SOC_REFERENCE_V2_24X7_POLICY_PILOT_RESULTS.json
```

El script verifica en cada semilla la identidad de los hashes de traza y realización ambiental, los conteos de alertas, la matriz TP/FP/TN/FN y las rutas entre políticas. El hash ambiental incluye dificultad por alerta y escala realizada (alpha/gamma); beta=0 implica que la dificultad no modifica el servicio efectivo en este perfil. Cada alerta tiene una investigación, TP/FP se dirigen a L2, TN/FN a L1, y el deadline original se conserva.

Pruebas focalizadas ejecutadas: `pytest -q studies/soc_triage_hls_availability_robustness/tests/test_policy_pilot.py studies/soc_triage_hls_availability_robustness/tests/test_execution_api.py studies/soc_triage_hls_availability_robustness/tests/test_scenario_integration.py` (**31 pasaron**). Incluyen emparejamiento por semilla, rutas/investigación única, deadlines, disponibilidad/elegibilidad y una comprobación de que la etiqueta oculta y el servicio efectivo no llegan al dispatcher. También contrastan el adaptador continuo con el motor nativo y ejercitan el flujo histórico en una semilla; no equivalen a repetir todas las campañas históricas. No se lanzó la regresión masiva ni se alteraron los ejecutores históricos.

## Acceso de las políticas e integridad del flujo

`scenario_loader.py::triage_scenario_for` genera las entradas emparejadas. `triage_execution.py::run_triage_flow` separa las alertas por recomendación y ejecuta una investigación única en el nivel indicado. `CalendarBackend.run` pasa el servicio efectivo al motor, pero no reenvía `hidden_need_by_alert`; la dificultad y escala realizada solo intervienen cuando el motor calcula servicio después de la asignación.

D1 y P1 reciben alertas con clase/deadline, disponibilidad, elegibilidad, competencia y tiempo previsto por analista-clase. WAPS/HLS-B en `availability_engine.py::simulate` estima llegadas con `observed_arrivals` hasta el instante de decisión; la señal no incluye alertas futuras, dificultad, etiquetas de referencia, confusión ni resultados posteriores. La herramienta de triaje sí determina el nivel de la cola por la recomendación aceptada, que es información pública para la asignación dentro de ese nivel. La auditoría de interfaces y las pruebas focalizadas respaldan este aislamiento; no es una prueba formal de todos los caminos posibles del código.

Se conservaron los parámetros HLS-B del JSON: ventana de 4 h, umbrales de salida/entrada `low=1.05`, `high=1.20`, capacidad de normalización 12 alertas/h para L1 y 3 alertas/h para L2. No se recalibraron para este perfil.

## Resultados globales

Las 10 trazas generaron entre 2,692 y 2,841 alertas (media 2,771.7). En conjunto hubo TP=2,394, FP=1,075, TN=23,809 y FN=439: L1 recibió 24,248 investigaciones y L2 3,469. Estos conteos son idénticos entre políticas en cada semilla. No hubo investigaciones duplicadas ni pendientes al corte común de 336 h.

`R/N` conserva la definición operativa usada por el simulador: suma de la competencia modelada del analista asignado para alertas terminadas dentro del SLA, dividida por todas las alertas admitidas. La competencia es un proxy sintético de calidad esperada, no una probabilidad empírica validada. Las cifras siguientes son media ± desviación estándar entre las diez semillas; tiempo en horas naturales.

| Política | R/N | Dentro SLA | Tarde | Pendiente | Calidad media modelada de completadas | Respuesta media (h) | Espera media hasta inicio (h) |
|---|---:|---:|---:|---:|---:|---:|---:|
| D1 | 0.7844 ± 0.0117 | 97.56% ± 1.65 pp | 2.44% ± 1.65 pp | 0% | 0.8030 ± 0.0022 | 1.218 ± 0.239 | 0.932 ± 0.238 |
| P1 | 0.7753 ± 0.0012 | 100% ± 0 pp | 0% ± 0 pp | 0% | 0.7753 ± 0.0012 | 1.186 ± 0.232 | 0.901 ± 0.231 |
| HLS-B (WAPS) | 0.7821 ± 0.0042 | 99.69% ± 0.50 pp | 0.31% ± 0.50 pp | 0% | 0.7845 ± 0.0012 | 1.195 ± 0.234 | 0.909 ± 0.233 |

Los totales sobre las 27,717 alertas fueron: D1 27,036 puntuales/681 tardías; P1 27,717/0; HLS-B 27,631/86. Las medias de respuesta se calculan sobre las completadas; todas las alertas terminaron antes del corte. La métrica principal no ordena las políticas igual que la puntualidad: D1 conserva mayor R/N medio por su mayor calidad de asignación modelada aunque presente más retrasos.

### Diferencias emparejadas globales

Cada diferencia es por semilla (`P1 − D1`, `HLS-B − D1`, `HLS-B − P1`). El intervalo es un intervalo t bilateral descriptivo del 95% con 9 grados de libertad; no representa una prueba confirmatoria. “+/−” cuenta semillas con diferencia positiva/negativa; diferencias cero se informan aparte.

| Diferencia | Métrica | Media | DE | IC descriptivo 95% | Semillas + / − / empate |
|---|---|---:|---:|---:|---:|
| P1 − D1 | R/N | −0.00910 | 0.01100 | [−0.01697, −0.00124] | 2 / 8 / 0 |
| P1 − D1 | Dentro SLA | +0.02436 | 0.01650 | [+0.01256, +0.03616] | 9 / 0 / 1 |
| P1 − D1 | Respuesta (h) | −0.03162 | 0.01482 | [−0.04223, −0.02102] | 0 / 10 / 0 |
| HLS-B − D1 | R/N | −0.00231 | 0.01047 | [−0.00980, +0.00518] | 4 / 6 / 0 |
| HLS-B − D1 | Dentro SLA | +0.02128 | 0.01410 | [+0.01119, +0.03137] | 9 / 0 / 1 |
| HLS-B − D1 | Respuesta (h) | −0.02319 | 0.01313 | [−0.03258, −0.01380] | 1 / 9 / 0 |
| HLS-B − P1 | R/N | +0.00679 | 0.00347 | [+0.00431, +0.00927] | 9 / 1 / 0 |
| HLS-B − P1 | Dentro SLA | −0.00308 | 0.00497 | [−0.00663, +0.00048] | 0 / 6 / 4 |
| HLS-B − P1 | Respuesta (h) | +0.00843 | 0.00438 | [+0.00530, +0.01156] | 10 / 0 / 0 |

El archivo de resultados contiene contrastes emparejados adicionales por régimen, nivel, clase y severidad, además de los indicadores por ejecución. El tamaño pequeño, la construcción sintética del modelo y la única configuración de demanda impiden concluir superioridad. En particular, intervalos descriptivos que no cubran cero no sustituyen un diseño confirmatorio preespecificado.

## Llegadas por cohorte y transiciones

El régimen se asigna por la hora de **llegada** de cada alerta. Sus resultados se siguen hasta el corte terminal común, aunque el servicio ocurra en otro régimen.

| Cohorte de llegada | Política | n medio | R/N | Dentro SLA | Tarde | Espera media (h) | Respuesta media (h) | Util. L1 | Util. L2 |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|
| Ordinario | D1 | 1,571.6 | 0.7964 | 99.99% | 0.01% | 0.103 | 0.390 | 84.0% | 16.0% |
|  | P1 | 1,571.6 | 0.7751 | 100% | 0% | 0.104 | 0.390 | 83.8% | 15.9% |
|  | HLS-B | 1,571.6 | 0.7800 | 100% | 0% | 0.104 | 0.390 | 83.9% | 16.0% |
| Pulso | D1 | 585.2 | 0.7513 | 90.13% | 9.87% | 3.128 | 3.413 | 99.6% | 23.1% |
|  | P1 | 585.2 | 0.7763 | 100% | 0% | 2.974 | 3.259 | 99.6% | 23.0% |
|  | HLS-B | 585.2 | 0.7771 | 99.20% | 0.80% | 3.000 | 3.285 | 99.6% | 23.0% |
| Recuperación | D1 | 614.9 | 0.7858 | 98.50% | 1.50% | 0.955 | 1.240 | 78.7% | 12.1% |
|  | P1 | 614.9 | 0.7748 | 100% | 0% | 0.961 | 1.244 | 78.4% | 12.0% |
|  | HLS-B | 614.9 | 0.7920 | 99.37% | 0.63% | 0.972 | 1.256 | 78.7% | 12.1% |

La utilización es trabajo ejecutado durante el intervalo dividido por la disponibilidad continua del roster; incluye servicios que cruzan una frontera entre cohortes. La carga L1 del pulso satura el equipo y coincide con mayor espera y más retrasos D1. La recuperación baja la utilización y drena la cola; no elimina los retrasos ya acumulados.

### Resultados agregados por nivel, clase y severidad

Media del R/N dentro de cada subgrupo entre las diez semillas; junto a ella se da la fracción puntual. En una fila de clase/severidad, el denominador incluye ambos niveles.

| Subgrupo | D1 R/N / puntual | P1 R/N / puntual | HLS-B R/N / puntual |
|---|---:|---:|---:|
| Ruta L1 | 0.7740 / 97.22% | 0.7639 / 100% | 0.7711 / 99.65% |
| Ruta L2 | 0.8569 / 100% | 0.8548 / 100% | 0.8588 / 100% |
| Clase Top5 | 0.7933 / 99.39% | 0.7823 / 100% | 0.7847 / 100% |
| Clase Next5 | 0.7437 / 93.11% | 0.7628 / 100% | 0.7693 / 99.06% |
| Clase Tail | 0.8237 / 99.73% | 0.7764 / 100% | 0.7948 / 99.88% |
| Severidad alta | 0.7902 / 98.05% | 0.7755 / 100% | 0.7811 / 99.76% |
| Severidad media | 0.7884 / 97.88% | 0.7747 / 100% | 0.7813 / 99.78% |
| Severidad baja | 0.7797 / 97.20% | 0.7756 / 100% | 0.7828 / 99.61% |

Los contrastes por subgrupo en el JSON de resultados muestran compensaciones: por ejemplo, P1 supera a D1 en R/N para Next5 pero queda por debajo en Tail; HLS-B frente a P1 aumenta R/N en Tail y reduce ligeramente puntualidad en algunos grupos. Son diferencias descriptivas y no un efecto causal generalizable.

## Congestión y trabajo pendiente

La cola se reconstruyó por hora con el inicio/final registrado de las tareas. La cantidad de trabajo residual corresponde solo a investigaciones ya iniciadas/asignadas; no se inventó una duración efectiva para alertas aún en cola. No se observó cola L2 relevante. Medias por semilla de la cola L1:

| Política | t=96 h (inicio pulso) | t=120 h (fin pulso) | pico por semilla, media (mín–máx) | t=144 h | t=168 h |
|---|---:|---:|---:|---:|---:|
| D1 | 1.9 | 111.8 | 111.8 (72–136) | 0.1 | 0.3 |
| P1 | 2.0 | 107.4 | 107.4 (69–130) | 0.1 | 0.2 |
| HLS-B | 1.9 | 107.2 | 107.7 (69–130) | 0.1 | 0.4 |

En t=120, había cinco L1 ocupados en promedio. La cola media bajó a casi cero en el muestreo de t=144; a t=168 quedaban algunas alertas nuevas en cola en parte de las réplicas. Ningún episodio tenía alertas pendientes al corte 336 h. El archivo de resultados conserva trayectorias horarias de cola, ocupación y residual asignado para las tres políticas.

## HLS-B: cambios de modo observados

En las diez ejecuciones hubo **265 transiciones registradas**: 176 en L1 y 89 en L2; 133 hacia P1 y 132 hacia D1. Se observaron 177 transiciones en el tramo ordinario, 42 durante el pulso y 46 durante recuperación. Esto cuenta cambios de modo en épocas con cola y profesional libre, no todas las épocas de decisión ni el tiempo total pasado en cada modo.

La implementación evalúa llegadas observadas en la ventana retrospectiva de 4 h cuando puede despachar. Las transiciones a P1 tuvieron presión entre 1.208 y 1.292 (media 1.228), por encima del umbral alto 1.20; las transiciones a D1, entre 0.333 y 1.042 (media 0.978), por debajo del umbral bajo 1.05. La variable de presión es la tasa observada en la ventana dividida por la capacidad de normalización fijada por nivel. Hubo cambios también en régimen ordinario: el controlador no se limita a detectar el pulso configurado y sus umbrales no constituyen una estimación validada de capacidad.

## Interpretación, mecanismos y límites

**Observado:** las tres políticas tienen trazas y rutas idénticas, pero producen asignaciones, calidad modelada y puntualidad diferentes. P1 tuvo menos espera/respuesta y cero retrasos en estas diez semillas; D1 presentó mayor calidad modelada entre alertas completadas y mayor R/N; HLS-B quedó entre ambos en R/N y puntualidad, con resultados modestamente distintos de P1. El desempeño de L2 se mantiene similar porque la misma traza y la cola pequeña ofrecen una condición mucho menos saturada que L1.

**Mecanismo comprobado en el código:** P1 ordena la selección local por menor holgura posterior al servicio; D1 usa una elección secuencial que pondera riesgo, competencia propia y cobertura de especialidad con orden aleatorio del pool; HLS-B conmuta entre D1 y P1 mediante presión de llegadas observadas y umbrales con histéresis. Es consistente que priorización temporal reduzca retrasos y que la asignación basada en competencia tenga otro resultado de R/N. La tabla por subgrupo muestra que esta compensación depende de la clase. El piloto no descompone causalmente la diferencia de cada alerta ni prueba contrafactuales.

**Incertidumbre:** diez bloques emparejados son útiles para detectar patrones y variación entre semillas, pero no bastan para confirmar superioridad. Los intervalos t se incluyen como resúmenes descriptivos; no se seleccionaron semillas ni umbrales a partir de los resultados. Una sola organización, perfil de llegada, clasificador sintético, calidad basada en competencia y una realización de dificultad beta=0 limitan la generalización. No se estudian coste como objetivo, beta>0, gamma>1 ni disponibilidad por turnos.

**Siguiente diseño recomendado:** congelar una hipótesis primaria y un conjunto reducido de métricas antes de ampliar réplicas; aumentar bloques emparejados con semillas nuevas y preespecificadas; mantener separados R/N, puntualidad y calidad; conservar análisis por cohorte y una evaluación explícita de calibración del umbral/capacidad HLS-B que no use el piloto para ajustar retrospectivamente el resultado. No se recomienda declarar un ganador a partir de este piloto.
