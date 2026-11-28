# SOCTRA-HLS: modelo organizativo canónico

> **NEW MODEL / MODELO NUEVO:** este documento especifica la línea activa de triaje automático seguido por exactamente una investigación. Las campañas históricas y el manuscrito LaTeX pertenecen al **OLD MODEL / MODELO VIEJO**. Véase [MODEL_GENERATIONS.md](MODEL_GENERATIONS.md) para estado, evidencia, restricciones de comparabilidad y preguntas pendientes.

**Referencia CONOPS base congelada:** [SOC_NEW_MODEL_CONOPS_REFERENCE.json](config/SOC_NEW_MODEL_CONOPS_REFERENCE.json), con `triage_single_investigation`, D1 en L1, P1 en L2 y disponibilidad individual continua como idealización experimental, no como jornada laboral real. La variante de taxonomía empírica [SOC_NEW_MODEL_CONOPS_REFERENCE_SOCTRA_SEVERITY_V1.json](config/SOC_NEW_MODEL_CONOPS_REFERENCE_SOCTRA_SEVERITY_V1.json) y el diagnóstico de demanda/capacidad que sigue son fundamentación y análisis separados: no cambian la referencia base ni resultados. V2/V2_24X7 y sus pilotos, incluida la validación confirmatoria, permanecen intactos como evidencia obtenida bajo sus parámetros anteriores; no se reinterpretan con este CONOPS.

> **Modelo organizativo vigente (decisión científica):** una herramienta automática recomienda L1 o L2 al llegar cada alerta; su recomendación se acepta automáticamente y se ejecuta una única investigación en el nivel elegido. En la referencia CONOPS la complejidad q determina una referencia sintética de especialización mediante q0, calibrado a la prevalencia de la etiqueta estandarizada SOCTRA (`19/14.449`), que no es verdad objetiva de necesidad. La dificultad determina el esfuerzo W(q); la velocidad profesional V determina la duración T=W/V; competencia determina únicamente la calidad esperada modelada. La organización de referencia es 5 L1 heterogéneos y 3 L2 elegibles para todas las clases, con D1 en L1 y P1 en L2. La ejecución previa V2_24X7 y sus resultados permanecen congelados en sus propios supuestos.

## 1. Objetivo y alcance

Representar alertas como tareas que, tras triaje, reciben una única investigación en L1 o L2. Se estudia cómo clase, severidad, dificultad, eficiencia, competencia, elegibilidad, calendarios y organización se relacionan con carga y resultados. El escenario es sintético, generalizable como estructura a otros dominios y no reproduce ni valida los procedimientos de un SOC concreto. Los diagnósticos de viabilidad y capacidad son evaluaciones externas, no políticas.

## 2. Taxonomía y datos disponibles

Una alerta contiene llegada, clase/proyecto, severidad, dificultad individual q en [0,1], una etiqueta de referencia operativa sobre escalado y deadline contractual absoluto. La etiqueta de referencia procede conceptualmente de las etiquetas históricas de escalado usadas por SOCTRA. No existe verdad independiente para determinar si aquellas decisiones humanas eran óptimas; por tanto, prevalencia de esa etiqueta no equivale a prevalencia objetiva de necesidad de especialización. En trazas sintéticas puede representarse como `reference_escalation` oculta al dispatcher. El evaluador conoce etiquetas/dificultad; la política solo recibe información observable permitida.

Cada profesional tiene nivel, elegibilidad y competencia por clase. El recurso agrega servicio nominal individual, forecast y calendario. La eficiencia temporal está codificada en el servicio nominal; la competencia es una propiedad de calidad distinta. L1/L2 son etapas funcionalmente distintas: no se impone que L2 sea más competente ni necesariamente más lento para la misma clase.

Llegadas, capacidad nominal, capacidad asignable, carga relativa, colas, trabajo pendiente, utilización y esperas son medidas distintas. rho = tasa ofrecida / capacidad asignable describe presión media bajo una mezcla/regla dada; no garantiza estabilidad ni cumplimiento de plazos.

D1, P1, WAPS/HLS-B, clasificadores y recomendaciones SOCTRA no cambian. Las políticas solo reciben el forecast y otra información disponible antes de ejecución. Los sidecars de dificultad, necesidad y TP/FP se usan solo por el motor/evaluador.

## 3. Esfuerzo, velocidad y servicio

En el CONOPS vigente se separan explícitamente el esfuerzo de la tarea y la
velocidad del profesional:

\[
W(q)=1+\beta(q-0.5)\quad[\text{unidades de trabajo}],\qquad
V_{i,k}=\frac{1}{b_{l_i,k}u_{i,k}}\quad[\text{unidades de trabajo/h}],
\]
\[
T_{i,a}=\frac{W(q_a)}{V_{i,k_a}}
 =b_{l_i,k_a}u_{i,k_a}[1+\beta(q_a-0.5)]\quad[\text{horas activas}].
\]

`b` es el tiempo nominal por unidad de trabajo para nivel y proyecto; `u` es
un factor sintético inverso de velocidad individual por proyecto. Menor `u`
significa mayor velocidad. `W(q)` es estrictamente creciente si `beta>0` y
positivo para todo `q∈[0,1]` si `0≤beta<2`. La competencia no interviene en
`V`: es un atributo distinto que alimenta la calidad esperada modelada.
`forecast_service_by_class` es una expectativa ex ante condicionada a la ruta
pública y a los parámetros agregados; no revela la dificultad, referencia o
confusión individuales. El motor aplica a cada alerta el factor efectivo
`W(q_a)` exactamente una vez.

La dificultad es sintética `q~Beta(2,2)`; `E[q]=0.5` y por tanto
`E[W(q)]=1` antes del condicionamiento por ruta. No se ha calibrado con tiempos
humanos. En la referencia CONOPS `beta=1`; en V2 y en las campañas confirmatoria
y exploratorias previas `beta=0`, por lo que estas últimas no validan el efecto
temporal de dificultad. El documento [SERVICE_TIME_DIFFICULTY_MODEL.md](SERVICE_TIME_DIFFICULTY_MODEL.md)
describe la extensión general ya disponible.

Para evitar contar dos veces la complejidad, en CONOPS `alpha=1` y `gamma=1`:
FP L2 conserva el esfuerzo ordinario `W(q)` de su alerta y FN L1 ya tiene más
esfuerzo porque su `q` está en la cola compleja. No se multiplica de nuevo por
un factor de FP/FN. Los perfiles V2 previos usaron `alpha=0.50`, `beta=0` y
`gamma=1`; se conservan sin reinterpretación y sus resultados no se cambian.

## 4. Triaje, ruta y resultados TP/FP/TN/FN

El triaje es preliminar y distinto de investigar. En el escenario principal, una herramienta automática produce recomendación L1/L2 con latencia despreciable respecto a trabajo humano y sin consumo significativo de capacidad. Se acepta el 100% de sus recomendaciones: es una hipótesis explícita, no un comportamiento observado. El analista no contradice la recomendación en el modelo principal.

Sea `Y=1` la etiqueta de referencia de escalado y `R=1` la recomendación L2. La etiqueta Y no afirma necesidad objetiva verificada.

| Caso | Y | R | Ruta adoptada | Trabajo asignado |
|---|---:|---:|---|---|
| TP | 1 | 1 | Triaje → L2 | Una investigación especializada; uso necesario según referencia |
| FP | 0 | 1 | Triaje → L2 | Una investigación L2 para una tarea ordinaria; consume capacidad especializada. En CONOPS `alpha=1`; no se asume trivialidad |
| TN | 0 | 0 | Triaje → L1 | Una investigación L1 ordinaria |
| FN | 1 | 0 | Triaje → L1 | Una investigación L1 compleja, con mayor esfuerzo `W(q)` por `q≥q0`; no hay segunda investigación ni factor gamma adicional |

Las etiquetas son para evaluación y realización ambiental. D1/P1/HLS-B no observan Y, TP/FP/FN/TN, q realizado ni servicio efectivo. En el CONOPS la ruta de referencia coincide con `Y=1[q≥q0]`; los errores se generan al aplicar sensibilidad y FPR del clasificador a Y. Las políticas observan solo alertas en su cola de nivel, deadlines, elegibilidad y forecast público. La velocidad/competencia del analista tampoco determina la ruta.

No se modelan fallos de investigación, reintentos, reaperturas, escalado tardío, revisión humana de recomendación, retorno L2→L1 ni varias etapas de investigación. Una alerta finaliza cuando termina el servicio asignado, aunque el modelo no verifique que la conclusión sea correcta; es una simplificación deliberada, no una afirmación sobre todos los SOC. El triaje humano es una posible extensión que consumiría tiempo L1 anterior a la decisión de ruta; no forma parte del escenario principal.

## 5. SLA contractual y deadlines

El SLA es un compromiso contractual en tiempo natural desde llegada hasta la finalización de la investigación asignada. En el simulador ese evento es el cierre operativo de la alerta, pero no demuestra que la conclusión sea sustantivamente correcta. El deadline absoluto permanece invariable; el reloj avanza de noche, fin de semana, durante colas y suspensión. No existe pausa contractual, deadline por etapa, reinicio ni extensión automática.

El deadline absoluto es `d_a`; llegada `t_a`; finalización de investigación `t_fin,a`. La alerta cumple SLA si `t_fin,a ≤ d_a`, incumple si `t_fin,a > d_a`. Finalizar no equivale a cumplir. A la fecha de corte se distinguen: A) finalizada en SLA; B) finalizada fuera de SLA; C) pendiente. B y C no son resoluciones puntuales. B no se elimina al cruzar deadline: el servicio sigue hasta terminar o hasta el corte contable definido por el experimento. C conserva el trabajo pendiente y cuenta como no puntual al corte, sin afirmar fallo terminal si el horizonte no ha madurado.

El reloj natural empieza con la llegada y nunca se pausa durante triaje, colas, noches, fines de semana o suspensión por calendario; tampoco se reinicia por cambios organizativos. No se crearán deadlines por etapa ni extensiones automáticas. El horario del equipo es restricción interna, no excepción contractual.

Los offsets históricos alta 1 h, media 4 h y baja 12 h pertenecen a configuraciones/campañas históricas. Los 12/24/72 h del estudio de disponibilidad también son hipótesis de su campaña. Ninguno se proclama default universal: cada experimento declara su deadline sin cambiar retrospectivamente sus resultados.

Métricas: fracciones finalizada en SLA, finalizada fuera de SLA y pendiente al corte usan todas las alertas admitidas como denominador, con corte y criterio de admisión declarados; las tres categorías suman uno si son exhaustivas. Tiempo de respuesta se calcula solo para completadas como `t_fin−t_llegada` y se informa con su denominador; espera y trabajo/utilización son métricas distintas. Calidad esperada se mantiene separada y no se infiere de SLA.

**R/N histórico no se redefine.** No existe una única semántica común a todos los estudios llamados R/N. En los estudios organizativos HLS citados, el estimando es la suma por alertas admitidas de `competencia_terminal × (1−0.35×dificultad) × indicador(finalización terminal ≤ deadline y corte)`, dividida por el total admitido; pendientes aportan cero. Es una calidad esperada modelada y condicionada a puntualidad, no exactitud empírica. Otros runners antiguos usan `competencia` sin factor de dificultad, o endpoints de rutas específicas; cada informe conserva su fórmula y denominador. Para experimentos nuevos reportar por separado las tres fracciones de estado, SLA global y cualquier proxy de calidad definido explícitamente; no reutilizar el nombre R/N sin fijar su fórmula.

**Estado de las métricas:** los motores actuales ya exponen, según backend, completadas dentro del SLA, tardías, pendientes al corte, espera, respuesta, trabajo y utilización. El runner de disponibilidad agrega sus estados y métricas en el ejecutor de campaña; no existe aún un evaluador común que garantice denominadores idénticos entre motores. `S_+` y `legacy_RN` pertenecen a endpoints históricos con sus definiciones publicadas, no son sinónimos de la fracción global finalizada en SLA ni de corrección investigativa. Las tres fracciones A/B/C arriba son el esquema recomendado para nuevas evaluaciones; no implica que todos los runners ya las exporten con una API uniforme.

## 6. Perfil organizativo V1 (diagnóstico anterior)

Esta subsección registra el perfil diagnóstico anterior y no constituye el
roster del modelo adoptado. Conceptualmente, L1 representa profesionales
generalistas, generalmente más junior y de menor coste, con cobertura de equipo
24x7 por turnos individuales. L2 representa profesionales especialistas,
generalmente más senior, con coste horario superior y calendario individual
8x5 de lunes a viernes 09:00–17:00. Son roles funcionales sintéticos. No se
impone superioridad universal de L2 en competencia ni velocidad: la relación
depende de la persona y de la clase/trabajo. El coste no determina competencia
ni eficiencia.

### L1: cobertura 24x7 con roster individual

Cinco profesionales cubren 168 h/semana, turnos de ocho horas y una posición activa en cada intervalo. No significa que una persona trabaje 24x7.

| Profesional | Turnos en hora local | h/semana |
|---|---|---:|
| L1-01 | Lun 00–08; Mar 16–24; Jue 08–16; Sáb 00–08; Dom 16–24 | 40 |
| L1-02 | Lun 08–16; Mié 00–08; Jue 16–24; Sáb 08–16 | 32 |
| L1-03 | Lun 16–24; Mié 08–16; Vie 00–08; Sáb 16–24 | 32 |
| L1-04 | Mar 00–08; Mié 16–24; Vie 08–16; Dom 00–08 | 32 |
| L1-05 | Mar 08–16; Jue 00–08; Vie 16–24; Dom 08–16 | 32 |

La suma es 168 horas y cada intervalo semanal queda cubierto una vez. Esta mezcla de jornadas es hipótesis de roster, no convenio observado. Todos los L1 son elegibles para las tres clases para evitar huecos de cobertura por especialización; competencia y velocidad sí varían por profesional/clase. Vacaciones, descansos, pausas, festivos, ausencias, solapamientos y relevo requieren datos/roster validado.

### L2: especialistas 8x5

Tres especialistas trabajan cada uno lunes-viernes 09:00–17:00 local (40 h/persona, 120 h/semana). No hay guardias, horas extra ni atención fuera de horario.

| Profesional | Clases elegibles | Calendario |
|---|---|---|
| L2-01 | top5, next5 | Lun–Vie 09–17 |
| L2-02 | next5, tail | Lun–Vie 09–17 |
| L2-03 | top5, tail | Lun–Vie 09–17 |

Cada clase tiene dos L2 elegibles; cada persona atiende dos clases. La capacidad se calcula respetando las aristas de elegibilidad. No se impone superioridad de competencia de L2.

El reloj usa horas naturales con semana iniciada lunes 00:00 en hora local del escenario. La API usa calendarios semanales abstractos; no modela zona IANA ni cambios DST y V1 supone semanas fijas de 168 h. Suspender servicio por calendario conserva tarea y trabajo pendiente, pero no detiene el SLA. La propiedad del trabajo en la implementación actual permanece en el analista asignado; el relevo entre L1 al acabar un turno sigue pendiente y no se infiere de la cobertura 24x7.

## 7. Servicios nominales V1 (diagnóstico anterior)

Estos números fueron elegidos para el perfil secuencial anterior y no deben
reinterpretarse como servicios comparables de la única investigación L1 o L2
del modelo vigente. Se deberán revisar tras implementar su ruta.

Valores en horas activas por tarea; hipótesis sintéticas más cortas que la referencia histórica para dejar holgura activa sin forzar viabilidad por calendario:

| Nivel | top5 | next5 | tail |
|---|---:|---:|---:|
| Base L1 (h) | 0.08 | 0.10 | 0.12 |
| Base L2 (h) | 0.30 | 0.36 | 0.42 |

Factores u: L1-01 0.90, L1-02 1.00, L1-03 1.10, L1-04 0.95, L1-05 1.05; L2-01 0.95, L2-02 1.05, L2-03 1.00. JSON declara el producto exacto por profesional/clase. beta=0.

Servicios históricos L1 0.20/0.25/0.30 h y L2 0.75/0.90/1.00 h siguen en sus configuraciones. En V1 la ruta con mayor trabajo activo mínimo cabe en el deadline alto de 1 h; la factibilidad por servicio no garantiza cumplimiento real.

## 8. Demanda y dimensionamiento V1 (diagnóstico anterior)

V1 declara metadatos de diagnóstico, no un generador nuevo. Aunque el cargador preserva compatibilidad con la referencia al generador Q1, el perfil siguiente no altera sus trazas ni está conectado a ese runner. Una campaña futura debe integrar explícitamente las tasas con los mecanismos existentes y conservar aisladas las trazas históricas.

Mezclas hipotéticas: clase top5/next5/tail = 0.50/0.30/0.20; severidad alta/media/baja = 0.20/0.30/0.50. Cada segmento postula tasa Poisson estacionaria con proporciones constantes:

| Régimen (semana desde lunes 00) | Duración | Tasa total (top5 / next5 / tail) |
|---|---:|---:|
| Ordinario: Lun 00–Sáb 00 | 120 h | 2.5/h (1.25 / 0.75 / 0.50) |
| Pulso: Sáb 00–Dom 00 | 24 h | 15/h (7.50 / 4.50 / 3.00) |
| Recuperación: Dom 00–Lun 00 | 24 h | 1.5/h (0.75 / 0.45 / 0.30) |

El escenario fija prevalence 0.10 por clase, sensibilidad 0.8421, FPR 0.045, alpha 0.50 y beta 0. Los classifier operating points son catalogados históricamente, pero prevalencia, llegadas, mezcla y transferencia de operating point a otros dominios son supuestos. Probabilidad esperada de recomendación L2: 0.10×0.8421 + 0.90×0.045 = 0.12521. Cálculo ex ante supone independencia de dificultad respecto a clase, necesidad y recomendación; si hay correlación se requieren sidecars conjuntos de una traza.

La plantilla de cinco L1 y tres L2 se eligió para dejar capacidad media en carga ordinaria, una sobrecarga L1 en el pulso y presión L2 no colapsada en promedio semanal. No se igualan rho ni se infieren dimensiones óptimas de una sola carga agregada. Capacidad media L2 oculta que el equipo tiene capacidad instantánea cero de noche y fin de semana.

## 9. Capacidad asignable y carga V1 (diagnóstico anterior)

analyze_reference_organization.py reutiliza assess_capacity() y el LP existente effective_capacity(): máximo flujo común para una mezcla, respetando clase, elegibilidad, servicio individual y disponibilidad semanal fraccional. No suma productividades de analistas incompatibles.

| Régimen | Capacidad L1 alertas/h | tasa L1 | rho L1 | Capacidad L2 rutas/h | tasa L2 | rho L2 |
|---|---:|---:|---:|---:|---:|---:|
| Ordinario | 10.746 | 2.500 | 0.233 | 2.498 | 0.312 | 0.125 |
| Pulso sábado | 10.746 | 15.000 | 1.396 | 2.498 | 1.871 | 0.749 |
| Recuperación domingo | 10.746 | 1.500 | 0.140 | 2.498 | 0.187 | 0.075 |

Todos los cinco L1 y tres L2 son recursos vinculantes en el óptimo fluido y no hay clase sin elegibilidad. Las parejas elegibles de L2 comparten la restricción de mezcla. L2 usa tasa esperada de recomendaciones y servicio medio TP/FP ponderado por alpha. En el pulso L1 ofrece 1.410 horas-persona de trabajo por hora natural, superior a una hora-persona disponible: exceso fluido aproximado 9.84 horas en sábado. Domingo ofrece 0.141 h-persona/h y capacidad media para recuperación. No son colas observadas ni garantía de estabilidad.

Sábado y domingo implican 49.385 recomendaciones L2 esperadas y aproximadamente 14.08 h de servicio L2. L2 no trabaja entonces: el trabajo se acumula hasta lunes 09. Es carga entrante ex ante, no cola observada; L1 desplaza el instante real de llegada a L2.

## 10. Viabilidad temporal V1 (diagnóstico anterior)

analyze_reference_organization.py evalúa puntos medios cada 15 min durante una semana desde lunes 00, ponderados por mezcla de clase/severidad y probabilidades TP/FP. Es enumeración determinística discretizada, no traza ni experimento. Con beta=0, alpha=0.50:

| Diagnóstico ponderado | Alta 1 h | Media 4 h | Baja 12 h | Total |
|---|---:|---:|---:|---:|
| Intrínsecamente inviable por tiempo activo | 0% | 0% | 0% | 0% |
| Inviable por calendario sin colas | 9.36% | 8.25% | 5.28% | 6.98% |

La holgura optimista tiene mínimo 0.472 h y cuantiles p10/p50/p90 de 0.910/3.928/11.928 h. Con calendarios, el mínimo es −63.546 h y los cuantiles globales p10/p50/p90 son 0.886/3.924/11.920 h. En rutas L1+L2, 56.01% son no viables sin cola por calendario; en L1 sola, 0% en la cuadrícula. Un escalado nocturno, tardío del viernes o de fin de semana puede violar incluso el SLA corto aunque el trabajo activo combinado sea menor a una hora. Esta limitación estructural se conserva intencionalmente. La estimación depende de cuadrícula, anclaje semanal, composición y probabilidades; no es medición empírica. La cota de calendario elige el mejor profesional por etapa, sin contención por otras tareas.

Ejemplo: una alerta alta llegada sábado 23:45 tiene deadline domingo 00:45. El servicio mínimo activo L1+L2 es inferior a 1 h, pero con el calendario su finalización más temprana es lunes 09:17; el slack calendarizado es −32.535 h. El reloj SLA no se detiene durante el cierre de L2.

Clasificación: (1) inviabilidad intrínseca si T_min > deadline-arrival; (2) calendario si el caso es viable sin turnos pero la primera finalización calendarizada excede deadline; (3) congestión/disponibilidad/asignación si era viable sin cola y la ejecución concreta acaba tarde. Factibilidad es necesaria, no suficiente. Capacidad nominal aquí se refiere a plantilla/horas contratadas antes de restricciones de elegibilidad; capacidad asignable es la tasa del LP con servicios, mezcla y calendarios; capacidad utilizada solo se obtiene de una ejecución. El LP semanal no modela colas ni sincronía instantánea; carga relativa no garantiza SLA. La utilización del óptimo LP no es utilización observada. Recuperación usa colas/trabajo pendiente de traza y criterio configurable.

## 11. Coste V1 (hipótesis diagnóstica)

No hay evidencia salarial/coste empresarial. Coste normalizado configurable por hora contratada y profesional, heredado por nivel: cada L1=1.0, cada L2=1.8. La razón es hipótesis de coste superior de especialista, no salario observado. Plantilla/turnos: 168 h L1 y 120 h L2; coste semanal 168 + 1.8×120 = 384 unidades relativas. El coste contratado existe aunque haya poca ocupación; no se equipara al coste de tiempo usado. Ninguna política optimiza este coste.

## 12. Decisiones de diseño del perfil V1

| Decisión | Motivo | Alternativa descartada |
|---|---|---|
| SLA natural continuo y deadline original L1/L2 | compromiso end-to-end | Pausar, reiniciar o ampliar deadline |
| L1 por turnos, cobertura 24x7; L2 L-V 09–17 | separar cobertura y horario personal | Persona individual L1 24x7, guardia L2 |
| Servicio V1 más corto, beta 0 | hipótesis temporal con holgura activa | Cambiar servicios/deadlines históricos |
| 5 L1 y 3 L2 con elegibilidad explícita | presión no trivial con régimen regular y pulso | igualar rho o declarar óptimo desde un promedio |
| Coste relativo 1.8 | distinguir coste horario sin inventar salarios | coste de ocupado solamente |
| Demanda como metadato diagnóstico | evitar fingir que JSON ya la genera | generador paralelo o cambio de campañas |

## 13. Escenario organizativo ejecutable V2 8x5 (variante de disponibilidad)

V2 8x5 fue la configuración central para el diagnóstico anterior y permanece
como variante reproducible de disponibilidad. No sustituye ni reescribe V1, las
configuraciones históricas, los resultados publicados ni los runners de campañas. Se carga y ejecuta con:

```sh
python studies/soc_triage_hls_availability_robustness/run_scenario.py --config studies/soc_triage_hls_availability_robustness/config/SOC_REFERENCE_ORGANIZATION_V2.json --seed 998001
```

El JSON declara `flow_mode: triage_single_investigation`. `scenario_loader`
construye la entrada de `triage_execution.py`; el runner llama al
`CalendarBackend` existente. Se puede seleccionar explícitamente el modo
histórico mediante `--flow-mode historical_l1_then_l2`. Los ejecutores antiguos
no leen este selector y mantienen su comportamiento y configuración históricos.
El modo de una investigación también acepta una política explícita con
`--policy`, pero una ejecución individual no es una comparación de políticas.

### Generación reproducible y supuestos

V2 reutiliza `src/hls/ia_l1_l2_simulation.py::generate_alerts`; no incorpora un
segundo generador. El adaptador traduce los tres regímenes contiguos con mezcla
fija a las primitivas existentes: tasa Poisson base, pulso acotado y tasa de
recuperación posterior. El generador produce clase, severidad, dificultad
Beta(2,2), referencia oculta de escalado y recomendación Bernoulli. Se fija el
seed en la configuración y cada ejecución también acepta `--seed`. El adaptador
rechaza perfiles con mezcla cambiante o regímenes que las primitivas existentes
no pueden representar, en lugar de aproximarlos silenciosamente.

Todos los valores siguientes de llegada, mezcla y prevalencia son hipótesis
sintéticas. La mezcla por clase `(top5,next5,tail)` es `(0.50,0.30,0.20)`; la
mezcla por severidad `(alta,media,baja)` es `(0.20,0.30,0.50)`. Las tasas son
alertas por hora natural:

| Régimen | Intervalo h desde lunes 00:00 | Top5 | Next5 | Tail | Total |
|---|---:|---:|---:|---:|---:|
| Habitual | [0,120) | 1.25 | 0.75 | 0.50 | 2.50 |
| Pulso | [120,144) | 3.00 | 1.80 | 1.20 | 6.00 |
| Recuperación | [144,168) | 0.75 | 0.45 | 0.30 | 1.50 |

La referencia sintética oculta de escalado tiene prevalencia 0.10 por clase;
no se sustituye por la prevalencia SOCTRA del conjunto Q1 ni representa una
verdad objetiva de especialización. Las recomendaciones se generan con
`pD=0.8421`, `pFA=0.045` del punto LightGBM APC simétrico documentado en Q1.
Aplicar esas tasas como sorteos Bernoulli a esta prevalencia sintética no
equivale a ejecutar el clasificador sobre cada alerta ni valida su calibración
en un SOC. La dificultad Beta(2,2) es independiente de clase y referencia.
Parámetros de V2: `beta=0`, `alpha=0.50`, `gamma=1.0`; la recomendación se
acepta siempre (100%, regla fija y no un parámetro). La necesidad etiquetada
sirve como referencia operativa sintética, no como verdad empírica.

### Servicios y equipo

Los servicios representan únicamente investigación de la única etapa asignada;
no incluyen triaje automático. Servicio nominal base en horas de trabajo:

| Clase | Base L1 | Base L2 | Interpretación sintética |
|---|---:|---:|---|
| Top5 | 0.25 h | 0.18 h | L2 puede ser más rápido en esta especialidad |
| Next5 | 0.30 h | 0.25 h | L2 puede ser más rápido en esta especialidad |
| Tail | 0.40 h | 0.55 h | L2 no es universalmente más rápido |

El servicio individual es `base(level,class) × u(analista,class)`; V2 conserva
los factores heterogéneos u de V1. El forecast L1 coincide con ese nominal
(beta=0, gamma=1). Para una recomendación positiva, el forecast L2 aplica el
factor ex ante
`E[m | recomendado L2] = [pi*pD + (1-pi)*pFA*alpha] / [pi*pD + (1-pi)*pFA]`
con `pi=0.10`, `pD=0.8421`, `pFA=0.045`, `alpha=0.50`, que da **0.837623**.
Así incorpora el promedio esperado de TP/FP sin revelar la etiqueta ni el
tiempo realizado de una alerta. Los servicios V2 son hipótesis centrales para
que el trabajo activo mínimo
quepa en deadlines sintéticos y las colas/calendarios puedan causar tardanza;
no son mediciones. L2-01 es elegible para Top5/Next5, L2-02 para Next5/Tail y
L2-03 para Top5/Tail. Cada uno tiene competencia elevada en sus focos y no hay
dominancia individual universal.

L1 conserva cinco calendarios rotatorios que cubren las 168 horas semanales con
exactamente un profesional disponible en cada intervalo; cada persona tiene
32–40 horas programadas. L2 conserva tres especialistas con 40 horas cada uno,
lunes a viernes 09:00–17:00. Son 120 horas-persona L2 contratadas por semana,
pero solo 40 horas naturales cubiertas; no hay guardias. Gamma se mantiene
neutro porque no hay evidencia para justificar un valor mayor que uno.
Deadlines: alta 1 h, media 4 h, baja 12 h naturales. Admisión: 168 h; corte de
evaluación: 336 h. Alpha afecta solo FP recomendados a L2; gamma solo FN
enrutados a L1; beta ajusta servicio efectivo por dificultad. Ningún factor
detiene ni reinicia el SLA.

### Capacidad y factibilidad V2

`analyze_reference_organization.py` reutiliza el LP de capacidad asignable con
elegibilidad, servicios individuales y fracciones de calendario, enroutando
ex ante negativos a L1 y positivos a L2. L1 recibe TN/FN; L2 recibe TP/FP. Con
beta cero, el factor esperado de dificultad es uno. El LP es una cota fluida
por régimen, no simula colas ni disponibilidad en instantes concretos:

| Régimen | Nivel | Capacidad asignable alertas/h naturales | Tasa ofrecida alertas/h | Carga relativa | Trabajo ofrecido h-persona/h | Diagnóstico |
|---|---|---:|---:|---:|---:|---|
| Habitual | L1 | 3.424 | 2.188 | 0.639 | 0.646 | Capacidad media suficiente |
| Habitual | L2 | 3.106 | 0.312 | 0.100 | 0.072 | Capacidad media suficiente |
| Pulso | L1 | 3.424 | 5.252 | 1.534 | 1.549 | Sobrecarga estructural del régimen |
| Pulso | L2 | 3.106 | 0.748 | 0.241 | 0.173 | Capacidad media suficiente |
| Recuperación | L1 | 3.424 | 1.313 | 0.383 | 0.387 | Capacidad media suficiente; margen para drenar |
| Recuperación | L2 | 3.106 | 0.187 | 0.060 | 0.043 | Capacidad media suficiente |

El pulso genera presión superior a la capacidad media de L1; la recuperación
ofrece margen medio para reducir cola. Las cargas no se igualan entre niveles.
La carga L2 media oculta que el equipo no opera por la noche ni fin de semana:
solo hay cobertura 40 horas naturales. Una integración determinista de 15
minutos estima **47.39 recomendaciones L2 y 10.94 horas de trabajo especializado
ofrecidas fuera de cobertura por semana** (24.94 alertas/5.76 h en habitual,
17.96/4.14 h en el pulso, 4.49/1.04 h en recuperación). Son llegadas/trabajo
acumulables antes de reabrir, no una cola simulada ni una espera individual.

La viabilidad temporal enumera puntos medios cada 15 minutos de la semana y
pondera clase, severidad y los cuatro resultados de clasificación. Evalúa rutas
directas: TP L2, FP alpha-L2, TN L1 y FN gamma-L1, sin colas y con dificultad
media 0.5:

- Inviabilidad por servicio activo mínimo: **0.00%** en esta enumeración.
- Inviabilidad calendarizada ponderada sobre todas las alertas: **6.92%**.
- Entre las rutas a L2, **55.47%** es inviable por calendario; principalmente
  por llegadas fuera de 8×5 con SLA corto.

Son resultados diagnósticos del perfil sintético, no garantías de SLA. La
factibilidad sin cola es necesaria, no suficiente; la enumeración calendarizada
representa una mejor asignación individual, no despacho ni congestión. No se
ajustan deadlines para evitar los incumplimientos fuera del horario L2.

### Coste y ejecución técnica reproducible

Se mantienen costes horarios normalizados L1=1.0 y L2=1.8 unidades por hora,
como razón hipotética no salarial. En V2 8x5, la metadata anterior daba 168
unidades L1, 216 L2 y 384 total por horas contratadas del roster. Estos importes
no se trasladan a disponibilidad 24x7: la variante conserva las tarifas
relativas, pero no modela plantilla, salarios ni coste real de tener a cada
profesional disponible 168 h/semana. No interpretar el coste semanal heredado
como coste de V2_24X7.

Una ejecución técnica con seed `998001`, configuración D1 individual y
`CalendarBackend` generó **476** alertas: TP=35, FP=28, TN=405, FN=8; 413 se
enrutaron a L1 y 63 a L2. Las 476 recibieron una investigación; 335 finalizaron
dentro de SLA, 141 tarde y 0 quedaron pendientes al corte 336 h. Es una prueba
técnica reproducible, no una campaña, estimación científica ni comparación
D1/P1/WAPS. No atribuye mejoras a ninguna política.

### Validación diagnóstica del episodio V2

La reproducción técnica de seed `998001` está documentada en [SOC_REFERENCE_V2_DIAGNOSTIC_VALIDATION.md](SOC_REFERENCE_V2_DIAGNOSTIC_VALIDATION.md), con detalle por alerta en su CSV anexo. Reprodujo 476 alertas y 335 puntuales, 141 tardías y ninguna pendiente. En la ruta recomendada y con las realizaciones efectivas, 35 retrasos fueron inviables por calendario L2 aun sin colas y 106 rutas L1 eran viables bajo la mejor cota sin contención pero tardías en la ejecución. El episodio evidencia saturación temporal L1 en el pulso y holgura semanal L2; no identifica efectos causales de política. Es diagnóstico de una única semilla, no campaña ni validación empírica.

## 13 bis. Configuración histórica V2_24X7 (disponibilidad individual continua)

La variante [`SOC_REFERENCE_ORGANIZATION_V2_24X7.json`](config/SOC_REFERENCE_ORGANIZATION_V2_24X7.json)
parte de V2 y cambia **solo el campo `calendar` de cada analista** a
`{"kind":"continuous"}`. Profesionales, clase, elegibilidad, competencia,
eficiencia, servicios, mezclas, severidades, parámetros alpha/beta/gamma,
clasificador, deadlines, tasas, regímenes y semilla permanecen idénticos. El
identificador y la referencia descriptiva del roster se heredan como procedencia;
la disponibilidad operativa la determinan los ocho campos `calendar`. Al citar
una corrida identificar siempre el archivo JSON y su hash/commit.

Esta fue la configuración base de los pilotos registrados a continuación; ya
no es la configuración organizativa de referencia actual:
triaje automático, una investigación directa por alerta y todos los L1/L2
individualmente disponibles todo el tiempo. Es una idealización deliberada
para eliminar cierres de calendario como mecanismo de espera/suspensión y
recuperar la simplificación de disponibilidad continua de los estudios
originales. No representa turnos reales, guardias ni relevos; no implica que
personas trabajen 24x7. No se cambian SLA ni demanda.

Ejecución y diagnóstico reutilizables:

```sh
python studies/soc_triage_hls_availability_robustness/run_scenario.py --config studies/soc_triage_hls_availability_robustness/config/SOC_REFERENCE_ORGANIZATION_V2_24X7.json --seed 998001
python studies/soc_triage_hls_availability_robustness/analyze_reference_organization.py --config studies/soc_triage_hls_availability_robustness/config/SOC_REFERENCE_ORGANIZATION_V2_24X7.json
```

El análisis comparativo técnico de la semilla 998001 y los diagnósticos por
régimen están en
[`SOC_REFERENCE_V2_24X7_VALIDATION.md`](SOC_REFERENCE_V2_24X7_VALIDATION.md).
La capacidad de las dos plantillas crece porque los calendarios pasan a
168 h/profesional/semana: L1 de 168 a 840 horas-persona/semana (×5), L2 de 120
a 504 (×4.2). Por tanto, la comparación V2/V2_24X7 elimina restricciones de
calendario **y aumenta capacidad disponible**; no es un efecto aislado de
quitar suspensiones. No se reescala la demanda para recuperar rho anterior.

La integración conserva el LP de capacidad, la cota de viabilidad y los
motores de calendario; con calendario continuo, la inviabilidad por cierre
desaparece, pero siguen existiendo carga, heterogeneidad y la posibilidad de
congestión bajo otra tasa. La semilla de control no muestra presión alta:
rho máximo esperado en el pulso = 0.308 para L1 y 0.057 para L2. En esa única
traza todas las 476 alertas cumplen; esto no valida el SLA ni demuestra que las
políticas producirán diferencias bajo esta carga. La V2 8x5 y su diagnóstico
se conservan como variante para una fase posterior sobre disponibilidad.

Las tarifas horarias relativas L1=1.0 y L2=1.8 permanecen como metadata
hipotética. `contracted_hours_per_week` conserva los valores heredados V2 y no
es válido para calcular coste de una organización 24x7. Tampoco se transforma
la idealización en coste laboral real.

## 13 ter. Perfil de carga para congestión y recuperación

La variante [`SOC_REFERENCE_V2_24X7_LOAD_REGIMES.json`](config/SOC_REFERENCE_V2_24X7_LOAD_REGIMES.json) conserva íntegra la organización V2_24X7 y cambia las tasas temporales a ρ_L1 objetivo 0.85/1.25/0.65 en ventanas de 96/24/48 h. Las tasas totales derivadas del LP son 16.542/24.327/12.650 alertas por hora; se ajustan por la fracción esperada L1=0.87529, no se equiparan a μ_L1=17.0346. La semilla 998001 produjo 2,812 alertas, 69 tardías y ninguna pendiente; la cola L1 alcanzó 122 alertas al final del pulso y se drenó durante la recuperación. Detalle, tasas por nivel, uso y criterio explícito de recuperación: [SOC_REFERENCE_V2_24X7_LOAD_REGIMES_VALIDATION.md](SOC_REFERENCE_V2_24X7_LOAD_REGIMES_VALIDATION.md). Es una sola ejecución diagnóstica, no validación estadística ni comparación de políticas.

## 13 quater. Piloto comparativo de políticas

Se ejecutó un piloto exploratorio emparejado de D1, P1 y HLS-B/WAPS sobre la configuración temporal anterior, con 10 semillas nuevas y 30 episodios. Las trazas y realizaciones ambientales coinciden por semilla; el R/N medio fue 0.7844/0.7753/0.7821, respectivamente, mientras la fracción puntual fue 97.56%/100%/99.69%. Las diferencias son exploratorias: no establecen superioridad ni cambian políticas o parámetros. El procedimiento, diferencias emparejadas, resultados por cohorte/subgrupo, transiciones de HLS-B, límites y JSON reproducible están en [SOC_REFERENCE_V2_24X7_POLICY_PILOT.md](SOC_REFERENCE_V2_24X7_POLICY_PILOT.md); los 30 registros y hashes están en [SOC_REFERENCE_V2_24X7_POLICY_PILOT_RESULTS.json](SOC_REFERENCE_V2_24X7_POLICY_PILOT_RESULTS.json). El runner es [run_policy_pilot.py](run_policy_pilot.py).

El postproceso de las mismas diez semillas por cohorte de llegada, con diferencias emparejadas e incertidumbre descriptiva, está en [SOC_NEW_MODEL_POLICY_COHORT_ANALYSIS.md](SOC_NEW_MODEL_POLICY_COHORT_ANALYSIS.md). No implica ejecuciones nuevas ni atribución causal de los patrones locales.

El piloto exploratorio prefijado de intensidad y duración de sobrecarga (cuatro perfiles, doce semillas emparejadas por perfil, 144 episodios) está documentado en [SOC_NEW_MODEL_OVERLOAD_INTENSITY_PILOT.md](SOC_NEW_MODEL_OVERLOAD_INTENSITY_PILOT.md), con [resultados por ejecución](SOC_NEW_MODEL_OVERLOAD_INTENSITY_RESULTS.json), [runner](run_overload_intensity_pilot.py) y [perfiles A–D](config/SOC_NEW_MODEL_OVERLOAD_PROFILE_A.json). Sus resultados son del NEW MODEL y no constituyen validación confirmatoria.

## 13 quinquies. Validación confirmatoria del perfil D

La hipótesis exploratoria de ventaja de HLS-B frente a ambas políticas fijas en el perfil D se sometió a una validación independiente y preespecificada con 60 semillas nuevas (180 episodios). R/N medio fue 0.63200 (D1), 0.63583 (P1) y 0.64049 (HLS-B); los contrastes HLS-B−D1=+0.008483, IC95% [+0.006775,+0.010190], y HLS-B−P1=+0.004656, IC95% [+0.004237,+0.005075], superaron conjuntamente la prueba de intersección-unión preespecificada con α=0.05. La conclusión se limita al perfil D sintético: no demuestra superioridad en cada régimen ni generalización universal, y no valida empíricamente el SOC, la calidad proxy ni los servicios. Se conservaron `alpha=0.50`, `beta=0` y `gamma=1`; beta y gamma son neutros en estos experimentos y sus efectos no han sido validados. El [protocolo](SOC_NEW_MODEL_PROFILE_D_CONFIRMATORY_PROTOCOL.md), [informe completo](SOC_NEW_MODEL_PROFILE_D_CONFIRMATORY_VALIDATION.md), [análisis estadístico](SOC_NEW_MODEL_PROFILE_D_CONFIRMATORY_ANALYSIS.json) y [registros](SOC_NEW_MODEL_PROFILE_D_CONFIRMATORY_RESULTS.json) conservan el diseño y la evidencia.

## 14. Compatibilidad y alcance de conclusiones históricas

La configuración V1, las configuraciones históricas, los ejecutores de campaña,
los motores, algoritmos, clasificadores, resultados y manuscritos permanecen
intactos. V2 y V2_24X7 conectan generación, flujo y backend para una ejecución
reproducible individual; V2_24X7 fue la base experimental sin cierres de
calendario de los pilotos consignados arriba. Los JSON históricos sin `flow_mode` cargan
`historical_l1_then_l2`; los ejecutores históricos no se redirigen al escenario
nuevo. Los runners de V2 conservan su configuración y valores predeterminados;
el diagnóstico CONOPS nuevo usa explícitamente su JSON versionado.

**Propiedades matemáticas:** normalización E[f]=1 bajo Beta(2,2); mínimos de
servicio y LP condicionado a entradas. **Hipótesis:** roster, competencias,
eficiencia, Beta, prevalencia, tasas, mezcla, alpha, coste y ausencia DST.
**Calculado:** capacidad fluida y factibilidad calendarizada discretizada para
V1, V2 8x5 y V2_24X7. Las verificaciones iniciales de V2_24X7 fueron controles
técnicos de una semilla; después se ejecutaron un piloto exploratorio y una
validación confirmatoria independiente, ambos documentados en las secciones
13 quater y 13 quinquies. La validación confirmatoria respalda la hipótesis
conjunta en el perfil D, condicionada al escenario sintético; no extiende la
conclusión a otros perfiles ni cambia el estado de la evidencia OLD MODEL.

V2 8x5 refleja que una alerta L2 fuera de turno puede incumplir un SLA corto
aunque su servicio activo quepa en el plazo. V2_24X7 elimina esa restricción en
la base experimental, pero multiplica las horas disponibles y reduce rho; no es
una comparación de calendario manteniendo capacidad constante. No se puede concluir estabilidad general, SLA real, costes reales, superioridad
de política ni mejoras de rendimiento.
Se necesitarían datos operativos representativos y experimentos futuros
preespecificados.

## 15. Archivos y referencias

- Referencia organizativa CONOPS vigente: config/SOC_NEW_MODEL_CONOPS_REFERENCE.json.
- Diagnóstico CONOPS reproducible: diagnose_new_model_conops.py y results/soc_new_model_conops/seed_2026112801.json.
- Base experimental histórica de carga baja: config/SOC_REFERENCE_ORGANIZATION_V2_24X7.json.
- Perfil temporal congestionado: config/SOC_REFERENCE_V2_24X7_LOAD_REGIMES.json.
- Variante disponibilidad L1 24x7/L2 8x5: config/SOC_REFERENCE_ORGANIZATION_V2.json.
- JSON diagnóstico anterior: config/SOC_REFERENCE_ORGANIZATION_V1.json.
- Ejecución técnica: run_scenario.py --seed 998001 (base); elegir JSON explícito para otros perfiles.
- Diagnóstico de carga/recuperación: analyze_load_regimes.py; reporte SOC_REFERENCE_V2_24X7_LOAD_REGIMES_VALIDATION.md.
- Diagnóstico: analyze_reference_organization.py.
- Interfaces: scenario_loader.py, execution_api.py, triage_execution.py, availability_engine.py; usage in EXECUTION_API.md.
- Viabilidad/capacidad: scenario_diagnostics.py y SCENARIO_FEASIBILITY_DIAGNOSTICS.md; LP en studies/soc_human_ai_organization/calibrate_a1_scenarios.py::effective_capacity.
- Servicio: SERVICE_TIME_DIFFICULTY_MODEL.md.
- Tests: tests/test_scenario_loader.py, tests/test_scenario_diagnostics.py, tests/test_execution_api.py, tests/test_triage_execution.py, tests/test_scenario_integration.py.
- Evidencia previa: studies/soc_human_ai_organization/ y studies/soc_triage_hls_q1_integration_evidence/.
- Métricas históricas: [auditoría final Q1](../soc_triage_hls_q1_integration_evidence/AUDIT_FINAL.md) y [comparación organizativa](../soc_human_ai_organization/SOC_POLICY_COMPARISON_RESULTS.md) preservan definiciones/denominadores de R/N propios de esos estudios.
- Generaciones científicas: [OLD MODEL / NEW MODEL](MODEL_GENERATIONS.md) identifica el manuscrito, evidencia histórica, configuraciones nuevas y límites de comparabilidad.
- Índices: README raíz y README de estudio enlazan este documento. LaTeX no se modifica.

Pendiente: (1) roster real con descansos, ausencias, festivos y relevos; (2) servicio medido por nivel/clase y asociación duración-calidad; (3) llegadas, mezcla y pulsos observados; (4) prevalence/need y errores clasificador por clase/dificultad; (5) costes autorizados para reemplazar 1.8; (6) horizonte de medición que no convierta tardanza en cumplimiento; (7) decidir si el calendario semanal abstracto requiere zona horaria, DST y fechas reales.

## 16. Estado de implementación, decisiones y cuestiones abiertas

### Modelo vigente frente a la implementación

| Elemento | Decisión/modelo científico vigente | Estado en el código auditado |
|---|---|---|
| Fuente de referencia para TP/FP/TN/FN | Dificultad q, con referencia Y=1[q≥q0]; q0 reproduce prevalencia estandarizada 19/14449 | `generate_alerts` genera q y referencia; loader verifica Beta(2,2), q0 y prevalencia; Y sigue siendo etiqueta de proceso, no verdad objetiva |
| Triaje principal | Automático, latencia despreciable, recomendación aceptada en 100% | `triage_execution.py` recibe las recomendaciones ya generadas y acepta la ruta; no simula latencia de clasificador |
| Generación CONOPS | Llegadas de Poisson homogéneas con intensidad media de registros como escala; clase/severidad independientes y sintéticas | JSON versionado, `scenario_loader.generate_trace` y `generate_alerts`; no representa el patrón horario empírico ni la asociación real entre atributos |
| Ruta | TP/FP van directamente a investigación L2; TN/FN a investigación L1 | JSON y `run_scenario.py` integrados con `triage_execution`; los runners históricos conservan L1 antes de L2 |
| Número de investigaciones | Una investigación por alerta en el nivel recomendado | V2 ejecutable asigna una etapa; el modo histórico preserva las etapas antiguas |
| FP L2 | Investigación de alerta ordinaria, con trabajo W(q); no trivialidad impuesta | CONOPS fija alpha=1; mantiene una sola escala de esfuerzo por complejidad |
| FN L1 | q≥q0 implica trabajo mayor por W(q), sin investigación secundaria | CONOPS fija gamma=1 y beta=1; no hay factor gamma adicional ni segunda investigación |
| SLA | Deadline absoluto y tiempo natural; finalización puntual, tardía o pendiente al corte | API clasifica los tres estados; nuevo runner los agrega; métricas históricas conservan sus definiciones |
| Calidad | Proxy separado; no exactitud validada | Competencia/proxies existen, pero no hay outcome adjudicado de resolución correcta |
| Calendarios | Disponibilidad individual continua de L1/L2 para aislar políticas en este diagnóstico | JSON CONOPS usa calendario `continuous`; V2 con L2 8x5 y V2_24X7 permanecen reproducibles |

V1 y sus resultados diagnósticos permanecen como perfil anterior. V2 8x5,
V2_24X7 y su validación seed 998001 se conservan intactos como evidencia de la
configuración anterior. El CONOPS nuevo es la referencia diagnóstica actual;
los pilotos V2 no se reinterpretan con él. Todos los valores organizativos
nuevos son hipótesis sintéticas y la disponibilidad individual continua es una
idealización.

### Qué está implementado, qué falta y qué se excluye

**Implementado/reutilizable:** perfiles de servicio y competencia por
profesional/clase; elegibilidad; dificultad q; beta como factor de esfuerzo;
alpha/gamma todavía disponibles para perfiles anteriores; generación de
recomendaciones y etiquetas ocultas; colas/calendarios/suspensión; deadline
natural; métricas de estado, trabajo y SLA. `triage_execution.py` ejecuta
flujo nuevo o histórico con los backends existentes.

**Integrado para ejecución técnica por escenario:**
`triage_execution.run_triage_flow(..., flow_mode="triage_single_investigation")`
envía cada alerta a la cola de un único nivel. El loader JSON conserva el
generador y ejecutor existentes, permite perfiles de eficiencia derivados de
`b·u`, y acepta `reference_escalation_difficulty_threshold`: cuando existe,
`Y=1[q≥q0]`; cuando se omite, se mantiene el generador de etiqueta previo para
compatibilidad. La prueba del CONOPS selecciona explícitamente D1 en L1 y P1
en L2. Los ejecutores históricos conservan el modo
`historical_l1_then_l2`. Los dispatchers
reciben forecasts y metadatos públicos, no etiqueta de referencia, confusión,
necesidad oculta, q realizada ni multiplicadores efectivos. Ninguna política
ni motor fue reescrito. El forecast solo contiene valores esperados de
duración por clase/ruta. En CONOPS beta=1 interviene una vez en duración,
alpha=gamma=1 son neutrales. El nuevo umbral reutiliza la extracción aleatoria
que ya existía para Y; al omitirlo, el camino histórico de generación sigue
igual.

**Descartado del estudio principal:** decisión humana de contradecir la
recomendación, escalado tardío, reintento, reapertura, retorno L2→L1 y múltiples
etapas. El triaje humano queda como extensión distinta con tiempo propio previo
a la investigación.

**Validación focalizada previa a V2_24X7:** `pytest -q studies/soc_triage_hls_availability_robustness/tests`
aprobó 90 pruebas en el commit anterior. Para V2_24X7 se ejecutaron 64 pruebas
focalizadas de loader, integración, orquestación y API; todas pasaron. Cubren ambos modos, rutas TP/FP/TN/FN, alpha/beta/gamma,
aislamiento de etiquetas, estados SLA, calendarios, suspensión, deadline,
generación JSON reproducible, capacidad y viabilidad de ruta única, selección
histórica y ausencia de streams aleatorios añadidos por el orquestador. Las ejecuciones técnicas V2/V2_24X7 verificaron integración end-to-end. No se ejecutaron campañas ni
la regresión masiva y no se compararon todos los resultados históricos bit a bit.

### Decisiones consolidadas

- Triaje e investigación son actividades diferentes; en el escenario principal
  el triaje es automático y de latencia despreciable.
- La recomendación inicial se acepta sin revisión humana y determina el único
  nivel que investiga.
- TP/FP/TN/FN se miden respecto a la etiqueta histórica de escalado usada como
  referencia operativa; no llamarla ground truth objetivo.
- FP L2 consume capacidad con investigación de complejidad ordinaria; el
  CONOPS fija alpha=1 para evitar un segundo ajuste del esfuerzo.
- FN L1 entra en la cola de complejidad q y exige más trabajo por beta=1; el
  CONOPS fija gamma=1 para evitar contabilizar de nuevo el mismo efecto.
- La referencia CONOPS usa disponibilidad individual continua 24x7 como
  idealización, no como jornada real. V2 8x5 y V2_24X7 siguen disponibles como
  versiones históricas. El SLA siempre corre en tiempo natural.
- Coste, competencia y velocidad son dimensiones separadas. Perfiles pueden
  favorecer L2 en clases concretas sin imponer superioridad universal.
- Finalización, puntualidad contractual y calidad esperada son resultados
  diferentes; no se afirma exactitud empírica.

### Decisiones todavía abiertas

1. Evidencia empírica para el vínculo entre q y esfuerzo, la velocidad por
   proyecto y la adecuación de beta=1; los valores actuales son hipótesis.
2. Relevo de trabajo L1 entre profesionales al cerrar turno; la continuidad
   actual de propiedad no debe confundirse con cobertura del equipo.
3. Calibración del coste relativo, los perfiles de servicio/competencia y la
   mezcla de tareas con datos autorizados.
4. Si una extensión futura de revisión humana tendrá coste/latencia propios.
5. Fechas, festivos, zona horaria y DST para calendarios no semanales.
6. Instrumento de calidad: outcome adjudicado o proxy definido. Hasta entonces
   no interpretar competencia como probabilidad observada de corrección.

### Versiones y documentos científicos

El material de campaña anterior sigue siendo evidencia histórica de la versión
implementada entonces. Sus cifras, parámetros y denominadores no se reescriben.
Cada informe histórico debe marcar de forma visible su flujo antiguo y enlazar
esta fuente canónica. Los documentos de modelo/arquitectura pueden describir
interfaces existentes, pero no presentar el flujo anterior como la
organización vigente. El documento canónico es la fuente única para las
decisiones organizativas actuales; los textos secundarios solo amplían su
implementación o registran metodología/resultados históricos.

## 17. CONOPS vigente y diagnóstico organizativo inicial

### Especificación operativa

La referencia ejecutable histórica es
[`config/SOC_NEW_MODEL_CONOPS_REFERENCE.json`](config/SOC_NEW_MODEL_CONOPS_REFERENCE.json)
y se conserva sin cambios, junto a sus resultados. La nueva versión con
severidad empírica es
[`config/SOC_NEW_MODEL_CONOPS_REFERENCE_SOCTRA_SEVERITY_V1.json`](config/SOC_NEW_MODEL_CONOPS_REFERENCE_SOCTRA_SEVERITY_V1.json);
ambas se cargan con el mismo loader y generador. Esta actualización fundamenta
la mezcla marginal de severidad, no constituye una campaña ni reemplaza
resultados históricos.
El flujo es triaje automático de latencia despreciable, recomendación aceptada
sin revisión y **una investigación única**: TP/FP se envían directamente a L2;
TN/FN, directamente a L1. No hay transferencia ni investigación L1 previa a
una ruta L2. Se usa el `CalendarBackend` existente y calendarios individuales
continuos en ambos niveles, una idealización de disponibilidad, no una jornada
laboral.

Las dimensiones de alerta se separan conceptualmente. Proyecto determina la
cartera; `q` es complejidad intrínseca en [0,1] y determina esfuerzo. En la
versión histórica, severidades `high/medium/low` y sus plazos pertenecen a la
hipótesis sintética original. La versión SOCTRA usa `critical/high/medium` y
las proporciones empíricas exactas 21.937/156.981, 87.545/156.981 y
47.499/156.981, respectivamente. Sus plazos de resolución son hipótesis del
simulador: critical 1 h, high 4 h, medium 12 h; no son SLA reales de GMV-CERT.
El dato SOCTRA `incumplimiento_sla` denota asignación inicial tardía, mientras
el simulador mide finalización de investigación. No se usa aquel indicador
para calibrar estos plazos.

En ambas versiones, clase/proyecto, severidad y dificultad se muestrean
independientemente. Para la versión SOCTRA, independencia severidad-complejidad
es una simplificación experimental, no una propiedad demostrada por los datos.
La variación empírica de severidad entre proyectos y periodos queda pendiente
de incorporarse al generador. Las prevalencias estandarizadas de escalado por
severidad (critical 137/21.937, high 237/87.545, medium 196/47.499) se registran
en configuración para estudios posteriores; no cambian `q0` ni el clasificador.
La distribución marginal no condiciona la severidad al escalado ni a `q`.

La referencia sintética de especialización se define como `Y=1[q≥q0]`, con
`q~Beta(2,2)`. En vez de introducir la prevalencia previa arbitraria de 10%,
`q0=0.9789151127185249` se obtiene resolviendo
`P(q≥q0)=(1−q0)^2(1+2q0)=19/14449=0.0013149699`. El numerador 19 es la
prevalencia auditada/artículo-implied de etiquetas positivas del conjunto de
prueba **estandarizado** después de la definición contrafactual usada por esa
fuente; se escoge esta versión porque el punto de clasificador fijado también
es el estandarizado. La evidencia está en
[`SIMULATOR_SPECIFICATION.md`](../soc_triage_hls_q1_integration_evidence/SIMULATOR_SPECIFICATION.md),
[`AUDIT_REPORT.md`](../soc_triage_hls_q1_integration_evidence/AUDIT_REPORT.md)
y [`primary_campaign.json`](../soc_triage_hls_q1_integration_evidence/config/primary_campaign.json).
La etiqueta histórica es proxy de proceso, no verdad objetiva de necesidad L2;
`q` no se presenta como complejidad medida. La prevalencia de complejidad en
este escenario coincide matemáticamente con la prevalencia proxy por
construcción, no por validación empírica.

El clasificador usa `pD=0.8421` y `pFA=0.045`, fijos del punto standardized
LightGBM. Por ello la proporción que se recomienda a L2 es
`πpD+(1−π)pFA=0.04604816` (4.6048%), mientras la referencia Y=1 es 0.1315%.
La diferencia se debe a las falsas alarmas, no a que q0 se haya calibrado a
4.6%. La simulación genera errores Bernoulli sintéticos condicionales a Y; los
valores publicados no aportan numeradores/denominadores por modelo para
cuantificar incertidumbre y se tratan como entradas fijas. No se atribuye
validez operativa a esa transferencia.

### Esfuerzo, velocidad y calidad

Para proyecto `k` y analista `i`,
`W(q)=1+β(q−0.5)` unidades de trabajo,
`V(i,k)=1/[b(level,k)·u(i,k)]` unidades/hora, y
`T(i,a)=W(q_a)/V(i,k_a)=b(level,k)u(i,k)[1+β(q_a−0.5)]` horas activas.
El factor `u` representa velocidad y no se deduce de competencia. La
competencia individual afecta al proxy de calidad, no al tiempo. En CONOPS
`β=1`, por lo que el factor de esfuerzo va de 0.5 a 1.5 y crece linealmente
con `q`; todas las duraciones son positivas. `alpha=gamma=1`: FP L2 conserva
su esfuerzo W(q), y FN L1 requiere más esfuerzo porque `q≥q0`; no se vuelve a
multiplicar por complejidad. Así se evita contarla dos veces. Estos valores son
hipótesis sintéticas, no calibraciones de servicio humano. El resultado de
calidad `competencia·(1−0.35q)` es un proxy definido por el simulador, no una
probabilidad observada de resolución correcta.

### Organización y supuestos congelados

La configuración usa tres proyectos existentes (`portfolio_top5`,
`portfolio_next5`, `portfolio_tail`), sin añadir tipos técnicos. La mezcla
0.50/0.30/0.20, la mezcla de severidad alta/media/baja 0.20/0.30/0.50, su
independencia y el punto de clasificador aplicado por clase son hipótesis
sintéticas.

| Elemento | L1 | L2 |
|---|---:|---:|
| Profesionales | 5 | 3 |
| Asignación | D1 | P1 |
| Calendario individual | Continuo 24x7, idealización | Continuo 24x7, idealización |
| Elegibilidad | Heterogénea; hay nulos/ineligibilidad individual; toda clase está cubierta | Todos elegibles para todos los proyectos |
| Competencia | 0.64–0.83; heterogénea por persona/proyecto | 0.90–0.93; mayor y relativamente homogénea |
| Tiempo nominal `b` (h/unidad de trabajo) | top5 0.25; next5 0.30; tail 0.40 | top5 0.18; next5 0.22; tail 0.30 |

Los factores individuales `u`, elegibilidad y competencia exactos están en el
JSON. Todos los valores son hipótesis. El roster proporciona cobertura de
todas las clases en L1 y L2; no se ha ajustado para maximizar el desempeño de
una política. L2 es más veloz que L1 para la misma clase según estos perfiles,
pero puede acumular más tiempo total porque la ruta contiene alertas de mayor
complejidad.

### Demanda y método del diagnóstico

La referencia aplica una llegada Poisson estacionaria total de `9.0125
alertas/h` (=216.3 registros/día dividido por 24) durante 168 h, y drenaje
hasta 336 h. El promedio diario de 216.3 procede del resumen agregado
SOCTRA ([`docs/RESEARCH.md`](../../docs/RESEARCH.md),
[`SOC_FOUNDATIONS_AND_MODEL.md`](../soc_human_ai_organization/SOC_FOUNDATIONS_AND_MODEL.md));
es solo escala de volumen. El extracto incluye 214,739 IDs en 993 fechas y
presenta variabilidad diaria/interllegadas incompatible con un Poisson
homogéneo simple. La tasa constante horaria es por tanto una simplificación
del diagnóstico, no una reproducción del proceso real. Mezclas y falta de
asociación horaria son sintéticas.

El análisis reutiliza `scenario_loader.generate_trace`,
`ia_l1_l2_simulation.generate_alerts`, `triage_execution.run_triage_flow`,
`CalendarBackend` y el LP de elegibilidad/servicio en
`scenario_diagnostics.assess_capacity`. No altera políticas ni la realización
de la simulación. La carga ex ante del LP usa las distribuciones condicionales
Beta(2,2) truncadas por q0, tasas fijas del clasificador y servicio efectivo
esperado. La traza post hoc conserva campos ocultos solo para evaluación.
`diagnose_new_model_conops.py` y su salida versionada permiten repetir la
misma semilla:

```sh
python studies/soc_triage_hls_availability_robustness/diagnose_new_model_conops.py \
  --seed 2026112801 \
  --output studies/soc_triage_hls_availability_robustness/results/soc_new_model_conops/seed_2026112801.json
```

La ejecución es una sola prueba técnica, no un estudio de prestaciones ni una
comparación de políticas.

SHA-256 del JSON de escenario: `1ac1603e69832f9ce607750a7e4d455a67333b66e2ba4345a9d0ae8ed68794e9`.
SHA-256 de la traza exógena generada: `59e4a2db548c3b613d9d3a16484c969845003361af1d1a319ff6882c9cf2a736`.

### Diagnóstico técnico, semilla 2026112801

La configuración y traza están hasheadas en el JSON de resultados. El control
generó 1,435 alertas en 168 h (8.5417/h observado frente a 9.0125/h esperado):
TP=1, FP=58, TN=1,376, FN=0. Se asignaron 1,376 investigaciones L1 y 59 L2;
cada alerta tuvo exactamente una. La cola de complejidad `q≥q0` tuvo 1 alerta
(0.0697% de la muestra), frente a 0.1315% esperado; la diferencia es variación
de una muestra y no motivo para recalibrar q0.

**Distribución observada por cartera y severidad** (conteo de alertas):

| Grupo | L1 | L2 | Total |
|---|---:|---:|---:|
| top5 | 715 | 30 | 745 |
| next5 | 415 | 19 | 434 |
| tail | 246 | 10 | 256 |
| Alta | 257 | 8 | 265 |
| Media | 420 | 23 | 443 |
| Baja | 699 | 28 | 727 |

**Resultados por nivel** (h de servicio activo; esperas en horas):

| Nivel/política | Alertas (tasa observada/h) | Trabajo ofrecido ex ante (h-persona/h) | Capacidad LP asignable (alertas/h) | rho LP | Utilización observada | Servicio total (h) | Servicio medio (h) | Espera media (h) | SLA puntual/tarde/pendiente |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| L1 / D1 | 1,376 (8.1905) | 2.5849 | 17.0881 | 0.5031 | 48.96% | 411.578 | 0.2991 | 0.00781 | 1,376 / 0 / 0 |
| L2 / P1 | 59 (0.3512) | 0.09063 | 13.9859 | 0.02967 | 2.55% | 12.841 | 0.2176 | 0 | 59 / 0 / 0 |

El LP respeta clases, elegibilidad, heterogeneidad, calendario (168 h por
analista/semana) y servicio esperado. Las horas disponibles durante admisión
son 840 L1-persona-h y 504 L2-persona-h; la oferta esperada consume
aproximadamente 51.7% y 3.02%, respectivamente. `rho` del LP es tasa de ruta
dividida por capacidad asignable y no equivale exactamente a utilización por
hora-persona (por discretización/capacidad fluida y perfiles de trabajo); se
reportan ambas.

| Utilización individual durante las 168 h de admisión | Valor |
|---|---:|
| L1-01 | 45.64% |
| L1-02 | 44.59% |
| L1-03 | 45.02% |
| L1-04 | 54.09% |
| L1-05 | 55.46% |
| L2-01 | 6.74% |
| L2-02 | 0.90% |
| L2-03 | 0.00% |

La causa cuantitativa de la infrautilización L2 es la baja prevalencia de la
etiqueta de referencia combinada con `pFA=4.5%`: se esperan 0.415 alertas/h a
L2, solo 4.60% de llegadas. La capacidad L2 estimada es cerca de 33.7 veces la
tasa de ruta esperada; la utilización observada del episodio fue 2.55%. L2 no
se congestiona. L1 recibe la mayor parte del tráfico, pero con una carga de
trabajo esperada menor que la capacidad de sus cinco profesionales. Todos los
analistas resultan vinculantes en el óptimo fluido por la asignación común de
la mezcla, aunque no significa que trabajen al límite.

**Confusión y ruta observadas:**

| Caso | n | Ruta | Espera media (h) | Servicio medio (h) | Calidad modelada media |
|---|---:|---|---:|---:|---:|
| TP | 1 | L2 | 0 | 0.2724 | 0.5967 |
| FP | 58 | L2 | 0 | 0.2167 | 0.7461 |
| TN | 1,376 | L1 | 0.00781 | 0.2991 | 0.6183 |
| FN | 0 | L1 | — | — | — |

No observar FN en esta realización no prueba que no ocurran. Bajo el modelo,
si se realiza FN, su `q≥q0` aumenta el esfuerzo en L1; `gamma=1` no añade
ningún esfuerzo aparte.

**Colas, tiempos y SLA:** el servicio total fue 424.419 h-persona; la respuesta
media global 0.3033 h y espera media 0.00749 h (aprox. 27 segundos). La cola
L1 muestreada cada 15 min alcanzó 3 alertas y un máximo estimado de trabajo
residual 1.456 h; L2 tuvo cola de espera cero y máximo residual durante
servicios de 0.377 h. En los límites de régimen muestreados (96, 120 y 168 h),
el residual fue <0.53 h en L1 y <0.21 h en L2; al corte 336 h no quedaba
trabajo. La estimación de residual incluye servicio efectivo registrado para
alertas iniciadas y forecast mínimo elegible para quienes esperaban; no es una
métrica exacta del orden completo de trabajo pendiente. El tamaño de cola es
exacto en instantes muestreados, pero puede perder picos entre muestras.

Cumplieron SLA 1,435/1,435; 0 tardías y 0 pendientes. Cumplieron 265/265
alertas altas, 443/443 medias y 727/727 bajas. Todas las clases y niveles
tuvieron 100% puntual en esta muestra. La dificultad compleja tuvo q cercano
a 0.984 y el resto media q≈0.504; la duración media fue 0.248 h en top5,
0.308 h en next5 y 0.414 h en tail. Por ello, la ejecución no proporciona
evidencia de incumplimientos ni de congestión sostenida bajo esta intensidad.

### Lectura y límites

Este primer episodio muestra un escenario operativo no trivial en composición
y heterogeneidad, pero **no genera presión suficiente para estudiar
congestión**: D1 tiene utilización observada cercana a la mitad y P1 en L2
está muy infrautilizada. Los breves episodios de cola L1 son variación local y
no causan SLA tardíos. La baja asignación L2 deriva principalmente del
umbral/prevalencia baja (19/14,449) y del clasificador con FPR 0.045, no de la
plantilla. No debe aumentarse q0, alterar el roster o modificar servicios a
partir de una semilla para producir congestión; cualquier cambio requiere una
pregunta científica y protocolo separados.

El valor de 216.3/día es un agregado de registros, no de esfuerzo útil; la
distribución Poisson homogénea ignora variabilidad empírica, interllegadas,
horario y correlaciones. La proporción de L2 y el patrón de cola dependen
fuertemente de la referencia sintética y de los errores supuestos del
clasificador. Los perfiles `b`, `u`, competencia, `beta=1`, mezclas y calidad
son hipótesis no calibradas. La etiqueta de escalado no demuestra necesidad
objetiva y la calidad no es tasa medida de resolución correcta. Una semilla no
estima incertidumbre de operación ni compara políticas. El SLA de este control
solo comprueba consistencia lógica de deadlines en la muestra.

**Decisiones consolidadas por este diagnóstico:** el JSON CONOPS, no V2, es la
referencia organizativa actual; se elige la prevalencia standardized disponible
para calibrar q0 y no el 10% previo; complejidad afecta esfuerzo solo una vez;
D1 se fija en L1 y P1 en L2 para el diagnóstico. **Pendiente:** validar
asociaciones conjuntas y servicio/calidad con datos autorizados, justificar el
uso de un proceso Poisson frente a llegadas empíricas, y definir una pregunta
posterior que explique la infrautilización L2 antes de cambiar plantilla o
caudal. Los resultados de los pilotos y confirmación V2 anteriores siguen
intactos y solo describen sus configuraciones originales.

## 18. Diagnóstico exploratorio de dimensionamiento humano

### Diseño y reproducibilidad

El análisis de plantillas conserva sin cambio el CONOPS de la sección 17, la
demanda absoluta `9.0125 alertas/h`, q0, clasificador, mezclas, W(q), perfiles,
competencias, SLA, calendarios y flujo. Se mantienen D1 en L1 y P1 en L2; no
hay transferencias. Se usaron 12 semillas emparejadas nuevas
(`2026120101`–`2026120112`), con una traza exógena por semilla reutilizada
literalmente en las nueve plantillas. La traza incluye llegada, proyecto,
severidad, q, referencia, recomendación y deadline. Hay 9 configuraciones ×
12 episodios = 108 episodios únicos. Los hashes por semilla están en el
resultado JSON.

La configuración y la regla explícita de selección de perfiles están en
[`config/SOC_NEW_MODEL_STAFFING_SIZING.json`](config/SOC_NEW_MODEL_STAFFING_SIZING.json);
el ejecutor reutiliza el generador, motor, políticas y LP existentes en
[`run_staffing_sizing.py`](run_staffing_sizing.py). Resultados detallados por
episodio, analista, severidad, colas y eventos tardíos:
[`results/soc_new_model_staffing_sizing.json`](results/soc_new_model_staffing_sizing.json).
La huella de la organización de referencia V2-CONOPS es
`1ac1603e69832f9ce607750a7e4d455a67333b66e2ba4345a9d0ae8ed68794e9`; el hash
de la configuración de dimensionamiento es
`2504af71f00b2a3ecf3b97c4788a8f2f4f8ccb02e2edb51d4cbf464031a2cbce`.
Reproducción:

```sh
python studies/soc_triage_hls_availability_robustness/run_staffing_sizing.py \
  --output studies/soc_triage_hls_availability_robustness/results/soc_new_model_staffing_sizing.json
```

Las alternativas L1 son anidadas: 5 conserva todos; 4 excluye L1-03; 3
conserva L1-01/L1-04/L1-05. L1-04 y L1-05 aseguran cobertura de las tres
clases en las reducciones; no se presupone que sustituyan las velocidades y
competencias de quienes salen. L2 compara los tres actuales, L2-01/L2-02 y
solo L2-01; todos son elegibles para todas las clases. Retener L2-01 en los
subconjuntos produce una comparación anidada, no una afirmación de que ese
perfil sea intercambiable con L2-02/03. La alternativa L2-1 es un límite de
capacidad dentro de la idealización continua, no una propuesta real de una
persona cubriendo una operación 24x7.

### Llegadas, rutas y capacidad asignable ex ante

En 12 episodios se admitieron en promedio 1.513,17 alertas por episodio
(rango 1.442–1.577; 9,007 alertas/h observadas frente a 9,0125/h configuradas).
Las tasas analíticas de ruta esperadas son 8,5975 L1/h y 0,4150 L2/h. La
realización común tuvo, acumulada sobre 18.158 alertas, TP=19, FP=837,
TN=17.299 y FN=3; 856 (4,71%) fueron a L2 y 97,78% de esas recomendaciones
fueron FP. Por episodio, los promedios fueron TP=1,58, FP=69,75, TN=1.441,58
y FN=0,25. Así, con el q0/prevalencia adoptados, el tamaño de la plantilla L2
no es el factor que limita su demanda: la etiqueta de referencia es muy rara y
la mayoría de la ruta positiva procede del FPR fijo. La baja cuenta de TP
implica incertidumbre considerable sobre demanda de trabajo especializado;
12 semillas no estiman con precisión la cola de eventos raros.

El LP fluido existente considera proporciones de clases en cada ruta,
elegibilidad, servicio individual por clase y calendario continuo. Maximiza la
tasa común de alertas asignables, no multiplica personas por una productividad
media. La columna de horas de trabajo ofrecido usa la convención existente de
servicio medio entre analistas elegibles por clase; se presenta aparte de la
capacidad LP y de la utilización observada bajo D1/P1. La utilización analítica
de horas-persona divide ese trabajo ofrecido por `n` horas-persona/h, porque
cada profesional se supone disponible continuamente.

| Equipo | n | Tasa de ruta (alertas/h) | Trabajo ofrecido (h-persona/h) | Horas-persona disponibles/h | Fracción de horas ocupadas ex ante | Capacidad LP asignable (alertas/h) | ρ LP |
|---|---:|---:|---:|---:|---:|---:|---:|
| L1 | 5 | 8,5975 | 2,5849 | 5 | 51,70% | 17,0881 | 0,5031 |
| L1 | 4 | 8,5975 | 2,5593 | 4 | 63,98% | 13,7989 | 0,6231 |
| L1 | 3 | 8,5975 | 2,5342 | 3 | 84,47% | 10,5688 | 0,8135 |
| L2 | 3 | 0,4150 | 0,09063 | 3 | 3,02% | 13,9859 | 0,0297 |
| L2 | 2 | 0,4150 | 0,09061 | 2 | 4,53% | 9,2764 | 0,0447 |
| L2 | 1 | 0,4150 | 0,09038 | 1 | 9,04% | 4,5917 | 0,0904 |

Todas las alternativas mantienen elegibilidad para cada proyecto; no aparece
una clase descubierta. Todas las personas retenidas son restricciones activas
del LP a su máximo asignable para esa mezcla, pero eso describe el punto de
capacidad máxima, no su utilización en la demanda configurada. La diferencia
entre horas-persona ocupadas y rho LP es esperable: uno usa servicio promedio
entre elegibles y el otro optimiza una asignación fraccional por velocidad y
elegibilidad. Ambas son referencias fluidas, no garantías de plazo.

### Ejecución emparejada por plantillas

Media ± desviación estándar entre las 12 semillas; utilización observada se
calcula como trabajo activo durante las 168 h de admisión dividido por las
horas-persona disponibles. El cumplimiento SLA agrupa la ruta indicada; la
tabla por severidad separa los retrasos. Espera/servicio/respuesta se expresan
en horas.

| L1 roster | Utilización L1 | SLA L1 | Servicio medio | Espera media (p90) | Respuesta media | Calidad proxy completadas | Retrasos medios/episodio | Cola L1 máx media (peor) |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| L1-5 actual | 51,26% ± 1,45 pp | 100,00% | 0,2990 | 0,0135 (0,0412) | 0,3126 | 0,6192 | 0 | 4,25 (7) |
| L1-4 sin L1-03 | 63,32% ± 1,84 pp | 99,982% | 0,2956 | 0,0459 (0,1573) | 0,3414 | 0,6280 | 0,25 | 6,25 (8) |
| L1-3 sin L1-02/03 | 82,97% ± 2,40 pp | 99,625% | 0,2908 | 0,2015 (0,4797) | 0,4923 | 0,6454 | 5,42 | 11,25 (16) |

| L2 roster | Utilización L2 | SLA L2 | Servicio medio | Espera media (p90) | Respuesta media | Calidad proxy completadas | Retrasos/pendientes |
|---|---:|---:|---:|---:|---:|---:|---:|
| L2-3 actual | 3,12% ± 0,32 pp | 100% | 0,2202 | 0 | 0,2202 | 0,7478 | 0 / 0 |
| L2-2 sin L2-03 | 4,67% ± 0,47 pp | 100% | 0,2202 | <0,0001 | 0,2202 | 0,7478 | 0 / 0 |
| L2-1 solo L2-01 | 9,34% ± 0,95 pp | 100% | 0,2201 | 0,0109 | 0,2311 | 0,7475 | 0 / 0 |

La utilización individual media en L1-5 fue L1-01 48,9%, L1-02 45,0%,
L1-03 49,6%, L1-04 55,8% y L1-05 57,1%. En L1-4 fue 60,6%, 55,4%, 68,1%
y 69,2% para L1-01/02/04/05; en L1-3 fue 77,4%, 84,9% y 86,6% para
L1-01/04/05. L2-3 utilizó 8,6%, 0,7% y 0,0%; L2-2, 8,6% y 0,7%; L2-1,
9,3%. Los perfiles no son intercambiables: la reducción L1 elimina dos
analistas relativamente menos competentes en parte de las clases, y sube el
proxy medio de calidad; al mismo tiempo sube espera y baja puntualidad. Esta
subida del proxy no es una mejora causada por menor plantilla, sino un efecto
de la composición seleccionada y de la asignación D1. No se interpreta como
calidad empírica.

### SLA, congestión y explicación de los retrasos

No hubo alertas pendientes al corte en ninguna de las 108 ejecuciones. L2
cumplió 100% en alta/media/baja para las tres plantillas. En L1, la tasa
puntual por severidad fue:

| L1 roster | Alta (deadline 1 h) | Media (4 h) | Baja (12 h) | Retrasos totales en 12 episodios |
|---|---:|---:|---:|---:|
| 5 | 100% | 100% | 100% | 0 |
| 4 | 99,91% | 100% | 100% | 3 |
| 3 | 98,08% | 100% | 100% | 65 |

Los 68 incumplimientos observados fueron alertas L1 de severidad alta,
clase tail/next5 y confusión TN. Todas tenían servicio activo inferior a 1 h
y `q<q0`; sin cola habrían sido temporalmente viables. En L1-4 las tres
tardías tuvieron en promedio 0,552 h de espera y 0,541 h de servicio (respuesta
1,094 h). En L1-3, 65 tardías promediaron 0,678 h de espera y 0,448 h de
servicio (respuesta 1,125 h). Por tanto, en esta traza son retrasos por
congestión/espera que interactúa con la cola de servicio de tareas tail y el
SLA corto, no inviabilidad intrínseca ni cierre de calendario. No se atribuye
el contrafactual de que otra política hubiera evitado esos eventos.

La cola máxima L1 muestreada cada 15 minutos creció desde 7 alertas en L1-5,
a 8 en L1-4 y 16 en L1-3; el promedio entre episodios de la cola máxima fue
4,25/6,25/11,25. Son colas reales de la ejecución, no capacidad estructural.
L2 tuvo cola de espera nula en todas las trazas salvo la configuración de un
analista, donde el máximo fue una alerta y el SLA siguió cumpliéndose. El
agregado temporal completo se conserva en el JSON; colas entre instantes de
muestreo pueden tener picos no registrados.

### Conclusión de dimensionamiento y alcance

**L1:** cinco perfiles no saturan la demanda (≈51% utilización), pero dan
holgura y no mostraron retrasos en estas semillas. Cuatro perfiles seleccionados
proporcionan un punto intermedio (≈63%, con 3 incumplimientos altos de 17.300
alertas L1). Tres perfiles acercan el equipo a 83% y revelan congestión
temporal, esperas mayores y 65 incumplimientos altos. Cuatro L1 es una
alternativa exploratoria defendible para una ocupación media más alta sin
retirar toda holgura; cinco es preferible si la prioridad única es reducir
retrasos observados. No hay una meta de utilización prefijada ni evidencia
suficiente para declarar ninguna plantilla óptima.

**L2:** con la demanda actual, incluso un analista all-class tiene capacidad
LP ≈11 veces superior a la tasa de ruta y uso simulado ≈9%; dos y tres caen a
≈4,7% y ≈3,1%. Por capacidad pura no se justifica la plantilla actual de tres;
sin embargo, tampoco puede recomendarse operativamente un único especialista:
la hipótesis 24x7 supone una disponibilidad imposible de atribuir a una persona
real y el simulador no modela ausencias, relevos, turnos, redundancia ni
continuidad del servicio. No hay evidencia en este modelo para convertir la
ocupación baja en un requisito de contratación concreto. Para justificar una
plantilla real harían falta calendarios/roster operativos y requisito de
cobertura/continuidad; no se debe inflar prevalencia o falsos positivos para
llenar capacidad.

La parte determinada por demanda es el número de alertas, mezcla, tasa de
recomendación y, por tanto, trabajo por nivel. La capacidad asignable depende
de la elegibilidad, plantilla y velocidades sintéticas `b·u`; la duración
realizada depende además de q y beta. Las competencias alteran el proxy de
calidad, no la velocidad. Con q0 bajo en prevalencia, D1/P1 no se enfrentan a
un balance L1/L2 donde un ratio global sea muy informativo: sí es útil para
describir uso de recursos bajo esta hipótesis, pero no para recomendar un
ratio real ni estudiar sensibilidad a prevalencia. Cambiar prevalencia,
servicios o flujo queda fuera de este diagnóstico.

Este estudio es exploratorio de dimensionamiento, con 12 semillas y demanda
Poisson sintética estacionaria. Sus niveles de servicio, ocupaciones y calidad
proxy no son datos de operación ni permiten inferencia confirmatoria. La
configuración CONOPS de referencia permanece en 5 L1/3 L2; estas variantes no
la sustituyen automáticamente. Las campañas confirmatorias anteriores,
OLD MODEL, políticas y LaTeX permanecen sin cambios.

## 19. Caracterización empírica de demanda y viabilidad L1/L2

Este diagnóstico usa el CSV SOCTRA de septiembre de 2025 (214.739 registros),
el Parquet canónico procesado (156.981 registros) y el Parquet de febrero.
Los IDs emparejan las 156.981 filas retenidas; 57.758 registros fuente no
están en la población procesada. Los códigos de proyecto del análisis son
anónimos, ordenados por volumen y no representan clientes. La herramienta
reproducible es
[`analyze_soctra_demand_capacity.py`](analyze_soctra_demand_capacity.py): lee
los datos locales existentes, imprime agregados anonimizados, no regenera
Parquet y no llama al simulador.

### 19.1 Registros, intensidad y patrón temporal

| Intervalo calendario | Media | DE | Mediana | P90 | P95 | Máximo | CV |
|---|---:|---:|---:|---:|---:|---:|---:|
| Hora | 9,02 | 7,39 | 7 | 18 | 23 | 161 | 0,82 |
| Día | 216,25 | 89,84 | 211 | 334,8 | 379 | 574 | 0,42 |
| Semana ISO | 1.501,7 | 379,3 | 1.514 | 1.962 | 2.105,6 | 2.553 | 0,25 |
| Mes | 6.315,9 | 1.597,8 | 6.833 | 8.011,5 | 8.071,7 | 8.463 | 0,25 |

La cobertura va de 2022-12-31 a 2025-09-18. Diciembre de 2022 contiene un
registro y septiembre de 2025 es parcial. La población procesada suma 6,59
registros/h, frente a 9,02/h en la fuente completa. Los máximos de ventanas
móviles solapadas son 161 registros/1 h, 288/6 h, 690/24 h y 2.668/7 días;
no son réplicas independientes. Las horas 08–11 aportan 5,95–6,33 % de los
registros cada una, frente a 2,30–3,33 % en 00–05. Por día de semana hay
258,8–262,3 registros/día lunes-martes, alrededor de 251–252 miércoles-jueves,
218,2 viernes y 133,9–137,7 en fin de semana. Los timestamps no incluyen zona
horaria y no identifican turnos locales ni disponibilidad humana.

Los cinco proyectos más voluminosos contienen 59,2 % de la fuente, los cinco
siguientes 23,6 % y la cola 17,2 %. En el procesado, usando el ranking propio
de esa población, los grupos representan 59,4 %, 27,5 % y 13,1 %. No coincide
exactamente con la mezcla sintética 50/30/20. Proyecto no se equipara a cliente
ni los grupos a habilidades.

Estos son registros, no mediciones de investigaciones humanas, asignaciones,
eventos de trabajo o FTE. Por ello 9,02 registros/h no se presenta como
investigaciones/h sin declarar un factor de conversión `κ` (investigaciones
por registro), que SOCTRA no identifica. El cálculo de carga escala linealmente
con κ; κ=1 es únicamente el supuesto del escenario.

### 19.2 Asociación proyecto, severidad y escalado

Proyecto-severidad tiene Cramér V=0,429 en la fuente y 0,308 en el procesado.
La relación proyecto-etiqueta varía según la etiqueta observada:

| Población / etiqueta | V proyecto×etiqueta | V severidad×etiqueta |
|---|---:|---:|
| Fuente `escalada_L2` | 0,034 | 0,024 |
| Fuente `escalada_procedimiento` | 0,228 | 0,010 |
| Procesado L2 original | 0,024 | 0,028 |
| Procesado procedimiento corregido | 0,268 | 0,017 |
| Procesado combinada pre-estandarización | 0,137 | 0,030 |
| Procesado estandarizada | 0,178 | 0,020 |

Dentro de las severidades procesadas, la asociación proyecto×etiqueta
estandarizada persiste: V=0,501 critical, 0,136 high y 0,343 medium. Los
rangos de prevalencia por proyecto-severidad del script excluyen celdas con
N<100. Hay variación temporal: entre meses con al menos 500 filas, la tasa
estandarizada mensual va de 0,016 % (agosto 2025) a 1,339 % (septiembre 2023).
Estos efectos son descriptivos, no causales; los valores p pequeños no miden
importancia práctica. La distribución de demanda debe conservar periodo,
proyecto y severidad como covariables conjuntas para estudiar esta variación.

| Población procesada | N | L2 original | Procedimiento original | Procedimiento corregido | Combinada pre-estand. | Estandarizada |
|---|---:|---:|---:|---:|---:|---:|
| Septiembre global | 156.981 | 444 (0,2828 %) | 152 (0,0968 %) | 154 (0,0981 %) | 582 (0,3707 %) | 570 (0,3631 %) |
| Febrero test | 14.449 | 33 (0,2284 %) | 7 (0,0484 %) | 7 (0,0484 %) | 40 (0,2768 %) | 19 (0,1315 %) |

La prevalencia estandarizada global de septiembre es 2,76 veces la del test de
febrero. Son snapshots y poblaciones distintas; no es una comparación pareada
ni una tasa constante. `19/14.449` pertenece al test de febrero.

El script imprime las tablas detalladas por proyecto anonimizado de: conteos
de severidad, prevalencias históricas y estandarizadas y retención de filas,
así como prevalencias por mes de L2, procedimiento original/corregido,
combinada y estandarizada. No se conserva en documentación una tabla de
correspondencia con los nombres originales.

### 19.3 Capacidad analítica, servicio y SLA

Se conservan D1 en L1, P1 en L2, una investigación por alerta recomendada,
sin transferencia ni balance, taxonomía critical/high/medium y plazos
sintéticos de resolución 1/4/12 h. También se mantienen `q~Beta(2,2)`, q0,
clasificador, W(q), competencias, velocidades y plantilla base 5 L1/3 L2.
Se mantiene la independencia entre severidad y q como simplificación, no como
hallazgo.

Con la prevalencia de referencia `19/14.449`, sensibilidad 0,8421 y FPR 0,045,
el modelo manda a L2 un 4,605 % de los registros: TP 0,1107 % y FP 4,4941 %.
L1 recibe TN 95,374 % y FN 0,0208 %. Los FP son 97,60 % de rutas a L2 en este
modelo. Son expectativas del clasificador hipotético, no prevalencias de
escalado de SOCTRA. FP consume investigación L2 con q ordinaria; TP tiene q
alto. FN permanece en L1 con q alto; gamma=1 no añade recargo extra.

`W(q)=1+β(q−0,5)`, β=1, genera 0,5–1,5 veces el servicio base; el multiplicador
esperado en q ordinaria es 0,999 y en q alto 1,486. Para la mezcla base, el
trabajo esperado es 2,585 h-persona/h en L1 (2,584 TN + 0,001 FN) y 0,091 en L2
(0,087 FP + 0,003 TP). El 96,5 % del trabajo L2 procede de FP en esta
construcción; esto cuantifica el costo sintético de esos falsos positivos,
no trabajo observado.

Por investigación, el servicio medio esperado queda en ~0,301 h L1 para TN,
~0,447 h L1 para FN, ~0,216 h L2 por FP y ~0,321 h L2 por TP. Así, con
0,405 FP/h al flujo base, se consumen ~0,087 h-persona/h en trabajo L2 FP.
Todos son tiempos sintéticos derivados del escenario y la mezcla de clases,
no mediciones SOCTRA.

| Celdas analista×clase elegible del escenario | L1 | L2 |
|---|---:|---:|
| Analistas | 5 | 3 |
| Competencia min/mediana/máx. | 0,640/0,750/0,830 | 0,900/0,910/0,930 |
| Servicio base h min/mediana/máx. | 0,225/0,307/0,440 | 0,176/0,220/0,306 |
| Velocidad 1/servicio min/mediana/máx. | 2,273/3,254/4,444 | 3,268/4,545/5,669 |

El LP fluido de capacidad asignable con elegibilidad calcula 17,088 rutas L1/h
y 13,986 rutas L2/h (este último es el stream seleccionado hacia L2; equivale
a ~303,7 registros/h total a una fracción de ruta de 4,605 %). No son colas ni
SLA garantizados.

| Multiplicador de intensidad | Registros/h | Utilización L1 | Utilización L2 | Carga LP L1 | Carga LP L2 |
|---:|---:|---:|---:|---:|---:|
| 0,25 | 2,253 | 12,9 % | 0,8 % | 0,126 | 0,007 |
| 0,50 | 4,506 | 25,8 % | 1,5 % | 0,252 | 0,015 |
| 1,00 | 9,013 | 51,7 % | 3,0 % | 0,503 | 0,030 |
| 1,50 | 13,519 | 77,5 % | 4,5 % | 0,755 | 0,045 |
| 2,00 | 18,025 | 103,4 % | 6,0 % | 1,006 | 0,059 |

Con 5/3, la carga está marcadamente desequilibrada. En una sensibilidad de
trabajo medio, las utilizaciones L1/L2 son 51,7/9,1 % con plantilla 5/1;
51,7/3,0 % con 5/3; 25,8/4,5 % con 10/2; y ~9,2/9,1 % con 28/1 al flujo
base. Con 28/1 y cinco veces el flujo, el cálculo homogéneo da cerca de 46 %
en cada nivel: existe una combinación matemática que evita tanto L1 saturado
como L2 casi ocioso, pero implica una razón de 28 L1 por L2 y una carga x5 sin
respaldo operacional. No es recomendación de plantilla; un L2 único no tiene
redundancia y se debe validar elegibilidad en una organización hipotética
completa antes de cualquier estudio. Para igualar el uso en una plantilla 5/3
el modelo requeriría aproximadamente 45,4 % de rutas L2, en lugar del 4,6 %
calculado; no procede inflar etiquetas ni inventar actividad especializada.

Para reservar margen de espera/congestión, el trabajo activo sin colas debe
ser como máximo la fracción de SLA restante. Con 50 % de holgura: critical
≤0,5 h, high ≤2 h, medium ≤6 h. Con 75 %: ≤0,25/1/3 h. Los extremos
teóricos del servicio base actual multiplicado por `W(q)` son ~0,66 h L1 y
0,46 h L2. El SLA crítico de 1 h resulta posible en el límite sin colas, pero
el extremo L1 dejaría solo ~20 min; para garantizar 50 % de margen, el
servicio crítico debe ser ≤0,5 h. Estos son intervalos de viabilidad
condicionados a supuestos, no duraciones reales estimadas.

### 19.4 Regímenes y recuperación

Con plantilla, habilidades, tiempos, clasificador y ruteo fijos, las
multiplicaciones de llegada anteriores producen carga reducida (x0,5, L1
~26 %), normal (x1, ~52 %), elevada (x1,5, ~78 %) y sobrecarga estructural
(x2, L1 apenas supera capacidad). Un cálculo fluido ilustrativo de x2,5 por
6 h seguido de retorno a x1 acumula ~8,77 h-persona y se recupera en ~3,63 h
bajo capacidad libre constante. No es una traza simulada ni un episodio
empírico. El pico de registros de una hora acredita ráfaga de registros, no
igual número de investigaciones.

### 19.5 Límite de identificación y recomendación

| Parámetro | Estado | Alcance |
|---|---|---|
| Conteos, timestamps, proyecto, severidad y etiquetas | A. Estimable | Dependiente de la población/filtro; asociación no implica causalidad. |
| Atención generalista a SLA / especialista a proyectos conocidos | B. Cualitativo | No identifica proporción de actividad, tiempo o plantilla. |
| Registro→investigación (`κ`), proceso de llegada, q/q0, errores, tiempo de investigación, competencia, velocidad, plantilla, SLA de resolución | C. Sintético | No observado en SOCTRA ni calibrado operacionalmente. |
| Número y actividad de investigaciones L2 | No identificado | No añadir actividades únicamente para llenar capacidad. |

La demanda más defendible para un estudio posterior sería reproducir timestamps
reales o remuestrear bloques temporales, preservando estacionalidad y ráfagas,
con `κ` explícito. La Poisson estacionaria de 9 registros/h sirve como escala
media, no como patrón completo. El flag `incumplimiento_sla` registra
asignación inicial tardía y no debe calibrar finalización de investigación.

Reproducción (imprime agregados anonimizados; no escribe datos ni ejecuta HLS):

```sh
export SOCTRA_RAW_SEPTEMBER=/path/local/dataset_20250919.csv
python studies/soc_triage_hls_availability_robustness/analyze_soctra_demand_capacity.py \
  --raw-september "$SOCTRA_RAW_SEPTEMBER" \
  --processed-september data/soctra/processed/soctra_preprocessed.parquet \
  --processed-february data/soctra/processed/soctra_february_reference.parquet
```

## 20. Estudio paramétrico algebraico de dimensionamiento

Este análisis complementa §19 con regiones de carga, sin alterar el CONOPS
de referencia ni ejecutar trazas, colas, campañas o comparación de políticas.
El script `parametric_soctra_capacity.py` reutiliza el LP de capacidad
fraccional con elegibilidad por clase/proyecto disponible en
`scenario_diagnostics.assess_capacity()`.

### 20.1 Parámetros y reparto

El ancla empírica es `p=570/156981=0,363101 %`, la prevalencia observada de
la etiqueta de escalado estandarizada. Se utiliza solo como proxy de referencia
para el parámetro experimental de necesidad L2: esa etiqueta no demuestra que
cada alerta requiera especialización real. Se estudian además p sintéticas de
1, 2, 5 y 10 %.
Para cada p, `q0` satisface `P(q≥q0)=p` bajo `q~Beta(2,2)`; no se trata de una
reestimación observada. Se mantienen sensibilidad 0,8421 y FPR 0,045 del
escenario. El reparto es `TP=p·sens`, `FN=p·(1−sens)`,
`FP=(1−p)·FPR`, `TN=(1−p)·(1−FPR)`: por tanto, p no es la proporción enviada
a L2. A p empírica se envía 4,789 % a L2; 93,6 % de esa ruta son FP. Con
p=5 %, la ruta L2 es 8,486 %; con p=10 %, 12,471 %.

La sensibilidad a FPR es material: con p empírica, variar FPR de 1 a 4,5 y
10 % cambia L2 de 1,302 a 4,789 y 10,269 %; los FP forman, respectivamente,
76,5, 93,6 y 97,0 % de esa ruta. Son sensibilidades hipotéticas, no una
calibración del clasificador.

### 20.2 Esfuerzo, SLA y plantillas

Se conserva `W(q)=1+β(q−0,5)` y `α=γ=1`, evitando multiplicadores duplicados.
Con β=1, el cociente de esfuerzo medio complejo/ordinario ronda 1,43–1,48 en
el rango de p estudiado; con β=0 es 1 y con β=2/3 queda aproximadamente
1,90–2,44. TN son tareas ordinarias de L1, FN complejas de L1, FP ordinarias
de L2 y TP complejas de L2. Las contribuciones esperadas por ruta se imprimen
separadamente en la salida reproducible.

Con perfiles sintéticos actuales, p empírica y β=1, el servicio esperado es
0,300 h en L1 y 0,222 h en L2. Contra deadlines sintéticos CRITICAL/HIGH/MEDIUM
de 1/4/12 h, el margen medio crítico es 0,700/0,778 h; la fracción
intrínsecamente inviable resulta 0 % con la distribución modelada. Esto mide
servicio sin espera: no predice colas ni resolución total. Los SLA siguen
siendo hipótesis, al igual que los perfiles y la relación entre q y esfuerzo.

El script amplía equipos ciclando perfiles existentes, con identificadores
replicados explícitos y conservando clase elegible, competencia y tiempos por
proyecto. No representa nuevas personas empíricamente observadas. El LP admite
asignación fraccional y respeta elegibilidad y tiempos distintos. Como control,
igualar velocidades dentro de cada clase (conservar elegibilidad y medias)
reduce la capacidad máxima estimada aproximadamente 2,7 % en 10/3 con p=10 %,
12/4 con p=5 % y 20/2 con p=5 %; competencia no interviene en el LP.

| Plantilla | p sintética | Ventana λ (registros equivalentes/h) para L1 25–80 %, L2 10–60 % y LP estable |
|---|---:|---:|
| 5/3 | 5 % | 13,72–14,80 |
| 5/3 | 10 % | 9,00–15,72 |
| 10/3 | 10 % | 9,83–31,45 |
| 12/4 | 10 % | 12,01–37,85 |
| 20/2 | 5 % | 18,49–54,90 |

Las franjas 25–80 % para L1 y 10–60 % para L2 son filtros exploratorios, no
umbrales operacionales empíricos. A 9,019 registros/h, el caso 5/3, p=10 % da
utilización media estimada 45,9/10,0 %; un pulso 2,5× durante 6 h rebasa la
capacidad LP de L1 (ρ=1,12), acumula aproximadamente 12,35 tareas equivalentes
y su recuperación fluida ideal a la tasa base es 1,26 h. L2 no se sobrecarga.
Con 10/3, p=10 %, el pulso mantiene ρ≤0,56 y no acumula atraso en el modelo.
Estas son cuentas fluidas con mezcla y disponibilidad constantes, no colas
simuladas. Las llegadas reducidas, normales y elevadas se calculan con la
misma plantilla (multiplicadores 0,5/1/1,5); la organización no se recalibra.

Con la plantilla original 5/3, p empírica y λ=9,019/h, la utilización L2
estimada es solo ~3,2 % (L1 ~51,6 %), señal de desbalance en estas hipótesis.
El caso p empírica presenta infrautilización relativa de L2 con FPR=4,5 %;
para aumentar su participación sin crear actividades hay que variar p, FPR,
el ratio de plantilla o la intensidad. 5/3 con p=10 % ofrece una región
exploratoria próxima a la intensidad media fuente; 10/3 con p=10 % y 20/2 con
p=5 % son sensibilidades adicionales en intensidades indicadas arriba. No se
declara ninguna como óptima o representativa de GMV-CERT. La compatibilidad
operacional depende especialmente de la conversión desconocida de registro a
investigación (`κ`), del mix real de clases/proyectos y de las duraciones,
turnos y perfiles no observados.

Reproducir las tablas algebraicas/LP (sin datos privados ni escrituras):

```sh
python studies/soc_triage_hls_availability_robustness/parametric_soctra_capacity.py
```
