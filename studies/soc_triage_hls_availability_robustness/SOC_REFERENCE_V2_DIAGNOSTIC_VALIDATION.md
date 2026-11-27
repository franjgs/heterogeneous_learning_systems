# Validación diagnóstica de V2 — episodio 998001

> **NEW MODEL / MODELO NUEVO:** esta ejecución usa `triage_single_investigation`; se conserva como diagnóstico de una semilla, no como resultado OLD MODEL ni como campaña comparativa.

**Estado:** informe de una ejecución técnica reproducible; no es campaña ni comparación de políticas.  
**Configuración:** [`SOC_REFERENCE_ORGANIZATION_V2.json`](config/SOC_REFERENCE_ORGANIZATION_V2.json).  
**Datos por alerta:** [`SOC_REFERENCE_V2_SEED_998001_ALERTS.csv`](SOC_REFERENCE_V2_SEED_998001_ALERTS.csv).  
**Modelo canónico:** [`SOC_ORGANIZATIONAL_MODEL.md`](SOC_ORGANIZATIONAL_MODEL.md).

## 1. Pregunta y alcance

Este informe explica los 141 incumplimientos observados en la ejecución V2 comunicada. Reproduce la semilla `998001`, clasifica cada alerta con realizaciones efectivas conocidas solo al evaluador y relaciona el resultado con calendario, esperas, trabajo y pulso de carga. No cambia V2, no estima un efecto causal de política ni predice resultados de otras semillas.

La asignación configurada en ambos niveles es D1. Los rótulos TP/FP/TN/FN, dificultad y multiplicadores se usan después de la ejecución para describir el episodio; nunca se suministran al dispatcher como atributos de alertas. El horizonte de admisión es 168 h y el corte de evaluación 336 h, con tiempo desde lunes 00:00. El calendario semanal es abstracto y no incorpora zona horaria/DST.

## 2. Reproducción y consistencia

Comando reproducible desde la raíz del repositorio:

```bash
python studies/soc_triage_hls_availability_robustness/run_scenario.py --config studies/soc_triage_hls_availability_robustness/config/SOC_REFERENCE_ORGANIZATION_V2.json --seed 998001
```

Se usó el JSON V2 sin overrides, `triage_single_investigation`, `CalendarBackend` y política D1 tal como está configurada. El resultado fue:

| Comprobación | Resultado |
|---|---:|
| Alertas generadas/admitidas | 476 |
| TP / FP / TN / FN | 35 / 28 / 405 / 8 |
| Ruta L1 / L2 | 413 / 63 |
| Investigaciones por alerta | 476 con una investigación; ninguna con dos |
| Finalizadas dentro del SLA | 335 (70.38%) |
| Finalizadas fuera del SLA | 141 (29.62%) |
| Pendientes al corte | 0 |
| Trabajo efectivo L1 / L2 | 122.020 / 12.085 h |
| Espera media llegada→primer servicio L1 / L2 | 2.245 / 18.193 h |
| Tiempo medio de respuesta, todas las finalizadas | 5.512 h |

La suma 335+141+0=476 y las rutas concuerdan con la matriz de confusión: TP+FP=63 recomendaciones L2; TN+FN=413 recomendaciones L1. Todas las alertas finalizaron antes de 336 h, incluso si su deadline ya había vencido. No se cancela trabajo al incumplir el SLA.

Se repitió el episodio completo con los mismos parámetros y semilla: la traza, asignaciones, segmentos de trabajo, estados por tarea y resultados fueron idénticos. Esta igualdad verifica reproducibilidad de esta ejecución; no equivale a una regresión de resultados históricos ni a validación del modelo.

## 3. Método de clasificación temporal

Se reutilizó `scenario_diagnostics.assess_deadline_feasibility` en modo de investigación única y con la ruta efectivamente recomendada. Se pasaron las realizaciones de dificultad y el multiplicador por alerta solamente a esta evaluación externa. Para cada alerta se compararon:

1. **Cota activa optimista:** menor servicio efectivo entre profesionales elegibles del nivel recomendado, sin espera ni calendario.
2. **Cota de calendario sin contención:** primera finalización posible desde la llegada entre los profesionales elegibles, respetando calendarios individuales y suponiendo que no hay otros trabajos.
3. **Ejecución observada:** finalización y trabajo registrado por el motor.

Las cuatro clases, mutuamente excluyentes, son:

- **A. Inviable por tiempo activo:** la cota activa supera el deadline.
- **B. Inviable por calendario:** A no aplica, pero ni la mejor calendarización elegible sin contención acaba a tiempo.
- **C. Viable sin contención, retrasada en la ejecución:** la cota de calendario cabe en el SLA, pero la alerta termina tarde en la traza.
- **D. Cumplida:** finaliza dentro del SLA.

Una pendiente al corte se informaría aparte; en este episodio no hay pendientes. Las cotas son específicas de la ruta recomendada y del mejor profesional elegible, no una estimación de contrafactual de política.

### Resultado de las cotas

| Categoría | Alertas | % del episodio | Lectura |
|---|---:|---:|---|
| A. Inviable sin calendario | 0 | 0.00% | Ningún deadline era menor que el mínimo servicio activo efectivo |
| B. Imposible por calendario sin colas | 35 | 7.35% | Las 35 rutas L2 incumplen incluso con asignación individual sin contención |
| C. Viable sin contención, tarde en traza | 106 | 22.27% | Las 106 son rutas L1; la ejecución real añade esperas/suspensiones suficientes para incumplir |
| D. Dentro de SLA | 335 | 70.38% | Puntuales en la traza |
| **Total** | **476** | **100%** | |

Por tanto, **35/141=24.82%** de los incumplimientos pertenecen a la cota de inviabilidad por calendario. Los otros **106/141=75.18%** eran factibles bajo la mejor calendarización sin contención, pero llegaron tarde en esta ejecución. No hay incumplimientos por insuficiencia de tiempo activo a calendario continuo. La etiqueta C no demuestra que una política alternativa los hubiera salvado: combina espera por despacho, decisiones de asignación y, en algunos casos, suspensión del profesional asignado.

El diagnóstico previo del 6.92% era una enumeración temporal ponderada del escenario, no una observación de esta traza. La traza arroja 7.35% (35/476). Para las rutas L2, 35/63=55.56%, frente al 55.47% estimado previamente. La proximidad es una comprobación de escala, no validación independiente: ambas cifras comparten configuración e hipótesis.

## 4. Resultados por nivel, error, severidad y clase

`A/B/C/D` son los conteos de las cotas anteriores. “Late” es finalización posterior al deadline, no tarea cancelada.

### Por nivel

| Nivel | n | Dentro SLA | Tarde | Pendiente | A/B/C/D |
|---|---:|---:|---:|---:|---|
| L1 | 413 | 307 | 106 | 0 | 0 / 0 / 106 / 307 |
| L2 | 63 | 28 | 35 | 0 | 0 / 35 / 0 / 28 |

Los 35 retrasos L2 se explican por la cota calendarizada. Son 21 alertas llegadas sábado/domingo y 14 llegadas en días laborables fuera de una ventana que permitiera acabar dentro del SLA. En las 35, la finalización real excede la mejor finalización calendarizada sin contención en una media de 0.48 h (mediana 0.29 h; máximo 1.54 h). Esa diferencia indica que hubo además algo de espera/elección no óptima para el deadline, pero no cambia la clasificación: todas ya eran calendarizadas inviables.

Las 106 tardías L1 estaban dentro de la cota calendarizada más optimista. La finalización real quedó, en promedio, 11.26 h después de esa cota (mediana 12.02 h; máximo 52.55 h), indicando una contribución de ejecución significativa sobre la factibilidad ideal. Este exceso no se atribuye exclusivamente a una política: puede incluir cola, asignación de un profesional no óptimo para calendario/servicio y propiedad persistente durante suspensión.

### Por tipo de triaje (solo para evaluación)

| Tipo | Ruta | n | Dentro SLA | Tarde | Pendiente | A/B/C/D |
|---|---|---:|---:|---:|---:|---|
| TP | L2 | 35 | 15 | 20 | 0 | 0 / 20 / 0 / 15 |
| FP | L2 | 28 | 13 | 15 | 0 | 0 / 15 / 0 / 13 |
| TN | L1 | 405 | 301 | 104 | 0 | 0 / 0 / 104 / 301 |
| FN | L1 | 8 | 6 | 2 | 0 | 0 / 0 / 2 / 6 |

Todos los retrasos TP/FP son B y todos los retrasos TN/FN son C. Esto describe rutas y cotas, no una “penalización del error”: la clasificación de referencia es sintética y no es verdad objetiva de especialización. En esta semilla alpha=0.5 afecta el servicio FP L2; gamma=1 y beta=0 son neutros.

### Por severidad y clase

| Severidad | n | Dentro SLA | Tarde | A/B/C/D |
|---|---:|---:|---:|---|
| Alta (deadline 1 h) | 98 | 58 | 40 | 0 / 11 / 29 / 58 |
| Media (4 h) | 142 | 106 | 36 | 0 / 13 / 23 / 106 |
| Baja (12 h) | 236 | 171 | 65 | 0 / 11 / 54 / 171 |

| Clase | n | Dentro SLA | Tarde | A/B/C/D |
|---|---:|---:|---:|---|
| portfolio_top5 | 239 | 165 | 74 | 0 / 20 / 54 / 165 |
| portfolio_next5 | 148 | 116 | 32 | 0 / 10 / 22 / 116 |
| portfolio_tail | 89 | 54 | 35 | 0 / 5 / 30 / 54 |

### Por momento de llegada

La semana comienza lunes 00:00. Las franjas horarias son horas del reloj local abstracto del calendario; la tabla no controla si una llegada ocurrió en fin de semana. La lista completa por alerta contiene la hora exacta.

| Día | n | L1 / L2 | Tarde | B / C |
|---|---:|---:|---:|---:|
| Lun | 74 | 61 / 13 | 4 | 3 / 1 |
| Mar | 45 | 44 / 1 | 2 | 0 / 2 |
| Mié | 64 | 54 / 10 | 7 | 5 / 2 |
| Jue | 60 | 47 / 13 | 7 | 5 / 2 |
| Vie | 62 | 57 / 5 | 7 | 1 / 6 |
| Sáb | 141 | 123 / 18 | 97 | 18 / 79 |
| Dom | 30 | 27 / 3 | 17 | 3 / 14 |

| Hora de llegada | n | L1 / L2 | Tarde | L2 en B | En C |
|---|---:|---:|---:|---:|---:|
| 00:00–07:59 | 174 | 149 / 25 | 38 | 14 | 24 |
| 08:00–08:59 | 26 | 23 / 3 | 4 | 0 | 4 |
| 09:00–16:59 | 157 | 136 / 21 | 51 | 7 | 44 |
| 17:00–23:59 | 119 | 105 / 14 | 48 | 14 | 34 |

El gran aumento del sábado coincide con el pulso. El horario 09:00–16:59 incluye fines de semana, por lo que no equivale a “L2 abierto”; 7 casos B en esa franja llegaron sábado/domingo.

## 5. Espera, suspensión y colas

El motor registra por alerta el primer inicio de servicio, finalización, trabajo realizado, suspensión acumulada, profesional asignado y segmentos de trabajo. En este episodio, para finalizadas, la identidad `respuesta = espera antes del primer servicio + suspensión + trabajo activo` se cumple salvo redondeo numérico. No hay tareas pendientes que requieran interpretar trabajo residual al corte.

| Cohorte de SLA | n | Espera antes del primer servicio media | Suspensión media | Trabajo activo medio | Exceso medio sobre deadline |
|---|---:|---:|---:|---:|---:|
| Dentro SLA | 335 | 0.63 h | 0 h | 0.281 h | — |
| Tarde, L1 (C) | 106 | 7.35 h | 3.92 h | 0.310 h | 4.33 h |
| Tarde, L2 (B) | 35 | 31.00 h de no-trabajo total¹ | 0 h | 0.202 h | 25.63 h |

¹ Para L2 las tareas aún no empezadas esperan por calendario/cola; el API conserva el primer inicio, no una descomposición causal exacta entre ambas fuentes. La espera llegada→primer servicio media de las 63 alertas L2 fue 18.19 h. No se interpreta toda espera como congestión: fines de semana y noches están cerrados por diseño.

Doce alertas L1 tardías registran suspensión, con **416 h acumuladas** (máximo 40 h por alerta). El motor conserva el propietario durante la suspensión y no releva automáticamente el trabajo a otro L1. Esto confirma que cobertura de equipo no equivale a disponibilidad de cada profesional. Las restantes alertas L1 no tuvieron suspensión registrada; sus retrasos se asocian temporalmente a espera antes del servicio, aunque la espera no identifica por sí sola una decisión concreta como causa.

### Cola y trabajo en el tiempo

El siguiente muestreo de estado cada 6 h se reconstruyó de las llegadas, comienzos, finalizaciones y segmentos registrados. “En cola” cuenta alertas llegadas aún no iniciadas; “en propiedad” cuenta investigaciones iniciadas pero no finalizadas. La columna de trabajo restante solo suma trabajo residual de tareas ya asignadas. El motor no da servicio futuro realizado a alertas aún no asignadas, así que no se inventa ese esfuerzo pendiente. Los máximos son del muestreo indicado, no máximos instantáneos certificados.

| Tiempo | Interpretación | Cola L1 | L1 en propiedad | Residual registrado L1 | Cola L2 | L2 en propiedad | Residual registrado L2 |
|---:|---|---:|---:|---:|---:|---:|---:|
| 120 h | Inicio pulso, sábado 00:00 | 0 | 3 | 0.573 h | 1 | 0 | 0.171 h |
| 144 h | Fin pulso, domingo 00:00 | 41 | 5 | 12.458 h | 19 | 0 | 3.614 h |
| 168 h | Fin admisión, lunes 00:00 | 0 | 4 | 0.400 h | 22 | 0 | 4.052 h |
| 180 h | Lunes 12:00, drenaje | 0 | 3 | 0.350 h | 0 | 0 | 0 h |
| 204 h | Martes 12:00, drenaje | 0 | 0 | 0 h | 0 | 0 | 0 h |

La cola L1 alcanzó 41 sin iniciar al fin del pulso (46 trabajos incompletos, incluyendo 5 ya asignados). El trabajo L1 asociado a llegadas durante el pulso fue 35.738 h frente a 24 horas-persona disponibles en ese día: sobrecarga efectiva clara. Durante la recuperación dominical hubo 7.520 h de trabajo L1 nuevo; junto con el backlog, la utilización de la cobertura fue 81.6%, y al lunes 00:00 no quedaban alertas L1 sin iniciar. Unas pocas tareas aún asignadas acabaron durante el lunes/martes por sus turnos individuales. La evidencia apunta a un pulso que satura L1 y deja retrasos residuales, no a colapso permanente.

L2 no tiene horas disponibles sábado/domingo. Su cola pasó de 19 al comenzar domingo a 22 al cierre de admisión; incluía alertas de fin de semana y trabajos que llegaron tras el cierre del viernes. Tras la apertura del lunes a las 09:00, el volumen terminó de procesarse antes del muestreo de las 12:00. Esta cola es principalmente acumulación por falta de cobertura en las horas cerradas, no falta de horas-persona disponibles durante la jornada observada. Los deadlines, en cambio, siguieron corriendo.

## 6. Utilización y dimensión de la organización

La utilización por régimen se calcula como horas de trabajo en segmentos del motor divididas por horas-persona programadas disponibles en el mismo intervalo. Es ocupación realizada, no capacidad asignable LP ni utilización futura.

| Régimen | Nivel | Trabajo ejecutado | Horas-persona programadas | Utilización realizada |
|---|---|---:|---:|---:|
| Habitual (0–120 h) | L1 | 78.190 h | 120 h | 65.2% |
|  | L2 | 8.033 h | 120 h | 6.7% |
| Pulso (120–144 h) | L1 | 23.852 h | 24 h | 99.4% |
|  | L2 | 0 h | 0 h | No disponible |
| Recuperación (144–168 h) | L1 | 19.578 h | 24 h | 81.6% |
|  | L2 | 0 h | 0 h | No disponible |
| Drenaje (168–336 h) | L1 | 0.400 h | 168 h | 0.2% |
|  | L2 | 4.053 h | 120 h | 3.4% |

Por cohorte de llegada, el servicio L1 fue 78.762 h en habitual, 35.738 h en pulso y 7.520 h en recuperación. L2 recibió respectivamente 8.204 h, 3.443 h y 0.438 h de trabajo efectivo; los 21 casos L2 de fin de semana acumularon 3.881 h de servicio que no podía iniciarse entonces. La utilización del drenaje es baja porque la admisión acaba a 168 h y la mayoría del trabajo se termina pronto en el segundo lunes; no representa una semana adicional de demanda.

En el episodio semanal, los tres L2 consumieron 12.085 h de investigación frente a 120 horas contratadas (10.1%). Individualmente el trabajo asignado fue 4.589 h, 3.491 h y 4.005 h, frente a 40 h/persona-semana. El roster L2 parece **holgado respecto a la demanda semanal media configurada**. Reducir plantilla no resolvería por sí solo la imposibilidad de SLA causada por cierre nocturno/fines de semana, y podría estrechar la cobertura de clases: Top5, Next5 y Tail tienen dos especialistas elegibles cada una. Debe revisarse el dimensionamiento L2 antes de fijar V2 para una campaña, con análisis de cobertura por clase e intervalos; no concluir que sea óptimo o innecesario a partir de una sola traza.

L1 consumió 122.020 h en 200 horas-persona contratadas durante la semana (61.0%). La capacidad semanal media es razonable para el régimen habitual y la recuperación, pero el pulso ocupa prácticamente toda la cobertura efectiva y crea cola. Esta combinación evita un escenario permanentemente colapsado y sí produce congestión temporal relevante.

## 7. Interpretación científica de V2

- **Inviabilidad por tiempo activo:** no se observa en esta semilla (0/476). Los tiempos base no son por sí solos incompatibles con los SLAs.
- **Inviabilidad por calendario:** 35/476; todos son L2. Es una limitación contractual real del horario L2 8x5, no una anomalía que deba corregirse extendiendo el SLA.
- **Congestión/organización:** 106 alertas L1 cumplen la cota sin contención, pero fallan en ejecución. La carga del pulso L1 casi alcanza 100% de utilización, y hay espera prolongada; además hay 12 tareas suspendidas bajo asignación persistente. No se puede separar el efecto causal de la regla D1, orden de eventos, asignación a persona, cola y continuidad sin un contrafactual, que aquí no se ejecuta.
- **Recuperación:** el domingo usa 81.6% de las horas L1 disponibles y drena la cola no iniciada del pulso antes de acabar la admisión. Quedan algunos trabajos en propiedad hasta el lunes/martes. El sistema recupera, pero parte del SLA ya se perdió.
- **L2:** el bajo uso medio y los retrasos calendarizados coexisten. Más capacidad en horas cerradas no ayudaría si no se cambia el horario, decisión que este análisis no propone. La capacidad semanal media no describe la disponibilidad temporal.
- **No trivialidad y políticas:** existe tanto cumplimiento (335) como retraso estructural y no estructural. Las 106 alertas C muestran margen potencial para que asignaciones distintas cambien resultados, pero no prueban que D1, P1 o HLS-B difieran ni cuál sería mejor. Las 35 B no son susceptibles de mejora mediante una política de despacho que respete el mismo calendario y ruta.

## 8. Límites de registro y decisión sobre V2

Se dispone de primer comienzo, final, horas activas, suspensión, propietario, segmentos de trabajo, deadline y estado. No se registra un motivo de espera por evento ni una historia completa de longitud de cola/utilización en cada instante; el perfil de cola anterior se reconstruyó a partir de eventos observados y se muestreó cada 6 h. No hay resultado empírico de resolución correcta, clase de verdad externa, ni calendario real con festivos, zona horaria o DST. La categoría C usa el profesional elegible que ofrece la mejor cota calendarizada, no necesariamente el asignado ni un despacho alternativo ejecutado.

**Recomendación:** conservar V2 sin cambios como escenario diagnóstico/versionado y como prueba técnica reproducible. Antes de utilizarlo como organización central de una comparación de políticas, revisar específicamente la holgura L2 (10.1% de utilización semanal; composición de clases) y declarar si se acepta esa holgura como reserva contratada. Mantener como propiedad del escenario los SLAs naturales y el L2 8x5: los 35 retrasos calendarizados hacen visible una limitación estructural coherente, no justifican mover deadlines ni añadir guardias. Mantener también explícita la regla de propiedad persistente L1; las suspensiones de 12 trabajos hacen que el relevo entre profesionales sea una limitación conocida, no una función que este informe presuponga.

No se recomienda modificar el roster ni la demanda a partir de esta única semilla. Un eventual ajuste debe apoyarse en objetivo de dimensionamiento/cobertura por clase declarado y evidencia o análisis de sensibilidad separado, nunca en favorecer una política.

## 9. Reproducción de los datos por alerta

El CSV contiene una fila por alerta, con clase, severidad, ruta, tipo de confusión (solo evaluación), llegada, deadline absoluto, primer servicio, finalización, trabajo activo, espera pre-servicio, no-trabajo total, suspensión, profesional, estado, categoría A/B/C/D, holgura activa y finalización calendarizada de mejor caso. Horas relativas a lunes 00:00. `first_service_h` puede estar vacío solo si nunca comenzó; en esta ejecución no hay tales casos. Los rótulos ocultos se incluyen para auditoría ex post y no forman parte de la entrada del dispatcher.

La validación fue una reproducción fija y una igualdad determinista de dos pasadas del mismo episodio. No se ejecutaron pytest, campañas comparativas, regresiones masivas ni manuscritos; el simulador no se modificó. El informe no afirma validación empírica.
