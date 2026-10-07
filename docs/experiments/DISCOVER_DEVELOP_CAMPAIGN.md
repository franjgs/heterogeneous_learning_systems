# DISCOVER × DEVELOP: pequeña campaña CONFIGURATION × ENVIRONMENT

La campaña reutiliza sin cambios el prototipo `7eb7530`: CES, Bayes, MIS,
acciones, parámetros y MPC. Las únicas dimensiones ambientales ya soportadas
son secuencias explícitas de los dos theta conocidos: persistente, cambio,
alternante y mixto. Incertidumbre inicial, complementariedad CES y ruido están
fijados; variarlos exigiría nueva física y se excluyeron.

La muestra contiene ocho estados canónicos de presupuesto tres, incluyendo
S001--S003 y extremos. Sus descriptores son concentración `sum s_ik^2`,
heterogeneidad inter-agente `sum_i (sum_k s_ik - mean_j sum_k s_jk)^2`,
cobertura por capacidad `sum_i s_ik`, balance, redundancia y `V_K` inicial.
Son descriptivos, no scores de decisión.

Resultado: S030 gana los cuatro entornos de esta campaña congelada. Por tanto,
la hipótesis task-force no queda soportada por la física actual: no se observó
un mapa de regímenes con diferentes geometrías ganadoras. Este resultado se
retiene sin rescate paramétrico. Los pares, distancias continuas de `V_K` y
trayectorias completas se conservan en los CSV de resultados.

La campaña principal tiene 8 configuraciones x 4 secuencias x 3 problemas x 3
decisiones (32 celdas principales y 288 pasos). Para S001--S003 se repitieron
las cuatro secuencias en los cuatro modos A/B/C/D. Todas las comparaciones usan
la misma semilla, secuencia, recursos, acciones y horizonte. `S001`--`S002`
es un par inicial casi igual en `V_K` (diferencia 0.002718), pero no invierte
su orden de forma que produzca un régimen ganador alternativo.

El prototipo sí representa producción, inferencia bayesiana dentro de un frame
conocido, desarrollo MIS histórico y reorganización de asignaciones. Aún no
representa reframing, transferencia, comunicación, restricciones de gestión,
ni una distribución ambiental más amplia que las secuencias explícitas de dos
theta ya definidos. CES, Bayes/belief control y MIS son componentes comprados
o reutilizados; esta campaña no establece una nueva teoría HLS.
