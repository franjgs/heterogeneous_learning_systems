HLS — CE-04 / E3
ADENDA AL PROTOCOLO EXPERIMENTAL
Fecha: 26/10/2026
Estado: PENDIENTE DE CONGELACIÓN

1. COMPOSICIÓN H0–H2

Aplicar el generador de competencias de E1.

Para cada tipo de tarea k y tamaño N:

(1/N) × Σ_i p(i,k) = μ_k

La igualdad debe cumplirse en H0, H1 y H2.

H0: competencias homogéneas.
H1: dispersión intermedia y especialización moderada.
H2: mayor dispersión y especialización.

Mantener constantes:
- Competencia media por tipo de tarea.
- Número de agentes.
- Capacidad operativa agregada.
- Presupuesto de recursos.

La dispersión y las correlaciones entre competencias
constituyen las diferencias de composición.

Verificar las igualdades numéricamente para cada
organización y semilla.

IMPORTANTE:
La especificación de E1 debe fijar los perfiles y
sus parámetros antes de ejecutar el experimento.
No reconstruirlos arbitrariamente.

2. POLÍTICAS ORGANIZATIVAS

P0: MENOR CARGA ESPERADA
Asignar al agente con menor carga de trabajo
pendiente estimada, sin utilizar competencias.

P1: INFORMACIÓN COMPLETA
Asignación informada por competencia verdadera,
tiempo esperado de servicio y plazo.

P2: COMPETENCIAS ESTIMADAS
Misma función de decisión que P1, sustituyendo
competencias verdaderas por estimaciones obtenidas
exclusivamente de observaciones anteriores.

P3: ADAPTATIVA CONTEXTUAL
Utilizar contexto observable, historial y estado
actual para adaptar la asignación.

P3 debe quedar definido mediante una política
existente del laboratorio, con configuración fija.

No introducir un algoritmo nuevo.

P1 es una referencia informacional, no un óptimo
global de planificación.

3. MATRIZ FACTORIAL

Composición: H0, H1, H2.
Política: P0, P1, P2, P3.
Escala: 12, 24, 48.

3 × 4 × 3 = 36 condiciones.

Campaña completa:
36 × 30 = 1.080 simulaciones.

Piloto técnico:
36 × 3 = 108 simulaciones.

Mantener cooperación desactivada.

4. CONTRASTES CONFIRMATORIOS

Para cada escala:

C1. H2-H0 bajo P1:
    efecto de composición con información completa.

C2. P1-P0 bajo H2:
    valor de asignación informada.

C3. P2-P1 bajo H2:
    pérdida por estimación imperfecta.

C4. P3-P2 bajo H2:
    valor incremental de adaptación contextual.

C5. Interacción composición-organización:
    (H2-H0 bajo P3) - (H2-H0 bajo P0).

Escala:
Contrastar cada efecto entre N=12, 24 y 48
manteniendo carga relativa constante.

Efectos expresados en puntos porcentuales
de tareas correctas y terminadas a tiempo.

IC del 95 % sobre diferencias pareadas por semilla.
Ajuste Holm para la familia confirmatoria.
TOST con margen ±2 pp para equivalencia.

No interpretar ausencia de significación
como equivalencia.

5. CONTROLES DE INFORMACIÓN

Todas las políticas comparten:
- Llegadas observadas.
- Tipos de tarea.
- Plazos.
- Disponibilidad y carga.
- Historial de resultados efectivamente observados.

P1 dispone adicionalmente de competencias verdaderas.

P2 y P3 no acceden a:
- Competencias verdaderas.
- Resultados futuros.
- Llegadas futuras.
- Etiquetas o resultados contrafactuales.
- Información posterior al instante de decisión.

Las estimaciones se actualizan únicamente después
de observar el resultado de una tarea ejecutada.

Los resultados de tareas rechazadas o no asignadas
no pueden utilizarse como observaciones supervisadas.

Congelar:
- Inicialización de estimadores.
- Regla de actualización.
- Política contextual P3.
- Desempates.
- Tratamiento de tareas pendientes.

No utilizar resultados del piloto para ajustar
las políticas.

6. COSTE COMPUTACIONAL

Mantener horizonte 400 y carga proporcional a N.

Llegadas esperadas por simulación:
N=12: 2.640
N=24: 5.280
N=48: 10.560

Campaña completa:
360 simulaciones por tamaño.

Total esperado:
6.652.800 tareas llegadas.

Piloto:
665.280 tareas llegadas.

La simulación de eventos y evaluación de agentes
tendrá un coste aproximado O(eventos × N) para
políticas que examinen todos los agentes.

P2 y P3 añaden costes de estimación y actualización.

No fijar tiempos de ejecución sin medir el piloto.
Registrar tiempo CPU, memoria máxima y tiempo
de decisión por política.

7. CONDICIÓN PARA CONGELAR

Antes de implementar, identificar y registrar:

- Generador exacto H0–H2 de E1.
- Parámetros de dispersión y especialización.
- Estimador compartido por P2/P3.
- Implementación y configuración exactas de P3.
- Función de decisión común a P1/P2.

Estos elementos no deben quedar a elección de Codex.

Todo lo demás permanece conforme al protocolo CE-04.

No ejecutar experimentos.
No introducir nuevos factores.
No modificar retrospectivamente el diseño.
