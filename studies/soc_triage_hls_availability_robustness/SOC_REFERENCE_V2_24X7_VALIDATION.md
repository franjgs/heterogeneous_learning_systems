# Control diagnóstico V2 frente a V2_24X7

> **NEW MODEL / MODELO NUEVO:** ambas configuraciones usan triaje y una investigación única. Este informe técnico no pertenece al OLD MODEL ni cambia sus campañas.

**Alcance:** comparación técnica de dos ejecuciones emparejadas; no campaña de políticas ni validación empírica.  
**Commit de partida:** `13c0bb7a7a2dddfbc6a6d1fde838a1fa4c4f704a`.  
**Archivos:** [`SOC_REFERENCE_ORGANIZATION_V2.json`](config/SOC_REFERENCE_ORGANIZATION_V2.json) y [`SOC_REFERENCE_ORGANIZATION_V2_24X7.json`](config/SOC_REFERENCE_ORGANIZATION_V2_24X7.json).  
**Semilla:** 998001.  
**SHA-256 de V2_24X7 JSON:** `12125bd1c5acb186c65d79f531b9b398f904bbdeb171ced58125156d65c4fe36`.

## 1. Cambio y procedimiento

V2_24X7 se creó copiando V2. La única diferencia de contenido JSON son los ocho objetos `organization.analysts[*].calendar`, cambiados a `{"kind":"continuous"}`. Los analistas, competencias, eficiencias, elegibilidades, servicios, forecasts, recomendaciones, etiquetas de referencia, dificultad, clase, severidad, deadline, alpha=0.50, beta=0, gamma=1, tasas, pulso, recuperación, configuración D1 y horizontes son idénticos. Se mantiene `triage_single_investigation` y el motor `CalendarBackend`; no se cambian motor ni políticas.

Ejecuciones:

```bash
python studies/soc_triage_hls_availability_robustness/run_scenario.py --config studies/soc_triage_hls_availability_robustness/config/SOC_REFERENCE_ORGANIZATION_V2.json --seed 998001
python studies/soc_triage_hls_availability_robustness/run_scenario.py --config studies/soc_triage_hls_availability_robustness/config/SOC_REFERENCE_ORGANIZATION_V2_24X7.json --seed 998001
python studies/soc_triage_hls_availability_robustness/analyze_reference_organization.py --config studies/soc_triage_hls_availability_robustness/config/SOC_REFERENCE_ORGANIZATION_V2.json
python studies/soc_triage_hls_availability_robustness/analyze_reference_organization.py --config studies/soc_triage_hls_availability_robustness/config/SOC_REFERENCE_ORGANIZATION_V2_24X7.json
```

La traza completa (incluidas llegadas, clases, severidades, referencias de escalado, recomendaciones y dificultad) coincide elemento por elemento entre las dos configuraciones. Se repitió cada ejecución y coincidieron traza, asignaciones, segmentos de trabajo, estados y resultados. Por ello, los cambios de salida que siguen se deben a la disponibilidad/capacidad resultante y a las asignaciones condicionadas por ella; no a cambios en la demanda aleatoria.

La disponibilidad cambia además las horas-persona posibles: L1 pasa de 168 horas-persona/semana de roster a 5×168=840 (factor 5); L2, de 3×40=120 a 3×168=504 (factor 4.2). Esta no es una intervención de “quitar turnos manteniendo capacidad fija”. No se reescaló la demanda para mantener rho.

## 2. Resultados de la misma semilla

| Medida | V2: L1 24x7 roster / L2 8x5 | V2_24X7: todos individualmente continuos |
|---|---:|---:|
| Alertas | 476 | 476 |
| Clases (Top5 / Next5 / Tail) | 239 / 148 / 89 | 239 / 148 / 89 |
| Severidades (alta / media / baja) | 98 / 142 / 236 | 98 / 142 / 236 |
| TP / FP / TN / FN | 35 / 28 / 405 / 8 | 35 / 28 / 405 / 8 |
| Ruta L1 / L2 | 413 / 63 | 413 / 63 |
| Investigaciones | 476 con una; 0 con dos | 476 con una; 0 con dos |
| Finalizadas dentro SLA | 335 (70.38%) | 476 (100%) |
| Finalizadas fuera SLA | 141 (29.62%) | 0 |
| Pendientes a 336 h | 0 | 0 |
| Trabajo efectivo L1 | 122.020 h | 121.8325 h |
| Trabajo efectivo L2 | 12.08475 h | 12.22925 h |
| Espera media llegada→primer servicio L1 | 2.245 h | 0 h |
| Espera media llegada→primer servicio L2 | 18.193 h | 0 h |
| Suspensión total L1 / L2 | 416 h / 0 h | 0 h / 0 h |
| Tareas suspendidas L1 / L2 | 12 / 0 | 0 / 0 |
| Tiempo medio de respuesta L1 | 3.548 h | 0.295 h |
| Tiempo medio de respuesta L2 | 18.385 h | 0.194 h |
| Tiempo medio de respuesta global | 5.512 h | 0.282 h |

La clase, severidad y confusión se mantienen. Las asignaciones por profesional y el servicio efectivo agregado cambian levemente: al estar todos disponibles, D1 tiene otro conjunto de profesionales libres en cada evento. La reproducción confirma una investigación única y deadlines absolutos en ambos casos. No se añade ni pausa ningún reloj; con esta configuración/semilla todas las tareas de V2_24X7 terminan antes de sus deadlines.

## 3. Capacidad asignable y carga relativa

Se reutilizó `analyze_reference_organization.py` con `scenario_diagnostics.assess_capacity` y el LP `effective_capacity`. La capacidad por nivel es tasa máxima de llegadas de la mezcla de clases esperada, con elegibilidad, servicio, alpha/beta/gamma y disponibilidad de calendario. No es una tasa de despacho observada ni una garantía de SLA. En V2_24X7 todos los calendarios tienen fracción disponible 1 durante las 168 h.

| Régimen | Nivel | Capacidad asignable alerta/h | Tasa ofrecida alerta/h | rho | Trabajo ofrecido h-persona/h |
|---|---|---:|---:|---:|---:|
| Habitual (0–120 h) | L1 | 17.035 | 2.188 | 0.128 | 0.646 |
|  | L2 | 13.046 | 0.312 | 0.024 | 0.072 |
| Pulso (120–144 h) | L1 | 17.035 | 5.252 | 0.308 | 1.549 |
|  | L2 | 13.046 | 0.748 | 0.057 | 0.173 |
| Recuperación (144–168 h) | L1 | 17.035 | 1.313 | 0.077 | 0.387 |
|  | L2 | 13.046 | 0.187 | 0.014 | 0.043 |

Las cargas bajas resultan directamente de mantener la llegada V2 y poner a los cinco L1/tres L2 disponibles durante toda la semana. El máximo rho esperado del perfil es 0.308, en L1 durante el pulso. No hay régimen con sobrecarga media según este diagnóstico, aunque otras realizaciones o tasas podrían congestionar.

### Elegibilidad

No hay clases sin profesionales elegibles. Los cinco L1 son elegibles para las tres clases. En L2 cada clase tiene dos profesionales elegibles: Top5 (L2-01/L2-03), Next5 (L2-01/L2-02), Tail (L2-02/L2-03). La capacidad condicional del LP al ofrecer una clase cada vez es:

| Clase ofrecida | L1 alerta/h | L2 alerta/h | Restricción de elegibilidad L2 |
|---|---:|---:|---|
| portfolio_top5 | 20.101 | 13.614 | L2-01/L2-03 |
| portfolio_next5 | 16.751 | 9.575 | L2-01/L2-02 |
| portfolio_tail | 12.563 | 4.238 | L2-02/L2-03 |

Tail es la menor capacidad condicional L2, no una clase sin servicio. Esta configuración conserva heterogeneidad y cuellos por mezcla/elegibilidad aunque la disponibilidad temporal ya no limite.

### Utilización realizada por intervalo

La utilización observada usa trabajo ejecutado dividido por las horas-persona programadas disponibles en el mismo intervalo. V2 no tiene denominador disponible L2 durante el fin de semana; no se reporta como 0%.

| Intervalo | Nivel | V2 trabajo / horas-persona (uso) | V2_24X7 trabajo / horas-persona (uso) |
|---|---|---:|---:|
| Habitual, 0–120 h | L1 | 78.190 / 120 (65.2%) | 77.850 / 600 (13.0%) |
|  | L2 | 8.033 / 120 (6.7%) | 8.337 / 360 (2.3%) |
| Pulso, 120–144 h | L1 | 23.852 / 24 (99.4%) | 36.253 / 120 (30.2%) |
|  | L2 | Sin cobertura | 3.455 / 72 (4.8%) |
| Recuperación, 144–168 h | L1 | 19.578 / 24 (81.6%) | 7.729 / 120 (6.4%) |
|  | L2 | Sin cobertura | 0.438 / 72 (0.6%) |

Las cifras muestran el efecto conjunto: V2 satura L1 en el pulso y L2 no puede trabajar durante sus intervalos cerrados; V2_24X7 elimina ambas limitaciones, pero también aumenta fuertemente el denominador de capacidad. Las pequeñas diferencias en trabajo total por nivel reflejan distintas asignaciones/eficiencias, no una traza distinta.

## 4. Colas y trabajo pendiente

Se reconstruyeron estados cada 6 horas desde eventos, inicios, finalizaciones y segmentos; es un muestreo, no un máximo instantáneo certificado. “Cola” significa llegada aún no iniciada; “propiedad” una tarea ya iniciada y no terminada. Residual solo suma servicios asignados y no inventa duración efectiva para tareas aún en cola.

| Tiempo | V2 L1 cola/propiedad | V2 L2 cola/propiedad | V2_24X7 L1 cola/propiedad | V2_24X7 L2 cola/propiedad |
|---:|---:|---:|---:|---:|
| 120 h, inicio pulso | 0 / 3 | 1 / 0 | 0 / 0 | 0 / 0 |
| 126 h | 12 / 3 | 5 / 0 | 0 / 3 | 0 / 0 |
| 132 h | 20 / 4 | 10 / 0 | 0 / 2 | 0 / 0 |
| 138 h | 32 / 5 | 14 / 0 | 0 / 2 | 0 / 0 |
| 144 h, fin pulso | 41 / 5 | 19 / 0 | 0 / 1 | 0 / 0 |
| 168 h, cierre admisión | 0 / 4 | 22 / 0 | 0 / 0 | 0 / 0 |
| 180 h | 0 / 3 | 0 / 0 | 0 / 0 | 0 / 0 |

En V2 el pulso produce una cola L1 grande y el fin de semana acumula L2 en espera. En V2_24X7 no aparece cola de alertas sin iniciar en estos puntos; durante el pulso hay como máximo tres L1 en servicio en los cortes mostrados, con capacidad concurrente para cinco, y L2 empieza al llegar. Toda el trabajo queda completado mucho antes del corte de evaluación.

## 5. Factibilidad de deadlines

El diagnóstico ex ante reutilizado enumera llegadas en una rejilla de 15 minutos ponderada por clase, severidad y resultados esperados del clasificador (no una muestra estocástica). En ambas configuraciones la inviabilidad intrínseca por servicio activo mínimo es 0%. La inviabilidad por calendario baja de **6.9176%** en V2 a **0%** en V2_24X7; condicionada a rutas L2 baja de **55.4691%** a **0%**. En la semilla concreta, la clasificación individual fue:

| Configuración | Inviable por servicio sin calendario | Inviable por calendario sin colas | Tarde en ejecución pese a cota viable | Cumple |
|---|---:|---:|---:|---:|
| V2 L1 roster 24x7/L2 8x5 | 0 | 35 | 106 | 335 |
| V2_24X7 | 0 | 0 | 0 | 476 |

La discrepancia entre 6.92% ex ante y 35/476=7.35% de V2 es esperable porque el primero es una enumeración ponderada y el segundo una realización. V2_24X7 no elimina congestión como posibilidad matemática; en esta semilla no hubo retrasos porque la demanda tuvo amplio margen frente a la capacidad disponible.

## 6. Decisión y límites

V2_24X7 es apropiada como base experimental controlada para aislar asignación, heterogeneidad, calidad de triaje, congestión y deadlines sin cierres de calendario. La disponibilidad continua por individuo es una hipótesis simplificadora heredada del estudio original, no una afirmación sobre horarios laborales. El motor de calendarios y la variante V2 original permanecen disponibles para estudios posteriores de turnos.

No obstante, con las tasas congeladas de V2, la nueva disponibilidad produce un escenario holgado: todas las alertas cumplen, la espera observada es cero y rho máximo del pulso es 0.308. Puede reducir diferencias observables entre políticas y no estresa congestión. No se aumentan tasas ahora, tal como se solicitó; futuros estudios deberán tratar el perfil temporal de demanda como variable experimental explícita, sin inferir de este episodio que una política sea mejor.

Las tarifas relativas horarias 1.0 L1/1.8 L2 y demás campos económicos se conservaron. La metadata `contracted_hours_per_week` heredada de V2 describe el roster anterior y no sirve para calcular costes de disponibilidad continua. No se reporta un nuevo coste laboral: poner personas “disponibles” 168 h/semana es idealización, no un contrato de trabajo modelado.

V2, su resultado previo, escenarios históricos, generadores, motores, clasificadores, políticas y manuscritos no se alteraron. El analizador admite `--config`; usa los diagnósticos existentes. La comprobación focalizada pasó **64 pruebas** de loader, integración, orquestación y API; la prueba de variante verifica que el JSON difiere únicamente en calendarios, que las trazas y deadlines son iguales y que no hay suspensiones. No se ejecutaron campañas ni regresiones masivas.
