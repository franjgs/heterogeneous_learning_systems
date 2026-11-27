# Diagnósticos de deadlines y capacidad

## Alcance

`scenario_diagnostics.py` añade evaluaciones ex ante y de trazas para describir
si un escenario puede absorber su trabajo y si sus deadlines son alcanzables.
No implementa ni modifica un dispatcher, clasificador, regla de escalado o
motor. Los informes son posteriores y externos a las decisiones; la
`SimulationRequest` y sus resultados no se mutan.

La API recibe `OrganizationConfig` y `SimulationRequest` de
`execution_api.py`. Por tanto reutiliza las mismas elegibilidades, tiempos
nominales individuales, calendarios y deadlines que la simulación. Los
parámetros de intensidad y mezcla de llegadas se suministran explícitamente en
un `CapacityDemandProfile`: los JSON actuales configuran la organización y el
generador, pero no expresan una serie general de tasas por clase y régimen.
Esto evita inferir una tasa absoluta a partir de un `rho` de otro experimento.

## 1. Factibilidad temporal por alerta

Para cada alerta (a), el slack temporal inicial es

\[
\tau_a=d_a-t_a,
\]

donde $d_a$ es su deadline absoluto y $t_a$ su instante de llegada, en las
unidades temporales de la petición. El servicio nominal individual ya incluye
la velocidad profesional: `AnalystResource.service_by_class[i][k]` corresponde
a $s_{base}(l_i,k)u_{i,k}$. Para dificultad individual $q_a\in[0,1]$,

\[
f(q_a)=1+\beta(q_a-0.5),\quad 0\le\beta<2.
\]

El límite inferior de servicio, sin colas ni calendarios, es

\[
T_{min}(a)=\min_{i\in E_{L1}(k_a)}s_{ia,L1}
+\mathbf{1}(a\text{ requiere L2})\,
 m_a\min_{j\in E_{L2}(k_a)}s_{ja,L2},
\]

con $s_{ia,L1}=s^{nom}_{ia,L1}f(q_a)$,
$s_{ja,L2}=s^{nom}_{ja,L2}f(q_a)$, y $m_a=1$ para trabajo L2 necesario
o el multiplicador alpha para trabajo L2 falso positivo. Alpha nunca escala L1.
El diagnóstico compara esta suma con $\tau_a$; si $T_{min}>\tau_a$, el
plazo es intrínsecamente inviable aun con despacho inmediato. Una holgura
positiva es solo una condición necesaria: no asegura que el dispatcher elija
esa combinación ni que no haya espera.

El mapping requerido `l2_required_by_alert` define la trayectoria que se está
evaluando. Use `route_basis="true_need"` para una evaluación según necesidad
real o `"simulated_route"`/`"scenario_route"` para la ruta efectivamente
simulada. Necesidad real y recomendación SOCTRA son variables distintas. Los
datos ocultos pueden entrar a esta función como evaluación externa, pero nunca
se pasan a una política. `severity_by_alert` es solo una clave de agrupación;
el deadline original de `Alert` es la autoridad y no se recalcula.

### Calendarios

El reporte ofrece dos resultados:

1. `optimistic_slack_h`: límite inferior que ignora turnos.
2. `calendar_slack_h`: holgura hasta la primera finalización que respeta los
   calendarios semanales de cada profesional elegible, sin colas y permitiendo
   que L2 empiece solo tras acabar L1.

El segundo cálculo integra el trabajo a través de ventanas disponibles; no
atribuye servicio fuera del turno. Es una cota de mejor caso con disponibilidad,
no una ejecución de una política: elige el profesional que termina antes en
cada etapa y no reserva recursos compartidos frente a otras tareas. Se marca
como inviable cuando su primera finalización posible excede el deadline.
Igualdad deadline/finalización cuenta como viable; se usa tolerancia numérica
de (10^{-12}) horas para comparar holguras flotantes.

El informe incluye cada alerta y grupos por severidad, clase y ruta con número,
proporción inviable, holgura mínima y cuantiles p10/p50/p90. La holgura se
calcula como `deadline-arrival - T_min`; no es el tiempo de espera observado.

## 2. Capacidad asignable y presión de demanda

Se reutiliza `effective_capacity` de
`soc_human_ai_organization/calibrate_a1_scenarios.py`. Su LP de flujo fraccional
maximiza la tasa común de llegadas para una mezcla fija de clases, respetando
aristas de elegibilidad y cada servicio individual. La extensión opcional del
helper permite vocabularios de clase genéricos y límites de horas disponibles
por analista. La llamada histórica de tres argumentos conserva clases y
capacidad unitaria por hora.

Formalmente, para tasa de capacidad \(\mu\), proporción de clase \(w_k\),
flujo fraccional \(x_{ik}\) y fracción disponible \(a_i\) del profesional:

\[
\max_{\mu,x}\;\mu\quad\text{sujeto a}\quad
\sum_{i:k\in E_i}x_{ik}=\mu w_k\;(\forall k),\qquad
\sum_{k\in E_i}s_{ik}x_{ik}\le a_i\;(\forall i),\qquad x_{ik}\ge0.
\]

En la notación del código, la elegibilidad es por analista, es decir
\(k\in E_i\). \(x_{ik}\) y \(\mu\) se expresan en tareas por hora, los
servicios \(s_{ik}\) en horas por tarea y \(a_i=1\) para 24x7 o la fracción
semanal disponible para un calendario restringido. Una clase con demanda y sin
ninguna arista elegible se informa como `infeasible_eligibility`.

Para una clase (k), las tasas entrantes por régimen (r) son
\(\lambda_{rk}\). El LP de L1 usa la mezcla
\(\lambda_{rk}/\sum_k\lambda_{rk}\). Su capacidad asignable es
\(\mu_{1r}\) y la carga relativa
\(\rho_{1r}=\sum_k\lambda_{rk}/\mu_{1r}\).

En modo ex ante, prevalencia \(\pi_k\), sensibilidad \(p_{D,k}\) y tasa de
falsos positivos \(p_{FA,k}\) dan

\[
p_{+,k}=\pi_kp_{D,k}+(1-\pi_k)p_{FA,k},\qquad
\lambda_{2,rk}=\lambda_{rk}p_{+,k}.
\]

El servicio medio por recomendación L2 incorpora el esfuerzo esperado de TP y
FP:

\[
\bar m_{k}=\frac{\pi_kp_{D,k}E[f(q)\mid k,Y=1]
+\alpha(1-\pi_k)p_{FA,k}E[f(q)\mid k,Y=0]}{p_{+,k}}.
\]

Por defecto, la hipótesis sintética es $q\sim Beta(2,2)$, independiente de
clase, necesidad y recomendación. Como $E[q]=0.5$, ambos factores esperados
son uno y cambiar beta no altera la demanda media ex ante. La variabilidad sí
afecta alertas individuales y deadlines. Si existe asociación de dificultad
con clase o necesidad, se pueden pasar medias condicionales de $q$ por clase
y estado. La fórmula declara además la hipótesis de independencia de la
recomendación respecto a dificultad dentro de cada estrato de necesidad. Si
esa hipótesis no es defendible, use la vía de traza realizada.

`realized_demand_regime()` calcula a partir de alertas existentes tasas por
clase, tasas L2 y medias observadas de $f(q)$ y $m_af(q)$. Requiere mapas
explícitos de ruta, necesidad real y dificultad; no genera datos aleatorios.
`route_basis` deja constancia de si se midió la ruta simulada, una ruta de
escenario o la necesidad real como contrafactual. Esta vía conserva
correlaciones observadas entre clase, dificultad, necesidad y ruta.

El LP de L2 usa la mezcla de alertas recomendadas/encaminadas y los servicios
individuales ajustados por su factor esperado o realizado. Devuelve capacidad
asignable \(\mu_{2r}\), carga relativa \(\rho_{2r}\), clases sin elegibilidad,
profesionales saturados en el óptimo fluido y una convención separada de horas
de trabajo ofrecidas. La carga de trabajo ofrecida usa la media de servicio de
profesionales elegibles, como en la auditoría Q1; la capacidad se determina por
el LP y no por esa media.

Los calendarios limitan las horas de cada persona mediante la fracción de
tiempo disponible en la semana (unión de sus ventanas). Así la capacidad es
promedio asignable con calendarios, no capacidad instantánea: no garantiza que
las horas estén disponibles cuando llega una alerta ni modela colas o plazos.
La utilización observada sigue siendo una métrica de ejecución (`Outcome` o
`ExecutionResult`); `analyst_utilization_at_capacity` describe el óptimo LP,
no utilización simulada.

En este informe, **capacidad nominal** es la capacidad configurada sin filtrar
clases ni horarios; **capacidad asignable** es \(\mu\) del LP; **demanda
ofrecida** es la tasa de llegadas y sus horas de servicio esperadas/realizadas;
**utilización usada** se lee de una ejecución, no se infiere de \(\rho\).

Si \(\rho>1\), el régimen estacionario presenta sobrecarga estructural para
esa mezcla. Si \(\rho\le1\), hay capacidad media suficiente según el LP, sin
garantía de estabilidad en escenarios no estacionarios o de deadlines. Una
cola positiva con carga media suficiente es evidencia de congestión temporal;
`classify_regime_pressure()` lo informa separadamente. Un régimen posterior
con carga suficiente no implica que el trabajo pendiente ya se haya drenado.

## 3. Pulsos, cambios de mezcla y recuperación

`DemandRegime` representa segmentos de tasa constantes y tasas por clase. Se
puede construir una secuencia para describir estado estacionario, pulso,
sobrecarga sostenida, cambio de mezcla y recuperación. No genera llegadas ni
reemplaza los mecanismos existentes de `ScenarioConfig.burst_window`, los
perfiles de llegadas y los estudios de sobrecarga/no estacionariedad en
`soc_human_ai_organization`.

Para recuperación, `QueueObservation` consume series ya disponibles con colas
L1/L2 y trabajo pendiente. `assess_queue_recovery()` aplica un criterio
explícito: ambas colas y trabajos pendientes deben permanecer por debajo de
umbrales configurables durante `sustain_h`. El tiempo de recuperación es el
primer punto muestreado de esa ventana. La garantía solo vale en la resolución
de muestreo; no afirma que no hubo excursiones entre observaciones.

## 4. Uso

```python
from studies.soc_triage_hls_availability_robustness.scenario_diagnostics import (
    CapacityDemandProfile, DemandRegime, assess_capacity,
)

from studies.soc_triage_hls_availability_robustness.scenario_loader import load_scenario

loaded = load_scenario(".../SYNTHETIC_SOC_24x7.json")
profile = CapacityDemandProfile(
    regimes=(DemandRegime("steady", 0, 168,
                          {"portfolio_top5": 0.8,
                           "portfolio_next5": 0.3,
                           "portfolio_tail": 0.1}),),
    prevalence_by_class={"portfolio_top5": .02, "portfolio_next5": .01,
                         "portfolio_tail": .005},
    sensitivity_by_class={"portfolio_top5": .84, "portfolio_next5": .84,
                          "portfolio_tail": .84},
    false_positive_rate_by_class={"portfolio_top5": .045, "portfolio_next5": .045,
                                  "portfolio_tail": .045},
    alpha=.25,
)
capacity = assess_capacity(loaded.organization, profile)
```

La ilustración numérica es una parametrización de ejemplo, no dato operacional.
Los valores por clase deben venir del escenario experimental. Para deadlines,
construya la petición común con alertas y pase un mapping explícito
`l2_required_by_alert` y su `route_basis`.

## 5. Interpretación y límites científicos

**Propiedades matemáticas:** el mínimo de servicios elegibles es una cota
inferior; $T_{min}>\tau$ prueba imposibilidad sin colas. El LP entrega la tasa
máxima fluida para la mezcla declarada y las restricciones de elegibilidad y
horas disponibles. Bajo $q\sim Beta(2,2)$ independiente, $E[f(q)]=1$.

**Hipótesis sintéticas:** servicios nominales codifican eficiencia individual;
la distribución Beta(2,2), independencia de dificultad y modelo de
clasificación son entradas del escenario, no mediciones empíricas. Para la
capacidad con calendarios, la disponibilidad semanal media aproxima una
restricción temporal agregada.

**Diagnósticos calculados:** inviabilidad por alerta, holguras, carga/capacidad
LP y resumen de colas se determinan para las entradas suministradas.

### Cálculos ilustrativos

- Con servicio L1 mínimo de 1 h, servicio L2 mínimo de 2 h y slack de 2,5 h,
  una ruta L1+L2 requiere al menos 3 h y queda intrínsecamente inviable con
  holgura de −0,5 h. Para una llegada el viernes a las 16:00, dos servicios de
  1 h son viables en el límite sin turnos si el plazo deja 3 h; con turnos
  lunes-viernes 09:00–17:00, L1 acaba el viernes a las 17:00 y L2 no termina
  hasta el lunes a las 10:00.
- Con un especialista exclusivo para cada una de dos clases y 1 h de servicio,
  una mezcla 50/50 tiene capacidad fluida de 2 alertas/h. A 0,2 alertas/h,
  \(\rho=0,1\). En un pulso de 4 alertas/h con mezcla 25/75, la clase del
  especialista más cargado limita la capacidad a 1,33 alertas/h y
  \(\rho\approx3\): la capacidad total del equipo no se obtiene sumando
  productividades medias sin considerar elegibilidad.
- Si \(\pi=0,2\), \(p_D=0,5\), \(p_{FA}=0,1\), servicio L2 nominal de 1 h y
  \(\alpha=0,25\), el modelo espera 0,18 recomendaciones L2 por alerta y
  0,12 h de trabajo L2 ofrecido por alerta entrante. Con dificultad
  independiente Beta(2,2), beta no cambia esa media esperada; puede cambiar la
  carga observada en una traza concreta.

**Resultados no obtenidos:** estos diagnósticos no prueban estabilidad general,
SLA organizativo, una política superior ni mejoras de rendimiento. Las
consecuencias para esperas, deadlines y desempeño requieren simulación
experimental emparejada, con semillas y escenarios identificados. La
factibilidad temporal es necesaria, no suficiente; la carga relativa es un
indicador de presión, no una garantía de servicio.
