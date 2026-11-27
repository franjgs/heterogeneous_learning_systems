# Validación independiente D1 frente a P1

> **OLD MODEL / MODELO VIEJO:** this document records the historical L1-first organizational model and its evidence. Its results remain valid only for that model and do not validate the NEW MODEL. See [MODEL_GENERATIONS.md](../soc_triage_hls_availability_robustness/MODEL_GENERATIONS.md). The current LaTeX manuscript belongs entirely to the OLD MODEL; NEW MODEL transfer is deferred.

**Estado:** contraste primario ejecutado conforme al [protocolo prefijado](SOC_CONFIRMATORY_PROTOCOL.md) el 19-11-2026. Resultado confirmatorio **dentro del simulador sintético**, no validación operativa de GMV-CERT. No se cambiaron D1, P1, motor ni recompensa.

## Diseño y procedencia

El estimando primario es la media, sobre episodios, de \(\Delta=R_{P1}/N-R_{D1}/N\) a las 48 h, con 24 h de llegadas y 24 h de drenaje, en \(\rho=1,25\) (35,5232 alertas/h). \(R/N\) es la suma de probabilidades modeladas de resolución correcta de las alertas finalizadas dentro del SLA, dividida por **todas las admitidas**. La alerta escalada finaliza en L2; pendiente o tardía suma cero. Las 100 semillas nuevas `261160000–261160099` se fijaron antes de ejecutar y no se solapan con A0, A3.2 o la comparación exploratoria. Se usó el roster, servicio, mezcla, deadlines nominales y escalado hipotético de la comparación exploratoria; latencia/coste de coordinación cero. El [archivo de configuración](config/soc_confirmatory.json) y [runner](run_soc_confirmatory.py) permiten reproducir las 1.800 ejecuciones política–episodio (9 celdas × 100 semillas × 2 políticas). Los CSV, metadatos y figuras quedan en `results/soc_confirmatory_d1_p1/`, excluido de Git.

Cada pareja recibió las mismas alertas, clases, prioridades, dificultad, recomendación IA y plazos. D1 utiliza su aleatoriedad propia de orden de analistas; P1 tiene desempates deterministas. Así, el emparejamiento controla demanda exógena, sin exigir decisiones endógenas iguales. La calidad es una **esperanza modelada**, no una realización Bernoulli ni precisión humana medida. Las observaciones independientes de la prueba son episodios, no alertas.

## Contraste primario

| ρ | D1 R/N terminal | P1 R/N terminal | Δ pareada, IC bilateral 95 % | Episodios P1>D1 |
|---:|---:|---:|---:|---:|
| 1,25 | 0,5180 | 0,6162 | **+0,0982 [0,0891; 0,1073]** | 98/100 |

La desviación de las 100 diferencias fue 0,0458; t pareada unilateral \(t_{99}=21,46\), \(p=2,57\times10^{-39}\) para \(H_0:E[\Delta]\leq0\) frente a \(H_1:E[\Delta]>0\), \(\alpha=0,05\). La mejora relativa de medias es 18,95 % respecto a D1. Dos episodios favorecieron D1. No existe un umbral económico mínimo validado para calificar el tamaño de efecto como suficiente en operación real.

En el corte H, D1/P1 obtuvieron R/N 0,4087/0,4675 (Δ +0,0588 [0,0518; 0,0657]); el resultado primario corresponde exclusivamente a H+D. El SLA terminal fue 0,7556/0,9663 (Δ +0,2107); la calidad esperada **entre completadas** fue 0,6749/0,6378 (Δ −0,0371). P1 mejora puntualidad y pierde calidad modelada; R/N incorpora ambos efectos y usa denominador de admitidas. Los resultados por prioridad, clase, pool, H y H+D constan en `strata.csv` y `summary.csv`.

| Estrato, R/N terminal | D1 | P1 |
|---|---:|---:|
| Prioridad alta | 0,5374 | 0,6129 |
| Prioridad media | 0,5247 | 0,6225 |
| Prioridad baja | 0,5076 | 0,6126 |
| Clase `portfolio_top5` | 0,4339 | 0,6196 |
| Clase `portfolio_next5` | 0,6343 | 0,6162 |
| Clase `portfolio_tail` | 0,6527 | 0,6044 |

Los estratos tienen sus propios denominadores de admitidas; la mejora global no significa mejora de todas las clases. Por pool, la utilización media en H fue L1 0,993/0,994 y L2 0,379/0,362 (D1/P1); la cola media temporal en H fue L1 115,20/107,92 y L2 0,036/0,027. Quedaron pendientes al corte H 228,68/223,81 alertas en promedio; a H+D, cero en ambas políticas, con 855,55 admitidas/completadas de media. `summary.csv` conserva los cortes y los pools por separado. El SLA terminal se define por **alerta admitida**, no como cociente separado de servicios L1/L2: para las escaladas se usa L2.

## Dependencia predefinida de la carga

Los siguientes IC95 % t pareados son descriptivos. Para inferencia sobre las **ocho** comparaciones secundarias (cuatro cargas y cuatro sensibilidades) se aplicó Holm a pruebas bilaterales; todos los valores ajustados fueron <0,05. La prueba primaria mantiene su contraste unilateral separado.

| ρ | D1 R/N | P1 R/N | Δ [IC95 %] | p bilateral ajustada Holm |
|---:|---:|---:|---:|---:|
| 0,85 | 0,6563 | 0,6354 | −0,0209 [−0,0223; −0,0196] | 2,67×10⁻⁵² |
| 1,00 | 0,6693 | 0,6343 | −0,0350 [−0,0359; −0,0341] | 4,36×10⁻⁸⁹ |
| 1,10 | 0,6563 | 0,6342 | −0,0221 [−0,0278; −0,0163] | 4,54×10⁻¹¹ |
| 1,15 | 0,6228 | 0,6342 | +0,0114 [0,0021; 0,0208] | 0,0168 |
| **1,25 (primario)** | **0,5180** | **0,6162** | **+0,0982 [0,0891; 0,1073]** | contraste primario |

El signo observado cambia entre ρ=1,10 y ρ=1,15; no se estima un umbral exacto. A ρ=1,10 P1 eleva SLA terminal 0,9696→0,9948, pero reduce calidad entre completadas 0,6759→0,6377 y pierde R/N. A ρ=1,25 la pérdida de calidad persiste, mientras el aumento de puntualidad la supera. [R/N frente a carga](figures/soc_confirmatory_rn_by_load.svg) · [efecto pareado e IC](figures/soc_confirmatory_paired_effect.svg) · [SLA y calidad](figures/soc_confirmatory_sla_quality.svg).

## Robustez mínima predefinida en ρ=1,25

Se modificó un factor cada vez; demanda, roster, elegibilidad y servicio se mantuvieron. Los multiplicadores son sensibilidad de **parámetros sintéticos**, no rangos medidos en GMV-CERT.

| Perturbación | D1 R/N | P1 R/N | Δ [IC95 %] | p Holm |
|---|---:|---:|---:|---:|
| Deadlines ×0,75 | 0,3646 | 0,4533 | +0,0887 [0,0827; 0,0947] | 4,34×10⁻⁵⁰ |
| Deadlines ×1,25 | 0,6084 | 0,6361 | +0,0277 [0,0185; 0,0370] | 8,38×10⁻⁸ |
| Dispersión de competencia ×0,75 | 0,5088 | 0,6160 | +0,1072 [0,0982; 0,1162] | 1,05×10⁻⁴¹ |
| Dispersión de competencia ×1,25 | 0,5272 | 0,6164 | +0,0892 [0,0800; 0,0983] | 7,78×10⁻³⁵ |

Al estrechar plazos, la cola máxima L1 de P1 fue mayor (220,47 frente a 215,92), aunque R/N mejoró. Cambiar la dispersión de competencia conservó medias por clase y no cambió las decisiones temporales de P1 ni el SLA de estas trazas; sí cambió la calidad y la selección aleatoria de D1 ponderada por competencia. Esta perturbación no prueba robustez ante equipos con otra elegibilidad o velocidades.

## Diagnóstico del mecanismo y resultados negativos

P1 ordena localmente por holgura posterior al servicio; D1 combina riesgo temporal, competencia propia y elegibilidad de compañeros. En ρ=1,25 P1 redujo espera L1 media 4,2606→4,0657 h, P95 11,9382→10,5481 h y máximo de cola L1 224,00→218,78. La fracción SLA de prioridad alta subió 0,7734→0,9610. El número medio de alertas altas que llegaron con **todos** sus L1 elegibles ocupados casi no cambió (127,40 frente a 127,47 por episodio): la falta de capacidad inmediata sigue existiendo. La suma de horas-alerta de espera de alta prioridad mientras todos sus elegibles estaban ocupados cayó 36,28→6,61; esta suma no es tiempo de reloj único. Estos diagnósticos son compatibles con mejor orden de atención, como las oportunidades locales de A0, pero no aíslan causalmente cada componente de la política ni convierten sus pérdidas locales en ganancia global recuperable.

P1 **empeora R/N** en las tres cargas inferiores ensayadas, pese a pequeñas mejoras de espera y, en ρ=1,10, de SLA. La calidad esperada menor constituye un compromiso real del modelo. La ventaja a ρ=1,25 disminuye con deadlines más holgados. El resultado no implica superioridad universal ni ganancias observadas en un SOC real.

## Integridad, reproducibilidad y límites

La ejecución verificó 100 semillas por celda, hash exógeno idéntico en cada pareja, admitidas idénticas, unicidad de asignaciones, conservación de alertas y separación H/H+D. Las 3.600 filas de corte y 1.800 filas pareadas (900 terminales) están en `episodes.csv` y `paired.csv` locales; la [copia versionada de `test_results.json`](evidence/soc_confirmatory_test_results.json) contiene estadísticos e IC, `run_metadata.json` local las nueve configuraciones y duración. Una regeneración de la primera semilla prefijada produjo de nuevo 903 admitidas y 903 asignaciones L1 en ambas políticas, y reprodujo exactamente R/N terminal D1=0,420851925805 y P1=0,605041311813. Se ejecutaron 74 tests funcionales relevantes. Las colas son ilimitadas; no hay descartes ni preempción. Demanda, escala temporal, competencia, dificultad, servicio, escalado y SLA son supuestos del simulador. Los resultados exploratorios previos (20 semillas, otras muestras) se conservan y **no** se añadieron al contraste actual. La correspondencia de los mecanismos con el trabajo real GMV-CERT y el coste de aplicarlos siguen sin validación operativa.

**Conclusión para el artículo:** existe evidencia independiente y preespecificada de que P1 mejora el rendimiento esperado por alerta frente a D1 en la sobrecarga sintética nominal ρ=1,25, sin ampliar plantilla. También hay evidencia de deterioro bajo cargas menores y de pérdida de calidad modelada. La afirmación defendible es, por tanto, **dependiente del régimen** y circunscrita a este modelo y parámetros.
