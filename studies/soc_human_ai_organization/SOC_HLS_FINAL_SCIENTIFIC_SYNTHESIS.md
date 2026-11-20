# SOCTRA–HLS — Síntesis científica final

**Propósito.** Consolidar la evidencia publicada para las secciones Results y Discussion de un artículo. Esta síntesis no introduce políticas ni simulaciones nuevas. D1, P1, HLS-B y el motor permanecen sin cambios. El barrido paramétrico, las sensibilidades a SLA/plantilla y sus CSV son exploratorios; solo los estudios previamente protocolizados se citan como confirmatorios.

## 1. Auditoría final y correcciones

Se contrastaron los informes de auditoría, valor adaptativo, mapa operativo, comparación D1/P1 y validación HLS-B con los runners, configuraciones, `scenario_summary.csv`, `paired_seed_results.csv`, episodios, series temporales, registros de modo, cohortes y prioridades publicados.

### Discrepancia 170 h frente a 69,40 h

La cifra reproducible para `rho160_d16` es **292,65 alertas en cola** y **69,395 horas estimadas de servicio nominal pendiente por etapas incompletas** en el snapshot horario más próximo al retorno HLS-B→D1. Se reconstruye de la siguiente manera:

| Magnitud del snapshot de retorno HLS-B | Media | Campo de origen | Significado |
|---|---:|---|---|
| Conteos en cola L1+L2 | 292,65 | `queue_l1 + queue_l2` | Etapas incompletas que todavía no han empezado servicio en ese nivel. |
| Servicio nominal pendiente estimado L1+L2 | 69,395 h | `work_l1_h_est + work_l2_h_est` | Suma de servicio nominal por clase para etapas incompletas, incluyendo espera y servicio activo. No son horas residuales medidas. |
| Analistas ocupados L1+L2 | 6,85 | `occupied_l1 + occupied_l2` | Ocupación instantánea media; no son trabajo adicional en horas. |

La cifra de **aproximadamente 170 h no aparece en los CSV, esquema, configuración ni informe publicado** y no se puede reconstruir a partir de las variables guardadas. Se originó en un resumen narrativo previo; se retira por falta de respaldo. No hay una medida directa de “trabajo total del sistema”: el estimador cuenta la carga nominal de cada etapa L1/L2 incompleta, sin descontar servicio ya consumido y sin añadir el trabajo L2 todavía no iniciado para alertas que siguen en L1. Por ello 69,395 h es un indicador de carga nominal por etapas, no una predicción exacta del tiempo hasta vaciar el sistema. La cola no incluye las etapas activas; la ocupación se guarda aparte. El snapshot más cercano no representa un checkpoint exacto del evento de conmutación.

Las series se calculan solo con alertas cuya llegada es estrictamente anterior al tiempo del snapshot (`arrival < t`); las llegadas futuras permanecen en el denominador terminal, no en cola ni trabajo instantáneo. Para `rho160_d16`, la hora media de transición de retorno es 21,679 h (1,679 h después del fin del pulso); cada registro físico es horario y el snapshot de cada semilla se selecciona por menor distancia temporal. La definición puede inspeccionarse en `run_soc_hls_final_operating_map.py` y su agregación en `summarize_soc_hls_final_operating_map.py`.

Las validaciones guardadas informan 8.040 filas de corte, 2.680 celdas escenario/semilla/condición/política/corte, hash de traza y admitidas iguales entre políticas, `admitted = completed + pending`, R/N acotado por SLA y cortes H/HD para todos los episodios. El máximo plazo es 12 h y el drenaje es 24 h: los deadlines maduran antes de H+24. Episodios y prioridades reproducen el R/N, SLA y calidad publicados; la calidad es esperada/modelada entre completadas, no precisión empírica. No se encontró una inconsistencia que requiera repetir episodios. La antigua serie de postproceso que contaba llegadas futuras ya fue descartada y sustituida antes del commit de referencia.

Correcciones documentales heredadas, ya incorporadas al mapa publicado: SLA en `nom_r125_d16` (D1 0,9105; P1 0,9943; HLS-B 0,9919) y llegadas esperadas para `nom_r125_d8_fastrec` (619,5, frente a 618,1 admitidas observadas; no 670,7). La campaña final no modificó las simulaciones históricas.

## 2. Diseño y lectura estadística

El mapa central contiene 30 perfiles: ρ alta {1,00; 1,10; 1,20; 1,25; 1,40; 1,60} × duración {2, 4, 8, 12, 16 h}; ρ habitual/recuperación=0,85, pulso desde t=4 h, 20 h de recuperación con llegadas y 24 h de drenaje. Se usaron 20 semillas pareadas por celda y 60 en seis celdas escogidas antes de observar rendimientos por proximidad de Γ a 1. Los IC son t pareados por semilla, sin ajuste por multiplicidad. Los 17 resultados inciertos siguen siendo inciertos; no se interpretan como victorias.

Para el mapa descriptivo, “liderazgo separado” significa que la mayor media queda separada de cada rival por el criterio nominal de IC95 pareados de esa celda. “Líder medio incierto” significa que no queda separado de todos los rivales. El umbral de diferencia práctica de 0,005 R/N usado en el mapa es una convención descriptiva, no un umbral económico o clínico validado. No se interpolan fronteras entre celdas.

## 3. Regiones operativas observadas

| Resultado del mapa (30 celdas) | Celdas/perfiles | Lectura |
|---|---|---|
| D1: media líder y separado | 9: rho110_d08/d12; rho120_d04/d08; rho125_d04/d08; rho140_d04; rho160_d02/d04 | Predomina en menor presión, donde proteger deadlines aporta menos y la calidad modelada de D1 pesa más en R/N. |
| P1: media líder y separado | 2: rho140_d16; rho160_d12 | En estos pulsos severos y persistentes la pérdida de puntualidad con D1 es grande; la priorización temporal recupera más alertas puntuales pese a menor calidad por completada. |
| HLS-B: media líder y separado | 2: rho120_d16; rho160_d16 | Son dos celdas concretas, no una región continua demostrada ni una superioridad general. |
| Líder medio estadísticamente incierto | 17 | Ninguna política se puede declarar ganadora en esas celdas según el criterio pareado usado. |
| Equivalencia práctica de las tres | 0 | Ninguna cumple que todas las diferencias medias entre políticas estén dentro de 0,005. Algunas parejas sí difieren muy poco, sin equivalencia de las tres. |

La región severa se define por el descriptor exógeno Γ≥1, no por qué política gana. En ella el rendimiento se deteriora y el backlog crece con intensidad y persistencia. Γ es una aproximación fluida: no incorpora composición de clases, ruteo y elegibilidad con exactitud. La tabla/figura completa, diferencias pareadas y sus IC están en [SOC_HLS_FINAL_OPERATING_MAP.md](SOC_HLS_FINAL_OPERATING_MAP.md), [mapa de políticas](figures/soc_hls_final_policy_map.svg) y [mapa de presión](figures/soc_hls_final_pressure_map.svg).

### Celdas ilustrativas del mapa existente

R/N es la media terminal H+D, con denominador todas las alertas admitidas. Los IC son exploratorios y no corregidos por selección/multiplicidad.

| Perfil | n | D1 R/N | P1 R/N | HLS-B R/N | HLS-B−D1 [IC95] | HLS-B−P1 [IC95] | Interpretación del líder medio |
|---|---:|---:|---:|---:|---:|---:|---|
| rho120_d16 | 60 | 0,6360 | 0,6347 | 0,6498 | +0,0137 [0,0074; 0,0200] | +0,0151 [0,0106; 0,0195] | HLS-B separado de ambas en esta celda. |
| rho125_d12 | 60 | 0,6547 | 0,6345 | 0,6561 | +0,0015 [−0,0030; 0,0060] | +0,0216 [0,0187; 0,0246] | Mayor media HLS-B, pero no separado de D1. |
| rho125_d16 | 60 | 0,5997 | 0,6342 | 0,6340 | +0,0343 [0,0267; 0,0419] | −0,0002 [−0,0062; 0,0058] | P1 mayor por 0,0002; no separado de HLS-B. |
| rho140_d12 | 20 | 0,5763 | 0,6330 | 0,6212 | +0,0449 [0,0309; 0,0589] | −0,0117 [−0,0236; 0,0002] | P1 mayor, pero HLS-B−P1 cruza cero nominalmente. |
| rho140_d16 | 20 | 0,4474 | 0,5335 | 0,5113 | +0,0639 [0,0537; 0,0741] | −0,0221 [−0,0401; −0,0041] | P1 separado de HLS-B y D1. |
| rho160_d12 | 20 | 0,4047 | 0,4883 | 0,4696 | +0,0649 [0,0533; 0,0765] | −0,0187 [−0,0371; −0,0004] | P1 separado de HLS-B y D1 en el contraste nominal. |
| rho160_d16 | 20 | 0,2662 | 0,3024 | 0,3147 | +0,0485 [0,0401; 0,0568] | +0,0123 [0,0095; 0,0150] | HLS-B separado de ambas en esta celda. |

## 4. Mecanismos compatibles con los datos

En las siete celdas anteriores, SLA terminal / calidad modelada entre completadas para D1, P1 y HLS-B, respectivamente:

| Perfil | SLA D1/P1/HLS-B | Calidad D1/P1/HLS-B | P1 durante el pulso HLS-B | Cola D1 L1 al final del pulso | Servicio nominal D1 L1 pendiente estimado |
|---|---|---|---:|---:|---:|
| rho120_d16 | 0,941 / 0,995 / 0,975 | 0,674 / 0,638 / 0,666 | 58,6% | 129,8 | 28,0 h |
| rho125_d12 | 0,971 / 0,995 / 0,986 | 0,674 / 0,638 / 0,665 | 64,3% | 116,7 | 25,5 h |
| rho125_d16 | 0,883 / 0,994 / 0,953 | 0,675 / 0,638 / 0,664 | 71,4% | 153,6 | 33,1 h |
| rho140_d12 | 0,847 / 0,992 / 0,933 | 0,675 / 0,638 / 0,664 | 78,7% | 168,2 | 36,7 h |
| rho140_d16 | 0,653 / 0,837 / 0,772 | 0,673 / 0,638 / 0,661 | 84,0% | 220,1 | 48,3 h |
| rho160_d12 | 0,589 / 0,766 / 0,709 | 0,673 / 0,637 / 0,662 | 83,6% | 238,1 | 52,3 h |
| rho160_d16 | 0,387 / 0,474 / 0,485 | 0,674 / 0,637 / 0,662 | 87,3% | 303,9 | 68,7 h |

**D1** conserva la calidad completada más alta en estas celdas; cuando crece el backlog, cae su SLA y el R/N terminal sufre. **P1** levanta el SLA bajo congestión sostenida, con una reducción de alrededor de 0,036 en calidad por completada respecto a D1. **HLS-B** produce un compromiso intermedio y, en las celdas rho120_d16 y rho160_d16, ese balance resulta en R/N mayor que ambas fijas. En rho140_d16/rho160_d12, aun activando P1 durante cerca de 84% del pulso, HLS-B no iguala a P1. En rho125_d16, HLS-B recupera mucho frente a D1, pero empata prácticamente con P1 en media.

En rho160_d16 HLS-B vuelve a D1 en promedio 1,679 h después del final del pulso, cuando persiste una cola grande. En el snapshot horario más cercano se observan 292,65 etapas en cola y 69,395 h de servicio nominal pendiente estimado. Este hecho describe la trayectoria del supervisor; por sí solo no demuestra que mantener P1 hubiera mejorado el resultado. Las comparaciones de política son episodios completos emparejados, no intervenciones causales sobre el instante de retorno.

En L1 se concentra el backlog de las celdas severas; la sensibilidad mantiene la demanda absoluta y muestra que subir de 6 a 7 analistas L1 en rho160_d16 lleva D1 R/N de 0,2662 a 0,6319 y HLS-B de 0,3147 a 0,6375; subir L2 de 2 a 4 con L1 fijo cambia poco. Esto identifica un cuello de botella L1 para estas configuraciones, no una ley económica. También hay falta de monotonía entre algunos rosters, consistente con heterogeneidad y asignación discreta. No se conocen costes para comparar capacidad y organización en términos económicos.

Los indicadores de backlog, SLA, calidad y fracción P1 covarían con la severidad; no prueban por separado mecanismos causales. La evidencia de mecanismo es descriptiva y coherente con las políticas definidas.

## 5. Sensibilidad SLA y dimensionamiento

La configuración de plazo es hipotética: crítica 1 h, alta 4 h, baja 12 h. No es un SLA contractual de GMV-CERT.

| Sensibilidad (20 semillas; condición) | R/N D1 / P1 / HLS-B | HLS-B−D1 [IC95] | HLS-B−P1 [IC95] | Cambio relevante |
|---|---|---|---|---|
| Ref. 1:4:12, rho140_d08 | 0,6627 / 0,6345 / 0,6605 | −0,0022 [−0,0080; +0,0037] | +0,0260 [+0,0236; +0,0285] | D1 media líder; diferencia HLS-B−D1 no separada. |
| Escala T0=0,75, rho140_d08 | 0,6004 / 0,6283 / 0,6317 | +0,0313 [+0,0196; +0,0430] | +0,0035 [−0,0091; +0,0160] | HLS-B supera D1; no queda separada de P1. |
| Escala T0=1,25, rho140_d08 | 0,6726 / 0,6362 / 0,6647 | −0,0079 [−0,0088; −0,0070] | +0,0285 [+0,0271; +0,0298] | D1 media líder. |
| Separación 1:2:8, rho140_d08 | 0,5583 / 0,6147 / 0,6040 | +0,0457 [+0,0342; +0,0572] | −0,0107 [−0,0231; +0,0016] | P1 media líder; HLS-B−P1 no separada. |
| Separación 1:8:16, rho140_d08 | 0,6705 / 0,6345 / 0,6627 | −0,0078 [−0,0088; −0,0068] | +0,0282 [+0,0268; +0,0296] | D1 media líder. |
| Ref. 1:4:12, rho160_d16 | 0,2662 / 0,3024 / 0,3147 | +0,0485 [+0,0401; +0,0568] | +0,0123 [+0,0095; +0,0150] | HLS-B media líder. |
| Escala T0=1,25, rho160_d16 | 0,3770 / 0,4596 / 0,4461 | +0,0691 [+0,0553; +0,0829] | −0,0135 [−0,0280; +0,0011] | P1 media líder; contraste HLS-B−P1 incierto. |
| Separación 1:8:16, rho160_d16 | 0,4607 / 0,5551 / 0,5259 | +0,0652 [+0,0563; +0,0741] | −0,0292 [−0,0430; −0,0154] | P1 supera a HLS-B. |

SLA global / calidad completada en el mismo orden de políticas (episodios H+D):

| Perfil | Configuración | SLA D1/P1/HLS-B | Calidad D1/P1/HLS-B |
|---|---|---|---|
| rho140_d08 | 1:4:12 | 0,982 / 0,995 / 0,991 | 0,674 / 0,638 / 0,666 |
| rho140_d08 | T0=0,75; 4:12 | 0,885 / 0,985 / 0,946 | 0,674 / 0,638 / 0,666 |
| rho140_d08 | T0=1,25; 4:12 | 0,997 / 0,997 / 0,998 | 0,674 / 0,638 / 0,666 |
| rho140_d08 | 1:2:8 | 0,821 / 0,964 / 0,904 | 0,674 / 0,638 / 0,666 |
| rho140_d08 | 1:8:16 | 0,994 / 0,995 / 0,995 | 0,674 / 0,638 / 0,666 |
| rho160_d16 | 1:4:12 | 0,387 / 0,474 / 0,485 | 0,674 / 0,637 / 0,662 |
| rho160_d16 | T0=0,75; 4:12 | 0,277 / 0,342 / 0,350 | 0,674 / 0,638 / 0,663 |
| rho160_d16 | T0=1,25; 4:12 | 0,548 / 0,720 / 0,676 | 0,673 / 0,638 / 0,661 |
| rho160_d16 | 1:2:8 | 0,244 / 0,299 / 0,305 | 0,675 / 0,638 / 0,663 |
| rho160_d16 | 1:8:16 | 0,671 / 0,871 / 0,792 | 0,674 / 0,638 / 0,662 |

Las cinco condiciones SLA están completas en el mapa y los CSV. La escala temporal y la separación relativa pueden cambiar el signo y el líder; no hay una sola frontera de congestión independiente del plazo.

| Plantilla y demanda absoluta fija | Rho efectiva normal/pulso en d16 | R/N D1 / P1 / HLS-B | HLS-B−D1 [IC95] | Efecto frente a 6×3 |
|---|---:|---|---|---|
| 5×3, rho160_d16 | 1,03 / 1,94 | 0,1913 / 0,1933 / 0,1977 | +0,0064 [0,0015; 0,0113] | Reducción de capacidad empeora marcadamente los tres rendimientos. |
| 6×2, rho160_d16 | 0,85 / 1,60 | 0,2656 / 0,3019 / 0,3141 | +0,0485 [0,0403; 0,0568] | Similar a 6×3; L2 cambia poco. |
| 6×3, rho160_d16 | 0,85 / 1,60 | 0,2662 / 0,3024 / 0,3147 | +0,0485 [0,0401; 0,0568] | Referencia. |
| 6×4, rho160_d16 | 0,85 / 1,60 | 0,2660 / 0,3025 / 0,3147 | +0,0486 [0,0403; 0,0570] | L2 adicional cambia poco. |
| 7×3, rho160_d16 | 0,72 / 1,36 | 0,6319 / 0,6094 / 0,6375 | +0,0056 [−0,0050; 0,0161] | Más L1 reduce la presión; HB−D1 deja de estar separada. |

La tabla completa de rostering y sus contrastes pareados está en [SOC_HLS_FINAL_OPERATING_MAP.md](SOC_HLS_FINAL_OPERATING_MAP.md) y `sla_staff_summary.csv`. Rho se recalculó al variar la plantilla porque se conservó la tasa absoluta de llegada. El aumento de L1 puede mejorar más que cambiar la organización en la región más saturada ensayada, pero no permite una recomendación económica sin costes, turnos ni requisitos operativos observados.

## 6. Contribuciones defendibles para el artículo

1. **Complementariedad confirmatoria de mecanismos de organización.** El contraste estacionario confirmado D1/P1 muestra dependencia del régimen (a ρ=1,25, P1−D1=+0,0982, IC95 [+0,0891; +0,1073], n=100; en cargas menores el balance difiere). La validación independiente de HLS-B, con parámetros congelados y 100 semillas, da HLS-B−D1=+0,02820 [0,02526; 0,03115] en la mezcla sintética predefinida de cuatro condiciones; el resultado agregado se concentra en sobrecarga estacionaria y no demuestra superioridad general en transiciones. **Respaldada como evidencia confirmatoria dentro de esos estimandos sintéticos.**

2. **Mapa exploratorio de dependencia conjunta entre intensidad, persistencia y congestión.** Las 30 celdas muestran deterioro de SLA/R/N y acumulación creciente, liderazgo de D1 en parte de presiones menores, liderazgo P1 en dos celdas severas, HLS-B separado de ambos en dos celdas, y 17 celdas sin líder estadísticamente separado. **Respaldada como caracterización exploratoria de las condiciones ensayadas; no es una frontera universal ni confirmación postselección.**

3. **SLA y capacidad desplazan el valor relativo de la adaptación.** Los contrastes condicionales muestran que escalas/plazos relativos y capacidad L1 pueden cambiar el signo de HLS-B−D1 y quién lidera; al incrementar L1 en el perfil severo mejora sustancialmente la prestación. **Respaldada exploratoriamente en los puntos ejecutados; los SLA y rosters son hipotéticos y no forman una distribución operativa.**

## 7. Conclusiones para Results y Discussion

- **Demostrado en validación confirmatoria:** D1 y P1 tienen fortalezas condicionadas al régimen sintético y la configuración congelada HLS-B mejora a D1 en la distribución confirmatoria predefinida. El estimando agregado no representa prevalencia real ni garantiza la ventaja en cada perfil dinámico.
- **Observado exploratoriamente:** al aumentar intensidad y duración, crecen cola y trabajo nominal pendiente y cae cumplimiento; P1 puede liderar bajo sobrecarga severa sostenida. HLS-B obtiene sus dos liderazgos separados en rho120_d16 y rho160_d16 y mantiene un compromiso intermedio en varias otras celdas.
- **Limitaciones de HLS-B:** su decisión responde a la presión estimada con ventana e histéresis; la fracción P1 crece en los pulsos severos, pero no alcanza consistentemente el rendimiento de la fija adecuada. Retornar a D1 con backlog residual demuestra que el estado de modo no equivale a recuperar el sistema, no que el retorno sea causa de pérdida.
- **SLA y recursos:** los cambios de escala/separación de plazos alteran prestaciones y diferencias; L1 domina el backlog en los perfiles examinados. Una política organizativa puede aliviar parte del problema, pero con capacidad claramente insuficiente la plantilla determina el techo de prestación.
- **Conclusión condicional permitida:** dentro del modelo, D1 es una opción fuerte cuando hay holgura temporal suficiente y se valora la calidad modelada; P1 protege plazos cuando la sobrecarga persistente vuelve crítica la puntualidad; HLS-B puede balancear ambas y aportar una ventaja localizada. No hay evidencia para recomendar una política universal ni para inferir en qué región opera un SOC real sin estimar primero sus demanda, servicios, deadlines, composición, elegibilidad, cobertura y capacidad.

## 8. Límites de validez externa y reproducibilidad

Las llegadas son Poisson por tramos; los tiempos de servicio, dificultad, escalado IA, competencia, elegibilidad, plazos, roster y capacidad continua son supuestos del modelo. Los deadlines son SLA hipotéticos de resolución terminal, no compromisos de GMV-CERT. No hay turnos, cobertura 8×5/24×7, ausencias, pausas, cambios de guardia, colas limitadas, rework, costes, ni modelo validado de L3. Las métricas de calidad son expectativas del modelo. SOCTRA no aporta tiempos de trabajo ni una distribución de episodios que permita asignar probabilidades operativas. Γ aproxima presión fluida, no la dinámica heterogénea completa.

Reproducción del mapa: [configuración](config/soc_hls_final_operating_map.json), [runner](run_soc_hls_final_operating_map.py), [resumen](summarize_soc_hls_final_operating_map.py), [validaciones](../../results/soc_hls_final_operating_map/validation_checks.json), resúmenes y episodios bajo `results/soc_hls_final_operating_map/`. Los archivos de serie/mode guardan el detalle temporal y de conmutaciones. La validación HLS-B y los estudios confirmatorios mantienen sus semillas y análisis separados. No se recalculó una prueba confirmatoria con el barrido exploratorio.
