# Validación independiente de HLS-B

**Estado:** configuración 4 h / retorno 1,05 / activación 1,20 congelada en el [protocolo previo](SOC_HLSB_VALIDATION_PROTOCOL.md). Se usaron 100 semillas nuevas (`261190000–261190099`) por escenario; no se modificó la regla durante la ejecución. Evidencia del simulador sintético, no medición de GMV-CERT.

## Resultado primario predefinido

Se promediaron por igual los cuatro escenarios **dentro de cada semilla** y luego se analizaron las 100 diferencias pareadas HLS-B−D1. R/N terminal medio conjunto: D1 **0,6259**, HLS-B **0,6541** (diferencia **+0,02820**, ≈**4,51 %** de la media D1, desviación de diferencias 0,01486, IC95 % bilateral **[0,02526; 0,03115]**, 98/100 semillas positivas). Prueba t unilateral prefijada: \(t_{99}=18,98\), \(p=4,62\times10^{-35}\), α=0,05. Esta distribución da igual peso a cuatro escenarios sintéticos; la conclusión no se extrapola a la frecuencia real de esos regímenes en un SOC.

## Resultados por escenario

| Escenario | D1 R/N | P1 R/N | HLS-A R/N | HLS-B R/N | HLS-B−D1 [IC95 %] |
|---|---:|---:|---:|---:|---:|
| ρ=1,00 | 0,6699 | 0,6346 | 0,6433 | 0,6686 | −0,0013 [−0,0018; −0,0009] |
| ρ=1,25 | 0,5233 | 0,6233 | 0,6260 | 0,6339 | +0,1106 [0,1036; 0,1175] |
| Moderada→sobrecarga | 0,6540 | 0,6347 | 0,6411 | 0,6542 | +0,0002 [−0,0041; 0,0045] |
| Sobrecarga→recuperación | 0,6563 | 0,6345 | 0,6372 | 0,6597 | +0,0034 [−0,0011; 0,0078] |

Las comparaciones secundarias HLS-B frente a D1/P1/HLS-A en cada escenario forman una familia de 12 pruebas bilaterales con ajuste Holm. HLS-B−D1 fue negativa en ρ=1,00 (p ajustada 5,21×10⁻⁸), positiva en ρ=1,25 (1,08×10⁻⁵²) e incierta en ambos escenarios variables (p ajustadas 0,925 y 0,272). HLS-B superó P1 y HLS-A en las cuatro celdas de esta familia (p Holm <0,05), pero esto no implica ventaja sobre la mejor referencia fija. Las diferencias frente a P1 fueron +0,0340, +0,0105, +0,0195 y +0,0252; frente a HLS-A, +0,0253, +0,0079, +0,0131 y +0,0225, en orden de tabla. Los IC y p exactos están en la [tabla estadística versionada](evidence/soc_hlsb_validation_statistics.json), copia del `results/soc_hlsb_validation/statistics.json` local.

| Escenario | HLS-B−P1 [IC95 % pareado] |
|---|---:|
| ρ=1,00 | +0,0340 [0,0331; 0,0350] |
| ρ=1,25 | +0,0105 [0,0079; 0,0131] |
| Moderada→sobrecarga | +0,0195 [0,0186; 0,0203] |
| Sobrecarga→recuperación | +0,0252 [0,0233; 0,0271] |

El corte H también se guardó: HLS-B R/N fue 0,6135, 0,4791, 0,5217 y 0,5818; D1 fue 0,6142, 0,4060, 0,5272 y 0,5774. El SLA terminal de HLS-B fue 0,9943, 0,9663, 0,9944 y 0,9909; la calidad esperada **entre completadas** fue 0,6724, 0,6557, 0,6580 y 0,6657. En ρ=1,25 D1 tuvo SLA 0,7618 y calidad 0,6759: HLS-B mejora principalmente la puntualidad, con pérdida de calidad modelada. Bajo esa carga, la espera media L1 pasó de 4,236 h (D1) a 4,048 h (HLS-B), la cola L1 media en H de 114,80 a 107,60 y la utilización L1 en H fue 0,9945 y 0,9948 respectivamente. La calidad por prioridad no debe inferirse de R/N: el R/N terminal de prioridad alta en ρ=1,25 fue 0,5336 (D1) y 0,6254 (HLS-B); en moderada→sobrecarga fue 0,6501 y 0,6298. Espera, colas y utilización por pool y ambos cortes están en `episodes.csv`; prestaciones por prioridad en `strata.csv`.

## Cohortes de llegada y transiciones

Las cohortes se definen por el instante **de llegada**; su R/N terminal se evalúa hasta H+D, incluso si el servicio terminó en otro intervalo. No son tasas de finalización dentro de cada régimen.

| Escenario y cohorte | D1 | P1 | HLS-A | HLS-B |
|---|---:|---:|---:|---:|
| Moderada→sobrecarga, llegadas 0–8 h | 0,6555 | 0,6362 | 0,6534 | 0,6553 |
| Moderada→sobrecarga, llegadas 8–24 h | 0,6535 | 0,6342 | 0,6368 | 0,6538 |
| Sobrecarga→recuperación, llegadas 0–12 h | 0,6648 | 0,6348 | 0,6382 | 0,6568 |
| Sobrecarga→recuperación, llegadas 12–24 h | 0,6436 | 0,6339 | 0,6357 | 0,6640 |

En moderada→sobrecarga, las 100 realizaciones estaban en D1 justo antes de 8 h. HLS-B entró en P1 en todas; retraso medio **3,87 h**, P95 **7,49 h** desde el cambio de demanda. En sobrecarga→recuperación, 16/100 ya estaban en D1 antes de 12 h; entre las otras 84, el retorno a D1 tardó **1,88 h** de media (P95 3,21 h), sin casos que permanecieran en P1 durante todo el resto del horizonte. El porcentaje de decisiones L1 en P1 fue 5,2 %, 58,9 %, 40,9 % y 33,4 % por escenario; la fracción aproximada del tiempo de reloj H en P1 fue 5,7 %, 75,7 %, 47,1 % y 37,4 %. Los cambios medios por episodio fueron 0,92, 2,98, 2,50 y 2,14. El historial por evento está en `modes.csv`.

La cohorte de sobrecarga inicial perdió R/N frente a D1 (0,6568 vs 0,6648), mientras la de recuperación ganó (0,6640 vs 0,6436). Estas diferencias son descriptivas; el retraso de retorno es compatible con cambios en la mezcla de modos, pero no demuestra que sea su única causa. En moderada→sobrecarga, la cohorte de sobrecarga prácticamente empató con D1 pese al retraso de activación. La cola existente, la heterogeneidad y los deadlines pueden modificar los efectos de cada conmutación.

## Reproducibilidad, límites y conclusión

El [runner](run_soc_hlsb_validation.py), la [configuración congelada](config/soc_hlsb_validation.json), `episodes.csv`, `strata.csv`, `modes.csv`, `metadata.json` y el [cálculo estadístico](summarize_soc_hlsb_validation.py) conservan las 1.600 ejecuciones política–episodio y 3.200 cortes. Se verificaron 100 semillas distintas por celda, **400 parejas escenario–semilla** con igual hash y número de admitidas en las cuatro políticas, unicidad por corte, conservación `admitidas = completadas + pendientes`, R/N ≤ SLA y separación H/H+D. Una repetición aislada de HLS-B con la semilla `261190000` en sobrecarga→recuperación produjo un objeto de simulación idéntico. Pasaron **74 tests relevantes**. Los datos de desarrollo y los confirmatorios anteriores no se incorporaron al contraste.

El modelo usa demanda y capacidades sintéticas, calidad esperada, colas ilimitadas y decisiones hipotéticas de escalado. El LP de capacidad supone mezcla de clases conocida y recursos fraccionables; la tasa observada con ventana 4 h tarda en reaccionar. No se midieron costes reales del supervisor. Los escenarios tienen ponderación igual por diseño, no por prevalencia operativa.

**Conclusión:** HLS-B supera D1 en el estimando conjunto predefinido, principalmente por su ganancia bajo ρ=1,25, y conserva casi todo el rendimiento de D1 en ρ=1,00 (pierde 0,0013). Supera P1 fijo en sobrecarga y a HLS-A en las cuatro celdas. **No hay evidencia de que supere D1 en los dos escenarios variables individuales**. Por tanto, la adaptación por carga observada aporta valor en esta distribución sintética prefijada, con límites claros para atribuirle mejora durante transiciones o trasladarla a un SOC real.
