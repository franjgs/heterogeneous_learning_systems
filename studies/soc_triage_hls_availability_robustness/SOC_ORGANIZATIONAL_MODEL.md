# SOCTRA-HLS: modelo organizativo canónico

> **NEW MODEL / MODELO NUEVO:** este documento especifica la línea activa de triaje automático seguido por exactamente una investigación. Las campañas históricas y el manuscrito LaTeX pertenecen al **OLD MODEL / MODELO VIEJO**. Véase [MODEL_GENERATIONS.md](MODEL_GENERATIONS.md) para estado, evidencia, restricciones de comparabilidad y preguntas pendientes.

**Escenario experimental base actual:** [V2_24X7](config/SOC_REFERENCE_ORGANIZATION_V2_24X7.json), selecciona `triage_single_investigation` y se ejecuta con [`run_scenario.py`](run_scenario.py). Todos los profesionales están disponibles de forma individual y continua como idealización experimental, no como jornada laboral real. V2 8x5 se conserva intacto como variante de análisis posterior; V1 y las campañas históricas siguen siendo antecedentes.

> **Modelo organizativo vigente (decisión científica):** una herramienta automática recomienda L1 o L2 al llegar cada alerta; su recomendación se acepta automáticamente y se ejecuta una única investigación en el nivel elegido. TP/FP/TN/FN se definen frente a la etiqueta histórica de escalado adoptada como referencia operativa, no frente a una verdad objetiva de especialización. La configuración V2_24X7 y `run_scenario.py` conectan este flujo a JSON, el generador existente y el backend; se recupera disponibilidad continua individual para aislar efectos de asignación y carga sin cierres de calendario. El modelo mantiene calendarios restringidos en V2 8x5 y los ejecutores/campañas históricos conservan su flujo anterior. Véase la sección 16 para estado y límites.

## 1. Objetivo y alcance

Representar alertas como tareas que, tras triaje, reciben una única investigación en L1 o L2. Se estudia cómo clase, severidad, dificultad, eficiencia, competencia, elegibilidad, calendarios y organización se relacionan con carga y resultados. El escenario es sintético, generalizable como estructura a otros dominios y no reproduce ni valida los procedimientos de un SOC concreto. Los diagnósticos de viabilidad y capacidad son evaluaciones externas, no políticas.

## 2. Taxonomía y datos disponibles

Una alerta contiene llegada, clase/proyecto, severidad, dificultad individual q en [0,1], una etiqueta de referencia operativa sobre escalado y deadline contractual absoluto. La etiqueta de referencia procede conceptualmente de las etiquetas históricas de escalado usadas por SOCTRA. No existe verdad independiente para determinar si aquellas decisiones humanas eran óptimas; por tanto, prevalencia de esa etiqueta no equivale a prevalencia objetiva de necesidad de especialización. En trazas sintéticas puede representarse como `reference_escalation` oculta al dispatcher. El evaluador conoce etiquetas/dificultad; la política solo recibe información observable permitida.

Cada profesional tiene nivel, elegibilidad y competencia por clase. El recurso agrega servicio nominal individual, forecast y calendario. La eficiencia temporal está codificada en el servicio nominal; la competencia es una propiedad de calidad distinta. L1/L2 son etapas funcionalmente distintas: no se impone que L2 sea más competente ni necesariamente más lento para la misma clase.

Llegadas, capacidad nominal, capacidad asignable, carga relativa, colas, trabajo pendiente, utilización y esperas son medidas distintas. rho = tasa ofrecida / capacidad asignable describe presión media bajo una mezcla/regla dada; no garantiza estabilidad ni cumplimiento de plazos.

D1, P1, WAPS/HLS-B, clasificadores y recomendaciones SOCTRA no cambian. Las políticas solo reciben el forecast y otra información disponible antes de ejecución. Los sidecars de dificultad, necesidad y TP/FP se usan solo por el motor/evaluador.

## 3. Servicio previsto y efectivo

Para alerta a, profesional i, nivel l_i y clase k_a:

\[
\widehat{s}_{ia}=s_{base}(l_i,k_a)u_{i,k_a},\quad
s_{ia}=\widehat{s}_{ia}f(q_a),\quad
f(q_a)=1+\beta(q_a-0.5),\;0\leq\beta<2.
\]

Unidades: horas de trabajo. beta < 2 asegura factor positivo en q∈[0,1]. El forecast_service_by_class se muestra al dispatcher; q realizado y servicio efectivo pertenecen al entorno/motor. V1 usa beta=0, de modo que no añade variabilidad temporal por dificultad.

El generador existente usa q ~ Beta(2,2): hipótesis sintética, acotada, simétrica y centrada en 0.5; no se estimó con observaciones SOC. E[q]=0.5, así que E[f(q)]=1. Bajo esas hipótesis se conserva el servicio medio nominal; no implica igualdad por alerta o traza. Detalle en [SERVICE_TIME_DIFFICULTY_MODEL.md](SERVICE_TIME_DIFFICULTY_MODEL.md).

En L2 se combina el factor de dificultad con el multiplicador preexistente para falsas positivas:
\[
s_{L2,ia}=s_{base}(L2,k_a)u_{i,k_a}f(q_a)m_a,\quad
m_a=1\text{ si hay necesidad real},\;m_a=\alpha\text{ para un FP escalado}.
\]
alpha solo modifica el esfuerzo de investigación de los FP asignados a L2, nunca L1. No significa que todo FP sea trivial; alpha=1 representa investigación completa y valores inferiores son hipótesis de esfuerzo reducido. El nuevo flujo conceptual asigna una sola investigación; se conserva el identificador y el deadline original de la alerta. alpha=0.50 del perfil V1 es una hipótesis previa diagnóstica, no una estimación ni un default confirmado para el modelo adoptado. Los experimentos históricos con alpha 0.25/0.50/0.75/1.00 y beta cero no se editan.

El modelo adoptado usa un factor gamma para FN investigados por L1:

\[
s_{L1,ia}=\widehat{s}_{ia}f(q_a)\gamma_a,\qquad
\gamma_a=\begin{cases}\gamma,&\text{FN},\\1,&\text{en otro caso},\end{cases}\quad \gamma\geq1.
\]

gamma es una hipótesis sintética de mayor esfuerzo de investigación cuando la referencia indicaba escalado pero el clasificador deja la alerta en L1. No es penalización estadística ni consecuencia universal de equivocarse. Está implementada como multiplicador ambiental optativo en el nuevo flujo; el valor predeterminado es gamma=1, que es neutral. No se fija un valor experimental mayor que uno. La misma etiqueta de referencia y la recomendación se utilizan solo por el entorno/evaluador para instanciar el esfuerzo, no para dar información oculta a la asignación.

Conceptualmente, `s_realizada = s_prevista × f(q) × m_alpha × m_gamma`, con cada multiplicador condicional no aplicable igual a uno. El dispatcher conoce servicios previstos por clase y cualquier forecast ex ante declarado; no ve q realizada ni etiquetas/multiplicadores individuales. La construcción de forecasts a partir de tasas agregadas es una decisión experimental por fijar, no permite filtrar Y ni la confusión individual.

## 4. Triaje, ruta y resultados TP/FP/TN/FN

El triaje es preliminar y distinto de investigar. En el escenario principal, una herramienta automática produce recomendación L1/L2 con latencia despreciable respecto a trabajo humano y sin consumo significativo de capacidad. Se acepta el 100% de sus recomendaciones: es una hipótesis explícita, no un comportamiento observado. El analista no contradice la recomendación en el modelo principal.

Sea `Y=1` la etiqueta de referencia de escalado y `R=1` la recomendación L2. La etiqueta Y no afirma necesidad objetiva verificada.

| Caso | Y | R | Ruta adoptada | Trabajo asignado |
|---|---:|---:|---|---|
| TP | 1 | 1 | Triaje → L2 | Una investigación especializada; uso necesario según referencia |
| FP | 0 | 1 | Triaje → L2 | Una investigación L2; uso innecesario según referencia; esfuerzo modulado por alpha |
| TN | 0 | 0 | Triaje → L1 | Una investigación L1 ordinaria |
| FN | 1 | 0 | Triaje → L1 | Una investigación L1 aunque la referencia favorezca L2; esfuerzo gamma como hipótesis |

Las etiquetas son para evaluación y realización ambiental. D1/P1/HLS-B no observan Y, TP/FP/FN/TN, q realizado ni los factores alpha/gamma realizados. Su decisión/distribución entre analistas ocurre dentro del nivel de la ruta y con sus entradas ex ante. La extensión de esfuerzo no cambia la recomendación ni la asignación de nivel.

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

## 13 bis. Base experimental V2_24X7 (disponibilidad individual continua)

La variante [`SOC_REFERENCE_ORGANIZATION_V2_24X7.json`](config/SOC_REFERENCE_ORGANIZATION_V2_24X7.json)
parte de V2 y cambia **solo el campo `calendar` de cada analista** a
`{"kind":"continuous"}`. Profesionales, clase, elegibilidad, competencia,
eficiencia, servicios, mezclas, severidades, parámetros alpha/beta/gamma,
clasificador, deadlines, tasas, regímenes y semilla permanecen idénticos. El
identificador y la referencia descriptiva del roster se heredan como procedencia;
la disponibilidad operativa la determinan los ocho campos `calendar`. Al citar
una corrida identificar siempre el archivo JSON y su hash/commit.

Esta es la configuración base de las siguientes investigaciones de políticas:
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

## 14. Compatibilidad y alcance de conclusiones

La configuración V1, las configuraciones históricas, los ejecutores de campaña,
los motores, algoritmos, clasificadores, resultados y manuscritos permanecen
intactos. V2 y V2_24X7 conectan generación, flujo y backend para una ejecución
reproducible individual; V2_24X7 es la base experimental sin cierres de
calendario. Los JSON históricos sin `flow_mode` cargan
`historical_l1_then_l2`; los ejecutores históricos no se redirigen al escenario
nuevo. El runner y analizador usan V2_24X7 como default; V2 requiere indicar su
JSON explícitamente.

**Propiedades matemáticas:** normalización E[f]=1 bajo Beta(2,2); mínimos de
servicio y LP condicionado a entradas. **Hipótesis:** roster, competencias,
eficiencia, Beta, prevalencia, tasas, mezcla, alpha, coste y ausencia DST.
**Calculado:** capacidad fluida y factibilidad calendarizada discretizada para
V1, V2 8x5 y V2_24X7. Las verificaciones iniciales de V2_24X7 fueron controles
técnicos de una semilla; después se ejecutó el piloto exploratorio de diez
semillas documentado en la sección 13 quater. Es la única comparación de
políticas NEW MODEL registrada aquí y no es confirmatoria.

V2 8x5 refleja que una alerta L2 fuera de turno puede incumplir un SLA corto
aunque su servicio activo quepa en el plazo. V2_24X7 elimina esa restricción en
la base experimental, pero multiplica las horas disponibles y reduce rho; no es
una comparación de calendario manteniendo capacidad constante. No se puede concluir estabilidad general, SLA real, costes reales, superioridad
de política ni mejoras de rendimiento.
Se necesitarían datos operativos representativos y experimentos futuros
preespecificados.

## 15. Archivos y referencias

- Base experimental de carga baja: config/SOC_REFERENCE_ORGANIZATION_V2_24X7.json.
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

### Modelo vigente acordado frente al código

| Elemento | Decisión/modelo científico vigente | Estado en el código auditado |
|---|---|---|
| Fuente de referencia para TP/FP/TN/FN | Etiqueta histórica de escalado SOCTRA adoptada como referencia operativa, no verdad objetiva de especialización | Existen etiquetas sintéticas ocultas para necesidad/ruta en campañas anteriores; su semántica no debe elevarse a verdad empírica |
| Triaje principal | Automático, latencia despreciable, recomendación aceptada en 100% | `triage_execution.py` recibe las recomendaciones ya generadas y acepta la ruta; no simula latencia de clasificador |
| Generación de V2 | Demanda temporal y mezcla declaradas en JSON, semilla fija | `scenario_loader.generate_trace` reutiliza `ia_l1_l2_simulation.generate_alerts`; traduce la mezcla/régimen V2 a rate base, pulso y recuperación |
| Ruta | TP/FP van directamente a investigación L2; TN/FN a investigación L1 | JSON y `run_scenario.py` integrados con `triage_execution`; los runners históricos conservan L1 antes de L2 |
| Número de investigaciones | Una investigación por alerta en el nivel recomendado | V2 ejecutable asigna una etapa; el modo histórico preserva las etapas antiguas |
| FP L2 | Investigación no necesariamente trivial; factor alpha modula el esfuerzo | alpha ambiental se aplica en ambos modos; políticas solo ven forecast, nunca etiqueta o escala efectiva |
| FN L1 | Esfuerzo gamma≥1, gamma=1 neutro, no fijar aún gamma>1 | `gamma` está implementado en API nueva con default 1; no se aplica al flujo histórico |
| SLA | Deadline absoluto y tiempo natural; finalización puntual, tardía o pendiente al corte | API clasifica los tres estados; nuevo runner los agrega; métricas históricas conservan sus definiciones |
| Calidad | Proxy separado; no exactitud validada | Competencia/proxies existen, pero no hay outcome adjudicado de resolución correcta |
| Calendarios | Base V2_24X7: disponibilidad continua individual para L1/L2, sin suspensiones por turno | `SOC_REFERENCE_ORGANIZATION_V2_24X7.json` cambia solo los calendarios; V2 8x5 se conserva como variante y los motores soportan ambos |

V1 y sus resultados diagnósticos permanecen como perfil anterior. V2 8x5 y su
validación seed 998001 se conservan intactos como variante de disponibilidad.
V2_24X7 es la base ejecutable recomendada para las siguientes comparaciones de
políticas sin restricción de calendarios. Todos sus parámetros siguen siendo
sintéticos y la disponibilidad individual continua es una idealización.

### Qué está implementado, qué falta y qué se excluye

**Implementado/reutilizable:** perfiles de servicio y competencia por
profesional/clase; elegibilidad; dificultad y beta de servicio; alpha como
realización ambiental L2; generación separada de recomendaciones y etiquetas
ocultas; colas/calendarios/suspensión; deadline natural; métricas de estado,
trabajo y SLA en runners existentes. `triage_execution.py` los orquesta ya en
modo nuevo o histórico usando los dos backends existentes.

**Integrado para ejecución técnica por escenario:**
`triage_execution.run_triage_flow(..., flow_mode="triage_single_investigation")`
envía las alertas recomendadas directamente a la cola de su único nivel de
investigación y compone alpha, beta y gamma como escalas ambientales. La misma
API mantiene `flow_mode="historical_l1_then_l2"` para reproducir la ruta
anterior. El loader JSON y `run_scenario.py` conectan el modo nuevo al generador
existente y al backend de calendario. Los ejecutores de campañas anteriores
conservan su flujo histórico. Los dispatchers
reciben forecasts y metadatos públicos, no etiqueta de referencia, confusión,
necesidad oculta, q realizada ni multiplicadores efectivos. Ninguna política
ni motor fue reescrito. Falta integrar el selector en futuros runners de
campaña. El forecast L2 V2 ya se ajusta con la mezcla TP/FP ex ante. Si un
estudio cambia alpha, gamma, beta o las dependencias entre dificultad y
referencia, debe recalcular y declarar el forecast agregado antes de ejecutar;
nunca debe usar labels individuales.

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
- FP L2 puede tener servicio reducido con alpha, pero no se supone trivialidad.
- FN L1 tiene esfuerzo adicional representable por gamma como hipótesis; no se
  fija gamma y el neutro es 1.
- La base experimental V2_24X7 ofrece disponibilidad individual continua para
  L1/L2 como idealización, no como jornada real; V2 L1 24x7/L2 8x5 queda para
  análisis posterior. El SLA siempre corre en tiempo natural.
- Coste, competencia y velocidad son dimensiones separadas. Perfiles pueden
  favorecer L2 en clases concretas sin imponer superioridad universal.
- Finalización, puntualidad contractual y calidad esperada son resultados
  diferentes; no se afirma exactitud empírica.

### Decisiones todavía abiertas

1. Evidencia para beta distinto de cero o gamma mayor que uno; V2_24X7 conserva
   beta=0 y gamma=1 como referencia neutra.
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
