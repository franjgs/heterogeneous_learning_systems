# Adaptación D1/P1 en regímenes variables — piloto de desarrollo

**Estado:** exploratorio, 4 semillas por celda. Ninguna elección ni reajuste posterior de duraciones o umbrales. No es validación confirmatoria.

## Hipótesis y diseño

H1: la conmutación puede superar a ambas políticas fijas si el régimen dura lo suficiente. H2: el retraso de HLS-B y la cola heredada pueden impedirlo. H3: aun con régimen nominal conocido, la conmutación puede perder por efectos de trayectoria y calidad modelada.

Se comparan D1, P1, HLS-B congelada (ventana 4 h; histéresis 1,05/1,20) y NOMINAL-REF. Esta última aplica D1 en ρ=1,00 y P1 en ρ=1,25 al siguiente despacho tras cada frontera conocida retrospectivamente. No es implementable con información disponible ni una cota superior matemática. Los trabajos iniciados continúan, sin preempción. Los cuatro brazos parten de colas vacías y comparten alertas, IA hipotética, clases, dificultad, plazos y semilla de despacho.

H=24 h de admisión y D=24 h de drenaje, corte terminal 48 h para todas las celdas. Cada escenario tiene 12 h en ρ=1,00 y 12 h en ρ=1,25; capacidad L1 28.419/h y llegadas esperadas comunes 767.3. Hay 4 semillas nuevas 261200000–261200003, independientes de las campañas confirmatorias. R/N suma la probabilidad modelada de corrección de resoluciones terminales puntuales, dividida por todas las admitidas; una escalada finaliza en L2.

## Matriz prefijada

| Duración por régimen | Orden | Tramos de 24 h | Fronteras de cambio (h) |
|---:|---|---:|---|
| 2 h | moderada→sobrecarga | 12 | 2, 4, 6, 8, 10, 12, 14, 16, 18, 20, 22 |
| 2 h | sobrecarga→moderada | 12 | 2, 4, 6, 8, 10, 12, 14, 16, 18, 20, 22 |
| 4 h | moderada→sobrecarga | 6 | 4, 8, 12, 16, 20 |
| 4 h | sobrecarga→moderada | 6 | 4, 8, 12, 16, 20 |
| 12 h | moderada→sobrecarga | 2 | 12 |
| 12 h | sobrecarga→moderada | 2 | 12 |

## Resultados terminales

Medias de cuatro episodios por celda. Δ compara HLS-B con la **mejor política fija de esa celda**, elegida por su media; las diferencias siguen emparejadas por semilla. IC95 % exploratorio t bilateral con 3 grados de libertad; seis comparaciones sin ajuste multiplicidad.

| Duración | Orden | D1 | P1 | HLS-B | Nominal | Mejor fija | Δ HLS-B | IC95 % Δ |
|---:|---|---:|---:|---:|---:|---|---:|---|
| 2 h | moderada primero | 0.6699 | 0.6318 | 0.6613 | 0.6549 | D1 | -0.0085 | [-0.0119; -0.0052] |
| 2 h | sobrecarga primero | 0.6711 | 0.6323 | 0.6642 | 0.6571 | D1 | -0.0070 | [-0.0138; -0.0001] |
| 4 h | moderada primero | 0.6537 | 0.6332 | 0.6644 | 0.6546 | D1 | +0.0107 | [-0.0477; +0.0692] |
| 4 h | sobrecarga primero | 0.6432 | 0.6360 | 0.6633 | 0.6618 | D1 | +0.0201 | [-0.0339; +0.0742] |
| 12 h | moderada primero | 0.6585 | 0.6347 | 0.6555 | 0.6452 | D1 | -0.0030 | [-0.0303; +0.0244] |
| 12 h | sobrecarga primero | 0.6297 | 0.6317 | 0.6527 | 0.6376 | P1 | +0.0210 | [-0.0055; +0.0474] |

## Cohortes, colas y detección

R/N por cohorte de llegada (cada tramo tiene su propio denominador de admitidas), agregado sobre los cuatro episodios. La cola en una frontera cuenta alertas L1 admitidas antes de esa frontera y aún sin iniciar L1; el trabajo por clase usa horas de servicio L1 nominal. La cola L2 cuenta escaladas que terminaron L1 y aún no iniciaron L2.

| Duración | Orden | Régimen de llegada | D1 | P1 | HLS-B | Nominal |
|---:|---|---|---:|---:|---:|---:|
| 2 h | moderada primero | ρ=1,00 | 0.6671 | 0.6300 | 0.6597 | 0.6683 |
| 2 h | moderada primero | ρ=1,25 | 0.6720 | 0.6333 | 0.6626 | 0.6446 |
| 2 h | sobrecarga primero | ρ=1,00 | 0.6681 | 0.6359 | 0.6621 | 0.6724 |
| 2 h | sobrecarga primero | ρ=1,25 | 0.6736 | 0.6293 | 0.6659 | 0.6445 |
| 4 h | moderada primero | ρ=1,00 | 0.6459 | 0.6317 | 0.6618 | 0.6655 |
| 4 h | moderada primero | ρ=1,25 | 0.6584 | 0.6344 | 0.6665 | 0.6459 |
| 4 h | sobrecarga primero | ρ=1,00 | 0.6465 | 0.6389 | 0.6595 | 0.6792 |
| 4 h | sobrecarga primero | ρ=1,25 | 0.6388 | 0.6336 | 0.6661 | 0.6478 |
| 12 h | moderada primero | ρ=1,00 | 0.6633 | 0.6336 | 0.6599 | 0.6610 |
| 12 h | moderada primero | ρ=1,25 | 0.6540 | 0.6356 | 0.6519 | 0.6327 |
| 12 h | sobrecarga primero | ρ=1,00 | 0.6086 | 0.6307 | 0.6485 | 0.6391 |
| 12 h | sobrecarga primero | ρ=1,25 | 0.6448 | 0.6325 | 0.6556 | 0.6355 |

| Duración | Orden | Cola L1 en cambios, HLS-B | Trabajo L1 pendiente | Cola L2 | Retraso hasta decisión concordante HLS-B | Referencia |
|---:|---|---:|---:|---:|---:|---:|
| 2 h | moderada primero | 60.6 | 13.0 h | 0.0 | 2.59 h (41/44) | 0.02 h |
| 2 h | sobrecarga primero | 62.5 | 13.1 h | 0.0 | 2.55 h (41/44) | 0.03 h |
| 4 h | moderada primero | 59.5 | 12.7 h | 0.1 | 2.72 h (19/20) | 0.04 h |
| 4 h | sobrecarga primero | 72.6 | 15.9 h | 0.0 | 2.55 h (18/20) | 0.04 h |
| 12 h | moderada primero | 26.2 | 5.5 h | 0.5 | 2.72 h (4/4) | 0.02 h |
| 12 h | sobrecarga primero | 100.8 | 22.7 h | 0.8 | 2.36 h (4/4) | 0.06 h |

Las marcas de cambio de demanda, decisiones de HLS-B y referencia, y estados de cola por frontera y clase están en `transitions.csv` y `modes.csv`. El retraso tabulado mide la primera **decisión** del modo concordante después de la frontera, no una detección continua; cuando el modo ya concordaba al cambiar la tasa, puede ser próximo a cero. Los casos sin decisión concordante quedan fuera de esa media y aparecen en el denominador. La referencia cambia en el primer despacho posterior, que puede no coincidir exactamente con la frontera.

## Interpretación

HLS-B supera descriptivamente a la mejor fija en 3/6 celdas; ningún IC exploratorio de una **ventaja positiva** excluye cero. En las dos celdas de 2 h, el IC de la diferencia negativa sí excluye cero, sin ajuste multiplicidad. Los seis resultados figuran arriba, incluidos los negativos. Las diferencias de orden son descriptivas y están entrelazadas con la cola y la realización exógena. NOMINAL-REF supera a la mejor fija en 3/6 celdas: conocer el régimen no garantiza mejorar el episodio.
Con tramos de 2 h, la diferencia HLS-B−mejor fija cambia +0.0016 al situar primero la sobrecarga (-0.0085→-0.0070); este contraste de orden no aísla un mecanismo causal.
Con tramos de 4 h, la diferencia HLS-B−mejor fija cambia +0.0094 al situar primero la sobrecarga (+0.0107→+0.0201); este contraste de orden no aísla un mecanismo causal.
Con tramos de 12 h, la diferencia HLS-B−mejor fija cambia +0.0239 al situar primero la sobrecarga (-0.0030→+0.0210); este contraste de orden no aísla un mecanismo causal.

La asociación entre duración, retraso y rendimiento se observa conjuntamente, pero no identifica un efecto causal del retraso: también cambian número de transiciones, estado de cola, orden y composición de cohortes. Los registros permiten examinar cada frontera; este piloto no interviene de forma aislada sobre cola o latencia.

## Limitaciones y conclusión

Cuatro semillas por celda y seis comparaciones exploratorias dan poca precisión; la mejor fija se selecciona con las mismas cuatro observaciones y sus IC no corrigen esa selección ni multiplicidad. Las colas son ilimitadas; roster, servicio, calidad, IA, plazos y escalado son sintéticos. El drenaje de 24 h es común y las pendientes se conservan en `episodes.csv`. La simulación separa L1 y L2 según el motor existente. No se extrapola a GMV-CERT ni se usa para reajustar HLS-B.

**Conclusión:** el piloto ofrece indicios positivos limitados de adaptación en algunas duraciones, pero no respalda una regla monótona «cuanto más largo, mejor». La referencia nominal tampoco establece una oportunidad universal. Con estas cuatro semillas, las explicaciones 1–3 no se distinguen de manera robusta; corresponde la explicación **4**. No se ha ejecutado validación confirmatoria.

## Reproducción

`config/soc_hls_nonstationary.json`, `run_soc_hls_nonstationary.py` y `summarize_soc_hls_nonstationary.py` fijan el diseño y el análisis. Los CSV completos y `metadata.json` están en `results/soc_hls_nonstationary/` (ignorado por Git); la figura versionada está en `figures/soc_hls_nonstationary_effect.svg`. Se verificaron 24 parejas escenario–semilla con el mismo hash, admitidas y conservación de completadas+pendientes entre cuatro políticas.
