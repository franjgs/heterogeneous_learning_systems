# Oportunidad temporal de conmutación D1/P1

**Estado:** diagnóstico exploratorio. Se comparan calendarios retrospectivos, sin selección ni validación de un supervisor nuevo. Se mantienen intactas D1, P1, HLS-B y el motor en esta fase.

## Diseño

Se reutilizan las seis configuraciones de alternancia: ρ=1,00/1,25, tramos de 2/4/12 h, ambos órdenes, H=24 h y D=24 h. Cada celda tiene 12 h por régimen, demanda esperada común de 767.3 llegadas y colas iniciales vacías. Se usan 20 semillas nuevas 261210000–261210019, emparejadas entre alternativas de cada celda. El resultado es R/N terminal a 48 h; las cohortes se definen por llegada. HLS-B conserva ventana 4 h y umbrales 1,05/1,20.

La referencia programada mantiene D1 durante tramos nominales moderados y P1 durante sobrecarga, con todas las fronteras desplazadas por δ. La primera frontera queda en 0 y las demás deben cumplir 0<t<24, estrictamente crecientes; los trabajos ya iniciados no se interrumpen. δ<0 usa información futura. También δ>0 usa un calendario nominal conocido y no es automáticamente desplegable. δ=0 equivale a la referencia nominal previa, evaluada aquí con otras semillas. La mejor δ se selecciona a posteriori **solo entre calendarios válidos de esta familia**; no es una cota superior.

| Duración | Desplazamientos válidos (h) | Excluidos por frontera en 0 o ≥24 h |
|---:|---|---|
| 2 | -1, +0, +1 | -2, +2, +4 |
| 4 | -2, -1, +0, +1, +2 | +4 |
| 12 | -2, -1, +0, +1, +2, +4 | ninguno |

## Fase 1: diferencias completas del piloto previo (n=4)

Cada entrada es media pareada ± desviación estándar **entre episodios**, en unidades R/N. La dispersión no es un intervalo concluyente.

| Celda | HLS-B−D1 | HLS-B−P1 | Nominal−D1 | Nominal−P1 | HLS-B−Nominal |
|---|---:|---:|---:|---:|---:|
| 2h_moderate_first | -0.0085 ± 0.0021 | +0.0295 ± 0.0031 | -0.0150 ± 0.0030 | +0.0230 ± 0.0021 | +0.0065 ± 0.0034 |
| 2h_overload_first | -0.0070 ± 0.0043 | +0.0319 ± 0.0027 | -0.0140 ± 0.0033 | +0.0249 ± 0.0029 | +0.0071 ± 0.0010 |
| 4h_moderate_first | +0.0107 ± 0.0367 | +0.0312 ± 0.0047 | +0.0009 ± 0.0373 | +0.0214 ± 0.0020 | +0.0098 ± 0.0035 |
| 4h_overload_first | +0.0201 ± 0.0340 | +0.0273 ± 0.0070 | +0.0187 ± 0.0422 | +0.0259 ± 0.0015 | +0.0014 ± 0.0082 |
| 12h_moderate_first | -0.0030 ± 0.0172 | +0.0208 ± 0.0041 | -0.0132 ± 0.0207 | +0.0105 ± 0.0041 | +0.0103 ± 0.0056 |
| 12h_overload_first | +0.0230 ± 0.0353 | +0.0210 ± 0.0166 | +0.0079 ± 0.0255 | +0.0059 ± 0.0269 | +0.0151 ± 0.0107 |

Las diferencias de pocas milésimas son pequeñas en la escala de R/N; las de 0,02–0,04 pueden ser materialmente interesantes dentro del modelo, pero el piloto de cuatro semillas no permite fijar un umbral operativo ni inferir una ventaja reproducible.

## Fase 2: curvas temporales con 20 semillas nuevas

Medias R/N por δ. En la columna «mejor fija» se elige D1 o P1 por la media de esta celda; Δ es diferencia pareada media frente a esa fija. DE es la dispersión entre las 20 diferencias pareadas. La selección de δ y de fija es exploratoria, sin ajuste por multiplicidad.

| Celda | δ (h) | R/N programada | Δ vs mejor fija | DE Δ | Episodios Δ>0 |
|---|---:|---:|---:|---:|---:|
| 2h_moderate_first | -1 | 0.6538 | +0.0006 | 0.0257 | 7/20 |
| 2h_moderate_first | +0 | 0.6552 | +0.0019 | 0.0261 | 7/20 |
| 2h_moderate_first | +1 | 0.6565 | +0.0032 | 0.0261 | 7/20 |
| 2h_overload_first | -1 | 0.6613 | +0.0111 | 0.0302 | 9/20 |
| 2h_overload_first | +0 | 0.6609 | +0.0107 | 0.0314 | 9/20 |
| 2h_overload_first | +1 | 0.6602 | +0.0100 | 0.0312 | 9/20 |
| 4h_moderate_first | -2 | 0.6516 | -0.0010 | 0.0243 | 8/20 |
| 4h_moderate_first | -1 | 0.6529 | +0.0002 | 0.0242 | 8/20 |
| 4h_moderate_first | +0 | 0.6542 | +0.0015 | 0.0243 | 8/20 |
| 4h_moderate_first | +1 | 0.6561 | +0.0035 | 0.0237 | 8/20 |
| 4h_moderate_first | +2 | 0.6578 | +0.0052 | 0.0244 | 9/20 |
| 4h_overload_first | -2 | 0.6619 | +0.0164 | 0.0251 | 12/20 |
| 4h_overload_first | -1 | 0.6622 | +0.0166 | 0.0267 | 13/20 |
| 4h_overload_first | +0 | 0.6610 | +0.0155 | 0.0281 | 12/20 |
| 4h_overload_first | +1 | 0.6608 | +0.0153 | 0.0295 | 12/20 |
| 4h_overload_first | +2 | 0.6597 | +0.0141 | 0.0291 | 12/20 |
| 12h_moderate_first | -2 | 0.6463 | -0.0078 | 0.0237 | 7/20 |
| 12h_moderate_first | -1 | 0.6475 | -0.0067 | 0.0245 | 7/20 |
| 12h_moderate_first | +0 | 0.6493 | -0.0049 | 0.0241 | 7/20 |
| 12h_moderate_first | +1 | 0.6505 | -0.0037 | 0.0240 | 7/20 |
| 12h_moderate_first | +2 | 0.6526 | -0.0016 | 0.0241 | 7/20 |
| 12h_moderate_first | +4 | 0.6561 | +0.0019 | 0.0245 | 8/20 |
| 12h_overload_first | -2 | 0.6185 | -0.0162 | 0.0276 | 5/20 |
| 12h_overload_first | -1 | 0.6208 | -0.0140 | 0.0288 | 8/20 |
| 12h_overload_first | +0 | 0.6238 | -0.0109 | 0.0280 | 9/20 |
| 12h_overload_first | +1 | 0.6277 | -0.0071 | 0.0264 | 9/20 |
| 12h_overload_first | +2 | 0.6310 | -0.0038 | 0.0238 | 11/20 |
| 12h_overload_first | +4 | 0.6352 | +0.0004 | 0.0217 | 11/20 |

### Comparadores emparejados de la muestra nueva

| Celda | D1 | P1 | HLS-B | Nominal δ=0 | HLS-B−D1 ± DE | HLS-B−P1 ± DE | Nominal−HLS-B ± DE |
|---|---:|---:|---:|---:|---:|---:|---:|
| 2h_moderate_first | 0.6532 | 0.6352 | 0.6635 | 0.6552 | +0.0103 ± 0.0235 | +0.0283 ± 0.0062 | -0.0083 ± 0.0052 |
| 2h_overload_first | 0.6502 | 0.6347 | 0.6619 | 0.6609 | +0.0117 ± 0.0257 | +0.0272 ± 0.0095 | -0.0010 ± 0.0103 |
| 4h_moderate_first | 0.6527 | 0.6346 | 0.6629 | 0.6542 | +0.0102 ± 0.0236 | +0.0283 ± 0.0044 | -0.0088 ± 0.0030 |
| 4h_overload_first | 0.6455 | 0.6354 | 0.6642 | 0.6610 | +0.0186 ± 0.0279 | +0.0287 ± 0.0043 | -0.0031 ± 0.0040 |
| 12h_moderate_first | 0.6542 | 0.6347 | 0.6593 | 0.6493 | +0.0051 ± 0.0222 | +0.0246 ± 0.0050 | -0.0101 ± 0.0036 |
| 12h_overload_first | 0.6047 | 0.6347 | 0.6398 | 0.6238 | +0.0352 ± 0.0317 | +0.0051 ± 0.0219 | -0.0160 ± 0.0129 |

### Cohortes de llegada

R/N ponderado por alertas admitidas de cada régimen de llegada, agregado sobre las 20 semillas. Las tablas completas por tramo, semilla y política quedan en `cohorts.csv`.

| Celda | Régimen | D1 | P1 | HLS-B | δ=0 | Mejor δ retrospectiva |
|---|---|---:|---:|---:|---:|---:|
| 2h_moderate_first | ρ=1,00 | 0.6479 | 0.6358 | 0.6617 | 0.6678 | 0.6613 |
| 2h_moderate_first | ρ=1,25 | 0.6564 | 0.6348 | 0.6648 | 0.6450 | 0.6526 |
| 2h_overload_first | ρ=1,00 | 0.6550 | 0.6355 | 0.6626 | 0.6740 | 0.6593 |
| 2h_overload_first | ρ=1,25 | 0.6451 | 0.6342 | 0.6612 | 0.6507 | 0.6629 |
| 4h_moderate_first | ρ=1,00 | 0.6574 | 0.6348 | 0.6619 | 0.6682 | 0.6631 |
| 4h_moderate_first | ρ=1,25 | 0.6479 | 0.6345 | 0.6636 | 0.6429 | 0.6536 |
| 4h_overload_first | ρ=1,00 | 0.6501 | 0.6368 | 0.6614 | 0.6768 | 0.6688 |
| 4h_overload_first | ρ=1,25 | 0.6409 | 0.6344 | 0.6663 | 0.6484 | 0.6567 |
| 12h_moderate_first | ρ=1,00 | 0.6654 | 0.6342 | 0.6653 | 0.6664 | 0.6682 |
| 12h_moderate_first | ρ=1,25 | 0.6442 | 0.6351 | 0.6546 | 0.6355 | 0.6465 |
| 12h_overload_first | ρ=1,00 | 0.5754 | 0.6352 | 0.6297 | 0.6172 | 0.6342 |
| 12h_overload_first | ρ=1,25 | 0.6258 | 0.6343 | 0.6470 | 0.6278 | 0.6349 |

## Colas, plazos y sensibilidad

La cola L1 al cambio nominal contiene alertas anteriores aún sin iniciar; el trabajo es la suma de servicios L1 nominales de esa cola. «Holgura ≤ servicio» incluye las ya vencidas; es un indicador aproximado de presión de plazos, no una predicción individual con servicio específico de analista ni L2. Se registra también la cola L2 y los recuentos/trabajo por clase en `transitions.csv`. El plazo de cada alerta se conserva al desplazar conmutaciones; las cohortes pueden terminar en otro régimen.

| Celda | Cola L1 al cambio, HLS-B | Trabajo L1, HLS-B (h) | Vencidas en cola | Holgura ≤ servicio nominal | Cola L2 | Mejor δ retrospectiva | Ganancia vs mejor fija | Ganancia vs HLS-B |
|---|---:|---:|---:|---:|---:|---:|---:|
| 2h_moderate_first | 63.3 | 13.7 | 0.0 | 0.0 | 0.0 | +1 h | +0.0032 | -0.0070 |
| 2h_overload_first | 69.9 | 15.0 | 0.0 | 0.0 | 0.0 | -1 h | +0.0111 | -0.0006 |
| 4h_moderate_first | 61.2 | 13.3 | 0.0 | 0.0 | 0.1 | +2 h | +0.0052 | -0.0051 |
| 4h_overload_first | 74.0 | 15.9 | 0.0 | 0.0 | 0.0 | -1 h | +0.0166 | -0.0020 |
| 12h_moderate_first | 32.1 | 6.8 | 0.0 | 0.0 | 0.1 | +4 h | +0.0019 | -0.0032 |
| 12h_overload_first | 108.7 | 24.6 | 0.0 | 0.0 | 0.0 | +4 h | +0.0004 | -0.0047 |

En estas fronteras HLS-B conserva cola sustancial, pero el diagnóstico nominal contabiliza 0 alertas ya vencidas o con holgura menor que un servicio L1 nominal. Por ello, los snapshots no apoyan explicar el patrón mediante plazos ya perdidos en el instante de cambio. Siguen siendo posibles efectos posteriores de espera, servicio heterogéneo y terminación L2.

El calendario con mejor media se selecciona con estas mismas 20 semillas y su ganancia está sesgada al alza. La tabla permite comparar cola acumulada, longitud del tramo y sensibilidad de R/N al desplazamiento; la asociación no identifica causalmente el papel separado de la cola o los deadlines. Cambiar δ modifica decisiones, servicios, cola posterior y la cohorte afectada.

## Interpretación y límites

- **2h_moderate_first:** máximo retrospectivo +1 h (Δ +0.0032 frente a D1); δ=0 da 0.6552; mejor retraso +1 h da 0.6565.
- **2h_overload_first:** máximo retrospectivo -1 h (Δ +0.0111 frente a D1); δ=0 da 0.6609; mejor retraso +1 h da 0.6602.
- **4h_moderate_first:** máximo retrospectivo +2 h (Δ +0.0052 frente a D1); δ=0 da 0.6542; mejor retraso +2 h da 0.6578.
- **4h_overload_first:** máximo retrospectivo -1 h (Δ +0.0166 frente a D1); δ=0 da 0.6610; mejor retraso +1 h da 0.6608.
- **12h_moderate_first:** máximo retrospectivo +4 h (Δ +0.0019 frente a D1); δ=0 da 0.6493; mejor retraso +4 h da 0.6561.
- **12h_overload_first:** máximo retrospectivo +4 h (Δ +0.0004 frente a P1); δ=0 da 0.6238; mejor retraso +4 h da 0.6352.

La mejor δ es posterior en cuatro celdas y anterior en dos; nunca coincide exactamente con el cambio nominal. Las ganancias de esos máximos frente a la mejor fija van de +0,0004 a +0,0166, con solo 7–13 de 20 diferencias positivas según la celda. No aparece una región temporal que gane de forma consistente a ambas fijas. En las seis celdas HLS-B supera en media incluso al máximo programado, por +0,0006 a +0,0070; esta comparación favorece artificialmente al calendario porque su máximo fue seleccionado con los mismos datos. Las curvas de 12 h muestran una mejora con el retraso, especialmente tras sobrecarga inicial (δ=0: 0,6238; δ=+4: 0,6352), pero la cola L1 media en la frontera es 108,7 alertas y 24,6 h de trabajo en HLS-B. Esta coincidencia es compatible con dependencia de la historia; no demuestra que la cola cause la mejora.

Esta búsqueda múltiple no valida la mejor alternativa. Las desviaciones entre episodios y la consistencia de signos informan la precisión descriptiva; no se hicieron pruebas confirmatorias ni se reajustó HLS-B. No hay coste de información futura, observación ni cambio de modo; el modelo mantiene colas ilimitadas y parámetros humanos/IA hipotéticos. Las referencias adelantadas y las posteriores usan el calendario nominal. Los resultados no miden un SOC real ni validan un nuevo supervisor.

**Conclusión — D, evidencia aún insuficiente para atribuir un mecanismo definitivo.** El calendario temporal restringido ofrece mejoras pequeñas y poco consistentes frente a las fijas (máximo seleccionado +0,0166; 13/20 episodios positivos en esa celda), y no revela margen medio sin explotar respecto a HLS-B en ninguna celda. El máximo se desplaza con duración y orden, por lo que hay indicios descriptivos de dependencia de historia, pero esta matriz no aísla cola, plazos y momento de conmutación. Una futura política tendría que usar estado observable y demostrar ventaja en semillas independientes; aquí no se selecciona ninguna.

## Reproducción

`config/soc_hls_switching_opportunity.json`, `run_soc_hls_switching_opportunity.py` y `summarize_soc_hls_switching_opportunity.py` generan los CSV completos y esta figura. Se verificaron 120 parejas escenario–semilla con la misma traza y número de admitidas en todas las alternativas válidas, además de conservación admitidas=completadas+pendientes. No hubo commit ni push.
