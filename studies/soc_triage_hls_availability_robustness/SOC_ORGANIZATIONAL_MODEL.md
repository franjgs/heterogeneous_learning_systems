# SOCTRA-HLS: modelo organizativo canónico

**Perfil organizativo V1:** [configuración](config/SOC_REFERENCE_ORGANIZATION_V1.json). Sus tasas, costes y roster son hipótesis sintéticas, no datos observados. La configuración es diagnóstica y no está integrada en un runner end-to-end.

## 1. Objetivo y alcance

Representar tareas y profesionales heterogéneos para estudiar cómo clase, severidad, dificultad, servicio, elegibilidad, competencia, calendarios y organización se relacionan con colas y resultados. El flujo integrado actualmente implementado envía todas las alertas a servicio L1 antes de aplicar la recomendación positiva para encaminarlas a L2. La distinción organizativa más reciente —triaje separado de investigación y positivas enviadas directamente a L2 tras triaje automático— aún no está implementada; véase la auditoría al final de este documento. Los diagnósticos de viabilidad y capacidad son evaluaciones externas, no nuevas políticas. El escenario no representa ni valida una organización cliente concreta.

## 2. Taxonomía y datos disponibles

Una alerta contiene llegada, clase/proyecto, severidad, dificultad individual q en [0,1] y deadline absoluto. Necesidad real de L2, recomendación SOCTRA y etiqueta TP/FP son variables distintas. El evaluador puede conocer etiquetas y dificultad para medir el escenario; no se exponen al dispatcher.

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

En L2 se combina el factor de dificultad con el multiplicador preexistente:
\[
s_{L2,ia}=s_{base}(L2,k_a)u_{i,k_a}f(q_a)m_a,\quad
m_a=1\text{ si hay necesidad real},\;m_a=\alpha\text{ para un FP escalado}.
\]
alpha solo modifica L2, nunca L1. Se conserva el mismo q, ID y deadline al pasar entre etapas. alpha=0.50 en V1 es una hipótesis de sensibilidad, no una estimación. Los experimentos históricos con alpha 0.25/0.50/0.75/1.00 y beta cero no se editan.

## 4. SLA contractual y deadlines

El SLA es un compromiso contractual en tiempo natural desde llegada hasta resolución final. El deadline original permanece invariable en L1→L2. El reloj avanza de noche, fin de semana, durante cola, turnos, suspensión y escalado. No existe pausa contractual, deadline por etapa, reinicio ni extensión automática.

V1 conserva los offsets alta 1 h, media 4 h y baja 12 h; deadline = llegada + offset. No se amplían para hacerlos compatibles con L2. El horario y dimensionamiento son restricciones internas, no excepciones contractuales. request_for crea el deadline absoluto y el motor lo conserva.

## 5. Organización operativa V1

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

El reloj usa horas naturales con semana iniciada lunes 00:00 en hora local del escenario. La API usa calendarios semanales abstractos; no modela zona IANA ni cambios DST y V1 supone semanas fijas de 168 h. Suspender servicio por calendario conserva tarea y trabajo pendiente, pero no detiene el SLA.

## 6. Servicios nominales V1

Valores en horas activas por tarea; hipótesis sintéticas más cortas que la referencia histórica para dejar holgura activa sin forzar viabilidad por calendario:

| Nivel | top5 | next5 | tail |
|---|---:|---:|---:|
| Base L1 (h) | 0.08 | 0.10 | 0.12 |
| Base L2 (h) | 0.30 | 0.36 | 0.42 |

Factores u: L1-01 0.90, L1-02 1.00, L1-03 1.10, L1-04 0.95, L1-05 1.05; L2-01 0.95, L2-02 1.05, L2-03 1.00. JSON declara el producto exacto por profesional/clase. beta=0.

Servicios históricos L1 0.20/0.25/0.30 h y L2 0.75/0.90/1.00 h siguen en sus configuraciones. En V1 la ruta con mayor trabajo activo mínimo cabe en el deadline alto de 1 h; la factibilidad por servicio no garantiza cumplimiento real.

## 7. Demanda y dimensionamiento

V1 declara metadatos de diagnóstico, no un generador nuevo. Aunque el cargador preserva compatibilidad con la referencia al generador Q1, el perfil siguiente no altera sus trazas ni está conectado a ese runner. Una campaña futura debe integrar explícitamente las tasas con los mecanismos existentes y conservar aisladas las trazas históricas.

Mezclas hipotéticas: clase top5/next5/tail = 0.50/0.30/0.20; severidad alta/media/baja = 0.20/0.30/0.50. Cada segmento postula tasa Poisson estacionaria con proporciones constantes:

| Régimen (semana desde lunes 00) | Duración | Tasa total (top5 / next5 / tail) |
|---|---:|---:|
| Ordinario: Lun 00–Sáb 00 | 120 h | 2.5/h (1.25 / 0.75 / 0.50) |
| Pulso: Sáb 00–Dom 00 | 24 h | 15/h (7.50 / 4.50 / 3.00) |
| Recuperación: Dom 00–Lun 00 | 24 h | 1.5/h (0.75 / 0.45 / 0.30) |

El escenario fija prevalence 0.10 por clase, sensibilidad 0.8421, FPR 0.045, alpha 0.50 y beta 0. Los classifier operating points son catalogados históricamente, pero prevalencia, llegadas, mezcla y transferencia de operating point a otros dominios son supuestos. Probabilidad esperada de recomendación L2: 0.10×0.8421 + 0.90×0.045 = 0.12521. Cálculo ex ante supone independencia de dificultad respecto a clase, necesidad y recomendación; si hay correlación se requieren sidecars conjuntos de una traza.

La plantilla de cinco L1 y tres L2 se eligió para dejar capacidad media en carga ordinaria, una sobrecarga L1 en el pulso y presión L2 no colapsada en promedio semanal. No se igualan rho ni se infieren dimensiones óptimas de una sola carga agregada. Capacidad media L2 oculta que el equipo tiene capacidad instantánea cero de noche y fin de semana.

## 8. Capacidad asignable y carga

analyze_reference_organization.py reutiliza assess_capacity() y el LP existente effective_capacity(): máximo flujo común para una mezcla, respetando clase, elegibilidad, servicio individual y disponibilidad semanal fraccional. No suma productividades de analistas incompatibles.

| Régimen | Capacidad L1 alertas/h | tasa L1 | rho L1 | Capacidad L2 rutas/h | tasa L2 | rho L2 |
|---|---:|---:|---:|---:|---:|---:|
| Ordinario | 10.746 | 2.500 | 0.233 | 2.498 | 0.312 | 0.125 |
| Pulso sábado | 10.746 | 15.000 | 1.396 | 2.498 | 1.871 | 0.749 |
| Recuperación domingo | 10.746 | 1.500 | 0.140 | 2.498 | 0.187 | 0.075 |

Todos los cinco L1 y tres L2 son recursos vinculantes en el óptimo fluido y no hay clase sin elegibilidad. Las parejas elegibles de L2 comparten la restricción de mezcla. L2 usa tasa esperada de recomendaciones y servicio medio TP/FP ponderado por alpha. En el pulso L1 ofrece 1.410 horas-persona de trabajo por hora natural, superior a una hora-persona disponible: exceso fluido aproximado 9.84 horas en sábado. Domingo ofrece 0.141 h-persona/h y capacidad media para recuperación. No son colas observadas ni garantía de estabilidad.

Sábado y domingo implican 49.385 recomendaciones L2 esperadas y aproximadamente 14.08 h de servicio L2. L2 no trabaja entonces: el trabajo se acumula hasta lunes 09. Es carga entrante ex ante, no cola observada; L1 desplaza el instante real de llegada a L2.

## 9. Viabilidad temporal

analyze_reference_organization.py evalúa puntos medios cada 15 min durante una semana desde lunes 00, ponderados por mezcla de clase/severidad y probabilidades TP/FP. Es enumeración determinística discretizada, no traza ni experimento. Con beta=0, alpha=0.50:

| Diagnóstico ponderado | Alta 1 h | Media 4 h | Baja 12 h | Total |
|---|---:|---:|---:|---:|
| Intrínsecamente inviable por tiempo activo | 0% | 0% | 0% | 0% |
| Inviable por calendario sin colas | 9.36% | 8.25% | 5.28% | 6.98% |

La holgura optimista tiene mínimo 0.472 h y cuantiles p10/p50/p90 de 0.910/3.928/11.928 h. Con calendarios, el mínimo es −63.546 h y los cuantiles globales p10/p50/p90 son 0.886/3.924/11.920 h. En rutas L1+L2, 56.01% son no viables sin cola por calendario; en L1 sola, 0% en la cuadrícula. Un escalado nocturno, tardío del viernes o de fin de semana puede violar incluso el SLA corto aunque el trabajo activo combinado sea menor a una hora. Esta limitación estructural se conserva intencionalmente. La estimación depende de cuadrícula, anclaje semanal, composición y probabilidades; no es medición empírica. La cota de calendario elige el mejor profesional por etapa, sin contención por otras tareas.

Ejemplo: una alerta alta llegada sábado 23:45 tiene deadline domingo 00:45. El servicio mínimo activo L1+L2 es inferior a 1 h, pero con el calendario su finalización más temprana es lunes 09:17; el slack calendarizado es −32.535 h. El reloj SLA no se detiene durante el cierre de L2.

Clasificación: (1) inviabilidad intrínseca si T_min > deadline-arrival; (2) calendario si el caso es viable sin turnos pero la primera finalización calendarizada excede deadline; (3) congestión/disponibilidad/asignación si era viable sin cola y la ejecución concreta acaba tarde. Factibilidad es necesaria, no suficiente. Capacidad nominal aquí se refiere a plantilla/horas contratadas antes de restricciones de elegibilidad; capacidad asignable es la tasa del LP con servicios, mezcla y calendarios; capacidad utilizada solo se obtiene de una ejecución. El LP semanal no modela colas ni sincronía instantánea; carga relativa no garantiza SLA. La utilización del óptimo LP no es utilización observada. Recuperación usa colas/trabajo pendiente de traza y criterio configurable.

## 10. Coste

No hay evidencia salarial/coste empresarial. Coste normalizado configurable por hora contratada y profesional, heredado por nivel: cada L1=1.0, cada L2=1.8. La razón es hipótesis de coste superior de especialista, no salario observado. Plantilla/turnos: 168 h L1 y 120 h L2; coste semanal 168 + 1.8×120 = 384 unidades relativas. El coste contratado existe aunque haya poca ocupación; no se equipara al coste de tiempo usado. Ninguna política optimiza este coste.

## 11. Decisiones de diseño

| Decisión | Motivo | Alternativa descartada |
|---|---|---|
| SLA natural continuo y deadline original L1/L2 | compromiso end-to-end | Pausar, reiniciar o ampliar deadline |
| L1 por turnos, cobertura 24x7; L2 L-V 09–17 | separar cobertura y horario personal | Persona individual L1 24x7, guardia L2 |
| Servicio V1 más corto, beta 0 | hipótesis temporal con holgura activa | Cambiar servicios/deadlines históricos |
| 5 L1 y 3 L2 con elegibilidad explícita | presión no trivial con régimen regular y pulso | igualar rho o declarar óptimo desde un promedio |
| Coste relativo 1.8 | distinguir coste horario sin inventar salarios | coste de ocupado solamente |
| Demanda como metadato diagnóstico | evitar fingir que JSON ya la genera | generador paralelo o cambio de campañas |

## 12. Compatibilidad y alcance de conclusiones

Nueva configuración: config/SOC_REFERENCE_ORGANIZATION_V1.json. No cambia HISTORICAL_REFERENCE.json, SYNTHETIC_SOC_24x7.json, SYNTHETIC_SOC_MIXED_SHIFTS.json, motores, algoritmos, clasificadores, resultados o manuscritos. Servicios históricos y deadlines históricos quedan intactos; beta predeterminado sigue cero. El cargador expone metadatos demand_profile y cost_model, pero no los introduce en SimulationRequest.

**Propiedades matemáticas:** normalización E[f]=1 bajo Beta(2,2); mínimos de servicio y LP condicionado a entradas. **Hipótesis:** roster, competencias, eficiencia, Beta, prevalence, tasas, mezcla, alpha, coste y ausencia DST. **Calculado:** capacidad fluida y factibilidad calendarizada discretizada. No se ejecutaron campañas.

Por ejemplo, una alerta alta que llega sábado 23:45 tiene deadline domingo 00:45; su trabajo activo mínimo cabe en el plazo, pero la finalización más temprana L1→L2 con estos turnos es lunes 09:17 (calendar slack −32.535 h). No se puede concluir estabilidad general, SLA real, costes reales, superioridad de política ni mejoras de rendimiento. Se necesitarían datos operativos representativos y experimentos futuros preespecificados. La configuración de demanda no autoriza ni inicia campaña.

## 13. Archivos, documentación y cuestiones abiertas

- JSON: config/SOC_REFERENCE_ORGANIZATION_V1.json.
- Diagnóstico: analyze_reference_organization.py.
- Interfaces: scenario_loader.py, execution_api.py, availability_engine.py.
- Viabilidad/capacidad: scenario_diagnostics.py y SCENARIO_FEASIBILITY_DIAGNOSTICS.md; LP en studies/soc_human_ai_organization/calibrate_a1_scenarios.py::effective_capacity.
- Servicio: SERVICE_TIME_DIFFICULTY_MODEL.md.
- Tests: tests/test_scenario_loader.py, tests/test_scenario_diagnostics.py, tests/test_execution_api.py.
- Evidencia previa: studies/soc_human_ai_organization/ y studies/soc_triage_hls_q1_integration_evidence/.
- Índices: README raíz y README de estudio enlazan este documento. LaTeX no se modifica.

Pendiente: (1) roster real con descansos, ausencias, festivos y relevos; (2) servicio medido por nivel/clase y asociación duración-calidad; (3) llegadas, mezcla y pulsos observados; (4) prevalence/need y errores clasificador por clase/dificultad; (5) costes autorizados para reemplazar 1.8; (6) horizonte de medición que no convierta tardanza en cumplimiento; (7) decidir si el calendario semanal abstracto requiere zona horaria, DST y fechas reales.

## 14. Auditoría del flujo de triaje e investigación

Esta sección registra la distinción organizativa acordada entre **triaje** e
**investigación** y la contrasta con el código de `9daefeaf`. No cambia la
interpretación de las campañas existentes: describe qué falta para que un
futuro runner represente el flujo nuevo. Los TP/TN/FP/FN son estados
ambientales/evaluativos; las etiquetas ocultas nunca se entregan al dispatcher.

### Flujo organizativo acordado

La alerta llega y recibe una recomendación de triaje. En el escenario de
referencia el triaje es automático, de latencia despreciable respecto al
trabajo humano y sin capacidad L1 significativa. La recomendación determina
la ruta inicial:

| Resultado | Necesidad real | Ruta inicial | Trabajo humano esperado |
|---|---|---|---|
| TP | Sí requiere especialización | L2 | Investigación especializada L2 completa; no investigación L1 completa |
| TN | No requiere especialización | L1 | Investigación ordinaria L1 |
| FP | No requiere especialización | L2 | Investigación L2 innecesaria; no se presume que sea trivial |
| FN | Sí requiere especialización | L1 | Investigación L1; se postula más esfuerzo medio y menor calidad esperada que con L2 |

Para triaje humano, el tiempo del analista L1 sería una etapa anterior a la
decisión de ruta. Ese modo no se adopta como referencia V1 porque requiere un
tiempo de triaje diferenciado. En ambos modos el reloj SLA empieza en la
llegada, conserva el deadline original y continúa durante colas, turnos,
suspensión y cualquier escalado o relevo.

La necesidad de L2 significa que la alerta necesita especialización para el
trabajo adecuado; no significa que L1 sea incapaz de resolverla. La afirmación
FN sobre más esfuerzo y menor calidad es una hipótesis sintética del escenario,
no evidencia empírica.

### Qué ejecuta hoy el código

`run_availability_campaign._make_trace()` crea previamente recomendaciones
Bernoulli con las tasas `pD` y `pFA`; el bucle del motor no asigna tiempo ni
recursos al clasificador. `run_availability_campaign._run_l1()` pasa todas las
alertas a la cola y servicio L1. Después, `_run_condition()` crea una llegada
L2 solo cuando la recomendación es positiva y existe finalización L1 dentro
del cutoff; la llegada L2 usa esa finalización y conserva el ID, la clase y el
deadline original. Las recomendaciones positivas se aceptan al 100% en ese
runner. Las negativas permanecen en la ruta L1. No se registra una decisión
humana L1, ni hay corrección de una negativa durante la investigación.

Por tanto, el runner actual es **servicio humano L1 para todas las alertas,
seguido de aceptación automática de las recomendaciones positivas**. No es
triaje automático seguido de investigación en L1 o L2. Una recomendación
positiva no llega directamente a L2 y sí soporta un servicio L1 completo. Una
recomendación negativa no puede producir una escalada tardía.

El orquestador más antiguo `simulate_l1_l2()` también fija la ruta antes de
ejecutar L1; ofrece el modo de etiqueta histórica o el modo de aceptar una
recomendación hipotética. `observed_effective_analyst_decision` queda vacío.
Esas opciones son referencias de ruteo, no decisiones de un profesional.

La configuración V1 de este documento es metadato para diagnósticos y el
`scenario_loader` construye solicitudes de un solo nivel. No configura por sí
sola este flujo integrado ni reemplaza la configuración de las campañas. En
particular, los servicios L1/L2 y alpha=0.50 de V1 pertenecen al perfil
diagnóstico anterior: no son parámetros ya conectados al nuevo flujo
TP/TN/FP/FN.

### Auditoría de servicios, dificultad, competencia y resolución

| Elemento | Lo que permite el modelo existente | Límite para el flujo acordado |
|---|---|---|
| `s_base(level,class)` y `u_(analyst,class)` | La configuración puede hacer que L2 tarde menos que L1 para una clase dada, o que la relación varíe por clase y persona. | Los valores V1 actuales hacen mayor el servicio L2 que L1 en las tres clases. No codifican por sí solos que esas actividades sean distintas ni la expectativa de especialista más eficiente. |
| `task_class` / elegibilidad | Separa top5/next5/tail y restringe qué profesionales pueden atender cada clase. | Son clases/proyectos, no el tipo ordinario/especializado del trabajo. Una clase puede contener alertas TN y FN. |
| Competencia `c_(i,k)` | Hay un valor por profesional y clase; pueden existir perfiles diferentes entre niveles y profesionales. | Para la misma persona y clase, la competencia no cambia entre TN y FN. No modela una penalización de corrección específica a la ruta fallida. |
| Dificultad `q_a` y `f(q_a)` | Con `beta>0` ajusta el tiempo efectivo por alerta y también alimenta proxies de calidad existentes. | El generador la trata como dificultad general, no como necesidad de especialización; el mismo factor se aplica a L1 y L2. Condicionarla a need para simular FN sería una hipótesis nueva y alteraría también el esfuerzo L2 y los proxies de calidad. |
| `alpha` | Escala solo el tiempo L2 de los FP; `alpha=1` implica trabajo completo. | `alpha<1` supone menor esfuerzo FP. Alpha no distingue investigación ordinaria y especializada ni justifica llamar trivial una falsa alarma. V1 alpha=0.50 es solo la hipótesis del perfil anterior. |
| Necesidad oculta y recomendación | Se generan y contabilizan TP/TN/FP/FN; el entorno puede conservar etiquetas ocultas. | La necesidad no condiciona el servicio L1 actual. Un FN consume el mismo servicio L1 que un TN si coinciden persona, clase y dificultad. |
| Calidad | Finalización, puntualidad y proxies basados en competencia/dificultad se calculan por separado. | No se sortea ni observa una resolución correcta/incorrecta; competencia no está calibrada como probabilidad de resolución. |

#### A. Rapidez de L2

Sí, matemáticamente se puede expresar con los parámetros existentes si la
clase y el contenido del trabajo comparado están definidos de forma
compatible: se eligen servicios base y factores individuales que den menor
servicio L2 para las clases en que se espera especialización. No hay una regla
que imponga esa relación. Los números de V1 son lo contrario en valor nominal
por clase (base L2 0.30/0.36/0.42 h, base L1 0.08/0.10/0.12 h); dado que el
runner anterior presta servicio completo L1 antes de L2, no es válido usar esa
diferencia para concluir que L2 sea menos eficiente. No se cambian esos
valores: su interpretación necesita redefinir primero las actividades.

#### B. Alertas ordinarias y especializadas en una misma clase

No de forma directa. La clase actual identifica proyecto/estrato; la
necesidad de especialización es otro booleano oculto. Para dos alertas de la
misma clase atendidas por la misma persona y con el mismo q, el servicio
previsto y efectivo L1 es idéntico, aunque una sea TN y otra FN. Separar los
tipos como clases distintas sería posible solo si la definición de clase se
refinara y los parámetros de clasificador, mezcla, elegibilidad, competencia y
servicio también se redefinieran. No debe hacerse por conveniencia sin decidir
qué significa una clase para SOCTRA.

#### C. Mayor esfuerzo L1 para FN

No con la formulación actual manteniendo iguales clase, analista y dificultad:

\[
s_{L1}=s_{base}(L1,k)u_{i,k}f(q_a).
\]

La necesidad/recomendación no aparece en esa expresión. `u_(i,k)` varía por
profesional y clase, no por resultado del clasificador. El factor de dificultad
podría producir más servicio si q fuese mayor para ciertos FN, pero el
generador actual no especifica esa dependencia y q no es sinónimo de necesidad
de especialización. Sería una hipótesis diferente, con efectos simultáneos
sobre L2 y los proxies de calidad. El sidecar genérico de escala realizada no
proporciona actualmente una regla configurable de sobreesfuerzo FN L1.

Si se desea conservar la hipótesis «FN requieren más tiempo medio que TN de la
misma clase», la extensión mínima y transparente sería un factor de esfuerzo
L1 específico para FN, aplicado solo dentro del entorno a la duración
realizada y nunca revelado al dispatcher. Se necesitarían justificar y
parametrizar ese factor; no se adopta ni se implementa aquí. Sin él, el modelo
debe declarar el mismo servicio medio TN/FN en L1.

#### D. Menor corrección esperada para FN

La competencia actual puede reflejar diferencias generales de desempeño por
profesional y clase, pero no cambia por necesidad/ruta dentro de una clase.
Las métricas existentes no definen una probabilidad calibrada de resolución:
`S_plus` es atención puntual de una necesidad correctamente recomendada; el
proxy `competence × (1 − 0.35 × difficulty)` es una puntuación modelada, no una
probabilidad observada ni validada. La finalización indica que terminó el
servicio; el SLA indica que acabó antes del deadline; ninguno demuestra que la
investigación fuera correcta.

Con clases que representen de forma explícita tipos de tarea especializada,
los perfiles `c_(i,k)` podrían servir como proxy comparativo de la capacidad
de L1/L2 en esos tipos. No separan, sin embargo, un FN y un TN de la misma
clase. Para afirmar una probabilidad menor de resolución correcta en FN hace
falta definir una función de corrección condicionada por profesional,
actividad/clase y tipo de ruta, además de hipótesis o calibración. No se
introduce una nueva ley de calidad en esta fase.

### Consecuencia para la secuencia del motor

La fórmula anterior de tiempo end-to-end presupone servicio L1 completo y,
después, servicio L2 en positivos. El flujo automático acordado requiere otra
secuencia: recomendación al llegar; investigación L2 para positivas; servicio
L1 para negativas, distinguiendo TN y FN en el esfuerzo. El servicio L1 actual
no se puede reinterpretar simultáneamente como triaje breve de positivas e
investigación completa de negativas. Esa diferencia es una incompatibilidad
del flujo, no un ajuste de calendario o deadline.

El ajuste mínimo futuro requiere cambiar el orden de enrutamiento del
orquestador para que las positivas automáticas no consuman una investigación
L1 completa. Si se conserva la hipótesis de mayor esfuerzo FN, requiere además
la regla ambiental de esfuerzo FN L1 descrita arriba. Ni esta regla ni la
reordenación están implementadas. Si se elige triaje humano, habrá que modelar
un tiempo L1 de triaje separado; no es necesario para el escenario automático
de latencia despreciable.

### Estados de decisión

| Estado | Decisión documentada | Estado |
|---|---|---|
| Triaje V1 | Automático, latencia despreciable y sin consumo humano significativo. | Hipótesis organizativa adoptada; no ejecutada así por el runner actual. |
| TP / FP | Ruta inicial a L2; FP usa trabajo especializado no trivial por defecto. | Regla conceptual; el runner actual pasa antes por servicio L1. Alpha=0.50 en JSON es un escenario previo, no valor empírico ni default consolidado para el nuevo flujo. |
| TN / FN | Permanecen inicialmente en L1; FN puede requerir más esfuerzo y tener menor calidad esperada. | Hipótesis sintética; diferencias de servicio/corrección no están implementadas. |
| Coste y perfiles | Coste no determina velocidad ni competencia; perfiles varían por profesional y clase. | Decisión conservada en el modelo, sin datos empíricos. |
| SLA/calendarios | Reloj natural continuo; L1 cobertura 24x7 por turnos; L2 L-V 09–17. | Reglas consolidadas, pero el runner integrado aún usa todas las alertas en L1 y L1 continuo. |
| Escalado tardío y relevo L1 | No se presupone override posterior ni reasignación entre analistas L1. | Pendiente organizativo. |

### Resultado de auditoría

**Implementado:** servicios por nivel/clase y profesional, elegibilidad,
competencia, dificultad y factor f(q), alpha L2 para FP, necesidad y
recomendación ocultas a dispatchers, calendarios, deadline natural y medición
de finalización puntual.

**Representable por parametrización, pero no configurado como regla general:**
L2 más rápido que L1 en clases seleccionadas; diferencias de competencia y
velocidad por profesional/clase. Los valores deben referirse a actividades
comparables.

**Propuesto pero no implementado:** triaje automático seguido directamente de
investigación en L1 o L2; menor servicio/ninguna investigación L1 completa en
TP/FP; esfuerzo medio FN mayor que TN en la misma clase; diferencia de
corrección esperada entre investigación L1 y especializada L2.

**Pendiente de evidencia:** tiempos por actividad, efecto de especialización
en servicio y corrección, reducción de servicio FP, distribución de q
condicionada por need, competencia calibrada y conducta ante escalado tardío o
relevo. Los supuestos propuestos no son mediciones SOC.

Esta auditoría no cambia parámetros, escenarios, motores, políticas,
clasificadores ni resultados históricos. No se ejecutaron experimentos.
