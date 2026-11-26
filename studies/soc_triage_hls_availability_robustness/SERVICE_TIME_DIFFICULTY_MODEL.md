# Dificultad, servicio efectivo y calendarios en SOCTRA-HLS

## Motivación y alcance

El tiempo de procesamiento depende de la clase de tarea, del nivel L1/L2, del
servicio nominal del profesional y de la dificultad particular de la alerta.
La extensión modela la variación de esfuerzo entre alertas sin revelar su
dificultad a D1, P1 o WAPS. Se apoya en las dos interfaces de ejecución
existentes: el motor continuo histórico y el motor de calendario con
suspensión y reanudación.

Los resultados históricos corresponden al modelo de servicio original. En
ellos la dificultad ya afecta a la calidad modelada, pero no modifica el
tiempo de servicio. El nuevo término es optativo y `difficulty_service_beta`
vale cero si se omite. No se han recalculado ni reinterpretado los resultados
publicados.

## Modelo matemático

Para alerta `a`, profesional `i`, nivel `l_i` y clase `k_a`, el servicio
previsto es

\[
\widehat{s}_{ia}=s_{\mathrm{base}}(l_i,k_a)u_{i,k_a}.
\]

El servicio efectivo por dificultad es

\[
s_{ia}=\widehat{s}_{ia}f(q_a),\qquad
f(q_a)=1+\beta(q_a-\tfrac12),\quad 0\leq\beta<2.
\]

`ŝ` y `s` se expresan en horas en los experimentos SOC. El producto
`s_base * u` se representa mediante los servicios nominales individuales por
profesional y clase ya admitidos por la API. No se introduce otra variable de
eficiencia redundante. La dificultad `q_a` está entre cero y uno. La restricción
`beta < 2` asegura que `f(q)` sea estrictamente positivo para todo `q` en ese
intervalo.

Para una alerta que entra en L2, el modelo experimental incorpora el
multiplicador alfa ya existente:

\[
s_{L2,ia}=s_{\mathrm{base}}(L2,k_a)u_{i,k_a}f(q_a)m_a,
\qquad
m_a=\begin{cases}
1,&\text{necesidad real de L2},\\
\alpha,&\text{falso positivo escalado}.
\end{cases}
\]

Los valores históricos de sensibilidad de alfa son 0.25, 0.50, 0.75 y 1.00.
El factor total se calcula una vez como `m_a * f(q_a)`. Dificultad se aplica
con el mismo valor `q_a` en L1 y L2. Alfa se aplica solo al servicio L2; no
altera el servicio L1.

## Distribución y normalización

El generador Q1 ya produce una dificultad `row.difficulty` con
`Beta(2,2)`. La integración reutiliza ese valor, sin generar una segunda
realización. Beta(2,2) es una hipótesis sintética acotada, simétrica y centrada
en 0.5; no se ha ajustado ni validado con datos observacionales de SOC.

Para `q ~ Beta(2,2)`,

\[
\mathrm{E}[q]=\frac{2}{2+2}=\frac12,
\qquad
\mathrm{E}[f(q)]=1+\beta(\mathrm{E}[q]-\tfrac12)=1.
\]

Por ello, el servicio efectivo esperado condicional a profesional, nivel y
clase coincide con el previsto, bajo la distribución especificada. Para L2,
esa igualdad condicional a la ruta TP/FP requiere además que dificultad sea
independiente de necesidad y recomendación, como asume el generador. Alfa sí
reduce el esfuerzo medio asignado a los falsos positivos. La normalización no
implica igualdad en cada traza ni para cada analista después de la asignación.

## Servicio previsto e información de las políticas

`AnalystResource.forecast_service_by_class` es el dato ex ante de despacho; si
se omite, hereda el servicio nominal individual. El servicio nominal/efectivo
base está en `service_by_class`. En el experimento integrado, el forecast de L2
puede incorporar la mezcla esperada de TP y FP derivada del operating point y
alfa, pero no usa las etiquetas reales de alertas individuales.

`EnvironmentRealization` conserva la información ambiental. Su
`service_scale_by_alert` existente representa `m_a`, como alfa para un falso
positivo; `difficulty_by_alert` y `difficulty_service_beta` representan
`q_a` y beta. `realized_scales_for()` compone ambos factores y devuelve la
escala que recibe el motor. Las políticas no reciben dificultad, necesidad
real, etiqueta TP/FP ni la escala realizada. D1, P1 y WAPS siguen usando solo
información disponible antes del procesamiento.

En el runner ampliado, la escala alfa solo se crea para las alertas enrutadas a
L2. El servicio L1 usa el factor de dificultad sin alfa. Cuando beta vale cero,
la escala L2 es exactamente uno para TP y alfa para FP, y el runner conserva
la secuencia aleatoria histórica.

## Etapas L1/L2, calendarios y deadlines

L1 y L2 conservan el mismo identificador, la misma dificultad y el deadline
absoluto original de la alerta. La finalización end-to-end incluye la espera y
el servicio de L1, la espera en L2 y el servicio efectivo de L2 cuando existe
escalado. La composición no modifica la regla de routing SOCTRA ni la decisión
de escalado.

El motor continuo programa la finalización con el trabajo efectivo completo.
El motor de calendario recibe ese mismo trabajo total requerido, pero lo
consume solo mientras el profesional está disponible. Al terminar un turno,
el motor conserva el trabajo remanente y la propiedad del analista, cierra el
segmento trabajado y reanuda el remanente en el siguiente turno. Ni dificultad
ni alfa cambian el calendario, provocan reasignación o alteran el deadline.

Las interfaces conservan el orden de eventos propio de cada motor. La
compatibilidad entre ellos se comprueba en escenarios equivalentes y sin
empates ambiguos; no se afirma equivalencia exacta para todas las trazas ni se
modifican las reglas de suspensión o asignación persistente.

## Interpretación experimental

Variar beta cambia la dispersión del esfuerzo entre alertas por su dificultad,
mientras mantiene en expectativa la escala media `f(q)` en uno bajo
`Beta(2,2)`. Las llegadas, clases, dificultad generada, operating point,
recomendaciones, roster, servicio nominal y política pueden mantenerse
emparejados. Alfa mantiene su interpretación previa para el esfuerzo de FP en
L2.

Los cambios de duración pueden modificar disponibilidad futura, colas,
congestión, esperas y cumplimiento de plazos, aun cuando la media de `f` sea
uno. El signo y la magnitud de esos efectos dependen del escenario y requieren
experimentación. La integración del modelo no es evidencia de mejora o
deterioro del rendimiento.

## Límites científicos

- `Beta(2,2)`, la función lineal `f`, beta, alfa y la relación sintética entre
  dificultad y calidad no están calibrados empíricamente.
- `E[f(q)]=1` es una propiedad matemática bajo `q ~ Beta(2,2)`, no una
  afirmación sobre tiempos observados en un SOC real.
- La asignación puede seleccionar alertas con una distribución de dificultad
  distinta de la distribución global.
- Los estudios publicados utilizaron beta cero: sus resultados no incluyen
  dificultad en los tiempos de servicio.
- No se ha ejecutado una campaña con beta positivo; no hay resultados sobre su
  efecto organizativo.

## Referencia de implementación

La integración se configura con el campo opcional `difficulty_service_beta`
del JSON de la campaña (valor predeterminado cero) y los valores de dificultad
ya presentes en la traza Q1. `EnvironmentRealization.realized_scales_for()`
compone dificultad y alfa. `ContinuousBackend` mantiene el camino continuo
histórico y usa el motor especializado existente cuando se suministra
necesidad oculta; `CalendarBackend` pasa el servicio previsto al dispatcher y
el servicio base escalado al motor con calendario. `availability_engine`
acumula el trabajo durante los intervalos laborales; los deadlines y las
configuraciones históricas no se reescriben.
