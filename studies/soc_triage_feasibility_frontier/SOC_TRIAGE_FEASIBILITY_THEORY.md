# SOCTRA–HLS: teoría de la frontera de viabilidad

## Alcance

Este documento formaliza una frontera operativa para configuraciones de clasificadores de escalado y especifica cómo se estima con episodios existentes. La formulación es una síntesis de restricciones estadísticas, de capacidad y de servicio; no se presenta como un teorema nuevo. El estudio usa la campaña congelada de la fase 2 y no ejecuta simulaciones.

Una configuración θ es admisible para demanda λ, plantilla/capacidades (C) y política organizativa (P) si satisface simultáneamente:

\[
\mathcal F_P(\lambda,C)=\{\theta:p_D(\theta)\ge d_{\min},\;\rho_2(\theta,\lambda,C)\le\rho_{\max},\;S_+(\theta,P,\lambda,C)\ge s_{\min}\}.
\]

Las tres condiciones dan fronteras distintas:

1. **Detección:** (p_D\ge d_{\min}).
2. **Capacidad:** carga ofrecida L2 compatible con el margen máximo ρmax.
3. **Servicio:** proporción de todas las necesidades L2 que se encaminan correctamente y se completan dentro del deadline.

Una celda que cumple medias puntuales no queda estadísticamente respaldada automáticamente; el informe de validación distingue admisibilidad puntual, respaldo por límite inferior bootstrap, incompatibilidad y resultado indeterminado.

## Frontera de servicio y descomposición

Sea (Y=1) una necesidad L2 sintética. Bajo aceptación automática, recomendación positiva necesaria para llegar a L2 y ausencia de recuperación posterior de falsos negativos, definimos:

\[
S_+(\theta,P,\lambda,C)=P(\text{necesidad L2 correctamente encaminada y terminada antes del deadline}\mid Y=1).
\]

Una necesidad con recomendación negativa no puede cumplir la definición aunque termine su servicio L1. Por tanto, teóricamente (S_+\le p_D). Definiendo

\[
G=P(\text{investigación L2 terminada antes del deadline}\mid Y=1,\text{recomendación positiva}),
\]

se obtiene (S_+=p_DG). (p_D) resume el filtro de encaminamiento; (G) resume servicio oportuno condicionado a que la recomendación sea positiva. No debe confundirse (S_+) con el SLA global, que incluye las alertas sin necesidad L2 y otras rutas.

### Estimador auditado

Para semillas (j), sea (n_j) el total de necesidades sintéticas (incluye TP y FN) y (t_j) el número de necesidades correctamente recomendadas y terminadas dentro del deadline. El estimador primario es la razón de conteos:

\[
\widehat S_+=\frac{\sum_j t_j}{\sum_j n_j}.
\]

No se promedian tasas por semilla: semillas con (n_j=0) tienen tasa indefinida, no rendimiento cero. No se excluyen semillas positivas tras observar resultados. En los CSV publicados, (t_j) se reconstruye como `necessary_L2_timely_per_need × true_need_count`; el producto debe ser entero dentro de tolerancia numérica (10^{-9}), no superar `TP_count`, y `TP_count + FN_count` debe ser igual al denominador. La auditoría valida estas identidades en todas las filas.

## Frontera de capacidad

Con prevalencia π homogénea y aceptación automática, la fracción positiva esperada es

\[
q(\theta)=\pi p_D(\theta)+(1-\pi)p_{FA}(\theta),\qquad
\lambda_{L2}=\lambda q(\theta).
\]

En un pool homogéneo de capacidad μ, ρL2=λL2/μ y, para π<1,

\[
p_{FA,\max}=\frac{\rho_{\max}\mu/\lambda-\pi p_D}{1-\pi}.
\]

La solución debe limitarse a [0,1] para interpretarla como una frontera de tasa: si el valor no recortado es menor que cero, ni (p_{FA}=0) satisface el límite; si es al menos uno, todo (p_{FA}\in[0,1]) satisface la aproximación. La ecuación supone tasas estacionarias, mezcla fija de tareas, aceptación automática y capacidad efectiva adecuada para esa mezcla. Mide **carga ofrecida**, no trabajo completado ni utilización realizada. Bajo saturación el backlog crece y ρ deja de describir la cola o el SLA por sí solo.

### Capacidad heterogénea

Para clases (k), analistas (a) y elegibilidad (E_a), se asignan tasas fraccionales (x_{ak}\ge0), con

\[
\sum_{a:k\in E_a}x_{ak}=\lambda_kq_k(\theta),\qquad
\sum_k s_{ak}x_{ak}\le\rho_{\max}\quad\forall a.
\]

Aquí (s_{ak}) es el servicio medio del analista (a) para la clase (k). La viabilidad fluida exige que estas restricciones tengan solución; alternativamente, el LP minimiza el máximo uso de analista. Una solución factible es una condición de capacidad promedio, **no** garantía de deadlines en el sistema discreto con colas, variabilidad y reglas de asignación.

El análisis resuelve el LP clase–analista con roster, elegibilidad, mezcla de proyectos y servicios originales. Comprueba numéricamente que la carga normalizada coincide con `effective_capacity` del modelo para la mezcla de L2 inducida. El formulario cerrado de (p_{FA,max}) coincide con el LP aquí porque π se aplica uniformemente a todas las clases: variar (p_{FA}) escala por igual los flujos de clases y no cambia su composición. Con prevalencias específicas por clase esa simplificación no sería válida.

Se desglosan las horas de servicio L2 necesarias recomendadas (TP), innecesarias (FP) y omitidas (FN). Esta partición evita llamar “trabajo reducido” a una necesidad omitida. Las tasas de ofrecimiento no son tasas de finalización.

## Frontera organizativa y admisibilidad estadística

Para políticas (P_1,P_2\), el contraste de servicio es

\[
\Delta(P_1,P_2)=S_+(\theta,P_1,\lambda,C)-S_+(\theta,P_2,\lambda,C).
\]

El diseño es pareado por semilla, con los mismos denominadores de necesidades entre políticas. Se remuestrean identificadores de semilla con reemplazo, usando exactamente los mismos índices de remuestreo para D1, P1, WAPS y todas las condiciones. En cada réplica se suman numeradores y denominadores, se calculan razones por política y sus diferencias. Los IC percentiles de 95% son exploratorios; el máximo de 40 semillas limita su resolución. Réplicas con denominador agregado cero se excluyen de cuantiles y se cuentan; para el caso prioritario no hubo ninguna.

El caso no incorpora incertidumbre sobre las estimaciones publicadas de (p_D,p_{FA}), la prevalencia real, la especificación de necesidad sintética ni los tiempos de servicio. La desigualdad teórica (S_+\le p_D) no obliga a que una tasa empírica pequeña quede por debajo del (p_D) publicado en cada muestra: se verifica frente al (p_D) empírico agrupado y se reporta la variación finita.

## Mapa de restricciones

La configuración de análisis predefine (d_{min}\in\{0.60,0.70,0.80,0.85,0.90,0.95,1.00\}), ρmax ∈ {0.5,0.8,1.0,1.2} y (s_{min}\in\{0.4,0.5,0.6,0.7,0.8,0.9,0.95\}). Se evalúa la rejilla completa para cada configuración, condición de demanda, roster y política compatible. Endurecer cualquier requisito no puede aumentar el conjunto admisible; un test comprueba esta monotonía. La rejilla es una herramienta de lectura, no una selección de requisitos contractuales.

Las prevalencias, definiciones de etiqueta y tasas publicadas se mantienen separadas. La necesidad (Y) es una variable sintética del simulador y la etiqueta histórica de escalado SOCTRA no se interpreta como verdad clínica/operativa de necesidad L2. Las probabilidades publicadas se toman como parámetros fijos de la campaña, no se reestiman con las realizaciones simuladas.
