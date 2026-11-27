# SOCTRA-HLS: modelo organizativo canónico

**Fuente de verdad V1:** [configuración organizativa](config/SOC_REFERENCE_ORGANIZATION_V1.json). Los valores nuevos son hipótesis sintéticas, no datos observados de un SOC.

## 1. Objetivo y alcance

Representar tareas y profesionales heterogéneos para estudiar cómo clase, severidad, dificultad, servicio, elegibilidad, competencia, calendarios y organización se relacionan con colas y resultados. Todas las alertas pasan inicialmente por L1; algunas pasan a L2 para trabajo especializado. Los diagnósticos de viabilidad y capacidad son evaluaciones externas, no nuevas políticas. El escenario no representa ni valida una organización cliente concreta.

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
