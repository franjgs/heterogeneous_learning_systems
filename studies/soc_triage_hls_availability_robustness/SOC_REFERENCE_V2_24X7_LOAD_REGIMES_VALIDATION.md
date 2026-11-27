# Validación de carga ordinaria, pulso y recuperación — V2_24X7

> **NEW MODEL / MODELO NUEVO:** perfil de demanda del flujo de investigación única; es una ejecución diagnóstica, no validación del OLD MODEL.

**Tipo:** diagnóstico técnico reproducible de una ejecución; no campaña ni comparación de políticas.  
**Commit de partida:** `ffeb64606f62560870f6142f7bbd8ec3a739fde0`.  
**Configuración:** [`SOC_REFERENCE_V2_24X7_LOAD_REGIMES.json`](config/SOC_REFERENCE_V2_24X7_LOAD_REGIMES.json).  
**Semilla:** 998001.  
**Flujo:** `triage_single_investigation`; `CalendarBackend`; D1 según la configuración fija.

## 1. Qué se cambió y cómo reproducirlo

La configuración se derivó de `SOC_REFERENCE_ORGANIZATION_V2_24X7.json`. Se mantuvieron la organización completa (roster, calendarios continuos, elegibilidad, competencia, eficiencia y servicios), forecast, clasificador y sus tasas, mezcla/severidad, prevalencia sintética, alpha=0.50, beta=0, gamma=1, deadline, horizonte de admisión (168 h), evaluación/drenaje (336 h), política configurada y semilla 998001. Solo cambian las intensidades y sus ventanas en `demand_profile.regimes`, más metadatos de identificación/descripción del perfil.

Ventanas desde lunes 00:00, en horas naturales:

| Régimen | Intervalo | Duración | rho_L1 objetivo |
|---|---:|---:|---:|
| Ordinario | [0, 96) | 96 h (4 días) | 0.85 |
| Pulso | [96, 120) | 24 h (1 día) | 1.25 |
| Recuperación | [120, 168) | 48 h (2 días) | 0.65 |

Se eligieron cuatro días ordinarios para observar el equipo bajo carga menor a capacidad antes del pulso, un pulso de 24 h para producir acumulación medible y 48 h de recuperación para permitir observar el drenaje sin modificar el horizonte semanal. Se reutiliza el generador Poisson no homogéneo: tasa base ordinaria, multiplicador de pulso acotado y tasa posterior de recuperación, con la misma mezcla de clases en los tres regímenes.

Comandos reproducibles desde la raíz:

```bash
python studies/soc_triage_hls_availability_robustness/run_scenario.py --config studies/soc_triage_hls_availability_robustness/config/SOC_REFERENCE_V2_24X7_LOAD_REGIMES.json --seed 998001
python studies/soc_triage_hls_availability_robustness/analyze_reference_organization.py --config studies/soc_triage_hls_availability_robustness/config/SOC_REFERENCE_V2_24X7_LOAD_REGIMES.json
python studies/soc_triage_hls_availability_robustness/analyze_load_regimes.py --seed 998001
```

`analyze_load_regimes.py` es un evaluador que invoca los motores existentes; no añade generador, motor, despacho ni mecanismo de control. Sus etiquetas de referencia/confusión se usan ex post. El dispatcher no recibe dificultad, confusión ni multiplicadores realizados.

## 2. Capacidad y tasas derivadas

Se reutilizó `scenario_diagnostics.assess_capacity`, que resuelve el LP de capacidad asignable condicionado a la mezcla, servicio, disponibilidad y elegibilidad, apoyándose en `effective_capacity`. Para la organización individualmente 24x7 y el modelo V2 actual:

- **μ_L1 = 17.034626 alertas destinadas a L1 por hora natural.**
- **μ_L2 = 13.045624 alertas destinadas a L2 por hora natural.**
- No hay clases sin profesional elegible. Los cinco L1 cubren las tres clases; cada clase L2 tiene dos especialistas elegibles.

La estimación orientativa previa μ_L1≈19.5 no coincide con este LP, que usa los servicios/eficiencias actuales y la mezcla enrutada del flujo único. Para fijar el escenario se usa el resultado reproducible de la formulación vigente, no aquella aproximación.

Con las probabilidades sintéticas homogéneas de referencia (prevalencia π=0.10, sensibilidad=0.8421, tasa de falso positivo=0.045):

\[
p_{L2}=\pi\,Se+(1-\pi)\,FPR=0.12471,\qquad p_{L1}=1-p_{L2}=0.87529.
\]

Por tanto, el objetivo L1 se impone sobre la tasa **de tareas que llegan a L1**:

\[
\lambda_{total}=\frac{\rho_{L1}\,\mu_{L1}}{p_{L1}},\quad
\lambda_{L1}=p_{L1}\lambda_{total},\quad
\lambda_{L2}=p_{L2}\lambda_{total}.
\]

No se igualan las utilizaciones de niveles ni se trata la tasa total de alertas como capacidad L1. Se mantiene la mezcla de clase Top5/Next5/Tail = 0.50/0.30/0.20 y severidades alta/media/baja = 0.20/0.30/0.50. Las tasas configuradas por clase (alertas por hora natural) quedan:

| Régimen | portfolio_top5 | portfolio_next5 | portfolio_tail | Total |
|---|---:|---:|---:|---:|
| Ordinario | 8.271220 | 4.962732 | 3.308488 | 16.542439 |
| Pulso | 12.163558 | 7.298135 | 4.865423 | 24.327117 |
| Recuperación | 6.325050 | 3.795030 | 2.530020 | 12.650101 |

Las tasas agregadas por nivel y la carga laboral esperada son:

| Régimen | λ total | λ destinada L1 | λ destinada L2 | Trabajo efectivo esperado L1 (h-persona/h) | Trabajo esperado L2 (h-persona/h) |
|---|---:|---:|---:|---:|---:|
| Ordinario | 16.542439 | 14.479432 | 2.063008 | 4.271432 | 0.476070 |
| Pulso | 24.327117 | 21.293282 | 3.033835 | 6.281518 | 0.700104 |
| Recuperación | 12.650101 | 11.072507 | 1.577594 | 3.266389 | 0.364054 |

Capacidad y rho del LP por régimen:

| Régimen | Nivel | Capacidad asignable de su flujo (alertas/h) | Tasa esperada destinada al nivel | rho recalculado | Clases sin servicio |
|---|---|---:|---:|---:|---|
| Ordinario | L1 | 17.034626 | 14.479432 | 0.850 | ninguna |
|  | L2 | 13.045624 | 2.063008 | 0.158 | ninguna |
| Pulso | L1 | 17.034626 | 21.293282 | 1.250 | ninguna |
|  | L2 | 13.045624 | 3.033835 | 0.233 | ninguna |
| Recuperación | L1 | 17.034626 | 11.072507 | 0.650 | ninguna |
|  | L2 | 13.045624 | 1.577594 | 0.121 | ninguna |

Las capacidades son para los respectivos flujos enrutados y la mezcla indicada. La oferta L2 incorpora expected TP/FP, alpha=0.50 y el forecast temporal esperado. Son tasas fluidas de asignación, no throughput garantizado ni medida de plazo.

## 3. Realización con semilla 998001

La semilla produjo **2,812 alertas**. Las tasas empíricas fluctúan respecto a las configuradas, como corresponde a una realización Poisson. Todos los tiempos son horas naturales desde lunes 00:00.

| Régimen | Alertas observadas (tasa/h) | L1 / L2 (tasas/h) | TP / FP / TN / FN | SLA por cohorte: puntual / tarde / pendiente |
|---|---:|---:|---:|---:|
| Ordinario, 96 h | 1,606 (16.729) | 1,425 / 181 (14.844 / 1.885) | 123 / 58 / 1,402 / 23 | 1,606 / 0 / 0 |
| Pulso, 24 h | 601 (25.042) | 533 / 68 (22.208 / 2.833) | 48 / 20 / 528 / 5 | 541 / 60 / 0 |
| Recuperación, 48 h | 605 (12.604) | 532 / 73 (11.083 / 1.521) | 53 / 20 / 526 / 6 | 596 / 9 / 0 |
| **Total** | **2,812** | **2,490 / 322** | **224 / 98 / 2,456 / 34** | **2,743 / 69 / 0** |

Se realizaron 2,812 investigaciones únicas: 2,490 L1 y 322 L2. No hubo tareas pendientes al corte de 336 h. 2,743 (97.55%) terminaron dentro del deadline; 69 (2.45%) terminaron tarde y no fueron canceladas. Los 69 retrasos fueron L1: 68 TN y 1 FN; por severidad, 10 altas, 15 medias y 44 bajas. Todas las rutas L2 finalizaron dentro del SLA en esta realización.

El diagnóstico ex ante por tiempos activos y calendarios continuos da 0% de deadlines intrínsecamente inviables para este perfil. Los incumplimientos observados no proceden de cierres de calendario: son compatibles con la congestión transitoria L1 y las esperas en cola. La realización única no separa causalmente cada decisión de asignación.

## 4. Congestión, utilización y drenaje

Las horas de trabajo ejecutadas en cada intervalo se dividen por las horas-persona disponibles (cinco L1 y tres L2 continuamente disponibles). El trabajo efectivo por cohorte de llegada es el servicio total de esas alertas, asignado a su intervalo de llegada; el trabajo ejecutado por intervalo también incluye trabajo pendiente de intervalos previos.

| Régimen | Nivel | Trabajo efectivo de cohorte | Trabajo ejecutado durante intervalo | Horas-persona disponibles | Utilización observada |
|---|---|---:|---:|---:|---:|
| Ordinario | L1 | 416.978 h | 416.380 h | 480 h | 86.7% |
|  | L2 | 41.210 h | 40.966 h | 288 h | 14.2% |
| Pulso | L1 | 154.235 h | 119.974 h | 120 h | 100.0% |
|  | L2 | 16.330 h | 15.898 h | 72 h | 22.1% |
| Recuperación | L1 | 156.502 h | 191.090 h | 240 h | 79.6% |
|  | L2 | 17.836 h | 18.513 h | 144 h | 12.9% |

El pulso ofrece a L1 unos 6.282 h-persona de trabajo por hora frente a cinco horas-persona disponibles, y la ejecución ocupa las 120 h-persona del día. La cola sin iniciar alcanzó un máximo **muestreado cada hora de 122 alertas** al final del pulso (t=120 h); además había cinco investigaciones asignadas con 0.774 h de trabajo residual registrado. El esfuerzo futuro de las alertas todavía en cola no está realizado ni asignado a un profesional; se conserva como cantidad de alertas, no se inventa duración efectiva.

| Instante | Estado L1: en cola / en servicio / residual asignado | Estado L2: en cola / en servicio / residual asignado |
|---:|---:|---:|
| t=96 h, inicio pulso | 0 / 5 / 0.598 h | 0 / 1 / 0.244 h |
| t=102 h | 28 / 5 / 0.779 h | 0 / 1 / 0.179 h |
| t=108 h | 73 / 5 / 0.869 h | 0 / 0 / 0 h |
| t=114 h | 109 / 5 / 0.539 h | 0 / 0 / 0 h |
| t=120 h, inicio recuperación | 122 / 5 / 0.774 h | 0 / 2 / 0.677 h |
| t=126 h | 97 / 5 / 0.354 h | 0 / 0 / 0 h |
| t=132 h | 53 / 5 / 0.857 h | 0 / 0 / 0 h |
| t=138 h | 23 / 5 / 0.827 h | 0 / 0 / 0 h |
| t=144 h | 0 / 4 / 0.290 h | 0 / 0 / 0 h |
| t=168 h, fin de admisión | 0 / 4 / 0.272 h | 0 / 0 / 0 h |

Los estados de trabajo residual corresponden solo a tareas iniciadas; cola y residual se muestran por separado. Los muestreos cada seis horas sirven para ilustrar la trayectoria, mientras que el máximo indicado procede de muestreo horario y puede no ser el máximo instantáneo exacto.

### Criterio explícito de recuperación

Se considera recuperado al finalizar el régimen de recuperación (t=168 h) si, en ambos niveles, (i) las alertas en cola son cero y (ii) el residual exacto de tareas ya asignadas no supera el observado al inicio del pulso (t=96 h). No es suficiente que rho esperado sea menor que uno.

El criterio se cumple: L1 pasa de cola 122 al inicio de recuperación a 0 al final, y su residual de tareas asignadas pasa de 0.774 h al comienzo de recuperación a 0.272 h al final; L2 termina con cola y residual cero. La cola L1 llegó a cero en el muestreo t=144 h; las alertas de la cohorte del pulso finalizaron como máximo en t=130.807 h. La última tarea de la cohorte de recuperación terminó en t=168.139 h, apenas después del fin de admisión y mucho antes del corte de evaluación.

Esto diferencia: (a) **capacidad disponible:** la configuración mantiene 5×24 y 3×24 horas-persona por día; (b) **reducción de cola:** el exceso del pulso se drena durante la recuperación; (c) **estado comparable:** en t=168 no hay cola y el residual asignado L1 es menor que el de t=96. Aun con recuperación del backlog, 69 deadlines ya se habían incumplido.

L2 se mantiene holgado: rho máximo esperado 0.233 en el pulso, utilización observada 22.1% y sin cola horaria en la traza. Esto no es evidencia de una capacidad L2 óptima; refleja el perfil de referencia y sus tasas positivas, no un objetivo de igualdad entre niveles.

## 5. Validación, límites e interpretación

Pruebas y comprobaciones focalizadas:

- `test_scenario_integration.py` comprueba que la organización completa, generador/clasificador, deadlines, política, costes, mezcla, severidades, prevalencia, alpha/beta/gamma y semilla coinciden con V2_24X7; solo difieren los tres intervalos/tasas de llegada y metadata de identificación.
- La traza con seed 998001 se reprodujo idénticamente al regenerarla. La clasificación de llegadas por las ventanas configuradas da 1,606 / 601 / 605 alertas.
- El LP verificó rho L1 = 0.85 / 1.25 / 0.65 (tolerancia numérica) y las cargas L2 recalculadas.
- El evaluador comparó estados SLA, ruta única, colas, suspensiones y estados de recuperación. No se cambió ninguna decisión del motor.

Los valores de llegada, prevalencia, clasificador y servicio son hipótesis sintéticas. El reporte se basa en una semilla y una asignación D1 únicamente para ejecutar la configuración congelada; no estima el comportamiento esperado de una política, no compara D1/P1/HLS-B y no demuestra resultados generalizables. El pulso y la recuperación sí producen la dinámica mecánica requerida en esta realización, pero su frecuencia, cola típica, probabilidad de SLA y recuperación deberían caracterizarse con réplicas en una campaña futura antes de sostener conclusiones estadísticas.

Los costes horarios relativos se heredan sin alteración y no se convierten en costes de personal real. Los motores, políticas, clasificadores, V2_24X7 de carga baja, escenarios históricos, semillas y manuscritos LaTeX permanecen intactos.
